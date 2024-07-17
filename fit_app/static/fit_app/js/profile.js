document.addEventListener("DOMContentLoaded", function () {
  const profileSection = document.getElementById("profile-section");
  const passwordSection = document.getElementById("password-section");
  const googleFitSection = document.getElementById("google-fit-section");
  const tabs = document.querySelectorAll(".tab");

  function showSection(section) {
    if (section === "profile") {
      profileSection.classList.add("active");
      passwordSection.classList.remove("active");
      googleFitSection.classList.remove("active");
    } else if (section === "password") {
      passwordSection.classList.add("active");
      profileSection.classList.remove("active");
      googleFitSection.classList.remove("active");
    } else if (section === "google-fit") {
      googleFitSection.classList.add("active");
      passwordSection.classList.remove("active");
      profileSection.classList.remove("active");
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      tabs.forEach((tab) => tab.classList.remove("active"));
      this.classList.add("active");
      showSection(this.getAttribute("data-section"));
    });
  });

  // document
  //   .querySelector(".profile-form")
  //   .addEventListener("submit", function (e) {
  //     e.preventDefault();
  //     alert("Profile changes saved.");
  //   });

  document
    .querySelector(".password-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      alert("Password changed.");
    });
});

function cancelChanges() {
  alert("Changes canceled.");
}
