# Part III — Give the model something to read

The author's lesson1.md supplies the first lesson's four questions: what RAG is, why we need it, its components, and where the LLM fits. Build four lessons from the supplied references; keep the remaining four course slots planned.

| Local lesson | Website | Example | Main idea |
|---|---|---|---|
| 1 | 17 | Four short course notes | Prepare searchable documents; decide whether to retrieve; generate using the retrieved context. |
| 2 | 18 | The supplied fables | Rewrite a follow-up question using history before retrieving. |
| 3 | 19 | Nexa product support documents | Combine vector search and BM25 keyword search with reciprocal rank fusion. |
| 4 | 20 | The supplied hierarchical product catalog | Route to product/variant details or complete subcategory summaries. |

Use small, sequential source snippets and explanations below them in the final drafts and HTML. Notebooks contain only useful headings, short comments, and executable code. Graph states have four meaningful fields; nodes return partial updates. No try/except boilerplate.

Preserve the reference ideas while updating imports and correcting non-runnable cells. Use the existing Groq model for answers and OpenAIEmbeddings for indexing/query embeddings. An in-memory vector store keeps the retrieval steps visible without persisted databases or model downloads. Text companions from the supplied doc directory avoid adding a PDF extraction step to these four lessons. Explain these choices and the separate API keys in the pages.

Copy the text stories, text product guides, and hierarchical JSON catalog into code/doc. Do not copy credentials, generated Chroma databases, or unrelated reference code. Keep source filenames as metadata, and return retrieved documents alongside answers.

Be precise about the examples: the first retrieval decision is a Python keyword rule, not autonomous model reasoning; embedding is separate from answer generation; history resolves references but is not evidence; search rankings do not prove an answer; the hierarchy uses two retrieval levels and is not GraphRAG. The summary route includes all subcategory summaries so a whole-catalog question is not answered from just two search hits.

Validate notebook structure, exact snippet/comment matches, real vector-store search, graph branches, conversation history, BM25 filtering, fusion deduplication, and summary coverage using deterministic offline fixtures. Do not make provider API calls during validation. Preview desktop/mobile pages, glossary, theme, and navigation.

Reference notebooks remain read-only in their original directories. The original lesson1.md also remains unchanged.

## Validation

From the code project:

- `uv run python ../scripts/render_lesson_snippets.py`
- `uv run python ../scripts/validate_lessons.py`
- `uv run python ../scripts/validate_part_three.py`

Live model/embedding response quality remains a separate check requiring the user's provider keys. The offline fixtures exercise the actual application pipeline without making provider requests.
