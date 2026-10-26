# RAG to the Future

## Folders

- `site/`: the website's HTML, CSS, JavaScript, course metadata, and `assets/`.
- `code/`: runnable notebooks, sample documents, Python dependencies, and lesson drafts in `Docs/Lessons/`.
- `scripts/`: page generators, the local server, and validation tools.
- `references/`: design guidance and implementation notes.

## Run the website

From the repository root:

```powershell
python scripts/serve_site.py
```

Open <http://127.0.0.1:8765/>. To use another port, add `--port 8000`.

The server serves `site/` at the original URLs, so bookmarks such as
`/lesson-21.html` still work. It also serves notebook and document links under
`/code/`. `/site/` URLs work as well. Directory listings and hidden files are
not served. Keep this server command when previewing the site so source links
continue to work.

## Update lesson pages

Edit the drafts in `code/Docs/Lessons/` and their associated notebooks. Preserve
the exact source code and comments displayed in the lessons. From `code/`, run:

```powershell
uv run python ../scripts/render_lesson_snippets.py
uv run python ../scripts/temporal_design.py
uv run python ../scripts/validate_lessons.py
uv run python ../scripts/validate_site.py
```

The generators read and write pages in `site/`. For appearance changes, edit the
stylesheets there; the shared design generator refreshes versioned asset links.
