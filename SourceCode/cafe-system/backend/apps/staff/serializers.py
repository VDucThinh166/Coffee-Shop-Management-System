"""
Serializers cho module Staff (Nhân sự & Chấm công).
"""
from rest_framework import serializers
from .models import NhanVien, CaLam, ChamCong


class NhanVienSerializer(serializers.ModelSerializer):
    class Meta:
        model = NhanVien
        fields = '__all__'
        read_only_fields = ('ma_nv', 'ngay_tao', 'ngay_cap_nhat')


class CaLamSerializer(serializers.ModelSerializer):
    nhan_vien_ten = serializers.CharField(
        source='ma_nv.ho_ten',
        read_only=True
    )

    class Meta:
        model = CaLam
        fields = (
            'ma_ca',
            'ma_nv',
            'nhan_vien_ten',
            'ngay_lam',
            'gio_bat_dau',
            'gio_ket_thuc',
            'ngay_tao'
        )
        read_only_fields = ('ma_ca', 'ngay_tao')


class ChamCongSerializer(serializers.ModelSerializer):
    nhan_vien_ten = serializers.CharField(
        source='ma_nv.ho_ten',
        read_only=True
    )
    ca_lam_thong_tin = serializers.SerializerMethodField()

    class Meta:
        model = ChamCong
        fields = (
            'id',
            'ma_ca',
            'ca_lam_thong_tin',
            'ma_nv',
            'nhan_vien_ten',
            'gio_vao_thuc',
            'gio_ra_thuc',
            'trang_thai',
            'ghi_chu',
            'ngay_tao',
            'ngay_cap_nhat'
        )
        read_only_fields = ('id', 'ngay_tao', 'ngay_cap_nhat')

    def get_ca_lam_thong_tin(self, obj):
        return f"{obj.ma_ca.ngay_lam} {obj.ma_ca.gio_bat_dau}-{obj.ma_ca.gio_ket_thuc}"
