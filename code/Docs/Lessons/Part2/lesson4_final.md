# Part II · Lesson 4 — Run a tool inside the graph

## A note from me

A model can sound confident about our stock. That does not mean it has checked the stock list.

We already know what a tool request looks like from Part I. Now we will give each part of that interaction a place in the graph: ask the model, execute the requested lookup, then write an answer using the result.

## What we are building

A small inventory assistant with one read-only stock tool. Our data is a local Python dictionary. The point is the flow, so we will not complicate it with a real database yet.

This graph permits one round of tool calls. If the first reply does not request a tool, we end immediately. Otherwise the tool node runs the calls, and a final model call writes the answer without being given tools again.

## Set up the model and tool

Run these setup cells first.

### Import the model and graph helpers

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-1-1 -->
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

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-1-2 -->
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

### Import the tool execution helpers

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-1-3 -->
```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
```

**What happens here**

ToolNode runs calls against the tools we supply and creates their ToolMessage results. tools_condition examines the latest model reply and routes to tools only when that reply contains a tool request.

**Result:** We can build the same application-controlled flow with less plumbing.

### Give the graph a stock lookup

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-1-4 -->
```python
@tool
def check_stock_service(item: str) -> int:
    """Return stock for headphone, keyboard, or laptop; use the singular item name."""
    stock = {"headphone": 6, "keyboard": 11, "laptop": 12}
    return stock.get(item.lower(), 0)
```

**What happens here**

This is a normal Python lookup exposed through @tool. The description tells the model when it is useful, and item is its input. We use a small local dictionary so we can follow the graph without adding a database or another API.

**Result:** The stock tool can return a quantity when the application executes it.

## Separate asking from answering

The first node can request a tool; the final node only writes an answer.

### Bind the allowed tool

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-2-1 -->
```python
stock_tools = [check_stock_service]
tool_model = model.bind_tools(stock_tools)
```

**What happens here**

bind_tools supplies the stock tool's description and arguments to the model. It does not run the function. stock_tools also supplies the actual tool object to the execution node below.

**Result:** The model knows which lookup it can request.

### Ask whether a tool is needed

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-2-2 -->
```python
def ask_model(state: MessagesState) -> dict:
    reply = tool_model.invoke([
        SystemMessage("Use the stock tool for inventory quantities."),
        *state["messages"],
    ])
    return {"messages": [reply]}
```

**What happens here**

The reply may contain tool_calls. We keep the complete message so the requested function name, arguments, and call ID reach the execution node.

**Result:** The state contains either a normal answer or a tool-call request.

### Answer after the lookup

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-2-3 -->
```python
def answer_from_tool(state: MessagesState) -> dict:
    reply = model.invoke([
        SystemMessage("Answer using the stock tool result."),
        *state["messages"],
    ])
    return {"messages": [reply]}
```

**What happens here**

Here we use the original model object rather than tool_model. It receives the question, tool-call request, and ToolMessage result, then writes a final answer.

**Result:** This node closes the single-round tool interaction.

## Connect the request and result

Keep the tool route visible.

### Register all three nodes

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-3-1 -->
```python
builder = StateGraph(MessagesState)
builder.add_node("ask_model", ask_model)
builder.add_node("tools", ToolNode(stock_tools))
builder.add_node("answer", answer_from_tool)
```

**What happens here**

ToolNode is the framework helper that executes the supplied tools and returns their results as ToolMessage objects. The model itself still does not execute the Python lookup.

**Result:** Our builder knows the request, tool execution, and final-answer steps.

### Route to tools only when requested

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-3-2 -->
```python
builder.add_edge(START, "ask_model")
builder.add_conditional_edges(
    "ask_model", tools_condition, {"tools": "tools", END: END}
)
builder.add_edge("tools", "answer")
builder.add_edge("answer", END)
graph = builder.compile()
```

**What happens here**

tools_condition looks at the latest model message. A tool request takes the tools path; a normal answer ends the run. After a lookup we always run answer, which has no bound tools.

**Result:** The graph can handle a direct answer or one round of lookups.

### Ask and inspect the conversation

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-3-3 -->
```python
response = graph.invoke({
    "messages": [HumanMessage("How many laptops are in stock?")]
})
for message in response["messages"]:
    print(message.type, message.text)
    if getattr(message, "tool_calls", None):
        print("Requested calls:", message.tool_calls)
```

**What happens here**

We inspect both text and tool_calls because a tool-request message may have empty text. The stock dictionary holds 12 laptops; when the model uses the lookup correctly, its answer can use that result.

**Result:** The trace makes the request, tool result, and final response visible.

## Check your understanding

1. Does bind_tools execute a tool?
2. What does ToolNode return?
3. Why does the final node use model instead of tool_model?
4. What happens if no tool call is requested?

## Where we go next

Next we will allow the model to revisit its decision after receiving a tool result.

Complete notebook: [4-Using-Tools.ipynb](../../../Part%20II%20Connecting%20the%20dots/4-Using-Tools.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/quickstart).
