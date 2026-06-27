
const AUTH_TOKEN_KEY = "slippage_shield_access_token";
const AUTH_USER_KEY = "slippage_shield_user";

function getStoredToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function getStoredUser() {
    try {
        return JSON.parse(localStorage.getItem(AUTH_USER_KEY) || "{}");
    } catch {
        return {};
    }
}

function authFetch(url, options = {}) {
    const token = getStoredToken();
    const headers = new Headers(options.headers || {});

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    return window.fetch(url, {
        ...options,
        headers
    });
}

function showApplication() {
    document.body.classList.add("authenticated");

    const storedUser = getStoredUser();
    const userName = storedUser.name || "Project User";

    const userDisplayName = document.getElementById("user-display-name");
    const userDisplayRole = document.getElementById("user-display-role");

    if (userDisplayName) {
        userDisplayName.textContent = userName;
    }

    if (userDisplayRole) {
        userDisplayRole.textContent = storedUser.role || "User";
    }

    if (!document.getElementById("logout-button")) {
        const logoutBtn = document.createElement("button");
        logoutBtn.id = "logout-button";
        logoutBtn.className = "logout-button";
        logoutBtn.textContent = "Logout";
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem(AUTH_TOKEN_KEY);
            localStorage.removeItem(AUTH_USER_KEY);
            window.location.reload();
        });
        document.body.appendChild(logoutBtn);
    }
}

function showLogin() {
    document.body.classList.remove("authenticated");
}

function showAuthPanel(panelName) {
    const panels = {
        login: document.getElementById("login-panel"),
        forgot: document.getElementById("forgot-panel"),
        reset: document.getElementById("reset-panel")
    };

    Object.values(panels).forEach((panel) => {
        if (panel) {
            panel.classList.add("is-hidden");
        }
    });

    if (panels[panelName]) {
        panels[panelName].classList.remove("is-hidden");
    }

    ["login-error", "forgot-message", "reset-message"].forEach((id) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = "";
            element.classList.remove("success-message");
        }
    });
}

async function readApiError(response, fallbackMessage) {
    try {
        const data = await response.json();
        return data.detail || data.message || fallbackMessage;
    } catch {
        return fallbackMessage;
    }
}

function setupLogin() {
    const loginForm = document.getElementById("login-form");
    const loginError = document.getElementById("login-error");

    const forgotForm = document.getElementById("forgot-password-form");
    const forgotMessage = document.getElementById("forgot-message");
    const showForgotButton = document.getElementById("show-forgot-password");

    const resetForm = document.getElementById("reset-password-form");
    const resetMessage = document.getElementById("reset-message");

    const backToLoginFromForgot = document.getElementById("back-to-login-from-forgot");
    const backToLoginFromReset = document.getElementById("back-to-login-from-reset");

    const resetTokenInput = document.getElementById("reset-token");

    const params = new URLSearchParams(window.location.search);
    const resetTokenFromUrl = params.get("reset_token");

    if (getStoredToken()) {
        showApplication();
        return;
    }

    showLogin();

    if (resetTokenFromUrl && resetTokenInput) {
        resetTokenInput.value = resetTokenFromUrl;
        showAuthPanel("reset");
    } else {
        showAuthPanel("login");
    }

    if (showForgotButton) {
        showForgotButton.addEventListener("click", () => {
            const loginEmail = document.getElementById("login-email");
            const forgotEmail = document.getElementById("forgot-email");

            if (loginEmail && forgotEmail && loginEmail.value.trim()) {
                forgotEmail.value = loginEmail.value.trim();
            }

            showAuthPanel("forgot");
        });
    }

    if (backToLoginFromForgot) {
        backToLoginFromForgot.addEventListener("click", () => {
            showAuthPanel("login");
        });
    }

    if (backToLoginFromReset) {
        backToLoginFromReset.addEventListener("click", () => {
            showAuthPanel("login");
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;

            if (loginError) {
                loginError.textContent = "";
            }

            try {
                const response = await window.fetch("/api/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                if (!response.ok) {
                    throw new Error(await readApiError(response, "Invalid email or password."));
                }

                const data = await response.json();

                localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
                localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data.user || { name: "Project User", role: "User" }));

                window.location.reload();
            } catch (error) {
                if (loginError) {
                    loginError.textContent = error.message || "Login failed. Please try again.";
                }
            }
        });
    }

    if (forgotForm) {
        forgotForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("forgot-email").value.trim();

            if (forgotMessage) {
                forgotMessage.textContent = "";
                forgotMessage.classList.remove("success-message");
            }

            try {
                const response = await window.fetch("/api/auth/forgot-password", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email })
                });

                if (!response.ok) {
                    throw new Error(await readApiError(response, "Unable to process password reset request."));
                }

                const data = await response.json();

                if (data.reset_token && resetTokenInput) {
                    resetTokenInput.value = data.reset_token;
                    showAuthPanel("reset");
                    if (resetMessage) {
                        resetMessage.textContent = "Account verified. Please set a new password.";
                        resetMessage.classList.add("success-message");
                    }
                } else if (forgotMessage) {
                    forgotMessage.textContent = data.message || "If the email exists, password reset instructions have been generated.";
                }
            } catch (error) {
                if (forgotMessage) {
                    forgotMessage.textContent = error.message || "Unable to process password reset request.";
                }
            }
        });
    }

    if (resetForm) {
        resetForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const resetToken = document.getElementById("reset-token").value;
            const newPassword = document.getElementById("new-password").value;
            const confirmPassword = document.getElementById("confirm-password").value;

            if (resetMessage) {
                resetMessage.textContent = "";
                resetMessage.classList.remove("success-message");
            }

            if (newPassword !== confirmPassword) {
                if (resetMessage) {
                    resetMessage.textContent = "New password and confirm password do not match.";
                }
                return;
            }

            try {
                const response = await window.fetch("/api/auth/reset-password", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        reset_token: resetToken,
                        new_password: newPassword,
                        confirm_password: confirmPassword
                    })
                });

                if (!response.ok) {
                    throw new Error(await readApiError(response, "Unable to reset password."));
                }

                document.getElementById("new-password").value = "";
                document.getElementById("confirm-password").value = "";

                showAuthPanel("login");

                if (loginError) {
                    loginError.textContent = "Password reset successful. Please login with the new password.";
                    loginError.classList.add("success-message");
                }

                window.history.replaceState({}, document.title, window.location.pathname);
            } catch (error) {
                if (resetMessage) {
                    resetMessage.textContent = error.message || "Unable to reset password.";
                }
            }
        });
    }
}

