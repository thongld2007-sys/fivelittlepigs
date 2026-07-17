import json
import os

def generate_questions():
    questions = []
    
    # -------------------------------------------------------------------------
    # TOÁN (MATH)
    # -------------------------------------------------------------------------
    math_data = {
        "MATH_G1": [
            ("Hình nào dưới đây có số lượng góc nhiều nhất?", ["Hình tam giác", "Hình vuông", "Hình tròn", "Hình lục giác"], "D", "Hãy đếm số góc của từng hình: tam giác có 3, vuông có 4, tròn có 0, lục giác có 6."),
            ("Hãy điền số thích hợp vào chỗ trống để hoàn thành dãy số sau: 2, 4, 6, ..., 10.", ["7", "8", "9", "5"], "B", "Đây là dãy số chẵn tăng dần liên tiếp cách nhau 2 đơn vị."),
            ("So sánh hai số: 45 và 54. Điền dấu thích hợp vào chỗ chấm: 45 ... 54.", ["<", ">", "=", "Không so sánh được"], "A", "So sánh chữ số hàng chục: 4 < 5 nên 45 < 54.")
        ],
        "MATH_G2": [
            ("Tính kết quả của phép tính: 38 + 25 = ?", ["53", "63", "73", "58"], "B", "Thực hiện cộng hàng đơn vị: 8 + 5 = 13 (viết 3 nhớ 1), cộng hàng chục: 3 + 2 + 1 = 6. Kết quả là 63."),
            ("Một cửa hàng có 82 quyển vở, đã bán đi 36 quyển. Hỏi cửa hàng còn lại bao nhiêu quyển vở?", ["46", "56", "48", "38"], "A", "Thực hiện phép tính trừ: 82 - 36 = 46."),
            ("Tìm x biết: x - 27 = 45.", ["18", "72", "62", "71"], "B", "Để tìm số bị trừ, ta lấy hiệu cộng với số trừ: x = 45 + 27 = 72.")
        ],
        "MATH_G3": [
            ("Tính kết quả của phép tính: 8 x 6 = ?", ["42", "48", "54", "36"], "B", "Dựa vào bảng nhân 8: 8 x 6 = 48."),
            ("Tìm số chia trong phép chia sau: 56 : x = 7.", ["7", "9", "8", "6"], "C", "Muốn tìm số chia, ta lấy số bị chia chia cho thương: x = 56 : 7 = 8."),
            ("Một tấm vải dài 32m. Người ta cắt đi 1/4 tấm vải đó. Hỏi người ta đã cắt đi bao nhiêu mét vải?", ["8m", "6m", "12m", "24m"], "A", "Tính 1/4 của 32m bằng cách thực hiện phép chia: 32 : 4 = 8m.")
        ],
        "MATH_G4": [
            ("Giá trị tuyệt đối của số nguyên âm -15 là bao nhiêu?", ["-15", "15", "0", "15 hoặc -15"], "B", "Giá trị tuyệt đối của một số luôn là số không âm, là khoảng cách từ số đó đến điểm 0 trên trục số: |-15| = 15."),
            ("So sánh |-12| và |-18|. Khẳng định nào sau đây là đúng?", ["|-12| > |-18|", "|-12| < |-18|", "|-12| = |-18|", "Không thể so sánh"], "B", "|-12| = 12 và |-18| = 18. Vì 12 < 18 nên |-12| < |-18|."),
            ("Tìm tất cả các giá trị nguyên của x thỏa mãn: |x| = 7.", ["x = 7", "x = -7", "x = 7 hoặc x = -7", "Không có giá trị nào"], "C", "Cả 7 và -7 đều cách điểm 0 một khoảng bằng 7 đơn vị trên trục số, nên |7| = |-7| = 7.")
        ],
        "MATH_G5_LCM": [
            ("Tìm Bội chung nhỏ nhất của hai số 6 và 8. BCNN(6, 8) = ?", ["48", "24", "12", "18"], "B", "Các bội của 6 là: 6, 12, 18, 24, 30... Các bội của 8 là: 8, 16, 24, 32... Số nhỏ nhất xuất hiện ở cả hai danh sách khác 0 là 24."),
            ("Tìm Bội chung nhỏ nhất của ba số 4, 6 và 9.", ["36", "18", "72", "24"], "A", "Ta có: 4 = 2^2; 6 = 2*3; 9 = 3^2. BCNN(4, 6, 9) = 2^2 * 3^2 = 4 * 9 = 36."),
            ("Hai bạn An và Bình cùng sinh hoạt câu lạc bộ toán học. An cứ 8 ngày đi một lần, Bình cứ 12 ngày đi một lần. Hôm nay hai bạn cùng gặp nhau. Hỏi sau ít nhất bao nhiêu ngày nữa hai bạn lại cùng gặp nhau?", ["20 ngày", "96 ngày", "24 ngày", "48 ngày"], "C", "Số ngày tối thiểu để hai bạn gặp lại là BCNN(8, 12) = 24 ngày.")
        ],
        "MATH_G5": [
            ("Quy đồng mẫu số hai phân số 3/4 và 5/6. Mẫu số chung nhỏ nhất của chúng là bao nhiêu?", ["24", "12", "18", "36"], "B", "Mẫu số chung nhỏ nhất là BCNN của 4 và 6. BCNN(4, 6) = 12."),
            ("Sau khi quy đồng mẫu số hai phân số 2/3 và 3/5 với mẫu số chung nhỏ nhất, ta được hai phân số nào?", ["10/15 và 9/15", "6/15 và 9/15", "10/15 và 6/15", "4/15 và 9/15"], "A", "Mẫu chung nhỏ nhất của 3 và 5 là 15. Nhân tử phụ: 15:3 = 5; 15:5 = 3. Quy đồng: 2/3 = 10/15 và 3/5 = 9/15."),
            ("Quy đồng mẫu số các phân số 1/6, 3/8 và 5/12. Mẫu số chung nhỏ nhất của ba phân số này là bao nhiêu?", ["48", "24", "72", "96"], "B", "Ta tìm BCNN(6, 8, 12). Phân tích: 6 = 2*3; 8 = 2^3; 12 = 2^2*3. BCNN(6, 8, 12) = 2^3 * 3 = 24.")
        ],
        "MATH_G6": [
            ("Tính kết quả của phép tính sau: (-15) + 8 = ?", ["7", "-7", "-23", "23"], "B", "Phép cộng hai số nguyên trái dấu: lấy giá trị tuyệt đối lớn trừ nhỏ (15 - 8 = 7) rồi mang dấu của số có trị tuyệt đối lớn hơn (-15), kết quả là -7."),
            ("Tính kết quả của phép tính sau: (-12) - (-18) = ?", ["-30", "6", "-6", "30"], "B", "Trừ một số nguyên là cộng với số đối của nó: (-12) - (-18) = -12 + 18 = 6."),
            ("Tính tổng của dãy số sau: S = (-10) + (-9) + ... + 9 + 10 + 11.", ["11", "0", "21", "-11"], "A", "Các cặp số đối nhau từ -10 đến 10 có tổng bằng 0. Số còn lại duy nhất không bị triệt tiêu là 11.")
        ],
        "MATH_G7": [
            ("Tính kết quả của phép tính sau: 1/2 + (-2/3) = ?", ["-1/6", "1/6", "-7/6", "7/6"], "A", "Quy đồng mẫu số chung là 6 trước: 3/6 + (-4/6) = -1/6."),
            ("Thực hiện phép tính: 0.75 - (-1/2) = ?", ["1/4", "5/4", "-1/4", "1.25"], "D", "Đổi 0.75 = 3/4 và -(-1/2) = 1/2. Quy đồng mẫu chung 4: 3/4 + 2/4 = 5/4 = 1.25."),
            ("Tính nhanh giá trị biểu thức: A = (-3/4) + (5/6) - (1/2) + (3/4) - (1/6).", ["1/3", "1/2", "0", "1/6"], "D", "Nhóm các số hạng: A = [(-3/4) + 3/4] + [(5/6) - 1/6] - 1/2 = 0 + 4/6 - 1/2 = 2/3 - 1/2 = 4/6 - 3/6 = 1/6.")
        ],
        "MATH_G8": [
            ("Khai triển hằng đẳng thức (x + 2)^2 ta được biểu thức nào?", ["x^2 + 4", "x^2 + 4x + 4", "x^2 + 2x + 4", "x^2 + 4x + 2"], "B", "Áp dụng công thức (a+b)^2 = a^2 + 2ab + b^2. Ta có (x+2)^2 = x^2 + 2*x*2 + 2^2 = x^2 + 4x + 4."),
            ("Viết biểu thức sau dưới dạng bình phương của một tổng hoặc một hiệu: x^2 - 6x + 9.", ["(x - 3)^2", "(x + 3)^2", "(x - 9)^2", "(x + 9)^2"], "A", "Nhận xét: x^2 - 2*x*3 + 3^2 chính là dạng a^2 - 2ab + b^2 = (a-b)^2, tương ứng (x - 3)^2."),
            ("Rút gọn biểu thức sau: (x - y)(x + y) - (x^2 - y^2).", ["2y^2", "0", "-2y^2", "2x^2"], "B", "Áp dụng hằng đẳng thức hiệu hai bình phương: (x-y)(x+y) = x^2 - y^2. Do đó biểu thức rút gọn thành (x^2 - y^2) - (x^2 - y^2) = 0.")
        ],
        "MATH_G9": [
            ("Tìm hệ số a, b, c của phương trình bậc hai: 3x^2 - 5x + 2 = 0.", ["a=3, b=5, c=2", "a=3, b=-5, c=2", "a=3, b=-5, c=-2", "a=-3, b=-5, c=2"], "B", "Dạng tổng quát ax^2 + bx + c = 0. Đối chiếu phương trình: a = 3, b = -5, c = 2."),
            ("Tính biệt thức Delta (Δ) của phương trình bậc hai: x^2 - 4x + 3 = 0.", ["Δ = 4", "Δ = 2", "Δ = 0", "Δ = -4"], "A", "Công thức Δ = b^2 - 4ac. Với a = 1, b = -4, c = 3, ta có Δ = (-4)^2 - 4*1*3 = 16 - 12 = 4."),
            ("Phương trình bậc hai 2x^2 + 5x - 3 = 0 có nghiệm là gì?", ["x = 1/2 hoặc x = -3", "x = -1/2 hoặc x = 3", "x = 1 hoặc x = -3", "Phương trình vô nghiệm"], "A", "Tính Δ = 5^2 - 4*2*(-3) = 25 + 24 = 49 > 0. Nghiệm x1 = (-5 + 7)/4 = 1/2; x2 = (-5 - 7)/4 = -3.")
        ]
    }
    
    # -------------------------------------------------------------------------
    # NGỮ VĂN (LITERATURE)
    # -------------------------------------------------------------------------
    lit_data = {
        "LIT_G1": [
            ("Chữ cái nào dưới đây đứng đầu tiên trong bảng chữ cái tiếng Việt?", ["Ă", "B", "A", "Â"], "C", "Chữ cái đầu tiên của bảng chữ cái tiếng Việt là chữ A."),
            ("Dấu thanh nào được dùng trong từ 'mèo'?", ["Thanh hỏi", "Thanh ngã", "Thanh huyền", "Thanh sắc"], "C", "Từ 'mèo' sử dụng dấu huyền (thanh huyền)."),
            ("Tìm từ bắt đầu bằng chữ cái 'b' chỉ một loài hoa có gai và rất thơm?", ["Hoa ban", "Hoa bưởi", "Hoa bách hợp", "Hoa bèo"], "B", "Hoa bưởi bắt đầu bằng 'b', rất thơm và cánh màu trắng tinh khôi.")
        ],
        "LIT_G2": [
            ("Từ nào dưới đây là từ chỉ hoạt động của học sinh?", ["Bút chì", "Học bài", "Trường học", "Sách giáo khoa"], "B", "Từ 'Học bài' là từ chỉ hoạt động, các từ còn lại là từ chỉ sự vật."),
            ("Trong câu 'Chú chim sơn ca hót líu lo trên cành cây', từ chỉ sự vật là từ nào?", ["hót", "líu lo", "sơn ca", "trên"], "C", "Chú chim 'sơn ca' là danh từ chỉ sự vật. 'Hót' chỉ hoạt động, 'líu lo' chỉ đặc điểm tiếng hót."),
            ("Tìm câu viết đúng quy tắc viết hoa trong tiếng Việt?", ["hôm nay em đi Học.", "Hôm nay em đi học.", "Hôm Nay Em Đi Học.", "Hôm nay Em đi học."], "B", "Viết hoa chữ cái đầu tiên của câu và kết thúc bằng dấu chấm: 'Hôm nay em đi học.'")
        ],
        "LIT_G3": [
            ("Xác định chủ ngữ trong câu sau: 'Mẹ em đang nấu cơm dưới bếp.'", ["Mẹ em", "đang nấu cơm", "dưới bếp", "nấu cơm dưới bếp"], "A", "Chủ ngữ trả lời cho câu hỏi 'Ai?' -> 'Mẹ em'."),
            ("Tìm vị ngữ trong câu: 'Đàn cò trắng bay lượn trên đồng ruộng.'", ["Đàn cò trắng", "bay lượn trên đồng ruộng", "trên đồng ruộng", "cò trắng bay lượn"], "B", "Vị ngữ trả lời cho câu hỏi 'làm gì?' -> 'bay lượn trên đồng ruộng'."),
            ("Câu nào dưới đây là câu đơn đầy đủ thành phần chủ ngữ và vị ngữ?", ["Lớp học rất.", "Dưới bóng tre xanh.", "Chúng em chăm chỉ học tập.", "Trong vườn hoa hồng đỏ."], "C", "Chúng em (chủ ngữ) + chăm chỉ học tập (vị ngữ). Các câu còn lại thiếu chủ ngữ hoặc vị ngữ hoặc không rõ nghĩa.")
        ],
        "LIT_G4": [
            ("Biện pháp tu từ nào được sử dụng trong câu: 'Trăng tròn như quả bóng thả trên trời'?", ["Nhân hóa", "So sánh", "Điệp từ", "Ẩn dụ"], "B", "Câu sử dụng từ so sánh 'như' để đối chiếu hình ảnh mặt trăng với quả bóng."),
            ("Trong câu 'Chị gió dịu dàng lướt qua cánh đồng', sự vật nào được nhân hóa?", ["cánh đồng", "gió", "cánh đồng và gió", "chị"], "B", "Gió được gọi bằng 'chị' và có hoạt động 'dịu dàng lướt' giống con người nên gió được nhân hóa."),
            ("Viết câu văn sử dụng biện pháp nhân hóa để tả ông mặt trời thức dậy?", ["Ông mặt trời từ từ nhô lên từ phía đông.", "Mặt trời chiếu những tia nắng vàng óng xuống mặt đất.", "Bác mặt trời vươn vai thức dậy sau một giấc ngủ dài.", "Mặt trời tròn xoe và đỏ rực như quả cầu lửa."], "C", "Từ 'Bác' và hành động 'vươn vai thức dậy', 'ngủ dài' là nhân hóa mặt trời như con người.")
        ],
        "LIT_G5": [
            ("Một bài văn miêu tả cảnh vật thường gồm có mấy phần chính?", ["2 phần", "3 phần", "4 phần", "5 phần"], "B", "Bố cục bài văn miêu tả gồm 3 phần: Mở bài, Thân bài và Kết bài."),
            ("Phần mở bài của bài văn miêu tả cảnh vật có nhiệm vụ gì?", ["Miêu tả chi tiết từng phần của cảnh.", "Giới thiệu cảnh sẽ tả và thời gian, địa điểm quan sát.", "Nêu cảm nghĩ chung của người viết về cảnh vật.", "Kể một câu chuyện liên quan đến cảnh vật."], "B", "Mở bài có nhiệm vụ giới thiệu bao quát về cảnh vật định tả."),
            ("Dàn ý chi tiết cho phần Thân bài tả cảnh một cơn mưa rào mùa hạ nên sắp xếp theo trình tự nào hợp lý nhất?", ["Tả cảnh trong cơn mưa trước, sau đó đến lúc mưa tạnh, cuối cùng tả lúc sắp mưa.", "Tả cảnh lúc sắp mưa, tả trong cơn mưa, và tả cảnh sau khi mưa tạnh.", "Tả cảnh sau khi mưa tạnh, tả lúc sắp mưa, rồi tả trong cơn mưa.", "Tả ngẫu nhiên các hiện tượng không cần theo trình tự thời gian."], "B", "Tả cơn mưa rào hợp lý nhất theo trình tự thời gian xảy ra: Lúc sắp mưa -> Trong cơn mưa -> Sau cơn mưa.")
        ],
        "LIT_G6": [
            ("Truyền thuyết dân gian là gì?", ["Những câu chuyện hoàn toàn có thật về lịch sử đất nước.", "Loại truyện dân gian kể về các nhân vật, sự kiện lịch sử nhưng có nhiều yếu tố kỳ ảo hoang đường.", "Truyện kể về các loài vật có khả năng nói tiếng người để khuyên răn đạo đức.", "Truyện thơ dài do các nhà thơ trung đại sáng tác."], "B", "Truyền thuyết gắn liền với lịch sử nhưng sử dụng nhiều chi tiết tưởng tượng kỳ ảo để tôn vinh anh hùng."),
            ("Chi tiết kỳ ảo nào thể hiện sức mạnh phi thường của Thánh Gióng?", ["Gióng thích ăn cà và uống nước.", "Gióng vươn vai một cái liền biến thành một tráng sĩ cao lớn khỏe mạnh.", "Gióng được dân làng góp gạo nuôi lớn.", "Gióng chào mẹ trước khi đi đánh giặc."], "B", "Chi tiết vươn vai biến thành tráng sĩ là chi tiết kỳ ảo tiêu biểu cho sức mạnh thần kỳ của người anh hùng chống giặc ngoại xâm."),
            ("Ý nghĩa sâu sắc nhất của chi tiết 'roi sắt gãy, Gióng nhổ những cụm tre bên đường quật vào giặc' là gì?", ["Gióng rất thông minh biết sử dụng cây tre làm vũ khí.", "Thể hiện tinh thần đánh giặc bằng mọi vũ khí sẵn có, tre làng cũng cùng nhân dân chống ngoại xâm.", "Gióng có sức khỏe phi thường nhổ được cả tre.", "Tre Việt Nam rất dẻo dai khó gãy."], "B", "Ý nghĩa biểu tượng cho sức mạnh toàn dân, sự đồng lòng của thiên nhiên đất nước cùng người anh hùng đánh giặc.")
        ],
        "LIT_G7": [
            ("Thơ bốn chữ hoặc năm chữ thường sử dụng những loại vần nào là phổ biến?", ["Vần chân và vần lưng", "Chỉ sử dụng vần chân", "Chỉ sử dụng vần lưng", "Không sử dụng vần"], "A", "Thơ bốn, năm chữ linh hoạt sử dụng cả vần chân (gieo ở cuối dòng) và vần lưng (gieo ở giữa dòng)."),
            ("Nhịp thơ phổ biến nhất của thể thơ bốn chữ là nhịp nào?", ["Nhịp 2/2", "Nhịp 1/3", "Nhịp 3/1", "Nhịp 2/3"], "A", "Thể thơ bốn chữ thường ngắt nhịp chẵn 2/2."),
            ("Đoạn thơ sau ngắt nhịp như thế nào là đúng nhất: 'Hạt gạo làng ta / Có vị phù sa / Của sông Kinh Thầy'?", ["Ngắt nhịp 1/3 ở tất cả các câu", "Ngắt nhịp 3/1 ở tất cả các câu", "Ngắt nhịp 2/2 ở tất cả các câu", "Ngắt nhịp hỗn hợp không quy luật"], "C", "Đoạn thơ trên thuộc thể thơ 4 chữ, ngắt nhịp đều đặn 2/2: Hạt gạo / làng ta // Có vị / phù sa // Của sông / Kinh Thầy.")
        ],
        "LIT_G8": [
            ("Luận điểm trong văn nghị luận xã hội là gì?", ["Những câu chuyện kể sinh động làm dẫn chứng.", "Ý kiến thể hiện quan điểm, tư tưởng của người viết về vấn đề nghị luận.", "Các từ ngữ giàu cảm xúc dùng để thuyết phục người đọc.", "Phần kết bài tóm tắt nội dung."], "B", "Luận điểm là linh hồn của bài nghị luận, thể hiện quan điểm rõ ràng của người viết."),
            ("Khi viết bài văn nghị luận về hiện tượng 'bạo lực học đường', đâu là luận cứ thích hợp?", ["Các số liệu thống kê về số vụ bạo lực học đường gần đây và nguyên nhân tâm lý học sinh.", "Kể lại một câu chuyện cổ tích về thiện thắng ác.", "Mô tả cảnh quan ngôi trường khang trang sạch đẹp.", "Cảm nghĩ của em về thầy cô giáo chủ nhiệm."], "A", "Luận cứ phải là lý lẽ và dẫn chứng thực tế, thuyết phục để chứng minh cho luận điểm bạo lực học đường."),
            ("Trong văn nghị luận xã hội, bước nào giúp người viết khẳng định lại vấn đề và đưa ra thông điệp hành động?", ["Mở bài", "Giải thích khái niệm", "Liên hệ bản thân và rút ra bài học", "Nêu phản đề (bàn bạc mở rộng)"], "C", "Khẳng định lại vấn đề, liên hệ bản thân và rút ra bài học hành động nằm ở phần kết bài/cuối thân bài để tạo thông điệp sâu sắc.")
        ],
        "LIT_G9": [
            ("Tác phẩm 'Truyện Kiều' của Nguyễn Du được viết bằng thể thơ nào của dân tộc?", ["Thể thơ Song thất lục bát", "Thể thơ Lục bát", "Thể thơ Tự do", "Thể thơ Thất ngôn bát cú"], "B", "Truyện Kiều là truyện thơ Nôm viết bằng thể thơ lục bát truyền thống gồm 3254 câu."),
            ("Trong đoạn trích 'Chị em Thúy Kiều', tác giả đã sử dụng biện pháp nghệ thuật ước lệ tượng trưng nào để miêu tả vẻ đẹp của Thúy Vân?", ["'Làn thu thủy nét xuân sơn'", "'Hoa cười ngọc thốt đoan trang'", "'Một hai nghiêng nước nghiêng thành'", "'Đau đớn thay phận đàn bà'"], "B", "Miêu tả vẻ đẹp Thúy Vân trang trọng đoan trang, lấy hình ảnh thiên nhiên làm chuẩn mực: hoa cười, ngọc thốt, mây thua nước tóc, tuyết nhường màu da."),
            ("Bút pháp tả cảnh ngụ tình đặc sắc của Nguyễn Du thể hiện rõ nhất qua đoạn trích nào sau đây?", ["Cảnh ngày xuân", "Chị em Thúy Kiều", "Kiều ở lầu Ngưng Bích", "Mã Giám Sinh mua Kiều"], "C", "Đoạn trích Kiều ở lầu Ngưng Bích khắc họa nỗi buồn cô đơn, tuyệt vọng của Kiều thông qua cảnh vật thiên nhiên mênh mông, hiu quạnh ngoài lầu cửa bể.")
        ]
    }
    
    # -------------------------------------------------------------------------
    # NGOẠI NGỮ (ENGLISH)
    # -------------------------------------------------------------------------
    eng_data = {
        "ENG_G1": [
            ("What color is a banana when it is ripe?", ["Red", "Green", "Yellow", "Blue"], "C", "A ripe banana is yellow."),
            ("Which shape has three sides and three corners?", ["Square", "Circle", "Rectangle", "Triangle"], "D", "A triangle has three sides and three corners."),
            ("If you mix red and yellow paint together, what color do you get?", ["Purple", "Green", "Orange", "Pink"], "C", "Mixing red and yellow paint makes orange.")
        ],
        "ENG_G2": [
            ("Which of the following is a farm animal that gives us milk?", ["Lion", "Cow", "Monkey", "Elephant"], "B", "A cow is a common farm animal that produces milk."),
            ("How do you write the number 15 in English?", ["Twelve", "Thirteen", "Fourteen", "Fifteen"], "D", "The spelling of 15 is F-I-F-T-E-E-N."),
            ("Choose the correct plural form of the word 'sheep'.", ["sheeps", "sheep", "sheepes", "shoop"], "B", "The word 'sheep' is an irregular plural; it remains 'sheep' in plural form.")
        ],
        "ENG_G3": [
            ("Choose the correct verb to complete the sentence: 'She ___ a student.'", ["am", "is", "are", "be"], "B", "For singular third-person subjects (he/she/it), the correct form of verb 'To Be' is 'is'."),
            ("Complete the question: '___ they your friends?'", ["Is", "Am", "Are", "Was"], "C", "For plural subjects (they/we/you), we use the verb 'are'."),
            ("Identify the sentence with correct verb 'To Be' grammar.", ["I are happy today.", "He am a doctor.", "You is my best friend.", "We are very excited about the trip."], "D", "The pronoun 'We' matches with 'are'. 'I' goes with 'am', 'He' goes with 'is', and 'You' goes with 'are'.")
        ],
        "ENG_G4": [
            ("Complete the sentence: 'He ___ to school every day.'", ["go", "goes", "going", "went"], "B", "In the present simple tense, for third-person singular subjects (he/she/it), we add -s or -es to the verb. 'Go' becomes 'goes'."),
            ("Complete the negative sentence: 'They ___ like playing football.'", ["don't", "doesn't", "isn't", "aren't"], "A", "For plural subjects (they/we/you/I), the helper verb for negative in present simple is 'don't'."),
            ("Choose the correct present simple sentence indicating a general truth.", ["Water boil at 100 degrees Celsius.", "Water boils at 100 degrees Celsius.", "Water is boiling at 100 degrees Celsius.", "Water will boil at 100 degrees Celsius."], "B", "Scientific facts/general truths use Present Simple. 'Water' is uncountable (singular), so verb takes -s: 'boils'.")
        ],
        "ENG_G5": [
            ("What is the past simple form of the verb 'play'?", ["plaied", "played", "playing", "plays"], "B", "For regular verbs, we add -ed to the base form: play + ed = played."),
            ("Complete the sentence: 'Yesterday, she ___ her homework.'", ["finish", "finishes", "finished", "finishing"], "C", "The time indicator 'Yesterday' requires the past simple tense. Since 'finish' is a regular verb, we add -ed: 'finished'."),
            ("Which sentence correctly forms the negative in the past simple tense?", ["She did not visited her grandmother last week.", "She did not visit her grandmother last week.", "She does not visit her grandmother last week.", "She not visited her grandmother last week."], "B", "The negative past simple formula is: Subject + did not + verb (in base form without -ed). 'did not visit' is correct.")
        ],
        "ENG_G6": [
            ("Choose the correct pronoun to complete the sentence: '___ went to the cinema last night.'", ["Us", "Me", "Him", "They"], "D", "We need a subject pronoun here. 'Us', 'Me', and 'Him' are object pronouns. 'They' is a subject pronoun."),
            ("Complete the sentence: 'My mother bought a book for ___.'", ["I", "he", "she", "me"], "D", "After prepositions like 'for', 'to', 'with', we use object pronouns. 'me' is correct, while 'I', 'he', and 'she' are subject pronouns."),
            ("Replace the underlined words with pronouns: '<u>The teacher</u> explained the lesson to <u>the students</u>.'", ["He / they", "She / them", "Subject / Object", "They / us"], "B", "The teacher (singular subject) -> She/He; the students (plural object) -> them. Option B 'She / them' is correct.")
        ],
        "ENG_G7": [
            ("What is the comparative form of the adjective 'tall'?", ["taller", "more tall", "tallest", "talles"], "B", "For short adjectives (one syllable), we add -er: tall + er = taller. (Wait, option B is 'taller' but the index is 0. Let's fix keys: A: taller, B: more tall... wait, the options array is [taller, more tall...], so the correct key is A). Let's write them carefully below."),
            ("Choose the correct comparative form: 'This laptop is ___ than that one.'", ["expensive", "more expensive", "expensiver", "most expensive"], "B", "For long adjectives (two or more syllables), we use 'more + adjective': 'more expensive'."),
            ("Complete the comparative sentence correctly: 'My new house is much ___ than my old one.'", ["gooder", "better", "best", "more good"], "B", "The adjective 'good' has an irregular comparative form, which is 'better'.")
        ],
        "ENG_G8": [
            ("What is the passive form of: 'She writes a letter'?", ["A letter is written by her.", "A letter was written by her.", "A letter is writing by her.", "A letter has been written by her."], "A", "Present simple passive formula: Subject + am/is/are + verb in past participle (V3) + by + Agent. 'A letter is written by her' is correct."),
            ("Change this sentence to passive voice: 'The boy broke the window.'", ["The window was broke by the boy.", "The window is broken by the boy.", "The window was broken by the boy.", "The window had broken by the boy."], "C", "Past simple passive formula: Subject + was/were + V3. 'The window was broken by the boy'. V3 of break is broken."),
            ("Identify the sentence in the passive voice that is grammatically correct.", ["English is spoken all over the world.", "English speaks all over the world.", "English is spoke all over the world.", "English was speak all over the world."], "A", "V3 of speak is spoken. 'English is spoken all over the world' is grammatically correct and describes a present general fact in passive voice.")
        ],
        "ENG_G9": [
            ("Choose the correct relative pronoun: 'The man ___ is talking to our teacher is my uncle.'", ["which", "whom", "who", "whose"], "C", "We use 'who' as a relative pronoun for a subject who is a person."),
            ("Complete the sentence: 'The book ___ you lent me yesterday was very interesting.'", ["who", "whom", "which", "whose"], "C", "We use 'which' or 'that' for things and objects. 'book' is an object, so 'which' is correct."),
            ("Combine the sentences: 'I know a girl. Her father is a famous surgeon.'", ["I know a girl who father is a famous surgeon.", "I know a girl whose father is a famous surgeon.", "I know a girl whom father is a famous surgeon.", "I know a girl which father is a famous surgeon."], "B", "We use 'whose' to show possession (her father -> whose father).")
        ]
    }
    # Fixing comparative tall keys:
    eng_data["ENG_G7"][0] = ("What is the comparative form of the adjective 'tall'?", ["taller", "more tall", "tallest", "talles"], "A", "For short adjectives (one syllable), we add -er: tall + er = taller.")

    # -------------------------------------------------------------------------
    # KHOA HỌC TỰ NHIÊN (SCIENCE)
    # -------------------------------------------------------------------------
    sci_data = {
        "SCI_G1": [
            ("Bộ phận nào của cây nằm dưới đất và có nhiệm vụ chính là hút nước và chất dinh dưỡng?", ["Lá cây", "Thân cây", "Rễ cây", "Hoa"], "C", "Rễ cây bám sâu vào đất để hút nước và muối khoáng nuôi cây."),
            ("Bộ phận nào của cây thực hiện chức năng quang hợp dưới ánh sáng mặt trời?", ["Rễ cây", "Lá cây", "Thân cây", "Quả"], "B", "Lá cây chứa chất diệp lục giúp cây quang hợp chế tạo chất hữu cơ dưới ánh sáng mặt trời."),
            ("Quá trình hô hấp ở thực vật diễn ra vào thời gian nào?", ["Chỉ vào ban đêm", "Chỉ vào ban ngày", "Suốt cả ngày và đêm", "Khi trời mát"], "C", "Hô hấp là quá trình diễn ra liên tục cả ngày lẫn đêm để duy trì sự sống cho thực vật.")
        ],
        "SCI_G2": [
            ("Nhóm động vật nào dưới đây thuộc loại động vật sống dưới nước và thở bằng mang?", ["Con khỉ", "Con cá", "Con gà", "Con thỏ"], "B", "Con cá là động vật dưới nước đặc trưng và hô hấp bằng mang."),
            ("Bộ phận di chuyển chính của các loài chim là gì?", ["Vây", "Đuôi", "Cánh", "Chân"], "C", "Chim sử dụng cánh để bay lượn và di chuyển chủ yếu trên không trung."),
            ("Đặc điểm nào giúp động vật lưỡng cư (như ếch) có thể sống được cả trên cạn và dưới nước?", ["Da trần ẩm ướt và hô hấp bằng cả da lẫn phổi", "Thở hoàn toàn bằng mang", "Có cánh để bay", "Có mai cứng bảo vệ"], "A", "Ếch có da trần ẩm ướt giúp trao đổi khí dưới nước, và có phổi để thở trên cạn.")
        ],
        "SCI_G3": [
            ("Đường đi của không khí khi ta hít vào lần lượt qua các cơ quan nào?", ["Mũi -> Phế quản -> Khí quản -> Phổi", "Mũi -> Khí quản -> Phế quản -> Phổi", "Mũi -> Phổi -> Khí quản -> Phế quản", "Khí quản -> Phế quản -> Mũi -> Phổi"], "B", "Không khí đi qua Mũi vào Khí quản, chia nhánh qua hai Phế quản rồi đi vào hai lá Phổi."),
            ("Cơ quan nào thực hiện việc trao đổi khí Oxy và Cacbonic giữa máu và không khí?", ["Mũi", "Khí quản", "Phổi", "Phế quản"], "C", "Phổi chứa hàng triệu phế nang, nơi xảy ra quá trình trao đổi khí Oxy từ không khí vào máu và Cacbonic từ máu ra ngoài."),
            ("Tại sao ta nên tập hít thở sâu bằng mũi thay vì thở bằng miệng?", ["Vì mũi lọc bụi tốt hơn, sưởi ấm và làm ẩm không khí trước khi vào phổi", "Vì thở bằng miệng tốn nhiều sức hơn", "Vì thở bằng mũi giúp ăn ngon miệng hơn", "Không có sự khác biệt nào"], "A", "Trong mũi có lông mũi ngăn bụi, chất nhầy diệt khuẩn, và các mao mạch sưởi ấm không khí.")
        ],
        "SCI_G4": [
            ("Nước trong tự nhiên tồn tại dưới những thể nào?", ["Rắn, lỏng, khí", "Chỉ ở thể lỏng", "Chỉ ở thể rắn và lỏng", "Chỉ ở thể lỏng và khí"], "A", "Nước tồn tại ở ba thể: rắn (băng, đá), lỏng (nước sinh hoạt), khí (hơi nước)."),
            ("Hiện tượng nước từ thể lỏng chuyển sang thể khí (hơi nước) được gọi là gì?", ["Ngưng tụ", "Bay hơi", "Đông đặc", "Nóng chảy"], "B", "Sự chuyển từ thể lỏng sang thể khí của nước gọi là sự bay hơi."),
            ("Nguyên nhân chính tạo nên vòng tuần hoàn nước trong tự nhiên là gì?", ["Do gió thổi liên tục trên mặt đất", "Do năng lượng nhiệt của ánh sáng Mặt Trời và lực hút của Trái Đất", "Do con người sử dụng nước hàng ngày", "Do lòng đất tỏa nhiệt"], "B", "Mặt Trời làm nóng nước bay hơi lên cao ngưng tụ thành mây, gặp lạnh rơi xuống thành mưa nhờ trọng lực Trái Đất tạo thành vòng tuần hoàn khép kín.")
        ],
        "SCI_G5": [
            ("Thiết bị nào dưới đây ứng dụng năng lượng gió để tạo ra điện năng?", ["Đập thủy điện", "Tua-bin gió (Phong điện)", "Tấm pin năng lượng mặt trời", "Nhà máy nhiệt điện"], "B", "Tua-bin gió sử dụng động năng của gió để quay cánh quạt sinh ra dòng điện."),
            ("Thủy điện hoạt động dựa trên việc khai thác nguồn năng lượng nào?", ["Năng lượng hóa thạch", "Thủy triều", "Năng lượng dòng nước chảy (động năng)", "Năng lượng địa nhiệt"], "C", "Đập thủy điện chặn nước ở trên cao, xả nước chảy xuống làm quay tua-bin máy phát điện."),
            ("Đâu là một nhược điểm lớn khi sử dụng năng lượng gió và năng lượng mặt trời làm điện năng?", ["Gây ô nhiễm không khí nặng nề", "Nguồn năng lượng nhanh cạn kiệt", "Phụ thuộc nhiều vào thời tiết và tính ổn định không cao", "Chi phí mua nguyên liệu vận hành quá đắt"], "C", "Gió và mặt trời là tài nguyên vô tận nhưng không liên tục, phụ thuộc vào thời tiết (trời âm u, lặng gió).")
        ],
        "SCI_G6": [
            ("Thành phần nào cấu tạo nên tế bào có vai trò bao bọc, bảo vệ và kiểm soát các chất ra vào tế bào?", ["Nhân tế bào", "Tế bào chất", "Màng tế bào", "Lục lạp"], "C", "Màng sinh chất (màng tế bào) thực hiện chức năng bảo vệ và trao đổi chất có chọn lọc."),
            ("Điểm khác biệt cơ bản giữa tế bào nhân sơ và tế bào nhân thực là gì?", ["Tế bào nhân sơ không có màng sinh chất", "Tế bào nhân sơ chưa có nhân hoàn chỉnh (chỉ có vùng nhân không có màng nhân)", "Tế bào nhân thực có kích thước nhỏ hơn", "Tế bào nhân sơ có nhiều lục lạp hơn"], "B", "Tế bào nhân sơ (như vi khuẩn) chưa có màng nhân bao bọc chất di truyền, còn nhân thực thì đã có nhân hoàn chỉnh."),
            ("Một tế bào thực hiện phân chia 3 lần liên tiếp. Từ 1 tế bào ban đầu sẽ tạo ra bao nhiêu tế bào con?", ["4 tế bào", "6 tế bào", "8 tế bào", "16 tế bào"], "C", "Công thức số tế bào con sau n lần phân chia là 2^n. Với n = 3, ta có 2^3 = 8 tế bào con.")
        ],
        "SCI_G7": [
            ("Định luật phản xạ ánh sáng phát biểu rằng góc phản xạ (i') quan hệ thế nào với góc tới (i)?", ["Góc phản xạ lớn hơn góc tới", "Góc phản xạ nhỏ hơn góc tới", "Góc phản xạ bằng góc tới", "Góc phản xạ luôn bằng 90 độ"], "C", "Định luật phản xạ ánh sáng khẳng định góc phản xạ luôn bằng góc tới: i' = i."),
            ("Góc tới là góc hợp bởi hai tia nào?", ["Tia tới và tia phản xạ", "Tia tới và pháp tuyến tại điểm tới", "Tia tới và mặt gương phản xạ", "Tia phản xạ và mặt gương"], "B", "Theo định nghĩa vật lý, góc tới i là góc hợp bởi tia tới và pháp tuyến tại điểm tới."),
            ("Chiếu một tia sáng tới mặt gương phẳng với góc tới i = 35 độ. Hỏi góc hợp bởi tia tới và tia phản xạ bằng bao nhiêu?", ["35 độ", "70 độ", "55 độ", "110 độ"], "B", "Góc tới bằng góc phản xạ (i' = i = 35 độ). Góc hợp bởi tia tới và tia phản xạ là i + i' = 35 + 35 = 70 độ.")
        ],
        "SCI_G8": [
            ("Chất nào dưới đây có độ pH nhỏ hơn 7 và làm giấy quỳ tím hóa đỏ?", ["Nước vôi trong", "Dịch acid trong dạ dày (HCl)", "Nước muối NaCl", "Dịch xà phòng"], "B", "Acid có độ pH < 7 và có tính chất đặc trưng làm quỳ tím chuyển màu đỏ."),
            ("Base (bazơ) là những chất khi tan trong nước phân ly ra ion nào?", ["Ion H+", "Ion OH-", "Ion Na+", "Ion Cl-"], "B", "Theo thuyết Arrhenius, base tan trong nước giải phóng anion hydroxide (OH-)."),
            ("Cho các chất: Nước chanh, Nước tinh khiết, Dung dịch xà phòng. Độ pH của chúng được sắp xếp tăng dần thế nào?", ["Nước chanh < Nước tinh khiết < Dung dịch xà phòng", "Dung dịch xà phòng < Nước tinh khiết < Nước chanh", "Nước tinh khiết < Nước chanh < Dung dịch xà phòng", "Nước chanh < Dung dịch xà phòng < Nước tinh khiết"], "A", "Nước chanh (acid, pH < 7) < Nước tinh khiết (trung tính, pH = 7) < Xà phòng (base, pH > 7).")
        ],
        "SCI_G9": [
            ("Theo thí nghiệm của Mendel, khi lai hai bố mẹ thuần chủng khác nhau về một cặp tính trạng tương phản thì F1 biểu hiện kiểu hình thế nào?", ["100% kiểu hình trung gian", "100% kiểu hình trội", "50% trội : 50% lặn", "3 trội : 1 lặn"], "B", "Định luật đồng tính của Mendel: F1 đồng tính mang kiểu hình của tính trạng trội."),
            ("Khi cho các cá thể F1 (Aa) tự thụ phấn, tỉ lệ kiểu gen ở thế hệ F2 sẽ là bao nhiêu?", ["1 AA : 2 Aa : 1 aa", "3 Aa : 1 aa", "1 AA : 1 aa", "100% Aa"], "A", "Sơ đồ lai Aa x Aa -> F2 có tỉ lệ kiểu gen là 1 AA : 2 Aa : 1 aa."),
            ("Mendel thực hiện phép lai hai cặp tính trạng độc lập giữa hạt vàng trơn (AABB) và hạt xanh nhăn (aabb). Kiểu hình hạt vàng, nhăn chiếm tỉ lệ bao nhiêu ở thế hệ F2?", ["9/16", "3/16", "1/16", "1/4"], "B", "Ở F2 tỉ lệ kiểu hình phân ly 9 vàng trơn : 3 vàng nhăn : 3 xanh trơn : 1 xanh nhăn. Do đó hạt vàng nhăn chiếm 3/16.")
        ]
    }
    
    # -------------------------------------------------------------------------
    # LỊCH SỬ VÀ ĐỊA LÝ (HISTORY & GEOGRAPHY)
    # -------------------------------------------------------------------------
    hisgeo_data = {
        "HISGEO_G1": [
            ("Mẹ của bố em được gọi là gì?", ["Bà ngoại", "Bà nội", "Dì", "Cô"], "B", "Mẹ của bố gọi là bà nội."),
            ("Trong trường học, thầy cô giáo có nhiệm vụ chính là gì?", ["Trồng cây", "Khám bệnh", "Dạy học và chăm sóc học sinh", "Lái xe buýt"], "C", "Nhiệm vụ của thầy cô giáo trong trường học là giảng dạy kiến thức và rèn luyện đạo đức cho học sinh."),
            ("Hành động nào dưới đây thể hiện sự hiếu thảo của em đối với ông bà, cha mẹ?", ["Vòi vĩnh đòi mua đồ chơi đắt tiền", "Lười học, ham chơi điện tử", "Vâng lời, lễ phép và giúp đỡ làm việc nhà nhẹ nhàng", "Đi chơi không xin phép"], "C", "Lễ phép, vâng lời và đỡ đần việc nhà là biểu hiện cụ thể của lòng hiếu thảo.")
        ],
        "HISGEO_G2": [
            ("Người làm công việc khám bệnh, kê đơn thuốc và điều trị cho bệnh nhân được gọi là gì?", ["Thợ xây", "Bác sĩ", "Công an", "Nông dân"], "B", "Bác sĩ thực hiện việc chẩn đoán và chữa bệnh trong xã hội."),
            ("Ngành nghề nào có vai trò làm ra lúa gạo, rau củ để cung cấp lương thực cho xã hội?", ["Nghề dạy học", "Nghề nông (nông dân)", "Nghề may mặc", "Nghề giao hàng"], "B", "Người nông dân cấy lúa, trồng rau củ quả tạo ra nguồn lương thực thiết yếu."),
            ("Nghĩa vụ bảo vệ trật tự an ninh xã hội, điều tiết giao thông và giúp đỡ người dân khi có sự cố khẩn cấp thuộc về ai?", ["Nhân viên ngân hàng", "Chiến sĩ Công an nhân dân", "Lập trình viên", "Ca sĩ"], "B", "Lực lượng công an nhân dân giữ gìn trật tự trị an, an toàn xã hội.")
        ],
        "HISGEO_G3": [
            ("Thủ đô của nước Cộng hòa Xã hội Chủ nghĩa Việt Nam là thành phố nào?", ["Thành phố Hồ Chí Minh", "Thành phố Đà Nẵng", "Thành phố Hà Nội", "Thành phố Hải Phòng"], "C", "Hà Nội là thủ đô của Việt Nam."),
            ("Việt Nam có đường biên giới trên đất liền giáp với các quốc gia nào?", ["Lào, Campuchia, Thái Lan", "Trung Quốc, Lào, Campuchia", "Trung Quốc, Lào, Thái Lan", "Campuchia, Thái Lan, Malaysia"], "B", "Việt Nam giáp Trung Quốc ở phía bắc, Lào và Campuchia ở phía tây."),
            ("Đảo lớn nhất của nước Việt Nam thuộc tỉnh Kiên Giang có tên là gì?", ["Đảo Cát Bà", "Đảo Lý Sơn", "Đảo Phú Quốc", "Đảo Côn Đảo"], "C", "Phú Quốc là hòn đảo có diện tích lớn nhất Việt Nam, mệnh danh là Đảo Ngọc.")
        ],
        "HISGEO_G4": [
            ("Vị vua đầu tiên lập nên nhà nước Văn Lang - nhà nước đầu tiên của nước ta là ai?", ["An Dương Vương", "Hùng Vương", "Kinh Dương Vương", "Ngô Quyền"], "B", "Vua Hùng thành lập nước Văn Lang đóng đô ở Phong Châu (Phú Thọ)."),
            ("Ngày giỗ tổ Hùng Vương được tổ chức hàng năm vào ngày nào âm lịch?", ["Ngày mùng 5 tháng 5", "Ngày mùng 10 tháng 3", "Ngày mùng 1 tháng Giêng", "Ngày mùng 15 tháng 8"], "B", "Giỗ tổ Hùng Vương diễn ra vào ngày 10/3 âm lịch."),
            ("Truyền thuyết nào giải thích nguồn gốc 'đồng bào' và dòng dõi 'Rồng Tiên' của người Việt?", ["Sơn Tinh Thủy Tinh", "Sự tích Hồ Gươm", "Lạc Long Quân và Âu Cơ", "Thánh Gióng"], "C", "Truyền thuyết Lạc Long Quân và Âu Cơ sinh ra bọc trăm trứng, nở trăm con, là nguồn gốc dòng dõi Rồng Tiên.")
        ],
        "HISGEO_G5": [
            ("Bác Hồ đọc bản Tuyên ngôn Độc lập khai sinh nước Việt Nam Dân chủ Cộng hòa vào ngày nào?", ["19/08/1945", "02/09/1945", "30/04/1975", "19/12/1946"], "B", "Ngày Quốc khánh Việt Nam bắt đầu từ sự kiện Bác Hồ đọc Tuyên ngôn Độc lập 2/9/1945."),
            ("Nơi diễn ra sự kiện Bác Hồ đọc Tuyên ngôn Độc lập lịch sử là địa điểm nào?", ["Bến Nhà Rồng", "Quảng trường Ba Đình (Hà Nội)", "Chiến khu Việt Bắc", "Nhà hát Lớn Hà Nội"], "B", "Quảng trường Ba Đình là nơi diễn ra lễ độc lập năm 1945."),
            ("Bản Tuyên ngôn Độc lập 1945 đã khẳng định quyền cơ bản nào của dân tộc Việt Nam?", ["Quyền tự do buôn bán thương mại toàn cầu", "Quyền sống, quyền tự do và quyền mưu cầu hạnh phúc của mọi người dân và quyền độc lập dân tộc trước thế giới", "Quyền xây dựng quân đội mạnh nhất khu vực", "Quyền lựa chọn thể chế hoàng gia"], "B", "Bản tuyên ngôn trích dẫn tuyên ngôn của Mỹ và Pháp để khẳng định quyền sống tự do, quyền độc lập tự chủ của dân tộc Việt Nam.")
        ],
        "HISGEO_G6": [
            ("Trong Hệ Mặt Trời, Trái Đất nằm ở vị trí thứ mấy tính từ Mặt Trời ra ngoài?", ["Vị trí thứ 2", "Vị trí thứ 3", "Vị trí thứ 4", "Vị trí thứ 5"], "B", "Thứ tự: Thủy tinh, Kim tinh, Trái Đất. Trái Đất ở vị trí thứ ba."),
            ("Hiện tượng ngày và đêm luân phiên trên Trái Đất là do nguyên nhân nào?", ["Do Mặt Trời quay quanh Trái Đất", "Do Trái Đất tự quay quanh trục của nó theo hướng từ tây sang đông", "Do Mặt Trăng che khuất Mặt Trời", "Do Trái Đất chuyển động quanh Mặt Trời"], "B", "Trái Đất hình cầu tự quay quanh trục sinh ra hiện tượng nơi này nhận ánh sáng (ngày) thì nơi kia khuất sáng (đêm)."),
            ("Khi khu vực giờ gốc (GMT) đang là 12 giờ trưa, thì ở Việt Nam (múi giờ số 7) đang là mấy giờ?", ["5 giờ chiều (17h)", "7 giờ tối (19h)", "19 giờ đêm (7h sáng hôm sau)", "12 giờ đêm"], "B", "Giờ Việt Nam = Giờ GMT + 7. Vậy 12 + 7 = 19h (7 giờ tối).")
        ],
        "HISGEO_G7": [
            ("Đông Nam Á gồm có bao nhiêu quốc gia thành viên?", ["10 quốc gia", "11 quốc gia", "12 quốc gia", "9 quốc gia"], "B", "Đông Nam Á gồm 11 quốc gia (Việt Nam, Lào, Campuchia, Thái Lan, Myanmar, Malaysia, Singapore, Indonesia, Philippines, Brunei, Đông Timor)."),
            ("Khí hậu chủ đạo của phần lớn các nước Đông Nam Á là kiểu khí hậu gì?", ["Khí hậu ôn đới hải dương", "Khí hậu nhiệt đới gió mùa", "Khí hậu hàn đới quanh năm băng giá", "Khí hậu sa mạc khô hạn"], "B", "Khu vực chịu ảnh hưởng mạnh của gió mùa, nóng ẩm mưa nhiều quanh năm."),
            ("Quốc gia nào ở Đông Nam Á là quốc gia quần đảo lớn nhất thế giới, có hàng vạn hòn đảo lớn nhỏ?", ["Singapore", "Philippines", "Indonesia", "Malaysia"], "C", "Indonesia được mệnh danh là đất nước vạn đảo với hơn 17.000 hòn đảo.")
        ],
        "HISGEO_G8": [
            ("Vua Quang Trung tên thật là gì?", ["Nguyễn Lữ", "Nguyễn Nhạc", "Nguyễn Huệ", "Nguyễn Ánh"], "C", "Nguyễn Huệ là vị anh hùng áo vải Tây Sơn, sau lên ngôi hoàng đế lấy niên hiệu Quang Trung."),
            ("Chiến thắng quân sự lừng lẫy nào của nghĩa quân Tây Sơn đánh bại 2 vạn quân xiêm xâm lược năm 1785?", ["Chiến thắng Chi Lăng - Xương Giang", "Chiến thắng Rạch Gầm - Xoài Mút", "Chiến thắng Ngọc Hồi - Đống Đa", "Chiến thắng Bạch Đằng"], "B", "Nguyễn Huệ chỉ huy trận thủy chiến phục kích đại phá quân Xiêm trên sông Tiền ở đoạn Rạch Gầm - Xoài Mút (Tiền Giang)."),
            ("Trận đánh quyết định nào vào dịp Tết Kỷ Dậu (1789) giúp vua Quang Trung quét sạch 29 vạn quân Thanh ra khỏi Thăng Long?", ["Trận Chi Lăng", "Trận Ngọc Hồi - Đống Đa", "Trận Bạch Đằng", "Trận Hàm Tử - Chương Dương"], "B", "Trận Ngọc Hồi - Đống Đa mùng 5 Tết Kỷ Dậu tiêu diệt quân xâm lược nhà Thanh giải phóng hoàn toàn kinh thành Thăng Long.")
        ],
        "HISGEO_G9": [
            ("Chiến tranh thế giới thứ hai chính thức bùng nổ vào năm nào?", ["1914", "1918", "1939", "1945"], "C", "Thế chiến thứ hai bắt đầu ngày 1/9/1939 khi phát xít Đức tấn công Ba Lan."),
            ("Sự kiện nào khiến nước Mỹ chính thức chấm dứt thái độ trung lập và tuyên chiến với phe Phát xít?", ["Phát xít Đức tấn công Ba Lan", "Phát xít Nhật bất ngờ tấn công căn cứ Trân Châu Cảng của Mỹ vào tháng 12/1941", "Đức tấn công Liên Xô", "Mỹ ném bom nguyên tử xuống Nhật Bản"], "B", "Trận Trân Châu Cảng do Nhật thực hiện đã kéo Mỹ tham chiến vào phe Đồng minh."),
            ("Hội nghị Yalta diễn ra vào tháng 2/1945 có vai trò quyết định như thế nào đối với thế giới sau chiến tranh?", ["Quyết định kéo dài chiến tranh thêm 5 năm", "Thành lập phe Trục phát xít mới", "Phân chia khu vực ảnh hưởng và thiết lập trật tự thế giới hai cực mới (Trật tự hai cực Yalta) giữa Liên Xô và Mỹ", "Ký hiệp ước hòa bình giữa Đức và Pháp"], "C", "Ba cường quốc Liên Xô, Mỹ, Anh thỏa thuận phân chia phạm vi ảnh hưởng ở châu Âu và châu Á, đặt nền móng cho trật tự thế giới mới sau thế chiến.")
        ]
    }
    
    # -------------------------------------------------------------------------
    # TIN HỌC VÀ CÔNG NGHỆ (INFORMATICS & TECH)
    # -------------------------------------------------------------------------
    inftech_data = {
        "INFTECH_G1": [
            ("Thiết bị nào của máy tính hiển thị hình ảnh và văn bản giúp em nhìn thấy kết quả làm việc?", ["Bàn phím", "Chuột máy tính", "Màn hình", "Thân máy"], "C", "Màn hình (monitor) là thiết bị xuất hiển thị thông tin trực quan."),
            ("Bộ phận nào của máy tính có nhiều phím chữ và phím số dùng để nhập thông tin?", ["Chuột", "Bàn phím", "Màn hình", "Loa"], "B", "Bàn phím (keyboard) dùng để gõ nhập văn bản dữ liệu."),
            ("Thiết bị nào vừa đóng vai trò là thiết bị nhập thông tin, vừa là thiết bị xuất thông tin của máy tính?", ["Chuột", "Tai nghe", "Màn hình cảm ứng", "Máy in"], "C", "Màn hình cảm ứng nhận diện ngón tay gõ nhập dữ liệu và hiển thị trực tiếp kết quả lên màn hình.")
        ],
        "INFTECH_G2": [
            ("Thao tác nháy nhanh nút trái chuột 2 lần liên tiếp được gọi là gì?", ["Nháy chuột", "Nháy đúp chuột (Double click)", "Nháy nút phải chuột", "Kéo thả chuột"], "B", "Nháy đúp chuột dùng để mở tệp tin hoặc khởi động chương trình."),
            ("Khi muốn di chuyển một biểu tượng thư mục từ vị trí này sang vị trí khác trên màn hình, em dùng thao tác nào?", ["Nháy đúp chuột", "Kéo thả chuột (Drag and drop)", "Nháy nút phải chuột", "Nháy nút trái chuột"], "B", "Nháy giữ chuột trái, di chuyển đến vị trí mới rồi thả ra gọi là kéo thả chuột."),
            ("Ngón trỏ của bàn tay phải thông thường được đặt ở vị trí nào khi cầm chuột máy tính?", ["Nút trái chuột", "Nút phải chuột", "Bánh lăn", "Bên hông chuột"], "A", "Theo tư thế cầm chuột chuẩn, ngón trỏ đặt lên nút trái chuột, ngón giữa đặt lên nút phải chuột.")
        ],
        "INFTECH_G3": [
            ("Khi bắt đầu tập gõ bàn phím, hai ngón tay trỏ của hai bàn tay luôn đặt trên hai phím có gai nào ở hàng phím cơ sở?", ["Phím G và H", "Phím F và J", "Phím D và K", "Phím A và L"], "B", "Phím F (tay trái) và J (tay phải) có gờ nổi để định vị tay không cần nhìn bàn phím."),
            ("Hàng phím nào được chọn làm hàng phím xuất phát chính cho các ngón tay khi luyện gõ 10 ngón?", ["Hàng phím số", "Hàng phím trên", "Hàng phím cơ sở", "Hàng phím dưới"], "C", "Hàng phím cơ sở (chứa A S D F J K L ;) là nơi đặt các ngón tay xuất phát."),
            ("Ngón tay nào có nhiệm vụ gõ phím cách (Spacebar) dài nhất nằm dưới cùng bàn phím?", ["Ngón trỏ", "Ngón út", "Hai ngón tay cái", "Ngón giữa"], "C", "Hai ngón cái phụ trách phím cách, ngón nào thuận sẽ gõ phím cách.")
        ],
        "INFTECH_G4": [
            ("Hành động nào dưới đây giúp bảo vệ thông tin cá nhân của em khi truy cập Internet?", ["Chia sẻ mật khẩu tài khoản cho bạn thân trong lớp", "Không cung cấp họ tên, số điện thoại, địa chỉ nhà hay mật khẩu cho người lạ trên mạng", "Đăng ảnh căn cước công dân lên Facebook", "Đặt mật khẩu là '123456' cho dễ nhớ"], "B", "Bảo mật thông tin cá nhân là nguyên tắc hàng đầu chống lừa đảo mạng."),
            ("Khi nhận được tin nhắn bắt nạt hoặc nội dung xấu từ một người lạ trên Internet, em nên làm gì?", ["Nhắn tin chửi bới lại người đó", "Im lặng chịu đựng một mình", "Chặn người đó và báo ngay cho bố mẹ hoặc thầy cô giáo", "Gửi tiền theo yêu cầu của họ"], "C", "Hãy chặn liên hệ và tìm sự trợ giúp ngay từ người lớn đáng tin cậy."),
            ("Đâu là dấu hiệu cảnh báo một trang web có thể không an toàn hoặc giả mạo?", ["Trang web sử dụng giao thức bảo mật bắt đầu bằng 'https://' và có biểu tượng ổ khóa khóa lại", "Trang web yêu cầu nhập thông tin mật khẩu ngân hàng lập tức và chứa nhiều quảng cáo độc hại, tên miền kỳ lạ như '.xyz', '.net-pay.tk'", "Trang web hiển thị thông tin học tập của nhà trường", "Trang web tải nhanh không có lỗi chính tả"], "B", "Các trang web lừa đảo thường dùng tên miền lạ, sai chính tả và yêu cầu thông tin nhạy cảm vô lý.")
        ],
        "INFTECH_G5": [
            ("Khối lệnh nào trong Scratch được dùng để làm cho nhân vật di chuyển về phía trước?", ["say 'Hello'", "move 10 steps", "turn 15 degrees", "wait 1 secs"], "B", "Khối lệnh 'move 10 steps' thay đổi tọa độ của nhân vật để tiến lên."),
            ("Để âm thanh phát ra khi nhân vật di chuyển, em ghép khối lệnh âm thanh thế nào với khối lệnh di chuyển?", ["Đặt khối âm thanh song song không kết nối", "Ghép khối lệnh 'play sound' ngay trước hoặc sau khối lệnh 'move'", "Không thể kết hợp âm thanh và di chuyển", "Sử dụng khối 'clear sound'"], "B", "Ghép nối tiếp các khối lệnh để thực thi tuần tự di chuyển và phát âm thanh."),
            ("Khối lệnh lặp nào giúp nhân vật Scratch thực hiện đi bộ liên tục không bao giờ dừng lại?", ["repeat 10", "repeat until", "forever", "if-then"], "C", "Khối 'forever' chạy vòng lặp vô hạn cho đến khi người dùng nhấn nút dừng (nút đỏ).")
        ],
        "INFTECH_G6": [
            ("Để viết chữ in hoa trong soạn thảo văn bản, em giữ phím nào trong lúc gõ chữ?", ["Phím Ctrl", "Phím Shift", "Phím Alt", "Phím Tab"], "B", "Giữ Shift + chữ cái để viết hoa chữ đó, hoặc dùng Caps Lock để viết hoa toàn bộ."),
            ("Phím nào trên bàn phím dùng để xóa ký tự đứng ngay phía trước con trỏ soạn thảo?", ["Phím Delete", "Phím Backspace", "Phím Enter", "Phím Spacebar"], "B", "Backspace xóa ký tự bên trái (phía trước), Delete xóa ký tự bên phải (phía sau) con trỏ."),
            ("Thao tác nhanh bằng tổ hợp phím nào dùng để sao chép (Copy) đoạn văn bản đã chọn?", ["Ctrl + V", "Ctrl + C", "Ctrl + X", "Ctrl + Z"], "B", "Ctrl+C sao chép, Ctrl+V dán, Ctrl+X cắt, Ctrl+Z hoàn tác.")
        ],
        "INFTECH_G7": [
            ("Trong bảng tính Excel, công thức tính tổng các ô từ A1 đến A5 viết thế nào là đúng?", ["=SUM(A1:A5)", "SUM(A1:A5)", "=A1+A5", "=AVERAGE(A1:A5)"], "A", "Công thức Excel luôn bắt đầu bằng dấu '='. Hàm tính tổng là SUM, ngăn cách vùng dữ liệu bằng dấu hai chấm."),
            ("Hàm nào được dùng để tính giá trị trung bình cộng của các ô chứa số?", ["SUM", "COUNT", "AVERAGE", "MIN"], "C", "AVERAGE tính trung bình cộng."),
            ("Nếu tại ô B1 chứa giá trị 10, ô B2 chứa giá trị 20. Khi nhập công thức tại ô B3: '=B1*2 + B2/2', kết quả hiển thị ở B3 là bao nhiêu?", ["15", "30", "20", "25"], "B", "Thực hiện phép tính: B1*2 = 10*2 = 20; B2/2 = 20/2 = 10. Tổng 20 + 10 = 30.")
        ],
        "INFTECH_G8": [
            ("Thuật toán là gì?", ["Một chương trình máy tính viết bằng ngôn ngữ Java.", "Dãy các chỉ dẫn rõ ràng, tuần tự từng bước để giải quyết một bài toán cụ thể.", "Một lỗi lập trình làm treo máy", "Bảng tính dữ liệu số liệu"], "B", "Thuật toán là tập hợp các bước logic để đạt được mục tiêu xác định."),
            ("Trong sơ đồ khối thuật toán, hình thoi thường biểu diễn cho thành phần nào?", ["Điểm bắt đầu hoặc kết thúc", "Bước thực hiện phép tính toán thông thường", "Điều kiện rẽ nhánh (Đúng / Sai)", "Dữ liệu đầu vào"], "C", "Hình thoi thể hiện phép so sánh điều kiện đưa ra quyết định rẽ nhánh."),
            ("Cho thuật toán sau: B1: Nhập số N. B2: Nếu N chia hết cho 2 thì xuất 'Chẵn', ngược lại xuất 'Lẻ'. Với N = 7, kết quả xuất ra là gì?", ["Chẵn", "Lẻ", "7", "Không có kết quả"], "B", "7 chia 2 dư 1 (không chia hết) nên thực hiện nhánh ngược lại, xuất ra 'Lẻ'.")
        ],
        "INFTECH_G9": [
            ("Lệnh nào trong ngôn ngữ lập trình Python được dùng để in thông tin ra màn hình?", ["input()", "print()", "output()", "display()"], "B", "Hàm `print()` là hàm cơ bản để xuất dữ liệu ra màn hình trong Python."),
            ("Kết quả của phép toán Python sau bằng bao nhiêu: 17 % 5?", ["3", "2", "1", "1.7"], "B", "Toán tử % là phép chia lấy phần dư. 17 chia 5 được 3 dư 2. Kết quả là 2."),
            ("Cho đoạn code Python sau:\nscore = 85\nif score >= 90:\n    print('A')\nelif score >= 80:\n    print('B')\nelse:\n    print('C')\nĐoạn code trên sẽ in ra chữ gì?", ["A", "B", "C", "Không in gì cả"], "B", "Biến `score` có giá trị 85. Điều kiện thứ nhất `score >= 90` sai. Điều kiện thứ hai `score >= 80` đúng (85 >= 80), nên in ra 'B'.")
        ]
    }
    
    # Merge all datasets
    all_subjects_data = {}
    all_subjects_data.update(math_data)
    all_subjects_data.update(lit_data)
    all_subjects_data.update(eng_data)
    all_subjects_data.update(sci_data)
    all_subjects_data.update(hisgeo_data)
    all_subjects_data.update(inftech_data)
    
    q_counter = 1
    for skill_id, q_list in all_subjects_data.items():
        for idx, q_tuple in enumerate(q_list):
            q_text, opts, correct, hint = q_tuple
            level = idx + 1 # 1: Dễ, 2: Vừa, 3: Khó
            level_str = "Dễ" if level == 1 else "Vừa" if level == 2 else "Khó"
            
            # Format options list
            formatted_opts = []
            keys = ["A", "B", "C", "D"]
            for opt_idx, opt_text in enumerate(opts):
                formatted_opts.append({
                    "key": keys[opt_idx],
                    "text": opt_text
                })
                
            questions.append({
                "id": f"q_{skill_id.lower()}_{level}",
                "skill_id": skill_id,
                "difficulty_level": level,
                "difficulty": level_str,
                "text": q_text,
                "options": formatted_opts,
                "correct_answer": correct,
                "hint": hint,
                "visual_hint": skill_id  # Use skill ID as fallback for frontend visual aid
            })
            q_counter += 1
            
    # Write to questions.json
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "questions.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Successfully generated {len(questions)} questions in {output_path}")

if __name__ == "__main__":
    generate_questions()
