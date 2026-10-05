const githubUrl = "https://github.com/shahbaaz12/rag-to-the-future";

const parts = {
  one: {
    label: "PART I · 1985 · OUT OF TIME",
    caption: "Start in the professor's workshop. Give the machine a voice, a memory, and evidence for its answers.",
    link: "part-one.html",
    linkText: "Enter the 1985 workshop →",
  },
  two: {
    label: "PART II · 2045 · YOUR CHILDREN'S TOMORROW",
    caption: "The assistant now has tools and agency. Learn to let it plan, check its work, and ask before it acts.",
    link: "part-two.html",
    linkText: "Enter the 2045 workshop →",
  },
  three: {
    label: "PART III · ???? · THE LAST DEPARTURE",
    caption: "Give the assistant useful evidence: retrieve documents, resolve follow-ups, and choose the right search strategy.",
    link: "part-three.html",
    linkText: "Enter the Part III reading room →",
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
    one: ["analogue", "1985 / ANALOGUE WORKSHOP"],
    two: ["future", "2045 / FUTURE WORKSHOP"],
    three: ["frontier", "FRONTIER / YEAR UNCONFIRMED"],
  };
  const [asset, label] = views[partId];
  const image = document.getElementById("atlas-image");
  if (!image) return;
  image.src = `assets/workshop-${asset}.svg`;
  image.alt = `The clocktower square in the ${asset} workshop setting`;
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
