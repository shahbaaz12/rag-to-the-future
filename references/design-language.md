# RAG to the Future design language

## Purpose

**RAG to the Future** is an interactive learning journey disguised as a time-travel rescue. The learner should feel as though they are repairing a machine with the professor, not consuming a disconnected course catalogue.

Each page must make three things legible at once:

1. the story problem at hand;
2. the AI-system capability being earned; and
3. the learner's position in the three-part journey.

The visual language takes its lead from an after-hours inventor's workshop: engineered, atmospheric, precise, and a little dangerous. It must remain readable and useful for learning. The experience references the emotional grammar of retro time-travel adventure—maps, instruments, hand-built machinery, risky jumps—while its illustrations, copy, interface shapes, and terminology remain original to RAG to the Future.

## Design principles

- **One system, visibly evolving.** Reuse the same companion machine, archive, instruments, and temporal map across the course. Each lesson adds a discernible capability or repair.
- **Pressure before explanation.** Open a lesson with a concrete failure, then reveal the concept that resolves it.
- **Make infrastructure physical.** Retrieval is an archive search. An agent is a control panel selecting actions. Observability is an instrument cluster. Evaluation is a test track.
- **Progress is a journey.** Lesson completion should charge the Flux Capacitor, repair a visible subsystem, or reveal a route. Never reduce progress to an anonymous percentage alone.
- **Cinematic restraint.** Use darkness, light, texture, and motion to create suspense. Reserve high-intensity effects for a meaningful action, failure, or milestone.

## Foundations

### Colour tokens

Use the existing CSS custom properties as the global base. Do not introduce a rainbow of one-off colours.

| Token | Value | Use |
|---|---:|---|
| `--ink` | `#06090f` | Primary page background; night outside the workshop. |
| `--panel` | `#0b111b` | Cards, navigation, contained reading surfaces. |
| `--panel-2` | `#111a27` | Raised panels and diagrams. |
| `--paper` | `#f3eee2` | Primary text; warm paper against the cold laboratory. |
| `--muted` | `#9da7b6` | Labels, secondary copy, inactive controls. |
| `--blue` | `#76e2ff` | Temporal energy, primary action, Part I, focus states. |
| `--blue-deep` | `#1aa3e5` | Blue glow and subtle diagram depth. |
| `--gold` | `#f4b85f` | Mission language, key insight, Part II, historical artefacts. |
| `--red` | `#f17667` | Faults, danger, Part III, destructive or high-stakes states. |
| `--line` | `rgba(220,235,255,.16)` | Panel rules, dividers, quiet technical structure. |

Use an almost-black background and warm off-white text by default. Blue is the main interactive colour. Gold highlights knowledge, clues, and planned actions. Red communicates a real issue, irreversible-looking risk, or the harsh conditions of the final frontier; never use it merely for decoration.

### Typography

| Role | Typeface | Treatment |
|---|---|---|
| Interface and body | `DM Sans` | Clear, calm, human. Use for explanations and controls. |
| Instrumentation | `DM Mono` | Uppercase labels, metadata, code-adjacent details, timestamps, status. Track out slightly. |
| Story and display | `Playfair Display` | Reserve for major page statements, professor quotations, and a few pivotal emphasis words. |

Use display type sparingly. The contrast between the practical sans and literary serif is what gives the story weight. Keep body copy at a comfortable reading size and 1.6–1.75 line height. Avoid all-caps for paragraphs; it belongs to instrumentation labels only.

### Texture and depth

Use a restrained film-grain/noise layer, radial blue illumination, thin scan lines, and soft inner shadows to suggest an analogue laboratory. Texture must not interfere with text or diagrams. Panels should feel fabricated from dark enamel, glass, and engraved metal: sharp or lightly rounded corners, thin luminous rules, and occasional warm brass details.

## Layout system

### Page anatomy

Every major page uses this order:

1. **Topbar:** brand, journey position, progress, and a route back to the map.
2. **Story header:** period, immediate problem, title, and the system capability being earned.
3. **Main learning body:** explanation, diagram/simulation, and practical work.
4. **Repair record:** what changed in the companion system and why it mattered.
5. **Next route:** the locked or unlocked next lesson, with a one-sentence story tease.

