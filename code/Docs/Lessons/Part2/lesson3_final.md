# Part II · Lesson 3 — Put an LLM inside the graph

## A note from me

We have spent two lessons on functions and arrows. Where is the AI?

Here it is. A model call can live inside a node just like our earlier Python logic. We do not need a new way to ask the model a question. We need to decide what context reaches it and what update its response adds to the workflow.

## What we are building

One chatbot node receives messages, calls the Groq model, and returns its reply. This is a graph around a single model interaction. There are no tools, automatic retries, or saved conversations yet.

Run this notebook from the top with GROQ_API_KEY in the project's .env file. Each invoke below makes a provider request, so normal input and output token usage applies.

## Set up once

Use the same provider connection from Part I.

### Import the model and graph helpers

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-1-1 -->
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

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-1-2 -->
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

## Define and connect the node

Notice how little the model call changes.

### Put the model call inside a node

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-2-1 -->
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

### Connect and compile the chat graph

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-2-2 -->
```python
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
graph = builder.compile()
```

**What happens here**

The flow has one working node. START sends the input to chatbot, and END finishes after its reply. This is intentionally small: adding a graph around one call helps us see where later steps will go.

**Result:** graph is ready to accept an initial messages list.

## Run a model-backed workflow

Send the user's message as graph state.

### Invoke the graph

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-3-1 -->
```python
response = graph.invoke({
    "messages": [HumanMessage("Explain a REST API in two sentences.")]
})
print(response["messages"][-1].text)
```

**What happens here**

The graph passes the initial message to chatbot. Its returned AIMessage is merged into state. We read the last message for the answer instead of trying response.text, because the graph returns a state dictionary.

**Result:** response contains the human request and the model reply. The wording may vary.

### See what the graph returned

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-3-2 -->
```python
for message in response["messages"]:
    print(message.type, ":", message.text)
```

**What happens here**

We inspect the conversation roles and text. The system instruction was supplied inside the node's model call; it was not appended to the stored messages list.

**Result:** The state contains one human message followed by one AI message.

## Check your understanding

1. What part of the code actually calls the model?
2. Why does the node return only its new reply?
3. Why is response a dictionary here?
4. Would a new invoke remember this conversation without a checkpointer?

## Where we go next

Next our graph will let the model request a tool and let the application execute it.

Complete notebook: [3-Connecting-LLM.ipynb](../../../Part%20II%20Connecting%20the%20dots/3-Connecting-LLM.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/graph-api).
