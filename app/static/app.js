// --- APP STATE & CONFIG ---
const STATE = {
    activeTab: 'dashboard',
    activeSubTab: 'chat',
    students: [],
    atRiskStudents: [],
    geminiConfigured: false,
    charts: {
        grade: null,
        attendance: null
    }
};

// --- DOM ELEMENTS ---
const DOM = {
    navItems: document.querySelectorAll('.nav-item'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    pageTitle: document.getElementById('page-title'),
    pageSubtitle: document.getElementById('page-subtitle'),
    
    // Status
    backendStatusText: document.getElementById('backend-status-text'),
    apiKeyStatus: document.getElementById('api-key-status'),
    
    // Metrics
    metricTotalStudents: document.getElementById('metric-total-students'),
    metricAvgGrade: document.getElementById('metric-avg-grade'),
    metricAtRisk: document.getElementById('metric-at-risk'),
    metricTopPerformer: document.getElementById('metric-top-performer'),
    
    // Lists
    topPerformersList: document.getElementById('top-performers-list'),
    atRiskList: document.getElementById('at-risk-list'),
    
    // Directory & Forms
    searchInput: document.getElementById('search-input'),
    studentsTableBody: document.getElementById('students-table-body'),
    
    // Add Student
    addStudentForm: document.getElementById('add-student-form'),
    addAttendance: document.getElementById('add-attendance'),
    addAttendanceVal: document.getElementById('add-attendance-val'),
    
    // Edit Student Drawer
    editDrawerOverlay: document.getElementById('edit-drawer-overlay'),
    closeEditDrawer: document.getElementById('close-edit-drawer'),
    editStudentForm: document.getElementById('edit-student-form'),
    editDbId: document.getElementById('edit-db-id'),
    editFirstName: document.getElementById('edit-first-name'),
    editLastName: document.getElementById('edit-last-name'),
    editStudentId: document.getElementById('edit-student-id'),
    editCourse: document.getElementById('edit-course'),
    editGrade: document.getElementById('edit-grade'),
    editAttendance: document.getElementById('edit-attendance'),
    editAttendanceVal: document.getElementById('edit-attendance-val'),
    
    // AI Assistant
    aiTabBtns: document.querySelectorAll('.ai-tab-btn'),
    aiSubpanes: document.querySelectorAll('.ai-subpane'),
    
    // Chat Subtab
    chatMessagesContainer: document.getElementById('chat-messages-container'),
    chatInputForm: document.getElementById('chat-input-form'),
    chatInputText: document.getElementById('chat-input-text'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    
    // Audit Subtab
    btnGenerateAudit: document.getElementById('btn-generate-audit'),
    auditResultCard: document.getElementById('audit-result-card'),
    auditReportText: document.getElementById('audit-report-text'),
    btnDownloadAudit: document.getElementById('btn-download-audit'),
    
    // Advisor Subtab
    advisorStudentSelect: document.getElementById('advisor-student-select'),
    advisorStudentCard: document.getElementById('advisor-student-card'),
    advProfileName: document.getElementById('adv-profile-name'),
    advProfileId: document.getElementById('adv-profile-id'),
    advProfileCourse: document.getElementById('adv-profile-course'),
    advProfileGrade: document.getElementById('adv-profile-grade'),
    advProfileAttendance: document.getElementById('adv-profile-attendance'),
    advProfileStanding: document.getElementById('adv-profile-standing'),
    btnGetAdvice: document.getElementById('btn-get-advice'),
    advisorResultCard: document.getElementById('advisor-result-card'),
    advisorRecommendationsText: document.getElementById('advisor-recommendations-text'),
    
    // Toast
    toast: document.getElementById('toast')
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
});

function initApp() {
    checkConnectionStatus();
    refreshData();
}

// --- API COMMUNICATIONS ---
async function apiFetch(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, options);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP error ${response.status}`);
        }
        if (response.status === 204) return null;
        return await response.json();
    } catch (error) {
        console.error(`API fetch error (${endpoint}):`, error);
        throw error;
    }
}

async function checkConnectionStatus() {
    try {
        const data = await apiFetch('/');
        if (data && data.status === 'online') {
            DOM.backendStatusText.innerHTML = "Server connection: Connected 🟢";
            DOM.backendStatusText.previousElementSibling.className = "status-dot online";
        }
    } catch {
        DOM.backendStatusText.innerHTML = "Server connection: Offline 🔴";
        DOM.backendStatusText.previousElementSibling.className = "status-dot offline";
    }

    try {
        const data = await apiFetch('/students/gemini-status');
        if (data && data.status === 'configured') {
            STATE.geminiConfigured = true;
            DOM.apiKeyStatus.innerHTML = "🔑 Gemini: Loaded";
            DOM.apiKeyStatus.classList.add('configured');
        } else {
            DOM.apiKeyStatus.innerHTML = "🔑 Gemini: Offline";
            DOM.apiKeyStatus.classList.remove('configured');
        }
    } catch {
        DOM.apiKeyStatus.innerHTML = "🔑 Gemini: Offline";
        DOM.apiKeyStatus.classList.remove('configured');
    }
}

async function refreshData() {
    try {
        // Fetch all students
        const allStudents = await apiFetch('/students');
        STATE.students = allStudents || [];
        
        // Fetch at-risk students
        const atRisk = await apiFetch('/students/at-risk');
        STATE.atRiskStudents = atRisk || [];
        
        updateMetrics();
        updateCharts();
        updateTopPerformers();
        updateAtRiskAlertList();
        renderStudentTable(STATE.students);
        populateAdvisorDropdown();
    } catch (err) {
        showToast(`Failed to load data: ${err.message}`, 'error');
    }
}

// --- STATE ACTIONS ---
function updateMetrics() {
    const total = STATE.students.length;
    DOM.metricTotalStudents.innerText = total;

    if (total === 0) {
        DOM.metricAvgGrade.innerText = "-";
        DOM.metricAtRisk.innerText = "0";
        DOM.metricTopPerformer.innerText = "None";
        return;
    }

    // Average grade
    const totalGrades = STATE.students.reduce((acc, s) => acc + gradeToNumeric(s.grade), 0);
    const avg = totalGrades / total;
    DOM.metricAvgGrade.innerText = `${avg.toFixed(1)}% (${numericToGrade(avg)})`;

    // At risk count
    DOM.metricAtRisk.innerText = STATE.atRiskStudents.length;

    // Top performer
    const sorted = [...STATE.students].sort((a, b) => {
        const gradeA = gradeToNumeric(a.grade);
        const gradeB = gradeToNumeric(b.grade);
        if (gradeB !== gradeA) return gradeB - gradeA;
        return (b.attendance || 0) - (a.attendance || 0);
    });
    
    if (sorted.length > 0) {
        const top = sorted[0];
        DOM.metricTopPerformer.innerText = `${top.first_name} ${top.last_name} (${top.grade})`;
        DOM.metricTopPerformer.title = `${top.first_name} ${top.last_name} (${top.grade}) - Course: ${top.course}`;
    } else {
        DOM.metricTopPerformer.innerText = "None";
    }
}

function updateTopPerformers() {
    DOM.topPerformersList.innerHTML = '';
    
    if (STATE.students.length === 0) {
        DOM.topPerformersList.innerHTML = '<div class="list-placeholder">No student records found.</div>';
        return;
    }

    const topList = [...STATE.students]
        .sort((a, b) => {
            const gradeA = gradeToNumeric(a.grade);
            const gradeB = gradeToNumeric(b.grade);
            if (gradeB !== gradeA) return gradeB - gradeA;
            return (b.attendance || 0) - (a.attendance || 0);
        })
        .slice(0, 3);

    topList.forEach(s => {
        const item = document.createElement('div');
        item.className = 'list-item top-performer';
        item.innerHTML = `
            <div class="list-item-info">
                <h5>${s.first_name} ${s.last_name} <span>(${s.student_id})</span></h5>
                <span>Course: ${s.course}</span>
            </div>
            <div class="list-item-stats">
                <span class="badge badge-success">Grade: ${s.grade}</span>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Attend: ${s.attendance}%</div>
            </div>
        `;
        DOM.topPerformersList.appendChild(item);
    });
}

function updateAtRiskAlertList() {
    DOM.atRiskList.innerHTML = '';

    if (STATE.atRiskStudents.length === 0) {
        DOM.atRiskList.innerHTML = '<div class="list-placeholder" style="color: var(--success);">🎉 Excellent! No students are currently marked at risk.</div>';
        return;
    }

    STATE.atRiskStudents.forEach(s => {
        const reasons = [];
        if (s.attendance < 65.0) {
            reasons.push(`low attendance (${s.attendance}%)`);
        }
        const gradeVal = s.grade;
        try {
            if (gradeVal && parseFloat(gradeVal) < 60.0) {
                reasons.push(`low grade (${gradeVal})`);
            }
        } catch {
            const val = String(gradeVal).trim().toUpperCase();
            if (val === 'F' || val === 'FAIL') {
                reasons.push("failing grade (F/FAIL)");
            }
        }

        const item = document.createElement('div');
        item.className = 'list-item at-risk';
        item.innerHTML = `
            <div class="list-item-info">
                <h5>${s.first_name} ${s.last_name} <span>(${s.student_id})</span></h5>
                <span style="color: var(--danger); font-weight: 500;">Reason: ${reasons.join(', ')}</span>
            </div>
            <div class="list-item-stats">
                <span class="badge badge-danger">At Risk</span>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Course: ${s.course}</div>
            </div>
        `;
        DOM.atRiskList.appendChild(item);
    });
}

// --- VISUAL CHARTS (Chart.js) ---
function updateCharts() {
    // 1. Grade Distribution Chart
    const gradeOrder = ["A+", "A", "B+", "B", "C+", "C", "D", "F", "Pass", "Fail"];
    const gradeCounts = {};
    gradeOrder.forEach(g => gradeCounts[g] = 0);
    
    STATE.students.forEach(s => {
        if (gradeCounts[s.grade] !== undefined) {
            gradeCounts[s.grade]++;
        }
    });

    const activeGrades = gradeOrder.filter(g => gradeCounts[g] > 0);
    const activeCounts = activeGrades.map(g => gradeCounts[g]);

    const ctxGrade = document.getElementById('gradeChart').getContext('2d');
    if (STATE.charts.grade) STATE.charts.grade.destroy();
    
    if (activeCounts.length === 0) {
        // Draw empty indicator
        STATE.charts.grade = null;
    } else {
        STATE.charts.grade = new Chart(ctxGrade, {
            type: 'bar',
            data: {
                labels: activeGrades,
                datasets: [{
                    label: 'Students',
                    data: activeCounts,
                    backgroundColor: '#6366f1',
                    borderRadius: 6,
                    borderWidth: 0,
                    barThickness: 24
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748b', font: { family: 'Outfit' } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#64748b', stepSize: 1, font: { family: 'Outfit' } }
                    }
                }
            }
        });
    }

    // 2. Attendance by Course Chart
    const courseMap = {};
    STATE.students.forEach(s => {
        if (!courseMap[s.course]) {
            courseMap[s.course] = { sum: 0, count: 0 };
        }
        courseMap[s.course].sum += s.attendance;
        courseMap[s.course].count++;
    });

    const courses = Object.keys(courseMap);
    const avgs = courses.map(c => courseMap[c].sum / courseMap[c].count);

    const ctxAttendance = document.getElementById('attendanceChart').getContext('2d');
    if (STATE.charts.attendance) STATE.charts.attendance.destroy();

    if (courses.length === 0) {
        STATE.charts.attendance = null;
    } else {
        STATE.charts.attendance = new Chart(ctxAttendance, {
            type: 'bar',
            data: {
                labels: courses,
                datasets: [{
                    label: 'Avg Attendance (%)',
                    data: avgs,
                    backgroundColor: '#a855f7',
                    borderRadius: 6,
                    borderWidth: 0,
                    barThickness: 20
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748b', font: { family: 'Outfit' } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#64748b', max: 100, font: { family: 'Outfit' } }
                    }
                }
            }
        });
    }
}

// --- STUDENT DIRECTORY TABLE ---
function renderStudentTable(studentsList) {
    DOM.studentsTableBody.innerHTML = '';
    
    if (studentsList.length === 0) {
        DOM.studentsTableBody.innerHTML = `
            <tr>
                <td colspan="9" class="table-placeholder">No matching student records found.</td>
            </tr>
        `;
        return;
    }

    studentsList.forEach(s => {
        const tr = document.createElement('tr');
        const status = calculateStatus(s);
        let badgeClass = 'badge-success';
        if (status === 'Needs Attention') badgeClass = 'badge-warning';
        if (status === 'At Risk') badgeClass = 'badge-danger';
        
        tr.innerHTML = `
            <td><strong>#${s.id}</strong></td>
            <td>${s.student_id}</td>
            <td>${s.first_name}</td>
            <td>${s.last_name}</td>
            <td>${s.course}</td>
            <td><strong>${s.grade}</strong></td>
            <td>${s.attendance}%</td>
            <td><span class="badge ${badgeClass}">${status}</span></td>
            <td>
                <button class="btn-action-icon edit-btn" data-id="${s.id}" title="Edit student">✏️</button>
                <button class="btn-action-icon delete-btn" data-id="${s.id}" title="Delete student">❌</button>
            </td>
        `;
        DOM.studentsTableBody.appendChild(tr);
    });

    // Attach actions
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.target.getAttribute('data-id');
            openEditDrawer(id);
        });
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.target.getAttribute('data-id');
            handleDeleteStudent(id);
        });
    });
}

// --- EVENT LISTENERS SETUP ---
function setupEventListeners() {
    // Navigation routing tabs
    DOM.navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Search action in directory
    DOM.searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const filtered = STATE.students.filter(s => 
            s.first_name.toLowerCase().includes(query) ||
            s.last_name.toLowerCase().includes(query) ||
            s.student_id.toLowerCase().includes(query) ||
            s.course.toLowerCase().includes(query)
        );
        renderStudentTable(filtered);
    });

    // Form inputs and sliders values
    DOM.addAttendance.addEventListener('input', (e) => {
        DOM.addAttendanceVal.innerText = `${e.target.value}%`;
    });

    DOM.editAttendance.addEventListener('input', (e) => {
        DOM.editAttendanceVal.innerText = `${e.target.value}%`;
    });

    // Add Student Submit form
    DOM.addStudentForm.addEventListener('submit', handleAddStudent);

    // Drawer overlay events
    DOM.closeEditDrawer.addEventListener('click', closeEditDrawer);
    DOM.editStudentForm.addEventListener('submit', handleUpdateStudent);

    // AI subtabs switcher
    DOM.aiTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const subtab = btn.getAttribute('data-subtab');
            switchAISubTab(subtab);
        });
    });

    // AI chat submission
    DOM.chatInputForm.addEventListener('submit', handleAIChatSend);
    DOM.clearChatBtn.addEventListener('click', clearChatHistory);

    // AI generate audit report
    DOM.btnGenerateAudit.addEventListener('click', handleGenerateAuditReport);

    // AI individual student selector dropdown
    DOM.advisorStudentSelect.addEventListener('change', (e) => {
        const studentId = e.target.value;
        if (studentId) {
            showAdvisorProfileCard(studentId);
        } else {
            DOM.advisorStudentCard.classList.add('hidden');
            DOM.btnGetAdvice.classList.add('hidden');
            DOM.advisorResultCard.classList.add('hidden');
        }
    });

    DOM.btnGetAdvice.addEventListener('click', handleGetAdvisorAdvice);
}

// --- PAGE TAB NAVIGATION ROUTING ---
function switchTab(tabName) {
    DOM.navItems.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabName) btn.classList.add('active');
        else btn.classList.remove('active');
    });

    DOM.tabPanes.forEach(pane => {
        if (pane.id === `tab-${tabName}`) pane.classList.add('active');
        else pane.classList.remove('active');
    });

    STATE.activeTab = tabName;
    
    // Custom Titles & Subtitles per tab page
    if (tabName === 'dashboard') {
        DOM.pageTitle.innerText = "Dashboard Overview";
        DOM.pageSubtitle.innerText = "Real-time educational monitoring, tracking, and student performance insights.";
    } else if (tabName === 'students') {
        DOM.pageTitle.innerText = "👥 Registered Students Directory";
        DOM.pageSubtitle.innerText = "View, edit, filter, or delete student profiles registered in the database.";
    } else if (tabName === 'add-student') {
        DOM.pageTitle.innerText = "➕ Register New Student";
        DOM.pageSubtitle.innerText = "Register a new student record. Verification will be run on the backend database.";
    } else if (tabName === 'ai-assistant') {
        DOM.pageTitle.innerText = "🤖 AI Classroom Assistant (Gemini)";
        DOM.pageSubtitle.innerText = "Consult Google Gemini regarding classroom performance metrics, audits, or roadmaps.";
    }

    refreshData();
}

function switchAISubTab(subtabName) {
    DOM.aiTabBtns.forEach(btn => {
        if (btn.getAttribute('data-subtab') === subtabName) btn.classList.add('active');
        else btn.classList.remove('active');
    });

    DOM.aiSubpanes.forEach(pane => {
        if (pane.id === `ai-subpane-${subtabName}`) pane.classList.add('active');
        else pane.classList.remove('active');
    });

    STATE.activeSubTab = subtabName;
}

// --- STUDENT ACTIONS CRUD LOGIC ---
async function handleAddStudent(e) {
    e.preventDefault();
    const fn = document.getElementById('add-first-name').value.trim();
    const ln = document.getElementById('add-last-name').value.trim();
    const sid = document.getElementById('add-student-id').value.trim();
    const course = document.getElementById('add-course').value.trim();
    const grade = document.getElementById('add-grade').value;
    const attendance = parseFloat(DOM.addAttendance.value);

    try {
        await apiFetch('/students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_name: fn,
                last_name: ln,
                student_id: sid,
                course: course,
                grade: grade,
                attendance: attendance
            })
        });

        showToast(`🎉 Student ${fn} ${ln} successfully registered!`, 'success');
        DOM.addStudentForm.reset();
        DOM.addAttendanceVal.innerText = '95%';
        switchTab('dashboard');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function openEditDrawer(dbId) {
    const s = STATE.students.find(student => String(student.id) === String(dbId));
    if (!s) return;

    DOM.editDbId.value = s.id;
    DOM.editFirstName.value = s.first_name;
    DOM.editLastName.value = s.last_name;
    DOM.editStudentId.value = s.student_id;
    DOM.editCourse.value = s.course;
    DOM.editGrade.value = s.grade;
    DOM.editAttendance.value = s.attendance;
    DOM.editAttendanceVal.innerText = `${s.attendance}%`;

    DOM.editDrawerOverlay.classList.add('open');
}

function closeEditDrawer() {
    DOM.editDrawerOverlay.classList.remove('open');
}

async function handleUpdateStudent(e) {
    e.preventDefault();
    const id = DOM.editDbId.value;
    const fn = DOM.editFirstName.value.trim();
    const ln = DOM.editLastName.value.trim();
    const sid = DOM.editStudentId.value.trim();
    const course = DOM.editCourse.value.trim();
    const grade = DOM.editGrade.value;
    const attendance = parseFloat(DOM.editAttendance.value);

    try {
        await apiFetch(`/students/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_name: fn,
                last_name: ln,
                student_id: sid,
                course: course,
                grade: grade,
                attendance: attendance
            })
        });

        showToast('Successfully updated record!', 'success');
        closeEditDrawer();
        refreshData();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleDeleteStudent(id) {
    const s = STATE.students.find(student => String(student.id) === String(id));
    if (!s) return;

    const confirmDel = confirm(`Are you sure you want to permanently delete student ${s.first_name} ${s.last_name} (${s.student_id})?`);
    if (!confirmDel) return;

    try {
        await apiFetch(`/students/${id}`, { method: 'DELETE' });
        showToast('Student successfully deleted!', 'success');
        refreshData();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- AI ASSISTANT TABS ACTIONS ---
async function handleAIChatSend(e) {
    e.preventDefault();
    if (!STATE.geminiConfigured) {
        showToast("Gemini key is offline. Configure it in Vercel settings.", "error");
        return;
    }

    const question = DOM.chatInputText.value.trim();
    if (!question) return;

    // Render User message bubble
    appendMessageBubble(question, 'user', '👤');
    DOM.chatInputText.value = '';

    // Render loading indicator for Assistant bubble
    const loadingBubble = appendMessageBubble('Thinking...', 'assistant', '🤖', true);

    try {
        const data = await apiFetch('/students/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        loadingBubble.remove();
        // Render Response using Marked markdown formatting
        appendMessageBubble(data.result, 'assistant', '🤖');
    } catch (err) {
        loadingBubble.remove();
        appendMessageBubble(`Error getting answer: ${err.message}`, 'assistant', '🤖');
    }
}

function appendMessageBubble(text, role, avatarSymbol, isLoading = false) {
    const bubbleWrapper = document.createElement('div');
    bubbleWrapper.className = `message ${role}`;
    
    let bubbleContent = text;
    if (role === 'assistant' && !isLoading) {
        bubbleContent = marked.parse(text); // parse markdown to html
    }

    bubbleWrapper.innerHTML = `
        <div class="msg-avatar">${avatarSymbol}</div>
        <div class="msg-bubble">${bubbleContent}</div>
    `;

    DOM.chatMessagesContainer.appendChild(bubbleWrapper);
    DOM.chatMessagesContainer.scrollTop = DOM.chatMessagesContainer.scrollHeight;
    
    return bubbleWrapper;
}

function clearChatHistory() {
    DOM.chatMessagesContainer.innerHTML = `
        <div class="message assistant">
            <div class="msg-avatar">🤖</div>
            <div class="msg-bubble">
                Chat history cleared. How can I help you today?
            </div>
        </div>
    `;
}

async function handleGenerateAuditReport() {
    if (!STATE.geminiConfigured) {
        showToast("Gemini key is offline. Configure it in Vercel settings.", "error");
        return;
    }

    DOM.btnGenerateAudit.innerText = "⚡ Analyzing records with Gemini...";
    DOM.btnGenerateAudit.disabled = true;

    try {
        const data = await apiFetch('/students/audit', { method: 'POST' });
        
        DOM.auditReportText.innerHTML = marked.parse(data.result);
        DOM.auditResultCard.classList.remove('hidden');
        DOM.btnGenerateAudit.innerText = "📊 Generate AI Analysis Report";
        DOM.btnGenerateAudit.disabled = false;

        // Configure download file action
        DOM.btnDownloadAudit.onclick = () => {
            const blob = new Blob([data.result], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'student_ai_analysis_report.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        };
    } catch (err) {
        showToast(`Audit failed: ${err.message}`, 'error');
        DOM.btnGenerateAudit.innerText = "📊 Generate AI Analysis Report";
        DOM.btnGenerateAudit.disabled = false;
    }
}

function populateAdvisorDropdown() {
    // Keep first option
    DOM.advisorStudentSelect.innerHTML = '<option value="">Choose student to analyze...</option>';
    STATE.students.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.innerText = `${s.first_name} ${s.last_name} (${s.student_id}) - ${s.course}`;
        DOM.advisorStudentSelect.appendChild(opt);
    });
}

function showAdvisorProfileCard(dbId) {
    const s = STATE.students.find(student => String(student.id) === String(dbId));
    if (!s) return;

    const standing = calculateStatus(s);
    let badgeHtml = `<span class="badge badge-success">${standing}</span>`;
    if (standing === 'Needs Attention') badgeHtml = `<span class="badge badge-warning">${standing}</span>`;
    if (standing === 'At Risk') badgeHtml = `<span class="badge badge-danger">${standing}</span>`;

    DOM.advProfileName.innerText = `Student Profile: ${s.first_name} ${s.last_name}`;
    DOM.advProfileId.innerText = s.student_id;
    DOM.advProfileCourse.innerText = s.course;
    DOM.advProfileGrade.innerText = s.grade;
    DOM.advProfileAttendance.innerText = `${s.attendance}%`;
    DOM.advProfileStanding.innerHTML = badgeHtml;

    DOM.advisorStudentCard.classList.remove('hidden');
    DOM.btnGetAdvice.classList.remove('hidden');
    DOM.advisorResultCard.classList.add('hidden'); // hide previous advice
}

async function handleGetAdvisorAdvice() {
    if (!STATE.geminiConfigured) {
        showToast("Gemini key is offline. Configure it in Vercel settings.", "error");
        return;
    }

    const id = DOM.advisorStudentSelect.value;
    if (!id) return;

    DOM.btnGetAdvice.innerText = "⚡ Consulting Gemini...";
    DOM.btnGetAdvice.disabled = true;

    try {
        const data = await apiFetch(`/students/${id}/analyze`, { method: 'POST' });
        
        DOM.advisorRecommendationsText.innerHTML = marked.parse(data.result);
        DOM.advisorResultCard.classList.remove('hidden');
        
        DOM.btnGetAdvice.innerText = "🤖 Get Advisor Recommendations";
        DOM.btnGetAdvice.disabled = false;
    } catch (err) {
        showToast(`Advice query failed: ${err.message}`, 'error');
        DOM.btnGetAdvice.innerText = "🤖 Get Advisor Recommendations";
        DOM.btnGetAdvice.disabled = false;
    }
}

// --- UTILITIES / Badges and Grades ---
function calculateStatus(s) {
    const attendance = parseFloat(s.attendance || 0);
    const grade = s.grade;
    
    let isAtRisk = false;
    if (attendance < 65.0) {
        isAtRisk = true;
    } else if (grade) {
        try {
            if (parseFloat(grade) < 60.0) isAtRisk = true;
        } catch {
            const val = String(grade).trim().toUpperCase();
            if (val === "F" || val === "FAIL") isAtRisk = true;
        }
    }

    if (isAtRisk) return "At Risk";

    let isNeedsAttention = false;
    if (attendance < 75.0) {
        isNeedsAttention = true;
    } else if (grade) {
        try {
            if (parseFloat(grade) < 70.0) isNeedsAttention = true;
        } catch {
            const val = String(grade).trim().toUpperCase();
            if (val === "D" || val === "C-") isNeedsAttention = true;
        }
    }

    if (isNeedsAttention) return "Needs Attention";
    return "On Track";
}

function gradeToNumeric(grade) {
    if (!grade) return 75.0;
    const num = parseFloat(grade);
    if (!isNaN(num)) return num;

    const gradeMap = {
        "A+": 97.0, "A": 93.0, "B+": 87.0, "B": 83.0,
        "C+": 77.0, "C": 73.0, "D": 65.0, "F": 50.0,
        "Pass": 80.0, "Fail": 50.0
    };
    return gradeMap[String(grade).trim()] || 75.0;
}

function numericToGrade(score) {
    if (score >= 95.0) return "A+";
    if (score >= 90.0) return "A";
    if (score >= 85.0) return "B+";
    if (score >= 80.0) return "B";
    if (score >= 75.0) return "C+";
    if (score >= 70.0) return "C";
    if (score >= 60.0) return "D";
    return "F";
}

function showToast(message, type = 'success') {
    DOM.toast.innerText = message;
    DOM.toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        DOM.toast.classList.remove('show');
    }, 4000);
}
