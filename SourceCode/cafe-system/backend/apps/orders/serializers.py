"""
Serializers cho module Orders (Hóa đơn).
"""
from rest_framework import serializers
from .models import HoaDon, ChiTietHoaDon


class ChiTietHoaDonSerializer(serializers.ModelSerializer):
    ten_mon = serializers.CharField(source='ma_mon.ten_mon', read_only=True)
    thanh_tien = serializers.DecimalField(
        max_digits=14, decimal_places=0, read_only=True
    )

    class Meta:
        model = ChiTietHoaDon
        fields = ('id', 'ma_mon', 'ten_mon', 'so_luong', 'gia_ban', 'ghi_chu', 'thanh_tien')
        read_only_fields = ('id', 'gia_ban', 'thanh_tien')


class HoaDonSerializer(serializers.ModelSerializer):
    nhan_vien_lap = serializers.CharField(source='ma_nv.ho_ten', read_only=True)
    ten_khach_hang = serializers.CharField(source='sdt_khach.ho_ten', read_only=True)
    hang_khach_hang = serializers.CharField(source='sdt_khach.hang_tv', read_only=True, default=None)
    chi_tiet = ChiTietHoaDonSerializer(many=True, read_only=True)
    trang_thai_ban = serializers.IntegerField(source='ma_ban.trang_thai', read_only=True)

    class Meta:
        model = HoaDon
        fields = (
            'ma_hd',
            'ngay_lap',
            'ma_nv',
            'nhan_vien_lap',
            'ma_ban',
            'trang_thai_ban',
            'sdt_khach',
            'ten_khach_hang',
            'hang_khach_hang',
            'tong_tien',
            'phuong_thuc',
            'trang_thai',
            'ma_km',
            'ngay_cap_nhat',
            'chi_tiet'
        )
        read_only_fields = ('ma_hd', 'ngay_lap', 'ma_nv', 'tong_tien', 'trang_thai', 'ngay_cap_nhat')


class HoaDonCreateSerializer(serializers.Serializer):
    """Serializer nhận dữ liệu đầu vào khi tạo hóa đơn mới"""
    ma_ban = serializers.IntegerField(required=True)
    sdt_khach = serializers.CharField(max_length=11, required=False, allow_null=True, allow_blank=True)


class ChiTietAddSerializer(serializers.Serializer):
    """Serializer dùng để add thêm món vào hóa đơn đang mở"""
    ma_mon = serializers.IntegerField(required=True)
    so_luong = serializers.IntegerField(required=True, min_value=1)
    ghi_chu = serializers.CharField(max_length=255, required=False, allow_blank=True)


class ThanhToanSerializer(serializers.Serializer):
    """Serializer cho request thanh toán hóa đơn"""
    phuong_thuc = serializers.ChoiceField(choices=HoaDon.PhuongThucThanhToan.choices)
    promotion_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
