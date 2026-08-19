// Category management page functionality
document.addEventListener("DOMContentLoaded", () => {
  const categoryForm = document.getElementById("categoryForm");
  const categoryMessage = document.getElementById("categoryMessage");
  const categoriesTable = document.getElementById("categoriesTable");

  // Load categories
  loadCategories();

  // Handle form submission
  categoryForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("categoryName").value.trim();

    if (!name) {
      showMessage("Please enter a category name", "error");
      return;
    }

    try {
      const response = await fetch("/api/categories", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name }),
      });

      const result = await response.json();

      if (result.success) {
        showMessage("Category created successfully!", "success");
        categoryForm.reset();
        loadCategories();
      } else {
        showMessage("Error: " + (result.error || "Unknown error"), "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showMessage("An unexpected error occurred.", "error");
    }
  });

  function showMessage(message, type) {
    categoryMessage.textContent = message;
    categoryMessage.className = type === "success" ? "success-message" : "error-message";
    setTimeout(() => {
      categoryMessage.textContent = "";
      categoryMessage.className = "";
    }, 5000);
  }

  async function loadCategories() {
    try {
      const response = await fetch("/api/categories");
      const categories = await response.json();

      const tbody = categoriesTable.querySelector("tbody");
      tbody.innerHTML = "";

      categories.forEach((category) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${category.name}</td>
          <td>${new Date(category.created_at).toLocaleDateString()}</td>
          <td>
            <button onclick="editCategory(${category.id}, '${category.name}')" class="btn-edit">Edit</button>
            <button onclick="deleteCategory(${category.id})" class="btn-delete">Delete</button>
          </td>
        `;
        tbody.appendChild(row);
      });
    } catch (error) {
      console.error("Error loading categories:", error);
    }
  }

  // Make functions globally available
  window.editCategory = async function (id, currentName) {
    const newName = prompt("Edit category name:", currentName);
    if (!newName || newName.trim() === "") return;

    try {
      const response = await fetch(`/api/categories/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: newName.trim() }),
      });

      const result = await response.json();

      if (result.success) {
        showMessage("Category updated successfully!", "success");
        loadCategories();
      } else {
        showMessage("Error: " + (result.error || "Unknown error"), "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showMessage("An unexpected error occurred.", "error");
    }
  };

  window.deleteCategory = async function (id) {
    if (!confirm("Are you sure you want to delete this category?")) return;

    try {
      const response = await fetch(`/api/categories/${id}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (result.success) {
        showMessage("Category deleted successfully!", "success");
        loadCategories();
      } else {
        showMessage("Error: " + (result.error || "Unknown error"), "error");
      }
    } catch (error) {
      console.error("Error:", error);
      showMessage("An unexpected error occurred.", "error");
    }
  };
});
