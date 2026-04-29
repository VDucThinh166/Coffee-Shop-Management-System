"""
Unit tests cho module Inventory (Kho hàng).
Chạy: python manage.py test apps.inventory --settings=config.settings_dev
"""
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.staff.models import NhanVien
from apps.inventory.models import TonKho, PhieuNhap, ChiTietPhieuNhap


class InventoryTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Tài khoản Quản lý
        self.tk_quan_ly = TaiKhoan.objects.create(
            ten_dang_nhap='quanly', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.QUAN_LY
        )
        self.tk_nhan_vien = TaiKhoan.objects.create(
            ten_dang_nhap='nhanvien', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN
        )

        self.nv = NhanVien.objects.create(
            ho_ten='NV Test', sdt='0123456789', ma_tk=self.tk_quan_ly
        )

        # Tạo nguyên liệu
        self.nl1 = TonKho.objects.create(
            ten_nl='Cà phê hạt', don_vi_tinh='kg', so_luong_ton=10, nguong_bao_dong=2
        )
        self.nl2 = TonKho.objects.create(
            ten_nl='Sữa tươi', don_vi_tinh='lít', so_luong_ton=1, nguong_bao_dong=5 # < báo động
        )

    def _authenticate(self, user):
        from apps.authentication.views import _make_tokens
        tokens = _make_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    # -----------------------------------------------------------------------
    # Tồn kho & Alerts
    # -----------------------------------------------------------------------
    def test_ton_kho_alerts(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/inventory/alerts/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Chỉ có nl2 là dưới ngưỡng báo động
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['data'][0]['ma_nl'], self.nl2.ma_nl)

    def test_create_ton_kho(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/inventory/', {
            'ten_nl': 'Đường', 'don_vi_tinh': 'kg', 'nguong_bao_dong': 10
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['so_luong_ton'], '0.000') # Mặc định 0

    # -----------------------------------------------------------------------
    # Nhập Kho Transaction
    # -----------------------------------------------------------------------
    def test_import_inventory_success(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/inventory/import/', {
            'ngay_nhap': '2023-10-10',
            'chi_tiet': [
                {'ma_nl': self.nl1.ma_nl, 'sl_nhap': 5, 'don_gia_nhap': 100000},
                {'ma_nl': self.nl2.ma_nl, 'sl_nhap': 10, 'don_gia_nhap': 20000}
            ]
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # Verify database changes
        self.nl1.refresh_from_db()
        self.nl2.refresh_from_db()
        self.assertEqual(self.nl1.so_luong_ton, Decimal('15.000')) # 10 + 5
        self.assertEqual(self.nl2.so_luong_ton, Decimal('11.000')) # 1 + 10

        # Verify PhieuNhap
        phieu = PhieuNhap.objects.first()
        self.assertIsNotNone(phieu)
        # 5*100000 + 10*20000 = 700000
        self.assertEqual(phieu.tong_gia_tri, Decimal('700000'))
        self.assertEqual(phieu.chi_tiet.count(), 2)

    def test_import_inventory_missing_material(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/inventory/import/', {
            'ngay_nhap': '2023-10-10',
            'chi_tiet': [
                {'ma_nl': 999, 'sl_nhap': 5, 'don_gia_nhap': 100000}
            ]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(PhieuNhap.objects.count(), 0) # Không tạo phiếu

    def test_import_inventory_invalid_data(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/inventory/import/', {
            'ngay_nhap': '2023-10-10',
            'chi_tiet': [
                {'ma_nl': self.nl1.ma_nl, 'sl_nhap': -5, 'don_gia_nhap': 100000} # SL âm
            ]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PhieuNhap.objects.count(), 0)

    def test_staff_forbidden(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.get('/api/inventory/alerts/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
