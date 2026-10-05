# Ticket: Carry the time-machine design through the course

Goal: Make the home, three course maps, and 20 published lessons feel like one evolving workshop, while keeping learning content readable.

Scope: original SVG setting illustrations; era instruments; journey route navigation; saved lesson completion; layout polish; renderer integration; updated design guidance.

Out: new story scenes, lesson prose/code changes, timeline date changes, audio, deployment, and unpublished lessons.

Constraints: follow `rule.md` and `references/design-language.md`; preserve exact teaching snippets and comments; retain light/dark themes, existing completion records, direct lesson access, keyboard navigation, and reduced motion. Keep 20 published lessons distinct from 4 planned lessons.

## Follow-up ticket: Remove numbered lesson routes

Goal and scope: Remove the 01, 02, … lesson-route strip from all pages and its generator, styles, and behavior. Retain course cards, three-era navigation, and completion records.

Assigned: FE — remove the component and unused CSS/JS; Ops — update the generator and regenerate pages; QA — verify absence across all pages and preservation of teaching content. BE and Design — n/a; no API or replacement design needed.

Acceptance: no numbered lesson-route strips in rendered pages or subsequent builds; existing lesson content and progress controls preserved.

Completed: removed the component, generator, CSS and update behavior; regenerated all 24 pages. Checked every page and repeated map generation. Browser verification shows zero lesson-route strips and the existing 1/8 completion record preserved.

## Follow-up ticket: Larger lesson reading text

Goal: Make lesson prose and code explanations comfortable to read. Scope: shared reading styles only; retain DM Sans and existing title/subtitle treatments, content, code and comments.

Assigned: Design — choose 22px desktop / 20px mobile prose with 1.8 line height; FE — apply consistent reading and snippet-explanation styles; Ops — refresh versioned assets through the existing generator; QA — inspect Lesson 1 and a code lesson at desktop/mobile widths and confirm unchanged content. BE — n/a; no API work.

Acceptance: larger prose and explanations across all lessons, unchanged heading styles, no page-wide overflow, and identical lesson content. Status: complete; all applicable roles finished sequentially.

Validation: Lesson 1 prose and Lesson 2 snippet explanations render at 22px / 39.6px line height on desktop and 20px / 36px on mobile. Heading styles remain identical. Both widths have no page-wide overflow. All 20 teaching articles match the checkpoint; the existing validator passes 286 exact-source snippets and 128 glossary terms. Shared asset versions refreshed across all 24 pages. Story and lesson content changes remain out of scope.

## Ticket: Professor-led story samples and remove repair counters

Goal: Make the author the professor guiding the visitor, with optional story openings independent of teaching.

Scope: homepage and part narrative copy; shared destinations 1985 / 2015 / 1885; three illustrated openings for Lessons 1, 9 and 17; migrate Lesson 1's old narrative into the opening layer; remove all repair-count panels and bars. Keep lesson-completion checkboxes and stored completion records. Out: scenes for the other lessons, new technical examples, sidebar, audio and departure animations.

Acceptance criteria:
- [x] First-person professor voice and consistent destinations across home, maps and lessons.
- [x] Exactly one optional, skippable opening outside each sample lesson's teaching article; no duplicate Lesson 1 story.
- [x] No repair counters, meters or “Repair recorded” labels remain on live pages or regeneration.
- [x] Teaching prose, source snippets, comments, glossary and lesson navigation preserved, apart from migration of the old optional narrative.
- [x] Responsive layouts, both themes, keyboard navigation, skip links, no-JavaScript story availability, and repeated regeneration pass QA.

Assigned, sequential:
- Design: write three short scenes and direct invitations; use wider illustrated openings with calm readable prose.
- FE: static native details/summary scenes, skip links and meter removal; retain existing lesson checkboxes.
- Ops: JSON story source and repeatable renderer integration; refresh asset versions.
- QA: validate content preservation, asset/link integrity, repeat builds and browser layouts/interactions.
- BE: n/a — static site, no API changes.

Status: complete. Design, FE, Ops and QA finished sequentially.

Validation: all 20 teaching articles match the checkpoint after excluding the migrated Lesson 1 narrative; the validator passes 286 snippets and 128 glossary terms. All 24 pages have valid fragment links, consistent destinations and no repair counters, meters or numbered lesson-route strips. Repeated static generation is stable. Six completion tests pass. Browser review confirms three scenes, 22px desktop / 20px mobile narrative text, no page-wide overflow, light/dark readability, keyboard collapse/replay, skip navigation and homepage destination switching. The existing Lesson 1 completion record remains checked. Story markup and native details/summary need no JavaScript. Temporary viewport and theme changes were restored; a frontier scene screenshot was saved outside the repository.

