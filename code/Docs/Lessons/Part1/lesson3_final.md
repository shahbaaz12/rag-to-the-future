# Lesson 3 — One Interface, Many Models

> **Review draft**
>
> This lesson introduces LangChain as a practical convenience layer. The learner will connect to different chat models with the same broad pattern, then learn how temperature and output limits affect a response.

## A note from me

In the previous lesson, we made direct calls to providers. That is useful because it shows what is actually happening. But applications rarely stay with one provider, one model, or one calling style forever.

This lesson introduces a tool that makes that movement easier. It does not make every provider identical, and it does not remove the need to understand the model you chose. It gives us a cleaner place to start.

## What you will be able to do

By the end of this lesson, you can:

- explain what LangChain gives an application developer;
- create a chat model with `init_chat_model`;
- invoke Groq and Gemini models through the same broad interface;
- choose a useful temperature for a task; and
- control how much output a model may generate.

---

## So, what is LangChain?



LangChain is a convenient set of tools for connecting to LLMs and building applications around them. One of its most useful ideas is a provider-agnostic interface: you can use a similar piece of application code with different model providers.

That does not mean every provider supports the same models, parameters, tools, or response fields. It means LangChain gives us a common starting point for the things that are shared.

### Follow the request path

<!-- snippet: code/Docs/Lessons/Part1/lesson3_final.md#supplement -->
```text
Your application → LangChain → provider integration → model provider → model
```

**What happens here**

Our application uses LangChain's interface, which delegates to a provider integration. The provider hosts and runs the chosen model.

**Result:** The common interface sits between our code and the provider.

---

## Connect with a model using LangChain

Open [2-Using-LangChain.ipynb](../../../Part%20I%20Understanding%20the%20Basics/2-Using-LangChain.ipynb). The important line is `init_chat_model`:

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#5a374f7e -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
```

**What happens here**

These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.

**Result:** The imported names are ready for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#5a374f7e -->
```python
# Load provider API keys from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Create a Groq model

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#2366c03c -->
```python
# Create a Groq chat model. LangChain reads GROQ_API_KEY from .env.
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)
```

**What happens here**

`init_chat_model` creates the connection to our chosen hosted model through the Groq integration. LangChain reads the key loaded during setup.

**Result:** groq_model is ready to use.

### Ask the question

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#2366c03c -->
```python
# Invoke the model and keep the full AIMessage response.
groq_response = groq_model.invoke(
    "How many permutations are there for a deck of 52 cards?"
)
```

**What happens here**

`invoke` sends the question and waits for a complete reply. We store that reply in groq_response.

**Result:** groq_response is an AIMessage, with text and metadata.

In this example, we name a model, tell LangChain which provider integration to use, and call `invoke`. The result is an AI message object, not only a string. It can include the generated text as well as useful metadata such as the model name and token usage.

### Read text and metadata

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#2366c03c -->
```python
print(groq_response.text)
print("Model name:", groq_response.response_metadata.get("model_name"))
print("Token usage:", groq_response.usage_metadata)
```

**What happens here**

The first print shows the answer. The other two show the reported model name and token usage; `.get` handles a missing metadata key without an indexing error.

**Result:** We can inspect both the answer and information about the call.

The direct provider SDK is still useful when you need a provider-specific feature. LangChain is useful when the common interface helps you write and maintain the application more easily.

---

## Invoke different models

Changing a model is now much simpler at the point where the model is created:

### Create the Gemini model

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#c4e34a7a -->
```python
# Create a Gemini chat model. LangChain reads GEMINI_API_KEY from .env.
gemini_model = init_chat_model(
    "gemini-3.1-flash-lite-preview",  # Same invoke interface; the model identifier and provider change.
    model_provider="google_genai",
)
```

**What happens here**

We change the model identifier and provider integration. The invoke pattern stays familiar.

**Result:** gemini_model is ready. GEMINI_API_KEY must be available.

### Ask Gemini a question

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#c4e34a7a -->
```python
gemini_response = gemini_model.invoke("What happens to Humpty Dumpty?")
```

**What happens here**

We send the nursery-rhyme question through the same invoke method.

