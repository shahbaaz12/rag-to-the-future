const githubUrl = "https://github.com/shahbaaz12/rag-to-the-future";

const parts = {
  one: {
    label: "PART I · 1985 · OUT OF TIME",
    caption: "Come into my workshop. I'll help you give the console a voice, carry a conversation, and connect its first tools.",
    link: "part-one.html",
    linkText: "Enter the 1985 workshop →",
  },
  two: {
    label: "PART II · 2015 · THE FUTURE WORKSHOP",
    caption: "Join me in the future workshop. We'll connect operations, trace their state, and pause for a person to choose.",
    link: "part-two.html",
    linkText: "Enter the 2015 workshop →",
  },
  three: {
    label: "PART III · 1885 · THE LAST DEPARTURE",
    caption: "Meet me at the frontier workshop. We'll find the relevant pages, resolve follow-ups, and inspect the information behind an answer.",
    link: "part-three.html",
    linkText: "Enter the 1885 workshop →",
  },
};

const dialog = document.querySelector("#syllabus-dialog");
const timeReadout = document.querySelector("#time-readout");
const capacitorCaption = document.querySelector("#capacitor-caption");
const destinationLink = document.querySelector("#destination-link");
const controlDeck = document.querySelector(".control-deck");

function setPart(partId) {
  const part = parts[partId];
  if (!part) return;

  document.querySelectorAll("[data-part]").forEach((control) => {
    const isActive = control.dataset.part === partId;
    control.classList.toggle("active", isActive);
    control.setAttribute("aria-pressed", String(isActive));
  });

  timeReadout.textContent = part.label;
  capacitorCaption.textContent = part.caption;
  destinationLink.href = part.link;
  destinationLink.textContent = part.linkText;
  if (controlDeck) controlDeck.dataset.activePart = partId;
  document.body.dataset.era = partId;
  updateAtlas(partId, part.link);
}

function updateAtlas(partId, link) {
  const views = {
    one: ["analogue", "1985 / ANALOG WORKSHOP"],
    two: ["future", "2015 / FUTURE WORKSHOP"],
    three: ["frontier", "1885 / FRONTIER WORKSHOP"],
  };
  const [asset, label] = views[partId];
  const image = document.getElementById("atlas-image");
  if (!image) return;
  image.src = `assets/workshop-${asset}.svg`;
  image.alt = `The clocktower square in the ${label.split(' / ')[1].toLowerCase()} setting`;
  document.getElementById("atlas-label").textContent = label;
  document.getElementById("atlas-link").href = link;
}

function openSyllabus() {
  if (dialog && !dialog.open) dialog.showModal();
}

document.querySelectorAll("[data-open-syllabus]").forEach((button) => {
  button.addEventListener("click", openSyllabus);
});

document.querySelector("[data-close-syllabus]")?.addEventListener("click", () => {
  dialog?.close();
});

dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

document.querySelectorAll("[data-part]").forEach((control) => {
  control.addEventListener("click", () => setPart(control.dataset.part));
});

document.querySelectorAll("[data-preview-part]").forEach((button) => {
  button.addEventListener("click", () => {
    setPart(button.dataset.previewPart);
    const behavior = matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth";
    controlDeck?.scrollIntoView({ behavior, block: "center" });
  });
});

document.querySelectorAll("#github-link, #footer-github-link").forEach((link) => {
  link.href = githubUrl;
});

setPart("one");
