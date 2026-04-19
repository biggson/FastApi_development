let currentPage = 0;
const PAGE_SIZE = 10;

const TYPE_BADGE = {
  IN:         "bg-green-100 text-green-700",
  OUT:        "bg-red-100 text-red-700",
  RETURN:     "bg-blue-100 text-blue-700",
  ADJUSTMENT: "bg-gray-100 text-gray-700",
};

async function loadTransactions() {
  const typeFilter = document.getElementById("filter-type").value;
  let url = `/transactions/?limit=${PAGE_SIZE}&offset=${currentPage * PAGE_SIZE}`;
  if (typeFilter) url += `&transaction_type=${typeFilter}`;

  const res = await apiGet(url);
  const tbody = document.getElementById("txn-body");

  if (!res || !res.ok) {
    tbody.innerHTML = `<tr><td colspan="8" class="px-4 py-6 text-red-500 text-center">Failed to load transactions</td></tr>`;
    return;
  }

  const txns = await res.json();

  if (txns.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="px-4 py-6 text-gray-400 text-center">No transactions found</td></tr>`;
  } else {
    tbody.innerHTML = txns.map(t => `
      <tr class="border-b border-gray-100 hover:bg-gray-50">
        <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">${formatDate(t.created_at)}</td>
        <td class="px-4 py-3 text-gray-900">
          <div>${t.product_name || "Product #" + t.product_id}</div>
          <div class="text-xs text-gray-400">${t.product_sku || ""}</div>
        </td>
        <td class="px-4 py-3">
          <span class="inline-block text-xs font-medium px-2 py-0.5 rounded ${TYPE_BADGE[t.transaction_type] || "bg-gray-100 text-gray-600"}">
            ${t.transaction_type}
          </span>
        </td>
        <td class="px-4 py-3 font-medium text-gray-900">${t.quantity}</td>
        <td class="px-4 py-3 text-gray-700">${formatCurrency(t.unit_price)}</td>
        <td class="px-4 py-3 font-medium text-gray-900">${formatCurrency(t.total_amount)}</td>
        <td class="px-4 py-3 text-gray-500">${t.reference_number || "—"}</td>
        <td class="px-4 py-3 text-gray-500">${t.performed_by || "—"}</td>
      </tr>
    `).join("");
  }

  document.getElementById("page-info").textContent = `Page ${currentPage + 1}`;
  document.getElementById("btn-prev").disabled = currentPage === 0;
  document.getElementById("btn-next").disabled = txns.length < PAGE_SIZE;
}

function changePage(dir) {
  currentPage = Math.max(0, currentPage + dir);
  loadTransactions();
}

async function openForm() {
  document.getElementById("txn-form").reset();
  hideError("form-error");

  // Show ADJUSTMENT option only for admin
  const adjOpt = document.getElementById("opt-adjustment");
  if (isAdmin()) {
    adjOpt.classList.remove("hidden");
  } else {
    adjOpt.classList.add("hidden");
  }

  // Load product list
  const res = await apiGet("/products/?limit=100");
  const select = document.getElementById("f-product");
  if (res && res.ok) {
    const products = await res.json();
    select.innerHTML = `<option value="">Select a product...</option>` +
      products.filter(p => p.is_active).map(p =>
        `<option value="${p.id}">${p.name} (${p.sku})</option>`
      ).join("");
  } else {
    select.innerHTML = `<option value="">Failed to load products</option>`;
  }

  document.getElementById("form-overlay").classList.remove("hidden");
  document.getElementById("form-panel").classList.remove("hidden");
}

function closeForm() {
  document.getElementById("form-overlay").classList.add("hidden");
  document.getElementById("form-panel").classList.add("hidden");
}

async function handleSubmit(e) {
  e.preventDefault();
  hideError("form-error");
  const btn = document.getElementById("form-submit-btn");
  btn.textContent = "Recording...";
  btn.disabled = true;

  const body = {
    product_id:       parseInt(document.getElementById("f-product").value),
    transaction_type: document.getElementById("f-type").value,
    quantity:         parseInt(document.getElementById("f-quantity").value),
    unit_price:       parseFloat(document.getElementById("f-price").value),
    reference_number: document.getElementById("f-reference").value.trim() || undefined,
    notes:            document.getElementById("f-notes").value.trim() || undefined,
  };

  const res = await apiPost("/transactions/", body);

  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    showError("form-error", data?.detail || "Failed to record transaction");
    btn.textContent = "Record Transaction";
    btn.disabled = false;
    return;
  }

  closeForm();
  showSuccess("txn-success", "Transaction recorded.");
  loadTransactions();
  btn.textContent = "Record Transaction";
  btn.disabled = false;
}
