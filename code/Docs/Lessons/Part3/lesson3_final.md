# Part III · Lesson 3 — Search by meaning and by exact words

## A note from me

“My robot's brush is jammed” and “What does E922 mean?” can point to the same product guide. One question describes the problem; the other gives us an exact code.

Vector search is useful for related meaning. Keyword search is useful when a particular code or product ID matters. Let’s give both a vote instead of expecting one search method to handle every question equally well.

## What we are building

We search the supplied Nexa product guides twice, combine the ranked results, and send the selected text to the model. This is hybrid retrieval: **vector results + keyword results → one ranked list → answer**.

BM25 is a keyword-ranking method. It rewards matching terms while accounting for how common they are and the document's length. Our tokenizer makes words lowercase and keeps hyphenated IDs together. These are search terms, not the chat model's billing tokens.

The two methods return different kinds of scores. We will use reciprocal rank fusion, or RRF, which combines their positions rather than pretending the raw scores are interchangeable. A document ranked highly by both methods receives two contributions.

Run the notebook from its directory. Live runs use the same Groq and OpenAI keys; rank-bm25 and langchain-text-splitters are declared in the project. We use the provided text guides rather than their PDF companions.

### Import the document and model helpers

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-01 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
```

**What happens here**

Document pairs a piece of text with metadata about its source. InMemoryVectorStore keeps documents and their vectors in this Python process. We import separate helpers for embeddings and chat replies.

**Result:** The building blocks are available; importing them makes no provider request.

### Connect the two kinds of model

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-02 -->
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

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-03 -->
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

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-04 -->
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

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-05 -->
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

### Build the vector index

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-06 -->
```python
vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

**What happens here**

The store asks the embedding model to encode the chunks, then keeps the vectors with their text. The retriever encodes a question with the same model and selects up to three similar chunks. This index is rebuilt when we rerun setup; it is not saved to disk. A returned search hit is a candidate, not proof that the question is answered.

**Result:** We can retrieve Documents by meaning without rebuilding the index for every question.

### Prepare readable context with source labels

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-07 -->
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

### Use the same tokenizer for documents and questions

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-08 -->
```python
import re
from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[\w-]+\b", text.lower())

bm25 = BM25Okapi([tokenize(chunk.page_content) for chunk in chunks])
```

**What happens here**

BM25Okapi builds a keyword index from lists of terms. The regular expression keeps a value such as NEX-1008 as one term. rank-bm25 does not preprocess our text for us, so we apply this same tokenize function when querying.

**Result:** We now have a keyword index over the same chunks as the vector store.

### Return only keyword hits with a positive score

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-09 -->
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

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-10 -->
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

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-11 -->
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

Each position contributes 1 divided by 60 plus its rank. The 60 is a smoothing constant, not the number of results or a similarity threshold. We identify each chunk by its stable ID, so a shared hit gains score without appearing twice. Different chunks from the same file remain separate candidates.

**Result:** The fused list contains up to three unique chunks, ordered by their combined rank contributions.

### Make hybrid retrieval reusable

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-12 -->
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

Both searches use the same question and underlying chunks. Fusion chooses the final candidates. We print a source and excerpt so the retrieval behaviour is visible before involving the answer model.

**Result:** Hybrid retrieval returns Documents ready to be used as context.

### Generate an answer and keep its evidence

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-13 -->
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

<!-- snippet: code/Part III Give the model something to read/3-hybrid-rag.ipynb#p3-3-step-14 -->
```python
code_result = ask_hybrid_rag("What does E922 mean and how do I fix it?")
description_result = ask_hybrid_rag("The brush on my robot vacuum is jammed. What should I do?")
print("Code:", code_result["answer"], code_result["sources"])
print("Description:", description_result["answer"], description_result["sources"])
```

**What happens here**

Both questions concern the CleanBot guide, but they supply different search clues. Generated answers can vary; check their claims against the returned chunks. The document says to turn off the robot and remove hair or thread from the main brush and end caps.

**Result:** We can compare retrieval evidence for an exact identifier and an everyday description.

## Why not just add the scores?

A vector similarity score and a BM25 score are not on the same scale. RRF uses where a chunk appears in each list. It is a simple way to merge rankings, not a guarantee that hybrid search always beats either method alone.

You can still miss the right passage. A very small chunk may separate an error code from its resolution, and a very large chunk may dilute the useful words. Inspect the excerpts before changing the model prompt.

Further reading: [rank-bm25 usage](https://github.com/dorianbrown/rank_bm25) describes the keyword index and its preprocessing requirements.

## Check your understanding

1. Why do exact codes help keyword search?
2. Why use the same tokenizer for documents and questions?
3. How does fusion avoid duplicate chunks?
4. Why is a search hit not proof that an answer is supported?

## Where we go next

Next we will choose the right information level: a product detail or a view across a catalog.

Complete notebook: [3-hybrid-rag.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/3-hybrid-rag.ipynb)

Further reading: [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
