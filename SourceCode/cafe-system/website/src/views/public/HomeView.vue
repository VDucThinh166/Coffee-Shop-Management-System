<template>
  <div>
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-overlay"></div>
      <div class="container hero-content animate-fade-in">
        <h1 class="hero-title">Đánh Thức Vị Giác<br>Trong Không Gian Tĩnh Lặng</h1>
        <p class="hero-subtitle">Thưởng thức ly cà phê đậm vị được pha chế từ những hạt cà phê hảo hạng nhất.</p>
        <router-link to="/menu" class="btn-primary">Khám Phá Thực Đơn</router-link>
      </div>
    </section>

    <!-- Intro Section -->
    <section class="intro container section-padding">
      <div class="intro-grid">
        <div class="intro-text">
          <h2 class="section-title">Nghệ thuật nguyên bản</h2>
          <p>Tại L'Aura Cafe, chúng tôi tin rằng mỗi tách cà phê là một tác phẩm nghệ thuật. Từ việc chọn lọc kỹ lưỡng từng hạt cà phê, rang xay thủ công cho đến khâu pha chế tỉ mỉ, mọi thứ đều được thực hiện với tình yêu và niềm đam mê mãnh liệt.</p>
          <router-link to="/about" class="read-more">Tìm hiểu câu chuyện của chúng tôi →</router-link>
        </div>
        <div class="intro-img-wrapper">
          <div class="intro-img">☕ Cà phê nguyên chất</div>
        </div>
      </div>
    </section>

    <!-- Featured Menu -->
    <section class="featured-menu bg-light section-padding">
      <div class="container">
        <div class="section-header center">
          <h2 class="section-title">Món Nổi Bật</h2>
          <p>Những hương vị được yêu thích nhất tại L'Aura Cafe</p>
        </div>
        
        <div class="menu-grid">
          <div v-for="item in featuredItems" :key="item.ma_mon" class="glass-card menu-card">
            <div class="card-img-placeholder">
              <img v-if="item.hinh_anh" :src="item.hinh_anh" alt="" class="real-img"/>
              <span v-else>🍰</span>
            </div>
            <div class="card-content">
              <h3>{{ item.ten_mon }}</h3>
              <p class="price">{{ formatPrice(item.don_gia) }}đ</p>
              <p class="desc">{{ item.mo_ta || 'Hương vị tuyệt hảo.' }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';

const featuredItems = ref([]);

const fetchFeatured = async () => {
  try {
    // API giả lập: lấy toàn bộ rồi random 3 món, vì backend hiện chưa có filter noi_bat=true
    const res = await api.get('/api/menu/');
    if (res.data.success) {
      const all = res.data.data;
      featuredItems.value = all.sort(() => 0.5 - Math.random()).slice(0, 3);
    }
  } catch (error) {
    console.error("Lỗi tải món nổi bật:", error);
  }
};

onMounted(() => {
  fetchFeatured();
});

const formatPrice = (price) => {
  return Number(price).toLocaleString('vi-VN');
};
</script>

<style scoped>
.section-padding { padding: 100px 0; }
.bg-light { background-color: #F8F9FA; }
.section-title { font-size: 36px; color: var(--secondary); margin-bottom: 20px;}
.section-header.center { text-align: center; margin-bottom: 50px; }

/* Hero */
.hero {
  height: 100vh;
  min-height: 600px;
  background: url('https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&q=80') center/cover;
  position: relative;
  display: flex;
  align-items: center;
}
.hero-overlay {
  position: absolute;
  top:0; left:0; width:100%; height:100%;
  background: linear-gradient(to right, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.3) 100%);
}
.hero-content {
  position: relative;
  z-index: 1;
  color: white;
  max-width: 600px;
}
.hero-title {
  font-size: 56px;
  line-height: 1.1;
  margin-bottom: 20px;
  font-weight: 800;
}
.hero-subtitle {
  font-size: 20px;
  color: #ecf0f1;
  margin-bottom: 40px;
  font-weight: 300;
}

/* Intro */
.intro-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}
.intro-text p { font-size: 18px; color: var(--text-secondary); margin-bottom: 30px;}
.read-more { color: var(--primary); font-weight: 600; font-size: 18px; }
.read-more:hover { color: var(--primary-hover); letter-spacing: 0.5px;}
.intro-img-wrapper { height: 400px; border-radius: 20px; overflow: hidden; background: #eee;}
.intro-img { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; font-size: 30px; background: var(--secondary); color: white;}

/* Menu Cards */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}
.menu-card { padding: 0; overflow: hidden;}
.card-img-placeholder { height: 250px; background: #e0e0e0; display: flex; justify-content: center; align-items: center; font-size: 50px;}
.real-img { width: 100%; height: 100%; object-fit: cover; }
.card-content { padding: 30px; text-align: center;}
.card-content h3 { font-size: 24px; margin-bottom: 10px; }
.price { color: var(--primary); font-size: 22px; font-weight: 800; margin-bottom: 15px; }
.desc { color: var(--text-secondary); font-size: 15px; }

@media (max-width: 768px) {
  .hero-title { font-size: 40px; }
  .intro-grid { grid-template-columns: 1fr; gap: 30px;}
  .menu-grid { grid-template-columns: 1fr; }
}
</style>
