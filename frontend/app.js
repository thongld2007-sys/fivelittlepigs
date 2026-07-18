// PorcusAI - Frontend Interactive Engine (Memphis Style)
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
    tutorChatHistory: [],
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
            multiple_choice: 6,
            true_false: 2,
            short_answer: 2,
            essay: 1
        }
    },
    teacherRealtime: {
        socket: null,
        pollingTimer: null,
        reconnectTimer: null,
        reconnectAttempts: 0
    },
    knowledgeGraph: {},
    loginStreak: 5,
    answerCombo: 0,
    xp: 1200,
    coins: 350,
    spinTickets: 0,
    redeemedRewards: [],
    rewardHistory: [],
    earnedBadges: [],
    teacherBonusTickets: [],
    aiDecisionLog: [],
    attendance: {
        checkedDates: [],
        lastCheckInDate: null
    },
    dailyQuest: {
        correctAnswers: 0,
        hardCorrectAnswers: 0,
        aiReviewsUnlocked: 0,
        coinsEarned: 0,
        claimed: []
    },
    
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

const REWARD_SHOP_ITEMS = [
    {
        id: "extra_hint",
        cost: 50,
        icon: "fa-solid fa-lightbulb",
        title: "Gợi ý thêm",
        description: "Mở gợi ý của câu hiện tại.",
        tone: "yellow",
        minLevel: 1
    },
    {
        id: "ai_review",
        cost: 150,
        icon: "fa-solid fa-route",
        title: "Bài ôn AI",
        description: "Tạo lộ trình ôn cá nhân từ skill đang học.",
        tone: "blue",
        minLevel: 3
    },
    {
        id: "focus_badge",
        cost: 300,
        icon: "fa-solid fa-medal",
        title: "Huy hiệu vượt ải",
        description: "Gắn huy hiệu vào hồ sơ học tập.",
        tone: "green",
        minLevel: 2
    },
    {
        id: "teacher_bonus",
        cost: 500,
        icon: "fa-solid fa-star",
        title: "Điểm thưởng GV duyệt",
        description: "Tạo phiếu thưởng chờ giáo viên xác nhận.",
        tone: "pink",
        minLevel: 5
    },
    {
        id: "lucky_spin",
        cost: 120,
        icon: "fa-solid fa-dharmachakra",
        title: "Mua 1 lượt quay",
        description: "Đổi xu lấy thêm một lượt quay may mắn.",
        tone: "orange",
        minLevel: 1
    },
    {
        id: "avatar_frame",
        cost: 220,
        icon: "fa-solid fa-user-astronaut",
        title: "Khung avatar vui",
        description: "Mở khung avatar trong hồ sơ học tập.",
        tone: "purple",
        minLevel: 4
    }
];

const REWARD_WHEEL_ITEMS = [
    {
        id: "coins_20",
        icon: "fa-solid fa-coins",
        label: "+20 xu",
        description: "Cộng xu vào ví học tập",
        color: "#FCD075",
        apply: () => {
            state.coins += 20;
            return "+20 xu";
        }
    },
    {
        id: "xp_80",
        icon: "fa-solid fa-gem",
        label: "+80 XP",
        description: "Tăng điểm kinh nghiệm",
        color: "#BFE3FF",
        apply: () => {
            state.xp += 80;
            return "+80 XP";
        }
    },
    {
        id: "hint_pass",
        icon: "fa-solid fa-lightbulb",
        label: "Gợi ý thêm",
        description: "Mở gợi ý câu hiện tại",
        color: "#D5F7D3",
        apply: () => "1 gợi ý thêm"
    },
    {
        id: "ai_review",
        icon: "fa-solid fa-route",
        label: "Bài ôn AI",
        description: "Mở lộ trình ôn cá nhân",
        color: "#E8ECFF",
        apply: () => {
            state.dailyQuest.aiReviewsUnlocked += 1;
            return "1 bài ôn AI";
        }
    },
    {
        id: "coins_50",
        icon: "fa-solid fa-sack-dollar",
        label: "+50 xu",
        description: "Phần thưởng hiếm",
        color: "#FFD2D2",
        apply: () => {
            state.coins += 50;
            return "+50 xu";
        }
    },
    {
        id: "badge_focus",
        icon: "fa-solid fa-medal",
        label: "Huy hiệu",
        description: "Huy hiệu chăm học",
        color: "#FDE68A",
        apply: () => "huy hiệu Chăm học"
    }
];

const SUBJECT_OVERVIEW = [
    {
        subject: "Toán",
        grade: 7,
        icon: "fa-solid fa-square-root-variable",
        progress: 42,
        status: "Cần ôn phân số nền",
        activeSkill: "Cộng trừ số hữu tỉ",
        backlog: 3,
        evidence: "Có quiz thích ứng sâu"
    },
    {
        subject: "Ngữ văn",
        grade: 7,
        icon: "fa-solid fa-book-open-reader",
        progress: 68,
        status: "Đọc hiểu ổn định",
        activeSkill: "Tìm ý chính đoạn văn",
        backlog: 1,
        evidence: "Roadmap mở rộng"
    },
    {
        subject: "Ngoại ngữ",
        grade: 7,
        icon: "fa-solid fa-language",
        progress: 55,
        status: "Cần luyện so sánh",
        activeSkill: "Comparatives",
        backlog: 2,
        evidence: "Roadmap mở rộng"
    },
    {
        subject: "Khoa học tự nhiên",
        grade: 7,
        icon: "fa-solid fa-flask",
        progress: 73,
        status: "Đúng tiến độ",
        activeSkill: "Tế bào và cơ thể",
        backlog: 0,
        evidence: "Roadmap mở rộng"
    },
    {
        subject: "Lịch sử và Địa lý",
        grade: 7,
        icon: "fa-solid fa-earth-asia",
        progress: 61,
        status: "Cần ôn mốc sự kiện",
        activeSkill: "Đọc bản đồ",
        backlog: 2,
        evidence: "Roadmap mở rộng"
    },
    {
        subject: "Tin học và Công nghệ",
        grade: 7,
        icon: "fa-solid fa-microchip",
        progress: 49,
        status: "Cần luyện thuật toán",
        activeSkill: "Biểu diễn dữ liệu",
        backlog: 4,
        evidence: "Roadmap mở rộng"
    }
];

const SUBJECT_PROGRESS_STATE = SUBJECT_OVERVIEW.reduce((acc, item) => {
    acc[item.subject] = {
        progress: item.progress,
        status: item.status,
        activeSkill: item.activeSkill,
        backlog: item.backlog,
        completedAssignments: item.backlog === 0 ? 4 : Math.max(1, 4 - item.backlog),
        totalAssignments: 4
    };
    return acc;
}, {});

const XP_LEVELS = [
    { level: 1, min: 0, title: "Khởi động", unlock: "Gợi ý cơ bản" },
    { level: 2, min: 500, title: "Chăm học", unlock: "Shop đổi gợi ý" },
    { level: 3, min: 1000, title: "Vượt ải", unlock: "Bài ôn AI cá nhân hóa" },
    { level: 4, min: 1600, title: "Bền bỉ", unlock: "Câu luyện AI nâng cao" },
    { level: 5, min: 2400, title: "Chuyên gia nhỏ", unlock: "Huy hiệu hồ sơ & đề thử thách" },
    { level: 6, min: 3400, title: "Thủ lĩnh học tập", unlock: "Phiếu giáo viên duyệt" }
];

const DAILY_QUEST_REWARDS = {
    correct5: { label: "Đúng 5 câu", coins: 40, xp: 80, tickets: 0 },
    hard2: { label: "Đúng 2 câu khó", coins: 60, xp: 120, tickets: 1 },
    coins100: { label: "Kiếm 100 xu", coins: 0, xp: 100, tickets: 1 }
};

function getSubjectProgress(subject = state.testSession.subject || "Toán") {
    if (!SUBJECT_PROGRESS_STATE[subject]) {
        SUBJECT_PROGRESS_STATE[subject] = {
            progress: 0,
            status: "Chưa bắt đầu",
            activeSkill: "Khởi động",
            backlog: 4,
            completedAssignments: 0,
            totalAssignments: 4
        };
    }
    return SUBJECT_PROGRESS_STATE[subject];
}

function getLearningLevel(xp = state.xp) {
    const current = [...XP_LEVELS].reverse().find(level => xp >= level.min) || XP_LEVELS[0];
    const next = XP_LEVELS.find(level => level.min > xp) || null;
    const previousMin = current.min;
    const nextMin = next ? next.min : previousMin + 1200;
    const progress = Math.max(0, Math.min(100, Math.round(((xp - previousMin) / (nextMin - previousMin)) * 100)));
    return {
        ...current,
        next,
        progress,
        xpIntoLevel: xp - previousMin,
        xpNeeded: next ? next.min - xp : 0,
        nextMin
    };
}

function canUseLevel(minLevel = 1) {
    return getLearningLevel().level >= minLevel;
}

function getRewardStorageKey(studentId = state.studentId) {
    return `porcus_reward_state_${studentId || "guest"}`;
}

function loadRewardState(profile) {
    const defaults = {
        xp: profile?.xp ?? state.xp,
        coins: profile?.coins ?? state.coins,
        spinTickets: state.spinTickets,
        loginStreak: profile?.streak ?? state.loginStreak,
        answerCombo: 0,
        redeemedRewards: [],
        rewardHistory: [],
        earnedBadges: [],
        teacherBonusTickets: [],
        aiDecisionLog: [],
        subjectProgress: SUBJECT_PROGRESS_STATE,
        attendance: {
            checkedDates: [],
            lastCheckInDate: null
        },
        dailyQuest: {
            correctAnswers: 0,
            hardCorrectAnswers: 0,
            aiReviewsUnlocked: 0,
            coinsEarned: 0,
            claimed: []
        }
    };

    try {
        const saved = JSON.parse(localStorage.getItem(getRewardStorageKey()) || "null");
        if (!saved || typeof saved !== "object") return defaults;
        return {
            ...defaults,
            ...saved,
            dailyQuest: { ...defaults.dailyQuest, ...(saved.dailyQuest || {}) },
            attendance: { ...defaults.attendance, ...(saved.attendance || {}) },
            redeemedRewards: Array.isArray(saved.redeemedRewards) ? saved.redeemedRewards : [],
            rewardHistory: Array.isArray(saved.rewardHistory) ? saved.rewardHistory : [],
            earnedBadges: Array.isArray(saved.earnedBadges) ? saved.earnedBadges : [],
            teacherBonusTickets: Array.isArray(saved.teacherBonusTickets) ? saved.teacherBonusTickets : [],
            aiDecisionLog: Array.isArray(saved.aiDecisionLog) ? saved.aiDecisionLog : []
        };
    } catch (error) {
        console.warn("[-] Reward state corrupted; using profile defaults.", error);
        return defaults;
    }
}

function applyRewardState(rewardState) {
    state.xp = Number(rewardState.xp) || 0;
    state.coins = Number(rewardState.coins) || 0;
    state.spinTickets = Number(rewardState.spinTickets) || 0;
    state.loginStreak = Number(rewardState.loginStreak ?? rewardState.streak) || 0;
    state.answerCombo = Number(rewardState.answerCombo) || 0;
    state.redeemedRewards = Array.isArray(rewardState.redeemedRewards) ? rewardState.redeemedRewards : [];
    state.rewardHistory = Array.isArray(rewardState.rewardHistory) ? rewardState.rewardHistory : [];
    state.earnedBadges = Array.isArray(rewardState.earnedBadges) ? rewardState.earnedBadges : [];
    state.teacherBonusTickets = Array.isArray(rewardState.teacherBonusTickets) ? rewardState.teacherBonusTickets : [];
    state.aiDecisionLog = Array.isArray(rewardState.aiDecisionLog) ? rewardState.aiDecisionLog : [];
    if (rewardState.subjectProgress && typeof rewardState.subjectProgress === "object") {
        Object.entries(rewardState.subjectProgress).forEach(([subject, progress]) => {
            SUBJECT_PROGRESS_STATE[subject] = {
                ...getSubjectProgress(subject),
                ...progress
            };
        });
    }
    state.attendance = {
        checkedDates: Array.isArray(rewardState.attendance?.checkedDates) ? rewardState.attendance.checkedDates : [],
        lastCheckInDate: rewardState.attendance?.lastCheckInDate || null
    };
    state.dailyQuest = {
        correctAnswers: Number(rewardState.dailyQuest?.correctAnswers) || 0,
        hardCorrectAnswers: Number(rewardState.dailyQuest?.hardCorrectAnswers) || 0,
        aiReviewsUnlocked: Number(rewardState.dailyQuest?.aiReviewsUnlocked) || 0,
        coinsEarned: Number(rewardState.dailyQuest?.coinsEarned) || 0,
        claimed: Array.isArray(rewardState.dailyQuest?.claimed) ? rewardState.dailyQuest.claimed : []
    };
}

function saveRewardState() {
    if (!state.studentId) return;
    localStorage.setItem(getRewardStorageKey(), JSON.stringify({
        xp: state.xp,
        coins: state.coins,
        spinTickets: state.spinTickets,
        loginStreak: state.loginStreak,
        answerCombo: state.answerCombo,
        redeemedRewards: state.redeemedRewards,
        rewardHistory: state.rewardHistory,
        earnedBadges: state.earnedBadges,
        teacherBonusTickets: state.teacherBonusTickets,
        aiDecisionLog: state.aiDecisionLog,
        subjectProgress: SUBJECT_PROGRESS_STATE,
        attendance: state.attendance,
        dailyQuest: state.dailyQuest
    }));
}

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
    initFinalReportModal();
    initTeacherClassSwitcher();
    initMascotReadAloud();
    initRewardShop();
    initQuestNotification();
    initPersonalReviewActions();
    initStudentProfileModal();
    initActionableDemoControls();
    
    // Load Knowledge Graph DAG
    await loadKnowledgeGraph();
    
    // Bind Subject and Grade Selector Events
    initSubjectSelectors();
    initSubjectOverview();
    renderSubjectOverview();

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
            renderSubjectOverview();
            if (state.testStarted) {
                prepareTestSetup();
            }
            showToast(`Đã chọn: ${subject} - Lớp ${grade}. Bấm Bắt đầu để vào bài test.`);
        };
        
        subjectSelect.addEventListener("change", onSelectChange);
        gradeSelect.addEventListener("change", onSelectChange);
    }

    if (startBtn) {
        startBtn.addEventListener("click", () => startAdaptiveTest(false));
    }
}

function renderSubjectOverview() {
    const grid = document.getElementById("subject-overview-grid");
    if (!grid) return;
    const activeSubject = state.testSession.subject || "Toán";
    grid.innerHTML = SUBJECT_OVERVIEW.map(item => {
        const isActive = item.subject === activeSubject;
        const progressState = getSubjectProgress(item.subject);
        return `
            <button class="subject-overview-card ${isActive ? "active" : ""}" data-subject="${escapeHTML(item.subject)}" data-grade="${item.grade}">
                <div class="subject-overview-icon"><i class="${item.icon}"></i></div>
                <div class="subject-overview-copy">
                    <strong>${escapeHTML(item.subject)} ${item.grade}</strong>
                    <span>${escapeHTML(progressState.activeSkill || item.activeSkill)}</span>
                </div>
                <div class="subject-overview-progress">
                    <em>${progressState.progress}%</em>
                    <div class="subject-mini-track"><span style="width: ${progressState.progress}%"></span></div>
                </div>
                <small>${escapeHTML(progressState.status || item.status)} · ${progressState.backlog} bài ôn · ${escapeHTML(item.evidence)}</small>
            </button>
        `;
    }).join("");
    updateLearningProgressUI();
}

function updateLearningProgressUI() {
    const subject = state.testSession.subject || "Toán";
    const progressState = getSubjectProgress(subject);
    const fill = document.getElementById("student-progress-fill");
    const activeSkill = document.getElementById("summary-active-skill");
    const aiCheck = document.getElementById("summary-ai-check");
    const nextStep = document.getElementById("summary-next-step");
    if (fill) fill.style.width = `${progressState.progress}%`;
    document.querySelectorAll(".path-score-badge strong").forEach(node => {
        node.textContent = `${progressState.progress}%`;
    });
    if (activeSkill) activeSkill.textContent = `${subject} ${state.testSession.grade || 7} · ${progressState.activeSkill}`;
    if (aiCheck) aiCheck.textContent = progressState.progress < 60
        ? "Ưu tiên tìm lỗi gốc trước khi tăng độ khó"
        : "Theo dõi khả năng vận dụng và lỗi lặp lại";
    if (nextStep) nextStep.textContent = progressState.progress >= 80
        ? "Mở câu vận dụng nâng cao nếu Level đủ"
        : "Làm khảo sát hoặc tự luận để AI cập nhật lộ trình";
    renderCoursesView();
    renderAIDecisionLog();
}