The home page is the exception: it leads with the Flux Capacitor and the complete three-part route.

### Grid and spacing

- Use a spacious single-column reading flow for lesson prose, capped around 720px.
- Use a wider 12-column desktop canvas for headers, maps, course cards, and diagrams.
- Keep a consistent outer gutter: `clamp(1.3rem, 5vw, 5.5rem)`.
- Use generous vertical rhythm. Section breaks should feel like entering a different workshop zone, not simply the next card.
- Place dense technical information inside distinct panels, then return to open space for narrative copy.

### Responsive behaviour

At narrow widths, preserve narrative order before visual symmetry. Collapse multi-column cards into stacked sections; retain labels, state, and route controls. Do not hide lesson context merely to fit a mobile layout. Instrument graphics may simplify, but must keep their equivalent text description.

## Reusable interface elements

### Navigation and wayfinding

- The `RTF` diamond is the maker's mark and always routes home.
- A compact **time readout** identifies `PART I · 1985`, `PART II · 2045`, or `PART III · FRONTIER`.
- Use a **route strip** or mini-map to show the three acts and current lesson. It should show progression through system state: voice → memory → action → trust.
- Controls read as deliberate instruments: mono labels, restrained borders, clear selected state, and a visible focus ring.

### Buttons

- **Primary:** electric blue fill with dark text. Use for the current next action only.
- **Secondary:** transparent dark panel with a thin rule. Use for optional reading or map actions.
- **Text button:** blue mono label and an arrow. Use for lower-emphasis navigation.
- **Danger/interrupt:** red only when an action carries narrative or functional risk. Pair it with plain language.

Use verb-led labels: `Begin the first jump`, `Inspect the archive`, `Run the test track`, `Set destination`.

### Cards and panels

- Major journey cards receive a 3px luminous left edge in their part accent.
- Panels use thin rules and low-contrast surfaces; avoid rounded, generic dashboard cards.
- Lesson cards carry an index, a time marker, a one-sentence story stake, concept tags, and a clear status.
- Code, traces, and data samples use a darker inset panel with mono type and a textual heading.

### System diagrams

Diagrams should be operational, not decorative. Use a small vocabulary of nodes, routes, containers, and signals:

- **Circle/node:** a model, tool, document source, or decision point.
- **Archive drawer/stack:** a knowledge source or vector store.
- **Wire/route:** data or control flow; animate only on explicit interaction.
- **Diamond:** validation, schema, or a human decision.
- **Instrument gauge:** measured quality, latency, cost, or system health.

Label every visual connection. Give diagrams a short caption that states the lesson's conclusion in plain language.

### Progress states

| State | Visual treatment | Meaning |
|---|---|---|
| Locked | Dim panel, muted route, a future time marker | The story has not yet reached this capability. |
| Available | Part accent rule and a subtle pulse | The learner can begin this repair. |
| In progress | Animated signal moving through the route | The learner is currently testing or building it. |
| Repaired | Charged node, solid route, concise repair note | The system capability is now earned. |
| Fault | Red alert light and a precise error statement | A known failure requires attention. |

Do not depend on colour alone; pair state with words, icons, or line patterns.

## The three time periods

The course remains one world. The base ink, paper, engineering rules, and typography do not change. Each act shifts its lighting, materials, landscapes, and system metaphor.

| Part | Story setting | Dominant palette | Visual materials | System metaphor | Motion |
|---|---|---|---|---|---|
| I — **Out of Time** | The professor's 1985 workshop | Electric blue, midnight, paper | Blueprints, notebooks, CRT grids, coils, labelled drawers | Give the machine a voice and a memory | Slow pulses, archive drawers opening, routes finding a signal |
| II — **Your Children's Tomorrow** | A busy future workshop and remote rescue route | Brass gold, blue, deep charcoal | Transit maps, service bays, route lines, component tags, controlled terminals | Turn knowledge into careful action | Deliberate route assembly, tool handoffs, paused approval gates |
| III — **The Last Departure** | A resource-poor frontier workshop | Signal red, ember gold, worn charcoal | Weathered instruments, low-power gauges, patched cables, field notes | Make the system trustworthy under pressure | Intermittent signal, restrained fault flicker, recovery routes reconnecting |

