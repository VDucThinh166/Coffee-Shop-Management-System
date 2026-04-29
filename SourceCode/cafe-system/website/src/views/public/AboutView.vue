<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Câu Chuyện Của Chúng Tôi</h1>
    </div>

    <div class="container section-padding">
      <div class="about-grid">
        <div class="about-content">
          <h2>Khởi nguồn đam mê</h2>
          <p>Được thành lập vào năm 2026, L'Aura Cafe không chỉ đơn thuần là một quán cà phê, mà là một hành trình tìm kiếm sự hoàn hảo trong từng hương vị. Chúng tôi bắt đầu từ một cửa hàng nhỏ ở góc phố, với khao khát mang đến cho khách hàng một không gian trú ẩn bình yên giữa lòng thành phố nhộn nhịp.</p>
          <p>Trải qua thời gian, dù quy mô có thay đổi, triết lý kinh doanh của chúng tôi vẫn giữ nguyên: Chất lượng đi đầu, dịch vụ từ trái tim.</p>
          
          <h2 class="mt-40">Giá trị cốt lõi</h2>
          <ul class="values-list">
            <li><strong>Nguyên bản:</strong> Hạt cà phê được tuyển chọn khắt khe từ những nông trại địa phương uy tín.</li>
            <li><strong>Tinh tế:</strong> Chăm chút từng chi tiết trong không gian để tạo cảm giác thoải mái nhất.</li>
            <li><strong>Bền vững:</strong> Sử dụng các vật liệu thân thiện với môi trường.</li>
          </ul>
        </div>
        
        <div class="about-images">
          <div class="img-box box-1">Nội thất ấm áp</div>
          <div class="img-box box-2">Góc check-in</div>
          <div class="img-box box-3">Pha chế chuyên nghiệp</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  padding-top: 80px; /* offset for fixed navbar */
}
.page-header {
  background-color: var(--secondary);
  color: white;
  padding: 80px 0;
  text-align: center;
}
.page-header h1 { margin: 0; font-size: 40px;}
.section-padding { padding: 80px 20px; }

.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
}

.about-content h2 {
  color: var(--primary);
  font-size: 32px;
  margin-bottom: 20px;
}
.mt-40 { margin-top: 40px; }
.about-content p {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 20px;
  line-height: 1.8;
}

.values-list {
  list-style: none;
  padding: 0;
}
.values-list li {
  font-size: 18px;
  margin-bottom: 15px;
  color: var(--text-secondary);
  padding-left: 30px;
  position: relative;
}
.values-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--primary);
  font-weight: bold;
}

/* Image Grid */
.about-images {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  grid-template-areas: 
    "box1 box2"
    "box1 box3";
}
.img-box {
  background-color: #ecf0f1;
  border-radius: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: #7f8c8d;
  font-size: 18px;
  text-align: center;
  padding: 20px;
}
.box-1 { grid-area: box1; background-color: var(--primary); color: white; min-height: 400px;}
.box-2 { grid-area: box2; min-height: 190px;}
.box-3 { grid-area: box3; min-height: 190px;}

@media (max-width: 992px) {
  .about-grid { grid-template-columns: 1fr; }
  .about-images { grid-template-areas: "box1 box1" "box2 box3"; }
  .box-1 { min-height: 250px;}
}
</style>