function addAIDecisionLog(entry) {
    const record = {
        source: entry.source || "AI",
        signal: entry.signal || "Dữ liệu học tập mới",
        decision: entry.decision || "Cập nhật lộ trình cá nhân",
        measurement: entry.measurement || "Đo lại bằng câu luyện tiếp theo",
        confidence: entry.confidence ?? null,
        time: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })
    };
    state.aiDecisionLog.unshift(record);
    state.aiDecisionLog = state.aiDecisionLog.slice(0, 8);
    saveRewardState();
    renderAIDecisionLog();
}

function renderAIDecisionLog() {
    const list = document.getElementById("ai-decision-log-list");
    const count = document.getElementById("ai-decision-count");
    if (!list) return;
    if (count) count.textContent = `${state.aiDecisionLog.length} quyết định`;
    if (!state.aiDecisionLog.length) {
        list.innerHTML = '<div class="ai-decision-empty">Làm bài khảo sát hoặc gửi tự luận để AI ghi lại quyết định chẩn đoán.</div>';
        return;
    }
    list.innerHTML = state.aiDecisionLog.slice(0, 4).map(item => `
        <article class="ai-decision-item">
            <div>
                <strong>${escapeHTML(item.source)}</strong>
                <span>${escapeHTML(item.time)} · ${item.confidence !== null ? `tin cậy ${Math.round(Number(item.confidence) * 100)}%` : "đã ghi nhận"}</span>
            </div>
            <p><b>Tín hiệu:</b> ${escapeHTML(item.signal)}</p>
            <p><b>Quyết định:</b> ${escapeHTML(item.decision)}</p>
            <small><i class="fa-solid fa-ruler"></i> ${escapeHTML(item.measurement)}</small>
        </article>
    `).join("");
}

function updateSubjectProgressFromSurvey(analysis) {
    const subject = state.testSession.subject || "Toán";
    const progressState = getSubjectProgress(subject);
    const previousProgress = Number(progressState.progress) || 0;
    const score = Number(analysis?.score || 0);
    const gained = score >= 85 ? 12 : score >= 65 ? 8 : score >= 40 ? 4 : 2;
    progressState.progress = Math.max(previousProgress, Math.min(100, previousProgress + gained));
    progressState.status = score >= 85
        ? "Đạt tốt, mở câu nâng cao"
        : score >= 65
            ? "Cơ bản ổn, còn vài điểm hổng"
            : "Cần ôn nền trước";
    progressState.activeSkill = analysis?.rootGap?.skillName || progressState.activeSkill;
    progressState.backlog = Math.max(0, Math.ceil((100 - progressState.progress) / 18));
    progressState.completedAssignments = Math.min(progressState.totalAssignments, Math.max(progressState.completedAssignments, Math.round(progressState.progress / 25)));
    addAIDecisionLog({
        source: "Khảo sát thích ứng",
        signal: `${state.testSession.subject} đạt ${score}/100, gốc cần kiểm tra: ${analysis?.rootGap?.skillName || progressState.activeSkill}`,
        decision: `Cập nhật tiến trình ${subject} lên ${progressState.progress}% và ưu tiên ${progressState.activeSkill}.`,
        measurement: score >= 65 ? "Đo lại bằng câu vận dụng và tự luận AI." : "Đo lại bằng gói ôn nền trước khi quay lại bài hiện tại.",
        confidence: Math.min(0.95, Math.max(0.55, score / 100))
    });
    saveRewardState();
    renderSubjectOverview();
}

function renderPersonalReviewSteps(steps, summary = "") {
    const list = document.getElementById("personal-review-list");
    if (!list) return;
    const safeSteps = Array.isArray(steps) && steps.length ? steps : getOfflinePersonalReviewSteps();
    const summaryHtml = summary ? `<div class="personal-review-summary">${escapeHTML(summary)}</div>` : "";
    list.innerHTML = `${summaryHtml}${safeSteps.slice(0, 4).map((step, index) => `
        <div class="personal-review-step">
            <span>${index + 1}</span>
            <div>
                <strong>${escapeHTML(step.skill_name || step.skill_id || `Bước ${index + 1}`)}</strong>
                <p>${escapeHTML(step.action || "Luyện tập theo gợi ý cá nhân.")}</p>
                <p><b>Đạt khi:</b> ${escapeHTML(step.success_signal || "đúng liên tiếp các câu cùng kỹ năng.")}</p>
            </div>
        </div>
    `).join("")}`;
}

async function buildPersonalAIReview({ silent = false } = {}) {
    const button = document.getElementById("btn-build-personal-review");
    const skillId = resolveActiveLearningSkillId();
    if (button) {
        button.disabled = true;
        setButtonIconLabel(button, "fa-solid fa-spinner fa-spin", "Đang tạo");
    }

    try {
        const params = new URLSearchParams({ target_skill: skillId });
        const response = await fetch(`/api/ai/student/${state.studentId}/learning-path?${params.toString()}`);
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || `AI HTTP ${response.status}`);
        }
        const data = await response.json();
        const path = data.learning_path || {};
        renderPersonalReviewSteps(path.steps, path.summary || `Lộ trình ôn cho ${getSkillDisplayName(skillId)}`);
        state.dailyQuest.aiReviewsUnlocked += 1;
        addAIDecisionLog({
            source: "Bài ôn AI",
            signal: `Mastery hiện tại của ${getSkillDisplayName(skillId)} cần lộ trình cá nhân.`,
            decision: "Sinh gói ôn theo prerequisite graph và mức thành thạo hiện tại.",
            measurement: "Học sinh phải đạt tín hiệu thành công của từng bước trong bài ôn.",
            confidence: 0.82
        });
        saveRewardState();
        updateStudentRewardsUI();
        if (!silent) showToast("Đã tạo bài ôn AI cá nhân hóa.");
        return path;
    } catch (error) {
        console.warn("[Personal Review] Fallback offline.", error);
        const steps = getOfflinePersonalReviewSteps(skillId);
        renderPersonalReviewSteps(steps, `Lộ trình dự phòng: ôn cho ${getSkillDisplayName(skillId)}.`);
        if (!silent) showToast("AI chưa sẵn sàng, đã dùng lộ trình dự phòng.");
        return { summary: `Lộ trình ôn cho ${getSkillDisplayName(skillId)}`, steps };
    } finally {
        if (button) {
            button.disabled = false;
            setButtonIconLabel(button, "fa-solid fa-route", "Tạo bài ôn");
        }
    }
}

async function generatePersonalReviewQuestion() {
    const button = document.getElementById("btn-generate-review-question");
    const level = getLearningLevel();
    if (button) {
        button.disabled = true;
        setButtonIconLabel(button, "fa-solid fa-spinner fa-spin", "Đang sinh");
    }

    try {
        const response = await fetch(`/api/ai/student/${state.studentId}/generate-question`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                subject: state.testSession.subject || "Toán",
                grade: state.testSession.grade || 7,
                skill_id: resolveActiveLearningSkillId(),
                difficulty_level: level.level >= 4 ? 3 : (state.currentQuestion?.difficulty_level || 2),
                count: 1,
                question_type: "multiple_choice"
            })
        });
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || `AI HTTP ${response.status}`);
        }
        const data = await response.json();
        const question = data.questions?.[0];
        if (!question) throw new Error("AI không trả về câu hỏi.");
        renderPersonalReviewSteps([
            {
                skill_name: question.difficulty || getSkillDisplayName(),
                action: question.text,
                success_signal: `${(question.options || []).map(opt => `${opt.key}. ${opt.text}`).join(" · ")}`
            },
            {
                skill_name: "Gợi ý",
                action: question.hint || "Nói rõ bước làm trước khi chọn đáp án.",
                success_signal: "Sau khi làm xong, hỏi trợ lý vì sao đúng hoặc sai."
            }
        ], level.level >= 4 ? "Câu luyện AI nâng cao đã mở nhờ Level học tập." : "Câu luyện AI củng cố theo mức hiện tại.");
        showToast(level.level >= 4 ? "Đã sinh câu luyện nâng cao." : "Đã sinh 1 câu luyện AI.");
    } catch (error) {
        console.warn("[Personal Review Question] Fallback offline.", error);
        renderPersonalReviewSteps([
            {
                skill_name: getSkillDisplayName(),
                action: "Tự tạo câu luyện: hãy giải 1/2 + (-2/3), viết đủ bước quy đồng rồi cộng tử số.",
                success_signal: "Kết quả đúng và giải thích được vì sao mẫu chung là 6."
            }
        ], "AI sinh câu chưa sẵn sàng, dùng câu luyện dự phòng.");
        showToast("AI chưa sinh được câu, đã dùng câu luyện dự phòng.");
    } finally {
        if (button) {
            button.disabled = false;
            setButtonIconLabel(button, "fa-solid fa-square-plus", "Sinh 1 câu luyện");
        }
    }
}

function initPersonalReviewActions() {
    const buildButton = document.getElementById("btn-build-personal-review");
    if (buildButton) buildButton.addEventListener("click", () => buildPersonalAIReview());

    const questionButton = document.getElementById("btn-generate-review-question");
    if (questionButton) questionButton.addEventListener("click", generatePersonalReviewQuestion);

    const assistantButton = document.getElementById("btn-open-review-assistant");
    if (assistantButton) {
        assistantButton.addEventListener("click", () => {
            const mascotTab = document.querySelector('[data-toolbox-tab="mascot"]');
            if (mascotTab) mascotTab.click();
            const chatInput = document.getElementById("mascot-chat-input");
            if (chatInput) {
                chatInput.value = "Tạo cho em bài ôn cá nhân theo phần em đang yếu.";
                chatInput.focus();
            }
        });
    }
}

function selectSubjectFromOverview(subject, grade) {
    const subjectSelect = document.getElementById("subject-select");
    const gradeSelect = document.getElementById("grade-select");
    if (subjectSelect) subjectSelect.value = subject;
    if (gradeSelect) gradeSelect.value = String(grade);
    const skillId = getSkillIdFromSubjectAndGrade(subject, grade);
    state.studentProgress.activeSkill = skillId;
    state.testSession.subject = subject;
    state.testSession.grade = grade;
    renderSubjectOverview();
    prepareTestSetup();
    showToast(`Đã chọn ${subject} - Lớp ${grade}. Bấm Bắt đầu để luyện môn này.`);
}

function initSubjectOverview() {
    const grid = document.getElementById("subject-overview-grid");
    if (!grid) return;
    grid.addEventListener("click", event => {
        const card = event.target.closest("[data-subject]");
        if (!card) return;
        selectSubjectFromOverview(card.getAttribute("data-subject"), parseInt(card.getAttribute("data-grade") || "7"));
    });
}

function switchStudentTab(tabName) {
    document.querySelectorAll("#student-sidebar-menu .menu-item").forEach(item => {
        item.classList.toggle("active", item.getAttribute("data-tab") === tabName);
    });
    document.querySelectorAll(".student-view-panel").forEach(panel => {
        panel.style.display = "none";
    });
    const activePanel = document.getElementById(`student-view-${tabName}`);
    if (activePanel) activePanel.style.display = "block";
    if (state.currentPortal === "teacher") switchPortalUI("student");
}

function openDashboardForSubject(subject, grade = 7, { startTest = false } = {}) {
    selectSubjectFromOverview(subject, grade);
    switchStudentTab("dashboard");
    if (startTest) {
        setTimeout(() => startAdaptiveTest(), 120);
    }
}

function renderCoursesView() {
    const focusTitle = document.querySelector(".course-focus-header h3");
    const focusDesc = document.querySelector(".course-focus-header p");
    const progressMeta = document.querySelector(".course-progress-meta strong");
    const progressFill = document.querySelector(".course-progress-large .progress-fill");
    const statGrid = document.querySelector(".course-stat-grid");
    const roadmapTitle = document.querySelector(".course-snapshot-card .course-roadmap-list")?.closest(".course-snapshot-card")?.querySelector("h3");
    const roadmapList = document.querySelector(".course-roadmap-list");
    const catalogList = document.querySelector(".course-catalog-list");
    const subject = state.testSession.subject || "Toán";
    const grade = state.testSession.grade || 7;
    const progressState = getSubjectProgress(subject);

    if (focusTitle) focusTitle.textContent = `${subject} ${grade}: ${progressState.activeSkill}`;
    if (focusDesc) focusDesc.textContent = `${progressState.status}. Tiến trình và bài ôn thay đổi theo kết quả khảo sát của riêng môn này.`;
    if (progressMeta) progressMeta.textContent = `${progressState.progress}%`;
    if (progressFill) progressFill.style.width = `${progressState.progress}%`;
    if (roadmapTitle) roadmapTitle.innerHTML = `<i class="fa-solid fa-layer-group"></i> Lộ trình cá nhân môn ${escapeHTML(subject)}`;
    if (roadmapList) {
        const rootGap = progressState.status.includes("nền") || progressState.progress < 60;
        roadmapList.innerHTML = `
            <div class="course-roadmap-item ${rootGap ? "active" : "complete"}">
                <strong>Nền tảng bắt buộc</strong>
                <span>${rootGap ? "Đang cần ôn lại trước khi học tiếp." : "Đã đủ chắc để chuyển bước tiếp theo."}</span>
            </div>
            <div class="course-roadmap-item ${rootGap ? "next" : "active"}">
                <strong>${escapeHTML(progressState.activeSkill)}</strong>
                <span>${escapeHTML(progressState.status)}</span>
            </div>
            <div class="course-roadmap-item next">
                <strong>Câu vận dụng mở rộng</strong>
                <span>Mở khi tiến trình môn đạt 80% và Level học tập đạt 4.</span>
            </div>
        `;
    }
    if (statGrid) {
        statGrid.innerHTML = `
            <div><strong>${progressState.totalAssignments}</strong><span>học phần</span></div>
            <div><strong>${Math.max(3, 11 - progressState.backlog)}</strong><span>kỹ năng đã mở</span></div>
            <div><strong>${progressState.progress}%</strong><span>tiến độ</span></div>
        `;
    }
    if (catalogList) {
        catalogList.innerHTML = SUBJECT_OVERVIEW.slice(0, 4).map(item => {
            const itemState = getSubjectProgress(item.subject);
            const isActive = item.subject === subject;
            return `
                <button class="course-catalog-item ${isActive ? "active" : ""}" data-course-subject="${escapeHTML(item.subject)}" data-course-grade="${item.grade}">
                    <span class="course-code">${escapeHTML(item.subject.slice(0, 3).toUpperCase())}-${item.grade}</span>
                    <strong>${escapeHTML(item.subject)} ${item.grade}</strong>
                    <small>${itemState.progress}% · ${escapeHTML(itemState.status)}</small>
                </button>
            `;
        }).join("");
    }
}

function openAssignmentReview() {
    const modal = document.getElementById("modal-diagnostic-inspector");
    const body = document.getElementById("diagnostic-inspector-body");
    if (!modal || !body) return;
    modal.style.display = "flex";
    body.innerHTML = `
        <div class="assignment-review-modal">
            <h3><i class="fa-solid fa-rotate-left"></i> Xem lại bài đã hoàn thành</h3>
            <p class="card-subtitle-desc">Bài ôn Quy đồng phân số cơ bản: 10/10. Hệ thống dùng kết quả này làm bằng chứng em đã chắc nền phân số lớp 5.</p>
            <div class="review-answer-grid">
                <div><strong>Câu mẫu</strong><span>Quy đồng 3/4 và 5/6</span></div>
                <div><strong>Đáp án đúng</strong><span>9/12 và 10/12</span></div>
                <div><strong>AI ghi nhận</strong><span>Không còn lỗi chọn mẫu chung 24 thay vì 12.</span></div>
            </div>
        </div>
    `;
}

