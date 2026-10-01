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
- explain how labelled messages shape a conversation.

---

## What else can we do with a model call?

### Streaming

Normally, `invoke` waits until the complete response is ready. Streaming lets our application receive small chunks while the model is still generating.

```python
for chunk in groq_model.stream("Explain API-key safety in three sentences."):
    print(chunk.text, end="", flush=True)
```

It makes a long answer feel more responsive because the user can start reading it sooner. The model is still generating the same kind of response; streaming only changes how our application receives it.

### Batching

Batching is for requests that do not depend on one another.

```python
batch_responses = groq_model.batch([
    "Define an LLM in one sentence.",
    "Give one use for a low temperature setting.",
])
```

It is useful when processing a list of records, prompts, or tests. It is not conversation memory, and it does not make dependent tasks safe to run at the same time.

---

## Structured output: ask for data, not just prose

Models are good at writing paragraphs. Applications often need a predictable shape instead: fields we can put in a UI, store in a database, or pass to another function. **Structured output** tells the model and LangChain what shape our response needs.

Let’s use a Pokédex. A normal prompt might return a nice paragraph about Pikachu. That is pleasant for a person to read, but our code cannot safely rely on the order of facts inside it. We want a name, type, level, and evolutions in named places.

### Pydantic: a validated Python object

A Pydantic model describes the expected fields. `Field(description=...)` is useful because it explains each field to the model as well as to the reader of our code.

```python
from pydantic import BaseModel, Field


class Pokemon(BaseModel):
    name: str = Field(description="The Pokémon's name.")
    type: str = Field(description="Its main Pokémon type.")
    level: int = Field(description="A sensible level for this example.")
    evolutions: list[str] = Field(description="Its possible evolution names.")
```

Now we wrap the normal model. The call still looks like `invoke`, but it returns a `Pokemon` object instead of a free-form `AIMessage`.

```python
pokemon_model = groq_model.with_structured_output(Pokemon)

pokemon = pokemon_model.invoke("Give Pokédex details for Pikachu.")
print(pokemon.name)
print(pokemon.evolutions)
```

We use dot notation because `pokemon` is a Pydantic object. Pydantic also checks that the returned fields can fit the types we asked for, such as a number for `level` and a list for `evolutions`.

### A nested output: a Pokédex list

One Pokémon is a flat object. A Pokédex needs a list of those objects. We can reuse the `Pokemon` model inside another Pydantic model.

```python
class PokemonList(BaseModel):
    pokemons: list[Pokemon] = Field(
        description="The Pokémon included in this Pokédex result."
    )


pokedex_model = groq_model.with_structured_output(PokemonList)
pokedex = pokedex_model.invoke(
    "Create a short Pokédex for three of Ash's Kanto Pokémon."
)

for pokemon in pokedex.pokemons:
    print(pokemon.name, "-", pokemon.type)
```

`PokemonList` is the outer box. Its `pokemons` field is a list, and every item in that list must have the `Pokemon` shape. This is called a nested structured output. It is useful whenever one response contains a collection of repeated items: products in an order, people in a team, or search results.

### TypedDict: the lighter option

`TypedDict` describes the same kind of keys and value types using Python's typing tools. It is useful when we only need a normal dictionary and do not need Pydantic's object features or runtime validation.

```python
from typing_extensions import TypedDict


class PokemonDict(TypedDict):
    name: str
    type: str
    level: int
    evolutions: list[str]


typed_dict_model = groq_model.with_structured_output(PokemonDict)
pokemon_dict = typed_dict_model.invoke("Give Pokédex details for Eevee.")

print(pokemon_dict["name"])
print(pokemon_dict["evolutions"])
```

The shape is similar, but the result is a regular dictionary, so we use square brackets instead of dot notation. Start with Pydantic when you want clear field descriptions, nested models, and validation. Use `TypedDict` when a simple typed dictionary is enough.

Structured output does not make a model's facts automatically correct. It gives the answer a predictable shape. We still need good instructions and, when facts matter, trustworthy data and validation.

The complete examples are in [5-Structured-Outputs.ipynb](../../../Part%20I%20Understanding%20the%20Basics/5-Structured-Outputs.ipynb).

---

## Messages give a conversation structure

A message is just **text plus a label saying who said it**.

```python
HumanMessage("How do I create a REST API?")
# label: human, text: "How do I create a REST API?"
```

Why bother with the label? So the model can tell which text is a rule and which text is a question.

**Without labels**, we send one string:

```python
groq_model.invoke("Be concise. Always show code. How do I create a REST API?")
```

The model sees one blob of text. It cannot reliably separate our instruction from the user’s actual question.

**With labels**, we give the model the structure:

```python
groq_model.invoke([
    SystemMessage("Be concise. Always show code."),  # rules
    HumanMessage("How do I create a REST API?"),     # question
])
```

Now the model can treat the system message as “this is how I should behave” and the human message as “this is what the user wants.”

Think of a new employee. The **system message** is the manager’s day-one rule: “Be polite and keep replies short.” The **human message** is a customer’s question. The employee follows the manager’s rules for every customer without making the customer repeat them.

Messages also let us carry a chat history forward by adding an `AIMessage` for an earlier reply:

```python
conversation = [
    SystemMessage("Be concise."),
    HumanMessage("What is Python?"),
    AIMessage("A programming language."),  # earlier model reply
    HumanMessage("Who created it?"),        # “it” means Python
]
```

Without the earlier messages, the model would not know what “it” means. Labels do not guarantee perfect behaviour, but they give the application and model a clear, reliable conversation structure.

---

For the streaming, batching, and messages examples, use [4-Messages-Streaming-Batching-and-Memory.ipynb](../../../Part%20I%20Understanding%20the%20Basics/4-Messages-Streaming-Batching-and-Memory.ipynb).

## Check your understanding

1. When would streaming improve a user’s experience?
2. Why is batching unsuitable for a conversation where each answer affects the next question?
3. What does structured output give an application that free-form text does not?
4. Why do message labels matter when an application gives the model rules and a question?

## Next lesson

We will make conversation memory explicit: manual history and checkpointers.
