import os
import re

# File paths for Adaptive Tutoring System
BRAINSTORMING_PATH = r"C:\Users\ThinkPad\.gemini\antigravity-ide\brain\94e64a21-1e1b-44c5-aa42-7f86b290601b\adaptive_tutor_brainstorming.md"
PLAN_PATH = r"C:\Users\ThinkPad\.gemini\antigravity-ide\brain\94e64a21-1e1b-44c5-aa42-7f86b290601b\implementation_plan.md"
OUTPUT_HTML_PATH = r"c:\Users\ThinkPad\OneDrive - MSFT\Desktop\VNAI\Adaptive_Tutoring_System_Report.html"

def md_to_html(md_text):
    """
    Custom lightweight Markdown to HTML parser with zero dependencies.
    """
    html = ""
    lines = md_text.split('\n')
    in_list = False
    in_code = False
    in_table = False
    table_headers = []
    
    for line in lines:
        stripped = line.strip()
        
        # Code block toggle
        if stripped.startswith('```'):
            if in_code:
                html += "</code></pre>\n"
                in_code = False
            else:
                lang = stripped[3:].strip()
                html += f'<pre class="code-block"><code class="language-{lang}">'
                in_code = True
            continue
            
        if in_code:
            # Escape HTML characters inside code blocks
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html += escaped + '\n'
            continue

        # Close list if not in list anymore
        if in_list and not (stripped.startswith('-') or stripped.startswith('*') or re.match(r'^\d+\.', stripped)):
            html += "</ul>\n"
            in_list = False

        # Close table if not in table
        if in_table and not stripped.startswith('|'):
            html += "</tbody></table></div>\n"
            in_table = False

        # Headers
        if stripped.startswith('# '):
            html += f"<h1>{stripped[2:]}</h1>\n"
        elif stripped.startswith('## '):
            html += f"<h2>{stripped[3:]}</h2>\n"
        elif stripped.startswith('### '):
            html += f"<h3>{stripped[4:]}</h3>\n"
        elif stripped.startswith('#### '):
            html += f"<h4>{stripped[5:]}</h4>\n"
            
        # Horizontal rule
        elif stripped == '---':
            html += "<hr>\n"
            
        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            content = stripped[2:]
            html += f"<li>{content}</li>\n"
            
        # Blockquotes & Alerts
        elif stripped.startswith('> '):
            content = stripped[2:]
            if "[!IMPORTANT]" in content:
                content = content.replace("[!IMPORTANT]", "")
                html += f'<blockquote class="alert alert-important">{content}</blockquote>\n'
            elif "[!WARNING]" in content:
                content = content.replace("[!WARNING]", "")
                html += f'<blockquote class="alert alert-warning">{content}</blockquote>\n'
            elif "[!NOTE]" in content:
                content = content.replace("[!NOTE]", "")
                html += f'<blockquote class="alert alert-note">{content}</blockquote>\n'
            else:
                html += f"<blockquote>{content}</blockquote>\n"
                
        # Tables
        elif stripped.startswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if not in_table:
                in_table = True
                table_headers = cells
                html += '<div class="table-container"><table><thead><tr>\n'
                for cell in cells:
                    html += f"<th>{cell}</th>\n"
                html += "</tr></thead><tbody>\n"
            else:
                # Skip divider line e.g. |---|---|
                if all(c.startswith('-') or c == '' for c in cells):
                    continue
                html += "<tr>\n"
                for cell in cells:
                    html += f"<td>{cell}</td>\n"
                html += "</tr>\n"
                
        # Blank line
        elif stripped == '':
            html += "<br>\n"
            
        # Plain text paragraphs
        else:
            html += f"<p>{stripped}</p>\n"

    # Clean up unclosed structures
    if in_list:
        html += "</ul>\n"
    if in_table:
        html += "</tbody></table></div>\n"

    # Inline formatting (Bold, Links, Code)
    # Bold **text**
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Inline code `code`
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    # Markdown links [text](url)
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

    return html

