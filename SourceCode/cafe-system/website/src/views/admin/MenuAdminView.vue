<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Quản lý Thực Đơn</h2>
      <button class="btn btn-success" @click="openModal()">+ Thêm Món</button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Ảnh</th>
            <th>Tên Món</th>
            <th>Loại</th>
            <th>Đơn Giá</th>
            <th>Trạng Thái</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mon in menu" :key="mon.ma_mon">
            <td>
              <img v-if="mon.hinh_anh" :src="mon.hinh_anh" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />
              <div v-else style="width: 50px; height: 50px; background: #eee; border-radius: 8px; line-height: 50px; text-align: center;">☕</div>
            </td>
            <td><strong>{{ mon.ten_mon }}</strong></td>
            <td>{{ mon.ma_loai }}</td>
            <td>{{ formatPrice(mon.don_gia) }}đ</td>
            <td>
              <button 
                :class="['btn', mon.trang_thai === 1 ? 'btn-success' : 'btn-danger']"
                @click="toggleStatus(mon)"
              >
                {{ mon.trang_thai === 1 ? 'Còn hàng' : 'Hết hàng' }}
              </button>
            </td>
            <td>
              <button class="btn btn-primary" style="margin-right: 5px;" @click="openModal(mon)">Sửa</button>
              <button class="btn btn-danger" @click="deleteItem(mon.ma_mon)">Xóa</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card">
        <h3>{{ isEdit ? 'Sửa Món' : 'Thêm Món' }}</h3>
        <form @submit.prevent="saveItem">
          <div class="form-group">
            <label>Tên món</label>
            <input type="text" v-model="formData.ten_mon" class="form-control" required />
          </div>
          <div style="display:flex; gap: 10px;">
            <div class="form-group" style="flex:1">
              <label>Loại (VD: Coffee, Tea)</label>
              <input type="text" v-model="formData.ma_loai" class="form-control" required />
            </div>
            <div class="form-group" style="flex:1">
              <label>Đơn giá</label>
              <input type="number" v-model="formData.don_gia" class="form-control" required />
            </div>
          </div>
          <div class="form-group">
            <label>Mô tả</label>
            <textarea v-model="formData.mo_ta" class="form-control" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Hình ảnh mới</label>
            <input type="file" @change="handleFile" class="form-control" accept="image/*" />
          </div>
          
          <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
            <button type="button" class="btn" @click="showModal = false">Hủy</button>
            <button type="submit" class="btn btn-success">Lưu lại</button>
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
const menu = ref([]);
const showModal = ref(false);
const isEdit = ref(false);
let selectedFile = null;

const formData = ref({
  ma_mon: null, ten_mon: '', ma_loai: '', don_gia: 0, mo_ta: ''
});

const getHeaders = (isFormData = false) => ({
  Authorization: `Bearer ${adminStore.adminToken}`,
  'Content-Type': isFormData ? 'multipart/form-data' : 'application/json'
});

const fetchMenu = async () => {
  try {
    const res = await api.get('/api/menu/'); // Public endpoint
    if (res.data.success) menu.value = res.data.data;
  } catch (err) {
    toast.error("Lỗi tải thực đơn");
  }
};

onMounted(() => fetchMenu());

const formatPrice = (price) => Number(price).toLocaleString('vi-VN');

const toggleStatus = async (mon) => {
  try {
    const newStatus = mon.trang_thai === 1 ? 0 : 1;
    await api.patch(`/api/menu/${mon.ma_mon}/status/`, { trang_thai: newStatus }, { headers: getHeaders() });
    toast.success("Đã cập nhật trạng thái");
    fetchMenu();
  } catch (err) {
    toast.error("Lỗi cập nhật trạng thái");
  }
};

const handleFile = (e) => {
  selectedFile = e.target.files[0];
};

const openModal = (mon = null) => {
  selectedFile = null;
  if (mon) {
    isEdit.value = true;
    formData.value = { ...mon };
  } else {
    isEdit.value = false;
    formData.value = { ma_mon: null, ten_mon: '', ma_loai: '', don_gia: 0, mo_ta: '' };
  }
  showModal.value = true;
};

const saveItem = async () => {
  const payload = new FormData();
  payload.append('ten_mon', formData.value.ten_mon);
  payload.append('ma_loai', formData.value.ma_loai);
  payload.append('don_gia', formData.value.don_gia);
  if (formData.value.mo_ta) payload.append('mo_ta', formData.value.mo_ta);
  if (selectedFile) payload.append('hinh_anh', selectedFile);

  try {
    if (isEdit.value) {
      await api.put(`/api/menu/${formData.value.ma_mon}/`, payload, { headers: getHeaders(true) });
      toast.success("Sửa thành công!");
    } else {
      await api.post('/api/menu/', payload, { headers: getHeaders(true) });
      toast.success("Thêm thành công!");
    }
    showModal.value = false;
    fetchMenu();
  } catch (err) {
    toast.error(err.response?.data?.message || "Có lỗi xảy ra");
  }
};

const deleteItem = async (id) => {
  if (confirm("Chắc chắn xóa món này?")) {
    try {
      await api.delete(`/api/menu/${id}/`, { headers: getHeaders() });
      toast.success("Đã xóa");
      fetchMenu();
    } catch (err) {
      toast.error("Lỗi xóa món");
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-card { background: white; padding: 30px; border-radius: 8px; width: 600px;}
</style>
