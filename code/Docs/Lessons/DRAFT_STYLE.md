# Lesson Drafting Style

**Reference:** [Part1/lesson1_final.md](Part1/lesson1_final.md). Treat that edited lesson as the primary example whenever you prepare a future lesson draft.

**Code presentation:** Always follow [CODE_SNIPPET_RULES.md](CODE_SNIPPET_RULES.md): small sequential snippets with a clear explanation directly below each one, using the exact notebook source and comments.

## Voice

- Use American English spelling consistently: organization, initialization, serialization, behavior and color. Preserve exact source code, comments, identifiers and filenames.
- Write as a developer speaking directly to another developer: warm, practical, and curious.
- Start with why the topic matters in a learner's working life. A short personal hook or question is welcome when it serves the lesson.
- Invite the learner to build and experiment. Use plain, encouraging language such as “Just follow along” and “let’s get our feet wet” where it fits naturally.
- Keep the speaker visible when useful: use “we”, “you”, and “developers like you and me”. Do not turn the lesson into impersonal textbook prose.
- Be hopeful without making promises. Acknowledge uncertainty and limits plainly.

## Teaching approach

- Explain the idea first, then connect it to what the learner will build in the repository.
- Prefer familiar words and concrete examples over dense terminology. Define a technical term immediately after introducing it.
- Strip hype from complex ideas, but keep the explanation accurate. State both a capability and its limit.
- Show how an idea affects an application developer: what the model does, and what the surrounding software must do.
- Separate an optional story from the lesson explanation and code. A learner must be able to skip the story without missing the teaching.

## Suggested lesson shape

Adapt this structure to the lesson; do not add sections that do not help.

1. A brief note or hook that connects the topic to the learner.
2. Lesson purpose and clear learner outcomes.
3. Optional story, explicitly marked as optional.
4. Plain-language explanation, supported by a table, timeline, diagram, or small example when useful.
5. A practical “how do I start?” or “why this matters” section tied to the supplied code or notebook.
6. A concise check-for-understanding section and a clear hand-off to the next lesson.

## Editing rules

- Preserve the learner-facing rhythm: short paragraphs, direct questions, and intentional emphasis.
- Introduce a concept before using it to explain another concept. Start a distinct concept introduction in its own paragraph and bold its opening term or short phrase, for example `**LangGraph** helps us...`. Keep related elaboration together; do not bold every paragraph or split every sentence. This reading emphasis is separate from first-use glossary highlights and must never change exact code/comments.
- Polish grammar and clarity without removing the author's personality or replacing their point of view.
- Use Markdown headings, lists, tables, and code blocks only when they make the teaching easier to scan.
- Keep claims proportionate. Prefer “can”, “may”, and “often” where behavior depends on a provider, model, or application design.
- Reference the exact associated notebook or code file when the lesson discusses it.
- Show each constructed graph beside its construction code, including branch labels, explicit joins and return loops. The shared graph component derives topology from displayed Python snippets; add its concise title/caption to `site/lesson-graphs.json`. Label framework-managed agent flows as conceptual, and keep checkpointer storage separate from execution nodes. Preserve all source code/comments when adding visuals.
- Lesson 9's first graph is an exception: preview it directly below the What we are building explanation, before the code walkthrough. Keep deriving its topology from the construction snippets.
- Lesson 10 previews each of its four independent graphs directly below that topic's What we are building explanation. Use a `data-graph-preview` marker naming the builder; keep deriving topology from the construction snippets.
- Lessons 11–16 begin with What we are building; omit A note from me. Preview the target graph before the code. Explain the practical project and the idea behind it, connecting each new capability to the state, nodes, and edges already learned. Use the `data-graph-preview` marker and derive the diagram from the construction snippets.
