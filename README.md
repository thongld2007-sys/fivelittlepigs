# Adaptive Tutoring System — Backend

FastAPI + SQLite backend chạy offline trên máy giáo viên hoặc máy chủ LAN. Hệ thống chấm
trắc nghiệm phía server, cập nhật Bayesian Knowledge Tracing, điều hướng xuống kỹ năng tiên
quyết và cung cấp dashboard API cho giáo viên.

## Chạy local

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Swagger UI: `http://localhost:8000/docs`. Health check: `GET /api/health`.

Giao diện VGap AI được đồng bộ từ repository `thongld2007-sys/fivelittlepigs` và được
FastAPI phục vụ trực tiếp tại `http://localhost:8000/`; không cần chạy thêm npm hoặc web
server riêng. Frontend đã được chuẩn hóa để dùng API an toàn của backend này thay cho API
prototype trong repository nguồn.

Ngân hàng mở rộng từ repo gồm 165 câu cho 55 kỹ năng thuộc 6 môn, lớp 1–9. Ba câu hỏi lõi
và ba mã kỹ năng chuẩn trong báo cáo vẫn được giữ lại, nâng tổng số lên 168 câu và 58 node
Knowledge Graph. Backend tự chuẩn hóa hai schema dữ liệu khi khởi động.

## Luồng API tối thiểu

1. `POST /api/students` tạo/cập nhật hồ sơ học sinh.
2. `GET /api/student/{id}/next-question` lấy câu tiếp theo không chứa đáp án.
3. `POST /api/student/{id}/submit` gửi `question_id`, `selected_index`, `time_spent` và
   `event_id` tùy chọn. Backend tự chấm và yêu cầu lặp có cùng `event_id` là idempotent.
4. Dashboard dùng `/api/teacher/priority-list`, `/api/teacher/groups`,
   `/api/teacher/gap-alerts` và `/api/teacher/students/{id}/reasoning-tree`.
5. Tab giáo viên "Bằng chứng final" dùng `GET /api/evidence/final-scorecard` để trình bày
   scorecard barem, benchmark, câu chuyện FPT AI và readiness triển khai trong một màn demo.

## Đồng bộ mạng yếu

Đặt `TUTOR_CLOUD_SYNC_URL` và tùy chọn `TUTOR_DEVICE_ID`. `POST /api/sync/push` gửi batch
log JSON nén gzip. Chỉ sau HTTP 2xx các event local mới được đánh dấu đã đồng bộ. Khi chưa
cấu hình hoặc mất mạng, log vẫn nằm an toàn trong SQLite.

Các biến khác: `TUTOR_DB_PATH`, `TUTOR_DATA_DIR`, `TUTOR_QUESTIONS_PATH`,
`TUTOR_REPO_QUESTIONS_PATH`,
`TUTOR_SYNC_TIMEOUT_SECONDS`, `TUTOR_MAX_SYNC_BATCH`.

## Kiểm thử

```powershell
python -m pytest -q
```

Test sử dụng SQLite tạm, không ghi vào `data/tutor.db` thật.

## Demo kịch bản backend

```powershell
py -3 demo_backend.py
```

Demo mô phỏng học sinh lớp 7 trả lời sai, chẩn đoán xuống lỗ hổng phân số lớp 5 và hiển thị
Priority List, Auto-Grouping, Gap Alert cùng Reasoning Tree. Demo dùng database tạm.

## Tài khoản giao diện demo

- Học sinh: chọn một hồ sơ có sẵn và nhập mật khẩu bất kỳ không rỗng.
- Giáo viên: mật khẩu demo `123456`.

Đây chỉ là luồng đăng nhập trình diễn phía frontend, chưa phải cơ chế xác thực dùng trong
production. Khi triển khai thực tế cần bổ sung tài khoản, mật khẩu băm và phân quyền API.

## Chuẩn bị FPT AI Hackathon Final

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
- `GET /api/evidence/final-scorecard`: payload tổng hợp cho tab "Bằng chứng final" trong
  dashboard giáo viên.

Các lát production đã có trong bản demo mới:

- Event log idempotent để đồng bộ SQLite local lên cloud theo batch.
- Pedagogical explanation log giải thích vì sao hệ thống hạ độ khó hoặc lùi prerequisite.
- Behavioral anomaly filter giảm trọng số BKT cho câu khó trả lời đúng quá nhanh.
- Grounded lesson-plan endpoint có citation từ local knowledge base, sẵn nối FPT AI Knowledge.
- Speech cache manifest để sinh audio một lần và phát lại qua LAN khi nối FPT AI Speech.
- WebSocket dashboard snapshot tại `/ws/teacher/dashboard`.

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
