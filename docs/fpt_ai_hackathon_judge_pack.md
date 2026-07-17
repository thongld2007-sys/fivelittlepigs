# FPT AI Hackathon Judge Pack

Tai lieu nay dung de chuan bi pitch theo goc nhin cua ban giam khao kho tinh. Mac dinh du an khong dat neu khong chung minh duoc gia tri giao duc, AI that su can thiet, benchmark va kha nang trien khai.

## 1. Ket Luan Nhanh Cho Final Round

VGap AI khong nen duoc pitch nhu mot chatbot hoc tap. San pham nen duoc pitch nhu mot he thong chan doan lo hong kien thuc goc cho giao vien va hoc sinh, chay offline-first, co knowledge graph, Bayesian Knowledge Tracing, ngan hang cau hoi, dashboard can thiep lop hoc va lo trinh hoc ca nhan.

Diem manh hien tai:

- Co bai toan giao duc ro: hoc sinh bi mat goc nhung giao vien khong biet mat o dau.
- Co co che adaptive that: chon do kho 2/3, sai thi ha muc, sai muc 1 thi lui ve tien quyet trong DAG.
- Co du lieu cuc bo: SQLite luu hoc sinh, responses, mastery; ngan hang 189 cau hoi.
- Co dashboard giao vien: phan nhom lo hong, danh sach uu tien, heatmap, chart tien trinh lop.
- Co API co the demo that: `/api/student/{id}/next-question`, `/api/check-answer`, `/api/teacher/dashboard`.

Rui ro bi tru diem:

- Chua co benchmark tren nguoi dung that.
- Chua co tich hop FPT AI that su trong code.
- Chua co evaluation day du: accuracy, precision, recall, latency, cost.
- Dang co login demo frontend, chua phai auth production.
- Ngan hang cau hoi con nho neu trien khai toan truong.

## 2. Bang Cham Diem Tam Thoi

| Hang muc | Diem toi da | Diem hien tai | Ly do |
|---|---:|---:|---|
| Bai toan giao duc | 15 | 10 | Dung van de that: mat goc va qua tai giao vien. Thieu khao sat/so lieu truong that. |
| AI co can thiet khong | 15 | 9 | BKT + knowledge graph tao gia tri hon chatbot. Can chung minh AI/FPT AI vuot rule engine o dau. |
| Khai thac FPT AI | 15 | 3 | Hien chua co FPT AI runtime. Can them Agent/Inference/Knowledge/Speech/OCR/MCP vao demo. |
| AI Engineering | 15 | 8 | Co data schema, BKT, DAG, API. Thieu benchmark, eval set, cost/latency log. |
| Gia tri giao duc | 15 | 8 | Co lo trinh va dashboard. Thieu pilot truoc/sau de chung minh tang diem/tiet kiem gio. |
| Kha nang trien khai | 10 | 7 | Offline-first va SQLite tot cho truong hoc. Chua co auth, backup, deployment guide day du. |
| Kha nang scale | 5 | 3 | FastAPI co the scale, nhung SQLite phu hop local/LAN hon la 10k+ user. |
| Dao duc va an toan | 5 | 2 | Co chong lo dap an truc tiep o short answer mot phan. Thieu policy hallucination, prompt injection, PII. |
| Tong | 100 | 50 | Du an co loi san pham that, nhung can bo sung FPT AI va bang chung dinh luong. |

Muc tieu truoc khi nop final: dua tong len 72-78 bang cach them evidence, FPT AI integration mock/real, benchmark va safety story.

## 3. Dinh Vi Bai Toan

### Bai toan

Hoc sinh lop 5-9 thuong sai bai lop hien tai khong phai vi bai moi qua kho, ma vi hong kien thuc tien quyet tu lop truoc. Giao vien co si so 35-45 hoc sinh kho theo doi tung em, nen viec phat hien lo hong goc thuong cham va cam tinh.

### Nguoi dau nhat

- Giao vien Toan/mon chinh: phai cham, phan nhom, ke hoach bo tro bang tay.
- Hoc sinh trung binh/yeu: khong biet minh hong o dau, cang hoc cang mat dong luc.
- Phu huynh/trung tam: ton tien hoc them nhung khong co chan doan goc.

### Gia tri can chung minh

- Giam thoi gian giao vien phan loai lop tu 2-3 gio/tuan xuong 10-15 phut.
- Tang ty le hoc sinh hoan thanh bai luyen tu baseline len them 15-25%.
- Tang diem post-test sau 2 tuan bo tro them 10-20% voi nhom hong goc.

## 4. Vi Sao AI Can Thiet

Khong pitch rang AI "tra loi cau hoi". Pitch rang AI duoc dung o 4 lop:

1. Diagnostic engine: Bayesian Knowledge Tracing cap nhat xac suat thanh thao theo tung ky nang.
2. Knowledge graph reasoning: sai muc 1 thi lui ve node tien quyet trong DAG, khong random lung tung.
3. Teacher intelligence: tu responses sinh phan nhom, priority score, canh bao giang lai.
4. Generative support: FPT AI sinh goi y Socratic, giao an bo tro va tom tat lo trinh, nhung khong thay the core diagnosis.