Shipped: professor-led homepage and act introductions; 1985 / 2015 / 1885 destinations; three optional illustrated samples and separate map field notes; repair-count UI removed. Other lesson openings, departure animations, audio and sidebar remain out of scope. No deployment or new commit requested for this pass.

## Original design acceptance criteria


- [x] Home and all three maps show the same location in different eras, with era-specific materials.
- [x] Every published lesson has a compact time instrument and route navigation outside the teaching article.
- [x] All published lessons can be marked complete; map and lesson instruments use the same saved record, preserving Part I progress.
- [x] Planned lessons remain clearly labeled and do not have broken links or completion controls.
- [x] Homepage logo/title separation and Part I hero spacing are improved.
- [x] Light/dark, desktop/mobile, keyboard, reduced-motion, and no-storage behavior pass QA.
- [x] Lesson regeneration retains design additions without duplicate components or changed teaching/source snippets.
- [x] No new story scenes or timeline rewrites are introduced.

## Assigned roles, completed sequentially

- [x] Design: create three original SVG workshop settings and shared instruments; update the guide to describe the live typography and design layer.
- [x] FE: add shared design styles, course routes, instrument panels, and completion state across all pages.
- [x] Ops: integrate the static design components with the existing lesson renderer. Deployment is out of scope.
- [x] QA: check content preservation, completion migration and synchronization, regeneration, existing lesson validators, and browser layouts/interactions.
- BE: n/a — static website; no server or API required.

## Design decisions

Preserve the current story destinations (1985, 2045, unspecified frontier) until the story pass. Create original vector scenes rather than film stills. Reuse the town-square clocktower across analog, future, and frontier workshops. Use a silver instrument housing, restrained luminous readouts, blueprint lines, and brass/rail motifs. Keep large illustrative surfaces on maps and the homepage; lessons receive only compact instruments. New UI labels describe navigation and recorded completion, not invented story events. Completion is learner-reported, not an assessment score.

## Validation and closure

Shipped across the home page, three maps, and 20 published lessons. Acceptance criteria and assigned roles are complete.

Validation:
- All 20 teaching articles match the checkpoint, including after repeated component regeneration.
- Existing validator passes 286 exact-source snippets and 128 glossary terms.
- All eight Part II and four Part III notebooks pass offline in the project's existing virtual environment; no provider calls were made.
- Six completion tests cover legacy migration, invalid records, undo, storage failure, cross-tab events, and history restoration.
- Browser review covers light/dark themes, all maps and representative lessons at narrow widths, homepage atlas switching, syllabus controls, keyboard repair expansion, persisted completion and undo, and no page-wide overflow.
- Reduced-motion rules disable transitions, animation, and smooth scrolling. Link/asset integrity, unique IDs, separated checkbox/link controls, and Git whitespace checks pass.
- Content-hashed styles/scripts prevent stale design assets from being reused after a rebuild.

Explicitly deferred: story openings, date rewrites, milestone departure animations, optional sound, and deployment. Existing story content remains intact. The preview's test completion was undone and the original light-theme preference was restored.

## Ticket: Consistent course cards and persistent reading navigation

Goal: Make navigation and completion visible across all three parts, with an accessible index for reading long lessons.

Scope: remove the two story action buttons; convert Part I to the shared course-card grid; make homepage part cards full links; move the three-era menu to a fixed bottom dock with saved-completion tracks and original DeLorean-style car, flying car and time-train markers; automatically record completion at the end of teaching; floating left index of current-lesson sections. Preserve technical text, snippets, comments, glossary, existing records, undo and direct access. Out: new lesson/story content, planned lessons and deployment.

Acceptance criteria:
- [x] Story Begin lesson / Skip story buttons absent, including after regeneration.
- [x] All three maps share lesson-card presentation, and all homepage part cards work as full keyboard-accessible links.
- [x] One bottom era dock per page; each part has a moving vehicle and accurate published-lesson progress.
- [x] Completion is saved only when the end of teaching becomes visible; records, manual undo, storage fallback and cross-tab updates remain supported.
- [x] Floating section index links, current-section indication and responsive collapse work without covering reading material.
- [x] Mobile, both themes, keyboard navigation, reduced motion, source validation and repeated generation pass QA.

