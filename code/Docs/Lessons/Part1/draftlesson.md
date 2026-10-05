# Part I — LLM Application Foundations

> Draft lesson plan for **RAG to the Future**. This document describes what we will build, why each capability matters, and how the lessons connect. Implementation comes later.

## The idea

We will build a simple **study assistant** that explains topics, handles follow-up questions, summarizes supplied notes, and uses small tools for data lookup and calculation. Each lesson introduces one capability through a familiar problem.

Examples should require almost no domain knowledge: “Explain HTTP to a beginner” and “How long will these two lessons take?” are enough. Reuse the assistant when continuity helps, while keeping exercises small enough to understand independently.

## Keep story, explanation, and code separate

The time-travel story in [material.md](../../../../material.md) can continue in optional introductions or a separate story section. The professor and workshop belong there. They do not determine application requirements, sample data, variable names, or technical terminology.

| Layer | Purpose | Content |
|---|---|---|
| Optional story | Continue the narrative. | A short scene that can be skipped without losing technical information. |
| Explanation | Teach the concept directly. | A practical problem, plain-language explanation, familiar example, and expected outcome. |
| Code exercise — later | Demonstrate the concept. | A small implementation with its own inputs, behavior, and checks, using ordinary names and data. |

**Independence check:** Removing every story section must leave the explanations and exercises complete. The explanation must make sense without reading code. Each code exercise must state its task without referring back to a story event.

This draft develops the explanations and exercise ideas. Story scenes can be authored separately. No code is included yet, and technical lesson titles stay descriptive so learners can find topics directly.

## Who this is for

This part is for learners who have tried AI chat tools but want to understand how an AI application works. No machine-learning background is assumed. Programming familiarity will help when implementation lessons are added, but this draft contains no code, setup commands, or library-specific recipes.

By the end, the learner should be able to explain the path from a user's question to a model response, distinguish conversation history from learned knowledge, and describe how an application validates output and executes tools.

## Proposed scope and ordering

The existing Part1 notes are the primary scope for this draft. They cover LLM foundations, LangChain, prompts, messages, memory, tools, agents, structured output, and middleware. We will retain those topics and arrange them into ten consecutive lessons, filling the current numbering gap at lesson 8.

The broader outline in [material.md](../../../../material.md) currently ends Part I with an archive assistant built using RAG. **This draft proposes a different boundary:** Part I establishes the assistant foundations, with a small, bounded agent as its final exercise. Document retrieval and the full archive assistant become the next learning block. Advanced agents and consequential actions can remain in the later operator-focused part.

This is a proposal for review. Existing lesson files and the broader outline do not need to be renamed or rewritten yet. If the original three-part boundary is retained, these foundation lessons can become opening sub-lessons, with the tools-and-agents lessons moved to Part II.

| Lesson | Technical topic | Capability gained |
|---|---|---|
| 1 | AI, LLMs, and the Application | Understand the system we are building and its limits. |
| 2 | Your First LLM Interaction | Send a request to a model and inspect its response. |
| 3 | Tokens, Context, and Model Selection | Understand tokens, context, and model choices. |
| 4 | Introducing LangChain | Use LangChain as a common application interface. |
| 5 | Prompts, Templates, and Messages | Construct reusable prompts and message sequences. |
| 6 | Conversation History and Memory | Manage conversation history and summaries. |
| 7 | Streaming and Batching | Understand streaming and batching. |
| 8 | Structured Output and Validation | Produce and validate structured results. |
| 9 | Tools and the Execution Loop | Request tools and complete the execution loop. |
| 10 | Agents, Workflows, and Middleware | Combine tools, agent decisions, and middleware. |

## Lesson 1 — AI, LLMs, and the Application

**Practical problem:** A learner has used chatbots but does not know how AI, ML, deep learning, LLMs, and AI applications fit together.

**What we will learn:** Build a practical vocabulary: artificial intelligence is the broad field; machine learning develops behavior from data; deep learning uses neural networks; and an LLM is a language model that can generate responses from context. An AI application also needs ordinary software around the model to manage inputs, data, tools, and results.

Discuss why the field feels fast-moving without turning the lesson into a catalogue of products. Our starting point is the request-and-response cycle because later capabilities build on it.

