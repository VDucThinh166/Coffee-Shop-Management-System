from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ThucDon(models.Model):
    """Danh sách món trong thực đơn"""

    class TrangThai(models.IntegerChoices):
        HET = 0, 'Hết'
        CON = 1, 'Còn'

    ma_mon = models.AutoField(
        primary_key=True,
        verbose_name='Mã món'
    )
    ten_mon = models.CharField(
        max_length=150,
        verbose_name='Tên món'
    )
    ma_loai = models.CharField(
        max_length=50,
        verbose_name='Mã loại / Danh mục'
    )
    don_gia = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Đơn giá (VNĐ)'
    )
    mo_ta = models.TextField(
        blank=True,
        default='',
        verbose_name='Mô tả'
    )
    hinh_anh = models.ImageField(
        upload_to='menu/',
        blank=True,
        null=True,
        verbose_name='Hình ảnh'
    )
    trang_thai = models.IntegerField(
        choices=TrangThai.choices,
        default=TrangThai.CON,
        verbose_name='Trạng thái'
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
        db_table = 'thuc_don'
        verbose_name = 'Thực đơn'
        verbose_name_plural = 'Thực đơn'
        ordering = ['ma_loai', 'ten_mon']

    def __str__(self):
        trang_thai = self.get_trang_thai_display()
        return f"{self.ten_mon} - {self.don_gia:,.0f}đ [{trang_thai}]"
