"""
Unit tests cho module Menu (Thực đơn).
Chạy: python manage.py test apps.menu --settings=config.settings_dev
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import TaiKhoan
from apps.menu.models import ThucDon


class MenuTests(TestCase):

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

        # Tạo sẵn một vài món ăn
        self.mon1 = ThucDon.objects.create(
            ten_mon='Cà phê sữa đá',
            ma_loai='coffee',
            don_gia=25000,
            trang_thai=ThucDon.TrangThai.CON
        )
        self.mon2 = ThucDon.objects.create(
            ten_mon='Trà đào cam sả',
            ma_loai='tea',
            don_gia=35000,
            trang_thai=ThucDon.TrangThai.CON
        )
        self.mon3 = ThucDon.objects.create(
            ten_mon='Bánh sừng trâu',
            ma_loai='cake',
            don_gia=20000,
            trang_thai=ThucDon.TrangThai.HET
        )

    def _authenticate(self, user):
        from apps.authentication.views import _make_tokens
        tokens = _make_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access'])

    # -----------------------------------------------------------------------
    # GET /api/menu/ (Public)
    # -----------------------------------------------------------------------
    def test_list_menu_public(self):
        res = self.client.get('/api/menu/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 3)

    def test_list_menu_filter_type(self):
        res = self.client.get('/api/menu/?type=coffee')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['data'][0]['ten_mon'], 'Cà phê sữa đá')

    def test_list_menu_filter_status(self):
        res = self.client.get('/api/menu/?status=1')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)

    # -----------------------------------------------------------------------
    # POST /api/menu/ (Admin only)
    # -----------------------------------------------------------------------
    def test_create_menu_item_as_manager(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.post('/api/menu/', {
            'ten_mon': 'Cà phê đen',
            'ma_loai': 'coffee',
            'don_gia': 20000,
            'trang_thai': 1
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ThucDon.objects.count(), 4)

    def test_create_menu_item_as_staff_forbidden(self):
        self._authenticate(self.tk_nhan_vien)
        res = self.client.post('/api/menu/', {
            'ten_mon': 'Cà phê đen',
            'ma_loai': 'coffee',
            'don_gia': 20000,
            'trang_thai': 1
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------------------------------------------------
    # PUT /api/menu/{id}/ (Admin only)
    # -----------------------------------------------------------------------
    def test_update_menu_item_as_manager(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.put(f'/api/menu/{self.mon1.ma_mon}/', {
            'don_gia': 30000
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.mon1.refresh_from_db()
        self.assertEqual(self.mon1.don_gia, 30000)

    # -----------------------------------------------------------------------
    # DELETE /api/menu/{id}/ (Admin only)
    # -----------------------------------------------------------------------
    def test_delete_menu_item_as_manager(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.delete(f'/api/menu/{self.mon1.ma_mon}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ThucDon.objects.count(), 2)

    # -----------------------------------------------------------------------
    # PATCH /api/menu/{id}/status/ (Admin only)
    # -----------------------------------------------------------------------
    def test_update_status_success(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.patch(f'/api/menu/{self.mon3.ma_mon}/status/', {
            'trang_thai': 1
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.mon3.refresh_from_db()
        self.assertEqual(self.mon3.trang_thai, ThucDon.TrangThai.CON)

    def test_update_status_invalid_data(self):
        self._authenticate(self.tk_quan_ly)
        res = self.client.patch(f'/api/menu/{self.mon3.ma_mon}/status/', {
            'trang_thai': 99
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