function initActionableDemoControls() {
    document.addEventListener("click", event => {
        const courseButton = event.target.closest("[data-course-subject]");
        if (courseButton) {
            selectSubjectFromOverview(courseButton.getAttribute("data-course-subject"), parseInt(courseButton.getAttribute("data-course-grade") || "7"));
            renderCoursesView();
            showToast(`Đã mở khóa học ${courseButton.getAttribute("data-course-subject")}.`);
            return;
        }

        const demoButton = event.target.closest(".demo-action-btn");
        if (!demoButton) return;
        const message = demoButton.getAttribute("data-message") || "";
        const label = demoButton.textContent || "";
        if (message.includes("lộ trình Toán") || label.includes("Làm tiếp") || message.includes("Bắt đầu")) {
            openDashboardForSubject("Toán", 7, { startTest: message.includes("Bắt đầu") || label.includes("Làm tiếp") });
        } else if (message.includes("bổ trợ lớp 6")) {
            openDashboardForSubject("Toán", 6, { startTest: true });
        } else if (message.includes("xem lại") || message.includes("bản xem lại")) {
            openAssignmentReview();
        } else if (message.includes("Ngữ văn")) {
            selectSubjectFromOverview("Ngữ văn", 7);
            renderCoursesView();
        } else if (message.includes("Tiếng Anh")) {
            selectSubjectFromOverview("Ngoại ngữ", 7);
            renderCoursesView();
        } else if (message.includes("KHTN")) {
            selectSubjectFromOverview("Khoa học tự nhiên", 7);
            renderCoursesView();
        }
        showToast(demoButton.getAttribute("data-message") || "Đã thực hiện thao tác.");
    });
}

function renderStudentProfile() {
    const body = document.getElementById("student-profile-modal-body");
    if (!body) return;
    const profile = getStudentLoginProfile(state.baseStudentId || state.studentId);
    const level = getLearningLevel();
    const subjectRows = SUBJECT_OVERVIEW.map(item => {
        const progress = getSubjectProgress(item.subject);
        return `
            <div class="profile-subject-row">
                <div>
                    <strong>${escapeHTML(item.subject)} ${item.grade}</strong>
                    <span>${escapeHTML(progress.activeSkill)} · ${escapeHTML(progress.status)}</span>
                </div>
                <em>${progress.progress}%</em>
                <div class="profile-progress-track"><span style="width:${progress.progress}%"></span></div>
            </div>
        `;
    }).join("");
    const badgeHtml = state.earnedBadges.length
        ? state.earnedBadges.map(badge => `<span class="profile-badge"><i class="fa-solid fa-medal"></i> ${escapeHTML(badge)}</span>`).join("")
        : `<span class="profile-empty">Chưa có huy hiệu. Đổi trong shop hoặc hoàn thành thử thách để mở.</span>`;
    const ticketHtml = state.teacherBonusTickets.length
        ? state.teacherBonusTickets.map(ticket => `
            <div class="profile-ticket">
                <strong>${escapeHTML(ticket.title)}</strong>
                <span>${escapeHTML(ticket.status)} · ${escapeHTML(ticket.createdAt)}</span>
            </div>
        `).join("")
        : `<span class="profile-empty">Chưa có phiếu giáo viên duyệt.</span>`;
    const recentHtml = state.rewardHistory.length
        ? state.rewardHistory.slice(0, 4).map(item => `
            <div class="profile-activity">
                <i class="${item.icon}"></i>
                <span>${escapeHTML(item.label)}</span>
                <small>${escapeHTML(item.time)}</small>
            </div>
        `).join("")
        : `<span class="profile-empty">Chưa có hoạt động thưởng gần đây.</span>`;

    body.innerHTML = `
        <div class="student-profile-layout">
            <section class="profile-hero-panel">
                <img src="https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(profile.avatar)}" alt="Avatar học sinh">
                <div>
                    <span class="badge badge-skill">Hồ sơ học sinh</span>
                    <h2>${escapeHTML(profile.name)}</h2>
                    <p>Lớp ${profile.grade} · ${state.loginStreak} ngày liên tiếp · ${state.coins.toLocaleString()} xu</p>
                </div>
                <div class="profile-level-card">
                    <strong>Level ${level.level}</strong>
                    <span>${escapeHTML(level.title)}</span>
                    <div class="level-progress-track"><span style="width:${level.progress}%"></span></div>
                    <small>${level.next ? `${level.xpNeeded.toLocaleString()} XP nữa mở ${level.next.unlock}` : "Đã mở khóa cao nhất"}</small>
                </div>
            </section>
            <section class="profile-grid">
                <div class="profile-panel">
                    <h3><i class="fa-solid fa-chart-line"></i> Tiến trình từng môn</h3>
                    <div class="profile-subject-list">${subjectRows}</div>
                </div>
                <div class="profile-panel">
                    <h3><i class="fa-solid fa-award"></i> Huy hiệu</h3>
                    <div class="profile-badge-list">${badgeHtml}</div>
                    <h3><i class="fa-solid fa-chalkboard-user"></i> Phiếu giáo viên</h3>
                    <div class="profile-ticket-list">${ticketHtml}</div>
                </div>
                <div class="profile-panel">
                    <h3><i class="fa-solid fa-clock-rotate-left"></i> Hoạt động gần đây</h3>
                    <div class="profile-activity-list">${recentHtml}</div>
                </div>
            </section>
        </div>
    `;
}

function initStudentProfileModal() {
    const avatar = document.getElementById("user-avatar-container");
    const modal = document.getElementById("modal-student-profile");
    const closeBtn = document.getElementById("btn-close-student-profile");
    const overlay = document.getElementById("student-profile-overlay");
    if (!avatar || !modal) return;

    const open = () => {
        renderStudentProfile();
        modal.style.display = "flex";
    };
    const close = () => {
        modal.style.display = "none";
    };
    avatar.setAttribute("role", "button");
    avatar.setAttribute("tabindex", "0");
    avatar.setAttribute("title", "Mở hồ sơ học tập");
    avatar.addEventListener("click", open);
    avatar.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            open();
        }
    });
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (overlay) overlay.addEventListener("click", close);
}

function prepareTestSetup() {
    state.testStarted = false;
    state.surveyCompleted = false;
    state.selectedOption = null;
    state.typedAnswer = "";
    state.currentQuestion = null;
    state.tutorChatHistory = []; // Clear chat history when loading new question
    clearChatUIs();
    resetTestStage();
    setQuestionVisibility(false);
    setSurveyResultVisibility(false);
    document.getElementById("current-skill-name").textContent = "Chọn lớp và môn";
    document.getElementById("current-question-difficulty").textContent = "Sẵn sàng";
    document.getElementById("question-text").textContent = "Hãy chọn lớp và môn rồi bấm Bắt đầu.";
    document.getElementById("mascot-comment").textContent = "Tôi sẽ chỉ mở câu hỏi sau khi bạn bắt đầu bài test.";
    renderPersonalPath();
}

