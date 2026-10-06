# Part II · Lesson 4 — Look up an employee's leave balance

## A note from me

An employee asks: “How many paid leave days do I have left?”

The model understands the question, but the answer lives in our company's records. Knowing how leave works is different from knowing this employee's balance.

We will expose one function, get_leave_balance. The model requests it; our application runs it and returns the result. Notice who actually executes the function.

## What we are building

We will build a small leave-balance assistant. An employee asks, “How many paid leave days do I have left?” Our application supplies the employee ID, and the assistant can look up that employee's record before writing an answer. For our sample employee, EMP101, the allowance is 20 days and 14 have been used, leaving 6.

<div data-graph-preview="builder"></div>

**The idea behind it** is to give the intelligent graph access to information through a tool. In Lesson 11, we added an LLM call to the graph design we had learned. Now we connect that model node to a Python function that reads a local leave record. The model understands the question and can request the lookup; our application executes the function and returns its result.

The state, nodes, and edges still have the same jobs. State carries the employee details and conversation. Nodes ask the model, execute the lookup, and write the answer. A conditional edge checks whether the model requested a tool and chooses the next step.

**Our workflow** has one tool round:

1. `ask_model` receives the question and selected employee ID. The model can request `get_leave_balance`.
2. If it requests the lookup, `tools` executes the function and adds the returned record to the conversation.
3. `answer` uses that record to explain the balance, then the graph ends. A model reply without a tool request can end directly from `ask_model`.

**The result** can be an answer such as “You have 6 paid leave days remaining.” The balance comes from our sample record. The model's role is to request the information and explain it in words.

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-01 -->
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

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-02 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
```

**What happens here**

These are the same model and message helpers we used in Part I. The graph will decide when to call the model.

**Result:** We can prepare the connection.

### Connect to our existing Groq model

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-03 -->
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

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-04 -->
```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
```

**What happens here**

ToolNode executes requests against the tools we supply. tools_condition checks whether the latest model reply contains tool calls.

**Result:** We can keep requesting a function separate from executing it.

### Keep the employee and conversation in state

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-05 -->
```python
class LeaveState(TypedDict):
    employee_id: str
    request_type: str
    messages: Annotated[list, add_messages]
    status: str
```

**What happens here**

LeaveState has four fields. The selected employee and leave type stay available while messages grows. add_messages appends new message IDs and updates existing IDs. status uses ordinary replacement.

**Result:** The tool exchange can keep its messages without resending the whole state.

### Expose the leave-record lookup

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-06 -->
```python
@tool
def get_leave_balance(employee_id: str) -> dict:
    """Read the paid leave allowance, days used, and balance for an employee."""
    records = {
        "EMP101": {"allowance": 20, "used": 14, "remaining": 6},
        "EMP102": {"allowance": 20, "used": 8, "remaining": 12},
    }
    return records[employee_id]
```

**What happens here**

The tool reads a local sample record. Its docstring tells the model what it does, and employee_id is its argument. Our application supplies the selected employee ID; a production application would derive that identity from the signed-in user.

**Result:** Executing the tool for EMP101 returns a six-day balance.

### Make the tool available to the model

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-07 -->
```python
leave_tools = [get_leave_balance]
tool_model = model.bind_tools(leave_tools)
```

**What happens here**

bind_tools supplies the tool description and input schema. It does not execute the function.

**Result:** The model can request a permitted leave lookup.

### Ask the model for the required information

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-08 -->
```python
def ask_model(state: LeaveState) -> dict:
    reply = tool_model.invoke([
        SystemMessage(
            f"Answer a {state['request_type']} request for {state['employee_id']}. "
            "Use get_leave_balance for the balance; do not guess it."
        ),
        *state["messages"],
    ])
    return {"messages": [reply], "status": "model replied"}
```

**What happens here**

The model receives the selected employee and the question. Its AIMessage may contain a tool name and arguments rather than answer text. We return that message itself so its tool-call ID and metadata survive.

**Result:** The graph receives a tool request if the model chooses the lookup.

### Write the answer from the tool result

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-09 -->
```python
def answer_from_tool(state: LeaveState) -> dict:
    reply = model.invoke([
        SystemMessage("Explain the employee's leave balance using the tool result."),
        *state["messages"],
    ])
    return {"messages": [reply], "status": "answered"}
```

**What happens here**

This final node uses the original model without bound tools. It reads the returned record and explains it. The node returns only the new reply and status; earlier messages remain in state.

**Result:** The tool result can become a clear answer.

### Register the model and execution nodes

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-10 -->
```python
builder = StateGraph(LeaveState)
builder.add_node("ask_model", ask_model)
builder.add_node("tools", ToolNode(leave_tools))
builder.add_node("answer", answer_from_tool)
```

**What happens here**

ToolNode is the application step that actually executes the requested lookup. It returns ToolMessage results through the messages field, preserving employee_id and request_type.

**Result:** The three jobs have explicit places in the graph.

### Connect one controlled tool round

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-11 -->
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

A tool request routes to execution. A reply with no tool request can end directly. After execution, answer writes the final response and ends. There is no route back for another tool round in this example.

**Result:** The application controls the lookup and final response.

### Ask about the selected employee

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-12 -->
```python
leave_input = {
    "employee_id": "EMP101", "request_type": "paid leave",
    "messages": [HumanMessage("How many paid leave days do I have left?")],
    "status": "new",
}
response = graph.invoke(leave_input)
print(response["messages"][-1].text)
```

**What happens here**

The employee ID is supplied by our application, rather than guessed from the question. When the lookup is used, the final answer can report six remaining days.

**Result:** We have an answer grounded in our sample record.

### Inspect the request and result

<!-- snippet: code/Part II Connecting the dots/4-Using-Tools.ipynb#p2-4-step-13 -->
```python
for message in response["messages"]:
    print(message.type, message.text)
    if getattr(message, "tool_calls", None):
        print("Requested calls:", message.tool_calls)
```

**What happens here**

Inspect tool_calls as well as text: a tool-request message may have empty text. The ToolMessage contains the returned record and matches the original request by its call ID.

**Result:** The trace shows request, application execution, and final answer.

## Check your understanding

1. Does bind_tools execute get_leave_balance?
2. Where does the employee ID come from?
3. Which node executes the function?
4. Why does answer use the unbound model?

## Where we go next

Next we will let a model request more information after seeing a first result.

Complete notebook: [4-Using-Tools.ipynb](../../../Part%20II%20Connecting%20the%20dots/4-Using-Tools.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/quickstart).
