from django.contrib import admin
from .models import ThucDon


@admin.register(ThucDon)
class ThucDonAdmin(admin.ModelAdmin):
    list_display = ('ma_mon', 'ten_mon', 'ma_loai', 'don_gia', 'get_trang_thai', 'ngay_cap_nhat')
    list_filter = ('trang_thai', 'ma_loai')
    search_fields = ('ten_mon', 'ma_loai')
    ordering = ('ma_loai', 'ten_mon')
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')

    fieldsets = (
        ('Thông tin món', {
            'fields': ('ten_mon', 'ma_loai', 'don_gia', 'mo_ta', 'hinh_anh')
        }),
        ('Trạng thái', {
            'fields': ('trang_thai',)
        }),
        ('Thời gian', {
            'fields': ('ngay_tao', 'ngay_cap_nhat'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Trạng thái')
    def get_trang_thai(self, obj):
        return obj.get_trang_thai_display()
