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

## Set up once

Run these snippets in order in the associated notebook. Later snippets reuse the objects created here.

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-1 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
```

**What happens here**

These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.

**Result:** The imported names are ready for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-1 -->
```python
# Load GROQ_API_KEY from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Choose the model and provider

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-1 -->
```python
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)
```

**What happens here**

`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.

**Result:** We can reuse this model object in the following snippets.

## Understand the response

A call through LangChain returns an AI message object. The text is the part we usually show a user, but it is not the only useful part.

### Make a request to inspect

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-3 -->
```python
response = groq_model.invoke("Tell me a joke about AI and humans.")
```

**What happens here**

We ask the model for a joke and keep its complete AIMessage response. Run the model setup above first.

**Result:** response holds the text and any metadata the provider reports.

### Read the response properties

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-3 -->
```python
print("Text:", response.text)
print()
print("Model name:", response.response_metadata.get("model_name"))
print("Model provider:", response.response_metadata.get("model_provider"))
print("Token usage:", response.usage_metadata)
```

**What happens here**

`response.text` gives readable text. response_metadata reports model details, and usage_metadata reports token counts when supplied by the integration.

**Result:** We can inspect the answer, its model, and its token usage.

### Handle missing usage information

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-5 -->
```python
usage = response.usage_metadata or {}
```

**What happens here**

`or {}` gives us an empty dictionary when the response has no usage metadata. This lets the next snippet use get safely.

**Result:** usage is a dictionary.

### Inspect incoming and outgoing tokens

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-5 -->
```python
# Input tokens are what we send; output tokens are what the model generates.
print("Input tokens:", usage.get("input_tokens", "not reported"))
print("Output tokens:", usage.get("output_tokens", "not reported"))
print("Total tokens:", usage.get("total_tokens", "not reported"))
```

**What happens here**

We read input, output, and total token counts separately. If a count is absent, the printed fallback says not reported.

**Result:** We can see which counts were supplied for this request.

### Record which model answered

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-5 -->
```python
# Record the provider and exact model when comparing behaviour or cost.
print("Provider:", response.response_metadata.get("model_provider"))
print("Model:", response.response_metadata.get("model_name"))
```

**What happens here**

We print the provider and reported model name so a later comparison can identify which configuration produced the answer.

**Result:** We have identifying information alongside the usage counts.

The metadata can tell us which model actually responded. Usage metadata can report input, output, and total tokens. Providers do not all report exactly the same fields, so use `.get(...)` or a fallback when reading optional metadata.

Follow the complete example in [3-Responses-and-Prompts.ipynb](../../../Part%20I%20Understanding%20the%20Basics/3-Responses-and-Prompts.ipynb).

---

## Tokens: what are they?

Before a model can work with text, it breaks that text into **tokens**. A token is a small piece of text. It can be a whole word, part of a word, punctuation, a space, or even a line break.

For example, the sentence below is one Python string to us:

### Start with a string

<!-- snippet: code/Docs/Lessons/Part1/lesson4_final.md#supplement -->
```text
I love building AI apps!
```

**What happens here**

To Python this whole sentence is one string. A model's tokenizer will divide it into smaller pieces before the model processes it.

**Result:** The string can contain several tokens.

The model may see it more like this:

### Picture the token pieces

<!-- snippet: code/Docs/Lessons/Part1/lesson4_final.md#supplement -->
```text
"I" | " love" | " building" | " AI" | " apps" | "!"
```

**What happens here**

This is an illustrative split into tokens, including spaces and punctuation. It is not output from a particular model's tokenizer.

**Result:** A word and a token are not always the same unit.

That is only an illustration. The exact token split changes from one model to another. The important point is that **a word is not always one token**. Long words may become several tokens, and a space often belongs to the token after it.

### Why do models use tokens instead of words or strings?

Models need a fixed set of small pieces that they can turn into numbers and work with consistently. Whole strings are too open-ended: there are endlessly many possible sentences, names, URLs, spelling mistakes, and made-up words. Whole words are also awkward because a model would need to know every word in every language before it could read a sentence.

Tokens are the practical middle ground. They are small enough to handle a new or unusual word by splitting it into pieces, but large enough that the model does not have to process every character one at a time. That is why we write strings in Python, while the model internally reads and generates tokens.

### Why should an application developer care?

Every request has two sides:

### Separate the two token counts

<!-- snippet: code/Docs/Lessons/Part1/lesson4_final.md#supplement -->
```text
your instructions + user input + context  →  input tokens
model answer                             →  output tokens
```

**What happens here**

Instructions, questions, and context become input tokens. The generated answer becomes output tokens.

**Result:** Both sides contribute to usage; the provider's pricing determines the charge.

You are normally charged for **both** incoming and outgoing tokens: the input you give the model and the output you receive from it. More tokens also usually mean more time and more pressure on the model’s context limit.

You do not need to count every token by hand. You do need to notice when a prompt, conversation history, or retrieved document is getting large. Token usage is one of the first signals that an application needs better context management.

## What does the model name mean?

Look again at the model setup we use in this course:

### Choose the model and provider

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-1 -->
```python
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)
```

**What happens here**

`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.

**Result:** We can reuse this model object in the following snippets.

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

