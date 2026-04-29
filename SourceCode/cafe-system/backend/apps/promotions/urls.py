"""
URL patterns cho app Promotions (Khuyến mãi).
"""
from django.urls import path
from .views import (
    KhuyenMaiListCreateView,
    KhuyenMaiDetailView,
    ActivePromotionsView
)

app_name = 'promotions'

urlpatterns = [
    path('', KhuyenMaiListCreateView.as_view(), name='promotion-list-create'),
    path('active/', ActivePromotionsView.as_view(), name='promotion-active'),
    path('<int:ma_km>/', KhuyenMaiDetailView.as_view(), name='promotion-detail'),
]
