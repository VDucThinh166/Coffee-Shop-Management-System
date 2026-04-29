# L'Aura Cafe Management System

Hệ thống quản lý quán Cafe toàn diện bao gồm:
1. **Backend**: RESTful API viết bằng Django 4.2 + MySQL.
2. **POS App**: Ứng dụng Web dành cho nhân viên bán hàng (Vue.js 3).
3. **Website & Admin**: Website quảng bá quán và Bảng điều khiển Quản trị (Vue.js 3).

## Hướng dẫn chạy dự án bằng Docker (Cách dễ nhất)

Bạn cần cài đặt sẵn **Docker** và **Docker Desktop** trên máy.

### Bước 1: Mở Terminal ở đúng thư mục
Dự án nằm trong thư mục `SourceCode/cafe-system`. Hãy mở Terminal (hoặc PowerShell) và điều hướng vào đúng thư mục này:
```bash
cd "SourceCode/cafe-system"
```

*(Lưu ý: File `docker-compose.yml` phải nằm ở ngay thư mục bạn đang đứng)*

### Bước 2: Build và Khởi động toàn bộ hệ thống
Gõ lệnh sau và đợi Docker tự động cài đặt mọi thứ (Python, Node.js, Nginx, MySQL):
```bash
docker-compose up --build -d
```
*(Cờ `-d` giúp hệ thống chạy ngầm để bạn không bị treo Terminal).*

Quá trình này có thể mất 3-5 phút trong lần chạy đầu tiên vì Docker phải tải các image về máy. Backend sẽ tự động chạy các lệnh cấu hình database và tạo dữ liệu mẫu (Seed Data).

### Bước 3: Truy cập Ứng dụng
Sau khi lệnh chạy xong (báo `Started` cho cả 4 services), bạn mở trình duyệt và truy cập:

1. **Website Khách hàng**: http://localhost:5174
2. **Admin Dashboard (Quản lý)**: http://localhost:5174/admin/login
   - Tên đăng nhập: `admin`
   - Mật khẩu: `123456`
3. **POS Bán hàng (Nhân viên)**: http://localhost:5173
   - Tên đăng nhập: `staff01` (hoặc `staff02`, `staff03`)
   - Mật khẩu: `123456`
4. **Backend API**: http://localhost:8000/api/

---

## Hướng dẫn chạy dự án thủ công (Không dùng Docker)

Nếu bạn không muốn dùng Docker, hãy làm theo các bước sau (Yêu cầu phải có Python 3.10+ và Node.js 20+):

### 1. Khởi động Backend (Django)
```bash
cd SourceCode/cafe-system/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate --settings=config.settings_dev
python seed.py
python manage.py runserver 8000
```

### 2. Khởi động POS App
Mở một Terminal khác:
```bash
cd SourceCode/cafe-system/pos-app
npm install
npm run dev
```

### 3. Khởi động Website & Admin
Mở một Terminal khác nữa:
```bash
cd SourceCode/cafe-system/website
npm install
npm run dev
```
Đường dẫn truy cập sẽ tương tự như phần Docker.
