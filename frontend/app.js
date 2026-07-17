// VGap AI - Frontend Interactive Engine (Memphis Style)
// Supporting both Offline Fallback Mode and Online API integration.

// Global State
const state = {
    currentPortal: 'student', // 'student' | 'teacher'
    currentTeacherTab: 'grouping', // 'grouping' | 'priority' | 'tree'
    studentId: 'emma_std_01',
    isLoggedIn: false,
    loggedInRole: null,
    selectedStudentForTree: null,
    currentQuestion: null,
    selectedOption: null,
    typedAnswer: "",
    isSubmitting: false,
    testStarted: false,
    surveyCompleted: false,
    baseStudentId: 'emma_std_01',
    testSession: {
        subject: "Toán",
        grade: 7,
        targetSkill: "MATH_G7",
        stage: "multiple_choice",
        stageIndex: 0,
        answeredInStage: 0,
        totalAnswered: 0,
        currentSkill: "MATH_G7",
        attempts: [],
        stageTargets: {
            multiple_choice: 12,
            true_false: 4,
            short_answer: 6
        }
    },
    teacherRealtime: {
        socket: null,
        pollingTimer: null,
        reconnectTimer: null,
        reconnectAttempts: 0
    },
    knowledgeGraph: {},
    streak: 0,
    xp: 1200,
    coins: 350,
    
    // Fallback progress state in case backend is offline
    studentProgress: {
        completedSkills: [],
        activeSkill: 'MATH_G7',
        lockedSkills: []
    },
    
    // Mock Students for Class Analysis Dashboard
    mockStudents: [
        { id: 'an_01', name: 'Nguyễn Văn An', currentSkill: 'MATH_G6', nFailed: 4, tStuck: 12, mastery: 0.18 },
        { id: 'binh_02', name: 'Trần Bình', currentSkill: 'MATH_G5', nFailed: 3, tStuck: 8, mastery: 0.22 },
        { id: 'chi_03', name: 'Lê Chi', currentSkill: 'MATH_G7', nFailed: 0, tStuck: 2, mastery: 0.78 },
        { id: 'dung_04', name: 'Nguyễn Dũng', currentSkill: 'MATH_G5_LCM', nFailed: 5, tStuck: 15, mastery: 0.12 },
        { id: 'giang_05', name: 'Phạm Giang', currentSkill: 'MATH_G4', nFailed: 2, tStuck: 5, mastery: 0.28 },
        { id: 'hoang_06', name: 'Lê Huy Hoàng', currentSkill: 'MATH_G7', nFailed: 1, tStuck: 3, mastery: 0.65 },
        { id: 'linh_08', name: 'Phạm Khánh Linh', currentSkill: 'MATH_G6', nFailed: 4, tStuck: 11, mastery: 0.15 }
    ]
};

function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function setButtonIconLabel(button, iconClass, label) {
    button.replaceChildren();
    const icon = document.createElement("i");
    icon.className = iconClass;
    button.append(icon, document.createTextNode(` ${label}`));
}

// Reasoning Path Mock for teacher tree tab
const REASONING_TREES = {
    "an_01": {
        student: "Nguyễn Văn An",
        nodes: [
            { id: "N1", label: "Cộng số hữu tỉ (L7)", status: "gap", level: 1 },
            { id: "N2", label: "Cộng số nguyên (L6)", status: "active", level: 2 },
            { id: "N3", label: "GTTĐ của số nguyên (L4)", status: "completed", level: 3 }
        ],
        edges: [
            { from: "N1", to: "N2", type: "active" },
            { from: "N2", to: "N3", type: "completed" }
        ]
    },
    "binh_02": {
        student: "Trần Bình",
        nodes: [
            { id: "N1", label: "Cộng số hữu tỉ (L7)", status: "gap", level: 1 },
            { id: "N2", label: "Quy đồng phân số (L5)", status: "active", level: 2 },
            { id: "N3", label: "Tìm BCNN (L5)", status: "completed", level: 3 }
        ],
        edges: [
            { from: "N1", to: "N2", type: "active" },
            { from: "N2", to: "N3", type: "completed" }
        ]
    },
    "chi_03": {
        student: "Lê Chi",
        nodes: [
            { id: "N1", label: "Cộng số hữu tỉ (L7)", status: "active", level: 1 },
            { id: "N2", label: "Cộng số nguyên (L6)", status: "completed", level: 2 },
            { id: "N3", label: "Quy đồng phân số (L5)", status: "completed", level: 2 }
        ],
        edges: [
            { from: "N1", to: "N2", type: "completed" },
            { from: "N1", to: "N3", type: "completed" }
        ]
    },
    "dung_04": {
        student: "Nguyễn Dũng",
        nodes: [
            { id: "N1", label: "Cộng số hữu tỉ (L7)", status: "gap", level: 1 },
            { id: "N2", label: "Quy đồng phân số (L5)", status: "gap", level: 2 },
            { id: "N3", label: "Tìm BCNN (L5)", status: "active", level: 3 }
        ],
        edges: [
            { from: "N1", to: "N2", type: "gap" },
            { from: "N2", to: "N3", type: "active" }
        ]
    }
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
    initAuthFlow();
    initPortalNavigation();
    initTeacherTabs();
    initAITutorChat();
    initToolboxTabs();
    initStudentMascotChat();
    initVirtualScratchpad();
    initFractionSlider();
    initTeacherModals();
    initMascotReadAloud();
    
    // Load Knowledge Graph DAG
    await loadKnowledgeGraph();
    
    // Bind Subject and Grade Selector Events
    initSubjectSelectors();

    prepareTestSetup();
});

// Load Knowledge Graph from backend
async function loadKnowledgeGraph() {
    try {
        const res = await fetch("/api/knowledge-graph");
        if (res.ok) {
            state.knowledgeGraph = await res.json();
            console.log("[+] Knowledge Graph loaded successfully:", state.knowledgeGraph);
        }
    } catch (e) {
        console.warn("[-] Could not connect to API backend. Falling back to offline simulator graph.", e);
        // Fallback local graph
        state.knowledgeGraph = {
            "MATH_G7": { name: "Cộng, trừ số hữu tỉ (Lớp 7)", grade: 7, subject: "Toán", prerequisites: ["MATH_G6", "MATH_G5"] },
            "MATH_G6": { name: "Cộng, trừ số nguyên (Lớp 6)", grade: 6, subject: "Toán", prerequisites: ["MATH_G4"] },
            "MATH_G4": { name: "Giá trị tuyệt đối của số nguyên (Lớp 4)", grade: 4, subject: "Toán", prerequisites: [] },
            "MATH_G5": { name: "Quy đồng mẫu số phân số (Lớp 5)", grade: 5, subject: "Toán", prerequisites: ["MATH_G5_LCM"] },
            "MATH_G5_LCM": { name: "Tìm Bội chung nhỏ nhất (Lớp 5)", grade: 5, subject: "Toán", prerequisites: [] }
        };
    }
}

// Bind Selectors for Subject & Grade
function initSubjectSelectors() {
    const subjectSelect = document.getElementById("subject-select");
    const gradeSelect = document.getElementById("grade-select");
    const startBtn = document.getElementById("btn-start-test");
    
    if (subjectSelect && gradeSelect) {
        const onSelectChange = () => {
            const subject = subjectSelect.value;
            const grade = parseInt(gradeSelect.value);
            const skillId = getSkillIdFromSubjectAndGrade(subject, grade);
            
            state.studentProgress.activeSkill = skillId;
            state.testSession.subject = subject;
            state.testSession.grade = grade;
            if (state.testStarted) {
                prepareTestSetup();
            }
            showToast(`Đã chọn: ${subject} - Lớp ${grade}. Bấm Bắt đầu để vào bài test.`);
        };
        
        subjectSelect.addEventListener("change", onSelectChange);
        gradeSelect.addEventListener("change", onSelectChange);
    }

    if (startBtn) {
        startBtn.addEventListener("click", startAdaptiveTest);
    }
}

function prepareTestSetup() {
    state.testStarted = false;
    state.surveyCompleted = false;
    state.selectedOption = null;
    state.typedAnswer = "";
    state.currentQuestion = null;
    resetTestStage();
    setQuestionVisibility(false);
    setSurveyResultVisibility(false);
    document.getElementById("current-skill-name").textContent = "Chọn lớp và môn";
    document.getElementById("current-question-difficulty").textContent = "Sẵn sàng";
    document.getElementById("question-text").textContent = "Hãy chọn lớp và môn rồi bấm Bắt đầu.";
    document.getElementById("mascot-comment").textContent = "Tôi sẽ chỉ mở câu hỏi sau khi bạn bắt đầu bài test.";
    renderPersonalPath();
}

async function startAdaptiveTest() {
    const subjectSelect = document.getElementById("subject-select");
    const gradeSelect = document.getElementById("grade-select");
    const subject = subjectSelect ? subjectSelect.value : state.testSession.subject;
    const grade = gradeSelect ? parseInt(gradeSelect.value) : state.testSession.grade;
    const skillId = getSkillIdFromSubjectAndGrade(subject, grade);

    state.testStarted = true;
    state.surveyCompleted = false;
    state.studentId = `${state.baseStudentId}_survey_${Date.now()}`;
    state.testSession.subject = subject;
    state.testSession.grade = grade;
    state.testSession.targetSkill = skillId;
    state.testSession.currentSkill = skillId;
    state.studentProgress.activeSkill = skillId;
    resetTestStage();
    setQuestionVisibility(true);
    setSurveyResultVisibility(false);
    updateTestStageUI();
    await createCleanSurveySession(grade);
    showToast(`Bắt đầu bài test ${subject} - Lớp ${grade}`);
    loadStudentQuestion(skillId);
}

function resetTestStage() {
    state.testSession.stage = "multiple_choice";
    state.testSession.stageIndex = 0;
    state.testSession.answeredInStage = 0;
    state.testSession.totalAnswered = 0;
    state.testSession.attempts = [];
    updateTestStageUI();
}

function setQuestionVisibility(isVisible) {
    const questionCard = document.getElementById("question-card");
    const progressCard = document.getElementById("test-progress-card");
    if (questionCard) questionCard.style.display = isVisible ? "block" : "none";
    if (progressCard) progressCard.style.display = isVisible ? "flex" : "none";
}

function setSurveyResultVisibility(isVisible) {
    const resultCard = document.getElementById("survey-result-card");
    if (resultCard) resultCard.style.display = isVisible ? "block" : "none";
}

async function createCleanSurveySession(grade) {
    try {
        const res = await fetch("/api/student/session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: state.studentId,
                name: "Emma - Phiên khảo sát",
                grade
            })
        });
        if (!res.ok) {
            console.warn("[-] Could not create clean survey session. Continuing with local state only.");
        }
    } catch (e) {
        console.warn("[-] Survey session API unavailable. Continuing with offline fallback.", e);
    }
}

// Helper mapping UI inputs to Skill ID
function getSkillIdFromSubjectAndGrade(subject, grade) {
    const matchingSkills = getSkillsForSubjectGrade(subject, grade);
    if (matchingSkills.length) return matchingSkills[0];

    if (subject === 'Toán') {
        if (grade === 5) return 'MATH_G5';
        return `MATH_G${grade}`;
    } else if (subject === 'Ngữ văn') {
        return `LIT_G${grade}`;
    } else if (subject === 'Ngoại ngữ') {
        return `ENG_G${grade}`;
    } else if (subject === 'Khoa học tự nhiên') {
        return `SCI_G${grade}`;
    } else if (subject === 'Lịch sử và Địa lý') {
        return `HISGEO_G${grade}`;
    } else if (subject === 'Tin học và Công nghệ') {
        return `INFTECH_G${grade}`;
    }
    return 'MATH_G7';
}

function getSkillsForSubjectGrade(subject, grade) {
    return Object.entries(state.knowledgeGraph || {})
        .filter(([, info]) => info.subject === subject && Number(info.grade) === Number(grade))
        .map(([skillId]) => skillId)
        .sort();
}

function getRandomSkillForCurrentSelection(excludeSkillId = null) {
    const skills = getSkillsForSubjectGrade(state.testSession.subject, state.testSession.grade);
    if (!skills.length) return state.testSession.targetSkill;
    const pool = skills.length > 1 ? skills.filter(skillId => skillId !== excludeSkillId) : skills;
    return pool[Math.floor(Math.random() * pool.length)] || skills[0];
}

// Load a question from backend API or local mock fallback
async function loadStudentQuestion(skillId) {
    if (!state.testStarted || state.surveyCompleted) return;

    state.selectedOption = null;
    state.typedAnswer = "";
    document.getElementById("btn-submit-answer").setAttribute("disabled", "true");
    
    try {
        const params = new URLSearchParams({
            current_skill: skillId,
            answer_format: state.testSession.stage === "short_answer" ? "short" : "choice"
        });
        const res = await fetch(`/api/student/${state.studentId}/next-question?${params.toString()}`);
        if (res.ok) {
            const data = await res.json();
            const question = data.question;
            state.currentQuestion = question;
            state.studentProgress.activeSkill = data.active_skill;
            state.testSession.currentSkill = data.active_skill;
            
            renderCurrentQuestion(question);
            
            // Setup Mascot
            document.getElementById("mascot-comment").textContent = "Hãy đọc kỹ đề bài nhé! Tôi tin bạn làm được!";
            document.getElementById("hint-content-box").style.display = "none";
            resetToolboxForNewQuestion();
            
            // Render the Path
            renderPersonalPath();
            return;
        }
    } catch (e) {
        console.warn("[-] Next-question API failed, fallback to offline mock mode simulation.", e);
    }
    
    // Offline Mock fallback simulator
    loadOfflineMockQuestion(skillId);
}

// Sync UI Dropdowns to Active Skill (for adaptive path shifts)
function syncSelectorsToActiveSkill(skillId) {
    const info = state.knowledgeGraph[skillId];
    if (!info) return;
    
    const subjectSelect = document.getElementById("subject-select");
    const gradeSelect = document.getElementById("grade-select");
    
    if (subjectSelect && gradeSelect) {
        subjectSelect.value = info.subject || "Toán";
        gradeSelect.value = info.grade ? info.grade.toString() : "7";
    }
}

