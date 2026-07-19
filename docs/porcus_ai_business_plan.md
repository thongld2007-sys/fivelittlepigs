# KẾ HOẠCH KINH DOANH & DỰ TOÁN KINH PHÍ: PORCUS AI
**Sản phẩm:** Hệ thống Chẩn đoán Thích ứng Lỗ hổng Kiến thức Gốc (Adaptive Diagnostic & Socratic Tutoring System)
**Dành cho:** Ban Giám khảo & Các Nhà đầu tư Vòng Chung kết Vietnam AI Innovation Challenge

---

## 1. TỔNG QUAN DỰ ÁN (EXECUTIVE SUMMARY)
PorcusAI là nền tảng gia sư trí tuệ nhân tạo (AI Tutor) thế hệ mới, hoạt động theo mô hình **Hybrid-Adaptive** giúp giải quyết tận gốc rễ nỗi đau "mất gốc lũy tiến" môn Toán THCS tại Việt Nam. Bằng việc kết hợp các thuật toán chẩn đoán toán học offline (xác suất BKT và Đồ thị kỹ năng DAG) với trí tuệ nhân tạo tạo sinh trực tuyến (FPT AI Inference & Speech), PorcusAI mang lại hiệu quả vượt trội với chi phí vận hành cực kỳ tối ưu, sẵn sàng scale từ quy mô trường học cục bộ lên hàng triệu người dùng trên toàn quốc.

---

## 2. KHÁCH HÀNG & MÔ HÌNH DOANH THU (MONETIZATION MODEL)
PorcusAI áp dụng mô hình **B2B2C (Trường học -> Học sinh/Phụ huynh)** và **B2C trực tiếp** với cơ chế thu phí đăng ký thuê bao (Subscription-based):

```
                     ┌────────────────────────────────────────┐
                     │          Hệ sinh thái PorcusAI         │
                     └───────────────────┬────────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
      ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
      │  Gói B2B2C Trường   │ │ Gói Phụ huynh (B2C) │ │ Gói Giáo viên (Free)│
      │ 15.000đ/học sinh/th │ │ 45.000đ/tháng       │ │ Hỗ trợ TA & Soạn bài│
      │   (Mua theo niên)   │ │ (Học thích ứng sâu) │ │ (Để viral thương hiệu)│
      └─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

1.  **Gói B2B2C (Cung cấp cho các trường học công/tư):**
    *   **Mức phí dự kiến:** **15.000 VND / học sinh / tháng** (thu theo năm học 9 tháng, tương đương 135.000 VND/học sinh/năm).
    *   **Quyền lợi:** Tích hợp tài khoản học sinh vào hệ thống quản lý của nhà trường, Dashboard phân tích gap group của Giáo viên, đồng bộ tiến trình học trên phòng máy trường học.
2.  **Gói B2C (Phụ huynh tự mua cho con tại nhà):**
    *   **Mức phí dự kiến:** **45.000 VND / tháng** (hoặc gói năm 360.000 VND).
    *   **Quyền lợi:** Bản đồ tri thức cá nhân hóa (Second Brain Obsidian Graph View), kết nối chatbot Zalo/SMS báo cáo tiến trình của con hàng ngày cho phụ huynh, mở khóa không giới hạn lượt tương tác Socratic Tutor.
3.  **Gói Giáo viên (Phát hành miễn phí):**
    *   Tặng miễn phí tài khoản phân tích lớp học và sinh giáo án tự động cho giáo viên nhằm tạo hiệu ứng lan tỏa (viral) và thúc đẩy các trường mua gói B2B2C.

---

## 3. DỰ TOÁN KINH PHÍ VẬN HÀNH CHI TIẾT (OPERATING & INFRASTRUCTURE BUDGET)

Dưới đây là bảng dự toán chi phí kỹ thuật cho **1.000 học sinh hoạt động thường xuyên trong 1 tháng** (sử dụng đơn giá API thực tế của hệ sinh thái FPT AI Factory):

### A. Chi phí API và Hạ tầng (Hàng tháng)

| Khoản mục | Cách tính toán | Số lượng / Tháng | Đơn giá | Thành tiền / Tháng |
| :--- | :--- | :---: | :---: | :---: |
| **Core BKT/DAG** | Chạy offline cục bộ trên server trường hoặc serverless | - | **0 VND** | **0 VND** |
| **API FPT AI Inference** | 8 lượt gọi Socratic/học sinh/tháng x 900 tokens/lượt | 7.200.000 tokens | 15 VND / 1K tokens | **108.000 VND** |
| **API FPT AI Speech (TTS)** | Phục vụ đọc câu hỏi, gợi ý giọng nói qua Speech cache | 50.000 ký tự | 10 VND / 1K ký tự | **500 VND** |
| **API FPT AI Vision (OCR)** | Quét và nhận diện lỗi sai từ bài làm giấy của học sinh | 200 ảnh bài làm | 50 VND / ảnh | **10.000 VND** |
| **Lesson Planner API** | Giáo viên sinh giáo án bổ trợ (40 giáo án/tháng) | 48.000 tokens | 15 VND / 1K tokens | **720 VND** |
| **Database & Hosting Cloud** | PostgreSQL Managed DB (Neon/Supabase) + Vercel Hosting | Gói Startup | Cố định | **750.000 VND** *(~30 USD)* |
| **TỔNG CHI PHÍ** | **Tính trên 1.000 học sinh tích cực** | | | **869.220 VND** |
| **CHI PHÍ / HỌC SINH** | **Chi phí biên (Marginal Cost) cho 1 học sinh / tháng** | | | **~870 VND** |

> [!TIP]
> **Nhận xét của Giám khảo:** Với chi phí hạ tầng biên chỉ **~870 VND / học sinh / tháng**, nếu PorcusAI thu phí ở mức tối thiểu **15.000 VND / học sinh / tháng** (gói trường học), biên lợi nhuận gộp (Gross Margin) của dự án sẽ đạt **> 94%**. Đây là con số mơ ước đối với bất kỳ mô hình SaaS giáo dục nào.

---

## 4. BẢNG DỰ BÁO TÀI CHÍNH TRONG 3 NĂM (3-YEAR FINANCIAL PROJECTIONS)

Dưới đây là kế hoạch tăng trưởng dự kiến dựa trên lộ trình Pilot và thương mại hóa sản phẩm:

```
                                  DỰ BÁO DOANH THU & LỢI NHUẬN (VND)
    4.5B ┼─────────────────────────────────────────────────────────────── Doanh thu
    4.0B ┼─────────────────────────────────────────────────────────────── Lợi nhuận ròng
    3.5B ┼───────────────────────────────────────────────────────────────
    3.0B ┼───────────────────────────────────────────────────────────────
    2.5B ┼───────────────────────────────────────────────────────────────
    2.0B ┼───────────────────────────────────────────────────────────────
    1.5B ┼─────────────────────────────────────────────────────────      
    1.0B ┼───────────────────────────────────────────────────            
    0.5B ┼─────────────────────────────────────────────                  
      0B ┼───■───────────────────────────────────────────────────────────
           Năm 1 (Pilot 10 trường)          Năm 2 (Scale 50 trường)       Năm 3 (150 trường)
