<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Thực Đơn L'Aura</h1>
      <p>Khám phá thế giới hương vị phong phú được tạo nên từ sự tinh tế và kỹ năng pha chế đỉnh cao.</p>
    </div>

    <div class="container section-padding">
      <!-- Filters -->
      <div class="category-filters">
        <button 
          v-for="cat in categories" 
          :key="cat"
          :class="['filter-btn', currentCategory === cat ? 'active' : '']"
          @click="currentCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Menu Grid -->
      <div v-if="loading" class="loading-state">
        <p>Đang tải thực đơn...</p>
      </div>
      
      <div v-else class="menu-grid animate-fade-in">
        <div v-for="item in filteredMenu" :key="item.ma_mon" class="glass-card menu-item">
          <div class="item-img-wrapper">
            <img v-if="item.hinh_anh" :src="item.hinh_anh" :alt="item.ten_mon" />
            <div v-else class="img-placeholder">L'AURA</div>
            
            <div v-if="item.trang_thai === 0" class="badge out-of-stock">Tạm hết</div>
          </div>
          <div class="item-details">
            <h3 class="item-name">{{ item.ten_mon }}</h3>
            <p class="item-desc">{{ item.mo_ta || 'Đang cập nhật mô tả...' }}</p>
            <div class="item-bottom">
              <span class="item-price">{{ formatPrice(item.don_gia) }}đ</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../api/axios';

const menu = ref([]);
const categories = ref(['Tất cả']);
const currentCategory = ref('Tất cả');
const loading = ref(true);

const fetchMenu = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/menu/');
    if (res.data.success) {
      menu.value = res.data.data;
      const cats = new Set(menu.value.map(m => m.ma_loai));
      categories.value = ['Tất cả', ...Array.from(cats)];
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchMenu();
});

const filteredMenu = computed(() => {
  if (currentCategory.value === 'Tất cả') return menu.value;
  return menu.value.filter(m => m.ma_loai === currentCategory.value);
});

const formatPrice = (price) => {
  return Number(price).toLocaleString('vi-VN');
};
</script>

<style scoped>
.page-container {
  padding-top: 80px;
}
.page-header {
  background-color: var(--secondary);
  color: white;
  padding: 80px 20px;
  text-align: center;
}
.page-header h1 { margin: 0 0 15px 0; font-size: 40px;}
.page-header p { font-size: 18px; opacity: 0.8; max-width: 600px; margin: 0 auto;}

.section-padding { padding: 60px 20px; }

/* Filters */
.category-filters {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 50px;
}
.filter-btn {
  background: white;
  border: 1px solid #ddd;
  padding: 10px 25px;
  border-radius: 30px;
  font-family: var(--font-heading);
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.filter-btn:hover { border-color: var(--primary); color: var(--primary); }
.filter-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

/* Loading */
.loading-state { text-align: center; padding: 50px; font-size: 20px; color: var(--text-secondary);}

/* Grid */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
}
.menu-item {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.item-img-wrapper {
  height: 220px;
  position: relative;
  overflow: hidden;
}
.item-img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}
.menu-item:hover .item-img-wrapper img { transform: scale(1.1); }
.img-placeholder {
  width: 100%;
  height: 100%;
  background: #ecf0f1;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: var(--font-heading);
  font-size: 30px;
  color: #bdc3c7;
  letter-spacing: 2px;
}
.badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}
.out-of-stock { background-color: var(--accent); }

.item-details { padding: 25px; display: flex; flex-direction: column; flex: 1;}
.item-name { font-size: 22px; margin-bottom: 10px; color: var(--secondary);}
.item-desc { font-size: 14px; color: var(--text-secondary); margin-bottom: 20px; flex: 1;}
.item-bottom { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 15px;}
.item-price { font-size: 20px; font-weight: 800; color: var(--primary);}
</style>
