from django.contrib import admin
from .models import KhuyenMai


@admin.register(KhuyenMai)
class KhuyenMaiAdmin(admin.ModelAdmin):
    list_display = (
        'ma_km', 'ten_chuong_trinh',
        'phan_tram_giam', 'dieu_kien_toi_thieu',
        'ngay_bd', 'ngay_kt', 'is_active'
    )
    list_filter = ('is_active',)
    search_fields = ('ten_chuong_trinh',)
    ordering = ('-ngay_bd',)
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')
    date_hierarchy = 'ngay_bd'
