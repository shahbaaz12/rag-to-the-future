# Lesson 5 — More Than One Answer

> **Review draft**
>
> A model can return text in several useful ways, return structured data instead of prose, and take part in a conversation. This lesson explains those features and shows how an application keeps long conversation history manageable.

## A note from me

Up to now, our model call has looked very simple: send one input, receive one answer, print it. That is useful, but it is only the beginning.

What if we want the answer to appear word by word? What if we have a hundred unrelated requests? What if our Python code needs a list or an object instead of a paragraph? And what happens when a conversation becomes too long to send again and again?

Let’s add those pieces one at a time.

## What you will be able to do

- stream a response as it is generated;
- batch independent requests;
- ask for validated structured output;
- use system, human, and AI messages;
- distinguish history from memory; and
- use summarisation middleware to control a growing conversation.

---

## What else can we do with a model call?

### Streaming

Normally, `invoke` waits until the complete response is ready. Streaming lets our application receive small chunks while the model is still generating.

```python
for chunk in groq_model.stream("Explain API-key safety in three sentences."):
    print(chunk.text, end="", flush=True)
```

It makes a long answer feel more responsive because the user can start reading it sooner. The model is still generating the same kind of response; streaming only changes how our application receives it.

### Batching

Batching is for requests that do not depend on one another.

```python
batch_responses = groq_model.batch([
    "Define an LLM in one sentence.",
    "Give one use for a low temperature setting.",
])
```

It is useful when processing a list of records, prompts, or tests. It is not conversation memory, and it does not make dependent tasks safe to run at the same time.

---

## Structured output: ask for data, not just prose

Models are very good at writing natural language. Applications often need something more precise: a Python object, a list of items, fields we can place in a database, or data we can show in a UI.

For example, imagine we ask a model what lesson a learner should take next. A paragraph is readable, but it is awkward for code that needs a lesson number, topic, reason, and preparation steps. We can describe that exact structure with a Pydantic model:

```python
class LessonRecommendation(BaseModel):
    lesson_number: int
    topic: str
    reason: str
    preparation: list[str]
```

Then we ask LangChain for that structure:

```python
structured_groq_model = groq_model.with_structured_output(LessonRecommendation)
recommendation = structured_groq_model.invoke("Recommend the next lesson for a learner.")

print(recommendation.topic)
```

The result is a `LessonRecommendation` object, so our code can use `recommendation.lesson_number` or loop over `recommendation.preparation`. The schema also validates the result before it reaches the rest of our application.

Structured output does not make a model’s facts automatically correct. It gives the response a predictable shape. We still need good instructions and, when facts matter, trustworthy data and validation.

The full structured-output example is in [5-Structured-Outputs-and-Middleware.ipynb](../../../Part%20I%20Understanding%20the%20Basics/5-Structured-Outputs-and-Middleware.ipynb).

---

## Messages give a conversation structure

A message is just **text plus a label saying who said it**.

```python
HumanMessage("How do I create a REST API?")
# label: human, text: "How do I create a REST API?"
```

Why bother with the label? So the model can tell which text is a rule and which text is a question.

**Without labels**, we send one string:

```python
groq_model.invoke("Be concise. Always show code. How do I create a REST API?")
```

The model sees one blob of text. It cannot reliably separate our instruction from the user’s actual question.

**With labels**, we give the model the structure:

```python
groq_model.invoke([
    SystemMessage("Be concise. Always show code."),  # rules
    HumanMessage("How do I create a REST API?"),     # question
])
```

Now the model can treat the system message as “this is how I should behave” and the human message as “this is what the user wants.”

Think of a new employee. The **system message** is the manager’s day-one rule: “Be polite and keep replies short.” The **human message** is a customer’s question. The employee follows the manager’s rules for every customer without making the customer repeat them.

Messages also let us carry a chat history forward by adding an `AIMessage` for an earlier reply:

```python
conversation = [
    SystemMessage("Be concise."),
    HumanMessage("What is Python?"),
    AIMessage("A programming language."),  # earlier model reply
    HumanMessage("Who created it?"),        # “it” means Python
]
```

Without the earlier messages, the model would not know what “it” means. Labels do not guarantee perfect behaviour, but they give the application and model a clear, reliable conversation structure.

---

## History and memory

**History** is the collection of earlier messages in a conversation. **Memory** is the method our application uses to decide what information from that history should be available on the next turn.

For a small demo, a Python list is enough:

```python
conversation = [
    SystemMessage("You are a concise assistant for a Python course."),
    HumanMessage("My name is Ada. I am learning about LLMs."),
]

first_response = groq_model.invoke(conversation)
conversation.append(first_response)
conversation.append(HumanMessage("What is my name and what am I learning?"))

second_response = groq_model.invoke(conversation)
```

The model remembers Ada only because the application sends the earlier messages again. The model does not hold a permanent personal memory between API calls.

This history grows with every turn. More history means more input tokens, more cost, more latency, and eventually a context limit. We need a rule for what to keep.

---

## Summarisation and middleware

One useful rule is: keep the recent messages in full, and replace older messages with a summary. The summary should preserve the important context while using fewer tokens.

**Middleware** is code that runs around a model or agent operation. In the supplied LangChain example, `SummarizationMiddleware` watches the conversation length, creates a summary after a chosen threshold, and keeps only a recent set of messages alongside that summary.

```python
SummarizationMiddleware(
    model="groq:openai/gpt-oss-120b",
    trigger=("messages", 10),
    keep=("messages", 4),
)
```

Here, `trigger` says when summarisation should happen, and `keep` says how many of the newest messages stay in full. A checkpointer, identified by a thread ID, stores the conversation between calls. We will meet agents properly in Lesson 7; for now, focus on the history-management idea.

Summaries are useful but imperfect. A summary can lose a detail or distort a decision, so choose carefully what needs to stay in full history and what can be compressed.

For the streaming, batching, messages, and short-term-memory examples, use [4-Messages-Streaming-Batching-and-Memory.ipynb](../../../Part%20I%20Understanding%20the%20Basics/4-Messages-Streaming-Batching-and-Memory.ipynb).

## Check your understanding

1. When would streaming improve a user’s experience?
2. Why is batching unsuitable for a conversation where each answer affects the next question?
3. What does structured output give an application that free-form text does not?
4. What is the difference between message history and memory?
5. Why might an application summarise old conversation messages?

## Next lesson

We will let a model request a tool, then see why the application must control every tool execution.
