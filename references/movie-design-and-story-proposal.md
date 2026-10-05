# Movie atmosphere and lesson story proposal

Status: recommendations for review; no website or lesson changes applied.

Checkpoint before this review: `faf265a` — Checkpoint lesson updates and Part III RAG course work.

## What the site already does well

The home page has the strongest movie connection: the title artwork, red/green/amber time circuits, Flux Capacitor, twin fire trails, and 88 MPH instrument establish the premise immediately. Part I adds a workshop mission, eight repair cards, completion checkboxes, and story moments.

The rendered home, Part I, Part II, Part III, and Lesson 17 pages were reviewed in the browser's saved light theme. Lesson headings, course metadata, story text, shared styles, progress code, and the lesson renderer were also inspected in the repository.

Part II and Part III currently share a technical course-card layout with little visible setting. Their optional story interludes sit after the course content. Most lesson openings go directly from a large title to teaching prose; Lesson 1 has an optional story inside the article. Consequently the adventure becomes less visible as the course progresses.

## Design additions, in priority order

| Priority | Addition | Placement and purpose |
|---|---|---|
| 1 | A compact time-circuit strip | Reuse the home page's instrument language at the beginning of every lesson: era, scene number, current location, and machine state. Keep a separate field for the course part rather than overloading the clock display. |
| 1 | One location shown across three eras | Add an original illustrated town square with a clocktower, workshop, road, and railway. Reuse the composition: analogue workshop in Part I, future transit district in Part II, unfinished frontier settlement in Part III. Recognisable geography makes the jumps feel connected. |
| 1 | A visibly repaired companion machine | Reuse one original time-machine illustration. Show a restored voice module after Part I, connected control routes after Part II, and a working archive reader during Part III. Keep this small in lessons and prominent on the part maps. |
| 1 | Separate opening scene | A short scene card above the teaching article, with a recap, immediate problem, and changed machine state. This is the main story-progress device. |
| 2 | A branching journey map | Make each lesson a stop along a visible route. Use branches for Part II, archive destinations for Part III, and explicit available/completed/planned labels. Allow direct access to every published lesson. |
| 2 | Era-specific physical artefacts | Part I: graph paper, taped labels, CRT console, workshop notes. Part II: layered glass instruments, transit maps, service terminals. Part III: folded letters, brass gauges, ink diagrams, railway tickets, weathered wood and metal. Apply these to narrative areas and maps. |
| 2 | A photograph or mission document that evolves | At act milestones, update an original workshop photograph or mission dossier to show a repaired component or clearer route. Use it as a visible consequence of progress; avoid a constant fading animation. |
| 3 | A jump transition at act boundaries | A brief pair of fire trails, a changed time readout, then the next location. Trigger only when the learner chooses the next act. Provide a static equivalent for reduced motion. |
| 3 | Optional instrument sounds | An explicit sound toggle can enable a short switch click or departure chime. Keep audio off by default. |

Start with the scene card, time strip, and three-era location. Those provide more continuity than adding more glow to every heading.

### Visual polish before adding detail

- The home page's large logo overlaps the title at the reviewed viewport. Give those elements independent space.
- Part I has a large empty region above the hero content at the reviewed viewport. An establishing illustration could give that space a purpose; otherwise reduce it.
- Use cinematic contrast in the narrative areas while preserving comfortable light and dark reading themes. The lesson text and code need calm surfaces.
- Reserve poster-style display lettering for act names and scene titles. Reduce its prominence for long technical lesson titles.
- Align the existing design-language document with the live site: it currently describes a different typography system and an earlier course progression.

## How closely to follow the movies

The films' key periods are 1955/1985 in the first adventure, 2015 and altered timelines in the second, and 1885 in the third. Sources: [official first-film synopsis](https://www.backtothefuture.com/movies/backtothefuture1), [official Back to the Future Day description](https://www.backtothefuture.com/home), and [official Part III production notes](https://www.backtothefuture.com/movies/production-notes-1990).

The current site uses 1985, 2045, and an unspecified frontier. For closer film alignment, the proposed course settings are **1985 workshop → 2015 future district → 1885 frontier railway workshop**. A 1955 notebook or photograph could supply an occasional visual clue. These would be course settings inspired by the films, not a claim to reproduce the films' plot.

Retaining 2045 is also coherent if the course intentionally follows the learner's children. In that case, present it clearly as an original continuation and preserve that date throughout the story. Do not silently mix the two timelines.

Use the professor and learner as the recurring pair, with original scene writing and illustrations. The stronger film connection comes from location, physical instruments, changing timelines, and consequences.

## A story opening that stays separate from teaching

Place the narrative **after the lesson title and before `<article id="lesson">`**. Keep the technical title, explanation, examples, and snippets intact.

Recommended order:

1. Lesson title and technical description.
2. Compact instrument strip: part, setting, and scene number.
3. An explicitly labelled **Story progress · optional** card.
4. One sentence labelled **Previously**, limited to events before this scene.
5. A 60–100 word scene, usually two short paragraphs and at most one line of dialogue.
6. A textual machine-state change or mission log entry.
7. **Begin lesson** and **Skip story** links, both reaching the teaching article.
8. Existing lesson article, unmodified.

The opening should acknowledge what changed in the previous scene and introduce the current obstacle. Show the current repair as pending; do not announce that the learner has completed the lesson merely because they opened the page. The next opening supplies the next story development. For direct visitors, the recap gives enough context without requiring earlier scenes.

Offer a remembered **Hide story openings** preference and a replay control. A collapsed card can still show the location and scene title. Story information must never be required for running the notebooks or understanding the teaching.

### Example opening for Lesson 17

**PART III · FRONTIER WORKSHOP · SCENE 17**

**Story progress · optional — The sealed archive**

