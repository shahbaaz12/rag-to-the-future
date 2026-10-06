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

### Initialize the project

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```powershell
uv init .
```

**What happens here**

Run this inside the project folder. uv creates the basic Python project configuration.

**Result:** The folder now contains the project files.

This creates the basic Python project files, including a `pyproject.toml` file. `uv` will manage the virtual environment for you, so you do not need to activate it manually for this course. Run programs through `uv run` and it will use the project environment.

If you do not yet have Python or `uv`, install them first. I used Python 3.11.9 and `uv` 0.11.3 while preparing the earlier examples. The current repository's `pyproject.toml` requires **Python 3.12 or newer**, so use that version for this project.

### Add the first dependencies

Create a `requirements.txt` file and add the packages below:

### List the packages

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```text
openai
google-genai
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

**What happens here**

Put these package names into requirements.txt. Some support later lessons; google-genai is needed for the direct Gemini SDK example.

**Result:** The installer has a list of dependencies to read.

Then install them:

### Install the dependencies

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```powershell
uv add -r requirements.txt
```

**What happens here**

The -r option reads package names from requirements.txt and adds them to the uv project.

**Result:** The project dependencies are installed and recorded.

Some of these packages belong to later lessons. Installing them now saves us from stopping every time a notebook introduces a new capability. For the first two notebooks, the important packages are `openai`, `python-dotenv`, `langchain`, `langchain-groq`, and `langchain-google-genai`.

### Check that it works

Create a file called `hi.py`:

### Check the installation

<!-- snippet: code/hi.py#setup-check -->
```python
import langchain
```

**What happens here**

We import LangChain, then print a simple message and its installed version. This is a small environment check before making any API requests.

**Result:** If both lines print, the import and script execution worked.

### Check the installation

<!-- snippet: code/hi.py#setup-check -->
```python
print("Everything is working fine")
print(langchain.__version__)
```

**What happens here**

We import LangChain, then print a simple message and its installed version. This is a small environment check before making any API requests.

**Result:** If both lines print, the import and script execution worked.

Run it with:

### Run through the project environment

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```powershell
uv run hi.py
```

**What happens here**

uv run uses the project's managed environment to run this Python file. Manual activation is unnecessary for this command.

**Result:** The script runs with the project's installed packages.

If you see the message and a version number, we are good. If it fails, fix the environment here before going further. Debugging one small import error is much easier than debugging it inside a larger AI application later.

---

## Organize the first part

Create a folder named:

### Name the notebook folder

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```text
Part I Understanding the Basics
```

**What happens here**

This is a folder name, not a terminal command. It matches the location of the course notebooks.

**Result:** The examples have a shared place in the project.

This is where we will work through the notebooks in the repository. Start with [1-Connecting-to-an-LLM.ipynb](../../../Part%20I%20Understanding%20the%20Basics/1-Connecting-to-an-LLM.ipynb).

---

## Get a model key

**An API key** identifies your application to a model provider. Under the hood, your code makes an authenticated HTTP request to that provider’s API. The key tells the provider who is making the request and lets it apply the correct account permissions and limits.

For these first examples, create a key from **Groq**. You can also create a key from **Gemini** and run the Gemini example in the notebook. Both are useful for learning because they offer ways to get started without committing to a paid OpenAI or Anthropic account.

Create a file named `.env` in the project root and keep the key there:

### Store the provider settings

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```text
GROQ_API_KEY=your_key_here
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
GEMINI_API_KEY=your_key_here
```

**What happens here**

These are .env entries, not Python statements. Replace the placeholders with your own keys and keep the file out of Git.

**Result:** The later load_dotenv call can load these settings.

Never commit `.env` to Git. Add it to `.gitignore` before you push anything.

OpenAI and Anthropic are excellent providers, but their APIs commonly require payment or billing setup. They are not required for these lessons. We are here to learn the application pattern first.

---

## Your first direct LLM call

We have many proprietary providers, including OpenAI and Anthropic. In the first notebook, I demonstrate Groq and Gemini instead.

The Groq example uses the OpenAI Python SDK:

### Import Python's environment helper

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
import os
```

**What happens here**

`os` lets us read the API settings that will be loaded into the environment.

**Result:** We can read settings with os.getenv.

### Import the SDK and settings loader

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
from dotenv import load_dotenv
from openai import OpenAI
```

**What happens here**

OpenAI is the SDK client we use for Groq's compatible API. load_dotenv lets us keep the key in a local file.

**Result:** The client constructor and settings loader are available.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
# Load API settings from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Connect the client to Groq

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
# Groq supports the OpenAI API format, so the OpenAI client can call Groq.
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
)
```

