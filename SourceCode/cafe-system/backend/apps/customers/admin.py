from django.contrib import admin
from .models import KhachHang


@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    list_display = ('sdt_khach', 'ho_ten', 'hang_tv', 'diem_tich_luy', 'ngay_tao')
    list_filter = ('hang_tv',)
    search_fields = ('sdt_khach', 'ho_ten')
    ordering = ('ho_ten',)
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')
