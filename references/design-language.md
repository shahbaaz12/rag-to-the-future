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
- **Progress is a journey.** Narrative chapters introduce the next obstacle. The bottom journey menu shows saved lesson completion on one continuous track with a single changing vehicle. Keep repair-count panels out of the workshop illustrations.
- **Cinematic restraint.** Use darkness, light, texture, and motion to create suspense. Reserve high-intensity effects for a meaningful action, failure, or milestone.

## Foundations

### Color tokens

Use the existing CSS custom properties as the global base. Do not introduce a rainbow of one-off colors.

| Token | Value | Use |
|---|---:|---|
| `--ink` | `#06090f` | Primary page background; night outside the workshop. |
| `--panel` | `#0b111b` | Cards, navigation, contained reading surfaces. |
| `--panel-2` | `#111a27` | Raised panels and diagrams. |
| `--paper` | `#f3eee2` | Primary text; warm paper against the cold laboratory. |
| `--muted` | `#9da7b6` | Labels, secondary copy, inactive controls. |
| `--blue` | `#76e2ff` | Temporal energy, primary action, Part I, focus states. |
| `--blue-deep` | `#1aa3e5` | Blue glow and subtle diagram depth. |
| `--gold` | `#f4b85f` | Mission language, key insight, Part II, historical artifacts. |
| `--red` | `#f17667` | Faults, danger, Part III, destructive or high-stakes states. |
| `--line` | `rgba(220,235,255,.16)` | Panel rules, dividers, quiet technical structure. |

Use an almost-black background and warm off-white text by default. Blue is the main interactive color. Gold highlights knowledge, clues, and planned actions. Red communicates a real issue, irreversible-looking risk, or the harsh conditions of the final frontier; never use it merely for decoration.

### Typography

| Role | Typeface | Treatment |
|---|---|---|
| Interface and body | `DM Sans` | Clear, calm, human. Use for explanations and controls. |
| Instrumentation | `Share Tech Mono`, with `DM Mono` as fallback | Uppercase labels, metadata, timestamps, status. Track out slightly. |
| Act and display | `Oswald` | Poster-style act names and major map statements. Technical lesson titles use a calmer upright treatment. |

Use display type sparingly. Let the practical body face and analog instrumentation provide contrast. Keep body copy at a comfortable reading size and 1.6–1.75 line height. Avoid all-caps for paragraphs; it belongs to instrumentation labels and display titles only.

### Texture and depth

Use a restrained film-grain/noise layer, radial blue illumination, thin scan lines, and soft inner shadows to suggest an analog laboratory. Texture must not interfere with text or diagrams. Panels should feel fabricated from dark enamel, glass, and engraved metal: sharp or lightly rounded corners, thin luminous rules, and occasional warm brass details.

## Layout system

### Page anatomy

Every major page uses this order:

1. **Topbar:** brand, journey position, and a route back to the map.
2. **Story header:** period, immediate problem, title, and the system capability being earned.
3. **Main learning body:** explanation, diagram/simulation, and practical work.
4. **Lesson completion:** automatically record the lesson when the end of teaching becomes visible, with a checkbox for manual completion and undo.
5. **Next route:** direct previous/next lesson links. Published lessons remain accessible regardless of recorded completion.

The home page is the exception: it leads with the Flux Capacitor and the complete three-part route.

### Grid and spacing

- Use a spacious single-column reading flow for lesson prose, capped around 720px.
- Use a wider 12-column desktop canvas for headers, maps, course cards, and diagrams.
- Keep a consistent outer gutter: `clamp(1.3rem, 5vw, 5.5rem)`.
- Use generous vertical rhythm. Section breaks should feel like entering a different workshop zone, not simply the next card.
- Place dense technical information inside distinct panels, then return to open space for narrative copy.

### Responsive behavior

At narrow widths, preserve narrative order before visual symmetry. Collapse multi-column cards into stacked sections; retain labels, state, and route controls. Do not hide lesson context merely to fit a mobile layout. Instrument graphics may simplify, but must keep their equivalent text description.

## Reusable interface elements

### Navigation and wayfinding

