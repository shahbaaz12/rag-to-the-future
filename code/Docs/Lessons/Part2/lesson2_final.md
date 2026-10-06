# Part II · Lesson 2 — Four ways to connect a graph

## A note from me

You already know how to put two nodes in a graph. Now let's make the connections do a little more: follow an order, run independent work together, choose a path, and try again.

We will build four small projects. Each uses ordinary Python functions and local sample data. No LLM, API key, or external service is needed. Just follow along and watch which node runs next.

## What we will learn

| Connection | Our project | The question it answers |
|---|---|---|
| Sequential | Pizza order pipeline | What must happen first? |
| Parallel | Trip dashboard | Which steps can work independently? |
| Conditional | Support ticket router | Which path should this input take? |
| Loop | OTP retry | Should we try again or stop? |

Each project has its own state and input. Run the shared imports once, then follow the snippets for the project you want to explore. None needs the result of another project.

## Shared imports

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-imports -->
```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
```

**What happens here**

`StateGraph`, `START`, and `END` are the same graph helpers we used in our first graph. `TypedDict` describes each project's state. We will reuse `Annotated` and `add_messages` when the parallel branches contribute messages.

**Result:** The shared helpers are ready. No graph has run yet.

## 1. Sequential — pizza order pipeline

**What we are building**

We will check a pizza order, calculate its total, apply a 10% coupon, and confirm the discounted amount. Each step follows the previous one. The coupon needs the calculated total; confirmation needs the discounted total.

<div data-graph-preview="sequential_builder"></div>

**Sequential edges** express an order: finish this node, then run that one. Our path is `START → validate_order → calculate_total → apply_coupon → confirm → END`.

### Describe the pizza state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-state -->
```python
class PizzaState(TypedDict):
    items: list[str]
    total: int
    status: str
```

**What happens here**

`PizzaState` carries just three fields: the pizza names, the current total in rupees, and the order status. These ordinary fields replace their old values when a node returns an update. We do not need a custom reducer.

**Result:** The pipeline has a small working record.

### Prepare a menu and an order

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-input -->
```python
menu = {"Margherita": 250, "Farmhouse": 350}
pizza_input = {
    "items": ["Margherita", "Farmhouse"],
    "total": 0,
    "status": "new",
}
```

**What happens here**

The local menu supplies prices. Our order contains one pizza of each kind, so its subtotal should be INR 600. Starting with `total` at zero makes the dependency on calculation easy to see.

**Result:** We have a repeatable order to run.

### Validate the order

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-validate -->
```python
def validate_order(state: PizzaState) -> dict:
    if not state["items"] or any(item not in menu for item in state["items"]):
        raise ValueError("Choose at least one pizza from the menu.")
    return {"status": "validated"}
```

**What happens here**

`validate_order` reads `items` and returns only `status`. An empty order or an unknown pizza stops this run with a validation error. For our valid sample, the original items and total stay in state.

**Result:** The sample order becomes validated.

### Calculate the total

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-total -->
```python
def calculate_total(state: PizzaState) -> dict:
    total = sum(menu[item] for item in state["items"])
    return {"total": total}
```

**What happens here**

`calculate_total` reads the validated items, looks up their prices, and returns the new `total`. It leaves `items` and `status` alone. Returning only the fields a node needs to change is a **partial update**.

**Result:** The total becomes INR 600.

### Apply the coupon

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-coupon -->
```python
def apply_coupon(state: PizzaState) -> dict:
    return {"total": state["total"] * 90 // 100}
```

**What happens here**

`apply_coupon` reads the total produced by the previous node and returns 90% of it. Whole-rupee arithmetic keeps this teaching example small. Applying the coupon before calculating the total would discount zero, and the later calculation would replace it with the full price.

**Result:** The sample total becomes INR 540.

### Confirm the discounted order

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-confirm -->
```python
def confirm(state: PizzaState) -> dict:
    return {"status": f"Confirmed at INR {state['total']}"}
```

**What happens here**

`confirm` reads the discounted total and returns a confirmation in `status`. It records the result locally.

**Result:** The status becomes `Confirmed at INR 540`.

### Register the pizza nodes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-nodes -->
```python
sequential_builder = StateGraph(PizzaState)
sequential_builder.add_node("validate_order", validate_order)
sequential_builder.add_node("calculate_total", calculate_total)
sequential_builder.add_node("apply_coupon", apply_coupon)
sequential_builder.add_node("confirm", confirm)
```

