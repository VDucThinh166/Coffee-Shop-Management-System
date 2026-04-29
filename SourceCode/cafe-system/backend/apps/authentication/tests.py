"""
Unit tests cho module Authentication.
Chạy: python manage.py test apps.authentication --settings=config.settings_dev
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.authentication.views import hash_password, _verify_password
from apps.authentication.permissions import IsQuanLy, IsNhanVien, IsQuanLyOrNhanVien


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_tai_khoan(ten_dang_nhap='testuser', phan_quyen=2, mat_khau='Password@123'):
    return TaiKhoan.objects.create(
        ten_dang_nhap=ten_dang_nhap,
        mat_khau=hash_password(mat_khau),
        ma_phan_quyen=phan_quyen,
        is_active=True,
    )


# ---------------------------------------------------------------------------
# Tests: Bcrypt helpers
# ---------------------------------------------------------------------------

class BcryptHelperTests(TestCase):

    def test_hash_and_verify_correct_password(self):
        raw = 'SecurePass@456'
        hashed = hash_password(raw)
        self.assertTrue(_verify_password(raw, hashed))

    def test_verify_wrong_password_returns_false(self):
        hashed = hash_password('CorrectPass@123')
        self.assertFalse(_verify_password('WrongPass', hashed))

    def test_hash_is_different_each_call(self):
        """bcrypt salt — mỗi lần hash cho kết quả khác nhau."""
        raw = 'SamePassword@123'
        h1 = hash_password(raw)
        h2 = hash_password(raw)
        self.assertNotEqual(h1, h2)
        self.assertTrue(_verify_password(raw, h1))
        self.assertTrue(_verify_password(raw, h2))


# ---------------------------------------------------------------------------
# Tests: LoginView
# ---------------------------------------------------------------------------

class LoginViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/login/'
        self.password = 'TestPass@123'
        self.tai_khoan = make_tai_khoan(
            ten_dang_nhap='nhanvien01',
            phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN,
            mat_khau=self.password
        )

    def test_login_success(self):
        resp = self.client.post(self.url, {
            'ten_dang_nhap': 'nhanvien01',
            'mat_khau': self.password,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        self.assertIn('access_token', resp.data)
        self.assertIn('refresh_token', resp.data)
        self.assertEqual(resp.data['ma_phan_quyen'], TaiKhoan.PhanQuyen.NHAN_VIEN)

    def test_login_wrong_password(self):
        resp = self.client.post(self.url, {
            'ten_dang_nhap': 'nhanvien01',
            'mat_khau': 'WrongPassword',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.data['code'], 'invalid_credentials')

    def test_login_nonexistent_user(self):
        resp = self.client.post(self.url, {
            'ten_dang_nhap': 'khong_ton_tai',
            'mat_khau': 'AnyPassword',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.data['code'], 'invalid_credentials')

    def test_login_disabled_account(self):
        self.tai_khoan.is_active = False
        self.tai_khoan.save()
        resp = self.client.post(self.url, {
            'ten_dang_nhap': 'nhanvien01',
            'mat_khau': self.password,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp.data['code'], 'account_disabled')

    def test_login_missing_fields(self):
        resp = self.client.post(self.url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Tests: Custom Permissions
# ---------------------------------------------------------------------------

class PermissionTests(TestCase):

    def _make_request(self, phan_quyen):
        """Mock request với user TaiKhoan."""
        from unittest.mock import MagicMock
        tk = TaiKhoan(
            ma_phan_quyen=phan_quyen,
            is_active=True,
            ten_dang_nhap='test'
        )
        req = MagicMock()
        req.user = tk
        return req

    def test_is_quan_ly_allows_manager(self):
        perm = IsQuanLy()
        req = self._make_request(TaiKhoan.PhanQuyen.QUAN_LY)
        self.assertTrue(perm.has_permission(req, None))

    def test_is_quan_ly_denies_staff(self):
        perm = IsQuanLy()
        req = self._make_request(TaiKhoan.PhanQuyen.NHAN_VIEN)
        self.assertFalse(perm.has_permission(req, None))

    def test_is_nhan_vien_allows_staff(self):
        perm = IsNhanVien()
        req = self._make_request(TaiKhoan.PhanQuyen.NHAN_VIEN)
        self.assertTrue(perm.has_permission(req, None))

    def test_is_nhan_vien_denies_manager(self):
        perm = IsNhanVien()
        req = self._make_request(TaiKhoan.PhanQuyen.QUAN_LY)
        self.assertFalse(perm.has_permission(req, None))

    def test_is_quan_ly_or_nhan_vien_allows_both(self):
        perm = IsQuanLyOrNhanVien()
        for quyen in (TaiKhoan.PhanQuyen.QUAN_LY, TaiKhoan.PhanQuyen.NHAN_VIEN):
            req = self._make_request(quyen)
            self.assertTrue(perm.has_permission(req, None))
