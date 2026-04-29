from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.staff.models import NhanVien


class TonKho(models.Model):
    """Nguyên liệu trong kho"""

    ma_nl = models.AutoField(
        primary_key=True,
        verbose_name='Mã nguyên liệu'
    )
    ten_nl = models.CharField(
        max_length=150,
        verbose_name='Tên nguyên liệu'
    )
    so_luong_ton = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Số lượng tồn'
    )
    don_vi_tinh = models.CharField(
        max_length=30,
        verbose_name='Đơn vị tính'
    )
    nguong_bao_dong = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Ngưỡng báo động'
    )
    ngay_cap_nhat = models.DateTimeField(
        auto_now=True,
        verbose_name='Cập nhật lần cuối'
    )

    class Meta:
        db_table = 'ton_kho'
        verbose_name = 'Tồn kho'
        verbose_name_plural = 'Tồn kho'
        ordering = ['ten_nl']

    @property
    def can_bao_dong(self):
        """Trả về True nếu tồn kho xuống dưới ngưỡng báo động."""
        return self.so_luong_ton <= self.nguong_bao_dong

    def __str__(self):
        canh_bao = ' ⚠️' if self.can_bao_dong else ''
        return (
            f"{self.ten_nl} - Tồn: {self.so_luong_ton} {self.don_vi_tinh}{canh_bao}"
        )


class PhieuNhap(models.Model):
    """Phiếu nhập kho"""

    ma_phieu = models.AutoField(
        primary_key=True,
        verbose_name='Mã phiếu nhập'
    )
    ngay_nhap = models.DateField(
        verbose_name='Ngày nhập'
    )
    ma_nv = models.ForeignKey(
        NhanVien,
        on_delete=models.PROTECT,
        db_column='ma_nv',
        related_name='phieu_nhap',
        verbose_name='Nhân viên nhập'
    )
    tong_gia_tri = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Tổng giá trị (VNĐ)'
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
        db_table = 'phieu_nhap'
        verbose_name = 'Phiếu nhập'
        verbose_name_plural = 'Phiếu nhập'
        ordering = ['-ngay_nhap', '-ma_phieu']

    def __str__(self):
        return (
            f"Phiếu {self.ma_phieu} - {self.ngay_nhap} "
            f"({self.tong_gia_tri:,.0f}đ)"
        )


class ChiTietPhieuNhap(models.Model):
    """Chi tiết từng nguyên liệu trong phiếu nhập"""

    ma_phieu = models.ForeignKey(
        PhieuNhap,
        on_delete=models.CASCADE,
        db_column='ma_phieu',
        related_name='chi_tiet',
        verbose_name='Phiếu nhập'
    )
    ma_nl = models.ForeignKey(
        TonKho,
        on_delete=models.PROTECT,
        db_column='ma_nl',
        related_name='chi_tiet_nhap',
        verbose_name='Nguyên liệu'
    )
    sl_nhap = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Số lượng nhập'
    )
    don_gia_nhap = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Đơn giá nhập (VNĐ)'
    )

    class Meta:
        db_table = 'chi_tiet_phieu_nhap'
        verbose_name = 'Chi tiết phiếu nhập'
        verbose_name_plural = 'Chi tiết phiếu nhập'
        unique_together = [['ma_phieu', 'ma_nl']]

    @property
    def thanh_tien(self):
        return self.sl_nhap * self.don_gia_nhap

    def __str__(self):
        return (
            f"Phiếu {self.ma_phieu_id} - "
            f"{self.ma_nl.ten_nl} x {self.sl_nhap} "
            f"@ {self.don_gia_nhap:,.0f}đ"
        )
