# Part II · Lesson 2 — Choose the path: food delivery

## A note from me

You place a food order. Before the application confirms it, a few things need to happen. Is the address valid? Is the restaurant open? Is anyone available to deliver it?

Some checks must happen in order. Others can happen together. Their results decide whether we continue, stop, or try again. That is what edges help us describe.

Just follow along. We will understand one connection at a time, then put the pieces together. Everything here uses local sample data.

## Four kinds of flow

| Flow | Our example |
|---|---|
| Sequential | Read the order, then validate the address. |
| Parallel | Check the restaurant and the preferred rider independently. |
| Conditional | Restaurant open: find a rider. Closed: reject the order. |
| Bounded loop | Try another candidate, stopping on success or after three attempts. |

## Our state and its update rules

We use five top-level fields. order holds the input details, checks collects availability results, attempts counts the fallback search, status records progress, and logs records the steps.

A reducer combines an existing value with a returned update. It is a function, so there is no fixed list of every possible reducer. Let’s cover the common behaviours with a small, useful example.

### Import the graph and update helpers

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-01 -->
```python
from operator import add
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Overwrite
```

**What happens here**

We add operator.add for joining lists, Annotated for attaching update rules, and Overwrite for an explicit reset later. START, END, and StateGraph remain the familiar building blocks.

**Result:** The graph and reducer helpers are available.

### Merge separate check results

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-02 -->
```python
def merge_checks(current: dict, update: dict) -> dict:
    return {**current, **update}
```

**What happens here**

merge_checks preserves existing dictionary entries and adds the new entries. An update to an existing key replaces that key's value. Our parallel checks will use different keys, avoiding a decision based on which branch writes last.

**Result:** Restaurant and rider results can live together in one dictionary.

### Keep the larger attempt count

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-03 -->
```python
def keep_larger(current: int, update: int) -> int:
    return max(current, update)
```

**What happens here**

keep_larger compares the stored count with the incoming count and keeps the larger one. This small function gives LangGraph an explicit two-argument reducer.

**Result:** An older, smaller count cannot move our attempt counter backwards.

### Describe the delivery state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-04 -->
```python
class DeliveryState(TypedDict):
    order: dict
    checks: Annotated[dict[str, bool], merge_checks]
    attempts: Annotated[int, keep_larger]
    status: str
    logs: Annotated[list[str], add]
```

**What happens here**

DeliveryState shows four update patterns. order and status replace old values. checks merges dictionaries. attempts keeps the larger count through keep_larger. logs joins lists through add. Each rule belongs to one field, not the whole state.

**Result:** We have a five-field record with explicit rules where accumulation is needed.

### Prepare sample input

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-05 -->
```python
sample_order = {
    "order": {
        "restaurant": "Spice Kitchen", "address": " 12 Park Road ",
        "preferred_rider": "Asha", "rider_responses": [False, True, False],
    },
    "checks": {}, "attempts": 0, "status": "new", "logs": [],
}
```

**What happens here**

order contains the details needed by our functions. The candidate responses are sample data: unavailable, available, unavailable. They make the later retry example repeatable.

**Result:** We can run every graph without an API or model.

## 1. Sequential — do this, then that

Read and clean the address first. Validate the cleaned address second. The second node needs the first node's update.

### Read and validate the order

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-06 -->
```python
def read_order(state: DeliveryState) -> dict:
    order = {**state["order"], "address": state["order"]["address"].strip()}
    return {"order": order, "logs": ["Order read."]}


def validate_address(state: DeliveryState) -> dict:
    if not state["order"]["address"]:
        raise ValueError("A delivery address is required.")
    return {"status": "validated", "logs": ["Address validated."]}
```

**What happens here**

read_order copies the nested order and cleans its address. validate_address checks the updated value. Both return partial updates. The log reducer keeps each new entry; we do not resend the old log.

**Result:** A valid address is cleaned and the order becomes validated.

### Connect and run the sequential graph

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-07 -->
```python
sequential_builder = StateGraph(DeliveryState)
sequential_builder.add_node("read", read_order)
sequential_builder.add_node("validate", validate_address)
sequential_builder.add_edge(START, "read")
sequential_builder.add_edge("read", "validate")
sequential_builder.add_edge("validate", END)
sequential_result = sequential_builder.compile().invoke(sample_order)
print(sequential_result)
prepared_order = {**sequential_result, "logs": []}
```