setupLogin();


// Slippage Shield Client Application Logic

const API_BASE = "/api";
let currentTheme = "dark";
let charts = {};

const MAX_PREDICTION_HORIZON_DAYS = 365;
const MAX_UNEXPLAINED_BUFFER_DAYS = 60;

function toIsoDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function buildLocalDate(year, month, day) {
    const date = new Date(year, month - 1, day);
    if (
        date.getFullYear() !== year ||
        date.getMonth() !== month - 1 ||
        date.getDate() !== day
    ) {
        return null;
    }
    return date;
}

function parseIsoDateLocal(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec((value || "").trim());
    if (!match) return null;

    return buildLocalDate(Number(match[1]), Number(match[2]), Number(match[3]));
}

function parseDisplayDateLocal(value) {
    const cleaned = (value || "").trim();
    const ddmmyyyy = /^(\d{2})[-/](\d{2})[-/](\d{4})$/.exec(cleaned);
    if (ddmmyyyy) {
        return buildLocalDate(Number(ddmmyyyy[3]), Number(ddmmyyyy[2]), Number(ddmmyyyy[1]));
    }

    const yyyymmddSlash = /^(\d{4})[/](\d{2})[/](\d{2})$/.exec(cleaned);
    if (yyyymmddSlash) {
        return buildLocalDate(Number(yyyymmddSlash[1]), Number(yyyymmddSlash[2]), Number(yyyymmddSlash[3]));
    }

    return null;
}

function normalizeDateInputValue(inputElement) {
    if (!inputElement) return null;

    // HTML <input type="date"> normally stores its real value as YYYY-MM-DD,
    // even when the browser visually displays DD-MM-YYYY for the user's locale.
    const rawValue = (inputElement.value || "").trim();
    let parsedDate = parseIsoDateLocal(rawValue);

    // Extra safety for browsers/custom controls that expose a display-format value.
    if (!parsedDate) {
        parsedDate = parseDisplayDateLocal(rawValue);
    }

    // Fallback only. valueAsDate can be UTC-based, so use UTC parts and rebuild locally.
    if (!parsedDate && inputElement.valueAsDate instanceof Date && !Number.isNaN(inputElement.valueAsDate.getTime())) {
        const valueAsDate = inputElement.valueAsDate;
        parsedDate = buildLocalDate(
            valueAsDate.getUTCFullYear(),
            valueAsDate.getUTCMonth() + 1,
            valueAsDate.getUTCDate()
        );
    }

    return parsedDate ? toIsoDate(parsedDate) : null;
}

function addDays(date, days) {
    const copy = new Date(date.getTime());
    copy.setDate(copy.getDate() + days);
    return copy;
}

function todayAtMidnight() {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}


function daysFromToday(value) {
    const selectedDate = parseIsoDateLocal(value);
    if (!selectedDate) return Number.NaN;
    const diffMs = selectedDate.getTime() - todayAtMidnight().getTime();
    return Math.round(diffMs / (1000 * 60 * 60 * 24));
}

function initializeDateControls() {
    const dateInput = document.getElementById("pred-date");
    if (!dateInput) return;
    const today = todayAtMidnight();
    dateInput.min = toIsoDate(today);
    dateInput.max = toIsoDate(addDays(today, MAX_PREDICTION_HORIZON_DAYS));
}

function validatePredictionSchedule(committedDate, plannedLeadDays) {
    const daysUntilCommitted = daysFromToday(committedDate);

    if (daysUntilCommitted < 0) {
        return "Committed delivery date cannot be in the past.";
    }

    if (daysUntilCommitted > MAX_PREDICTION_HORIZON_DAYS) {
        return `Committed delivery date is ${daysUntilCommitted} days from today. This model is intended for operational predictions up to ${MAX_PREDICTION_HORIZON_DAYS} days ahead.`;
    }

    const unexplainedBufferDays = daysUntilCommitted - plannedLeadDays;
    if (unexplainedBufferDays > MAX_UNEXPLAINED_BUFFER_DAYS) {
        return `Committed delivery date is ${daysUntilCommitted} days from today, but planned lead time is only ${plannedLeadDays} days. For a long-term order, increase planned lead time close to ${daysUntilCommitted} days instead of leaving it as ${plannedLeadDays}.`;
    }

    return null;
}


function getApiErrorMessage(data) {
    if (Array.isArray(data?.detail)) {
        return data.detail.map(item => item.msg || item.message || JSON.stringify(item)).join("\n");
    }
    return data?.detail || data?.message || "Request failed. Please check the entered values.";
}

// 1. TRANSITION: LANDING PAGE TO CONSOLE
function launchConsole() {
    const landing = document.getElementById("landing-view");
    const consoleView = document.getElementById("app-console");
    
    // Add fade-out animation classes
    landing.classList.add("fade-out");
    
    setTimeout(() => {
        consoleView.style.display = "flex";
        setTimeout(() => {
            consoleView.classList.add("active");
            switchView("dashboard"); // Default view on console load
        }, 100);
    }, 400);
}

// Bind Open Dashboard Buttons
document.getElementById("btn-launch-console-nav").addEventListener("click", launchConsole);
document.getElementById("btn-launch-console-hero").addEventListener("click", launchConsole);

// 2. COLLAPSIBLE SIDEBAR LOGIC
const sidebar = document.querySelector("aside.console-sidebar");
const toggleBtn = document.getElementById("sidebar-toggle");

toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    const icon = toggleBtn.querySelector("i");
    if (sidebar.classList.contains("collapsed")) {
        icon.className = "fa-solid fa-chevron-right";
        toggleBtn.title = "Expand Menu";
    } else {
        icon.className = "fa-solid fa-chevron-left";
        toggleBtn.title = "Collapse Menu";
    }
});

