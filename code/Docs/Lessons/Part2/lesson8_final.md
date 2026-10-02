# Part II · Lesson 8 — Pause and ask a person

## A note from me

Letting a model suggest an action is one thing. Letting an application carry it out is another. Sometimes we want a person to review what will happen before the next step runs.

We do not need to ask an LLM to demonstrate this. A plain graph can pause a request, show the proposed action, and wait for a human decision. That makes the boundary easy to see.

## What we are building

A demo request to order two laptops. The graph pauses before deciding whether to take the approved path. We will try approval in one thread and rejection in another.

No purchase is made. The final nodes only return text describing which demo path ran. In a real application, a purchasing API would belong after approval, with the application's own permission checks.

## Three pieces that work together

interrupt pauses the graph and exposes a review payload. A checkpointer saves the state needed to continue. Command(resume=...) supplies the decision using the same thread ID.

On resume, the interrupted node starts again from its beginning; interrupt then returns the supplied decision. Keep irreversible side effects out of the code before interrupt. An API action after approval also needs protection against repeated execution in a real system.

## Set up a local approval workflow

No model key is needed for this notebook.

### Import the approval helpers

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-1-1 -->
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
```

**What happens here**

We use the same graph and checkpointing pieces, plus interrupt and Command for the pause-and-resume interaction.

**Result:** The local workflow helpers are ready.

### Describe the review state

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-1-2 -->
```python
class ApprovalState(TypedDict):
    request: str
    approved: bool
    result: str
```

**What happens here**

ApprovalState gives our review record three fields. request says what is proposed. approved records the human decision, and result records which final path ran. Each field uses normal replacement behaviour.

**Result:** We have a small review record.

### Pause before deciding

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-1-3 -->
```python
def review_request(state: ApprovalState) -> dict:
    decision = interrupt({
        "request": state["request"],
        "question": "Approve this demo request? Resume with True or False.",
    })
    if not isinstance(decision, bool):
        raise ValueError("Approval must be True or False.")
    return {"approved": decision}
```

**What happens here**

interrupt exposes the proposed request and pauses execution. The line after it runs only after the graph resumes. We accept an actual boolean, so text such as the string False cannot accidentally act as approval.

**Result:** The node waits for an explicit True or False decision.

### Define the two possible outcomes

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-1-4 -->
```python
def approved_request(state: ApprovalState) -> dict:
    # Demo only: no external order or payment is created.
    return {"result": f"Approved demo request: {state['request']}"}


def rejected_request(state: ApprovalState) -> dict:
    return {"result": "Request rejected. No action taken."}
```

**What happens here**

We keep the approved and rejected paths separate. Both are local functions; the approved path does not call a shop, send a message, or spend money.

**Result:** Each outcome can provide a clear final result.

### Route according to the human decision

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-1-5 -->
```python
def approval_route(state: ApprovalState) -> str:
    return "approved" if state["approved"] else "rejected"
```

**What happens here**

This routing function uses the decision stored by the review node. It chooses one path rather than running both.

**Result:** The graph has an explicit approval branch.

## Compile with a checkpointer

The saved state is what makes a later resume possible.

### Connect review and outcomes

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-2-1 -->
```python
builder = StateGraph(ApprovalState)
builder.add_node("review", review_request)
builder.add_node("approved", approved_request)
builder.add_node("rejected", rejected_request)
builder.add_edge(START, "review")
builder.add_conditional_edges(
    "review", approval_route,
    {"approved": "approved", "rejected": "rejected"},
)
builder.add_edge("approved", END)
builder.add_edge("rejected", END)
```

**What happens here**

Every request reaches review first. Once the review returns its decision, the conditional edge chooses the approved or rejected node, then ends.

**Result:** Neither final path can bypass the review node.

### Attach memory for the paused run

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-2-2 -->
```python
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)
review_config = {"configurable": {"thread_id": "order-review-1"}}
```

**What happens here**

The checkpointer stores the paused workflow. review_config identifies the run we must return to when supplying a decision. This storage is still in-memory, so a kernel restart loses the pending review.

**Result:** We can pause and resume this thread within the current process.

## Try approval, then rejection

The decision is supplied explicitly in the notebook. A real UI would wait for the reviewer to choose it.

### Start the request and inspect the pause

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-3-1 -->
```python
paused = graph.invoke(
    {"request": "Order two laptops", "approved": False, "result": ""},
    review_config,
)
print("Review needed:", paused["__interrupt__"][0].value)
```

**What happens here**

The run reaches interrupt and returns the review payload. The initial approved=False is only a default in the record; it is not the human's decision. The final outcome nodes have not run yet.

**Result:** The workflow is paused with an empty result.

### Resume the same thread with approval

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-3-2 -->
```python
approved_response = graph.invoke(Command(resume=True), review_config)
print(approved_response["result"])
```

**What happens here**

Command supplies True to the paused interrupt using the same thread ID. review_request returns the decision, and the graph selects the approved path.

**Result:** The approved demo message is returned; no external order is placed.

### Start another review

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-3-3 -->
```python
reject_config = {"configurable": {"thread_id": "order-review-2"}}
rejected_pause = graph.invoke(
    {"request": "Order two laptops", "approved": False, "result": ""},
    reject_config,
)
print("Review needed:", rejected_pause["__interrupt__"][0].value)
```

**What happens here**

We use a new thread so this example starts its own review. It does not modify the approved thread.

**Result:** The second request is paused independently.

### Resume with rejection

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-3-4 -->
```python
rejected_response = graph.invoke(Command(resume=False), reject_config)
print(rejected_response["result"])
```

**What happens here**

False is returned by interrupt for the second thread. The router chooses rejected, so the approved path is never entered for this request.

**Result:** Request rejected. No action taken.

## Check your understanding

1. Which three pieces make interrupt and resume work?
2. Why must the resume use the same thread ID?
3. Does the interrupted node continue only from the next line?
4. Which path runs when the reviewer sends False?

## Where we go next

You can now assemble, route, remember, stream, and pause a workflow. Return to the Part II map and try changing one connection at a time before adding a more complicated application.

Complete notebook: [7-human-in-loop.ipynb](../../../Part%20II%20Connecting%20the%20dots/7-human-in-loop.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/interrupts).
