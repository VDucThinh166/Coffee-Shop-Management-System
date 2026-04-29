"""
Unit tests cho module Promotions (Khuyến mãi).
Chạy: python manage.py test apps.promotions --settings=config.settings_dev
"""
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.promotions.models import KhuyenMai


class PromotionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Tài khoản Quản lý
        self.tk_quan_ly = TaiKhoan.objects.create(
            ten_dang_nhap='quanly', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.QUAN_LY
        )

        today = timezone.localtime().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Voucher đang active
        self.km1 = KhuyenMai.objects.create(
            ten_chuong_trinh='Giảm 10%', ngay_bd=yesterday, ngay_kt=tomorrow,
            phan_tram_giam=10, dieu_kien_toi_thieu=0, is_active=True
        )
        
        # Voucher hết hạn
        self.km2 = KhuyenMai.objects.create(
            ten_chuong_trinh='Giảm 20%', ngay_bd=yesterday, ngay_kt=yesterday,
            phan_tram_giam=20, dieu_kien_toi_thieu=50000, is_active=True
        )

        # Voucher chưa tới
        self.km3 = KhuyenMai.objects.create(
            ten_chuong_trinh='Giảm 30%', ngay_bd=tomorrow, ngay_kt=tomorrow + timedelta(days=1),
            phan_tram_giam=30, dieu_kien_toi_thieu=100000, is_active=True
        )

    def _authenticate(self, user):
        from apps.authentication.views import _make_tokens
        tokens = _make_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    def test_list_active_promotions(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/promotions/active/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Chỉ có km1 có hiệu lực trong hôm nay
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['data'][0]['ma_km'], self.km1.ma_km)

    def test_create_promotion_validation_dates(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/promotions/', {
            'ten_chuong_trinh': 'Lỗi ngày',
            'ngay_bd': '2024-12-31',
            'ngay_kt': '2024-12-01', # Ngày kết thúc < bắt đầu
            'phan_tram_giam': 15,
            'dieu_kien_toi_thieu': 0
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ngay_kt', res.data['errors'])

    def test_create_promotion_validation_percent(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/promotions/', {
            'ten_chuong_trinh': 'Lỗi phần trăm',
            'ngay_bd': '2024-12-01',
            'ngay_kt': '2024-12-31',
            'phan_tram_giam': 105, # > 100
            'dieu_kien_toi_thieu': 0
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phan_tram_giam', res.data['errors'])

    def test_delete_promotion(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.delete(f'/api/promotions/{self.km3.ma_km}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Chắc chắn đã xóa hoặc vô hiệu hóa
        self.assertEqual(KhuyenMai.objects.filter(pk=self.km3.ma_km).count(), 0)
