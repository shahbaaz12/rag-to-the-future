# Part II · Lesson 5 — Compare travel options with a tool loop

## A note from me

“Compare the available trains and flights from Mumbai to Goa. Which option fits a ₹2,000 budget?”

One lookup gives us route IDs. Another gives us prices and durations for those routes. The model needs the first result before it can request details for the returned IDs.

**A tool-execution loop** lets the model request another tool after seeing a result. After receiving a result, the model decides whether to request more information or give its answer.

## What we are building

We will build a travel comparison assistant for a Mumbai-to-Goa trip with a ₹2,000 budget. It first needs to find available routes, then read their prices and durations before comparing them. Our local sample train costs ₹900 and takes 10 hours; the flight costs ₹4,500 and takes 1.5 hours. These are teaching values, not current fares.

<div data-graph-preview="builder"></div>

**The idea behind it** is to let the intelligent graph use a result to decide what information it needs next. In Lesson 12, a tool lookup led to a final answer step. Here, we add a backward edge from `tools` to `assistant`. That familiar loop connection gives the model another turn with the latest tool results in state.

We still define the available tools and graph connections. On each visit, the model can request a tool or write its final answer. Our application executes requested functions and adds their results to the conversation. The next model call can use those results.

**A typical comparison** follows these steps:

1. The assistant requests `find_routes`, which returns `TRAIN-01` and `FLIGHT-01`.
2. After seeing those IDs, it requests `get_route_details` for the returned routes. The model may request both details together or in separate rounds.
3. With the prices and durations available, it can compare the options and explain that the sample train fits the budget while the flight exceeds it. A reply without tool requests reaches `END`.

**ReAct** is often expanded as reasoning and acting. In this example, we can inspect the model's tool requests, the application's returned results, and the final answer. The new capability comes from revisiting the model node after each tool round.

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-01 -->
```python
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
```

**What happens here**

**TypedDict** describes our state fields.

**StateGraph** builds the workflow, while START and END mark its boundaries. Annotated attaches add_messages to the messages field, giving message updates their own merge rule.

**Result:** The helpers are ready; no graph has run.

### Import the model and messages

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-02 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
```

**What happens here**

These are the same model and message helpers we used in Part I. The graph will decide when to call the model.

**Result:** We can prepare the connection.

### Connect to our existing Groq model

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-03 -->
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

load_dotenv makes the API key available.

**init_chat_model** creates our reusable model object; it has not generated an answer yet.

**Result:** The model is ready. Running its node will make a provider request.

### Import the tool helpers

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-04 -->
```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
```

**What happens here**

ToolNode executes requests against the tools we supply. tools_condition checks whether the latest model reply contains tool calls.

**Result:** We can keep requesting a function separate from executing it.

### Describe the travel request

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-05 -->
```python
class TravelState(TypedDict):
    origin: str
    destination: str
    budget: int
    messages: Annotated[list, add_messages]
    status: str
```

**What happens here**

TravelState keeps three request facts alongside the conversation and status. A budget update would replace its earlier value; new messages merge through add_messages.

**Result:** The model can reuse the request context on every visit.

### Find the available route IDs

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-06 -->
```python
@tool
def find_routes(origin: str, destination: str) -> list[str]:
    """Find sample route IDs between an origin and destination."""
    if origin.lower() == "mumbai" and destination.lower() == "goa":
        return ["TRAIN-01", "FLIGHT-01"]
    return []
```

**What happens here**

The first tool returns identifiers, not prices. This keeps the dependency visible: the model must obtain the IDs before requesting their details.

**Result:** The sample Mumbai-to-Goa search can identify two routes.

### Read a route's details

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-07 -->
```python
@tool
def get_route_details(route_id: str) -> dict:
    """Read the sample price, duration, and availability for a returned route ID."""
    routes = {
        "TRAIN-01": {"mode": "train", "price": 900, "duration": "10 hours", "available": True},
        "FLIGHT-01": {"mode": "flight", "price": 4500, "duration": "1.5 hours", "available": True},
    }
    return routes[route_id]
```

**What happens here**

The second tool supplies the facts needed for comparison. It expects an ID returned by the first tool. All records are local sample data.

**Result:** The application can return prices and durations without a travel-service setup.

### Bind both tools

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-08 -->
```python
travel_tools = [find_routes, get_route_details]
tool_model = model.bind_tools(travel_tools)
```

**What happens here**

Both permitted functions are described to the model. The model can choose which one to request at each visit.

**Result:** The tool-enabled model is ready.

### Let the model decide what it needs next

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-09 -->
```python
def assistant(state: TravelState) -> dict:
    reply = tool_model.invoke([
        SystemMessage(
            f"Compare {state['origin']} to {state['destination']} travel "
            f"within a budget of INR {state['budget']}. Find routes first, "
            "then get details for the returned IDs before comparing. Use the tools."
        ),
        *state["messages"],
    ])
    status = "working" if reply.tool_calls else "answered"
    return {"messages": [reply], "status": status}
```

**What happens here**

Every visit includes the accumulated tool results. A tool request keeps the work going; a reply without requests is the final answer. The node returns only its new message and status.

**Result:** The next decision can depend on the latest facts.

### Connect the model-and-tool loop

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-10 -->
```python
builder = StateGraph(TravelState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(travel_tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant", tools_condition, {"tools": "tools", END: END}
)
builder.add_edge("tools", "assistant")
graph = builder.compile()
```

**What happens here**

The important changed edge is tools back to assistant. The model can ask again after reading a result. A final reply routes to END.

**Result:** We have a loop with a clear stopping route.

### Run a comparison with an execution limit

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-11 -->
```python
travel_input = {
    "origin": "Mumbai", "destination": "Goa", "budget": 2000,
    "messages": [HumanMessage("Compare the available trains and flights within my budget.")],
    "status": "new",
}
response = graph.invoke(travel_input, {"recursion_limit": 12})
print(response["messages"][-1].text)
```

**What happens here**

The application supplies the cities and budget. Our sample train fits the budget and the sample flight exceeds it. The exact wording and grouping of calls can vary. recursion_limit guards graph execution; it does not guarantee a useful answer if the model keeps requesting tools.

**Result:** The completed answer can compare facts from several lookups.

### Read the visible execution trace

<!-- snippet: code/Part II Connecting the dots/5-ReActive-Graph.ipynb#p2-5-step-12 -->
```python
for message in response["messages"]:
    print(message.type, message.text)
    if getattr(message, "tool_calls", None):
        print("Requested calls:", message.tool_calls)
```

**What happens here**

Look for route discovery, returned IDs, requests for details, returned records, and the final comparison. ToolMessage IDs tie each result to its request.

**Result:** The loop is visible in the saved messages.

## Check your understanding

1. Why does the first lookup not return the final comparison?
2. What changed from the one-round tool graph?
3. How does the assistant receive earlier results?
4. What makes the normal loop finish?

## Where we go next

Next a student will ask follow-up questions that rely on saved conversation context.

Complete notebook: [5-ReActive-Graph.ipynb](../../../Part%20II%20Connecting%20the%20dots/5-ReActive-Graph.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/quickstart).