- The `RTF` diamond is the maker's mark and always routes home.
- A compact **time readout** identifies `PART I · 1985`, `PART II · 2015`, or `PART III · 1885`. The first sample opening also references a 1955 diagram.
- Use one bottom **journey menu** in normal document flow with all three eras. Each part shows its completed/published lesson count. One continuous track spans the whole menu, with each workshop occupying a third. Combine the three part-completion fractions to position a single vehicle: car in the first third, flying car in the second, train in the last. The menu scrolls with the page; do not make it sticky or fixed.
- On lesson pages, a floating left **On this page** index links to sections within the current lesson and highlights the current section. Below 1200px it becomes a collapsible control at the lower left. Leave room below the lesson menu so floating reading controls do not cover it. Keep a clear gutter between the desktop index and reading material.
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
- All three maps share the same lesson-card grid: index, title, concise description, reading link and a separate completion checkbox. Stack cards on small screens. Homepage part cards are whole-card links with visible keyboard focus.
- Code, traces, and data samples use a darker inset panel with mono type and a textual heading.

### System diagrams

Diagrams should be operational, not decorative. Use a small vocabulary of nodes, routes, containers, and signals:

- **Circle/node:** a model, tool, document source, or decision point.
- **Archive drawer/stack:** a knowledge source or vector store.
- **Wire/route:** data or control flow; animate only on explicit interaction.
- **Diamond:** validation, schema, or a human decision.
- **Instrument gauge:** measured quality, latency, cost, or system health.

Label every visual connection. Give diagrams a short caption that states the lesson's conclusion in plain language.

Lesson graph panels use `lesson-graphs.css` and static SVG with the current era's accent. `scripts/graph_topology.py` reads registered nodes, ordinary/conditional edges, explicit joins and loops from the displayed construction snippets without executing them. `scripts/lesson_graphs.py` inserts a diagram immediately after each compilation snippet and renders the three framework-managed agent wrappers as conceptual flows. Keep a readable caption and expandable connection list with every diagram; permit horizontal scrolling inside the diagram on narrow screens while the caption stays in the reading column. Keep checkpointer storage outside the node path. Add a title/caption in `lesson-graphs.json` for new constructions so rebuilds retain the visual.

### Progress states

| State | Visual treatment | Meaning |
|---|---|---|
| Locked | Dim panel, muted route, a future time marker | The story has not yet reached this capability. |
| Available | Part accent rule and a subtle pulse | The learner can begin this repair. |
| In progress | Animated signal moving through the route | The learner is currently testing or building it. |
| Repaired | Charged node, solid route, concise repair note | The system capability is now earned. |
| Fault | Red alert light and a precise error statement | A known failure requires attention. |

Do not depend on color alone; pair state with words, icons, or line patterns.

## The three time periods

The course remains one world. The base ink, paper, engineering rules, and typography do not change. Each act shifts its lighting, materials, landscapes, and system metaphor.

| Part | Story setting | Dominant palette | Visual materials | System metaphor | Motion |
|---|---|---|---|---|---|
| I — **Out of Time** | The professor's 1985 workshop | Electric blue, midnight, paper | Blueprints, notebooks, CRT grids, coils, labeled drawers | Give the machine a voice and a memory | Slow pulses, archive drawers opening, routes finding a signal |
| II — **The Future Workshop** | A busy 2015 workshop | Brass gold, blue, deep charcoal | Transit maps, service bays, route lines, component tags, controlled terminals | Connect operations into workflows | Deliberate route assembly, tool handoffs, paused approval gates |
| III — **The Last Departure** | A resource-poor frontier workshop | Signal red, ember gold, worn charcoal | Weathered instruments, low-power gauges, patched cables, field notes | Make the system trustworthy under pressure | Intermittent signal, restrained fault flicker, recovery routes reconnecting |

### Part I: Out of Time

Part I feels intimate and investigative. Blue dominates, with gold used for notebooks and the professor's guidance. The space is quiet enough to learn from first principles. Use visual motifs of fragments becoming a coherent route: scattered notes, highlighted passages, a search beam, and a growing archive.

The Flux Capacitor begins incomplete. Its branches are dim; every lesson restores a component. The closing **First Jump** should feel like the first time the machine has earned a burst of speed and light.

### Part II: The Future Workshop

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

