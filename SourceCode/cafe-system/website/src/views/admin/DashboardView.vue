<template>
  <div>
    <h2>Tổng Quan (Hôm nay)</h2>
    
    <div class="dashboard-stats">
      <div class="stat-card">
        <div class="stat-icon revenue">💰</div>
        <div class="stat-info">
          <h3>Doanh thu</h3>
          <p class="value">{{ formatPrice(dailyRevenue) }}đ</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orders">📝</div>
        <div class="stat-info">
          <h3>Hóa đơn</h3>
          <p class="value">{{ dailyOrders }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tables">🪑</div>
        <div class="stat-info">
          <h3>Bàn phục vụ</h3>
          <p class="value">{{ dailyOrders }}</p>
        </div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Biểu đồ -->
      <div class="card chart-card">
        <h3>Doanh thu 7 ngày qua</h3>
        <div class="chart-container">
          <Line v-if="chartLoaded" :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Cảnh báo & Top Món -->
      <div class="side-widgets">
        <div class="card alert-card">
          <h3 class="text-danger">⚠️ Cảnh báo Tồn kho</h3>
          <ul v-if="lowStock.length > 0" class="alert-list">
            <li v-for="item in lowStock" :key="item.ma_nl">
              <strong>{{ item.ten_nl }}</strong>: Còn {{ item.so_luong_ton }} {{ item.don_vi_tinh }} (Ngưỡng: {{ item.nguong_bao_dong }})
            </li>
          </ul>
          <p v-else class="text-success">Kho hàng an toàn.</p>
        </div>

        <div class="card top-card">
          <h3>🏆 Top 5 Món Bán Chạy (Tháng này)</h3>
          <ul class="top-list">
            <li v-for="(item, index) in topItems" :key="index">
              <span class="rank">#{{ index + 1 }}</span>
              <span class="name">{{ item.ten_mon }}</span>
              <span class="qty">{{ item.total_qty }} ly</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';
import { useAdminAuthStore } from '../../stores/adminAuth';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const adminStore = useAdminAuthStore();

// Trạng thái hiển thị
const dailyRevenue = ref(0);
const dailyOrders = ref(0);
const lowStock = ref([]);
const topItems = ref([]);

// Biểu đồ
const chartLoaded = ref(false);
const chartData = ref({ labels: [], datasets: [] });
const chartOptions = { responsive: true, maintainAspectRatio: false };

const fetchDashboardData = async () => {
  const headers = { Authorization: `Bearer ${adminStore.adminToken}` };
  
  try {
    // 1. Lấy doanh thu hôm nay
    const today = new Date().toISOString().split('T')[0];
    const resDaily = await api.get(`/api/reports/revenue/daily/?date=${today}`, { headers });
    if (resDaily.data.success) {
      dailyRevenue.value = resDaily.data.data.doanh_thu || 0;
      dailyOrders.value = resDaily.data.data.so_luong_hd || 0;
    }

    // 2. Lấy cảnh báo kho
    const resStock = await api.get('/api/inventory/alerts/', { headers });
    if (resStock.data.success) {
      lowStock.value = resStock.data.data;
    }

    // 3. Lấy Top món tháng này
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    const resTop = await api.get(`/api/reports/bestseller/?thang=${currentMonth}&nam=${currentYear}`, { headers });
    if (resTop.data.success) {
      topItems.value = resTop.data.data.slice(0, 5); // top 5
    }

    // 4. Lấy dữ liệu biểu đồ 7 ngày (Giả lập bằng API tháng)
    const resMonthly = await api.get(`/api/reports/revenue/monthly/?thang=${currentMonth}&nam=${currentYear}`, { headers });
    if (resMonthly.data.success) {
      const data = resMonthly.data.data;
      // Lấy 7 ngày cuối cùng có dữ liệu hoặc 7 ngày cuối tháng
      const last7 = data.slice(-7);
      
      chartData.value = {
        labels: last7.map(d => `Ngày ${d.day}`),
        datasets: [
          {
            label: 'Doanh thu (VNĐ)',
            backgroundColor: '#3498db',
            borderColor: '#3498db',
            data: last7.map(d => parseFloat(d.doanh_thu))
          }
        ]
      };
      chartLoaded.value = true;
    }

  } catch (err) {
    console.error("Lỗi lấy dữ liệu Dashboard", err);
  }
};

onMounted(() => {
  fetchDashboardData();
});

const formatPrice = (price) => {
  return Number(price).toLocaleString('vi-VN');
};
</script>

<style scoped>
.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.stat-icon {
  font-size: 40px;
  margin-right: 20px;
  width: 70px;
  height: 70px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
}
.stat-icon.revenue { background-color: #e8f8f5; color: #2ecc71; }
.stat-icon.orders { background-color: #ebf5fb; color: #3498db; }
.stat-icon.tables { background-color: #fef9e7; color: #f1c40f; }

.stat-info h3 { margin: 0; font-size: 16px; color: #7f8c8d; font-weight: normal;}
.stat-info .value { margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #2c3e50;}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}
.chart-card { min-height: 400px; }
.chart-container { height: 350px; position: relative;}

.side-widgets { display: flex; flex-direction: column; gap: 20px; }
.text-danger { color: #e74c3c; }
.text-success { color: #2ecc71; }
.alert-list { padding-left: 20px; margin: 10px 0 0 0;}
.alert-list li { margin-bottom: 8px; color: #c0392b;}

.top-list { list-style: none; padding: 0; margin: 0;}
.top-list li {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px dashed #eee;
}
.top-list li:last-child { border: none;}
.rank { font-weight: bold; color: #f39c12; width: 30px;}
.name { flex: 1; font-weight: 500;}
.qty { color: #7f8c8d; font-size: 14px;}
</style>
