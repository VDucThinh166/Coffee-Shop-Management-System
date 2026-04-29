from django.contrib import admin
from .models import NhanVien, CaLam, ChamCong


class CaLamInline(admin.TabularInline):
    model = CaLam
    extra = 0
    fields = ('ngay_lam', 'gio_bat_dau', 'gio_ket_thuc')


@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    list_display = ('ma_nv', 'ho_ten', 'sdt', 'get_phan_quyen', 'is_active')
    list_filter = ('is_active', 'ma_tk__ma_phan_quyen')
    search_fields = ('ho_ten', 'sdt')
    ordering = ('ho_ten',)
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')
    inlines = [CaLamInline]

    @admin.display(description='Phân quyền')
    def get_phan_quyen(self, obj):
        if obj.ma_tk:
            return obj.ma_tk.get_ma_phan_quyen_display()
        return '—'


class ChamCongInline(admin.TabularInline):
    model = ChamCong
    extra = 0
    fields = ('ma_nv', 'gio_vao_thuc', 'gio_ra_thuc', 'trang_thai', 'ghi_chu')


@admin.register(CaLam)
class CaLamAdmin(admin.ModelAdmin):
    list_display = ('ma_ca', 'ma_nv', 'ngay_lam', 'gio_bat_dau', 'gio_ket_thuc')
    list_filter = ('ngay_lam',)
    search_fields = ('ma_nv__ho_ten',)
    ordering = ('-ngay_lam', 'gio_bat_dau')
    date_hierarchy = 'ngay_lam'
    inlines = [ChamCongInline]


@admin.register(ChamCong)
class ChamCongAdmin(admin.ModelAdmin):
    list_display = ('id', 'ma_nv', 'ma_ca', 'gio_vao_thuc', 'gio_ra_thuc', 'trang_thai')
    list_filter = ('trang_thai',)
    search_fields = ('ma_nv__ho_ten',)
    ordering = ('-ngay_tao',)
    readonly_fields = ('ngay_tao', 'ngay_cap_nhat')
