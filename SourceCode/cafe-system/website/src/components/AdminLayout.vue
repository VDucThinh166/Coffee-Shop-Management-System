<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <h2>L'Aura Admin</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin/dashboard" class="nav-item">📊 Tổng quan</router-link>
        <router-link to="/admin/staff" class="nav-item">👥 Nhân sự</router-link>
        <router-link to="/admin/shifts" class="nav-item">📅 Ca làm việc</router-link>
        <router-link to="/admin/attendance" class="nav-item">⏱️ Chấm công</router-link>
        <router-link to="/admin/menu" class="nav-item">☕ Thực đơn</router-link>
        <router-link to="/admin/inventory" class="nav-item">📦 Kho hàng</router-link>
        <router-link to="/admin/promotions" class="nav-item">🎟️ Khuyến mãi</router-link>
        <router-link to="/admin/customers" class="nav-item">👑 Khách VIP</router-link>
        <router-link to="/admin/reports" class="nav-item">📈 Báo cáo</router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="handleLogout" class="btn-logout">Đăng xuất</button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="admin-main">
      <header class="admin-header">
        <div class="header-title">Hệ thống Quản lý</div>
        <div class="header-user">
          Xin chào, <strong>Quản lý</strong>
        </div>
      </header>
      
      <div class="admin-content">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAdminAuthStore } from '../stores/adminAuth';

const router = useRouter();
const adminAuthStore = useAdminAuthStore();

const handleLogout = () => {
  adminAuthStore.logout();
  router.push('/admin/login');
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: #f4f6f9;
  font-family: 'Inter', sans-serif;
  color: #333;
}

/* Sidebar */
.admin-sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.sidebar-brand {
  padding: 20px;
  background-color: #1a252f;
  text-align: center;
}
.sidebar-brand h2 {
  margin: 0;
  font-size: 24px;
  color: #d3a17e;
  font-family: 'Outfit', sans-serif;
}
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  overflow-y: auto;
}
.nav-item {
  padding: 12px 20px;
  color: #bdc3c7;
  text-decoration: none;
  font-size: 15px;
  transition: all 0.3s;
  border-left: 4px solid transparent;
}
.nav-item:hover {
  background-color: rgba(255,255,255,0.05);
  color: white;
}
.nav-item.router-link-active {
  background-color: #34495e;
  color: white;
  border-left-color: #3498db;
  font-weight: 600;
}
.sidebar-footer {
  padding: 20px;
  background-color: #1a252f;
}
.btn-logout {
  width: 100%;
  padding: 10px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-logout:hover {
  background-color: #c0392b;
}

/* Main Area */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.admin-header {
  height: 60px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  z-index: 10;
}
.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}
.header-user {
  font-size: 14px;
}
.admin-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

/* Global Admin CSS Utilities */
:deep(.card) {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 20px;
  margin-bottom: 20px;
}
:deep(.table) {
  width: 100%;
  border-collapse: collapse;
}
:deep(.table th, .table td) {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}
:deep(.table th) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}
:deep(.btn) {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}
:deep(.btn-primary) { background: #3498db; color: white; }
:deep(.btn-danger) { background: #e74c3c; color: white; }
:deep(.btn-success) { background: #2ecc71; color: white; }
:deep(input.form-control) {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 15px;
}
</style>