### Send a static prompt

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-7 -->
```python
static_prompt = "Will Ash's Pikachu ever evolve ?"
print(groq_model.invoke(static_prompt, max_tokens=200).text)
```

**What happens here**

static_prompt is a fixed string. We send it directly and print the answer, with an output limit of 200 tokens.

**Result:** The model answers the Pikachu question.

A **dynamic prompt** adds values known only while the application is running:

### Build a prompt from a changing question

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#response-prompt-7 -->
```python
users_question = "How do you make a sandwich?"  # This is your user input, which can be dynamically changed at runtime.
dynamic_prompt = f"Answer this question like a comedian: {users_question}"  # simple string interpolation to create a dynamic prompt
print("Dynamic Prompt:")
print(groq_model.invoke(dynamic_prompt, max_tokens=200).text)
```

**What happens here**

The f-string inserts users_question into the instruction. We can replace the user question at runtime without rewriting the surrounding wording.

**Result:** The model receives the comedian instruction and the sandwich question together.

Dynamic prompts are how an application personalises an answer, inserts a user question, or supplies retrieved information. They are also where string-building gets messy surprisingly quickly.

---

## Use a prompt template

You can absolutely build a prompt with a normal Python string or an f-string. For a one-off prompt, that is often the simplest thing to do. `PromptTemplate` becomes useful when the same prompt appears in several places or needs a clearer contract for its values.

### Import PromptTemplate

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#fbe75c2c -->
```python
from langchain_core.prompts import PromptTemplate
```

**What happens here**

This helper describes a reusable prompt with named placeholders.

**Result:** PromptTemplate is available.

### Fill the question placeholder

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#fbe75c2c -->
```python
dynamic_question_template = PromptTemplate(
    template="Answer the question as a sarcastic teacher: {question}",
    input_variables=["question"],
)
question = "Why did jack and jill go up the hill?"  # This is your user input, which can be dynamically changed at runtime.
prompt = dynamic_question_template.invoke({"question": question})
```

**What happens here**

The template expects one value named question. We supply that value through invoke, which produces a prompt value. A missing question raises an error before we send the prompt to the model.

**Result:** prompt contains the filled-in teacher instruction and question.

### Send the filled prompt

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#fbe75c2c -->
```python
result = groq_model.invoke(prompt, max_tokens=200)
print(result.text)
```

**What happens here**

We pass the prompt value to groq_model.invoke, limit the output, and print the response text.

**Result:** The model answers using the reusable template.

### Keep reuse in mind

<!-- snippet: code/Part I Understanding the Basics/3-Responses-and-Prompts.ipynb#fbe75c2c -->
```python
# if requred we can save the above prompt template to a file and load it later for reuse. This is useful for maintaining consistency in prompts across different parts of an application or across different applications.
```

**What happens here**

This exact notebook comment points out that templates can be stored for reuse. It does not itself save a file. The supplementary JSON snippets below show that next step.

**Result:** No code runs here; this is a source comment.

It is not magic prompt engineering. It is useful validation and reuse. If we forget `question`, the template raises an error before we make a model call. An f-string can also fail when a Python variable is undefined. The template's advantage is an explicit set of named inputs and reusable wording.

The template can also live outside the Python file. The notebook mentions saving a template. These supplementary snippets extend that idea: we save the same template as JSON and load it again.

### Import the file and serialisation helpers

<!-- snippet: code/Docs/Lessons/Part1/lesson4_final.md#supplement -->
```python
from pathlib import Path
from langchain_core.load import dumps, loads
```

**What happens here**

Path handles the file location. dumps and loads convert the LangChain template to JSON and reconstruct it later.

**Result:** The helpers for the supplementary save-and-load example are ready.

### Save the reusable template

<!-- snippet: code/Docs/Lessons/Part1/lesson4_final.md#supplement -->
```python
template_path = Path("prompts/explanation_template.json")
template_path.parent.mkdir(exist_ok=True)
template_path.write_text(dumps(dynamic_question_template, pretty=True), encoding="utf-8")
```

**What happens here**

We choose a JSON path, create the prompts folder if needed, and write the existing dynamic_question_template. dumps serialises the template rather than sending a request to the model.

**Result:** The JSON file can be reused by another part of the application.

### Load the saved template

<!-- snippet: code/Docs/Lessons/Part1/lesson4_final.md#supplement -->
```python
loaded_template = loads(
    template_path.read_text(encoding="utf-8"),
    valid_namespaces=["langchain_core"],
)
```

**What happens here**

We read the JSON file and reconstruct its LangChain prompt template. Only load a template file you trust; the allowed namespace names the LangChain objects used here.

**Result:** loaded_template is ready for another question.

That gives us a reusable prompt file that another part of the application can load. Later, it also gives us a clean place to review, test, or change prompt wording without mixing it into every Python function.

## Check your understanding

1. What can you learn from response metadata that you cannot learn from `response.text` alone?
2. Why might a long conversation become expensive or fail?
3. When is a dynamic prompt more useful than a static prompt?
4. What problem does `PromptTemplate` solve?

## Next lesson

We will work with chat messages, stream responses as they arrive, batch independent requests, and see what “memory” really means in an application.
