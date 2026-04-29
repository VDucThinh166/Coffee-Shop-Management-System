"""
URL patterns cho app Inventory (Kho hàng).
"""
from django.urls import path
from .views import (
    TonKhoListCreateView,
    TonKhoDetailView,
    PhieuNhapListView,
    NhapKhoView,
    InventoryAlertView
)

app_name = 'inventory'

urlpatterns = [
    # Kho hàng (TonKho)
    path('', TonKhoListCreateView.as_view(), name='inventory-list-create'),
    path('alerts/', InventoryAlertView.as_view(), name='inventory-alerts'),
    path('<int:ma_nl>/', TonKhoDetailView.as_view(), name='inventory-detail'),

    # Nhập kho
    path('imports/', PhieuNhapListView.as_view(), name='inventory-imports'),
    path('import/', NhapKhoView.as_view(), name='inventory-import'),
]
