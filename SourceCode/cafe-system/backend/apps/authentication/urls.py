"""
URL patterns cho app Authentication.
"""
from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    MeView,
    DoiMatKhauView,
)

app_name = 'authentication'

urlpatterns = [
    # Đăng nhập — POST { ten_dang_nhap, mat_khau }
    path('login/', LoginView.as_view(), name='login'),

    # Đăng xuất — POST { refresh_token } (Header: Bearer <access>)
    path('logout/', LogoutView.as_view(), name='logout'),

    # Refresh access token — POST { refresh_token }
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),

    # Thông tin tài khoản hiện tại — GET (Header: Bearer <access>)
    path('me/', MeView.as_view(), name='me'),

    # Đổi mật khẩu — POST { mat_khau_cu, mat_khau_moi, xac_nhan_mat_khau }
    path('doi-mat-khau/', DoiMatKhauView.as_view(), name='doi-mat-khau'),
]
