# Lesson 8 — Agents: Models That Can Choose Tools

> **Review draft**
>
> This lesson turns the tool loop from Lesson 7 into an agent. An agent combines a model, instructions, and an approved tool set so it can decide which tool might help answer a request.

## A note from me

In Lesson 7, we wrote the tool-execution loop ourselves. The model asked for a function, our code ran it, and then we sent the result back for a final answer.

That is exactly the right way to understand the flow. But writing that loop again for every application becomes repetitive. An agent framework can manage the loop for us while we focus on defining useful tools and setting the rules around them.

## What you will be able to do

- explain what an agent adds to a chat model;
- create an agent with one tool;
- create an agent with several approved tools; and
- inspect the messages produced during an agent run.

---

## What is an agent?

An agent is a small system made from three main parts:

### Identify the agent's parts

<!-- snippet: code/Docs/Lessons/Part1/lesson8_final.md#supplement -->
```text
model + instructions + allowed tools = agent
```

**What happens here**

The model reasons about the request, instructions guide its behavior, and allowed tools provide actions or information.

**Result:** The framework can coordinate these parts as an agent.

The model reads the user request and decides whether a tool can help. The agent framework runs the approved tool, adds its result to the conversation, and asks the model to produce the final answer.

An agent is not a magical employee that can do anything. It can only use the tools we give it, with the permissions and checks we build around those tools.

---

## Set up once

Run these snippets in order in the associated notebook. Later snippets reuse the objects created here.

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#agent-imports -->
```python
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import tool
```

**What happens here**

These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.

**Result:** The imported names are ready for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#agent-imports -->
```python
# Load GROQ_API_KEY from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Choose the model and provider

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#agent-imports -->
```python
inventory_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)
```

**What happens here**

`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.

**Result:** We can reuse this model object in the following snippets.

## A basic agent with one tool

Let’s use a small inventory service. The tool is only a Python function here, but in a real project it could call a service, query a database, or read an approved repository.

### Define the stock tool

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#basic-agent-code -->
```python
@tool
def check_stock_service(item: str) -> str:
    """Return the remaining stock quantity for an inventory item."""
    stock_by_item = {
        "headphone": 6,
        "keyboard": 11,
        "laptop": 12,
    }
    quantity = stock_by_item.get(item.lower())
    if quantity is None:
        return f"{item} is not present in the stock database."
    return f"{item} has {quantity} units left in stock."
```

**What happens here**

The function looks up an item's stock using a lowercase name. It returns either a quantity or a clear message for an unknown item. The decorator and docstring describe the tool to the model.

**Result:** check_stock_service is our one allowed stock tool.

Then we create the agent:

### Create the one-tool agent

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#basic-agent-code -->
```python
basic_inventory_agent = create_agent(
    model=inventory_model,
    tools=[check_stock_service],
)
```

**What happens here**

We give create_agent our model and a list containing the stock tool. The framework can manage the tool-call conversation using these supplied parts.

**Result:** basic_inventory_agent is ready to receive a question.

### Ask about laptop stock

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#basic-agent-code -->
```python
basic_agent_result = basic_inventory_agent.invoke(
    {
        "messages": [
            SystemMessage("You are a helpful inventory assistant."),
            HumanMessage("How many laptops do we have?"),
        ]
    }
)
```

**What happens here**

We invoke the agent with the inventory instruction and a human question. The framework runs the allowed tool when the model requests it and returns the resulting message history.

**Result:** basic_agent_result contains the agent's conversation and response.

### Read the final reply

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#basic-agent-code -->
```python
print(basic_agent_result["messages"][-1].content)
```

**What happens here**

The returned messages list includes the run's conversation. `[-1]` selects its last message and content gives its text.

**Result:** We print the final response about laptop stock.

When a user asks, “How many laptops do we have?”, the agent can decide that `check_stock_service` is relevant. The framework handles the tool request, function call, tool result, and final answer.

---

## Give an agent multiple tools

One tool answers one type of question. Real users often ask questions that need more than one source of information.

### Define the price tool

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#multiple-tools-code -->
```python
@tool
def get_price_service(item: str) -> str:
    """Return the price in rupees for an inventory item."""
    price_by_item = {
        "headphone": 1999,
        "keyboard": 1499,
        "laptop": 54999,
    }
    price = price_by_item.get(item.lower())
    if price is None:
        return f"{item} does not have a price in the catalogue."
    return f"{item} costs Rs {price}."
```

**What happens here**

This tool looks up an item's price in rupees. Its input style matches the stock tool, but it provides different information.

**Result:** get_price_service supplies the price lookup.

### Give the agent both tools

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#multiple-tools-code -->
```python
shopping_agent = create_agent(
    model=inventory_model,
    tools=[check_stock_service, get_price_service],
)
```

**What happens here**

The tools list now contains stock and price lookups. The model can request either supplied tool as it works on the question.

**Result:** shopping_agent has two available tools.

### Ask a question needing both lookups

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#multiple-tools-code -->
```python
multi_tool_result = shopping_agent.invoke(
    {
        "messages": [
            SystemMessage("You are a helpful inventory assistant."),
            HumanMessage("Do we have laptops in stock, and what is the price?"),
        ]
    }
)
```

**What happens here**

We ask whether laptops are available and what they cost. The agent manages the tool requests and results needed for its answer.

**Result:** multi_tool_result contains the conversation from this run.

Now a question such as “Do we have laptops in stock, and what is the price?” can require two tools. The model chooses which one to call and in what order; the framework only lets it choose from the tools we supplied.

You can inspect the returned messages to see the flow:

### Inspect the agent's messages

<!-- snippet: code/Part I Understanding the Basics/8-Agents.ipynb#multiple-tools-code -->
```python
# Inspect the messages to see the agent's tool requests and final answer.
for agent_message in multi_tool_result["messages"]:
    print(f"{type(agent_message).__name__}: {agent_message.content}")
```

**What happens here**

We print each message's class name and content to follow the conversation. A tool-call AIMessage may have empty content: inspect its tool_calls property in the notebook if you also want the exact requested arguments.

**Result:** We can follow the human question, tool results, and final response.

This is useful while learning and debugging. It lets you see the user request, AI tool calls, tool results, and final response rather than treating the agent as a black box.

---

## Agent versus tool loop

The underlying idea has not changed:

### Follow the tool loop

<!-- snippet: code/Docs/Lessons/Part1/lesson8_final.md#supplement -->
```text
user request → model requests a tool → application runs an allowed tool
             → tool result returns to the model → final answer
```

**What happens here**

The model requests a tool. The application executes an allowed call and returns its result. The model then uses that result to write an answer.

**Result:** Tool execution happens in the application or framework.

In Lesson 7, we wrote each step ourselves. With `create_agent`, LangChain manages the standard loop. We still own the parts that matter most: the tool definitions, data access, permissions, error handling, and what the user is allowed to ask the system to do.

Start with [8-Agents.ipynb](../../../Part%20I%20Understanding%20the%20Basics/8-Agents.ipynb). It contains both the one-tool and multi-tool inventory examples.

## Check your understanding

1. What three things make up the basic agent in this lesson?
2. Can an agent call a tool that was not supplied in its `tools` list?
3. Why is a tool docstring useful to an agent?
4. What does `create_agent` manage for us, and what do we still control?

## Next lesson

We will make the agent more useful by connecting it to information that is relevant, current, and approved for the task.
