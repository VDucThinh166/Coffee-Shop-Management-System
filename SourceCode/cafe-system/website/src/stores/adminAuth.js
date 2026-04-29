import { defineStore } from 'pinia';
import axios from '../api/axios'; // Dùng chung instance nhưng thêm JWT cho Admin

export const useAdminAuthStore = defineStore('adminAuth', {
    state: () => ({
        adminToken: localStorage.getItem('admin_token') || null,
        adminUser: JSON.parse(localStorage.getItem('admin_user')) || null,
    }),
    getters: {
        isAuthenticatedAdmin: (state) => !!state.adminToken && state.adminUser?.ma_phan_quyen === 1,
    },
    actions: {
        async login(username, password) {
            try {
                const response = await axios.post('/api/auth/login/', {
                    ten_dang_nhap: username,
                    mat_khau: password
                });
                
                if (response.data.success) {
                    const data = response.data;
                    if (data.ma_phan_quyen !== 1) {
                        throw new Error('Tài khoản không có quyền truy cập quản trị!');
                    }

                    this.adminToken = data.access_token;
                    this.adminUser = {
                        ten_dang_nhap: username,
                        ma_phan_quyen: data.ma_phan_quyen
                    };
                    
                    localStorage.setItem('admin_token', this.adminToken);
                    localStorage.setItem('admin_user', JSON.stringify(this.adminUser));
                    
                    return true;
                }
                return false;
            } catch (error) {
                console.error("Admin Login failed", error);
                throw error;
            }
        },
        logout() {
            this.adminToken = null;
            this.adminUser = null;
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_user');
        }
    }
});
