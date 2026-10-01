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

```text
Your application → LangChain → provider integration → model provider → model
```

---

## Connect with a model using LangChain

Open [2-Using-LangChain.ipynb](../../../Part%20I%20Understanding%20the%20Basics/2-Using-LangChain.ipynb). The important line is `init_chat_model`:

```python
from langchain.chat_models import init_chat_model

groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)

groq_response = groq_model.invoke("How many permutations are there for a deck of 52 cards?")
print(groq_response.text)
```

In this example, we name a model, tell LangChain which provider integration to use, and call `invoke`. The result is an AI message object, not only a string. It can include the generated text as well as useful metadata such as the model name and token usage.

```python
print(groq_response.response_metadata.get("model_name"))
print(groq_response.usage_metadata)
```

The direct provider SDK is still useful when you need a provider-specific feature. LangChain is useful when the common interface helps you write and maintain the application more easily.

---

## Invoke different models

Changing a model is now much simpler at the point where the model is created:

```python
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)

gemini_model = init_chat_model(
    "gemini-3.1-flash-lite-preview",
    model_provider="google_genai",
)

print(groq_model.invoke("Explain RAG in one sentence.").text)
print(gemini_model.invoke("Explain RAG in one sentence.").text)
```

The calling pattern stays familiar. That is the win. But changing the model is still an engineering decision: responses can differ in quality, speed, price, safety settings, available context, and supported features. Use the shared interface to experiment; use evaluation to decide what belongs in the application.

---

## Temperature: how much variation should we allow?

Temperature is a parameter that controls the randomness of a language model’s output. It influences how predictable or how varied the responses are.

Lower values make the model more likely to choose the most probable next tokens. Higher values let it explore less likely choices more often. It is not a “truth” dial and it cannot fix a weak prompt or missing context.

| Task | A sensible starting temperature | Why |
|---|---:|---|
| Factual answers, maths, code, extraction | 0.0–0.3 | Favour consistency and predictable formatting. |
| General questions and explanations | 0.5–0.7 | Balance clarity with natural variation. |
| Creative writing, stories, and jokes | 0.9–1.2 | Allow more diverse phrasing and ideas. |
| Wild brainstorming | 1.5+ | Encourage surprising directions; expect less consistency. |

For example:

```python
model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
    temperature=0.2,
)
```

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
