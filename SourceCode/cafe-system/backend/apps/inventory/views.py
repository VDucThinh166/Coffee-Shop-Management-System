"""
Views cho module Inventory (Kho hàng).
Tất cả đều yêu cầu quyền Quản lý.
"""
import logging
from decimal import Decimal
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLy
from .models import TonKho, PhieuNhap, ChiTietPhieuNhap
from .serializers import TonKhoSerializer, PhieuNhapSerializer, NhapKhoSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tồn kho (TonKho)
# ---------------------------------------------------------------------------

class TonKhoListCreateView(APIView):
    """
    GET  /api/inventory/  → Xem danh sách nguyên liệu
    POST /api/inventory/  → Thêm nguyên liệu mới (lúc tạo, số lượng tồn = 0)
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        queryset = TonKho.objects.all()
        serializer = TonKhoSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})

    def post(self, request):
        serializer = TonKhoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        nl = serializer.save()
        return Response({'success': True, 'message': 'Thêm nguyên liệu thành công.', 'data': TonKhoSerializer(nl).data}, status=status.HTTP_201_CREATED)


class TonKhoDetailView(APIView):
    """
    GET /api/inventory/{ma_nl}/
    PUT /api/inventory/{ma_nl}/
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get_object(self, ma_nl):
        return get_object_or_404(TonKho, pk=ma_nl)

    def get(self, request, ma_nl):
        nl = self.get_object(ma_nl)
        return Response({'success': True, 'data': TonKhoSerializer(nl).data})

    def put(self, request, ma_nl):
        nl = self.get_object(ma_nl)
        # Chỉ cho sửa tên, đơn vị tính, ngưỡng báo động. 
        # so_luong_ton chỉ được thay đổi thông qua Nhập Kho (PhieuNhap).
        serializer = TonKhoSerializer(nl, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        nl = serializer.save()
        return Response({'success': True, 'message': 'Cập nhật nguyên liệu thành công.', 'data': TonKhoSerializer(nl).data})


class InventoryAlertView(APIView):
    """
    GET /api/inventory/alerts/ → Lấy các nguyên liệu có số lượng tồn <= ngưỡng báo động
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        # Filter raw logic: so_luong_ton <= nguong_bao_dong
        queryset = TonKho.objects.filter(so_luong_ton__lte=models.F('nguong_bao_dong'))
        
        serializer = TonKhoSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})


# ---------------------------------------------------------------------------
# Nhập kho (PhieuNhap)
# ---------------------------------------------------------------------------

class PhieuNhapListView(APIView):
    """
    GET /api/inventory/imports/ → Lịch sử nhập kho
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        queryset = PhieuNhap.objects.all()
        serializer = PhieuNhapSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})


class NhapKhoView(APIView):
    """
    POST /api/inventory/import/
    Body: 
    {
        "ngay_nhap": "YYYY-MM-DD",
        "chi_tiet": [
            {"ma_nl": 1, "sl_nhap": 5.5, "don_gia_nhap": 150000},
            {"ma_nl": 2, "sl_nhap": 10, "don_gia_nhap": 50000}
        ]
    }
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    @transaction.atomic
    def post(self, request):
        serializer = NhapKhoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        ngay_nhap = serializer.validated_data['ngay_nhap']
        chi_tiet_list = serializer.validated_data['chi_tiet']
        ma_nv = request.user.nhan_vien  # Sẽ throw lỗi nếu user ko có NhanVien, cần try-except

        try:
            nv = request.user.nhan_vien
        except Exception:
            return Response({'success': False, 'message': 'Tài khoản của bạn không được liên kết với nhân viên nào.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Kiểm tra nguyên liệu tồn tại trước khi làm gì khác
        ma_nl_ids = [item['ma_nl'] for item in chi_tiet_list]
        ton_kho_qs = TonKho.objects.select_for_update().filter(pk__in=ma_nl_ids)
        ton_kho_dict = {tk.ma_nl: tk for tk in ton_kho_qs}

        missing_nls = [ma for ma in ma_nl_ids if ma not in ton_kho_dict]
        if missing_nls:
            return Response({'success': False, 'message': f'Nguyên liệu không tồn tại: {missing_nls}'}, status=status.HTTP_404_NOT_FOUND)

        # 2. Tạo Phiếu Nhập
        phieu_nhap = PhieuNhap.objects.create(
            ngay_nhap=ngay_nhap,
            ma_nv=nv,
            tong_gia_tri=0
        )

        tong_gia_tri = Decimal('0')
        chi_tiet_objs = []
        for item in chi_tiet_list:
            tk = ton_kho_dict[item['ma_nl']]
            sl_nhap = Decimal(str(item['sl_nhap']))
            don_gia = Decimal(str(item['don_gia_nhap']))
            
            # Cập nhật số lượng tồn
            tk.so_luong_ton += sl_nhap
            
            # Cộng dồn tổng giá trị
            thanh_tien = sl_nhap * don_gia
            tong_gia_tri += thanh_tien

            # Tạo chi tiết
            chi_tiet_objs.append(ChiTietPhieuNhap(
                ma_phieu=phieu_nhap,
                ma_nl=tk,
                sl_nhap=sl_nhap,
                don_gia_nhap=don_gia
            ))

        # Lưu database batch
        ChiTietPhieuNhap.objects.bulk_create(chi_tiet_objs)
        TonKho.objects.bulk_update(ton_kho_dict.values(), ['so_luong_ton', 'ngay_cap_nhat'])
        
        # Cập nhật tổng giá trị phiếu
        phieu_nhap.tong_gia_tri = tong_gia_tri
        phieu_nhap.save(update_fields=['tong_gia_tri', 'ngay_cap_nhat'])

        logger.info("Nhập kho: Phiếu %s, Tổng %s VNĐ — bởi %s", phieu_nhap.ma_phieu, tong_gia_tri, request.user.ten_dang_nhap)

        return Response({
            'success': True, 
            'message': 'Nhập kho thành công.', 
            'data': PhieuNhapSerializer(phieu_nhap).data
        }, status=status.HTTP_201_CREATED)
