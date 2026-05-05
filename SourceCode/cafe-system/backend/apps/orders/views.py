"""
Views cho module Orders (Hóa đơn).
Yêu cầu quyền Quản lý hoặc Nhân viên.
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLyOrNhanVien, IsQuanLy
from apps.customers.models import KhachHang
from apps.promotions.models import KhuyenMai
from apps.menu.models import ThucDon
from apps.tables.models import Ban
from .models import HoaDon, ChiTietHoaDon
from .serializers import (
    HoaDonSerializer, 
    HoaDonCreateSerializer,
    ChiTietAddSerializer,
    ThanhToanSerializer
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Quản lý Hóa đơn
# ---------------------------------------------------------------------------

class HoaDonListCreateView(APIView):
    """
    GET  /api/orders/  → Xem danh sách hóa đơn (filter theo ban, trang_thai)
    POST /api/orders/  → Tạo hóa đơn mới
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    def get(self, request):
        queryset = HoaDon.objects.all().prefetch_related('chi_tiet', 'chi_tiet__ma_mon')

        ban = request.query_params.get('ban')
        if ban:
            queryset = queryset.filter(ma_ban_id=ban)

        trang_thai = request.query_params.get('trang_thai')
        if trang_thai:
            queryset = queryset.filter(trang_thai=trang_thai)

        serializer = HoaDonSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})

    @transaction.atomic
    def post(self, request):
        serializer = HoaDonCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=400)

        ma_ban = serializer.validated_data['ma_ban']
        sdt_khach = serializer.validated_data.get('sdt_khach')

        # Lock bàn
        try:
            ban = Ban.objects.select_for_update().get(pk=ma_ban)
        except Ban.DoesNotExist:
            return Response({'success': False, 'message': 'Bàn không tồn tại.'}, status=404)

        if ban.trang_thai != Ban.TrangThai.TRONG:
            return Response({'success': False, 'message': 'Bàn không trống, không thể tạo hóa đơn mới.'}, status=400)

        khach_hang = None
        if sdt_khach:
            try:
                khach_hang = KhachHang.objects.get(pk=sdt_khach)
            except KhachHang.DoesNotExist:
                return Response({'success': False, 'message': 'Không tìm thấy khách hàng với SĐT này.'}, status=404)

        try:
            nv = request.user.nhan_vien
        except Exception:
            return Response({'success': False, 'message': 'Tài khoản không gắn với nhân viên.'}, status=400)

        hd = HoaDon.objects.create(
            ma_nv=nv,
            ma_ban=ban,
            sdt_khach=khach_hang,
            trang_thai=HoaDon.TrangThai.CHO_PHA_CHE
        )

        ban.trang_thai = Ban.TrangThai.CO_KHACH
        ban.save(update_fields=['trang_thai'])

        return Response({'success': True, 'message': 'Tạo hóa đơn thành công.', 'data': HoaDonSerializer(hd).data}, status=201)


class HoaDonDetailView(APIView):
    """
    GET /api/orders/{ma_hd}/
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    def get(self, request, ma_hd):
        hd = get_object_or_404(HoaDon, pk=ma_hd)
        return Response({'success': True, 'data': HoaDonSerializer(hd).data})


class HuyHoaDonView(APIView):
    """
    PATCH /api/orders/{ma_hd}/cancel/
    Chỉ Quản lý mới được hủy hóa đơn. Cập nhật HD -> Đã hủy, Bàn -> Trống.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    @transaction.atomic
    def patch(self, request, ma_hd):
        hd = get_object_or_404(HoaDon.objects.select_for_update(), pk=ma_hd)
        if hd.trang_thai != HoaDon.TrangThai.CHO_PHA_CHE:
            return Response({'success': False, 'message': 'Chỉ có thể hủy hóa đơn đang chờ pha chế.'}, status=400)

        ban = Ban.objects.select_for_update().get(pk=hd.ma_ban_id)
        
        hd.trang_thai = HoaDon.TrangThai.DA_HUY
        hd.save(update_fields=['trang_thai', 'ngay_cap_nhat'])

        ban.trang_thai = Ban.TrangThai.TRONG
        ban.save(update_fields=['trang_thai'])

        return Response({'success': True, 'message': 'Đã hủy hóa đơn và trả lại bàn.'})


