"""
Serializers cho module Menu (Thực đơn).
"""
from rest_framework import serializers
from .models import ThucDon


class ThucDonSerializer(serializers.ModelSerializer):
    """
    Serializer đầy đủ cho model ThucDon.
    Trường hinh_anh sẽ tự động trả về full URL nếu request context có sẵn.
    """
    trang_thai_display = serializers.CharField(
        source='get_trang_thai_display',
        read_only=True
    )

    class Meta:
        model = ThucDon
        fields = (
            'ma_mon',
            'ten_mon',
            'ma_loai',
            'don_gia',
            'mo_ta',
            'hinh_anh',
            'trang_thai',
            'trang_thai_display',
            'ngay_tao',
            'ngay_cap_nhat',
        )
        read_only_fields = ('ma_mon', 'trang_thai_display', 'ngay_tao', 'ngay_cap_nhat')


class ThucDonStatusSerializer(serializers.Serializer):
    """
    Serializer cho việc cập nhật riêng trạng thái món (bật/tắt).
    """
    trang_thai = serializers.ChoiceField(
        choices=ThucDon.TrangThai.choices,
        error_messages={
            'invalid_choice': 'Trạng thái không hợp lệ. Chọn: 0 (Hết) hoặc 1 (Còn).'
        }
    )