**Previously:** The workshop restored its control routes. The last dangerous command now waits for a human decision.

The professor spreads a bundle of stained journals across the bench. Outside, a locomotive stands motionless beside the unfinished station. The console can follow a plan, but the repair instructions were written decades before its records began.

You ask how to reconnect the damaged power line. It offers a plausible answer. The professor points to a different instruction in the journal.

“We brought the tools,” he says. “Now we need the right page.”

**Mission log:** Control routes ready · Archive reader pending.

**Begin lesson ↓** · **Skip story ↓**

Then the current “A note from me” section begins exactly as it does today. The scene introduces an obstacle; the lesson continues to use its actual course-note example.

### Example opening for Lesson 18

**Story progress · optional — The missing reference**

**Previously:** The archive reader found a relevant page. The console can now consult the notes supplied to it.

The professor asks about a repair described in an old journal. A page appears on the console. Then he asks, “And what happened after that?”

The machine searches again, this time without the question that gave “that” its meaning. An unrelated page slides into view. You leave the first entry on the bench and write the follow-up beside it. The next search needs the conversation, not just the latest sentence.

**Mission log:** Archive reader ready · Follow-up reference unresolved.

## Story beats for the 20 published lessons

These are opening-scene premises, not replacements for the lessons' everyday examples. Each opening can acknowledge the previous scene's repair before introducing its own pending task.

| Lesson | Current teaching topic | Proposed story beat |
|---|---|---|
| 1 | LLM foundations | The silent console speaks, then confidently names a destination that does not exist. Establish the professor, learner, and damaged machine. |
| 2 | Setup and first call | A signal can be reached, but the workshop must first connect its equipment correctly. The first deliberate request produces a reply. |
| 3 | LangChain and model interfaces | Two model connections use different controls. The professor builds one panel for changing between them. |
| 4 | Responses and prompts | A reply arrives with instrument readings. You inspect what was sent, what returned, and how the instructions shaped it. |
| 5 | Messages, streaming, batching, structured output | Fragments arrive from several workshop requests. Roles and structured fields help keep the console's records usable. |
| 6 | Memory | The console forgets the departure instruction when the next question arrives. You carry the right conversation record forward. |
| 7 | Tools and tool loops | The console proposes checking a component. The workshop must recognise and execute the permitted action. |
| 8 | Agents | The console selects among approved tools. The first jump is possible; retrieval and source verification are still pending. |
| 9 | First graph | After arrival, the service bay needs several steps connected in a dependable order. You begin with two simple stations. |
| 10 | Edges and branching | One repair route is closed. The workshop checks alternatives, branches on availability, and limits repeated attempts. |
| 11 | LLM inside a graph | A message must be drafted at the correct point in a larger repair procedure. The console becomes one station in the route. |
| 12 | Tool execution in a graph | A decision needs a real workshop record. The console requests a lookup; the application supplies the result. |
| 13 | Repeated tool use | A route listing supplies identifiers, not enough detail to choose. A second lookup is needed before the console can answer. |
| 14 | Graph memory | Two crew members use the console. Their separate records must remain distinct between visits. |
| 15 | Streaming | The crew waits for an instruction to finish. The display distinguishes completed workflow steps from text still arriving. |
| 16 | Human approval | A consequential change reaches the final switch. The workflow pauses, saves its state, and waits for a person. Close the second act. |
| 17 | First RAG | The frontier repair depends on journals outside the console's knowledge. Find the relevant page before asking for an answer. |
| 18 | Conversational RAG | A follow-up says “that” without naming its subject. Resolve the reference before searching again. |
| 19 | Hybrid search | Two similar replacement parts have different identifiers. Search must respect exact labels as well as related meaning. |
| 20 | Hierarchical RAG | The crew sometimes needs a single component specification and sometimes the whole assembly. Choose the appropriate information level. |

Leave scenes 21–24 reserved until their lessons are defined. Any future final departure should depend on the capabilities actually taught there.

## Continuity fixes

Part I currently promises an Archive Assistant that can search and show evidence, although retrieval begins in Lesson 17. Reframe its end state as a **Workshop Assistant** with conversation and approved-tool capabilities. Part II connects those capabilities into workflows. Part III adds the archive reader and progressively improves retrieval.

The Part I instrument shows 33% power even with zero repairs complete, while its subsystem labels remain static. Label an act-position indicator as act position, or make machine power reflect actual recorded repairs. Opening a scene is not proof of learning or completion.

Retain the existing distinction between 20 available lessons and four planned lessons wherever a route or progress denominator appears.

## Implementation approach after choosing the direction

- Add a separate `lesson-stories.json` containing lesson number, scene title, era, location, recap, scene paragraphs, and machine-state labels. Keep it independent of lesson Markdown and notebook cells.
- Add shared `lesson-story.css` and a small `lesson-story.js` for collapse/replay preferences. Render the scene text into HTML so it remains available without JavaScript.
- Insert the story section through `scripts/render_lesson_snippets.py`, immediately before the teaching article. Replace an existing generated story section on every render so reruns cannot duplicate it.
- Lesson 1's existing optional story needs a deliberate migration to the opening layer; retain its technical teaching and avoid two copies of the same scene.
- Extend the Part I completion model to all published lessons, preserve existing progress, and share its state with map instruments. Keep story chapter position separate from learner completion.
- Update part-map setting illustrations and instrument labels once the film-era or original-2045 direction is chosen.
- Verify desktop/mobile layouts, both themes, keyboard access, skip targets, direct lesson visits, reduced motion, unavailable storage, renderer reruns, and unchanged snippet/source matching.

Suggested first implementation slice: one scene component previewed on Lessons 1, 9, and 17, showing the three settings. Then expand the same component across the course.
