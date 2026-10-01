# Part I — Draft Content for Lessons 1 and 2

This is the teaching-content draft for the first two lesson pages. It is based on the supplied notebooks:

- [1-Connecting-to-an-LLM.ipynb](../../../Part%20I%20Understanding%20the%20Basics/1-Connecting-to-an-LLM.ipynb)
- [2-Using-LangChain.ipynb](../../../Part%20I%20Understanding%20the%20Basics/2-Using-LangChain.ipynb)

Keep the three layers separate on the final pages:

1. **Optional story:** a short workshop scene that gives the learner a reason to care.
2. **Explanation:** plain-language concepts that stand on their own.
3. **Code walkthrough:** the existing notebook code, broken into small snippets with an explanation after each one.

The story should be removable without changing the explanation or code exercise.

## Shared setup for both lessons

### Goal

Create a small Python project, store credentials outside the source code, and run either direct provider SDK code or LangChain code.

### Setup steps

From an empty project folder:

```bash
uv init .
uv add openai google-genai langchain langchain-groq langchain-google-genai python-dotenv
```

These packages are enough for the supplied notebooks:

| Package | Why it is included now |
|---|---|
| `openai` | The Groq example imports `OpenAI` directly. Groq supports an OpenAI-compatible API format. |
| `google-genai` | The Gemini example imports `from google import genai` directly. |
| `langchain` | Provides `init_chat_model` in the second notebook. |
| `langchain-groq` | Lets LangChain construct a Groq chat model. |
| `langchain-google-genai` | Lets LangChain construct a Gemini chat model. |
| `python-dotenv` | Loads local variables from `.env`. |

`langchain-community`, `langchain-openai`, `langgraph`, `langsmith`, and `langchain-tavily` are not needed for these two notebooks. Introduce them only in the lesson where they are first used. This keeps setup faster and makes each new dependency meaningful.

`uv` records project dependencies in `pyproject.toml` and `uv.lock`. If a platform specifically requires a `requirements.txt` file, create it from the project instead of maintaining a duplicate list:

```bash
uv export --format requirements-txt --output-file requirements.txt
```

### Local credentials

Create a `.env` file beside the Python files. It must stay local and be listed in `.gitignore`.

```text
GROQ_API_KEY=replace_with_your_key
GEMINI_API_KEY=replace_with_your_key
```

The Groq code uses a fixed API base URL, so `GROQ_API_BASE_URL` is optional for the supplied notebook. If you prefer configuration over a hard-coded value, add it to `.env`:

```text
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
```

Do not copy a real key into the notebook, source file, output, screenshot, or Git repository. Groq and Gemini both require an account and API key; current creation steps belong on their official [Groq quickstart](https://console.groq.com/docs/quickstart) and [Gemini API-key guide](https://ai.google.dev/gemini-api/docs/api-key). OpenAI and Anthropic can be presented as optional providers; neither is required for these lessons.

---

# Lesson 1 — AI, LLMs, and the Application

## Optional story

The workshop console speaks for the first time. Its answer is fluent, but it confidently describes a destination that does not exist. The professor's point is simple: a model can generate language before the application has earned the right to trust it.

The learner may skip this section and begin at the technical explanation.

## Technical explanation

### Why AI feels like it changes so quickly

Several layers change at once: research ideas, models, provider APIs, libraries, and products built on top of them. A learner does not need to chase every release. The stable starting point is a request-and-response loop:

```text
User question → application code → model provider → model response → application code
```

The model generates a response. The application owns the prompt, credentials, error handling, private data access, validation, and what the user sees next.

### The vocabulary

| Term | Meaning in this course |
|---|---|
| AI | The broad field of making software perform tasks associated with intelligence. |
| Machine learning | A way of building some AI systems by learning patterns from data. |
| Deep learning | A family of machine-learning methods based on multi-layer neural networks. |
| LLM | A deep-learning model that works with language and generates output from the context it receives. |
| Chat model | An LLM exposed as a conversation interface, usually with messages and roles. |
| AI application | The ordinary software around the model: UI, inputs, data, tools, checks, and output handling. |

An LLM does not automatically know the learner's private documents, current database values, or whether its answer is correct. Those are application concerns addressed in later lessons.

### Why begin here

The first request is deliberately small. It has one prompt, one model call, and one response. If it fails, the learner can inspect credentials, model ID, provider settings, or the request. Adding memory, retrieval, tools, and agents before this loop works would hide the cause of a problem.

## Code walkthrough: a direct provider call

The first notebook gives two direct-SDK examples. They are useful because they reveal the provider boundary before LangChain adds a common interface.

### Snippet 1 — load local configuration

```python
import os

from dotenv import load_dotenv

load_dotenv()
```

`load_dotenv()` reads key-value pairs from `.env` and makes them available through `os.getenv(...)` for the current process. The key stays out of source code. In a Jupyter notebook, run this cell before the provider-specific cells. In a standalone Python file, these imports and `load_dotenv()` must appear in that file.

### Snippet 2 — connect to Groq with the OpenAI client

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
```

The `OpenAI` class is an HTTP client, not proof that this request reaches OpenAI's service. The `base_url` points it to Groq's OpenAI-compatible endpoint, and the API key identifies the Groq account. This is a useful first example of the difference between a client library and a model provider.

### Snippet 3 — request a response

```python
response = client.responses.create(
    model="openai/gpt-oss-120b",
    instructions="You are a ghost of a sarcastic developer.",
    input="Suggest one excuse for being late to office.",
)

print(response.output_text)
```

`model` chooses the provider's model identifier. `instructions` sets the desired behaviour for this request, while `input` contains the task. The returned `response` is a full response object; `response.output_text` extracts the generated text for display.

The notebook's model ID is a recorded example, not a permanent course constant. Provider model catalogs and availability change, so learners should choose a currently available model from the Groq console when their request fails with a model error.

### Snippet 4 — connect to Gemini directly

```python
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)

