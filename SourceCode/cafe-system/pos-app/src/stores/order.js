import { defineStore } from 'pinia';

export const useOrderStore = defineStore('order', {
    state: () => ({
        currentTable: null, // Bàn đang được chọn
        currentOrderId: null, // Hóa đơn đang mở
        orderItems: [], // Chi tiết món đang gọi
        currentCustomerTier: null, // Hạng khách hàng
    }),
    actions: {
        setOrder(tableId, orderId, items, customerTier = null) {
            this.currentTable = tableId;
            this.currentOrderId = orderId;
            this.orderItems = items || [];
            this.currentCustomerTier = customerTier;
        },
        clearOrder() {
            this.currentTable = null;
            this.currentOrderId = null;
            this.orderItems = [];
            this.currentCustomerTier = null;
        }
    }
});
