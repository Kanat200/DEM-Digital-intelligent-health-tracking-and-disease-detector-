function showModal(event) {
  event.preventDefault(); // Prevent form submission
  document.getElementById("modal").style.display = "flex";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

// Ensure the modal is hidden when the page loads
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("modal").style.display = "none";
});
