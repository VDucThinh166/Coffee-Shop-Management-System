"""
Unit tests cho module Tables.
Chạy: python manage.py test apps.tables --settings=config.settings_dev
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.tables.models import Ban
from apps.orders.models import HoaDon
from apps.staff.models import NhanVien


class BanTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Tạo tài khoản Quản lý và Nhân viên
        self.tk_quan_ly = TaiKhoan.objects.create(
            ten_dang_nhap='quanly',
            mat_khau='hashed',
            ma_phan_quyen=TaiKhoan.PhanQuyen.QUAN_LY
        )
        self.tk_nhan_vien = TaiKhoan.objects.create(
            ten_dang_nhap='nhanvien',
            mat_khau='hashed',
            ma_phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN
        )

        # Tạo nhân viên record để tạo hóa đơn
        self.nv = NhanVien.objects.create(
            ho_ten='NV Test', sdt='0123456789', ma_tk=self.tk_nhan_vien
        )

        # Tạo sẵn một vài bàn
        self.ban1 = Ban.objects.create(ten_khu_vuc='Tầng 1', trang_thai=Ban.TrangThai.TRONG)
        self.ban2 = Ban.objects.create(ten_khu_vuc='Tầng 1', trang_thai=Ban.TrangThai.CO_KHACH)
        self.ban3 = Ban.objects.create(ten_khu_vuc='Tầng 2', trang_thai=Ban.TrangThai.DANG_DON)
        self.ban4 = Ban.objects.create(ten_khu_vuc='Tầng 2', trang_thai=Ban.TrangThai.CO_KHACH)

    def _authenticate(self, user):
        from apps.authentication.views import _make_tokens
        tokens = _make_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    # -----------------------------------------------------------------------
    # GET /api/tables/
    # -----------------------------------------------------------------------
    def test_list_ban_success(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.get('/api/tables/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 4)

    def test_list_ban_filter_khu_vuc(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.get('/api/tables/?khu_vuc=Tầng 1')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)

    def test_list_ban_filter_trang_thai(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.get('/api/tables/?trang_thai=1')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)

    # -----------------------------------------------------------------------
    # POST /api/tables/
    # -----------------------------------------------------------------------
    def test_create_ban_as_manager(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/tables/', {'ten_khu_vuc': 'VIP 1'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ban.objects.count(), 5)

    def test_create_ban_as_staff_forbidden(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.post('/api/tables/', {'ten_khu_vuc': 'VIP 1'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------------------------------------------------
    # PATCH /api/tables/{id}/status/
    # -----------------------------------------------------------------------
    def test_update_status_success(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.patch(f'/api/tables/{self.ban1.ma_ban}/status/', {'trang_thai': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.ban1.refresh_from_db()
        self.assertEqual(self.ban1.trang_thai, Ban.TrangThai.CO_KHACH)

    def test_update_status_to_trong_fails_with_open_orders(self):
        # Tạo hóa đơn cho ban2
        HoaDon.objects.create(
            ma_nv=self.nv, ma_ban=self.ban2, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE
        )
        self._authenticate(self.tk_nhan_vien)
        res = self.client.patch(f'/api/tables/{self.ban2.ma_ban}/status/', {'trang_thai': 0})
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data['code'], 'open_orders_exist')

    # -----------------------------------------------------------------------
    # POST /api/tables/transfer/
    # -----------------------------------------------------------------------
    def test_transfer_ban_success(self):
        HoaDon.objects.create(
            ma_nv=self.nv, ma_ban=self.ban2, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE
        )
        self._authenticate(self.tk_nhan_vien)
        res = self.client.post('/api/tables/transfer/', {
            'tu_ban': self.ban2.ma_ban,
            'den_ban': self.ban1.ma_ban
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.ban1.refresh_from_db()
        self.ban2.refresh_from_db()
        self.assertEqual(self.ban2.trang_thai, Ban.TrangThai.DANG_DON)
        self.assertEqual(self.ban1.trang_thai, Ban.TrangThai.CO_KHACH)

    def test_transfer_ban_fails_target_not_empty(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.post('/api/tables/transfer/', {
            'tu_ban': self.ban2.ma_ban,
            'den_ban': self.ban4.ma_ban
        })
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data['code'], 'ban_dich_not_empty')

    # -----------------------------------------------------------------------
    # POST /api/tables/merge/
    # -----------------------------------------------------------------------
    def test_merge_ban_success(self):
        HoaDon.objects.create(ma_nv=self.nv, ma_ban=self.ban2, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE)
        HoaDon.objects.create(ma_nv=self.nv, ma_ban=self.ban4, trang_thai=HoaDon.TrangThai.CHO_PHA_CHE)

        self._authenticate(self.tk_nhan_vien)
        res = self.client.post('/api/tables/merge/', {
            'ban_chinh': self.ban2.ma_ban,
            'ban_phu': [self.ban4.ma_ban]
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.ban2.refresh_from_db()
        self.ban4.refresh_from_db()
        self.assertEqual(self.ban2.trang_thai, Ban.TrangThai.CO_KHACH)
        self.assertEqual(self.ban4.trang_thai, Ban.TrangThai.DANG_DON)
        
        # Check orders moved to ban2
        self.assertEqual(HoaDon.objects.filter(ma_ban=self.ban2).count(), 2)
        self.assertEqual(HoaDon.objects.filter(ma_ban=self.ban4).count(), 0)

    def test_merge_ban_fails_phu_not_occupied(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.post('/api/tables/merge/', {
            'ban_chinh': self.ban2.ma_ban,
            'ban_phu': [self.ban1.ma_ban]  # ban1 is TRONG
        })
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data['code'], 'ban_phu_not_occupied')