**What happens here**

The edge ensures validation sees the cleaned address. prepared_order starts a new graph input with an empty log. Creating this fresh input is different from returning a node update inside a running graph.

**Result:** The address is 12 Park Road and status is validated.

## 2. Parallel — independent checks

Checking whether the restaurant is open does not require the rider's answer. Checking the rider does not require the restaurant's answer. We can run both in the same super-step and wait for their results.

Both nodes contribute to checks and logs. The dictionary reducer keeps the separate restaurant and rider keys; the list reducer keeps both log entries.

### Define the two checks

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-08 -->
```python
def check_restaurant(state: DeliveryState) -> dict:
    restaurants = {"Spice Kitchen": True, "Night Cafe": False}
    is_open = restaurants.get(state["order"]["restaurant"], False)
    return {"checks": {"restaurant": is_open}, "logs": ["Restaurant checked."]}


def check_rider(state: DeliveryState) -> dict:
    riders = {"Asha": True, "Ravi": False}
    available = riders.get(state["order"]["preferred_rider"], False)
    return {"checks": {"rider": available}, "logs": ["Rider checked."]}
```

**What happens here**

Each lookup returns only its result and a new log entry. They leave order, attempts, and status alone. These partial updates can be merged even though both nodes finish in the same round.

**Result:** The two checks can safely contribute separate results.

### Define the step after both checks

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-09 -->
```python
def finish_checks(state: DeliveryState) -> dict:
    return {"status": "checks complete", "logs": ["Both checks finished."]}
```

**What happens here**

finish_checks records completion. The edges will make it wait for both checks, so it receives their combined state.

**Result:** We have a finishing node for the parallel example.

### Split the path and join the results

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-10 -->
```python
parallel_builder = StateGraph(DeliveryState)
parallel_builder.add_node("restaurant", check_restaurant)
parallel_builder.add_node("rider", check_rider)
parallel_builder.add_node("finish", finish_checks)
parallel_builder.add_edge(START, "restaurant")
parallel_builder.add_edge(START, "rider")
# Wait for both checks before running finish.
parallel_builder.add_edge(["restaurant", "rider"], "finish")
parallel_builder.add_edge("finish", END)
parallel_graph = parallel_builder.compile()
```

**What happens here**

Both checks start independently. The list passed to add_edge creates a join that waits for both named nodes. We should not treat the order of their log entries as a promise about completion timing.

**Result:** The final step sees both availability results.

### Inspect the parallel result

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-11 -->
```python
parallel_result = parallel_graph.invoke(prepared_order)
print(parallel_result["checks"])
print(parallel_result["logs"])
```

**What happens here**

The checks dictionary contains restaurant True and rider True for our sample. Both log entries survive, followed by the finishing entry.

**Result:** The reducers combine simultaneous updates without losing a check.

## Partial versus full returns — why parallel work makes this matter

A node's return is an update, even when it contains the full state. Returning every field makes the node a writer to every field.

| Return | Effect |
|---|---|
| Only changed fields | Untouched fields keep their existing values. |
| Full state with replacement fields, sequentially | Can work with replacement fields, but writes every field again. |
| Full state containing an accumulating log | Old entries can be appended again. |
| Full state from both parallel branches | Both write replacement fields such as order and status in the same round. LangGraph raises InvalidUpdateError. |

A reducer does not make any full return safe. It still applies its rule to everything you return. Keep each parallel node's update small and intentional.

### Show a full return that resends an old log

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-12 -->
```python
def full_status_update(state: DeliveryState) -> dict:
    return {**state, "status": "reviewed"}

full_builder = StateGraph(DeliveryState)
full_builder.add_node("review", full_status_update)
full_builder.add_edge(START, "review")
full_builder.add_edge("review", END)
full_result = full_builder.compile().invoke(
    {**prepared_order, "logs": ["Existing entry."]}
)
print(full_result["logs"])
```

**What happens here**

The full return sends Existing entry again. add combines the stored log with that returned log, so the entry appears twice. A partial return containing only status would keep the original log once.

**Result:** This sequential example runs, but its full return duplicates accumulated data.

