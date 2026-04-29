"""
Custom DRF Permission classes cho hệ thống phân quyền Cafe.
Hoạt động với model TaiKhoan (ma_phan_quyen: 1=Quản lý, 2=Nhân viên).
"""
from rest_framework.permissions import BasePermission
from .models import TaiKhoan


class IsQuanLy(BasePermission):
    """
    Chỉ cho phép tài khoản có ma_phan_quyen = 1 (Quản lý).
    """
    message = 'Bạn không có quyền truy cập. Chỉ dành cho Quản lý.'

    def has_permission(self, request, view):
        if not request.user or not isinstance(request.user, TaiKhoan):
            return False
        return (
            request.user.is_active
            and request.user.ma_phan_quyen == TaiKhoan.PhanQuyen.QUAN_LY
        )


class IsNhanVien(BasePermission):
    """
    Chỉ cho phép tài khoản có ma_phan_quyen = 2 (Nhân viên).
    """
    message = 'Bạn không có quyền truy cập. Chỉ dành cho Nhân viên.'

    def has_permission(self, request, view):
        if not request.user or not isinstance(request.user, TaiKhoan):
            return False
        return (
            request.user.is_active
            and request.user.ma_phan_quyen == TaiKhoan.PhanQuyen.NHAN_VIEN
        )


class IsQuanLyOrNhanVien(BasePermission):
    """
    Cho phép cả Quản lý lẫn Nhân viên — tức là bất kỳ tài khoản đã đăng nhập nào.
    """
    message = 'Bạn phải đăng nhập để thực hiện hành động này.'

    def has_permission(self, request, view):
        if not request.user or not isinstance(request.user, TaiKhoan):
            return False
        return request.user.is_active and request.user.ma_phan_quyen in (
            TaiKhoan.PhanQuyen.QUAN_LY,
            TaiKhoan.PhanQuyen.NHAN_VIEN,
        )