Assigned sequentially: Design — matching cards, three original vector markers, readable dock and index; FE — navigation, progress and end-of-lesson observation; Ops — renderer and asset-version integration; QA — meaningful completion tests, rendering integrity and responsive browser checks. BE — n/a, static website with local browser storage.

Status: complete. Design, FE, Ops and QA finished sequentially. The index lists sections within the current lesson.

Validation: all 24 pages have one bottom dock, three loaded vehicle assets, valid IDs/fragments and intact local assets. All maps share the card grid; homepage part links have no nested anchors. All 20 teaching articles are preserved through repeated, byte-stable component generation. The source validator passes 285 snippets and 128 glossary terms. Eleven tests cover completion migration, persistence, undo, blocked storage, cross-tab/history refresh, end visibility, background-tab deferral and the dock clearance fallback. Browser checks confirm automatic completion and undo, moving progress, whole-card links, keyboard era navigation, desktop index clearance, mobile collapse and section links, three visible mobile destinations, light/dark themes and no page-wide overflow. Reduced-motion styles disable animation, transitions and smooth scrolling. Test completion was undone, the original dark theme restored, and temporary viewport settings reset. Preview screenshots were saved outside the repository.

Shipped: removed story action buttons; consistent Part I cards; full homepage part links; persistent bottom journey tracks with car, flying car and train; automatic end-of-lesson completion with manual undo; floating section index. New lesson/story content, planned lessons and deployment remain out of scope.


## Ticket: One flowing journey track

Goal: Place the era menu at the page bottom in normal document flow, with one continuous progress track and one changing vehicle.

Scope: shared menu markup, styling and progress behavior; remove obsolete dock clearances; retain completion records, undo, automatic completion and the floating section index. No teaching/story changes or deployment.

Acceptance criteria:
- [x] One static bottom menu, one continuous track and exactly one vehicle per page, retained by regeneration.
- [x] Each workshop occupies a third of the track. Progress combines each part’s completion fraction; the marker changes at the one-third and two-thirds boundaries.
- [x] Existing completion, undo, storage and section navigation remain intact; no unnecessary sticky-menu clearance remains.
- [x] Boundary tests, stable generation, content preservation and desktop/mobile/theme browser checks pass.

Assigned sequentially: Design — one track aligned to three eras; FE — vehicle changes and normal flow, remove dock offsets; Ops — regenerate and update guidance; QA — boundary/progress tests and responsive checks. BE — n/a, browser storage only.

Status: complete. Design, FE, Ops and QA finished sequentially.

Validation: all 24 pages contain exactly one normal-flow era menu, one continuous progress track and one image marker. Repeated generation is stable and all 20 teaching articles are unchanged by this pass. Sixteen tests pass, including both vehicle boundaries, the shorter frontier segment, full completion and undo. The source validator passes 285 snippets and 128 glossary terms; Git whitespace checks pass. Browser checks confirm the shared track, actual car-to-flying-car change, saved-progress restoration, desktop/mobile width, light/dark themes and mobile reading controls clear of the menu. Temporary viewport/theme changes were restored, the user’s lesson preview refreshed, and a screenshot saved outside the repository.

Shipped: the menu scrolls in normal page flow; a single progress track spans all three workshop links; one marker changes from car to flying car to train according to its position. Obsolete dock spacing and completion-observer clearances were removed. Teaching/story content and deployment remain outside this pass.


## Ticket: Lesson 4 tokenizer playground

Goal: Replace the static “Picture the token pieces” supplement with the linked live tokenizer simulation.

Scope: that lesson section, draft marker, reusable static component, scoped styles and local interaction script; live chips, token/character counts and illustrative cost at $5/1M tokens. Keep the reference’s default sentence and 12 / 44 / $0.000060 values. Preserve other teaching code/comments, glossary, navigation and saved progress. No real tokenizer/provider integration or deployment.

Acceptance criteria:
- [x] Static snippet replaced by the live playground in the page and draft-backed renderer.
- [x] Default state matches the reference; edits update all results safely, including empty input and punctuation.
- [x] Simulation and rate clearly labeled; keyboard, mobile, light/dark and no-JavaScript fallback remain readable.
- [x] Exact-source validation, meaningful splitter tests, content preservation and repeated rendering pass.

Assigned sequentially: Design — match course readability and tokens; FE — local, safe input/rendering; Ops — draft marker and renderer/assets; QA — values, edge cases and responsive interaction. BE — n/a, no API or server state.

Status: complete. Design, FE, Ops and QA finished sequentially.

