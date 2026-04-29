from django.db import models
from django.core.validators import RegexValidator


sdt_validator = RegexValidator(
    regex=r'^\d{9,11}$',
    message='Số điện thoại phải có từ 9 đến 11 chữ số.'
)


class KhachHang(models.Model):
    """Thông tin khách hàng thân thiết"""

    class HangThanhVien(models.TextChoices):
        DONG = 'Đồng', 'Đồng'
        BAC = 'Bạc', 'Bạc'
        VANG = 'Vàng', 'Vàng'
        KIM_CUONG = 'Kim cương', 'Kim cương'

    sdt_khach = models.CharField(
        max_length=11,
        primary_key=True,
        validators=[sdt_validator],
        verbose_name='Số điện thoại (PK)'
    )
    ho_ten = models.CharField(
        max_length=100,
        verbose_name='Họ tên'
    )
    diem_tich_luy = models.PositiveIntegerField(
        default=0,
        verbose_name='Điểm tích lũy'
    )
    hang_tv = models.CharField(
        max_length=20,
        choices=HangThanhVien.choices,
        default=HangThanhVien.DONG,
        verbose_name='Hạng thành viên'
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
        db_table = 'khach_hang'
        verbose_name = 'Khách hàng'
        verbose_name_plural = 'Khách hàng'
        ordering = ['ho_ten']

    def __str__(self):
        return f"{self.ho_ten} - {self.sdt_khach} [{self.hang_tv}]"
