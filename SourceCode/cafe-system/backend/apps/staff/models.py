from django.db import models
from django.core.validators import RegexValidator
from apps.authentication.models import TaiKhoan


sdt_validator = RegexValidator(
    regex=r'^\d{9,11}$',
    message='Số điện thoại phải có từ 9 đến 11 chữ số.'
)


class NhanVien(models.Model):
    """Thông tin nhân viên"""

    ma_nv = models.AutoField(
        primary_key=True,
        verbose_name='Mã nhân viên'
    )
    ho_ten = models.CharField(
        max_length=100,
        verbose_name='Họ tên'
    )
    sdt = models.CharField(
        max_length=11,
        validators=[sdt_validator],
        verbose_name='Số điện thoại'
    )
    dia_chi = models.TextField(
        blank=True,
        default='',
        verbose_name='Địa chỉ'
    )
    ma_tk = models.OneToOneField(
        TaiKhoan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ma_tk',
        related_name='nhan_vien',
        verbose_name='Tài khoản'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Đang làm việc'
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
        db_table = 'nhan_vien'
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'
        ordering = ['ho_ten']

    def __str__(self):
        return f"{self.ma_nv} - {self.ho_ten}"


class CaLam(models.Model):
    """Ca làm việc của nhân viên"""

    ma_ca = models.AutoField(
        primary_key=True,
        verbose_name='Mã ca'
    )
    ma_nv = models.ForeignKey(
        NhanVien,
        on_delete=models.CASCADE,
        db_column='ma_nv',
        related_name='ca_lam',
        verbose_name='Nhân viên'
    )
    ngay_lam = models.DateField(
        verbose_name='Ngày làm'
    )
    gio_bat_dau = models.TimeField(
        verbose_name='Giờ bắt đầu'
    )
    gio_ket_thuc = models.TimeField(
        verbose_name='Giờ kết thúc'
    )
    ngay_tao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )

    class Meta:
        db_table = 'ca_lam'
        verbose_name = 'Ca làm'
        verbose_name_plural = 'Ca làm'
        ordering = ['-ngay_lam', 'gio_bat_dau']
        unique_together = [['ma_nv', 'ngay_lam', 'gio_bat_dau']]

    def __str__(self):
        return (
            f"Ca {self.ma_ca} - {self.ma_nv.ho_ten} "
            f"({self.ngay_lam} {self.gio_bat_dau}–{self.gio_ket_thuc})"
        )


class ChamCong(models.Model):
    """Chấm công thực tế của nhân viên theo ca"""

    class TrangThai(models.TextChoices):
        DUNG_GIO = 'Đúng giờ', 'Đúng giờ'
        DI_TRE = 'Đi trễ', 'Đi trễ'
        DI_TRE_NANG = 'Đi trễ nặng', 'Đi trễ nặng'
        CHUA_CHAM = 'Chưa chấm', 'Chưa chấm'
        VANG = 'Vắng', 'Vắng'

    ma_ca = models.ForeignKey(
        CaLam,
        on_delete=models.CASCADE,
        db_column='ma_ca',
        related_name='cham_cong',
        verbose_name='Ca làm'
    )
    ma_nv = models.ForeignKey(
        NhanVien,
        on_delete=models.CASCADE,
        db_column='ma_nv',
        related_name='cham_cong',
        verbose_name='Nhân viên'
    )
    gio_vao_thuc = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Giờ vào thực tế'
    )
    gio_ra_thuc = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Giờ ra thực tế'
    )
    trang_thai = models.CharField(
        max_length=20,
        choices=TrangThai.choices,
        default=TrangThai.CHUA_CHAM,
        verbose_name='Trạng thái'
    )
    ghi_chu = models.TextField(
        blank=True,
        default='',
        verbose_name='Ghi chú'
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
        db_table = 'cham_cong'
        verbose_name = 'Chấm công'
        verbose_name_plural = 'Chấm công'
        ordering = ['-ngay_tao']
        unique_together = [['ma_ca', 'ma_nv']]

    def __str__(self):
        return (
            f"Chấm công - {self.ma_nv.ho_ten} "
            f"ca {self.ma_ca_id} [{self.trang_thai}]"
        )