// Sidebar menu item tab switcher
document.querySelectorAll(".sidebar-menu li").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".sidebar-menu li").forEach(li => li.classList.remove("active"));
        item.classList.add("active");
        
        const viewName = item.getAttribute("data-view");
        switchView(viewName);
    });
});

function switchView(viewName) {
    document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
    const activeSec = document.getElementById(`section-${viewName}`);
    if (activeSec) activeSec.classList.add("active");
    
    // Header text updating
    const titles = {
        dashboard: { title: "Dashboard Overview", sub: "Delivery-risk monitoring, prediction controls, and procurement decision support." },
        prediction: { title: "Delivery Risk Predictor", sub: "Step-wizard machine learning analysis of material delays." },
        suppliers: { title: "Supplier Intelligence", sub: "Reliability scorecards, OTIF performance levels, and lists." },
        planner: { title: "Procurement Planner", sub: "Lead time math and safety buffers scheduling." },
        "what-if": { title: "What-If Simulator", sub: "Operational scenario comparisons and cost delta models." },
        analytics: { title: "Analytics Center", sub: "Aggregated charts, monthly trends, and region indexes." },
        alerts: { title: "Active Risk Alerts", sub: "Early warning signals for critical path shipments." },
        copilot: { title: "AI Procurement Copilot", sub: "Assistant-style interface for procurement and delivery-risk insights." }
    };
    
    const info = titles[viewName] || { title: "Slippage Shield", sub: "" };
    document.getElementById("view-title").textContent = info.title;
    document.getElementById("view-subtitle").textContent = info.sub;
    
    // View-specific loaders
    if (viewName === "dashboard") loadDashboardData();
    if (viewName === "suppliers") loadSupplierData();
    if (viewName === "analytics") loadAnalyticsData();
    if (viewName === "alerts") loadAlertsData();
}

// Theme Switcher for both views
function toggleThemeStyle() {
    if (currentTheme === "dark") {
        document.body.classList.add("light-mode");
        currentTheme = "light";
    } else {
        document.body.classList.remove("light-mode");
        currentTheme = "dark";
    }
}
const themeToggle = document.getElementById("theme-toggle");
if (themeToggle) {
    themeToggle.addEventListener("click", toggleThemeStyle);
}
document.getElementById("theme-toggle-console").addEventListener("click", () => {
    toggleThemeStyle();
    if (document.getElementById("section-analytics").classList.contains("active")) {
        loadAnalyticsData();
    }
});

// User display
const userDisplayName = document.getElementById("user-display-name");
const userDisplayRole = document.getElementById("user-display-role");

if (userDisplayName) {
    userDisplayName.textContent = "Project User";
}

if (userDisplayRole) {
    userDisplayRole.textContent = storedUser.role || "User";
}


// 3. WIZARD CONTROLLER
window.navigateWizard = function(stepNum) {
    // Hide all panels
    document.querySelectorAll(".wizard-panel").forEach(p => p.classList.remove("active"));
    // Show target panel
    document.getElementById(`wizard-panel-${stepNum}`).classList.add("active");
    
    // Update indicator progress bar width
    const progressWidth = ((stepNum - 1) / 2) * 100;
    document.getElementById("wizard-progress").style.width = `${progressWidth}%`;
    
    // Update dots
    for (let i = 1; i <= 3; i++) {
        const dot = document.getElementById(`step-dot-${i}`);
        if (i < stepNum) {
            dot.className = "step-indicator-dot completed";
            dot.innerHTML = '<i class="fa-solid fa-check"></i>';
        } else if (i === stepNum) {
            dot.className = "step-indicator-dot active";
            dot.textContent = i;
        } else {
            dot.className = "step-indicator-dot";
            dot.textContent = i;
        }
    }
};

// 4. LIVE TRANSACTION TICKER FOR LANDING PAGE
function startLiveTickerFeed() {
    const tickerContainer = document.getElementById("landing-live-ticker");
    tickerContainer.innerHTML = "";
    
    const sampleTickerItems = [
        { supplier: "Apex Steel Solutions", material: "Structural Steel Beams", prob: "18%", level: "low" },
        { supplier: "Precast Concrete Specialists", material: "Precast Concrete Stairs", prob: "58%", level: "medium" },
        { supplier: "Metro Facades & Glazing", material: "Double-Glazed Facade Panels", prob: "82%", level: "high" },
        { supplier: "London Merchant Goods", material: "Merchant Cement", prob: "35%", level: "medium" },
        { supplier: "Highland Timber Partners", material: "Timber Joists", prob: "22%", level: "low" }
    ];
    
    // Render initial items
    sampleTickerItems.forEach(item => {
        tickerContainer.insertAdjacentHTML("beforeend", createTickerItemHTML(item));
    });
    
    // Periodically add new items
    setInterval(() => {
        const randomItem = sampleTickerItems[Math.floor(Math.random() * sampleTickerItems.length)];
        
        // Remove first item and slide in new one
        if (tickerContainer.children.length >= 4) {
            tickerContainer.children[0].remove();
        }
        
        tickerContainer.insertAdjacentHTML("beforeend", createTickerItemHTML(randomItem));
    }, 5000);
}

function createTickerItemHTML(item) {
    return `
        <div class="ticker-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700;">${item.material}</span>
                <span class="badge badge-${item.level}">${item.prob} Delay</span>
            </div>
            <div style="font-size:11px; color:var(--text-secondary);">${item.supplier}</div>
        </div>
    `;
}

// 5. MASTER DROP DOWNS POPULATION
async function populateDropdowns() {
    try {
        const supRes = await authFetch(`${API_BASE}/suppliers`);
        const suppliers = await supRes.json();
        
        const matRes = await authFetch(`${API_BASE}/suppliers/materials`);
        const materials = await matRes.json();
        
        const predMat = document.getElementById("pred-material");
        const predSup = document.getElementById("pred-supplier");
        const planMat = document.getElementById("plan-material");
        const planSup = document.getElementById("plan-supplier");
        
        predMat.innerHTML = "";
        predSup.innerHTML = "";
        planMat.innerHTML = "";
        planSup.innerHTML = "";
        
        materials.forEach(m => {
            const opt = `<option value="${m.id}" data-category="${m.category}">${m.material_name} (${m.category})</option>`;
            predMat.insertAdjacentHTML("beforeend", opt);
            planMat.insertAdjacentHTML("beforeend", opt);
        });
        
        suppliers.forEach(s => {
            const opt = `<option value="${s.id}" data-tier="${s.supplier_type}">${s.name} - ${s.supplier_type.replace("  ", " - ")}</option>`;
            predSup.insertAdjacentHTML("beforeend", opt);
            planSup.insertAdjacentHTML("beforeend", opt);
        });
        
        planSup.addEventListener("change", triggerPlannerDefaults);
        planMat.addEventListener("change", triggerPlannerDefaults);
        document.getElementById("plan-required-date").addEventListener("change", triggerPlannerDefaults);
        
    } catch (e) {
        console.error("Error populating select listings", e);
    }
}

