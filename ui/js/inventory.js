let currentPage = 0;
const PAGE_SIZE = 10;
let viewMode = "all"; // "all" or "low"

function filterView(mode) {
  viewMode = mode;
  currentPage = 0;
  document.getElementById("btn-all").className =
    "text-sm border rounded-md px-3 py-1.5 " +
    (mode === "all" ? "border-gray-300 bg-gray-800 text-white" : "border-gray-200 text-gray-600 hover:bg-gray-50");
  document.getElementById("btn-low").className =
    "text-sm border rounded-md px-3 py-1.5 " +
    (mode === "low" ? "border-gray-300 bg-gray-800 text-white" : "border-gray-200 text-gray-600 hover:bg-gray-50");
  loadInventory();
}

async function loadInventory() {
  const url = viewMode === "low"
    ? "/inventory/low-stock"
    : `/inventory/?limit=${PAGE_SIZE}&offset=${currentPage * PAGE_SIZE}`;

  const res = await apiGet(url);
  const tbody = document.getElementById("inv-body");

  if (!res || !res.ok) {
    tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-6 text-red-500 text-center">Failed to load inventory</td></tr>`;
    return;
  }

  const items = await res.json();
  const admin = isAdmin();

  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-6 text-gray-400 text-center">No inventory records found</td></tr>`;
  } else {
    tbody.innerHTML = items.map(item => {
      const lowStock = item.quantity_on_hand <= item.reorder_level;
      const rowClass = lowStock ? "bg-amber-50" : "hover:bg-gray-50";
      return `
        <tr class="border-b border-gray-100 ${rowClass}">
          <td class="px-4 py-3 font-medium text-gray-900">${item.product_name || "Product #" + item.product_id}</td>
          <td class="px-4 py-3 text-gray-600">${item.product_sku || "—"}</td>
          <td class="px-4 py-3 font-semibold ${lowStock ? "text-amber-700" : "text-gray-900"}">${item.quantity_on_hand}</td>
          <td class="px-4 py-3 text-gray-600">${item.reorder_level}</td>
          <td class="px-4 py-3 text-gray-600">${item.reorder_quantity}</td>
          <td class="px-4 py-3">
            ${lowStock
              ? `<span class="inline-block text-xs font-medium px-2 py-0.5 rounded bg-amber-100 text-amber-700">Low Stock</span>`
              : `<span class="inline-block text-xs font-medium px-2 py-0.5 rounded bg-green-100 text-green-700">OK</span>`}
          </td>
          <td class="px-4 py-3 admin-only">
            ${admin ? `<button onclick="openModal(${item.product_id}, '${(item.product_name || "").replace(/'/g, "\\'")}', ${item.reorder_level}, ${item.reorder_quantity})"
              class="text-xs text-gray-600 hover:text-gray-900 border border-gray-200 rounded px-2 py-1">
              Edit
            </button>` : ""}
          </td>
        </tr>`;
    }).join("");
  }

  // Pagination controls (only for "all" mode)
  const paginationEls = document.querySelectorAll("#btn-prev, #btn-next, #page-info");
  paginationEls.forEach(el => el.style.visibility = viewMode === "all" ? "visible" : "hidden");
  document.getElementById("page-info").textContent = `Page ${currentPage + 1}`;
  document.getElementById("btn-prev").disabled = currentPage === 0;
  document.getElementById("btn-next").disabled = items.length < PAGE_SIZE;
}

function changePage(dir) {
  currentPage = Math.max(0, currentPage + dir);
  loadInventory();
}

function openModal(productId, productName, reorderLevel, reorderQty) {
  document.getElementById("m-product-id").value = productId;
  document.getElementById("modal-product-name").textContent = productName;
  document.getElementById("m-reorder-level").value = reorderLevel;
  document.getElementById("m-reorder-qty").value = reorderQty;
  hideError("modal-error");
  document.getElementById("modal-overlay").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("modal-overlay").classList.add("hidden");
}

async function saveReorder() {
  hideError("modal-error");
  const productId    = document.getElementById("m-product-id").value;
  const reorderLevel = parseInt(document.getElementById("m-reorder-level").value);
  const reorderQty   = parseInt(document.getElementById("m-reorder-qty").value);

  if (isNaN(reorderLevel) || isNaN(reorderQty)) {
    showError("modal-error", "Please enter valid numbers");
    return;
  }

  const res = await apiPut(`/inventory/${productId}`, {
    reorder_level: reorderLevel,
    reorder_quantity: reorderQty,
  });

  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    showError("modal-error", data?.detail || "Failed to update");
    return;
  }

  closeModal();
  showSuccess("inv-success", "Reorder settings updated.");
  loadInventory();
}
