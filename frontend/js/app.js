// Base URL for API (Change if testing across local Wi-Fi network)
const API_BASE_URL = "http://localhost:8000";

// let currentTab = 'scan';
let currentTab = 'manual';
let isProcessing = false;

document.addEventListener('DOMContentLoaded', () => {
  checkBackendHealth();
  // initScanner();
});

// Check if FastAPI backend is online
async function checkBackendHealth() {
  const statusEl = document.getElementById('api-status');
  try {
    const res = await fetch(`${API_BASE_URL}/`);
    if (res.ok) {
      statusEl.textContent = "Online";
      statusEl.className = "font-mono text-emerald-600 font-semibold";
    } else {
      throw new Error();
    }
  } catch (err) {
    statusEl.textContent = "Offline / Unreachable";
    statusEl.className = "font-mono text-rose-600 font-semibold";
  }
}

// Tab navigation handler
function switchTab(tab) {
  currentTab = tab;
  ['manual', 'scan', 'admin'].forEach(t => {
    const btn = document.getElementById(`tab-${t}`);
    const view = document.getElementById(`view-${t}`);
    
    if (t === tab) {
      btn.className = "flex-1 py-2 text-sm font-semibold rounded-lg bg-indigo-600 text-white transition shadow";
      view.classList.remove('hidden');
      view.classList.add('flex');
    } else {
      btn.className = "flex-1 py-2 text-sm font-semibold rounded-lg text-slate-600 hover:bg-slate-100 transition";
      view.classList.add('hidden');
      view.classList.remove('flex');
    }
  });

  if (tab === 'scan') {
    if (!html5QrCode) {
      initScanner();
    } else {
      startScanner();
    }
  } else {
    stopScanner();
  }
}

// Display alert messages (Success 🟢, Duplicate 🔴, Not Found 🟡)
function showStatus(type, message, detail = "") {
  const card = document.getElementById('status-card');
  const msgEl = document.getElementById('status-message');
  const detailEl = document.getElementById('status-detail');

  card.classList.remove('hidden', 'bg-emerald-100', 'text-emerald-800', 'bg-rose-100', 'text-rose-800', 'bg-amber-100', 'text-amber-800');

  if (type === 'success') {
    card.classList.add('bg-emerald-100', 'text-emerald-800');
  } else if (type === 'duplicate') {
    card.classList.add('bg-rose-100', 'text-rose-800');
  } else {
    card.classList.add('bg-amber-100', 'text-amber-800');
  }

  msgEl.textContent = message;
  detailEl.textContent = detail;

  // Auto-hide banner after 4 seconds
  setTimeout(() => {
    card.classList.add('hidden');
  }, 4000);
}

// Send delivery scan to FastAPI backend
async function sendDeliveryRecord(studentId) {
  if (isProcessing) return;
  isProcessing = true;

  try {
    const res = await fetch(`${API_BASE_URL}/api/deliver`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, staff_user: "Staff-Mobile" })
    });

    const data = await res.json();

    if (res.ok) {
      showStatus('success', '🟢 Snack Delivered!', `${data.student_name} (${studentId})`);
    } else if (res.status === 409) {
      showStatus('duplicate', '🔴 Already Delivered Today!', data.detail);
    } else if (res.status === 404) {
      showStatus('warning', '🟡 Student Not Found', data.detail);
    } else {
      showStatus('warning', '⚠️ Error Processing Delivery', data.detail || "Server error.");
    }
  } catch (err) {
    showStatus('duplicate', '❌ Connection Error', "Unable to reach the backend server.");
  } finally {
    // Cooldown pause before allowing next scan
    setTimeout(() => { isProcessing = false; }, 2500);
  }
}

// Manual delivery submission
function submitManualDelivery() {
  const input = document.getElementById('manual-id');
  const val = input.value.trim();
  if (val) {
    sendDeliveryRecord(val);
    input.value = '';
  }
}

// Trigger printable PDF download from API
function downloadPDF() {
  window.open(`${API_BASE_URL}/api/generate-pdf`, '_blank');
}