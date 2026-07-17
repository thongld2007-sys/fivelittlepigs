# Middle School and Primary School Knowledge Graph (Grades 1-9, GDPT 2018)
# Nodes represent specific skills, edges (prerequisites) represent directed dependencies (DAG)

KNOWLEDGE_GRAPH = {}

# --- TOÁN (MATH) ---
# Math G1-G9 skills
KNOWLEDGE_GRAPH.update({
    "MATH_G1": {
        "name": "Đếm số và So sánh (Lớp 1)",
        "grade": 1,
        "subject": "Toán",
        "description": "Nhận biết các số trong phạm vi 100, đếm số, so sánh lớn bé.",
        "prerequisites": []
    },
    "MATH_G2": {
        "name": "Phép cộng, trừ phạm vi 100 (Lớp 2)",
        "grade": 2,
        "subject": "Toán",
        "description": "Thực hiện phép cộng và trừ có nhớ trong phạm vi 100.",
        "prerequisites": ["MATH_G1"]
    },
    "MATH_G3": {
        "name": "Phép nhân, chia cơ bản (Lớp 3)",
        "grade": 3,
        "subject": "Toán",
        "description": "Thực hiện phép nhân và chia trong bảng nhân chia từ 2 đến 9.",
        "prerequisites": ["MATH_G2"]
    },
    "MATH_G4": {
        "name": "Giá trị tuyệt đối của số nguyên (Lớp 4)",
        "grade": 4,
        "subject": "Toán",
        "description": "Hiểu về giá trị tuyệt đối và khoảng cách trên trục số.",
        "prerequisites": ["MATH_G3"]
    },
    "MATH_G5_LCM": {
        "name": "Tìm Bội chung nhỏ nhất (Lớp 5)",
        "grade": 5,
        "subject": "Toán",
        "description": "Tìm số tự nhiên nhỏ nhất chia hết cho cả hai số cho trước.",
        "prerequisites": ["MATH_G3"]
    },
    "MATH_G5": {
        "name": "Quy đồng mẫu số phân số (Lớp 5)",
        "grade": 5,
        "subject": "Toán",
        "description": "Biến đổi các phân số khác mẫu thành các phân số cùng mẫu chung.",
        "prerequisites": ["MATH_G5_LCM"]
    },
    "MATH_G6": {
        "name": "Cộng, trừ số nguyên (Lớp 6)",
        "grade": 6,
        "subject": "Toán",
        "description": "Cộng và trừ các số nguyên cùng dấu hoặc khác dấu.",
        "prerequisites": ["MATH_G4"]
    },
    "MATH_G6_GEO": {
        "name": "Góc, tia và đường thẳng (Lớp 6)",
        "grade": 6,
        "subject": "Toán",
        "description": "Nhận biết góc, tia, đường thẳng và tính số đo góc đơn giản.",
        "prerequisites": ["MATH_G3"]
    },
    "MATH_G7": {
        "name": "Cộng, trừ số hữu tỉ (Lớp 7)",
        "grade": 7,
        "subject": "Toán",
        "description": "Cộng, trừ phân số và số thập phân ở dạng hữu tỉ.",
        "prerequisites": ["MATH_G6", "MATH_G5"]
    },
    "MATH_G7_GEO": {
        "name": "Tam giác và các góc (Lớp 7)",
        "grade": 7,
        "subject": "Toán",
        "description": "Tính góc trong tam giác, nhận biết tam giác cân và quan hệ góc.",
        "prerequisites": ["MATH_G6_GEO"]
    },
    "MATH_G8": {
        "name": "Hằng đẳng thức đáng nhớ (Lớp 8)",
        "grade": 8,
        "subject": "Toán",
        "description": "Sử dụng 7 hằng đẳng thức đáng nhớ để biến đổi biểu thức đại số.",
        "prerequisites": ["MATH_G7"]
    },
    "MATH_G8_GEO": {
        "name": "Tứ giác và định lý Thales (Lớp 8)",
        "grade": 8,
        "subject": "Toán",
        "description": "Nhận biết tính chất tứ giác, đường trung bình và tỉ lệ đoạn thẳng.",
        "prerequisites": ["MATH_G7_GEO"]
    },
    "MATH_G9": {
        "name": "Phương trình bậc hai (Lớp 9)",
        "grade": 9,
        "subject": "Toán",
        "description": "Giải phương trình bậc hai một ẩn số sử dụng công thức nghiệm biệt thức Delta.",
        "prerequisites": ["MATH_G8"]
    },
    "MATH_G9_GEO": {
        "name": "Hệ thức lượng trong tam giác vuông (Lớp 9)",
        "grade": 9,
        "subject": "Toán",
        "description": "Sử dụng hệ thức lượng, tỉ số lượng giác và định lý Pythagoras trong tam giác vuông.",
        "prerequisites": ["MATH_G8_GEO"]
    }
})

