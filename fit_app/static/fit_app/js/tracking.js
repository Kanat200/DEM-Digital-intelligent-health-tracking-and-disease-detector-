document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modal");
  const closeBtn = document.querySelector(".close");
  const stateForm = document.getElementById("state-form");

  function openModal() {
    modal.style.display = "flex";
  }

  function closeModal() {
    modal.style.display = "none";
  }

  closeBtn.addEventListener("click", closeModal);
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      closeModal();
    }
  });

  stateForm.addEventListener("submit", function (e) {
    e.preventDefault();
    alert("State and advice saved.");
    closeModal();
  });

  // Attach event listeners to all elements with class "state"
  document.querySelectorAll(".state").forEach((item) => {
    item.addEventListener("click", function () {
      openModal();
    });
  });
});
