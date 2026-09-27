const storageKey = "rag-to-the-future-part-one-progress";

const repairTriggers = document.querySelectorAll(".repair-trigger");
const completionInputs = document.querySelectorAll("[data-complete]");
const progressCount = document.querySelector("[data-progress-count]");

function loadCompletedLessons() {
  try {
    const storedProgress = JSON.parse(localStorage.getItem(storageKey));
    return Array.isArray(storedProgress) ? storedProgress : [];
  } catch {
    return [];
  }
}

function saveCompletedLessons(completedLessons) {
  try {
    localStorage.setItem(storageKey, JSON.stringify(completedLessons));
  } catch {
    // Progress remains visible for this visit when browser storage is unavailable.
  }
}

function updateProgress() {
  const completedLessons = [...completionInputs]
    .filter((input) => input.checked)
    .map((input) => input.dataset.complete);

  progressCount.textContent = completedLessons.length;
  saveCompletedLessons(completedLessons);
}

function restoreProgress() {
  const lessonIds = new Set([...completionInputs].map((input) => input.dataset.complete));
  const completedLessons = new Set(loadCompletedLessons().filter((lessonId) => lessonIds.has(lessonId)));

  completionInputs.forEach((input) => {
    input.checked = completedLessons.has(input.dataset.complete);
    input.closest(".repair").classList.toggle("is-complete", input.checked);
  });

  progressCount.textContent = completedLessons.size;
}

function toggleRepair(trigger) {
  const detail = document.querySelector(`#${trigger.getAttribute("aria-controls")}`);
  const isOpen = trigger.getAttribute("aria-expanded") === "true";

  trigger.setAttribute("aria-expanded", String(!isOpen));
  detail.hidden = isOpen;
}

repairTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => toggleRepair(trigger));
});

completionInputs.forEach((input) => {
  input.addEventListener("change", () => {
    input.closest(".repair").classList.toggle("is-complete", input.checked);
    updateProgress();
  });
});

restoreProgress();