async function startAdaptiveTest(isInitialAssessment = false) {
    const subjectSelect = document.getElementById("subject-select");
    const gradeSelect = document.getElementById("grade-select");
    const subject = subjectSelect ? subjectSelect.value : state.testSession.subject;
    const grade = gradeSelect ? parseInt(gradeSelect.value) : state.testSession.grade;
    const skillId = getSkillIdFromSubjectAndGrade(subject, grade);

    state.testStarted = true;
    state.surveyCompleted = false;
    if (!isInitialAssessment) {
        state.studentId = `${state.baseStudentId}_survey_${Date.now()}`;
    } else {
        state.studentId = state.baseStudentId;
    }
    state.testSession.subject = subject;
    state.testSession.grade = grade;
    state.testSession.targetSkill = skillId;
    state.testSession.currentSkill = skillId;
    state.studentProgress.activeSkill = skillId;
    resetTestStage();
    setQuestionVisibility(true);
    setSurveyResultVisibility(false);
    updateTestStageUI();
    if (!isInitialAssessment) {
        await createCleanSurveySession(grade);
    }
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
    const workspace = document.querySelector(".student-workspace");
    if (questionCard) questionCard.style.display = isVisible ? "block" : "none";
    if (progressCard) progressCard.style.display = isVisible ? "flex" : "none";
    if (workspace) {
        workspace.classList.toggle("is-testing", isVisible);
        workspace.classList.toggle("is-waiting", !isVisible);
    }
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

function resolveActiveLearningSkillId() {
    return state.currentQuestion?.skill_id || state.testSession.currentSkill || state.studentProgress.activeSkill || state.testSession.targetSkill || "MATH_G7";
}

function resolveActiveQuestionId() {
    if (state.currentQuestion?.id) return state.currentQuestion.id;
    const activeSkill = resolveActiveLearningSkillId();
    return OFFLINE_MOCK_QUESTIONS[activeSkill]?.id || OFFLINE_MOCK_QUESTIONS.MATH_G7.id;
}

function getSkillDisplayName(skillId = resolveActiveLearningSkillId()) {
    return state.knowledgeGraph?.[skillId]?.name || KNOWLEDGE_GRAPH_LOCAL_NAMES?.[skillId] || skillId;
}

function getOfflinePersonalReviewSteps(skillId = resolveActiveLearningSkillId()) {
    const skillName = getSkillDisplayName(skillId);
    const prereqs = state.knowledgeGraph?.[skillId]?.prerequisites || [];
    const firstPrereq = prereqs[0];
    const baseSkill = firstPrereq ? getSkillDisplayName(firstPrereq) : "kiến thức nền gần nhất";
    return [
        {
            skill_name: baseSkill,
            action: "Làm 3 câu mức nhận biết để xác nhận em có hổng nền hay không.",
            success_signal: "Đúng ít nhất 2/3 câu và giải thích được cách làm."
        },
        {
            skill_name: skillName,
            action: "Luyện 5 câu thông hiểu, mỗi câu phải nói rõ bước đổi dấu hoặc quy đồng.",
            success_signal: "Đạt 80% và không lặp lại cùng một lỗi sai."
        },
        {
            skill_name: skillName,
            action: "Làm 1 câu vận dụng ngắn để kiểm tra em đã nối được kiến thức nền với bài hiện tại.",
            success_signal: "Hoàn thành trong 4 phút, có lời giải từng bước."
        }
    ];
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
            state.tutorChatHistory = []; // Clear chat history
            clearChatUIs();
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
        short_answer: "Trả lời ngắn",
        essay: "Tự luận AI"
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

function buildEssayPrompt(question) {
    return `${question.text}\n\nTự luận AI: Hãy viết cách làm hoặc giải thích vì sao em chọn đáp án. AI sẽ đọc lập luận, phát hiện lỗi gốc và tạo gói ôn cá nhân hóa.`;
}

function renderQuestionVisual(question) {
    const visualBox = document.getElementById("question-visual-box");
    if (!visualBox) return;

    const visual = getQuestionVisualMarkup(question);
    visualBox.innerHTML = visual;
    visualBox.style.display = visual ? "block" : "none";
}

function clearChatUIs() {
    const mainChat = document.getElementById("chat-history-box");
    if (mainChat) mainChat.innerHTML = "";
    
    const mascotChat = document.getElementById("mascot-chat-history");
    if (mascotChat) mascotChat.innerHTML = "";
    
    const mascotComment = document.getElementById("mascot-comment");
    if (mascotComment) mascotComment.textContent = "Bạn cần giúp gì ở câu này?";
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
    } else if (state.testSession.stage === "short_answer" || state.testSession.stage === "essay") {
        const isEssay = state.testSession.stage === "essay";
        document.getElementById("question-text").textContent = isEssay ? buildEssayPrompt(question) : buildShortAnswerPrompt(question);
        textInputContainer.style.display = "block";
        if (textInput) {
            textInput.focus();
            textInput.placeholder = isEssay
                ? "Viết lời giải hoặc cách nghĩ của em. Ví dụ: Em quy đồng mẫu số rồi mới cộng tử số..."
                : "Nhập đáp án, ví dụ: -1/6, 1.25, <, >, =";
            textInput.classList.toggle("essay-answer-input", isEssay);
            textInput.oninput = handleShortAnswerInput;
            textInput.onkeydown = (e) => {
                if (isEssay && (e.metaKey || e.ctrlKey) && e.key === "Enter" && state.selectedOption && !state.isSubmitting) submitAnswer();
                if (!isEssay && e.key === "Enter" && state.selectedOption && !state.isSubmitting) submitAnswer();
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

    if (state.testSession.stage === "essay") {
        return "__ESSAY_AI__";
    }

    return state.selectedOption;
}

function updateTestStageUI() {
    const stageOrder = ["multiple_choice", "true_false", "short_answer", "essay"];
    document.querySelectorAll(".test-stage-pill").forEach(pill => {
        const stage = pill.getAttribute("data-stage");
        const stageIndex = stageOrder.indexOf(stage);
        pill.classList.toggle("active", stage === state.testSession.stage);
        pill.classList.toggle("completed", stageIndex < state.testSession.stageIndex);
    });
}

function advanceQuestionFormatIfNeeded() {
    const stageOrder = ["multiple_choice", "true_false", "short_answer", "essay"];
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
        correctAnswerText: getCorrectAnswerText(question),
        essayAnalysis: null
    });
}

function attachEssayAnalysisToLastAttempt(analysis) {
    const lastAttempt = state.testSession.attempts[state.testSession.attempts.length - 1];
    if (lastAttempt && lastAttempt.stage === "essay") {
        lastAttempt.essayAnalysis = analysis;
    }
}

function completeSurvey() {
    state.surveyCompleted = true;
    state.testStarted = false;
    state.isSubmitting = false;
    updateSubjectProgressFromSurvey(generateSurveyAnalysis());
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
        short_answer: "Trả lời ngắn",
        essay: "Tự luận AI"
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

function getEssayAnalysisAttempt() {
    return [...state.testSession.attempts].reverse().find(attempt => attempt.stage === "essay" && attempt.essayAnalysis) || null;
}

function renderEssayAnalysisEvidence() {
    const attempt = getEssayAnalysisAttempt();
    if (!attempt) return "";

    const analysis = attempt.essayAnalysis || {};
    const misconception = analysis.misconception || {};
    const measurement = analysis.measurement || {};
    const pack = Array.isArray(analysis.remediation_pack) ? analysis.remediation_pack : [];
    const confidence = Math.round(Number(misconception.confidence || 0) * 100);
    const packHtml = pack.slice(0, 3).map((step, index) => `
        <li><strong>${index + 1}. ${escapeHTML(step.title || step.type || "Bước ôn")}</strong>: ${escapeHTML(step.content || "Luyện lại kỹ năng nền.")}</li>
    `).join("");

    return `
        <div class="survey-essay-ai-card">
            <div>
                <span class="badge badge-skill"><i class="fa-solid fa-brain"></i> AI chấm tự luận</span>
                <h4>Giá trị AI nhìn thấy ngay</h4>
            </div>
            <div class="essay-ai-grid">
                <div>
                    <span>Lỗi lập luận</span>
                    <strong>${escapeHTML(misconception.detected_error || "Chưa phát hiện lỗi lớn")}</strong>
                    <p>${escapeHTML(misconception.wrong_step || "AI đọc phần tự luận để kiểm tra cách nghĩ, không chỉ đáp án cuối.")}</p>
                </div>
                <div>
                    <span>Độ tin cậy</span>
                    <strong>${confidence || 0}%</strong>
                    <p>${escapeHTML(misconception.missing_prerequisite || analysis.skill_name || "Tự động nối lỗi về kỹ năng nền cần ôn.")}</p>
                </div>
                <div>
                    <span>Đo lại</span>
                    <strong>${escapeHTML(measurement.target || "Làm đúng gói ôn")}</strong>
                    <p>${escapeHTML(analysis.why_ai_is_needed || "AI biến bài làm tự do thành can thiệp cá nhân hóa.")}</p>
                </div>
            </div>
            <ul>${packHtml || "<li>AI chưa đủ dữ liệu để tạo gói ôn. Học sinh cần viết rõ bước làm hơn.</li>"}</ul>
        </div>
    `;
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
    const essayEvidenceHtml = renderEssayAnalysisEvidence();

    resultCard.innerHTML = `
        <div class="survey-result-header">
            <div>
                <span class="badge badge-skill"><i class="fa-solid fa-wand-magic-sparkles"></i> AI phân tích khảo sát</span>
                <h3>Kết quả ${escapeHTML(state.testSession.subject)} lớp ${state.testSession.grade}</h3>
                <p>Hoàn thành ${analysis.total} câu: 6 trắc nghiệm, 2 đúng/sai, 2 trả lời ngắn, 1 tự luận AI.</p>
            </div>
            <div class="survey-score">
                <strong>${analysis.score}</strong>
                <span>/100</span>
            </div>
        </div>
        <div class="survey-stats-grid">${stageHtml}</div>
        ${essayEvidenceHtml}
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

    if (state.testSession.stage === "essay") {
        await submitEssayAnswer();
        return;
    }

    const submittedOption = resolveSubmissionOption();
    
    showLoadingOverlay("Đang chấm điểm và cập nhật chẩn đoán...");
    
    // 1. Submit through backend API
    try {
        const result = await submitSelectedAnswerToApi(submittedOption);
        if (result) {
            hideLoadingOverlay();
            
            if (result.assessment_just_completed) {
                document.getElementById("assessment-result-overlay").classList.remove("hidden");
                const btnStartLearning = document.getElementById("btn-start-learning");
                if (btnStartLearning) {
                    btnStartLearning.onclick = () => {
                        document.getElementById("assessment-result-overlay").classList.add("hidden");
                        document.body.classList.remove("assessment-mode");
                        setQuestionVisibility(false);
                        switchPortalUI("student");
                    };
                }
            }
            
            const isCorrect = result.is_correct;
            recordSurveyAttempt(isCorrect, submittedOption);
            const stageMessage = advanceQuestionFormatIfNeeded();
            const nextSkill = chooseNextSkillAfterSubmit(result, isCorrect);
            updateAnswerFeedbackUI(result, isCorrect);
            const reward = awardQuizRewards(isCorrect);
            
            if (isCorrect) {
                showToast(reward.message);
                
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

async function submitEssayAnswer() {
    const essayText = String(state.typedAnswer || "").trim();
    showLoadingOverlay("AI đang chấm tự luận và tìm lỗi gốc...");

    try {
        const response = await fetch(`/api/ai/student/${state.studentId}/analyze-work`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mode: "find_error",
                subject: state.testSession.subject || "Toán",
                grade: state.testSession.grade || 7,
                skill_id: state.currentQuestion?.skill_id || state.testSession.currentSkill || state.testSession.targetSkill,
                work_text: [
                    `Đề bài: ${state.currentQuestion?.text || ""}`,
                    `Bài tự luận của học sinh: ${essayText}`
                ].join("\n"),
                attachment_name: null
            })
        });
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || `Essay analyzer failed: ${response.status}`);
        }

        const data = await response.json();
        const analysis = data.analysis || {};
        const misconception = analysis.misconception || {};
        const confidence = Number(misconception.confidence || 0);
        const detectedError = normalizeAnswer(misconception.detected_error || "");
        const hasClearError = confidence >= 0.7 && !detectedError.includes("can them du lieu") && !detectedError.includes("chua phat hien");
        const isCorrect = !hasClearError;

        hideLoadingOverlay();
        recordSurveyAttempt(isCorrect, "__ESSAY_AI__");
        attachEssayAnalysisToLastAttempt(analysis);
        addAIDecisionLog({
            source: "Chấm tự luận AI",
            signal: misconception.detected_error || "AI đọc lập luận tự do của học sinh",
            decision: hasClearError
                ? `Tạo gói ôn để sửa lỗi: ${misconception.missing_prerequisite || "kiến thức nền"}`
                : "Cho phép chuyển sang câu vận dụng vì chưa thấy lỗi lập luận lớn.",
            measurement: analysis.measurement?.target || "Đo lại bằng 3-4 câu cùng dạng.",
            confidence
        });
        const stageMessage = advanceQuestionFormatIfNeeded();
        const reward = awardQuizRewards(isCorrect);

        document.getElementById("mascot-comment").textContent = hasClearError
            ? `AI phát hiện lỗi gốc: ${misconception.detected_error || "cần kiểm tra lại lập luận"}. Lộ trình ôn đã được cập nhật.`
            : "AI chưa phát hiện lỗi lập luận lớn. Em đã giải thích khá rõ, tiếp tục luyện câu vận dụng nhé.";
        showToast(hasClearError ? "AI đã tìm lỗi và tạo gói ôn cá nhân hóa." : reward.message);

        if (Array.isArray(analysis.remediation_pack) && analysis.remediation_pack.length) {
            renderPersonalReviewSteps(analysis.remediation_pack.map(step => ({
                skill_name: step.title || step.type,
                action: step.content,
                success_signal: analysis.measurement?.target || "Làm đúng câu đo lại mastery."
            })), analysis.summary || "AI đã tạo gói ôn từ bài tự luận.");
        }

        setTimeout(() => {
            state.isSubmitting = false;
            if (stageMessage?.message) showToast(stageMessage.message);
            if (stageMessage?.completed) {
                completeSurvey();
                return;
            }
            loadStudentQuestion(chooseNextSkillAfterSubmit(null, isCorrect));
        }, hasClearError ? 2600 : 1800);
    } catch (error) {
        console.warn("[Essay AI] Analyzer failed.", error);
        hideLoadingOverlay();
        recordSurveyAttempt(false, "__ESSAY_AI_ERROR__");
        attachEssayAnalysisToLastAttempt({
            summary: "AI chấm tự luận chưa phản hồi được trong phiên này.",
            misconception: {
                detected_error: "Chưa chấm được tự luận",
                wrong_step: "Kết nối AI bị lỗi hoặc phản hồi không hợp lệ.",
                missing_prerequisite: "Cần thử lại để lấy chẩn đoán.",
                confidence: 0
            },
            remediation_pack: [],
            measurement: {
                target: "Gửi lại bài tự luận khi AI sẵn sàng."
            },
            why_ai_is_needed: "Tự luận cần AI đọc lập luận tự do, rule engine không đủ để hiểu bước giải."
        });
        const stageMessage = advanceQuestionFormatIfNeeded();
        awardQuizRewards(false);
        document.getElementById("mascot-comment").textContent = "AI chấm tự luận đang lỗi kết nối. Hệ thống vẫn lưu bài và đánh dấu cần chấm lại.";
        showToast("AI chấm tự luận chưa hoạt động, đã lưu phần cần kiểm tra lại.");
        setTimeout(() => {
            state.isSubmitting = false;
            if (stageMessage?.completed) completeSurvey();
            else loadStudentQuestion(state.testSession.currentSkill);
        }, 2000);
    }
}

function awardQuizRewards(isCorrect) {
    const difficultyLevel = Number(state.currentQuestion?.difficulty_level || 2);
    if (!isCorrect) {
        state.answerCombo = 0;
        saveRewardState();
        updateStudentRewardsUI();
        return {
            xp: 0,
            coins: 0,
            comboBonus: 0,
            message: "Combo tạm dừng. Làm câu tiếp theo để lấy lại nhịp nhé."
        };
    }

    const baseXp = difficultyLevel >= 3 ? 100 : 50;
    const baseCoins = difficultyLevel >= 3 ? 20 : 10;
    state.answerCombo += 1;
    let comboBonus = 0;
    if (state.answerCombo > 0 && state.answerCombo % 5 === 0) {
        comboBonus = 40;
    } else if (state.answerCombo > 0 && state.answerCombo % 3 === 0) {
        comboBonus = 15;
    }

    state.xp += baseXp;
    state.coins += baseCoins + comboBonus;
    state.dailyQuest.correctAnswers += 1;
    state.dailyQuest.coinsEarned += baseCoins + comboBonus;
    if (difficultyLevel >= 3) state.dailyQuest.hardCorrectAnswers += 1;
    if (state.dailyQuest.correctAnswers === 5) state.dailyQuest.aiReviewsUnlocked += 1;

    saveRewardState();
    updateStudentRewardsUI();
    const comboText = comboBonus ? ` · combo +${comboBonus} xu` : "";
    return {
        xp: baseXp,
        coins: baseCoins,
        comboBonus,
        message: `+${baseCoins + comboBonus} xu · +${baseXp} XP${comboText}`
    };
}

// Update Student XP/Coins/Streak tags
function updateStudentRewardsUI() {
    const rewardsRow = document.getElementById("student-rewards");
    const level = getLearningLevel();
    renderQuestShopPanel();
    if (!rewardsRow) return;
    
    rewardsRow.innerHTML = `
        <span class="reward-tag streak-tag"><i class="fa-solid fa-calendar-check"></i> ${state.loginStreak} ngày liên tiếp</span>
        <span class="reward-tag xp-tag"><i class="fa-solid fa-gem"></i> Lv.${level.level} · ${state.xp.toLocaleString()} XP</span>
        <span class="reward-tag coin-tag"><i class="fa-solid fa-coins"></i> ${state.coins} Xu</span>
    `;
}

function updateLearningLevelUI() {
    const level = getLearningLevel();
    const label = document.getElementById("learning-level-label");
    const next = document.getElementById("learning-level-next");
    const fill = document.getElementById("learning-level-fill");
    if (label) label.textContent = `Level ${level.level} · ${level.title}`;
    if (next) {
        next.textContent = level.next
            ? `Còn ${level.xpNeeded.toLocaleString()} XP để mở: ${level.next.unlock}`
            : `Đã mở khóa cao nhất: ${level.unlock}`;
    }
    if (fill) fill.style.width = `${level.progress}%`;
}

function renderQuestShopPanel() {
    const questList = document.getElementById("daily-quest-list");
    const pageQuestList = document.getElementById("reward-page-quest-list");
    const shopList = document.getElementById("reward-shop-list");
    const comboLabel = document.getElementById("quest-combo-label");
    const notificationCount = document.getElementById("quest-notification-count");
    const walletTitle = document.getElementById("reward-wallet-title");
    const ticketCount = document.getElementById("reward-ticket-count");
    const xpCount = document.getElementById("reward-xp-count");
    const spinStatus = document.getElementById("reward-spin-status");
    const spinButton = document.getElementById("btn-spin-reward");
    const attendanceStreakLabel = document.getElementById("attendance-streak-label");
    const attendanceStatusLabel = document.getElementById("attendance-status-label");
    const attendanceButton = document.getElementById("btn-attendance-checkin");
    if (comboLabel) comboLabel.textContent = "Nhiệm vụ hôm nay";
    if (walletTitle) walletTitle.textContent = `${state.coins.toLocaleString()} xu khả dụng`;
    if (ticketCount) ticketCount.textContent = String(state.spinTickets);
    if (xpCount) xpCount.textContent = state.xp.toLocaleString();
    updateLearningLevelUI();
    if (spinStatus) spinStatus.textContent = state.spinTickets > 0 ? `${state.spinTickets} lượt quay sẵn sàng` : "Điểm danh để nhận lượt quay";
    if (spinButton) {
        spinButton.disabled = state.spinTickets <= 0;
        spinButton.innerHTML = state.spinTickets > 0
            ? '<i class="fa-solid fa-play"></i> Quay ngay'
            : '<i class="fa-solid fa-lock"></i> Hết lượt quay';
    }
    if (attendanceStreakLabel) attendanceStreakLabel.textContent = `${state.loginStreak} ngày liên tiếp`;
    const today = getTodayKey();
    const checkedToday = state.attendance.checkedDates.includes(today);
    const checkInTickets = getTodayCheckInTickets();
    if (attendanceStatusLabel) {
        attendanceStatusLabel.textContent = checkedToday
            ? "Hôm nay đã điểm danh"
            : `Hôm nay nhận ${checkInTickets} lượt quay`;
    }
    if (attendanceButton) {
        attendanceButton.disabled = checkedToday;
        attendanceButton.innerHTML = checkedToday
            ? '<i class="fa-solid fa-circle-check"></i> Đã điểm danh'
            : '<i class="fa-solid fa-calendar-plus"></i> Điểm danh';
    }
    renderAttendanceCalendar();

    const quests = [
        {
            id: "correct5",
            label: "Đúng 5 câu để mở bài ôn AI",
            value: Math.min(state.dailyQuest.correctAnswers, 5),
            target: 5,
            icon: "fa-solid fa-bullseye"
        },
        {
            id: "hard2",
            label: "Đúng 2 câu khó",
            value: Math.min(state.dailyQuest.hardCorrectAnswers, 2),
            target: 2,
            icon: "fa-solid fa-mountain"
        },
        {
            id: "coins100",
            label: "Kiếm 100 xu hôm nay",
            value: Math.min(state.dailyQuest.coinsEarned, 100),
            target: 100,
            icon: "fa-solid fa-coins"
        }
    ];
    const completedQuests = quests.filter(quest => quest.value >= quest.target).length;
    if (notificationCount) notificationCount.textContent = String(completedQuests);
    const questsHtml = quests.map(quest => {
        const percent = Math.round((quest.value / quest.target) * 100);
        const isComplete = quest.value >= quest.target;
        const isClaimed = state.dailyQuest.claimed.includes(quest.id);
        const actionLabel = isClaimed ? "Đã nhận" : isComplete ? "Nhận thưởng" : "Đang làm";
        return `
            <div class="daily-quest-item">
                <div class="daily-quest-copy">
                    <i class="${quest.icon}"></i>
                    <span>${escapeHTML(quest.label)}</span>
                    <strong>${quest.value}/${quest.target}</strong>
                </div>
                <div class="daily-quest-track"><span style="width: ${percent}%"></span></div>
                <button class="quest-claim-btn" data-quest-id="${quest.id}" ${isComplete && !isClaimed ? "" : "disabled"}>${actionLabel}</button>
            </div>
        `;
    }).join("");
    if (questList) questList.innerHTML = questsHtml;
    if (pageQuestList) pageQuestList.innerHTML = questsHtml;

    if (shopList) {
        shopList.innerHTML = REWARD_SHOP_ITEMS.map(item => {
            const redeemedCount = state.redeemedRewards.filter(id => id === item.id).length;
            const levelLocked = !canUseLevel(item.minLevel || 1);
            const disabled = state.coins < item.cost || levelLocked;
            const lockText = levelLocked ? ` · cần Lv.${item.minLevel}` : "";
            return `
                <button class="reward-shop-item tone-${item.tone || "blue"}" data-reward-id="${item.id}" ${disabled ? "disabled" : ""}>
                    <i class="${item.icon}"></i>
                    <span>
                        <strong>${escapeHTML(item.title)}</strong>
                        <small>${escapeHTML(item.description)}${lockText}</small>
                    </span>
                    <em>${item.cost} xu${redeemedCount ? ` · x${redeemedCount}` : ""}</em>
                </button>
            `;
        }).join("");
    }
    renderRewardWheelPrizes();
    renderRewardHistory();
}

function getTodayKey(offsetDays = 0) {
    const date = new Date();
    date.setDate(date.getDate() + offsetDays);
    return date.toISOString().slice(0, 10);
}

function getLocalDateFromKey(dateKey) {
    const [year, month, day] = String(dateKey).split("-").map(Number);
    return new Date(year, month - 1, day);
}

function getVietnameseWeekdayLabel(date) {
    const labels = ["Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];
    return labels[date.getDay()] || "Hôm nay";
}

function getShortDateLabel(date) {
    return `${date.getDate()}/${date.getMonth() + 1}`;
}

function renderAttendanceCalendar() {
    const grid = document.getElementById("attendance-calendar-grid");
    if (!grid) return;
    const todayKey = getTodayKey();
    grid.innerHTML = Array.from({ length: 7 }, (_, index) => {
        const dateKey = getTodayKey(index - 6);
        const date = getLocalDateFromKey(dateKey);
        const isWeekend = [0, 6].includes(date.getDay());
        const checked = state.attendance.checkedDates.includes(dateKey);
        const isToday = dateKey === todayKey;
        const rewardText = isWeekend ? "2 lượt" : "1 lượt";
        return `
            <div class="attendance-day ${checked ? "checked" : ""} ${isToday ? "today" : ""}">
                <strong>${getVietnameseWeekdayLabel(date)}</strong>
                <small>${getShortDateLabel(date)}</small>
                <span>${checked ? "Đã học" : rewardText}</span>
            </div>
        `;
    }).join("");
}

function getTodayCheckInTickets() {
    const day = new Date().getDay();
    return [0, 6].includes(day) ? 2 : 1;
}

function checkInToday() {
    const today = getTodayKey();
    if (state.attendance.checkedDates.includes(today)) {
        showToast("Hôm nay đã điểm danh rồi.");
        return;
    }
    state.attendance.checkedDates.push(today);
    state.attendance.lastCheckInDate = today;
    state.loginStreak += 1;
    const earnedTickets = getTodayCheckInTickets();
    state.spinTickets += earnedTickets;
    state.xp += 30;
    saveRewardState();
    updateStudentRewardsUI();
    renderStudentProfile();
    setRewardFeedback(`Điểm danh thành công: +${earnedTickets} lượt quay, +30 XP.`);
    showToast(`Điểm danh thành công: +${earnedTickets} lượt quay.`);
}

function renderRewardWheelPrizes() {
    const prizeGrid = document.getElementById("reward-wheel-prizes");
    if (!prizeGrid) return;
    prizeGrid.innerHTML = REWARD_WHEEL_ITEMS.map(item => `
        <div class="wheel-prize-chip">
            <i class="${item.icon}" style="background:${item.color}"></i>
            <span>${escapeHTML(item.label)}</span>
        </div>
    `).join("");
}

function renderRewardHistory() {
    const historyList = document.getElementById("reward-history-list");
    if (!historyList) return;
    const recent = state.rewardHistory.slice(0, 5);
    if (!recent.length) {
        historyList.innerHTML = '<p>Chưa có quà nào. Điểm danh rồi quay thử nhé.</p>';
        return;
    }
    historyList.innerHTML = recent.map(item => `
        <div class="reward-history-item">
            <i class="${item.icon}"></i>
            <span>${escapeHTML(item.label)}</span>
            <small>${escapeHTML(item.time)}</small>
        </div>
    `).join("");
}

function spinRewardWheel() {
    if (state.spinTickets <= 0) {
        showToast("Chưa có lượt quay. Điểm danh để nhận lượt quay nhé.");
        return;
    }
    const wheel = document.getElementById("reward-wheel");
    const button = document.getElementById("btn-spin-reward");
    if (!wheel || !button || button.dataset.spinning === "true") return;

    state.spinTickets -= 1;
    button.dataset.spinning = "true";
    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang quay';

    const prizeIndex = Math.floor(Math.random() * REWARD_WHEEL_ITEMS.length);
    const prize = REWARD_WHEEL_ITEMS[prizeIndex];
    const segmentAngle = 360 / REWARD_WHEEL_ITEMS.length;
    const targetAngle = 360 * 5 + (360 - prizeIndex * segmentAngle) - segmentAngle / 2;
    wheel.style.transform = `rotate(${targetAngle}deg)`;

    setTimeout(() => {
        const resultLabel = prize.apply();
        state.rewardHistory.unshift({
            id: prize.id,
            icon: prize.icon,
            label: resultLabel,
            time: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })
        });
        state.rewardHistory = state.rewardHistory.slice(0, 12);
        saveRewardState();
        updateStudentRewardsUI();
        renderStudentProfile();
        setRewardFeedback(`Vòng quay trúng ${resultLabel}.`);
        showToast(`Bạn nhận được ${resultLabel}.`);
        button.dataset.spinning = "false";
    }, 1800);
}

function initQuestNotification() {
    const wrapper = document.getElementById("quest-notification");
    const button = document.getElementById("btn-quest-toggle");
    if (!wrapper || !button) return;
    button.addEventListener("click", event => {
        event.stopPropagation();
        const isOpen = wrapper.classList.toggle("open");
        button.setAttribute("aria-expanded", String(isOpen));
    });
    document.addEventListener("click", event => {
        if (wrapper.contains(event.target)) return;
        wrapper.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
    });
}

function setRewardFeedback(message) {
    const feedback = document.getElementById("reward-feedback");
    const wheelFeedback = document.getElementById("reward-wheel-feedback");
    if (feedback) feedback.textContent = message;
    if (wheelFeedback) wheelFeedback.textContent = message;
}

function claimDailyQuestReward(questId) {
    const reward = DAILY_QUEST_REWARDS[questId];
    if (!reward) return;
    if (state.dailyQuest.claimed.includes(questId)) {
        showToast("Nhiệm vụ này đã nhận thưởng rồi.");
        return;
    }

    const questReady = {
        correct5: state.dailyQuest.correctAnswers >= 5,
        hard2: state.dailyQuest.hardCorrectAnswers >= 2,
        coins100: state.dailyQuest.coinsEarned >= 100
    };
    if (!questReady[questId]) {
        showToast("Nhiệm vụ chưa hoàn thành.");
        return;
    }

    state.dailyQuest.claimed.push(questId);
    state.coins += reward.coins;
    state.xp += reward.xp;
    state.spinTickets += reward.tickets;
    state.rewardHistory.unshift({
        id: `quest_${questId}`,
        icon: "fa-solid fa-gift",
        label: `${reward.label}: +${reward.coins} xu, +${reward.xp} XP${reward.tickets ? `, +${reward.tickets} lượt quay` : ""}`,
        time: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })
    });
    state.rewardHistory = state.rewardHistory.slice(0, 12);
    saveRewardState();
    updateStudentRewardsUI();
    renderStudentProfile();
    setRewardFeedback(`Đã nhận thưởng ${reward.label}.`);
    showToast(`Nhận thưởng: +${reward.coins} xu, +${reward.xp} XP${reward.tickets ? `, +${reward.tickets} lượt quay` : ""}.`);
}

function openAITutorTab(action = "learning-path") {
    const mascotTab = document.querySelector('[data-toolbox-tab="mascot"]');
    if (mascotTab) mascotTab.click();
    const aiButton = document.querySelector(`[data-ai-action="${action}"]`);
    if (aiButton) aiButton.click();
}

function redeemRewardItem(rewardId) {
    const item = REWARD_SHOP_ITEMS.find(entry => entry.id === rewardId);
    if (!item) return;
    if (!canUseLevel(item.minLevel || 1)) {
        setRewardFeedback(`${item.title} cần Level ${item.minLevel}. Hãy lấy thêm XP bằng quiz hoặc điểm danh.`);
        showToast(`Cần Level ${item.minLevel} để đổi món này.`);
        return;
    }
    if (state.coins < item.cost) {
        setRewardFeedback(`Cần thêm ${item.cost - state.coins} xu để đổi ${item.title}.`);
        showToast("Chưa đủ xu để đổi phần thưởng này.");
        return;
    }

    state.coins -= item.cost;
    state.redeemedRewards.push(item.id);

    if (item.id === "extra_hint") {
        const hintButton = document.getElementById("btn-show-hint");
        if (hintButton) hintButton.click();
        setRewardFeedback("Đã đổi gợi ý thêm cho câu hiện tại.");
    } else if (item.id === "ai_review") {
        state.dailyQuest.aiReviewsUnlocked += 1;
        buildPersonalAIReview({ silent: true });
        setRewardFeedback("Đã mở bài ôn AI cá nhân hóa trong khung trợ lý.");
    } else if (item.id === "focus_badge") {
        if (!state.earnedBadges.includes("Vượt ải kiến thức")) state.earnedBadges.push("Vượt ải kiến thức");
        setRewardFeedback("Đã gắn huy hiệu Vượt ải kiến thức vào hồ sơ.");
    } else if (item.id === "teacher_bonus") {
        state.teacherBonusTickets.unshift({
            title: "Phiếu điểm thưởng",
            status: "Chờ giáo viên duyệt",
            createdAt: new Date().toLocaleDateString("vi-VN")
        });
        state.teacherBonusTickets = state.teacherBonusTickets.slice(0, 5);
        setRewardFeedback("Đã tạo phiếu điểm thưởng trong hồ sơ, trạng thái chờ giáo viên duyệt.");
    } else if (item.id === "lucky_spin") {
        state.spinTickets += 1;
        setRewardFeedback("Đã mua thêm 1 lượt quay may mắn.");
    } else if (item.id === "avatar_frame") {
        const avatar = document.getElementById("user-avatar-container");
        if (avatar) avatar.classList.add("avatar-prize-frame");
        setRewardFeedback("Đã mở khung avatar vui cho Emma.");
    }

    saveRewardState();
    updateStudentRewardsUI();
    renderStudentProfile();
    showToast(`Đã đổi ${item.title}.`);
}

function initRewardShop() {
    const shopList = document.getElementById("reward-shop-list");
    if (shopList) {
        shopList.addEventListener("click", event => {
            const button = event.target.closest("[data-reward-id]");
            if (!button) return;
            redeemRewardItem(button.getAttribute("data-reward-id"));
        });
    }
    document.addEventListener("click", event => {
        const claimButton = event.target.closest("[data-quest-id]");
        if (!claimButton) return;
        claimDailyQuestReward(claimButton.getAttribute("data-quest-id"));
    });
    const attendanceButton = document.getElementById("btn-attendance-checkin");
    if (attendanceButton) attendanceButton.addEventListener("click", checkInToday);
    const spinButton = document.getElementById("btn-spin-reward");
    if (spinButton) spinButton.addEventListener("click", spinRewardWheel);
    renderQuestShopPanel();
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
    
    const svgWidth = 620;
    const svgHeight = 430;
    let svgHtml = `<svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;
    
    const nodes = [];
    const edges = [];

    const getNodeX = (count, index) => {
        if (count <= 1) return 310;
        const start = count === 2 ? 210 : 120;
        const step = count === 2 ? 200 : 190;
        return start + index * step;
    };

    const compactLabel = (name) => {
        const clean = String(name || "")
            .replace(/\([^)]*\)/g, "")
            .replace(/[,;:]/g, "")
            .trim();
        const words = clean.split(/\s+/).filter(Boolean);
        return words.slice(0, 4);
    };

    const renderNodeText = (x, y, labelLines) => labelLines.map((line, index) => (
        `<tspan x="${x}" y="${y + 5 + index * 17}">${escapeHTML(line)}</tspan>`
    )).join("");
    
    // Base prerequisite knowledge sits above the current skill.
    prereqs.slice(0, 3).forEach((prereqId, index) => {
        if (graph[prereqId]) {
            const x = getNodeX(Math.min(prereqs.length, 3), index);
            nodes.push({
                id: prereqId,
                x,
                y: 88,
                labelLines: compactLabel(graph[prereqId].name),
                fullName: graph[prereqId].name,
                color: '#4CAF50',
                status: 'completed'
            });
            edges.push({ fromX: x, fromY: 130, toX: 310, toY: 182 });
        }
    });

    // Current class skill is the unstable focus and stays in the middle.
    nodes.push({
        id: activeSkillId,
        x: 310,
        y: 220,
        labelLines: compactLabel(activeSkill.name),
        fullName: activeSkill.name,
        color: '#FCD075',
        status: 'unstable'
    });
    
    // Harder/newer dependent knowledge sits below and remains grey until unlocked.
    nextSkills.slice(0, 3).forEach((nextId, index) => {
        if (graph[nextId]) {
            const x = getNodeX(Math.min(nextSkills.length, 3), index);
            nodes.push({
                id: nextId,
                x,
                y: 350,
                labelLines: compactLabel(graph[nextId].name),
                fullName: graph[nextId].name,
                color: '#cbd5e1',
                status: 'locked'
            });
            edges.push({ fromX: 310, fromY: 262, toX: x, toY: 308 });
        }
    });
    
    // Render links
    edges.forEach(e => {
        svgHtml += `<line x1="${e.fromX}" y1="${e.fromY}" x2="${e.toX}" y2="${e.toY}" stroke="#0f172a" stroke-width="4" stroke-linecap="round" />`;
    });
    
    // Render nodes
    nodes.forEach(n => {
        svgHtml += `
            <g class="web-node" style="cursor: pointer;" data-full-name="${escapeHTML(n.fullName)}">
                <circle cx="${n.x}" cy="${n.y}" r="48" fill="${n.color}" stroke="#000000" stroke-width="4" />
                <text font-family="Poppins" font-size="13.5" font-weight="900" text-anchor="middle" fill="#000000">${renderNodeText(n.x, n.y - (n.labelLines.length > 1 ? 16 : 0), n.labelLines)}</text>
            </g>
        `;
    });
    
    svgHtml += `</svg>`;
    
    const legendHtml = `
        <div style="display: flex; justify-content: space-around; gap: 0.55rem; flex-wrap: wrap; font-size: 0.72rem; font-family: Poppins; font-weight: 800; border-top: 2px dashed #000; padding-top: 0.7rem; margin-top: 0.65rem; width: 100%;">
            <div><span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:#4CAF50; border:1.5px solid #000; margin-right:4px; vertical-align:middle;"></span>Đã hoàn thành</div>
            <div><span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:#FCD075; border:1.5px solid #000; margin-right:4px; vertical-align:middle;"></span>Chưa ổn định</div>
            <div><span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:#cbd5e1; border:1.5px solid #000; margin-right:4px; vertical-align:middle;"></span>Chưa đạt</div>
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

function summarizeTopGap(groups = []) {
    if (!groups.length) return { title: "Chưa đủ dữ liệu", count: 0, skillId: "" };
    const sorted = [...groups].sort((a, b) => Number(b.count || 0) - Number(a.count || 0));
    const top = sorted[0];
    return {
        title: KNOWLEDGE_GRAPH_LOCAL_NAMES[top.skill_id] || top.title || top.skill_id || "Nhóm cần can thiệp",
        count: Number(top.count || 0),
        skillId: top.skill_id || ""
    };
}

function updateTeacherCommandCenter(data) {
    const priorityList = data.priority_list || [];
    const groups = data.groups || [];
    const topGap = summarizeTopGap(groups);
    const riskCount = priorityList.length || state.mockStudents.length;
    const savedMinutes = Math.max(45, Math.min(150, groups.length * 30 + riskCount * 6));

    const riskStudents = document.getElementById("teacher-risk-students");
    const gapSummary = document.getElementById("teacher-gap-group-summary");
    const topGapSkill = document.getElementById("teacher-top-gap-skill");
    const timeSaved = document.getElementById("teacher-time-saved");
    const teachingNextStep = document.getElementById("teaching-next-step");
    const assignmentNextStep = document.getElementById("assignment-next-step");
    const progressNextStep = document.getElementById("progress-next-step");

    if (riskStudents) riskStudents.textContent = `${riskCount} học sinh`;
    if (gapSummary) gapSummary.textContent = data.metrics.gap_groups_count || `${groups.length} nhóm`;
    if (topGapSkill) topGapSkill.textContent = topGap.title;
    if (timeSaved) timeSaved.textContent = `${savedMinutes} phút/tuần`;
    if (teachingNextStep) teachingNextStep.textContent = `Ưu tiên mini-lesson cho ${topGap.title}, nhóm ${topGap.count || "đang xác định"} học sinh.`;
    if (assignmentNextStep) assignmentNextStep.textContent = topGap.skillId
        ? `Giao bài luyện prerequisite ${topGap.skillId} cho nhóm này sau khi dạy lại.`
        : "Chờ thêm dữ liệu làm bài để giao đúng prerequisite.";
    if (progressNextStep) progressNextStep.textContent = "Sau can thiệp, theo dõi mastery và số câu sai liên tiếp trong dashboard realtime.";

    renderInterventionQueue(priorityList, groups);
}

function renderInterventionQueue(priorityList = [], groups = []) {
    const container = document.getElementById("teacher-intervention-queue");
    if (!container) return;
    container.replaceChildren();

    const topGap = summarizeTopGap(groups);
    const queueItems = [];

    if (topGap.skillId) {
        queueItems.push({
            icon: "fa-solid fa-person-chalkboard",
            title: `Dạy lại: ${topGap.title}`,
            meta: `${topGap.count} học sinh cùng lỗ hổng`,
            action: "Tạo giáo án",
            handler: () => triggerLessonPlanForSkill(topGap.skillId, topGap.title, topGap.members)
        });
    }

    priorityList.slice(0, 3).forEach((student, index) => {
        queueItems.push({
            icon: index === 0 ? "fa-solid fa-triangle-exclamation" : "fa-solid fa-user-clock",
            title: student.name,
            meta: `${student.n_failed} câu sai, kẹt ${student.t_stuck} phút, PS ${student.priority_score}`,
            action: "Xem lý do",
            handler: () => openDiagnosticInspector(student.id)
        });
    });

    if (!queueItems.length) {
        queueItems.push({
            icon: "fa-solid fa-circle-check",
            title: "Lớp đang ổn định",
            meta: "Chưa có nhóm cần can thiệp khẩn cấp.",
            action: "Xem tiến trình",
            handler: () => showToast("Hãy theo dõi biểu đồ tiến trình để phát hiện thay đổi mới.")
        });
    }

    queueItems.forEach(item => {
        const card = document.createElement("div");
        card.className = "intervention-queue-item";
        card.innerHTML = `
            <div class="queue-icon"><i class="${item.icon}"></i></div>
            <div class="queue-copy">
                <strong>${escapeHTML(item.title)}</strong>
                <span>${escapeHTML(item.meta)}</span>
            </div>
            <button class="btn btn-hint-outline btn-sm" type="button">${escapeHTML(item.action)}</button>
        `;
        card.querySelector("button").addEventListener("click", item.handler);
        container.appendChild(card);
    });
}

function initTeacherClassSwitcher() {
    const select = document.getElementById("teacher-class-select");
    const nameEl = document.getElementById("teacher-active-class-name");
    const descEl = document.getElementById("teacher-active-class-desc");
    if (!select || !nameEl || !descEl) return;

    select.addEventListener("change", () => {
        const option = select.selectedOptions[0];
        const className = option?.dataset.name || "Lớp đang quản lý";
        const classCode = option?.dataset.code || option?.value || "";
        const meta = option?.dataset.meta || "Đang tải dữ liệu lớp";
        nameEl.textContent = className;
        descEl.innerHTML = `Mã lớp: <strong>${escapeHTML(classCode)}</strong> · ${escapeHTML(meta)}`;
        showToast(`Đã chuyển sang lớp ${classCode}. Dữ liệu demo đang dùng cùng API mẫu.`);
    });
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
    const dashboardPayload = data.payload || data;
    return {
        metrics: dashboardPayload.metrics || {},
        groups: Array.isArray(dashboardPayload.groups) ? dashboardPayload.groups : [],
        priority_list: Array.isArray(dashboardPayload.priority_list) ? dashboardPayload.priority_list : [],
        class_progress: Array.isArray(dashboardPayload.class_progress) && dashboardPayload.class_progress.length
            ? dashboardPayload.class_progress
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
    updateTeacherCommandCenter(data);
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
            <div class="group-plan-summary">
                <span><i class="fa-solid fa-person-chalkboard"></i> Dạy lại 15 phút</span>
                <span><i class="fa-solid fa-file-circle-plus"></i> Giao bài prerequisite</span>
                <span><i class="fa-solid fa-chart-line"></i> Đo mastery sau can thiệp</span>
            </div>
            <div class="group-action">
                <button class="btn btn-hint-outline btn-sm" data-skill-id="${escapeHTML(grp.skill_id)}" data-title="${escapeHTML(grp.title || grp.skill_id)}">
                    <i class="fa-solid fa-share-nodes"></i> Xem giáo án bổ trợ
                </button>
                <button class="btn btn-secondary-memphis btn-sm" data-assign-skill="${escapeHTML(grp.skill_id)}">
                    <i class="fa-solid fa-file-circle-plus"></i> Giao bài
                </button>
            </div>
        `;
        const lessonBtn = card.querySelector("button[data-skill-id]");
        lessonBtn.addEventListener("click", () => triggerLessonPlanForSkill(grp.skill_id, grp.title, grp.members));
        const assignBtn = card.querySelector("button[data-assign-skill]");
        assignBtn.addEventListener("click", () => showToast(`Đã tạo gói bài luyện cho nhóm ${KNOWLEDGE_GRAPH_LOCAL_NAMES[grp.skill_id] || grp.skill_id}.`));
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
                <button class="btn btn-hint-outline btn-sm" data-ai-path-student-id="${escapeHTML(std.id)}" data-ai-path-skill="${escapeHTML(std.current_skill)}">
                    <i class="fa-solid fa-route"></i> Lộ trình AI
                </button>
            </td>
        `;
        row.querySelector("button[data-student-id]").addEventListener("click", () => openDiagnosticInspector(std.id));
        row.querySelector("button[data-ai-path-student-id]").addEventListener("click", () => openTeacherAILearningPath(std.id, std.current_skill_id));
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
    const wsUrl = `${protocol}://${window.location.host}/ws/teacher/dashboard`;
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

function triggerLessonPlanForSkill(skillId, title, groupMembers = null) {
    let contextStr = "Nhóm học sinh có xác suất thành thạo dưới 0.50.";
    if (groupMembers && groupMembers.length > 0) {
        contextStr = "Danh sách học sinh cần hỗ trợ trong nhóm: " + groupMembers.join(", ") + ".";
    }
    generateAILessonPlan(title || skillId, skillId, contextStr);
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
    state.tutorChatHistory = []; // Clear chat history
    clearChatUIs();
    state.selectedOption = null;
    state.typedAnswer = "";
    
    renderCurrentQuestion(question);
    
    document.getElementById("hint-content-box").style.display = "none";
    document.getElementById("btn-submit-answer").setAttribute("disabled", "true");
    document.getElementById("mascot-comment").textContent = "Hãy đọc kỹ đề bài nhé! Tôi tin bạn làm được!";
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
        const reward = awardQuizRewards(true);
        if (selectedBtn) selectedBtn.classList.add("correct-feedback");
        document.getElementById("mascot-comment").textContent = isShortAnswer ? buildShortAnswerFeedback(true) : "Tuyệt vời! Bạn đã làm hoàn toàn chính xác!";
        showToast(`Trả lời đúng! ${reward.message}`);
        
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
        awardQuizRewards(false);
        if (selectedBtn) selectedBtn.classList.add("error-feedback");
        document.getElementById("mascot-comment").textContent = isShortAnswer ? buildShortAnswerFeedback(false) : "Chưa đúng rồi. Bạn thử suy nghĩ thêm một chút xem?";
        showToast("Chưa chính xác!");
        
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
            <div class="group-plan-summary">
                <span><i class="fa-solid fa-person-chalkboard"></i> Dạy lại 15 phút</span>
                <span><i class="fa-solid fa-file-circle-plus"></i> Giao bài prerequisite</span>
                <span><i class="fa-solid fa-chart-line"></i> Đo mastery sau can thiệp</span>
            </div>
            <div class="group-action">
                <button class="btn btn-hint-outline btn-sm" onclick="triggerLessonPlanForSkill('${grp.skill_id}', '${grp.title}', ${JSON.stringify(grp.members).replace(/"/g, '&quot;')})"><i class="fa-solid fa-share-nodes"></i> Xem giáo án</button>
                <button class="btn btn-secondary-memphis btn-sm" onclick="showToast('Đã tạo gói bài luyện cho ${grp.title}.')"><i class="fa-solid fa-file-circle-plus"></i> Giao bài</button>
            </div>
        `;
        groupsGrid.appendChild(card);
    });

    updateTeacherCommandCenter({
        metrics: { gap_groups_count: `${mockGroups.length} nhóm` },
        groups: mockGroups,
        priority_list: state.mockStudents.map((student, index) => ({
            id: student.id,
            name: student.name,
            n_failed: student.nFailed,
            t_stuck: student.tStuck,
            priority_score: (1.5 + index * 0.1).toFixed(2),
        }))
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
    const workInput = document.getElementById("ai-work-input");
    const runTaskBtn = document.getElementById("btn-run-ai-task");
    const imageInput = document.getElementById("ai-image-input");
    const imageLabel = document.getElementById("ai-image-label");
    const chatHistory = document.getElementById("chat-history-box");
    const aiStatusPill = document.getElementById("ai-status-pill");
    let selectedAIMode = "explain";

    const aiModeConfig = {
        explain: {
            label: "Giải thích",
            prompt: "Hãy giải thích nội dung này theo cách dễ hiểu cho học sinh, có ví dụ ngắn nếu cần.",
            placeholder: "Dán phần em chưa hiểu, ví dụ: Vì sao 3/4 và 5/6 phải quy đồng mẫu số?"
        },
        find_error: {
            label: "Tìm lỗi sai",
            prompt: "Hãy tìm lỗi sai trong bài làm của học sinh. Chỉ ra bước sai, vì sao sai, và gợi ý sửa từng bước.",
            placeholder: "Dán bài làm của em, ví dụ: 1/2 + 2/3 = 3/5 vì cộng tử với tử, mẫu với mẫu."
        },
        similar_question: {
            label: "Tạo câu hỏi tương tự",
            prompt: "Hãy tạo một câu hỏi tương tự dựa trên nội dung học sinh gửi. Không tự tạo thêm nếu dữ liệu chưa đủ; nếu thiếu, hãy hỏi lại.",
            placeholder: "Dán câu mẫu để AI tạo một câu tương tự cùng kỹ năng và độ khó."
        },
        step_hint: {
            label: "Gợi ý từng bước",
            prompt: "Hãy đưa gợi ý Socratic từng bước, không tiết lộ đáp án cuối cùng ngay.",
            placeholder: "Dán câu em đang làm để AI gợi ý bước tiếp theo."
        },
        summarize: {
            label: "Tóm tắt kiến thức",
            prompt: "Hãy tóm tắt kiến thức chính thành các ý ngắn, dễ nhớ, phù hợp học sinh cấp 1-2.",
            placeholder: "Dán đoạn lý thuyết hoặc chủ đề em muốn tóm tắt."
        }
    };

    async function updateAIStatusBadge() {
        if (!aiStatusPill) return;
        try {
            const response = await fetch("/api/ai/status");
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const status = await response.json();
            aiStatusPill.className = `realtime-status ${status.configured ? "connected" : "polling"}`;
            aiStatusPill.textContent = status.configured ? `FPT AI online · ${status.model || "model"}` : "AI chưa cấu hình · dùng offline";
        } catch (error) {
            aiStatusPill.className = "realtime-status disconnected";
            aiStatusPill.textContent = "Không kết nối AI";
        }
    }

    function buildOfflineTutorReply(msg) {
        let replyText = "Tôi là trợ lý học tập PorcusAI. Đang phân tích câu hỏi của bạn...";
        if (msg.toLowerCase().includes("bcnn")) {
            replyText = "Bội chung nhỏ nhất (BCNN) của hai số là số tự nhiên nhỏ nhất khác 0 chia hết cho cả hai số đó. Ví dụ: BCNN(6, 8) = 24.";
        } else if (msg.toLowerCase().includes("quy đồng")) {
            replyText = "Để quy đồng mẫu số, ta tìm BCNN của các mẫu số làm mẫu chung, rồi nhân cả tử và mẫu với nhân tử phụ tương ứng.";
        } else if (msg.toLowerCase().includes("số hữu tỉ")) {
            replyText = "Số hữu tỉ là số viết được dưới dạng phân số a/b (a, b thuộc Z, b khác 0). Ví dụ: 0.5, -3/4, 2.";
        }
        return replyText;
    }

    function appendTutorBubble(role, text) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${role === "user" ? "user-bubble" : "robot-bubble"}`;
        const avatar = document.createElement("div");
        avatar.className = "bubble-avatar";
        const icon = document.createElement("i");
        icon.className = role === "user" ? "fa-solid fa-user-ninja" : "fa-solid fa-robot";
        avatar.appendChild(icon);

        const content = document.createElement("div");
        content.className = "bubble-content";
        const paragraph = document.createElement("p");
        paragraph.textContent = text;
        content.appendChild(paragraph);

        if (role === "user") {
            bubble.append(content, avatar);
        } else {
            bubble.append(avatar, content);
        }
        chatHistory.appendChild(bubble);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return paragraph;
    }

    function resolveTutorQuestionId() {
        if (state.currentQuestion?.id) return state.currentQuestion.id;
        const activeSkill = state.studentProgress.activeSkill || "MATH_G7";
        return OFFLINE_MOCK_QUESTIONS[activeSkill]?.id || OFFLINE_MOCK_QUESTIONS.MATH_G7.id;
    }

    function resolveActiveTutorSkill() {
        return state.currentQuestion?.skill_id || state.testSession.currentSkill || state.studentProgress.activeSkill || "MATH_G7";
    }

    function resolveActiveTutorDifficulty() {
        return state.currentQuestion?.difficulty_level || 2;
    }

    async function fetchAITutorReply(msg) {
        const response = await fetch(`/api/ai/student/${state.studentId}/tutor`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_id: resolveTutorQuestionId(),
                message: msg,
                history: state.tutorChatHistory.length > 0 ? state.tutorChatHistory : undefined
            })
        });
        if (!response.ok) {
            const errorPayload = await response.json().catch(() => ({}));
            throw new Error(errorPayload.detail || `AI HTTP ${response.status}`);
        }
        return response.json();
    }

    async function fetchAIWorkAnalysis(rawText) {
        const attachedFile = imageInput?.files?.[0];
        const response = await fetch(`/api/ai/student/${state.studentId}/analyze-work`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mode: selectedAIMode,
                subject: state.testSession.subject || "Toán",
                grade: state.testSession.grade || 7,
                skill_id: resolveActiveTutorSkill(),
                work_text: String(rawText || "").trim(),
                attachment_name: attachedFile?.name || null
            })
        });
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || `AI HTTP ${response.status}`);
        }
        return response.json();
    }

    function buildTutorTaskMessage(rawText) {
        const mode = aiModeConfig[selectedAIMode] || aiModeConfig.explain;
        const attachedFile = imageInput?.files?.[0];
        const attachmentText = attachedFile
            ? `\nẢnh đính kèm: ${attachedFile.name}. Hệ thống hiện chưa bật OCR ảnh trực tiếp, hãy xử lý theo mô tả học sinh đã nhập và nhắc học sinh mô tả phần trong ảnh nếu thiếu dữ liệu.`
            : "";
        return [
            "Đây là một yêu cầu học tập trong PorcusAI. Hãy xử lý đúng chế độ và trả lời trực tiếp nhiệm vụ.",
            `Chế độ AI: ${mode.label}.`,
            `Yêu cầu: ${mode.prompt}`,
            `Môn/lớp hiện tại: ${state.testSession.subject || "Toán"} lớp ${state.testSession.grade || 7}.`,
            `Kỹ năng hiện tại: ${getSkillDisplayName(resolveActiveTutorSkill())}.`,
            `Nội dung học sinh gửi: ${rawText.trim() || "(chưa nhập nội dung)"}`,
            attachmentText
        ].filter(Boolean).join("\n");
    }

    function validateAITaskInput(rawText) {
        const text = String(rawText || "").trim();
        const attachedFile = imageInput?.files?.[0];
        const mode = aiModeConfig[selectedAIMode] || aiModeConfig.explain;
        if (!text && !attachedFile) {
            return `Em cần nhập câu hỏi, dán bài làm hoặc gửi ảnh trước khi dùng chế độ "${mode.label}".`;
        }
        if (!text && attachedFile) {
            return "Ảnh đã được nhận. Hệ thống hiện chưa bật OCR thật, em hãy mô tả nội dung trong ảnh hoặc nhập vài bước làm để AI phân tích đúng.";
        }
        if (text.length > 0 && text.length < 8 && !attachedFile) {
            if (selectedAIMode === "similar_question") {
                return "Để tạo câu tương tự, em hãy dán nguyên câu mẫu hoặc mô tả dạng bài rõ hơn.";
            }
            if (selectedAIMode === "find_error") {
                return "Để tìm lỗi sai, em hãy dán bài làm hoặc bước giải em đang nghi ngờ.";
            }
            return "Em viết rõ hơn một chút nhé, ví dụ: phần nào chưa hiểu hoặc câu em đang làm.";
        }
        return "";
    }

    async function sendUserMessage(msg, { useMode = false } = {}) {
        if (!String(msg || "").trim() && !imageInput?.files?.[0]) return;

        const mode = aiModeConfig[selectedAIMode] || aiModeConfig.explain;
        const validationMessage = useMode ? validateAITaskInput(msg) : "";
        if (validationMessage) {
            appendTutorBubble("user", `[${mode.label}] ${String(msg || "").trim() || "Đã chọn ảnh"}`);
            appendTutorBubble("bot", validationMessage);
            return;
        }

        const attachedFile = imageInput?.files?.[0];
        const displayText = String(msg || "").trim() || `Ảnh bài làm: ${attachedFile?.name || "đã chọn"}`;
        const displayMessage = useMode ? `[${mode.label}] ${displayText}` : displayText;
        const aiMessage = useMode ? buildTutorTaskMessage(msg) : msg;

        appendTutorBubble("user", displayMessage);
        if (workInput) workInput.value = "";

        const replyParagraph = appendTutorBubble("bot", "AI đang phân tích bài làm và nối với lộ trình học...");
        try {
            const data = await fetchAITutorReply(msg);
            replyParagraph.textContent = data.content;
            state.tutorChatHistory.push({ role: "user", content: msg });
            state.tutorChatHistory.push({ role: "assistant", content: data.content });
            await updateAIStatusBadge();
        } catch (error) {
            console.warn("[AI Tutor] Fallback offline.", error);
            replyParagraph.textContent = useMode
                ? `Tôi đã nhận chế độ "${mode.label}". ${buildOfflineTutorReply(msg)}`
                : buildOfflineTutorReply(msg);
            if (aiStatusPill) {
                aiStatusPill.className = "realtime-status polling";
                aiStatusPill.textContent = "AI fallback offline";
            }
        }
    }

    function renderAIAnalysisReply(paragraph, analysis) {
        const misconception = analysis.misconception || {};
        const measurement = analysis.measurement || {};
        const pack = Array.isArray(analysis.remediation_pack) ? analysis.remediation_pack : [];
        paragraph.style.whiteSpace = "pre-wrap";
        paragraph.textContent = [
            `AI phát hiện lỗi: ${misconception.detected_error || "Cần thêm dữ liệu bài làm"}`,
            `Bước sai: ${misconception.wrong_step || "Chưa xác định"}`,
            `Kiến thức nền thiếu: ${misconception.missing_prerequisite || analysis.skill_name || "Chưa xác định"}`,
            `Độ tin cậy: ${Math.round(Number(misconception.confidence || 0) * 100)}%`,
            "",
            "Gói ôn cá nhân hóa:",
            ...pack.slice(0, 4).map((step, index) => `${index + 1}. ${step.title || step.type}: ${step.content || ""}`),
            "",
            `Đo lại: ${measurement.target || "Làm đúng các câu kiểm tra lại."}`,
            `Vì sao cần AI: ${analysis.why_ai_is_needed || "AI đọc bài làm tự do và biến lỗi sai thành can thiệp."}`
        ].join("\n");
    }

    function applyAIAnalysisToReview(analysis) {
        const pack = Array.isArray(analysis.remediation_pack) ? analysis.remediation_pack : [];
        if (!pack.length) return;
        const misconception = analysis.misconception || {};
        addAIDecisionLog({
            source: "Trợ lý học tập",
            signal: misconception.detected_error || "Bài làm/câu hỏi tự do của học sinh",
            decision: `Cập nhật bài ôn theo lỗi: ${misconception.missing_prerequisite || analysis.skill_name || "kỹ năng hiện tại"}.`,
            measurement: analysis.measurement?.target || "Làm đúng gói ôn để đo lại mastery.",
            confidence: misconception.confidence ?? 0.75
        });
        renderPersonalReviewSteps(pack.map(step => ({
            skill_name: step.title || step.type,
            action: step.content,
            success_signal: analysis.measurement?.target || "Làm đúng gói ôn để đo lại mastery."
        })), analysis.summary || "AI đã tạo gói ôn từ lỗi sai trong bài làm.");
        state.dailyQuest.aiReviewsUnlocked += 1;
        saveRewardState();
        updateStudentRewardsUI();
    }

    async function generateAIQuestion() {
        appendTutorBubble("user", "Sinh cho em một câu hỏi theo mức hiện tại.");
        const replyParagraph = appendTutorBubble("bot", "AI đang sinh câu hỏi theo skill và độ khó hiện tại...");
        try {
            const response = await fetch(`/api/ai/student/${state.studentId}/generate-question`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    subject: state.testSession.subject || "Toán",
                    grade: state.testSession.grade || 7,
                    skill_id: resolveActiveTutorSkill(),
                    difficulty_level: resolveActiveTutorDifficulty(),
                    count: 1,
                    question_type: "multiple_choice"
                })
            });
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.detail || `AI HTTP ${response.status}`);
            }
            const data = await response.json();
            const question = data.questions?.[0];
            if (!question) throw new Error("AI không trả về câu hỏi.");
            const options = (question.options || [])
                .map(opt => `${opt.key}. ${opt.text}`)
                .join("\n");
            replyParagraph.textContent = [
                `${question.difficulty || "Thông hiểu"} · ${question.text}`,
                options,
                `Gợi ý: ${question.hint || "Hãy phân tích kiến thức nền trước."}`
            ].join("\n");
            replyParagraph.style.whiteSpace = "pre-wrap";
        } catch (error) {
            console.warn("[AI Question] Không thể sinh câu hỏi.", error);
            replyParagraph.textContent = "Hiện chưa sinh được câu hỏi AI. Em tiếp tục làm bài thích ứng, hệ thống vẫn chọn câu theo luật độ khó 3 mức.";
        }
    }

    async function generateAILearningPath() {
        appendTutorBubble("user", "Tạo lộ trình học cá nhân cho em.");
        const replyParagraph = appendTutorBubble("bot", "AI đang đọc mastery và prerequisite graph để tạo lộ trình...");
        try {
            const params = new URLSearchParams({ target_skill: resolveActiveTutorSkill() });
            const response = await fetch(`/api/ai/student/${state.studentId}/learning-path?${params.toString()}`);
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.detail || `AI HTTP ${response.status}`);
            }
            const data = await response.json();
            const path = data.learning_path || {};
            const steps = (path.steps || []).map((step, index) => {
                return `${index + 1}. ${step.skill_name || step.skill_id} - ${step.recommended_difficulty || "Thông hiểu"}\n   ${step.action || "Luyện tập theo gợi ý hệ thống."}\n   Đạt khi: ${step.success_signal || "đúng liên tiếp các câu cùng kỹ năng."}`;
            }).join("\n");
            replyParagraph.textContent = `${path.summary || "Lộ trình học cá nhân"}\n${steps}`;
            replyParagraph.style.whiteSpace = "pre-wrap";
        } catch (error) {
            console.warn("[AI Path] Không thể sinh lộ trình.", error);
            replyParagraph.textContent = "Hiện chưa sinh được lộ trình AI. Em vẫn có thể tiếp tục bài test để hệ thống cập nhật lộ trình bằng BKT.";
        }
    }
    
    document.querySelectorAll("[data-ai-mode]").forEach(btn => {
        btn.addEventListener("click", () => {
            selectedAIMode = btn.getAttribute("data-ai-mode") || "explain";
            document.querySelectorAll("[data-ai-mode]").forEach(item => item.classList.remove("active"));
            btn.classList.add("active");
            const mode = aiModeConfig[selectedAIMode] || aiModeConfig.explain;
            if (workInput) workInput.placeholder = mode.placeholder;
        });
    });

    if (runTaskBtn && workInput) {
        runTaskBtn.addEventListener("click", () => sendUserMessage(workInput.value, { useMode: true }));
        workInput.addEventListener("keydown", event => {
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                sendUserMessage(workInput.value, { useMode: true });
            }
        });
    }

    if (imageInput && imageLabel) {
        imageInput.addEventListener("change", () => {
            const file = imageInput.files?.[0];
            imageLabel.textContent = file ? file.name : "Gửi ảnh bài làm";
        });
    }
    
    document.querySelectorAll(".quick-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            sendUserMessage(btn.getAttribute("data-prompt") || btn.textContent, { useMode: true });
        });
    });

    document.querySelectorAll("[data-ai-action]").forEach(btn => {
        btn.addEventListener("click", () => {
            const action = btn.getAttribute("data-ai-action");
            if (action === "generate-question") generateAIQuestion();
            if (action === "learning-path") generateAILearningPath();
        });
    });

    updateAIStatusBadge();
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

    function appendMascotMessage(role, text) {
        chatHistory.style.display = "flex";
        const message = document.createElement("div");
        message.className = `mascot-msg ${role === "user" ? "user" : "bot"}`;
        message.textContent = text;
        if (text.includes("\n")) message.style.whiteSpace = "pre-wrap";
        chatHistory.appendChild(message);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        if (role !== "user" && commentPara) commentPara.textContent = text.split("\n")[0];
        return message;
    }

    function buildOfflineMascotReply(text) {
        let reply = "Tôi sẽ không đưa đáp án ngay. Em hãy nói rõ mình kẹt ở bước nào: hiểu đề, chọn công thức, hay tính toán?";
        const activeSkill = resolveActiveLearningSkillId();
        const textL = text.toLowerCase();

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

        if (state.currentQuestion && state.isLoggedIn) {
            try {
                const response = await fetch(`/api/ai/student/${state.studentId}/tutor`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        question_id: state.currentQuestion.id,
                        message: text,
                        history: state.tutorChatHistory.length > 0 ? state.tutorChatHistory : undefined
                    })
                });
                if (response.ok) {
                    const data = await response.json();
                    appendTutorReply(data.content);
                    state.tutorChatHistory.push({ role: "user", content: text });
                    state.tutorChatHistory.push({ role: "assistant", content: data.content });
                    return;
                }
            } catch (error) {
                console.warn("[FPT AI] Không khả dụng, chuyển sang trợ lý offline.", error);
            }
        }

        if (activeSkill === 'MATH_G7') {
            if (textL.includes("quy đồng") || textL.includes("mẫu số") || textL.includes("làm sao") || textL.includes("mẫu chung")) {
                reply = "Bước 1: tìm mẫu chung nhỏ nhất. Với 1/2 và -2/3, mẫu chung là 6. Bước 2: đổi 1/2 thành 3/6 và -2/3 thành -4/6. Bây giờ em thử cộng tử số.";
            } else if (textL.includes("dấu") || textL.includes("âm") || textL.includes("sai")) {
                reply = "Hãy kiểm tra dấu ở tử số sau khi quy đồng. 3/6 + (-4/6) nghĩa là 3 + (-4), kết quả là số âm vì 4 lớn hơn 3.";
            } else {
                reply = "Gợi ý từng bước: xác định mẫu chung, quy đồng từng phân số, giữ nguyên mẫu, rồi cộng tử số. Em thử viết bước quy đồng trước nhé.";
            }
        } else if (activeSkill === 'MATH_G6') {
            reply = "Đây là dạng cộng trừ số nguyên. Em hãy so sánh trị tuyệt đối hai số trước, rồi lấy dấu của số có trị tuyệt đối lớn hơn.";
        } else if (activeSkill === 'MATH_G5' || activeSkill === 'MATH_G5_LCM') {
            reply = "Hãy liệt kê bội của từng mẫu số, tìm bội chung nhỏ nhất, rồi dùng nó làm mẫu chung. Đừng nhân tử mà quên nhân mẫu nhé.";
        }
        return reply;
    }

    async function fetchMascotAIReply(text) {
        const response = await fetch(`/api/ai/student/${state.studentId}/tutor`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_id: resolveActiveQuestionId(),
                message: text
            })
        });
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || `AI HTTP ${response.status}`);
        }
        return response.json();
    }

    async function handleSend(rawText = chatInput.value) {
        const text = String(rawText || "").trim();
        if (!text) return;

        appendMascotMessage("user", text);
        chatInput.value = "";
        if (commentPara) commentPara.textContent = "Trợ lý đang suy nghĩ...";
        const pending = appendMascotMessage("bot", "Đang phân tích câu hỏi theo lộ trình của em...");

        try {
            const data = await fetchMascotAIReply(text);
            pending.textContent = data.content || buildOfflineMascotReply(text);
            if (commentPara) commentPara.textContent = pending.textContent.split("\n")[0];
            return;
        } catch (error) {
            console.warn("[Mascot AI] Fallback offline.", error);
        }

        pending.textContent = buildOfflineMascotReply(text);
        if (pending.textContent.includes("\n")) pending.style.whiteSpace = "pre-wrap";
        if (commentPara) commentPara.textContent = pending.textContent.split("\n")[0];
    }

    sendBtn.addEventListener("click", () => handleSend());
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSend();
    });

    document.querySelectorAll("[data-mascot-prompt]").forEach(btn => {
        btn.addEventListener("click", () => handleSend(btn.getAttribute("data-mascot-prompt")));
    });

    document.querySelectorAll("[data-mascot-action='review']").forEach(btn => {
        btn.addEventListener("click", async () => {
            appendMascotMessage("user", "Tạo bài ôn AI cá nhân hóa cho em.");
            const pending = appendMascotMessage("bot", "Đang tạo bài ôn theo skill hiện tại...");
            const path = await buildPersonalAIReview({ silent: true });
            const steps = path.steps || getOfflinePersonalReviewSteps();
            pending.textContent = [
                path.summary || `Bài ôn cho ${getSkillDisplayName()}`,
                ...steps.slice(0, 3).map((step, index) => `${index + 1}. ${step.skill_name || step.skill_id}: ${step.action}`)
            ].join("\n");
            pending.style.whiteSpace = "pre-wrap";
            if (commentPara) commentPara.textContent = "Đã tạo bài ôn cá nhân hóa cho em.";
        });
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
    const studentSidebarMenu = document.getElementById("student-sidebar-menu");
    const teacherSidebarMenu = document.getElementById("teacher-sidebar-menu");
    const progressWrapper = document.getElementById("student-progress-wrapper");
    const teacherTitleWrapper = document.getElementById("teacher-title-wrapper");
    const studentRewards = document.getElementById("student-rewards");
    const questNotification = document.getElementById("quest-notification");
    const userDisplayName = document.getElementById("user-display-name");
    const userAvatarImg = document.getElementById("user-avatar-img");

    if (targetRole === "teacher") {
        state.currentPortal = "teacher";
        if (portalStudent) portalStudent.classList.remove("active");
        if (portalTeacher) portalTeacher.classList.add("active");
        if (studentSidebarMenu) studentSidebarMenu.style.display = "none";
        if (teacherSidebarMenu) teacherSidebarMenu.style.display = "flex";
        if (progressWrapper) progressWrapper.style.display = "none";
        if (studentRewards) studentRewards.style.display = "none";
        if (questNotification) questNotification.style.display = "none";
        if (teacherTitleWrapper) teacherTitleWrapper.style.display = "block";
        if (userDisplayName) userDisplayName.textContent = "Thầy Hùng (GV Toán)";
        if (userAvatarImg) userAvatarImg.src = "https://api.dicebear.com/7.x/adventurer/svg?seed=TeacherHung";
        if (btnTogglePortal) btnTogglePortal.style.display = "none";
        activateTeacherTab(state.currentTeacherTab || "grouping");
        renderTeacherDashboard();
        return;
    }

    const profile = getStudentLoginProfile(state.baseStudentId || state.studentId);
    state.currentPortal = "student";
    if (portalTeacher) portalTeacher.classList.remove("active");
    if (portalStudent) portalStudent.classList.add("active");
    if (studentSidebarMenu) studentSidebarMenu.style.display = "flex";
    if (teacherSidebarMenu) teacherSidebarMenu.style.display = "none";
    if (progressWrapper) progressWrapper.style.display = "block";
    if (studentRewards) studentRewards.style.display = "flex";
    if (questNotification) questNotification.style.display = "block";
    if (teacherTitleWrapper) teacherTitleWrapper.style.display = "none";
    if (userDisplayName) userDisplayName.textContent = profile.name;
    if (userAvatarImg) userAvatarImg.src = `https://api.dicebear.com/7.x/adventurer/svg?seed=${profile.avatar}`;
    const avatarContainer = document.getElementById("user-avatar-container");
    if (avatarContainer) avatarContainer.classList.toggle("avatar-prize-frame", state.redeemedRewards.includes("avatar_frame"));
    if (btnTogglePortal) btnTogglePortal.style.display = "none";
    renderSubjectOverview();
    updateLearningLevelUI();
}

function initAuthFlow() {
    const loginOverlay = document.getElementById("login-overlay");
    const tabBtns = document.querySelectorAll(".login-tab-btn");
    const formPanels = document.querySelectorAll(".login-form-panel");
    const loginSubmitBtn = document.getElementById("btn-login-submit");
    const logoutBtn = document.getElementById("btn-logout");
    const errorMsg = document.getElementById("login-error-msg");
    const btnLoginText = document.getElementById("btn-login-text");
    const btnLoginIcon = document.getElementById("btn-login-icon");
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
            
            if (btnLoginText && btnLoginIcon) {
                if (activeRole === "register") {
                    btnLoginText.textContent = "Đăng ký";
                    btnLoginIcon.className = "fa-solid fa-user-plus";
                } else {
                    btnLoginText.textContent = "Đăng nhập";
                    btnLoginIcon.className = "fa-solid fa-arrow-right-to-bracket";
                }
            }
        });
    });

    if (loginSubmitBtn) {
        loginSubmitBtn.addEventListener("click", async () => {
            if (errorMsg) errorMsg.style.display = "none";

            if (activeRole === "teacher") {
                const username = document.getElementById("teacher-username")?.value || "";
                const password = document.getElementById("teacher-pass")?.value || "";
                try {
                    const response = await fetch("/api/auth/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username, password, role: "teacher" })
                    });
                    if (!response.ok) {
                        showError("Tài khoản hoặc mật khẩu không đúng.");
                        return;
                    }
                    const auth = await response.json();
                    state.isLoggedIn = true;
                    state.loggedInRole = "teacher";
                    localStorage.setItem("isLoggedIn", "true");
                    localStorage.setItem("loggedInRole", "teacher");
                    localStorage.removeItem("studentId");
                    localStorage.setItem("accessToken", auth.access_token);
                    if (loginOverlay) loginOverlay.classList.add("hidden");
                    switchPortalUI("teacher");
                    showToast("Đăng nhập giáo viên thành công.");
                } catch (e) {
                    showError("Lỗi kết nối máy chủ.");
                }
                return;
            } else if (activeRole === "register") {
                const username = document.getElementById("reg-username")?.value || "";
                const password = document.getElementById("reg-password")?.value || "";
                const name = document.getElementById("reg-name")?.value || "";
                const grade = document.getElementById("reg-grade")?.value || "5";
                try {
                    const response = await fetch("/api/auth/student/register", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username, password, name, grade: parseInt(grade) })
                    });
                    if (!response.ok) {
                        const err = await response.json();
                        showError(err.detail || "Đăng ký thất bại.");
                        return;
                    }
                    const auth = await response.json();
                    await handleSuccessfulStudentLogin(auth);
                } catch (e) {
                    showError("Lỗi kết nối máy chủ.");
                }
                return;
            } else {
                const username = document.getElementById("student-pass")?.value || ""; // For backward-compat test logic, but we should use a real username input if available. For now, since there's no username input in student form, let's use the dropdown value.
                const studentId = document.getElementById("student-select-login")?.value || "emma_std_01";
                const password = document.getElementById("student-pass")?.value || "";
                try {
                    const response = await fetch("/api/auth/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username: studentId, password: password, role: "student" })
                    });
                    if (!response.ok) {
                        showError("Tài khoản hoặc mật khẩu không đúng.");
                        return;
                    }
                    const auth = await response.json();
                    await handleSuccessfulStudentLogin(auth);
                } catch (e) {
                    showError("Lỗi kết nối máy chủ.");
                }
            }
        });
    }

    async function handleSuccessfulStudentLogin(auth) {
        const studentId = auth.user?.student_id;
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
        localStorage.setItem("accessToken", auth.access_token);
        await ensureStudentProfileForLogin(studentId, profile);
        if (loginOverlay) loginOverlay.classList.add("hidden");
        
        if (auth.user && auth.user.initial_assessment_completed === false) {
            document.body.classList.add("assessment-mode");
            showToast("Bạn cần hoàn thành bài test đầu vào.");
            startAdaptiveTest(true);
        } else {
            switchPortalUI("student");
            updateStudentRewardsUI();
            prepareTestSetup();
            showToast("Đăng nhập thành công.");
        }
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            const token = localStorage.getItem("accessToken");
            if (token) await fetch("/api/auth/logout", { method: "POST", headers: { "Authorization": `Bearer ${token}` } }).catch(() => null);
            localStorage.removeItem("isLoggedIn");
            localStorage.removeItem("loggedInRole");
            localStorage.removeItem("studentId");
            localStorage.removeItem("accessToken");
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
    const storedToken = localStorage.getItem("accessToken");
    
    async function checkSession() {
        let sessionValid = false;
        let sessionUser = null;
        if (storedToken) {
            try {
                const sessionResponse = await fetch("/api/auth/me", { headers: { "Authorization": `Bearer ${storedToken}` } });
                sessionValid = sessionResponse.ok;
                if (sessionValid) {
                    const sessionData = await sessionResponse.json();
                    sessionUser = sessionData.user;
                }
            } catch (error) {
                console.warn("[Auth] Không thể xác minh phiên đăng nhập.", error);
            }
        }
        
        if (storedLoggedIn === "true" && storedRole && sessionValid) {
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
                
                if (sessionUser && sessionUser.initial_assessment_completed === false) {
                    document.body.classList.add("assessment-mode");
                    showToast("Bạn cần hoàn thành bài test đầu vào.");
                    startAdaptiveTest(true);
                } else {
                    switchPortalUI("student");
                    updateStudentRewardsUI();
                    prepareTestSetup();
                }
            } else {
                switchPortalUI("teacher");
            }
            if (loginOverlay) loginOverlay.classList.add("hidden");
        } else if (loginOverlay) {
            localStorage.removeItem("isLoggedIn");
            localStorage.removeItem("loggedInRole");
            localStorage.removeItem("studentId");
            localStorage.removeItem("accessToken");
            loginOverlay.classList.remove("hidden");
        }
    }
    checkSession();
}