# --- NGỮ VĂN (LITERATURE) ---
KNOWLEDGE_GRAPH.update({
    "LIT_G1": {
        "name": "Nhận biết chữ cái tiếng Việt (Lớp 1)",
        "grade": 1,
        "subject": "Ngữ văn",
        "description": "Nhận diện bảng chữ cái, dấu thanh tiếng Việt.",
        "prerequisites": []
    },
    "LIT_G2": {
        "name": "Từ ngữ chỉ sự vật, hoạt động (Lớp 2)",
        "grade": 2,
        "subject": "Ngữ văn",
        "description": "Phân biệt danh từ và động từ chỉ sự vật, hoạt động đơn giản.",
        "prerequisites": ["LIT_G1"]
    },
    "LIT_G3": {
        "name": "Cách viết câu đơn ngắn (Lớp 3)",
        "grade": 3,
        "subject": "Ngữ văn",
        "description": "Viết câu đơn có đầy đủ chủ ngữ, vị ngữ.",
        "prerequisites": ["LIT_G2"]
    },
    "LIT_G4": {
        "name": "Biện pháp so sánh, nhân hóa (Lớp 4)",
        "grade": 4,
        "subject": "Ngữ văn",
        "description": "Nhận biết và sử dụng biện pháp so sánh, nhân hóa trong câu văn.",
        "prerequisites": ["LIT_G3"]
    },
    "LIT_G5": {
        "name": "Viết đoạn văn miêu tả cảnh (Lớp 5)",
        "grade": 5,
        "subject": "Ngữ văn",
        "description": "Lập dàn ý và viết đoạn văn miêu tả cảnh vật thiên nhiên.",
        "prerequisites": ["LIT_G4"]
    },
    "LIT_G6": {
        "name": "Truyền thuyết dân gian (Lớp 6)",
        "grade": 6,
        "subject": "Ngữ văn",
        "description": "Hiểu đặc điểm thể loại truyền thuyết qua câu chuyện Thánh Gióng, Sơn Tinh Thủy Tinh.",
        "prerequisites": ["LIT_G5"]
    },
    "LIT_G7": {
        "name": "Phân tích thơ bốn, năm chữ (Lớp 7)",
        "grade": 7,
        "subject": "Ngữ văn",
        "description": "Nhận biết vần, nhịp và hình ảnh trong thơ bốn chữ, năm chữ.",
        "prerequisites": ["LIT_G6"]
    },
    "LIT_G8": {
        "name": "Nghị luận xã hội cơ bản (Lớp 8)",
        "grade": 8,
        "subject": "Ngữ văn",
        "description": "Viết bài văn nghị luận về một vấn đề tư tưởng đạo lý hoặc hiện tượng đời sống.",
        "prerequisites": ["LIT_G7"]
    },
    "LIT_G9": {
        "name": "Phân tích tác phẩm Truyện Kiều (Lớp 9)",
        "grade": 9,
        "subject": "Ngữ văn",
        "description": "Phân tích giá trị nội dung, nghệ thuật của Truyện Kiều và ngòi bút Nguyễn Du.",
        "prerequisites": ["LIT_G8"]
    }
})

