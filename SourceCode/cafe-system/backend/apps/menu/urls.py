"""
URL patterns cho app Menu (Thực đơn).
"""
from django.urls import path
from .views import (
    ThucDonListCreateView,
    ThucDonDetailView,
    CapNhatTrangThaiThucDonView,
)

app_name = 'menu'

urlpatterns = [
    # Danh sách món + thêm món (GET public, POST quản lý)
    path('', ThucDonListCreateView.as_view(), name='menu-list-create'),

    # Chi tiết, sửa, xóa món
    path('<int:ma_mon>/', ThucDonDetailView.as_view(), name='menu-detail'),

    # Cập nhật trạng thái
    path('<int:ma_mon>/status/', CapNhatTrangThaiThucDonView.as_view(), name='menu-status'),
]
