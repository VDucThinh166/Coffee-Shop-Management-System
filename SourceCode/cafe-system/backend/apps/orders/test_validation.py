"""
Test Cases Kiểm Định Lỗ Hổng — Tìm bugs trong module Orders.
Tập trung vào các edge cases và boundary conditions.

Chạy: python manage.py test apps.orders.test_validation --settings=config.settings_dev -v2
"""
from datetime import timedelta
from decimal import Decimal
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
from apps.orders.services import calculate_total


class CheckoutEdgeCaseTests(TestCase):
    """Test các trường hợp biên và lỗ hổng trong luồng thanh toán."""

    def setUp(self):
        self.client = APIClient()

        # Users
        self.tk = TaiKhoan.objects.create(
            ten_dang_nhap='nhanvien', mat_khau='hashed',
            ma_phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN
        )
        self.nv = NhanVien.objects.create(
            ho_ten='NV Test', sdt='0123456789', ma_tk=self.tk
        )
        self._authenticate(self.tk)

        # Bàn
        self.ban1 = Ban.objects.create(ten_khu_vuc='Tầng 1')
        self.ban2 = Ban.objects.create(ten_khu_vuc='Tầng 1')
        self.ban3 = Ban.objects.create(ten_khu_vuc='Tầng 1')

        # Khách hàng
        self.kh_thuong = KhachHang.objects.create(
            sdt_khach='0901', ho_ten='KH Thuong', hang_tv='Đồng'
        )
        self.kh_vip = KhachHang.objects.create(
            sdt_khach='0902', ho_ten='KH VIP', hang_tv='Vàng', diem_tich_luy=1500
        )

        # Thực đơn
        self.mon_dat = ThucDon.objects.create(ten_mon='Món đắt', don_gia=500000, ma_loai='M')
        self.mon_re = ThucDon.objects.create(ten_mon='Món rẻ', don_gia=100000, ma_loai='M')

        # Khuyến mãi
        today = timezone.localtime().date()
        self.km_active = KhuyenMai.objects.create(
            ten_chuong_trinh='KM Active',
            ngay_bd=today - timedelta(days=1),
            ngay_kt=today + timedelta(days=1),
            phan_tram_giam=30,
            dieu_kien_toi_thieu=200000,
            is_active=True
        )
        self.km_expired = KhuyenMai.objects.create(
            ten_chuong_trinh='KM Het Han',
            ngay_bd=today - timedelta(days=30),
            ngay_kt=today - timedelta(days=1),  # Đã hết hạn
            phan_tram_giam=10,
            dieu_kien_toi_thieu=0,
            is_active=True
        )
        self.km_high_min = KhuyenMai.objects.create(
            ten_chuong_trinh='KM Min Cao',
            ngay_bd=today - timedelta(days=1),
            ngay_kt=today + timedelta(days=1),
            phan_tram_giam=50,
            dieu_kien_toi_thieu=999999,  # Điều kiện rất cao
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
    # BUG-01: earned_points undefined khi thanh toán khách vãng lai
    # =========================================================================

    def test_checkout_guest_no_customer_should_not_crash(self):
        """
        [BUG-01] Thanh toán hóa đơn KHÔNG có khách hàng (khách vãng lai).
        Biến earned_points chỉ được khai báo trong block if hd.sdt_khach,
        nhưng lại được tham chiếu ở response → NameError.
        """
        # Tạo order KHÔNG có sdt_khach (khách vãng lai)
        ma_hd = self._create_order(self.ban1.ma_ban, sdt=None, item=self.mon_re)

        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })

        # Phải trả 200, KHÔNG được crash 500
        self.assertEqual(res.status_code, status.HTTP_200_OK, 
            f"BUG-01: Checkout khách vãng lai CRASH! Response: {res.data}")
        self.assertEqual(res.data['checkout_summary']['points_earned'], 0)

    # =========================================================================
    # Edge Case: Thanh toán hóa đơn trống
    # =========================================================================

    def test_checkout_empty_order_should_reject(self):
        """Hóa đơn chưa có món nào → Không cho thanh toán."""
        res = self.client.post('/api/orders/', {'ma_ban': self.ban2.ma_ban})
        ma_hd = res.data['data']['ma_hd']
        # Không thêm món nào

        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # =========================================================================
    # Edge Case: Thanh toán hóa đơn đã hoàn tất (double checkout)
    # =========================================================================

    def test_checkout_already_completed_should_reject(self):
        """Hóa đơn đã thanh toán → Không cho thanh toán lần 2."""
        ma_hd = self._create_order(self.ban3.ma_ban, '0901', self.mon_re)

        # Thanh toán lần 1
        res1 = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Thanh toán lần 2 — phải bị từ chối
        res2 = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt'
        })
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    # =========================================================================
    # Voucher: Hết hạn
    # =========================================================================

    def test_checkout_expired_voucher_should_reject(self):
        """Voucher hết hạn → Không cho sử dụng."""
        ban_extra = Ban.objects.create(ten_khu_vuc='Extra')
        ma_hd = self._create_order(ban_extra.ma_ban, '0901', self.mon_dat)

        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt',
            'promotion_code': str(self.km_expired.ma_km)
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('hiệu lực', res.data['message'].lower())

    # =========================================================================
    # Voucher: Chưa đủ điều kiện tối thiểu
    # =========================================================================

    def test_checkout_voucher_below_minimum_should_reject(self):
        """HĐ chưa đạt điều kiện tối thiểu của voucher → Từ chối."""
        ban_extra = Ban.objects.create(ten_khu_vuc='Extra 2')
        ma_hd = self._create_order(ban_extra.ma_ban, '0901', self.mon_re)  # 100k

        res = self.client.post(f'/api/orders/{ma_hd}/checkout/', {
            'phuong_thuc': 'Tiền mặt',
            'promotion_code': str(self.km_high_min.ma_km)  # min = 999,999
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('điều kiện', res.data['message'].lower())


class CalculateTotalEdgeCaseTests(TestCase):
    """Test các trường hợp biên cho hàm calculate_total()."""

    # =========================================================================
    # BUG-06: VIP + Voucher + < 500k
    # =========================================================================

    def test_vip_under_500k_with_voucher_returns_5_percent(self):
        """
        [BUG-06] VIP + Voucher nhưng subtotal < 500k.
        Hiện tại chỉ trả 5% (do elif is_vip).
        Document: Đây là behavior đã biết, cần xác nhận với đề bài.
        """
        final, pct = calculate_total(Decimal('300000'), True, True)
        # Hiện tại theo Decision Table → 5% (vì < 500k, rơi vào elif is_vip)
        self.assertEqual(pct, 5)
        self.assertEqual(final, Decimal('285000'))

    # =========================================================================
    # Edge Case: Subtotal = 0
    # =========================================================================

    def test_calculate_total_zero_subtotal(self):
        """Subtotal = 0 → Không crash, trả 0."""
        final, pct = calculate_total(Decimal('0'), False, False)
        self.assertEqual(pct, 0)
        self.assertEqual(final, Decimal('0'))

    def test_calculate_total_zero_subtotal_vip(self):
        """VIP nhưng subtotal = 0 → Vẫn trả 5% (nhưng final = 0)."""
        final, pct = calculate_total(Decimal('0'), True, False)
        self.assertEqual(pct, 5)
        self.assertEqual(final, Decimal('0'))

    # =========================================================================
    # Boundary: 499999 vs 500000
    # =========================================================================

    def test_boundary_just_below_500k(self):
        """499,999 VNĐ → Không đạt ngưỡng 500k → 0% (khách thường)."""
        final, pct = calculate_total(Decimal('499999'), False, False)
        self.assertEqual(pct, 0)
        self.assertEqual(final, Decimal('499999'))

    def test_boundary_exactly_500k(self):
        """500,000 VNĐ → Đạt ngưỡng → 10% (khách thường, không voucher)."""
        final, pct = calculate_total(Decimal('500000'), False, False)
        self.assertEqual(pct, 10)
        self.assertEqual(final, Decimal('450000'))

    def test_boundary_just_above_500k(self):
        """500,001 VNĐ → Đạt ngưỡng → 10%."""
        final, pct = calculate_total(Decimal('500001'), False, False)
        self.assertEqual(pct, 10)
        # 500001 * 90 / 100 = 450000.9
        expected = Decimal('500001') * Decimal('90') / Decimal('100')
        self.assertEqual(final, expected)
