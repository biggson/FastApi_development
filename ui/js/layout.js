// Injects navbar + sidebar into every authenticated page.
// Each page must have: <div id="navbar-slot"></div> and <aside id="sidebar-slot"></aside>

function renderLayout(activePage) {
  requireAuth();

  const user = getUser();
  const admin = isAdmin();

  // Navbar
  document.getElementById("navbar-slot").innerHTML = `
    <nav class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-6">
        <svg class="w-7 h-7 text-gray-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
          <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
        <span class="font-semibold text-gray-900 text-base">Inventory Manager</span>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500" id="nav-username"></span>
        <button onclick="logout()"
          class="text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-md px-3 py-1 hover:bg-gray-50 transition-colors">
          Logout
        </button>
      </div>
    </nav>`;

  // Sidebar links
  const links = [
    { href: "dashboard.html",     label: "Dashboard",     key: "dashboard" },
    { href: "products.html",      label: "Products",      key: "products" },
    { href: "inventory.html",     label: "Inventory",     key: "inventory" },
    { href: "transactions.html",  label: "Transactions",  key: "transactions" },
    { href: "users.html",         label: "Users",         key: "users", adminOnly: true },
  ];

  const navItems = links
    .filter(l => !l.adminOnly || admin)
    .map(l => {
      const active = l.key === activePage;
      return `<a href="${l.href}"
        class="block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          active
            ? "bg-gray-100 text-gray-900"
            : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
        }">${l.label}</a>`;
    }).join("");

  document.getElementById("sidebar-slot").innerHTML = navItems;

  setNavUser();
}
