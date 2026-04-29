<template>
  <div id="app">
    <!-- Admin Layout -->
    <AdminLayout v-if="isAdminRoute" />

    <!-- Public Layout -->
    <template v-else>
      <Navbar />
      <main class="main-content">
        <router-view></router-view>
      </main>
      <Footer />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from './components/Navbar.vue';
import Footer from './components/Footer.vue';
import AdminLayout from './components/AdminLayout.vue';

const route = useRoute();
const isAdminRoute = computed(() => route.meta.layout === 'admin');
</script>

<style>
/* Root styles are handled in src/assets/main.css */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-content {
  flex: 1;
}
</style>