response = client.interactions.create(
    model="gemini-3.1-flash-lite",
    system_instruction="You are a T-Rex who loves cute things.",
    input="Make an excuse for going to watch the butterflies",
)

print(response.output_text)
```

This has the same overall shape as the Groq example: configure a client, choose a model, give it instructions and input, then print text. The method names differ because this is Gemini's own SDK rather than an OpenAI-compatible client. `system_instruction` provides the behavioural guidance, and `input` provides the user task.

## Lesson 1 check

The learner can explain all five parts of a basic interaction: local configuration, client, provider endpoint, model identifier, and response text. They should also know that a fluent answer is not evidence that the answer is correct or that the model has access to private information.

---

# Lesson 2 — Connecting and Switching Chat Models with LangChain

## Optional story

The console can receive an answer from two different sources, but the wiring begins to spread through every panel. The professor wants one control surface for choosing a model while keeping the lesson task unchanged.

The learner may skip this section and begin at the technical explanation.

## Technical explanation

The previous lesson used each provider's direct SDK. That is valuable for learning what a provider does. This lesson introduces LangChain's common model interface: construct a chat model, call `invoke(...)`, and inspect the returned message.

LangChain reduces repeated provider-integration code. It does not make models identical. Model identifiers, API keys, costs, rate limits, supported features, metadata, and output shapes still vary by provider and model.

## Code walkthrough: the LangChain notebook

### Snippet 1 — initialise notebook configuration

```python
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
```

`load_dotenv()` again makes local keys available to the process. `init_chat_model` is LangChain's factory function: it reads a provider-qualified model string and returns a chat-model object for that provider.

### Snippet 2 — create and call a Groq model

```python
model = init_chat_model("groq:openai/gpt-oss-120b")

response = model.invoke("How many permutations for a deck of 52 cards?")

print(response)
```

The text before the colon, `groq`, selects the integration. The text after the colon is the model ID. `model.invoke(...)` sends one prompt and returns an `AIMessage`, not just a string. Printing the entire response is useful while learning because it exposes the generated content and provider metadata.

The question is intentionally simple, but learners should still verify mathematical answers independently. A model may present a confident explanation without making it correct.

### Snippet 3 — switch to Gemini without changing the call pattern

```python
model = init_chat_model("google_genai:gemini-3.1-flash-lite-preview")

response = model.invoke("What happens of Humpty dumpty?")

print(response.text)
```

Only the model configuration changes. The rest of the application still uses `model.invoke(...)`. This is the main benefit of a common interface: feature code can stay focused on the task while model construction remains in one place.

For this Gemini response, `response.content` may be a list of content blocks, for example:

```python
response.content[0]["text"]
```

That shape is provider- and model-dependent. Prefer the normalized property used by the notebook:

```python
print(response.text)
```

`response.text` is more robust because it extracts the text whether the underlying `content` is a plain string or structured content blocks.

### Snippet 4 — inspect model metadata and usage

```python
print("Model name:", response.response_metadata.get("model_name"))
print("Model provider:", response.response_metadata.get("model_provider"))
print("Token usage:", response.usage_metadata)
```

Use `.get(...)` for optional provider metadata. A particular model may not provide fields such as `model_version`, `model_type`, or `token_usage` inside `response_metadata`. In the supplied Gemini response, token counts live in `response.usage_metadata`, with keys such as `input_tokens`, `output_tokens`, and `total_tokens`.

This distinction matters: a response message contains the answer, metadata describes the provider's result, and usage data helps explain consumption and later cost trade-offs.

## The important limitation

A common function call does not create a common provider contract. When learners switch models, they must still check:

| Question | Why it matters |
|---|---|
| Is the model ID available? | Provider catalogs change and access can differ by account. |
| Is the correct API key set? | Groq and Gemini use separate credentials. |
| Does the model support the needed feature? | Context size, streaming, images, tools, and structured output vary. |
| What does the returned message look like? | Content and metadata can differ across models. |
| What are the limits and price terms? | Rate limits and pricing are provider-specific and change over time. |

The notebook model strings remain useful examples, but the final lesson should instruct learners to consult the current [ChatGroq integration guide](https://docs.langchain.com/oss/python/integrations/chat/groq) and [ChatGoogleGenerativeAI integration guide](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai) before selecting a model.

## Lesson 2 exercise

1. Run the Groq `init_chat_model(...)` example with a currently available Groq model.
2. Ask the same prompt twice and compare the response text and usage metadata.
3. Change only the model configuration to Gemini and repeat the prompt.
4. Record the provider, model ID, whether the request succeeded, the response shape, and one observed difference.
5. Explain why two runs are evidence about this specific task and configuration, rather than a universal ranking of models.

## Lesson 2 check

The learner can connect a model through LangChain, switch between Groq and Gemini, print response text safely, and inspect metadata without assuming every provider returns the same fields.

## References for the final lesson pages

- [uv project initialization](https://docs.astral.sh/uv/concepts/projects/init/)
- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Gemini Python interactions](https://ai.google.dev/gemini-api/docs/text-generation)
- [LangChain ChatGroq](https://docs.langchain.com/oss/python/integrations/chat/groq)
- [LangChain ChatGoogleGenerativeAI](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)
