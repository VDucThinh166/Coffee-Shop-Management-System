from decimal import Decimal

def calculate_total(subtotal, is_vip, khuyen_mai):
    """
    Dịch bảng quyết định Chương 3 thành code.
    Tính tổng tiền cuối cùng dựa trên:
    - subtotal: Tổng tiền các món (trước giảm giá)
    - is_vip: Khách hàng có phải VIP không (hạng >= Bạc)
    - khuyen_mai: Object KhuyenMai (Voucher) hoặc None

    Returns: (final_total, discount_percent)
    """
    # Decision Table — Bảng quyết định Chương 3
    if subtotal >= 500000 and is_vip and khuyen_mai:
        discount_percent = 20
    elif subtotal >= 500000 and khuyen_mai:
        discount_percent = 15
    elif subtotal >= 500000:
        discount_percent = 10
    elif is_vip:
        discount_percent = 5
    else:
        discount_percent = 0

    final_total = subtotal * Decimal(100 - discount_percent) / Decimal(100)
    return final_total, discount_percent
