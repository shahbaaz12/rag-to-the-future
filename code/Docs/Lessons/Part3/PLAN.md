# Part III — Give the model something to read

| Local lesson | Website | Example | Main idea |
|---|---|---|---|
| 1 | 17 | Embedding and cosine illustrations | Understand vectors, dimensions, related meaning and RAG. |
| 2 | 18 | Classic_Fables_Collection.pdf | Load, chunk, embed once, save in Chroma, query many times, and inspect scores. |
| 3 | 19 | The supplied fables | Rewrite a follow-up using history before retrieval. |
| 4 | 20 | Nexa product support guides | Combine vector and keyword searches with reciprocal rank fusion. |
| 5 | 21 | The hierarchical product catalog | Choose detail or complete subcategory summaries. |

Omit the author-removed Why RAG topic from Lesson 17. Lesson 17 retains its original introduction, What is RAG, components, step-by-step workflow, and a brief explanation of the model roles after Steps 8–9. Omit the separate How does the LLM fit in section. Add the embeddings, dimensions, and cosine geometry material before introducing the vector store. Include interactive arithmetic, a relationship map, and a four-strategy chunking comparison inspired by the supplied lecture page. Keep the cosine similarity definition and score table; omit the author-removed angle slider and sentence similarity meter from the lesson page. Use handmade word coordinates and label topic-keyword grouping as a semantic-chunking illustration. Show overlap and repeated storage in the fixed-size demo. Remove only the practical graph-building example from the lesson page; retain its notebook in the repository. Do not represent handmade points, preset scores, or word analogies as measured modern text embeddings. Do not teach universal similarity thresholds or interpretable names for individual embedding dimensions.

Lesson 18 uses the supplied PDF copied into code/doc. Extract page text with pypdf, preserve page metadata, split recursively, create 1,536-dimensional OpenAI embeddings, and use persistent Chroma with an explicitly configured cosine metric. Save IDs, text, vectors and metadata together. Index the unchanged document once; each new query is embedded separately. Show retrieval excerpts and both cosine distance and 1 - distance similarity. Use a new collection or deliberately update when the document, splitter or embedding setup changes.

Lessons 19–21 preserve the supplied examples' persistent Chroma backend and named collections. Use stable IDs so rerunning indexing with unchanged data does not add duplicate entries. Keep the existing Groq answer model and OpenAI embeddings. Keep the supplied text companions in the conversational and hybrid examples; the PDF extraction demonstration belongs in Lesson 18.

Lessons 18–21 begin with What we are building and a clear The idea behind it subsection. Omit A note from me in those lessons. Preview Lesson 21's conditional graph before its code. Use exact notebook source and comments in sequential snippets, each explained immediately below. Notebook Markdown contains only titles and useful headings.

Reference notebooks and PDFs remain unchanged in their original directories. Do not copy credentials or generated Chroma databases.

Lesson 20 introduces the support assistant, then the ten Nexa guides, then BM25 in its own plain-language section. Explain the benefit of meaning and keyword search with a labeled illustrative flow. Omit the standalone RRF theory section; preserve the exact ranking-combination source and explain its behavior briefly beneath the code.

Lesson 21 starts with the limits of k matching documents for a comparison across all products. Use heaters only as a familiar comparison example; the supplied catalog example compares Climate Control products. Describe the JSON hierarchy and its 20 products, 26 variants, and 10 category/subcategory groups. Define hierarchical retrieval as choosing specific details or a broader overview, then explain the contents of both collections and the model's routing choice. DETAIL retrieves up to three product/variant Documents; SUMMARY retrieves all ten group summaries for this small catalog. Explain the fields summaries omit. Omit the standalone What does global mean here section and the introductory run-directory, API-key, and shopping-advice paragraph.

Show how both Lesson 21 retrieval paths are constructed in a visual: catalog fields become 46 product/variant Documents or 10 Python-assembled group summaries, the shared embedding model creates vectors, and separate Chroma collections feed separate retrievers. Clarify that these are two retrieval paths sharing the same embedding and chat models; the chat model does not generate the summaries.

## Validation

From the code folder:

- uv run python ../scripts/render_lesson_snippets.py
- uv run python ../scripts/validate_lessons.py
- uv run python ../scripts/validate_part_three.py
- uv run python ../scripts/test_lesson_graphs.py
- node --test scripts/test_lesson_embeddings.cjs (from the repository root)

Validate with offline chat and embedding fixtures and real PDF extraction, splitting, Chroma storage, query scores, and retrieval code. Reopen collections in a new process and verify that documents are not re-embedded. Validate score direction and the cosine-distance conversion. Check conversation history, BM25 fusion, catalog routes and full-summary coverage. Check browser interactions, desktop/mobile layout, navigation and progress migration. Live provider quality is a separate check requiring API requests.
