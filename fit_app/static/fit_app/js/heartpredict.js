document.addEventListener("DOMContentLoaded", function () {
  const tooltipElements = document.querySelectorAll(".tooltip");
  tooltipElements.forEach((el) => {
    el.addEventListener("mouseover", function () {
      const tooltip = document.createElement("div");
      tooltip.className = "tooltip-text";
      tooltip.innerText = el.getAttribute("data-tooltip");
      document.body.appendChild(tooltip);
      const rect = el.getBoundingClientRect();
      tooltip.style.left = `${rect.left + window.scrollX}px`;
      tooltip.style.top = `${rect.bottom + window.scrollY}px`;
    });
    el.addEventListener("mouseout", function () {
      document.querySelectorAll(".tooltip-text").forEach((tip) => tip.remove());
    });
  });
});
