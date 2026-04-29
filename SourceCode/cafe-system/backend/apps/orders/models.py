from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.staff.models import NhanVien
from apps.tables.models import Ban
from apps.customers.models import KhachHang
from apps.promotions.models import KhuyenMai
from apps.menu.models import ThucDon


class HoaDon(models.Model):
    """Hóa đơn bán hàng"""

    class PhuongThucThanhToan(models.TextChoices):
        TIEN_MAT = 'Tiền mặt', 'Tiền mặt'
        CHUYEN_KHOAN = 'Chuyển khoản', 'Chuyển khoản'

    class TrangThai(models.TextChoices):
        CHO_PHA_CHE = 'Chờ pha chế', 'Chờ pha chế'
        HOAN_TAT = 'Hoàn tất', 'Hoàn tất'
        DA_HUY = 'Đã hủy', 'Đã hủy'

    ma_hd = models.AutoField(
        primary_key=True,
        verbose_name='Mã hóa đơn'
    )
    ngay_lap = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày lập'
    )
    ma_nv = models.ForeignKey(
        NhanVien,
        on_delete=models.PROTECT,
        db_column='ma_nv',
        related_name='hoa_don',
        verbose_name='Nhân viên lập'
    )
    ma_ban = models.ForeignKey(
        Ban,
        on_delete=models.PROTECT,
        db_column='ma_ban',
        related_name='hoa_don',
        verbose_name='Bàn'
    )
    sdt_khach = models.ForeignKey(
        KhachHang,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='sdt_khach',
        to_field='sdt_khach',
        related_name='hoa_don',
        verbose_name='Khách hàng (SDT)'
    )
    tong_tien = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Tổng tiền (VNĐ)'
    )
    phuong_thuc = models.CharField(
        max_length=20,
        choices=PhuongThucThanhToan.choices,
        default=PhuongThucThanhToan.TIEN_MAT,
        verbose_name='Phương thức thanh toán'
    )
    trang_thai = models.CharField(
        max_length=20,
        choices=TrangThai.choices,
        default=TrangThai.CHO_PHA_CHE,
        verbose_name='Trạng thái'
    )
    ma_km = models.ForeignKey(
        KhuyenMai,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ma_km',
        related_name='hoa_don',
        verbose_name='Khuyến mãi áp dụng'
    )
    ngay_cap_nhat = models.DateTimeField(
        auto_now=True,
        verbose_name='Ngày cập nhật'
    )

    class Meta:
        db_table = 'hoa_don'
        verbose_name = 'Hóa đơn'
        verbose_name_plural = 'Hóa đơn'
        ordering = ['-ngay_lap']

    def __str__(self):
        return (
            f"HD-{self.ma_hd:05d} | Bàn {self.ma_ban_id} | "
            f"{self.tong_tien:,.0f}đ [{self.trang_thai}]"
        )


class ChiTietHoaDon(models.Model):
    """Chi tiết các món trong hóa đơn"""

    ma_hd = models.ForeignKey(
        HoaDon,
        on_delete=models.CASCADE,
        db_column='ma_hd',
        related_name='chi_tiet',
        verbose_name='Hóa đơn'
    )
    ma_mon = models.ForeignKey(
        ThucDon,
        on_delete=models.PROTECT,
        db_column='ma_mon',
        related_name='chi_tiet_hoa_don',
        verbose_name='Món'
    )
    so_luong = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Số lượng'
    )
    gia_ban = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Giá bán tại thời điểm (VNĐ)'
    )
    ghi_chu = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Ghi chú'
    )

    class Meta:
        db_table = 'chi_tiet_hoa_don'
        verbose_name = 'Chi tiết hóa đơn'
        verbose_name_plural = 'Chi tiết hóa đơn'
        unique_together = [['ma_hd', 'ma_mon']]

    @property
    def thanh_tien(self):
        return self.so_luong * self.gia_ban

    def __str__(self):
        return (
            f"HD-{self.ma_hd_id:05d} | "
            f"{self.ma_mon.ten_mon} x{self.so_luong} "
            f"= {self.thanh_tien:,.0f}đ"
        )
