# Part III · Lesson 2 — Turn a PDF into a searchable collection

## What we are building

We are building a **searchable collection of fables** from Classic_Fables_Collection.pdf. We will load the PDF, split its text into chunks, create vectors, and save the chunks in Chroma. Then we will ask several questions and inspect the returned passages and their scores.

### The idea behind it

In Lesson 17, we learned why related text can have similar vectors. Here, we make that idea visible in a real store. Chroma compares a question's vector with saved chunk vectors and returns the original text of the nearest matches.

**Prepare once, query many times:** load → chunk → embed → save. For each new question: embed the question → search the saved vectors → read the matching text. We re-index when the source material or indexing setup changes, not for every question.

We stop at retrieval in this lesson. You will see exactly what text a later chat model could receive before it writes an answer.

### The document we will search

**Classic_Fables_Collection.pdf** contains ten short fables, including **The Boy Who Cried Wolf**, **The Milkmaid and Her Pail**, and **The Wolf in Sheep's Clothing**. It has a title page followed by one page for each story.

We will load each page, split its text into chunks, and keep the **page number in each chunk's metadata**. Metadata is information saved alongside the text. When a search returns a chunk, its page number tells us where to find that passage in the original PDF.

Some words repeat: **wolf** appears in two different stories, and **milk** appears several times in the milkmaid's story. This gives us a useful way to check retrieval. We can read the returned passage and use its page number to see which story it came from and whether it answers our question.

## Chunking: cut the document into useful passages

**Chunking** means splitting a long document into smaller pieces of text. A large chunk may bury the useful sentence among unrelated material. A tiny chunk may lose the sentences needed to understand it. We want each piece to contain a useful amount of context.

| Strategy | How it cuts the text |
|---|---|
| Fixed size | Cut after a set number of characters or tokens; this can break words or sentences. |
| Recursive | Try larger text boundaries first, then smaller ones when a piece is still too long. |
| Semantic | Use changes in topic or meaning to choose boundaries; this usually adds processing. |
| Structure-aware | Follow headings, sections, or other structure already in the document. |

We will use **recursive splitting** with a limit of 800 characters and up to 100 characters of overlap. Overlap repeats some text around boundaries. It can help preserve context, but it does not guarantee that every answer fits inside one chunk. These settings are a starting point to inspect, not universal best values.

## How the vectors are stored

**Chroma** keeps a record for each chunk: an ID, its original text, its vector, and source metadata. The vector is used for search. The text is what we retrieve and read. Metadata tells us which PDF page to check.

| Record field | What we save |
|---|---|
| ID | A stable label for this chunk. |
| Text | The chunk's original words. |
| Embedding | The list of numbers representing those words. |
| Metadata | The source filename, page number, and chunk ID. |

**A vector's dimensions** are the number of coordinates it contains. In this example, each embedding has 1,536 numbers. All stored vectors and query vectors must use the same embedding model and dimension settings.

## How to read the search scores

We will configure Chroma to use **cosine distance**. Its similarity_search_with_score method returns a distance, even though the method name includes “similarity.” Lower distance means a closer match. We also print **cosine similarity = 1 − distance**, where higher means a closer match.

| Illustrative cosine distance | Corresponding similarity | How to compare these results |
|---|---|---|
| 0.10 | 0.90 | Closest of these three examples. |
| 0.35 | 0.65 | Less similar than the first example. |
| 0.80 | 0.20 | Least similar of these three examples. |

These numbers demonstrate the calculation; they are not recorded results from the fables. The notebook prints the actual scores when you run it. A score is not a percentage of correctness, and there is no universal cutoff for a useful passage. Compare the excerpts and check whether they contain the information you need.

## Build and search the collection

Run the snippets in order in 2-pdf-retrieval.ipynb. The PDF is included in code/doc. The first indexing run needs OPENAI_API_KEY in the code project's .env file. Each new search also makes an embedding request; this lesson does not call a chat model.

### Import the PDF and retrieval helpers

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-01 -->
```python
from pathlib import Path
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
```

**What happens here**

PdfReader extracts text from the supplied PDF. Document keeps text with source information. The splitter creates chunks, the embedding model creates vectors, and Chroma stores them. We do not need a chat model for this lesson.