function getCurrentStageLabel() {
    const labels = {
        multiple_choice: "Trắc nghiệm",
        true_false: "Đúng/Sai",
        short_answer: "Trả lời ngắn"
    };
    return labels[state.testSession.stage] || "Trắc nghiệm";
}

function getCorrectOption(question) {
    return question.options.find(opt => opt.key === question.correct_answer) || question.options[0];
}

function getWrongOptions(question) {
    return question.options.filter(opt => opt.key !== question.correct_answer);
}

function getCorrectAnswerText(question) {
    return getCorrectOption(question)?.text || "";
}

function buildTrueFalsePrompt(question) {
    const wrongOptions = getWrongOptions(question);
    const useCorrect = ((state.testSession.answeredInStage + question.id.length) % 2) === 0 || wrongOptions.length === 0;
    const statementOption = useCorrect ? getCorrectOption(question) : wrongOptions[(state.testSession.answeredInStage + question.id.length) % wrongOptions.length];
    question.true_false_answer = useCorrect;
    question.true_false_option_key = statementOption.key;
    return `${question.text}\n\nNhận định: Đáp án đúng là "${statementOption.text}".`;
}

function buildShortAnswerPrompt(question) {
    return `${question.text}\n\nNhập đáp án ngắn bằng đúng một số, một phân số, số thập phân, phần trăm hoặc ký hiệu <, >, =.`;
}

function renderQuestionVisual(question) {
    const visualBox = document.getElementById("question-visual-box");
    if (!visualBox) return;

    const visual = getQuestionVisualMarkup(question);
    visualBox.innerHTML = visual;
    visualBox.style.display = visual ? "block" : "none";
}

function getQuestionVisualMarkup(question) {
    const skillId = question.visual_hint || question.skill_id || "";
    const text = `${question.text || ""} ${question.hint || ""}`.toLowerCase();

    if (skillId.startsWith("MATH_G1") && (text.includes("hình") || text.includes("góc"))) {
        return `
            <div class="visual-panel">
                <div class="shape-row">
                    <span class="shape triangle"></span>
                    <span class="shape square"></span>
                    <span class="shape circle"></span>
                    <span class="shape hexagon"></span>
                </div>
                <p>Đếm góc, cạnh hoặc so sánh số lượng trực quan.</p>
            </div>
        `;
    }

    if ((skillId.startsWith("MATH_G4") || skillId.startsWith("MATH_G6")) && (text.includes("số nguyên") || text.includes("giá trị tuyệt đối") || text.includes("trái dấu"))) {
        return `
            <div class="visual-panel">
                <svg viewBox="0 0 520 90" role="img" aria-label="Trục số minh họa">
                    <line x1="30" y1="45" x2="490" y2="45" stroke="#0f172a" stroke-width="4" />
                    ${[-20,-15,-10,-5,0,5,10,15,20].map((n, i) => {
                        const x = 30 + i * 57.5;
                        const marker = n === 0 ? '#557AFA' : n < 0 ? '#EF5350' : '#4CAF50';
                        return `<line x1="${x}" y1="32" x2="${x}" y2="58" stroke="#0f172a" stroke-width="2" />
                            <text x="${x}" y="78" text-anchor="middle" font-family="Poppins" font-size="14" font-weight="700">${n}</text>
                            <circle cx="${x}" cy="45" r="5" fill="${marker}" stroke="#0f172a" stroke-width="1.5" />`;
                    }).join("")}
                </svg>
                <p>Dùng trục số để kiểm tra dấu và khoảng cách tới 0.</p>
            </div>
        `;
    }

    if ((skillId.startsWith("MATH_G5") || skillId.startsWith("MATH_G7")) && (text.includes("phân số") || text.includes("mẫu") || text.includes("quy đồng"))) {
        return `
            <div class="visual-panel">
                <svg viewBox="0 0 360 150" role="img" aria-label="Minh họa quy đồng phân số">
                    <rect x="30" y="30" width="120" height="34" rx="6" fill="#FCD075" stroke="#0f172a" stroke-width="3" />
                    <line x1="90" y1="30" x2="90" y2="64" stroke="#0f172a" stroke-width="2" />
                    <text x="90" y="92" text-anchor="middle" font-family="Poppins" font-size="16" font-weight="800">1/2 = 3/6</text>
                    <rect x="210" y="30" width="120" height="34" rx="6" fill="#e8ecff" stroke="#0f172a" stroke-width="3" />
                    <line x1="250" y1="30" x2="250" y2="64" stroke="#0f172a" stroke-width="2" />
                    <line x1="290" y1="30" x2="290" y2="64" stroke="#0f172a" stroke-width="2" />
                    <text x="270" y="92" text-anchor="middle" font-family="Poppins" font-size="16" font-weight="800">2/3 = 4/6</text>
                    <text x="180" y="128" text-anchor="middle" font-family="Inter" font-size="13" font-weight="700">Quy đồng về cùng mẫu rồi mới cộng/trừ tử số.</text>
                </svg>
            </div>
        `;
    }

    if (skillId.startsWith("SCI_G1") || text.includes("cây") || text.includes("rễ") || text.includes("lá")) {
        return `
            <div class="visual-panel">
                <svg viewBox="0 0 260 170" role="img" aria-label="Cấu tạo cây">
                    <line x1="130" y1="70" x2="130" y2="125" stroke="#4CAF50" stroke-width="10" stroke-linecap="round" />
                    <ellipse cx="95" cy="65" rx="36" ry="20" fill="#8BC34A" stroke="#0f172a" stroke-width="3" transform="rotate(-25 95 65)" />
                    <ellipse cx="165" cy="62" rx="36" ry="20" fill="#8BC34A" stroke="#0f172a" stroke-width="3" transform="rotate(25 165 62)" />
                    <path d="M130 124 C105 140 92 150 78 160 M130 124 C130 145 130 154 130 166 M130 124 C155 140 168 150 182 160" fill="none" stroke="#8B5E3C" stroke-width="5" stroke-linecap="round" />
                    <rect x="30" y="126" width="200" height="12" rx="6" fill="#F9A46B" stroke="#0f172a" stroke-width="2" />
                    <text x="62" y="38" font-family="Poppins" font-size="13" font-weight="800">Lá</text>
                    <text x="146" y="108" font-family="Poppins" font-size="13" font-weight="800">Thân</text>
                    <text x="170" y="158" font-family="Poppins" font-size="13" font-weight="800">Rễ</text>
                </svg>
            </div>
        `;
    }

    if (skillId.startsWith("SCI_G4") || text.includes("nước") || text.includes("bay hơi") || text.includes("ngưng tụ")) {
        return `
            <div class="visual-panel">
                <svg viewBox="0 0 360 150" role="img" aria-label="Vòng tuần hoàn nước">
                    <circle cx="62" cy="38" r="22" fill="#FCD075" stroke="#0f172a" stroke-width="3" />
                    <path d="M55 105 C105 68 155 68 205 105" fill="none" stroke="#557AFA" stroke-width="5" stroke-linecap="round" />
                    <path d="M225 45 C245 25 285 25 305 45 C325 45 333 70 313 82 L226 82 C205 70 208 48 225 45Z" fill="#e8ecff" stroke="#0f172a" stroke-width="3" />
                    <path d="M255 88 l-10 22 M278 88 l-10 22 M301 88 l-10 22" stroke="#557AFA" stroke-width="4" stroke-linecap="round" />
                    <text x="180" y="136" text-anchor="middle" font-family="Inter" font-size="13" font-weight="700">Bay hơi → ngưng tụ → mưa</text>
                </svg>
            </div>
        `;
    }

    if (skillId.startsWith("SCI_G7") || text.includes("phản xạ") || text.includes("góc tới")) {
        return `
            <div class="visual-panel">
                <svg viewBox="0 0 360 150" role="img" aria-label="Phản xạ ánh sáng">
                    <line x1="40" y1="118" x2="320" y2="118" stroke="#0f172a" stroke-width="5" />
                    <line x1="180" y1="25" x2="180" y2="118" stroke="#94a3b8" stroke-width="3" stroke-dasharray="8 6" />
                    <line x1="65" y1="25" x2="180" y2="118" stroke="#EF5350" stroke-width="5" marker-end="url(#arrow)" />
                    <line x1="180" y1="118" x2="295" y2="25" stroke="#557AFA" stroke-width="5" marker-end="url(#arrow)" />
                    <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" fill="#0f172a" /></marker></defs>
                    <text x="98" y="78" font-family="Poppins" font-size="14" font-weight="800">tia tới</text>
                    <text x="226" y="78" font-family="Poppins" font-size="14" font-weight="800">tia phản xạ</text>
                </svg>
            </div>
        `;
    }

    if (skillId.includes("_GEO") || text.includes("tam giác") || text.includes("tứ giác") || text.includes("góc")) {
        return `
            <div class="visual-panel">
                <svg viewBox="0 0 320 170" role="img" aria-label="Minh họa hình học">
                    <polygon points="60,130 160,35 260,130" fill="#e8ecff" stroke="#0f172a" stroke-width="4" />
                    <path d="M82 130 A25 25 0 0 1 101 112" fill="none" stroke="#EF5350" stroke-width="4" />
                    <path d="M238 130 A25 25 0 0 0 219 112" fill="none" stroke="#557AFA" stroke-width="4" />
                    <text x="160" y="28" text-anchor="middle" font-family="Poppins" font-size="15" font-weight="800">A</text>
                    <text x="48" y="150" font-family="Poppins" font-size="15" font-weight="800">B</text>
                    <text x="266" y="150" font-family="Poppins" font-size="15" font-weight="800">C</text>
                    <text x="160" y="154" text-anchor="middle" font-family="Inter" font-size="13" font-weight="700">Tổng góc tam giác = 180°</text>
                </svg>
            </div>
        `;
    }

    return "";
}

function renderCurrentQuestion(question) {
    const stageLabel = getCurrentStageLabel();
    const stageTarget = state.testSession.stageTargets[state.testSession.stage];
    const ordinal = state.testSession.answeredInStage + 1;
    const difficultyText = `Mức độ: ${question.difficulty} | ${stageLabel} ${ordinal}/${stageTarget}`;

    document.getElementById("current-skill-name").textContent = question.skill_name || KNOWLEDGE_GRAPH_LOCAL_NAMES[question.skill_id] || question.skill_id;
    document.getElementById("current-question-difficulty").textContent = difficultyText;

    const optionsContainer = document.getElementById("options-container");
    const textInputContainer = document.getElementById("text-input-container");
    const textInput = document.getElementById("answer-text-input");
    optionsContainer.replaceChildren();
    textInputContainer.style.display = "none";
    if (textInput) textInput.value = "";
    renderQuestionVisual(question);

    if (state.testSession.stage === "true_false") {
        document.getElementById("question-text").textContent = buildTrueFalsePrompt(question);
        renderQuestionOptions([
            { key: "TRUE", label: "Đ", text: "Đúng" },
            { key: "FALSE", label: "S", text: "Sai" }
        ]);
    } else if (state.testSession.stage === "short_answer") {
        document.getElementById("question-text").textContent = buildShortAnswerPrompt(question);
        textInputContainer.style.display = "block";
        if (textInput) {
            textInput.focus();
            textInput.placeholder = "Nhập đáp án, ví dụ: -1/6, 1.25, <, >, =";
            textInput.oninput = handleShortAnswerInput;
            textInput.onkeypress = (e) => {
                if (e.key === "Enter" && state.selectedOption && !state.isSubmitting) submitAnswer();
            };
        }
    } else {
        document.getElementById("question-text").textContent = question.text;
        renderQuestionOptions(question.options);
    }

    updateTestStageUI();
}

function handleShortAnswerInput(e) {
    state.typedAnswer = e.target.value;
    state.selectedOption = state.typedAnswer.trim() ? "__SHORT_ANSWER__" : null;
    const submitBtn = document.getElementById("btn-submit-answer");
    if (state.selectedOption) {
        submitBtn.removeAttribute("disabled");
    } else {
        submitBtn.setAttribute("disabled", "true");
    }
}