Validation: default browser state matches 12 tokens / 44 characters / $0.000060. Input edits update pieces/counts/cost; empty input clears the results; markup stays text. Four tests cover defaults, empty/whitespace, punctuation, reconstructing long input and Unicode. All remaining Lesson 4 source snippets and glossary records are preserved; the other 19 pages are untouched by rendering. Repeated Lesson 4 rendering is stable and creates one playground. Source validation passes 284 snippets and 128 glossary terms. Browser checks confirm 22px desktop / 20px mobile input text, mobile stat stacking, no page overflow, keyboard focus, and light/dark readability. Static default chips/counts plus a noscript explanation remain available without JavaScript. Original theme, viewport and completion records were restored. A preview screenshot was saved outside the repository.

Shipped: the static token-pieces supplement was replaced by a local live playground, backed by the draft marker and renderer. Other teaching source/comments, glossary and navigation remain intact. Real tokenizer/provider integration and deployment remain outside this pass.


## Ticket: Consistent American English spelling

Goal: Use American English spelling throughout site prose and its content sources.

Scope: home, maps, 20 lessons, metadata, glossary definitions, story copy, draft prose and authored UI/generator labels. Preserve executable examples, exact source comments, filenames, URLs, identifiers and quoted source code. No design changes or deployment.

Acceptance criteria:
- [x] British spelling variants in editable site prose are replaced with American equivalents.
- [x] Drafts, content data and generated components retain the spelling after rebuilding.
- [x] Exact teaching snippets/comments, identifiers, links, glossary anchors and layout are preserved.
- [x] Focused spelling audit, source validation and browser review pass.

Assigned sequentially: Design — spelling map and wording consistency; FE — page prose/metadata and visible UI labels; Ops — content-source/generator parity; QA — prose audit and exact-source preservation. BE — n/a, no API or state changes.

Status: complete. Design, FE, Ops and QA finished sequentially.

Validation: audited all 24 pages and updated 24 authored content files, glossary definitions and SVG descriptions. The rendering policy standardizes readable text, metadata and embedded glossary definitions while excluding code, exact source comments, technical term names and paths. Original teaching code/comments, IDs and links match the pre-change snapshot. Repeated generation is stable. Source validation passes 284 snippets and 128 glossary terms. Focused conversion checks preserve unrelated words such as conversation/exercise, inline code and fenced comments. Browser review confirms serialization/serializes in Lesson 4 and American spelling in dynamic homepage labels and accessible image descriptions. A proof screenshot was saved outside the repository.

Shipped: consistent American English prose across home, maps, lessons and authored sources, with an explicit drafting policy and renderer enforcement. Executable source, exact comments, filenames and identifiers remain intact. No deployment requested.


## Ticket: Clear lesson topic boundaries

Goal: Make major topics and subtopics visibly distinct throughout the lessons.

Scope: a shared reading stylesheet and renderer asset integration. Major topics receive numbered header panels, part-accent borders and clearer spacing; direct subtopic headings receive smaller number markers and dividers. Preserve heading wording/typefaces, all teaching content, exact code/comments, glossary, section anchors and progress. No story/map changes or deployment.

Acceptance criteria:
- [x] All 20 lessons have visible major topic boundaries and subordinate subtopic markers.
- [x] Existing text, code/comments, IDs and links are unchanged; story/playground headings keep their own treatments.
- [x] Desktop/mobile and both themes remain readable with no page-wide overflow.
- [x] Regeneration retains the shared styles; source validation and browser review pass.

Assigned sequentially: Design — numbered chapter panels and restrained subtopic markers; FE — scoped styles using existing themes; Ops — shared versioned asset inclusion; QA — responsive/theme review, exact content preservation and generation checks. BE — n/a, no data/API changes.

Status: complete. Design, FE, Ops and QA finished sequentially. Baseline committed as 9b19612 before implementation.

Validation: all 20 teaching articles match the pre-change snapshot exactly, including code/comments, links and anchors. Every lesson includes one versioned topic stylesheet, and repeated generation is stable. Source validation passes 284 snippets and 128 glossary terms. Browser review confirms numbered major panels, subordinate markers, unchanged display typefaces and an unaffected nested tokenizer title. Desktop and narrow mobile layouts have no page-wide overflow; both light and dark themes retain readable topic contrast. Original theme, viewport and completion records were restored, and a preview screenshot was saved outside the repository.

Shipped: consistent topic panels, smaller subtopic dividers and clearer spacing across all published lessons, integrated into repeatable generation. No teaching content, story, map or progress changes; no deployment requested.