**Result:** The helpers are ready; importing them makes no embedding request.

### Choose the embedding model

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-02 -->
```python
load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)
```

**What happens here**

We load OPENAI_API_KEY from .env and choose 1,536 numbers per vector. Creating this object does not embed anything yet. Later, this same model will embed both the stored chunks and new questions.

**Result:** Every live embedding in this example uses the same model and dimensions.

### Open the supplied PDF

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-03 -->
```python
# Run this notebook with its own directory as the working directory.
pdf_path = Path("../doc/Classic_Fables_Collection.pdf")
reader = PdfReader(pdf_path)
print("PDF:", pdf_path.name)
print("Pages:", len(reader.pages))
```

**What happens here**

The repository contains a copy of the supplied Classic_Fables_Collection.pdf. It has eleven pages: a title page and ten fables. We read the local file.

**Result:** The notebook prints the filename and eleven pages.

### Keep each page with its source details

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-04 -->
```python
documents = []
for page_number, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    if text.strip():
        documents.append(Document(
            page_content=text,
            metadata={"source": pdf_path.name, "page": page_number},
        ))
print(documents[3].metadata)
print(documents[3].page_content[:200])
```

**What happens here**

Each nonempty page becomes a Document. The metadata records the filename and a page number starting at one. Page 4 contains The Ant and the Grasshopper. This PDF already has extractable text; scanned image PDFs would need OCR first.

**Result:** The text stays linked to the page it came from.

### Split the page text into chunks

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-05 -->
```python
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(documents)
for index, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = f"{pdf_path.stem}:{chunk.metadata['page']}:{index}"
chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
print("Pages:", len(documents), "Chunks:", len(chunks))
print(chunks[0].metadata)
print(chunks[0].page_content[:200])
```

**What happens here**

The splitter tries to keep natural text boundaries within an 800-character limit. Neighboring chunks may share up to 100 characters. These are characters, not tokens. Each chunk inherits its page metadata and gets a stable ID for this unchanged PDF and splitting setup.

**Result:** We have smaller searchable passages, each with a filename, page, and ID.

### Open a persistent Chroma collection

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-06 -->
```python
vector_store = Chroma(
    collection_name="classic_fables_cosine",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
    collection_configuration={"hnsw": {"space": "cosine"}},
)
```

**What happens here**

Chroma opens the named collection, creating it if needed. persist_directory saves it on disk. We choose cosine distance so the score interpretation below is explicit. Opening the collection alone does not embed the PDF.

**Result:** The collection is ready to store or search vectors.

### Index once, then reuse the saved collection

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-07 -->
```python
# This lesson uses one unchanged PDF and the same chunking setup.
if not vector_store.get(limit=1)["ids"]:
    vector_store.add_documents(documents=chunks, ids=chunk_ids)
    print("Indexed", len(chunks), "chunks.")
else:
    print("Using the saved collection; no document embeddings created.")
```

**What happens here**

The first run embeds each chunk and saves its text, vector, and metadata. Later runs reuse the existing collection. This simple check assumes the same PDF, splitter settings, and embedding model. If those change, build a new named collection or deliberately update the old one.

**Result:** The document vectors are created once for this collection, not once per question.

### Inspect one saved record and its vector dimensions

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-08 -->
```python
saved_record = vector_store.get(
    ids=[chunk_ids[0]], include=["documents", "metadatas", "embeddings"],
)
stored_vector = saved_record["embeddings"][0]
print("ID:", saved_record["ids"][0])
print("Metadata:", saved_record["metadatas"][0])
print("Text:", saved_record["documents"][0][:120])
print("Dimensions:", len(stored_vector))
print("First 8 coordinates:", stored_vector[:8])
```

**What happens here**

get reads one saved record by its chunk ID. The original text, metadata, and embedding belong to that same record, but are stored in separate fields. Metadata tells us the source and page; the embedding is the list of numbers used for search.

len(stored_vector) counts only the numbers in the embedding. It does not count the text or metadata. We configured the live embedding model to return 1,536 numbers, so we expect 1,536 dimensions. The printed length confirms what is actually stored. The preview shows only the first eight numbers. Reading this record does not embed the text again.

**Result:** We can see what is saved and verify the actual vector length.