**What we will make:** A plain-language blueprint of the study assistant: user request, application, model, and response. Identify what the model provides and what the surrounding application must control.

**Demonstration idea:** Compare “What is HTTP?” with “What did I write in my private notes yesterday?” A fluent answer alone does not establish access to the learner's notes.

**Learning outcome:** The learner can describe the assistant's purpose and explain why an LLM is only one component.

**Next problem:** We understand the application structure and now need one working model interaction.

## Lesson 2 — Your First LLM Interaction

**Practical problem:** We need to send a question to a model and inspect its response before adding abstractions.

**What we will learn:** Follow one request from the application to a model and back. Distinguish the user's text, the request sent to the provider, and the response returned to the application. Introduce connection settings and credentials conceptually, without setup instructions.

Read the response as more than an answer string: the surrounding result may also contain usage information, completion status, or other metadata. A request can fail, and repeated successful requests need not produce identical text.

**What we will make:** A single-turn assistant that explains a topic. It has no conversation history, tools, or private reference material yet.

**Demonstration idea:** Ask “Explain HTTP in three sentences,” then repeat the request. Inspect what stayed consistent, what varied, and what would need verification.

**Learning outcome:** The learner can trace one complete model interaction and distinguish a returned answer from a failed request.

**Next problem:** The request works, but its resource use and behavior are still unfamiliar.

## Lesson 3 — Tokens, Context, and Model Selection

**Practical problem:** A long conversation no longer fits, and a different model gives a different answer to the same request.

**What we will learn:** Tokens are units used to represent model input and output; they are not reliably equivalent to words. The context window limits the information available in an interaction. Instructions, conversation messages, and tool results all contribute to the context the application manages.

Explore model selection through task quality, response time, resource use, deployment needs, and supported capabilities. Read model names using their provider's documentation rather than treating naming conventions as universal rules.

Separate two choices often mixed together: hosted versus self-hosted deployment, and proprietary versus open-weight or open-source licensing. Available weights do not automatically imply an unrestricted license or free operation.

Introduce temperature as a sampling control where supported. Lower temperature does not guarantee truth or identical results; higher temperature does not automatically improve creativity. Exact settings belong in later model-specific implementation material.

**What we will make:** A comparison plan for choosing the assistant's model, using the same tasks for each candidate: explain HTTP, summarize a supplied paragraph, and rewrite an explanation for a beginner.

**Learning outcome:** The learner can explain why “the biggest model” and “the lowest temperature” are insufficient selection rules.

**Next problem:** Trying another model should not require rewriting the application.

## Lesson 4 — Introducing LangChain

**Practical problem:** We want to try another model, but connection details are spreading throughout the application design.

**What we will learn:** Introduce LangChain as a framework that helps organize model interactions and related application components. Begin with the direct interaction from lesson 2 so the learner understands what the framework is abstracting.


Discuss a common interface for invoking models and handling messages. A shared interface can reduce repetitive integration work, but it does not make providers identical. Model capabilities, options, and response details still need checking.

**What we will make:** A topic-explanation exercise with a replaceable model integration. We will plan how to try another model without rewriting the assistant's purpose and conversation flow.

**Demonstration idea:** Send the same request through two model configurations and compare both answer quality and capability differences.

**Learning outcome:** The learner can explain why a framework is useful and which responsibilities remain with the application.

**Next problem:** A reusable connection still needs clear, reusable instructions.

## Lesson 5 — Prompts, Templates, and Messages

**Practical problem:** The assistant changes tone, omits important details, or receives an incomplete request because instructions are assembled inconsistently.

**What we will learn:** A prompt supplies the instructions and context for a task. Distinguish fixed instructions from values supplied for a particular request. Introduce message roles such as system, human/user, and AI/assistant before using them to construct a conversation.

Explain prompt templates through purpose, required variables, examples, and reuse. A template can help detect missing required inputs; it does not establish that the values are correct, safe, or meaningful. Handling extra inputs depends on the template mechanism. Saving a prompt separately makes it easier to review and maintain.

**What we will make:** A reusable “explain a topic” interaction that accepts the topic, learner experience level, and desired level of detail. For example: HTTP, beginner, short explanation.

**Demonstration idea:** Compare an underspecified question with a request containing a clear audience, task, and response expectation. Also show an incomplete request that needs clarification.

