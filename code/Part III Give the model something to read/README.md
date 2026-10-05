# Part III notebooks

Run the notebooks independently, in order:

1. `1-first-rag.ipynb`: a small collection and a conditional retrieval graph.
2. `2-conversational-rag.ipynb`: history-aware questions over the supplied fables.
3. `3-hybrid-rag.ipynb`: vector search, BM25, and rank fusion over product guides.
4. `4-hierarchical-rag.ipynb`: detail and complete-summary routes over the catalog.

From the `code` project, run `uv sync`, then `uv run jupyter lab`. Run each notebook with this notebook directory as its working directory; document paths point to `../doc`. The notebook contains section headings and code. The corresponding `Docs/Lessons/Part3/lessonN_final.md` and website pages contain the teaching explanations.

Live runs need these settings in `code/.env`:

```dotenv
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
```

Groq's `openai/gpt-oss-120b` writes answers, question rewrites, and route classifications. OpenAI's `text-embedding-3-small` creates document and query embeddings. Indexing and vector searches make embedding API calls; chat calls use Groq's API. Provider usage is separate. This setup reuses the project's installed integrations and avoids a local model download. No provider calls are needed for the offline checks.

The vector stores and conversation history live in the current Python process. Rerunning setup rebuilds indexes. Restarting the kernel clears them. No persisted Chroma/FAISS database from the reference projects is copied.

The supplied text companions and JSON catalog are used directly, so PDF extraction is not part of these examples. Keep the reference projects unchanged. `code/doc/README.md` records the data sources.

From `code`, validate with:

```powershell
uv run python ../scripts/render_lesson_snippets.py
uv run python ../scripts/validate_lessons.py
uv run python ../scripts/validate_part_three.py
```

The offline validator substitutes deterministic chat and lexical embedding fixtures while executing the real indexes, BM25, fusion, and graphs. It verifies application behavior, not the quality of hosted models or production semantic retrieval.