**Result:** gemini_response holds the model's reply.

### Inspect Gemini's reply

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#c4e34a7a -->
```python
print(gemini_response.text)
print("Model name:", gemini_response.response_metadata.get("model_name"))
print("Model provider:", gemini_response.response_metadata.get("model_provider"))
print("Token usage:", gemini_response.usage_metadata)
```

**What happens here**

We read the text, reported model and provider, and token usage using the same response properties.

**Result:** We can compare how the providers report their results.

The calling pattern stays familiar. That is the win. But changing the model is still an engineering decision: responses can differ in quality, speed, price, safety settings, available context, and supported features. Use the shared interface to experiment; use evaluation to decide what belongs in the application.

---

## Temperature: how much variation should we allow?

Temperature is a parameter that controls the randomness of a language model’s output. It influences how predictable or how varied the responses are.

Lower values make the model more likely to choose the most probable next tokens. Higher values let it explore less likely choices more often. It is not a “truth” dial and it cannot fix a weak prompt or missing context.

| Task | A sensible starting temperature | Why |
|---|---:|---|
| Factual answers, maths, code, extraction | 0.0–0.3 | Favor consistency and predictable formatting. |
| General questions and explanations | 0.5–0.7 | Balance clarity with natural variation. |
| Creative writing, stories, and jokes | 0.9–1.2 | Allow more diverse phrasing and ideas. |
| Wild brainstorming | 1.5+ | Encourage surprising directions; expect less consistency. |

For example:

### Keep the comparison prompt fixed

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#be396d66 -->
```python
# Use the same prompt to compare low and high temperature settings.
prompt = "Write a one-sentence opening line for a story about a goldfish."
groq_model_name = "openai/gpt-oss-120b"
```

**What happens here**

We use one goldfish prompt and one model name. That gives us a shared starting point for comparing temperature settings.

**Result:** Both calls below will receive the same prompt.

### Create the lower-temperature model

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#be396d66 -->
```python
low_temperature_model = init_chat_model(
    groq_model_name,
    model_provider="groq",
    temperature=0.0,
    max_tokens=300,
    reasoning_effort="low",
)
```

**What happens here**

We configure the first model with temperature 0.0, an output limit of 300 tokens, and low reasoning effort. Lower temperature favors more consistent token choices.

**Result:** low_temperature_model is ready for the shared prompt.

### Create the higher-temperature model

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#be396d66 -->
```python
high_temperature_model = init_chat_model(
    groq_model_name,
    model_provider="groq",
    temperature=2.0,
    max_tokens=300,
    reasoning_effort="low",
)
```

**What happens here**

We configure the same hosted model with temperature 2.0. The output limit and reasoning setting stay the same so we can compare the effect of temperature.

**Result:** high_temperature_model is ready for the same prompt.

### Compare their answers

<!-- snippet: code/Part I Understanding the Basics/2-Using-LangChain.ipynb#be396d66 -->
```python
print("Temperature 0.0:", low_temperature_model.invoke(prompt).text)
print("Temperature 2.0:", high_temperature_model.invoke(prompt).text)
```

**What happens here**

We invoke each object with the shared prompt and print the answers beside their temperature labels. These are two separate API calls.

**Result:** We can compare the generated openings. Temperature is not a guarantee of quality or correctness.

Start with the task, not with a fashionable number. If you need reliable structured output, start low. If you need ten different campaign ideas, raise it and review the results.

---

## Max tokens: how much may the model say?

Models generate output in tokens. `max_tokens` or a provider-specific equivalent limits the amount of output the model may produce in one response.

This matters for three practical reasons:

- **Cost:** more generated tokens usually cost more.
- **Speed:** longer answers generally take longer to generate.
- **Control:** a clear limit helps stop a short task from producing an essay.

Choose a limit that suits the result you need. A single classification label needs very little output. A detailed report or a long code explanation needs more. If the response is cut off, raise the limit or ask the model to produce a smaller, more focused answer.

The exact parameter name and accepted range can vary by provider, so check the integration documentation for the model you use.

## Next lesson

We will move beyond a single request and response: messages, prompt structure, and the context an application gives to a model.
