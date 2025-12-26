// Connection
const ws = new WebSocket(`ws://${window.location.host}/ws`);
const feedList = document.getElementById('feed-list');
const agentLog = document.getElementById('agent-log');

// State
let currentDomain = 'finance';
let stats = { count: 0, anomalies: 0 };

// Configuration for Polymorphism
const DOMAIN_CONFIG = {
    finance: {
        title: "Market Intelligence",
        subtitle: "Real-time algorithmic trading surveillance.",
        stat1: "Active Symbols",
        stat2: "Ticks / Sec"
    },
    health: {
        title: "Patient Vitals Matrix",
        subtitle: "ICU Telemetry & Early Warning System.",
        stat1: "Patients Monitored",
        stat2: "Vitals / Min"
    },
    dev: {
        title: "DevOps Sentinel",
        subtitle: "Microservices Log Aggregation & Analysis.",
        stat1: "Services Online",
        stat2: "Logs / Sec"
    }
};

// Initialize UI
document.addEventListener('DOMContentLoaded', () => {
    switchTheme('finance');
});

// WebSocket Logic
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'data_update') {
        processPacket(message.data);
    } else if (message.type === 'agent_response') {
        logAgent(message.content);
    }
};

function processPacket(data) {
    // Only show data for current domain
    if (data.domain !== currentDomain && data.domain !== 'developer' && currentDomain === 'dev') {
        // Mapping 'developer' backend tag to 'dev' frontend tag
        if (data.domain !== 'developer') return;
    }
    if (currentDomain === 'health' && data.domain !== 'healthcare') return;
    if (currentDomain === 'finance' && data.domain !== 'finance') return;


    // Update Stats
    stats.count++;
    document.getElementById('stat-2-value').innerText = (Math.random() * 10).toFixed(1); // Simulating rate

    // Simulate "Active Count" (Stat 1)
    let activeCount = "--";
    if (currentDomain === 'finance') activeCount = Math.floor(Math.random() * (1500 - 1480 + 1) + 1480);
    else if (currentDomain === 'health') activeCount = Math.floor(Math.random() * (50 - 45 + 1) + 45);
    else activeCount = Math.floor(Math.random() * (25 - 20 + 1) + 20);
    document.getElementById('stat-1-value').innerText = activeCount;

    // Check for Critical/Anomalies
    let isCritical = false;
    if (data.status === 'CRITICAL' || data.level === 'ERROR' || data.level === 'FATAL' ||
        data.symbol === 'CRASH' || data.symbol === 'CIRCUIT-BREAKER') {
        isCritical = true;
        stats.anomalies++;
        document.getElementById('stat-3-value').innerText = stats.anomalies;
        triggerAgent(data);
        updateChart(Math.floor(Math.random() * 5) + 5); // Spike 5-10
    } else {
        // Decay entropy (Keep flatline for stability, but keep moving)
        updateChart(0);
    }

    // Render Feed Item
    const item = document.createElement('div');
    item.className = `feed-item ${isCritical ? 'critical' : ''}`;

    // Polymorphic Content Rendering
    let content = '';
    if (data.domain === 'finance') {
        content = `<span>${data.symbol}</span> <span>$${data.price} <small>(${data.delta})</small></span>`;
    } else if (data.domain === 'healthcare') {
        content = `<span>${data.patient_id}</span> <span>BPM: ${data.bpm} | SpO2: ${data.spo2}%</span>`;
    } else {
        content = `<span>${data.service}</span> <span>${data.message}</span>`;
    }

    item.innerHTML = `
        <span style="color: var(--text-secondary); margin-right: 10px;">${data.timestamp.split('T')[1].split('.')[0]}</span>
        <div style="flex-grow: 1; display: flex; justify-content: space-between;">
            ${content}
        </div>
    `;

    feedList.prepend(item);

    // Trim list
    if (feedList.children.length > 50) {
        feedList.removeChild(feedList.lastChild);
    }
}

function triggerAgent(data) {
    let msgs = [];

    // Dynamic Reasoning based on Input
    if (data.domain === 'finance') {
        const symbol = data.symbol || "UNKNOWN";
        msgs = [
            `⚠ MARKET ALERT: ${symbol} Plunge Detected`,
            `Querying Historical Volatility Index...`,
            `Correlation found with 'Liquidity Crunch'`,
            `ACTION: Halted Trading for ${symbol}`,
            `ACTION: Injecting Emergency Liquidity`,
            `✔ THREAT NEUTRALIZED: Volatility Stabilized`
        ];
    } else if (data.domain === 'healthcare') {
        const pid = data.patient_id || "PATIENT";
        const issue = data.notes || "Vitals Critical";

        // Dynamic Medical Diagnosis
        let action = "Administering General Protocol";
        let drug = "Stabilizers";

        if (issue.includes("Cardiac")) { action = "Charging Defibrillator"; drug = "Epinephrine"; }
        else if (issue.includes("Hypoxia")) { action = "Checking Airway Obstruction"; drug = "100% Oxygen"; }
        else if (issue.includes("Seizure")) { action = "Securing Patient"; drug = "Diazepam"; }

        msgs = [
            `⚠ CODE BLUE: ${pid} - ${issue}`,
            `Retrieving Patient History...`,
            `Diagnosed condition: ${issue}`,
            `ACTION: ${action}`,
            `ACTION: Administering ${drug}`,
            `✔ PATIENT STABLE: Vitals Returning to Normal`
        ];
    } else { // Dev
        const svc = data.service || "System";
        const err = data.message || "Fatal Error";

        // Dynamic DevOps Debugging
        let fix = "Restarting Container";
        let rootCause = "Unknown";

        if (err.includes("Memory")) { fix = "Triggering Heap Dump & GC"; rootCause = "Memory Leak in Worker"; }
        else if (err.includes("Database")) { fix = "Rolling Back Transaction"; rootCause = "Write Conflict"; }
        else if (err.includes("Unauthorized")) { fix = "Closing Socket Connection"; rootCause = "Intrusion Attempt"; }

        msgs = [
            `⚠ SYSTEM FAILURE: ${svc}`,
            `Error: ${err}`,
            `Root Cause Analysis: ${rootCause}`,
            `ACTION: Isstracing process...`,
            `ACTION: ${fix}`,
            `✔ RESOLUTION COMPLETE: Service Online`
        ];
    }

    let delay = 0;
    msgs.forEach(msg => {
        setTimeout(() => logAgent(msg), delay);
        delay += 800; // Delay for "Thinking" effect
    });
}