**What happens here**

Each name identifies one Python function in this graph. Registering nodes gives the builder its steps; the next snippet supplies their order.

**Result:** The four working nodes are registered.

### Connect the pipeline

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-edges -->
```python
sequential_builder.add_edge(START, "validate_order")
sequential_builder.add_edge("validate_order", "calculate_total")
sequential_builder.add_edge("calculate_total", "apply_coupon")
sequential_builder.add_edge("apply_coupon", "confirm")
sequential_builder.add_edge("confirm", END)
pizza_graph = sequential_builder.compile()
```

**What happens here**

`add_edge("calculate_total", "apply_coupon")` means the coupon node runs after calculation. Each next node sees the updated state. `compile()` creates the runnable graph after the connections are in place.

**Result:** The graph follows the target path shown above.

### Run the pizza order

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-pizza-run -->
```python
pizza_result = pizza_graph.invoke(pizza_input)
print(pizza_result)
```

**What happens here**

`invoke` runs the whole pipeline. The graph validates, calculates, discounts, and confirms in that order. Each node updates one field.

**Result:** The items are preserved, `total` is `540`, and `status` is `Confirmed at INR 540`.

| After this node | total | status |
|---|---|---|
| validate_order | 0 | validated |
| calculate_total | 600 | validated |
| apply_coupon | 540 | validated |
| confirm | 540 | Confirmed at INR 540 |

**Try it:** Move `apply_coupon` before `calculate_total` by changing the edges. What total will confirmation see? Restore the original connections before continuing.

## 2. Parallel — trip dashboard

**What we are building**

We will plan a trip to Goa, look up weather, flights, and hotels independently, then combine their results into one dashboard. The lookups return fixed local sample data. Each waits one second to simulate a slow service.

<div data-graph-preview="parallel_builder"></div>

**Fan-out** means one step leads to several independent steps. Here, `plan` starts all three lookups. **Fan-in** brings their paths together. Our explicit join makes `combine` wait for all three.

### Describe the trip state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-state -->
```python
import time

class TripState(TypedDict):
    city: str
    messages: Annotated[list, add_messages]
    report: str
```

**What happens here**

`TripState` holds the city, collected messages, and final report. All three parallel lookups will return an update to `messages`, so we reuse `add_messages` from our first graph. It combines their new messages. `city` and `report` remain ordinary replacement fields.

**Result:** The branches can safely contribute to one shared messages field.

### Plan the trip

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-plan -->
```python
def plan(state: TripState) -> dict:
    return {"messages": [f"Planning a trip to {state['city']}."]}
```

**What happens here**

`plan` reads `city` and adds one message. Once it finishes, the three outgoing edges can start the independent lookups.

**Result:** The trip has a starting message.

### Look up the weather

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-weather -->
```python
def get_weather(state: TripState) -> dict:
    time.sleep(1)
    return {"messages": [f"Weather in {state['city']}: sunny, 28 C."]}
```

**What happens here**

`get_weather` reads the city, waits one second, and returns only a new weather message. The value is sample data. It does not need a flight or hotel result.

**Result:** The weather lookup contributes one message.

### Look up flights

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-flights -->
```python
def get_flights(state: TripState) -> dict:
    time.sleep(1)
    return {"messages": [f"Flights to {state['city']}: 3 sample options."]}
```

**What happens here**

`get_flights` also reads only the city and returns one new message. It can work while the weather and hotel lookups wait.

**Result:** The flight lookup contributes one message.

### Look up hotels

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-hotels -->
```python
def get_hotels(state: TripState) -> dict:
    time.sleep(1)
    return {"messages": [f"Hotels in {state['city']}: 5 sample options."]}
```

**What happens here**

`get_hotels` follows the same pattern. Each lookup returns only `messages`, rather than copying the whole state. Copying it would make all three nodes write ordinary fields such as `city` and `report` in the same execution round, which causes conflicting updates.

**Result:** All three lookups have safe partial returns.

### Combine the lookup results

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-combine -->
```python
def combine(state: TripState) -> dict:
    report = "\n".join(message.content for message in state["messages"])
    return {"report": report}
```

**What happens here**

`combine` reads the accumulated messages and writes `report`. `add_messages` stores message objects, so we read their `.content` when preparing the text. The join we build next ensures all three lookup results are available.

