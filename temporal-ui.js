(() => {
  const progress = window.CourseProgress;
  if (!progress) return;

  function refreshMeters() {
    document.querySelectorAll("[data-course-meter]").forEach(meter => {
      const start = Number(meter.dataset.start || 1);
      const end = Number(meter.dataset.end || 20);
      const count = progress.count(start, end);
      const total = end - start + 1;
      meter.querySelector("[data-meter-count]").textContent = count;
      const bar = meter.querySelector("[role='progressbar']");
      bar.setAttribute("aria-valuenow", String(count));
      bar.style.setProperty("--charge", `${count / total * 100}%`);
      meter.dataset.charged = String(count > 0);
    });
  }

  function refreshInputs() {
    document.querySelectorAll("[data-complete]").forEach(input => {
      input.checked = progress.has(input.dataset.complete);
      input.closest(".repair, .course-card, .lesson-completion")?.classList.toggle("is-complete", input.checked);
    });
  }

  function refreshLegacyInstrument() {
    const count = progress.count(1, 8);
    document.querySelectorAll("[data-progress-count]").forEach(label => { label.textContent = count; });
    document.querySelectorAll("[data-subsystem]").forEach(label => {
      const lessons = label.dataset.subsystem.split(",").map(Number);
      label.textContent = lessons.every(progress.has) ? "RECORDED" : "PENDING";
      label.dataset.ready = String(lessons.every(progress.has));
    });
  }

  function refresh() {
    refreshMeters();
    refreshInputs();
    refreshLegacyInstrument();
    document.querySelectorAll("[data-save-note]").forEach(note => {
      note.textContent = progress.isPersistent() ? "Saved on this browser · self-reported" : "This visit only · browser storage unavailable";
    });
  }

  document.querySelectorAll("[data-complete]").forEach(input => {
    input.addEventListener("change", () => progress.set(input.dataset.complete, input.checked));
  });
  window.addEventListener("course-progress-change", refresh);
  refresh();
})();