Neu bo generative AI, he thong van cham va dieu huong duoc. Neu bo diagnostic AI/BKT/DAG, san pham chi con la quiz app. Day la cau tra loi can noi voi giam khao.

## 5. Ke Hoach Khai Thac FPT AI

Can trinh bay ro FPT AI khong chi la logo trong slide.

| FPT AI thanh phan | Cach dung trong VGap AI | Gia tri |
|---|---|---|
| FPT AI Inference | Sinh goi y Socratic va tom tat lo trinh tu diagnostic events | Giam thoi gian giao vien viet nhan xet |
| FPT AI Knowledge | Luu chuong trinh GDPT, rubric ky nang, cau hoi da kiem dinh | RAG dung ngu canh giao duc Viet Nam |
| FPT AI Agents | Agent giao vien: tu gap groups de xuat giao an 15 phut | Bien dashboard thanh hanh dong |
| FPT AI Speech | Doc cau hoi/goi y cho hoc sinh tieu hoc hoac hoc sinh kho doc | Tang kha nang tiep can |
| FPT AI OCR | Giao vien chup de/bai lam giay, tach cau hoi va loi sai | Dua workflow that cua lop hoc vao he thong |
| FPT AI MCP | Ket noi LMS, Google Sheet/Excel diem, dashboard truong | Trien khai enterprise de hon |

Thong diep: ChatGPT co the tra loi mot cau hoi. FPT AI ecosystem giup ket noi du lieu truong hoc, tieng Viet, giong noi, OCR, knowledge base va workflow giao vien.

## 6. Benchmark Bat Buoc Can Co

Them mot file CSV/JSON benchmark nho truoc demo:

| Metric | Cach do | Muc demo chap nhan |
|---|---|---|
| Diagnostic accuracy | So sanh root gap du doan voi nhan xet giao vien tren 30 hoc sinh | >= 70% |
| Precision gap alert | Trong cac canh bao "can kem", bao nhieu em that su can kem | >= 75% |
| Recall gap alert | Trong cac em can kem, he thong bat duoc bao nhieu | >= 70% |
| Latency next-question | p95 API `/next-question` | < 300 ms local |
| Latency dashboard | p95 API `/teacher/dashboard` | < 500 ms local |
| Cost | Chi phi AI moi hoc sinh/thang | Co 2 che do: offline rule/BKT gan 0 dong, FPT AI chi goi khi can sinh nhan xet |

Can tao script `tests/benchmark_diagnostics.py` neu con thoi gian.

## 7. Kich Ban Demo 3 Phut

1. Mo dashboard hoc sinh, dang nhap.
2. Chon Toan lop 7, bat dau test.
3. Tra loi sai cau huu ti muc 1 de he thong lui ve quy dong/BCNN.
4. Tra loi dung lien tiep de thay do kho tang lai.
5. Hoan thanh mot phan va mo dashboard giao vien.
6. Cho thay: chart tien trinh lop, nhom hong kien thuc, danh sach uu tien, heatmap.
7. Mo giao an bo tro/AI summary: "day la viec giao vien can ngay sau tiet kiem tra".

Khong demo nhu chatbot. Demo nhu mot quy trinh can thiep giao duc.

## 8. Red Team Answers

### Hieu truong: Tai sao toi phai mua?

Vi san pham giam thoi gian phat hien hoc sinh mat goc va tao dashboard can thiep cho giao vien. Muc mua khong dua tren chatbot, ma dua tren ty le hoc sinh duoc can thiep som va bao cao tien bo co the giai trinh voi phu huynh.

### Giao vien: Tai sao toi phai dung?

Vi co ngay danh sach em nao can kem, dang hong ky nang nao, va nhom nao nen giang lai chung. Giao vien khong phai tu loc 40 bai lam va doan cam tinh.

### Hoc sinh: Tai sao toi khong dung ChatGPT mien phi?

ChatGPT tra loi cau hoi hien tai. VGap AI phat hien em sai vi hong o dau trong chuoi kien thuc, bat em luyen dung muc, va khong cho nhay qua goc mat nen em tien bo ben vung hon.

### Nha dau tu: Dieu gi ngan Google/OpenAI sao chep?

Loi the khong nam o model nen. Loi the nam o du lieu hoc tap Viet Nam, knowledge graph GDPT, workflow giao vien, tich hop truong hoc, va diagnostic history theo tung hoc sinh.

### CTO: He thong sap o dau dau tien?

Ban demo local se sap o cac diem: SQLite khi ghi dong thoi qua nhieu, login demo khong co auth, WebSocket chua co backend stream, ngan hang cau hoi con nho. Ke hoach production: PostgreSQL, queue event, auth role-based, cache dashboard, AI call async.

## 9. Checklist Can Lam Truoc Khi Pitch

- [ ] Them benchmark script va ket qua mau.
- [ ] Them bang cost/latency vao README.
- [ ] Them FPT AI integration adapter interface, ke ca mock neu chua co key.
- [ ] Them safety section: PII, prompt injection, hallucination, anti-cheating.
- [ ] Demo dashboard giao vien truoc chatbot.
- [ ] Chuan bi 3 so lieu gia dinh co can cu: thoi gian tiet kiem, p95 latency, cost per student.
- [ ] Co video offline phong khi Wi-Fi su kien yeu.