```

| Chỉ số tài chính | Năm 1 (Thử nghiệm & Pilot) | Năm 2 (Mở rộng khu vực) | Năm 3 (Scale toàn quốc) |
| :--- | :---: | :---: | :---: |
| **Số lượng Trường học** | 10 trường | 50 trường | 150 trường |
| **Số lượng Học sinh tích cực** | 4.000 học sinh | 25.000 học sinh | 80.000 học sinh |
| **Tổng Doanh thu (VND)** | **630.000.000** | **3.950.000.000** | **12.800.000.000** |
| **Chi phí API & Hosting (VND)** | 35.000.000 | 220.000.000 | 700.000.000 |
| **Chi phí R&D, Marketing (VND)** | 350.000.000 | 1.200.000.000 | 3.200.000.000 |
| **Lợi nhuận trước thuế (VND)** | **245.000.000** | **2.530.000.000** | **8.900.000.000** |
| **Biên lợi nhuận ròng (%)** | **38.8%** | **64.0%** | **69.5%** |

---

## 5. ĐIỂM HÒA VỐN & THỜI GIAN HOÀN VỐN (BREAK-EVEN ANALYSIS)
*   **Chi phí định định ban đầu (Fixed Costs):** Hoàn thiện phần mềm, thiết lập cơ sở dữ liệu nền, bản quyền ngân hàng 189 câu hỏi toán học GDPT ban đầu: **120.000.000 VND**.
*   **Giá bán trung bình (ARPU):** **15.000 VND / học sinh / tháng**.
*   **Chi phí biến đổi (Variable Cost):** **870 VND / học sinh / tháng**.
*   **Công thức tính điểm hòa vốn (Học sinh/Tháng):**
    $$\text{Điểm hòa vốn} = \frac{\text{Chi phí định định}}{\text{Giá bán} - \text{Chi phí biến đổi}} = \frac{120.000.000}{15.000 - 870} \approx 8.492 \text{ lượt học sinh/tháng}$$
*   **Kết luận:** Dự án sẽ chính thức hòa vốn ngay trong **Tháng thứ 3 của Năm 1** khi số lượng học sinh đăng ký gói Pilot đạt ngưỡng **8.500 học sinh** (tương đương quy mô của 4-5 trường THCS cỡ vừa tại Hà Nội hoặc TP.HCM).
