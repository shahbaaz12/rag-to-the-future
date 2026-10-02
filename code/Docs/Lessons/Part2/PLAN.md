# Part II — Connecting the dots

Keep the existing notebook filenames so current links and bookmarks still work. Two filenames begin with `5`; the learning order below makes their roles explicit.

| Part II lesson | Website lesson | Notebook | What we build |
|---|---|---|---|
| 1 | 9 | `1-first-graph.ipynb` | Two ordinary Python nodes sharing state. |
| 2 | 10 | `2-working-with-edges.ipynb` | Sequential, parallel, conditional, and bounded looping flows. |
| 3 | 11 | `3-Connecting-LLM.ipynb` | A model call inside one graph node. |
| 4 | 12 | `4-Using-Tools.ipynb` | One controlled round of tool execution. |
| 5 | 13 | `5-ReActive-Graph.ipynb` | A model/tool loop that can request further information. |
| 6 | 14 | `5-adding-memory.ipynb` | Checkpointed conversations with separate thread IDs. |
| 7 | 15 | `6-Streaming.ipynb` | Node updates and generated text chunks. |
| 8 | 16 | `7-human-in-loop.ipynb` | A paused request that resumes with a human decision. |

Use `lesson1.md` as the foundation for the first final draft. Preserve the developer-to-developer voice: familiar examples, short questions, and plain explanations of what our code actually does. Keep any story optional and separate from code examples.

Each notebook is independent: run its cells from the top. Lessons 1, 2, and 8 run without a model API; model examples use the existing Groq setup. All teaching snippets must be copied exactly from their notebook cells, with comments preserved and explanations directly below them.

Build final Markdown drafts, then render the pages with the shared snippet styles, glossary, and previous/next navigation. Validate notebook structure and source matches, execute the local graphs, and test model graphs using deterministic offline replies. Check the website at desktop and mobile sizes.
