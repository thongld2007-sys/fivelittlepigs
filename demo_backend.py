"""One-command backend demo for the Adaptive Tutoring System.

Run: py -3 demo_backend.py
The script uses a temporary SQLite database and never changes data/tutor.db.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")

# Configuration must be set before importing the backend modules.
DEMO_DIR = tempfile.TemporaryDirectory(prefix="adaptive_tutor_demo_")
os.environ["TUTOR_DB_PATH"] = str(Path(DEMO_DIR.name) / "demo.db")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402


def title(text: str) -> None:
    print(f"\n{'=' * 68}\n{text}\n{'=' * 68}")


def show_probability(payload: dict) -> None:
    diagnostic = payload["diagnostic"]
    print(f"  Kết quả: {'ĐÚNG' if payload['is_correct'] else 'SAI'}")
    print(
        f"  Xác suất thành thạo: {payload['previous_probability']:.4f}"
        f" → {payload['new_probability']:.4f}"
    )
    print(f"  Quyết định: {diagnostic['action']}")
    print(f"  Kỹ năng tiếp theo: {diagnostic['target_skill'] or 'Không có'}")
    print(f"  Giải thích: {diagnostic['reason']}")


def run_demo() -> None:
    title("DEMO ADAPTIVE TUTORING SYSTEM — BACKEND ENGINEERING")
    print("Kịch bản: Minh, học sinh lớp 7, gặp khó khăn với số hữu tỉ.")
    print("Database demo:", os.environ["TUTOR_DB_PATH"])

    with TestClient(app) as client:
        title("BƯỚC 1 — TẠO HỒ SƠ HỌC SINH")
        response = client.post(
            "/api/students",
            json={"student_id": "student_minh", "name": "Nguyễn Văn Minh", "grade": 7},
        )
        response.raise_for_status()
        print(response.json())

        title("BƯỚC 2 — BACKEND CẤP CÂU HỎI LỚP 7")
        response = client.get(
            "/api/student/student_minh/next-question",
            params={"current_skill_id": "MATH7_ADD_RATIONAL"},
        )
        response.raise_for_status()
        question = response.json()["question"]
        print("Câu hỏi:", question["content"])
        for index, option in enumerate(question["options"]):
            print(f"  [{index}] {option}")
        print("Đáp án đúng đã được backend ẩn:", "correct_index" not in question)

        title("BƯỚC 3 — MINH TRẢ LỜI SAI, BKT MỞ LUỒNG CHẨN ĐOÁN")
        response = client.post(
            "/api/student/student_minh/submit",
            json={"question_id": "math7_q01", "selected_index": 1, "time_spent": 35},
        )
        response.raise_for_status()
        show_probability(response.json())

        title("BƯỚC 4 — KIỂM TRA KỸ NĂNG GỐC LỚP 5")
        print("Minh tiếp tục trả lời sai 3 câu kiểm tra quy đồng phân số.")
        latest = None
        for attempt in range(1, 4):
            response = client.post(
                "/api/student/student_minh/submit",
                json={"question_id": "math5_q01", "selected_index": 0, "time_spent": 30},
            )
            response.raise_for_status()
            latest = response.json()
            print(
                f"  Lần {attempt}: P(M)={latest['new_probability']:.4f}, "
                f"sai liên tiếp={latest['consecutive_fails']}, "
                f"action={latest['diagnostic']['action']}"
            )
        print("\nKết luận:", latest["diagnostic"]["reason"])

        title("BƯỚC 5 — DASHBOARD TRỢ LÝ GIÁO VIÊN")
        priority = client.get("/api/teacher/priority-list").json()
        groups = client.get("/api/teacher/groups").json()
        alerts = client.get("/api/teacher/gap-alerts").json()
        print("Priority List:")
        for item in priority:
            print(
                f"  {item['student_name']} | {item['skill_id']} | "
                f"score={item['priority_score']}"
            )
        print("\nAuto-Grouping:")
        for group in groups["groups"]:
            print(
                f"  {group['skill_name']}: {group['weak_students']} học sinh "
                f"({group['percentage']}%)"
            )
        print("\nClass-wide Gap Alerts:")
        for alert in alerts["alerts"]:
            print(" ", alert["message"])

        title("BƯỚC 6 — REASONING TREE MINH BẠCH")
        events = client.get(
            "/api/teacher/students/student_minh/reasoning-tree"
        ).json()["events"]
        for number, event in enumerate(events, 1):
            print(
                f"  {number}. {event['skill_id']}: "
                f"{event['previous_probability']:.4f} → {event['new_probability']:.4f} "
                f"| {event['action']} → {event['target_skill']}"
            )

        title("DEMO HOÀN TẤT")
        print("✓ Chấm đáp án phía server")
        print("✓ BKT cập nhật xác suất thành thạo")
        print("✓ Chẩn đoán lỗ hổng đa tầng lớp 7 → lớp 5")
        print("✓ Priority List, Auto-Grouping và Gap Alert")
        print("✓ Reasoning Tree giải thích mọi quyết định")
        print("✓ Không thay đổi database thật")


if __name__ == "__main__":
    try:
        run_demo()
    finally:
        DEMO_DIR.cleanup()
