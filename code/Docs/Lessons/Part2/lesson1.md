1. Understanding agentic AI:

    **Generative AI** can create content and reason about the input we give it.

    **Agentic AI** builds on those capabilities to work toward a goal: it can choose the next step, use tools, and use the results to decide how to continue.

    For example, an agentic AI system could draft a LinkedIn post, ask for our approval, publish it through an authorized tool, and check the result. To answer a customer's question, it could look up the relevant database record before composing its response.

    **An AI agent** can carry out this cycle. Agentic AI describes the broader approach, which may involve one agent or several working together.

    We still build and control the software around the model. We choose the tools, manage the state, and set permissions and approval steps. The model proposes actions; our application decides whether and how to execute them.

2. LangChain versus LangGraph:

    Before we compare the frameworks, let’s name the work we want to arrange. Imagine receiving a request, validating it, and then writing a reply. We need a way to describe how those steps connect.

    **A workflow** is a set of connected steps that carry out a task. We define the steps and the rules for moving between them. For example: receive a request → validate it → write a reply. A workflow can also choose a branch, run independent work in parallel, or return to an earlier step.

    **LangChain** is our collection of model connections, messages, prompts, and tool helpers.

    **LangGraph** helps us arrange those pieces into workflows with state and explicit connections between steps. LangChain's create_agent already uses LangGraph underneath; here we build the graph ourselves to understand that control.

    **Multi-agent coordination** is another use for LangGraph: several agents can each handle a different part of a task. But let’s get our feet wet with two simple functions first. The same ideas about steps, connections, and shared data still apply.

    A graph with two fixed functions is a workflow. It does not become an autonomous agent just because we drew some arrows.

3. What is a Graph?

    **A graph** is a collection of nodes and the connections between them. It describes how things relate to one another. In this lesson, we use a graph to describe the steps of an application and how work moves between them.

    **Nodes** are the units of work. One node might check an input, another might look up a record, and another might ask a model to write an answer. In LangGraph, we write the work inside Python functions.

    **Edges** connect those nodes and describe which steps can run next. In a workflow graph, we draw them as arrows. A connection can lead to the next step, choose between paths, or return to an earlier step.

    **For example:** Receive a request → check the input → write a reply. Each action is a node; each arrow is an edge. If the input is invalid, another path could ask the user to correct it before continuing.

    **Why use a graph?** An application often needs several pieces of work to cooperate. Some steps depend on earlier results; others can run independently. A graph makes these relationships explicit, so we can inspect the paths, change a step, and see where decisions belong. A couple of direct function calls may be enough for a small task; a graph becomes useful as those connections grow.

    **LangGraph** gives us the building blocks to turn this plan into running code. We define the data the steps share, register our functions as nodes, and connect them with edges. The builder then creates a runnable graph. When we supply the starting input, LangGraph coordinates the connected steps and applies their updates to that shared data.

    **Our first graph** will use two ordinary Python functions in a fixed order. We do not need an LLM to learn the pattern. Once the connections make sense, we can put a model call or a tool inside a node.

4. Node, : It is a single task in our workflow.
every node is a python function to be executed.

5. Edges : it is the connector that connects one or more nodes,
it can be sequential, parallel or a loop.
In simple it controls the flow of execution (what is excuted after current.)

6. State : it is a shared, structured data object that acts as the central memory bank for your application, tracking all inputs, intermediate outputs, and messages as they flow through the graph
it is usually a kv pair.

The node in execution have full access to the state. a state is shared mutable and evolves as it moves the graph.

7. Reducers : a reducer is a function that defines how a state variable updates when a node returns a new value
                It is a policy driven : whether we add, replace or update the existing value

                Reducers in LangGraph define how updates from nodes are applied to the shared state.
                Each key in the state can have its own reducer, which determines whether new
                data replaces, merges, or adds to the existing value.

C:\a\pproj\AI\SecondTutorial\lg\1-chatbot\1-basicGraph.ipynb
