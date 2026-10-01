"""Build the Lesson 6 review page from exact notebook snippets and teaching notes."""

import html
import json
import re
from pathlib import Path

import mistune
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "code/Part I Understanding the Basics/6-Memory.ipynb"
DRAFT = ROOT / "code/Docs/Lessons/Part1/lesson6_final.md"
PAGE = ROOT / "lesson-6.html"
cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
code_cells = {cell["id"]: "".join(cell["source"]).rstrip("\n") for cell in cells if cell["cell_type"] == "code"}

# Each note corresponds to a contiguous paragraph of the source code, in order.
groups = [
    ("Set up once", "Run these setup snippets first. All three examples use this same model object.", "memory-imports", [
        ("Import the building blocks", "We import the model constructor and three message types. SystemMessage holds instructions, HumanMessage holds our question, and AIMessage represents a model reply.", "The names we need are available for the next snippets."),
        ("Load the API key", "load_dotenv reads the local .env file so the Groq integration can find its API key in this notebook session.", "The API settings are available before we create the model."),
        ("Create the model connection", "init_chat_model creates the Groq model object. The model name selects the hosted model, and reasoning_effort sets the requested reasoning level. This prepares the object; invoke will send the actual request.", "We can reuse model for every example below. Make GROQ_API_KEY available before running the notebook."),
    ]),
    ("1. Manual memory", "The simplest memory is a Python list. Our application keeps the messages and sends them again on each turn.", "manual-code", [
        ("Start the conversation", "We start a list with the assistant's instruction. This is the first message that later requests will receive.", "messages contains one system message."),
        ("Send the first message and save the reply", "append adds Ada's introduction. invoke sends the current list to the model. We then add the reply as an AIMessage so the next request can include both sides of the exchange.", "The list now contains the instruction, Ada's introduction, and the model's reply."),
        ("Ask a follow-up with the same history", "We add the follow-up, then send the entire list again. The earlier introduction is still in that list, so the model has context for Ada's name and what she is learning. We also save this second reply.", "The model can answer using the introduction sent earlier. Its wording may vary."),
        ("Count what we have stored", "len(messages) counts message objects, rather than tokens. We have one instruction plus two human messages and two AI replies.", "Messages stored: 5"),
    ]),
    ("2. Manual memory with summarisation", "A growing history becomes more input on every call. Here we replace older details with a short summary. This example starts its own history list.", "summary-code", [
        ("Prepare a sample history", "We create a five-message conversation to practise on. Ada's name, Python preference, and Groq usage are the useful facts we want to carry forward.", "This replaces the messages list from the manual-memory example."),
        ("Turn the older messages into a summary", "messages[1:] skips the system instruction. The join builds text containing each message's role and content. We ask the model to summarise that text and take the response content.", "summary holds the generated summary. Creating it uses an additional model call."),
        ("Replace the full history", "We keep messages[0], the original instruction, and add the summary as another message. The full older conversation is no longer included in this list.", "Messages stored after summary: 2. Fewer messages only save tokens when their text is shorter too."),
        ("Ask using the compact context", "We append a new question and send the instruction, summary, and question together. The model now relies on the summary to answer.", "The answer can use the facts retained in the summary. Summaries can omit details; keep or recover exact facts when needed."),
    ]),
    ("3. Checkpointer", "A checkpointer stores and restores conversation state for a named thread. We use create_agent with no tools here as a simple conversation wrapper; the tools and agents lessons will explain it further.", "checkpointer-code", [
        ("Import the conversation wrapper and storage", "create_agent builds the conversation wrapper. InMemorySaver supplies a place to store its state inside this Python process.", "The imports are ready. This storage will disappear when the process ends."),
        ("Create the checkpointer", "We create one InMemorySaver instance. The agent in the next snippet will use this same instance to save and restore conversation state.", "memory is our local checkpointer."),
        ("Attach it to the agent", "We pass the existing model, an empty tools list, the assistant instruction, and our checkpointer to create_agent. The wrapper handles the saved conversation around each call.", "agent is ready to accept new messages with a thread configuration."),
        ("Choose a conversation ID", "thread_id names the conversation whose saved state we want to use. It identifies a thread, rather than authenticating a user. In this example we name the first thread user1.", "Calls with this configuration will continue the same conversation."),
        ("Send just the new introduction", "We send message1 with user1_config. The agent records the conversation in the checkpointer. The returned messages list includes the conversation state, so [-1] selects its latest reply.", "The user1 thread now contains Ada's introduction and the reply."),
        ("Continue the same thread", "We send only the new question with the same configuration. The agent restores the earlier state for this thread and includes that context in the model request.", "The model can use Ada's introduction even though we did not manually resend it."),
        ("Try a different thread", "user2_config selects a new thread. We ask for a name without supplying one in this conversation. The earlier user1 history is not restored for this ID.", "There is no supplied name in user2's context. The assistant should ask for it rather than claim to remember Ada."),
    ]),
]

