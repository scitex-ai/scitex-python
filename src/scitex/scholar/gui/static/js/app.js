/**
 * Scholar GUI - Tab Manager
 *
 * Manages tab switching for the Scholar SPA.
 */
document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab-btn");
  const panels = document.querySelectorAll(".tab-panel");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;

      tabs.forEach((t) => t.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));

      tab.classList.add("active");
      const panel = document.getElementById("tab-" + target);
      if (panel) panel.classList.add("active");
    });
  });
});
