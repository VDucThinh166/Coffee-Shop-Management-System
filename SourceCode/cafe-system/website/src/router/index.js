import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/public/HomeView.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/public/AboutView.vue')
    },
    {
      path: '/menu',
      name: 'menu',
      component: () => import('../views/public/MenuView.vue')
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/public/ContactView.vue')
    },
    // ==========================================
    // ADMIN ROUTES
    // ==========================================
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('../views/admin/LoginAdminView.vue'),
      meta: { layout: 'admin-login' } // Không dùng Sidebar
    },
    {
      path: '/admin',
      redirect: '/admin/dashboard'
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('../views/admin/DashboardView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/staff',
      name: 'admin-staff',
      component: () => import('../views/admin/StaffView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/shifts',
      name: 'admin-shifts',
      component: () => import('../views/admin/ShiftView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/attendance',
      name: 'admin-attendance',
      component: () => import('../views/admin/AttendanceView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/menu',
      name: 'admin-menu',
      component: () => import('../views/admin/MenuAdminView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/inventory',
      name: 'admin-inventory',
      component: () => import('../views/admin/InventoryView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/promotions',
      name: 'admin-promotions',
      component: () => import('../views/admin/PromotionView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/customers',
      name: 'admin-customers',
      component: () => import('../views/admin/CustomerView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    },
    {
      path: '/admin/reports',
      name: 'admin-reports',
      component: () => import('../views/admin/ReportsView.vue'),
      meta: { requiresAdmin: true, layout: 'admin' }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0, behavior: 'smooth' };
    }
  }
});

// Route Guard
import { useAdminAuthStore } from '../stores/adminAuth';

router.beforeEach((to, from, next) => {
  const adminStore = useAdminAuthStore();
  
  if (to.meta.requiresAdmin && !adminStore.isAuthenticatedAdmin) {
    next('/admin/login');
  } else if (to.path === '/admin/login' && adminStore.isAuthenticatedAdmin) {
    next('/admin/dashboard');
  } else {
    next();
  }
});

export default router;