original = DRAFT.read_text(encoding="utf-8")
intro = re.split(r"## (?:Set up once|1\. Manual memory)", original, maxsplit=1)[0]
ending = original.split("Work through the complete examples", 1)[1]
parts = [intro]
snippets = []
for heading, lead, cell_id, notes in groups:
    chunks = code_cells[cell_id].split("\n\n")
    assert len(chunks) == len(notes), (cell_id, len(chunks), len(notes))
    assert "\n\n".join(chunks) == code_cells[cell_id]
    parts.append(f"## {heading}\n\n{lead}\n")
    for code, (title, explanation, result) in zip(chunks, notes):
        parts.append(f"### {title}\n\n```python\n{code}\n```\n\n**What happens here**\n\n{explanation}\n\n**Result:** {result}\n")
        snippets.append((code, title, explanation, result, cell_id))
parts.append("Work through the complete examples" + ending)
markdown = "\n".join(parts)
DRAFT.write_text(markdown, encoding="utf-8")
renderer = mistune.create_markdown()
body = renderer(markdown)
body = re.sub(r"<h1>.*?</h1>\n", "", body, count=1)
body = re.sub(r"<h2>(.*?)</h2>", r'<h2 class="snippet-section">\1</h2>', body)

def card(snippet, number):
    code, title, explanation, result, cell_id = snippet
    formatter = HtmlFormatter(nowrap=True)
    lexer = PythonLexer(stripnl=False, ensurenl=False)
    lines = []
    for line_number, line in enumerate(code.splitlines(), 1):
        coloured = highlight(line, lexer, formatter)
        lines.append(f'<span class="code-explorer__line" data-line="{line_number}">{coloured}</span>')
    comments = [line.strip() for line in code.splitlines() if line.lstrip().startswith("#")]
    comment_html = "".join(f'<p class="snippet-comment">{html.escape(comment)}</p>' for comment in comments)
    return f'''<figure class="code-explorer snippet-card">
<div class="code-explorer__panel"><div class="code-explorer__toolbar">
<p class="code-explorer__title">Snippet {number:02d}</p>
<div class="code-explorer__toolbar-actions"><span class="code-explorer__language">Python</span><button class="code-explorer__copy" type="button" data-copy-code aria-label="Copy snippet {number}" title="Copy snippet">⧉</button></div></div>
<code class="code-explorer__source" hidden>{html.escape(code)}</code>
<pre class="code-explorer__lines"><code>{"".join(lines)}</code></pre></div>
<figcaption class="snippet-explanation"><p class="snippet-label">What happens here</p>
<p class="snippet-prose">{html.escape(explanation)}</p>
{f'<div class="snippet-source-comments"><span>Source comment</span>{comment_html}</div>' if comments else ''}
<p class="snippet-result"><strong>Result</strong> {html.escape(result)}</p>
<a class="snippet-source" href="code/Part%20I%20Understanding%20the%20Basics/6-Memory.ipynb">6-Memory.ipynb · {html.escape(cell_id)}</a>
</figcaption></figure>'''

# Replace each Markdown example and its teaching prose with the same styled card.
for number, snippet in enumerate(snippets, 1):
    pattern = r'<pre><code class="language-python">.*?</code></pre>\s*<p><strong>What happens here</strong></p>\s*<p>.*?</p>\s*<p><strong>Result:</strong>.*?</p>'
    body, count = re.subn(pattern, lambda match: card(snippet, number), body, count=1, flags=re.S)
    assert count == 1
body = body.replace('../../../Part%20I%20Understanding%20the%20Basics/', 'code/Part%20I%20Understanding%20the%20Basics/')
page = PAGE.read_text(encoding="utf-8")
if 'href="lesson-snippets.css"' not in page:
    page = page.replace("</head>", '<link rel="stylesheet" href="lesson-snippets.css"/></head>')
page, count = re.subn(r'(<article\b[^>]*id="lesson"[^>]*>).*?(</article>)', lambda m: m[1] + body + m[2], page, count=1, flags=re.S)
assert count == 1
PAGE.write_text(page, encoding="utf-8")
print(f"Rendered {len(snippets)} exact source snippets into Lesson 6.")
