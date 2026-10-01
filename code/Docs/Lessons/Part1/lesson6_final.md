# Lesson 6 — Memory: What the Model Knows Between Turns

> **Review draft**
>
> This lesson makes conversation memory explicit. We first carry messages ourselves, then compress old history, and finally let a checkpointer restore the right conversation for each user.

## A note from me

A chat model can look as if it remembers you. It does not. Each model call only knows the messages and context that reach it in that call.

So when a model remembers that Ada is learning about LLMs, something in our application carried that information forward. This lesson is about that “something.”

## What you will be able to do

- explain why a model does not remember a previous API call by itself;
- keep a short conversation history manually;
- replace old history with a compact summary; and
- use a checkpointer to keep separate conversations by `thread_id`.

---



## Set up once

Run these setup snippets first. All three examples use this same model object.

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#memory-imports -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage
```

**What happens here**

We import the model constructor and three message types. SystemMessage holds instructions, HumanMessage holds our question, and AIMessage represents a model reply.

**Result:** The names we need are available for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#memory-imports -->
```python
# Load GROQ_API_KEY from the local .env file.
load_dotenv()
```

**What happens here**

We use load_dotenv to read the API key from the local .env file, just as we did in the earlier notebooks.

**Result:** The Groq integration can find the key when we create the model.

### Create the model connection

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#memory-imports -->
```python
model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
    reasoning_effort="low",
)
```

**What happens here**

init_chat_model creates the Groq model object. The model name selects the hosted model, and reasoning_effort sets the requested reasoning level. This prepares the object; invoke will send the actual request.

**Result:** We can reuse model for every example below. Make GROQ_API_KEY available before running the notebook.

## 1. Manual memory

The simplest memory is a Python list. Our application keeps the messages and sends them again on each turn.

### Start the conversation

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#manual-code -->
```python
messages = [SystemMessage("You are a concise assistant.")]
```

**What happens here**

We start a list with the assistant's instruction. This is the first message that later requests will receive.

**Result:** messages contains one system message.

### Send the first message and save the reply

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#manual-code -->
```python
# Turn 1
messages.append(HumanMessage("My name is Ada. I am learning about LLMs."))
reply = model.invoke(messages)
messages.append(AIMessage(reply.content))
print("AI:", reply.content)
```

**What happens here**

append adds Ada's introduction. invoke sends the current list to the model. We then add the reply as an AIMessage so the next request can include both sides of the exchange.

**Result:** The list now contains the instruction, Ada's introduction, and the model's reply.

### Ask a follow-up with the same history

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#manual-code -->
```python
# Turn 2: the model only knows Ada because we resend the whole list.
messages.append(HumanMessage("What is my name and what am I learning?"))
reply = model.invoke(messages)
messages.append(AIMessage(reply.content))
print("AI:", reply.content)
```

**What happens here**

We add the follow-up, then send the entire list again. The earlier introduction is still in that list, so the model has context for Ada's name and what she is learning. We also save this second reply.

**Result:** The model can answer using the introduction sent earlier. Its wording may vary.

### Count what we have stored

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#manual-code -->
```python
print("Messages stored:", len(messages))
```

**What happens here**

len(messages) counts message objects, rather than tokens. We have one instruction plus two human messages and two AI replies.

**Result:** Messages stored: 5

## 2. Manual memory with summarisation

A growing history becomes more input on every call. Here we replace older details with a short summary. This example starts its own history list.

### Prepare a sample history

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#summary-code -->
```python
# Pretend a long conversation already happened.
messages = [
    SystemMessage("You are a concise assistant."),
    HumanMessage("My name is Ada. I am learning about LLMs."),
    AIMessage("Nice to meet you, Ada!"),
    HumanMessage("I like Python and I use Groq."),
    AIMessage("Great combo."),
]
```

**What happens here**

We create a five-message conversation to practise on. Ada's name, Python preference, and Groq usage are the useful facts we want to carry forward.

**Result:** This replaces the messages list from the manual-memory example.

### Turn the older messages into a summary

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#summary-code -->
```python
# Step 1: summarise every old message except the system instruction.
old_text = "\n".join(f"{message.type}: {message.content}" for message in messages[1:])
summary = model.invoke(
    f"Summarize this conversation in one line:\n{old_text}"
).content
print("Summary:", summary)
```

**What happens here**

messages[1:] skips the system instruction. The join builds text containing each message's role and content. We ask the model to summarise that text and take the response content.

**Result:** summary holds the generated summary. Creating it uses an additional model call.

### Replace the full history

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#summary-code -->
```python
# Step 2: replace detailed history with a compact summary.
messages = [
    messages[0],
    SystemMessage(f"Summary of earlier chat: {summary}"),
]
print("Messages stored after summary:", len(messages))
```

**What happens here**

We keep messages[0], the original instruction, and add the summary as another message. The full older conversation is no longer included in this list.

**Result:** Messages stored after summary: 2. Fewer messages only save tokens when their text is shorter too.

### Ask using the compact context

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#summary-code -->
```python
# Step 3: the model keeps useful context using fewer input tokens.
messages.append(HumanMessage("What is my name and what do I use?"))
print("AI:", model.invoke(messages).content)
```

**What happens here**

We append a new question and send the instruction, summary, and question together. The model now relies on the summary to answer.

**Result:** The answer can use the facts retained in the summary. Summaries can omit details; keep or recover exact facts when needed.

## 3. Checkpointer

A checkpointer stores and restores conversation state for a named thread. We use create_agent with no tools here as a simple conversation wrapper; the tools and agents lessons will explain it further.

### Import the conversation wrapper and storage

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
```

