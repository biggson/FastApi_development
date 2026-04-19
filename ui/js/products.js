let currentPage = 0;
const PAGE_SIZE = 10;

async function loadProducts() {
  const search   = document.getElementById("search-input").value.trim();
  const category = document.getElementById("category-input").value.trim();

  let url = `/products/?limit=${PAGE_SIZE}&offset=${currentPage * PAGE_SIZE}&active_only=false`;
  if (search)   url += `&search=${encodeURIComponent(search)}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;

  const res = await apiGet(url);
  const tbody = document.getElementById("products-body");

  if (!res || !res.ok) {
    tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-6 text-red-500 text-center">Failed to load products</td></tr>`;
    return;
  }

  const products = await res.json();

  if (products.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-6 text-gray-400 text-center">No products found</td></tr>`;
  } else {
    tbody.innerHTML = products.map(p => `
      <tr class="border-b border-gray-100 hover:bg-gray-50">
        <td class="px-4 py-3 font-medium text-gray-900">${p.name}</td>
        <td class="px-4 py-3 text-gray-600">${p.sku}</td>
        <td class="px-4 py-3 text-gray-600">${p.category || "—"}</td>
        <td class="px-4 py-3 text-gray-700">${formatCurrency(p.price)}</td>
        <td class="px-4 py-3 text-gray-700">${p.quantity_on_hand ?? "—"}</td>
        <td class="px-4 py-3">
          <span class="inline-block text-xs font-medium px-2 py-0.5 rounded ${p.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}">
            ${p.is_active ? "Active" : "Inactive"}
          </span>
        </td>
        <td class="px-4 py-3">
          <button onclick="openEdit(${JSON.stringify(p).replace(/"/g, '&quot;')})"
            class="text-xs text-gray-600 hover:text-gray-900 border border-gray-200 rounded px-2 py-1 mr-1">
            Edit
          </button>
          ${p.is_active ? `
          <button onclick="deleteProduct(${p.id})"
            class="text-xs text-red-600 hover:text-red-800 border border-red-200 rounded px-2 py-1">
            Delete
          </button>` : ""}
        </td>
      </tr>
    `).join("");
  }

  document.getElementById("page-info").textContent = `Page ${currentPage + 1}`;
  document.getElementById("btn-prev").disabled = currentPage === 0;
  document.getElementById("btn-next").disabled = products.length < PAGE_SIZE;
}

function changePage(dir) {
  currentPage = Math.max(0, currentPage + dir);
  loadProducts();
}

function openForm() {
  document.getElementById("edit-id").value = "";
  document.getElementById("form-title").textContent = "New Product";
  document.getElementById("product-form").reset();
  document.getElementById("stock-fields").classList.remove("hidden");
  document.getElementById("f-unit").value = "pcs";
  document.getElementById("f-initial-stock").value = "0";
  document.getElementById("f-reorder-level").value = "10";
  document.getElementById("f-reorder-qty").value = "50";
  hideError("form-error");
  document.getElementById("form-overlay").classList.remove("hidden");
  document.getElementById("form-panel").classList.remove("hidden");
}

function openEdit(p) {
  document.getElementById("edit-id").value = p.id;
  document.getElementById("form-title").textContent = "Edit Product";
  document.getElementById("f-name").value = p.name || "";
  document.getElementById("f-sku").value = p.sku || "";
  document.getElementById("f-category").value = p.category || "";
  document.getElementById("f-price").value = p.price || "";
  document.getElementById("f-unit").value = p.unit_of_measure || "pcs";
  document.getElementById("f-description").value = p.description || "";
  document.getElementById("stock-fields").classList.add("hidden");
  hideError("form-error");
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
  btn.textContent = "Saving...";
  btn.disabled = true;

  const editId = document.getElementById("edit-id").value;
  const isEdit = !!editId;

  const body = {
    name:            document.getElementById("f-name").value.trim(),
    sku:             document.getElementById("f-sku").value.trim(),
    category:        document.getElementById("f-category").value.trim() || undefined,
    price:           parseFloat(document.getElementById("f-price").value),
    unit_of_measure: document.getElementById("f-unit").value.trim() || "pcs",
    description:     document.getElementById("f-description").value.trim() || undefined,
  };

  if (!isEdit) {
    body.initial_stock    = parseInt(document.getElementById("f-initial-stock").value) || 0;
    body.reorder_level    = parseInt(document.getElementById("f-reorder-level").value) || 10;
    body.reorder_quantity = parseInt(document.getElementById("f-reorder-qty").value) || 50;
  }

  const res = isEdit
    ? await apiPut(`/products/${editId}`, body)
    : await apiPost("/products/", body);

  if (!res || !res.ok) {
    const data = await res?.json().catch(() => ({}));
    showError("form-error", data?.detail || "Failed to save product");
    btn.textContent = "Save Product";
    btn.disabled = false;
    return;
  }

  closeForm();
  showSuccess("products-success", isEdit ? "Product updated." : "Product created.");
  loadProducts();
  btn.textContent = "Save Product";
  btn.disabled = false;
}

async function deleteProduct(id) {
  if (!confirm("Deactivate this product?")) return;
  const res = await apiDelete(`/products/${id}`);
  if (res && res.ok) {
    showSuccess("products-success", "Product deactivated.");
    loadProducts();
  } else {
    const data = await res?.json().catch(() => ({}));
    showError("products-error", data?.detail || "Failed to deactivate product");
  }
}
