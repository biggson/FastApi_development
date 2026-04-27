function requireAuth() {
  const token = localStorage.getItem("inv_token");
  if (!token) {
    window.location.href = "index.html";
  }
}

function getUser() {
  const raw = localStorage.getItem("inv_user");
  try { return raw ? JSON.parse(raw) : null; } catch { return null; }
}

function isAdmin() {
  const user = getUser();
  return user && user.role === "admin";
}


function logout() {
  localStorage.removeItem("inv_token");
  localStorage.removeItem("inv_user");
  window.location.href = "index.html";
}

function setNavUser() {
  const user = getUser();
  const el = document.getElementById("nav-username");
  if (el && user) {
    el.textContent = user.first_name
      ? `${user.first_name} ${user.last_name || ""}`.trim()
      : user.username;
  }
  // Hide admin-only nav items for regular users
  if (!isAdmin()) {
    document.querySelectorAll(".admin-only").forEach(el => el.classList.add("hidden"));
  }
}

async function login(usernameOrEmail, password) {
  const body = { password };
  if (usernameOrEmail.includes("@")) {
    body.email = usernameOrEmail;
  } else {
    body.username = usernameOrEmail;
  }

  const res = await apiPost("/auth/login", body);
  if (!res) return { ok: false, error: "No response from server" };

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    return { ok: false, error: data.detail || "Login failed" };
  }

  const token = await res.json();
  localStorage.setItem("inv_token", token.access_token);

  // Fetch current user info
  const meRes = await apiGet("/users/me");
  if (meRes && meRes.ok) {
    const user = await meRes.json();
    localStorage.setItem("inv_user", JSON.stringify(user));
  }

  return { ok: true };
}

async function register(data) {
  const res = await apiPost("/auth/register", data);
  if (!res) return { ok: false, error: "No response from server" };

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    return {
      ok: false,
      error:
        body.detail ||
        body.message ||
        body.error ||
        JSON.stringify(body) ||
        "Registration failed. see details"
    };
      }

  // Auto-login after registration
  return login(data.username, data.password);
}
