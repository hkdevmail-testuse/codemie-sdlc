// Budget management page functionality
document.addEventListener("DOMContentLoaded", () => {
  const budgetForm = document.getElementById("budgetForm");
  const budgetMessage = document.getElementById("budgetMessage");
  const budgetsTable = document.getElementById("budgetsTable");
  const budgetCategorySelect = document.getElementById("budgetCategory");
  const budgetStatusContainer = document.getElementById("budgetStatusContainer");

  // Load categories for dropdown
  loadCategoriesForBudget();

  // Load budgets
  loadBudgets();

  // Load budget status
  loadBudgetStatus();

  // Handle form submission
  budgetForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const category = budgetCategorySelect.value;
    const budget_amount = parseFloat(document.getElementById("budgetAmount").value);
    const period_type = document.getElementById("periodType").value;

    if (!category || isNaN(budget_amount)) {
      showMessage("Please fill in all required fields", "error");
      return;
    }

    try {
      const response = await fetch("/api/budgets", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ category, budget_amount, period_type }),
      });

      const result = await response.json();

      if (result.success) {
        showMessage("Budget created successfully!", "success");
        budgetForm.reset();
        loadBudgets();
        loadBudgetStatus();
      } else {
        showMessage("Error: " + (result.error || "Unknown error"), "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showMessage("An unexpected error occurred.", "error");
    }
  });

  function showMessage(message, type) {
    budgetMessage.textContent = message;
    budgetMessage.className = type === "success" ? "success-message" : "error-message";
    setTimeout(() => {
      budgetMessage.textContent = "";
      budgetMessage.className = "";
    }, 5000);
  }

  async function loadCategoriesForBudget() {
    try {
      const response = await fetch("/api/categories");
      const categories = await response.json();

      budgetCategorySelect.innerHTML = '<option value="">Select a category</option>';
      categories.forEach((cat) => {
        const option = document.createElement("option");
        option.value = cat.name;
        option.textContent = cat.name;
        budgetCategorySelect.appendChild(option);
      });
    } catch (error) {
      console.error("Error loading categories:", error);
    }
  }

  async function loadBudgets() {
    try {
      const response = await fetch("/api/budgets");
      const budgets = await response.json();

      const tbody = budgetsTable.querySelector("tbody");
      tbody.innerHTML = "";

      budgets.forEach((budget) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${budget.category}</td>
          <td>$${budget.budget_amount.toFixed(2)}</td>
          <td>${budget.period_type}</td>
          <td>
            <button onclick="editBudget(${budget.id}, ${budget.budget_amount})" class="btn-edit">Edit</button>
            <button onclick="deleteBudget(${budget.id})" class="btn-delete">Delete</button>
          </td>
        `;
        tbody.appendChild(row);
      });
    } catch (error) {
      console.error("Error loading budgets:", error);
    }
  }

  async function loadBudgetStatus() {
    try {
      const response = await fetch("/api/budget-status");
      const statuses = await response.json();

      budgetStatusContainer.innerHTML = "";

      if (statuses.length === 0) {
        budgetStatusContainer.innerHTML = '<p>No budgets set. Add budgets below to track your spending.</p>';
        return;
      }

      statuses.forEach((status) => {
        const statusDiv = document.createElement("div");
        statusDiv.className = `budget-status-card ${status.exceeded ? "exceeded" : ""}`;

        const progressPercent = Math.min(status.percentage, 100);
        const progressColor = status.exceeded
          ? "#ff4444"
          : status.percentage > 80
          ? "#ff9800"
          : "#4caf50";

        statusDiv.innerHTML = `
          <h4>${status.category}</h4>
          <div class="budget-progress">
            <div class="progress-bar" style="width: ${progressPercent}%; background-color: ${progressColor};"></div>
          </div>
          <div class="budget-details">
            <span>Spent: $${status.spent.toFixed(2)} / $${status.budget.toFixed(2)}</span>
            <span class="budget-percentage">${status.percentage.toFixed(1)}%</span>
          </div>
          ${
            status.exceeded
              ? `<div class="budget-warning">⚠️ Over budget by $${Math.abs(status.remaining).toFixed(2)}</div>`
              : `<div class="budget-remaining">Remaining: $${status.remaining.toFixed(2)}</div>`
          }
        `;
        budgetStatusContainer.appendChild(statusDiv);
      });
    } catch (error) {
      console.error("Error loading budget status:", error);
    }
  }

  // Make functions globally available
  window.editBudget = async function (id, currentAmount) {
    const newAmount = prompt("Edit budget amount:", currentAmount);
    if (!newAmount || newAmount.trim() === "") return;

    const amount = parseFloat(newAmount);
    if (isNaN(amount) || amount < 0) {
      alert("Invalid amount");
      return;
    }

    try {
      const response = await fetch(`/api/budgets/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ budget_amount: amount }),
      });

      const result = await response.json();

      if (result.success) {
        showMessage("Budget updated successfully!", "success");
        loadBudgets();
        loadBudgetStatus();
      } else {
        showMessage("Error: " + (result.error || "Unknown error"), "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showMessage("An unexpected error occurred.", "error");
    }
  };

  window.deleteBudget = async function (id) {
    if (!confirm("Are you sure you want to delete this budget?")) return;

    try {
      const response = await fetch(`/api/budgets/${id}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (result.success) {
        showMessage("Budget deleted successfully!", "success");
        loadBudgets();
        loadBudgetStatus();
      } else {
        showMessage("Error: " + (result.error || "Unknown error"), "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showMessage("An unexpected error occurred.", "error");
    }
  };
});