// Dynamic pre-population of planner defaults
async function triggerPlannerDefaults() {
    const supplierId = document.getElementById("plan-supplier").value;
    const materialId = document.getElementById("plan-material").value;
    const reqDate = document.getElementById("plan-required-date").value;
    
    if (!supplierId || !materialId || !reqDate) return;
    
    try {
        const res = await authFetch(`${API_BASE}/planner/defaults?supplier_id=${supplierId}&material_id=${materialId}&required_delivery_date=${reqDate}`);
        const defaults = await res.json();
        
        document.getElementById("planner-auto-calc-box").style.display = "block";
        document.getElementById("plan-lead-days-text").textContent = `${defaults.planned_lead_days} Days`;
        
        const delayText = document.getElementById("plan-delay-days-text");
        delayText.textContent = `${defaults.predicted_delay_days} Days`;
        delayText.style.color = defaults.predicted_delay_days > 3 ? "var(--danger)" : "var(--warning)";
        
        document.getElementById("plan-buffer-days-text").textContent = `${defaults.safety_buffer_days} Days`;
        document.getElementById("plan-buffer-input").value = defaults.safety_buffer_days;
        
        document.getElementById("planner-form").dataset.lead = defaults.planned_lead_days;
        document.getElementById("planner-form").dataset.delay = defaults.predicted_delay_days;
    } catch (e) {
        console.error("Error fetching planner defaults", e);
    }
}

// 6. DASHBOARD MODULE DATA LOAD
async function loadDashboardData() {
    try {
        const kpiRes = await authFetch(`${API_BASE}/analytics/kpis`);
        const kpis = await kpiRes.json();
        
        document.getElementById("kpi-total-orders").textContent = kpis.total_orders;
        document.getElementById("kpi-delayed-orders").textContent = kpis.delayed_orders;
        document.getElementById("kpi-active-suppliers").textContent = kpis.active_suppliers;
        document.getElementById("kpi-avg-risk").textContent = `${kpis.average_risk_score}%`;
        document.getElementById("kpi-critical-alerts").textContent = kpis.critical_alerts;
        document.getElementById("kpi-cost-impact").textContent = `£${kpis.expected_cost_impact.toLocaleString()}`;
        
        if (kpis.critical_alerts > 0) {
            const ab = document.getElementById("alert-badge-count");
            ab.textContent = kpis.critical_alerts;
            ab.style.display = "inline-flex";
        }
        
        // Populate deliveries table
        const ordersTable = document.getElementById("dashboard-orders-table");
        ordersTable.innerHTML = "";
        
        const mockOrders = [
            { id: "CSC-DEL-0000000001", supplier: "Metro Facades & Glazing", material: "Double-Glazed Facade Panels", qty: 120, date: "2026-06-15", prob: "82%", level: "HIGH" },
            { id: "CSC-DEL-0000000002", supplier: "Apex Steel Solutions", material: "Structural Steel Beams", qty: 50, date: "2026-06-20", prob: "18%", level: "LOW" },
            { id: "CSC-DEL-0000000003", supplier: "Precast Concrete Specialists", material: "Precast Concrete Stairs", qty: 30, date: "2026-06-18", prob: "58%", level: "MEDIUM" },
            { id: "CSC-DEL-0000000004", supplier: "Rapid Scaffolding Supply", material: "Scaffold Poles & Couplers", qty: 500, date: "2026-06-10", prob: "74%", level: "HIGH" },
            { id: "CSC-DEL-0000000005", supplier: "Midlands MEP Cable Co.", material: "Heavy Duty Copper Cable", qty: 200, date: "2026-06-25", prob: "12%", level: "LOW" }
        ];
        
        mockOrders.forEach(o => {
            const probNum = parseInt(o.prob);
            let barColor = "var(--success)";
            if (o.level === "HIGH") barColor = "var(--danger)";
            else if (o.level === "MEDIUM") barColor = "var(--warning)";
            
            const tr = `
                <tr>
                    <td style="font-weight: 600; color: var(--primary-light);">${o.id}</td>
                    <td>${o.supplier}</td>
                    <td>${o.material}</td>
                    <td>${o.qty}</td>
                    <td>${o.date}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-weight: 700; min-width: 32px;">${o.prob}</span>
                            <div style="flex-grow: 1; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; min-width: 60px; overflow: hidden; position: relative;">
                                <div style="width: ${o.prob}; height: 100%; background: ${barColor}; border-radius: 3px; box-shadow: 0 0 8px ${barColor};"></div>
                            </div>
                        </div>
                    </td>
                    <td><span class="badge badge-${o.level.toLowerCase()}">${o.level}</span></td>
                </tr>
            `;
            ordersTable.insertAdjacentHTML("beforeend", tr);
        });
        
        // Populate alerts list
        const alertsList = document.getElementById("dashboard-alerts-list");
        alertsList.innerHTML = "";
        
        const mockAlerts = [
            { type: "CRITICAL", msg: "Delivery of Double-Glazed Facade Panels from Metro Facades & Glazing has a 82% probability of delay. Expected delay: 6 days." },
            { type: "CRITICAL", msg: "Delivery of Scaffold Poles & Couplers from Rapid Scaffolding Supply has a 74% probability of delay. Expected delay: 5 days." },
            { type: "WARNING", msg: "Delivery of Precast Concrete Stairs from Precast Concrete Specialists has a 58% probability of delay. Expected delay: 3 days." }
        ];
        
        mockAlerts.forEach(a => {
            const severityClass = a.type === 'CRITICAL' ? 'critical-alert' : 'warning-alert';
            const icon = a.type === 'CRITICAL' ? 'fa-circle-exclamation' : 'fa-triangle-exclamation';
            const block = `
                <div class="alert-box ${severityClass}">
                    <div class="alert-box-header">
                        <span class="alert-title-text"><i class="fa-solid ${icon}"></i> ${a.type} SIGNAL</span>
                        <span class="alert-time-text">Just now</span>
                    </div>
                    <p class="alert-message-text">${a.msg}</p>
                </div>
            `;
            alertsList.insertAdjacentHTML("beforeend", block);
        });
        
    } catch (e) {
        console.error("Error loading dashboard data", e);
    }
}
function buildBusinessSummary(data, payload, probabilityPercent) {
    const riskLevel = String(data.risk_level || "LOW").toUpperCase();
    const expectedDelayDays = Number(data.expected_delay_days || 0);
    const committedDate = payload.committed_delivery_date;
    const plannedLeadDays = payload.planned_lead_calendar_days;

    if (riskLevel === "HIGH") {
        return `
            <strong style="color: var(--danger);">High-risk delivery detected.</strong>
            The model estimates a ${probabilityPercent}% probability of delay with an expected delay impact of ${expectedDelayDays} days.
            The committed delivery date is ${committedDate}, and the planned lead time is ${plannedLeadDays} days.
            This delivery should be treated as a priority risk item because it may affect downstream construction activities if not monitored early.
        `;
    }

    if (riskLevel === "MEDIUM") {
        return `
            <strong style="color: var(--warning);">Moderate delivery risk detected.</strong>
            The model estimates a ${probabilityPercent}% probability of delay with an expected delay impact of ${expectedDelayDays} days.
            The committed delivery date is ${committedDate}, and the planned lead time is ${plannedLeadDays} days.
            This delivery does not require immediate escalation, but it should be monitored before the committed gate date.
        `;
    }

    return `
        <strong style="color: var(--success);">Low delivery risk detected.</strong>
        The model estimates a ${probabilityPercent}% probability of delay with an expected delay impact of ${expectedDelayDays} days.
        The committed delivery date is ${committedDate}, and the planned lead time is ${plannedLeadDays} days.
        The delivery can proceed under normal monitoring, while maintaining standard supplier follow-up.
    `;
}