# --- NGOẠI NGỮ (ENGLISH) ---
KNOWLEDGE_GRAPH.update({
    "ENG_G1": {
        "name": "English Colors and Shapes (Grade 1)",
        "grade": 1,
        "subject": "Ngoại ngữ",
        "description": "Recognize primary colors and simple shapes in English.",
        "prerequisites": []
    },
    "ENG_G2": {
        "name": "Animals and Numbers (Grade 2)",
        "grade": 2,
        "subject": "Ngoại ngữ",
        "description": "Vocabulary of farm and wild animals, and numbers up to 20.",
        "prerequisites": ["ENG_G1"]
    },
    "ENG_G3": {
        "name": "Verb 'To Be' Present Tense (Grade 3)",
        "grade": 3,
        "subject": "Ngoại ngữ",
        "description": "Proper usage of am, is, are in sentences.",
        "prerequisites": ["ENG_G2"]
    },
    "ENG_G4": {
        "name": "Present Simple Tense (Grade 4)",
        "grade": 4,
        "subject": "Ngoại ngữ",
        "description": "Express habits, routines, and general truths using present simple tense.",
        "prerequisites": ["ENG_G3"]
    },
    "ENG_G5": {
        "name": "Past Simple of Regular Verbs (Grade 5)",
        "grade": 5,
        "subject": "Ngoại ngữ",
        "description": "Formation and use of past simple tense for regular actions with -ed.",
        "prerequisites": ["ENG_G4"]
    },
    "ENG_G6": {
        "name": "Subject and Object Pronouns (Grade 6)",
        "grade": 6,
        "subject": "Ngoại ngữ",
        "description": "Differentiating subject pronouns (I, he) from object pronouns (me, him).",
        "prerequisites": ["ENG_G5"]
    },
    "ENG_G7": {
        "name": "Comparative Adjectives (Grade 7)",
        "grade": 7,
        "subject": "Ngoại ngữ",
        "description": "Constructing comparative sentences with short and long adjectives.",
        "prerequisites": ["ENG_G6"]
    },
    "ENG_G8": {
        "name": "Passive Voice Basics (Grade 8)",
        "grade": 8,
        "subject": "Ngoại ngữ",
        "description": "Transforming active sentences to passive sentences in present simple and past simple.",
        "prerequisites": ["ENG_G7"]
    },
    "ENG_G9": {
        "name": "Defining Relative Clauses (Grade 9)",
        "grade": 9,
        "subject": "Ngoại ngữ",
        "description": "Using who, whom, which, that, whose to combine sentences.",
        "prerequisites": ["ENG_G8"]
    }
})

# --- KHOA HỌC TỰ NHIÊN (SCIENCE) ---
KNOWLEDGE_GRAPH.update({
    "SCI_G1": {
        "name": "Các bộ phận của thực vật (Lớp 1)",
        "grade": 1,
        "subject": "Khoa học tự nhiên",
        "description": "Nhận biết rễ, thân, lá, hoa, quả của thực vật.",
        "prerequisites": []
    },
    "SCI_G2": {
        "name": "Động vật xung quanh ta (Lớp 2)",
        "grade": 2,
        "subject": "Khoa học tự nhiên",
        "description": "Phân loại động vật trên cạn, dưới nước, và các cơ quan di chuyển.",
        "prerequisites": ["SCI_G1"]
    },
    "SCI_G3": {
        "name": "Cơ quan hô hấp của con người (Lớp 3)",
        "grade": 3,
        "subject": "Khoa học tự nhiên",
        "description": "Nhận biết mũi, khí quản, phế quản, phổi và chức năng hô hấp.",
        "prerequisites": ["SCI_G2"]
    },
    "SCI_G4": {
        "name": "Ba thể của nước và vòng tuần hoàn (Lớp 4)",
        "grade": 4,
        "subject": "Khoa học tự nhiên",
        "description": "Hiểu sự chuyển thể của nước (rắn, lỏng, khí) và vòng tuần hoàn nước.",
        "prerequisites": ["SCI_G3"]
    },
    "SCI_G5": {
        "name": "Năng lượng gió và năng lượng nước (Lớp 5)",
        "grade": 5,
        "subject": "Khoa học tự nhiên",
        "description": "Tìm hiểu ứng dụng của năng lượng gió, năng lượng nước chảy trong đời sống.",
        "prerequisites": ["SCI_G4"]
    },
    "SCI_G6": {
        "name": "Cấu tạo tế bào sinh học (Lớp 6)",
        "grade": 6,
        "subject": "Khoa học tự nhiên",
        "description": "Nhận biết màng tế bào, tế bào chất, nhân/vùng nhân và phân biệt tế bào nhân sơ/nhân thực.",
        "prerequisites": ["SCI_G5"]
    },
    "SCI_G7": {
        "name": "Định luật phản xạ ánh sáng (Lớp 7)",
        "grade": 7,
        "subject": "Khoa học tự nhiên",
        "description": "Hiểu tia tới, tia phản xạ, pháp tuyến và góc tới bằng góc phản xạ.",
        "prerequisites": ["SCI_G6"]
    },
    "SCI_G8": {
        "name": "Khái niệm Acid và Base hóa học (Lớp 8)",
        "grade": 8,
        "subject": "Khoa học tự nhiên",
        "description": "Hiểu định nghĩa Acid, Base, tính chất làm đổi màu quỳ tím.",
        "prerequisites": ["SCI_G7"]
    },
    "SCI_G9": {
        "name": "Di truyền học Mendel (Lớp 9)",
        "grade": 9,
        "subject": "Khoa học tự nhiên",
        "description": "Quy luật phân ly, phân ly độc lập và cơ chế di truyền tính trạng trội lặn.",
        "prerequisites": ["SCI_G8"]
    }
})

