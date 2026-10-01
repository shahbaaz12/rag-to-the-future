# Lesson 2 — Set Up, Then Make the Call

> **Review draft**
>
> This lesson gets the learner’s local project ready and makes the first real calls to hosted LLMs. The goal is a working environment, not a perfect production setup.

## A note before we start

We will build the exact code that is present in the GitHub repository. Before we get into prompts, models, or frameworks, we need a small project that can run Python, keep secrets out of source code, and install the libraries we need.

Do not overthink the setup. Create the folder, run the commands, make one request, and move on. We will improve the application as the course gives us a reason to do so.

## What you will be able to do

By the end of this lesson, you can:

- create a Python project with `uv`;
- install the dependencies used in the first notebooks;
- run a quick check that confirms the project works;
- create and store a Groq or Gemini API key safely; and
- explain how the first direct model calls work.

---

## Set up the project

Create a new folder wherever you prefer, then open it in a terminal, VS Code, or another IDE.

```powershell
uv init .
```

This creates the basic Python project files, including a `pyproject.toml` file. `uv` will manage the virtual environment for you, so you do not need to activate it manually for this course. Run programs through `uv run` and it will use the project environment.

If you do not yet have Python or `uv`, install them first. I used Python 3.11.9 and `uv` 0.11.3 while preparing these examples, but nearby versions should work too.

### Add the first dependencies

Create a `requirements.txt` file and add the packages below:

```text
openai
langchain
langchain-community
langchain-openai
langchain-groq
python-dotenv
langchain-google-genai
langgraph
langsmith
langchain-tavily
jupyter
```

Then install them:

```powershell
uv add -r requirements.txt
```

Some of these packages belong to later lessons. Installing them now saves us from stopping every time a notebook introduces a new capability. For the first two notebooks, the important packages are `openai`, `python-dotenv`, `langchain`, `langchain-groq`, and `langchain-google-genai`.

### Check that it works

Create a file called `hi.py`:

```python
import langchain

print("Everything is working fine")
print(langchain.__version__)
```

Run it with:

```powershell
uv run hi.py
```

If you see the message and a version number, we are good. If it fails, fix the environment here before going further. Debugging one small import error is much easier than debugging it inside a larger AI application later.

---

## Organise the first part

Create a folder named:

```text
Part I Understanding the Basics
```

This is where we will work through the notebooks in the repository. Start with [1-Connecting-to-an-LLM.ipynb](../../../Part%20I%20Understanding%20the%20Basics/1-Connecting-to-an-LLM.ipynb).

---

## Get a model key

An API key identifies your application to a model provider. Under the hood, your code makes an authenticated HTTP request to that provider’s API. The key tells the provider who is making the request and lets it apply the correct account permissions and limits.

For these first examples, create a key from **Groq**. You can also create a key from **Gemini** and run the Gemini example in the notebook. Both are useful for learning because they offer ways to get started without committing to a paid OpenAI or Anthropic account.

Create a file named `.env` in the project root and keep the key there:

```text
GROQ_API_KEY=your_key_here
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
GEMINI_API_KEY=your_key_here
```

Never commit `.env` to Git. Add it to `.gitignore` before you push anything.

OpenAI and Anthropic are excellent providers, but their APIs commonly require payment or billing setup. They are not required for these lessons. We are here to learn the application pattern first.

---

## Your first direct LLM call

We have many proprietary providers, including OpenAI and Anthropic. In the first notebook, I demonstrate Groq and Gemini instead.

The Groq example uses the OpenAI Python SDK:

```python
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
)

groq_response = groq_client.responses.create(
    model="openai/gpt-oss-120b",
    instructions="You are a ghost of a sarcastic developer.",
    input="Suggest one excuse for being late to office.",
)

print(groq_response.output_text)
```

Groq is compatible with the OpenAI API format, so we can comfortably use OpenAI-style APIs to call Groq-hosted models. Gemini has its own SDK and call shape. The important part is the same in both cases:

```text
load API key → create client → choose model → send input → inspect response
```

The provider hosts and runs the model. Your application decides what to send, receives the response, and decides what to do with it.

---

## When changing the model becomes a problem

Say you built your application around one provider’s API. Then its price changes, its privacy policy no longer meets your company’s standards, or another provider becomes a better fit. Switching can become a real undertaking.

The notebook can demonstrate a small change in only a few lines. In a real application, models may be woven into prompts, output parsing, evaluation, security reviews, deployment configuration, and user-facing behaviour. The change can easily turn into a multi-sprint development cycle.

Yes, we will learn better ways to organise code. But let’s be honest: many projects accumulate shortcuts before anyone gets around to the architecture book. The useful lesson here is simple: know which parts of your code are provider-specific, and keep an eye on them from the beginning.

---

## A quick note on open-source models

While we are here: you can download an open-source model, host it yourself, and make calls without paying a hosted-model provider for each request.

Free is doing a lot of work in that sentence. You still pay for machines, electricity, deployment, monitoring, and your own time. Self-hosting is valuable and we will come back to it, but do not divert into it yet. First, learn to make a reliable hosted-model call and understand the application around it.



## Next lesson

We will use LangChain to give multiple model providers a more consistent interface, then see what still changes when we switch models.
