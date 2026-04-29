from django.contrib import admin
from .models import TaiKhoan


@admin.register(TaiKhoan)
class TaiKhoanAdmin(admin.ModelAdmin):
    list_display = ('ma_tk', 'ten_dang_nhap', 'get_phan_quyen', 'is_active', 'ngay_tao')
    list_filter = ('ma_phan_quyen', 'is_active')
    search_fields = ('ten_dang_nhap',)
    ordering = ('ten_dang_nhap',)
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')

    fieldsets = (
        ('Thông tin đăng nhập', {
            'fields': ('ten_dang_nhap', 'mat_khau')
        }),
        ('Phân quyền', {
            'fields': ('ma_phan_quyen', 'is_active')
        }),
        ('Thời gian', {
            'fields': ('ngay_tao', 'ngay_cap_nhat'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Phân quyền')
    def get_phan_quyen(self, obj):
        return obj.get_ma_phan_quyen_display()
