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

## Embeddings: words become coordinates

Before we can search by meaning, we need a way to turn text into numbers.

**A vector** is a list of numbers. **An embedding** is a vector created by a model to represent a piece of text. Related meanings often produce similar vectors, which helps us find related passages even when the wording differs.

**Keep this in mind:** text → embedding model → list of numbers. We use the numbers to search, then return to the original text.

### Why use embeddings in the first place?

People can express the same idea with different words. You might ask, **“How do I change my password?”**, while a help document says, **“Reset your login credentials.”** A search that only matches exact words may miss that useful passage.

Embeddings help us search for **related meaning**, even when the wording is different. We turn both the question and the document passages into vectors. The application compares these vectors and selects the closest matches.

**Why numbers?** Numbers give the computer a way to calculate similarity and rank passages from a large collection. In RAG, this helps us choose useful text to send to the chat model instead of sending every document. We still check the selected text to see whether it answers the question.

### Imagine a two-dimensional world

Think of a chart with height on one axis and weight on the other. A person becomes a point with two coordinates, such as height 170 cm and weight 65 kg. People with a similar build appear near each other.

Text embeddings use the same general idea of representing something with coordinates, but in many more dimensions. The following diagrams use illustrative points; they are not measured embeddings from a trained model.

<!-- visual: embedding-basics -->

### How many dimensions does a vector have?

**Dimensions** means the number of coordinates in the vector. `[0.2, -0.5, 0.8]` has three dimensions. A vector with 1,536 numbers has 1,536 dimensions.

Different embedding models use different vector sizes. You may see 384, 768, 1,536, or 3,072 dimensions. More dimensions are not automatically better; the model and the retrieval task matter too.

Meaning has many patterns to learn, so two coordinates are usually not enough. But do not imagine that one coordinate is explicitly “topic” and another is “tone.” The model learns its representation, and individual coordinates usually do not have simple names we can read.

### Vector arithmetic: try a few examples

Classic word embeddings can capture relationships that show up in vector arithmetic. A familiar example is **king − man + woman ≈ queen**. The idea is to subtract one relationship and add another. Results from learned embeddings are approximate and depend on the model and vocabulary; this is not a rule every embedding model must follow. The [Word2Vec paper](https://arxiv.org/abs/1301.3781) explores these kinds of relationships.

Pick an equation below. We use small, handmade vectors so you can see every number being subtracted and added. The demo calculates the result and finds the closest point in its toy vocabulary.

<!-- visual: vector-arithmetic -->

### Why this matters for RAG

**For RAG, we do not need word arithmetic.**

We need one practical operation: **compare the question's vector with the passage vectors and find close matches.**

The useful idea is that we can work with meaning through numbers. Vector arithmetic illustrates relationships; vector similarity helps us search. After searching, we give the matching **text** to the chat model.

### See it in 2D — same idea, drawable

Click a relationship on the map. Notice how the two arrows have the same direction and length. In this illustration, the move from **france to paris** matches the move from **india to delhi**: country → capital.

The points are chosen for teaching. They are not real model vectors squeezed into two dimensions. A real embedding has many more coordinates, and drawing it in two dimensions can hide or distort relationships.

<!-- visual: vector-map -->

## Cosine similarity: compare directions

**Cosine similarity** is a score for comparing two vectors. In RAG, we can use it to compare the question's vector with each passage's vector.

Picture two arrows starting at the same point, like the hands of a clock. We compare **where they point**, not how long they are.

| If the arrows point… | The score is… |
|---|---|
| In the same direction | **1** |
| At a right angle to each other | **0** |
| In opposite directions | **−1** |

## Components of a RAG system

**A chunk** is a small piece of a document. We split long documents into chunks so we can search for a useful passage instead of sending the entire document to the model.

**An embedding model** turns text into a vector. That vector is called an **embedding**. We use the same embedding model for the document chunks and the question so their vectors can be compared.

**A vector store** keeps each chunk's text, vector, and source details together. This lets us search using vectors and get back the matching text. Chroma is the vector database we will use in the next lesson.

### How RAG works, step by step

First, we prepare the documents. Then, whenever a question arrives, we search the prepared collection and give the useful text to the chat model. Follow the numbered steps and connecting arrows in each phase.

<!-- visual: rag-flow -->

**Steps 1–4: prepare the documents.** Load the documents, split long ones into chunks, create a vector for each chunk, and store each vector with the text it came from. **Prepare once, query many times:** the saved document vectors can serve many questions. We update the collection when the documents or indexing setup change.

**Step 5: turn the question into a vector.** We usually embed the whole question as one piece of text. We do not split it into document-style chunks. Each new question gets its own vector. The original question is kept for the final prompt.

**Steps 6–7: search and retrieve.** Compare the question's vector with the stored chunk vectors. Select similar chunks, then return their original text and source details. A retriever is the helper that performs this search and returns the selected documents.

**Steps 8–9: build the prompt and answer.** Put the original question and retrieved text into a prompt. The chat model reads that prompt and writes an answer. It receives the **text**, not the vectors.

**The embedding model** creates the vectors for searching; **the LLM (chat model)** uses the retrieved text to write the answer.

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

## Chunking: cut the book into snippets

**Chunking** means splitting a long document into smaller passages before embedding it. A whole book may exceed an embedding model's input limit. Even when a document fits, one vector for many topics can make it harder to find the specific passage we need.

Think of pizza slices: a huge slice is hard to handle, while tiny crumbs lose what makes the slice useful. **Large chunks** can include too much unrelated text. **Very small chunks** can lose context, such as who “she” refers to or which instruction comes next.

### Four ways to cut the same text

| Strategy | How it chooses a boundary |
|---|---|
| Fixed size | Count characters or tokens, then cut. A boundary can land inside a word or sentence. |
| Recursive | Try larger boundaries first, then smaller ones when the text is still too long. |
| Semantic | Group nearby sentences by related meaning or changes in topic. |
| Structure-aware | Follow headings, sections, or other structure already in the document. |

In the demo, set the size to **80 characters** and compare **Fixed size** with **Recursive**. Then choose **Semantic** and **Structure-aware** to see topic groups and heading boundaries. Semantic grouping here uses a small set of topic keywords to illustrate the idea; it does not run an embedding model.

<!-- visual: chunking-demo -->

### Why repeat some text between chunks?

**Overlap** means the end of one chunk also appears at the start of the next. It can keep context around a boundary. In the fixed-size demo, increase overlap and look for the underlined repeated text. Notice that we store more characters because some words appear in multiple chunks.

Overlap can help, but it does not guarantee that every answer fits into one chunk. There is no single best chunk size or overlap for every document. Inspect the returned passages and adjust the settings. In Lesson 18, we will apply a real splitter to the fables PDF.

## Check your understanding

1. What is the difference between a vector and an embedding?
2. How many numbers does a 1,536-dimensional vector contain?
3. Why do the question and chunks use the same embedding model?
4. Does a high similarity score guarantee that a passage answers the question?
5. What is sent to the chat model: vectors or retrieved text?
6. What does the embedding model do, and what does the chat model do?
7. What can go wrong when chunks are too large or too small?
8. How does overlap change the text we store?

## Where we go next

In Lesson 18, we will load Classic_Fables_Collection.pdf, split it into chunks, save embeddings in Chroma, and inspect several searches with their scores.

Further reading: [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings) and [the Word2Vec paper](https://arxiv.org/abs/1301.3781).
