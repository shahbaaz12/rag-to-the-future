document.addEventListener("click", async (event) => {
  const copyButton = event.target.closest("[data-copy-code]");
  if (copyButton) {
    const explorer = copyButton.closest(".code-explorer");
    const code = explorer?.querySelector(".code-explorer__source")?.textContent || "";
    await navigator.clipboard.writeText(code);
    copyButton.textContent = "✓";
    window.setTimeout(() => { copyButton.textContent = "⧉"; }, 1400);
    return;
  }

  const note = event.target.closest(".code-explorer__note");
  if (!note) return;
  const explorer = note.closest(".code-explorer");
  explorer.querySelectorAll(".code-explorer__note, .code-explorer__line").forEach((element) => {
    element.classList.remove("is-active");
  });
  explorer.querySelectorAll(".code-explorer__note").forEach((element) => {
    element.setAttribute("aria-expanded", "false");
  });
  note.classList.add("is-active");
  note.setAttribute("aria-expanded", "true");
  explorer.querySelector(`.code-explorer__line[data-line="${note.dataset.line}"]`)?.classList.add("is-active");
});
