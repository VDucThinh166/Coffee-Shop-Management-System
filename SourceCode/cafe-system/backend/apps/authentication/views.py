"""
Views cho module Authentication.
Dùng DRF APIView, custom TaiKhoan model, bcrypt password hashing.
Không phụ thuộc vào Django's auth.User.
"""
import logging
import bcrypt
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .authentication import CustomJWTAuthentication
from .models import TaiKhoan
from .serializers import (
    LoginSerializer,
    TaiKhoanSerializer,
    DoiMatKhauSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tokens(tai_khoan: TaiKhoan) -> dict:
    """
    Tạo cặp access + refresh token cho TaiKhoan.
    Thêm các custom claims: ma_phan_quyen, ten_dang_nhap.
    """
    refresh = RefreshToken()

    # Ghi đè user_id claim — CustomJWTAuthentication sẽ dùng field này
    refresh['user_id'] = tai_khoan.ma_tk
    refresh['ma_phan_quyen'] = tai_khoan.ma_phan_quyen
    refresh['ten_dang_nhap'] = tai_khoan.ten_dang_nhap

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def _verify_password(raw_password: str, hashed: str) -> bool:
    """So sánh mật khẩu plain-text với bcrypt hash an toàn."""
    try:
        return bcrypt.checkpw(
            raw_password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Utility function (dùng khi tạo tài khoản / đổi mật khẩu)
# ---------------------------------------------------------------------------

def hash_password(raw_password: str) -> str:
    """
    Hash mật khẩu bằng bcrypt với cost factor 12.
    Gọi hàm này khi tạo hoặc đổi mật khẩu.

    Ví dụ:
        tai_khoan.mat_khau = hash_password('MatKhauMoi@123')
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class LoginView(APIView):
    """
    POST /api/auth/login/

    Body:
        { "ten_dang_nhap": "...", "mat_khau": "..." }

    Response 200:
        {
            "access_token": "...",
            "refresh_token": "...",
            "tai_khoan": {
                "ma_tk": 1,
                "ten_dang_nhap": "admin",
                "ma_phan_quyen": 1,
                "phan_quyen_display": "Quản lý"
            }
        }
    """
    authentication_classes = []     # Không yêu cầu token trước khi login
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'message': 'Dữ liệu không hợp lệ.',
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        ten_dang_nhap = serializer.validated_data['ten_dang_nhap']
        mat_khau = serializer.validated_data['mat_khau']

        # Tra cứu tài khoản
        try:
            tai_khoan = TaiKhoan.objects.get(ten_dang_nhap=ten_dang_nhap)
        except TaiKhoan.DoesNotExist:
            # Vẫn chạy _verify_password với dummy hash để tránh timing attack
            _verify_password(mat_khau, '$2b$12$dummyhashtopreventtimingattackX')
            logger.warning("Đăng nhập thất bại — tài khoản '%s' không tồn tại.", ten_dang_nhap)
            return Response(
                {
                    'success': False,
                    'message': 'Tên đăng nhập hoặc mật khẩu không đúng.',
                    'code': 'invalid_credentials',
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Kiểm tra tài khoản có hoạt động không
        if not tai_khoan.is_active:
            return Response(
                {
                    'success': False,
                    'message': 'Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ quản lý.',
                    'code': 'account_disabled',
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra mật khẩu (bcrypt)
        if not _verify_password(mat_khau, tai_khoan.mat_khau):
            logger.warning("Đăng nhập thất bại — sai mật khẩu cho tài khoản '%s'.", ten_dang_nhap)
            return Response(
                {
                    'success': False,
                    'message': 'Tên đăng nhập hoặc mật khẩu không đúng.',
                    'code': 'invalid_credentials',
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Tạo token
        tokens = _make_tokens(tai_khoan)

        logger.info("Đăng nhập thành công — tài khoản '%s'.", ten_dang_nhap)

        return Response(
            {
                'success': True,
                'message': 'Đăng nhập thành công.',
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
                'ma_phan_quyen': tai_khoan.ma_phan_quyen,
                'tai_khoan': TaiKhoanSerializer(tai_khoan).data,
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Header: Authorization: Bearer <access_token>
    Body:   { "refresh_token": "<refresh_token>" }

    Blacklist refresh token để vô hiệu hoá session.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token_str = request.data.get('refresh_token')

        if not refresh_token_str:
            return Response(
                {
                    'success': False,
                    'message': 'Vui lòng cung cấp refresh_token.',
                    'code': 'refresh_token_required',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()            # Yêu cầu rest_framework_simplejwt.token_blacklist trong INSTALLED_APPS
            logger.info("Đăng xuất — tài khoản '%s'.", request.user.ten_dang_nhap)
        except TokenError as exc:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh token không hợp lệ hoặc đã hết hạn.',
                    'code': 'token_invalid',
                    'detail': str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'success': True,
                'message': 'Đăng xuất thành công.',
            },
            status=status.HTTP_200_OK
        )


class RefreshTokenView(APIView):
    """
    POST /api/auth/refresh/

    Body: { "refresh_token": "<refresh_token>" }

    Trả về access token mới. Không cần access token hợp lệ trong header.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token_str = request.data.get('refresh_token')

        if not refresh_token_str:
            return Response(
                {
                    'success': False,
                    'message': 'Vui lòng cung cấp refresh_token.',
                    'code': 'refresh_token_required',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token_str)

            # Lấy thông tin từ payload để gắn vào access token mới
            ma_tk = refresh.get('user_id')
            ma_phan_quyen = refresh.get('ma_phan_quyen')
            ten_dang_nhap = refresh.get('ten_dang_nhap')

            # Tạo access token mới từ refresh token hiện tại
            new_access = refresh.access_token

            # Giữ nguyên custom claims
            new_access['user_id'] = ma_tk
            new_access['ma_phan_quyen'] = ma_phan_quyen
            new_access['ten_dang_nhap'] = ten_dang_nhap

        except TokenError as exc:
            return Response(
                {
                    'success': False,
                    'message': 'Refresh token không hợp lệ hoặc đã hết hạn.',
                    'code': 'token_invalid',
                    'detail': str(exc),
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {
                'success': True,
                'access_token': str(new_access),
            },
            status=status.HTTP_200_OK
        )


class MeView(APIView):
    """
    GET /api/auth/me/
    Trả về thông tin tài khoản đang đăng nhập.
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = TaiKhoanSerializer(request.user)
        return Response(
            {
                'success': True,
                'tai_khoan': serializer.data,
            },
            status=status.HTTP_200_OK
        )


class DoiMatKhauView(APIView):
    """
    POST /api/auth/doi-mat-khau/
    Đổi mật khẩu cho tài khoản đang đăng nhập.

    Body:
        {
            "mat_khau_cu": "...",
            "mat_khau_moi": "...",
            "xac_nhan_mat_khau": "..."
        }
    """
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DoiMatKhauSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'message': 'Dữ liệu không hợp lệ.',
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tai_khoan = request.user
        mat_khau_cu = serializer.validated_data['mat_khau_cu']
        mat_khau_moi = serializer.validated_data['mat_khau_moi']

        # Kiểm tra mật khẩu cũ
        if not _verify_password(mat_khau_cu, tai_khoan.mat_khau):
            return Response(
                {
                    'success': False,
                    'message': 'Mật khẩu hiện tại không đúng.',
                    'code': 'wrong_password',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Không cho đặt mật khẩu giống cũ
        if _verify_password(mat_khau_moi, tai_khoan.mat_khau):
            return Response(
                {
                    'success': False,
                    'message': 'Mật khẩu mới không được trùng mật khẩu hiện tại.',
                    'code': 'same_password',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tai_khoan.mat_khau = hash_password(mat_khau_moi)
        tai_khoan.save(update_fields=['mat_khau', 'ngay_cap_nhat'])

        logger.info("Đổi mật khẩu thành công — tài khoản '%s'.", tai_khoan.ten_dang_nhap)

        return Response(
            {
                'success': True,
                'message': 'Đổi mật khẩu thành công. Vui lòng đăng nhập lại.',
            },
            status=status.HTTP_200_OK
        )
