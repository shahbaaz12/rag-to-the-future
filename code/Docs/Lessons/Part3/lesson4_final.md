# Part III · Lesson 4 — Search by meaning and by exact words

## What we are building

We are building a **support assistant for the Nexa product guides**. A user can enter an error code, such as **“What does E922 mean?”**, or describe a problem, such as **“The brush on my robot vacuum is jammed.”** The assistant should find the relevant instructions and explain what to do.

We will split the guides into chunks and search those same chunks in two ways: **by meaning** using Chroma, and **by matching words** using BM25. We will combine the useful passages and give their text to the chat model so it can answer with a source filename.

### The idea behind it

An error code and a problem description give us different clues. Searching by meaning helps with everyday descriptions. Searching by words helps with exact codes and product IDs. Using both gives us two ways to find the information we need.

This is **hybrid retrieval**: search the same collection in two ways, select useful passages from both results, then write an answer from that text.

## The documents we will search

The collection contains **ten sample Nexa product guides**, including **HomeHub Mini**, **AirSense**, and **CleanBot S2**. Each guide describes a product, its features, setup and usage instructions, and error codes with suggested resolutions.

We use the supplied text files. Each chunk keeps the **source filename and a unique chunk ID in metadata**. The filename tells us which guide it came from. The chunk ID lets us recognize a passage found by both searches and keep it once.

Some words, such as **app**, **power**, and **brush**, appear in several places. The guides also contain specific IDs and error codes. The CleanBot S2 guide contains **NEX-1008** and **E922**, its brush-jam code. These give us useful examples of a description we can search by meaning and a code we can search by words.

## BM25: search by matching words

### What is BM25?

**BM25** is a way to rank passages by the words they share with a question. It gives each passage a score based on matching words, how common those words are across the collection, and the passage's length. We can then take the highest-scoring matches.

Think of looking up a code in a manual. If the question contains **E922**, a passage containing **E922** is a useful place to look.

### Why do we need it here?

Our guides contain exact names, product IDs, and error codes. We want those clues to help the search. BM25 adds a keyword search alongside our meaning search, so an exact code can help bring the right instructions into the results.

