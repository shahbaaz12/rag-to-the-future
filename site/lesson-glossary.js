(() => {
  const data = document.getElementById("lesson-terms");
  if (!data) return;
  const terms = JSON.parse(data.textContent);
  const toggle = document.querySelector("[data-glossary-toggle]");
  const panel = document.getElementById("lesson-glossary");
  const search = panel.querySelector("input");
  const list = panel.querySelector("[data-glossary-list]");
  const count = panel.querySelector("[data-glossary-count]");

  function renderList() {
    const query = search.value.trim().toLowerCase();
    const matches = terms.filter(term => `${term.term} ${term.definition}`.toLowerCase().includes(query));
    list.replaceChildren();
    for (const term of matches) {
      const item = document.createElement("li");
      const name = document.createElement("strong");
      name.className = `glossary-name glossary-name--${term.category}`;
      name.textContent = term.term;
      const description = document.createElement("p");
      description.textContent = term.definition;
      const origin = document.createElement("a");
      origin.href = `lesson-${term.lesson}.html#${term.anchor}`;
      origin.textContent = `Introduced in Lesson ${term.lesson}`;
      item.append(name, description, origin);
      list.append(item);
    }
    count.textContent = `${matches.length} of ${terms.length} terms`;
    if (!matches.length) {
      const empty = document.createElement("li");
      empty.textContent = "No matching terms. Try another word.";
      list.append(empty);
    }
  }

  function close(returnFocus = false) {
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    if (returnFocus) toggle.focus();
  }

  toggle.addEventListener("click", () => {
    if (!panel.hidden) return close(true);
    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    search.focus();
  });
  panel.querySelector("[data-glossary-close]").addEventListener("click", () => close(true));
  document.addEventListener("click", event => {
    if (!panel.hidden && !panel.contains(event.target) && !toggle.contains(event.target)) close();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !panel.hidden) close(true);
  });
  document.addEventListener("focusin", event => {
    if (!panel.hidden && !panel.contains(event.target) && !toggle.contains(event.target)) close();
  });
  search.addEventListener("input", renderList);
  renderList();
})();
