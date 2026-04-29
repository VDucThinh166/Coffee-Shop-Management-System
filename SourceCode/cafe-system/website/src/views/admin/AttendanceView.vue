<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Bảng Chấm Công</h2>
      <div style="display: flex; gap: 10px;">
        <input type="month" v-model="selectedMonth" class="form-control" style="width: auto; margin:0;" @change="fetchAttendance" />
        <button class="btn btn-primary" @click="exportExcel">Xuất Excel</button>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Ngày</th>
            <th>Nhân Viên</th>
            <th>Ca Làm</th>
            <th>Giờ Vào</th>
            <th>Giờ Ra</th>
            <th>Trạng Thái</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="att in attendanceRecords" :key="att.id">
            <td>{{ att.ca_lam.ngay_lam }}</td>
            <td><strong>{{ att.ca_lam.ten_nhan_vien }}</strong></td>
            <td>{{ att.ca_lam.gio_bat_dau }} - {{ att.ca_lam.gio_ket_thuc }}</td>
            <td>{{ att.gio_vao_thuc || '--:--' }}</td>
            <td>{{ att.gio_ra_thuc || '--:--' }}</td>
            <td>
              <span :class="getStatusBadgeClass(att.trang_thai)">
                {{ att.trang_thai }}
              </span>
            </td>
          </tr>
          <tr v-if="attendanceRecords.length === 0">
            <td colspan="6" style="text-align: center;">Chưa có dữ liệu chấm công.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';
import { useAdminAuthStore } from '../../stores/adminAuth';
import { toast } from 'vue3-toastify';

const adminStore = useAdminAuthStore();
const attendanceRecords = ref([]);
const selectedMonth = ref(new Date().toISOString().slice(0, 7)); // YYYY-MM

const getHeaders = () => ({ Authorization: `Bearer ${adminStore.adminToken}` });

const fetchAttendance = async () => {
  try {
    const res = await api.get(`/api/attendance/`, { headers: getHeaders() });
    if (res.data.success) {
      // Lọc theo tháng ở Frontend cho nhanh (Hoặc truyền params lên backend)
      const targetMonth = selectedMonth.value;
      attendanceRecords.value = res.data.data.filter(att => 
        att.ca_lam.ngay_lam.startsWith(targetMonth)
      );
    }
  } catch (err) {
    toast.error("Lỗi tải bảng chấm công");
  }
};

onMounted(() => {
  fetchAttendance();
});

const getStatusBadgeClass = (status) => {
  if (status === 'Đúng giờ') return 'badge badge-success';
  if (status === 'Vắng') return 'badge badge-danger';
  if (status.includes('Đi trễ')) return 'badge badge-warning';
  return 'badge badge-secondary';
};

const exportExcel = () => {
  toast.info("Tính năng xuất Excel đang được nâng cấp!");
};
</script>

<style scoped>
.badge {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}
.badge-success { background-color: #d4edda; color: #155724; }
.badge-danger { background-color: #f8d7da; color: #721c24; }
.badge-warning { background-color: #fff3cd; color: #856404; }
.badge-secondary { background-color: #e2e3e5; color: #383d41; }
</style>