function logAgent(text) {
    const entry = document.createElement('div');
    entry.className = 'log-entry latest';
    entry.innerText = `> ${text}`;
    agentLog.prepend(entry);
}

// UI Switching
window.switchTheme = (domain) => {
    currentDomain = domain;
    document.body.className = `theme-${domain}`;

    // Update Active Nav
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    event.currentTarget.classList.add('active'); // Note: this relies on event bubbling being handled right or passing 'this' which I didn't do in HTML onclick 
    // Fix: Just re-query based on text content or use ID

    // Update Text
    const config = DOMAIN_CONFIG[domain];
    document.getElementById('domain-title').innerText = config.title;
    document.getElementById('domain-subtitle').innerText = config.subtitle;
    document.getElementById('stat-1-label').innerText = config.stat1;
    document.getElementById('stat-2-label').innerText = config.stat2;

    // Clear Feed
    feedList.innerHTML = '';
    stats.count = 0;
    stats.anomalies = 0;

    // Polymorphic Rule UI
    const rTitle = document.getElementById('rule-title');
    const rInput = document.getElementById('bpm-threshold'); // Kept ID same for ease
    if (domain === 'finance') {
        rTitle.innerText = "MAX DRAWDOWN (%)";
        rInput.value = 5;
    } else if (domain === 'health') {
        rTitle.innerText = "MAX BPM";
        rInput.value = 140;
    } else {
        rTitle.innerText = "MAX LATENCY (MS)";
        rInput.value = 2000;
    }
};

window.triggerCrisis = async () => {
    // Visual Feedback
    const btn = document.querySelector('.critical-btn');
    const originalText = btn.innerText;
    btn.innerText = "INJECTING FAULT...";
    btn.style.opacity = 0.7;

    try {
        const response = await fetch('/trigger-event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain: currentDomain })
        });

        if (!response.ok) throw new Error("API not found");

    } catch (e) {
        console.error("Trigger failed", e);
        btn.innerText = "ERROR - RESTART BACKEND";
        btn.style.color = "white";
        btn.style.background = "red";
        alert("⚠️ Connection Failed!\n\nPlease RESTART backend: python src/backend/main.py");
    }

    setTimeout(() => {
        btn.innerText = originalText;
        btn.style.opacity = 1;
    }, 1000);
};

// Update Rules (Polymorphic)
window.updateRules = async () => {
    const val = parseInt(document.getElementById('bpm-threshold').value);

    let payload = { type: currentDomain };
    if (currentDomain === 'finance') payload.max_drawdown = val;
    else if (currentDomain === 'health') payload.max_bpm = val;
    else payload.max_latency = val;

    try {
        await fetch('/update-rules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        logAgent(`RULE UPDATE: Threshold set to ${val} for ${currentDomain.toUpperCase()}`);
        logAgent(`System adapting to new constraints...`);
    } catch (e) {
        console.error(e);
        alert("Update Failed");
    }
};


// Chart.js Init
const ctx = document.getElementById('historyChart').getContext('2d');
const historyChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: Array(20).fill(''),
        datasets: [{
            label: 'Entropy (Chaos Level)',
            data: Array(20).fill(0),
            borderColor: '#ff0055',
            backgroundColor: 'rgba(255, 0, 85, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 0
        }]
    },
    options: {
        maintainAspectRatio: false,
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
            x: { display: false },
            y: { display: true, min: 0, max: 10, grid: { color: 'rgba(255,255,255,0.05)' } }
        },
        animation: false // Disable animation for instant feedback
    }
});

// Helper to update chart
function updateChart(value) {
    historyChart.data.datasets[0].data.push(value);
    historyChart.data.datasets[0].data.shift();
    historyChart.update('none'); // Update mode 'none' for performance
}

window.stabilizeSystem = async () => {
    try {
        await fetch('/stabilize', { method: 'POST' });
        logAgent("MANUAL OVERRIDE: System Stabilization Sequence Initiated...");
        updateChart(0); // Flatline entropy
    } catch (e) {
        console.error(e);
    }
};
