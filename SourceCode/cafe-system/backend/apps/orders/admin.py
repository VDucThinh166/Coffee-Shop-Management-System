from django.contrib import admin
from .models import HoaDon, ChiTietHoaDon


class ChiTietHoaDonInline(admin.TabularInline):
    model = ChiTietHoaDon
    extra = 1
    fields = ('ma_mon', 'so_luong', 'gia_ban', 'ghi_chu')
    readonly_fields = ()


@admin.register(HoaDon)
class HoaDonAdmin(admin.ModelAdmin):
    list_display = (
        'ma_hd', 'ngay_lap', 'ma_nv', 'ma_ban',
        'sdt_khach', 'tong_tien', 'phuong_thuc', 'trang_thai'
    )
    list_filter = ('trang_thai', 'phuong_thuc', 'ngay_lap')
    search_fields = ('ma_hd', 'ma_nv__ho_ten', 'sdt_khach__ho_ten')
    ordering = ('-ngay_lap',)
    date_hierarchy = 'ngay_lap'
    readonly_fields = ('ngay_lap', 'ngay_cap_nhat')
    inlines = [ChiTietHoaDonInline]

    fieldsets = (
        ('Thông tin hóa đơn', {
            'fields': ('ma_nv', 'ma_ban', 'sdt_khach', 'ma_km')
        }),
        ('Thanh toán', {
            'fields': ('tong_tien', 'phuong_thuc', 'trang_thai')
        }),
        ('Thời gian', {
            'fields': ('ngay_lap', 'ngay_cap_nhat'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChiTietHoaDon)
class ChiTietHoaDonAdmin(admin.ModelAdmin):
    list_display = ('id', 'ma_hd', 'ma_mon', 'so_luong', 'gia_ban', 'ghi_chu')
    search_fields = ('ma_hd__ma_hd', 'ma_mon__ten_mon')
    ordering = ('ma_hd',)
