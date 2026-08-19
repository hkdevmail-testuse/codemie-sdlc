// Recent purchases page with enhanced filtering
document.addEventListener("DOMContentLoaded", () => {
  const filterCategorySelect = document.getElementById("filterCategory");
  const purchasesTable = document.getElementById("purchasesTable");

  // Load categories for filter dropdown
  loadCategoriesForFilter();

  // Load initial purchases
  loadPurchases();

  async function loadCategoriesForFilter() {
    try {
      const response = await fetch("/api/categories");
      const categories = await response.json();

      filterCategorySelect.innerHTML = '<option value="">All Categories</option>';
      categories.forEach((cat) => {
        const option = document.createElement("option");
        option.value = cat.name;
        option.textContent = cat.name;
        filterCategorySelect.appendChild(option);
      });
    } catch (error) {
      console.error("Error loading categories:", error);
    }
  }

  async function loadPurchases(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.month) params.append("month", filters.month);
      if (filters.category) params.append("category", filters.category);
      if (filters.tag) params.append("tag", filters.tag);
      if (filters.recurring !== undefined && filters.recurring !== "")
        params.append("recurring", filters.recurring);

      const response = await fetch(`/month-data?${params.toString()}`);
      const purchases = await response.json();

      const tbody = purchasesTable.querySelector("tbody");
      tbody.innerHTML = "";

      if (purchases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9">No purchases found.</td></tr>';
        return;
      }

      purchases.forEach((purchase) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${purchase.date}</td>
          <td>${purchase.business}</td>
          <td>$${purchase.amount.toFixed(2)}</td>
          <td>${purchase.category}</td>
          <td>${purchase.description || "-"}</td>
          <td>${purchase.tags || "-"}</td>
          <td>${purchase.is_recurring ? "Yes" : "No"}</td>
          <td>${purchase.notes || "-"}</td>
          <td>
            ${
              purchase.photo
                ? `<img src="data:image/jpeg;base64,${purchase.photo}" alt="Receipt" style="max-width: 100px; max-height: 100px;">`
                : "No Photo"
            }
          </td>
        `;
        tbody.appendChild(row);
      });
    } catch (error) {
      console.error("Error loading purchases:", error);
    }
  }

  // Make functions globally available
  window.applyFilters = function () {
    const month = document.getElementById("filterMonth").value;
    const category = document.getElementById("filterCategory").value;
    const tag = document.getElementById("filterTag").value.trim();
    const recurring = document.getElementById("filterRecurring").value;

    const filters = {};
    if (month) filters.month = month;
    if (category) filters.category = category;
    if (tag) filters.tag = tag;
    if (recurring) filters.recurring = recurring;

    loadPurchases(filters);
  };

  window.clearFilters = function () {
    document.getElementById("filterMonth").value = "";
    document.getElementById("filterCategory").value = "";
    document.getElementById("filterTag").value = "";
    document.getElementById("filterRecurring").value = "";
    loadPurchases();
  };
});
