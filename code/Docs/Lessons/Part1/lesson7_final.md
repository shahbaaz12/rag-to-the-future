# Lesson 7 — Agents: Models That Can Choose Tools

> **Review draft**
>
> This lesson turns the tool loop from Lesson 6 into an agent. An agent combines a model, instructions, and an approved tool set so it can decide which tool might help answer a request.

## A note from me

In Lesson 6, we wrote the tool-execution loop ourselves. The model asked for a function, our code ran it, and then we sent the result back for a final answer.

That is exactly the right way to understand the flow. But writing that loop again for every application becomes repetitive. An agent framework can manage the loop for us while we focus on defining useful tools and setting the rules around them.

## What you will be able to do

- explain what an agent adds to a chat model;
- create an agent with one tool;
- create an agent with several approved tools; and
- inspect the messages produced during an agent run.

---

## What is an agent?

An agent is a small system made from three main parts:

```text
model + instructions + allowed tools = agent
```

The model reads the user request and decides whether a tool can help. The agent framework runs the approved tool, adds its result to the conversation, and asks the model to produce the final answer.

An agent is not a magical employee that can do anything. It can only use the tools we give it, with the permissions and checks we build around those tools.

---

## A basic agent with one tool

Let’s use a small inventory service. The tool is only a Python function here, but in a real project it could call a service, query a database, or read an approved repository.

```python
@tool
def check_stock_service(item: str) -> str:
    """Return the remaining stock quantity for an inventory item."""
    stock_by_item = {"headphone": 6, "keyboard": 11, "laptop": 12}
    quantity = stock_by_item.get(item.lower())
    if quantity is None:
        return f"{item} is not present in the stock database."
    return f"{item} has {quantity} units left in stock."
```

Then we create the agent:

```python
basic_inventory_agent = create_agent(
    model=inventory_model,
    tools=[check_stock_service],
)
```

When a user asks, “How many laptops do we have?”, the agent can decide that `check_stock_service` is relevant. The framework handles the tool request, function call, tool result, and final answer.

---

## Give an agent multiple tools

One tool answers one type of question. Real users often ask questions that need more than one source of information.

```python
shopping_agent = create_agent(
    model=inventory_model,
    tools=[check_stock_service, get_price_service],
)
```

Now a question such as “Do we have laptops in stock, and what is the price?” can require two tools. The model chooses which one to call and in what order; the framework only lets it choose from the tools we supplied.

You can inspect the returned messages to see the flow:

```python
for agent_message in multi_tool_result["messages"]:
    print(f"{type(agent_message).__name__}: {agent_message.content}")
```

This is useful while learning and debugging. It lets you see the user request, AI tool calls, tool results, and final response rather than treating the agent as a black box.

---

## Agent versus tool loop

The underlying idea has not changed:

```text
user request → model requests a tool → application runs an allowed tool
             → tool result returns to the model → final answer
```

In Lesson 6, we wrote each step ourselves. With `create_agent`, LangChain manages the standard loop. We still own the parts that matter most: the tool definitions, data access, permissions, error handling, and what the user is allowed to ask the system to do.

Start with [7-Agents.ipynb](../../../Part%20I%20Understanding%20the%20Basics/7-Agents.ipynb). It contains both the one-tool and multi-tool inventory examples.

## Check your understanding

1. What three things make up the basic agent in this lesson?
2. Can an agent call a tool that was not supplied in its `tools` list?
3. Why is a tool docstring useful to an agent?
4. What does `create_agent` manage for us, and what do we still control?

## Next lesson

We will make the agent more useful by connecting it to information that is relevant, current, and approved for the task.
