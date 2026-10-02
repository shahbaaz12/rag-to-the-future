# Part II · Lesson 1 — Connect the dots: your first graph

## A note from me

We have worked with models, messages, tools, and agents. Now let’s connect those pieces in a way we can control and understand.

Do not worry about making the model clever in this first lesson. We will use two ordinary Python functions. If we understand how data moves between them, adding an LLM later becomes a much smaller step.

## Understanding agents

Generative AI can create content and reason about the input we give it. An agent can also use tools to work towards a task.

For example, a model can write a LinkedIn post. An agent with the right tool and permission can also publish it. A chatbot can answer from the information in its prompt; an agent can use an approved database tool to check a record before answering.

The extra capability comes from the software around the model. We still choose the tools and decide what the application is allowed to do.

## LangChain versus LangGraph

Think of LangChain as our collection of model connections, messages, prompts, and tool helpers. LangGraph helps us arrange work into a workflow with state and an explicit path between steps. LangChain's create_agent already uses LangGraph underneath; here we build the graph ourselves to understand that control.

LangGraph can also coordinate several agents, with each agent handling a different part of a task. But let’s get our feet wet with two simple functions first. The same ideas about steps, connections, and shared data still apply.

A workflow may follow a predefined sequence, choose a branch, run independent work in parallel, or return to an earlier step. A graph with two fixed functions is a workflow; it does not become an autonomous agent just because we drew some arrows.

## The words we need

| Word | In simple terms |
|---|---|
| Node | One unit of work. Our nodes are Python functions. |
| Edge | A connection that controls which node runs next. |
| State | The shared, structured data carried through this graph run. |
| Reducer | The rule used to combine a node's update with an existing state value. |

State is usually a dictionary-like object with named keys. A node receives the current values declared in its input schema and returns the updates it wants to make. Think of a shared record that evolves as the workflow progresses. We return updates rather than letting every node rewrite one shared mutable dictionary.

Each state key can have its own reducer. One key might replace its old value; another might collect new entries into a list. Choosing that rule is part of designing the workflow.

So what does **stateful** mean here? The next node can use data produced by an earlier node in the same run. That does not automatically give our application memory between separate runs. For that, we will attach a checkpointer in the memory lesson. For now, think of state as the working record for this one workflow.

## What happens behind the scenes?

First we define the state, nodes, and edges. Then compile checks the graph structure. Finally invoke supplies an initial state and starts the run.

Execution proceeds in rounds called **super-steps**. Sequential nodes run in separate rounds. Independent nodes can run in the same round, and their updates are combined before the next round begins. We will see that parallel case in the next lesson.

## What we are building

Our first path is START → STEP ONE → STEP TWO → END. Each working node adds one completion message. No API key is required. Just follow along and keep an eye on which part describes the graph and which part actually runs it.

## Import the graph building blocks

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#e2ff7b3c -->
```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
```

**What happens here**

Annotated associates a type with an update rule. TypedDict describes our state keys. StateGraph builds the workflow, START and END mark its boundaries, and add_messages merges message updates.

**Result:** We can define the shared state and the two nodes.

## Describe the shared state

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#d24bf8db -->
```python
# The class name can be anything: State, GraphState, GS, MyState...
# It describes what data flows through the graph.
class State(TypedDict):
    # Annotated[list, add_messages] means:
    #   list         -> the type of this field
    #   add_messages -> append new messages; replace messages with matching IDs
    # Without add_messages, a node's returned messages would REPLACE the old ones.
    messages: Annotated[list, add_messages]
```

**What happens here**

State is the schema, not a model and not a running conversation. It says that our graph carries a messages list. add_messages appends new messages and can replace a message with the same ID; without a reducer, a new list would replace the old list.

**Result:** We have a state shape and an explicit message-update rule.