**What happens here**

We give the client our Groq key and endpoint.

**`os.getenv`** reads the settings; the endpoint has a fallback if the URL is absent from .env.

**Result:** groq_client points at Groq's API.

### Send the first request

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
# Send one prompt and keep the complete response object.
groq_response = groq_client.responses.create(
    model="openai/gpt-oss-120b",
    instructions="You are a ghost of a sarcastic developer.",
    input="Suggest one excuse for being late to office.",
)
```

**What happens here**

`responses.create` sends the model name, the assistant's instructions, and our question. We keep the entire response in groq_response.

**Result:** The provider returns a response object. The generated excuse can vary.

### Print the answer

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
# Print only the text generated by the model.
print(groq_response.output_text)
```

**What happens here**

`output_text` extracts the generated text, so we can read the answer without printing all the response metadata.

**Result:** The model's answer appears in the notebook.

### Optionally inspect available models

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#b260017c -->
```python
# Optional: inspect the model IDs available to this account.
# available_models = groq_client.models.list()
# for available_model in available_models.data:
#     print(available_model.id)
```

**What happens here**

These lines are commented out in the notebook. If you choose to uncomment them, models.list asks the provider for the model IDs available to the account.

**Result:** Nothing runs while these lines remain comments.

### Try the direct Gemini example

Continue after the Groq setup above.

### Switch to Gemini's SDK

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#8845c25c -->
```python
from google import genai
```

**What happens here**

Gemini uses the google.genai client here. We reuse the environment settings loaded earlier.

**Result:** genai is available. Install google-genai to run this direct SDK example.

### Create the Gemini client

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#8845c25c -->
```python
# Create a Gemini client with the key loaded from .env.
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
```

**What happens here**

`genai.Client` reads the Gemini key from the environment. It is a separate provider client from groq_client.

**Result:** gemini_client is ready for the request.

### Send the Gemini request

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#8845c25c -->
```python
# Send one interaction and keep the complete response object.
gemini_response = gemini_client.interactions.create(
    model="gemini-3.1-flash-lite",
    system_instruction="You are a T-Rex who loves cute things.",
    input="Make an excuse for going to watch the butterflies.",
)
```

**What happens here**

The interaction has a model, a system instruction, and an input. The calling shape differs from Groq's SDK example, but we still send a prompt and receive a response.

**Result:** gemini_response holds the complete interaction response.

### Read Gemini's answer

<!-- snippet: code/Part I Understanding the Basics/1-Connecting-to-an-LLM.ipynb#8845c25c -->
```python
# Print only the text generated by the model.
print(gemini_response.output_text)
```

**What happens here**

We print the output_text from the interaction response. The exact wording is generated by the model.

**Result:** The answer appears in the notebook.

**Groq** is compatible with the OpenAI API format, so we can comfortably use OpenAI-style APIs to call Groq-hosted models.

**Gemini** has its own SDK and call shape. The important part is the same in both cases:

### Follow a direct call

<!-- snippet: code/Docs/Lessons/Part1/lesson2_final.md#supplement -->
```text
load API key → create client → choose model → send input → inspect response
```

**What happens here**

We prepare credentials and a client before sending the input to a chosen model. After the response arrives, our application decides how to use it.

**Result:** The same broad sequence applies across providers.

The provider hosts and runs the model. Your application decides what to send, receives the response, and decides what to do with it.

---

## When changing the model becomes a problem

Say you built your application around one provider’s API. Then its price changes, its privacy policy no longer meets your company’s standards, or another provider becomes a better fit. Switching can become a real undertaking.

The notebook can demonstrate a small change in only a few lines. In a real application, models may be woven into prompts, output parsing, evaluation, security reviews, deployment configuration, and user-facing behavior. The change can easily turn into a multi-sprint development cycle.

Yes, we will learn better ways to organize code. But let’s be honest: many projects accumulate shortcuts before anyone gets around to the architecture book. The useful lesson here is simple: know which parts of your code are provider-specific, and keep an eye on them from the beginning.

---

## A quick note on open-source models

While we are here: you can download an open-source model, host it yourself, and make calls without paying a hosted-model provider for each request.

Free is doing a lot of work in that sentence. You still pay for machines, electricity, deployment, monitoring, and your own time. Self-hosting is valuable and we will come back to it, but do not divert into it yet. First, learn to make a reliable hosted-model call and understand the application around it.



## Next lesson

We will use LangChain to give multiple model providers a more consistent interface, then see what still changes when we switch models.
