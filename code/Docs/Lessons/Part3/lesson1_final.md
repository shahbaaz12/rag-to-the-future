# Part III · Lesson 1 — Give the model something to read

## A note from me

We have given the model questions, messages, tools, and a workflow. But suppose we ask about something written in our own notes. How would the model know what those notes say?

We could paste the whole file into every prompt. That works for a small note, but becomes awkward as our collection grows. Let’s give the application a way to find the useful pieces first.

## What is RAG?

**RAG** stands for **Retrieval-Augmented Generation**.

**Retrieval** means finding relevant information.

**Augmented** means adding that information to the model's input.

**Generation** is the answer the model writes from that input.

Suppose we ask, “What does RAG do?” and the answer is in our course notes. Our application finds the useful note and sends it to the model along with the question. The model reads that note and uses it to write an answer. This is the basic idea of RAG: **find useful text, then ask the model to answer using it.**

## Why RAG?

A model may not know what is in our private files or recently updated notes. RAG gives it the relevant text when we ask a question. When our notes change, we can update the searchable collection without retraining the chat model.

The answer still depends on what we find and how the model uses it. If we find the wrong passage, the answer may be wrong too. We should check the retrieved text and ask the model to say when that text does not contain the answer.

## Components of a RAG system

**A chunk** is a small piece of a document. We split long documents into chunks so we can search for a useful passage instead of sending the entire document to the model.

**A vector** is a list of numbers, such as `[0.2, -0.5, 0.8]`. In RAG, we use vectors to represent text and compare it with other text. These three numbers are only an illustration; real vectors usually have many more numbers.

**An embedding model** turns text into a vector. That vector is called an **embedding**. We use the same embedding model for the document chunks and the question so their vectors can be compared.

**A vector store** keeps each chunk's text, vector, and source details together. This lets us search using vectors and get back the matching text. A vector database serves this purpose too; our small example uses an in-memory vector store.

### How RAG works, step by step

First, we prepare the documents. Then, whenever a question arrives, we search the prepared collection and give the useful text to the chat model. Follow the arrows down each phase.

<!-- visual: rag-flow -->

**Steps 1–4: prepare the documents.** Load the documents, split long ones into chunks, create a vector for each chunk, and store each vector with the text it came from. We do this before answering questions, and update the collection when the documents change.

**Step 5: turn the question into a vector.** We usually embed the whole question as one piece of text. We do not split it into document-style chunks. The original question is kept for the final prompt.

**Steps 6–7: search and retrieve.** Compare the question's vector with the stored chunk vectors. Select similar chunks, then return their original text and source details. A retriever is the helper that performs this search and returns the selected documents.

**Steps 8–9: build the prompt and answer.** Put the original question and retrieved text into a prompt. The chat model reads that prompt and writes an answer. It receives the **text**, not the vectors.

Similar vectors help us find related passages. They do not tell us whether a passage is true or whether it contains enough information to answer.

### Which piece does each job?

| Piece | Its job in our application |
|---|---|
| Source documents | Our notes, files, or other material containing possible answers. |
| Splitter | Divide a long document into smaller pieces called chunks. |
| Embedding model | Turn each chunk and the question into vectors we can compare. |
| Vector store | Save each chunk's text, vector, and source details together. |
| Retriever | Search the stored vectors and return the selected chunks as text. |
| Prompt and chat model | Give the model the question and selected text, then ask it to write an answer. |

**In this lesson**, our four sample notes are already short. Each note can be one searchable Document, so we skip splitting. In the next lesson, we will split longer files into chunks. The rest of the flow stays the same.

## How does the LLM fit in?

**The chat model** writes the answer in Step 9. Our application gives it the original question, the retrieved text, and instructions for answering from that text.

**The embedding model** creates the vectors in Steps 3 and 5. It helps us search; it does not write the final answer. The retriever uses the vector store to find useful text before we call the chat model.

For this example, OpenAI creates the embeddings and Groq supplies the chat model that writes answers. These are separate jobs, so we can use different providers.

To run the notebook, put GROQ_API_KEY and OPENAI_API_KEY in the code project's .env file. From the code folder, run uv sync to install the dependencies, then run the notebook from its own directory. Creating and searching embeddings makes OpenAI API calls; generating an answer makes a Groq API call.

## What we are building

Our path is **decide → retrieve if needed → generate**. It follows the supplied agenticrag reference, with current imports and small partial state updates.

The decision here is a simple Python keyword rule. Although the reference calls this agentic RAG, this example does not ask an autonomous agent to choose its own search strategy. It shows the retrieval branch clearly before adding more moving parts.

### Import the document and model helpers

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-01 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
```

**What happens here**

**Document** pairs a piece of text with metadata about its source.

**InMemoryVectorStore** keeps documents and their vectors in this Python process. We import separate helpers for embeddings and chat replies.

**Result:** The building blocks are available; importing them makes no provider request.

### Connect the two kinds of model

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-02 -->
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

### Create a tiny knowledge collection

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-03 -->
```python
sample_texts = [
    "LangGraph connects Python functions into a stateful workflow using nodes and edges.",
    "RAG retrieves relevant documents and adds their text to a prompt before generating an answer.",
    "A vector store keeps embeddings with their source text so similar material can be searched.",
    "The application executes tools requested by a model and returns the results to the model.",
]
documents = [
    Document(page_content=text, metadata={"source": f"course-note-{index}"})
    for index, text in enumerate(sample_texts, start=1)
]
```

**What happens here**

These four short notes are the knowledge collection. The source labels are local names for these sample notes. We are not asking the model to browse the web; this application will search only the Documents we put into its index.

**Result:** Each note has text and a source label.

### Make the notes searchable

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-04 -->
```python
vector_store = InMemoryVectorStore.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
```

**What happens here**

from_documents embeds and indexes the notes. search_kwargs passes k to the retriever, so each search returns up to two candidates. We keep this index in memory for a small example. The reference uses FAISS; the same retrieve-then-answer idea works here without adding another database package.

**Result:** The retriever is ready to return the original text selected by vector similarity.

### Describe the four-field state

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-05 -->
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class RagState(TypedDict):
    question: str
    documents: list[Document]
    answer: str
    needs_retrieval: bool
```

