# Lesson 5 — More Than One Answer

> **Review draft**
>
> A model can return text in several useful ways, return structured data instead of prose, and take part in a conversation. This lesson explains those features and gives each one a clear purpose.

## A note from me

Up to now, our model call has looked very simple: send one input, receive one answer, print it. That is useful, but it is only the beginning.

What if we want the answer to appear word by word? What if we have a hundred unrelated requests? What if our Python code needs a list or an object instead of a paragraph? And how does a model distinguish a rule from a question?

Let’s add those pieces one at a time.

## What you will be able to do

- stream a response as it is generated;
- batch independent requests;
- ask for validated structured output;
- use system, human, and AI messages;
- explain how labeled messages shape a conversation.

---

## Set up once

Run these snippets in order in the associated notebook. Later snippets reuse the objects created here.

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-1 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
```

**What happens here**

These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.

**Result:** The imported names are ready for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-1 -->
```python
# Load GROQ_API_KEY from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Choose the model and provider

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-1 -->
```python
groq_model = init_chat_model("openai/gpt-oss-120b", model_provider="groq")
```

**What happens here**

`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.

**Result:** We can reuse this model object in the following snippets.

## What else can we do with a model call?

### Streaming

Normally, `invoke` waits until the complete response is ready.

**Streaming** lets our application receive small chunks while the model is still generating.

### Choose the streaming prompt

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-5 -->
```python
stream_prompt = "In a funny way explain why burgers are better than salads in 10 sentences."
```

**What happens here**

We store the question before starting the stream. This separates what we ask from how we receive the answer.

**Result:** stream_prompt contains our burger-and-salad request.

### Print each arriving chunk

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-5 -->
```python
for chunk in groq_model.stream(stream_prompt):
    # Each chunk contains the next available piece of the model response.
    print(chunk.text, end="", flush=True)
print()
```

**What happens here**

The loop receives chunks as the model produces them. `end=""` keeps them on the same line, and flush=True asks Python to show them immediately. The final print adds a newline.

**Result:** The answer gradually appears while generation continues.

### Why stream the answer?

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-5 -->
```python
# Print chunks as they arrive.
```

**What happens here**

This source comment explains the experience we just created: the user can start reading before the complete response is ready.

**Result:** The comment documents the purpose; it does not make another API call.

It makes a long answer feel more responsive because the user can start reading it sooner. The model is still generating the same kind of response; streaming only changes how our application receives it.

### Batching

**Batching** is for requests that do not depend on one another.

### Prepare independent prompts

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-7 -->
```python
batch_prompts = [
    "Give one use for a low temperature setting.",
    "Give one use for a high temperature setting.",
    "Define an LLM in one sentence.",
]
```

**What happens here**

Each item asks a separate question. None needs the answer from an earlier item.

**Result:** batch_prompts holds three independent requests.

### Run the batch and pair the results

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-7 -->
```python
batch_responses = groq_model.batch(batch_prompts)
for prompt, batch_response in zip(batch_prompts, batch_responses):
    print(f"Prompt: {prompt}")
    print(f"Answer: {batch_response.text}")
    print()
```

**What happens here**

`batch` submits the list through LangChain.

**zip** pairs each original prompt with its response so our prints remain easy to follow.

**Result:** We see a prompt and answer for every batch item. Provider limits still apply.

It is useful when processing a list of records, prompts, or tests. It is not conversation memory, and it does not make dependent tasks safe to run at the same time.

---

## Structured output: ask for data, not just prose

Models are good at writing paragraphs. Applications often need a predictable shape instead: fields we can put in a UI, store in a database, or pass to another function.

**Structured output** tells the model and LangChain what shape our response needs.

Let’s use a Pokédex. A normal prompt might return a nice paragraph about Pikachu. That is pleasant for a person to read, but our code cannot safely rely on the order of facts inside it. We want a name, type, level, and evolutions in named places.

### Set up the structured-output notebook

Switch to 5-Structured-Outputs.ipynb and run its setup first. This notebook uses the same provider and adds our schema helpers.

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#f0a76624 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
```

**What happens here**

These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.

**Result:** The imported names are ready for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#f0a76624 -->
```python
# Load GROQ_API_KEY from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Choose the model and provider

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#f0a76624 -->
```python
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
    reasoning_effort="low",
)
```

**What happens here**

`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.

**Result:** We can reuse this model object in the following snippets.

### Pydantic: a validated Python object

**A Pydantic model** describes the expected fields. `Field(description=...)` is useful because it explains each field to the model as well as to the reader of our code.

### Describe one Pokémon

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#84f43421 -->
```python
class Pokemon(BaseModel):
    """One Pokémon entry returned by the model."""

    name: str = Field(description="The Pokémon name.")
    type: str = Field(description="Its main Pokémon type.")
    level: int = Field(description="A sensible level for this example.")
    evolutions: list[str] = Field(description="Its possible evolution names.")
```

