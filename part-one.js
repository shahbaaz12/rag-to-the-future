const storageKey = "rag-to-the-future-part-one-progress";

const repairTriggers = document.querySelectorAll(".repair-trigger");
const completionInputs = document.querySelectorAll("[data-complete]");
const progressCount = document.querySelector("[data-progress-count]");

function loadCompletedLessons() {
  try {
    return JSON.parse(localStorage.getItem(storageKey)) ?? [];
  } catch {
    return [];
  }
}

function saveCompletedLessons(completedLessons) {
  localStorage.setItem(storageKey, JSON.stringify(completedLessons));
}

function updateProgress() {
  const completedLessons = [...completionInputs]
    .filter((input) => input.checked)
    .map((input) => input.dataset.complete);

  progressCount.textContent = completedLessons.length;
  saveCompletedLessons(completedLessons);
}

function restoreProgress() {
  const completedLessons = new Set(loadCompletedLessons());

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