function normalizeAnswer(value) {
    return String(value ?? "")
        .trim()
        .toLowerCase()
        .replace(/\s+/g, " ")
        .replaceAll(",", ".")
        .replace(/[()]/g, "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}

function compactAnswer(value) {
    return normalizeAnswer(value).replace(/[^a-z0-9./:=+\-*<>]/g, "");
}

function parseNumericAnswer(value) {
    const normalized = compactAnswer(value);
    if (!normalized) return null;

    const fractionMatch = normalized.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
    if (fractionMatch) {
        const numerator = Number(fractionMatch[1]);
        const denominator = Number(fractionMatch[2]);
        if (Number.isFinite(numerator) && Number.isFinite(denominator) && denominator !== 0) {
            return numerator / denominator;
        }
    }

    const percentMatch = normalized.match(/^(-?\d+(?:\.\d+)?)%$/);
    if (percentMatch) {
        return Number(percentMatch[1]) / 100;
    }

    const simpleNumber = normalized.match(/^-?\d+(?:\.\d+)?$/);
    if (simpleNumber) return Number(normalized);

    return null;
}

function isShortAnswerCompatibleText(value) {
    const raw = String(value ?? "").trim();
    const compact = compactAnswer(raw);
    if (!compact) return false;
    if (/^[<>=]+$/.test(compact)) return true;
    if (/\b(hoac|va|ngay|tebao|hinh|ngon|phim)\b/i.test(compact) || compact.includes(",")) return false;
    const numericTokens = compact.match(/-?\d+(?:\.\d+)?(?:\/\d+(?:\.\d+)?)?/g) || [];
    if (numericTokens.length !== 1) return false;
    if (/^-?\d+(?:\.\d+)?(?:\/\d+(?:\.\d+)?)?%?$/i.test(compact)) return true;
    return false;
}

function answerTextMatches(inputValue, optionText) {
    if (!isShortAnswerCompatibleText(optionText)) return false;
    const input = normalizeAnswer(inputValue);
    const option = normalizeAnswer(optionText);
    const compactInput = compactAnswer(inputValue);
    const compactOption = compactAnswer(optionText);
    if (!input || !option) return false;
    if (input === option || compactInput === compactOption) return true;

    const inputNumber = parseNumericAnswer(inputValue);
    const optionNumber = parseNumericAnswer(optionText);
    if (inputNumber !== null && optionNumber !== null && Math.abs(inputNumber - optionNumber) < 1e-9) {
        return true;
    }

    return false;
}

function findOptionByShortAnswer(question, typedAnswer) {
    const answer = String(typedAnswer ?? "").trim();
    if (!answer) return null;

    return question.options.find(opt => isShortAnswerCompatibleText(opt.text) && answerTextMatches(answer, opt.text)) || null;
}

function buildShortAnswerFeedback(isCorrect) {
    if (isCorrect) return "Tuyệt vời! Đáp án ngắn của bạn khớp với kết quả đúng.";
    const hint = state.currentQuestion?.hint || "Hãy kiểm tra lại kết quả cuối cùng và cách viết đáp án.";
    return `Chưa khớp rồi. Gợi ý: ${hint}`;
}

function resolveSubmissionOption() {
    const question = state.currentQuestion;
    if (!question) return state.selectedOption;

    if (state.testSession.stage === "true_false") {
        const pickedTrue = state.selectedOption === "TRUE";
        if (pickedTrue === question.true_false_answer) return question.correct_answer;
        return question.true_false_option_key === question.correct_answer
            ? (getWrongOptions(question)[0]?.key || question.correct_answer)
            : question.true_false_option_key;
    }

    if (state.testSession.stage === "short_answer") {
        const matchedOption = findOptionByShortAnswer(question, state.typedAnswer);
        return matchedOption?.key || getWrongOptions(question)[0]?.key || "__WRONG__";
    }

    return state.selectedOption;
}

function updateTestStageUI() {
    const stageOrder = ["multiple_choice", "true_false", "short_answer"];
    document.querySelectorAll(".test-stage-pill").forEach(pill => {
        const stage = pill.getAttribute("data-stage");
        const stageIndex = stageOrder.indexOf(stage);
        pill.classList.toggle("active", stage === state.testSession.stage);
        pill.classList.toggle("completed", stageIndex < state.testSession.stageIndex);
    });
}

function advanceQuestionFormatIfNeeded() {
    const stageOrder = ["multiple_choice", "true_false", "short_answer"];
    state.testSession.answeredInStage += 1;
    state.testSession.totalAnswered += 1;
    const currentTarget = state.testSession.stageTargets[state.testSession.stage];
    const totalTarget = getSurveyTotalTarget();
    if (state.testSession.totalAnswered >= totalTarget) {
        updateTestStageUI();
        return {
            completed: true,
            message: "Đã hoàn thành bài khảo sát. AI đang tổng hợp kết quả và lộ trình học."
        };
    }

    if (state.testSession.answeredInStage < currentTarget) return null;

    if (state.testSession.stageIndex < stageOrder.length - 1) {
        state.testSession.stageIndex += 1;
        state.testSession.stage = stageOrder[state.testSession.stageIndex];
        state.testSession.answeredInStage = 0;
        updateTestStageUI();
        return {
            completed: false,
            message: `Chuyển sang phần ${getCurrentStageLabel()}. Độ khó vẫn được điều chỉnh như phần trước.`
        };
    }

    state.testSession.answeredInStage = Math.max(currentTarget - 1, 0);
    return null;
}

function getSurveyTotalTarget() {
    return Object.values(state.testSession.stageTargets).reduce((sum, count) => sum + count, 0);
}

function recordSurveyAttempt(isCorrect, submittedOption) {
    const question = state.currentQuestion;
    if (!question) return;

    state.testSession.attempts.push({
        questionId: question.id,
        questionText: question.text,
        stage: state.testSession.stage,
        skillId: question.skill_id,
        skillName: question.skill_name || KNOWLEDGE_GRAPH_LOCAL_NAMES[question.skill_id] || question.skill_id,
        difficulty: question.difficulty,
        difficultyLevel: question.difficulty_level || 2,
        isCorrect,
        submittedOption,
        typedAnswer: state.typedAnswer,
        correctAnswerText: getCorrectAnswerText(question)
    });
}

function completeSurvey() {
    state.surveyCompleted = true;
    state.testStarted = false;
    state.isSubmitting = false;
    setQuestionVisibility(false);
    setSurveyResultVisibility(true);
    const banner = document.getElementById("diagnostic-banner");
    if (banner) banner.style.display = "none";
    renderSurveyResult();
}

function groupAttemptsBySkill() {
    return state.testSession.attempts.reduce((groups, attempt) => {
        if (!groups[attempt.skillId]) {
            groups[attempt.skillId] = {
                skillId: attempt.skillId,
                skillName: attempt.skillName,
                total: 0,
                wrong: 0,
                attempts: []
            };
        }
        groups[attempt.skillId].total += 1;
        if (!attempt.isCorrect) groups[attempt.skillId].wrong += 1;
        groups[attempt.skillId].attempts.push(attempt);
        return groups;
    }, {});
}

function getStageStats() {
    const labels = {
        multiple_choice: "Trắc nghiệm",
        true_false: "Đúng/Sai",
        short_answer: "Trả lời ngắn"
    };
    return Object.entries(state.testSession.stageTargets).map(([stage, target]) => {
        const attempts = state.testSession.attempts.filter(item => item.stage === stage);
        const correct = attempts.filter(item => item.isCorrect).length;
        return {
            stage,
            label: labels[stage],
            total: target,
            attempted: attempts.length,
            correct
        };
    });
}

function chooseRootGap(skillGroups) {
    const gapCandidates = Object.values(skillGroups)
        .filter(group => group.wrong > 0)
        .sort((a, b) => {
            const gradeA = state.knowledgeGraph[a.skillId]?.grade || state.testSession.grade;
            const gradeB = state.knowledgeGraph[b.skillId]?.grade || state.testSession.grade;
            if (gradeA !== gradeB) return gradeA - gradeB;
            return (b.wrong / b.total) - (a.wrong / a.total);
        });

    if (gapCandidates.length) return gapCandidates[0];

    const targetSkill = state.testSession.targetSkill;
    return {
        skillId: targetSkill,
        skillName: state.knowledgeGraph[targetSkill]?.name || targetSkill,
        total: 0,
        wrong: 0,
        attempts: []
    };
}

function buildLearningPathFromRoot(rootSkillId) {
    const graph = state.knowledgeGraph || {};
    const targetSkill = state.testSession.targetSkill;
    if (!graph[rootSkillId] || !graph[targetSkill]) {
        return [rootSkillId, targetSkill].filter(Boolean);
    }

    const queue = [[rootSkillId]];
    const seen = new Set([rootSkillId]);
    while (queue.length) {
        const path = queue.shift();
        const current = path[path.length - 1];
        if (current === targetSkill) return path;

        const nextSkills = Object.entries(graph)
            .filter(([, info]) => (info.prerequisites || []).includes(current))
            .map(([id]) => id);

        for (const next of nextSkills) {
            if (!seen.has(next)) {
                seen.add(next);
                queue.push([...path, next]);
            }
        }
    }

    return rootSkillId === targetSkill ? [targetSkill] : [rootSkillId, targetSkill];
}

function getNextSkillTowardTarget(currentSkillId) {
    const targetSkill = state.testSession.targetSkill;
    if (!currentSkillId || currentSkillId === targetSkill) return targetSkill;

    const path = buildLearningPathFromRoot(currentSkillId);
    const currentIndex = path.indexOf(currentSkillId);
    if (currentIndex >= 0 && currentIndex < path.length - 1) {
        return path[currentIndex + 1];
    }

    return targetSkill;
}

function chooseNextSkillAfterSubmit(result, isCorrect) {
    const currentSkill = state.currentQuestion?.skill_id || state.testSession.currentSkill || state.testSession.targetSkill;
    if (isCorrect) return getRandomSkillForCurrentSelection(currentSkill);
    return result?.next_recommended_skill || currentSkill;
}

function generateSurveyAnalysis() {
    const attempts = state.testSession.attempts;
    const correct = attempts.filter(item => item.isCorrect).length;
    const total = getSurveyTotalTarget();
    const score = Math.round((correct / total) * 100);
    const skillGroups = groupAttemptsBySkill();
    const rootGap = chooseRootGap(skillGroups);
    const pathSkillIds = buildLearningPathFromRoot(rootGap.skillId);
    const weakGroups = Object.values(skillGroups)
        .filter(group => group.wrong > 0)
        .sort((a, b) => (b.wrong / b.total) - (a.wrong / a.total))
        .slice(0, 4);

    let level = "Cần củng cố nền tảng";
    if (score >= 85) level = "Vững kiến thức lớp hiện tại";
    else if (score >= 65) level = "Đạt mức cơ bản, cần vá vài điểm hổng";

    return {
        correct,
        total,
        score,
        level,
        weakGroups,
        stageStats: getStageStats(),
        rootGap,
        pathSkillIds
    };
}

function renderSurveyResult() {
    const resultCard = document.getElementById("survey-result-card");
    if (!resultCard) return;

    const analysis = generateSurveyAnalysis();
    const pathHtml = analysis.pathSkillIds.map((skillId, index) => {
        const info = state.knowledgeGraph[skillId] || {};
        const name = info.name || KNOWLEDGE_GRAPH_LOCAL_NAMES[skillId] || skillId;
        const grade = info.grade ? `Lớp ${info.grade}` : "Kỹ năng";
        const status = index === 0 ? "Gốc cần vá" : index === analysis.pathSkillIds.length - 1 ? "Mục tiêu hiện tại" : "Cầu nối";
        return `
            <div class="learning-step">
                <span class="learning-step-index">${index + 1}</span>
                <div>
                    <strong>${escapeHTML(name)}</strong>
                    <p>${escapeHTML(grade)} · ${status}</p>
                </div>
            </div>
        `;
    }).join("");

    const weakHtml = analysis.weakGroups.length
        ? analysis.weakGroups.map(group => `
            <li><strong>${escapeHTML(group.skillName)}</strong>: sai ${group.wrong}/${group.total} câu, cần luyện lại bằng ví dụ trực quan trước khi làm bài tổng hợp.</li>
        `).join("")
        : `<li>Không phát hiện điểm hổng rõ rệt trong phiên này. Có thể chuyển sang luyện vận dụng nâng cao của ${escapeHTML(state.testSession.subject)} lớp ${state.testSession.grade}.</li>`;

    const stageHtml = analysis.stageStats.map(stat => `
        <div class="survey-stat">
            <span>${escapeHTML(stat.label)}</span>
            <strong>${stat.correct}/${stat.total}</strong>
        </div>
    `).join("");

    resultCard.innerHTML = `
        <div class="survey-result-header">
            <div>
                <span class="badge badge-skill"><i class="fa-solid fa-wand-magic-sparkles"></i> AI phân tích khảo sát</span>
                <h3>Kết quả ${escapeHTML(state.testSession.subject)} lớp ${state.testSession.grade}</h3>
                <p>Hoàn thành ${analysis.total} câu: 12 trắc nghiệm, 4 đúng/sai, 6 trả lời ngắn.</p>
            </div>
            <div class="survey-score">
                <strong>${analysis.score}</strong>
                <span>/100</span>
            </div>
        </div>
        <div class="survey-stats-grid">${stageHtml}</div>
        <div class="survey-ai-summary">
            <h4><i class="fa-solid fa-magnifying-glass-chart"></i> Nhận định</h4>
            <p>${escapeHTML(analysis.level)}. Gốc cần kiểm tra trước tiên là <strong>${escapeHTML(analysis.rootGap.skillName)}</strong>.</p>
            <h4><i class="fa-solid fa-triangle-exclamation"></i> Điểm yếu còn thiếu</h4>
            <ul>${weakHtml}</ul>
            <h4><i class="fa-solid fa-route"></i> Lộ trình học giả định</h4>
            <div class="learning-path-list">${pathHtml}</div>
        </div>
        <button id="btn-retake-survey" class="btn btn-primary-memphis btn-retake-survey"><i class="fa-solid fa-rotate-right"></i> Làm lại khảo sát</button>
    `;

    const retakeBtn = document.getElementById("btn-retake-survey");
    if (retakeBtn) retakeBtn.addEventListener("click", startAdaptiveTest);
    document.getElementById("mascot-comment").textContent = "AI đã tổng hợp xong kết quả khảo sát và lộ trình học gợi ý.";
}

/**
 * Handles a student's answer selection and updates the submit state.
 *
 * @param {string} optionKey - The selected option key, for example "A", "TRUE", or "FALSE".
 * @param {HTMLButtonElement} optionButton - Button element that was selected.
 */
function handleAnswerSelection(optionKey, optionButton) {
    if (state.isSubmitting) return;

    const optionsContainer = document.getElementById("options-container");
    optionsContainer.querySelectorAll(".option-btn").forEach(btn => {
        btn.classList.remove("selected", "correct-feedback", "error-feedback");
    });

    optionButton.classList.add("selected");
    state.selectedOption = optionKey;
    document.getElementById("btn-submit-answer").removeAttribute("disabled");
}

/**
 * Renders clickable answer buttons for multiple-choice or true/false questions.
 *
 * Basic HTML skeleton for isolated testing:
 * <div id="options-container"></div>
 * <button id="btn-submit-answer" disabled>Submit</button>
 *
 * @param {Array<{key: string, label?: string, text: string}>} options - Answer options.
 */
function renderQuestionOptions(options) {
    const optionsContainer = document.getElementById("options-container");
    optionsContainer.replaceChildren();
    
    options.forEach(opt => {
        const optBtn = document.createElement("button");
        optBtn.className = "option-btn";
        optBtn.setAttribute("data-val", opt.key);
        const letter = document.createElement("span");
        letter.className = "option-letter";
        letter.textContent = opt.label || opt.key;
        optBtn.append(letter, document.createTextNode(` ${opt.text}`));
        
        optBtn.addEventListener("click", () => handleAnswerSelection(opt.key, optBtn));
        
        optionsContainer.appendChild(optBtn);
    });
}

/**
 * Submits a selected answer to the backend check endpoint.
 *
 * The function first uses the report-specified endpoint `/api/check-answer`.
 * If an older backend is running, it falls back to `/api/student/{id}/submit`.
 *
 * @param {string} submittedOption - Normalized option key selected by the student.
 * @returns {Promise<object>} Backend grading result.
 */
async function submitSelectedAnswerToApi(submittedOption) {
    const payload = {
        student_id: state.studentId,
        question_id: state.currentQuestion.id,
        selected_option: submittedOption
    };

    const checkAnswerRes = await fetch("/api/check-answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    if (checkAnswerRes.ok) return checkAnswerRes.json();

    const legacyRes = await fetch(`/api/student/${state.studentId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            question_id: payload.question_id,
            selected_option: payload.selected_option
        })
    });
    if (!legacyRes.ok) {
        throw new Error(`Answer submit failed: ${legacyRes.status}`);
    }
    return legacyRes.json();
}

/**
 * Displays answer feedback and dynamic hints returned by the backend.
 *
 * @param {object} result - Backend response.
 * @param {boolean} isCorrect - Whether the selected answer was correct.
 */
function updateAnswerFeedbackUI(result, isCorrect) {
    const isShortAnswer = state.testSession.stage === "short_answer";
    const isMultipleChoice = state.testSession.stage === "multiple_choice";
    const optionsContainer = document.getElementById("options-container");
    const selectedBtn = optionsContainer.querySelector(`.option-btn[data-val="${state.selectedOption}"]`);
    const mascotComment = document.getElementById("mascot-comment");

    if (isCorrect) {
        if (selectedBtn) selectedBtn.classList.add("correct-feedback");
        mascotComment.textContent = isShortAnswer
            ? buildShortAnswerFeedback(true)
            : "Tuyệt vời! Bạn đã làm hoàn toàn chính xác!";
        showToast("Chúc mừng! Bạn đã trả lời đúng!");
        return;
    }

    if (selectedBtn) selectedBtn.classList.add("error-feedback");
    const backendHint = result?.hint || state.currentQuestion?.hint || "";
    mascotComment.textContent = isShortAnswer
        ? buildShortAnswerFeedback(false)
        : (backendHint ? `Gợi ý: ${backendHint}` : "Chưa đúng rồi. Bạn thử suy nghĩ thêm một chút xem sao?");
    showToast("Chưa chính xác. Hệ thống đang cập nhật chẩn đoán...");

    const distractorBox = document.getElementById("distractor-feedback-box");
    const distractorText = document.getElementById("distractor-feedback-text");
    if (!distractorBox || !distractorText) return;

    const explanation = isMultipleChoice
        ? (result?.distractor_explanation || state.currentQuestion?.distractor_explanations?.[state.selectedOption])
        : null;
    if (explanation) {
        distractorText.textContent = explanation;
        distractorBox.style.display = "block";
    } else {
        distractorBox.style.display = "none";
    }
}

/**
 * Handles the full submit flow after a student has selected an answer.
 */
async function submitAnswer() {
    state.isSubmitting = true;
    document.getElementById("btn-submit-answer").setAttribute("disabled", "true");
    const submittedOption = resolveSubmissionOption();
    
    showLoadingOverlay("Đang chấm điểm và cập nhật chẩn đoán...");
    
    // 1. Submit through backend API
    try {
        const result = await submitSelectedAnswerToApi(submittedOption);
        if (result) {
            hideLoadingOverlay();
            const isCorrect = result.is_correct;
            recordSurveyAttempt(isCorrect, submittedOption);
            const stageMessage = advanceQuestionFormatIfNeeded();
            const nextSkill = chooseNextSkillAfterSubmit(result, isCorrect);
            updateAnswerFeedbackUI(result, isCorrect);
            
            if (isCorrect) {
                // Streak & Rewards update
                if (state.currentQuestion.difficulty_level === 3) {
                    state.streak += 1;
                    state.xp += 100;
                    state.coins += 20;
                } else {
                    state.xp += 50;
                    state.coins += 10;
                }
                updateStudentRewardsUI();
                
                setTimeout(() => {
                    state.isSubmitting = false;
                    if (stageMessage?.message) showToast(stageMessage.message);
                    if (stageMessage?.completed) {
                        completeSurvey();
                        return;
                    }
                    loadStudentQuestion(nextSkill);
                }, 2000);
            } else {
                state.streak = 0; // Reset streak
                updateStudentRewardsUI();
                
                setTimeout(() => {
                    state.isSubmitting = false;
                    if (stageMessage?.message) showToast(stageMessage.message);
                    if (stageMessage?.completed) {
                        completeSurvey();
                        return;
                    }
                    loadStudentQuestion(nextSkill);
                }, 4000);
            }
            return;
        }
    } catch (e) {
        console.warn("[-] Submit API failed. Falling back to offline mock mode simulation.", e);
    }
    
    // 2. Offline Mock submission
    submitAnswerOffline();
}

// Update Student XP/Coins/Streak tags
function updateStudentRewardsUI() {
    const rewardsRow = document.getElementById("student-rewards");
    if (!rewardsRow) return;
    
    rewardsRow.innerHTML = `
        <span class="reward-tag streak-tag"><i class="fa-solid fa-fire"></i> Chuỗi: ${state.streak}</span>
        <span class="reward-tag xp-tag"><i class="fa-solid fa-gem"></i> ${state.xp.toLocaleString()} XP</span>
        <span class="reward-tag coin-tag"><i class="fa-solid fa-coins"></i> ${state.coins} Xu</span>
    `;
}

// Render dynamic path based on knowledge graph API structure
function renderPersonalPath() {
    const flowContainer = document.getElementById("personal-path-flow");
    if (!flowContainer) return;
    flowContainer.innerHTML = "";
    
    const graph = state.knowledgeGraph;
    const activeSkillId = state.studentProgress.activeSkill;
    if (!graph || !graph[activeSkillId]) {
        flowContainer.innerHTML = "<p>Đang tải lộ trình...</p>";
        return;
    }
    
    const activeSkill = graph[activeSkillId];
    const prereqs = activeSkill.prerequisites || [];
    
    // Find next dependent nodes (skills having active as prerequisite)
    const nextSkills = [];
    for (const [skId, skVal] of Object.entries(graph)) {
        if (skVal.prerequisites && skVal.prerequisites.includes(activeSkillId)) {
            nextSkills.push(skId);
        }
    }
    
    const svgWidth = 200;
    const svgHeight = 200;
    let svgHtml = `<svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;
    
    const nodes = [];
    const edges = [];
    
    // 1. Add active node (Middle)
    nodes.push({
        id: activeSkillId,
        x: 100,
        y: 90,
        label: activeSkill.name.split(' ')[0],
        fullName: activeSkill.name,
        color: '#FCD075'
    });
    
    // 2. Add prerequisites (Bottom)
    prereqs.forEach((prereqId, index) => {
        if (graph[prereqId]) {
            const x = prereqs.length === 1 ? 100 : (index === 0 ? 50 : 150);
            nodes.push({
                id: prereqId,
                x: x,
                y: 150,
                label: graph[prereqId].name.split(' ')[0],
                fullName: graph[prereqId].name,
                color: '#4CAF50'
            });
            edges.push({ fromX: x, fromY: 150, toX: 100, toY: 90 });
        }
    });
    
    // 3. Add next/dependent nodes (Top)
    nextSkills.slice(0, 2).forEach((nextId, index) => {
        if (graph[nextId]) {
            const x = nextSkills.length === 1 ? 100 : (index === 0 ? 50 : 150);
            nodes.push({
                id: nextId,
                x: x,
                y: 35,
                label: graph[nextId].name.split(' ')[0],
                fullName: graph[nextId].name,
                color: '#cbd5e1'
            });
            edges.push({ fromX: 100, fromY: 90, toX: x, toY: 35 });
        }
    });
    
    // Render links
    edges.forEach(e => {
        svgHtml += `<line x1="${e.fromX}" y1="${e.fromY}" x2="${e.toX}" y2="${e.toY}" stroke="#0f172a" stroke-width="2.5" />`;
    });
    
    // Render nodes
    nodes.forEach(n => {
        svgHtml += `
            <g class="web-node" style="cursor: pointer;" data-full-name="${escapeHTML(n.fullName)}">
                <circle cx="${n.x}" cy="${n.y}" r="22" fill="${n.color}" stroke="#000000" stroke-width="2.5" />
                <text x="${n.x}" y="${n.y + 4}" font-family="Poppins" font-size="7.5" font-weight="700" text-anchor="middle" fill="#000000">${escapeHTML(n.label)}</text>
            </g>
        `;
    });
    
    svgHtml += `</svg>`;
    
    const legendHtml = `
        <div style="display: flex; justify-content: space-around; font-size: 0.68rem; font-family: Poppins; font-weight: 700; border-top: 2px dashed #000; padding-top: 0.6rem; margin-top: 0.5rem; width: 100%;">
            <div><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#4CAF50; border:1.5px solid #000; margin-right:3px; vertical-align:middle;"></span>Đạt</div>
            <div><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#FCD075; border:1.5px solid #000; margin-right:3px; vertical-align:middle;"></span>Đang học</div>
            <div><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#cbd5e1; border:1.5px solid #000; margin-right:3px; vertical-align:middle;"></span>Chưa học</div>
        </div>
    `;
    
    flowContainer.innerHTML = `<div style="display: flex; flex-direction: column; align-items: center; width: 100%;">${svgHtml}${legendHtml}</div>`;
    flowContainer.querySelectorAll(".web-node").forEach(node => {
        node.addEventListener("click", () => showToast(node.getAttribute("data-full-name")));
    });
}

const MOCK_CLASS_PROGRESS = [
    { label: "Toán 5", percent: 82 },
    { label: "Toán 6", percent: 68 },
    { label: "Toán 7", percent: 54 },
    { label: "Hình 7", percent: 61 },
    { label: "KHTN 7", percent: 73 }
];

/**
 * Updates the small realtime status badge on the teacher dashboard.
 *
 * @param {"connected"|"polling"|"disconnected"} mode - Connection mode.
 * @param {string} label - Human-readable status label.
 */
function setTeacherRealtimeStatus(mode, label) {
    const status = document.getElementById("teacher-realtime-status");
    if (!status) return;
    status.className = `realtime-status ${mode}`;
    status.textContent = label;
}

/**
 * Renders a lightweight bar chart using only DOM and CSS.
 *
 * Basic HTML skeleton for isolated testing:
 * <div id="class-progress-chart" class="class-progress-chart"></div>
 *
 * @param {Array<{label: string, percent: number}>} progressData - Skill progress data.
 */
function renderClassProgressChart(progressData = MOCK_CLASS_PROGRESS) {
    const chart = document.getElementById("class-progress-chart");
    if (!chart) return;

    chart.replaceChildren();
    progressData.forEach(({ label, percent }) => {
        const clampedPercent = Math.max(0, Math.min(100, Number(percent) || 0));
        const item = document.createElement("div");
        item.className = "progress-bar-item";

        const track = document.createElement("div");
        track.className = "progress-bar-track";

        const fill = document.createElement("div");
        fill.className = "progress-bar-fill";
        fill.style.height = `${clampedPercent}%`;
        fill.style.background = clampedPercent >= 75
            ? "var(--success)"
            : clampedPercent >= 50
                ? "var(--primary)"
                : "var(--danger)";
        fill.dataset.value = `${clampedPercent}%`;
        fill.title = `${label}: ${clampedPercent}%`;

        const caption = document.createElement("div");
        caption.className = "progress-bar-label";
        caption.textContent = label;

        track.appendChild(fill);
        item.append(track, caption);
        chart.appendChild(item);
    });
}

/**
 * Normalizes dashboard API or WebSocket payloads into one shape for rendering.
 *
 * @param {object} data - Dashboard payload from API/WebSocket.
 * @returns {object} Safe dashboard data with default arrays.
 */
function normalizeTeacherDashboardData(data = {}) {
    return {
        metrics: data.metrics || {},
        groups: Array.isArray(data.groups) ? data.groups : [],
        priority_list: Array.isArray(data.priority_list) ? data.priority_list : [],
        class_progress: Array.isArray(data.class_progress) && data.class_progress.length
            ? data.class_progress
            : MOCK_CLASS_PROGRESS
    };
}

/**
 * Applies dashboard data to all teacher dashboard widgets.
 *
 * @param {object} dashboardData - Normalized or raw dashboard payload.
 */
function applyTeacherDashboardData(dashboardData) {
    const data = normalizeTeacherDashboardData(dashboardData);
    const totalStudents = document.getElementById("teacher-total-students");
    const averageMastery = document.getElementById("teacher-average-mastery");
    const gapCount = document.getElementById("total-gap-groups-count");
    const reteachBanner = document.getElementById("class-reteach-banner");

    if (totalStudents) totalStudents.textContent = `${data.metrics.total_students ?? 40} học sinh`;
    if (averageMastery) averageMastery.textContent = data.metrics.average_mastery || "72%";
    if (gapCount) gapCount.textContent = data.metrics.gap_groups_count || `${data.groups.length} nhóm`;

    if (reteachBanner) {
        const reTeachAlert = data.metrics.re_teach_alert;
        reteachBanner.style.display = reTeachAlert ? "flex" : "none";
        if (reTeachAlert) {
            document.getElementById("class-reteach-skill-name").textContent = reTeachAlert;
        }
    }

    renderClassProgressChart(data.class_progress);
    renderGapGroups(data.groups);
    renderPriorityList(data.priority_list);
    renderClassroomHeatmap();
}

/**
 * Renders automatic knowledge-gap groups.
 *
 * @param {Array<object>} groups - Group records from backend.
 */
function renderGapGroups(groups) {
    const groupsGrid = document.getElementById("groups-grid-container");
    if (!groupsGrid) return;
    groupsGrid.replaceChildren();

    groups.forEach(grp => {
        const card = document.createElement("div");
        card.className = "group-card";
        const membersTags = (grp.members || [])
            .map(member => `<span class="member-tag">${escapeHTML(member)}</span>`)
            .join("");

        card.innerHTML = `
            <div class="group-card-header">
                <h4>${escapeHTML(KNOWLEDGE_GRAPH_LOCAL_NAMES[grp.skill_id] || grp.title || grp.skill_id)}</h4>
                <span class="student-count">${escapeHTML(grp.count ?? 0)} học sinh</span>
            </div>
            <div class="group-members">${membersTags}</div>
            <div class="group-action">
                <button class="btn btn-hint-outline btn-sm" data-skill-id="${escapeHTML(grp.skill_id)}" data-title="${escapeHTML(grp.title || grp.skill_id)}">
                    <i class="fa-solid fa-share-nodes"></i> Xem giáo án bổ trợ
                </button>
            </div>
        `;
        const lessonBtn = card.querySelector("button[data-skill-id]");
        lessonBtn.addEventListener("click", () => triggerLessonPlanForSkill(grp.skill_id, grp.title));
        groupsGrid.appendChild(card);
    });
}

/**
 * Renders the teacher priority table.
 *
 * @param {Array<object>} students - Priority student records.
 */
function renderPriorityList(students) {
    const tableBody = document.getElementById("priority-table-body");
    if (!tableBody) return;
    tableBody.replaceChildren();

    students.forEach((std, index) => {
        const row = document.createElement("tr");
        if (index < 2) row.className = "priority-pulsing-row";
        row.innerHTML = `
            <td><strong>${escapeHTML(std.name)}</strong></td>
            <td><span class="badge badge-skill">${escapeHTML(std.current_skill)}</span></td>
            <td><span class="badge badge-danger">${escapeHTML(std.n_failed)} câu</span></td>
            <td><span class="badge badge-warning">${escapeHTML(std.t_stuck)} phút</span></td>
            <td><strong>${escapeHTML(std.priority_score)}</strong></td>
            <td>
                <button class="btn btn-primary-memphis btn-sm" data-student-id="${escapeHTML(std.id)}">
                    <i class="fa-solid fa-hand-holding-hand"></i> Kèm cặp ngay
                </button>
            </td>
        `;
        row.querySelector("button[data-student-id]").addEventListener("click", () => openDiagnosticInspector(std.id));
        tableBody.appendChild(row);
    });
}

/**
 * Fetches teacher dashboard data once via HTTP.
 *
 * @returns {Promise<object>} Dashboard payload.
 */
async function fetchTeacherDashboardData() {
    const res = await fetch("/api/teacher/dashboard");
    if (!res.ok) throw new Error(`Teacher dashboard fetch failed: ${res.status}`);
    return res.json();
}

/**
 * Starts API polling as a fallback when WebSocket is unavailable.
 *
 * @param {number} intervalMs - Poll interval in milliseconds.
 */
function startTeacherDashboardPolling(intervalMs = 8000) {
    if (state.teacherRealtime.pollingTimer) return;
    setTeacherRealtimeStatus("polling", "Polling API");
    state.teacherRealtime.pollingTimer = setInterval(async () => {
        try {
            const data = await fetchTeacherDashboardData();
            applyTeacherDashboardData(data);
        } catch (e) {
            setTeacherRealtimeStatus("disconnected", "Mất kết nối");
            console.warn("[-] Teacher polling failed.", e);
        }
    }, intervalMs);
}

/**
 * Stops teacher dashboard polling.
 */
function stopTeacherDashboardPolling() {
    if (!state.teacherRealtime.pollingTimer) return;
    clearInterval(state.teacherRealtime.pollingTimer);
    state.teacherRealtime.pollingTimer = null;
}

/**
 * Connects to a teacher dashboard WebSocket and falls back to polling on failure.
 */
function connectTeacherDashboardRealtime() {
    if (!("WebSocket" in window)) {
        startTeacherDashboardPolling();
        return;
    }
    if (
        state.teacherRealtime.socket &&
        [WebSocket.CONNECTING, WebSocket.OPEN].includes(state.teacherRealtime.socket.readyState)
    ) {
        return;
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/teacher-dashboard`;
    const socket = new WebSocket(wsUrl);
    state.teacherRealtime.socket = socket;
    setTeacherRealtimeStatus("polling", "Đang nối realtime");

    socket.addEventListener("open", () => {
        state.teacherRealtime.reconnectAttempts = 0;
        stopTeacherDashboardPolling();
        setTeacherRealtimeStatus("connected", "Realtime");
    });

    socket.addEventListener("message", (event) => {
        try {
            const payload = JSON.parse(event.data);
            applyTeacherDashboardData(payload);
        } catch (e) {
            console.warn("[-] Invalid teacher dashboard WebSocket payload.", e);
        }
    });

    const fallbackToPolling = () => {
        state.teacherRealtime.socket = null;
        setTeacherRealtimeStatus("polling", "Polling API");
        startTeacherDashboardPolling();
    };

    socket.addEventListener("error", fallbackToPolling);
    socket.addEventListener("close", fallbackToPolling);
}

// Render Teacher Dashboard using real API data
async function renderTeacherDashboard() {
    try {
        const data = await fetchTeacherDashboardData();
        applyTeacherDashboardData(data);
        connectTeacherDashboardRealtime();
        return;
    } catch (e) {
        console.warn("[-] Teacher dashboard API failed. Using simulated mock panels.", e);
    }
    
    // Offline Mock dashboard fallback
    renderOfflineTeacherDashboard();
}

function triggerLessonPlanForSkill(skillId, title) {
    generateAILessonPlan(title || skillId);
    document.getElementById("modal-lesson-plan").style.display = "flex";
}

const KNOWLEDGE_GRAPH_LOCAL_NAMES = {
    "MATH_G7": "Cộng số hữu tỉ (L7)",
    "MATH_G6": "Cộng số nguyên (L6)",
    "MATH_G4": "GTTĐ của số nguyên (L4)",
    "MATH_G5": "Quy đồng phân số (L5)",
    "MATH_G5_LCM": "Tìm BCNN (L5)"
};

// Heatmap Renderer
function renderClassroomHeatmap() {
    const container = document.getElementById("heatmap-grid-container");
    if (!container) return;
    container.innerHTML = "";
    
    for (let i = 1; i <= 40; i++) {
        const box = document.createElement("div");
        box.className = "heatmap-box";
        box.textContent = i;
        
        if (i === 1) {
            box.className += " danger";
            box.title = "Nguyễn Văn An - Cần kèm gấp!";
            box.addEventListener("click", () => openDiagnosticInspector("an_01"));
        } else if (i === 2) {
            box.className += " warning";
            box.title = "Trần Bình - Đang chẩn đoán";
            box.addEventListener("click", () => openDiagnosticInspector("binh_02"));
        } else if (i === 4) {
            box.className += " danger";
            box.title = "Lê Công Hoàng - Cần kèm gấp!";
            box.addEventListener("click", () => openDiagnosticInspector("hoang_04"));
        } else {
            box.className += " normal";
            box.title = `Học sinh số ${i} - Đang học tập ổn định`;
            box.addEventListener("click", () => openDiagnosticInspector(`std_${i}`));
        }
        container.appendChild(box);
    }
}

// -----------------------------------------------------------------------------
// OFFLINE SIMULATION FALLBACKS (In case API is disconnected)
// -----------------------------------------------------------------------------

const OFFLINE_MOCK_QUESTIONS = {
    "MATH_G7": {
        id: "q_math_g7_2",
        skill_id: "MATH_G7",
        difficulty_level: 2,
        difficulty: "Vừa",
        text: "Tính kết quả của phép tính sau: 1/2 + (-2/3)",
        options: [{key:"A",text:"-1/6"}, {key:"B",text:"1/6"}, {key:"C",text:"-7/6"}, {key:"D",text:"7/6"}],
        correct_answer: "A",
        hint: "Quy đồng mẫu số của 2 phân số trước khi cộng. Mẫu chung là 6.",
        distractor_explanations: {
            "B": "Bạn có thể đã tính nhầm dấu ở tử số khi thực hiện phép cộng 3 + (-4). Nhớ là 3 + (-4) phải là -1, chứ không phải +1.",
            "C": "Bạn có thể đã quy đồng đúng mẫu số chung là 6 nhưng nhân sai tử số hoặc tính sai phép cộng ở tử số. 1/2 thành 3/6; -2/3 thành -4/6. Thực hiện cộng tử số: 3 + (-4) = -1. Kết quả phải là -1/6.",
            "D": "Bạn đã tính sai cả dấu và tử số. Hãy lưu ý quy đồng mẫu số chung là 6 và giữ đúng dấu âm của phân số thứ hai nhé."
        }
    },
    "MATH_G6": {
        id: "q_math_g6_2",
        skill_id: "MATH_G6",
        difficulty_level: 2,
        difficulty: "Vừa",
        text: "Tính kết quả của phép tính sau: (-15) + 8",
        options: [{key:"A",text:"7"}, {key:"B",text:"-7"}, {key:"C",text:"-23"}, {key:"D",text:"23"}],
        correct_answer: "B",
        hint: "Hai số trái dấu, lấy trị tuyệt đối lớn trừ nhỏ, đặt dấu của số lớn trước kết quả.",
        distractor_explanations: {
            "A": "Bạn đã lấy trị tuyệt đối lớn trừ trị tuyệt đối bé (15 - 8 = 7) nhưng lại quên lấy dấu của số có trị tuyệt đối lớn hơn (số -15 mang dấu âm).",
            "C": "Bạn đã cộng hai giá trị tuyệt đối lại với nhau (15 + 8 = 23) rồi lấy dấu âm. Hãy nhớ đây là cộng hai số trái dấu, ta thực hiện phép trừ nhé!",
            "D": "Bạn đã cộng hai giá trị tuyệt đối lại với nhau (15 + 8 = 23) và lấy dấu dương. Hãy lưu ý dấu của hai số hạng và cách cộng hai số nguyên trái dấu."
        }
    },
    "MATH_G5": {
        id: "q_math_g5_2",
        skill_id: "MATH_G5",
        difficulty_level: 2,
        difficulty: "Vừa",
        text: "Quy đồng mẫu số 3/4 và 5/6. Mẫu chung nhỏ nhất của chúng là bao nhiêu?",
        options: [{key:"A",text:"24"}, {key:"B",text:"12"}, {key:"C",text:"10"}, {key:"D",text:"8"}],
        correct_answer: "B",
        hint: "Tìm số tự nhiên nhỏ nhất chia hết cho cả 4 và 6, chính là BCNN(4, 6) = 12.",
        distractor_explanations: {
            "A": "24 quả thực là một bội chung của 4 và 6, nhưng đề bài yêu cầu tìm bội chung NHỎ NHẤT (BCNN). Có một số nhỏ hơn 24 chia hết cho cả 4 và 6 đấy (số 12)!",
            "C": "10 không chia hết cho cả 4 và 6. Bạn có thể đã lấy 4 + 6 = 10. Mẫu số chung phải chia hết cho cả hai mẫu số cũ nhé!",
            "D": "8 chia hết cho 4 nhưng không chia hết cho 6. Mẫu số chung phải là bội chung của cả hai số."
        }
    },
    "MATH_G5_LCM": {
        id: "q_math_g5_lcm_2",
        skill_id: "MATH_G5_LCM",
        difficulty_level: 2,
        difficulty: "Vừa",
        text: "Tìm Bội chung nhỏ nhất của hai số 6 và 8. BCNN(6, 8) = ?",
        options: [{key:"A",text:"48"}, {key:"B",text:"24"}, {key:"C",text:"12"}, {key:"D",text:"18"}],
        correct_answer: "B",
        hint: "Tìm số nhỏ nhất chia hết cho cả 6 và 8.",
        distractor_explanations: {
            "A": "48 là tích của 6 và 8, đây là một bội chung nhưng chưa phải bội chung nhỏ nhất. Có số nhỏ hơn 48 chia hết cho cả 6 và 8 đấy!",
            "C": "12 chia hết cho 6 nhưng không chia hết cho 8. BCNN phải chia hết cho cả hai số.",
            "D": "18 chia hết cho 6 nhưng không chia hết cho 8. Hãy xem lại các bội của 8 nhé!"
        }
    }
};

function loadOfflineMockQuestion(skillId) {
    if (!state.testStarted) return;

    const question = OFFLINE_MOCK_QUESTIONS[skillId] || OFFLINE_MOCK_QUESTIONS["MATH_G7"];
    state.currentQuestion = question;
    state.selectedOption = null;
    state.typedAnswer = "";
    
    renderCurrentQuestion(question);
    
    document.getElementById("hint-content-box").style.display = "none";
    document.getElementById("btn-submit-answer").setAttribute("disabled", "true");
    document.getElementById("mascot-comment").textContent = "[MOCK] Hãy đọc kỹ đề bài nhé! Tôi tin bạn làm được!";
    resetToolboxForNewQuestion();
    renderPersonalPath();
}

function submitAnswerOffline() {
    hideLoadingOverlay();
    const submittedOption = resolveSubmissionOption();
    const isCorrect = submittedOption === state.currentQuestion.correct_answer;
    const isShortAnswer = state.testSession.stage === "short_answer";
    const isMultipleChoice = state.testSession.stage === "multiple_choice";
    const optionsContainer = document.getElementById("options-container");
    const selectedBtn = optionsContainer.querySelector(`.option-btn[data-val="${state.selectedOption}"]`);
    
    const banner = document.getElementById("diagnostic-banner");
    recordSurveyAttempt(isCorrect, submittedOption);
    const stageMessage = advanceQuestionFormatIfNeeded();
    
    if (isCorrect) {
        if (selectedBtn) selectedBtn.classList.add("correct-feedback");
        document.getElementById("mascot-comment").textContent = isShortAnswer ? buildShortAnswerFeedback(true) : "Tuyệt vời! Bạn đã làm hoàn toàn chính xác!";
        showToast("[MOCK] Trả lời đúng!");
        
        setTimeout(() => {
            state.studentProgress.activeSkill = getNextSkillTowardTarget(state.currentQuestion.skill_id);
            if (state.studentProgress.activeSkill === state.testSession.targetSkill && banner) banner.style.display = "none";
            state.isSubmitting = false;
            if (stageMessage?.message) showToast(stageMessage.message);
            if (stageMessage?.completed) {
                completeSurvey();
                return;
            }
            loadStudentQuestion(state.studentProgress.activeSkill);
        }, 2000);
    } else {
        if (selectedBtn) selectedBtn.classList.add("error-feedback");
        document.getElementById("mascot-comment").textContent = isShortAnswer ? buildShortAnswerFeedback(false) : "Chưa đúng rồi. Bạn thử suy nghĩ thêm một chút xem?";
        showToast("[MOCK] Chưa chính xác!");
        
        // Show distractor explanation
        const distractorBox = document.getElementById("distractor-feedback-box");
        const distractorText = document.getElementById("distractor-feedback-text");
        if (distractorBox && distractorText && state.currentQuestion.distractor_explanations && isMultipleChoice) {
            const expl = state.currentQuestion.distractor_explanations[state.selectedOption];
            if (expl) {
                distractorText.textContent = expl;
                distractorBox.style.display = "block";
            }
        } else if (distractorBox) {
            distractorBox.style.display = "none";
        }
        
        setTimeout(() => {
            // Shift down logic mock
            if (state.studentProgress.activeSkill === 'MATH_G7') {
                state.studentProgress.activeSkill = 'MATH_G5';
                if (banner) banner.style.display = "flex";
            } else if (state.studentProgress.activeSkill === 'MATH_G5') {
                state.studentProgress.activeSkill = 'MATH_G5_LCM';
            }
            state.isSubmitting = false;
            if (stageMessage?.message) showToast(stageMessage.message);
            if (stageMessage?.completed) {
                completeSurvey();
                return;
            }
            loadStudentQuestion(state.studentProgress.activeSkill);
        }, 4000);
    }
}

function renderOfflineTeacherDashboard() {
    const reteachBanner = document.getElementById("class-reteach-banner");
    reteachBanner.style.display = "flex";
    document.getElementById("class-reteach-skill-name").textContent = "Quy đồng mẫu số phân số (Lớp 5)";
    document.getElementById("teacher-total-students").textContent = "40 học sinh";
    document.getElementById("teacher-average-mastery").textContent = "72%";
    document.getElementById("total-gap-groups-count").textContent = "2 nhóm";
    setTeacherRealtimeStatus("disconnected", "Mock offline");
    renderClassProgressChart(MOCK_CLASS_PROGRESS);
    
    const groupsGrid = document.getElementById("groups-grid-container");
    groupsGrid.innerHTML = "";
    
    const mockGroups = [
        { title: "Nhóm hổng: Quy đồng phân số (Lớp 5)", count: 12, members: ["Trần Bình", "Trần Minh Khánh", "+10 học sinh khác"], skill_id: "MATH_G5" },
        { title: "Nhóm hổng: Cộng trừ số nguyên (Lớp 6)", count: 8, members: ["Nguyễn Văn An", "Phạm Khánh Linh", "+6 học sinh khác"], skill_id: "MATH_G6" }
    ];
    
    mockGroups.forEach(grp => {
        const card = document.createElement("div");
        card.className = "group-card";
        let membersTags = grp.members.map(m => `<span class="member-tag">${m}</span>`).join("");
        
        card.innerHTML = `
            <div class="group-card-header">
                <h4>${grp.title}</h4>
                <span class="student-count">${grp.count} học sinh</span>
            </div>
            <div class="group-members">${membersTags}</div>
            <div class="group-action">
                <button class="btn btn-hint-outline btn-sm" onclick="triggerLessonPlanForSkill('${grp.skill_id}', '${grp.title}')"><i class="fa-solid fa-share-nodes"></i> Xem giáo án</button>
            </div>
        `;
        groupsGrid.appendChild(card);
    });
    
    const tableBody = document.getElementById("priority-table-body");
    tableBody.innerHTML = "";
    state.mockStudents.forEach((std, index) => {
        const row = document.createElement("tr");
        if (index < 2) row.className = "priority-pulsing-row";
        
        row.innerHTML = `
            <td><strong>${std.name}</strong></td>
            <td><span class="badge badge-skill">${std.currentSkill}</span></td>
            <td><span class="badge badge-danger">${std.nFailed} câu</span></td>
            <td><span class="badge badge-warning">${std.tStuck} phút</span></td>
            <td><strong>${(1.5 + index * 0.1).toFixed(2)}</strong></td>
            <td><button class="btn btn-primary-memphis btn-sm" onclick="openDiagnosticInspector('${std.id}')"><i class="fa-solid fa-hand-holding-hand"></i> Kèm cặp</button></td>
        `;
        tableBody.appendChild(row);
    });
    
    renderClassroomHeatmap();
}

// -----------------------------------------------------------------------------
// CHAT, MODALS, HEATMAP, SCRATCHPAD, SLIDER LOGIC
// -----------------------------------------------------------------------------

function initMascotReadAloud() {
    const speakBtn = document.getElementById("btn-read-aloud");
    if (!speakBtn) return;
    
    speakBtn.addEventListener("click", () => {
        const textToSpeak = document.getElementById("mascot-comment").textContent;
        if (!textToSpeak) return;
        
        // Stop any currently speaking voice
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = "vi-VN";
        
        const robotIcon = document.querySelector(".robot-icon-face");
        
        utterance.onstart = () => {
            if (robotIcon) {
                robotIcon.classList.add("fa-beat");
                robotIcon.classList.remove("animate-bounce-slow");
            }
            speakBtn.style.color = "var(--danger)";
        };
        
        utterance.onend = () => {
            if (robotIcon) {
                robotIcon.classList.remove("fa-beat");
                robotIcon.classList.add("animate-bounce-slow");
            }
            speakBtn.style.color = "";
        };
        
        utterance.onerror = () => {
            if (robotIcon) {
                robotIcon.classList.remove("fa-beat");
                robotIcon.classList.add("animate-bounce-slow");
            }
            speakBtn.style.color = "";
        };
        
        // Find Vietnamese voice if possible
        const voices = window.speechSynthesis.getVoices();
        const viVoice = voices.find(voice => voice.lang.includes("vi") || voice.lang.includes("VI"));
        if (viVoice) {
            utterance.voice = viVoice;
        }
        
        window.speechSynthesis.speak(utterance);
    });
}

function initAITutorChat() {
    const chatInput = document.getElementById("tutor-chat-input");
    const sendBtn = document.getElementById("btn-send-tutor");
    const chatHistory = document.getElementById("chat-history-box");
    
    function sendUserMessage(msg) {
        if (!msg.trim()) return;
        
        const userBubble = document.createElement("div");
        userBubble.className = "chat-bubble user-bubble";
        userBubble.innerHTML = `
            <div class="bubble-content"><p>${escapeHTML(msg)}</p></div>
            <div class="bubble-avatar"><i class="fa-solid fa-user-ninja"></i></div>
        `;
        chatHistory.appendChild(userBubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        if (chatInput) chatInput.value = "";
        
        setTimeout(() => {
            const robotBubble = document.createElement("div");
            robotBubble.className = "chat-bubble robot-bubble";
            
            let replyText = "Tôi là trợ lý học tập VGap. Đang phân tích câu hỏi của bạn...";
            if (msg.toLowerCase().includes("bcnn")) {
                replyText = "Bội chung nhỏ nhất (BCNN) của hai số là số tự nhiên nhỏ nhất khác 0 chia hết cho cả hai số đó. Ví dụ: BCNN(6, 8) = 24.";
            } else if (msg.toLowerCase().includes("quy đồng")) {
                replyText = "Để quy đồng mẫu số, ta tìm BCNN của các mẫu số làm mẫu chung, rồi nhân cả tử và mẫu với nhân tử phụ tương ứng.";
            } else if (msg.toLowerCase().includes("số hữu tỉ")) {
                replyText = "Số hữu tỉ là số viết được dưới dạng phân số a/b (a, b thuộc Z, b khác 0). Ví dụ: 0.5, -3/4, 2.";
            }
            
            robotBubble.innerHTML = `
                <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="bubble-content"><p>${escapeHTML(replyText)}</p></div>
            `;
            chatHistory.appendChild(robotBubble);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }, 1000);
    }
    
    if (sendBtn && chatInput) {
        sendBtn.addEventListener("click", () => sendUserMessage(chatInput.value));
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === 'Enter') sendUserMessage(chatInput.value);
        });
    }
    
    document.querySelectorAll(".quick-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            sendUserMessage(btn.getAttribute("data-prompt") || btn.textContent);
        });
    });

    document.querySelectorAll(".demo-action-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            showToast(btn.getAttribute("data-message") || "Đã ghi nhận thao tác.");
        });
    });
}

// AI Learning Toolbox Tab Switching Logic
function initToolboxTabs() {
    const tabBtns = document.querySelectorAll(".toolbox-tab-btn");
    const panels = document.querySelectorAll(".toolbox-panel");
    
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const targetTab = btn.getAttribute("data-toolbox-tab");
            
            panels.forEach(panel => {
                panel.classList.remove("active");
                panel.style.display = "none";
            });
            
            const activePanel = document.getElementById(`toolbox-panel-${targetTab}`);
            if (activePanel) {
                activePanel.classList.add("active");
                if (targetTab === "mascot") {
                    activePanel.style.display = "flex";
                } else {
                    activePanel.style.display = "block";
                }
            }
        });
    });
}

// Student Socratic Mascot Chat Integration
function initStudentMascotChat() {
    const chatInput = document.getElementById("mascot-chat-input");
    const sendBtn = document.getElementById("btn-send-mascot-chat");
    const chatHistory = document.getElementById("mascot-chat-history");
    const commentPara = document.getElementById("mascot-comment");

    if (!chatInput || !sendBtn || !chatHistory) return;

    function handleSend() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Show chat history if hidden
        chatHistory.style.display = "flex";

        // Append user message
        const userMsg = document.createElement("div");
        userMsg.className = "mascot-msg user";
        userMsg.textContent = text;
        chatHistory.appendChild(userMsg);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        chatInput.value = "";
        commentPara.textContent = "Trợ lý đang suy nghĩ...";

        // Simulate AI response delay
        setTimeout(() => {
            let reply = "Tôi là trợ lý Socratic của VGap. Bạn hãy thử làm tiếp và hỏi tôi nếu có bước nào chưa rõ nhé!";
            const activeSkill = state.studentProgress.activeSkill;
            const textL = text.toLowerCase();

            if (activeSkill === 'MATH_G7') {
                if (textL.includes("quy đồng") || textL.includes("mẫu số") || textL.includes("làm sao") || textL.includes("mẫu chung")) {
                    reply = "Để quy đồng 1/2 và -2/3, ta tìm mẫu số chung nhỏ nhất của 2 và 3. Đó chính là 6. Bạn hãy nhân cả tử và mẫu của 1/2 với 3, và nhân cả tử và mẫu của -2/3 với 2 nhé.";
                } else if (textL.includes("dấu") || textL.includes("âm")) {
                    reply = "Khi cộng hai số trái dấu ở tử số (3 và -4), bạn lấy trị tuyệt đối lớn trừ nhỏ: 4 - 3 = 1, rồi lấy dấu âm của số lớn hơn. Kết quả tử số là -1.";
                } else {
                    reply = "Gợi ý: Mẫu số chung nhỏ nhất là 6. Bạn hãy quy đồng hai phân số này rồi thực hiện phép cộng các tử số nhé.";
                }
            } else if (activeSkill === 'MATH_G6') {
                if (textL.includes("trái dấu") || textL.includes("cộng") || textL.includes("làm sao")) {
                    reply = "Để cộng (-15) và 8 (hai số trái dấu), bạn hãy tìm hiệu hai giá trị tuyệt đối: 15 - 8 = 7, sau đó đặt dấu âm của số -15 trước kết quả.";
                } else {
                    reply = "Gợi ý: Đây là phép cộng hai số nguyên trái dấu. Bạn hãy lấy hiệu hai trị tuyệt đối rồi lấy dấu của số có trị tuyệt đối lớn hơn.";
                }
            } else if (activeSkill === 'MATH_G5') {
                if (textL.includes("bcnn") || textL.includes("mẫu chung") || textL.includes("nhỏ nhất")) {
                    reply = "Bội chung nhỏ nhất của 4 và 6 là số nhỏ nhất chia hết cho cả hai số này. Bội của 4 là 4, 8, 12... Bội của 6 là 6, 12... Vậy số nhỏ nhất là 12.";
                } else {
                    reply = "Gợi ý: Hãy liệt kê các bội số của 4 và 6, sau đó tìm số nhỏ nhất xuất hiện ở cả hai danh sách nhé.";
                }
            } else if (activeSkill === 'MATH_G5_LCM') {
                if (textL.includes("bcnn") || textL.includes("bội chung") || textL.includes("làm thế nào")) {
                    reply = "BCNN của 6 và 8 là số nhỏ nhất chia hết cho cả hai. Bạn thử tìm xem bội nào của 8 chia hết cho 6 nhé (8, 16, 24...). Số 24 chính là số cần tìm.";
                } else {
                    reply = "Gợi ý: BCNN(6, 8) là số nhỏ nhất khác 0 chia hết cho cả 6 và 8. Hãy thử nhân nhẩm bội của 8 xem số nào đầu tiên chia hết cho 6 nhé.";
                }
            }

            // Append bot reply
            const botMsg = document.createElement("div");
            botMsg.className = "mascot-msg bot";
            botMsg.textContent = reply;
            chatHistory.appendChild(botMsg);
            chatHistory.scrollTop = chatHistory.scrollHeight;

            // Sync main mascot comment
            commentPara.textContent = reply;
        }, 1200);
    }

    sendBtn.addEventListener("click", handleSend);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSend();
    });
}

function getStudentLoginProfile(studentId) {
    const profiles = {
        emma_std_01: { name: "Emma (Lớp 7A)", avatar: "Emma", grade: 7, skill: "MATH_G7", xp: 1200, coins: 350, streak: 5 },
        an_01: { name: "Nguyễn Văn An", avatar: "An", grade: 6, skill: "MATH_G6", xp: 850, coins: 150, streak: 2 },
        binh_02: { name: "Trần Bình", avatar: "Binh", grade: 5, skill: "MATH_G5", xp: 920, coins: 210, streak: 3 },
        hoang_06: { name: "Lê Huy Hoàng", avatar: "Hoang", grade: 7, skill: "MATH_G7", xp: 1050, coins: 280, streak: 4 }
    };
    return profiles[studentId] || profiles.emma_std_01;
}

async function ensureStudentProfileForLogin(studentId, profile) {
    try {
        await fetch("/api/students", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: studentId,
                name: profile.name,
                grade: profile.grade
            })
        });
    } catch (e) {
        console.warn("[-] Student profile API unavailable; login will continue locally.", e);
    }
}

function switchPortalUI(targetRole) {
    const btnTogglePortal = document.getElementById("btn-toggle-portal");
    const portalStudent = document.getElementById("portal-student");
    const portalTeacher = document.getElementById("portal-teacher");
    const progressWrapper = document.getElementById("student-progress-wrapper");
    const teacherTitleWrapper = document.getElementById("teacher-title-wrapper");
    const studentRewards = document.getElementById("student-rewards");
    const userDisplayName = document.getElementById("user-display-name");
    const userAvatarImg = document.getElementById("user-avatar-img");

    if (targetRole === "teacher") {
        state.currentPortal = "teacher";
        if (portalStudent) portalStudent.classList.remove("active");
        if (portalTeacher) portalTeacher.classList.add("active");
        if (progressWrapper) progressWrapper.style.display = "none";
        if (studentRewards) studentRewards.style.display = "none";
        if (teacherTitleWrapper) teacherTitleWrapper.style.display = "block";
        if (userDisplayName) userDisplayName.textContent = "Thầy Hùng (GV Toán)";
        if (userAvatarImg) userAvatarImg.src = "https://api.dicebear.com/7.x/adventurer/svg?seed=TeacherHung";
        if (btnTogglePortal) setButtonIconLabel(btnTogglePortal, "fa-solid fa-graduation-cap", "Học sinh");
        renderTeacherDashboard();
        return;
    }

    const profile = getStudentLoginProfile(state.baseStudentId || state.studentId);
    state.currentPortal = "student";
    if (portalTeacher) portalTeacher.classList.remove("active");
    if (portalStudent) portalStudent.classList.add("active");
    if (progressWrapper) progressWrapper.style.display = "block";
    if (studentRewards) studentRewards.style.display = "flex";
    if (teacherTitleWrapper) teacherTitleWrapper.style.display = "none";
    if (userDisplayName) userDisplayName.textContent = profile.name;
    if (userAvatarImg) userAvatarImg.src = `https://api.dicebear.com/7.x/adventurer/svg?seed=${profile.avatar}`;
    if (btnTogglePortal) setButtonIconLabel(btnTogglePortal, "fa-solid fa-arrows-rotate", "Chuyển Bảng");
}

function initAuthFlow() {
    const loginOverlay = document.getElementById("login-overlay");
    const tabBtns = document.querySelectorAll(".login-tab-btn");
    const formPanels = document.querySelectorAll(".login-form-panel");
    const loginSubmitBtn = document.getElementById("btn-login-submit");
    const logoutBtn = document.getElementById("btn-logout");
    const errorMsg = document.getElementById("login-error-msg");
    let activeRole = "student";

    const showError = (message) => {
        if (!errorMsg) return;
        errorMsg.textContent = message;
        errorMsg.style.display = "flex";
    };

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeRole = btn.getAttribute("data-login-role") || "student";
            formPanels.forEach(panel => panel.classList.remove("active"));
            const panel = document.getElementById(`login-form-${activeRole}`);
            if (panel) panel.classList.add("active");
            if (errorMsg) errorMsg.style.display = "none";
        });
    });

    if (loginSubmitBtn) {
        loginSubmitBtn.addEventListener("click", async () => {
            if (errorMsg) errorMsg.style.display = "none";

            if (activeRole === "teacher") {
                const password = document.getElementById("teacher-pass")?.value || "";
                if (password.trim() !== "123456") {
                    showError("Mật khẩu giáo viên mặc định là 123456.");
                    return;
                }
                state.isLoggedIn = true;
                state.loggedInRole = "teacher";
                localStorage.setItem("isLoggedIn", "true");
                localStorage.setItem("loggedInRole", "teacher");
                localStorage.removeItem("studentId");
                if (loginOverlay) loginOverlay.classList.add("hidden");
                switchPortalUI("teacher");
                showToast("Đăng nhập giáo viên thành công.");
                return;
            }

            const selectEl = document.getElementById("student-select-login");
            const studentId = selectEl?.value || "emma_std_01";
            const password = document.getElementById("student-pass")?.value || "";
            if (!password.trim()) {
                showError("Vui lòng nhập mật khẩu.");
                return;
            }

            const profile = getStudentLoginProfile(studentId);
            state.isLoggedIn = true;
            state.loggedInRole = "student";
            state.baseStudentId = studentId;
            state.studentId = studentId;
            state.xp = profile.xp;
            state.coins = profile.coins;
            state.streak = profile.streak;
            state.studentProgress.activeSkill = profile.skill;

            localStorage.setItem("isLoggedIn", "true");
            localStorage.setItem("loggedInRole", "student");
            localStorage.setItem("studentId", studentId);
            await ensureStudentProfileForLogin(studentId, profile);
            if (loginOverlay) loginOverlay.classList.add("hidden");
            switchPortalUI("student");
            updateStudentRewardsUI();

            const subjectSelect = document.getElementById("subject-select");
            const gradeSelect = document.getElementById("grade-select");
            if (subjectSelect) subjectSelect.value = "Toán";
            if (gradeSelect) gradeSelect.value = String(profile.grade);
            prepareTestSetup();
            showToast(`Đăng nhập thành công. Chọn lớp/môn rồi bấm Bắt đầu để làm bài test.`);
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("isLoggedIn");
            localStorage.removeItem("loggedInRole");
            localStorage.removeItem("studentId");
            state.isLoggedIn = false;
            state.loggedInRole = null;
            state.studentId = "emma_std_01";
            state.baseStudentId = "emma_std_01";
            prepareTestSetup();
            if (loginOverlay) loginOverlay.classList.remove("hidden");
            showToast("Đã đăng xuất.");
        });
    }

    const storedLoggedIn = localStorage.getItem("isLoggedIn");
    const storedRole = localStorage.getItem("loggedInRole");
    const storedStudentId = localStorage.getItem("studentId") || "emma_std_01";
    if (storedLoggedIn === "true" && storedRole) {
        state.isLoggedIn = true;
        state.loggedInRole = storedRole;
        if (storedRole === "student") {
            const profile = getStudentLoginProfile(storedStudentId);
            state.baseStudentId = storedStudentId;
            state.studentId = storedStudentId;
            state.xp = profile.xp;
            state.coins = profile.coins;
            state.streak = profile.streak;
            state.studentProgress.activeSkill = profile.skill;
            switchPortalUI("student");
            updateStudentRewardsUI();
        } else {
            switchPortalUI("teacher");
        }
        if (loginOverlay) loginOverlay.classList.add("hidden");
    } else if (loginOverlay) {
        loginOverlay.classList.remove("hidden");
    }
}

function initPortalNavigation() {
    const btnTogglePortal = document.getElementById("btn-toggle-portal");
    
    btnTogglePortal.addEventListener("click", () => {
        switchPortalUI(state.currentPortal === 'student' ? 'teacher' : 'student');
    });
    
    const menuItems = document.querySelectorAll(".menu-item");
    menuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            menuItems.forEach(i => i.classList.remove("active"));
            item.classList.add("active");
            
            const tabName = item.getAttribute("data-tab");
            if (state.currentPortal === 'teacher') btnTogglePortal.click();
            
            document.querySelectorAll(".student-view-panel").forEach(p => p.style.display = "none");
            const activePanel = document.getElementById(`student-view-${tabName}`);
            if (activePanel) activePanel.style.display = "block";
            
            showToast(`Đang mở: ${item.querySelector('span').textContent}`);
        });
    });
}

