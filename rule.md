# Rule

Use this workflow for every task that produces code, a UI, a document, or a deck. Scale the ceremony to the task: even a one-line fix gets a one-line plan and ticket.

## Workflow

1. **Plan** — Before writing code or content, state the goal, scope (in and out), and constraints in a few lines.
2. **Ticket** — Turn the plan into the ticket template below.
3. **Assign** — Split the ticket into applicable FE, BE, Ops, QA, and Design sub-tasks. State why any unused roles are not applicable.
4. **Orchestrate** — Complete assigned sub-tasks one at a time and check them off. When all assigned roles are done, run a QA pass against the acceptance criteria. Reopen, fix, and re-check any gaps; do not close with gaps open.
5. **Close** — Summarize what shipped against the acceptance criteria and note anything explicitly descoped.

Do not jump straight to code before planning, ticketing, and assigning.

## Ticket template

```yaml
### Ticket: <short title>
Goal: <what this achieves>
Scope: <in / out>
Acceptance criteria:
- [ ] ...
- [ ] ...
Assigned:
- FE: <task, or "n/a — no UI surface">
- BE: <task, or "n/a">
- Ops: <task, or "n/a">
- QA: <task, or "n/a">
- Design: <task, or "n/a">
```

## Role responsibilities

- **FE** — UI components, client-side state, rendering, and interaction.
- **BE** — Business logic, data models, APIs, and integrations.
- **Ops** — Build/deploy configuration, environment setup, CI, and infrastructure scripts.
- **QA** — Appropriate test cases, edge cases, and final acceptance pass.
- **Design** — Visual language, layout, copy tone, and the style guide in `references/design-language.md`.

When literal sub-agents are unavailable, complete the applicable roles sequentially and identify which role is being handled.

## Code-quality rules

1. **Structured** — One clear responsibility per file or module; no grab-bag files.
2. **Small functions** — Keep functions focused and roughly under 20–30 lines; extract helpers instead of deeply nesting.
3. **Separated by layer** — Keep frontend, backend, design tokens/assets, and tests in separate files or folders. Do not mix UI components, business logic, and test code in one file.
4. **Clean code** — Use descriptive names, remove dead code and commented-out blocks, and comment only when the reasoning is not obvious from the code.

## Applicability

This rule applies to requests to build, add, fix, make, or ship code, UIs, documents, or decks. It does not apply to trivial requests with no code or visible deliverable, such as factual questions or quick explanations.

For any UI, deck, or document, apply the user's guided-realm visual language from *The Last Cachebender*, *Dungeons & Databases*, and *Silicon Lanes*, following `references/design-language.md` when it exists.