**Learning outcome:** The assistant receives a consistent task description with explicit inputs.

**Next problem:** Good instructions do not make the assistant remember the previous turn.

## Lesson 6 — Conversation History and Memory

**Practical problem:** The learner says “explain that more simply,” but the assistant no longer has the earlier explanation available.

**What we will learn:** Conversation continuity comes from information supplied or retrieved by the application. It is not evidence that the model has learned the conversation permanently.

Distinguish stored conversation history from the subset included in the current model context. Introduce recent-message windows, summaries of older messages, and explicitly stored preferences as different ways to retain useful information.

Summaries reduce volume but can lose detail or preserve mistakes. Important facts should remain inspectable and correctable. Different users or sessions must not accidentally share history.

**What we will make:** A multi-turn study assistant that understands follow-up questions, retains recent context, and uses a concise summary when the conversation grows.

**Demonstration idea:** Tell the assistant “I am new to networking and have 30 minutes to study.” Discuss HTTP, then request a recap that fits the available time. Compare complete history, truncated history, and a summary that omitted the time limit.

**Learning outcome:** The learner can explain what the assistant remembers, where it is stored, and what can be lost.

**Next problem:** Conversation works, but long responses and repeated requests feel slow to use.

## Lesson 7 — Streaming and Batching

**Practical problem:** A long answer leaves the user waiting without feedback, and several independent notes need summaries.

**What we will learn:** Streaming exposes a response incrementally so a person can begin reading before it is complete. Batching groups multiple independent requests for processing. They address different needs and can have different operational behavior.

Streaming does not inherently improve correctness or reduce total generation time. A partial response may be unfinished or unsuitable for immediate downstream use. Batching still requires the application to associate each result with its input and handle failures individually; it is not the same as combining unrelated questions into one prompt.

**What we will make:** Two planned interaction modes: a live explanation that appears progressively, and a batch task that summarizes three short, supplied paragraphs separately.

**Demonstration idea:** Interrupt a streamed answer and include one failed request in a batch. Define what the learner should see in each case.

**Learning outcome:** The learner can choose an appropriate delivery mode and describe partial or failed results honestly.

**Next problem:** Readable prose is still awkward for a application that requires specific fields.

## Lesson 8 — Structured Output and Validation

**Practical problem:** The assistant responds in prose, but the application needs consistent fields to display or process.

**What we will learn:** Structured output gives a response an explicit shape. Introduce schemas, field types, required values, permitted choices, and validation. Separate asking for a format from checking that the returned result meets the application's requirements.

A structurally valid result can still contain incorrect information. Missing or uncertain information needs an explicit representation or a clarification step, rather than an invented value.

**What we will make:** A study-request record with a topic, experience level, available minutes, and status indicating whether more information is needed. Given “I am a beginner and want to study HTTP for 30 minutes,” the assistant should extract those values. If the time is absent, it should preserve that uncertainty instead of silently choosing a duration.

**Demonstration idea:** Compare a valid record, a record missing a required field, and a correctly shaped record that changes the user's stated time from 30 to 60 minutes.

**Learning outcome:** The learner can distinguish format validation from factual verification.

**Next problem:** A properly shaped answer still needs a reliable way to retrieve application data and perform calculations.

## Lesson 9 — Tools and the Execution Loop

**Practical problem:** The assistant guesses how long a lesson takes because it has not consulted the application's lesson list.

**What we will learn:** A tool is a capability the application exposes for the model to request. The model proposes a tool and arguments; the application validates the request, executes the permitted operation, and returns its result. The model can then use that result in its response.

Trace the full loop: user request, tool request, argument validation, execution, observation, and final response or next step. Tool execution can fail or return insufficient information. A request to run a tool is not proof that it ran successfully.

**What we will make:** An assistant with two small, read-only tools: a calculator and an exact lookup over a fixed sample lesson list containing names and durations. This exercise needs no database, external service, or document-retrieval system.

**Demonstration idea:** Ask for the duration of a named lesson, then calculate the total duration of two lessons. Include an unknown lesson and a failed lookup to show when clarification or an error response is appropriate.

**Learning outcome:** The assistant can use returned results and distinguish success, missing data, and tool failure.

**Next problem:** Some requests need several steps, and the application must bound how those steps are chosen.

