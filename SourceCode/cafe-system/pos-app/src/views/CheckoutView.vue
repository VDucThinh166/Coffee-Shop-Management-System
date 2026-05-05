<template>
  <div class="checkout-container">
    <div class="checkout-card">
      <header class="header">
        <button class="btn-back" @click="goBack">← Trở lại</button>
        <h2>Thanh toán Hóa đơn {{ orderStore.currentOrderId }}</h2>
        <div></div>
      </header>

      <div class="checkout-body">
        <div class="summary-section">
          <h3>Tổng quan</h3>
          <div class="summary-row">
            <span>Tạm tính:</span>
            <span class="price">{{ formatPrice(subtotal) }}đ</span>
          </div>
          <div class="summary-row discount">
            <span>Giảm giá ({{ discountPercent }}%):</span>
            <span class="price">-{{ formatPrice(discountAmount) }}đ</span>
          </div>
          <div class="summary-row total">
            <span>Thành tiền:</span>
            <span class="price final">{{ formatPrice(finalTotal) }}đ</span>
          </div>
        </div>

        <div class="form-section">
          <div class="form-group">
            <label>Mã Voucher (Nếu có)</label>
            <select v-model="selectedVoucher" @change="calculateMockDiscount">
              <option value="">-- Không dùng voucher --</option>
              <option v-for="v in activePromotions" :key="v.ma_km" :value="v.ma_km">
                {{ v.ten_chuong_trinh }} (Giảm {{ v.phan_tram_giam }}%)
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Phương thức thanh toán</label>
            <select v-model="paymentMethod">
              <option value="Tiền mặt">Tiền mặt</option>
              <option value="Chuyển khoản">Chuyển khoản</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <button class="btn-confirm" @click="confirmPayment" :disabled="loading">
        {{ loading ? 'Đang xử lý...' : 'XÁC NHẬN THANH TOÁN' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/axios';
import { useOrderStore } from '../stores/order';

const router = useRouter();
const orderStore = useOrderStore();

const activePromotions = ref([]);
const selectedVoucher = ref('');
const paymentMethod = ref('Tiền mặt');
const loading = ref(false);
const error = ref('');

// Discount logic locally before confirm for real-time preview
// This is a simplified preview. The backend is the ultimate source of truth.
const discountPercent = ref(0);

onMounted(() => {
  if (!orderStore.currentOrderId) {
    router.push('/tables');
    return;
  }
  fetchPromotions();
});

const fetchPromotions = async () => {
  try {
    const res = await api.get('/api/promotions/active/');
    if (res.data.success) {
      activePromotions.value = res.data.data;
    }
  } catch (err) {
    console.error("Lỗi lấy voucher", err);
  }
};

const subtotal = computed(() => {
  return orderStore.orderItems.reduce((acc, curr) => acc + parseFloat(curr.thanh_tien), 0);
});

const calculateMockDiscount = () => {
  // Logic giả lập hiển thị dựa theo Decision Table (Backend sẽ tính chuẩn xác)
  let percent = 0;
  if (subtotal.value >= 500000 && selectedVoucher.value) percent = 15; // Giả lập KH thường
  else if (subtotal.value >= 500000) percent = 10;
  discountPercent.value = percent;
};

const discountAmount = computed(() => {
  return (subtotal.value * discountPercent.value) / 100;
});

const finalTotal = computed(() => {
  return subtotal.value - discountAmount.value;
});

const confirmPayment = async () => {
  loading.value = true;
  error.value = '';
  try {
    const payload = {
      phuong_thuc: paymentMethod.value
    };
    if (selectedVoucher.value) {
      payload.promotion_code = selectedVoucher.value;
    }

    const res = await api.post(`/api/orders/${orderStore.currentOrderId}/checkout/`, payload);
    
    if (res.data.success) {
      alert(`Thanh toán thành công! Khách được cộng ${res.data.checkout_summary.points_earned} điểm.`);
      orderStore.clearOrder();
      router.push('/tables');
    }
  } catch (err) {
    error.value = err.response?.data?.message || 'Có lỗi xảy ra khi thanh toán.';
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push('/order');
};

const formatPrice = (price) => {
  return Number(price).toLocaleString('vi-VN');
};
</script>

<style scoped>
.checkout-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #34495e;
}
.checkout-card {
  background: white;
  width: 600px;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #ecf0f1;
  border-bottom: 1px solid #ddd;
}
.header h2 { margin: 0; font-size: 20px; }
.btn-back { background: transparent; border: 1px solid #95a5a6; padding: 8px 12px; color: #34495e;}

.checkout-body {
  padding: 30px;
}
.summary-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}
.summary-section h3 { margin-top: 0; color: #7f8c8d; font-size: 16px; text-transform: uppercase; }
.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 18px;
}
.summary-row.discount { color: #e67e22; }
.summary-row.total { 
  margin-top: 15px; 
  padding-top: 15px; 
  border-top: 2px dashed #ddd; 
  font-weight: bold; 
  font-size: 24px;
}
.price.final { color: #c0392b; }

.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
}
.form-group select {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.error-msg {
  color: #c0392b;
  text-align: center;
  margin-bottom: 15px;
  padding: 0 20px;
}

.btn-confirm {
  background-color: #27ae60;
  color: white;
  padding: 20px;
  font-size: 20px;
  border-radius: 0; /* flat bottom */
}
.btn-confirm:disabled { background-color: #95a5a6; }
</style>
