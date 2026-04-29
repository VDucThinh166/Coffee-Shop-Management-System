import { defineStore } from 'pinia';
import axios from '../services/axios'; // Cần tạo axios instance

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        user: null, // Thông tin nhân viên
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
    },
    actions: {
        async login(username, password) {
            try {
                const response = await axios.post('/api/auth/login/', {
                    ten_dang_nhap: username,
                    mat_khau: password
                });
                if (response.data.success) {
                    this.token = response.data.access_token;
                    localStorage.setItem('token', this.token);
                    // Decode token hoặc gọi API lấy info
                    return true;
                }
                return false;
            } catch (error) {
                console.error("Login failed", error);
                throw error;
            }
        },
        logout() {
            this.token = null;
            this.user = null;
            localStorage.removeItem('token');
        }
    }
});
