# Part III · Lesson 3 — Let a follow-up keep its meaning

## What we are building

We are building a **story assistant that understands follow-up questions**, using the supplied fables. We can ask, “What happened to the grasshopper in winter?” and then, “Who helped him?” The assistant should understand that “him” means the grasshopper and search the right story.

We will store the story chunks in **Chroma**, a vector database that saves our searchable collection to disk. We will search those chunks for each question and keep the conversation as messages.

### The idea behind it

In Lesson 18, we searched using the user's question directly. A follow-up such as “Who helped him?” is missing the name the search needs. Here, we give the model the earlier conversation first and ask it to rewrite the follow-up as a complete search question: for example, “Who helped the grasshopper in winter?”

**A standalone question** makes sense without reading earlier messages. We use that rewritten question to retrieve story text, then ask the model to answer the user's original question using that text. Finally, we save the new question and answer in history so the next follow-up has context too.

Our flow is **history + question → rewrite → retrieve from Chroma → answer → save history**. It builds on the sequential steps and message history we already learned. History tells us what the user means; the retrieved story supplies the facts for the answer.

Chroma saves the searchable stories on disk. The conversation history is a separate Python list in this example. Saving one does not automatically save the other.

The reference shows manual prompts, templates, and older chain helpers. We will keep one clear version using ChatPromptTemplate and MessagesPlaceholder. It lets us see the work without teaching three wrappers for the same flow.

Live runs need GROQ_API_KEY and OPENAI_API_KEY. Run the notebook from its directory; uv sync from the code project installs its dependencies, including langchain-chroma. The embedding model is used for indexing and search, and Groq writes the rewrite and answer. Local Chroma needs no separate database service or Chroma API key.

### Import the document and model helpers

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-01 -->
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

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-02 -->
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

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-03 -->
```python
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Run this notebook with its own directory as the working directory.
data_dir = Path("../doc/smallStories")
text_files = sorted(data_dir.glob("*.txt"))
print("Files:", len(text_files))
```

**What happens here**

We use the text companions supplied alongside your PDFs. This lets us focus on retrieval rather than PDF extraction. The relative path points from this notebook's folder to code/doc/smallStories. These are the actual fables used by the example.

**Result:** The source filenames are listed in a predictable order.