function initPortalNavigation() {
    const btnTogglePortal = document.getElementById("btn-toggle-portal");

    if (btnTogglePortal) {
        btnTogglePortal.style.display = "none";
        btnTogglePortal.addEventListener("click", () => {
            if (state.loggedInRole !== "student" && state.loggedInRole !== "teacher") {
                switchPortalUI(state.currentPortal === 'student' ? 'teacher' : 'student');
            }
        });
    }

    const menuItems = document.querySelectorAll("#student-sidebar-menu .menu-item");
    menuItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            if (state.loggedInRole === "teacher") {
                showToast("Tài khoản giáo viên không có luồng làm bài của học sinh.");
                return;
            }
            menuItems.forEach(i => i.classList.remove("active"));
            item.classList.add("active");
            
            const tabName = item.getAttribute("data-tab");
            if (state.currentPortal === 'teacher') switchPortalUI("student");
            
            document.querySelectorAll(".student-view-panel").forEach(p => p.style.display = "none");
            const activePanel = document.getElementById(`student-view-${tabName}`);
            if (activePanel) activePanel.style.display = "block";
            
            showToast(`Đang mở: ${item.querySelector('span').textContent}`);
        });
    });

    document.querySelectorAll("#teacher-sidebar-menu .menu-item").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            if (state.loggedInRole === "student") {
                showToast("Tài khoản học sinh không có quyền xem bảng điều phối giáo viên.");
                return;
            }
            const tabName = item.getAttribute("data-teacher-nav") || "grouping";
            activateTeacherTab(tabName);
            showToast(`Đang mở: ${item.querySelector('span').textContent}`);
        });
    });
}

