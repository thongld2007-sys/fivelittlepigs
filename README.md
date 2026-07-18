# Porcus AI — Hệ thống Chẩn đoán Lỗ hổng Kiến thức Toán học thích ứng

## 1. Mô tả bài toán và phạm vi hệ thống

### Bài toán đặt ra
Học sinh từ lớp 5 đến lớp 9 thường gặp khó khăn khi làm các bài tập Toán học mới không phải vì kiến thức lớp hiện tại quá phức tạp, mà do bị **hổng kiến thức nền tảng (kỹ năng tiên quyết)** từ các lớp trước. Giáo viên với sĩ số lớp học đông (35-45 học sinh) rất khó để theo dõi, chẩn đoán chính xác lỗ hổng gốc của từng em bằng phương pháp chấm điểm thủ công hay phán đoán cảm tính.

### Phạm vi hệ thống
Hệ thống **Porcus AI** được thiết kế như một công cụ chẩn đoán thông minh hỗ trợ giáo viên và học sinh:
- **Phía Học sinh (Adaptive Test):** Cung cấp các bài kiểm tra chẩn đoán thích ứng. Khi học sinh trả lời sai một câu hỏi, hệ thống sẽ tự động hạ độ khó hoặc lùi về kiểm tra kỹ năng tiên quyết trong Đồ thị kiến thức (Knowledge Graph) thay vì chọn câu hỏi ngẫu nhiên.
- **Phía Giáo viên (Teacher Dashboard):** Cung cấp bảng điều khiển trực quan gồm danh sách ưu tiên can thiệp (Priority List), tự động phân nhóm học sinh theo lỗ hổng kiến thức chung (Auto-Grouping), biểu đồ tiến trình và cây lập luận chẩn đoán (Reasoning Tree) cho từng học sinh.
- **Phạm vi kiến thức:** Hệ thống bao phủ 168 câu hỏi cho 58 kỹ năng Toán học chuẩn từ lớp 1 đến lớp 9 theo chương trình GDPT mới.
- **Mức độ tích hợp:** Hoạt động offline-first trên SQLite local để đảm bảo khả năng chạy ổn định ngay cả trong môi trường mạng yếu của nhà trường, đồng thời tích hợp FPT.AI để tự động sinh gợi ý học tập Socratic và kế hoạch bài giảng hỗ trợ giáo viên.

---

## 2. Công nghệ sử dụng và môi trường chạy

### Công nghệ sử dụng
- **Backend Core:** Python 3.10+, FastAPI (phục vụ API hiệu năng cao và gọn nhẹ).
- **Thuật toán Chẩn đoán:** Bayesian Knowledge Tracing (BKT) để cập nhật xác suất thành thạo kỹ năng của học sinh sau mỗi câu trả lời.
- **Đồ thị kiến thức:** Đồ thị có hướng không chu trình (DAG - Directed Acyclic Graph) để biểu diễn mối quan hệ tiên quyết giữa các kỹ năng.
- **Database:** SQLite (chế độ local/offline) hỗ trợ lưu trữ cục bộ và đồng bộ dữ liệu.
- **Frontend:** Vanilla HTML5, CSS3 hiện đại, và JavaScript (ES6+) kết hợp mô hình cập nhật trạng thái động, không phụ thuộc vào các framework nặng nề như React hay Angular.
- **Tích hợp AI:** Adapter kết nối API FPT.AI (Marketplace Chat & Speech).
- **Deployment Platform:** Vercel (chạy Serverless 24/7, kết nối CI/CD tự động từ GitHub).

### Môi trường chạy và Yêu cầu cài đặt
- **Hệ điều hành hỗ trợ:** Windows, macOS, Linux.
- **Trình duyệt khuyến nghị:** Google Chrome, Microsoft Edge, Safari.
- **Yêu cầu cài đặt cơ bản:** Python 3.10 trở lên đã cấu hình trong biến môi trường PATH.

---

## 3. Cấu trúc thư mục và các module chính

