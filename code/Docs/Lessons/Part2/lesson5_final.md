# Part II · Lesson 5 — Let the graph ask again

## A note from me

One lookup is useful. But a user can ask a question that needs more than one fact: do we have enough laptops, and what would two of them cost?

Rather than writing a separate fixed path for every possible question, we can let the model inspect a result and decide whether it needs another tool. The graph still defines the allowed choices.

## What is a ReAct-style loop?

ReAct is often expanded as reasoning and acting. Here we focus on the observable flow: the model chooses a tool, the application runs it, the result returns to the model, and the model either asks again or gives an answer. We do not need to display hidden reasoning to understand that flow.

Our previous graph went from tools to a final-answer node. This graph goes from tools back to the assistant node. That one changed edge makes repeated decisions possible.

The tools remain local, read-only examples. An agent loop does not grant access to anything beyond the tools we actually provide.

## Set up the model and tools

This notebook is independent; run its setup from the top.

### Import the model and graph helpers

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-1-1 -->
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

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-1-2 -->
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

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-1-3 -->
```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
```

**What happens here**

ToolNode runs calls against the tools we supply and creates their ToolMessage results. tools_condition examines the latest model reply and routes to tools only when that reply contains a tool request.

**Result:** We can build the same application-controlled flow with less plumbing.

### Give the graph a stock lookup

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-1-4 -->
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

### Add a price lookup

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-1-5 -->
```python
@tool
def get_price_service(item: str) -> int:
    """Return the unit price in rupees for headphone, keyboard, or laptop."""
    prices = {"headphone": 1999, "keyboard": 1499, "laptop": 54999}
    return prices.get(item.lower(), 0)
```

**What happens here**

The second tool answers a different question: what one item costs. Both tools use the same item name, but their results have different meanings. These are sample catalogue values, not live prices.

**Result:** We have separate tools for stock and unit price.

## Let the assistant choose from both tools

Return the complete message each time.

### Bind both tools

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-2-1 -->
```python
inventory_tools = [check_stock_service, get_price_service]
tool_model = model.bind_tools(inventory_tools)
```

**What happens here**

The model can request stock, price, or both. The tool list defines the available choices; it is not a list of actions that always runs.

**Result:** The tool-enabled model can make inventory lookup requests.

### Define the assistant node

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-2-2 -->
```python
def assistant(state: MessagesState) -> dict:
    reply = tool_model.invoke([
        SystemMessage("Use inventory tools for stock and prices. Answer when you have the facts."),
        *state["messages"],
    ])
    return {"messages": [reply]}
```

**What happens here**

The assistant sees all messages already in state, including earlier tool results. It can decide whether the facts are sufficient or whether another available tool would help.

**Result:** Each visit adds a fresh model message.

### Connect the loop and its exit

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-2-3 -->
```python
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(inventory_tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant", tools_condition, {"tools": "tools", END: END}
)
builder.add_edge("tools", "assistant")
graph = builder.compile()
```

**What happens here**

After tools run, the graph returns to assistant. A model reply containing tool calls continues the loop; a reply without tool calls routes to END. The model can request multiple tools in one round or use separate rounds.

**Result:** The graph can repeat its model-and-tool interaction.

## Run and inspect the loop

Set an execution limit even for a small example.

### Ask a question using both facts

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-3-1 -->
```python
response = graph.invoke(
    {"messages": [HumanMessage("Do we have two laptops in stock, and what is their total price?")]},
    {"recursion_limit": 12},
)
print(response["messages"][-1].text)
```

**What happens here**

We send the question and a graph-step limit. The sample catalogue has 12 laptops at Rs 54,999 each. A successful answer using these tools can report availability and Rs 109,998 for two. The limit guards against endless execution; reaching it raises an error and is not a successful stopping condition.

**Result:** The model produces an answer using the tool results; the exact wording and tool-call order may vary.

### See which decisions were made

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-3-2 -->
```python
for message in response["messages"]:
    print(message.type, message.text)
    if getattr(message, "tool_calls", None):
        print("Requested calls:", message.tool_calls)
```

**What happens here**

We inspect the externally visible conversation. Tool requests and ToolMessage results tell us what actually happened, even when the model's final answer sounds confident.

**Result:** We can follow the loop rather than treating it as a black box.

## Check your understanding

1. Which edge turns the previous workflow into a loop?
2. When does tools_condition route to END?
3. Can two tools be requested in the same round?
4. Does reaching recursion_limit mean the task succeeded?

## Where we go next

Next we will keep a conversation's state between graph invocations.

Complete notebook: [5-ReActive-Graph.ipynb](../../../Part%20II%20Connecting%20the%20dots/5-ReActive-Graph.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/quickstart).
