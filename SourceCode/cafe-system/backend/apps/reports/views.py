"""
Views cho module Reports (Báo cáo & Thống kê).
Yêu cầu quyền Quản lý.
"""
import calendar
from datetime import datetime, date
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import ExtractDay
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.authentication.authentication import CustomJWTAuthentication
from apps.authentication.permissions import IsQuanLy
from apps.orders.models import HoaDon, ChiTietHoaDon
from apps.staff.models import ChamCong
from apps.customers.models import KhachHang


class DailyRevenueReportView(APIView):
    """
    GET /api/reports/revenue/daily/?date=2026-04-28
    Returns: total_revenue, invoice_count, average_per_invoice
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'success': False, 'message': 'Thiếu tham số date (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'success': False, 'message': 'Định dạng ngày không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lọc hóa đơn hoàn tất trong ngày
        qs = HoaDon.objects.filter(
            trang_thai=HoaDon.TrangThai.HOAN_TAT,
            ngay_lap__date=target_date
        )

        agg = qs.aggregate(
            total_revenue=Sum('tong_tien'),
            invoice_count=Count('ma_hd'),
            average_per_invoice=Avg('tong_tien')
        )

        data = {
            'date': date_str,
            'total_revenue': agg['total_revenue'] or 0,
            'invoice_count': agg['invoice_count'] or 0,
            'average_per_invoice': float(agg['average_per_invoice']) if agg['average_per_invoice'] else 0
        }

        return Response({'success': True, 'data': data})


class MonthlyRevenueReportView(APIView):
    """
    GET /api/reports/revenue/monthly/?thang=4&nam=2026
    Returns: Mảng doanh thu theo từng ngày trong tháng để vẽ biểu đồ
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        thang = request.query_params.get('thang')
        nam = request.query_params.get('nam')

        if not thang or not nam:
            return Response({'success': False, 'message': 'Thiếu tham số thang hoặc nam.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            thang = int(thang)
            nam = int(nam)
            num_days = calendar.monthrange(nam, thang)[1]
        except ValueError:
            return Response({'success': False, 'message': 'Tháng/Năm không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = HoaDon.objects.filter(
            trang_thai=HoaDon.TrangThai.HOAN_TAT,
            ngay_lap__year=nam,
            ngay_lap__month=thang
        ).annotate(
            day=ExtractDay('ngay_lap')
        ).values('day').annotate(
            daily_revenue=Sum('tong_tien')
        ).order_by('day')

        # Convert queryset to dictionary for quick lookup
        revenue_dict = {item['day']: item['daily_revenue'] for item in qs}

        # Trả về mảng đủ số ngày trong tháng, ngày nào không có doanh thu = 0
        chart_data = []
        for day in range(1, num_days + 1):
            chart_data.append({
                'day': day,
                'date': f"{nam}-{thang:02d}-{day:02d}",
                'revenue': revenue_dict.get(day, 0)
            })

        return Response({'success': True, 'data': chart_data})


class BestSellerReportView(APIView):
    """
    GET /api/reports/bestseller/?thang=4&nam=2026
    Returns: Top 10 món bán chạy nhất
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        thang = request.query_params.get('thang')
        nam = request.query_params.get('nam')
        
        if not thang or not nam:
            return Response({'success': False, 'message': 'Thiếu tham số thang hoặc nam.'}, status=400)

        qs = ChiTietHoaDon.objects.filter(
            ma_hd__trang_thai=HoaDon.TrangThai.HOAN_TAT,
            ma_hd__ngay_lap__year=nam,
            ma_hd__ngay_lap__month=thang
        ).values(
            'ma_mon__ma_mon',
            'ma_mon__ten_mon'
        ).annotate(
            total_quantity=Sum('so_luong'),
            total_revenue=Sum(F('so_luong') * F('gia_ban'))
        ).order_by('-total_quantity')[:10]

        data = []
        for item in qs:
            data.append({
                'item_id': item['ma_mon__ma_mon'],
                'item_name': item['ma_mon__ten_mon'],
                'quantity_sold': item['total_quantity'] or 0,
                'revenue': item['total_revenue'] or 0
            })

        return Response({'success': True, 'data': data})


class StaffAttendanceReportView(APIView):
    """
    GET /api/reports/staff/attendance/?thang=4&nam=2026
    Returns: Thống kê chấm công nhân viên (Số ngày đúng giờ, đi trễ, vắng)
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        thang = request.query_params.get('thang')
        nam = request.query_params.get('nam')

        if not thang or not nam:
            return Response({'success': False, 'message': 'Thiếu tham số thang hoặc nam.'}, status=400)

        # Count with conditions
        qs = ChamCong.objects.filter(
            ma_ca__ngay_lam__year=nam,
            ma_ca__ngay_lam__month=thang
        ).values(
            'ma_nv__ma_nv',
            'ma_nv__ho_ten'
        ).annotate(
            on_time=Count('id', filter=Q(trang_thai=ChamCong.TrangThai.DUNG_GIO)),
            late=Count('id', filter=Q(trang_thai__in=[ChamCong.TrangThai.DI_TRE, ChamCong.TrangThai.DI_TRE_NANG])),
            absent=Count('id', filter=Q(trang_thai=ChamCong.TrangThai.VANG)),
            unrecorded=Count('id', filter=Q(trang_thai=ChamCong.TrangThai.CHUA_CHAM))
        ).order_by('ma_nv__ma_nv')

        data = []
        for item in qs:
            data.append({
                'staff_id': item['ma_nv__ma_nv'],
                'staff_name': item['ma_nv__ho_ten'],
                'on_time_days': item['on_time'],
                'late_days': item['late'],
                'absent_days': item['absent'],
                'unrecorded_days': item['unrecorded']
            })

        return Response({'success': True, 'data': data})


class TopCustomersReportView(APIView):
    """
    GET /api/reports/customers/top/?thang=4&nam=2026
    Returns: Top 10 khách hàng theo doanh thu
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsQuanLy]

    def get(self, request):
        thang = request.query_params.get('thang')
        nam = request.query_params.get('nam')

        if not thang or not nam:
            return Response({'success': False, 'message': 'Thiếu tham số thang hoặc nam.'}, status=400)

        qs = HoaDon.objects.filter(
            trang_thai=HoaDon.TrangThai.HOAN_TAT,
            ngay_lap__year=nam,
            ngay_lap__month=thang,
            sdt_khach__isnull=False
        ).values(
            'sdt_khach__sdt_khach',
            'sdt_khach__ho_ten',
            'sdt_khach__hang_tv'
        ).annotate(
            total_spent=Sum('tong_tien'),
            invoice_count=Count('ma_hd')
        ).order_by('-total_spent')[:10]

        data = []
        for item in qs:
            data.append({
                'phone': item['sdt_khach__sdt_khach'],
                'name': item['sdt_khach__ho_ten'],
                'membership_tier': item['sdt_khach__hang_tv'],
                'total_spent': item['total_spent'] or 0,
                'invoice_count': item['invoice_count'] or 0
            })

        return Response({'success': True, 'data': data})
