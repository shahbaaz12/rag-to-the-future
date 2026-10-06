# Part II · Lesson 6 — Remember a student's selected topics

## A note from me

A student says, “I'm a beginner learning Python. I want to understand lists and tuples.”

Then: “Explain the first one with an example.” Later: “How is it different from the second one?” And finally: “Give me three practice questions on both.”

The student does not repeat the topic names in every question. Our application carries the earlier conversation so the model can understand first one, second one, and both.

## What we are building

We will build a Python study assistant that can continue a student's conversation. The student chooses lists and tuples, then asks, “Explain the first one with an example.” Later questions refer to “the second one” and “both.” The assistant needs the earlier topics and messages to understand those references.

<div data-graph-preview="builder"></div>

**The idea behind it** is to give our intelligent graph memory between requests. We have already learned how state carries information through one graph run and how a node sends that information to a model. Now we save the state so a later run can continue with the same student's context.

The execution path stays simple: `START → tutor → END`. We attach storage to the graph rather than adding a memory node to that path. The tutor reads the restored context, makes a model call, and returns its new reply.

**A checkpointer** saves the graph state: the student ID, learning level, selected topics, conversation messages, and latest answer.

**thread_id** identifies which saved conversation to continue. Reusing the same ID restores that student's context; a different ID keeps another conversation separate.

**InMemorySaver** is the checkpointer we use here. It keeps the saved state while the current Python process remains alive.

**Our conversation** starts by supplying the student's details and first question. For each follow-up, we send only the new message with the same thread ID. The graph restores the earlier state and supplies it to the tutor. In our sample, “the first one” refers to lists for one student and loops for another because their saved topics differ.

**The result** is an assistant that can use earlier context to answer a follow-up. The application provides that context by saving and restoring state; the model receives it in each request.

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-01 -->
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

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-02 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
```

**What happens here**

These are the same model and message helpers we used in Part I. The graph will decide when to call the model.

**Result:** We can prepare the connection.

### Connect to our existing Groq model

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-03 -->
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

### Describe the student's context

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-04 -->
```python
class StudyState(TypedDict):
    student_id: str
    level: str
    topics: list[str]
    messages: Annotated[list, add_messages]
    last_answer: str
```

**What happens here**

StudyState preserves useful learning context alongside the conversation. topics is an ordinary list that replaces on update. messages has a message-aware reducer. last_answer gives us an easy place to read the latest reply.

**Result:** List-shaped fields can have different update rules because their meanings differ.

### Answer using the restored context

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-05 -->
```python
def tutor(state: StudyState) -> dict:
    reply = model.invoke([
        SystemMessage(
            f"You are a concise Python tutor for a {state['level']} student. "
            f"Selected topics, in order: {', '.join(state['topics'])}. "
            "Use the conversation to understand follow-up references."
        ),
        *state["messages"],
    ])
    return {"messages": [reply], "last_answer": reply.text}
```

**What happens here**

The tutor receives saved metadata and earlier messages. It returns only the new AIMessage and last_answer. Resending the entire old message list is unnecessary.

**Result:** The node can answer a follow-up using its context.

### Attach a checkpointer to the graph

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-06 -->
```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
builder = StateGraph(StudyState)
builder.add_node("tutor", tutor)
builder.add_edge(START, "tutor")
builder.add_edge("tutor", END)
graph = builder.compile(checkpointer=memory)
```

**What happens here**

The checkpointer stores the state needed by later invocations. It saves our metadata as well as messages. A thread ID identifies which saved conversation to load; it is not an authentication mechanism.

**Result:** The graph can continue separate conversations.

### Start the first student's conversation

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-07 -->
```python
student1_config = {"configurable": {"thread_id": "student1"}}
first_response = graph.invoke({
    "student_id": "student1", "level": "beginner",
    "topics": ["lists", "tuples"], "last_answer": "",
    "messages": [HumanMessage("I want to understand Python lists and tuples.")],
}, student1_config)
print(first_response["last_answer"])
```

**What happens here**

The first turn supplies all five fields. The selected topics have an explicit order, which makes first one and second one meaningful.

**Result:** The first student's context and reply are saved.

### Continue with only the new messages

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-08 -->
```python
for question in [
    "Explain the first one with an example.",
    "How is it different from the second one?",
    "Give me three practice questions on both.",
]:
    response = graph.invoke(
        {"messages": [HumanMessage(question)]}, student1_config
    )
    print("Student:", question)
    print("Tutor:", response["last_answer"])