### Part I: Out of Time

Part I feels intimate and investigative. Blue dominates, with gold used for notebooks and the professor's guidance. The space is quiet enough to learn from first principles. Use visual motifs of fragments becoming a coherent route: scattered notes, highlighted passages, a search beam, and a growing archive.

The Flux Capacitor begins incomplete. Its branches are dim; every lesson restores a component. The closing **First Jump** should feel like the first time the machine has earned a burst of speed and light.

### Part II: Your Children's Tomorrow

Part II feels active and consequential. Gold becomes the part accent because this is the era of systems that can affect the world. Retain blue for the intelligence thread so the learner sees continuity with Part I. Diagrams should show explicit choices, branches, and pause points.

Show a real workshop ecology: order boards, compatible-part labels, repair routes, tool bays, and human approval controls. The system should appear more capable, but every action must have a visible check, evidence source, or person responsible.

### Part III: The Last Departure

Part III feels exposed and rigorous. Red is a warning light, not a page wash; pair it with embers of gold and low-power blue to retain contrast. The frontier has less polish: patched panels, sparse readouts, intermittent routes, and a landscape beyond the workshop.

This part makes quality visible. Use test traces, evidence trails, failure classifications, cost gauges, and recovery paths. When a system succeeds, do not celebrate with a generic confetti effect; show a stable instrument reading, a restored route, and enough charged power for the final departure.

## Motion and interaction

Motion explains state changes. It must never be required to understand the lesson.

- Use a 180–300ms ease-out transition for hover and focus feedback.
- Use 800–1600ms slow pulses for stable energy and available routes.
- Reserve 1.5–3s staged sequences for an intentional action: selecting a destination, running retrieval, asking approval, or completing a repair.
- Avoid continuous large-area animation, camera shake, auto-playing sounds, or flashing content.
- Under `prefers-reduced-motion: reduce`, remove nonessential movement, transitions, and scroll effects. Replace animated flow with static routes and clear state text.

Interactive moments should teach: selecting a journey changes the time readout and its system premise; an archive search shows why retrieval picked a source; a tool action stops at approval; an evaluation run exposes a specific failure mode.

## Narrative voice and copy

Write as a practical guide within a cinematic world. The professor is warm, exacting, and concise. The learner is capable; the story gives them a reason to practise, never a reason to feel inadequate.

- Open with a concrete situation: “The navigation console returned a place that does not exist.”
- Name the cost of failure before the concept: “A similar part is not a compatible part.”
- Explain the technical idea in clear language immediately after the story beat.
- End with a repair statement: “The archive assistant can now cite the notebook passage it used.”
- Use short, original period labels and mission names. Avoid extended quotes or visual imitation of any film dialogue, logos, props, or signature type treatments.

Preferred verbs: **repair, trace, inspect, ground, route, verify, pause, recover, test, choose**.

Avoid generic course language such as “master,” “unlock your potential,” “revolutionary,” and “next-generation.”

## Accessibility requirements

- Meet WCAG AA contrast for text and controls. Check blue and gold text against the dark background at the actual font size.
- Use semantic landmarks, ordered headings, visible keyboard focus, and native buttons for actions.
- Give every instrument, diagram, and animated state a short text equivalent. Decorative texture is `aria-hidden`.
- Never communicate completion, risk, or route availability by colour alone.
- Keep body content selectable, zoomable to 200%, and readable without horizontal scrolling.
- Support `prefers-reduced-motion` and do not auto-play audio.
- Dialogs trap focus, return focus to their trigger on close, and provide an explicit close control.
- Keep labels concise and specific: `Open all 24 lessons`, not `Click here`.

## Build checklist

Before a new page or component ships, check:

- Does it show the current story problem and the system capability being built?
- Does it use the base tokens and the correct part accent instead of a new visual language?
- Does every interactive effect explain something or provide feedback?
- Is the important information still available without motion, colour, hover, or large-screen layout?
- Does the page leave the learner with a visible repair, insight, or route forward?
