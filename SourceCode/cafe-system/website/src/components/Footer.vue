<template>
  <footer class="footer">
    <div class="container footer-content">
      <div class="footer-col brand">
        <h2 class="logo">L'Aura Cafe</h2>
        <p>Nơi đánh thức mọi giác quan qua từng giọt cà phê nguyên bản và không gian thư giãn tuyệt đối.</p>
      </div>
      <div class="footer-col links">
        <h3>Liên kết</h3>
        <router-link to="/">Trang chủ</router-link>
        <router-link to="/about">Giới thiệu</router-link>
        <router-link to="/menu">Thực đơn</router-link>
        <router-link to="/contact">Liên hệ</router-link>
      </div>
      <div class="footer-col contact">
        <h3>Liên hệ</h3>
        <p>📍 123 Đường Sách, Quận 1, TP. HCM</p>
        <p>📞 090 123 4567</p>
        <p>✉️ hello@lauracafe.vn</p>
      </div>
      <div class="footer-col hours">
        <h3>Giờ mở cửa</h3>
        <p>Thứ 2 - Thứ 6: 07:00 - 22:00</p>
        <p>Thứ 7 - CN: 08:00 - 23:00</p>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 L'Aura Cafe. All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background-color: var(--secondary);
  color: white;
  padding-top: 60px;
  margin-top: auto;
}
.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}
.logo {
  color: var(--primary);
  font-size: 28px;
  margin-bottom: 15px;
}
.footer-col h3 {
  font-size: 18px;
  color: #fff;
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
}
.footer-col h3::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 40px;
  height: 2px;
  background-color: var(--primary);
}
.footer-col p {
  color: #bdc3c7;
  margin-bottom: 10px;
}
.links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.links a {
  color: #bdc3c7;
}
.links a:hover {
  color: var(--primary);
  padding-left: 5px;
}
.footer-bottom {
  text-align: center;
  padding: 20px 0;
  border-top: 1px solid rgba(255,255,255,0.1);
  color: #7f8c8d;
  font-size: 14px;
}

@media (max-width: 992px) {
  .footer-content {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 576px) {
  .footer-content {
    grid-template-columns: 1fr;
  }
}
</style>