## Define the first node

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#247ed45e -->
```python
# Creating some dummy nodes that will perform operations on the messages in the state. In a real application, these would be more complex and meaningful.


def Step1(state: State) -> State:  # previous state passed to it.
    # This step appends a message to the state's messages list.
    return {
        "messages": ["Step 1 completed."]
    }  # new state returned, which will be merged with the previous state. using the reducer add_messages, the new message will be appended to the old list.
```

**What happens here**

Step1 receives the current state and returns an update for messages. It does not mutate the old list itself. LangGraph applies the returned update through our reducer.

**Result:** The first node can contribute its completion message.

## Define the second node

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#64b93a6c -->
```python
def Step2(state: State) -> State:
    return {"messages": ["Step 2 completed."]}
```

**What happens here**

Step2 follows the same pattern. It returns only the new message it wants added. We keep these functions ordinary Python so the graph concepts are easier to see.

**Result:** The second node can contribute its own message.

## Register the nodes

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#5cc03122 -->
```python
builder = StateGraph(
    State
)  # The StateGraph class is initialized with the State TypedDict, which defines the structure of the state that will be passed through the graph. This allows the graph to manage and update the state as it processes each node.

builder.add_node(
    "STEP ONE", Step1
)  # The add_node method is called to add the Step1 function as a node in the graph. The first argument gives the node its name; the second supplies the function it runs.
builder.add_node(
    "STEP TWO", Step2
)  # Register Step2 under the exact name used by the edges.
```

**What happens here**

StateGraph creates a builder using our schema. add_node takes the registered name first and the function second. These registered names must match the names used by our edges; the function can have a different Python name.

**Result:** The builder knows STEP ONE and STEP TWO.

## Connect the steps

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#3e9ebd35 -->
```python
builder.add_edge(
    START, "STEP ONE"
)  # The add_edge method is used to define the flow of the graph. Here, an edge is added from the START node to the "STEP ONE" node, indicating that STEP ONE should be executed first.
builder.add_edge(
    "STEP ONE", "STEP TWO"
)  # Another edge is added from "STEP ONE" to "STEP TWO", indicating that STEP TWO should be executed after STEP ONE.
builder.add_edge(
    "STEP TWO", END
)  # Finally, an edge is added from "STEP TWO" to the END node, indicating that the graph processing should end after STEP TWO
```

**What happens here**

add_edge defines the order: START, STEP ONE, STEP TWO, then END. An edge describes what comes next; it does not run the next node while we are assembling the graph.

**Result:** We have a complete sequential path.

## Compile the graph

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#a9716953 -->
```python
graph = builder.compile()  # The compile method is called to finalize the graph structure and prepare it for execution. This checks the graph structure and creates the runnable graph; it does not execute our nodes.

graph  # in a Jupyter notebook, this will display the graph structure visually, allowing you to see the nodes and edges that have been defined.
```

**What happens here**

compile validates the connections and prepares a runnable graph. It does not call either function yet. The last line can display the graph in Jupyter.

**Result:** The graph is ready for input.

## Run the first workflow

<!-- snippet: code/Part II Connecting the dots/1-first-graph.ipynb#714d585a -->
```python
response = graph.invoke(
    {"messages": ["Starting Message"]}
)  # The invoke method is called to execute the graph. with a starting state that contains an initial message. The graph will process each node in the order defined by the edges, updating the state as it goes.

response
```

**What happens here**

invoke supplies the starting state and executes the connected nodes. The starting message and the two node updates are merged into the messages list. Because these dummy updates are plain strings, add_messages converts them to human messages; later we will return explicit AIMessage objects for model replies.

**Result:** The result contains Starting Message, Step 1 completed., and Step 2 completed. in that order.

## Check your understanding

1. What is the difference between a node and an edge?
2. Why do we return a new message instead of the whole old list?
3. Does compile run our nodes?
4. Why must the registered node names match the edge names?

## Where we go next

Next we will change the connections: sequential, parallel, conditional, and looping flows.

Complete notebook: [1-first-graph.ipynb](../../../Part%20II%20Connecting%20the%20dots/1-first-graph.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/graph-api).
