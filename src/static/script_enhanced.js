document.addEventListener("DOMContentLoaded", () => {
  // Get today's date in the format YYYY-MM-DD
  const today = new Date();

  const localDate =
    today.getFullYear() +
    "-" +
    String(today.getMonth() + 1).padStart(2, "0") +
    "-" +
    String(today.getDate()).padStart(2, "0");

  // Set the default value of the date input to today's date
  let ele = document.getElementById("date");
  if (ele) {
    ele.value = localDate;
  }

  const form = document.getElementById("purchaseForm");
  const statusMessage = document.getElementById("statusMessage");
  const purchasesTable = document.getElementById("purchasesTable");
  const monthlyOverview = document.getElementById("monthlyOverview");
  const monthlySpendingChart = document.getElementById("monthlySpendingChart");
  const allTimeCategoriesChart = document.getElementById(
    "allTimeCategoriesChart"
  );

  // Handle form submission
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();
    let tempDate = form.date.value;
    formData.append("date", form.date.value);
    formData.append("business", form.business.value);
    formData.append("amount", parseFloat(form.amount.value));

    if (form.category.value === "Other") {
      formData.append("category", form.customCategory.value);
    } else {
      formData.append("category", form.category.value);
    }
    formData.append("description", form.description.value);

    const photoFile = form.photo.files[0];
    if (photoFile) {
      formData.append("photo", photoFile);
    }

    try {
      const response = await fetch("/add", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (result.success) {
        statusMessage.textContent = "Purchase added successfully!";
        statusMessage.style.color = "green";
        form.reset();
        document.getElementById("date").value = tempDate;
        const customCategoryInput = document.getElementById("customCategory");
        customCategoryInput.style.display = "none";
        customCategoryInput.required = false;
        customCategoryInput.value = "";
      } else {
        statusMessage.textContent = "Error adding purchase: " + (result.error || "Unknown error");
        statusMessage.style.color = "red";
      }
    } catch (error) {
      console.error("Error:", error);
      statusMessage.textContent = "An unexpected error occurred.";
      statusMessage.style.color = "red";
    }
  });

  // Load and display purchases with edit/delete functionality
  if (purchasesTable) {
    loadPurchases();
  }

  function loadPurchases(filters = {}) {
    const queryParams = new URLSearchParams();
    
    // Add filters to query params
    if (filters.startDate) queryParams.append("start_date", filters.startDate);
    if (filters.endDate) queryParams.append("end_date", filters.endDate);
    if (filters.category) queryParams.append("category", filters.category);
    if (filters.business) queryParams.append("business", filters.business);
    if (filters.minAmount) queryParams.append("min_amount", filters.minAmount);
    if (filters.maxAmount) queryParams.append("max_amount", filters.maxAmount);

    fetch(`/month-data?${queryParams.toString()}`)
      .then((response) => response.json())
      .then((purchases) => {
        const tbody = purchasesTable.querySelector("tbody");
        tbody.innerHTML = ""; // Clear existing rows

        if (purchases.length === 0) {
          const row = document.createElement("tr");
          row.innerHTML = `<td colspan="7" style="text-align: center;">No expenses found</td>`;
          tbody.appendChild(row);
          return;
        }

        purchases.forEach((purchase) => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${purchase.date}</td>
            <td>${purchase.business}</td>
            <td>$${purchase.amount.toFixed(2)}</td>
            <td>${purchase.category}</td>
            <td>${purchase.description}</td>
            <td>
              ${
                purchase.photo
                  ? `<img src="data:image/jpeg;base64,${purchase.photo}" alt="Receipt" style="max-width: 100px; max-height: 100px;">`
                  : "No Photo"
              }
            </td>
            <td>
              <button class="btn-edit" onclick="editPurchase(${purchase.id})">Edit</button>
              <button class="btn-delete" onclick="deletePurchase(${purchase.id})">Delete</button>
            </td>
          `;
          tbody.appendChild(row);
        });
      })
      .catch((error) => {
        console.error("Error fetching purchases:", error);
      });
  }

  // Make loadPurchases available globally for filter functionality
  window.loadPurchases = loadPurchases;

  // Setup filter functionality if filter form exists
  const filterForm = document.getElementById("filterForm");
  if (filterForm) {
    filterForm.addEventListener("submit", (e) => {
      e.preventDefault();
      
      const filters = {
        startDate: document.getElementById("startDate")?.value || "",
        endDate: document.getElementById("endDate")?.value || "",
        category: document.getElementById("filterCategory")?.value || "",
        business: document.getElementById("filterBusiness")?.value || "",
        minAmount: document.getElementById("minAmount")?.value || "",
        maxAmount: document.getElementById("maxAmount")?.value || "",
      };
      
      loadPurchases(filters);
    });

    // Add clear filter button handler
    const clearFilterBtn = document.getElementById("clearFilters");
    if (clearFilterBtn) {
      clearFilterBtn.addEventListener("click", () => {
        filterForm.reset();
        loadPurchases();
      });
    }
  }

  // Load categories for filter dropdown
  loadCategories();

  // Populate the monthly overview if on overview page
  if (monthlyOverview) {
    loadMonthlyOverview();
  }

  // Load charts if they exist
  if (monthlySpendingChart) {
    loadMonthlySpendingChart();
    loadAllTimeCategoriesChart();
  }

  // Add date range filter for analytics
  const analyticsFilterForm = document.getElementById("analyticsFilterForm");
  if (analyticsFilterForm) {
    analyticsFilterForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const startDate = document.getElementById("analyticsStartDate")?.value || "";
      const endDate = document.getElementById("analyticsEndDate")?.value || "";
      
      loadMonthlySpendingChart(startDate, endDate);
      loadAllTimeCategoriesChart(startDate, endDate);
    });

    const clearAnalyticsBtn = document.getElementById("clearAnalyticsFilters");
    if (clearAnalyticsBtn) {
      clearAnalyticsBtn.addEventListener("click", () => {
        analyticsFilterForm.reset();
        loadMonthlySpendingChart();
        loadAllTimeCategoriesChart();
      });
    }
  }
});

// Load categories for dropdown
function loadCategories() {
  fetch("/categories")
    .then((response) => response.json())
    .then((categories) => {
      const filterCategory = document.getElementById("filterCategory");
      if (filterCategory) {
        categories.forEach((category) => {
          const option = document.createElement("option");
          option.value = category;
          option.textContent = category;
          filterCategory.appendChild(option);
        });
      }
    })
    .catch((error) => {
      console.error("Error loading categories:", error);
    });
}

// Edit purchase function
window.editPurchase = function(purchaseId) {
  // Fetch purchase data
  fetch(`/purchase/${purchaseId}`)
    .then((response) => response.json())
    .then((purchase) => {
      // Create modal for editing
      const modal = createEditModal(purchase);
      document.body.appendChild(modal);
      modal.style.display = "block";
    })
    .catch((error) => {
      console.error("Error fetching purchase:", error);
      alert("Error loading purchase data");
    });
};

// Delete purchase function
window.deletePurchase = function(purchaseId) {
  if (!confirm("Are you sure you want to delete this expense?")) {
    return;
  }

  fetch(`/purchase/${purchaseId}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((result) => {
      if (result.success) {
        alert("Expense deleted successfully!");
        window.loadPurchases(); // Reload the table
      } else {
        alert("Error deleting expense: " + (result.error || "Unknown error"));
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An unexpected error occurred while deleting");
    });
};

// Create edit modal
function createEditModal(purchase) {
  const modal = document.createElement("div");
  modal.className = "modal";
  modal.id = "editModal";

  modal.innerHTML = `
    <div class="modal-content">
      <span class="close" onclick="closeEditModal()">&times;</span>
      <h2>Edit Expense</h2>
      <form id="editForm">
        <input type="hidden" id="editId" value="${purchase.id}">
        
        <label for="editDate">Date:</label>
        <input type="date" id="editDate" value="${purchase.date}" required>
        
        <label for="editBusiness">Business:</label>
        <input type="text" id="editBusiness" value="${purchase.business}" required>
        
        <label for="editAmount">Amount:</label>
        <input type="number" id="editAmount" step="0.01" value="${purchase.amount}" required>
        
        <label for="editCategory">Category:</label>
        <select id="editCategory" required>
          <option value="">Select a category</option>
          <option value="Groceries" ${purchase.category === "Groceries" ? "selected" : ""}>Groceries</option>
          <option value="Furniture/Home" ${purchase.category === "Furniture/Home" ? "selected" : ""}>Furniture/Home</option>
          <option value="Gas/Car" ${purchase.category === "Gas/Car" ? "selected" : ""}>Gas/Car</option>
          <option value="Clothes" ${purchase.category === "Clothes" ? "selected" : ""}>Clothes</option>
          <option value="School/Office Supplies" ${purchase.category === "School/Office Supplies" ? "selected" : ""}>School/Office Supplies</option>
          <option value="Restaurants" ${purchase.category === "Restaurants" ? "selected" : ""}>Restaurants</option>
          <option value="Misc" ${purchase.category === "Misc" ? "selected" : ""}>Misc</option>
        </select>
        
        <label for="editDescription">Description:</label>
        <textarea id="editDescription" rows="3">${purchase.description}</textarea>
        
        <div style="margin-top: 20px;">
          <button type="submit" class="btn-save">Save Changes</button>
          <button type="button" class="btn-cancel" onclick="closeEditModal()">Cancel</button>
        </div>
      </form>
    </div>
  `;

  // Add form submit handler
  const editForm = modal.querySelector("#editForm");
  editForm.addEventListener("submit", (e) => {
    e.preventDefault();
    saveEditedPurchase();
  });

  return modal;
}

// Close edit modal
window.closeEditModal = function() {
  const modal = document.getElementById("editModal");
  if (modal) {
    modal.remove();
  }
};

// Save edited purchase
function saveEditedPurchase() {
  const purchaseId = document.getElementById("editId").value;
  const data = {
    date: document.getElementById("editDate").value,
    business: document.getElementById("editBusiness").value,
    amount: parseFloat(document.getElementById("editAmount").value),
    category: document.getElementById("editCategory").value,
    description: document.getElementById("editDescription").value,
  };

  fetch(`/purchase/${purchaseId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((result) => {
      if (result.success) {
        alert("Expense updated successfully!");
        closeEditModal();
        window.loadPurchases(); // Reload the table
      } else {
        alert("Error updating expense: " + (result.error || "Unknown error"));
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An unexpected error occurred while updating");
    });
}

// Load monthly overview
function loadMonthlyOverview() {
  const monthlyOverview = document.getElementById("monthlyOverview");
  
  fetch("/overview-data")
    .then((response) => response.json())
    .then((months) => {
      monthlyOverview.innerHTML = ""; // Clear existing content
      
      months.forEach((item) => {
        const div = document.createElement("div");
        div.className = "overview-item";

        const monthSpan = document.createElement("span");
        monthSpan.className = "month-name";
        monthSpan.textContent = getMonthName(item.month);

        const totalSpan = document.createElement("span");
        totalSpan.className = "total-amount";
        totalSpan.textContent = `Total: $${item.total.toFixed(2)}`;

        const chartContainer = document.createElement("div");
        chartContainer.className = "pie-chart-container";

        const canvas = document.createElement("canvas");
        canvas.className = "pie-chart";
        chartContainer.appendChild(canvas);

        div.appendChild(monthSpan);
        div.appendChild(totalSpan);
        div.appendChild(chartContainer);

        monthlyOverview.appendChild(div);

        fetch(`/monthly-category-data?month=${item.month}`)
          .then((response) => response.json())
          .then((categorical_data) => {
            if (!Array.isArray(categorical_data)) {
              throw new Error("Expected an array but got something else");
            }

            const categories = categorical_data.map((data) => data.category);
            const totals = categorical_data.map((data) => data.category_amount);

            const categoryColors = getCategoryColors();
            const backgroundColors = categories.map(
              (category) => categoryColors[category] || "grey"
            );

            new Chart(canvas, {
              type: "pie",
              data: {
                labels: categories,
                datasets: [
                  {
                    data: totals,
                    backgroundColor: backgroundColors,
                  },
                ],
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
              },
            });
          })
          .catch((error) => {
            console.error("Error fetching monthly category data:", error);
          });
      });
    })
    .catch((error) => {
      console.error("Error fetching monthly overview data:", error);
    });
}

// Load monthly spending chart
function loadMonthlySpendingChart(startDate = "", endDate = "") {
  const queryParams = new URLSearchParams({ sort: "ASC" });
  if (startDate) queryParams.append("start_date", startDate);
  if (endDate) queryParams.append("end_date", endDate);

  fetch(`/overview-data?${queryParams.toString()}`)
    .then((response) => response.json())
    .then((data) => {
      const ctx = document.getElementById("monthlySpendingChart").getContext("2d");
      
      // Destroy existing chart if it exists
      if (window.monthlyChart) {
        window.monthlyChart.destroy();
      }

      window.monthlyChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: data.map((item) => getMonthYear(item.month)),
          datasets: [
            {
              label: "Total Spent",
              data: data.map((item) => item.total),
              borderColor: "#36A2EB",
              backgroundColor: "rgba(54, 162, 235, 0.2)",
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            x: {
              title: {
                display: true,
                text: "Month",
              },
            },
            y: {
              title: {
                display: true,
                text: "Total Spent ($)",
              },
            },
          },
        },
      });
    })
    .catch((error) =>
      console.error("Error fetching monthly total data:", error)
    );
}

// Load all-time categories chart
function loadAllTimeCategoriesChart(startDate = "", endDate = "") {
  const queryParams = new URLSearchParams();
  if (startDate) queryParams.append("start_date", startDate);
  if (endDate) queryParams.append("end_date", endDate);

  fetch(`/monthly-category-data?${queryParams.toString()}`)
    .then((response) => response.json())
    .then((categorical_data) => {
      if (!Array.isArray(categorical_data)) {
        throw new Error("Expected an array but got something else");
      }

      const categories = categorical_data.map((data) => data.category);
      const totals = categorical_data.map((data) => data.category_amount);

      const categoryColors = getCategoryColors();
      const backgroundColors = categories.map(
        (category) => categoryColors[category] || "grey"
      );

      const ctx = document.getElementById("allTimeCategoriesChart").getContext("2d");
      
      // Destroy existing chart if it exists
      if (window.categoryChart) {
        window.categoryChart.destroy();
      }

      window.categoryChart = new Chart(ctx, {
        type: "pie",
        data: {
          labels: categories,
          datasets: [
            {
              data: totals,
              backgroundColor: backgroundColors,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "right",
            },
          },
        },
      });
    })
    .catch((error) => {
      console.error("Error fetching category data:", error);
    });
}

// Helper functions
const getMonthName = (dateString) => {
  const [year, month] = dateString.split("-");
  const date = new Date(year, month - 1);
  return date.toLocaleString("default", { month: "long" });
};

const getMonthYear = (dateString) => {
  const [year, month] = dateString.split("-");
  return `${getMonthName(dateString)} ${year}`;
};

function getCategoryColors() {
  return {
    Restaurants: "#FF5733",
    "Furniture/Home": "#33FF57",
    "Gas/Car": "#3357FF",
    Clothes: "#FF33A1",
    "School/Office Supplies": "#FF8C33",
    Misc: "#33FFF5",
    Groceries: "#8C33FF",
  };
}

function toggleCustomCategory(select) {
  const customCategoryInput = document.getElementById("customCategory");
  if (select.value === "Other") {
    customCategoryInput.style.display = "block";
    customCategoryInput.required = true;
  } else {
    customCategoryInput.style.display = "none";
    customCategoryInput.required = false;
    customCategoryInput.value = "";
  }
}
