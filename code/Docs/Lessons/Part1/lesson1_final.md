# Lesson 1 — The First Signal

> **Review draft**
>
> This lesson is the entry point to the course. It should leave a learner feeling oriented and ready to write their first small AI program. It does not require prior AI, maths, or machine-learning knowledge.

## A note from me

Hi, and thanks for stopping by.

If you already work in AI or ML, I would value your feedback. For everyone else: things are changing fast. When was the last time you wrote a piece of code completely by hand? Every day brings news of another “revolutionary” model, another AI breakthrough, and another prediction that AI will make our jobs obsolete.

So let’s learn and adapt. Whether AI takes jobs, creates new ones, or simply changes the work we do, having a useful skill never hurts.

## Lesson purpose

This course is for developers who want to understand and use this shift rather than only watch it happen. We will build the code in this repository, starting with existing LLMs and chat models. We will get a feel for how they respond, then use the same building blocks to create applications. This lesson explains why that is now possible and gives us the vocabulary for the work ahead.

## What the learner will be able to do

By the end of this lesson, the learner can:

- explain why AI is visible everywhere now;
- distinguish AI, machine learning, deep learning, an LLM, and a chat model;
- describe the path from a prompt to a response;
- explain why this course begins with building rather than advanced mathematics; and
- prepare to run the first example in the repository.

---

## Optional story — A voice through the static

The professor switches on the workshop console. It answers immediately, sounding certain and helpful. Then it suggests a destination that does not exist.

“A voice is useful,” he says. “It is not a map.”

The machine can generate language. It still needs software around it to decide what question to ask, what information it may use, and what to do with its answer.

> This story is optional. Skip to the next section without losing any technical content.

---

## Why is AI suddenly everywhere?

AI is not new; it is more than seventy years old. For most of that time, it was a research-lab thing. Decades of progress mattered, but doing anything useful usually required a PhD, a university, expensive hardware, and years of work. Two shifts changed what developers can do with it.

| Period | What changed | Why it matters to a developer |
|---|---|---|
| 1950s–2000s | AI was mainly a research field. Progress was real, but systems were expensive, specialised, and difficult to use. | Building with AI usually required significant expertise, data, and computing resources. |
| 2017 | The Transformer architecture was introduced. It made it possible to train language models that could work with large amounts of text effectively. | This became a major foundation for modern systems such as GPT, Claude, Gemini, and many open-weight models. |
| 2022 onwards | Chat interfaces made language models easy for anyone to try. Providers then exposed APIs that developers could call from ordinary applications. | A developer can now add language capabilities without training a model from scratch. |
| Today → you | Major labs train the difficult foundation models. Developers can call them through an API in a few lines of code. | That is what this class is about: learning the stable application pattern before chasing every release. |

What once often required a team, months of work, and a serious data setup can now sometimes be prototyped by one person in an afternoon with an internet connection. Not every problem is that simple, but the drop in cost and friction is real. We are not training a frontier model from scratch; we are learning how developers like you and me can use its power in the software we build.


---

## The terms, without the fog

These words describe related ideas, but they are not interchangeable.

| Term | Plain-language meaning |
|---|---|
| **Artificial intelligence (AI)** | The broad field of making software perform tasks we associate with intelligence, such as recognising patterns, reasoning, planning, or working with language. |
| **Machine learning (ML)** | A way of creating some AI systems by learning patterns from data instead of writing every decision as a hand-written rule. |
| **Deep learning (DL)** | A family of machine-learning techniques that uses multi-layer neural networks. It has been especially effective for images, audio, and language. |
| **Large language model (LLM)** | A deep-learning model trained to work with language. Given the context it receives, it generates likely and useful next pieces of text. |
| **Chat model** | An LLM exposed through a conversation interface. It usually accepts messages with roles such as system, user, and assistant. |
| **AI application** | The complete product that uses a model: UI, prompts, data access, tools, validation, logging, and response handling. |


## How do I start?

Just follow along. We will build the code in this repository, begin with existing LLMs and chat models, get a feel for how they respond, and then build applications with them. The early goal is to build intuition:

1. Send a short request to an LLM.
2. Read the response and its metadata.
3. Change the prompt and observe what changes.
4. Try a different provider or model.
5. Build small applications around the same request-and-response loop.

The first notebook for this journey is [1-Connecting-to-an-LLM.ipynb](../../../Part%20I%20Understanding%20the%20Basics/1-Connecting-to-an-LLM.ipynb). It connects directly to Groq and Gemini. The next notebook, [2-Using-LangChain.ipynb](../../../Part%20I%20Understanding%20the%20Basics/2-Using-LangChain.ipynb), shows how LangChain gives different providers a similar calling interface.

For now, success means something modest but valuable: you can ask a model a question, receive a response, and understand which part of the system did what.

---

## Why start with building instead of mathematics?

Statistics, probability, linear algebra, and optimisation matter if you want to understand how models are trained or build new models. But instead of diving straight into all of that, let’s get our feet wet first and understand how developers like you and me can use and harness AI in real applications.

---

## What is an LLM?

LLM stands for **large language model**. Strip away the hype and it does one thing unbelievably well: it predicts the next token from the context it receives. A token is a small unit of text; it may be a whole word, part of a word, punctuation, or whitespace.

That simple mechanism can produce many useful behaviours:

- answering questions;
- rewriting text;
- summarising a passage;
- extracting fields from text;
- generating code; and
- continuing a conversation.

It is important to keep the limit in view: fluent output is not proof of truth. An LLM can give a helpful answer, make a mistake, or confidently invent a detail. We will learn how an application reduces those risks in later lessons.

---

## What is a chat model?

A chat model is an LLM designed for conversational use cases. Instead of only supplying one string of text, an application usually sends a sequence of messages with different roles. Depending on the provider and model, it can also accept images or other media alongside text.

### Read the message roles

<!-- snippet: code/Docs/Lessons/Part1/lesson1_final.md#supplement -->
```text
System message: sets the assistant's behaviour or rules
User message: asks for help
Assistant message: records a previous model response
```

**What happens here**

The system message carries the assistant's instructions. The user message carries the request, and the assistant message carries the reply. This is a conceptual example rather than executable code.

**Result:** The conversation has explicit roles.

Chat models may support features such as text and image input, tool calling, structured output, streaming, and conversation history. Support varies by model and provider, so a feature should always be checked in the provider documentation.

The word “chat” does not mean the model remembers everything forever. The model only receives the messages and other context your application includes in the current call. Long-term memory, private-data access, and tool execution are application features we design around the model, not automatic chat-model powers.

---

## Next lesson

Set up the local project, keep API keys out of the code, connect to Groq and Gemini, and inspect the response returned by each provider.
