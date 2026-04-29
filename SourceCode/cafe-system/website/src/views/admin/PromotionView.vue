<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Quản lý Khuyến Mãi (Voucher)</h2>
      <button class="btn btn-success" @click="showModal = true">+ Thêm Chương Trình</button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Mã KM</th>
            <th>Tên Chương Trình</th>
            <th>Ngày Bắt Đầu</th>
            <th>Ngày Kết Thúc</th>
            <th>Giảm %</th>
            <th>Điều Kiện (VNĐ)</th>
            <th>Tình Trạng</th>
            <th>Kích Hoạt</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="promo in promotions" :key="promo.ma_km">
            <td><strong>{{ promo.ma_km }}</strong></td>
            <td>{{ promo.ten_chuong_trinh }}</td>
            <td>{{ promo.ngay_bd }}</td>
            <td>{{ promo.ngay_kt }}</td>
            <td style="color: #e67e22; font-weight: bold;">{{ promo.phan_tram_giam }}%</td>
            <td>{{ formatPrice(promo.dieu_kien_toi_thieu) }}</td>
            <td>
              <span :class="getStatusClass(promo)">{{ getStatusText(promo) }}</span>
            </td>
            <td>
              <input type="checkbox" :checked="promo.is_active" @change="toggleActive(promo)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card">
        <h3>Thêm Khuyến Mãi Mới</h3>
        <form @submit.prevent="savePromo">
          <div class="form-group"><label>Tên CT</label><input type="text" v-model="formData.ten_chuong_trinh" class="form-control" required></div>
          <div style="display:flex; gap:10px;">
            <div class="form-group" style="flex:1"><label>Ngày BĐ</label><input type="date" v-model="formData.ngay_bd" class="form-control" required></div>
            <div class="form-group" style="flex:1"><label>Ngày KT</label><input type="date" v-model="formData.ngay_kt" class="form-control" required></div>
          </div>
          <div style="display:flex; gap:10px;">
            <div class="form-group" style="flex:1"><label>% Giảm (1-100)</label><input type="number" v-model="formData.phan_tram_giam" class="form-control" min="1" max="100" required></div>
            <div class="form-group" style="flex:1"><label>ĐK tối thiểu</label><input type="number" v-model="formData.dieu_kien_toi_thieu" class="form-control" required></div>
          </div>
          <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
            <button type="button" class="btn" @click="showModal = false">Hủy</button>
            <button type="submit" class="btn btn-success">Lưu</button>
          </div>
        </form>
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
const promotions = ref([]);
const showModal = ref(false);

const formData = ref({
  ten_chuong_trinh: '', ngay_bd: '', ngay_kt: '', phan_tram_giam: 10, dieu_kien_toi_thieu: 0
});

const getHeaders = () => ({ Authorization: `Bearer ${adminStore.adminToken}` });

const fetchPromos = async () => {
  try {
    const res = await api.get('/api/promotions/', { headers: getHeaders() });
    if (res.data.success) promotions.value = res.data.data;
  } catch (err) { toast.error("Lỗi lấy khuyến mãi"); }
};

onMounted(() => fetchPromos());

const formatPrice = (p) => Number(p).toLocaleString('vi-VN');

const getStatusText = (promo) => {
  const today = new Date().toISOString().split('T')[0];
  if (!promo.is_active) return 'Tạm dừng';
  if (today < promo.ngay_bd) return 'Chưa bắt đầu';
  if (today > promo.ngay_kt) return 'Đã hết hạn';
  return 'Đang diễn ra';
};

const getStatusClass = (promo) => {
  const text = getStatusText(promo);
  if (text === 'Đang diễn ra') return 'badge badge-success';
  if (text === 'Đã hết hạn' || text === 'Tạm dừng') return 'badge badge-danger';
  return 'badge badge-warning';
};

const toggleActive = async (promo) => {
  try {
    await api.put(`/api/promotions/${promo.ma_km}/`, { ...promo, is_active: !promo.is_active }, { headers: getHeaders() });
    toast.success("Cập nhật trạng thái thành công");
    fetchPromos();
  } catch (err) { toast.error("Lỗi"); }
};

const savePromo = async () => {
  try {
    await api.post('/api/promotions/', formData.value, { headers: getHeaders() });
    toast.success("Thêm khuyến mãi thành công");
    showModal.value = false;
    fetchPromos();
  } catch (err) { toast.error(err.response?.data?.message || "Có lỗi xảy ra"); }
};
</script>

<style scoped>
.badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
.badge-success { background-color: #d4edda; color: #155724; }
.badge-danger { background-color: #f8d7da; color: #721c24; }
.badge-warning { background-color: #fff3cd; color: #856404; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-card { background: white; padding: 30px; border-radius: 8px; width: 500px; }
</style>