# ---------------------------------------------------------------------------
# Chi Tiết Hóa Đơn (Thêm/Xóa món)
# ---------------------------------------------------------------------------

class ChiTietHoaDonView(APIView):
    """
    POST   /api/orders/{ma_hd}/items/   → Thêm món
    DELETE /api/orders/{ma_hd}/items/{id}/ → Xóa món
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    @transaction.atomic
    def post(self, request, ma_hd):
        hd = get_object_or_404(HoaDon.objects.select_for_update(), pk=ma_hd)
        if hd.trang_thai != HoaDon.TrangThai.CHO_PHA_CHE:
            return Response({'success': False, 'message': 'Không thể thêm món vào hóa đơn đã chốt.'}, status=400)

        serializer = ChiTietAddSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=400)

        ma_mon = serializer.validated_data['ma_mon']
        so_luong = serializer.validated_data['so_luong']
        ghi_chu = serializer.validated_data.get('ghi_chu', '')

        mon = get_object_or_404(ThucDon, pk=ma_mon)

        # Nếu món đã có trong HD -> cộng dồn số lượng. Nếu chưa -> tạo mới.
        ct, created = ChiTietHoaDon.objects.get_or_create(
            ma_hd=hd, ma_mon=mon,
            defaults={'so_luong': so_luong, 'gia_ban': mon.don_gia, 'ghi_chu': ghi_chu}
        )

        if not created:
            ct.so_luong += so_luong
            if ghi_chu:
                ct.ghi_chu = ct.ghi_chu + " | " + ghi_chu if ct.ghi_chu else ghi_chu
            ct.save()

        # Update tổng tiền tạm thời
        hd.tong_tien = sum(item.thanh_tien for item in hd.chi_tiet.all())
        hd.save(update_fields=['tong_tien'])

        return Response({'success': True, 'message': 'Đã thêm món vào hóa đơn.', 'data': HoaDonSerializer(hd).data})

    @transaction.atomic
    def delete(self, request, ma_hd, item_id):
        hd = get_object_or_404(HoaDon.objects.select_for_update(), pk=ma_hd)
        if hd.trang_thai != HoaDon.TrangThai.CHO_PHA_CHE:
            return Response({'success': False, 'message': 'Không thể xóa món khỏi hóa đơn đã chốt.'}, status=400)

        ct = get_object_or_404(ChiTietHoaDon, pk=item_id, ma_hd=hd)
        ct.delete()

        # Cập nhật tổng tiền
        hd.tong_tien = sum(item.thanh_tien for item in hd.chi_tiet.all())
        hd.save(update_fields=['tong_tien'])

        return Response({'success': True, 'message': 'Đã xóa món khỏi hóa đơn.', 'data': HoaDonSerializer(hd).data})


# ---------------------------------------------------------------------------
# Thanh toán (Checkout)
# ---------------------------------------------------------------------------

class ThanhToanView(APIView):
    """
    POST /api/orders/{ma_hd}/checkout/
    Thực hiện logic giảm giá (Voucher, VIP), cộng điểm và hoàn tất hóa đơn.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    @transaction.atomic
    def post(self, request, ma_hd):
        hd = get_object_or_404(HoaDon.objects.select_for_update(), pk=ma_hd)
        if hd.trang_thai != HoaDon.TrangThai.CHO_PHA_CHE:
            return Response({'success': False, 'message': 'Hóa đơn không ở trạng thái chờ pha chế.'}, status=400)

        if hd.chi_tiet.count() == 0:
            return Response({'success': False, 'message': 'Hóa đơn trống, không thể thanh toán.'}, status=400)

        serializer = ThanhToanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=400)

        phuong_thuc = serializer.validated_data['phuong_thuc']
        promo_code = serializer.validated_data.get('promotion_code')

        subtotal = sum(item.thanh_tien for item in hd.chi_tiet.all())
        discount_percent = 0
        khuyen_mai = None

        # 1. Kiểm tra Khuyến Mãi
        if promo_code:
            # Assuming promo_code matches ten_chuong_trinh or ma_km. In real systems it's a code, but we use ma_km for simplicity
            try:
                # Trích xuất ma_km nếu client gửi dạng số
                khuyen_mai = KhuyenMai.objects.get(pk=int(promo_code), is_active=True)
                today = timezone.localtime().date()
                if not (khuyen_mai.ngay_bd <= today <= khuyen_mai.ngay_kt):
                    return Response({'success': False, 'message': 'Mã khuyến mãi không trong thời gian hiệu lực.'}, status=400)
                if subtotal < khuyen_mai.dieu_kien_toi_thieu:
                    return Response({'success': False, 'message': 'Hóa đơn chưa đủ điều kiện áp dụng mã này.'}, status=400)
            except (ValueError, KhuyenMai.DoesNotExist):
                return Response({'success': False, 'message': 'Mã khuyến mãi không hợp lệ.'}, status=400)

        # 2. Tính tỷ lệ giảm giá theo Decision Table
        is_vip = False
        if hd.sdt_khach and hd.sdt_khach.hang_tv != KhachHang.HangThanhVien.DONG:
            is_vip = True

        if subtotal >= 500000 and is_vip and khuyen_mai:
            discount_percent = 20
        elif subtotal >= 500000 and khuyen_mai:
            discount_percent = 15
        elif subtotal >= 500000:
            discount_percent = 10
        elif is_vip:
            discount_percent = 5
        else:
            discount_percent = 0

        # Nếu bản thân voucher lớn hơn mức giảm giá Decision Table -> ưu tiên dùng voucher
        # VD: Voucher 30%, điều kiện trên chỉ áp tối đa 20% thì dùng 30% hợp lý hơn. 
        # Nhưng theo đề bài "Áp dụng bảng quyết định", tôi sẽ tuân thủ tuyệt đối bảng.
        # Ở đây discount_percent đè lên voucher percent. Hoặc có thể là max. Ta lấy theo bảng quyết định của đề.

        final_total = subtotal * Decimal(100 - discount_percent) / Decimal(100)
        
        # Cập nhật hóa đơn
        hd.tong_tien = final_total
        hd.phuong_thuc = phuong_thuc
        hd.trang_thai = HoaDon.TrangThai.HOAN_TAT
        hd.ma_km = khuyen_mai
        hd.save()

        # Cập nhật Bàn -> Đang dọn
        ban = Ban.objects.select_for_update().get(pk=hd.ma_ban_id)
        ban.trang_thai = Ban.TrangThai.DANG_DON
        ban.save(update_fields=['trang_thai'])

        # 3. Tích điểm và thăng hạng thành viên
        if hd.sdt_khach:
            kh = KhachHang.objects.select_for_update().get(pk=hd.sdt_khach_id)
            earned_points = int(final_total // 10000)
            kh.diem_tich_luy += earned_points

            # Check hạng mới
            if kh.diem_tich_luy >= 3000:
                kh.hang_tv = KhachHang.HangThanhVien.KIM_CUONG
            elif kh.diem_tich_luy >= 1000:
                kh.hang_tv = KhachHang.HangThanhVien.VANG
            elif kh.diem_tich_luy >= 500:
                kh.hang_tv = KhachHang.HangThanhVien.BAC
            else:
                kh.hang_tv = KhachHang.HangThanhVien.DONG

            kh.save(update_fields=['diem_tich_luy', 'hang_tv', 'ngay_cap_nhat'])

        logger.info("Thanh toán HD %s thành công. Sub: %s, Discount: %s%%, Final: %s", hd.ma_hd, subtotal, discount_percent, final_total)

        return Response({
            'success': True, 
            'message': 'Thanh toán thành công.', 
            'data': HoaDonSerializer(hd).data,
            'checkout_summary': {
                'subtotal': float(subtotal),
                'discount_percent': discount_percent,
                'final_total': float(final_total),
                'points_earned': earned_points if hd.sdt_khach else 0
            }
        })