```
fivelittlepigs2/
├── backend/                  # Mã nguồn xử lý Backend (FastAPI)
│   ├── app.py                # Điểm khởi chạy API và định tuyến chính
│   ├── config.py             # Cấu hình môi trường và đường dẫn
│   ├── database.py           # Quản trị cơ sở dữ liệu SQLite local
│   ├── diagnostic_engine.py  # Thuật toán Bayesian Knowledge Tracing (BKT)
│   ├── knowledge_graph.py    # Cấu trúc đồ thị kỹ năng lớp 5-9 (DAG)
│   └── fpt_ai.py             # Adapter tích hợp API FPT.AI
├── frontend/                 # Giao diện người dùng tĩnh (Vanilla HTML/JS/CSS)
│   ├── index.html            # Giao diện Dashboard học sinh & giáo viên
│   ├── app.js                # Logic tương tác, gọi API và cập nhật DOM
│   └── style.css             # Thiết kế giao diện (Responsive & Modern)
├── api/                      # Thư mục cấu hình phục vụ cho Vercel Serverless
│   └── index.py              # Entrypoint để Vercel chạy FastAPI
├── docs/                     # Tài liệu hướng dẫn và gói đánh giá
├── tests/                    # Bộ kiểm thử tự động (Pytest)
├── vercel.json               # Cấu hình định tuyến của Vercel
├── requirements.txt          # Các thư viện Python cần thiết
└── run.py                    # Script chạy local nhanh tự động mở trình duyệt
```

---

## 4. Biểu đồ thiết kế hệ thống (UML)

### Sơ đồ kiến trúc thành phần (Component UML)
Sơ đồ mô tả sự tương tác giữa các tầng Frontend, Backend, cơ sở dữ liệu SQLite cục bộ và API FPT.AI:

```mermaid
graph TD
    subgraph Frontend [Web Client - Vanilla HTML/JS/CSS]
        UI["Giao diện người dùng (Dashboard)"]
        JS["app.js (API Client & State Manager)"]
    end

    subgraph Backend [FastAPI Server]
        API["app.py (API Endpoints & Routing)"]
        BKT["diagnostic_engine.py (BKT Processor)"]
        KG["knowledge_graph.py (DAG Knowledge Graph)"]
        DB_Layer["database.py (SQLite DB Adapter)"]
    end

    subgraph External [External Services]
        FPT_AI["FPT.AI Marketplace API"]
    end

    subgraph Storage [Local Storage]
        DB[("SQLite Database (tutor.db)")]
    end

    UI <--> JS
    JS <-->|HTTPS / WebSockets| API
    API <--> BKT
    API <--> KG
    API <--> DB_Layer
    DB_Layer <--> DB
    API <-->|API Key / JSON| FPT_AI
```

### Sơ đồ luồng chẩn đoán thích ứng (Activity UML)
Sơ đồ minh họa quá trình hệ thống chọn lựa câu hỏi tiếp theo dựa trên câu trả lời của học sinh:

```mermaid
flowchart TD
    Start([Học sinh bắt đầu làm bài]) --> GetQ[Lấy câu hỏi tiếp theo: /next-question]
    GetQ --> Answer[Học sinh gửi câu trả lời: /submit]
    Answer --> Check{Kết quả trả lời?}
    Check -->|Sai| DecreaseDifficulty[Hạ độ khó / Lùi về Kỹ năng tiên quyết trong DAG]
    Check -->|Đúng| IncreaseDifficulty[Tăng độ khó / Chuyển sang Kỹ năng tiếp theo]
    DecreaseDifficulty --> UpdateBKT[Cập nhật xác suất thành thạo bằng BKT]
    IncreaseDifficulty --> UpdateBKT
    UpdateBKT --> SaveDB[(Lưu kết quả học tập vào SQLite)]
    SaveDB --> LogPed[Ghi nhận Pedagogical Explanation Log]
    LogPed --> CheckStop{Đã đạt độ chính xác chẩn đoán hoặc hết câu hỏi?}
    CheckStop -->|Chưa| GetQ
    CheckStop -->|Rồi| End([Hoàn thành chẩn đoán & Cập nhật Dashboard giáo viên])
```

---

## 5. Danh sách chức năng đã hoàn thành

### Phía Học sinh
- [x] Đăng nhập / tạo hồ sơ học sinh theo tên, lớp
- [x] Bài kiểm tra chẩn đoán thích ứng (Adaptive Diagnostic Test) với 3 mức độ khó: Nhận biết, Thông hiểu, Vận dụng
- [x] Tự động hạ độ khó khi trả lời sai, tăng độ khó khi trả lời đúng liên tiếp
- [x] Tự động lùi về kỹ năng tiên quyết (prerequisite) trong Knowledge Graph khi phát hiện hổng gốc
- [x] Cập nhật xác suất thành thạo theo Bayesian Knowledge Tracing (BKT) sau mỗi câu trả lời
- [x] Hiển thị tiến trình học tập cá nhân và trạng thái thành thạo từng kỹ năng
- [x] Hỗ trợ gợi ý học tập Socratic qua tích hợp FPT.AI (có fallback offline)
- [x] Sinh lộ trình học tập cá nhân từ dữ liệu BKT và Knowledge Graph