### Define the unsafe parallel versions

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-13 -->
```python
def full_restaurant_check(state: DeliveryState) -> dict:
    return {**state, **check_restaurant(state)}


def full_rider_check(state: DeliveryState) -> dict:
    return {**state, **check_rider(state)}
```

**What happens here**

Both functions copy every field into their return. Even though order and status were not changed, both nodes now write those fields. Their ordinary replacement channels do not accept simultaneous writes.

**Result:** These definitions let us inspect the mistake without stopping the notebook.

### Build the demonstration of conflicting writes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-14 -->
```python
unsafe_builder = StateGraph(DeliveryState)
unsafe_builder.add_node("restaurant", full_restaurant_check)
unsafe_builder.add_node("rider", full_rider_check)
unsafe_builder.add_edge(START, "restaurant")
unsafe_builder.add_edge(START, "rider")
unsafe_builder.add_edge("restaurant", END)
unsafe_builder.add_edge("rider", END)
unsafe_graph = unsafe_builder.compile()
# Optional: uncomment to see InvalidUpdateError for simultaneous full returns.
# unsafe_graph.invoke(prepared_order)
```

**What happens here**

Building a graph does not execute its nodes. The call is deliberately commented because it demonstrates an error. The fix is to use the earlier partial-return checks, not to hide the error inside try/except.

**Result:** The main notebook remains runnable; the failing case is available as an explicit experiment.

## 3. Conditional — choose one next step

A conditional edge chooses the next step based on a result. Keep this decision simple: **is the restaurant open?**

check_restaurant records True or False. True runs find_rider. False runs reject_order. We do not run both branches. Think of an ordinary Python if/else.

| Restaurant result | Next node |
|---|---|
| Open | find_rider |
| Closed | reject_order |

The rider retry loop belongs in the next section. Here we make only one rider lookup.

### Define the two branch outcomes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-15 -->
```python
def find_rider(state: DeliveryState) -> dict:
    result = check_rider(state)
    result["status"] = "rider found" if result["checks"]["rider"] else "rider needed"
    return result


def reject_order(state: DeliveryState) -> dict:
    return {"status": "restaurant closed", "logs": ["Order rejected."]}
```

**What happens here**

find_rider reuses our lookup and adds its outcome. reject_order records the closed-restaurant result. Each working node returns a partial state update.

**Result:** The two possible next steps are ready.

### Choose the open or closed route

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-16 -->
```python
def restaurant_route(state: DeliveryState) -> str:
    if state["checks"]["restaurant"]:
        return "open"
    return "closed"
```

**What happens here**

The routing function reads the latest restaurant result and returns a label. It chooses a path; it does not return a state update.

**Result:** The decision has exactly two routes.

### Connect the conditional graph

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-17 -->
```python
conditional_builder = StateGraph(DeliveryState)
conditional_builder.add_node("restaurant", check_restaurant)
conditional_builder.add_node("find_rider", find_rider)
conditional_builder.add_node("reject_order", reject_order)
conditional_builder.add_edge(START, "restaurant")
conditional_builder.add_conditional_edges(
    "restaurant", restaurant_route,
    {"open": "find_rider", "closed": "reject_order"},
)
conditional_builder.add_edge("find_rider", END)
conditional_builder.add_edge("reject_order", END)
conditional_graph = conditional_builder.compile()
```

**What happens here**

After the check, add_conditional_edges asks restaurant_route which label to use. The mapping translates that label into a node name. Each selected branch ends after its work.

**Result:** Only the selected next step runs.

### Try both restaurant cases

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-18 -->
```python
open_result = conditional_graph.invoke(prepared_order)
closed_order = {**prepared_order["order"], "restaurant": "Night Cafe"}
closed_result = conditional_graph.invoke(
    {**prepared_order, "order": closed_order}
)
print("Open:", open_result["status"], open_result["logs"])
print("Closed:", closed_result["status"], closed_result["logs"])
```

**What happens here**

Spice Kitchen finds Asha. Night Cafe rejects the order and has no rider-lookup log. These are two independent runs with different input.

**Result:** The logs make the chosen branch visible.

## 4. Bounded loop — another attempt, with an exit

Assume the restaurant is open but we need another rider. Each visit tries the next candidate. Stop on success or after three attempts in total, including the first.

Our sample responses are False, True, False. The second candidate accepts, so the third should never be tried.

### Try the next candidate

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-19 -->
```python
def search_rider(state: DeliveryState) -> dict:
    attempt = state["attempts"] + 1
    responses = state["order"]["rider_responses"]
    available = responses[attempt - 1] if attempt <= len(responses) else False
    return {
        "attempts": attempt, "checks": {"rider": available},
        "logs": [f"Rider attempt {attempt}: {available}"],
    }
```

**What happens here**

The count increases on every visit. keep_larger uses max to retain the larger returned count, while merge_checks updates only the rider result and preserves other check keys. A missing sample response means unavailable.

**Result:** Every visit makes progress towards success or the attempt limit.

### Decide whether to repeat or finish

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-20 -->
```python
def rider_route(state: DeliveryState) -> str:
    if state["checks"]["rider"]:
        return "assigned"
    if state["attempts"] >= 3:
        return "unavailable"
    return "again"


def confirm_dispatch(state: DeliveryState) -> dict:
    return {"status": "confirmed", "logs": ["Delivery confirmed."]}


def no_rider_available(state: DeliveryState) -> dict:
    return {"status": "no rider available", "logs": ["Search stopped."]}
```

**What happens here**

Success is checked first, including success on attempt three. Three failures stop the search; otherwise again revisits the search node. The two final nodes record the outcomes.

**Result:** The loop has clear success and exhaustion exits.

### Connect the loop

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-21 -->
```python
loop_builder = StateGraph(DeliveryState)
loop_builder.add_node("search", search_rider)
loop_builder.add_node("confirm", confirm_dispatch)
loop_builder.add_node("no_rider", no_rider_available)
loop_builder.add_edge(START, "search")
loop_builder.add_conditional_edges(
    "search", rider_route,
    {"again": "search", "assigned": "confirm", "unavailable": "no_rider"},
)
loop_builder.add_edge("confirm", END)
loop_builder.add_edge("no_rider", END)
loop_graph = loop_builder.compile()
```

**What happens here**

again creates the loop. The other routes record a result and end. This is a conditional edge with one destination pointing back to an earlier step.

**Result:** The graph can try again without searching forever.

### Run success and exhaustion cases

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-22 -->
```python
loop_result = loop_graph.invoke(prepared_order, {"recursion_limit": 12})
failed_order = {**prepared_order["order"], "rider_responses": [False, False, False]}
exhausted_result = loop_graph.invoke(
    {**prepared_order, "order": failed_order}, {"recursion_limit": 12}
)
print("Accepted:", loop_result["attempts"], loop_result["status"])
print("Exhausted:", exhausted_result["attempts"], exhausted_result["status"])
```

**What happens here**

The first run confirms after two attempts. The second stops after three failures. recursion_limit is an additional limit on graph super-steps, not a rider-attempt count. Our normal exit comes from rider_route.

**Result:** The bounded search has predictable stopping behaviour.

## Put the pieces together

Read and validate first, then check restaurant and rider availability in parallel. Once both checks finish, reject a closed restaurant, confirm an available rider, or start the bounded fallback search.

### Choose the combined next step

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-23 -->
```python
def dispatch_route(state: DeliveryState) -> str:
    if not state["checks"]["restaurant"]:
        return "closed"
    if state["checks"]["rider"]:
        return "ready"
    return "search"
```

**What happens here**

The restaurant result takes priority. A rider cannot make a closed restaurant prepare food. An open restaurant either confirms its preferred rider or searches for another.

**Result:** The combined decision uses both results.

### Register the combined workflow

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-24 -->
```python
dispatch_builder = StateGraph(DeliveryState)
for name, function in [
    ("read", read_order), ("validate", validate_address),
    ("restaurant", check_restaurant), ("rider", check_rider),
    ("finish", finish_checks), ("reject", reject_order),
    ("search", search_rider), ("confirm", confirm_dispatch),
    ("no_rider", no_rider_available),
]:
    dispatch_builder.add_node(name, function)
```

**What happens here**

We register the functions already introduced above. The short loop avoids repeating the same add_node call nine times.

**Result:** All working nodes are available.