function initTeacherTabs() {
    const tabBtns = document.querySelectorAll(".teacher-tab-btn");
    const panels = document.querySelectorAll(".teacher-tab-panel");
    
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const tabName = btn.getAttribute("data-teacher-tab");
            state.currentTeacherTab = tabName;
            
            panels.forEach(p => p.classList.remove("active"));
            document.getElementById(`teacher-tab-${tabName}`).classList.add("active");
            
            if (tabName === 'tree') renderReasoningTreeVisualizer();
        });
    });
}

function initVirtualScratchpad() {
    const canvas = document.getElementById("scratchpad-canvas");
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d");
    const penBtn = document.getElementById("btn-scratchpad-pen");
    const eraserBtn = document.getElementById("btn-scratchpad-eraser");
    const clearBtn = document.getElementById("btn-scratchpad-clear");
    const colorBtns = document.querySelectorAll(".color-btn");
    
    let isDrawing = false;
    let currentColor = "#000000";
    
    // Setup initial canvas dimensions
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.strokeStyle = currentColor;
    
    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseout", stopDrawing);
    
    // Touch Events for mobile/tablet
    canvas.addEventListener("touchstart", (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = canvas.getBoundingClientRect();
        isDrawing = true;
        ctx.beginPath();
        ctx.moveTo(touch.clientX - rect.left, touch.clientY - rect.top);
    });
    canvas.addEventListener("touchmove", (e) => {
        e.preventDefault();
        if (!isDrawing) return;
        const touch = e.touches[0];
        const rect = canvas.getBoundingClientRect();
        ctx.lineTo(touch.clientX - rect.left, touch.clientY - rect.top);
        ctx.stroke();
    });
    canvas.addEventListener("touchend", stopDrawing);
    
    function startDrawing(e) {
        isDrawing = true;
        ctx.beginPath();
        const rect = canvas.getBoundingClientRect();
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    }
    function draw(e) {
        if (!isDrawing) return;
        const rect = canvas.getBoundingClientRect();
        ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
        ctx.stroke();
    }
    function stopDrawing() {
        isDrawing = false;
        ctx.closePath();
    }
    
    penBtn.addEventListener("click", () => {
        ctx.strokeStyle = currentColor;
        ctx.lineWidth = 3;
        penBtn.classList.add("active");
        eraserBtn.classList.remove("active");
    });
    eraserBtn.addEventListener("click", () => {
        ctx.strokeStyle = "#FFFFFF";
        ctx.lineWidth = 15;
        eraserBtn.classList.add("active");
        penBtn.classList.remove("active");
    });
    clearBtn.addEventListener("click", () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        showToast("Đã xóa bảng nháp!");
    });
    
    colorBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            colorBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentColor = btn.getAttribute("data-color");
            
            // Auto switch back to Pen mode
            penBtn.click();
        });
    });
}

