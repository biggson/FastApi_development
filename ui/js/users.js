async function initUsersPage() {
  await loadProfile();
  if (isAdmin()) {
    document.getElementById("admin-section").classList.remove("hidden");
    loadAllUsers();
  }
}

// ── Own Profile ─────────────────────────────────────────────────────────────

async function loadProfile() {
  const res = await apiGet("/users/me");
  if (!res || !res.ok) return;
  const user = await res.json();
  localStorage.setItem("inv_user", JSON.stringify(user)); // refresh cache

  document.getElementById("profile-info").innerHTML = `
    <div class="grid grid-cols-2 gap-y-2">
      <span class="text-gray-500">Name</span>
      <span>${[user.first_name, user.last_name].filter(Boolean).join(" ") || "—"}</span>
      <span class="text-gray-500">Username</span>
      <span>${user.username}</span>
      <span class="text-gray-500">Email</span>
      <span>${user.email}</span>
      <span class="text-gray-500">Phone</span>
      <span>${user.phone_number || "—"}</span>
      <span class="text-gray-500">Role</span>
      <span class="capitalize">${user.role}</span>
      <span class="text-gray-500">Joined</span>
      <span>${formatDate(user.created_at)}</span>
    </div>
  `;
}

function showEditProfile() {
  const user = getUser();
  if (!user) return;
  document.getElementById("edit-user-id").value = user.id;
  document.getElementById("edit-modal-title").textContent = "Edit Profile";
  document.getElementById("e-firstname").value = user.first_name || "";
  document.getElementById("e-lastname").value  = user.last_name  || "";
  document.getElementById("e-email").value     = user.email      || "";
  document.getElementById("e-phone").value     = user.phone_number || "";
  document.getElementById("role-field").classList.add("hidden");
  hideError("edit-error");
  document.getElementById("edit-overlay").classList.remove("hidden");
}

// ── Admin: All Users ─────────────────────────────────────────────────────────

async function loadAllUsers() {
  const res = await apiGet("/users/?limit=100");
  const tbody = document.getElementById("users-body");

  if (!res || !res.ok) {
    tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-6 text-red-500 text-center">Failed to load users</td></tr>`;
    return;
  }

  const users = await res.json();

  if (users.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-6 text-gray-400 text-center">No users found</td></tr>`;
    return;
  }

  tbody.innerHTML = users.map(u => `
    <tr class="border-b border-gray-100 hover:bg-gray-50">
      <td class="px-4 py-3 text-gray-900">${[u.first_name, u.last_name].filter(Boolean).join(" ") || "—"}</td>
      <td class="px-4 py-3 text-gray-600">${u.username}</td>
      <td class="px-4 py-3 text-gray-600">${u.email}</td>
      <td class="px-4 py-3 capitalize text-gray-700">${u.role}</td>
      <td class="px-4 py-3">
        <span class="inline-block text-xs font-medium px-2 py-0.5 rounded ${u.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}">
          ${u.is_active ? "Active" : "Inactive"}
        </span>
      </td>
      <td class="px-4 py-3 flex gap-1">
        <button onclick='openEditUser(${JSON.stringify(u)})'
          class="text-xs text-gray-600 hover:text-gray-900 border border-gray-200 rounded px-2 py-1">
          Edit
        </button>
        ${u.is_active ? `
        <button onclick="deactivateUser(${u.id})"
          class="text-xs text-red-600 hover:text-red-800 border border-red-200 rounded px-2 py-1">
          Deactivate
        </button>` : ""}
      </td>
    </tr>
  `).join("");
}

function openEditUser(u) {
  document.getElementById("edit-user-id").value = u.id;
  document.getElementById("edit-modal-title").textContent = `Edit: ${u.username}`;
  document.getElementById("e-firstname").value = u.first_name || "";
  document.getElementById("e-lastname").value  = u.last_name  || "";
  document.getElementById("e-email").value     = u.email      || "";
  document.getElementById("e-phone").value     = u.phone_number || "";
  document.getElementById("role-field").classList.remove("hidden");
  document.getElementById("e-role").value = u.role || "user";
  hideError("edit-error");
  document.getElementById("edit-overlay").classList.remove("hidden");
}

async function deactivateUser(id) {
  if (!confirm("Deactivate this user?")) return;
  const res = await apiDelete(`/users/${id}`);
  if (res && res.ok) {
    showSuccess("users-success", "User deactivated.");
    loadAllUsers();
  } else {
    const data = await res?.json().catch(() => ({}));
    showError("users-error", data?.detail || "Failed to deactivate user");
  }
}

// ── Shared Edit Modal ────────────────────────────────────────────────────────

function closeEditModal() {
  document.getElementById("edit-overlay").classList.add("hidden");
}

async function handleEditUser(e) {
  e.preventDefault();
  hideError("edit-error");

  const userId = document.getElementById("edit-user-id").value;
  const body = {
    first_name:   document.getElementById("e-firstname").value.trim() || undefined,
    last_name:    document.getElementById("e-lastname").value.trim()  || undefined,
    email:        document.getElementById("e-email").value.trim()     || undefined,
    phone_number: document.getElementById("e-phone").value.trim()     || undefined,
  };

  // Include role only if admin editing another user
  const roleField = document.getElementById("role-field");
  if (!roleField.classList.contains("hidden")) {
    body.role = document.getElementById("e-role").value;
  }

  const res = await apiPut(`/users/${userId}`, body);
  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    showError("edit-error", data?.detail || "Failed to update");
    return;
  }

  closeEditModal();
  showSuccess("users-success", "User updated.");
  await loadProfile();
  if (isAdmin()) loadAllUsers();
}

// ── Change Password ──────────────────────────────────────────────────────────

async function handleChangePassword(e) {
  e.preventDefault();
  hideError("pw-error");
  hideError("pw-success");

  const res = await apiPut("/auth/change-password", {
    old_password: document.getElementById("pw-old").value,
    new_password: document.getElementById("pw-new").value,
  });

  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    showError("pw-error", data?.detail || "Failed to change password");
    return;
  }

  document.getElementById("pw-old").value = "";
  document.getElementById("pw-new").value = "";
  showSuccess("pw-success", "Password changed successfully.");
}
