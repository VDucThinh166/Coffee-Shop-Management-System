"""
URL patterns cho app Tables (Bàn).

Mapping:
    GET  /api/tables/                  → Danh sách tất cả bàn
    POST /api/tables/                  → Thêm bàn (Quản lý)
    GET  /api/tables/<ma_ban>/         → Chi tiết 1 bàn
    DELETE /api/tables/<ma_ban>/       → Xóa bàn (Quản lý)
    PATCH /api/tables/<ma_ban>/status/ → Cập nhật trạng thái bàn
    POST /api/tables/transfer/         → Chuyển bàn
    POST /api/tables/merge/            → Gộp bàn
"""
from django.urls import path
from .views import (
    BanListCreateView,
    BanDetailView,
    CapNhatTrangThaiBanView,
    ChuyenBanView,
    GopBanView,
)

app_name = 'tables'

urlpatterns = [
    # Danh sách bàn + thêm bàn
    path('', BanListCreateView.as_view(), name='ban-list-create'),

    # Chuyển bàn — đặt TRƯỚC <ma_ban>/ để Django không nhầm 'transfer' là int
    path('transfer/', ChuyenBanView.as_view(), name='ban-transfer'),

    # Gộp bàn
    path('merge/', GopBanView.as_view(), name='ban-merge'),

    # Chi tiết & xóa bàn
    path('<int:ma_ban>/', BanDetailView.as_view(), name='ban-detail'),

    # Cập nhật trạng thái bàn
    path('<int:ma_ban>/status/', CapNhatTrangThaiBanView.as_view(), name='ban-status'),
]