function initFractionSlider() {
    const slider = document.getElementById("fraction-slider");
    const sliderVal = document.getElementById("fraction-slider-val");
    const sliderContainer = document.getElementById("fraction-slider-container");
    const btnShowHint = document.getElementById("btn-show-hint");
    
    if (!slider || !sliderVal || !sliderContainer) return;
    
    btnShowHint.addEventListener("click", () => {
        // Auto-switch to Hint Tab
        const hintTabBtn = document.querySelector(`.toolbox-tab-btn[data-toolbox-tab="hint"]`);
        if (hintTabBtn) hintTabBtn.click();
        
        const skill = state.studentProgress.activeSkill;
        if (skill === "MATH_G7" || skill === "MATH_G5") {
            sliderContainer.style.display = "block";
            drawInteractiveFractionCircle(parseInt(slider.value));
        } else {
            sliderContainer.style.display = "none";
        }
        
        // Fill hint text
        const hintTextPara = document.getElementById("hint-text");
        if (hintTextPara && state.currentQuestion) {
            hintTextPara.textContent = state.currentQuestion.hint || "Hãy đọc kỹ đề bài nhé! Tôi tin bạn làm được!";
        }
    });
    
    slider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        sliderVal.textContent = val;
        drawInteractiveFractionCircle(val);
    });
}

