<template>
  <nav :class="['navbar', { 'scrolled': isScrolled }]">
    <div class="container nav-content">
      <router-link to="/" class="logo">
        L'Aura Cafe
      </router-link>
      <div class="nav-links">
        <router-link to="/">Trang chủ</router-link>
        <router-link to="/about">Giới thiệu</router-link>
        <router-link to="/menu">Thực đơn</router-link>
        <router-link to="/contact">Liên hệ</router-link>
      </div>
      <router-link to="/menu" class="btn-primary nav-cta">Xem Menu</router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const isScrolled = ref(false);

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50;
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  padding: 20px 0;
  z-index: 1000;
  transition: all 0.3s ease;
  background: transparent;
}
.navbar.scrolled {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  padding: 15px 0;
  box-shadow: var(--shadow-sm);
  border-bottom: 1px solid var(--glass-border);
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-family: var(--font-heading);
  font-size: 28px;
  font-weight: 800;
  color: var(--secondary);
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 30px;
}
.nav-links a {
  font-weight: 500;
  color: var(--text-primary);
  position: relative;
}
.nav-links a::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -4px;
  left: 0;
  background-color: var(--primary);
  transition: width 0.3s ease;
}
.nav-links a:hover::after,
.nav-links a.router-link-exact-active::after {
  width: 100%;
}
.nav-links a.router-link-exact-active {
  color: var(--primary);
}

.nav-cta {
  padding: 10px 20px;
}

@media (max-width: 768px) {
  .nav-links, .nav-cta {
    display: none;
  }
}
</style>
