import os
import django
import sys
from datetime import date, timedelta, datetime

# Cấu hình môi trường Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from apps.authentication.models import TaiKhoan
from apps.staff.models import NhanVien
from apps.tables.models import Ban
from apps.menu.models import ThucDon
from apps.inventory.models import TonKho
from apps.promotions.models import KhuyenMai
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def seed_data():
    print("Xóa dữ liệu cũ...")
    TaiKhoan.objects.all().delete()
    NhanVien.objects.all().delete()
    Ban.objects.all().delete()
    ThucDon.objects.all().delete()
    TonKho.objects.all().delete()
    KhuyenMai.objects.all().delete()

    print("1. Tạo Tài khoản và Nhân viên...")
    # Manager
    tk_ql = TaiKhoan.objects.create(
        ten_dang_nhap='admin', 
        mat_khau=hash_password('123456'), 
        ma_phan_quyen=TaiKhoan.PhanQuyen.QUAN_LY
    )
    NhanVien.objects.create(ho_ten='Nguyễn Quản Lý', sdt='0901234567', ma_tk=tk_ql)

    # 3 Employees
    for i in range(1, 4):
        tk_nv = TaiKhoan.objects.create(
            ten_dang_nhap=f'staff0{i}', 
            mat_khau=hash_password('123456'), 
            ma_phan_quyen=TaiKhoan.PhanQuyen.NHAN_VIEN
        )
        NhanVien.objects.create(ho_ten=f'Trần Nhân Viên {i}', sdt=f'090900000{i}', ma_tk=tk_nv)

    print("2. Tạo Bàn (10 Bàn)...")
    for i in range(1, 6):
        Ban.objects.create(ten_khu_vuc=f'Bàn T{i:02d} (Trong nhà)')
    for i in range(1, 6):
        Ban.objects.create(ten_khu_vuc=f'Bàn O{i:02d} (Ngoài trời)')

    print("3. Tạo Thực Đơn (15 Món)...")
    menu_items = [
        # Coffee
        ('Cà phê Đen', 'Coffee', 25000), ('Cà phê Sữa', 'Coffee', 30000), 
        ('Bạc xỉu', 'Coffee', 35000), ('Espresso', 'Coffee', 40000), ('Americano', 'Coffee', 40000),
        # Tea
        ('Trà Đào Cam Sả', 'Tea', 45000), ('Trà Vải', 'Tea', 45000), 
        ('Trà Sen Vàng', 'Tea', 50000), ('Trà Ô Long', 'Tea', 40000), ('Lục Trà', 'Tea', 35000),
        # Juice
        ('Nước Ép Cam', 'Juice', 40000), ('Nước Ép Dưa Hấu', 'Juice', 40000),
        ('Nước Ép Thơm', 'Juice', 40000), ('Sinh tố Bơ', 'Juice', 50000), ('Sinh tố Dâu', 'Juice', 50000),
    ]
    for item in menu_items:
        ThucDon.objects.create(
            ten_mon=item[0], ma_loai=item[1], 
            don_gia=item[2], trang_thai=1
        )

    print("4. Tạo Kho Nguyên Liệu (5 Loại)...")
    inventory_items = [
        ('Hạt Cà phê', 'kg', 5, 2),
        ('Sữa đặc', 'lon', 50, 10),
        ('Đường cát', 'kg', 10, 3),
        ('Trà sấy', 'kg', 3, 1),
        ('Ly nhựa', 'cái', 1000, 200),
    ]
    for item in inventory_items:
        TonKho.objects.create(
            ten_nl=item[0], don_vi_tinh=item[1], 
            so_luong_ton=item[2], nguong_bao_dong=item[3]
        )

    print("5. Tạo Khuyến Mãi...")
    today = date.today()
    # Active Promo
    KhuyenMai.objects.create(
        ten_chuong_trinh='Giảm 20% Khai Trương',
        ngay_bd=today - timedelta(days=1), ngay_kt=today + timedelta(days=30),
        phan_tram_giam=20, dieu_kien_toi_thieu=100000, is_active=True
    )
    # Expired Promo
    KhuyenMai.objects.create(
        ten_chuong_trinh='Lì xì Tết',
        ngay_bd=today - timedelta(days=60), ngay_kt=today - timedelta(days=30),
        phan_tram_giam=15, dieu_kien_toi_thieu=50000, is_active=True
    )

    print("Hoàn tất Seed Data!")

if __name__ == '__main__':
    seed_data()