function drawInteractiveFractionCircle(segments) {
    const container = document.getElementById("hint-visual-representation");
    if (!container) return;
    
    const size = 160;
    const center = size / 2;
    const radius = 65;
    
    let svgHtml = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" style="background: #FFF; border-radius: 50%; border: 3px solid #000;">`;
    const sliceAngle = (2 * Math.PI) / segments;
    const coloredCount = Math.round(segments / 2);
    
    for (let i = 0; i < coloredCount; i++) {
        const startAngle = i * sliceAngle - Math.PI / 2;
        const endAngle = (i + 1) * sliceAngle - Math.PI / 2;
        const x1 = center + radius * Math.cos(startAngle);
        const y1 = center + radius * Math.sin(startAngle);
        const x2 = center + radius * Math.cos(endAngle);
        const y2 = center + radius * Math.sin(endAngle);
        svgHtml += `<path d="M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2} Z" fill="#FCD075" stroke="#000" stroke-width="1.5" />`;
    }
    for (let i = coloredCount; i < segments; i++) {
        const startAngle = i * sliceAngle - Math.PI / 2;
        const endAngle = (i + 1) * sliceAngle - Math.PI / 2;
        const x1 = center + radius * Math.cos(startAngle);
        const y1 = center + radius * Math.sin(startAngle);
        const x2 = center + radius * Math.cos(endAngle);
        const y2 = center + radius * Math.sin(endAngle);
        svgHtml += `<path d="M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2} Z" fill="#FFF" stroke="#000" stroke-width="1.5" />`;
    }
    
    svgHtml += `</svg>`;
    container.innerHTML = svgHtml + `<p style="font-family: Poppins; font-weight: 700; margin-top: 0.5rem; font-size: 0.85rem; text-align: center;">Cắt hình tròn thành ${segments} phần. Tô màu: ${coloredCount}/${segments} = 1/2</p>`;
}

