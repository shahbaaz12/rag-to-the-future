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

## Original design acceptance criteria

- [x] Home and all three maps show the same location in different eras, with era-specific materials.
- [x] Every published lesson has a compact time instrument and route navigation outside the teaching article.
- [x] All published lessons can be marked complete; map and lesson instruments use the same saved record, preserving Part I progress.
- [x] Planned lessons remain clearly labelled and do not have broken links or completion controls.
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

Preserve the current story destinations (1985, 2045, unspecified frontier) until the story pass. Create original vector scenes rather than film stills. Reuse the town-square clocktower across analogue, future, and frontier workshops. Use a silver instrument housing, restrained luminous readouts, blueprint lines, and brass/rail motifs. Keep large illustrative surfaces on maps and the homepage; lessons receive only compact instruments. New UI labels describe navigation and recorded completion, not invented story events. Completion is learner-reported, not an assessment score.

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