**What happens here**

create_agent builds the conversation wrapper. InMemorySaver supplies a place to store its state inside this Python process.

**Result:** The imports are ready. This storage will disappear when the process ends.

### Create the checkpointer

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
# The checkpointer is the notebook that stores chat history.
memory = InMemorySaver()
```

**What happens here**

We create one InMemorySaver instance. The agent in the next snippet will use this same instance to save and restore conversation state.

**Result:** memory is our local checkpointer.

### Attach it to the agent

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
agent = create_agent(
    model,
    tools=[],
    system_prompt="You are a concise assistant.",
    checkpointer=memory,
)
```

**What happens here**

We pass the existing model, an empty tools list, the assistant instruction, and our checkpointer to create_agent. The wrapper handles the saved conversation around each call.

**Result:** agent is ready to accept new messages with a thread configuration.

### Choose a conversation ID

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
# The same thread ID means the same stored conversation.
user1_config = {"configurable": {"thread_id": "user1"}}
```

**What happens here**

thread_id names the conversation whose saved state we want to use. It identifies a thread, rather than authenticating a user. In this example we name the first thread user1.

**Result:** Calls with this configuration will continue the same conversation.

### Send just the new introduction

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
# Turn 1: send only the new message.
message1 = HumanMessage("My name is Ada. I am learning about LLMs.")
response1 = agent.invoke({"messages": [message1]}, user1_config)
print("AI:", response1["messages"][-1].content)
```

**What happens here**

We send message1 with user1_config. The agent records the conversation in the checkpointer. The returned messages list includes the conversation state, so [-1] selects its latest reply.

**Result:** The user1 thread now contains Ada's introduction and the reply.

### Continue the same thread

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
# Turn 2: the checkpointer restores user1's history.
message2 = HumanMessage("What is my name and what am I learning?")
response2 = agent.invoke({"messages": [message2]}, user1_config)
print("AI:", response2["messages"][-1].content)
```

**What happens here**

We send only the new question with the same configuration. The agent restores the earlier state for this thread and includes that context in the model request.

**Result:** The model can use Ada's introduction even though we did not manually resend it.

### Try a different thread

<!-- snippet: code/Part I Understanding the Basics/6-Memory.ipynb#checkpointer-code -->
```python
# A different thread ID starts with empty memory.
user2_config = {"configurable": {"thread_id": "user2"}}
message3 = HumanMessage("What is my name?")
response3 = agent.invoke({"messages": [message3]}, user2_config)
print("AI:", response3["messages"][-1].content)
```

**What happens here**

user2_config selects a new thread. We ask for a name without supplying one in this conversation. The earlier user1 history is not restored for this ID.

**Result:** There is no supplied name in user2's context. The assistant should ask for it rather than claim to remember Ada.

Work through the complete examples in [6-Memory.ipynb](../../../Part%20I%20Understanding%20the%20Basics/6-Memory.ipynb).

## Check your understanding

1. Why does the manual-memory example send the whole list again on turn two?
2. What benefit and risk come from summarising old messages?
3. What does a `thread_id` do?
4. Why does a new `thread_id` not know Ada’s name?

## Next lesson

We will let a model request a tool, then see why the application must control every tool execution.
