1. Understanding agentic AI. :

    Agents are AI systems that have the capabilities of generative ai eg creating content reasoning.
    But now they also have the tools to go beyond and acheieve the task.
    Eg if a gen ai can write a linkedn post,
    Agentic ai can use tools to actually post it to linkedin too.

    If gen ai can work as a human like chatbot,
    agentic ai can give it powers to check your database and respond to the users request.


2.  LC vs LG :
    While langchain are the set of tools to work with an LLM,
    LG is the framework that can use the above tools to create a predefined
    workflows.

3. LG : it is a framework designed to build stateful, multi-agent AI applications that follow a specific workflow

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

                --------------------------------

behind the scene :

LangGraph Execution Model


1. Graph Definition
You define:

. The state schema

. Nodes (functions that perform tasks)

· Edges (which node connects to which)

2. Compilation
You call .compile() on the StateGraph.
This checks the graph structure and prepares it for execution.

3. Invocation

You run the graph with .invoke(initial_state).
LangGraph sends the initial state as a message to the entry node(s).

4. Super-Steps Begin
Execution proceeds in rounds. ( meaning the task proceeds in 1 step at a time. there coulbe a case where we may have multiple nodes
        in a round, which all needs to be executed, so it is called super steps.)


        -----------------------

C:\a\pproj\AI\SecondTutorial\lg\1-chatbot\1-basicGraph.ipynb