### Keep text and source together

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-04 -->
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

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-05 -->
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

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-06 -->
```python
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    ids=[chunk.metadata["chunk_id"] for chunk in chunks],
    collection_name="fables",
    persist_directory="./chroma_db",
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

**What happens here**

Chroma embeds the chunks and saves their text, vectors, and metadata in the fables collection inside ./chroma_db. The IDs come from chunk_id, so rerunning this cell with the unchanged notes updates the same entries instead of adding duplicates. It still makes embedding requests. The retriever embeds a question with the same model and selects up to three similar chunks. A search hit is a candidate, not proof that the question is answered.

**Result:** We can retrieve Documents by meaning without rebuilding the index for every question.

### Reopen the saved collection

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-06-reopen -->
```python
vector_store = Chroma(
    collection_name="fables",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

**What happens here**

Chroma opens the existing fables collection from the same folder. This cell also works after restarting the kernel and rerunning the imports and embedding-model setup. Opening the collection does not embed its saved documents again. Searching still embeds each new question, so we use the same embedding model that created the stored vectors. After a restart, skip the previous indexing cell if the saved collection is already ready.

**Result:** The retriever searches the saved collection without re-indexing the source documents.

### Prepare readable context with source labels

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-07 -->
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

### Keep the conversation as typed messages

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-08 -->
```python
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

chat_history = []
```

**What happens here**

We keep earlier HumanMessage and AIMessage objects in a list. MessagesPlaceholder will insert that list into a prompt without flattening the roles into one text blob. This list belongs to this notebook session.

**Result:** We have an initially empty conversation and reusable prompt helpers.

### Describe the question-rewriting job

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-09 -->
```python
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", "Rewrite the latest question so it makes sense alone. "
     "Use the history to resolve references. Do not answer it. Return only the question."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
```

**What happens here**

The model sees earlier messages and the latest question. Its job here is to replace a reference such as him with the relevant character. We ask for only the question because a generated answer would be the wrong thing to search for.

**Result:** The template expects history and question values.

### Rewrite only when there is earlier history

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-10 -->
```python
def contextualize_question(question: str) -> str:
    if not chat_history:
        return question
    prompt = rewrite_prompt.invoke({"history": chat_history, "question": question})
    return model.invoke(prompt).text.strip()
```

**What happens here**

The first turn is already standalone, so we avoid an unnecessary rewrite call. Later turns use the saved conversation. A rewritten question can still be wrong; returning it in the final result helps us inspect that step.

**Result:** The retriever will receive a question that includes the missing reference.

### Describe the answering job separately

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-11 -->
```python
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "Use only the context for factual claims. History helps resolve references. "
     "If the context is insufficient, say you could not find the answer. "
     "Cite filenames in brackets.\nContext:\n{context}"),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
```

**What happens here**

This prompt has a different job: answer from the retrieved story text. History helps the conversation make sense, but an earlier model reply is not a source document. We ask the model to acknowledge missing evidence rather than complete the story from its general knowledge.

**Result:** The answer prompt expects context as well as history and question.

### Run and store one conversation turn

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-12 -->
```python
def ask_conversational_rag(question: str) -> dict:
    standalone_question = contextualize_question(question)
    retrieved_documents = retriever.invoke(standalone_question)
    prompt = answer_prompt.invoke({
        "history": chat_history, "question": question,
        "context": format_context(retrieved_documents),
    })
    answer = model.invoke(prompt).text
    chat_history.extend([HumanMessage(question), AIMessage(answer)])
    return {
        "question": question, "standalone_question": standalone_question,
        "answer": answer, "documents": retrieved_documents,
    }
```

**What happens here**

We search with the standalone question while answering the user's original wording. Only after generation do we store the user question and reply. The four returned fields let us inspect the original input, search input, answer, and evidence together.

**Result:** A completed turn adds exactly two messages to history.

### Ask the first question

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-13 -->
```python
first_turn = ask_conversational_rag("What happened to the grasshopper in winter?")
print("Search question:", first_turn["standalone_question"])
print("Answer:", first_turn["answer"])
```

**What happens here**

There is no earlier history, so the search question is unchanged. The source story describes the hungry grasshopper visiting the ant in winter. Inspect the returned Documents to see the passage used; the exact generated wording varies.

**Result:** The first question and answer are saved in history.

### Ask a question that needs the previous turn

<!-- snippet: code/Part III Give the model something to read/3-conversational-rag.ipynb#p3-2-step-14 -->
```python
second_turn = ask_conversational_rag("Who helped him?")
print("Original:", second_turn["question"])
print("Search question:", second_turn["standalone_question"])
print("Sources:", [doc.metadata["source"] for doc in second_turn["documents"]])
print("Answer:", second_turn["answer"])
print("History messages:", len(chat_history))
```

**What happens here**

The rewrite should identify the grasshopper. For example, Who helped the grasshopper in winter? is a useful search question; it is illustrative, not a guaranteed string. We now have four history messages. The supplied story names the ant as the helper.

**Result:** The original short follow-up remains visible beside the expanded search question and retrieved evidence.

## What did memory change?

It changed the query we sent to retrieval. We did not add every old message to the vector index, and we did not retrain either model. Our application used conversational context to choose a better search input.

Restarting the kernel clears chat_history, but the Chroma index stays on disk. Saving source documents is different from saving the conversation: reopen the collection to search the stories again, and save or restore chat history separately if you want to continue the same conversation. Longer conversations also need a deliberate history policy; sending everything forever uses more input tokens. We keep that concern separate from this small example.

## Check your understanding

1. Why rewrite before searching?
2. Why does the first turn skip the rewrite call?
3. Which question is stored in history?
4. Why are earlier model answers different from source evidence?

## Where we go next

Next we will combine meaning-based retrieval with keyword matching for an exact product error code.

Complete notebook: [3-conversational-rag.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/3-conversational-rag.ipynb)

Further reading: [LangChain Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma), [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
