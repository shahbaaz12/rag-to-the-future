(() => {
  const progress = window.CourseProgress;
  if (!progress) return;

  function refreshRoutes() {
    const counts = [...document.querySelectorAll('[data-route-count]')];
    document.querySelectorAll('[data-route-progress]').forEach(track => {
      const lesson = Number(track.dataset.currentLesson);
      const part = Number(track.dataset.currentPart);
      const index = counts.findIndex(label => lesson >= Number(label.dataset.start) && lesson <= Number(label.dataset.end));
      const current = counts[index];
      const position = current ? lesson - Number(current.dataset.start) + 1 : 0;
      const total = current ? Number(current.dataset.end) - Number(current.dataset.start) + 1 : 0;
      const segment = current ? index : Math.max(0, part - 1);
      const percent = counts.length ? (segment + (current ? position / total : 0)) / counts.length * 100 : 0;
      const vehicle = segment >= 2 ? 'train' : segment >= 1 ? 'flying-car' : 'car';
      counts.forEach(label => {
        const size = Number(label.dataset.end) - Number(label.dataset.start) + 1;
        label.textContent = label === current ? `${position} / ${size}` : `${size} lessons`;
      });
      track.style.setProperty('--route-progress', `${percent}%`);
      track.setAttribute('aria-valuenow', String(Math.round(percent)));
      track.setAttribute('aria-valuetext', current ? `Lesson ${lesson}, lesson ${position} of ${total} in Part ${index + 1}` : part ? `Part ${part}` : 'Course start');
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
