# Lesson 7 — Give the Model Tools, Keep the Control

> **Review draft**
>
> This lesson introduces tool calling and the execution loop around it. The key idea is that the model may request a tool, but the application decides whether and how that tool runs.

## A note from me

A model can write a very convincing answer about the current weather, your order status, or a course module. That does not mean it has actually checked any of them.

**Tools** let the model request information or an action from the outside world. The important word is *request*. The model does not get to run random code on its own. Our application stays in charge.

## What you will be able to do

- define a small LangChain tool;
- let a model request that tool;
- execute only recognized tool calls; and
- explain the tool-execution loop.

---

## Set up once

Run these snippets in order in the associated notebook. Later snippets reuse the objects created here.

### Import the building blocks

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-1 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
```

**What happens here**

These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.

**Result:** The imported names are ready for the next snippets.

### Load the API key

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-1 -->
```python
# Load GROQ_API_KEY from the local .env file.
load_dotenv()
```

**What happens here**

`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.

**Result:** The API settings are available in this Python process.

### Choose the model and provider

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-1 -->
```python
groq_model = init_chat_model(
    "openai/gpt-oss-120b",
    model_provider="groq",
)
```

**What happens here**

`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.

**Result:** We can reuse this model object in the following snippets.

## What is a tool?

**A tool** is simply a function thats it, a function that the application makes available to a model. It has a clear name, description, inputs, and output. A tool might read a database, look up a delivery status, search approved documents, or perform an action the user authorized.

For the first example, we use a tiny local lookup. It keeps the focus on the flow rather than adding another API key.

### Define the course lookup tool

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-3 -->
```python
@tool  # This decorator registers the function as a tool that can be used in LangChain.
def get_course_module(module_number: int) -> str:
    """Return the topic for a course module number from 1 through 7."""
    modules = {
        1: "AI foundations",
        2: "environment setup and direct model calls",
        3: "LangChain and model settings",
        4: "responses and prompts",
        5: "streaming, batching, structured output, and messages",
        6: "conversation memory and checkpointers",
        7: "tools and tool-execution loops",
    }
    return modules.get(module_number, "That module number is not available.")
```

**What happens here**

The decorator exposes this function as a tool. The docstring describes its purpose, module_number is the input, and the dictionary provides a local lookup. get supplies a fallback for an unknown module.

**Result:** The tool can answer a module-number lookup when our application runs it.

### Keep an explicit tool list

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-3 -->
```python
course_tools = [
    get_course_module
]  # This list can be expanded with more tools as needed.
tools_by_name = {course_tool.name: course_tool for course_tool in course_tools}
```

**What happens here**

course_tools contains the allowed tools. tools_by_name maps each tool's name to the object we can execute later.

**Result:** Our application has an explicit lookup for permitted tools.

**The docstring** matters. It helps the model understand when the tool is useful and what its input means.

---

## The model requests; the application executes

First, bind the permitted tools to the model:

### Tell the model which tools exist

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-5 -->
```python
tool_enabled_model = groq_model.bind_tools(course_tools)
```

**What happens here**

bind_tools attaches the allowed tool descriptions to the model interface. This makes the tools available for requests; it does not execute one.

**Result:** tool_enabled_model can produce tool-call requests.

### Prepare the question

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-5 -->
```python
messages = [
    SystemMessage("Use the course tool when the learner asks about a module number."),
    HumanMessage("What will I learn in module 6?"),
]
```

**What happens here**

The system message explains when to use the course lookup. The human message asks about module 6.

**Result:** messages contains the instruction and question.

### Inspect the requested tool calls

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-5 -->
```python
model_message = tool_enabled_model.invoke(messages)
print("Requested tool calls:", model_message.tool_calls)
```

**What happens here**

We invoke the model and inspect tool_calls. Each requested call describes a tool name and proposed arguments. The function has not run at this point.

**Result:** model_message holds the model's request, if it chose a tool.

The response may contain `tool_calls`. That is structured data describing the function the model wants to use and the arguments it proposes. It is not proof that the tool ran.

Our application then finds the requested tool in its allow-list and executes it.

**ToolMessage** carries the result back to the model.

### Save the model's request

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-7 -->
```python
messages.append(model_message)
```

**What happens here**

We append the model message before adding tool results, keeping the request and its results together in the conversation.

**Result:** The message history includes the tool-call request.

### Execute an allowed tool and return its result

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-7 -->
```python
for tool_call in model_message.tool_calls:
    requested_tool = tools_by_name.get(tool_call["name"])
    if requested_tool is None:
        # Do not execute a tool that the application did not explicitly allow.
        tool_result = "This tool is not available."
    else:
        tool_result = requested_tool.invoke(tool_call["args"])

    messages.append(
        ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"],
        )
    )
```

**What happens here**

We look up the requested name in tools_by_name. A recognized tool runs with the proposed arguments; an unknown name receives a fallback.

**ToolMessage** carries the result with the original call ID so the model can match it to the request.

**Result:** The history now contains the tool result for each request. This small example checks the tool name; real applications also need argument and permission checks.

### Ask for the final answer

<!-- snippet: code/Part I Understanding the Basics/7-Tools-and-Tool-Loops.ipynb#tool-loop-7 -->
```python
final_response = tool_enabled_model.invoke(messages)
print(final_response.text)
```

**What happens here**

We send the updated history back to the model. It can now use the tool result when composing an answer for the learner.

**Result:** final_response holds the final text. This example handles one round of tool calls; more complex requests may need a repeated loop.

Finally, send the model’s request and the tool result back to the model so it can give the user a normal answer.

### Follow the tool loop

<!-- snippet: code/Docs/Lessons/Part1/lesson7_final.md#supplement -->
```text
user request → model requests a tool → application validates and runs it
             → application sends result → model writes final answer
```

**What happens here**

The model requests a tool. The application executes an allowed call and returns its result. The model then uses that result to write an answer.

**Result:** Tool execution happens in the application or framework.

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

Work through the complete example in [7-Tools-and-Tool-Loops.ipynb](../../../Part%20I%20Understanding%20the%20Basics/7-Tools-and-Tool-Loops.ipynb).


## Next lesson

We will let a framework manage this same loop as an agent, while we continue to control its tools and boundaries.
