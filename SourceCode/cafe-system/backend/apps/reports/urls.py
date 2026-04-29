"""
URL patterns cho app Reports.
"""
from django.urls import path
from .views import (
    DailyRevenueReportView,
    MonthlyRevenueReportView,
    BestSellerReportView,
    StaffAttendanceReportView,
    TopCustomersReportView
)

app_name = 'reports'

urlpatterns = [
    path('revenue/daily/', DailyRevenueReportView.as_view(), name='report-daily-revenue'),
    path('revenue/monthly/', MonthlyRevenueReportView.as_view(), name='report-monthly-revenue'),
    path('bestseller/', BestSellerReportView.as_view(), name='report-bestseller'),
    path('staff/attendance/', StaffAttendanceReportView.as_view(), name='report-staff-attendance'),
    path('customers/top/', TopCustomersReportView.as_view(), name='report-top-customers'),
]
