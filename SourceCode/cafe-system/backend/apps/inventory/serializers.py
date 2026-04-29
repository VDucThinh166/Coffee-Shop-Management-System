"""
Serializers cho module Inventory (Kho hàng).
"""
from rest_framework import serializers
from .models import TonKho, PhieuNhap, ChiTietPhieuNhap


class TonKhoSerializer(serializers.ModelSerializer):
    can_bao_dong = serializers.BooleanField(read_only=True)

    class Meta:
        model = TonKho
        fields = (
            'ma_nl',
            'ten_nl',
            'so_luong_ton',
            'don_vi_tinh',
            'nguong_bao_dong',
            'can_bao_dong',
            'ngay_cap_nhat'
        )
        read_only_fields = ('ma_nl', 'so_luong_ton', 'can_bao_dong', 'ngay_cap_nhat')


class ChiTietPhieuNhapSerializer(serializers.ModelSerializer):
    ten_nl = serializers.CharField(source='ma_nl.ten_nl', read_only=True)
    thanh_tien = serializers.DecimalField(
        max_digits=14, decimal_places=0, read_only=True
    )

    class Meta:
        model = ChiTietPhieuNhap
        fields = ('ma_nl', 'ten_nl', 'sl_nhap', 'don_gia_nhap', 'thanh_tien')


class PhieuNhapSerializer(serializers.ModelSerializer):
    nhan_vien_nhap = serializers.CharField(source='ma_nv.ho_ten', read_only=True)
    chi_tiet = ChiTietPhieuNhapSerializer(many=True, read_only=True)

    class Meta:
        model = PhieuNhap
        fields = (
            'ma_phieu',
            'ngay_nhap',
            'ma_nv',
            'nhan_vien_nhap',
            'tong_gia_tri',
            'ngay_tao',
            'ngay_cap_nhat',
            'chi_tiet'
        )
        read_only_fields = ('ma_phieu', 'ma_nv', 'tong_gia_tri', 'ngay_tao', 'ngay_cap_nhat')


class NhapKhoSerializer(serializers.Serializer):
    """Serializer dùng để validate request POST nhập kho."""
    ngay_nhap = serializers.DateField(required=True)
    chi_tiet = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        error_messages={'min_length': 'Phiếu nhập phải có ít nhất 1 chi tiết.'}
    )

    def validate_chi_tiet(self, chi_tiet):
        # Kiểm tra từng chi tiết phải có ma_nl, sl_nhap, don_gia_nhap
        ma_nl_list = []
        for item in chi_tiet:
            if 'ma_nl' not in item or 'sl_nhap' not in item or 'don_gia_nhap' not in item:
                raise serializers.ValidationError('Mỗi chi tiết phải có đủ ma_nl, sl_nhap, don_gia_nhap.')
            
            try:
                sl_nhap = float(item['sl_nhap'])
                don_gia_nhap = float(item['don_gia_nhap'])
            except ValueError:
                raise serializers.ValidationError('Số lượng và đơn giá phải là số.')

            if sl_nhap <= 0 or don_gia_nhap < 0:
                raise serializers.ValidationError('Số lượng phải > 0 và đơn giá phải >= 0.')

            if item['ma_nl'] in ma_nl_list:
                raise serializers.ValidationError(f'Nguyên liệu mã {item["ma_nl"]} bị trùng lặp trong phiếu.')
            ma_nl_list.append(item['ma_nl'])

        return chi_tiet
