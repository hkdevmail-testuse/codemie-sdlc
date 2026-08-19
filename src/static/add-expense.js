// Add expense page specific functionality - Category Autocomplete
document.addEventListener("DOMContentLoaded", () => {
  const categoryInput = document.getElementById("category");
  const categoryList = document.getElementById("categoryList");

  // Load categories for autocomplete
  if (categoryInput && categoryList) {
    fetch("/api/categories")
      .then((response) => response.json())
      .then((categories) => {
        categoryList.innerHTML = "";
        categories.forEach((cat) => {
          const option = document.createElement("option");
          option.value = cat.name;
          categoryList.appendChild(option);
        });
      })
      .catch((error) => {
        console.error("Error loading categories:", error);
      });
  }
});
