# Part II · Lesson 7 — Watch the graph work

## A note from me

Waiting for the final answer can make an application feel frozen. Sometimes the user wants the text as it appears. Sometimes we want to know which step has finished.

Those are two different kinds of progress. A node update tells us that a step has produced a state change. A model text chunk lets us start displaying an answer while the model is still generating it.

## What we are building

We will use the same one-node chat graph and try two stream modes. updates shows the changes a node returns. messages exposes supported model message chunks together with metadata about where they came from.

Each stream below starts a separate graph run and makes its own model request. They are two demonstrations, not two views of one shared API call. No checkpointer is attached here, so the examples do not retain chat memory.

## Set up the familiar chat graph

The node can still use model.invoke; LangGraph's streaming machinery observes the model's supported streaming callbacks.

### Import the model and graph helpers

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-1-1 -->
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

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-1-2 -->
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

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-1-3 -->
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

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-1-4 -->
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

## 1. Stream node updates

This mode describes completed work in the workflow.

### Inspect each completed node's update

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-2-1 -->
```python
for event in graph.stream(
    {"messages": [HumanMessage("Explain a graph node in one sentence.")]},
    stream_mode="updates",
):
    for node_name, update in event.items():
        print("Finished node:", node_name)
        print(update["messages"][-1].text)
```

**What happens here**

updates emits the state changes returned by completed nodes. Our graph has one chatbot node, so its update contains one complete AI reply. It does not emit one update for each generated word.

**Result:** We see the node name and its returned message after that node completes.

## 2. Stream the model's text

Here we can show text before the node's full answer is ready.

### Print chunks from the chatbot node

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-3-1 -->
```python
for message_chunk, metadata in graph.stream(
    {"messages": [HumanMessage("Explain nodes and edges in three short sentences.")]},
    stream_mode="messages",
):
    if metadata.get("langgraph_node") == "chatbot":
        print(message_chunk.text, end="", flush=True)
print()
```

**What happens here**

messages yields a chunk and metadata. langgraph_node identifies the node responsible for the model call. We print text chunks from chatbot as they arrive. A chunk may contain part of a word, several words, or no display text; it is not necessarily one token.

**Result:** The response appears gradually when the chosen integration supports text streaming.

## Check your understanding

1. What does updates show?
2. Does a node update necessarily mean one model token?
3. What does langgraph_node identify?
4. How many model requests do these two demonstrations make?

## Where we go next

Next we will deliberately pause a workflow and let a person decide whether it should continue.

Complete notebook: [6-Streaming.ipynb](../../../Part%20II%20Connecting%20the%20dots/6-Streaming.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/streaming).