**What happens here**

question is the input. documents holds retrieved evidence, answer holds the reply, and needs_retrieval records our decision. These fields use replacement updates. Each node returns only the fields it changes.

**Result:** Our working record separates the question, evidence, answer, and routing decision.

### Decide whether to search the notes

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-06 -->
```python
def decide_retrieval(state: RagState) -> dict:
    keywords = ["what", "how", "explain", "describe", "tell me"]
    needs_retrieval = any(word in state["question"].lower() for word in keywords)
    return {"needs_retrieval": needs_retrieval}

def should_retrieve(state: RagState) -> str:
    return "retrieve" if state["needs_retrieval"] else "generate"
```

**What happens here**

The first function updates the decision flag. The second reads that flag and returns a route name. A greeting such as Hello skips retrieval; a question beginning with How takes the retrieval path. This rule is deliberately limited: it can miss a question phrased differently and can retrieve for an unrelated question.

**Result:** We can see which branch runs without hiding the decision inside a model call.

### Retrieve the relevant documents

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-07 -->
```python
def retrieve_documents(state: RagState) -> dict:
    return {"documents": retriever.invoke(state["question"])}
```

**What happens here**

The retriever searches using the question and returns Documents. It does not generate an answer. Its partial return replaces the documents field while leaving the question and routing flag intact.

**Result:** The generation node can read the retrieved text from state.

### Prepare readable context with source labels

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-08 -->
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

### Generate from context or answer directly

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-09 -->
```python
def generate_answer(state: RagState) -> dict:
    if state["needs_retrieval"]:
        instruction = (
            "Use only the context. If it is insufficient, say you could not find the answer. "
            "Cite source labels in brackets.\nContext:\n" + format_context(state["documents"])
        )
    else:
        instruction = "Reply briefly to the user."
    reply = model.invoke([
        SystemMessage(instruction), HumanMessage(state["question"]),
    ])
    return {"answer": reply.text}
```

**What happens here**

The retrieval branch supplies the selected text as context and asks for source labels. Even an empty retrieval result stays on this grounded branch; it does not silently turn into an unrestricted factual answer. The direct branch handles the greeting. The model reads the prompt we construct; it does not search the vector store itself.

**Result:** The answer is returned as one state update; retrieved Documents remain available for inspection.

### Register the three working nodes

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-10 -->
```python
builder = StateGraph(RagState)
builder.add_node("decide", decide_retrieval)
builder.add_node("retrieve", retrieve_documents)
builder.add_node("generate", generate_answer)
```

**What happens here**

The graph contains a decision step, a retrieval step, and an answer step. We keep the responsibilities separate so we can inspect what each part does.

**Result:** The nodes are registered; they have not run.

### Connect the retrieval branch

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-11 -->
```python
builder.add_edge(START, "decide")
builder.add_conditional_edges(
    "decide", should_retrieve,
    {"retrieve": "retrieve", "generate": "generate"},
)
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
graph = builder.compile()
```

**What happens here**

After deciding, we either retrieve and then generate, or go straight to generation. Both paths end after the answer. This is a single retrieval pass, not the repeated model/tool loop from Part II.

**Result:** The graph makes the two possible paths explicit.

### Start each question with fresh state

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-12 -->
```python
def ask_question(question: str) -> RagState:
    return graph.invoke({
        "question": question, "documents": [],
        "answer": "", "needs_retrieval": False,
    })
```

**What happens here**

Each invocation starts with an empty document list and answer. Evidence from an earlier question is not accidentally reused. This graph has no checkpointer; separate calls are independent.

**Result:** We have a small helper for running either path.

### Inspect a retrieval question

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-13 -->
```python
result = ask_question("How does RAG use retrieved documents?")
print("Retrieved:", result["needs_retrieval"])
print("Sources:", [doc.metadata["source"] for doc in result["documents"]])
print("Answer:", result["answer"])
```

**What happens here**

How triggers retrieval. The printed source labels show which notes were selected; the Documents also contain their actual text. The answer wording can vary. Compare its claims with those returned notes instead of trusting a citation label alone.

**Result:** The retrieval flag is True, with up to two context documents and a generated reply.

### Try the direct path

<!-- snippet: code/Part III Give the model something to read/1-first-rag.ipynb#p3-1-step-14 -->
```python
greeting = ask_question("Hello!")
print("Retrieved:", greeting["needs_retrieval"])
print("Documents:", greeting["documents"])
print("Answer:", greeting["answer"])
```

**What happens here**

This input contains none of our retrieval keywords. The graph goes directly from decide to generate. The empty document list makes that difference visible.

**Result:** The flag is False and the document list is empty.

## Check your understanding

1. Which model searches and which model writes?
2. Are vectors or retrieved text sent as answer context?
3. What happens when our keyword rule misses a factual question?
4. Does a citation label prove the model used the source correctly?

## Where we go next

Next we will search longer files and resolve a follow-up such as Who helped him? using the conversation.

Complete notebook: [1-first-rag.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/1-first-rag.ipynb)

Further reading: [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