### Print retrieved passages with their scores

This snippet defines a helper function. **We supply the questions in the next three snippets** when we call show_matches. Defining the function does not run a search yet.

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-09 -->
```python
def show_matches(question: str, k: int = 3):
    matches = vector_store.similarity_search_with_score(question, k=k)
    print("Question:", question)
    for document, distance in matches:
        similarity = 1 - distance
        print(f"Page {document.metadata['page']} | cosine distance {distance:.3f} | similarity {similarity:.3f}")
        print(document.page_content[:350])
        print()
    return matches
```

**What happens here**

question is the input we pass to the function. In Snippet 10, `grasshopper_matches = show_matches("Who helped the hungry grasshopper in winter?")` passes that sentence into question. Snippets 11 and 12 pass questions about the lion and the crow. We write these questions ourselves; the function does not generate them.

**k is the number of matching chunks we ask the search to return.** In `def show_matches(question: str, k: int = 3):`, the default is 3. The next three calls use that default, so each search asks for up to three closest chunks. Several chunks can come from the same page.

In `matches = vector_store.similarity_search_with_score(question, k=k)`, the first k is Chroma's parameter name, and the second k is the value supplied to our helper. We pass the result count through to Chroma.

When we call the function, Chroma embeds the supplied question, searches the saved chunk vectors, and returns text with cosine distance. Smaller distance means a closer match. Because we chose cosine distance, 1 - distance gives cosine similarity: larger similarity means a closer direction. We print the page and excerpt so we can judge whether the passage actually helps.

**Result:** The helper is ready to search and print passages when we supply a question.

### Search for the grasshopper story

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-10 -->
```python
grasshopper_matches = show_matches("Who helped the hungry grasshopper in winter?")
```

**What happens here**

Inspect the returned passages for the ant helping the grasshopper. In the supplied PDF, that story is on page 4. The top three passages can overlap or include other candidates; check the text rather than trusting the score alone.

**Result:** The notebook shows actual retrieved excerpts and scores for this question.

### Ask about a different story

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-11 -->
```python
lion_matches = show_matches("How did the mouse free the lion from the hunters' net?")
```

**What happens here**

This is a new question using the same saved collection. The query gets its own vector; the document chunks are not re-embedded. The Lion and the Mouse is on page 5. Look for the passage about gnawing through the ropes.

**Result:** A second question searches the same stored vectors.

### Try another query without rebuilding the index

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-12 -->
```python
crow_matches = show_matches("How did the crow get water from the pitcher?")
```

**What happens here**

The Crow and the Pitcher is on page 8. Compare the returned passages with the previous searches. Each question changes the query vector and the ranking, while the saved document vectors remain the same.

**Result:** One indexed PDF supports many queries.

### Reopen the collection after a restart

<!-- snippet: code/Part III Give the model something to read/2-pdf-retrieval.ipynb#p3-pdf-step-13 -->
```python
reopened_store = Chroma(
    collection_name="classic_fables_cosine",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
reopened_matches = reopened_store.similarity_search("a mouse helping a lion", k=2)
for document in reopened_matches:
    print("Page:", document.metadata["page"], document.page_content[:200])
```

**What happens here**

After a restart, rerun the imports and embedding-model setup, then this cell. Use the same folder, collection name, and embedding model. Chroma reads the saved collection and its cosine configuration. We can search without rerunning PDF loading, chunking, or document indexing. The new question still needs an embedding.

Here, k=2 asks for up to two matching chunks.

**Result:** Persistence lets us reuse the indexed PDF across notebook sessions.

## Check your understanding

1. Why split the PDF before embedding it?
2. Which fields let you check where a retrieved passage came from?
3. Which work happens only during indexing, and which work happens for each question?
4. Does a smaller cosine distance mean a better or worse vector match?
5. Why can a close match still fail to answer the question?

## Where we go next

Next, we will use conversation history to make a follow-up question clear before searching.

Complete notebook: [2-pdf-retrieval.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/2-pdf-retrieval.ipynb)

Source PDF: [Classic_Fables_Collection.pdf](code/doc/Classic_Fables_Collection.pdf).

Further reading: [Chroma collection configuration](https://cookbook.chromadb.dev/core/collections/) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