function initTeacherModals() {
    const btnCreatePlan = document.getElementById("btn-create-lesson-plan");
    const lpModal = document.getElementById("modal-lesson-plan");
    const lpOverlay = document.getElementById("lesson-plan-overlay");
    const lpCloseBtn = document.getElementById("btn-close-lesson-plan");
    
    const diagModal = document.getElementById("modal-diagnostic-inspector");
    const diagOverlay = document.getElementById("diagnostic-overlay");
    const diagCloseBtn = document.getElementById("btn-close-diagnostic");
    
    if (btnCreatePlan) {
        btnCreatePlan.addEventListener("click", () => {
            const warningSkillName = document.getElementById("class-reteach-skill-name").textContent;
            generateAILessonPlan(warningSkillName);
            lpModal.style.display = "flex";
        });
    }
    if (lpCloseBtn) lpCloseBtn.addEventListener("click", () => lpModal.style.display = "none");
    if (lpOverlay) lpOverlay.addEventListener("click", () => lpModal.style.display = "none");
    
    if (diagCloseBtn) diagCloseBtn.addEventListener("click", () => diagModal.style.display = "none");
    if (diagOverlay) diagOverlay.addEventListener("click", () => diagModal.style.display = "none");
}

function generateAILessonPlan(skillName) {
    const container = document.getElementById("lesson-plan-modal-body");
    if (!container) return;
    
    let topic = skillName || "Quy đồng mẫu số phân số (Kiến thức nền gốc Lớp 5)";
    let targetGroup = "Nhóm học sinh bị hổng kiến thức nền tương ứng.";
    let objectives = "";
    let activity = "";
    let exercises = "";
    
    if (topic.includes("Quy đồng") || topic.includes("MATH_G5")) {
        topic = "Quy đồng mẫu số phân số (Kiến thức nền gốc Lớp 5)";
        objectives = "<ul><li>Nắm vững cách tìm BCNN để chọn mẫu số chung.</li><li>Tìm nhân tử phụ chính xác và nhân cả tử và mẫu.</li></ul>";
        activity = "<strong>Trò chơi 'Cắt bánh Pizza':</strong> Sử dụng hình tròn cắt lát trực quan giúp học sinh nhận diện sự tương đương giữa 1/2 và 3/6, 2/4.";
        exercises = "<li>Quy đồng 1/3 và 1/4 (MSC = 12)</li><li>Quy đồng 3/8 và 5/6 (MSC = 24)</li>";
    } else if (topic.includes("Số nguyên") || topic.includes("MATH_G6")) {
        topic = "Cộng, trừ số nguyên trái dấu (Kiến thức Lớp 6)";
        objectives = "<ul><li>Hiểu rõ quy tắc cộng hai số nguyên khác dấu.</li><li>Biết so sánh trị tuyệt đối để đặt dấu phù hợp trước kết quả.</li></ul>";
        activity = "<strong>Trò chơi 'Leo cầu thang':</strong> Học sinh bước tiến (số dương) và bước lùi (số âm) trên vạch kẻ sàn lớp để hình dung trục số.";
        exercises = "<li>Tính (-15) + 8</li><li>Tính 12 - (-18)</li>";
    } else if (topic.includes("BCNN") || topic.includes("MATH_G5_LCM")) {
        topic = "Tìm Bội chung nhỏ nhất - BCNN (Kiến thức Lớp 5)";
        objectives = "<ul><li>Biết phân tích các số ra thừa số nguyên tố.</li><li>Tìm các thừa số chung và riêng với số mũ lớn nhất.</li></ul>";
        activity = "<strong>Hộp số nhấp nháy:</strong> Học sinh viết danh sách các bội số của hai số và khoanh tròn số đầu tiên trùng nhau khác 0.";
        exercises = "<li>Tìm BCNN(6, 8)</li><li>Tìm BCNN(4, 6, 9)</li>";
    } else if (topic.includes("hữu tỉ") || topic.includes("MATH_G7")) {
        topic = "Cộng, trừ số hữu tỉ trái dấu (Kiến thức Lớp 7)";
        objectives = "<ul><li>Quy đồng mẫu số các số hữu tỉ ở dạng phân số hoặc đổi về dạng số thập phân.</li><li>Thực hiện đúng quy tắc cộng trừ số nguyên với phần tử số.</li></ul>";
        activity = "<strong>Chiếc cân cân bằng:</strong> Học sinh đặt các miếng khối lượng đại diện cho số hữu tỉ dương và âm lên hai đĩa cân để trực quan hóa phép cộng.";
        exercises = "<li>Tính 1/2 + (-2/3)</li><li>Tính 0.75 - (-1/2)</li>";
    } else {
        topic = `${topic} (Giáo án Bổ trợ Chuyên sâu)`;
        objectives = "<ul><li>Tái thiết lập các khái niệm cơ bản còn hổng trong chu kỳ chẩn đoán trước.</li><li>Giúp học sinh rèn luyện và tự tin vượt qua bài kiểm tra bù.</li></ul>";
        activity = "<strong>Kèm cặp 1-1:</strong> Phân chia học sinh khá kèm học sinh yếu trong nhóm làm bài tập dự án nhóm.";
        exercises = "<li>Bài tập ôn luyện trọng tâm cấp độ dễ (Level 1)</li><li>Bài tập thực hành củng cố trung bình (Level 2)</li>";
    }
    
    container.innerHTML = `
        <div style="font-family: Inter; line-height: 1.6;">
            <div style="background: var(--secondary-light); border: 2px solid #000; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem;">
                <strong>📚 Giáo án bổ trợ:</strong> ${topic} <br>
                <strong>🎯 Đối tượng áp dụng:</strong> ${targetGroup}
            </div>
            
            <h4>1. Mục tiêu bài học (Objectives)</h4>
            ${objectives}
            
            <h4>2. Hoạt động khởi động (Warm-up Activity)</h4>
            <p>${activity}</p>
            
            <h4>3. Bài tập ôn tập trọng tâm (Core Practice)</h4>
            <ol>
                ${exercises}
            </ol>
            
            <div style="margin-top: 1.5rem; background: var(--primary-light); border: 2px solid #000; padding: 0.9rem; border-radius: 12px; font-weight: 600;">
                Gợi ý này được sinh từ nhóm lỗ hổng hiện tại và có thể dùng ngay làm khung kèm cặp 15 phút trên lớp.
            </div>
        </div>
    `;
}

