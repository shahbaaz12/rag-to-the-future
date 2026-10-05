(() => {
  const progress = window.CourseProgress;
  if (!progress) return;

  function refreshRoutes() {
    let completed = 0;
    let partFractions = 0;
    const counts = document.querySelectorAll('[data-route-count]');
    counts.forEach(label => {
      const start = Number(label.dataset.start);
      const end = Number(label.dataset.end);
      const total = end - start + 1;
      const count = progress.count(start, end);
      label.textContent = `${count} / ${total}`;
      completed += count;
      partFractions += count / total;
    });
    document.querySelectorAll('[data-route-progress]').forEach(track => {
      const percent = counts.length ? partFractions / counts.length * 100 : 0;
      const vehicle = partFractions >= 2 ? 'train' : partFractions >= 1 ? 'flying-car' : 'car';
      track.style.setProperty('--route-progress', `${percent}%`);
      track.setAttribute('aria-valuenow', String(Math.round(percent)));
      track.setAttribute('aria-valuetext', `${completed} of 20 lessons complete`);
      track.querySelector('img').setAttribute('src', `assets/progress-${vehicle}.svg`);
    });
  }

  function refreshInputs() {
    document.querySelectorAll("[data-complete]").forEach(input => {
      input.checked = progress.has(input.dataset.complete);
      input.closest(".repair, .course-card, .lesson-completion")?.classList.toggle("is-complete", input.checked);
    });
  }

  function refreshLegacyInstrument() {
    document.querySelectorAll("[data-subsystem]").forEach(label => {
      const lessons = label.dataset.subsystem.split(",").map(Number);
      label.textContent = lessons.every(progress.has) ? "COMPLETE" : "PENDING";
      label.dataset.ready = String(lessons.every(progress.has));
    });
  }

  function refresh() {
    refreshRoutes();
    refreshInputs();
    refreshLegacyInstrument();
    document.querySelectorAll("[data-save-note]").forEach(note => {
      note.textContent = progress.isPersistent() ? "Saved on this browser" : "This visit only · browser storage unavailable";
    });
  }

  document.querySelectorAll("[data-complete]").forEach(input => {
    input.addEventListener("change", () => progress.set(input.dataset.complete, input.checked));
  });
  window.addEventListener("course-progress-change", refresh);
  refresh();
})();
