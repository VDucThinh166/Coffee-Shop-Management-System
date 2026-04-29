"""
URL patterns cho app Orders.
"""
from django.urls import path
from .views import (
    HoaDonListCreateView,
    HoaDonDetailView,
    HuyHoaDonView,
    ChiTietHoaDonView,
    ThanhToanView
)

app_name = 'orders'

urlpatterns = [
    path('', HoaDonListCreateView.as_view(), name='order-list-create'),
    path('<int:ma_hd>/', HoaDonDetailView.as_view(), name='order-detail'),
    path('<int:ma_hd>/cancel/', HuyHoaDonView.as_view(), name='order-cancel'),
    path('<int:ma_hd>/items/', ChiTietHoaDonView.as_view(), name='order-items-add'),
    path('<int:ma_hd>/items/<int:item_id>/', ChiTietHoaDonView.as_view(), name='order-items-delete'),
    path('<int:ma_hd>/checkout/', ThanhToanView.as_view(), name='order-checkout'),
]
