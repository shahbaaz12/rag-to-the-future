document.querySelectorAll(".repair-trigger").forEach(trigger => {
  trigger.addEventListener("click", () => {
    const detail = document.getElementById(trigger.getAttribute("aria-controls"));
    const isOpen = trigger.getAttribute("aria-expanded") === "true";
    trigger.setAttribute("aria-expanded", String(!isOpen));
    detail.hidden = isOpen;
  });
});

function openLinkedRepair() {
  const id = location.hash.slice(1);
  const trigger = [...document.querySelectorAll(".repair-trigger")].find(button => button.getAttribute("aria-controls") === id);
  if (!trigger) return;
  document.getElementById(id).hidden = false;
  trigger.setAttribute("aria-expanded", "true");
}

window.addEventListener("hashchange", openLinkedRepair);
openLinkedRepair();
