<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Lịch Ca Làm Việc</h2>
      <button class="btn btn-success" @click="showModal = true">+ Thêm Ca Mới</button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Ngày Làm</th>
            <th>Nhân Viên</th>
            <th>Giờ Bắt Đầu</th>
            <th>Giờ Kết Thúc</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="shift in shifts" :key="shift.ma_ca">
            <td><strong>{{ shift.ngay_lam }}</strong></td>
            <td>{{ shift.ten_nhan_vien }}</td>
            <td>{{ shift.gio_bat_dau }}</td>
            <td>{{ shift.gio_ket_thuc }}</td>
          </tr>
          <tr v-if="shifts.length === 0">
            <td colspan="4" style="text-align: center;">Chưa có dữ liệu lịch ca.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card">
        <h3>Thêm Ca Làm</h3>
        <div class="form-group">
          <label>Nhân Viên</label>
          <select v-model="formData.ma_nv" class="form-control">
            <option v-for="nv in staffList" :key="nv.ma_nv" :value="nv.ma_nv">{{ nv.ho_ten }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Ngày làm (YYYY-MM-DD)</label>
          <input type="date" v-model="formData.ngay_lam" class="form-control" />
        </div>
        <div style="display: flex; gap: 10px;">
          <div class="form-group" style="flex:1">
            <label>Giờ bắt đầu</label>
            <input type="time" v-model="formData.gio_bat_dau" class="form-control" />
          </div>
          <div class="form-group" style="flex:1">
            <label>Giờ kết thúc</label>
            <input type="time" v-model="formData.gio_ket_thuc" class="form-control" />
          </div>
        </div>
        
        <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
          <button class="btn" @click="showModal = false">Hủy</button>
          <button class="btn btn-success" @click="saveShift">Lưu Ca</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api/axios';
import { useAdminAuthStore } from '../../stores/adminAuth';
import { toast } from 'vue3-toastify';

const adminStore = useAdminAuthStore();
const shifts = ref([]);
const staffList = ref([]);
const showModal = ref(false);

const formData = ref({
  ma_nv: '',
  ngay_lam: '',
  gio_bat_dau: '',
  gio_ket_thuc: ''
});

const getHeaders = () => ({ Authorization: `Bearer ${adminStore.adminToken}` });

const fetchData = async () => {
  try {
    const resShifts = await api.get('/api/shifts/', { headers: getHeaders() });
    if (resShifts.data.success) shifts.value = resShifts.data.data;

    const resStaff = await api.get('/api/staff/', { headers: getHeaders() });
    if (resStaff.data.success) staffList.value = resStaff.data.data;
  } catch (err) {
    toast.error("Lỗi tải dữ liệu");
  }
};

onMounted(() => { fetchData(); });

const saveShift = async () => {
  try {
    await api.post('/api/shifts/', formData.value, { headers: getHeaders() });
    toast.success("Thêm ca thành công!");
    showModal.value = false;
    fetchData();
  } catch (err) {
    toast.error(err.response?.data?.message || "Có lỗi xảy ra");
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-card {
  background: white; padding: 30px; border-radius: 8px; width: 500px;
}
</style>
