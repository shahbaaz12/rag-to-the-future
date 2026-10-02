# Part II · Lesson 2 — Choose the path: working with edges

## A note from me

In our first graph, the next step was always obvious. Step one finished, then step two ran. Real applications are not always that tidy.

Sometimes we can do two checks together. Sometimes the answer to a check decides what happens next. Sometimes we need another attempt. Edges give us a way to describe those choices without hiding them inside one large function.

## Four kinds of flow

A sequential edge says “do this next.” Parallel branches say “these jobs can start independently.” A conditional edge chooses a destination from the current state. A loop uses that same choice to revisit a node until a clear stopping condition is met.

We will keep the examples local and small. There is no model call in this notebook, so the results come entirely from our Python functions.

## Set up the state and nodes

The logs field collects updates; value uses the usual replacement behaviour.

### Import the helpers

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-1-1 -->
```python
from operator import add
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
```

**What happens here**

operator.add will be our reducer for a list of log entries. This is a list-concatenation example, so we do not need message objects.

**Result:** The graph and reducer helpers are ready.

### Describe this workflow's state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-1-2 -->
```python
class FlowState(TypedDict):
    value: int
    logs: Annotated[list[str], add]
```

**What happens here**

FlowState describes a current number and our logs. A returned value replaces the previous value. A returned logs list is concatenated with the existing logs. Different keys can use different update rules.

**Result:** One state can hold a current number and a growing record of work.

### Create two simple steps

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-1-3 -->
```python
def increment(state: FlowState) -> dict:
    return {"value": state["value"] + 1, "logs": ["increment"]}


def double(state: FlowState) -> dict:
    return {"value": state["value"] * 2, "logs": ["double"]}
```

**What happens here**

Each function reads the current number and returns its own updates. These are ordinary functions; the graph decides when to call them.

**Result:** We have two reusable nodes.

## 1. Sequential

Here double needs the result of increment, so it belongs in the next round.

### Connect an ordered path

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-2-1 -->
```python
sequential_builder = StateGraph(FlowState)
sequential_builder.add_node("increment", increment)
sequential_builder.add_node("double", double)
sequential_builder.add_edge(START, "increment")
sequential_builder.add_edge("increment", "double")
sequential_builder.add_edge("double", END)
sequential_graph = sequential_builder.compile()
```

**What happens here**

The path runs increment before double. The second node receives the first node's updated value.

**Result:** The order of operations is explicit.

### Run the ordered steps

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-2-2 -->
```python
sequential_result = sequential_graph.invoke({"value": 2, "logs": []})
print(sequential_result)
```

**What happens here**

Two becomes three, then three becomes six. The reducer preserves both log entries.

**Result:** value is 6, and logs contains increment followed by double.

## 2. Parallel

Both checks read the same input. Neither needs to modify value, so each returns only a logs update.

### Return partial updates from independent checks

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-3-1 -->
```python
def check_stock(state: FlowState) -> dict:
    return {"logs": [f"stock checked for {state['value']} items"]}


def check_price(state: FlowState) -> dict:
    return {"logs": [f"price checked for {state['value']} items"]}


def finish_checks(state: FlowState) -> dict:
    return {"logs": ["both checks finished"]}
```

**What happens here**

Each check returns the field it actually changes. Returning the whole state from both branches would also make both write value in the same round, and that key has no reducer for simultaneous writes.

**Result:** The two logs updates can be combined without conflicting writes to value.

### Split, then wait for both branches

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-3-2 -->
```python
parallel_builder = StateGraph(FlowState)
parallel_builder.add_node("stock", check_stock)
parallel_builder.add_node("price", check_price)
parallel_builder.add_node("finish", finish_checks)
parallel_builder.add_edge(START, "stock")
parallel_builder.add_edge(START, "price")
# This join waits for both named nodes before running finish.
parallel_builder.add_edge(["stock", "price"], "finish")
parallel_builder.add_edge("finish", END)
parallel_graph = parallel_builder.compile()
```

**What happens here**

Two outgoing edges activate the independent checks in the same super-step. The list in add_edge creates a join that waits for both before running finish. Parallel execution does not promise which check completes first.

**Result:** The finishing node sees the combined updates.

### Inspect the combined result

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-3-3 -->
```python
parallel_result = parallel_graph.invoke({"value": 2, "logs": []})
print(parallel_result)
```

**What happens here**

The number remains two. We inspect the log entries rather than assuming a timing order for the independent checks.

**Result:** Both check entries are present before the final completion entry.

## 3. Conditional

Now the next node depends on the updated number.

### Choose a destination from state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-4-1 -->
```python
def choose_next(state: FlowState) -> str:
    return "double" if state["value"] < 3 else "stop"
```

**What happens here**

This routing function returns a label. It chooses a path; it does not return a state update.

**Result:** We can route to double or stop.

### Map those labels to destinations

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-4-2 -->
```python
conditional_builder = StateGraph(FlowState)
conditional_builder.add_node("increment", increment)
conditional_builder.add_node("double", double)
conditional_builder.add_edge(START, "increment")
conditional_builder.add_conditional_edges(
    "increment", choose_next, {"double": "double", "stop": END}
)
conditional_builder.add_edge("double", END)
conditional_graph = conditional_builder.compile()
```

**What happens here**

add_conditional_edges runs choose_next after increment. The mapping explains where each label leads. We use this choice instead of also adding an unconditional edge from increment.

**Result:** Only the selected next path runs.

### Try both branches

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-4-3 -->
```python
print(conditional_graph.invoke({"value": 1, "logs": []}))
print(conditional_graph.invoke({"value": 5, "logs": []}))
```

**What happens here**

Starting at one gives two after increment, so double runs and produces four. Starting at five gives six, which routes straight to END.

**Result:** The final values are 4 and 6, with different logs.

## 4. Iterative

A loop is a route back to an earlier node. Give it an exit before you run it.

### Define the stopping decision

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-5-1 -->
```python
def keep_counting(state: FlowState) -> str:
    return "again" if state["value"] < 3 else "done"
```

**What happens here**

The condition is based on state that increment changes on every visit. Without progress towards a stopping condition, a loop could continue until the execution limit is reached.

**Result:** The loop will stop when value reaches three.

### Connect the bounded loop

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-5-2 -->
```python
loop_builder = StateGraph(FlowState)
loop_builder.add_node("increment", increment)
loop_builder.add_edge(START, "increment")
loop_builder.add_conditional_edges(
    "increment", keep_counting, {"again": "increment", "done": END}
)
loop_graph = loop_builder.compile()
```

**What happens here**

The again label revisits increment. The done label ends the run. We can now read both the repetition and its exit directly from the connections.

**Result:** The graph has a loop with an explicit end.

### Run with an extra execution limit

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-5-3 -->
```python
loop_result = loop_graph.invoke(
    {"value": 0, "logs": []}, {"recursion_limit": 10}
)
print(loop_result)
```

**What happens here**

The node runs three times. recursion_limit is an additional limit on graph execution steps; exceeding it raises an error rather than returning a successful answer.

**Result:** value is 3 and the log contains three increment entries.

## Check your understanding

1. Why do parallel branches return partial updates?
2. What does the join wait for?
3. How does a conditional edge differ from a normal edge?
4. What makes this loop stop?

## Where we go next

Next we will put our familiar model.invoke call inside a graph node.

Complete notebook: [2-working-with-edges.ipynb](../../../Part%20II%20Connecting%20the%20dots/2-working-with-edges.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/graph-api).