**Result:** The final report includes planning, weather, flights, and hotels.

### Register the trip nodes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-nodes -->
```python
parallel_builder = StateGraph(TripState)
parallel_builder.add_node("plan", plan)
parallel_builder.add_node("get_weather", get_weather)
parallel_builder.add_node("get_flights", get_flights)
parallel_builder.add_node("get_hotels", get_hotels)
parallel_builder.add_node("combine", combine)
```

**What happens here**

The builder has one planning node, three independent lookup nodes, and one combining node. They share this project's small state.

**Result:** The five working nodes are registered.

### Fan out and wait for all three lookups

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-edges -->
```python
parallel_builder.add_edge(START, "plan")
parallel_builder.add_edge("plan", "get_weather")
parallel_builder.add_edge("plan", "get_flights")
parallel_builder.add_edge("plan", "get_hotels")
# Wait for every lookup before combining the results.
parallel_builder.add_edge(["get_weather", "get_flights", "get_hotels"], "combine")
parallel_builder.add_edge("combine", END)
trip_graph = parallel_builder.compile()
```

**What happens here**

The three edges from `plan` create the fan-out. Passing all three lookup names together to `add_edge` creates the join. They run in the same **super-step**, an execution round in which independent nodes can run together. Their message order is not a promise about which lookup finished first.

**Result:** The graph combines results only after every lookup finishes.

### Run and time the dashboard

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-trip-run -->
```python
trip_input = {"city": "Goa", "messages": [], "report": ""}
started = time.perf_counter()
trip_result = trip_graph.invoke(trip_input)
elapsed = time.perf_counter() - started
print(trip_result["report"])
print(f"Elapsed: {elapsed:.2f} seconds")
```

**What happens here**

`time.perf_counter()` measures the whole graph run. The three one-second waits overlap, so a typical run takes about one second plus graph overhead. Putting the same waits in a sequence would require about three seconds plus overhead. Your measured duration depends on the machine and execution settings.

**Result:** The report contains all three lookup results, and the measured duration is printed.

## 3. Conditional — support ticket router

**What we are building**

We will classify a support ticket and send it to exactly one handler: urgent, billing, or general. All handlers are plain Python functions that record a local outcome. The urgent handler marks the ticket as queued for human review.

<div data-graph-preview="conditional_builder"></div>

**A conditional edge** chooses the next node using the current data. This is an ordinary decision: classify the ticket, read its category, then follow the matching path.

### Describe the ticket state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-state -->
```python
class TicketState(TypedDict):
    text: str
    type: str
    response: str
```

**What happens here**

`TicketState` carries the original text, the category assigned by classification, and the selected handler's response. Only one handler will run, so these fields need no accumulating reducer.

**Result:** The router has three straightforward fields.

### Classify the ticket

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-classify -->
```python
def classify(state: TicketState) -> dict:
    text = state["text"].lower()
    if "urgent" in text:
        ticket_type = "urgent"
    elif "bill" in text:
        ticket_type = "billing"
    else:
        ticket_type = "general"
    print(f"classify -> {ticket_type}")
    return {"type": ticket_type}
```

**What happens here**

`classify` reads `text` and returns only `type`. The keyword rules are deliberately simple: urgent takes priority, a mention of bill goes to billing, and everything else goes to general. The print makes the decision visible.

**Result:** Each ticket receives one of three category labels.

### Define the three possible handlers

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-handlers -->
```python
def urgent_handler(state: TicketState) -> dict:
    print("urgent_handler")
    return {"response": "Queued for human review."}

def billing_handler(state: TicketState) -> dict:
    print("billing_handler")
    return {"response": "Sent to the billing queue."}

def general_handler(state: TicketState) -> dict:
    print("general_handler")
    return {"response": "Sent to the general support queue."}
```

**What happens here**

Each handler prints its own name and returns a response. These are local outcome messages. The edges will choose which handler runs; defining three functions does not mean all three execute.

**Result:** The three possible outcomes are ready.

### Read the category to choose a path

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-route -->
```python
def route(state: TicketState) -> str:
    return state["type"]  # "urgent", "billing", or "general"
```

**What happens here**

`route` reads the category already stored by `classify` and returns a route label. Classification updates the state; routing selects the next node.

**Result:** The route label matches one of the three handlers.

