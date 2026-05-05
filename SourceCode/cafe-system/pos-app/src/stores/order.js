import { defineStore } from 'pinia';

export const useOrderStore = defineStore('order', {
    state: () => ({
        currentTable: null, // Bàn đang được chọn
        currentOrderId: null, // Hóa đơn đang mở
        orderItems: [], // Chi tiết món đang gọi
    }),
    actions: {
        setOrder(tableId, orderId, items) {
            this.currentTable = tableId;
            this.currentOrderId = orderId;
            this.orderItems = items || [];
        },
        clearOrder() {
            this.currentTable = null;
            this.currentOrderId = null;
            this.orderItems = [];
        }
    }
});
