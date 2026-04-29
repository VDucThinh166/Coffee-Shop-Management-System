"""
Views cho module Staff (Nhân sự & Chấm công).
"""
import logging
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLy, IsQuanLyOrNhanVien
from .models import NhanVien, CaLam, ChamCong
from .serializers import NhanVienSerializer, CaLamSerializer, ChamCongSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Quản lý Nhân viên (Manager only)
# ---------------------------------------------------------------------------

class NhanVienListCreateView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        queryset = NhanVien.objects.all()
        serializer = NhanVienSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})

    def post(self, request):
        serializer = NhanVienSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        nv = serializer.save()
        return Response({'success': True, 'message': 'Thêm nhân viên thành công.', 'data': NhanVienSerializer(nv).data}, status=status.HTTP_201_CREATED)


class NhanVienDetailView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get_object(self, pk):
        return get_object_or_404(NhanVien, pk=pk)

    def get(self, request, pk):
        nv = self.get_object(pk)
        return Response({'success': True, 'data': NhanVienSerializer(nv).data})

    def put(self, request, pk):
        nv = self.get_object(pk)
        serializer = NhanVienSerializer(nv, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        nv = serializer.save()
        return Response({'success': True, 'message': 'Cập nhật thành công.', 'data': NhanVienSerializer(nv).data})

    def delete(self, request, pk):
        nv = self.get_object(pk)
        nv.is_active = False
        nv.save(update_fields=['is_active'])
        return Response({'success': True, 'message': 'Đã vô hiệu hóa nhân viên.'})


# ---------------------------------------------------------------------------
# Quản lý Ca làm (Manager only)
# ---------------------------------------------------------------------------

class CaLamListCreateView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        queryset = CaLam.objects.all()
        serializer = CaLamSerializer(queryset, many=True)
        return Response({'success': True, 'count': queryset.count(), 'data': serializer.data})

    def post(self, request):
        serializer = CaLamSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        ca = serializer.save()
        return Response({'success': True, 'message': 'Tạo ca làm thành công.', 'data': CaLamSerializer(ca).data}, status=status.HTTP_201_CREATED)


class CaLamDetailView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get_object(self, pk):
        return get_object_or_404(CaLam, pk=pk)

    def get(self, request, pk):
        ca = self.get_object(pk)
        return Response({'success': True, 'data': CaLamSerializer(ca).data})

    def put(self, request, pk):
        ca = self.get_object(pk)
        serializer = CaLamSerializer(ca, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Dữ liệu không hợp lệ.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        ca = serializer.save()
        return Response({'success': True, 'message': 'Cập nhật thành công.', 'data': CaLamSerializer(ca).data})


# ---------------------------------------------------------------------------
# Chấm công (Check-in / Check-out / Timesheet)
# ---------------------------------------------------------------------------

class CheckInView(APIView):
    """
    POST /api/attendance/checkin/
    Nhân viên thực hiện check-in (tại POS).
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Lấy nhân viên từ tài khoản đang đăng nhập
        try:
            nv = request.user.nhan_vien
        except NhanVien.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Tài khoản không được liên kết với nhân viên nào.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.localtime()
        today = now.date()
        current_time = now.time()

        # Tìm ca làm của nhân viên trong ngày hôm nay
        # Giả định nhân viên check-in vào ca gần nhất với giờ hiện tại hoặc ca duy nhất trong ngày
        ca_lam = CaLam.objects.filter(ma_nv=nv, ngay_lam=today).first()

        if not ca_lam:
            return Response(
                {'success': False, 'message': 'Bạn không có ca làm việc nào được xếp trong hôm nay.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Nếu đã chấm công ca này rồi thì không cho chấm lại
        if ChamCong.objects.filter(ma_ca=ca_lam, ma_nv=nv).exists():
            return Response(
                {'success': False, 'message': 'Bạn đã thực hiện check-in cho ca này rồi.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Tính toán trễ giờ (đổi ra phút để so sánh)
        # Vì so sánh time, ta tạo datetime cùng ngày để trừ
        dt_vao = datetime.combine(today, current_time)
        dt_bat_dau = datetime.combine(today, ca_lam.gio_bat_dau)
        
        diff_minutes = (dt_vao - dt_bat_dau).total_seconds() / 60

        if diff_minutes <= 0:
            trang_thai = ChamCong.TrangThai.DUNG_GIO
        elif diff_minutes <= 15:
            trang_thai = ChamCong.TrangThai.DI_TRE
        else:
            trang_thai = ChamCong.TrangThai.DI_TRE_NANG

        # Tạo record chấm công
        cham_cong = ChamCong.objects.create(
            ma_ca=ca_lam,
            ma_nv=nv,
            gio_vao_thuc=current_time,
            trang_thai=trang_thai
        )

        logger.info("Check-in: NV %s - %s", nv.ho_ten, trang_thai)
        return Response({
            'success': True,
            'message': f'Check-in thành công. Trạng thái: {cham_cong.get_trang_thai_display()}.',
            'data': ChamCongSerializer(cham_cong).data
        })


class CheckOutView(APIView):
    """
    POST /api/attendance/checkout/
    Nhân viên thực hiện check-out (tại POS).
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            nv = request.user.nhan_vien
        except NhanVien.DoesNotExist:
            return Response({'success': False, 'message': 'Tài khoản không hợp lệ.'}, status=400)

        now = timezone.localtime()
        today = now.date()
        current_time = now.time()

        # Tìm record chấm công hôm nay
        cham_cong = ChamCong.objects.filter(ma_nv=nv, ma_ca__ngay_lam=today).first()

        if not cham_cong:
            return Response(
                {'success': False, 'message': 'Không tìm thấy dữ liệu check-in trong hôm nay.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if cham_cong.gio_ra_thuc:
            return Response(
                {'success': False, 'message': 'Bạn đã thực hiện check-out rồi.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cham_cong.gio_ra_thuc = current_time
        cham_cong.save(update_fields=['gio_ra_thuc', 'ngay_cap_nhat'])

        logger.info("Check-out: NV %s lúc %s", nv.ho_ten, current_time)
        return Response({
            'success': True,
            'message': 'Check-out thành công.',
            'data': ChamCongSerializer(cham_cong).data
        })


class ChamCongListView(APIView):
    """
    GET /api/attendance/
    Quản lý xem bảng chấm công, có thể filter theo nhân viên, tháng, năm.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        queryset = ChamCong.objects.all().select_related('ma_nv', 'ma_ca')

        ma_nv = request.query_params.get('ma_nv')
        if ma_nv:
            queryset = queryset.filter(ma_nv_id=ma_nv)

        thang = request.query_params.get('thang')
        if thang:
            queryset = queryset.filter(ma_ca__ngay_lam__month=thang)

        nam = request.query_params.get('nam')
        if nam:
            queryset = queryset.filter(ma_ca__ngay_lam__year=nam)

        serializer = ChamCongSerializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })
