// CSV Import/Export functionality
async function handleCSVImport(event) {
  const file = event.target.files[0];
  if (!file) return;

  const importMessage = document.getElementById("importMessage");
  importMessage.style.display = "block";
  importMessage.textContent = "Importing...";
  importMessage.className = "info-message";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/import-csv", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      importMessage.textContent = `Import successful! Imported: ${result.imported}, Skipped: ${result.skipped}`;
      importMessage.className = "success-message";

      if (result.errors && result.errors.length > 0) {
        const errorList = result.errors
          .map((e) => `Row ${e.row}: ${e.error}`)
          .join("<br>");
        importMessage.innerHTML += `<br><br><strong>Errors:</strong><br>${errorList}`;
      }

      // Reload the page after 3 seconds to show updated data
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    } else {
      importMessage.textContent = "Import failed: " + (result.error || "Unknown error");
      importMessage.className = "error-message";
    }
  } catch (error) {
    console.error("Error:", error);
    importMessage.textContent = "An unexpected error occurred during import.";
    importMessage.className = "error-message";
  }

  // Clear the file input
  event.target.value = "";
}
