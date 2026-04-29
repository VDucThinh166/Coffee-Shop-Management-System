"""
JWT Middleware — bổ sung lớp bảo vệ cấp Django middleware.

Lưu ý kiến trúc:
- PRIMARY guard: DRF's authentication_classes (CustomJWTAuthentication)
  → xử lý 401 / InvalidToken cho mọi API view
- SECONDARY guard (middleware này): reject ngay ở tầng WSGI nếu
  request đến các path được bảo vệ mà không có Authorization header.

Middleware này KHÔNG thay thế DRF authentication — nó là "fail-fast"
trước khi request chạm đến view layer.
"""
import logging
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)

# Các path PUBLIC — không cần JWT
PUBLIC_PATHS = (
    '/api/auth/login/',
    '/api/token/',
    '/api/token/refresh/',
    '/api/token/verify/',
    '/api/menu/',  # Public GET, DRF will secure POST/PUT/DELETE
    '/api/docs/',
    '/api/redoc/',
    '/api/schema/',
    '/admin/',
    '/static/',
    '/media/',
    '/__debug__/',
)


def _is_public(path: str) -> bool:
    """Kiểm tra xem path có nằm trong danh sách public không."""
    return any(path.startswith(p) for p in PUBLIC_PATHS)


class JWTAuthMiddleware:
    """
    Django middleware kiểm tra Authorization header cho mọi request
    đến /api/ (trừ PUBLIC_PATHS).

    Trả về 401 JSON nếu:
    - Không có header Authorization
    - Token không hợp lệ / hết hạn
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # Bỏ qua các path public và path không thuộc API
        if not path.startswith('/api/') or _is_public(path):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return JsonResponse(
                {
                    'detail': 'Xác thực thất bại. Vui lòng đăng nhập.',
                    'code': 'not_authenticated',
                },
                status=401
            )

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return JsonResponse(
                {
                    'detail': 'Định dạng Authorization header không hợp lệ. '
                              'Dùng: "Bearer <token>"',
                    'code': 'bad_authorization_header',
                },
                status=401
            )

        raw_token = parts[1]

        try:
            AccessToken(raw_token)          # Validate token (chữ ký + thời hạn)
        except TokenError as exc:
            logger.debug("JWT middleware: token không hợp lệ — %s", exc)
            return JsonResponse(
                {
                    'detail': 'Token không hợp lệ hoặc đã hết hạn.',
                    'code': 'token_invalid',
                },
                status=401
            )

        return self.get_response(request)