# --- LỊCH SỬ VÀ ĐỊA LÝ (HISTORY & GEOGRAPHY) ---
KNOWLEDGE_GRAPH.update({
    "HISGEO_G1": {
        "name": "Gia đình và Trường học của em (Lớp 1)",
        "grade": 1,
        "subject": "Lịch sử và Địa lý",
        "description": "Nhận biết các mối quan hệ gia đình, các khu vực trong trường học.",
        "prerequisites": []
    },
    "HISGEO_G2": {
        "name": "Nghề nghiệp trong cộng đồng (Lớp 2)",
        "grade": 2,
        "subject": "Lịch sử và Địa lý",
        "description": "Nhận biết công việc của các ngành nghề xung quanh.",
        "prerequisites": ["HISGEO_G1"]
    },
    "HISGEO_G3": {
        "name": "Bản đồ hành chính Việt Nam (Lớp 3)",
        "grade": 3,
        "subject": "Lịch sử và Địa lý",
        "description": "Xác định thủ đô, các tỉnh thành lớn và biên giới địa lý cơ bản.",
        "prerequisites": ["HISGEO_G2"]
    },
    "HISGEO_G4": {
        "name": "Truyền thuyết Hùng Vương dựng nước (Lớp 4)",
        "grade": 4,
        "subject": "Lịch sử và Địa lý",
        "description": "Hiểu nguồn gốc lịch sử thời đại các vua Hùng và ngày Giỗ tổ Hùng Vương.",
        "prerequisites": ["HISGEO_G3"]
    },
    "HISGEO_G5": {
        "name": "Tuyên ngôn Độc lập năm 1945 (Lớp 5)",
        "grade": 5,
        "subject": "Lịch sử và Địa lý",
        "description": "Ý nghĩa lịch sử ngày 2/9/1945 tại Quảng trường Ba Đình.",
        "prerequisites": ["HISGEO_G4"]
    },
    "HISGEO_G6": {
        "name": "Hệ mặt trời và Chuyển động Trái Đất (Lớp 6)",
        "grade": 6,
        "subject": "Lịch sử và Địa lý",
        "description": "Các hành tinh trong hệ mặt trời, hiện tượng ngày đêm luân phiên và mùa.",
        "prerequisites": ["HISGEO_G5"]
    },
    "HISGEO_G7": {
        "name": "Địa lý và Khí hậu Đông Nam Á (Lớp 7)",
        "grade": 7,
        "subject": "Lịch sử và Địa lý",
        "description": "Đặc điểm vị trí địa lý, khí hậu nhiệt đới gió mùa của khu vực Đông Nam Á.",
        "prerequisites": ["HISGEO_G6"]
    },
    "HISGEO_G8": {
        "name": "Phong trào Tây Sơn và Nguyễn Huệ (Lớp 8)",
        "grade": 8,
        "subject": "Lịch sử và Địa lý",
        "description": "Chiến thắng Rạch Gầm - Xoài Mút, Ngọc Hồi - Đống Đa đại phá quân Thanh.",
        "prerequisites": ["HISGEO_G7"]
    },
    "HISGEO_G9": {
        "name": "Chiến tranh thế giới thứ hai 1939-1945 (Lớp 9)",
        "grade": 9,
        "subject": "Lịch sử và Địa lý",
        "description": "Nguyên nhân, diễn biến chính và hậu quả của cuộc thế chiến thứ hai.",
        "prerequisites": ["HISGEO_G8"]
    }
})

