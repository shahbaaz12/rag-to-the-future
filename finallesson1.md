# Lesson 1 — Is Anybody There?

**Part I: Out of Time**  
**Workshop log:** The First Signal  
**Learning focus:** AI foundations, LLM applications, chat models, and a safe local setup.

## Mission

The workshop console speaks for the first time. Its answer is fluent, but it confidently describes a destination that does not exist.

The professor points at the wiring:

> “A voice is useful. It is not a map.”

Your first repair is not to make the machine clever. It is to understand the smallest useful AI application: a request goes in, a language model responds, and your software decides what happens next.

## By the end of this lesson, you can

- Explain the difference between AI, machine learning, deep learning, and an LLM.
- Describe the request-and-response loop of a simple LLM application.
- Explain the difference between an LLM and a chat model.
- State what an LLM does *not* know or control by default.
- Set up a small local project without exposing an API key.

## Why AI feels like it is changing so quickly

AI is not one moving target. Research, model releases, provider APIs, developer libraries, and products all evolve at different speeds. You do not need to chase every release to begin.

Start with the stable shape underneath the tools:

```text
User question → application code → model provider → model response → application code
```

The model generates a response. Your application owns the prompt, credentials, error handling, private-data access, validation, and what the user sees next.

## The vocabulary

| Term | Meaning in this course |
|---|---|
| **Artificial intelligence (AI)** | The broad field of making software perform tasks associated with intelligence, such as perception, reasoning, planning, or language. |
| **Machine learning (ML)** | A way to build some AI systems by learning patterns from data instead of writing every rule by hand. |
| **Deep learning (DL)** | A family of ML methods based on multi-layer neural networks. It is often effective for images, audio, and language. |
| **Large language model (LLM)** | A deep-learning model that works with language. Given context, it predicts useful next pieces of text. |
| **Chat model** | An LLM exposed through a conversation interface, usually using messages and roles such as system, user, and assistant. |
| **AI application** | The normal software around the model: UI, inputs, data, tools, checks, and output handling. |

These terms overlap, but they are not interchangeable. An LLM is one kind of model; an AI application is the full product that uses it.

## The first circuit: one visible round trip

An LLM application can be understood as a small circuit:

1. A person asks for help.
2. Your application prepares the request, including instructions and credentials.
3. A model provider runs an LLM.
4. Your application receives, displays, and possibly checks the response.

Starting with one visible round trip keeps failures understandable. If the answer is poor, inspect the request and response. If the request fails, inspect the credentials, model identifier, and provider settings. Do not add memory, retrieval, tools, or agents until this loop works.

## LLM versus chat model

An **LLM** is the language engine. It can be used for tasks such as completion, extraction, classification, summarization, and generating an answer.

A **chat model** is an LLM presented through a conversational interface. It is useful when an application needs instructions and a user conversation.

Neither one automatically has:

- Permanent memory of earlier conversations.
- Access to private documents or a current database.
- Permission to perform actions in other systems.
- Proof that its answer is factual or correct.

Those are application responsibilities. The later repairs in this journey add memory, retrieval, validation, and controlled actions deliberately.

## Workshop setup

Create a small Python project and add only the packages needed for the first model experiments:

```bash
uv init rag-study-assistant
cd rag-study-assistant
uv add langchain langchain-groq langchain-google-genai python-dotenv
```

`uv` records dependencies in `pyproject.toml` and locks them in `uv.lock`. If a platform specifically requires `requirements.txt`, generate it rather than maintaining a duplicate list:

```bash
uv export --format requirements-txt --output-file requirements.txt
```

### Keep credentials local

Create a `.env` file beside your code and keep it out of Git:

```text
# .env — never commit this file
GROQ_API_KEY=your_key_here
# or
GOOGLE_API_KEY=your_key_here
```

```text
# .gitignore
.env
```

Never paste a real API key into source code, a notebook, terminal output, a screenshot, or this repository. If a key is exposed, revoke it in the provider console and create a replacement.

## Practice task

Create a Python file that:

1. Loads a provider key from `.env`.
2. Creates either a Groq or Gemini chat model.
3. Sends this message: `Explain HTTP to a beginner in three sentences.`
4. Prints the returned text.
5. Runs the same request again and records one similarity and one difference.

For this first exercise, the application should either print a response or show a clear request error. It does not need conversation history, private documents, tools, or factual verification yet.

## Completion check

You have completed the first repair when you can answer these questions:

- What sits between a user and an LLM in a real application?
- Why is a fluent answer not proof that it is correct?
- What is the difference between an LLM and a chat model?
- Why must an API key stay outside source code?
- Why is a single request-and-response loop the right place to begin?

## Repair record

**Status: stabilized.**

You can now place an LLM inside an application, describe the limits of that model connection, and prepare a local project without exposing credentials.

**Next jump:** Lesson 2 — *Coordinates, Please*: connect a chat model and inspect the response it returns.

## References

- [uv project initialization](https://docs.astral.sh/uv/concepts/projects/init/)
- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Gemini API-key guide](https://ai.google.dev/gemini-api/docs/api-key)
- [LangChain ChatGroq integration](https://docs.langchain.com/oss/python/integrations/chat/groq)
- [LangChain ChatGoogleGenerativeAI integration](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)
