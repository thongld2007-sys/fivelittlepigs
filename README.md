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
