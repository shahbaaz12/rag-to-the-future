# RAG to the Future — Draft 1

## Core premise

**RAG to the Future** is a three-part learning journey about three fears: falling behind, losing control, and leaving behind something unreliable.

The learner builds the same AI companion throughout all three parts. It begins as a voice, becomes an assistant that can act, and eventually becomes a system that can be trusted with meaningful responsibilities.

The website is the Flux Capacitor. Its three branches represent the three journeys, and each lesson repairs or upgrades a component needed for the next jump.

## Part I — Out of Time

Everyone seems to have already crossed into the AI age. Colleagues are building agents, feeds are full of unfamiliar terminology, and trying a chatbot has made the learner feel further behind.

Then the professor arrives.

> “You haven’t run out of time. You’ve been starting in the wrong place.”

He has accomplished time travel using the Flux Capacitor, but its navigation intelligence is unreliable. It invents destinations, forgets previous instructions, and cannot understand his research journals.

The learner travels back to the professor’s first workshop, when there are no polished assistants—only a model connection, scattered research notes, and an unfinished machine.

**Mission:** teach the machine enough to find the way home.

| Lesson | Story moment | Learning focus |
|---|---|---|
| 1. Is Anybody There? | The machine speaks for the first time. | Calling an LLM, messages, tokens, response variability, model limitations. |
| 2. Coordinates, Please | The destination controls require exact fields. | Prompt construction, examples, structured outputs, schemas, validation. |
| 3. You Told Me That Yesterday | The machine forgets between conversations. | Conversation history, context windows, memory, limits. |
| 4. The Professor’s Notebooks | The answers are scattered across records. | Document loading, metadata, chunking, preserving context. |
| 5. Finding the Right Memory | Questions use different words from the notebook. | Embeddings, semantic similarity, similarity limits. |
| 6. The Memory Vault | Searching every page becomes impractical. | Vector stores, indexing, retrieval, filters, inspection. |
| 7. An Answer with Evidence | The machine can consult notes before answering. | RAG, grounding, citations, abstention. |
| 8. The First Jump | Navigation must be proved before the machine is entered. | Evaluation set; retrieval vs. answer failures. |

The learner returns home with a working **Professor’s Archive Assistant**.

## Part II — Your Children’s Tomorrow

Years have passed. The learner’s children inherit the workshop and expand the assistant into an intelligence that runs its operations. It answers questions, orders parts, schedules repairs, and coordinates other systems.

Then a routine request triggers a chain of wrong decisions. The children are stranded at a remote workshop, and the system cannot arrange a safe return.

The professor’s warning defines the second part:

> “Everything you learned still works. But the world has started asking the machine to do more than answer.”

**Mission:** turn a knowledgeable assistant into a capable, controlled operator.

| Lesson | Story moment | Learning focus |
|---|---|---|
| 9. Give It Hands | Knowing a part number does not place an order. | Tool calling, argument schemas, execution, tool errors. |
| 10. A Plan Before a Leap | Some repairs have a known sequence. | Deterministic workflows, routing, graph state, nodes, edges. |
| 11. The Machine Chooses | An unfamiliar fault requires a next-tool choice. | Agent loops, action/observation, stopping conditions, bounded autonomy. |
| 12. Ask Before Changing Tomorrow | The agent proposes a consequential action. | Checkpoints, persistence, human approval, resuming work. |
| 13. The Almost-Right Part | Search finds a similar component with the wrong model number. | Keyword search, hybrid retrieval, rank fusion, reranking. |
| 14. One Question, Several Archives | A repair needs overview and precise specification. | Hierarchical retrieval, parent/child context, metadata, routing. |
| 15. Follow the Missing Clue | One retrieval attempt cannot resolve the fault. | Conversational rewriting, agentic RAG, retries, evidence sufficiency. |
| 16. The Rescue Run | The assistant coordinates the whole return. | Capstone: retrieval, tools, state, approvals, progress. |

The learner gets the children home. During the rescue, the professor disappears into an earlier timeline. His last message says:

> “The machine passed the demonstration. We never tested the world around it.”

## Part III — The Last Departure

The learner follows the professor into a frontier version of the workshop: unreliable power, intermittent connections, limited compute, and replacement parts that do not quite match the manuals.

The system from Part II now fails in revealing ways. Requests time out. A tool retries an order twice. Documents contradict one another. A cheaper model behaves differently. The dashboard looks healthy while users receive incorrect answers.

**Mission:** make the system dependable enough to bring everyone home—and leave something the next generation can maintain.

| Lesson | Story moment | Learning focus |
|---|---|---|
| 17. The Test Track | A few successful answers prove too little. | Golden datasets, component/end-to-end evaluation, regression checks. |
| 18. The Confident Impostor | The machine agrees with an incorrect diagnosis under pressure. | Correctness, faithfulness, sycophancy, judge limits, benchmarks. |
| 19. The Poisoned Almanac | A retrieved document tries to redirect the assistant. | Prompt injection, evidence vs. instructions, permissions, boundaries. |
| 20. Read the Instruments | The journey fails and the cause is unclear. | Traces, logs, retrieval inspection, outcomes, latency, cost. |
| 21. Enough Power for One Jump | Extra model calls consume scarce resources. | Token budgets, model selection, context reduction, caching, trade-offs. |
| 22. It Worked in the Professor’s Lab | Behaviour changes outside the workshop. | Packaging, Docker, configuration, secrets, reproducible deployment. |
| 23. When the Connection Breaks | A consequential operation fails halfway through. | Timeouts, retries, idempotency, recovery, fallbacks, escalation. |
| 24. The Future Is Unwritten | The final departure happens under difficult conditions. | Capstone: deploy, evaluate, observe, break, repair, justify. |

The professor reaches for the controls, then steps aside.

> “You know how it works now.”

For the first time, the learner chooses the destination.

## Source-material mapping

- **Part I:** Weekly AI Learning Lab Weeks 1–2 and the basic RAG work.
- **Part II:** Weeks 4–5, Week 10 advanced RAG, and the Agentic RAG project.
- **Part III:** Docker work, Week 11, evaluation projects, observability notes, and production examples.
- **Optional alternate timelines:** MCP, multi-agent coordination, Deep Agents, provider-specific implementations, the interview coach, and shipment-triage projects.

## Narrative progression

**Understand an answer → control an action → earn trust in a system.**

The 24 lessons are provisional chapter names. They can be split into smaller lessons while preserving the three-act arc.