**What happens here**

Pokemon inherits from BaseModel. Its fields describe the shape we want: name, type, level, and a list of evolution names. Field descriptions tell the model what belongs in each field.

**Result:** We have a Pydantic schema that checks the returned field types.

Now we wrap the normal model. The call still looks like `invoke`, but it returns a `Pokemon` object instead of a free-form `AIMessage`.

### Wrap the model with the schema

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#84f43421 -->
```python
# This wrapped model returns a Pokemon object instead of free-form text.
pokemon_model = groq_model.with_structured_output(Pokemon)
```

**What happens here**

with_structured_output connects the Pokemon schema to the model call. We keep the wrapper in pokemon_model.

**Result:** The wrapper is ready to return a Pokemon object.

### Ask for Pikachu's data

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#ce853fb7 -->
```python
pokemon = pokemon_model.invoke("Give Pokédex details for Pikachu.")
```

**What happens here**

The request still uses invoke, but it goes through the structured wrapper.

**Result:** pokemon contains the generated Pokemon object.

### Read the named fields

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#ce853fb7 -->
```python
print(pokemon)
print("Name:", pokemon.name)
print("Evolutions:", pokemon.evolutions)
```

**What happens here**

We print the whole object, then use dot notation for its name and evolutions. A valid shape does not guarantee that every generated fact is correct.

**Result:** Our code can read the fields without scraping a paragraph.

We use dot notation because `pokemon` is a Pydantic object. Pydantic also checks that the returned fields can fit the types we asked for, such as a number for `level` and a list for `evolutions`.

### A nested output: a Pokédex list

One Pokémon is a flat object. A Pokédex needs a list of those objects. We can reuse the `Pokemon` model inside another Pydantic model.

### Describe a list of Pokémon

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#e70700b1 -->
```python
class PokemonList(BaseModel):
    """A small Pokédex result containing several Pokémon."""

    pokemons: list[Pokemon] = Field(
        description="The Pokémon included in this Pokédex result."
    )
```

**What happens here**

PokemonList is the outer object. Its pokemons field contains a list of Pokemon objects, reusing the schema we just defined.

**Result:** We have a nested schema: one list containing several structured entries.

### Create the Pokédex wrapper

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#e70700b1 -->
```python
pokedex_model = groq_model.with_structured_output(PokemonList)
```

**What happens here**

We wrap the same model with PokemonList for requests that need a collection.

**Result:** pokedex_model expects the nested result shape.

### Request a small Pokédex

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#45350e28 -->
```python
pokedex = pokedex_model.invoke(
    "Create a short Pokédex for three of Ash's Kanto Pokémon."
)
```

**What happens here**

We ask for three of Ash's Kanto Pokémon through the collection wrapper.

**Result:** pokedex holds the generated list of Pokémon objects.

### Read each nested entry

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#45350e28 -->
```python
for pokemon in pokedex.pokemons:
    print(f"{pokemon.name}: {pokemon.type}")
    print("Evolutions:", pokemon.evolutions)
```

**What happens here**

We loop through pokedex.pokemons and access each object's name, type, and evolutions with dot notation.

**Result:** We can use every entry in the same predictable way.

**`PokemonList`** is the outer box. Its `pokemons` field is a list, and every item in that list must have the `Pokemon` shape. This is called a nested structured output. It is useful whenever one response contains a collection of repeated items: products in an order, people in a team, or search results.

### TypedDict: the lighter option

**`TypedDict`** describes the same kind of keys and value types using Python's typing tools. It is useful when we only need a normal dictionary and do not need Pydantic's object features or runtime validation.

### Describe dictionary keys

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#37741c0a -->
```python
class PokemonDict(TypedDict):
    """One simple Pokémon dictionary."""

    name: str
    type: str
    level: int
    evolutions: list[str]
```

**What happens here**

PokemonDict declares the keys and expected value types.

**TypedDict** describes the shape for tooling and the structured-output schema; it does not perform Pydantic-style runtime validation on its own.

**Result:** We have a schema for a regular Python dictionary.

### Create the dictionary wrapper

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#37741c0a -->
```python
# This wrapped model returns a regular dictionary.
typed_dict_model = groq_model.with_structured_output(PokemonDict)
```

**What happens here**

We pass PokemonDict to with_structured_output. This wrapper returns a dictionary rather than a Pydantic object.

**Result:** typed_dict_model is ready for the request.

### Ask for Eevee's data

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#4b5db0e1 -->
```python
pokemon_dict = typed_dict_model.invoke("Give Pokédex details for Eevee.")
```

**What happens here**

We invoke the dictionary wrapper with the Pokédex question.

**Result:** pokemon_dict contains the generated keys and values.

### Read values with square brackets

