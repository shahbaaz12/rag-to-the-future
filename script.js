const githubUrl = "https://github.com/shahbaaz12/rag-to-the-future";

const parts = {
  one: { label: "PART I · 1985", power: "33%", caption: "Foundation systems: teach the machine how to speak, remember, and retrieve." },
  two: { label: "PART II · 2045", power: "67%", caption: "Capable systems: let the machine plan, use tools, and ask before it acts." },
  three: { label: "PART III · UNKNOWN", power: "100%", caption: "Reliable systems: measure, secure, observe, and recover the machine." },
};

const dialog = document.querySelector("#syllabus-dialog");
const timeReadout = document.querySelector("#time-readout");
const powerFill = document.querySelector("#power-fill");
const powerNumber = document.querySelector("#power-number");
const capacitorCaption = document.querySelector("#capacitor-caption");

function setPart(partId) {
  const part = parts[partId];
  document.querySelectorAll(".terminal").forEach((terminal) => {
    terminal.classList.toggle("active", terminal.dataset.part === partId);
  });
  timeReadout.textContent = part.label;
  powerFill.style.width = part.power;
  powerNumber.textContent = part.power;
  capacitorCaption.textContent = part.caption;
}

function openSyllabus() {
  dialog.showModal();
}

document.querySelectorAll("[data-open-syllabus]").forEach((button) => {
  button.addEventListener("click", openSyllabus);
});

document.querySelector("[data-close-syllabus]").addEventListener("click", () => dialog.close());

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

document.querySelectorAll(".terminal").forEach((terminal) => {
  terminal.addEventListener("click", () => setPart(terminal.dataset.part));
});

document.querySelectorAll("[data-select-part]").forEach((button) => {
  button.addEventListener("click", () => {
    const partId = button.dataset.selectPart;
    setPart(partId);
    document.querySelector(".capacitor-stage").scrollIntoView({ behavior: "smooth", block: "center" });
  });
});

document.querySelectorAll("#github-link, #footer-github-link").forEach((link) => {
  link.href = githubUrl;
});
