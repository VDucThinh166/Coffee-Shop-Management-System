<template>
  <div class="checkout-shift-container">
    <div class="checkout-shift-card">
      <h2>Kết thúc ca làm việc</h2>
      <div class="shift-info">
        <p>Bạn sắp kết thúc ca làm việc hiện tại.</p>
        <p>Hệ thống sẽ ghi nhận giờ ra (checkout) cho tài khoản của bạn.</p>
      </div>
      
      <div v-if="error" class="error-box">{{ error }}</div>
      
      <div class="actions">
        <button class="btn-cancel" @click="goBack" :disabled="loading">Trở lại làm việc</button>
        <button class="btn-confirm" @click="endShift" :disabled="loading">
          {{ loading ? 'Đang xử lý...' : 'Xác nhận Kết thúc ca' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/axios';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const error = ref('');

const endShift = async () => {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.post('/api/attendance/checkout/');
    if (res.data.success) {
      alert("Kết thúc ca thành công! Đã ghi nhận giờ ra.");
      authStore.logout();
      router.push('/login');
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Có lỗi xảy ra khi kết thúc ca.';
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push('/tables');
};
</script>

<style scoped>
.checkout-shift-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #e74c3c;
}
.checkout-shift-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  width: 450px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
h2 {
  margin-top: 0;
  color: #c0392b;
}
.shift-info {
  margin: 30px 0;
  font-size: 16px;
  color: #555;
  line-height: 1.5;
}
.actions {
  display: flex;
  gap: 15px;
}
.btn-cancel {
  flex: 1;
  padding: 14px;
  background-color: #ecf0f1;
  color: #7f8c8d;
}
.btn-confirm {
  flex: 1;
  padding: 14px;
  background-color: #c0392b;
  color: white;
}
.error-box {
  background-color: #fee;
  color: #c0392b;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>
