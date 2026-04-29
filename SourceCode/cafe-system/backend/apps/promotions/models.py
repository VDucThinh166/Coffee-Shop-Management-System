from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class KhuyenMai(models.Model):
    """Chương trình khuyến mãi"""

    ma_km = models.AutoField(
        primary_key=True,
        verbose_name='Mã khuyến mãi'
    )
    ten_chuong_trinh = models.CharField(
        max_length=200,
        verbose_name='Tên chương trình'
    )
    ngay_bd = models.DateField(
        verbose_name='Ngày bắt đầu'
    )
    ngay_kt = models.DateField(
        verbose_name='Ngày kết thúc'
    )
    phan_tram_giam = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('100.00')),
        ],
        verbose_name='Phần trăm giảm (%)'
    )
    dieu_kien_toi_thieu = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Điều kiện tối thiểu (VNĐ)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang hoạt động'
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
        db_table = 'khuyen_mai'
        verbose_name = 'Khuyến mãi'
        verbose_name_plural = 'Khuyến mãi'
        ordering = ['-ngay_bd']

    def clean(self):
        if self.ngay_bd and self.ngay_kt and self.ngay_bd > self.ngay_kt:
            raise ValidationError({
                'ngay_kt': 'Ngày kết thúc phải sau ngày bắt đầu.'
            })

    def __str__(self):
        return (
            f"{self.ten_chuong_trinh} "
            f"(-{self.phan_tram_giam}%) "
            f"[{self.ngay_bd} → {self.ngay_kt}]"
        )