BM25 uses the words in the text; it does not need an embedding model or a chat model. We build its keyword index from the same chunks we save in Chroma. The [rank-bm25 usage guide](https://github.com/dorianbrown/rank_bm25) shows how to build the index and search it.

## How both searches help

Imagine asking, **“E922: the brush on my robot vacuum is jammed. How do I fix it?”**

The meaning search uses the description to find related passages. The keyword search uses the exact code to find passages that mention it. Each returns a list of possible matches. We choose useful chunks from both lists and keep any shared chunk once.

<!-- visual: hybrid-search -->

**The benefit:** a relevant passage has two ways to be found—through the problem's meaning or through the words and codes in the question. The model gets selected guide text to read before answering.

The two searches can return different passages, or they can find the same one. Combining them can help, but we still inspect the selected text to check that it answers the question.

## Build the support assistant

Run the notebook from its directory. Live runs use the Groq and OpenAI keys. The project includes langchain-chroma, rank-bm25, and langchain-text-splitters. Chroma saves the vector index on disk; setup builds the BM25 keyword index from the same chunks.

### Import the document and model helpers

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-01 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
```

**What happens here**

**Document** pairs a piece of text with metadata about its source.

**Chroma** is the vector database used in the supplied example. With persist_directory, it saves the indexed text, vectors, and source details to a local folder. We import separate helpers for embeddings and chat replies.

**Result:** The building blocks are available; importing them makes no provider request.

### Connect the two kinds of model

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-02 -->
```python
load_dotenv()
# Groq generates answers; OpenAI creates search embeddings.
model = init_chat_model(
    "openai/gpt-oss-120b", model_provider="groq", reasoning_effort="low",
)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

**What happens here**

Keep GROQ_API_KEY and OPENAI_API_KEY in the code project's .env file. The chat model writes answers. OpenAIEmbeddings turns text into vectors for searching; it does not write an answer. Creating these objects is setup. Indexing documents and searching later make embedding requests.

**Result:** We have a chat model and an embedding model, with different jobs.

### Find the supplied text documents

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-03 -->
```python
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Run this notebook with its own directory as the working directory.
data_dir = Path("../doc/products")
text_files = sorted(data_dir.glob("*.txt"))
print("Files:", len(text_files))
```

**What happens here**

We use the text companions supplied alongside your PDFs. This lets us focus on retrieval rather than PDF extraction. The relative path points from this notebook's folder to code/doc/products. These are the actual product guides used by the example.

**Result:** The source filenames are listed in a predictable order.

### Keep text and source together

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-04 -->
```python
documents = [
    Document(
        page_content=path.read_text(encoding="utf-8"),
        metadata={"source": path.name},
    )
    for path in text_files
]
print(documents[0].metadata)
```

**What happens here**

Each file becomes a Document. page_content holds its text, and metadata records the filename. We will carry that filename through splitting and retrieval so we can inspect where an answer's context came from.

**Result:** We have one source document per text file.

### Split the documents into searchable pieces

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-05 -->
```python
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
chunks = splitter.split_documents(documents)
for index, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = f"{chunk.metadata['source']}:{index}"
print("Documents:", len(documents), "Chunks:", len(chunks))
```

**What happens here**

A chunk is a smaller piece we can retrieve and send to the model. This splitter uses character counts, not token counts. It aims for 600 characters with up to 80 characters of overlap, preferring natural boundaries. Overlap helps nearby sentences stay connected; it also repeats some text. We attach a stable ID to each chunk.

**Result:** Every searchable chunk keeps its source filename and its own ID.

### Save the vector index in Chroma

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-06 -->
```python
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    ids=[chunk.metadata["chunk_id"] for chunk in chunks],
    collection_name="hybrid",
    persist_directory="./chroma_db",
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

**What happens here**

Chroma embeds the chunks and saves their text, vectors, and metadata in the hybrid collection inside ./chroma_db. The IDs come from chunk_id, so rerunning this cell with the unchanged notes updates the same entries instead of adding duplicates. It still makes embedding requests. The retriever embeds a question with the same model and selects up to three similar chunks. A search hit is a candidate, not proof that the question is answered.

**Result:** The hybrid collection is saved on disk and can retrieve Documents by meaning. As in Lesson 18, reopen it with Chroma using the same collection name, folder, and embedding model to avoid re-indexing.

### Prepare readable context with source labels

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-07 -->
```python
def format_context(documents: list[Document]) -> str:
    return "\n\n".join(
        f"[{doc.metadata['source']}]\n{doc.page_content}"
        for doc in documents
    )
```

**What happens here**

We join the retrieved text into the context the chat model will receive. The bracketed filename gives the model a label it can cite. Our application still returns the actual Documents so we can check the supporting text ourselves.

**Result:** A model prompt can include both the evidence and its source names.

### Build the BM25 keyword index

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-08 -->
```python
import re
from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[\w-]+\b", text.lower())

bm25 = BM25Okapi([tokenize(chunk.page_content) for chunk in chunks])
```

**What happens here**

**The indexing happens in `bm25 = BM25Okapi([tokenize(chunk.page_content) for chunk in chunks])`.** We turn every chunk into a list of words, then pass all those lists to BM25Okapi. It prepares the keyword index we will use for searching. This step uses text; it does not create embedding vectors or call a model.

The tokenize function makes the text lowercase and keeps a value such as NEX-1008 as one term. We use the same function on questions so their words can match the indexed words.

The next snippet searches this index with `scores = bm25.get_scores(tokenize(question))`.

**Result:** We now have a keyword index over the same chunks as the vector store.

### Return only keyword hits with a positive score

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-09 -->
```python
def keyword_search(question: str, k: int = 5) -> list[Document]:
    scores = bm25.get_scores(tokenize(question))
    ranked = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)
    return [chunks[index] for index in ranked[:k] if scores[index] > 0]
