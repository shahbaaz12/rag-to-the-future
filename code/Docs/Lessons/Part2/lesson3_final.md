# Part II · Lesson 3 — Draft an office email reply

## A note from me

A colleague writes: “Can we move Thursday's project review to Friday afternoon?”

We want a friendly acknowledgement that asks for their preferred time. We have not checked our calendar, so the draft should not confirm availability.

Until now, our nodes performed work written entirely in Python. This time, one node asks a model to help write something. The surrounding pattern stays familiar: receive state, perform the work, return an update.

## What we are building

**START → draft_reply → END.** One node makes one model call and stores the draft for review. It does not send an email.

The state holds the original email, the requested tone, the draft, and the status. This makes it easy to see what went into the call and what came back.

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-01 -->
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
```

**What happens here**

TypedDict describes our state fields. StateGraph builds the workflow, while START and END mark its boundaries.

**Result:** The helpers are ready; no graph has run.

### Import the model and messages

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-02 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
```

**What happens here**

These are the same model and message helpers we used in Part I. The graph will decide when to call the model.

**Result:** We can prepare the connection.

### Connect to our existing Groq model

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-03 -->
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

load_dotenv makes the API key available. init_chat_model creates our reusable model object; it has not generated an answer yet.

**Result:** The model is ready. Running its node will make a provider request.

### Describe the email record

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-04 -->
```python
class EmailState(TypedDict):
    email: str
    tone: str
    draft: str
    status: str
```

**What happens here**

EmailState separates the incoming message and requested tone from the generated draft and workflow status. All four fields use ordinary replacement behaviour.

**Result:** We can inspect the input and output together.

### Make the model call inside a node

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-05 -->
```python
def draft_reply(state: EmailState) -> dict:
    reply = model.invoke([
        SystemMessage(
            f"Draft a {state['tone']} office email reply. "
            "Acknowledge the request and ask for a preferred time. "
            "Do not confirm calendar availability."
        ),
        HumanMessage(state["email"]),
    ])
    return {"draft": reply.text, "status": "draft ready"}
```

**What happens here**

The node reads email and tone, calls the model once, then returns only draft and status. The graph preserves the original email and tone. SystemMessage explains the writing task; HumanMessage supplies the email.

**Result:** The node can produce a reviewable draft. Its exact wording can vary.

### Connect the one-node graph

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-06 -->
```python
builder = StateGraph(EmailState)
builder.add_node("draft_reply", draft_reply)
builder.add_edge(START, "draft_reply")
builder.add_edge("draft_reply", END)
graph = builder.compile()
```

**What happens here**

The graph controls where the model call belongs. START provides the email record, and END finishes after the node returns its update.

**Result:** One working node sits between the graph boundaries.

### Request and inspect the draft

<!-- snippet: code/Part II Connecting the dots/3-Connecting-LLM.ipynb#p2-3-step-07 -->
```python
email_input = {
    "email": "Hi, can we move Thursday's project review to Friday afternoon?",
    "tone": "friendly and concise", "draft": "", "status": "new",
}
response = graph.invoke(email_input)
print(response["draft"])
print(response["status"])
```

**What happens here**

We provide all four initial fields. An illustrative draft might acknowledge the change and ask what time on Friday the colleague prefers. Check its wording before using it; a model response is generated text, not a calendar result.

**Result:** The record contains the original request and a draft ready for review.

## Check your understanding

1. Which state fields does the node read?
2. Which fields does it return?
3. How many model calls does this graph make?
4. Why should the reply avoid confirming availability?

## Where we go next

Next we will supply information the model cannot infer: an employee's leave balance.

Complete notebook: [3-Connecting-LLM.ipynb](../../../Part%20II%20Connecting%20the%20dots/3-Connecting-LLM.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/quickstart).
