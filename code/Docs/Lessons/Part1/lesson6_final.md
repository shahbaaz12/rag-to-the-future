# Lesson 6 — Give the Model Tools, Keep the Control

> **Review draft**
>
> This lesson introduces tool calling and the execution loop around it. The key idea is that the model may request a tool, but the application decides whether and how that tool runs.

## A note from me

A model can write a very convincing answer about the current weather, your order status, or a course module. That does not mean it has actually checked any of them.

Tools let the model request information or an action from the outside world. The important word is *request*. The model does not get to run random code on its own. Our application stays in charge.

## What you will be able to do

- define a small LangChain tool;
- let a model request that tool;
- execute only recognised tool calls; and
- explain the tool-execution loop.

---

## What is a tool?

A tool is simply a function thats it, a function that the application makes available to a model. It has a clear name, description, inputs, and output. A tool might read a database, look up a delivery status, search approved documents, or perform an action the user authorised.

For the first example, we use a tiny local lookup. It keeps the focus on the flow rather than adding another API key.

```python
@tool
def get_course_module(module_number: int) -> str:
    """Return the topic for a course module number from 1 through 6."""
    modules = {
        5: "messages, streaming, batching, and memory",
        6: "tools and tool-execution loops",
    }
    return modules.get(module_number, "That module number is not available.")
```

The docstring matters. It helps the model understand when the tool is useful and what its input means.

---

## The model requests; the application executes

First, bind the permitted tools to the model:

```python
tool_enabled_model = groq_model.bind_tools([get_course_module])
model_message = tool_enabled_model.invoke(messages)
```

The response may contain `tool_calls`. That is structured data describing the function the model wants to use and the arguments it proposes. It is not proof that the tool ran.

Our application then finds the requested tool in its allow-list, executes it, and returns a `ToolMessage` with the result.

```python
for tool_call in model_message.tool_calls:
    requested_tool = tools_by_name.get(tool_call["name"])
    if requested_tool is None:
        tool_result = "This tool is not available."
    else:
        tool_result = requested_tool.invoke(tool_call["args"])

    messages.append(
        ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
    )
```

Finally, send the model’s request and the tool result back to the model so it can give the user a normal answer.

```text
user request → model requests a tool → application validates and runs it
             → application sends result → model writes final answer
```

That is a tool-execution loop.

Notice what the model did here. It handed our application structured information saying that a particular function could help answer the user’s question. It did **not** automatically call the function.

Our application receives that request, checks whether the function is allowed, runs it with the proposed arguments, and returns the result to the model. That separation is deliberate: the model can suggest a tool, but the software we write controls what actually happens.

---

## Why the application must stay in control

The tool call is a suggestion from a model. Treat it like any other untrusted input. Before an application executes a real tool, it should decide:

- Is this tool on the allow-list?
- Are the arguments valid?
- Is this user allowed to perform this action?
- What happens if the external service is slow or fails?
- What should we log so we can investigate a mistake?

We will add stronger patterns around this later. For now, keep the core idea: models reason about tools; applications own the permissions and execution.

Work through the complete example in [6-Tools-and-Tool-Loops.ipynb](../../../Part%20I%20Understanding%20the%20Basics/6-Tools-and-Tool-Loops.ipynb).


## Next lesson

We will use these building blocks to connect a model to useful external information without asking it to guess.