<!-- snippet: code/Part I Understanding the Basics/5-Structured-Outputs.ipynb#4b5db0e1 -->
```python
print("Name:", pokemon_dict["name"])
print("Evolutions:", pokemon_dict["evolutions"])
```

**What happens here**

We access name and evolutions by their dictionary keys. This is the main difference in how we use the returned data.

**Result:** The values print without dot notation.

The shape is similar, but the result is a regular dictionary, so we use square brackets instead of dot notation. Start with Pydantic when you want clear field descriptions, nested models, and validation. Use `TypedDict` when a simple typed dictionary is enough.

Structured output does not make a model's facts automatically correct. It gives the answer a predictable shape. We still need good instructions and, when facts matter, trustworthy data and validation.

The complete examples are in [5-Structured-Outputs.ipynb](../../../Part%20I%20Understanding%20the%20Basics/5-Structured-Outputs.ipynb).

---

## Messages give a conversation structure

**A message** is just **text plus a label saying who said it**.

### Inspect a human message

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#message-feature-3 -->
```python
# A HumanMessage carries both the text and the "human" label.
human_question = HumanMessage("How do I create a vegan chicken sandwich?")
print("Label:", human_question.type)
print("Text:", human_question.content)
```

**What happens here**

HumanMessage holds the question text and the human role. Its type property shows the label; content shows the text.

**Result:** We can see both parts of the message explicitly.

Why bother with the label? So the model can tell which text is a rule and which text is a question.

**Without labels**, we send one string:

### Send everything as one string

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#8803651c -->
```python
# Without labels, the model receives one blob of instructions and question text.
plain_text_response = groq_model.invoke(
    "You are a mad street chef. How do I create a vegan chicken sandwich?",
    max_tokens=200,  # limit the response length
)
print(plain_text_response.text)
```

**What happens here**

The instruction and question share a single string. The model may infer their meaning, but our application has not marked a separate system instruction and user question.

**Result:** plain_text_response holds the answer to the combined prompt.

The model receives one string and may infer which part is an instruction. Separate message roles make that distinction explicit.

**With labels**, we give the model the structure:

### Separate the rule from the question

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#c85f112c -->
```python
# With labels, rules and the user's question are separate messages.
message_response = groq_model.invoke(
    [
        SystemMessage("You are a mad street chef."),  # application rules
        HumanMessage("How do I create a vegan chicken sandwich?"),  # user question
    ],
    max_tokens=200,  # limit the response length
)
print(message_response.text)
```

**What happens here**

SystemMessage carries the chef instruction, while HumanMessage carries the question. We pass the list to invoke and print the response text.

**Result:** The model receives an explicit role for each message.

Now the model can treat the system message as “this is how I should behave” and the human message as “this is what the user wants.”

Think of a new employee.

**The system message** is the manager’s day-one rule: “Be polite and keep replies short.”

**The human message** is a customer’s question. The employee follows the manager’s rules for every customer without making the customer repeat them.

Messages also let us carry a chat history forward by adding an `AIMessage` for an earlier reply:

### Include an earlier reply

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#e255e7e0 -->
```python
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# An AIMessage can carry an earlier reply into the next model call.
conversation_with_history = [
    SystemMessage("You are a mad street chef."),
    HumanMessage("How do I create a vegan chicken sandwich?"),
    AIMessage(
        "First, you'll need to find a vegan chicken. And fry it "
    ),  # earlier model reply
    # note we are assuming this is the model's response to the previous question.
    HumanMessage("can I create a bread from it?"),
]
```

**What happens here**

The list contains instructions, the first question, an illustrative AI reply, and a follow-up. The notebook supplies that earlier reply itself; it was not generated by the preceding call.

**Result:** conversation_with_history contains context for the follow-up.

### Ask with the supplied history

<!-- snippet: code/Part I Understanding the Basics/4-Messages-Streaming-Batching-and-Memory.ipynb#e255e7e0 -->
```python
history_response = groq_model.invoke(conversation_with_history, max_tokens=200)
print(history_response.text)
```

**What happens here**

We resend the conversation list. The model can use the earlier messages to interpret the follow-up.

**Result:** The response uses the history that our application provided.

Without earlier context, a follow-up like this can become ambiguous. Labels do not guarantee perfect behavior, but they give the application and model a clear, reliable conversation structure.

---

For the streaming, batching, and messages examples, use [4-Messages-Streaming-Batching-and-Memory.ipynb](../../../Part%20I%20Understanding%20the%20Basics/4-Messages-Streaming-Batching-and-Memory.ipynb).

## Check your understanding

1. When would streaming improve a user’s experience?
2. Why is batching unsuitable for a conversation where each answer affects the next question?
3. What does structured output give an application that free-form text does not?
4. Why do message labels matter when an application gives the model rules and a question?

## Next lesson

We will make conversation memory explicit: manual history and checkpointers.
