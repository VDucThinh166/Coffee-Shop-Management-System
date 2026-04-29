"""
Unit tests cho module Orders.
Chạy: python manage.py test apps.orders --settings=config.settings_dev
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.staff.models import NhanVien
from apps.customers.models import KhachHang
from apps.tables.models import Ban
from apps.menu.models import ThucDon
from apps.promotions.models import KhuyenMai
from apps.orders.models import HoaDon, ChiTietHoaDon


class OrdersTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Users
        self.tk = TaiKhoan.objects.create(ten_dang_nhap='nhanvien', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN)
        self.nv = NhanVien.objects.create(ho_ten='NV Test', sdt='0123456789', ma_tk=self.tk)

        self._authenticate(self.tk)

        # Bàn
        self.ban1 = Ban.objects.create(ten_khu_vuc='Tầng 1')
        self.ban2 = Ban.objects.create(ten_khu_vuc='Tầng 1')

        # Khách hàng
        self.kh_thuong = KhachHang.objects.create(sdt_khach='0901', ho_ten='KH Thuong', hang_tv='Đồng')
        self.kh_vip = KhachHang.objects.create(sdt_khach='0902', ho_ten='KH VIP', hang_tv='Vàng', diem_tich_luy=1500)

        # Thực đơn
        self.mon1 = ThucDon.objects.create(ten_mon='Món đắt', don_gia=500000, ma_loai='M')
        self.mon2 = ThucDon.objects.create(ten_mon='Món rẻ', don_gia=100000, ma_loai='M')

        # Khuyến mãi
        today = timezone.localtime().date()
        self.km = KhuyenMai.objects.create(
            ten_chuong_trinh='KM Test', 
            ngay_bd=today - timedelta(days=1),
            ngay_kt=today + timedelta(days=1),
            phan_tram_giam=30, # Sẽ không dùng tỷ lệ này mà dùng decision table
            dieu_kien_toi_thieu=200000,
            is_active=True
        )

    def _authenticate(self, user):
        from apps.authentication.views import _make_tokens
        tokens = _make_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    def _create_order(self, ma_ban, sdt=None, item=None):
        res = self.client.post('/api/orders/', {'ma_ban': ma_ban, 'sdt_khach': sdt})
        ma_hd = res.data['data']['ma_hd']
        if item:
            self.client.post(f'/api/orders/{ma_hd}/items/', {'ma_mon': item.ma_mon, 'so_luong': 1})
        return ma_hd

    # =========================================================================
    # Test Decision Table Discount
    # =========================================================================

    def test_case_1_gte500k_vip_voucher_20_percent(self):
        """Case 1: >= 500k + VIP + Voucher -> 20%"""
        ma_hd = self._create_order(self.ban1.ma_ban, '0902', self.mon1) # 500k, VIP
        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt',
            'promotion_code': str(self.km.ma_km)
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['checkout_summary']['discount_percent'], 20)
        self.assertEqual(res.data['checkout_summary']['final_total'], 400000) # 500k - 20%

    def test_case_2_gte500k_voucher_15_percent(self):
        """Case 2: >= 500k + Voucher (Normal KH) -> 15%"""
        ma_hd = self._create_order(self.ban1.ma_ban, '0901', self.mon1) # 500k, Đồng
        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt',
            'promotion_code': str(self.km.ma_km)
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['checkout_summary']['discount_percent'], 15)
        self.assertEqual(res.data['checkout_summary']['final_total'], 425000)

    def test_case_3_gte500k_only_10_percent(self):
        """Case 3: >= 500k, Không Voucher, Không VIP -> 10%"""
        ma_hd = self._create_order(self.ban1.ma_ban, '0901', self.mon1)
        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['checkout_summary']['discount_percent'], 10)
        self.assertEqual(res.data['checkout_summary']['final_total'], 450000)

    def test_case_4_vip_only_5_percent(self):
        """Case 4: < 500k, VIP -> 5%"""
        ma_hd = self._create_order(self.ban1.ma_ban, '0902', self.mon2) # 100k, VIP
        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['checkout_summary']['discount_percent'], 5)
        self.assertEqual(res.data['checkout_summary']['final_total'], 95000)

    def test_case_5_normal_0_percent(self):
        """Case 5: Khách thường, Không Voucher, < 500k -> 0%"""
        ma_hd = self._create_order(self.ban1.ma_ban, '0901', self.mon2) # 100k, Đồng
        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['checkout_summary']['discount_percent'], 0)
        self.assertEqual(res.data['checkout_summary']['final_total'], 100000)

    # =========================================================================
    # Test Side Effects (Points, Tiers, Table Status)
    # =========================================================================

    def test_checkout_loyalty_points_and_table_status(self):
        """Kiểm tra tích điểm và đổi trạng thái bàn"""
        ma_hd = self._create_order(self.ban1.ma_ban, '0901', self.mon1) # 500k -> 450k
        
        self.ban1.refresh_from_db()
        self.assertEqual(self.ban1.trang_thai, Ban.TrangThai.CO_KHACH)

        self.client.post(f'/api/orders/{ma_hd}/checkout/', {'phuong_thuc': 'Tiền mặt'})
        
        self.ban1.refresh_from_db()
        self.assertEqual(self.ban1.trang_thai, Ban.TrangThai.DANG_DON)

        self.kh_thuong.refresh_from_db()
        # Final = 450k -> 45 điểm
        self.assertEqual(self.kh_thuong.diem_tich_luy, 45)
        self.assertEqual(self.kh_thuong.hang_tv, KhachHang.HangThanhVien.DONG) # 45 < 500
