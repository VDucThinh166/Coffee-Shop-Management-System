<template>
  <div class="layout-container">
    <header class="pos-header">
      <div class="logo">Cafe POS</div>
      <div class="actions">
        <button class="btn-warning" @click="handleCheckoutShift">Kết thúc ca</button>
        <button class="btn-danger" @click="handleLogout">Đăng xuất</button>
      </div>
    </header>

    <div class="main-content">
      <div class="sidebar">
        <h3>Ghi chú bàn</h3>
        <ul class="legend">
          <li><span class="color-box empty"></span> Trống (0)</li>
          <li><span class="color-box occupied"></span> Có khách (1)</li>
          <li><span class="color-box cleaning"></span> Đang dọn (2)</li>
        </ul>
        <div class="table-actions">
          <button class="btn-info" @click="transferModal = true">Chuyển bàn</button>
          <button class="btn-info" @click="mergeModal = true">Gộp bàn</button>
        </div>
      </div>

      <div class="map-area">
        <h2 style="margin-top: 0;">Sơ đồ Bàn</h2>
        <div v-if="loading" class="loading">Đang tải sơ đồ...</div>
        
        <div v-else class="table-grid">
          <div 
            v-for="ban in tables" 
            :key="ban.ma_ban"
            class="table-card"
            :class="getStatusClass(ban.trang_thai)"
            @click="handleTableClick(ban)"
          >
            <div class="table-name">Bàn {{ ban.ma_ban }}</div>
            <div class="table-zone">{{ ban.ten_khu_vuc }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/axios';
import { useAuthStore } from '../stores/auth';
import { useOrderStore } from '../stores/order';

const router = useRouter();
const authStore = useAuthStore();
const orderStore = useOrderStore();

const tables = ref([]);
const loading = ref(true);

const transferModal = ref(false);
const mergeModal = ref(false);

const fetchTables = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/tables/');
    if (res.data.success) {
      tables.value = res.data.data;
    }
  } catch (err) {
    console.error("Failed to load tables", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchTables();
});

const getStatusClass = (status) => {
  // 0=Trống, 1=Có khách, 2=Đang dọn
  if (status === 0) return 'status-empty';
  if (status === 1) return 'status-occupied';
  if (status === 2) return 'status-cleaning';
  return '';
};

const handleTableClick = async (ban) => {
  if (ban.trang_thai === 2) {
    alert("Bàn đang dọn, vui lòng chờ!");
    return;
  }

  if (ban.trang_thai === 0) {
    // Tạo hóa đơn mới
    try {
      const res = await api.post('/api/orders/', { ma_ban: ban.ma_ban });
      if (res.data.success) {
        orderStore.setOrder(ban.ma_ban, res.data.data.ma_hd, [], res.data.data.hang_khach_hang);
        router.push('/order');
      }
    } catch (err) {
      alert(err.response?.data?.message || "Lỗi tạo hóa đơn");
    }
  } else if (ban.trang_thai === 1) {
    // Tìm hóa đơn đang mở của bàn này
    try {
      const res = await api.get(`/api/orders/?ban=${ban.ma_ban}&trang_thai=Chờ pha chế`);
      if (res.data.success && res.data.data.length > 0) {
        const order = res.data.data[0];
        orderStore.setOrder(ban.ma_ban, order.ma_hd, order.chi_tiet, order.hang_khach_hang);
        router.push('/order');
      } else {
        alert("Không tìm thấy hóa đơn mở cho bàn này!");
      }
    } catch (err) {
      console.error(err);
    }
  }
};

const handleCheckoutShift = () => {
  router.push('/checkout-shift');
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.pos-header {
  background-color: #2c3e50;
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 1px;
}
.actions button {
  padding: 8px 16px;
  margin-left: 10px;
}
.btn-warning { background-color: #f39c12; color: white; }
.btn-danger { background-color: #e74c3c; color: white; }
.btn-info { background-color: #3498db; color: white; width: 100%; padding: 12px; margin-bottom: 10px;}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.sidebar {
  width: 250px;
  background-color: white;
  border-right: 1px solid #ddd;
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.legend {
  list-style: none;
  padding: 0;
  margin-bottom: 40px;
}
.legend li {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 16px;
}
.color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  margin-right: 10px;
}
.empty { background-color: #2ecc71; }
.occupied { background-color: #e74c3c; }
.cleaning { background-color: #f1c40f; }

.map-area {
  flex: 1;
  padding: 20px;
  background-color: #ecf0f1;
  overflow-y: auto;
}
.table-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
}
.table-card {
  height: 120px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  color: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.1s;
}
.table-card:hover {
  transform: scale(1.05);
}
.table-card .table-name {
  font-size: 20px;
  font-weight: bold;
}
.table-card .table-zone {
  font-size: 14px;
  opacity: 0.8;
  margin-top: 5px;
}

.status-empty { background-color: #2ecc71; }
.status-occupied { background-color: #e74c3c; }
.status-cleaning { background-color: #f1c40f; color: #333; }
</style>
