# Part II · Lesson 7 — Watch a recipe appear

## A note from me

“Suggest a quick vegetarian dinner using rice, peas, and carrots.”

Waiting for the whole answer can make an application feel frozen. Sometimes we want to see which step finished. Sometimes we want to start reading while the model is still writing.

Those are two different kinds of progress.

**A node update** reports the fields a completed node returned.

**Message chunks** reveal the model's answer as it is generated.

## What we are building

We will build a recipe assistant that shows progress while it works. We supply rice, peas, and carrots and ask for a quick vegetarian dinner for two people. One Python node prepares the request; a second node asks the model to write a short recipe with numbered steps.

<div data-graph-preview="builder"></div>

**The idea behind it** is to make the work inside our intelligent graph visible as it happens. We already know how to connect sequential nodes and put an LLM call inside a node. Now we change how our application receives the output so a user can see completed steps or start reading while the model is still writing.

The graph still follows `START → prepare_request → write_recipe → END`. State carries the ingredients, servings, prepared request, recipe, and status. Streaming changes when we receive progress; the node order stays the same.

**updates streaming** shows the fields returned by completed nodes. We first see that the ingredients have been prepared, then receive the finished recipe after the model node completes.

**messages streaming** shows chunks of the model's text as they arrive. This lets us display the recipe gradually during generation. A chunk may contain part of a word or several words, so we print the arriving text as supplied.

**Our experiment** runs the same recipe workflow twice: once to inspect completed node updates and once to display arriving model text. Each run makes its own model call, so the recipe wording can differ between runs.

**The result** is a clear distinction between “this step has finished” and “the answer is still being written.” We can choose the kind of progress that helps the user of our application.

### Import the graph helpers

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-01 -->
```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
```

**What happens here**

**TypedDict** describes our state fields.

**StateGraph** builds the workflow, while START and END mark its boundaries.

**Result:** The helpers are ready; no graph has run.

### Import the model and messages

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-02 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
```

**What happens here**

These are the same model and message helpers we used in Part I. The graph will decide when to call the model.

**Result:** We can prepare the connection.

### Connect to our existing Groq model

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-03 -->
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

### Describe the recipe record

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-04 -->
```python
class RecipeState(TypedDict):
    ingredients: list[str]
    servings: int
    request: str
    recipe: str
    status: str
```

**What happens here**

RecipeState has five fields that let us inspect input, prepared work, and generated output. All fields replace on update; none needs an accumulating reducer in this graph.

**Result:** The progress can be described by actual state changes.

### Prepare a clear recipe request

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-05 -->
```python
def prepare_request(state: RecipeState) -> dict:
    ingredients = ", ".join(state["ingredients"])
    request = (
        f"Suggest a quick vegetarian dinner for {state['servings']} people "
        f"using {ingredients}. Give a short recipe with numbered steps."
    )
    return {"request": request, "status": "ingredients prepared"}
```

**What happens here**

The Python node combines ingredients and servings into one request. It returns only the prepared text and status; the original ingredients remain in state.

**Result:** The model will receive a clear request.

### Generate the recipe

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-06 -->
```python
def write_recipe(state: RecipeState) -> dict:
    reply = model.invoke([
        SystemMessage("You are a concise recipe assistant."),
        HumanMessage(state["request"]),
    ])
    return {"recipe": reply.text, "status": "recipe ready"}
```

**What happens here**

The node still uses invoke. LangGraph can observe the model's supported streaming callbacks when the graph is streamed in messages mode. We return the final recipe and status after the model call finishes.

**Result:** The completed node contributes a finished recipe.

### Connect the two-node graph

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-07 -->
```python
builder = StateGraph(RecipeState)
builder.add_node("prepare_request", prepare_request)
builder.add_node("write_recipe", write_recipe)
builder.add_edge(START, "prepare_request")
builder.add_edge("prepare_request", "write_recipe")
builder.add_edge("write_recipe", END)
graph = builder.compile()
recipe_input = {
    "ingredients": ["rice", "peas", "carrots"], "servings": 2,
    "request": "", "recipe": "", "status": "new",
}
```

**What happens here**

The model node waits for the prepared request. The initial record supplies all five fields. This graph has no checkpointer, so every demonstration starts a fresh run.

**Result:** We can inspect progress from two genuinely different steps.

### Stream completed node updates

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-08 -->
```python
for event in graph.stream(recipe_input, stream_mode="updates"):
    for node_name, update in event.items():
        print("Finished node:", node_name)
        print(update)
```

**What happens here**

updates mode emits each node's returned update after that node finishes. First we see the prepared request and status; later we see the complete recipe and recipe-ready status. These are partial updates, not full state snapshots or live word-by-word output.

**Result:** The learner can tell which work has finished.

### Stream the model's arriving text

<!-- snippet: code/Part II Connecting the dots/6-Streaming.ipynb#p2-7-step-09 -->
```python
for chunk, metadata in graph.stream(recipe_input, stream_mode="messages"):
    if metadata["langgraph_node"] == "write_recipe":
        print(chunk.text, end="", flush=True)
print()
```

**What happens here**

messages mode exposes supported model message chunks with metadata. We select the write_recipe node and print arriving text without adding a newline after every chunk. A chunk is not guaranteed to equal one word or one token.

**Result:** The recipe appears gradually while the model generates it.

## What is the difference?

| Output | Meaning |
|---|---|
| prepare_request update | Preparation finished and returned new request text. |
| write_recipe update | The full recipe-generation step finished. |
| Text chunks from write_recipe | Parts of the answer arrive while generation is still happening. |

Showing a node update does not mean the user has received every intermediate model chunk. Choose the stream that represents the progress your application needs.

## Check your understanding

1. Which node uses ordinary Python?
2. When does updates mode report write_recipe?
3. Why do we filter the message metadata?
4. Does each text chunk represent one token?
5. How many separate model requests do the two demonstrations make?

## Where we go next

Finally we will pause a refund request for a person's approval or rejection.

Complete notebook: [6-Streaming.ipynb](../../../Part%20II%20Connecting%20the%20dots/6-Streaming.ipynb)

Further reading: [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/streaming).
