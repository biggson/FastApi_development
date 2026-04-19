// Local development
//const API = "http://127.0.0.1:8001";

// Production — Azure Container Apps
const API = "https://boarder-api.calmgrass-7d4f20d8.eastus.azurecontainerapps.io";

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("inv_token");
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(API + path, { ...options, headers });

  if (res.status === 401) {
    logout();
    return null;
  }

  return res;
}

async function apiGet(path) {
  return apiFetch(path, { method: "GET" });
}

async function apiPost(path, body) {
  return apiFetch(path, { method: "POST", body: JSON.stringify(body) });
}

async function apiPut(path, body) {
  return apiFetch(path, { method: "PUT", body: JSON.stringify(body) });
}

async function apiDelete(path) {
  return apiFetch(path, { method: "DELETE" });
}

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = message;
    el.classList.remove("hidden");
  }
}

function hideError(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.classList.add("hidden");
}

function showSuccess(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = message;
    el.classList.remove("hidden");
    setTimeout(() => el.classList.add("hidden"), 3000);
  }
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });
}

function formatCurrency(amount) {
  if (amount == null) return "—";
  return "$" + Number(amount).toFixed(2);
}