```

**What happens here**

Each invocation sends a partial input update containing just the new message. The checkpointer restores the level, topics, and prior conversation for student1. The model receives that history even though our calling code sends only one new turn.

**Result:** The follow-up references can be interpreted from the saved context.

### Start a different student's thread

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-09 -->
```python
student2_config = {"configurable": {"thread_id": "student2"}}
graph.invoke({
    "student_id": "student2", "level": "beginner",
    "topics": ["loops", "functions"], "last_answer": "",
    "messages": [HumanMessage("I want to understand Python loops and functions.")],
}, student2_config)
second_student = graph.invoke(
    {"messages": [HumanMessage("Explain the first one.")]}, student2_config
)
print(second_student["last_answer"])
```

**What happens here**

student2 has their own topics and messages. Their first one refers to loops, while student1's first one refers to lists. Separate threads prevent these two example conversations from sharing state.

**Result:** The two students can ask the same words with different context.

### Inspect the stored state

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-10 -->
```python
saved_student1 = graph.get_state(student1_config).values
saved_student2 = graph.get_state(student2_config).values
print(saved_student1["topics"], len(saved_student1["messages"]))
print(saved_student2["topics"], len(saved_student2["messages"]))
```

**What happens here**

get_state reads the saved snapshot. Student1 has eight messages from four exchanges; student2 has four from two exchanges. Counting messages does not count their tokens.

**Result:** We can verify thread separation directly.

## Updating selected topics

A student can choose a new topic.

**A topics update** replaces that ordinary list.

**A messages update** merges into the history. The two fields deliberately behave differently.

### Change topics without discarding the conversation

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-11 -->
```python
changed_topics = graph.invoke({
    "topics": ["dictionaries"],
    "messages": [HumanMessage("Switch to dictionaries. Explain this new topic simply.")],
}, student1_config)
print(changed_topics["topics"])
print(len(changed_topics["messages"]))
```

**What happens here**

The selected topics become dictionaries. The earlier messages remain, and this exchange adds two more. The tutor's system instruction uses the current selection while the history still records how the conversation evolved.

**Result:** The new topic list contains one item and the history contains ten messages.

## Why add_messages is more than list addition

**A new message ID** appends a message. Returning a message with an existing ID replaces that message instead. This is useful when correcting a stored reply.

### Demonstrate an update by message ID

<!-- snippet: code/Part II Connecting the dots/5-adding-memory.ipynb#p2-6-step-12 -->
```python
from langchain_core.messages import AIMessage

earlier = [AIMessage(content="Earlier explanation.", id="reply-1")]
corrected = AIMessage(content="Corrected explanation.", id="reply-1")
merged = add_messages(earlier, [corrected])
print(len(merged), merged[0].text)
```

**What happens here**

Both replies use reply-1, so add_messages updates that entry and the length stays one. This small standalone demonstration does not edit either student's checkpoint.

**Result:** The stored message becomes Corrected explanation without appending a duplicate.

## Check your understanding

1. Which state fields are restored for a follow-up?
2. What does the same thread ID mean?
3. Why does student2's first one mean loops?
4. Why does topics replace while messages merges?
5. What happens when a returned message has an existing ID?

## Where we go next

Next we will show progress while a recipe is being generated.

Complete notebook: [5-adding-memory.ipynb](../../../Part%20II%20Connecting%20the%20dots/5-adding-memory.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/persistence).
