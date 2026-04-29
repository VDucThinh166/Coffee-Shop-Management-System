"""
Custom JWT Authentication backend.
Lookup TaiKhoan thay vì Django's default User model.
"""
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import TaiKhoan

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    """
    Override JWTAuthentication để dùng model TaiKhoan thay vì Django User.
    Đọc 'user_id' claim từ JWT token và trả về đối tượng TaiKhoan.
    """

    def get_user(self, validated_token):
        """
        Tìm TaiKhoan dựa trên 'user_id' claim trong token.
        Raises InvalidToken nếu không tìm thấy hoặc tài khoản bị vô hiệu.
        """
        try:
            ma_tk = validated_token['user_id']
        except KeyError:
            raise InvalidToken(
                'Token không chứa định danh người dùng (user_id).'
            )

        try:
            tai_khoan = TaiKhoan.objects.get(ma_tk=ma_tk)
        except TaiKhoan.DoesNotExist:
            logger.warning("JWT token chứa ma_tk=%s nhưng không tồn tại.", ma_tk)
            raise InvalidToken('Tài khoản không tồn tại.')

        if not tai_khoan.is_active:
            raise InvalidToken('Tài khoản đã bị vô hiệu hóa.')

        return tai_khoan
