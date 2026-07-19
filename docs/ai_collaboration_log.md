# NHẬT KÝ CỘNG TÁC AI (AI COLLABORATION LOG) - PORCUS AI

**Dự án:** PorcusAI — Hệ thống Chẩn đoán Thích ứng Lỗ hổng Kiến thức Toán học  
**Cuộc thi:** Vietnam AI Innovation Challenge  

---

## 1. TỔNG QUAN VỀ CÁC CÔNG CỤ AI SỬ DỤNG
Trong suốt 48 giờ phát triển dự án PorcusAI, đội ngũ phát triển đã áp dụng mô hình **AI-Assisted Pair Programming** nhằm tối ưu hóa 80% thời gian lập trình và tập trung vào tư duy bài toán.

*   **Trợ lý AI chính:** Antigravity Agentic Coding AI (DeepMind Team) & OpenAI Codex.
*   **Mô hình ngôn ngữ (LLM Engine):** OpenAI Codex, Gemini 3.5 Flash & Claude 3.5 Sonnet.
*   **Dịch vụ AI tích hợp trong sản phẩm:** FPT AI Factory (LLM Chat, Speech TTS/STT, Vision OCR).

---

## 2. NHẬT KÝ HỢP TÁC VÀ PHÂN CHIA VAI TRÒ (AI PAIR PROGRAMMING LOG)

### Phase 1: Kiến trúc Hệ thống & Thuật toán Chẩn đoán (Hours 0 - 12)
*   **Con người:** Định nghĩa bài toán chẩn đoán mất gốc môn Toán THCS (Lớp 5 - Lớp 9) và thiết lập cấu trúc đồ thị kỹ năng tiên quyết (Prerequisite DAG).
*   **AI Cộng tác:** 
    *   Hỗ trợ thiết kế thuật toán **Bayesian Knowledge Tracing (BKT)** trong `backend/diagnostic_engine.py`.
    *   Tự động hóa sinh bộ dữ liệu câu hỏi kiểm định GDPT 189 câu (`data/questions.json`).

### Phase 2: Backend API & Bảo mật Tài khoản (Hours 12 - 24)
*   **Con người:** Định nghĩa các luồng nghiệp vụ Học sinh, Giáo viên và Phụ huynh.
*   **AI Cộng tác:** 
    *   Viết mã nguồn các endpoint FastAPI trong `backend/app.py` và module xác thực Argon2/JWT trong `backend/student_auth.py`.
    *   Hỗ trợ cấu hình Alembic migration và chuyển đổi linh hoạt giữa SQLite (Offline) và PostgreSQL (Production).

### Phase 3: Frontend Adaptive UI & Trực quan hóa DAG (Hours 24 - 36)
*   **Con người:** Phối cảnh giao diện Memphis-style, phân bố layout Dashboard cho Giáo viên và Trợ lý Socratic cho Học sinh.
*   **AI Cộng tác:**
    *   Sinh mã JavaScript (`frontend/app.js`) xử lý vẽ sơ đồ cây quyết định chẩn đoán động bằng SVG (`drawSVGTree`).
    *   Tối ưu hóa các lớp CSS tĩnh không phụ thuộc thư viện ngoài giúp giao diện tải siêu nhanh (<100ms).

### Phase 4: Benchmark Mô phỏng & Kế hoạch Kinh doanh (Hours 36 - 48)
*   **Con người:** Đặt ra các kịch bản kiểm thử giả lập 1.000 học sinh và mô hình định giá B2B2C/B2C.
*   **AI Cộng tác:**
    *   Chạy mô phỏng khoa học so sánh phương pháp Thích ứng (Adaptive) vs Tuyến tính (Linear), xuất biểu đồ `artifacts/benchmark_1000.svg`.
    *   Soạn thảo Kế hoạch Kinh doanh chi tiết và thiết kế trang in PDF chuẩn doanh nghiệp (`docs/porcus_ai_business_plan.html`).

---

## 3. KẾT QUẢ ĐẠT ĐƯỢC NHỜ CỘNG TÁC AI
*   **Tốc độ hoàn thiện:** Giảm thời gian phát triển sản phẩm full-stack từ **2 tuần xuống 48 giờ**.
*   **Chất lượng mã nguồn:** 100% API đều có kiểm thử tự động (`pytest`) và tuân thủ các tiêu chuẩn bảo mật OWASP.
