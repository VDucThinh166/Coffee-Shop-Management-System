<template>
  <div class="checkin-container">
    <div class="checkin-card">
      <h2>Bắt đầu Ca Làm Việc</h2>
      <div class="time-display">{{ currentTime }}</div>
      
      <div v-if="error" class="error-box">{{ error }}</div>
      <div v-if="successMsg" class="success-box">{{ successMsg }}</div>

      <button @click="startShift" class="btn-checkin" :disabled="loading">
        {{ loading ? 'Đang xử lý...' : 'Chấm công (Bắt đầu)' }}
      </button>

      <button @click="skipToCheckin" class="btn-skip">
        Bỏ qua (Tiếp tục vào Sơ đồ Bàn)
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/axios';

const router = useRouter();
const currentTime = ref('');
const loading = ref(false);
const error = ref('');
const successMsg = ref('');
let timer = null;

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('vi-VN') + ' - ' + now.toLocaleDateString('vi-VN');
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});

const startShift = async () => {
  loading.value = true;
  error.value = '';
  successMsg.value = '';
  try {
    const res = await api.post('/api/attendance/checkin/');
    if (res.data.success) {
      successMsg.value = `Chấm công thành công! Trạng thái: ${res.data.data.trang_thai}`;
      setTimeout(() => {
        router.push('/tables');
      }, 1500);
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Có lỗi xảy ra khi chấm công.';
  } finally {
    loading.value = false;
  }
};

const skipToCheckin = () => {
  router.push('/tables');
};
</script>

<style scoped>
.checkin-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2c3e50;
}
.checkin-card {
  background: white;
  padding: 50px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 15px 30px rgba(0,0,0,0.2);
  width: 500px;
}
h2 {
  color: #333;
  margin-top: 0;
}
.time-display {
  font-size: 28px;
  font-weight: bold;
  color: #e67e22;
  margin: 30px 0;
}
.btn-checkin {
  width: 100%;
  padding: 16px;
  background-color: #27ae60;
  color: white;
  font-size: 18px;
  margin-bottom: 15px;
}
.btn-skip {
  width: 100%;
  padding: 16px;
  background-color: transparent;
  color: #7f8c8d;
  border: 1px solid #bdc3c7;
  font-size: 16px;
}
.btn-skip:hover {
  background-color: #f5f6fa;
}
.error-box {
  background-color: #fee;
  color: #c0392b;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.success-box {
  background-color: #e8f8f5;
  color: #16a085;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
}
</style>
