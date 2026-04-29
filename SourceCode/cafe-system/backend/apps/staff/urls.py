"""
URL patterns cho app Staff.
"""
from django.urls import path
from .views import (
    NhanVienListCreateView,
    NhanVienDetailView,
    CaLamListCreateView,
    CaLamDetailView,
    CheckInView,
    CheckOutView,
    ChamCongListView,
)

app_name = 'staff'

urlpatterns = [
    # Nhân viên
    path('staff/', NhanVienListCreateView.as_view(), name='staff-list-create'),
    path('staff/<int:pk>/', NhanVienDetailView.as_view(), name='staff-detail'),

    # Ca làm
    path('shifts/', CaLamListCreateView.as_view(), name='shift-list-create'),
    path('shifts/<int:pk>/', CaLamDetailView.as_view(), name='shift-detail'),

    # Chấm công
    path('attendance/', ChamCongListView.as_view(), name='attendance-list'),
    path('attendance/checkin/', CheckInView.as_view(), name='attendance-checkin'),
    path('attendance/checkout/', CheckOutView.as_view(), name='attendance-checkout'),
]
