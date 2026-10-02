(() => {
  const storageKey = "rag-to-the-future-theme";
  const root = document.documentElement;
  let theme = "dark";
  try {
    if (localStorage.getItem(storageKey) === "light") theme = "light";
  } catch { /* The switch still works when browser storage is unavailable. */ }
  // Apply the saved preference in the head, before the page is painted.
  root.dataset.theme = theme;

  const icons = {
    light: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4m11.2 11.2L19 19M5 19l1.4-1.4M17.6 6.4 19 5"/></svg>',
    dark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M20.5 13a9 9 0 0 1-9.5-9.5A9 9 0 1 0 20.5 13Z"/></svg>',
  };

  function updateButton() {
    const button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    button.innerHTML = `${icons[next]}<span>${next === "light" ? "Light" : "Dark"}</span>`;
    button.setAttribute("aria-label", `Switch to ${next} theme`);
    button.setAttribute("title", `Switch to ${next} theme`);
  }

  function initialise() {
    const menu = document.querySelector(".topbar nav");
    if (!menu) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "theme-toggle";
    button.setAttribute("data-theme-toggle", "");
    menu.append(button);
    updateButton();
    button.addEventListener("click", () => {
      root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
      try { localStorage.setItem(storageKey, root.dataset.theme); } catch {}
      updateButton();
    });
  }

  window.addEventListener("storage", event => {
    if (event.key !== storageKey && event.key !== null) return;
    root.dataset.theme = event.newValue === "light" ? "light" : "dark";
    updateButton();
  });
  // Restore the preference when Back/Forward revives a cached page.
  window.addEventListener("pageshow", () => {
    try { root.dataset.theme = localStorage.getItem(storageKey) === "light" ? "light" : "dark"; } catch {}
    updateButton();
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialise, { once: true });
  else initialise();
})();
