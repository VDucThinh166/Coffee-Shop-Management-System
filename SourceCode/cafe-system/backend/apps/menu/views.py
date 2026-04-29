"""
Views cho module Menu (Thực đơn).
"""
import logging
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLy
from .models import ThucDon
from .serializers import ThucDonSerializer, ThucDonStatusSerializer

logger = logging.getLogger(__name__)


class ThucDonListCreateView(APIView):
    """
    GET  /api/menu/  → Lấy toàn bộ menu (Public). Hỗ trợ filter ma_loai, trang_thai.
    POST /api/menu/  → Thêm món mới (Chỉ quản lý). Hỗ trợ upload file ảnh (multipart/form-data).
    """
    # Khai báo CustomJWTAuthentication, nhưng permission tùy theo method
    authentication_classes = [CustomJWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsQuanLy()]
        # GET: Public (không cần đăng nhập)
        return []

    def get(self, request):
        queryset = ThucDon.objects.all()

        ma_loai = request.query_params.get('type') or request.query_params.get('ma_loai')
        if ma_loai:
            queryset = queryset.filter(ma_loai__iexact=ma_loai)

        trang_thai = request.query_params.get('status') or request.query_params.get('trang_thai')
        if trang_thai is not None:
            try:
                queryset = queryset.filter(trang_thai=int(trang_thai))
            except ValueError:
                pass

        serializer = ThucDonSerializer(queryset, many=True, context={'request': request})
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data,
        })

    def post(self, request):
        serializer = ThucDonSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mon = serializer.save()
        logger.info("Thêm món mới: %s — bởi %s", mon.ten_mon, request.user.ten_dang_nhap)
        return Response(
            {'success': True, 'message': 'Thêm món thành công.', 'data': ThucDonSerializer(mon, context={'request': request}).data},
            status=status.HTTP_201_CREATED
        )


class ThucDonDetailView(APIView):
    """
    GET    /api/menu/{ma_mon}/  → Chi tiết món (Public)
    PUT    /api/menu/{ma_mon}/  → Sửa món (Quản lý)
    DELETE /api/menu/{ma_mon}/  → Xóa món (Quản lý)
    """
    authentication_classes = [CustomJWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsQuanLy()]
        return []

    def get(self, request, ma_mon):
        mon = get_object_or_404(ThucDon, pk=ma_mon)
        serializer = ThucDonSerializer(mon, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

    def put(self, request, ma_mon):
        mon = get_object_or_404(ThucDon, pk=ma_mon)
        serializer = ThucDonSerializer(mon, data=request.data, partial=True, context={'request': request})
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_mon = serializer.save()
        logger.info("Cập nhật món %s — bởi %s", ma_mon, request.user.ten_dang_nhap)
        return Response({
            'success': True,
            'message': 'Cập nhật món thành công.',
            'data': ThucDonSerializer(updated_mon, context={'request': request}).data
        })

    def delete(self, request, ma_mon):
        mon = get_object_or_404(ThucDon, pk=ma_mon)
        
        # NOTE: Trong thực tế, nếu món đã nằm trong ChiTietHoaDon, ta không nên xóa hẳn
        # (do PROTECT constraint). Thay vì xóa, thường ta chuyển trang_thai = HET (0)
        # hoặc có trường is_deleted. Ở đây tạm cứ xóa, nếu bị lỗi ProtectError thì xử lý.
        try:
            ten_mon = mon.ten_mon
            mon.delete()
            logger.info("Xóa món: %s — bởi %s", ten_mon, request.user.ten_dang_nhap)
            return Response({'success': True, 'message': 'Xóa món thành công.'})
        except Exception as e:
            return Response(
                {'success': False, 'message': 'Không thể xóa món này vì nó đã được sử dụng trong hóa đơn.', 'detail': str(e)},
                status=status.HTTP_409_CONFLICT
            )


class CapNhatTrangThaiThucDonView(APIView):
    """
    PATCH /api/menu/{ma_mon}/status/
    Body: { "trang_thai": 0 | 1 }
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def patch(self, request, ma_mon):
        mon = get_object_or_404(ThucDon, pk=ma_mon)
        serializer = ThucDonStatusSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        mon.trang_thai = serializer.validated_data['trang_thai']
        mon.save(update_fields=['trang_thai', 'ngay_cap_nhat'])
        
        logger.info("Cập nhật trạng thái món %s → %s — bởi %s", ma_mon, mon.get_trang_thai_display(), request.user.ten_dang_nhap)
        return Response({
            'success': True,
            'message': f'Cập nhật trạng thái thành công: {mon.get_trang_thai_display()}.',
            'data': ThucDonSerializer(mon, context={'request': request}).data
        })
