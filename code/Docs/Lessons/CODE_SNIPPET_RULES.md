# Code snippets and explanations

Apply these rules whenever drafting or updating a lesson or lesson page. Use [DRAFT_STYLE.md](DRAFT_STYLE.md) for the author's voice. Lessons 1–8 use this layout; Lesson 6 was the initial review example.

## One idea per snippet

- Split code into small, sequential snippets, each teaching one action: setup, first request, storing a reply, or a follow-up.
- Aim for 3–12 lines; allow a longer snippet when splitting would obscure a complete function or data structure.
- Give each snippet a descriptive heading. Explain its purpose briefly before the code when needed.
- Make execution order clear. Later snippets may reuse objects defined earlier; say so rather than repeating setup everywhere.

## Use the actual source

- Copy code and comments exactly from the associated notebook or source file. Preserve indentation, variable names, prompts, and order.
- Never change source code solely to manufacture an annotation.
- Cite the notebook and relevant section. Keep the complete runnable example in the notebook.
- If the source and lesson disagree, resolve the mismatch explicitly rather than displaying a different implementation.

## Explain below the code

- Display syntax-coloured code at full width, with line numbers and a copy button.
- Place a visible **What happens here** explanation directly below each snippet.
- Start with a short plain-language explanation of the action. Add a few ordered points only when the snippet has distinct steps.
- Quote exact code lines when explaining important operations. Preserve existing comments verbatim as source comments; keep additional teaching prose clearly separate.
- End with the expected result or state change when it helps. Label illustrative model responses as examples, not guaranteed outputs.
- Keep explanations readable without hover, expansion, truncated labels, or side panels. Use normal prose typography for explanations and monospace for code.
- Highlight newly introduced terms only at their first explanation in course order. Use consistent colours for functions, classes, files, and concepts; never alter the code or source comments to add a highlight.
- Maintain `lesson-terms.json` with a short, plain definition for each term. The floating glossary carries introduced terms forward, opens from its icon, and closes on an outside click or Escape.

## Page layout

- Use a dark code panel followed by a calm explanation panel, with generous spacing and clear visual hierarchy.
- Show the complete important code line. Allow code to scroll horizontally on narrow screens; wrap explanation text.
- Preserve accessible contrast, keyboard-accessible copy controls, and a mobile layout without page-wide overflow.
- Verify snippet text against the source and check the page at desktop and mobile widths before delivery.
- End every lesson with clear previous/next navigation; use the course map at the beginning and end of Part I.

## Regenerate the pages

The `lessonN_final.md` drafts remain the content source. Each snippet has a `<!-- snippet: path#cell-id -->` source marker, its code fence, a **What happens here** explanation, and a **Result:** paragraph. Keep these together when editing. Supplementary examples cite the lesson Markdown itself.

From the `code` project folder, run `uv run python ../scripts/render_lesson_snippets.py`. The renderer uses the shared styles, preserves copyable source text, and checks notebook snippets against their referenced cells. After changing a notebook, update the corresponding draft snippets before rendering.
