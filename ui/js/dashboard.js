const TYPE_BADGE = {
  IN:         "bg-green-100 text-green-700",
  OUT:        "bg-red-100 text-red-700",
  RETURN:     "bg-blue-100 text-blue-700",
  ADJUSTMENT: "bg-gray-100 text-gray-700",
};

async function loadDashboard() {
  const [productsRes, lowStockRes, txnRes] = await Promise.all([
    apiGet("/products/?limit=100"),
    apiGet("/inventory/low-stock"),
    apiGet("/transactions/?limit=10"),
  ]);

  // Products count
  if (productsRes && productsRes.ok) {
    const data = await productsRes.json();
    document.getElementById("stat-products").textContent = data.length;
  }

  // Low stock count + list
  if (lowStockRes && lowStockRes.ok) {
    const items = await lowStockRes.json();
    document.getElementById("stat-lowstock").textContent = items.length;

    const list = document.getElementById("low-stock-list");
    if (items.length === 0) {
      list.innerHTML = `<p class="px-4 py-4 text-sm text-gray-400 text-center">No low stock items</p>`;
    } else {
      list.innerHTML = items.map(item => `
        <div class="px-4 py-3 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-900">${item.product_name || "—"}</p>
            <p class="text-xs text-gray-500">${item.product_sku || ""}</p>
          </div>
          <div class="text-right">
            <span class="inline-block bg-amber-100 text-amber-700 text-xs font-medium px-2 py-0.5 rounded">
              ${item.quantity_on_hand} / ${item.reorder_level}
            </span>
          </div>
        </div>
      `).join("");
    }
  }

  // Recent transactions
  if (txnRes && txnRes.ok) {
    const txns = await txnRes.json();
    document.getElementById("stat-transactions").textContent = txns.length < 10 ? txns.length : "10+";
    const tbody = document.getElementById("recent-txn-body");
    if (txns.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="px-4 py-4 text-gray-400 text-center">No transactions yet</td></tr>`;
    } else {
      tbody.innerHTML = txns.map(t => `
        <tr class="border-b border-gray-50 hover:bg-gray-50">
          <td class="px-4 py-2 text-gray-900">${t.product_name || "Product #" + t.product_id}</td>
          <td class="px-4 py-2">
            <span class="inline-block text-xs font-medium px-2 py-0.5 rounded ${TYPE_BADGE[t.transaction_type] || "bg-gray-100 text-gray-600"}">
              ${t.transaction_type}
            </span>
          </td>
          <td class="px-4 py-2 text-gray-700">${t.quantity}</td>
          <td class="px-4 py-2 text-gray-500 text-xs">${formatDate(t.created_at)}</td>
        </tr>
      `).join("");
    }
  }

  // Active users (admin only)
  if (isAdmin()) {
    const usersRes = await apiGet("/users/?limit=100");
    if (usersRes && usersRes.ok) {
      const users = await usersRes.json();
      const active = users.filter(u => u.is_active).length;
      document.getElementById("stat-users").textContent = active;
    }
  }
}
