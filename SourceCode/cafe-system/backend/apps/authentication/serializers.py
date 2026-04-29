"""
Serializers cho module Authentication.
Không dùng Django User — hoạt động trực tiếp với model TaiKhoan.
"""
from rest_framework import serializers
from .models import TaiKhoan


class LoginSerializer(serializers.Serializer):
    """Serialize và validate dữ liệu đăng nhập."""

    ten_dang_nhap = serializers.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': 'Vui lòng nhập tên đăng nhập.',
            'blank': 'Tên đăng nhập không được để trống.',
        }
    )
    mat_khau = serializers.CharField(
        required=True,
        write_only=True,           # Không bao giờ trả về mật khẩu
        style={'input_type': 'password'},
        error_messages={
            'required': 'Vui lòng nhập mật khẩu.',
            'blank': 'Mật khẩu không được để trống.',
        }
    )

    def validate_ten_dang_nhap(self, value):
        return value.strip().lower()


class TaiKhoanSerializer(serializers.ModelSerializer):
    """Serialize thông tin tài khoản (đọc — không expose mật khẩu)."""

    phan_quyen_display = serializers.CharField(
        source='get_ma_phan_quyen_display',
        read_only=True
    )

    class Meta:
        model = TaiKhoan
        fields = (
            'ma_tk',
            'ten_dang_nhap',
            'ma_phan_quyen',
            'phan_quyen_display',
            'is_active',
            'ngay_tao',
        )
        read_only_fields = fields  # Serializer này chỉ dùng để đọc


class DoiMatKhauSerializer(serializers.Serializer):
    """Validate dữ liệu đổi mật khẩu."""

    mat_khau_cu = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    mat_khau_moi = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'min_length': 'Mật khẩu mới phải có ít nhất 8 ký tự.',
        }
    )
    xac_nhan_mat_khau = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if data['mat_khau_moi'] != data['xac_nhan_mat_khau']:
            raise serializers.ValidationError({
                'xac_nhan_mat_khau': 'Mật khẩu xác nhận không khớp.'
            })
        return data