```

**What happens here**

get_scores returns one score per chunk, in corpus order. We sort the indices and return up to k positive-scoring candidates. For a code that never appears, this branch returns an empty list rather than filling the result with zero-score matches.

**Result:** Exact matches can contribute useful evidence, while absent terms add no keyword candidates.

### Inspect both methods for one error code

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-10 -->
```python
question = "What does E922 mean?"
vector_results = vector_store.similarity_search(question, k=5)
keyword_results = keyword_search(question)
print("Vector IDs:", [doc.metadata["chunk_id"] for doc in vector_results])
print("Keyword IDs:", [doc.metadata["chunk_id"] for doc in keyword_results])
```

**What happens here**

The vector search ranks by embedding similarity. BM25 ranks matching terms. In the supplied CleanBot guide, E922 means a brush jam. Inspecting the IDs shows whether the two methods selected the same chunk; their rankings need not agree.

**Result:** We have two lists of candidate Documents for the same question.

### Combine rankings without duplicating a chunk

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-11 -->
```python
def reciprocal_rank_fusion(vector_results, keyword_results, final_k=3):
    scores, documents_by_id = {}, {}
    for results in [vector_results, keyword_results]:
        for rank, document in enumerate(results, start=1):
            chunk_id = document.metadata["chunk_id"]
            documents_by_id[chunk_id] = document
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (60 + rank)
    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    return [documents_by_id[chunk_id] for chunk_id in ranked_ids[:final_k]]
```

**What happens here**

This helper combines the two result lists using each chunk's position in those lists. A chunk near the top of a list gets more weight. If both searches return the same chunk ID, we add its contributions and keep one copy. The code uses 1 / (60 + rank) to assign that weight; we can focus on the resulting list here.

**Result:** We have up to three different chunks selected from the two search results.

### Make hybrid retrieval reusable

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-12 -->
```python
def hybrid_search(question: str) -> list[Document]:
    vector_results = vector_store.similarity_search(question, k=5)
    keyword_results = keyword_search(question, k=5)
    return reciprocal_rank_fusion(vector_results, keyword_results)

hybrid_results = hybrid_search("What does E922 mean?")
for document in hybrid_results:
    print(document.metadata["source"], document.page_content[:120])
```

**What happens here**

Both searches use the same question and chunks. The helper combines their results and selects the final passages. We print the source and some text from each passage before asking the chat model for an answer.

**Result:** Hybrid retrieval returns Documents ready to be used as context.

### Generate an answer and keep its evidence

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-13 -->
```python
def ask_hybrid_rag(question: str) -> dict:
    retrieved_documents = hybrid_search(question)
    instruction = (
        "Answer using only the context. If it is insufficient, say you could not find the answer. "
        "Cite filenames in brackets.\nContext:\n" + format_context(retrieved_documents)
    )
    answer = model.invoke([SystemMessage(instruction), HumanMessage(question)]).text
    return {
        "question": question, "answer": answer, "documents": retrieved_documents,
        "sources": sorted({doc.metadata["source"] for doc in retrieved_documents}),
    }
```

**What happens here**

The generation step has the same job as before: read selected text and answer the question. Hybrid retrieval changes how we select the context, not how a chat model learns. We return distinct filenames plus the actual chunks, so multiple excerpts from one guide do not create duplicate source labels.

**Result:** The result carries the question, answer, retrieved Documents, and source filenames.

### Try an exact code and a natural description

<!-- snippet: code/Part III Give the model something to read/4-hybrid-rag.ipynb#p3-3-step-14 -->
```python
code_result = ask_hybrid_rag("What does E922 mean and how do I fix it?")
description_result = ask_hybrid_rag("The brush on my robot vacuum is jammed. What should I do?")
print("Code:", code_result["answer"], code_result["sources"])
print("Description:", description_result["answer"], description_result["sources"])
```

**What happens here**

Both questions concern the CleanBot guide, but they supply different search clues. Generated answers can vary; check their claims against the returned chunks. The document says to turn off the robot and remove hair or thread from the main brush and end caps.

**Result:** We can compare retrieval evidence for an exact identifier and an everyday description.

## Check your understanding

1. Why do exact codes help keyword search?
2. Why use the same tokenizer for documents and questions?
3. Why keep a chunk ID when combining the two search results?
4. Why is a search hit not proof that an answer is supported?

## Where we go next

Next we will choose the right information level: a product detail or a view across a catalog.

Complete notebook: [4-hybrid-rag.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/4-hybrid-rag.ipynb)

Further reading: [LangChain Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma), [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
