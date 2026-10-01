# Lesson 4 — Read the Response, Shape the Prompt

> **Review draft**
>
> This lesson moves past printing model text. We inspect the whole response, understand why tokens matter, and make prompts reusable without turning them into a fragile collection of f-strings.

## A note from me

We made a model call. It answered. Nice. But an application needs more than `print(response.text)`.

We need to know which model answered, how much text went in and came out, and how to give the model a consistent instruction as our application grows. This is where the response object and prompts start doing real work for us.

## What you will be able to do

- inspect generated text, model metadata, and token usage;
- explain why models use tokens instead of plain strings;
- distinguish a static prompt from a dynamic prompt; and
- use a `PromptTemplate` to reuse and validate prompt variables.

---

## Understand the response

A call through LangChain returns an AI message object. The text is the part we usually show a user, but it is not the only useful part.

```python
response = groq_model.invoke("Explain what an API key is in one sentence.")

print(response.text)
print(response.response_metadata.get("model_name"))
print(response.usage_metadata)
```

The metadata can tell us which model actually responded. Usage metadata can report input, output, and total tokens. Providers do not all report exactly the same fields, so use `.get(...)` or a fallback when reading optional metadata.

Follow the complete example in [3-Responses-and-Prompts.ipynb](../../../Part%20I%20Understanding%20the%20Basics/3-Responses-and-Prompts.ipynb).

---

## Tokens: what are they?

Before a model can work with text, it breaks that text into **tokens**. A token is a small piece of text. It can be a whole word, part of a word, punctuation, a space, or even a line break.

For example, the sentence below is one Python string to us:

```text
I love building AI apps!
```

The model may see it more like this:

```text
"I" | " love" | " building" | " AI" | " apps" | "!"
```

That is only an illustration. The exact token split changes from one model to another. The important point is that **a word is not always one token**. Long words may become several tokens, and a space often belongs to the token after it.

### Why do models use tokens instead of words or strings?

Models need a fixed set of small pieces that they can turn into numbers and work with consistently. Whole strings are too open-ended: there are endlessly many possible sentences, names, URLs, spelling mistakes, and made-up words. Whole words are also awkward because a model would need to know every word in every language before it could read a sentence.

Tokens are the practical middle ground. They are small enough to handle a new or unusual word by splitting it into pieces, but large enough that the model does not have to process every character one at a time. That is why we write strings in Python, while the model internally reads and generates tokens.

### Why should an application developer care?

Every request has two sides:

```text
your instructions + user input + context  →  input tokens
model answer                             →  output tokens
```

You are normally charged for **both** incoming and outgoing tokens: the input you give the model and the output you receive from it. More tokens also usually mean more time and more pressure on the model’s context limit.

You do not need to count every token by hand. You do need to notice when a prompt, conversation history, or retrieved document is getting large. Token usage is one of the first signals that an application needs better context management.

## What does the model name mean?

Look again at the model setup we use in this course:

```python
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)
```

There are three different names here, and they mean different things:

| Name | What it means |
|---|---|
| `groq_model` | Our Python variable name. We chose it so a reader knows this object talks to Groq. You could call it `model`, but the more specific name is easier to follow. |
| `model_provider="groq"` | The provider integration LangChain uses to send the request. Groq hosts the API endpoint we call. |
| `"openai/gpt-oss-120b"` | The exact model identifier we ask Groq to run. It distinguishes this model from the other models Groq may offer. |

The identifier is like ordering a specific item from a menu. `Groq` is the restaurant serving it; `openai/gpt-oss-120b` is the item we selected. The provider, the model family, and the particular model variant all affect what the application can do.

### What does `120b` mean?

The `b` means **billion**. In `gpt-oss-120b`, `120b` is the rounded size label for a model with roughly 120 billion **parameters**. Parameters are the learned numbers inside a model: during training, the model adjusts them to capture patterns in language, code, and other data.

It is included in the name to distinguish this model from smaller variants, such as `gpt-oss-20b`. It gives developers a quick hint about the model family and scale when choosing a model to host or compare. A larger parameter count can mean more capacity to represent learned patterns, but it does **not** automatically mean a better answer for every task.

There is one extra detail here: this model uses a mixture-of-experts design. Its name is a rounded total-size label; not all of those parameters are used for every token it generates. That is why parameter count is useful context, not a direct prediction of speed, cost, or quality.

When we call this model through Groq, our laptop is not downloading or loading 120 billion parameters. Groq hosts the model and performs the computation. We only send the request and receive the response through the API.

Two models can give different answers to the same prompt because they may differ in training, speed, context size, tool support, safety behaviour, and price.

Record the name returned in the response metadata when you test an application. “The model gave a strange answer” is difficult to investigate; “this prompt behaved differently on this model through this provider” is useful information.

---

## What is a prompt?

A prompt is everything we provide to guide a model’s response: instructions, a question, examples, formatting requirements, and any context we include. In a chat application, the prompt can be spread across system, user, and previous assistant messages.

A **static prompt** stays fixed:

```python
static_prompt = "Explain RAG in one sentence."
```

A **dynamic prompt** adds values known only while the application is running:

```python
question = "What is the difference between an LLM and a chat model?"
dynamic_prompt = f"Answer this question for a beginner developer: {question}"
```

Dynamic prompts are how an application personalises an answer, inserts a user question, or supplies retrieved information. They are also where string-building gets messy surprisingly quickly.

---

## Use a prompt template

You can absolutely build a prompt with a normal Python string or an f-string. For a one-off prompt, that is often the simplest thing to do. `PromptTemplate` becomes useful when the same prompt appears in several places or needs a clearer contract for its values.

```python
from langchain_core.prompts import PromptTemplate

explanation_template = PromptTemplate.from_template(
    "Explain {topic} to a {audience} in no more than {sentence_count} sentences."
)

formatted_prompt = explanation_template.invoke(
    {
        "topic": "tokens",
        "audience": "beginner Python developer",
        "sentence_count": 2,
    }
)
```

It is not magic prompt engineering. It is useful validation and reuse. If we forget `audience` or `sentence_count`, the template raises an error before we make a model call. With a plain f-string, we may not notice the missing value until later, or we may accidentally build a different prompt in another file.

The template can also live outside the Python file. In the notebook, we save the template as JSON and load it again:

```python
from pathlib import Path
from langchain_core.load import dumps, loads

template_path = Path("prompts/explanation_template.json")
template_path.parent.mkdir(exist_ok=True)
template_path.write_text(dumps(explanation_template, pretty=True), encoding="utf-8")

loaded_template = loads(
    template_path.read_text(encoding="utf-8"),
    valid_namespaces=["langchain_core"],
)
```

That gives us a reusable prompt file that another part of the application can load. Later, it also gives us a clean place to review, test, or change prompt wording without mixing it into every Python function.

## Check your understanding

1. What can you learn from response metadata that you cannot learn from `response.text` alone?
2. Why might a long conversation become expensive or fail?
3. When is a dynamic prompt more useful than a static prompt?
4. What problem does `PromptTemplate` solve?

## Next lesson

We will work with chat messages, stream responses as they arrive, batch independent requests, and see what “memory” really means in an application.