### Register classification and the handlers

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-nodes -->
```python
conditional_builder = StateGraph(TicketState)
conditional_builder.add_node("classify", classify)
conditional_builder.add_node("urgent_handler", urgent_handler)
conditional_builder.add_node("billing_handler", billing_handler)
conditional_builder.add_node("general_handler", general_handler)
```

**What happens here**

The graph has one classification step and three possible handler steps. The next snippet connects classification to the selected handler.

**Result:** The four working nodes are registered.

### Connect the three conditional routes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-edges -->
```python
conditional_builder.add_edge(START, "classify")
conditional_builder.add_conditional_edges(
    "classify", route,
    {"urgent": "urgent_handler", "billing": "billing_handler", "general": "general_handler"},
)
conditional_builder.add_edge("urgent_handler", END)
conditional_builder.add_edge("billing_handler", END)
conditional_builder.add_edge("general_handler", END)
ticket_graph = conditional_builder.compile()
```

**What happens here**

`add_conditional_edges` calls `route` after classification and uses the mapping to select a destination. For example, `"billing"` selects `billing_handler`. Each handler has a path to `END`; only the selected one runs for that input.

**Result:** The ticket chooses one path at runtime.

### Run one ticket for each category

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-ticket-run -->
```python
ticket_inputs = ["Urgent: the site is down", "My bill is incorrect", "How do I change my name?"]
for text in ticket_inputs:
    print(f"\nTicket: {text}")
    result = ticket_graph.invoke({"text": text, "type": "", "response": ""})
    print(result["response"])
```

**What happens here**

Each input starts a fresh run. The printed classifier result is followed by exactly one handler name. The urgent ticket does not also run billing or general.

**Result:** The traces are `classify → urgent_handler`, `classify → billing_handler`, and `classify → general_handler`.

## 4. Loop — OTP retry with a limit

**What we are building**

We will ask for a one-time password (OTP), verify it, and retry after a wrong entry. A correct code reaches `success`. Three wrong entries reach `locked`. We will supply a list of sample entries so the notebook runs without interactive input.

<div data-graph-preview="loop_builder"></div>

**A loop** is a conditional edge that points back to an earlier node. Our backward edge returns from `verify` to `ask_otp`. The decision has three routes: success, another attempt, or lockout.

### Describe the OTP state

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-state -->
```python
class OtpState(TypedDict):
    entries: list[str]
    otp: str
    tries: int
    verified: bool
    status: str
```

**What happens here**

`OtpState` carries five values. `entries` supplies simulated user input. `otp` holds the latest submitted code, `tries` counts submissions, `verified` stores the latest check, and `status` records the outcome. One node updates the counter in sequence, so `tries` is a plain integer.

**Result:** The loop has only the values needed to simulate and control retries.

### Take the next sample entry

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-ask -->
```python
def ask_otp(state: OtpState) -> dict:
    entries = state["entries"]
    # Repeat the last sample entry if the list runs out.
    otp = entries[state["tries"]] if state["tries"] < len(entries) else entries[-1]
    tries = state["tries"] + 1
    print(f"ask_otp: attempt {tries}")
    return {"otp": otp, "tries": tries}
```

**What happens here**

`ask_otp` reads the sample entries and current attempt count, then returns the next code and increased count. Our examples always provide at least one entry. Repeating the last entry lets a single wrong sample represent repeated failures.

**Result:** Each visit consumes an attempt, including the first visit.

### Verify the submitted code

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-verify -->
```python
def verify(state: OtpState) -> dict:
    verified = state["otp"] == "123456"
    print(f"verify: {verified}")
    return {"verified": verified}
```

**What happens here**

`verify` reads the current code and returns whether it matches our fixed sample code. The local comparison makes the success and retry paths easy to follow.

**Result:** The latest verification result becomes `True` or `False`.

### Choose success, retry, or lockout

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-route -->
```python
def otp_route(state: OtpState) -> str:
    if state["verified"]:
        return "correct"
    if state["tries"] >= 3:
        return "locked"
    return "retry"
```

**What happens here**

`otp_route` checks success first, so a correct third entry still succeeds. A wrong entry on attempt three locks the run. Earlier failures choose `retry`, which will point back to `ask_otp`.

**Result:** Every run has a normal exit: a correct code or three failed attempts.