function activateTeacherTab(tabName) {
    const tabBtns = document.querySelectorAll(".teacher-tab-btn");
    const panels = document.querySelectorAll(".teacher-tab-panel");
    const sidebarItems = document.querySelectorAll("#teacher-sidebar-menu .menu-item");

    state.currentTeacherTab = tabName;
    tabBtns.forEach(btn => btn.classList.toggle("active", btn.getAttribute("data-teacher-tab") === tabName));
    panels.forEach(panel => panel.classList.toggle("active", panel.id === `teacher-tab-${tabName}`));
    sidebarItems.forEach(item => item.classList.toggle("active", item.getAttribute("data-teacher-nav") === tabName));

    if (tabName === "tree") renderReasoningTreeVisualizer();
}

function initTeacherTabs() {
    const tabBtns = document.querySelectorAll(".teacher-tab-btn");
    
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabName = btn.getAttribute("data-teacher-tab");
            activateTeacherTab(tabName);
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
    const btnCommandPlan = document.getElementById("btn-command-lesson-plan");
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
    if (btnCommandPlan) {
        btnCommandPlan.addEventListener("click", () => {
            const topGapSkill = document.getElementById("teacher-top-gap-skill")?.textContent || "Quy đồng phân số";
            generateAILessonPlan(topGapSkill);
            lpModal.style.display = "flex";
        });
    }
    if (lpCloseBtn) lpCloseBtn.addEventListener("click", () => lpModal.style.display = "none");
    if (lpOverlay) lpOverlay.addEventListener("click", () => lpModal.style.display = "none");
    
    if (diagCloseBtn) diagCloseBtn.addEventListener("click", () => diagModal.style.display = "none");
    if (diagOverlay) diagOverlay.addEventListener("click", () => diagModal.style.display = "none");
}