### Connect preparation, parallel checks, and the decision

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-25 -->
```python
dispatch_builder.add_edge(START, "read")
dispatch_builder.add_edge("read", "validate")
dispatch_builder.add_edge("validate", "restaurant")
dispatch_builder.add_edge("validate", "rider")
dispatch_builder.add_edge(["restaurant", "rider"], "finish")
dispatch_builder.add_conditional_edges(
    "finish", dispatch_route,
    {"closed": "reject", "ready": "confirm", "search": "search"},
)
```

**What happens here**

Preparation is sequential. The two checks share the next round, and their join waits for both before routing.

**Result:** The first three flow patterns work together.

### Attach the bounded search and run the workflow

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-26 -->
```python
dispatch_builder.add_conditional_edges(
    "search", rider_route,
    {"again": "search", "assigned": "confirm", "unavailable": "no_rider"},
)
for final_node in ["reject", "confirm", "no_rider"]:
    dispatch_builder.add_edge(final_node, END)
dispatch_graph = dispatch_builder.compile()
dispatch_result = dispatch_graph.invoke(sample_order, {"recursion_limit": 20})
print(dispatch_result["status"], dispatch_result["logs"])
```

**What happens here**

The search uses the same stopping rules as before. With Asha available and Spice Kitchen open, this run confirms immediately and attempts stays zero.

**Result:** One clear workflow combines all four connection patterns.

## Resetting an accumulated field deliberately

Returning an empty list to an add-based reducer would append nothing; it would not clear the old log. Use Overwrite when you deliberately want to bypass that reducer for one update.

### Clear the log with an explicit overwrite

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-27 -->
```python
def clear_log(state: DeliveryState) -> dict:
    return {"logs": Overwrite(value=[])}

reset_builder = StateGraph(DeliveryState)
reset_builder.add_node("clear", clear_log)
reset_builder.add_edge(START, "clear")
reset_builder.add_edge("clear", END)
reset_result = reset_builder.compile().invoke(parallel_result)
print(reset_result["logs"])
```

**What happens here**

Overwrite replaces the stored log instead of calling add for this update. The other fields remain unchanged. We use one node for this reset; competing overwrite requests in parallel would need their own design.

**Result:** The final log is empty.

## The same reducer can mean different things

add joins lists, but it also adds numbers. A numeric field annotated with add should receive the amount to add, not the new total. Our attempts field uses keep_larger because search_rider returns the new total instead.

### Compare adding a delta with keeping a total

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-step-28 -->
```python
# A sum-based counter receives a delta: one additional attempt.
print(add(2, 1))  # 3
# Our counter receives the new total: three attempts so far.
print(keep_larger(2, 3))  # 3
print(keep_larger(3, 1))  # 3: a smaller update cannot lower it
```

**What happens here**

These are direct calls to the reducer functions, so we can see their behaviour without building another graph. For a sum reducer, returning 3 when the current count is 2 would produce 5. For keep_larger, returning 3 means keep the total at 3.

**Result:** Match the returned value to the field's reducer: a delta for addition, a total for our maximum reducer.

## The update rules we have seen

| Behaviour | Example | What happens |
|---|---|---|
| Replace | status: str | A sequential update replaces the earlier value. |
| Accumulate a list | logs with add | New entries join the existing list. Resending old entries duplicates them. |
| Merge a dictionary | checks with merge_checks | Separate check keys are preserved; an existing key can be updated. |
| Add numbers | An integer field with add | Each returned number is added to the stored value. |
| Keep the larger value | attempts with keep_larger | A smaller returned number does not reduce the stored count. |
| Explicitly bypass a reducer | Overwrite | One intentional update replaces an accumulated value. |
| Merge messages by ID | add_messages, in later lessons | New IDs append; an existing ID updates that message. |

The simplest habit is to return only the fields the node changes. Choose a reducer because it represents the data's meaning, rather than adding one merely to silence a parallel-write error.

## Check your understanding

1. Why must address validation follow reading?
2. What does the join wait for?
3. Why do the parallel nodes return partial updates?
4. Why does returning an unchanged old log duplicate entries?
5. Does a closed restaurant run find_rider?
6. What stops the rider loop?
7. How does Overwrite differ from returning an empty list?

## Where we go next

Next we will use an office email to put one LLM call inside a graph node.

Complete notebook: [2-working-with-edges.ipynb](../../../Part%20II%20Connecting%20the%20dots/2-working-with-edges.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/graph-api).