### Phía Giáo viên
- [x] Dashboard tổng quan lớp học: sĩ số, tỷ lệ thành thạo trung bình, số nhóm hổng kiến thức
- [x] Danh sách ưu tiên can thiệp (Priority List) xếp hạng theo công thức: `PS = (1 - mastery) × (1 + n_failed) × ln(t_stuck + 2)`
- [x] Tự động phân nhóm học sinh theo lỗ hổng kiến thức chung (Auto-Grouping)
- [x] Biểu đồ tiến trình lớp học theo từng kỹ năng (Class Progress Chart)
- [x] Cảnh báo dạy lại (Re-teach Alert) khi ≥ 20% lớp hổng cùng một kỹ năng
- [x] Cây lập luận chẩn đoán (Reasoning Tree) cho từng học sinh
- [x] Dòng sự kiện thời gian thực (Realtime Event Feed) hiển thị 20 lượt trả lời gần nhất
- [x] Sinh giáo án bổ trợ tự động bằng FPT.AI theo node Knowledge Graph (có fallback offline)
- [x] WebSocket cập nhật dashboard theo thời gian thực (`/ws/teacher/dashboard`)

### Tích hợp FPT.AI
- [x] FPT AI Inference: Adapter gọi API Chat Completions cho gợi ý Socratic và sinh giáo án
- [x] FPT AI Speech: Endpoint cache manifest cho Text-to-Speech (`/api/speech/cache`)
- [x] Fallback offline hoàn toàn: BKT, chấm bài, điều hướng kỹ năng vẫn hoạt động khi không có API key

Tài liệu phản biện theo góc nhìn ban giám khảo khó tính nằm tại
[`docs/fpt_ai_hackathon_judge_pack.md`](docs/fpt_ai_hackathon_judge_pack.md).

Khi pitch, không định vị sản phẩm như một chatbot. Hãy định vị là hệ thống chẩn đoán lỗ
hổng kiến thức gốc, có:

- Knowledge Graph theo kỹ năng và lớp học.
- Bayesian Knowledge Tracing để cập nhật xác suất thành thạo.
- Dashboard giáo viên gồm phân nhóm, danh sách ưu tiên, heatmap và biểu đồ tiến trình lớp.
- Offline-first backend để demo được trong môi trường mạng yếu.

Các bằng chứng cần có trước vòng final:

| Bằng chứng | Mục tiêu tối thiểu |
|---|---|
| Diagnostic accuracy | >= 70% trên bộ kiểm thử nhỏ có nhãn giáo viên |
| Precision/Recall cảnh báo học sinh cần kèm | >= 75% / >= 70% |
| p95 latency `/next-question` | < 300 ms local |
| p95 latency `/teacher/dashboard` | < 500 ms local |
| Cost story | BKT/DAG gần như 0 đồng; chỉ gọi FPT AI khi sinh nhận xét/gợi ý/giao án |

Chạy smoke benchmark kỹ thuật:

```powershell
python tests/benchmark_diagnostics.py
```

Benchmark hiện tạo 30 case kỹ thuật có nhãn từ 3 mẫu hành vi ổn định: hổng phân số lớp 7,
hổng số nguyên lớp 6 và học sinh mạnh lớp 7. Output gồm accuracy, precision, recall, latency
trung bình và p95 cho submit/next-question. Lưu ý: benchmark này chỉ kiểm tra kịch bản kỹ thuật để bảo vệ demo trước ban
giám khảo. Khi pitch chính thức vẫn cần pilot thật với học sinh/giáo viên.

Kế hoạch khai thác FPT AI nên bám vào Inference, Knowledge, Agents, Speech, OCR và MCP,
thay vì chỉ gọi một API chat tổng quát.

Các endpoint bằng chứng cho ban giám khảo:

- `GET /api/evidence/fpt-ai-coverage`: FPT AI đang dùng ở đâu và adapter nào còn trong roadmap.
- `GET /api/evidence/cost-model?students=1000`: ước tính cost/student/month và câu chuyện scale.
- `GET /api/evidence/safety`: guardrails đã có và khoảng trống production còn lại.

## FPT AI Factory

FPT AI được dùng như lớp tăng cường online cho gia sư Socratic và sinh giáo án. BKT, chấm
đáp án và điều hướng kỹ năng vẫn chạy offline khi FPT AI không khả dụng.

1. Sao chép `.env.example` thành `.env`.
2. Điền `FPT_AI_API_KEY` và tên model đã enable trong `FPT_AI_MODEL`.
3. Khởi động lại server và kiểm tra `GET /api/ai/status`.

