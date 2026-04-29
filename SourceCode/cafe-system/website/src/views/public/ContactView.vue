<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Liên Hệ Với Chúng Tôi</h1>
    </div>

    <div class="container section-padding">
      <div class="contact-grid">
        <!-- Contact Info -->
        <div class="contact-info glass-card">
          <h2>Thông tin liên hệ</h2>
          <p class="desc">Chúng tôi luôn lắng nghe và sẵn sàng giải đáp mọi thắc mắc của bạn.</p>
          
          <div class="info-item">
            <span class="icon">📍</span>
            <div>
              <h4>Địa chỉ</h4>
              <p>123 Đường Sách, Quận 1, TP. Hồ Chí Minh</p>
            </div>
          </div>
          
          <div class="info-item">
            <span class="icon">📞</span>
            <div>
              <h4>Điện thoại</h4>
              <p>090 123 4567</p>
            </div>
          </div>
          
          <div class="info-item">
            <span class="icon">✉️</span>
            <div>
              <h4>Email</h4>
              <p>hello@lauracafe.vn</p>
            </div>
          </div>

          <div class="info-item">
            <span class="icon">🕒</span>
            <div>
              <h4>Giờ mở cửa</h4>
              <p>T2 - T6: 07:00 - 22:00<br>T7 - CN: 08:00 - 23:00</p>
            </div>
          </div>
        </div>

        <!-- Contact Form -->
        <div class="contact-form-wrapper glass-card">
          <h2>Gửi tin nhắn</h2>
          <form @submit.prevent="submitForm" class="contact-form">
            <div class="input-group">
              <input type="text" placeholder="Họ và tên" required />
            </div>
            <div class="input-group">
              <input type="email" placeholder="Email của bạn" required />
            </div>
            <div class="input-group">
              <textarea rows="5" placeholder="Nội dung tin nhắn..." required></textarea>
            </div>
            <button type="submit" class="btn-primary w-100">Gửi Tin Nhắn</button>
          </form>
        </div>
      </div>

      <!-- Google Maps -->
      <div class="map-container glass-card">
        <iframe 
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1m3!1d3919.4602324217154!2d106.69744131533413!3d10.776019492321852!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31752f385570472f%3A0x1787491df0ed8d6a!2sIndependence%20Palace!5e0!3m2!1sen!2s!4v1684300000000!5m2!1sen!2s" 
          width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade">
        </iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
const submitForm = () => {
  alert("Cảm ơn bạn! Tin nhắn của bạn đã được gửi. Chúng tôi sẽ phản hồi sớm nhất.");
};
</script>

<style scoped>
.page-container { padding-top: 80px; }
.page-header { background-color: var(--secondary); color: white; padding: 60px 20px; text-align: center; }
.page-header h1 { margin: 0; font-size: 40px;}
.section-padding { padding: 80px 20px; }

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 40px;
  margin-bottom: 60px;
}

/* Info */
.contact-info h2 { color: var(--primary); margin-bottom: 10px;}
.contact-info .desc { color: var(--text-secondary); margin-bottom: 30px;}
.info-item {
  display: flex;
  margin-bottom: 25px;
}
.icon { font-size: 24px; margin-right: 15px;}
.info-item h4 { margin: 0 0 5px 0; font-size: 18px; color: var(--secondary);}
.info-item p { margin: 0; color: var(--text-secondary);}

/* Form */
.contact-form-wrapper h2 { color: var(--secondary); margin-bottom: 25px;}
.input-group { margin-bottom: 20px; }
.input-group input, .input-group textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: var(--font-body);
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}
.input-group input:focus, .input-group textarea:focus {
  outline: none;
  border-color: var(--primary);
}
.w-100 { width: 100%; border-radius: 8px;}

/* Map */
.map-container { padding: 0; overflow: hidden;}
.map-container iframe { display: block; }

@media (max-width: 768px) {
  .contact-grid { grid-template-columns: 1fr; }
}
</style>
