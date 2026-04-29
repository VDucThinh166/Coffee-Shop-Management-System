<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Quản lý Kho Nguyên Liệu</h2>
      <div>
        <button class="btn btn-primary" style="margin-right: 10px;" @click="showAddModal = true">+ Thêm NL mới</button>
        <button class="btn btn-success" @click="showImportModal = true">Nhập Kho (Lô hàng)</button>
      </div>
    </div>

    <!-- Alert Tồn kho -->
    <div v-if="lowStock.length > 0" class="alert-box">
      <strong>⚠️ CHÚ Ý:</strong> Có {{ lowStock.length }} nguyên liệu đang dưới ngưỡng báo động. Cần nhập hàng ngay!
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Mã NL</th>
            <th>Tên Nguyên Liệu</th>
            <th>Đơn Vị Tính</th>
            <th>Tồn Hiện Tại</th>
            <th>Ngưỡng Báo Động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in inventory" :key="item.ma_nl" :class="{'row-danger': isLowStock(item)}">
            <td>{{ item.ma_nl }}</td>
            <td><strong>{{ item.ten_nl }}</strong></td>
            <td>{{ item.don_vi_tinh }}</td>
            <td style="font-weight: bold;">{{ item.so_luong_ton }}</td>
            <td>{{ item.nguong_bao_dong }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Thêm NL mới -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal-card">
        <h3>Thêm Nguyên Liệu Mới</h3>
        <div class="form-group"><label>Tên NL</label><input type="text" v-model="addForm.ten_nl" class="form-control"></div>
        <div class="form-group"><label>Đơn vị (kg, chai,...)</label><input type="text" v-model="addForm.don_vi_tinh" class="form-control"></div>
        <div class="form-group"><label>Ngưỡng báo động</label><input type="number" v-model="addForm.nguong_bao_dong" class="form-control"></div>
        <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
          <button class="btn" @click="showAddModal = false">Hủy</button>
          <button class="btn btn-success" @click="saveNewMaterial">Lưu</button>
        </div>
      </div>
    </div>

    <!-- Modal Nhập Kho -->
    <div v-if="showImportModal" class="modal-overlay">
      <div class="modal-card" style="width: 800px; max-height: 90vh; overflow-y: auto;">
        <h3>Tạo Phiếu Nhập Kho</h3>
        <div style="margin-bottom: 20px;">
          <select v-model="selectedMaterial" class="form-control" style="width: 50%; display: inline-block;">
            <option value="">-- Chọn NL cần nhập --</option>
            <option v-for="item in inventory" :key="item.ma_nl" :value="item">{{ item.ten_nl }}</option>
          </select>
          <button class="btn btn-primary" style="margin-left: 10px;" @click="addToImportList">Thêm vào phiếu</button>
        </div>

        <table class="table" style="margin-bottom: 20px;" v-if="importList.length > 0">
          <thead><tr><th>Tên NL</th><th>Số lượng nhập</th><th>Đơn giá</th><th>Xóa</th></tr></thead>
          <tbody>
            <tr v-for="(imp, idx) in importList" :key="idx">
              <td>{{ imp.ten_nl }}</td>
              <td><input type="number" v-model="imp.so_luong" class="form-control" style="margin:0"></td>
              <td><input type="number" v-model="imp.don_gia" class="form-control" style="margin:0"></td>
              <td><button class="btn btn-danger" @click="importList.splice(idx, 1)">X</button></td>
            </tr>
          </tbody>
        </table>
        
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <button class="btn" @click="showImportModal = false">Hủy</button>
          <button class="btn btn-success" :disabled="importList.length === 0" @click="submitImport">Xác nhận Nhập</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../api/axios';
import { useAdminAuthStore } from '../../stores/adminAuth';
import { toast } from 'vue3-toastify';

const adminStore = useAdminAuthStore();
const inventory = ref([]);

const showAddModal = ref(false);
const showImportModal = ref(false);

const addForm = ref({ ten_nl: '', don_vi_tinh: '', nguong_bao_dong: 10 });
const selectedMaterial = ref('');
const importList = ref([]);

const getHeaders = () => ({ Authorization: `Bearer ${adminStore.adminToken}` });

const fetchInventory = async () => {
  try {
    const res = await api.get('/api/inventory/', { headers: getHeaders() });
    if (res.data.success) inventory.value = res.data.data;
  } catch (err) { toast.error("Lỗi lấy kho hàng"); }
};

onMounted(() => fetchInventory());

const lowStock = computed(() => {
  return inventory.value.filter(item => item.so_luong_ton < item.nguong_bao_dong);
});

const isLowStock = (item) => parseFloat(item.so_luong_ton) < parseFloat(item.nguong_bao_dong);

const saveNewMaterial = async () => {
  try {
    await api.post('/api/inventory/', addForm.value, { headers: getHeaders() });
    toast.success("Thêm NL thành công");
    showAddModal.value = false;
    fetchInventory();
  } catch (err) { toast.error("Có lỗi xảy ra"); }
};

const addToImportList = () => {
  if (!selectedMaterial.value) return;
  importList.value.push({
    ma_nl: selectedMaterial.value.ma_nl,
    ten_nl: selectedMaterial.value.ten_nl,
    so_luong: 1,
    don_gia: 0
  });
  selectedMaterial.value = '';
};

const submitImport = async () => {
  const payload = {
    nguoi_giao: "Nhà cung cấp", // Mock
    chi_tiet: importList.value.map(i => ({
      ma_nl: i.ma_nl,
      so_luong: i.so_luong,
      don_gia: i.don_gia
    }))
  };
  
  try {
    await api.post('/api/inventory/import/', payload, { headers: getHeaders() });
    toast.success("Nhập kho lô hàng thành công!");
    showImportModal.value = false;
    importList.value = [];
    fetchInventory();
  } catch (err) {
    toast.error(err.response?.data?.message || "Lỗi nhập kho");
  }
};
</script>

<style scoped>
.alert-box {
  background-color: #fce4e4; color: #c0392b; padding: 15px; border-radius: 8px; margin-bottom: 20px;
}
.row-danger td { background-color: #fce4e4 !important; color: #c0392b; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-card { background: white; padding: 30px; border-radius: 8px; width: 500px; }
</style>
