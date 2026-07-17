import sqlite3
import os
import json
from backend.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL
        )
    """)
    
    # Create student_mastery table (P(M) for each skill)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_mastery (
            student_id TEXT,
            skill_id TEXT,
            mastery_probability REAL DEFAULT 0.5,
            PRIMARY KEY (student_id, skill_id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    
    # Create responses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            question_id TEXT,
            skill_id TEXT,
            difficulty_level INTEGER DEFAULT 2,
            is_correct INTEGER,
            timestamp INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    
    # Try adding the difficulty_level column in case the table already existed
    try:
        cursor.execute("ALTER TABLE responses ADD COLUMN difficulty_level INTEGER DEFAULT 2")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    
    # Insert mock students if database is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        mock_students = [
            ("emma_std_01", "Emma", 7),
            ("an_01", "Nguyễn Văn An", 6),
            ("binh_02", "Trần Bình", 5),
            ("chi_03", "Lê Chi", 7),
            ("dung_04", "Nguyễn Dũng", 5),
            ("giang_05", "Phạm Giang", 6),
            ("hoang_06", "Lê Huy Hoàng", 7),
            ("linh_08", "Phạm Khánh Linh", 6)
        ]
        cursor.executemany("INSERT INTO students (id, name, grade) VALUES (?, ?, ?)", mock_students)
        conn.commit()
        
        # Initialize default mastery values
        cursor.execute("SELECT id FROM students")
        student_ids = [row[0] for row in cursor.fetchall()]
        
        from backend.knowledge_graph import KNOWLEDGE_GRAPH
        for s_id in student_ids:
            for skill_id in KNOWLEDGE_GRAPH.keys():
                # Set specific gap states for mock students for demo purposes
                prob = 0.5
                if s_id == "an_01" and skill_id == "MATH_G7": prob = 0.1
                elif s_id == "an_01" and skill_id == "MATH_G6": prob = 0.3
                elif s_id == "binh_02" and skill_id == "MATH_G5": prob = 0.22
                elif s_id == "dung_04" and skill_id == "MATH_G5_LCM": prob = 0.15
                elif s_id == "chi_03" and skill_id == "MATH_G7": prob = 0.88
                
                cursor.execute("""
                    INSERT OR REPLACE INTO student_mastery (student_id, skill_id, mastery_probability)
                    VALUES (?, ?, ?)
                """, (s_id, skill_id, prob))
        conn.commit()
        
    conn.close()

def get_student(student_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_mastery(student_id, skill_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT mastery_probability FROM student_mastery 
        WHERE student_id = ? AND skill_id = ?
    """, (student_id, skill_id)).fetchone()
    conn.close()
    return row[0] if row else 0.5

def update_student_mastery(student_id, skill_id, prob):
    conn = get_db_connection()
    conn.execute("""
        INSERT OR REPLACE INTO student_mastery (student_id, skill_id, mastery_probability)
        VALUES (?, ?, ?)
    """, (student_id, skill_id, prob))
    conn.commit()
    conn.close()

def record_response(student_id, question_id, skill_id, difficulty_level, is_correct, timestamp):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO responses (student_id, question_id, skill_id, difficulty_level, is_correct, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, question_id, skill_id, difficulty_level, 1 if is_correct else 0, timestamp))
    conn.commit()
    conn.close()

def get_consecutive_failed_count(student_id, skill_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_correct FROM responses 
        WHERE student_id = ? AND skill_id = ?
        ORDER BY id DESC LIMIT 10
    """, (student_id, skill_id))
    rows = cursor.fetchall()
    conn.close()
    
    count = 0
    for row in rows:
        if row[0] == 0:
            count += 1
        else:
            break
    return count

def get_stuck_time_minutes(student_id, skill_id):
    # Returns estimated minutes student has been stuck on a skill (time difference from first response in active streak to now)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp FROM responses 
        WHERE student_id = ? AND skill_id = ?
        ORDER BY id DESC
    """, (student_id, skill_id))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 2  # default fallback mock
    
    # Calculate time between first and last attempt in current session
    last_attempt = rows[0][0]
    # Let's count how far back the failure goes
    failures_time = [r[0] for r in rows]
    if len(failures_time) > 1:
        diff_secs = failures_time[0] - failures_time[-1]
        return max(2, int(diff_secs / 60))
    return 2
