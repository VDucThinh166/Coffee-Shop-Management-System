<template>
  <div>
    <h2>Danh sách Khách Hàng (VIP)</h2>

    <div class="card" style="margin-bottom: 20px;">
      <div style="display: flex; gap: 10px;">
        <input type="text" v-model="searchQuery" class="form-control" placeholder="Nhập SĐT để tìm kiếm..." style="width: 300px; margin: 0;">
        <button class="btn btn-primary" @click="searchCustomer">Tìm kiếm</button>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>Số Điện Thoại</th>
            <th>Họ Tên</th>
            <th>Điểm Tích Lũy</th>
            <th>Hạng Thành Viên</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="kh in filteredList" :key="kh.sdt_khach">
            <td><strong>{{ kh.sdt_khach }}</strong></td>
            <td>{{ kh.ho_ten }}</td>
            <td><span class="points">{{ kh.diem_tich_luy }}</span></td>
            <td><span :class="getTierClass(kh.hang_tv)">{{ kh.hang_tv }}</span></td>
          </tr>
          <tr v-if="filteredList.length === 0">
            <td colspan="4" style="text-align: center;">Không tìm thấy khách hàng.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../../api/axios';
import { useAdminAuthStore } from '../../stores/adminAuth';
import { toast } from 'vue3-toastify';

const adminStore = useAdminAuthStore();
const customers = ref([]);
const searchQuery = ref('');

// Báo cáo có API /api/reports/customers/top/ có thể dùng tạm để list ra.
// Do hệ thống backend chưa làm CRUD KhachHang riêng, ta dùng API này để lấy danh sách khách tốt.
const fetchCustomers = async () => {
  try {
    const res = await api.get('/api/reports/customers/top/', { 
      headers: { Authorization: `Bearer ${adminStore.adminToken}` } 
    });
    if (res.data.success) {
      customers.value = res.data.data.map(c => ({
        sdt_khach: c.sdt_khach,
        ho_ten: c.ho_ten,
        diem_tich_luy: c.diem_tich_luy,
        hang_tv: c.hang_tv
      }));
    }
  } catch (err) {
    toast.error("Không thể lấy danh sách khách hàng");
  }
};

onMounted(() => fetchCustomers());

const filteredList = computed(() => {
  if (!searchQuery.value) return customers.value;
  return customers.value.filter(c => c.sdt_khach.includes(searchQuery.value));
});

const getTierClass = (tier) => {
  if (tier === 'Kim cương') return 'tier-diamond';
  if (tier === 'Vàng') return 'tier-gold';
  if (tier === 'Bạc') return 'tier-silver';
  return 'tier-bronze';
};

const searchCustomer = () => {
  // Đã compute tự động, nút này chỉ để UX tốt hơn.
};
</script>

<style scoped>
.points { font-weight: bold; color: #2980b9; }
.tier-diamond { color: #8e44ad; font-weight: 900; background: #f4ecf8; padding: 4px 8px; border-radius: 4px; }
.tier-gold { color: #f1c40f; font-weight: bold; background: #fef9e7; padding: 4px 8px; border-radius: 4px; }
.tier-silver { color: #7f8c8d; font-weight: bold; background: #f2f4f4; padding: 4px 8px; border-radius: 4px; }
.tier-bronze { color: #d35400; font-weight: bold; background: #fdf2e9; padding: 4px 8px; border-radius: 4px; }
</style>
