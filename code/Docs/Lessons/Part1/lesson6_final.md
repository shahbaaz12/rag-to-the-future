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

## 1. Manual memory: resend the history

The simplest memory is a Python list of messages. A message is text plus its role, and we send the complete list again on every turn.

```python
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage

model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
    reasoning_effort="low",
)

messages = [SystemMessage("You are a concise assistant.")]

# Turn 1
messages.append(HumanMessage("My name is Ada. I am learning about LLMs."))
reply = model.invoke(messages)
messages.append(AIMessage(reply.content))
print("AI:", reply.content)

# Turn 2: the model only knows Ada because we resend the whole list.
messages.append(HumanMessage("What is my name and what am I learning?"))
reply = model.invoke(messages)
messages.append(AIMessage(reply.content))
print("AI:", reply.content)

print(len(messages))
```

This is clear and useful for a short conversation. But every earlier message becomes input again. The history grows, token usage grows, and eventually we reach a context limit.

---

## 2. Manual memory with summarisation

When history becomes large, we can keep the important idea while removing the full detail. First, turn old messages into text and ask the model for a short summary. Then replace the old messages with that summary.

```python
# Pretend a long conversation already happened.
messages = [
    SystemMessage("You are a concise assistant."),
    HumanMessage("My name is Ada. I am learning about LLMs."),
    AIMessage("Nice to meet you, Ada!"),
    HumanMessage("I like Python and I use Groq."),
    AIMessage("Great combo."),
]

# Step 1: summarise every old message except the system instruction.
old_text = "\n".join(f"{message.type}: {message.content}" for message in messages[1:])
summary = model.invoke(
    f"Summarize this conversation in one line:\n{old_text}"
).content

# Step 2: replace the detailed history with the summary.
messages = [
    messages[0],
    SystemMessage(f"Summary of earlier chat: {summary}"),
]

# Step 3: the model has useful context with fewer tokens.
messages.append(HumanMessage("What is my name and what do I use?"))
print("AI:", model.invoke(messages).content)
```

Five messages became two. That is the benefit. The trade-off is that a summary can miss or alter a detail, so do not summarise facts that must remain exact without a way to recover them.

---

## 3. Checkpointer: let the application store the history

Manually passing a list works, but a real application needs to keep different users and conversations separate. A **checkpointer** is the notebook that stores the chat history for us.

`InMemorySaver` is a simple in-process checkpointer for learning and local development. The important identifier is the `thread_id`: the same ID restores the same conversation; a different ID starts a different one.

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# The checkpointer stores history by thread ID.
memory = InMemorySaver()

agent = create_agent(
    model,
    tools=[],
    system_prompt="You are a concise assistant.",
    checkpointer=memory,
)

user1_config = {"configurable": {"thread_id": "user1"}}

# Turn 1: send only the new message.
message1 = HumanMessage("My name is Ada. I am learning about LLMs.")
response1 = agent.invoke({"messages": [message1]}, user1_config)
print("AI:", response1["messages"][-1].content)

# Turn 2: the checkpointer restores user1's earlier history.
message2 = HumanMessage("What is my name and what am I learning?")
response2 = agent.invoke({"messages": [message2]}, user1_config)
print("AI:", response2["messages"][-1].content)

# A new thread starts with no memory of Ada.
user2_config = {"configurable": {"thread_id": "user2"}}
message3 = HumanMessage("What is my name?")
response3 = agent.invoke({"messages": [message3]}, user2_config)
print("AI:", response3["messages"][-1].content)
```

The checkpointer does not give the model a magical long-term brain. It gives the application a place to store and restore the right state. In production, choose storage, retention, access controls, and deletion rules deliberately.

Work through the complete examples in [6-Memory.ipynb](../../../Part%20I%20Understanding%20the%20Basics/6-Memory.ipynb).

## Check your understanding

1. Why does the manual-memory example send the whole list again on turn two?
2. What benefit and risk come from summarising old messages?
3. What does a `thread_id` do?
4. Why does a new `thread_id` not know Ada’s name?

## Next lesson

We will let a model request a tool, then see why the application must control every tool execution.
