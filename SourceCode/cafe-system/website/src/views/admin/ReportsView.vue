<template>
  <div class="reports-page">
    <h2>Báo Cáo Thống Kê</h2>

    <!-- Controls -->
    <div class="card controls">
      <div class="tabs">
        <button :class="['tab-btn', activeTab === 'revenue' ? 'active' : '']" @click="activeTab = 'revenue'">Doanh thu</button>
        <button :class="['tab-btn', activeTab === 'bestseller' ? 'active' : '']" @click="activeTab = 'bestseller'">Bán chạy</button>
      </div>
      <div class="filters">
        <label>Chọn tháng:</label>
        <input type="month" v-model="selectedMonth" class="form-control" style="width: 200px; margin: 0 10px;" />
        <button class="btn btn-primary" @click="fetchData">Cập nhật dữ liệu</button>
      </div>
    </div>

    <!-- REVENUE TAB -->
    <div v-if="activeTab === 'revenue'" class="card">
      <h3>Doanh Thu Theo Tháng</h3>
      <div style="height: 400px; position: relative;">
        <Line v-if="chartData.labels" :data="chartData" :options="lineOptions" />
      </div>
    </div>

    <!-- BESTSELLER TAB -->
    <div v-if="activeTab === 'bestseller'" class="card">
      <h3>Top Sản Phẩm Bán Chạy</h3>
      <div style="height: 400px; position: relative;">
        <Bar v-if="barChartData.labels" :data="barChartData" :options="barOptions" />
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';
import { useAdminAuthStore } from '../../stores/adminAuth';
import { toast } from 'vue3-toastify';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend
} from 'chart.js';
import { Line, Bar } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const adminStore = useAdminAuthStore();
const activeTab = ref('revenue');
const selectedMonth = ref(new Date().toISOString().slice(0, 7)); // YYYY-MM

const chartData = ref({});
const barChartData = ref({});

const lineOptions = { responsive: true, maintainAspectRatio: false };
const barOptions = { responsive: true, maintainAspectRatio: false };

const getHeaders = () => ({ Authorization: `Bearer ${adminStore.adminToken}` });

const fetchData = async () => {
  const [year, month] = selectedMonth.value.split('-');
  try {
    // 1. Fetch Revenue
    const resRev = await api.get(`/api/reports/revenue/monthly/?thang=${month}&nam=${year}`, { headers: getHeaders() });
    if (resRev.data.success) {
      const data = resRev.data.data;
      chartData.value = {
        labels: data.map(d => `Ngày ${d.day}`),
        datasets: [{
          label: 'Doanh thu (VNĐ)',
          backgroundColor: '#27ae60',
          borderColor: '#2ecc71',
          data: data.map(d => parseFloat(d.doanh_thu)),
          tension: 0.3
        }]
      };
    }

    // 2. Fetch Bestsellers
    const resBest = await api.get(`/api/reports/bestseller/?thang=${month}&nam=${year}`, { headers: getHeaders() });
    if (resBest.data.success) {
      const data = resBest.data.data.slice(0, 10);
      barChartData.value = {
        labels: data.map(d => d.ten_mon),
        datasets: [{
          label: 'Số lượng bán',
          backgroundColor: '#e67e22',
          data: data.map(d => d.total_qty)
        }]
      };
    }
  } catch (err) {
    toast.error("Lỗi lấy dữ liệu báo cáo");
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.controls { display: flex; justify-content: space-between; align-items: center; }
.tabs { display: flex; gap: 10px; }
.tab-btn {
  padding: 10px 20px;
  background: #ecf0f1;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  color: #7f8c8d;
}
.tab-btn.active {
  background: #34495e;
  color: white;
}
.filters { display: flex; align-items: center; }
</style>
