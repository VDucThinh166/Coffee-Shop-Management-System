"""
Serializers cho module Promotions (Khuyến mãi).
"""
from rest_framework import serializers
from .models import KhuyenMai


class KhuyenMaiSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhuyenMai
        fields = '__all__'
        read_only_fields = ('ma_km', 'ngay_tao', 'ngay_cap_nhat')

    def validate(self, data):
        # Xác thực ngay_kt >= ngay_bd
        # Vì đây có thể là thao tác PUT (partial update), ta lấy data từ instance nếu thiếu
        ngay_bd = data.get('ngay_bd', getattr(self.instance, 'ngay_bd', None))
        ngay_kt = data.get('ngay_kt', getattr(self.instance, 'ngay_kt', None))

        if ngay_bd and ngay_kt and ngay_bd > ngay_kt:
            raise serializers.ValidationError({
                'ngay_kt': 'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.'
            })
            
        # Xác thực phan_tram_giam 1 - 100
        phan_tram = data.get('phan_tram_giam', getattr(self.instance, 'phan_tram_giam', None))
        if phan_tram is not None and (phan_tram <= 0 or phan_tram > 100):
            raise serializers.ValidationError({
                'phan_tram_giam': 'Phần trăm giảm phải từ 1 đến 100.'
            })

        # Xác thực dieu_kien_toi_thieu >= 0
        dieu_kien = data.get('dieu_kien_toi_thieu', getattr(self.instance, 'dieu_kien_toi_thieu', None))
        if dieu_kien is not None and dieu_kien < 0:
            raise serializers.ValidationError({
                'dieu_kien_toi_thieu': 'Điều kiện tối thiểu không được âm.'
            })

        return data
