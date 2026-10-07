# Part II · Lesson 8 — Approve or reject a refund

## What we are building

We will build a refund review workflow for order ORD-102: a customer requests ₹5,000 because an item arrived damaged. The graph prepares the request, pauses so a person can review the details, then follows the approval or rejection path. The demo records the outcome in local state; no actual money moves, and this notebook uses ordinary Python nodes without a model call.

<div data-graph-preview="builder"></div>

**The idea behind it** is to add a person's decision to the graph design we have learned. Our earlier lessons gave model nodes the ability to write answers and request information. An intelligent workflow can also need a person to decide whether the next step should run. Here we focus on that pause and decision using a small Python example.

We already know how a conditional edge chooses a path from state. The new piece is waiting for a decision that is not available yet. The graph saves its progress, exposes the request for review, and continues after we supply the person's response.

**Our workflow** has three stages:

1. `prepare` checks the amount and marks the request as awaiting review.
2. `review` pauses with the order, amount, and reason. We resume the saved request with `True` for approval or `False` for rejection.
3. The conditional edge selects `process` or `reject`. The selected node records its outcome, then the graph ends.

**interrupt** exposes the review details and pauses execution inside the review node.

**A checkpointer** stores progress while the workflow waits.

**Command(resume=...)** supplies the decision using the same thread ID. On resume, the interrupted node starts again from its beginning, so actions that should happen only once belong outside the code before `interrupt`. Our processing step sits after the approval branch.

**The result** is a workflow whose next action depends on a recorded human decision. We will try both outcomes: `refund processed` after approval and `refund rejected` after rejection.

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-01 -->
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
```

**What happens here**

**TypedDict** describes our state fields.

**StateGraph** builds the workflow, while START and END mark its boundaries.

**Result:** The helpers are ready; no graph has run.

### Describe the refund request

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-02 -->
```python
class RefundState(TypedDict):
    order_id: str
    amount: int
    reason: str
    approved: bool
    status: str
```

**What happens here**

RefundState carries three request facts, the reviewer's decision, and the workflow status. All five fields use replacement behavior. approved starts as a placeholder and changes only after the reviewer responds.

**Result:** The review payload and outcome have clear places in state.

### Prepare the request for review

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-03 -->
```python
def prepare_refund(state: RefundState) -> dict:
    if state["amount"] <= 0:
        raise ValueError("The refund amount must be positive.")
    return {"status": "awaiting review"}
```

**What happens here**

The preparation step checks our sample amount and returns only status. order_id, amount, and reason remain available for review.

**Result:** The request is ready for the pause.

### Pause and request an explicit decision

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-04 -->
```python
def review_refund(state: RefundState) -> dict:
    decision = interrupt({
        "order_id": state["order_id"], "amount_inr": state["amount"],
        "reason": state["reason"], "question": "Approve this refund?",
    })
    if not isinstance(decision, bool):
        raise ValueError("Resume with True or False.")
    return {"approved": decision, "status": "reviewed"}
```

**What happens here**

interrupt pauses before a decision is available. When resumed, it returns the supplied value. We require a real boolean so the text False cannot accidentally act as approval through Python truthiness.

**Result:** The graph waits for a person's decision and then records it.

### Define approval and rejection outcomes

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-05 -->
```python
def process_refund(state: RefundState) -> dict:
    # Demo only: record the result without moving money.
    return {"status": "refund processed"}


def reject_refund(state: RefundState) -> dict:
    return {"status": "refund rejected"}
```

**What happens here**

Only the approval branch reaches process_refund. Both functions merely update this local demo record. The rejection branch records its own result without processing a refund.

**Result:** The two possible outcomes are explicit.

### Choose the branch after review

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-06 -->
```python
def refund_route(state: RefundState) -> str:
    return "approve" if state["approved"] else "reject"
```

**What happens here**

The routing function reads the saved boolean decision. It returns a label rather than changing the state.

**Result:** The review result selects one final step.

### Register and connect the refund workflow

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-07 -->
```python
builder = StateGraph(RefundState)
builder.add_node("prepare", prepare_refund)
builder.add_node("review", review_refund)
builder.add_node("process", process_refund)
builder.add_node("reject", reject_refund)
builder.add_edge(START, "prepare")
builder.add_edge("prepare", "review")
builder.add_conditional_edges(
    "review", refund_route, {"approve": "process", "reject": "reject"}
)
builder.add_edge("process", END)
builder.add_edge("reject", END)
```

**What happens here**

Preparation precedes review. The conditional edge selects process or reject, and both outcomes end. The review node must finish with a decision before either final node can run.

**Result:** The graph describes the approval boundary.

### Attach memory and prepare the sample request

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-08 -->
```python
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)
refund_input = {
    "order_id": "ORD-102", "amount": 5000, "reason": "Item arrived damaged.",
    "approved": False, "status": "new",
}
approve_config = {"configurable": {"thread_id": "refund-review-1"}}
```

**What happens here**

The checkpointer stores the interrupted workflow. The thread ID identifies this review. False is only the initial placeholder; it does not bypass the pause or automatically reject the request.

**Result:** The graph can pause and later resume this exact request.

### Start the workflow and inspect the pause

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-09 -->
```python
paused = graph.invoke(refund_input, approve_config)
print(paused["__interrupt__"][0].value)
print(graph.get_state(approve_config).values["status"])
```

**What happens here**

Preparation runs and review pauses. The interrupt payload contains the order, amount, and reason. The saved status remains awaiting review because the review node has not returned its update yet.

**Result:** Neither process_refund nor reject_refund has run.

### Resume with approval

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-10 -->
```python
approved_response = graph.invoke(Command(resume=True), approve_config)
print(approved_response["approved"], approved_response["status"])
```

**What happens here**

We resume with True and the same thread. The review node receives the decision, then the approval branch reaches the demo refund function.

**Result:** The final result is True and refund processed.

### Try rejection in another review

<!-- snippet: code/Part II Connecting the dots/7-human-in-loop.ipynb#p2-8-step-11 -->
```python
reject_config = {"configurable": {"thread_id": "refund-review-2"}}
graph.invoke(refund_input, reject_config)
rejected_response = graph.invoke(Command(resume=False), reject_config)
print(rejected_response["approved"], rejected_response["status"])
```

**What happens here**

A separate thread starts and pauses its own copy of the request. False then selects rejection. Using another thread keeps this experiment independent of the already completed approval.

**Result:** The final result is False and refund rejected.

## Check your understanding

1. What information does the reviewer see?
2. Why must the decision be a boolean?
3. Why does the resume use the same thread ID?
4. Does either final node run before review finishes?
5. Why is processing placed after approval?

## Where we go next

We now have fixed steps, branches, tools, loops, memory, streaming, and approval. These are useful foundations for the next part of the course.

Complete notebook: [7-human-in-loop.ipynb](../../../Part%20II%20Connecting%20the%20dots/7-human-in-loop.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/interrupts).