function renderReasoningTreeVisualizer() {
    const listContainer = document.getElementById("student-select-list");
    listContainer.innerHTML = "";
    
    Object.keys(REASONING_TREES).forEach(key => {
        const std = REASONING_TREES[key];
        const item = document.createElement("div");
        item.className = `student-select-item ${state.selectedStudentForTree === key ? 'selected' : ''}`;
        item.textContent = std.student;
        
        item.addEventListener("click", () => {
            listContainer.querySelectorAll(".student-select-item").forEach(i => i.classList.remove("selected"));
            item.classList.add("selected");
            state.selectedStudentForTree = key;
            drawSVGTree(std);
        });
        listContainer.appendChild(item);
    });
}

function drawSVGTree(treeData) {
    const container = document.getElementById("dag-visualizer-container");
    container.innerHTML = "";
    
    document.getElementById("tree-student-desc").innerHTML = `Đang hiển thị phân tích cây quyết định chẩn đoán của học sinh <strong>${treeData.student}</strong>`;
    
    const svgWidth = 500;
    const svgHeight = 350;
    
    let svgHtml = `<svg class="dag-svg" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;
    svgHtml += `
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#0f172a" />
            </marker>
        </defs>
    `;
    
    const nodeCoords = {};
    treeData.nodes.forEach((node, idx) => {
        const x = svgWidth / 2;
        const y = 50 + (idx * 110);
        nodeCoords[node.id] = { x, y };
        
        let strokeColor = "#0f172a";
        let fillColor = "#FFFFFF";
        let glowStyle = "";
        
        if (node.status === 'gap') {
            strokeColor = "#EF5350";
            fillColor = "#ffebee";
            glowStyle = "filter: drop-shadow(2px 2px 0px #0f172a);";
        } else if (node.status === 'active') {
            strokeColor = "#557AFA";
            fillColor = "#e8ecff";
            glowStyle = "filter: drop-shadow(4px 4px 0px #0f172a);";
        } else if (node.status === 'completed') {
            strokeColor = "#4CAF50";
            fillColor = "#e8f5e9";
            glowStyle = "filter: drop-shadow(2px 2px 0px #0f172a);";
        }
        
        svgHtml += `
            <g class="dag-node ${node.status}" transform="translate(${x - 90}, ${y - 25})" style="${glowStyle}">
                <rect class="dag-node-rect" width="180" height="50" rx="16" fill="${fillColor}" stroke="${strokeColor}" stroke-width="2" />
                <text x="90" y="28" class="dag-node-text" text-anchor="middle" font-size="11" font-family="Poppins" font-weight="700" fill="#0f172a">${node.label}</text>
            </g>
        `;
    });
    
    treeData.edges.forEach(edge => {
        const from = nodeCoords[edge.from];
        const to = nodeCoords[edge.to];
        if (from && to) {
            svgHtml += `<line x1="${from.x}" y1="${from.y + 25}" x2="${to.x}" y2="${to.y - 25}" class="dag-edge" marker-end="url(#arrow)" />`;
        }
    });
    
    svgHtml += `</svg>`;
    container.innerHTML = svgHtml;
}

function showToast(message) {
    const toast = document.getElementById("notification-toast");
    document.getElementById("toast-message").textContent = message;
    toast.style.display = "block";
    setTimeout(() => { toast.style.display = "none"; }, 3000);
}

function showLoadingOverlay(text = "Đang tải...") {
    document.getElementById("loading-text").textContent = text;
    document.getElementById("loading-overlay").style.display = "flex";
}
function hideLoadingOverlay() {
    document.getElementById("loading-overlay").style.display = "none";
}

function openDiagnosticInspector(studentId) {
    const modal = document.getElementById("modal-diagnostic-inspector");
    const container = document.getElementById("diagnostic-inspector-body");
    if (!modal || !container) return;
    
    let name = "Học sinh";
    let activeSkill = "Đang học ổn định";
    let diagnosedError = "Học sinh học tập tốt, chưa phát hiện lỗ hổng kiến thức.";
    let attempts = [];
    
    if (studentId === "an_01") {
        name = "Nguyễn Văn An";
        activeSkill = "Cộng số nguyên (Lớp 6)";
        diagnosedError = "Học sinh thường sai ở bước tính tổng hai số nguyên trái dấu có trị tuyệt đối khác nhau (ví dụ: lấy -15 + 8 ra -23 thay vì -7).";
        attempts = [
            { question: "(-15) + 8", answer: "-23", status: "Incorrect", time: "10 phút trước" },
            { question: "(-15) + 8", answer: "23", status: "Incorrect", time: "15 phút trước" }
        ];
    } else if (studentId === "binh_02") {
        name = "Trần Bình";
        activeSkill = "Quy đồng mẫu số (Lớp 5)";
        diagnosedError = "Học sinh gặp khó khăn trong việc tìm Bội chung nhỏ nhất (BCNN) của hai mẫu số chẵn khác nhau (ví dụ: BCNN của 4 và 6 tính ra 24 thay vì mẫu số chung nhỏ nhất 12).";
        attempts = [
            { question: "Quy đồng 3/4 và 5/6", answer: "24", status: "Incorrect", time: "5 phút trước" }
        ];
    } else if (studentId === "hoang_04") {
        name = "Lê Công Hoàng";
        activeSkill = "Cộng số hữu tỉ (Lớp 7)";
        diagnosedError = "Học sinh bị hổng kiến thức nền về phép cộng phân số âm cùng mẫu số, dẫn tới việc cộng sai số hữu tỉ trái dấu.";
        attempts = [
            { question: "1/2 + (-2/3)", answer: "-7/6", status: "Incorrect", time: "2 phút trước" }
        ];
    } else {
        // Standard normal student
        const num = studentId.replace("std_", "");
        name = `Học sinh số ${num}`;
        activeSkill = "Đạt chuẩn tiến trình";
        diagnosedError = "Tiến độ học tập bình thường. Học sinh đạt tỷ lệ làm đúng trên 85% ở tất cả các kỹ năng môn học hiện tại.";
        attempts = [
            { question: "Luyện tập bài học", answer: "Chính xác", status: "Correct", time: "1 giờ trước" },
            { question: "Kiểm tra định kỳ", answer: "Chính xác", status: "Correct", time: "Hôm qua" }
        ];
    }
    
    let attemptsRows = attempts.map(att => `
        <tr>
            <td><code>${att.question}</code></td>
            <td style="color: ${att.status === 'Correct' ? 'var(--success)' : 'var(--danger)'}; font-weight: 700;">${att.answer}</td>
            <td><span class="badge ${att.status === 'Correct' ? 'badge-success' : 'badge-danger'}">${att.status === 'Correct' ? 'Đúng' : 'Sai'}</span></td>
            <td>${att.time}</td>
        </tr>
    `).join("");
    
    container.innerHTML = `
        <div style="font-family: Inter;">
            <p style="font-size: 1.1rem; margin-bottom: 1rem;">
                <strong>👤 Học sinh:</strong> ${name} <br>
                <strong>🎯 Kỹ năng đang kẹt:</strong> <span class="badge badge-skill">${activeSkill}</span>
            </p>
            <div style="background: rgba(239, 83, 80, 0.1); border: 2px solid var(--danger); padding: 1.2rem; border-radius: 16px; margin-bottom: 1.5rem;">
                <h4 style="color: var(--danger); margin-top: 0;"><i class="fa-solid fa-bug"></i> Phân tích lỗi sai gốc rễ (Root Cause):</h4>
                <p style="margin: 0; font-weight: 500;">${diagnosedError}</p>
            </div>
            <h4 style="margin-bottom: 0.8rem;"><i class="fa-solid fa-clock-rotate-left"></i> Nhật ký làm bài gần đây</h4>
            <div class="table-container">
                <table class="memphis-table" style="font-size: 0.85rem;">
                    <thead>
                        <tr>
                            <th>Câu hỏi</th>
                            <th>Học sinh nhập</th>
                            <th>Trạng thái</th>
                            <th>Thời gian</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${attemptsRows || `<tr><td colspan="4" style="text-align: center;">Chưa có nhật ký làm bài gần đây.</td></tr>`}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    modal.style.display = "flex";
}

// Bind Submit Button Click
const submitBtn = document.getElementById("btn-submit-answer");
if (submitBtn) {
    submitBtn.onclick = () => {
        if (!state.selectedOption || state.isSubmitting) return;
        submitAnswer();
    };
}

function resetToolboxForNewQuestion() {
    // Reset toolbox tab back to scratchpad
    const scratchpadTabBtn = document.querySelector(`.toolbox-tab-btn[data-toolbox-tab="scratchpad"]`);
    if (scratchpadTabBtn) scratchpadTabBtn.click();
    
    // Hide distractor feedback box
    const distractorBox = document.getElementById("distractor-feedback-box");
    if (distractorBox) distractorBox.style.display = "none";
    
    // Reset mascot chat panel
    const chatHistory = document.getElementById("mascot-chat-history");
    if (chatHistory) {
        chatHistory.innerHTML = "";
        chatHistory.style.display = "none";
    }
    const chatInput = document.getElementById("mascot-chat-input");
    if (chatInput) chatInput.value = "";
    
    // Reset hint visual representation
    const visualRep = document.getElementById("hint-visual-representation");
    if (visualRep) visualRep.innerHTML = "";
    const sliderContainer = document.getElementById("fraction-slider-container");
    if (sliderContainer) sliderContainer.style.display = "none";
    const hintTextPara = document.getElementById("hint-text");
    if (hintTextPara) hintTextPara.textContent = "Vui lòng bấm nút Gợi ý ở bên cạnh bài tập để nhận trợ giúp trực quan.";
}