# --- TIN HỌC VÀ CÔNG NGHỆ (INFORMATICS & TECH) ---
KNOWLEDGE_GRAPH.update({
    "INFTECH_G1": {
        "name": "Thiết bị máy tính cơ bản (Lớp 1)",
        "grade": 1,
        "subject": "Tin học và Công nghệ",
        "description": "Nhận biết màn hình, bàn phím, chuột, thân máy.",
        "prerequisites": []
    },
    "INFTECH_G2": {
        "name": "Sử dụng chuột máy tính (Lớp 2)",
        "grade": 2,
        "subject": "Tin học và Công nghệ",
        "description": "Thao tác click trái, click phải, nháy đúp và kéo thả chuột.",
        "prerequisites": ["INFTECH_G1"]
    },
    "INFTECH_G3": {
        "name": "Tập gõ bàn phím 10 ngón (Lớp 3)",
        "grade": 3,
        "subject": "Tin học và Công nghệ",
        "description": "Đặt tay đúng vị trí xuất phát trên hàng phím cơ sở.",
        "prerequisites": ["INFTECH_G2"]
    },
    "INFTECH_G4": {
        "name": "An toàn trên không gian mạng (Lớp 4)",
        "grade": 4,
        "subject": "Tin học và Công nghệ",
        "description": "Bảo vệ thông tin cá nhân, ứng xử văn minh khi sử dụng Internet.",
        "prerequisites": ["INFTECH_G3"]
    },
    "INFTECH_G5": {
        "name": "Lập trình khối kéo thả Scratch (Lớp 5)",
        "grade": 5,
        "subject": "Tin học và Công nghệ",
        "description": "Tạo hoạt ảnh di chuyển và âm thanh cơ bản cho nhân vật Scratch.",
        "prerequisites": ["INFTECH_G4"]
    },
    "INFTECH_G6": {
        "name": "Soạn thảo văn bản cơ bản (Lớp 6)",
        "grade": 6,
        "subject": "Tin học và Công nghệ",
        "description": "Định dạng chữ, căn lề văn bản bằng Microsoft Word hoặc Google Docs.",
        "prerequisites": ["INFTECH_G5"]
    },
    "INFTECH_G7": {
        "name": "Trình bày bảng tính và công thức (Lớp 7)",
        "grade": 7,
        "subject": "Tin học và Công nghệ",
        "description": "Sử dụng hàm SUM, AVERAGE trong Microsoft Excel hoặc Google Sheets.",
        "prerequisites": ["INFTECH_G6"]
    },
    "INFTECH_G8": {
        "name": "Khái niệm thuật toán tuần tự (Lớp 8)",
        "grade": 8,
        "subject": "Tin học và Công nghệ",
        "description": "Hiểu cấu trúc điều kiện rẽ nhánh và lặp trong thuật toán.",
        "prerequisites": ["INFTECH_G7"]
    },
    "INFTECH_G9": {
        "name": "Lập trình Python cơ bản (Lớp 9)",
        "grade": 9,
        "subject": "Tin học và Công nghệ",
        "description": "Khai báo biến, câu lệnh điều kiện if-else và vòng lặp for trong Python.",
        "prerequisites": ["INFTECH_G8"]
    }
})


def get_skill(skill_id):
    return KNOWLEDGE_GRAPH.get(skill_id)

def get_prerequisites(skill_id):
    skill = get_skill(skill_id)
    return skill["prerequisites"] if skill else []

def get_all_skills():
    return list(KNOWLEDGE_GRAPH.keys())
