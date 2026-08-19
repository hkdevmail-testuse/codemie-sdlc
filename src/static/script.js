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

  // Create edit modal if it doesn't exist
  createEditModal();

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
        statusMessage.className = "success-message";
        form.reset();
        document.getElementById("date").value = tempDate;
        const customCategoryInput = document.getElementById("customCategory");
        if (customCategoryInput) {
          customCategoryInput.style.display = "none";
          customCategoryInput.required = false;
          customCategoryInput.value = "";
        }

        // Refresh the table if it exists
        if (purchasesTable) {
          loadPurchases();
        }

        // Show budget alert if exceeded
        if (result.budget_alert) {
          const alert = result.budget_alert;
          const budgetAlert = document.getElementById("budgetAlert");
          if (budgetAlert) {
            budgetAlert.innerHTML = `
              <strong>⚠️ Budget Alert!</strong><br>
              Category: ${alert.category}<br>
              Budget: $${alert.budget.toFixed(2)}<br>
              Spent: $${alert.spent.toFixed(2)}<br>
              Over by: $${alert.over_by.toFixed(2)}
            `;
            budgetAlert.className = "budget-alert exceeded";
            budgetAlert.style.display = "block";
          }
        }
      } else {
        statusMessage.textContent = "Error: " + (result.error || "Unknown error");
        statusMessage.className = "error-message";
      }
    } catch (error) {
      console.error("Error:", error);
      statusMessage.textContent = "An unexpected error occurred.";
      statusMessage.className = "error-message";
    }
  });

  // Populate the purchases table if it exists
  if (purchasesTable) {
    loadPurchases();
  }

  // Populate the monthly overview if on overview page
  if (monthlyOverview) {
    fetch("/overview-data")
      .then((response) => response.json())
      .then((months) => {
        months.forEach((item) => {
          const div = document.createElement("div");
          div.className = "overview-item";

          const monthSpan = document.createElement("span");
          monthSpan.className = "month-name";
          monthSpan.textContent = getMonthName(item.month);

          const totalSpan = document.createElement("span");
          totalSpan.className = "total-amount";
          totalSpan.textContent = `Total: $${item.total.toFixed(2)}`;

          // Container for the pie chart
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
              const totals = categorical_data.map(
                (data) => data.category_amount
              );

              const categoryColors = {
                Restaurants: "#FF5733", // Red
                "Furniture/Home": "#33FF57", // Green
                "Gas/Car": "#3357FF", // Blue
                Clothes: "#FF33A1", // Pink
                "School/Office Supplies": "#FF8C33", // Orange
                Misc: "#33FFF5", // Cyan
                Groceries: "#8C33FF", // Purple
              };

              const defaultColor = "grey"; // Default color for categories not in the mapping

              const backgroundColors = categories.map((category) => {
                const color = categoryColors[category] || defaultColor;
                return color;
              });

              // Create the pie chart of categories
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
  if (monthlySpendingChart) {
    fetch("/overview-data?sort=ASC")
      .then((response) => response.json())
      .then((data) => {
        const ctx = document
          .getElementById("monthlySpendingChart")
          .getContext("2d");
        new Chart(ctx, {
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
                  text: "Total Spent",
                },
              },
            },
          },
        });
      })
      .catch((error) =>
        console.error("Error fetching monthly total data:", error)
      );

    fetch(`/monthly-category-data`)
      .then((response) => response.json())
      .then((categorical_data) => {
        if (!Array.isArray(categorical_data)) {
          throw new Error("Expected an array but got something else");
        }

        const categories = categorical_data.map((data) => data.category);
        const totals = categorical_data.map((data) => data.category_amount);

        const categoryColors = {
          Restaurants: "#FF5733", // Red
          "Furniture/Home": "#33FF57", // Green
          "Gas/Car": "#3357FF", // Blue
          Clothes: "#FF33A1", // Pink
          "School/Office Supplies": "#FF8C33", // Orange
          Misc: "#33FFF5", // Cyan
          Groceries: "#8C33FF", // Purple
        };

        const defaultColor = "grey"; // Default color for categories not in the mapping

        const backgroundColors = categories.map((category) => {
          const color = categoryColors[category] || defaultColor;
          return color;
        });

        // Create the pie chart of categories
        new Chart(allTimeCategoriesChart, {
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
  }
});

const getMonthName = (dateString) => {
  const [year, month] = dateString.split("-");
  const date = new Date(year, month - 1);
  return date.toLocaleString("default", { month: "long" });
};

const getMonthYear = (dateString) => {
  const [year, month] = dateString.split("-");
  return `${getMonthName(dateString)} ${year}`;
};

function toggleCustomCategory(select) {
  const customCategoryInput = document.getElementById("customCategory");
  if (customCategoryInput && select.value === "Other") {
    customCategoryInput.style.display = "block";
    customCategoryInput.required = true;
  } else if (customCategoryInput) {
    customCategoryInput.style.display = "none";
    customCategoryInput.required = false;
    customCategoryInput.value = "";
  }
}

function toggleEditCustomCategory(select) {
  const customCategoryInput = document.getElementById("editCustomCategory");
  if (customCategoryInput && select.value === "Other") {
    customCategoryInput.style.display = "block";
    customCategoryInput.required = true;
  } else if (customCategoryInput) {
    customCategoryInput.style.display = "none";
    customCategoryInput.required = false;
    customCategoryInput.value = "";
  }
}

// Create edit modal
function createEditModal() {
  const modal = document.createElement("div");
  modal.id = "editModal";
  modal.className = "modal";
  modal.innerHTML = `
    <div class="modal-content">
      <span class="close-modal" onclick="closeEditModal()">&times;</span>
      <h2>Edit Expense</h2>
      <form id="editExpenseForm">
        <input type="hidden" id="editExpenseId" />
        
        <label for="editDate">Date:</label>
        <input type="date" id="editDate" name="date" required />
        
        <label for="editBusiness">Business:</label>
        <input type="text" id="editBusiness" name="business" required />
        
        <label for="editAmount">Amount:</label>
        <input type="number" id="editAmount" name="amount" step="0.01" min="0" required />
        
        <label for="editCategory">Category:</label>
        <select id="editCategory" name="category" onchange="toggleEditCustomCategory(this)" required>
          <option value="">Select a category</option>
          <option value="Restaurants">Restaurants</option>
          <option value="Furniture/Home">Furniture/Home</option>
          <option value="Gas/Car">Gas/Car</option>
          <option value="Clothes">Clothes</option>
          <option value="School/Office Supplies">School/Office Supplies</option>
          <option value="Groceries">Groceries</option>
          <option value="Misc">Misc</option>
          <option value="Other">Other (Custom)</option>
        </select>
        
        <input type="text" id="editCustomCategory" name="customCategory" placeholder="Enter custom category" style="display: none;" />
        
        <label for="editDescription">Description:</label>
        <textarea id="editDescription" name="description" rows="3"></textarea>
        
        <label for="editPhoto">Photo:</label>
        <input type="file" id="editPhoto" name="photo" accept="image/*" />
        
        <div id="currentPhotoContainer" style="margin: 10px 0;">
          <label>Current Photo:</label>
          <div id="currentPhoto"></div>
        </div>
        
        <div id="editStatusMessage"></div>
        
        <button type="submit" id="updateExpenseBtn">Update Expense</button>
        <button type="button" onclick="closeEditModal()">Cancel</button>
      </form>
    </div>
  `;
  document.body.appendChild(modal);

  // Add event listener for edit form submission
  const editForm = document.getElementById("editExpenseForm");
  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const expenseId = document.getElementById("editExpenseId").value;
    const formData = new FormData();
    
    formData.append("date", document.getElementById("editDate").value);
    formData.append("business", document.getElementById("editBusiness").value);
    formData.append("amount", parseFloat(document.getElementById("editAmount").value));
    
    const category = document.getElementById("editCategory").value;
    if (category === "Other") {
      formData.append("category", document.getElementById("editCustomCategory").value);
    } else {
      formData.append("category", category);
    }
    
    formData.append("description", document.getElementById("editDescription").value);
    
    const photoFile = document.getElementById("editPhoto").files[0];
    if (photoFile) {
      formData.append("photo", photoFile);
    }
    
    await updateExpense(expenseId, formData);
  });
}

// Load purchases with optional filters
async function loadPurchases(filters = {}) {
  const purchasesTable = document.getElementById("purchasesTable");
  if (!purchasesTable) return;

  const tbody = purchasesTable.querySelector("tbody");
  tbody.innerHTML = '<tr><td colspan="10" style="text-align: center;">Loading...</td></tr>';

  try {
    let url = "/month-data";
    const queryParams = new URLSearchParams();
    
    if (filters.search) queryParams.append("search", filters.search);
    if (filters.category) queryParams.append("category", filters.category);
    if (filters.minAmount) queryParams.append("min_amount", filters.minAmount);
    if (filters.maxAmount) queryParams.append("max_amount", filters.maxAmount);
    if (filters.startDate) queryParams.append("start_date", filters.startDate);
    if (filters.endDate) queryParams.append("end_date", filters.endDate);
    if (filters.sort) queryParams.append("sort", filters.sort);
    
    if (queryParams.toString()) {
      url += "?" + queryParams.toString();
    }

    const response = await fetch(url);
    const purchases = await response.json();
    
    tbody.innerHTML = "";
    
    if (purchases.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10" style="text-align: center;">No purchases found</td></tr>';
      return;
    }

    purchases.forEach((purchase) => {
      const row = document.createElement("tr");
      row.setAttribute("data-id", purchase.id);
      row.innerHTML = `
        <td>${purchase.date}</td>
        <td>${purchase.business}</td>
        <td>$${purchase.amount.toFixed(2)}</td>
        <td>${purchase.category}</td>
        <td>${purchase.description}</td>
        <td>${purchase.tags || '-'}</td>
        <td>${purchase.is_recurring ? 'Yes' : 'No'}</td>
        <td>${purchase.notes || '-'}</td>
        <td>
          ${
            purchase.photo
              ? `<img src="data:image/jpeg;base64,${purchase.photo}" alt="Purchase Photo" style="max-width: 100px; max-height: 100px;">`
              : "No Photo"
          }
        </td>
        <td class="action-buttons">
          <button class="edit-btn" onclick="editExpense(${purchase.id})" title="Edit">✏️ Edit</button>
          <button class="delete-btn" onclick="deleteExpense(${purchase.id})" title="Delete">🗑️ Delete</button>
        </td>
      `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error("Error fetching purchases:", error);
    tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: red;">Error loading purchases</td></tr>';
  }
}

// Edit expense function
async function editExpense(expenseId) {
  const modal = document.getElementById("editModal");
  const editStatusMessage = document.getElementById("editStatusMessage");
  editStatusMessage.textContent = "";
  
  try {
    const response = await fetch(`/expense/${expenseId}`);
    if (!response.ok) {
      throw new Error("Failed to fetch expense data");
    }
    
    const expense = await response.json();
    
    // Populate form fields
    document.getElementById("editExpenseId").value = expense.id;
    document.getElementById("editDate").value = expense.date;
    document.getElementById("editBusiness").value = expense.business;
    document.getElementById("editAmount").value = expense.amount;
    document.getElementById("editDescription").value = expense.description || "";
    
    // Handle category
    const categorySelect = document.getElementById("editCategory");
    const customCategoryInput = document.getElementById("editCustomCategory");
    
    const standardCategories = ["Restaurants", "Furniture/Home", "Gas/Car", "Clothes", "School/Office Supplies", "Groceries", "Misc"];
    
    if (standardCategories.includes(expense.category)) {
      categorySelect.value = expense.category;
      customCategoryInput.style.display = "none";
      customCategoryInput.required = false;
    } else {
      categorySelect.value = "Other";
      customCategoryInput.value = expense.category;
      customCategoryInput.style.display = "block";
      customCategoryInput.required = true;
    }
    
    // Display current photo
    const currentPhotoDiv = document.getElementById("currentPhoto");
    if (expense.photo) {
      currentPhotoDiv.innerHTML = `
        <img src="data:image/jpeg;base64,${expense.photo}" alt="Current Photo" style="max-width: 200px; max-height: 200px;">
        <p style="font-size: 12px; color: #666;">Upload a new photo to replace this one</p>
      `;
    } else {
      currentPhotoDiv.innerHTML = '<p>No photo available</p>';
    }
    
    // Show modal
    modal.style.display = "block";
  } catch (error) {
    console.error("Error fetching expense:", error);
    alert("Failed to load expense data. Please try again.");
  }
}

// Update expense function
async function updateExpense(expenseId, formData) {
  const updateBtn = document.getElementById("updateExpenseBtn");
  const editStatusMessage = document.getElementById("editStatusMessage");
  
  updateBtn.disabled = true;
  updateBtn.textContent = "Updating...";
  editStatusMessage.textContent = "";
  
  try {
    const response = await fetch(`/update/${expenseId}`, {
      method: "PUT",
      body: formData,
    });
    
    const result = await response.json();
    
    if (result.success) {
      editStatusMessage.textContent = "Expense updated successfully!";
      editStatusMessage.className = "success-message";
      editStatusMessage.style.color = "green";
      
      // Close modal after 1 second
      setTimeout(() => {
        closeEditModal();
        loadPurchases();
        
        // Refresh analytics if on overview page
        const monthlyOverview = document.getElementById("monthlyOverview");
        if (monthlyOverview) {
          location.reload();
        }
      }, 1000);
    } else {
      editStatusMessage.textContent = "Error: " + (result.error || "Unknown error");
      editStatusMessage.className = "error-message";
      editStatusMessage.style.color = "red";
    }
  } catch (error) {
    console.error("Error updating expense:", error);
    editStatusMessage.textContent = "An unexpected error occurred.";
    editStatusMessage.className = "error-message";
    editStatusMessage.style.color = "red";
  } finally {
    updateBtn.disabled = false;
    updateBtn.textContent = "Update Expense";
  }
}

// Close edit modal
function closeEditModal() {
  const modal = document.getElementById("editModal");
  modal.style.display = "none";
  
  // Reset form
  document.getElementById("editExpenseForm").reset();
  document.getElementById("editCustomCategory").style.display = "none";
  document.getElementById("editStatusMessage").textContent = "";
  document.getElementById("currentPhoto").innerHTML = "";
}

// Delete expense function
async function deleteExpense(expenseId) {
  const confirmed = confirm("Are you sure you want to delete this expense? This action cannot be undone.");
  
  if (!confirmed) {
    return;
  }
  
  try {
    const response = await fetch(`/delete/${expenseId}`, {
      method: "DELETE",
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Remove row from table
      const row = document.querySelector(`tr[data-id="${expenseId}"]`);
      if (row) {
        row.remove();
      }
      
      // Show success message
      const statusMessage = document.getElementById("statusMessage");
      if (statusMessage) {
        statusMessage.textContent = "Expense deleted successfully!";
        statusMessage.className = "success-message";
        statusMessage.style.color = "green";
        
        setTimeout(() => {
          statusMessage.textContent = "";
        }, 3000);
      }
      
      // Reload purchases to update the table
      loadPurchases();
      
      // Refresh analytics if on overview page
      const monthlyOverview = document.getElementById("monthlyOverview");
      if (monthlyOverview) {
        location.reload();
      }
    } else {
      alert("Error: " + (result.error || "Failed to delete expense"));
    }
  } catch (error) {
    console.error("Error deleting expense:", error);
    alert("An unexpected error occurred while deleting the expense.");
  }
}

// Filter expenses function
function filterExpenses(filters) {
  loadPurchases(filters);
}

// Apply date range filter
function applyDateRangeFilter(startDate, endDate) {
  const filters = {
    startDate: startDate,
    endDate: endDate
  };
  
  loadPurchases(filters);
  
  // Update analytics if needed
  const monthlyOverview = document.getElementById("monthlyOverview");
  if (monthlyOverview) {
    // Reload analytics with date range
    location.reload();
  }
}

// Close modal when clicking outside
window.onclick = function(event) {
  const modal = document.getElementById("editModal");
  if (event.target === modal) {
    closeEditModal();
  }
}