Use American English spelling throughout authored prose and UI labels, including organization, initialization, serialization, behavior and color. Preserve exact quoted source code/comments, technical identifiers and asset paths. The renderer applies this policy to readable HTML, metadata and glossary definitions.

Write as a practical guide within a cinematic world. The professor is warm, exacting, and concise. The learner is capable; the story gives them a reason to practice, never a reason to feel inadequate.

The author is the professor and speaks as **I**; the visitor is **you**; shared work is **we**. Keep original course adventures distinguishable from film events. Recaps describe earlier chapters rather than claiming that a direct visitor has completed them.

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
- Never communicate completion, risk, or route availability by color alone.
- Keep body content selectable, zoomable to 200%, and readable without horizontal scrolling.
- Support `prefers-reduced-motion` and do not auto-play audio.
- Dialogs trap focus, return focus to their trigger on close, and provide an explicit close control.
- Keep labels concise and specific: `Open all 24 lessons`, not `Click here`.

## Implemented temporal design layer

The shared layer in `temporal-design.css` follows the existing theme styles. Its scoped tokens give light and dark reading surfaces equivalent contrast. Destinations are 1985, 2015 and 1885. These are story settings, not dates in AI history.

- `assets/workshop-analogue.svg`, `workshop-future.svg`, and `workshop-frontier.svg` show the same original clocktower square and mobile workshop. Architecture remains recognizable as service bays, transit routes, and railways change around it. Keep setting artwork on maps and the home atlas.
- Every lesson has a three-part route and compact time instrument outside its teaching article. Keep lesson prose, source snippets, copy controls, and glossary unchanged by visual updates.
- Reading prose uses DM Sans at 22px on desktop and 20px on mobile, with 1.8 line height. Lists, table cells, and snippet explanations share this scale. Keep display headings and instrument labels at their existing sizes; do not shrink explanations back to the old 16px panel default.
- `lesson-topics.css` separates direct teaching-article topics with numbered header panels, an era-accent edge and generous spacing. Direct subtopic headings use smaller numbered markers and a divider; numbering restarts within each topic. Keep prose in open space and preserve heading wording/typefaces, anchors and exact snippets. Scope these treatments to `#lesson` so story scenes and nested playground headings retain their own styles.
- Map panels use a silver instrument housing, a dark viewfinder and labeled subsystem lamps. `PENDING` and `COMPLETE` describe saved lesson completion; a filled lamp is not an assessment result. Repair-count panels remain removed; the user-requested single completion track belongs only in the bottom journey menu.
- The shared progress record covers 20 published lessons, preserves original Part I records, supports undo, and uses browser storage. Record completion when the end of teaching is visible in an active tab; do not immediately reapply it after manual undo on that visit. Four planned lessons remain labeled in the syllabus and are excluded from the progress totals. Do not add the numbered lesson-route strip; it was removed by user request. Never lock published lessons based on completion.
- `scripts/temporal_design.py` supplies repeatable static components; the lesson renderer calls it on every build. Do not hand-insert instruments into the teaching Markdown.
- `lesson-stories.json` holds three sample scenes for Lessons 1, 9 and 17, rendered by `scripts/lesson_stories.py` outside `#lesson`. Use `lesson-story.css` for the wider illustrated setting and readable narrative column. Native details/summary provides keyboard collapse/replay without JavaScript. Begin lesson and Skip story buttons were removed by user request; reading follows the opening naturally.
- Lesson 1's old optional narrative was migrated into the opening layer; retain its technical explanation in the teaching article. The other 17 openings, audio and departure animations remain deferred.
- Lesson 4 uses a draft marker (`<!-- interactive: tokenizer-playground -->`) for the live token simulation. `scripts/lesson_tokenizer.py` supplies readable static defaults; `lesson-tokenizer.js` updates safe text chips and counts locally. Keep the illustrative splitter and example $5/1M rate explicit. Scoped styles preserve 22px desktop / 20px mobile input text and both themes; this does not call a model tokenizer or API.

## Build checklist

Before a new page or component ships, check:

- Does it show the current story problem and the system capability being built?
- Does it use the base tokens and the correct part accent instead of a new visual language?
- Does every interactive effect explain something or provide feedback?
- Is the important information still available without motion, color, hover, or large-screen layout?
- Does the page leave the learner with a visible repair, insight, or route forward?
