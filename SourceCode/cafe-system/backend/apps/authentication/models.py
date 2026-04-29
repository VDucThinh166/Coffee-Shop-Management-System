from django.db import models


class TaiKhoan(models.Model):
    """Tài khoản đăng nhập hệ thống"""

    class PhanQuyen(models.IntegerChoices):
        QUAN_LY = 1, 'Quản lý'
        NHAN_VIEN = 2, 'Nhân viên'

    ma_tk = models.AutoField(
        primary_key=True,
        verbose_name='Mã tài khoản'
    )
    ten_dang_nhap = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Tên đăng nhập'
    )
    mat_khau = models.CharField(
        max_length=255,
        verbose_name='Mật khẩu (hash)'
    )
    ma_phan_quyen = models.IntegerField(
        choices=PhanQuyen.choices,
        default=PhanQuyen.NHAN_VIEN,
        verbose_name='Phân quyền'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Hoạt động'
    )
    ngay_tao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    ngay_cap_nhat = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    class Meta:
        db_table = 'tai_khoan'
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Tài khoản'
        ordering = ['ten_dang_nhap']

    @property
    def is_authenticated(self):
        """Yêu cầu bởi DRF IsAuthenticated permission."""
        return True

    def __str__(self):
        phan_quyen = self.get_ma_phan_quyen_display()
        return f"{self.ten_dang_nhap} ({phan_quyen})"