function buildRecommendedActions(data, payload) {
    const riskLevel = String(data.risk_level || "LOW").toUpperCase();

    if (riskLevel === "HIGH") {
        return [
            "Contact the supplier immediately and confirm production or dispatch readiness.",
            "Prepare an alternate supplier or carrier option in case the current delivery slips.",
            "Notify the project planner if this material is linked to critical-path work.",
            "Re-check site access, unloading arrangements, and delivery slot availability.",
            "Monitor this order daily until the committed delivery date."
        ];
    }

    if (riskLevel === "MEDIUM") {
        return [
            "Confirm supplier progress before the committed delivery date.",
            "Track carrier capacity and site access constraints during the delivery week.",
            "Keep a contingency buffer in the work schedule if the material supports near-term tasks.",
            "Review supplier OTIF performance before placing similar future orders.",
            "Escalate only if supplier confirmation is delayed or risk increases."
        ];
    }

    return [
        "Proceed with the current delivery plan.",
        "Continue standard supplier follow-up and documentation.",
        "Maintain normal delivery tracking until gate arrival.",
        "No immediate escalation is required for this delivery.",
        "Re-run prediction if supplier, lead time, or delivery constraints change."
    ];
}

function renderPredictionDecisionSupport(data, payload, probabilityPercent) {
    const summaryElement = document.getElementById("pred-business-summary");
    const actionListElement = document.getElementById("pred-action-plan");

    if (!summaryElement || !actionListElement) {
        return;
    }

    summaryElement.innerHTML = buildBusinessSummary(data, payload, probabilityPercent);

    const actions = buildRecommendedActions(data, payload);
    actionListElement.innerHTML = "";

    actions.forEach((action) => {
        const listItem = document.createElement("li");
        listItem.textContent = action;
        actionListElement.appendChild(listItem);
    });
}
// 7. PREDICTION ENGINE SUBMISSION
document.getElementById("prediction-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const matSelect = document.getElementById("pred-material");
    const supSelect = document.getElementById("pred-supplier");
    
    const matOpt = matSelect.options[matSelect.selectedIndex];
    const supOpt = supSelect.options[supSelect.selectedIndex];
    
    const dateInput = document.getElementById("pred-date");
    const committedDate = normalizeDateInputValue(dateInput);
    const plannedLeadDays = parseInt(document.getElementById("pred-lead").value, 10);

    if (!committedDate) {
        alert("Committed delivery date is required. Please select a valid committed delivery date from the date picker.");
        return;
    }

    if (!Number.isFinite(plannedLeadDays) || plannedLeadDays <= 0) {
        alert("Planned lead time must be a valid number greater than 0.");
        return;
    }

    // Keep the value sent to the backend as YYYY-MM-DD even if the browser displays DD-MM-YYYY.
    dateInput.value = committedDate;

    const scheduleError = validatePredictionSchedule(committedDate, plannedLeadDays);
    if (scheduleError) {
        alert(scheduleError);
        return;
    }

    const payload = {
        committed_delivery_date: committedDate,
        planned_lead_calendar_days: plannedLeadDays,
        distance_supplier_to_site_km: parseInt(document.getElementById("pred-distance").value),
        material_category: matOpt.getAttribute("data-category"),
        supplier_tier: supOpt.getAttribute("data-tier"),
        delivery_terms: document.getElementById("pred-terms").value,
        site_access_restriction_level: document.getElementById("pred-restriction").value,
        project_sector: document.getElementById("pred-sector").value,
        region_site: document.getElementById("pred-region").value,
        order_value_band_gbp: document.getElementById("pred-value").value,
        shipment_mode: document.getElementById("pred-shipment").value,
        import_or_customs_hold_liable: document.getElementById("pred-import").value,
        made_to_order_or_long_fabrication: "Yes",
        upstream_delay_flag_programme: "No",
        market_shortage_stress_band: "Moderate",
        po_line_changes_before_release_count: 0,
        weather_or_temperature_sensitive_goods: "No",
        busy_season_construction_index: "Typical",
        jit_critical_path_item: "No",
        supplier_rolling_otif_band: "85%  94%",
        haulier_capacity_stress_quarter: "No",
        packaging_handling_complexity: "Standard Pallet / Bulk"
    };
    
    try {
        const res = await authFetch(`${API_BASE}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (!res.ok) {
            alert(getApiErrorMessage(data));
            return;
        }
        
        document.getElementById("pred-empty-state").style.display = "none";
        document.getElementById("pred-results-content").style.display = "flex";
        
        const probPct = Math.round(data.delay_probability * 100);
        document.getElementById("pred-prob-val").textContent = `${probPct}%`;
        
        const gaugeSvg = document.getElementById("pred-gauge-svg");
        let gaugeColor = "var(--success)";
        if (data.risk_level === "HIGH") gaugeColor = "var(--danger)";
        else if (data.risk_level === "MEDIUM") gaugeColor = "var(--warning)";
        
        const circumference = 408.4;
        const offset = circumference - (probPct / 100) * circumference;
        gaugeSvg.style.strokeDashoffset = offset;
        gaugeSvg.style.stroke = gaugeColor;
        
        const rBadge = document.getElementById("pred-risk-badge-text");
        rBadge.textContent = `${data.risk_level} RISK`;
        rBadge.style.color = gaugeColor;
        
        document.getElementById("pred-delay-days-val").textContent = `${data.expected_delay_days} Days`;
        document.getElementById("pred-ai-explanation").innerHTML = data.ai_explanation.replace(/\n/g, "<br>");
        renderPredictionDecisionSupport(data, payload, probPct);
        
        // Feature contribution chart
        const shapContainer = document.getElementById("pred-shap-container");
        shapContainer.innerHTML = "";
        
        const maxShap = Math.max(...data.shap_features.map(f => Math.abs(f.shap_value)), 0.05);
        
        data.shap_features.forEach(f => {
            const isPos = f.shap_value > 0;
            const widthPct = Math.min(100, Math.round((Math.abs(f.shap_value) / maxShap) * 50));
            
            const barRow = `
                <div class="shap-bar-row">
                    <span class="shap-label" title="${f.display_name}">${f.display_name}</span>
                    <div class="shap-bar-axis">
                        <div class="shap-bar ${isPos ? 'positive' : 'negative'}" style="width: ${widthPct}%; ${isPos ? 'left:50%;' : 'right:50%;'}"></div>
                    </div>
                    <span class="shap-val-text" style="color: ${isPos ? 'var(--danger)' : 'var(--success)'}; text-align: ${isPos ? 'left' : 'right'}">
                        ${isPos ? '+' : ''}${f.shap_value.toFixed(3)}
                    </span>
                </div>
            `;
            shapContainer.insertAdjacentHTML("beforeend", barRow);
        });
        
    } catch (e) {
        console.error("Error running ML prediction", e);
    }
});

// 8. SUPPLIER INTELLIGENCE LOAD
async function loadSupplierData() {
    try {
        const res = await authFetch(`${API_BASE}/suppliers`);
        const suppliers = await res.json();
        
        const topTable = document.getElementById("suppliers-top-performers-table");
        const riskTable = document.getElementById("suppliers-high-risk-table");
        const masterTable = document.getElementById("suppliers-master-table");
        
        topTable.innerHTML = "";
        riskTable.innerHTML = "";
        masterTable.innerHTML = "";
        
        const top5 = [...suppliers].filter(s => s.reliability_score >= 75).slice(0, 5);
        const risk5 = [...suppliers].filter(s => s.risk_score >= 50).sort((a,b) => b.risk_score - a.risk_score).slice(0, 5);
        
        top5.forEach(s => {
            topTable.insertAdjacentHTML("beforeend", `
                <tr>
                    <td style="font-weight: 600;">${s.name}</td>
                    <td>${s.supplier_type.replace("  ", " - ")}</td>
                    <td><strong style="color: var(--success);"><i class="fa-solid fa-star"></i> ${s.performance_rating}/5.0</strong></td>
                    <td><span class="badge badge-low">${s.reliability_score} / 100</span></td>
                </tr>
            `);
        });
        
        risk5.forEach(s => {
            riskTable.insertAdjacentHTML("beforeend", `
                <tr>
                    <td style="font-weight: 600; color: var(--danger);">${s.name}</td>
                    <td>${s.supplier_type.replace("  ", " - ")}</td>
                    <td>${s.delayed_orders} delays</td>
                    <td><span class="badge badge-high">${s.risk_score} / 100</span></td>
                </tr>
            `);
        });
        
        suppliers.forEach(s => {
            masterTable.insertAdjacentHTML("beforeend", `
                <tr>
                    <td style="font-weight: 600;">${s.name}</td>
                    <td>${s.supplier_type.replace("  ", " - ")}</td>
                    <td><strong style="color: ${s.risk_score > 60 ? 'var(--danger)' : s.risk_score > 30 ? 'var(--warning)' : 'var(--success)'};">${s.risk_score}%</strong></td>
                    <td>${s.performance_rating}/5.0</td>
                    <td>${s.total_orders}</td>
                    <td>${s.delivery_success_rate}%</td>
                    <td>${s.average_delay_days} days</td>
                </tr>
            `);
        });
        
    } catch (e) {
        console.error("Error loading supplier profiles", e);
    }
}

// Supplier search input
document.getElementById("supplier-search-input").addEventListener("input", (e) => {
    const val = e.target.value.toLowerCase();
    document.querySelectorAll("#suppliers-master-table tr").forEach(tr => {
        const text = tr.textContent.toLowerCase();
        tr.style.display = text.includes(val) ? "" : "none";
    });
});

// 9. PROCUREMENT PLANNER CALCULATIONS
document.getElementById("planner-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const requiredDateInput = document.getElementById("plan-required-date");
    const reqDate = normalizeDateInputValue(requiredDateInput);
    if (!reqDate) {
        alert("Required delivery date is required. Please select a valid required delivery date from the date picker.");
        return;
    }
    requiredDateInput.value = reqDate;

    const buffer = parseInt(document.getElementById("plan-buffer-input").value);
    const lead = parseInt(document.getElementById("planner-form").dataset.lead || 30);
    const delay = parseInt(document.getElementById("planner-form").dataset.delay || 0);
    
    const payload = {
        required_delivery_date: reqDate,
        predicted_delay_days: delay,
        safety_buffer_days: buffer,
        planned_lead_days: lead
    };
    
    try {
        const res = await authFetch(`${API_BASE}/planner/calculate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (!res.ok) {
            alert(getApiErrorMessage(data));
            return;
        }
        
        document.getElementById("planner-empty-state").style.display = "none";
        document.getElementById("planner-results").style.display = "flex";
        
        document.getElementById("planner-rec-date-text").textContent = data.recommended_order_date;
        document.getElementById("planner-summary-paragraph").textContent = `Place order before ${data.recommended_order_date} to offset the estimated lead window of ${data.total_lead_time_days} days.`;
        
        document.getElementById("planner-row-req-date").textContent = data.required_delivery_date;
        document.getElementById("planner-row-lead-days").textContent = `${data.planned_lead_days} days`;
        document.getElementById("planner-row-delay-days").textContent = `+${data.predicted_delay_days} days`;
        document.getElementById("planner-row-buffer-days").textContent = `+${data.safety_buffer_days} days`;
        document.getElementById("planner-row-total-days").textContent = `${data.total_lead_time_days} days`;
        
    } catch (e) {
        console.error("Error running planner calculation", e);
    }
});

