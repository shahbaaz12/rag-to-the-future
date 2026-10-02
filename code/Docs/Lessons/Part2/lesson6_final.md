# Part II · Lesson 6 — Keep the right conversation

## A note from me

Our graph can carry messages from node to node. That is useful, but what happens after the run finishes and the user asks another question?

A fresh graph call has no earlier conversation unless our application provides it or restores saved state. We met checkpointers in Part I through create_agent. Now we attach one directly to our own graph.

## What we are building

A small chat graph with separate conversations for user1 and user2. We send only the new message on the second turn; the checkpointer restores the saved messages for the same thread.

We use a simple chatbot here rather than adding tools again. The same checkpointer mechanism can also be attached when compiling the tool loop from the previous lesson.

InMemorySaver stores state only in the current Python process. Restarting the kernel loses it. A thread ID chooses conversation state; it is not a login or an access-control check.

## Set up the chat node

The model and node match the earlier single-node graph.

### Import the model and graph helpers

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-1-1 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
```

**What happens here**

These are familiar LangChain model and message helpers, plus our graph building blocks. MessagesState already defines a messages list with the add_messages reducer, so we do not need to write that same schema again.

**Result:** The model, message, and graph helpers are available.

### Load the key and create the model

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-1-2 -->
```python
# Keep GROQ_API_KEY in the local .env file.
load_dotenv()
model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
    reasoning_effort="low",
)
```

**What happens here**

We use the same Groq model as Part I. load_dotenv makes the key available, and init_chat_model prepares our connection. No question has been sent yet.

**Result:** model is ready for the node that will call it.

### Put the model call inside a node

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-1-3 -->
```python
def chatbot(state: MessagesState) -> dict:
    reply = model.invoke([
        SystemMessage("You are a concise assistant for a Python learner."),
        *state["messages"],
    ])
    # Return only the new reply; the reducer keeps the earlier messages.
    return {"messages": [reply]}
```

**What happens here**

Our node receives the current messages, adds an instruction for this model call, and invokes the model. The star expands the existing list into the request. We return the new AIMessage itself, preserving its metadata and any structured fields. We do not return the whole old conversation again.

**Result:** The node adds one model reply to the graph state.

## Compile with memory

This is where persistence enters the graph.

### Create a checkpointer

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-2-1 -->
```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
```

**What happens here**

InMemorySaver gives this Python process a place to hold saved graph state. Reuse the same instance for the conversations you want to continue.

**Result:** memory is ready to attach to the graph.

### Attach it during compilation

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-2-2 -->
```python
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
graph = builder.compile(checkpointer=memory)
```

**What happens here**

Passing checkpointer at compile time lets the graph save and restore state around execution. MessagesState still controls how new messages merge with the stored list.

**Result:** The graph can continue a named thread.

## Continue one thread, then try another

Send only the new input on each turn.

### Start the first conversation

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-3-1 -->
```python
user1_config = {"configurable": {"thread_id": "user1"}}
first_response = graph.invoke(
    {"messages": [HumanMessage("My name is Ada. I am learning LangGraph.")]},
    user1_config,
)
print(first_response["messages"][-1].text)
```

**What happens here**

The configuration names the conversation. The graph stores Ada's introduction and the model's reply under that thread.

**Result:** user1 has a saved conversation.

### Ask a follow-up in the same thread

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-3-2 -->
```python
second_response = graph.invoke(
    {"messages": [HumanMessage("What is my name, and what am I learning?")]},
    user1_config,
)
print(second_response["messages"][-1].text)
```

**What happens here**

We send only the new question with the same thread ID. The checkpointer restores the earlier state, and the message reducer adds this question. The model receives Ada's earlier introduction as context.

**Result:** The reply can use the facts supplied in the first turn.

### Start a different conversation

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-3-3 -->
```python
user2_config = {"configurable": {"thread_id": "user2"}}
other_response = graph.invoke(
    {"messages": [HumanMessage("What is my name?")]}, user2_config
)
print(other_response["messages"][-1].text)
```

**What happens here**

A different thread selects different saved state. We have not supplied a name in user2's conversation, so the model should ask for one rather than claim to remember Ada.

**Result:** The two threads do not share their message histories.

### Inspect the stored state

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-3-4 -->
```python
saved_state = graph.get_state(user1_config)
print("Messages saved for user1:", len(saved_state.values["messages"]))
```

**What happens here**

get_state gives us a snapshot of the saved graph state for this thread. We count message objects, not tokens. The history normally contains two human requests and two AI replies.

**Result:** user1 has four conversation messages after the two turns.

## Check your understanding

1. Where do we attach the checkpointer?
2. Why do we send only new messages on the second turn?
3. What happens when the kernel restarts?
4. Does a thread ID prove which user is logged in?

## Where we go next

Next we will watch a graph's progress and receive model text as it arrives.

Complete notebook: [5-adding-memory.ipynb](../../../Part%20II%20Connecting%20the%20dots/5-adding-memory.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/persistence).
