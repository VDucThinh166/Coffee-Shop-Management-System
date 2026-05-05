"""
Views cho module Promotions (Khuyến mãi).
Tất cả đều yêu cầu quyền Quản lý.
"""
from datetime import date
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLy
from .models import KhuyenMai
from .serializers import KhuyenMaiSerializer


class KhuyenMaiListCreateView(APIView):
    """
    GET /api/promotions/  → Danh sách khuyến mãi
    POST /api/promotions/ → Thêm mới
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        queryset = KhuyenMai.objects.all()
        serializer = KhuyenMaiSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})

    def post(self, request):
        serializer = KhuyenMaiSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        km = serializer.save()
        return Response({'success': True, 'message': 'Tạo khuyến mãi thành công.', 'data': KhuyenMaiSerializer(km).data}, status=status.HTTP_201_CREATED)


class KhuyenMaiDetailView(APIView):
    """
    GET /api/promotions/{ma_km}/
    PUT /api/promotions/{ma_km}/
    DELETE /api/promotions/{ma_km}/
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get_object(self, ma_km):
        return get_object_or_404(KhuyenMai, pk=ma_km)

    def get(self, request, ma_km):
        km = self.get_object(ma_km)
        return Response({'success': True, 'data': KhuyenMaiSerializer(km).data})

    def put(self, request, ma_km):
        km = self.get_object(ma_km)
        serializer = KhuyenMaiSerializer(km, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        km = serializer.save()
        return Response({'success': True, 'message': 'Cập nhật thành công.', 'data': KhuyenMaiSerializer(km).data})

    def delete(self, request, ma_km):
        km = self.get_object(ma_km)
        # Tương tự như Món, Khuyến mãi có thể đã được gán vào Hóa Đơn, nên dùng cờ is_active.
        # Hoặc delete cứng nếu chưa dùng. Ta có thể thử delete cứng, nếu lỗi thì soft delete.
        try:
            km.delete()
            return Response({'success': True, 'message': 'Xóa khuyến mãi thành công.'})
        except Exception as e:
            # Soft delete fallback
            km.is_active = False
            km.save(update_fields=['is_active', 'ngay_cap_nhat'])
            return Response({'success': True, 'message': 'Khuyến mãi đã được sử dụng nên chỉ bị vô hiệu hóa (is_active=False).', 'detail': str(e)})


class ActivePromotionsView(APIView):
    """
    GET /api/promotions/active/ → Lấy các voucher có hiệu lực trong hôm nay.
    Điều kiện: is_active=True, ngay_bd <= today <= ngay_kt
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]  # Hoặc Nhân viên nếu cần, nhưng đề ghi Management only

    def get(self, request):
        today = timezone.localtime().date()
        queryset = KhuyenMai.objects.filter(
            is_active=True,
            ngay_bd__lte=today,
            ngay_kt__gte=today
        )
        serializer = KhuyenMaiSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})