// 10. WHAT-IF SCENARIO COMPARATOR
document.getElementById("what-if-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const whatIfDateInput = document.getElementById("what-if-date");
    const whatIfDate = normalizeDateInputValue(whatIfDateInput);
    if (!whatIfDate) {
        alert("Target date is required. Please select a valid target date from the date picker.");
        return;
    }
    whatIfDateInput.value = whatIfDate;

    const payload = {
        material_category: document.getElementById("what-if-category").value,
        current_supplier_tier: document.getElementById("what-if-current-tier").value,
        target_supplier_tier: document.getElementById("what-if-target-tier").value,
        current_shipment_mode: document.getElementById("what-if-current-shipment").value,
        target_shipment_mode: document.getElementById("what-if-target-shipment").value,
        committed_delivery_date: whatIfDate
    };
    
    try {
        const res = await authFetch(`${API_BASE}/what-if/simulate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (!res.ok) {
            alert(getApiErrorMessage(data));
            return;
        }
        
        document.getElementById("what-if-results-card").style.display = "block";
        
        document.getElementById("what-if-kpi-current-risk").textContent = `${data.current_risk_score}%`;
        document.getElementById("what-if-kpi-target-risk").textContent = `${data.target_risk_score}%`;
        
        const diffText = document.getElementById("what-if-kpi-diff");
        if (data.risk_difference > 0) {
            diffText.textContent = `-${Math.abs(data.risk_difference)}%`;
            diffText.style.color = "var(--success)";
        } else if (data.risk_difference < 0) {
            diffText.textContent = `+${Math.abs(data.risk_difference)}%`;
            diffText.style.color = "var(--danger)";
        } else {
            diffText.textContent = "0%";
            diffText.style.color = "var(--text-primary)";
        }
        
        const costText = document.getElementById("what-if-kpi-cost");
        if (data.expected_cost_saving_gbp > 0) {
            costText.textContent = `Saving: £${data.expected_cost_saving_gbp.toLocaleString()}`;
            costText.style.color = "var(--success)";
        } else if (data.expected_cost_saving_gbp < 0) {
            costText.textContent = `Premium: +£${Math.abs(data.expected_cost_saving_gbp).toLocaleString()}`;
            costText.style.color = "var(--warning)";
        } else {
            costText.textContent = "Neutral";
            costText.style.color = "var(--text-primary)";
        }
        
        document.getElementById("what-if-days-saved-text").textContent = `${data.expected_delay_days_saved} days`;
        
    } catch (e) {
        console.error("Error executing what-if simulation", e);
    }
});

// 11. ANALYTICS CHARTS (Chart.js)
async function loadAnalyticsData() {
    try {
        const res = await authFetch(`${API_BASE}/analytics/charts`);
        const data = await res.json();
        
        const ctxTrend = document.getElementById("chart-monthly-trend").getContext("2d");
        if (charts["trend"]) charts["trend"].destroy();
        
        const isDark = currentTheme === "dark";
        const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
        const textColor = isDark ? "#94a3b8" : "#475569";
        
        charts["trend"] = new Chart(ctxTrend, {
            type: "bar",
            data: {
                labels: data.monthly_delay_trend.map(d => d.month),
                datasets: [
                    {
                        label: "Delayed",
                        data: data.monthly_delay_trend.map(d => d.delayed_deliveries),
                        backgroundColor: "#ef4444",
                        borderRadius: 6
                    },
                    {
                        label: "On-Time",
                        data: data.monthly_delay_trend.map(d => d.on_time_deliveries),
                        backgroundColor: "#10b981",
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, grid: { display: false }, ticks: { color: textColor, font: { family: "Plus Jakarta Sans" } } },
                    y: { stacked: true, grid: { color: gridColor }, ticks: { color: textColor, font: { family: "Plus Jakarta Sans" } } }
                },
                plugins: {
                    legend: { labels: { color: textColor, font: { family: "Plus Jakarta Sans", weight: "500" } } }
                }
            }
        });
        
        const ctxRank = document.getElementById("chart-supplier-ranking").getContext("2d");
        if (charts["rank"]) charts["rank"].destroy();
        
        charts["rank"] = new Chart(ctxRank, {
            type: "bar",
            data: {
                labels: data.supplier_risk_ranking.map(s => s.name),
                datasets: [{
                    label: "Risk Score (%)",
                    data: data.supplier_risk_ranking.map(s => s.risk_score),
                    backgroundColor: data.supplier_risk_ranking.map(s => s.risk_score > 60 ? "rgba(239, 68, 68, 0.85)" : "rgba(245, 158, 11, 0.85)"),
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: "y",
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor, font: { family: "Plus Jakarta Sans" } }, max: 100 },
                    y: { grid: { display: false }, ticks: { color: textColor, font: { family: "Plus Jakarta Sans" } } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
        
        const matTable = document.getElementById("analytics-material-categories-table");
        matTable.innerHTML = "";
        data.high_risk_material_categories.forEach(m => {
            matTable.insertAdjacentHTML("beforeend", `
                <tr>
                    <td style="font-weight: 600;">${m.category}</td>
                    <td><strong style="color: ${m.average_risk > 50 ? 'var(--danger)' : 'var(--warning)'};">${m.average_risk}%</strong></td>
                    <td>${m.volume}</td>
                </tr>
            `);
        });
        
        const projTable = document.getElementById("analytics-projects-heatmap-table");
        projTable.innerHTML = "";
        data.project_risk_heatmap.forEach(p => {
            const hs = data.project_health_scores.find(h => h.project_name === p.project_name) || {health_score: 80, status: "STABLE"};
            projTable.insertAdjacentHTML("beforeend", `
                <tr>
                    <td style="font-weight: 600;">${p.project_name}</td>
                    <td>${p.region}</td>
                    <td><strong>${p.risk_index}%</strong></td>
                    <td><span class="badge badge-${hs.status.toLowerCase()}">${hs.status} (Health: ${hs.health_score})</span></td>
                </tr>
            `);
        });
        
    } catch (e) {
        console.error("Error rendering charts", e);
    }
}

// 12. ALERTS LOG DATA LOAD
async function loadAlertsData() {
    try {
        const table = document.getElementById("alerts-master-table");
        table.innerHTML = "";
        
        const mockAlerts = [
            { type: "CRITICAL", order: "CSC-DEL-0000000001", msg: "Delivery of Double-Glazed Facade Panels from Metro Facades & Glazing has a 82% probability of delay. Expected delay: 6 days. This item is on the project critical path.", time: "2026-06-03 10:15:33" },
            { type: "CRITICAL", order: "CSC-DEL-0000000004", msg: "Delivery of Scaffold Poles & Couplers from Rapid Scaffolding Supply has a 74% probability of delay. Expected delay: 5 days.", time: "2026-06-03 09:42:15" },
            { type: "WARNING", order: "CSC-DEL-0000000003", msg: "Delivery of Precast Concrete Stairs from Precast Concrete Specialists has a 58% probability of delay. Expected delay: 3 days.", time: "2026-06-03 08:30:00" }
        ];
        
        mockAlerts.forEach(a => {
            table.insertAdjacentHTML("beforeend", `
                <tr>
                    <td><span class="badge badge-${a.type.toLowerCase()}">${a.type}</span></td>
                    <td style="font-weight: 600;">${a.order}</td>
                    <td>${a.msg}</td>
                    <td>${a.time}</td>
                </tr>
            `);
        });
        
    } catch (e) {
        console.error("Error loading alerts logs", e);
    }
}

// 13. COPILOT DIALOGUE CONTROLLER
const chatHistory = document.getElementById("copilot-chat-history");
const chatInput = document.getElementById("copilot-user-input");
const sendBtn = document.getElementById("copilot-send-btn");

sendBtn.addEventListener("click", sendCopilotMessage);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendCopilotMessage();
});

async function sendCopilotMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    chatInput.value = "";
    chatHistory.insertAdjacentHTML("beforeend", `
        <div class="chat-msg user">${text}</div>
    `);
    
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    const typingId = `typing-${Date.now()}`;
    chatHistory.insertAdjacentHTML("beforeend", `
        <div class="chat-msg assistant" id="${typingId}">
            <i class="fa-solid fa-spinner fa-spin-pulse"></i> Searching predictive records...
        </div>
    `);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        const res = await authFetch(`${API_BASE}/copilot/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: text })
        });
        
        const data = await res.json();
        document.getElementById(typingId).remove();
        
        const sourcesTags = data.sources.map(s => `<span class="chat-source-tag"><i class="fa-solid fa-file-invoice"></i> ${s}</span>`).join("");
        
        chatHistory.insertAdjacentHTML("beforeend", `
            <div class="chat-msg assistant">
                ${data.answer.replace(/\n/g, "<br>")}
                <div class="chat-sources">
                    ${sourcesTags}
                </div>
            </div>
        `);
        
    } catch (e) {
        document.getElementById(typingId).innerHTML = "Sorry, I experienced an error matching our database coordinates.";
    }
    
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