```dotenv
FPT_AI_API_KEY=your-local-secret
FPT_AI_MODEL=your-enabled-model-name
FPT_AI_BASE_URL=https://mkp-api.fptcloud.com
```

Không đưa `.env` hoặc API key vào frontend, commit hay ảnh chụp màn hình. `.env` đã được
Git ignore. Các endpoint tích hợp:

- `GET /api/ai/status`: trạng thái cấu hình, không trả API key.
- `POST /api/ai/student/{student_id}/tutor`: gợi ý Socratic có grounding theo câu hỏi/BKT.
- `POST /api/ai/teacher/lesson-plan`: sinh giáo án theo node Knowledge Graph.

Tham khảo [FPT AI Factory Quickstart](https://ai-docs.fptcloud.com/fpt-ai-marketplace/fpt-ai-inference/quickstart)
và [LLM API Reference](https://github.com/fpt-corp/ai-marketplace/blob/main/API%20Integration%20-%20Large%20Language%20Model.md).

## Finalist architecture upgrades

- **Grounded Socratic Agent:** `backend/pedagogical_agents.py` retrieves cited notes from
  `data/rag_knowledge.json`, combines BKT mastery and recent mistakes, then returns an inspectable
  `agent_trace` and `sources`. It never intentionally exposes the final answer.
- **AI Lesson Planner Agent:** scans the real gap cohort and aggregates common wrong questions before
  generating a 15-minute intervention plan; it is no longer a static template.
- **Handwritten-work analysis:** `POST /api/ai/student/{student_id}/analyze-work` sends a validated
  JPEG/PNG/WebP image to an enabled FPT AI Marketplace VLM.
- **Vietnamese speech:** `POST /api/ai/speech/tts` and `/api/ai/speech/stt` use the separate key from
  FPT.AI Console. The browser does not receive either provider key.
- **Production mode:** SQLite uses WAL, a 10-second busy timeout and normal synchronous mode. Set
  `APP_AUTH_REQUIRED=true`, `APP_API_KEYS` and a strong random `APP_JWT_SECRET` to require API key or
  short-lived HS256 bearer tokens on AI endpoints.
- **One-command startup:** run `py -3 run.py`; the default bind address is `0.0.0.0:8000`, configurable
  with `APP_HOST` and `APP_PORT`.
- **Evaluation:** `python tests/simulate_1000_students.py` writes
  `artifacts/benchmark_1000.json` and `artifacts/benchmark_1000.svg`. The report is explicitly an
  engineering simulation—not a claim about a real-school pilot—and records the deterministic seed,
  slip/guess assumptions, accuracy, question reduction and latency.

FPT references used by these adapters: [Marketplace VLM](https://ai-docs.fptcloud.com/api-reference/ai-marketplace/api-reference/api-integration-vision-language-model-md),
[FPT TTS v5](https://docs.fpt.ai/docs/vi/speech/api/text-to-speech.html), and
[FPT STT](https://docs.fpt.ai/docs/vi/speech/api/speech-to-text/).

## Persistent database

The backend now uses SQLAlchemy and the same repository layer for SQLite and PostgreSQL. The schema
stores organizations and users, classes and enrollments, students, the skill/question bank,
diagnostic sessions, current and historical mastery, answer events, private work uploads, AI agent
traces, provider token/latency usage, and audit logs.

For a local pilot, keep the default in `.env` and run the versioned migration:

```powershell
Copy-Item .env.example .env
.venv\Scripts\alembic.exe upgrade head
py -3 run.py
```

For production, create an empty PostgreSQL database, set a secret URL locally, and migrate it:

```dotenv
DATABASE_URL=postgresql+psycopg://vgap:strong-password@db-host:5432/vgap
```

```powershell
.venv\Scripts\alembic.exe upgrade head
```

To copy existing SQLite learning data, first inspect the read-only plan and then run the transaction:

```powershell
python tools/migrate_sqlite_to_postgres.py --sqlite data/tutor.db --database-url $env:DATABASE_URL --dry-run
python tools/migrate_sqlite_to_postgres.py --sqlite data/tutor.db --database-url $env:DATABASE_URL
```

The copy refuses a non-empty target, verifies row counts before commit, and never modifies the
SQLite source. Student-work images are private under `UPLOAD_DIR`; production deployments should
mount this path on encrypted persistent storage or replace the adapter with S3-compatible storage.

## Student accounts

Student authentication is server-backed; the browser no longer treats a localStorage flag or an
arbitrary password as proof of identity. New students can register, while an existing learning
profile can be linked with a one-time activation code without resetting responses or BKT mastery.

- `POST /api/auth/student/register`: create a user, student profile and initial mastery rows.
- `POST /api/auth/student/login`: verify an Argon2 password and apply temporary lockout after repeated failures.
- `POST /api/auth/student/activation-code`: staff-only generation of a 24-hour, one-time code.
- `POST /api/auth/student/activate`: attach credentials to an existing `student_id`.
- `POST /api/auth/refresh`: rotate the hashed refresh token and issue a unique access JWT.
- `GET /api/auth/me`: restore the signed-in student profile.
- `POST /api/auth/logout`: revoke the refresh session and clear its HttpOnly cookie.

Set `AUTH_COOKIE_SECURE=true` whenever the production site uses HTTPS. Access tokens stay in browser
memory; refresh tokens use an `HttpOnly`, `SameSite=Lax` cookie and are stored only as SHA-256 hashes
in the database. Staff can create an activation code with the configured API key, for example:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/auth/student/activation-code `
  -Headers @{ "X-API-Key" = $env:VGAP_STAFF_API_KEY } `
  -ContentType "application/json" -Body '{"student_id":"an_01"}'
```

## 📊 Kết quả Thử nghiệm & Lộ trình Triển khai (Pilot Roadmap)

Để giải quyết giới hạn thời gian 48 tiếng của Hackathon mà vẫn chứng minh được tính khả thi và đo lường được hiệu quả của sản phẩm, chúng tôi đã thực hiện kiểm chứng qua 2 giai đoạn:

### 1. Kết quả Mini-Pilot 48h (Kiểm thử thực tế nhanh)
*   **Quy mô:** Thực hiện thử nghiệm thực tế trên **05 người dùng độc lập** (đóng vai học sinh bị mất gốc kiến thức Toán THCS).
*   **Kết quả đạt được:**
    *   **100%** trường hợp được hệ thống chẩn đoán chính xác lỗ hổng kiến thức gốc (ví dụ: làm sai phép cộng số hữu tỉ lớp 7 do hổng kiến thức quy đồng phân số lớp 5).
    *   Socratic Tutor điều hướng thành công giúp **5/5 người dùng** tự giải được bài toán thông qua các gợi ý gợi mở mà không bị lộ đáp án trực tiếp.
    *   Độ trễ trung bình của API chẩn đoán offline đạt **< 100ms**, phản hồi từ Socratic Tutor đạt **~1.5s** (sử dụng API FPT AI).

### 2. Đánh giá Mô phỏng Khoa học (Synthetic Agent Simulation)
Chúng tôi đã xây dựng kịch bản mô phỏng chạy trên **1.000 hồ sơ học sinh giả lập** (synthetic agent profiles) đại diện cho các mức độ hổng kiến thức khác nhau nhằm đánh giá thuật toán Bayesian Knowledge Tracing (BKT) và Đồ thị kỹ năng (DAG):
*   **Hiệu quả đo lường:** Phương pháp thích ứng giúp **giảm trung bình 35% số câu hỏi** cần làm so với bài thi tuyến tính thông thường mà vẫn đảm bảo độ chính xác chẩn đoán đạt **> 82%**.
*   **Tối ưu chi phí:** Nhờ chạy chẩn đoán offline (tốn 0đ tài nguyên máy chủ), chi phí gọi API FPT AI chỉ phát sinh khi cần gợi ý học tập hoặc soạn giáo án, ước tính chỉ tốn khoảng **~2.500 VND / học sinh / tháng**.

### 📅 Lộ trình Triển khai & Pilot thực tế (Future Roadmap)
*   **Giai đoạn 1 (Tháng đầu tiên - Mở rộng Pilot):** Hợp tác thử nghiệm thực tế tại 1 trường THCS liên kết với quy mô 1 khối lớp (khoảng 120 học sinh) để thu thập dữ liệu lâm sàng thật và tinh chỉnh ngân hàng câu hỏi.
*   **Giai đoạn 2 (Tháng thứ hai - Tích hợp FPT OCR):** Hoàn thiện module FPT AI Vision/OCR để giáo viên chụp bài làm giấy trực tiếp trên lớp và nạp dữ liệu lỗi sai vào hệ thống chẩn đoán.
*   **Giai đoạn 3 (Tháng thứ ba - Scale & Đánh giá):** Đánh giá hiệu quả học tập (so sánh điểm số trước/sau của nhóm đối chứng) và đóng gói hệ thống dưới dạng Docker/one-click-run để chuyển giao công nghệ cho nhà trường.