def build_report():
    print("[*] Reading source files...")
    
    # Read brainstorming
    brainstorm_content = ""
    if os.path.exists(BRAINSTORMING_PATH):
        with open(BRAINSTORMING_PATH, "r", encoding="utf-8") as f:
            brainstorm_content = f.read()
    else:
        print(f"[!] Brainstorming file not found at {BRAINSTORMING_PATH}")

    # Read implementation plan
    plan_content = ""
    if os.path.exists(PLAN_PATH):
        with open(PLAN_PATH, "r", encoding="utf-8") as f:
            plan_content = f.read()
    else:
        print(f"[!] Plan file not found at {PLAN_PATH}")

    # Convert to HTML
    print("[*] Converting Markdown to HTML...")
    brainstorm_html = md_to_html(brainstorm_content)
    plan_html = md_to_html(plan_content)

    # 5-member team division content (Embedded in HTML directly)
    team_tasks_html = """
    <h1>Phân Chia Nhiệm Vụ 5 Thành Viên</h1>
    <p>Để tối ưu hóa năng suất và chạy nước rút hiệu quả, kế hoạch phân chia vai trò cho 5 thành viên được thiết lập như sau:</p>
    
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Thành viên & Vai trò</th>
                    <th>Thư mục & File chính</th>
                    <th>Nhiệm vụ cụ thể</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>👤 Người 1: Backend Engineer</strong><br>Hạ tầng, Database & API Server</td>
                    <td><code>backend/app.py</code><br><code>backend/database.py</code><br><code>backend/config.py</code></td>
                    <td>
                        <ul>
                            <li>Thiết lập SQLite Database để lưu trữ dữ liệu học sinh, nhật ký làm bài (responses) và trạng thái thành thạo kiến thức.</li>
                            <li>Xây dựng FastAPI routes cung cấp câu hỏi tiếp theo, nhận kết quả chấm điểm và trả báo cáo giáo viên.</li>
                            <li>Hiện thực giao thức đồng bộ log nhẹ (Sync Queue) khi phát hiện kết nối internet.</li>
                        </ul>
                    </td>
                </tr>
                <tr>
                    <td><strong>👤 Người 2: AI & Math Specialist</strong><br>Đồ thị kiến thức & Engine chẩn đoán</td>
                    <td><code>backend/knowledge_graph.py</code><br><code>backend/diagnostic_engine.py</code><br><code>data/questions.json</code></td>
                    <td>
                        <ul>
                            <li>Khai báo cấu trúc DAG kết nối các kỹ năng toán THCS lớp 5, 6, 7.</li>
                            <li>Lập trình lớp BKTProcessor chứa các công thức cập nhật xác suất Bayesian và logic hạ độ khó tìm lỗi gốc.</li>
                            <li>Chuẩn bị ngân hàng câu hỏi phân loại theo mã kỹ năng (sử dụng Gemini sinh tự động).</li>
                        </ul>
                    </td>
                </tr>
                <tr>
                    <td><strong>👤 Người 3: Frontend Developer 1</strong><br>Thiết kế UI/UX & Layout CSS</td>
                    <td><code>frontend/index.html</code><br><code>frontend/style.css</code></td>
                    <td>
                        <ul>
                            <li>Thiết kế giao diện ôn luyện của học sinh (Student View) trực quan và tập trung.</li>
                            <li>Thiết kế Dashboard của giáo viên (Teacher View) chia tab: Phân nhóm học sinh (Auto-Grouping) và bảng ưu tiên.</li>
                            <li>Viết CSS Glassmorphic hiện đại, tương phản tốt và tối ưu responsive trên mọi dòng máy tính trường học.</li>
                        </ul>
                    </td>
                </tr>
                <tr>
                    <td><strong>👤 Người 4: Frontend Developer 2</strong><br>Lập trình Logic JS & Tương tác</td>
                    <td><code>frontend/app.js</code></td>
                    <td>
                        <ul>
                            <li>Xử lý sự kiện học sinh chọn đáp án, gọi API Backend và hiển thị đúng/sai kèm gợi ý động (Hints).</li>
                            <li>Vẽ biểu đồ hình cột tiến trình học tập của lớp học bằng CSS/HTML động.</li>
                            <li>Kết nối WebSocket/API để cập nhật dữ liệu báo cáo thời gian thực về Dashboard giáo viên.</li>
                        </ul>
                    </td>
                </tr>
                <tr>
                    <td><strong>👤 Người 5: Product Owner & Pitcher</strong><br>Trưởng nhóm - Thuyết trình & Business</td>
                    <td>Slide thuyết trình<br>Video Demo<br>Báo cáo chi phí</td>
                    <td>
                        <ul>
                            <li>Thiết kế Slide Pitch Deck bám sát 6 tiêu chí chấm điểm, đặc biệt làm rõ ROI thực tế cho vùng khó khăn.</li>
                            <li>Dựng video vận hành thực tế dự phòng trường hợp mạng sự kiện yếu khi demo trực tiếp.</li>
                            <li>Ước tính chi phí gọi API Vbee/LLM thực tế cho 1 trường học để đưa vào phần kinh doanh.</li>
                            <li>Đại diện nhóm thuyết trình và trả lời phản biện trước Ban giám khảo.</li>
                        </ul>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    # HTML Template
    template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Thiết kế Dự án Adaptive Tutoring System</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #4facfe;
            --text-main: #334155;
            --text-headers: #0f172a;
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --border: #e2e8f0;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background: var(--bg-body);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            line-height: 1.7;
            padding: 3rem 1.5rem;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--bg-card);
            padding: 4rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 4rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 2rem;
        }}
        
        .header h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--text-headers);
            margin-bottom: 1rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            color: #64748b;
        }}
        
        .section-separator {{
            margin: 4rem 0;
            border: 0;
            height: 2px;
            background: linear-gradient(to right, transparent, var(--border), transparent);
        }}
        
        h1, h2, h3, h4 {{
            font-family: 'Outfit', sans-serif;
            color: var(--text-headers);
            margin-top: 2rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }}
        
        h1 {{ font-size: 2.2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
        h2 {{ font-size: 1.7rem; }}
        h3 {{ font-size: 1.3rem; }}
        h4 {{ font-size: 1.1rem; }}
        
        p {{
            margin-bottom: 1.2rem;
            font-size: 1.05rem;
        }}
        
        ul {{
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.6rem;
            font-size: 1.05rem;
        }}
        
        blockquote {{
            background: #f1f5f9;
            border-left: 4px solid #94a3b8;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            font-style: italic;
            border-radius: 4px;
        }}
        
        .alert {{
            border-left-width: 4px;
        }}
        
        .alert-important {{
            background: #fef2f2;
            border-left-color: #ef4444;
            color: #991b1b;
        }}
        
        .alert-warning {{
            background: #fffbeb;
            border-left-color: #f59e0b;
            color: #92400e;
        }}
        
        .alert-note {{
            background: #eff6ff;
            border-left-color: #3b82f6;
            color: #1e40af;
        }}
        
        .code-block {{
            background: #0f172a;
            color: #f8fafc;
            padding: 1.2rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: Courier, monospace;
            margin: 1.5rem 0;
            font-size: 0.95rem;
        }}
        
        code {{
            background: #f1f5f9;
            color: #0f172a;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: Courier, monospace;
            font-size: 0.9em;
        }}
        
        .code-block code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        
        .table-container {{
            overflow-x: auto;
            margin: 1.5rem 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 1rem;
        }}
        
        th, td {{
            padding: 0.8rem 1rem;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: #f8fafc;
            font-weight: 600;
            color: var(--text-headers);
        }}
        
        .print-btn-container {{
            position: fixed;
            top: 2rem;
            right: 2rem;
            z-index: 1000;
        }}
        
        .print-btn {{
            background: #0f172a;
            color: #ffffff;
            border: none;
            padding: 0.8rem 1.5rem;
            font-family: 'Outfit', sans-serif;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .print-btn:hover {{
            transform: translateY(-2px);
            background: #1e293b;
        }}
        
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border: none;
                padding: 0;
            }}
            .print-btn-container {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-btn-container">
        <button class="print-btn" onclick="window.print()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v8H6z"/></svg>
            In / Xuất PDF
        </button>
    </div>

    <div class="container">
        <div class="header">
            <h1>BÁO CÁO THIẾT KẾ & KẾ HOẠCH TRIỂN KHAI</h1>
            <p>Hệ thống Gia sư Thích ứng chẩn đoán Lỗ hổng Kiến thức Gốc GDPT 2018</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem; color: #94a3b8;">Đội thi: Antigravity | VAIC Hackathon 2026</p>
        </div>

        <section>
            {brainstorm_html}
        </section>

        <hr class="section-separator">

        <section>
            {plan_html}
        </section>
        
        <hr class="section-separator">

        <section>
            {team_tasks_html}
        </section>
    </div>
</body>
</html>
"""

    # Save to output
    print(f"[*] Writing final HTML report to {OUTPUT_HTML_PATH}...")
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(template)
        
    print("[*] Done! Report created successfully.")

if __name__ == "__main__":
    build_report()