window.askCopilotQuick = function(question) {
    document.querySelectorAll(".sidebar-menu li").forEach(li => li.classList.remove("active"));
    document.querySelector("[data-view='copilot']").classList.add("active");
    switchView("copilot");
    
    chatInput.value = question;
    sendCopilotMessage();
};

// Sync controls
document.getElementById("refresh-db-btn").addEventListener("click", () => {
    loadDashboardData();
    if (document.getElementById("section-suppliers").classList.contains("active")) loadSupplierData();
    if (document.getElementById("section-analytics").classList.contains("active")) loadAnalyticsData();
    if (document.getElementById("section-alerts").classList.contains("active")) loadAlertsData();
    
    const syncBtn = document.getElementById("refresh-db-btn");
    syncBtn.innerHTML = '<i class="fa-solid fa-check"></i> Synchronized';
    setTimeout(() => {
        syncBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Sync Data';
    }, 2000);
});

// Excel download endpoints
document.getElementById("export-risk-btn").addEventListener("click", () => window.open(`${API_BASE}/reports/risk-assessment`));
document.getElementById("export-supplier-btn").addEventListener("click", () => window.open(`${API_BASE}/reports/suppliers`));
document.getElementById("export-planning-btn").addEventListener("click", () => window.open(`${API_BASE}/reports/planning`));
document.getElementById("export-analytics-project-btn").addEventListener("click", () => window.open(`${API_BASE}/reports/project-delays`));

// Init on DOM ready
window.addEventListener("DOMContentLoaded", () => {
    initializeDateControls();
    startLiveTickerFeed();
    populateDropdowns();
    
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 14);
    const formattedTomorrow = toIsoDate(tomorrow);
    
    document.getElementById("pred-date").value = formattedTomorrow;
    document.getElementById("plan-required-date").value = formattedTomorrow;
    document.getElementById("what-if-date").value = formattedTomorrow;
});
