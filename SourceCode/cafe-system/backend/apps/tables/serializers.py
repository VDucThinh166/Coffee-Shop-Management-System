"""
Serializers cho module Tables (Bàn).
"""
from rest_framework import serializers
from .models import Ban


class BanSerializer(serializers.ModelSerializer):
    """
    Serializer đầy đủ cho model Ban.
    Thêm trang_thai_display để frontend không cần map số → chữ.
    """

    trang_thai_display = serializers.CharField(
        source='get_trang_thai_display',
        read_only=True,
        help_text='Nhãn trạng thái dạng text: Trống / Có khách / Đang dọn'
    )

    class Meta:
        model = Ban
        fields = (
            'ma_ban',
            'ten_khu_vuc',
            'trang_thai',
            'trang_thai_display',
            'ngay_cap_nhat',
        )
        read_only_fields = ('ma_ban', 'trang_thai_display', 'ngay_cap_nhat')


class TaoBanSerializer(serializers.ModelSerializer):
    """Serializer dùng khi Quản lý thêm bàn mới."""

    class Meta:
        model = Ban
        fields = ('ten_khu_vuc', 'trang_thai')
        extra_kwargs = {
            'trang_thai': {'required': False},
        }

    def validate_ten_khu_vuc(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Tên/khu vực không được để trống.')
        return value


class CapNhatTrangThaiSerializer(serializers.Serializer):
    """Validate body khi cập nhật trạng thái bàn."""

    trang_thai = serializers.ChoiceField(
        choices=Ban.TrangThai.choices,
        error_messages={
            'invalid_choice': (
                'Trạng thái không hợp lệ. Chọn: '
                '0 (Trống), 1 (Có khách), 2 (Đang dọn).'
            )
        }
    )


class ChuyenBanSerializer(serializers.Serializer):
    """Validate body khi chuyển bàn."""

    tu_ban = serializers.IntegerField(
        min_value=1,
        error_messages={
            'required': 'Vui lòng cung cấp mã bàn nguồn (tu_ban).',
            'min_value': 'Mã bàn phải là số dương.',
        }
    )
    den_ban = serializers.IntegerField(
        min_value=1,
        error_messages={
            'required': 'Vui lòng cung cấp mã bàn đích (den_ban).',
            'min_value': 'Mã bàn phải là số dương.',
        }
    )

    def validate(self, data):
        if data['tu_ban'] == data['den_ban']:
            raise serializers.ValidationError(
                'Bàn nguồn và bàn đích không được trùng nhau.'
            )
        return data


class GopBanSerializer(serializers.Serializer):
    """Validate body khi gộp bàn."""

    ban_chinh = serializers.IntegerField(
        min_value=1,
        error_messages={'required': 'Vui lòng cung cấp mã bàn chính (ban_chinh).'}
    )
    ban_phu = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        error_messages={
            'required': 'Vui lòng cung cấp danh sách bàn phụ (ban_phu).',
            'min_length': 'Phải có ít nhất 1 bàn phụ để gộp.',
        }
    )

    def validate(self, data):
        ban_chinh = data['ban_chinh']
        ban_phu_list = data['ban_phu']

        # Không cho bàn chính nằm trong danh sách bàn phụ
        if ban_chinh in ban_phu_list:
            raise serializers.ValidationError(
                'Bàn chính không được nằm trong danh sách bàn phụ.'
            )

        # Không cho trùng trong danh sách bàn phụ
        if len(ban_phu_list) != len(set(ban_phu_list)):
            raise serializers.ValidationError(
                'Danh sách bàn phụ không được chứa bàn trùng nhau.'
            )

        return data
