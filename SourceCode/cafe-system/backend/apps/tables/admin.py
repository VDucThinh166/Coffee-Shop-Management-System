from django.contrib import admin
from .models import Ban


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ('ma_ban', 'ten_khu_vuc', 'get_trang_thai', 'ngay_cap_nhat')
    list_filter = ('trang_thai',)
    search_fields = ('ten_khu_vuc',)
    ordering = ('ten_khu_vuc', 'ma_ban')

    @admin.display(description='Trạng thái')
    def get_trang_thai(self, obj):
        return obj.get_trang_thai_display()
