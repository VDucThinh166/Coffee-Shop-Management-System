from django.db import models


class Ban(models.Model):
    """Quản lý bàn trong quán"""

    class TrangThai(models.IntegerChoices):
        TRONG = 0, 'Trống'
        CO_KHACH = 1, 'Có khách'
        DANG_DON = 2, 'Đang dọn'

    ma_ban = models.AutoField(
        primary_key=True,
        verbose_name='Mã bàn'
    )
    ten_khu_vuc = models.CharField(
        max_length=100,
        verbose_name='Tên / Khu vực'
    )
    trang_thai = models.IntegerField(
        choices=TrangThai.choices,
        default=TrangThai.TRONG,
        verbose_name='Trạng thái'
    )
    ngay_cap_nhat = models.DateTimeField(
        auto_now=True,
        verbose_name='Cập nhật lần cuối'
    )

    class Meta:
        db_table = 'ban'
        verbose_name = 'Bàn'
        verbose_name_plural = 'Bàn'
        ordering = ['ten_khu_vuc', 'ma_ban']

    def __str__(self):
        return f"Bàn {self.ma_ban} - {self.ten_khu_vuc} [{self.get_trang_thai_display()}]"
