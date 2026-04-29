<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Cafe POS System</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Tên đăng nhập</label>
          <input type="text" v-model="username" required placeholder="Nhập tài khoản..." />
        </div>
        <div class="form-group">
          <label>Mật khẩu</label>
          <input type="password" v-model="password" required placeholder="Nhập mật khẩu..." />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const router = useRouter();
const authStore = useAuthStore();

const handleLogin = async () => {
  error.value = '';
  loading.value = true;
  try {
    const success = await authStore.login(username.value, password.value);
    if (success) {
      router.push('/checkin');
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Đăng nhập thất bại. Vui lòng kiểm tra lại.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}
.login-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 400px;
  text-align: center;
}
h2 {
  margin-top: 0;
  color: #333;
  margin-bottom: 30px;
}
.form-group {
  margin-bottom: 20px;
  text-align: left;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-weight: 500;
}
.form-group input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}
.btn-primary {
  width: 100%;
  padding: 14px;
  background-color: #2c3e50;
  color: white;
  font-size: 16px;
  margin-top: 10px;
}
.error {
  color: #e74c3c;
  font-size: 14px;
  margin-bottom: 15px;
}
</style>