function initFinalReportModal() {
    const openBtn = document.getElementById("btn-open-final-report");
    const modal = document.getElementById("modal-final-report");
    const overlay = document.getElementById("final-report-overlay");
    const closeBtn = document.getElementById("btn-close-final-report");
    const body = document.getElementById("final-report-modal-body");

    if (!openBtn || !modal || !body) return;

    const close = () => {
        modal.style.display = "none";
    };

    openBtn.addEventListener("click", async () => {
        modal.style.display = "flex";
        body.innerHTML = `<p class="card-subtitle-desc">Đang tải scorecard, benchmark và readiness từ backend...</p>`;
        try {
            const response = await fetch("/api/evidence/final-scorecard");
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const payload = await response.json();
            renderFinalReport(payload);
        } catch (error) {
            console.warn("[-] Could not load final scorecard. Using offline report.", error);
            renderFinalReport({
                summary: {
                    product: "PorcusAI",
                    positioning: "Hệ thống chẩn đoán lỗ hổng kiến thức gốc, không phải chatbot học tập.",
                    current_score: 76,
                    max_score: 100,
                    final_message: "Evidence report chỉ phục vụ demo/pitch, không phải luồng giáo viên hằng ngày."
                },
                judge_barem: [
                    { category: "Bài toán giáo dục", current_score: 13, max_score: 15 },
                    { category: "AI Engineering", current_score: 13, max_score: 15 },
                    { category: "Giá trị giáo dục", current_score: 9, max_score: 15 },
                    { category: "Khai thác FPT AI", current_score: 10, max_score: 15 }
                ],
                benchmarks: [
                    { metric: "Diagnostic smoke benchmark", target: ">= 70%", current: "30 case kỹ thuật", status: "ready" },
                    { metric: "Pilot học sinh thật", target: "30-50 học sinh", current: "Cần bổ sung", status: "gap" }
                ],
                readiness: [
                    { item: "Offline-first local/LAN demo", implemented: true },
                    { item: "Real classroom pilot dataset", implemented: false },
                    { item: "Production auth/tenant isolation", implemented: false }
                ]
            });
        }
    });

    if (closeBtn) closeBtn.addEventListener("click", close);
    if (overlay) overlay.addEventListener("click", close);
}

