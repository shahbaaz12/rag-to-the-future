/* Shared reading completion and manual records, migrated from the original Part I map. */
(() => {
  const key = "rag-to-the-future-course-progress";
  const legacyKey = "rag-to-the-future-part-one-progress";
  const structureKey = "rag-to-the-future-course-structure-version";
  let persistent = true;

  function normalise(values) {
    if (!Array.isArray(values)) return [];
    const valid = values.filter(value => typeof value === "number" || (typeof value === "string" && /^\d+$/.test(value)));
    return [...new Set(valid.map(Number).filter(value => Number.isInteger(value) && value >= 1 && value <= 21))];
  }

  function parse(raw) {
    try {
      const values = JSON.parse(raw);
      return Array.isArray(values) ? normalise(values) : null;
    } catch {
      return null;
    }
  }

  function read() {
    try {
      return parse(localStorage.getItem(key)) ?? parse(localStorage.getItem(legacyKey))?.filter(value => value <= 8) ?? [];
    } catch {
      persistent = false;
      return [];
    }
  }

  // Inserting the PDF lesson moves the existing Part III completions by one.
  try {
    if (localStorage.getItem(structureKey) !== "2") {
      const previous = parse(localStorage.getItem(key));
      if (previous) {
        const migrated = previous.filter(value => value <= 20).map(value => value >= 18 ? value + 1 : value);
        localStorage.setItem(key, JSON.stringify(migrated));
      }
      localStorage.setItem(structureKey, "2");
    }
  } catch { persistent = false; }
  let completed = new Set(read());

  function notify() {
    window.dispatchEvent(new CustomEvent("course-progress-change"));
  }

  function set(lesson, checked) {
    const number = Number(lesson);
    if (!normalise([number]).length) return;
    if (checked) completed.add(number);
    else completed.delete(number);
    try {
      localStorage.setItem(key, JSON.stringify([...completed]));
      localStorage.setItem(legacyKey, JSON.stringify([...completed].filter(value => value <= 8).map(String)));
      persistent = true;
    } catch {
      persistent = false;
    }
    notify();
  }

  window.CourseProgress = {
    has: lesson => completed.has(Number(lesson)),
    count: (start = 1, end = 21) => [...completed].filter(value => value >= start && value <= end).length,
    isPersistent: () => persistent,
    set,
  };

  window.addEventListener("storage", event => {
    if (event.key !== key && event.key !== legacyKey && event.key !== null) return;
    completed = new Set(read());
    notify();
  });
  window.addEventListener("pageshow", () => {
    if (persistent) completed = new Set(read());
    notify();
  });
})();
