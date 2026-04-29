<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Quản lý Nhân Sự</h2>
      <button class="btn btn-success" @click="openModal()">+ Thêm Nhân Viên</button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Mã NV</th>
            <th>Họ Tên</th>
            <th>Số Điện Thoại</th>
            <th>Địa Chỉ</th>
            <th>Tài Khoản Gắn Kèm</th>
            <th>Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="nv in staffList" :key="nv.ma_nv">
            <td>{{ nv.ma_nv }}</td>
            <td><strong>{{ nv.ho_ten }}</strong></td>
            <td>{{ nv.sdt }}</td>
            <td>{{ nv.dia_chi }}</td>
            <td>{{ nv.ma_tk ? nv.ma_tk.ten_dang_nhap : 'Chưa có' }}</td>
            <td>
              <button class="btn btn-primary" style="margin-right: 5px;" @click="openModal(nv)">Sửa</button>
              <button class="btn btn-danger" @click="deleteStaff(nv.ma_nv)">Xóa</button>
            </td>
          </tr>
          <tr v-if="staffList.length === 0">
            <td colspan="6" style="text-align: center;">Chưa có dữ liệu.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Form (Mockup cơ bản) -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card">
        <h3>{{ isEdit ? 'Sửa Nhân Viên' : 'Thêm Nhân Viên (Cấp Tài khoản)' }}</h3>
        
        <div class="form-group">
          <label>Họ Tên</label>
          <input type="text" v-model="formData.ho_ten" class="form-control" />
        </div>
        <div class="form-group">
          <label>Số điện thoại</label>
          <input type="text" v-model="formData.sdt" class="form-control" />
        </div>
        <div class="form-group">
          <label>Địa chỉ</label>
          <input type="text" v-model="formData.dia_chi" class="form-control" />
        </div>

        <div v-if="!isEdit" style="border-top: 1px solid #ddd; margin-top: 15px; padding-top: 15px;">
          <h4>Thông tin Đăng nhập (Cho POS)</h4>
          <div class="form-group">
            <label>Tên đăng nhập</label>
            <input type="text" v-model="formData.ten_dang_nhap" class="form-control" />
          </div>
          <div class="form-group">
            <label>Mật khẩu</label>
            <input type="password" v-model="formData.mat_khau" class="form-control" />
          </div>
        </div>

        <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
          <button class="btn" @click="showModal = false">Hủy</button>
          <button class="btn btn-success" @click="saveStaff">Lưu lại</button>
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
import 'vue3-toastify/dist/index.css';

const adminStore = useAdminAuthStore();
const staffList = ref([]);
const showModal = ref(false);
const isEdit = ref(false);

const formData = ref({
  ma_nv: null,
  ho_ten: '',
  sdt: '',
  dia_chi: '',
  ten_dang_nhap: '',
  mat_khau: ''
});

const getHeaders = () => ({ Authorization: `Bearer ${adminStore.adminToken}` });

const fetchStaff = async () => {
  try {
    const res = await api.get('/api/staff/', { headers: getHeaders() });
    if (res.data.success) {
      staffList.value = res.data.data;
    }
  } catch (err) {
    toast.error("Lỗi tải danh sách nhân viên");
  }
};

onMounted(() => {
  fetchStaff();
});

const openModal = (nv = null) => {
  if (nv) {
    isEdit.value = true;
    formData.value = {
      ma_nv: nv.ma_nv,
      ho_ten: nv.ho_ten,
      sdt: nv.sdt,
      dia_chi: nv.dia_chi,
      ten_dang_nhap: '',
      mat_khau: ''
    };
  } else {
    isEdit.value = false;
    formData.value = { ma_nv: null, ho_ten: '', sdt: '', dia_chi: '', ten_dang_nhap: '', mat_khau: '' };
  }
  showModal.value = true;
};

const saveStaff = async () => {
  try {
    if (isEdit.value) {
      await api.put(`/api/staff/${formData.value.ma_nv}/`, formData.value, { headers: getHeaders() });
      toast.success("Cập nhật thành công!");
    } else {
      // Vì API thiết kế chỉ Add NV, ta gửi kèm thông tin TK (Nếu Backend hỗ trợ tạo gộp, hoặc tách 2 API)
      // Giả định backend /api/staff/ POST có xử lý tạo luôn TaiKhoan nếu truyền ten_dang_nhap
      await api.post('/api/staff/', formData.value, { headers: getHeaders() });
      toast.success("Thêm nhân viên thành công!");
    }
    showModal.value = false;
    fetchStaff();
  } catch (err) {
    toast.error(err.response?.data?.message || "Có lỗi xảy ra");
  }
};

const deleteStaff = async (id) => {
  if (confirm("Bạn có chắc chắn muốn xóa nhân viên này?")) {
    try {
      await api.delete(`/api/staff/${id}/`, { headers: getHeaders() });
      toast.success("Xóa thành công!");
      fetchStaff();
    } catch (err) {
      toast.error("Lỗi xóa nhân viên");
    }
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