### Record the two final outcomes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-outcomes -->
```python
def success(state: OtpState) -> dict:
    return {"status": "verified"}

def locked(state: OtpState) -> dict:
    return {"status": "locked"}
```

**What happens here**

Each final node writes only `status`. The success and lockout routes both finish the graph after recording their outcome.

**Result:** The final state shows how the loop ended.

### Register the OTP nodes

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-nodes -->
```python
loop_builder = StateGraph(OtpState)
loop_builder.add_node("ask_otp", ask_otp)
loop_builder.add_node("verify", verify)
loop_builder.add_node("success", success)
loop_builder.add_node("locked", locked)
```

**What happens here**

The graph has an input step, a verification step, and two possible final steps. Repetition will come from the backward connection, rather than another Python loop around `invoke`.

**Result:** The four working nodes are registered.

### Connect the retry edge and both exits

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-edges -->
```python
loop_builder.add_edge(START, "ask_otp")
loop_builder.add_edge("ask_otp", "verify")
loop_builder.add_conditional_edges(
    "verify", otp_route,
    {"correct": "success", "retry": "ask_otp", "locked": "locked"},
)
loop_builder.add_edge("success", END)
loop_builder.add_edge("locked", END)
otp_graph = loop_builder.compile()
```

**What happens here**

The mapping `"retry": "ask_otp"` creates the backward edge. `correct` and `locked` select final nodes. A **recursion_limit** is a separate limit on graph super-steps; it does not count OTP submissions. Our three-attempt rule belongs in `otp_route`.

**Result:** The graph can repeat and has explicit stopping paths.

### Try a wrong entry followed by a correct one

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-success-run -->
```python
otp_input = {
    "entries": ["000000", "123456"], "otp": "",
    "tries": 0, "verified": False, "status": "new",
}
otp_result = otp_graph.invoke(otp_input, {"recursion_limit": 12})
print(otp_result["tries"], otp_result["status"])
```

**What happens here**

The first entry fails and follows the backward edge. The second entry succeeds, so the graph runs `success` and ends. The graph-step limit leaves enough room for all three permitted attempts and a final outcome node.

**Result:** The final output is `2 verified`.

### Try repeated wrong entries

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-locked-run -->
```python
locked_input = {**otp_input, "entries": ["000000"]}
locked_result = otp_graph.invoke(locked_input, {"recursion_limit": 12})
print(locked_result["tries"], locked_result["status"])
```

**What happens here**

This is a fresh input with the original zero attempt count. The wrong sample repeats. After the third failure, the router selects `locked`; there is no fourth attempt.

**Result:** The final output is `3 locked`.

**Optional experiment: remove the normal retry limit**

In `otp_route`, remove the two lines that check `state["tries"] >= 3` and return `"locked"`. Rerun that function definition, then rerun the registration and connection snippets to compile a fresh graph. Keep the wrong sample input from the previous snippet.

### Observe the graph-step limit

<!-- snippet: code/Part II Connecting the dots/2-working-with-edges.ipynb#p2-2-otp-recursion -->
```python
# Optional: run only after removing the attempt limit and rebuilding the graph.
# otp_graph.invoke(locked_input, {"recursion_limit": 6})
```

**What happens here**

Uncomment the call only for the optional experiment. Without the attempt limit, every wrong entry chooses `retry`. LangGraph stops this run with `GraphRecursionError` when its graph-step limit is reached. Restore the original routing function and rebuild the graph afterward. The normal notebook run leaves this call commented out.

**Result:** The experiment demonstrates why a loop needs its own exit condition; the graph-step limit catches the missing exit.

## Check your understanding

1. Why must `calculate_total` run before `apply_coupon`?
2. Which edge makes `combine` wait for all three trip lookups?
3. Why do the parallel lookups return only their new messages?
4. Does a billing ticket run the urgent handler too?
5. Which connection makes the OTP workflow a loop?
6. What happens if the correct OTP arrives on the third attempt?
7. How does the three-attempt rule differ from `recursion_limit`?

## Where we go next

We have built four independent graphs: an ordered pipeline, parallel lookups with a join, a data-dependent route, and a bounded retry loop. Next we will put one LLM call inside a graph node to draft an office email reply.

Complete notebook: [2-working-with-edges.ipynb](../../../Part%20II%20Connecting%20the%20dots/2-working-with-edges.ipynb)

Further reading: [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) and [graph recursion limits](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT).
