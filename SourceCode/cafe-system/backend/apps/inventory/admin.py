from django.contrib import admin
from .models import TonKho, PhieuNhap, ChiTietPhieuNhap


@admin.register(TonKho)
class TonKhoAdmin(admin.ModelAdmin):
    list_display = (
        'ma_nl', 'ten_nl', 'so_luong_ton',
        'don_vi_tinh', 'nguong_bao_dong', 'bao_dong_flag'
    )
    search_fields = ('ten_nl',)
    ordering = ('ten_nl',)

    @admin.display(description='Báo động?', boolean=True)
    def bao_dong_flag(self, obj):
        return obj.can_bao_dong


class ChiTietPhieuNhapInline(admin.TabularInline):
    model = ChiTietPhieuNhap
    extra = 1
    fields = ('ma_nl', 'sl_nhap', 'don_gia_nhap')


@admin.register(PhieuNhap)
class PhieuNhapAdmin(admin.ModelAdmin):
    list_display = ('ma_phieu', 'ngay_nhap', 'ma_nv', 'tong_gia_tri', 'ngay_tao')
    list_filter = ('ngay_nhap',)
    search_fields = ('ma_nv__ho_ten',)
    ordering = ('-ngay_nhap',)
    date_hierarchy = 'ngay_nhap'
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')
    inlines = [ChiTietPhieuNhapInline]


@admin.register(ChiTietPhieuNhap)
class ChiTietPhieuNhapAdmin(admin.ModelAdmin):
    list_display = ('id', 'ma_phieu', 'ma_nl', 'sl_nhap', 'don_gia_nhap')
    search_fields = ('ma_nl__ten_nl',)