function renderFinalReport(payload) {
    const body = document.getElementById("final-report-modal-body");
    if (!body) return;
    const summary = payload.summary || {};
    const productName = summary.product === "VGap AI" ? "PorcusAI" : (summary.product || "PorcusAI");
    const positioning = String(summary.positioning || "Báo cáo bằng chứng cho vòng final.").replaceAll("VGap AI", "PorcusAI");
    const finalMessage = String(summary.final_message || "Dùng phần này khi giám khảo hỏi bằng chứng, không đặt nó thành workflow chính của giáo viên.").replaceAll("VGap AI", "PorcusAI");
    const scoreRows = (payload.judge_barem || []).map(item => `
        <tr>
            <td>${escapeHTML(item.category)}</td>
            <td><strong>${escapeHTML(item.current_score)}/${escapeHTML(item.max_score)}</strong></td>
            <td>${escapeHTML(item.next_step || item.evidence || "Cần thêm bằng chứng thực tế.")}</td>
        </tr>
    `).join("");
    const benchmarkItems = (payload.benchmarks || []).map(item => `
        <div class="final-report-chip">
            <strong>${escapeHTML(item.metric)}</strong>
            <span>${escapeHTML(item.current)} / mục tiêu ${escapeHTML(item.target)}</span>
        </div>
    `).join("");
    const readinessItems = (payload.readiness || []).map(item => `
        <span class="readiness-pill ${item.implemented ? "ready" : "gap"}">
            <i class="fa-solid ${item.implemented ? "fa-check" : "fa-triangle-exclamation"}"></i>
            ${escapeHTML(item.item)}
        </span>
    `).join("");

    body.innerHTML = `
        <div class="final-report-summary">
            <div>
                <span class="teacher-command-kicker"><i class="fa-solid fa-scale-balanced"></i> Judge mode</span>
                <h2>${escapeHTML(productName)}: ${escapeHTML(summary.current_score ?? "76")}/${escapeHTML(summary.max_score || 100)}</h2>
                <p>${escapeHTML(positioning)}</p>
            </div>
            <strong>${escapeHTML(summary.current_score ?? "76")}</strong>
        </div>
        <p class="card-subtitle-desc">${escapeHTML(finalMessage)}</p>
        <div class="final-report-chip-grid">${benchmarkItems}</div>
        <div class="table-container">
            <table class="memphis-table final-report-table">
                <thead><tr><th>Hạng mục</th><th>Điểm</th><th>Việc cần làm để lên 85+</th></tr></thead>
                <tbody>${scoreRows}</tbody>
            </table>
        </div>
        <div class="readiness-pill-row">${readinessItems}</div>
    `;
}

async function generateAILessonPlan(skillName, skillId, groupContext) {
    const container = document.getElementById("lesson-plan-modal-body");
    if (!container) return;

    if (skillId) {
        container.innerHTML = "<em>FPT AI đang xây dựng giáo án bám sát SGK theo dữ liệu chẩn đoán...</em>";
        try {
            const response = await fetch("/api/ai/teacher/lesson-plan-grounded", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    skill_id: normalizeSkillId(skillId),
                    group_context: groupContext || "Nhóm học sinh có xác suất thành thạo dưới 0.50.",
                    textbook_series: "Kết nối tri thức"
                })
            });
            if (response.ok) {
                const data = await response.json();
                container.innerHTML = marked.parse(data.content || data.error || data.detail || "");
                return;
            } else {
                const errorData = await response.json().catch(() => ({}));
                container.innerHTML = `<div class="alert-error">Lỗi từ AI: ${errorData.detail || response.statusText}</div>`;
                return;
            }
        } catch (error) {
            console.warn("[FPT AI] Không thể sinh giáo án, dùng mẫu offline.", error);
        }
    }

    // Fallback if needed
    container.style.whiteSpace = "";
    
    let topic = skillName || "Quy đồng mẫu số phân số (Kiến thức nền gốc Lớp 5)";
    let targetGroup = groupContext || "Nhóm học sinh bị hổng kiến thức nền tương ứng.";
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

async function openTeacherAILearningPath(studentId, targetSkill) {
    const modal = document.getElementById("modal-diagnostic-inspector");
    const container = document.getElementById("diagnostic-inspector-body");
    if (!modal || !container) return;

    modal.style.display = "flex";
    container.innerHTML = "<em>AI đang tạo lộ trình can thiệp theo mastery và prerequisite graph...</em>";
    try {
        const querySkill = encodeURIComponent(targetSkill || "MATH_G7");
        const response = await fetch(`/api/ai/teacher/student/${studentId}/learning-path?target_skill=${querySkill}`);
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || `AI HTTP ${response.status}`);
        }
        const data = await response.json();
        const path = data.learning_path || {};
        const steps = (path.steps || []).map((step, index) => `
            <article class="reasoning-step-card">
                <strong>${index + 1}. ${escapeHTML(step.skill_name || step.skill_id)}</strong>
                <p><span class="badge badge-warning">${escapeHTML(step.recommended_difficulty || "Thông hiểu")}</span></p>
                <p>${escapeHTML(step.action || "Giao bài luyện phù hợp với lỗ hổng hiện tại.")}</p>
                <small>Đo tiến bộ: ${escapeHTML(step.success_signal || "đúng liên tiếp các câu cùng kỹ năng.")}</small>
            </article>
        `).join("");

        container.innerHTML = `
            <div class="diagnostic-ai-path">
                <h3><i class="fa-solid fa-route"></i> Lộ trình AI cho học sinh</h3>
                <p class="card-subtitle-desc">${escapeHTML(path.summary || "Đề xuất dựa trên dữ liệu mastery và prerequisite graph.")}</p>
                <div class="reasoning-step-list">${steps}</div>
                <p class="card-subtitle-desc">${escapeHTML(path.teacher_notes || "Giáo viên có thể gom nhóm học sinh cùng skill_id để dạy lại 15 phút.")}</p>
            </div>
        `;
    } catch (error) {
        console.warn("[Teacher AI Path] Không thể sinh lộ trình.", error);
        container.innerHTML = `<div class="alert-error">Chưa tạo được lộ trình AI. Kiểm tra FPT AI key/model hoặc thử lại sau. Lỗi: ${error.message}</div>`;
    }
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
