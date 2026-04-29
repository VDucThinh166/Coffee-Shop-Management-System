<template>
  <div class="admin-login-wrapper">
    <div class="admin-login-card">
      <div class="brand">
        <h2>Hệ Thống Quản Trị</h2>
        <p>L'Aura Cafe</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>Tài khoản Quản lý</label>
          <input type="text" v-model="username" required placeholder="Nhập tên đăng nhập" class="form-control" />
        </div>
        <div class="form-group">
          <label>Mật khẩu</label>
          <input type="password" v-model="password" required placeholder="Nhập mật khẩu" class="form-control" />
        </div>
        
        <div v-if="error" class="error-msg">{{ error }}</div>
        
        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          {{ loading ? 'Đang xác thực...' : 'Đăng nhập Admin' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAdminAuthStore } from '../../stores/adminAuth';

const router = useRouter();
const adminStore = useAdminAuthStore();

const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  error.value = '';
  loading.value = true;
  try {
    const success = await adminStore.login(username.value, password.value);
    if (success) {
      router.push('/admin/dashboard');
    }
  } catch (err) {
    error.value = err.message || err.response?.data?.message || 'Đăng nhập thất bại!';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.admin-login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2c3e50;
  font-family: 'Inter', sans-serif;
}
.admin-login-card {
  background: white;
  width: 400px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  overflow: hidden;
}
.brand {
  background-color: #1a252f;
  color: white;
  padding: 30px 20px;
  text-align: center;
}
.brand h2 { margin: 0 0 10px 0; color: #d3a17e; font-family: 'Outfit', sans-serif;}
.brand p { margin: 0; color: #bdc3c7;}

.login-form {
  padding: 30px;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #34495e;
}
.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}
.error-msg {
  color: #e74c3c;
  background-color: #fce4e4;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}
.w-100 { width: 100%; padding: 14px; font-size: 16px;}
.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-primary:hover { background-color: #2980b9;}
</style>
