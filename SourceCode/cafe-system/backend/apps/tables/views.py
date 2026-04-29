"""
Views cho module Tables (Bàn).
Dùng DRF APIView + db.transaction.atomic để đảm bảo tính nhất quán
khi chuyển bàn / gộp bàn.
"""
import logging
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLy, IsQuanLyOrNhanVien
from .models import Ban
from .serializers import (
    BanSerializer,
    TaoBanSerializer,
    CapNhatTrangThaiSerializer,
    ChuyenBanSerializer,
    GopBanSerializer,
)

logger = logging.getLogger(__name__)


def _get_hoa_don_model():
    """Lazy import tránh circular: orders → tables → orders."""
    from apps.orders.models import HoaDon
    return HoaDon


# ─────────────────────────────────────────────────────────────────────────────
# Sơ đồ bàn & thêm bàn
# ─────────────────────────────────────────────────────────────────────────────

class BanListCreateView(APIView):
    """
    GET  /api/tables/  → Toàn bộ sơ đồ bàn
    POST /api/tables/  → Thêm bàn mới (Quản lý)
    """
    authentication_classes = [CustomJWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsQuanLy()]
        return [IsQuanLyOrNhanVien()]

    def get(self, request):
        queryset = Ban.objects.all()

        khu_vuc = request.query_params.get('khu_vuc')
        if khu_vuc:
            queryset = queryset.filter(ten_khu_vuc__icontains=khu_vuc)

        trang_thai = request.query_params.get('trang_thai')
        if trang_thai is not None:
            try:
                queryset = queryset.filter(trang_thai=int(trang_thai))
            except (ValueError, TypeError):
                return Response(
                    {'success': False, 'message': 'trang_thai không hợp lệ. Dùng: 0, 1 hoặc 2.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = BanSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})

    def post(self, request):
        serializer = TaoBanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        ban = serializer.save()
        logger.info("Thêm bàn: ma_ban=%s — bởi %s", ban.ma_ban, request.user.ten_dang_nhap)
        return Response(
            {'success': True, 'message': 'Thêm bàn thành công.', 'data': BanSerializer(ban).data},
            status=status.HTTP_201_CREATED
        )


# ─────────────────────────────────────────────────────────────────────────────
# Chi tiết & xóa bàn
# ─────────────────────────────────────────────────────────────────────────────

class BanDetailView(APIView):
    """
    GET    /api/tables/{ma_ban}/  → Chi tiết 1 bàn
    DELETE /api/tables/{ma_ban}/  → Xóa bàn (Quản lý, bàn phải trống)
    """
    authentication_classes = [CustomJWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsQuanLy()]
        return [IsQuanLyOrNhanVien()]

    def get(self, request, ma_ban):
        ban = get_object_or_404(Ban, pk=ma_ban)
        HoaDon = _get_hoa_don_model()
        hoa_don_mo = HoaDon.objects.filter(
            ma_ban=ban, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE
        ).values('ma_hd', 'ngay_lap', 'tong_tien', 'trang_thai')

        return Response({
            'success': True,
            'data': {**BanSerializer(ban).data, 'hoa_don_dang_mo': list(hoa_don_mo)},
        })

    def delete(self, request, ma_ban):
        ban = get_object_or_404(Ban, pk=ma_ban)
        if ban.trang_thai != Ban.TrangThai.TRONG:
            return Response(
                {'success': False, 'message': 'Không thể xóa bàn đang có khách hoặc đang dọn.', 'code': 'ban_not_empty'},
                status=status.HTTP_409_CONFLICT
            )
        HoaDon = _get_hoa_don_model()
        if HoaDon.objects.filter(ma_ban=ban, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE).exists():
            return Response(
                {'success': False, 'message': 'Bàn còn hóa đơn đang chờ xử lý.', 'code': 'open_orders_exist'},
                status=status.HTTP_409_CONFLICT
            )
        ban_info = str(ban)
        ban.delete()
        logger.info("Xóa bàn: %s — bởi %s", ban_info, request.user.ten_dang_nhap)
        return Response({'success': True, 'message': 'Xóa bàn thành công.'})


# ─────────────────────────────────────────────────────────────────────────────
# Cập nhật trạng thái bàn
# ─────────────────────────────────────────────────────────────────────────────

class CapNhatTrangThaiBanView(APIView):
    """PATCH /api/tables/{ma_ban}/status/"""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    def patch(self, request, ma_ban):
        ban = get_object_or_404(Ban, pk=ma_ban)
        serializer = CapNhatTrangThaiSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        trang_thai_moi = serializer.validated_data['trang_thai']

        # Không cho về Trống khi còn hóa đơn mở
        if trang_thai_moi == Ban.TrangThai.TRONG:
            HoaDon = _get_hoa_don_model()
            if HoaDon.objects.filter(ma_ban=ban, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE).exists():
                return Response(
                    {'success': False, 'message': 'Không thể đặt bàn về Trống khi còn hóa đơn chưa hoàn tất.', 'code': 'open_orders_exist'},
                    status=status.HTTP_409_CONFLICT
                )

        cu = Ban.TrangThai(ban.trang_thai).label
        ban.trang_thai = trang_thai_moi
        ban.save(update_fields=['trang_thai', 'ngay_cap_nhat'])

        logger.info("Trạng thái bàn %s: %s → %s — bởi %s", ma_ban, cu, ban.get_trang_thai_display(), request.user.ten_dang_nhap)
        return Response({
            'success': True,
            'message': f'Cập nhật trạng thái bàn {ma_ban} thành công: {ban.get_trang_thai_display()}',
            'data': BanSerializer(ban).data,
        })


# ─────────────────────────────────────────────────────────────────────────────
# Chuyển bàn
# ─────────────────────────────────────────────────────────────────────────────

class ChuyenBanView(APIView):
    """
    POST /api/tables/transfer/
    Body: { "tu_ban": <int>, "den_ban": <int> }

    Logic (atomic):
        1. Bàn nguồn phải đang Có khách.
        2. Bàn đích phải đang Trống.
        3. Chuyển toàn bộ HoaDon 'Chờ pha chế' từ nguồn → đích.
        4. Nguồn → Đang dọn, Đích → Có khách.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    @transaction.atomic
    def post(self, request):
        serializer = ChuyenBanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        ma_tu = serializer.validated_data['tu_ban']
        ma_den = serializer.validated_data['den_ban']

        try:
            ban_nguon = Ban.objects.select_for_update().get(pk=ma_tu)
        except Ban.DoesNotExist:
            return Response(
                {'success': False, 'message': f'Bàn nguồn {ma_tu} không tồn tại.', 'code': 'ban_nguon_not_found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            ban_dich = Ban.objects.select_for_update().get(pk=ma_den)
        except Ban.DoesNotExist:
            return Response(
                {'success': False, 'message': f'Bàn đích {ma_den} không tồn tại.', 'code': 'ban_dich_not_found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if ban_nguon.trang_thai != Ban.TrangThai.CO_KHACH:
            return Response(
                {'success': False, 'message': f'Bàn nguồn {ma_tu} không đang có khách ({ban_nguon.get_trang_thai_display()}).', 'code': 'ban_nguon_not_occupied'},
                status=status.HTTP_409_CONFLICT
            )

        if ban_dich.trang_thai != Ban.TrangThai.TRONG:
            return Response(
                {'success': False, 'message': f'Bàn đích {ma_den} không trống ({ban_dich.get_trang_thai_display()}).', 'code': 'ban_dich_not_empty'},
                status=status.HTTP_409_CONFLICT
            )

        HoaDon = _get_hoa_don_model()
        hoa_don_qs = HoaDon.objects.filter(ma_ban=ban_nguon, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE)
        so_hd = hoa_don_qs.count()

        if so_hd == 0:
            return Response(
                {'success': False, 'message': f'Bàn nguồn {ma_tu} không có hóa đơn nào đang mở.', 'code': 'no_open_orders'},
                status=status.HTTP_409_CONFLICT
            )

        hoa_don_qs.update(ma_ban=ban_dich)
        ban_nguon.trang_thai = Ban.TrangThai.DANG_DON
        ban_dich.trang_thai = Ban.TrangThai.CO_KHACH
        Ban.objects.bulk_update([ban_nguon, ban_dich], ['trang_thai', 'ngay_cap_nhat'])

        logger.info("Chuyển bàn %s → %s (%d HĐ) — bởi %s", ma_tu, ma_den, so_hd, request.user.ten_dang_nhap)
        return Response({
            'success': True,
            'message': f'Chuyển {so_hd} hóa đơn từ Bàn {ma_tu} → Bàn {ma_den} thành công.',
            'data': {
                'ban_nguon': BanSerializer(ban_nguon).data,
                'ban_dich': BanSerializer(ban_dich).data,
                'so_hoa_don_chuyen': so_hd,
            },
        })


# ─────────────────────────────────────────────────────────────────────────────
# Gộp bàn
# ─────────────────────────────────────────────────────────────────────────────

class GopBanView(APIView):
    """
    POST /api/tables/merge/
    Body: { "ban_chinh": <int>, "ban_phu": [<int>, ...] }

    Logic (atomic):
        1. Bàn chính phải đang Có khách.
        2. Mỗi bàn phụ phải đang Có khách.
        3. Chuyển HoaDon 'Chờ pha chế' từ các bàn phụ → bàn chính.
        4. Các bàn phụ → Đang dọn. Bàn chính giữ nguyên.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLyOrNhanVien]

    @transaction.atomic
    def post(self, request):
        serializer = GopBanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        ma_chinh = serializer.validated_data['ban_chinh']
        ma_phu_list = serializer.validated_data['ban_phu']
        tat_ca_ma = [ma_chinh] + ma_phu_list

        # Lock tất cả bàn trong 1 query
        ban_qs = Ban.objects.select_for_update().filter(pk__in=tat_ca_ma)
        ban_dict = {b.ma_ban: b for b in ban_qs}

        missing = [ma for ma in tat_ca_ma if ma not in ban_dict]
        if missing:
            return Response(
                {'success': False, 'message': f'Các bàn không tồn tại: {missing}', 'code': 'ban_not_found'},
                status=status.HTTP_404_NOT_FOUND
            )

        ban_chinh = ban_dict[ma_chinh]
        ban_phu_objs = [ban_dict[ma] for ma in ma_phu_list]

        if ban_chinh.trang_thai != Ban.TrangThai.CO_KHACH:
            return Response(
                {'success': False, 'message': f'Bàn chính {ma_chinh} phải đang có khách (hiện: {ban_chinh.get_trang_thai_display()}).', 'code': 'ban_chinh_not_occupied'},
                status=status.HTTP_409_CONFLICT
            )

        ban_phu_sai = [b for b in ban_phu_objs if b.trang_thai != Ban.TrangThai.CO_KHACH]
        if ban_phu_sai:
            sai_info = [f"Bàn {b.ma_ban} ({b.get_trang_thai_display()})" for b in ban_phu_sai]
            return Response(
                {'success': False, 'message': f'Các bàn phụ phải đang có khách. Không hợp lệ: {", ".join(sai_info)}', 'code': 'ban_phu_not_occupied'},
                status=status.HTTP_409_CONFLICT
            )

        HoaDon = _get_hoa_don_model()
        tong_hd = 0
        for ban_phu in ban_phu_objs:
            so_hd = HoaDon.objects.filter(
                ma_ban=ban_phu, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE
            ).update(ma_ban=ban_chinh)
            tong_hd += so_hd

        for b in ban_phu_objs:
            b.trang_thai = Ban.TrangThai.DANG_DON
        Ban.objects.bulk_update(ban_phu_objs, ['trang_thai', 'ngay_cap_nhat'])

        logger.info("Gộp bàn %s → bàn chính %s (%d HĐ) — bởi %s", ma_phu_list, ma_chinh, tong_hd, request.user.ten_dang_nhap)
        return Response({
            'success': True,
            'message': f'Gộp {len(ma_phu_list)} bàn phụ vào Bàn {ma_chinh} thành công. Đã chuyển {tong_hd} hóa đơn.',
            'data': {
                'ban_chinh': BanSerializer(ban_chinh).data,
                'ban_phu': BanSerializer(ban_phu_objs, many=True).data,
                'tong_hoa_don_gop': tong_hd,
            },
        })