## Lesson 10 — Agents, Workflows, and Middleware

**Practical problem:** The assistant can use individual tools, but a multi-step request may cause repeated calls, unnecessary work, or an unsupported conclusion.

**What we will learn:** Contrast a fixed workflow, whose sequence is defined by the application, with an agent loop, where the model chooses next steps within application-defined limits. Use a fixed workflow when the sequence is already known.

Introduce middleware as application logic around model or tool interactions. Give it concrete purposes: validate a request, record a tool result, enforce a call budget, or stop a loop. Distinguish these enforced controls from instructions merely asking the model to behave.

**What we will make:** A bounded study assistant that can interpret a request, consult the permitted tools, perform a calculation, and produce a structured result. It must stop when the task is complete, essential information is missing, a tool failure prevents progress, or its step budget is exhausted.

**Demonstration idea:** Supply a tiny lesson list: HTTP basics takes 20 minutes and caching basics takes 25 minutes. Ask “Can I finish both in 60 minutes?” The assistant should look up the durations, calculate 45 minutes, and report that 15 minutes remain. Also try a missing duration or unavailable lesson and check that it does not invent a result.

**Learning outcome:** The learner can inspect the assistant's actions and explain why it answered, requested clarification, or stopped.

**Next topic:** The user asks a question whose answer is buried across their study documents. The assistant needs a way to find relevant evidence before answering. That becomes the entry point to RAG.

## Final experience: what the assistant would do

At the end of this foundation block, a learner could ask the assistant to explain HTTP, simplify the explanation in a follow-up, summarize supplied notes, extract a structured study request, and calculate whether selected lessons fit into the available study time.

The assistant would carry useful conversation context forward, show progress during longer responses, and explain when it lacks information. Its limited agent loop would use only the available tools and stop within a defined budget.

Searching a document collection and producing evidence-backed answers across those documents remain topics for the next learning block. The sample lesson lookup is deliberately small and uses exact records.

## Completion checks

Use a small set of scenarios throughout the lessons so progress is visible:

| Scenario | Expected behavior |
|---|---|
| Clear explanation request | Gives an answer suited to the specified audience. |
| Follow-up referring to an earlier answer | Uses the conversation context supplied by the application. |
| Request missing essential information | Identifies the gap and asks for clarification. |
| Structured study request | Meets the schema and does not silently invent missing values. |
| Calculation using known lesson durations | Uses the lookup and calculator results. |
| Unknown lesson or failed tool | Reports the limitation without claiming successful execution. |
| Repeated tool requests | Stops when the configured execution limit is reached. |
| Question requiring unavailable document evidence | Acknowledges the evidence gap and motivates retrieval. |

These checks demonstrate the intended behavior on selected examples; they do not establish general reliability.

## Mapping from the current notes

| Current file | Proposed destination | Reason for the change |
|---|---|---|
| lesson1.md | Lesson 1 | Establish vocabulary, motivation, and the project goal. |
| lesson2.md | Lessons 2–3 | Separate the first connection from model-selection trade-offs. |
| lesson3.md | Lessons 3–4 | Explain model behavior before adding the LangChain abstraction. |
| lesson4.md | Lessons 2–3 and 5 | Separate response inspection, tokens, and prompt construction. |
| lesson5.md | Lessons 5–7 | Introduce message roles before memory; give streaming and batching a distinct purpose. |
| lesson6.md | Lesson 9 | Teach structured arguments and validation before tool execution. |
| lesson7.md | Lesson 10 | Explain agents only after the complete tool loop is understood. |
| lesson8.md — currently absent | Lesson 8 | Fill the sequence with structured output. |
| lesson9.md | Lessons 8 and 10 | Separate output contracts from controls around execution. |
| lesson10.md | Lesson 6 | Teach history and summarization together as context-management choices. |

## Suggested format for the eventual lessons

Keep the optional story in a clearly separate section. The technical explanation should begin with a practical problem, teach the concept directly, and compare a successful example with a revealing failure. End with a learning outcome and the next technical question. The future code exercise should repeat its own task, inputs, and expected behavior so it can be followed independently.

When code is introduced later, it should implement this progression in small steps. Avoid adding a framework, a new model, memory, and tools in the same first exercise: learners should be able to explain each capability before combining them.
