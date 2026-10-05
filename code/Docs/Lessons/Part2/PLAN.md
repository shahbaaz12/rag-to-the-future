# Part II — Connecting the dots

Keep the existing notebook filenames so current links and bookmarks still work. Two filenames begin with `5`; the learning order below makes their roles explicit.

| Part II lesson | Website lesson | Notebook | What we build |
|---|---|---|---|
| 1 | 9 | `1-first-graph.ipynb` | The original two-step graph: Step1 and Step2 each return a new message. |
| 2 | 10 | `2-working-with-edges.ipynb` | Food delivery: read/validate, parallel availability checks, restaurant open/closed routing, and a three-attempt rider search. |
| 3 | 11 | `3-Connecting-LLM.ipynb` | Draft a reply to a meeting reschedule request with one model call. |
| 4 | 12 | `4-Using-Tools.ipynb` | Look up an employee's sample leave balance with one tool round. |
| 5 | 13 | `5-ReActive-Graph.ipynb` | Find Mumbai–Goa route IDs, fetch sample details, and compare within a budget through a model/tool loop. |
| 6 | 14 | `5-adding-memory.ipynb` | Remember a student's selected topics and learning level; keep two student threads separate. |
| 7 | 15 | `6-Streaming.ipynb` | Prepare a recipe request, then show completed node updates and live model text separately. |
| 8 | 16 | `7-human-in-loop.ipynb` | Pause a sample refund request and resume along approve or reject paths. |

Use `lesson1.md` as the foundation for the first final draft. Preserve the developer-to-developer voice: familiar examples, short questions, and plain explanations of what our code actually does. Keep any story optional and separate from code examples.

Each notebook is independent: run its cells from the top. Lessons 1, 2, and 8 run without a model API; model examples use the existing Groq setup. All teaching snippets must be copied exactly from their notebook cells, with comments preserved and explanations directly below them.

Build final Markdown drafts, then render the pages with the shared snippet styles, glossary, and previous/next navigation. Validate notebook structure and source matches, execute the local graphs, and test model graphs using deterministic offline replies. Check the website at desktop and mobile sizes.

## State and reducer coverage

Lesson 1 retains the original messages-only graph requested by the author: Step1 and Step2 demonstrate nodes, edges, and `add_messages`. Lessons 2–8 have four or five meaningful state fields. Lesson 2 adds replacement, list accumulation, dictionary merging, and a custom maximum reducer. It contrasts safe parallel partial updates with an optional full-copy failure, explains duplicate logs, compares numeric deltas with totals, and uses `Overwrite` to clear accumulated data.

Lessons 4–6 introduce message accumulation using `add_messages`. Lesson 6 also demonstrates replacement of a message with a matching ID, replacement of the selected-topic list, and separate checkpointed conversations. Reducers are functions rather than a closed set of types: choose the behavior that matches the field's meaning.

Keep comments short and steps straightforward. Do not add try/except boilerplate to teaching code. The intentional parallel-write failure is commented out so the delivery notebook runs from the top; the offline validator executes and checks that failure separately. Refund processing is a local demonstration and moves no money. Travel prices are sample data.

## Checks

From the `code` folder:

- `uv run python ../scripts/render_lesson_snippets.py`
- `uv run python ../scripts/validate_lessons.py`
- `uv run python ../scripts/validate_part_two.py`

The offline validator executes all notebook cells, exercises retry and routing alternatives, checks the conflicting parallel return, validates reducer behavior and student threads, and tests both refund decisions. It supplies deterministic model responses without provider API calls.
