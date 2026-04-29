"""
Unit tests cho module Reports (Báo cáo & Thống kê).
Chạy: python manage.py test apps.reports --settings=config.settings_dev
"""
from datetime import datetime, date, time
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.staff.models import NhanVien, CaLam, ChamCong
from apps.customers.models import KhachHang
from apps.tables.models import Ban
from apps.menu.models import ThucDon
from apps.orders.models import HoaDon, ChiTietHoaDon


class ReportsTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Tài khoản Quản lý
        self.tk_quan_ly = TaiKhoan.objects.create(
            ten_dang_nhap='quanly', mat_khau='hashed', ma_phan_quyen=TaiKhoan.PhanQuyen.QUAN_LY
        )
        self.nv = NhanVien.objects.create(ho_ten='NV Test', sdt='0123456789')
        
        self.kh = KhachHang.objects.create(sdt_khach='0901234567', ho_ten='KH VIP', hang_tv='Vàng')
        self.ban = Ban.objects.create(ten_khu_vuc='Tầng 1')
        self.mon1 = ThucDon.objects.create(ten_mon='Cà phê', ma_loai='cf', don_gia=20000)
        self.mon2 = ThucDon.objects.create(ten_mon='Trà', ma_loai='tea', don_gia=30000)

        # Mock datetime for consistent reporting
        self.report_date = date(2026, 4, 28)
        self.report_datetime = datetime(2026, 4, 28, 10, 0, 0, tzinfo=timezone.utc)

        # Hóa đơn 1 (Hoàn tất)
        hd1 = HoaDon.objects.create(
            ma_nv=self.nv, ma_ban=self.ban, sdt_khach=self.kh, 
            tong_tien=70000, trang_thai=HoaDon.TrangThai.HOAN_TAT
        )
        hd1.ngay_lap = self.report_datetime # Override auto_now_add for testing
        hd1.save()
        ChiTietHoaDon.objects.create(ma_hd=hd1, ma_mon=self.mon1, so_luong=2, gia_ban=20000) # 40k
        ChiTietHoaDon.objects.create(ma_hd=hd1, ma_mon=self.mon2, so_luong=1, gia_ban=30000) # 30k

        # Hóa đơn 2 (Hoàn tất)
        hd2 = HoaDon.objects.create(
            ma_nv=self.nv, ma_ban=self.ban, sdt_khach=self.kh, 
            tong_tien=40000, trang_thai=HoaDon.TrangThai.HOAN_TAT
        )
        hd2.ngay_lap = self.report_datetime
        hd2.save()
        ChiTietHoaDon.objects.create(ma_hd=hd2, ma_mon=self.mon1, so_luong=2, gia_ban=20000) # 40k

        # Chấm công
        ca = CaLam.objects.create(ma_nv=self.nv, ngay_lam=self.report_date, gio_bat_dau=time(8, 0), gio_ket_thuc=time(12, 0))
        ChamCong.objects.create(ma_ca=ca, ma_nv=self.nv, trang_thai=ChamCong.TrangThai.DUNG_GIO)

    def _authenticate(self, user):
        from apps.authentication.views import _make_tokens
        tokens = _make_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    def test_daily_revenue_report(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/reports/revenue/daily/?date=2026-04-28')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['data']
        self.assertEqual(data['invoice_count'], 2)
        self.assertEqual(data['total_revenue'], 110000) # 70k + 40k
        self.assertEqual(data['average_per_invoice'], 55000)

    def test_monthly_revenue_report(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/reports/revenue/monthly/?thang=4&nam=2026')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['data']
        self.assertEqual(len(data), 30) # Tháng 4 có 30 ngày
        day_28 = next(item for item in data if item['day'] == 28)
        self.assertEqual(day_28['revenue'], 110000)

    def test_bestseller_report(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/reports/bestseller/?thang=4&nam=2026')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['data']
        self.assertEqual(len(data), 2)
        # Cà phê (mon1) bán 4 ly, Trà (mon2) bán 1 ly
        self.assertEqual(data[0]['item_name'], 'Cà phê')
        self.assertEqual(data[0]['quantity_sold'], 4)

    def test_staff_attendance_report(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/reports/staff/attendance/?thang=4&nam=2026')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['on_time_days'], 1)
        self.assertEqual(data[0]['late_days'], 0)

    def test_top_customers_report(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.get('/api/reports/customers/top/?thang=4&nam=2026')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'KH VIP')
        self.assertEqual(data[0]['total_spent'], 110000)
