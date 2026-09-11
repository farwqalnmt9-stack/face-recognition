(() => {
  document.querySelectorAll("[data-product-showcase]").forEach((showcase) => {
    const tabs = [...showcase.querySelectorAll("[data-product-tab]")];
    const panels = [...showcase.querySelectorAll("[data-product-panel]")];
    if (!tabs.length || !panels.length) return;

    const activate = (index, moveFocus = false) => {
      tabs.forEach((tab, tabIndex) => {
        const active = tabIndex === index;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", String(active));
        tab.tabIndex = active ? 0 : -1;
        if (active && moveFocus) tab.focus();
      });
      panels.forEach((panel, panelIndex) => {
        const active = panelIndex === index;
        panel.hidden = !active;
        panel.classList.toggle("is-active", active);
      });
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => activate(index));
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowUp", "ArrowDown", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let next = index;
        if (event.key === "ArrowDown") next = (index + 1) % tabs.length;
        if (event.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        activate(next, true);
      });
    });
  });
})();
