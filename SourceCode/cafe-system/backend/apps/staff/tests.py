"""
Unit tests cho module Staff & Chấm công.
"""
from datetime import timedelta, time
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.staff.models import NhanVien, CaLam, ChamCong


class StaffTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Users
        self.tk_ql = TaiKhoan.objects.create(ten_dang_nhap='quanly', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.QUAN_LY)
        self.nv_ql = NhanVien.objects.create(ho_ten='QL Test', sdt='0900', ma_tk=self.tk_ql)

        self.tk_nv = TaiKhoan.objects.create(ten_dang_nhap='nhanvien', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN)
        self.nv = NhanVien.objects.create(ho_ten='NV Test', sdt='0901', ma_tk=self.tk_nv)

        # Token nhân viên
        from apps.authentication.views import _make_tokens
        self.nv_token = _make_tokens(self.tk_nv)['access']

        # Ca làm hôm nay cho nhân viên
        self.today = timezone.localtime().date()
        
    def _create_shift(self, start_hour, start_minute):
        return CaLam.objects.create(
            ma_nv=self.nv,
            ngay_lam=self.today,
            gio_bat_dau=time(start_hour, start_minute),
            gio_ket_thuc=time((start_hour + 4) % 24, start_minute)
        )

    def test_checkin_on_time(self):
        """Test check-in đúng giờ (Sớm hơn hoặc trễ <= 0 phút)"""
        now = timezone.localtime()
        # Tạo ca làm bắt đầu sau thời điểm hiện tại 5 phút (tức là đi làm sớm 5 phút)
        shift_start = (now + timedelta(minutes=5)).time()
        self._create_shift(shift_start.hour, shift_start.minute)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.nv_token)
        res = self.client.post('/api/attendance/checkin/')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['trang_thai'], 'Đúng giờ')

    def test_checkin_late(self):
        """Test check-in trễ (1-15 phút)"""
        now = timezone.localtime()
        # Ca làm bắt đầu trước thời điểm hiện tại 10 phút (tức là đi trễ 10 phút)
        shift_start = (now - timedelta(minutes=10)).time()
        self._create_shift(shift_start.hour, shift_start.minute)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.nv_token)
        res = self.client.post('/api/attendance/checkin/')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['trang_thai'], 'Đi trễ')

    def test_checkin_severely_late(self):
        """Test check-in trễ nặng (> 15 phút)"""
        now = timezone.localtime()
        # Ca làm bắt đầu trước thời điểm hiện tại 30 phút (trễ 30 phút)
        shift_start = (now - timedelta(minutes=30)).time()
        self._create_shift(shift_start.hour, shift_start.minute)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.nv_token)
        res = self.client.post('/api/attendance/checkin/')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['trang_thai'], 'Đi trễ nặng')

    def test_checkout(self):
        """Test luồng checkout"""
        now = timezone.localtime()
        shift_start = (now - timedelta(hours=1)).time()
        ca = self._create_shift(shift_start.hour, shift_start.minute)
        
        # Fake đã checkin
        ChamCong.objects.create(ma_ca=ca, ma_nv=self.nv, gio_vao_thuc=now.time(), trang_thai='Đúng giờ')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.nv_token)
        res = self.client.post('/api/attendance/checkout/')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['data']['gio_ra_thuc'])
