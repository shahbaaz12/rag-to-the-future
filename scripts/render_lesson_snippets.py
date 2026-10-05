"""Render all three course parts with exact source snippets and teaching notes.

Run from code/: uv run python ../scripts/render_lesson_snippets.py
The first run aligns the older drafts with their notebooks. Later runs render
the edited drafts directly, so the author's prose remains the source of truth.
"""

import html
import io
import json
import re
import tokenize
from pathlib import Path
from urllib.parse import quote

import mistune
from bs4 import BeautifulSoup, NavigableString
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, PowerShellLexer, TextLexer
from temporal_design import apply_design

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "code/Docs/Lessons/Part1"
NOTEBOOKS = ROOT / "code/Part I Understanding the Basics"
PART_TWO = {entry["number"]: entry for entry in json.loads((ROOT / "part-two-lessons.json").read_text(encoding="utf-8"))}
PART_THREE = {entry["number"]: entry for entry in json.loads((ROOT / "part-three-lessons.json").read_text(encoding="utf-8"))}
ADVANCED_LESSONS = {**PART_TWO, **PART_THREE}
LAST_LESSON = max(ADVANCED_LESSONS)
TERMS = json.loads((ROOT / "lesson-terms.json").read_text(encoding="utf-8"))
ENCOUNTERED = {}
TERM_LOOKUP = {alias.lower(): entry for entry in TERMS for alias in [entry["term"], *entry.get("aliases", [])]}
TERM_PATTERN = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(alias) for alias in sorted(TERM_LOOKUP, key=len, reverse=True)) + r")(?!\w)", re.I)
FENCE = re.compile(r"```(\w+)\n(.*?)\n```", re.S)
NOTE = re.compile(r"<!-- snippet: (.*?) -->\n```(\w+)\n(.*?)\n```\n\n\*\*What happens here\*\*\n\n(.*?)\n\n\*\*Result:\*\* (.*?)(?=\n\n|\Z)", re.S)


def cell(book, index):
    path = next(NOTEBOOKS.glob(f"{book}-*.ipynb"))
    entry = json.loads(path.read_text(encoding="utf-8"))["cells"][index]
    return "".join(entry["source"]).strip("\n"), path, entry["id"]


def chunks(book, index):
    code, path, cell_id = cell(book, index)
    # Blank lines inside a class or loop must not split its indented body.
    return [(part, path, cell_id) for part in re.split(r"\n{2,}(?=\S)", code)]


def example(source, title, explanation, result):
    code, path, cell_id = source
    reference = path.relative_to(ROOT).as_posix() + "#" + cell_id
    return f"### {title}\n\n<!-- snippet: {reference} -->\n```python\n{code}\n```\n\n**What happens here**\n\n{explanation}\n\n**Result:** {result}"


def group(book, index, notes, select=None):
    sources = chunks(book, index)
    if select is not None:
        sources = [sources[i] for i in select]
    assert len(sources) == len(notes), (book, index, len(sources), len(notes))
    return "\n\n".join(example(source, *note) for source, note in zip(sources, notes))


IMPORTS = ("Import the building blocks", "These imports make the model constructor and the helpers used below available. We only need to run this setup once in the notebook session.", "The imported names are ready for the next snippets.")
ENV = ("Load the API key", "`load_dotenv()` reads the local .env file so the provider integration can find its API key. Keep the key in that file rather than putting it into the lesson code.", "The API settings are available in this Python process.")
MODEL = ("Choose the model and provider", "`init_chat_model` creates the model object. The model identifier selects what we ask to run; `model_provider` selects the integration that sends the request. Creating this object does not generate a reply yet.", "We can reuse this model object in the following snippets.")


def setup(book):
    return "## Set up once\n\nRun these snippets in order in the associated notebook. Later snippets reuse the objects created here.\n\n" + group(book, 1, [IMPORTS, ENV, MODEL]) + "\n\n"


def replacements(lesson):
    if lesson == 2:
        groq = group(1, 1, [
            ("Import Python's environment helper", "`os` lets us read the API settings that will be loaded into the environment.", "We can read settings with os.getenv."),
            ("Import the SDK and settings loader", "OpenAI is the SDK client we use for Groq's compatible API. load_dotenv lets us keep the key in a local file.", "The client constructor and settings loader are available."),
            ENV,
            ("Connect the client to Groq", "We give the client our Groq key and endpoint. `os.getenv` reads the settings; the endpoint has a fallback if the URL is absent from .env.", "groq_client points at Groq's API."),
            ("Send the first request", "`responses.create` sends the model name, the assistant's instructions, and our question. We keep the entire response in groq_response.", "The provider returns a response object. The generated excuse can vary."),
            ("Print the answer", "`output_text` extracts the generated text, so we can read the answer without printing all the response metadata.", "The model's answer appears in the notebook."),
            ("Optionally inspect available models", "These lines are commented out in the notebook. If you choose to uncomment them, models.list asks the provider for the model IDs available to the account.", "Nothing runs while these lines remain comments."),
        ])
        gemini = group(1, 3, [
            ("Switch to Gemini's SDK", "Gemini uses the google.genai client here. We reuse the environment settings loaded earlier.", "genai is available. Install google-genai to run this direct SDK example."),
            ("Create the Gemini client", "`genai.Client` reads the Gemini key from the environment. It is a separate provider client from groq_client.", "gemini_client is ready for the request."),
            ("Send the Gemini request", "The interaction has a model, a system instruction, and an input. The calling shape differs from Groq's SDK example, but we still send a prompt and receive a response.", "gemini_response holds the complete interaction response."),
            ("Read Gemini's answer", "We print the output_text from the interaction response. The exact wording is generated by the model.", "The answer appears in the notebook."),
        ])
        return {1: groq + "\n\n### Try the direct Gemini example\n\nContinue after the Groq setup above.\n\n" + gemini}
    if lesson == 3:
        notes = [
            ("Create a Groq model", "We choose the hosted model and the Groq integration. LangChain reads the key loaded during setup.", "groq_model is ready to use."),
            ("Ask the question", "`invoke` sends the question and waits for a complete reply. We store that reply in groq_response.", "groq_response is an AIMessage, with text and metadata."),
            ("Read text and metadata", "The first print shows the answer. The other two show the reported model name and token usage; `.get` handles a missing metadata key without an indexing error.", "We can inspect both the answer and information about the call."),
        ]
        return {0: group(2, 1, [IMPORTS, ENV]) + "\n\n" + group(2, 3, notes[:2], [0, 1]),
                1: group(2, 3, notes[2:], [2]),
                2: group(2, 5, [
                    ("Create the Gemini model", "We change the model identifier and provider integration. The invoke pattern stays familiar. The inline comment is copied from the notebook; both provider and identifier are different here.", "gemini_model is ready. GEMINI_API_KEY must be available."),
                    ("Ask Gemini a question", "We send the nursery-rhyme question through the same invoke method.", "gemini_response holds the model's reply."),
                    ("Inspect Gemini's reply", "We read the text, reported model and provider, and token usage using the same response properties.", "We can compare how the providers report their results."),
                ]),
                3: group(2, 7, [
                    ("Keep the comparison prompt fixed", "We use one goldfish prompt and one model name. That gives us a shared starting point for comparing temperature settings.", "Both calls below will receive the same prompt."),
                    ("Create both temperature settings", "The first model uses temperature 0.0; the second uses 2.0. Both use the same output limit and requested reasoning level. Lower temperature favours consistent choices; higher temperature allows more variation.", "We have two configured model objects. Neither has answered yet."),
                    ("Compare their answers", "We invoke each object with the shared prompt and print the answers beside their temperature labels. These are two separate API calls.", "We can compare the generated openings. Temperature is not a guarantee of quality or correctness."),
                ])}
    if lesson == 4:
        prompt_notes = [
            ("Import PromptTemplate", "This helper describes a reusable prompt with named placeholders.", "PromptTemplate is available."),
            ("Fill the question placeholder", "The template expects one value named question. We supply that value through invoke, which produces a prompt value. A missing question raises an error before we send the prompt to the model.", "prompt contains the filled-in teacher instruction and question."),
            ("Send the filled prompt", "We pass the prompt value to groq_model.invoke, limit the output, and print the response text.", "The model answers using the reusable template."),
            ("Keep reuse in mind", "This exact notebook comment points out that templates can be stored for reuse. It does not itself save a file. The supplementary JSON snippets below show that next step.", "No code runs here; this is a source comment."),
        ]
        return {0: group(3, 3, [
            ("Make a request to inspect", "We ask the model for a joke and keep its complete AIMessage response. Run the model setup above first.", "response holds the text and any metadata the provider reports."),
            ("Read the response properties", "`response.text` gives readable text. response_metadata reports model details, and usage_metadata reports token counts when supplied by the integration.", "We can inspect the answer, its model, and its token usage."),
        ]) + "\n\n" + group(3, 5, [
            ("Handle missing usage information", "`or {}` gives us an empty dictionary when the response has no usage metadata. This lets the next snippet use get safely.", "usage is a dictionary."),
            ("Inspect incoming and outgoing tokens", "We read input, output, and total token counts separately. If a count is absent, the printed fallback says not reported.", "We can see which counts were supplied for this request."),
            ("Record which model answered", "We print the provider and reported model name so a later comparison can identify which configuration produced the answer.", "We have identifying information alongside the usage counts."),
        ]), 1: group(3, 1, [MODEL], [2]),
                2: group(3, 7, [("Send a static prompt", "static_prompt is a fixed string. We send it directly and print the answer, with an output limit of 200 tokens.", "The model answers the Pikachu question.")], [0]),
                3: group(3, 7, [("Build a prompt from a changing question", "The f-string inserts users_question into the instruction. We can replace the user question at runtime without rewriting the surrounding wording.", "The model receives the comedian instruction and the sandwich question together.")], [1]),
                4: group(3, 9, prompt_notes)}
    if lesson == 5:
        return {0: group(4, 8, [
            ("Choose the streaming prompt", "We store the question before starting the stream. This separates what we ask from how we receive the answer.", "stream_prompt contains our burger-and-salad request."),
            ("Print each arriving chunk", "The loop receives chunks as the model produces them. `end=\"\"` keeps them on the same line, and flush=True asks Python to show them immediately. The final print adds a newline.", "The answer gradually appears while generation continues."),
            ("Why stream the answer?", "This source comment explains the experience we just created: the user can start reading before the complete response is ready.", "The comment documents the purpose; it does not make another API call."),
        ]), 1: group(4, 10, [
            ("Prepare independent prompts", "Each item asks a separate question. None needs the answer from an earlier item.", "batch_prompts holds three independent requests."),
            ("Run the batch and pair the results", "`batch` submits the list through LangChain. zip pairs each original prompt with its response so our prints remain easy to follow.", "We see a prompt and answer for every batch item. Provider limits still apply."),
        ]), 2: group(5, 3, [("Describe one Pokémon", "Pokemon inherits from BaseModel. Its fields describe the shape we want: name, type, level, and a list of evolution names. Field descriptions tell the model what belongs in each field.", "We have a Pydantic schema that checks the returned field types.")], [0]),
                3: group(5, 3, [("Wrap the model with the schema", "with_structured_output connects the Pokemon schema to the model call. We keep the wrapper in pokemon_model.", "The wrapper is ready to return a Pokemon object.")], [1]) + "\n\n" + group(5, 4, [
                    ("Ask for Pikachu's data", "The request still uses invoke, but it goes through the structured wrapper.", "pokemon contains the generated Pokemon object."),
                    ("Read the named fields", "We print the whole object, then use dot notation for its name and evolutions. A valid shape does not guarantee that every generated fact is correct.", "Our code can read the fields without scraping a paragraph."),
                ]),
                4: group(5, 6, [
                    ("Describe a list of Pokémon", "PokemonList is the outer object. Its pokemons field contains a list of Pokemon objects, reusing the schema we just defined.", "We have a nested schema: one list containing several structured entries."),
                    ("Create the Pokédex wrapper", "We wrap the same model with PokemonList for requests that need a collection.", "pokedex_model expects the nested result shape."),
                ]) + "\n\n" + group(5, 7, [
                    ("Request a small Pokédex", "We ask for three of Ash's Kanto Pokémon through the collection wrapper.", "pokedex holds the generated list of Pokémon objects."),
                    ("Read each nested entry", "We loop through pokedex.pokemons and access each object's name, type, and evolutions with dot notation.", "We can use every entry in the same predictable way."),
                ]),
                5: group(5, 9, [
                    ("Describe dictionary keys", "PokemonDict declares the keys and expected value types. TypedDict describes the shape for tooling and the structured-output schema; it does not perform Pydantic-style runtime validation on its own.", "We have a schema for a regular Python dictionary."),
                    ("Create the dictionary wrapper", "We pass PokemonDict to with_structured_output. This wrapper returns a dictionary rather than a Pydantic object.", "typed_dict_model is ready for the request."),
                ]) + "\n\n" + group(5, 10, [
                    ("Ask for Eevee's data", "We invoke the dictionary wrapper with the Pokédex question.", "pokemon_dict contains the generated keys and values."),
                    ("Read values with square brackets", "We access name and evolutions by their dictionary keys. This is the main difference in how we use the returned data.", "The values print without dot notation."),
                ]),
                6: group(4, 3, [("Inspect a human message", "HumanMessage holds the question text and the human role. Its type property shows the label; content shows the text.", "We can see both parts of the message explicitly.")]),
                7: group(4, 4, [("Send everything as one string", "The instruction and question share a single string. The model may infer their meaning, but our application has not marked a separate system instruction and user question.", "plain_text_response holds the answer to the combined prompt.")]),
                8: group(4, 5, [("Separate the rule from the question", "SystemMessage carries the chef instruction, while HumanMessage carries the question. We pass the list to invoke and print the response text.", "The model receives an explicit role for each message.")]),
                9: group(4, 6, [
                    ("Include an earlier reply", "The list contains instructions, the first question, an illustrative AI reply, and a follow-up. The notebook supplies that earlier reply itself; it was not generated by the preceding call.", "conversation_with_history contains context for the follow-up."),
                    ("Ask with the supplied history", "We resend the conversation list. The model can use the earlier messages to interpret the follow-up.", "The response uses the history that our application provided."),
                ])}
    if lesson == 7:
        return {0: group(7, 3, [
            ("Define the course lookup tool", "The decorator exposes this function as a tool. The docstring describes its purpose, module_number is the input, and the dictionary provides a local lookup. get supplies a fallback for an unknown module.", "The tool can answer a module-number lookup when our application runs it."),
            ("Keep an explicit tool list", "course_tools contains the allowed tools. tools_by_name maps each tool's name to the object we can execute later.", "Our application has an explicit lookup for permitted tools."),
        ]), 1: group(7, 5, [
            ("Tell the model which tools exist", "bind_tools attaches the allowed tool descriptions to the model interface. This makes the tools available for requests; it does not execute one.", "tool_enabled_model can produce tool-call requests."),
            ("Prepare the question", "The system message explains when to use the course lookup. The human message asks about module 6.", "messages contains the instruction and question."),
            ("Inspect the requested tool calls", "We invoke the model and inspect tool_calls. Each requested call describes a tool name and proposed arguments. The function has not run at this point.", "model_message holds the model's request, if it chose a tool."),
        ]), 2: group(7, 7, [
            ("Save the model's request", "We append the model message before adding tool results, keeping the request and its results together in the conversation.", "The message history includes the tool-call request."),
            ("Execute an allowed tool and return its result", "We look up the requested name in tools_by_name. A recognised tool runs with the proposed arguments; an unknown name receives a fallback. ToolMessage carries the result with the original call ID so the model can match it to the request.", "The history now contains the tool result for each request. This small example checks the tool name; real applications also need argument and permission checks."),
            ("Ask for the final answer", "We send the updated history back to the model. It can now use the tool result when composing an answer for the learner.", "final_response holds the final text. This example handles one round of tool calls; more complex requests may need a repeated loop."),
        ])}
    if lesson == 8:
        return {0: group(8, 3, [("Define the stock tool", "The function looks up an item's stock using a lowercase name. It returns either a quantity or a clear message for an unknown item. The decorator and docstring describe the tool to the model.", "check_stock_service is our one allowed stock tool.")], [0]),
                1: group(8, 3, [
                    ("Create the one-tool agent", "We give create_agent our model and a list containing the stock tool. The framework can manage the tool-call conversation using these supplied parts.", "basic_inventory_agent is ready to receive a question."),
                    ("Ask about laptop stock", "We invoke the agent with the inventory instruction and a human question. The framework runs the allowed tool when the model requests it and returns the resulting message history.", "basic_agent_result contains the agent's conversation and response."),
                    ("Read the final reply", "The returned messages list includes the run's conversation. `[-1]` selects its last message and content gives its text.", "We print the final response about laptop stock."),
                ], [1, 2, 3]),
                2: group(8, 5, [
                    ("Define the price tool", "This tool looks up an item's price in rupees. Its input style matches the stock tool, but it provides different information.", "get_price_service supplies the price lookup."),
                    ("Give the agent both tools", "The tools list now contains stock and price lookups. The model can request either supplied tool as it works on the question.", "shopping_agent has two available tools."),
                    ("Ask a question needing both lookups", "We ask whether laptops are available and what they cost. The agent manages the tool requests and results needed for its answer.", "multi_tool_result contains the conversation from this run."),
                ], [0, 1, 2]),
                3: group(8, 5, [("Inspect the agent's messages", "We print each message's class name and content to follow the conversation. A tool-call AIMessage may have empty content: inspect its tool_calls property in the notebook if you also want the exact requested arguments.", "We can follow the human question, tool results, and final response.")], [3])}
    return {}


def draft_note(language, code):
    """Notes for setup commands and conceptual examples already in the drafts."""
    if code == "uv init .":
        return "Initialise the project", "Run this inside the project folder. uv creates the basic Python project configuration.", "The folder now contains the project files."
    if code.startswith("uv add"):
        return "Install the dependencies", "The -r option reads package names from requirements.txt and adds them to the uv project.", "The project dependencies are installed and recorded."
    if code.startswith("uv run"):
        return "Run through the project environment", "uv run uses the project's managed environment to run this Python file. Manual activation is unnecessary for this command.", "The script runs with the project's installed packages."
    if "import langchain" in code or 'print("Everything is working fine")' in code:
        return "Check the installation", "We import LangChain, then print a simple message and its installed version. This is a small environment check before making any API requests.", "If both lines print, the import and script execution worked."
    if "GROQ_API_KEY=" in code:
        return "Store the provider settings", "These are .env entries, not Python statements. Replace the placeholders with your own keys and keep the file out of Git.", "The later load_dotenv call can load these settings."
    if "langchain-community" in code:
        return "List the packages", "Put these package names into requirements.txt. Some support later lessons; google-genai is needed for the direct Gemini SDK example.", "The installer has a list of dependencies to read."
    if code.startswith("Part I"):
        return "Name the notebook folder", "This is a folder name, not a terminal command. It matches the location of the course notebooks.", "The examples have a shared place in the project."
    if "valid_namespaces" in code:
        return "Load the saved template", "We read the JSON file and reconstruct its LangChain prompt template. Only load a template file you trust; the allowed namespace names the LangChain objects used here.", "loaded_template is ready for another question."
    if "template_path =" in code:
        return "Save the reusable template", "We choose a JSON path, create the prompts folder if needed, and write the existing dynamic_question_template. dumps serialises the template rather than sending a request to the model.", "The JSON file can be reused by another part of the application."
    if "from pathlib" in code:
        return "Import the file and serialisation helpers", "Path handles the file location. dumps and loads convert the LangChain template to JSON and reconstruct it later.", "The helpers for the supplementary save-and-load example are ready."
    if "input tokens" in code:
        return "Separate the two token counts", "Instructions, questions, and context become input tokens. The generated answer becomes output tokens.", "Both sides contribute to usage; the provider's pricing determines the charge."
    if '"I" |' in code:
        return "Picture the token pieces", "This is an illustrative split into tokens, including spaces and punctuation. It is not output from a particular model's tokenizer.", "A word and a token are not always the same unit."
    if code == "I love building AI apps!":
        return "Start with a string", "To Python this whole sentence is one string. A model's tokenizer will divide it into smaller pieces before the model processes it.", "The string can contain several tokens."
    if "system" in code.lower() and ("human" in code.lower() or "user" in code.lower()):
        return "Read the message roles", "The label tells us which text is the instruction, which is the user's request, and which is the assistant's answer. This is a conceptual example rather than executable code.", "The conversation has explicit roles."
    if "LangChain" in code:
        return "Follow the request path", "Our application uses LangChain's interface, which delegates to a provider integration. The provider hosts and runs the chosen model.", "The common interface sits between our code and the provider."
    if "model +" in code:
        return "Identify the agent's parts", "The model reasons about the request, instructions guide its behaviour, and allowed tools provide actions or information.", "The framework can coordinate these parts as an agent."
    if "model requests a tool" in code:
        return "Follow the tool loop", "The model requests a tool. The application executes an allowed call and returns its result. The model then uses that result to write an answer.", "Tool execution happens in the application or framework."
    if "load API key" in code:
        return "Follow a direct call", "We prepare credentials and a client before sending the input to a chosen model. After the response arrives, our application decides how to use it.", "The same broad sequence applies across providers."
    raise ValueError(f"Missing teaching note for {language}: {code[:100]}")


def prepare(lesson):
    path = DRAFTS / f"lesson{lesson}_final.md"
    markdown = path.read_text(encoding="utf-8")
    if "<!-- snippet:" in markdown:
        return
    if lesson == 6:
        # Preserve the approved notes and add source references to its fences.
        notebook = next(NOTEBOOKS.glob("6-*.ipynb"))
        cells = json.loads(notebook.read_text(encoding="utf-8"))["cells"]
        def reference_memory(match):
            entry = next(c for c in cells if c["cell_type"] == "code" and match[2] in "".join(c["source"]))
            return f'<!-- snippet: {notebook.relative_to(ROOT).as_posix()}#{entry["id"]} -->\n{match[0]}'
        path.write_text(FENCE.sub(reference_memory, markdown), encoding="utf-8")
        return
    updates = replacements(lesson)
    ordinal = -1

    def replace(match):
        nonlocal ordinal
        if match[1] != "python":
            return match[0]
        ordinal += 1
        return updates.get(ordinal, match[0])

    markdown = FENCE.sub(replace, markdown)
    if lesson in (4, 5, 7, 8):
        anchor = {4: "## Understand the response", 5: "## What else can we do", 7: "## What is a tool?", 8: "## A basic agent"}[lesson]
        book = {4: 3, 5: 4, 7: 7, 8: 8}[lesson]
        markdown = markdown.replace(anchor, setup(book) + anchor, 1)
    if lesson == 2:
        markdown = markdown.replace("openai\nlangchain", "openai\ngoogle-genai\nlangchain", 1)
    if lesson == 4:
        markdown = markdown.replace("If we forget `audience` or `sentence_count`", "If we forget `question`")
        markdown = markdown.replace("In the notebook, we save the template as JSON and load it again:", "The notebook mentions saving a template. These supplementary snippets extend that idea: we save the same template as JSON and load it again.")
        markdown = markdown.replace("dumps(explanation_template,", "dumps(dynamic_question_template,")
    if lesson == 5:
        markdown = markdown.replace("## Structured output: ask for data, not just prose", "## Structured output: ask for data, not just prose", 1)
        # The second notebook has its own setup; make that transition explicit.
        anchor = "### Pydantic: a validated Python object"
        markdown = markdown.replace(anchor, "### Set up the structured-output notebook\n\nSwitch to 5-Structured-Outputs.ipynb and run its setup first. This notebook uses the same provider and adds our schema helpers.\n\n" + group(5, 1, [IMPORTS, ENV, MODEL]) + "\n\n" + anchor, 1)
        markdown = markdown.replace("Without the earlier messages, the model would not know what “it” means.", "Without earlier context, a follow-up like this can become ambiguous.")

    # Format remaining draft-only examples using the same presentation. Their
    # source is the authored Markdown, not a fabricated notebook location.
    def supplement(match):
        language, code = match[1], match[2]
        if language == "python":
            pieces = re.split(r"\n{2,}(?=\S)", code)
        else:
            pieces = [code]
        return "\n\n".join(
            f"### {title}\n\n<!-- snippet: {path.relative_to(ROOT).as_posix()}#supplement -->\n```{language}\n{piece}\n```\n\n**What happens here**\n\n{explanation}\n\n**Result:** {result}"
            for piece in pieces for title, explanation, result in [draft_note(language, piece)]
        )

    # Protect notebook blocks while annotating remaining original fences.
    stored = []
    def protect(match):
        stored.append(match[0])
        return f"@@SOURCE_SNIPPET_{len(stored)-1}@@"
    markdown = NOTE.sub(protect, markdown)
    markdown = FENCE.sub(supplement, markdown)
    for i, content in enumerate(stored):
        markdown = markdown.replace(f"@@SOURCE_SNIPPET_{i}@@", content)
    path.write_text(markdown, encoding="utf-8")


def card(reference, language, code, explanation, result, number):
    source, location = reference.split("#", 1)
    if source.endswith(".ipynb"):
        entries = json.loads((ROOT / source).read_text(encoding="utf-8"))["cells"]
        actual = "".join(next(entry for entry in entries if entry["id"] == location)["source"])
        assert code in actual, f"Snippet differs from {source}, cell {location}"
    elif source.endswith(".py"):
        assert code in (ROOT / source).read_text(encoding="utf-8"), f"Snippet differs from {source}"
    lexer = {"python": PythonLexer, "powershell": PowerShellLexer}.get(language, TextLexer)(stripnl=False, ensurenl=False)
    formatter = HtmlFormatter(nowrap=True)
    lines = "".join(f'<span class="code-explorer__line" data-line="{i}">{highlight(line, lexer, formatter)}</span>' for i, line in enumerate(code.splitlines(), 1))
    comments = []
    if language == "python":
        comments = [item.string for item in tokenize.generate_tokens(io.StringIO(code).readline) if item.type == tokenize.COMMENT]
    comments_html = "".join(f'<p class="snippet-comment">{html.escape(comment)}</p>' for comment in comments)
    prose = mistune.create_markdown()(explanation).replace("<p>", '<p class="snippet-prose">')
    result_html = mistune.create_markdown()(result).removeprefix("<p>").removesuffix("</p>\n")
    return f'''<figure class="code-explorer snippet-card" data-source="{html.escape(reference)}">
<div class="code-explorer__panel"><div class="code-explorer__toolbar">
<p class="code-explorer__title">Snippet {number:02d}</p>
<div class="code-explorer__toolbar-actions"><span class="code-explorer__language">{html.escape(language.title())}</span><button class="code-explorer__copy" type="button" data-copy-code aria-label="Copy snippet {number}" title="Copy snippet">⧉</button></div></div>
<code class="code-explorer__source" hidden>{html.escape(code)}</code>
<pre class="code-explorer__lines"><code>{lines}</code></pre></div>
<figcaption class="snippet-explanation"><p class="snippet-label">What happens here</p>
{prose}
{f'<div class="snippet-source-comments"><span>Source comments</span>{comments_html}</div>' if comments else ''}
<p class="snippet-result"><strong>Result</strong> {result_html}</p>
<a class="snippet-source" href="{quote(source, safe='/')}">{html.escape(Path(source).name)} · {html.escape(location)}</a>
</figcaption></figure>'''


def add_learning_aids(page, article, lesson):
    """Highlight each term once in course order; carry its definition forward."""
    explanation_nodes = article.select(".snippet-prose, .snippet-result, .snippet-source")
    if lesson in ADVANCED_LESSONS:
        explanation_nodes = [node for node in article.select("p, li, td, .snippet-source") if not node.find_parent(class_="code-explorer__panel") and not node.find_parent(class_="snippet-source-comments") and not node.find_parent("pre")]
    for text_node in explanation_nodes:
        for node in list(text_node.descendants):
            if not isinstance(node, NavigableString):
                continue
            text = str(node)
            pieces = []
            cursor = 0
            for match in TERM_PATTERN.finditer(text):
                entry = TERM_LOOKUP[match[0].lower()]
                key = entry["term"]
                if key in ENCOUNTERED:
                    continue
                anchor = "term-" + re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
                ENCOUNTERED[key] = {**entry, "lesson": lesson, "anchor": anchor}
                pieces.append(NavigableString(text[cursor:match.start()]))
                mark = page.new_tag("mark", attrs={"class": f'lesson-term lesson-term--{entry["category"]}', "data-term": key, "id": anchor, "title": entry["definition"]})
                mark.string = match[0]
                pieces.append(mark)
                cursor = match.end()
            if pieces:
                pieces.append(NavigableString(text[cursor:]))
                for piece in pieces:
                    node.insert_before(piece)
                node.extract()

    navigation = page.new_tag("nav", attrs={"class": "lesson-pagination", "aria-label": "Continue to another lesson"})
    for destination, direction in [(lesson - 1, "previous"), (lesson + 1, "next")]:
        if 1 <= destination <= LAST_LESSON:
            if destination in ADVANCED_LESSONS:
                title = ADVANCED_LESSONS[destination]["title"]
            else:
                target = BeautifulSoup((ROOT / f"lesson-{destination}.html").read_text(encoding="utf-8"), "html.parser")
                title = target.select_one(".hero h1").get_text().strip().rstrip(".")
            href = f"lesson-{destination}.html"
            label = f"{'←' if direction == 'previous' else '→'} {direction.title()} · Lesson {destination}"
        else:
            title, href = ("Explore Part I", "part-one.html") if lesson <= 8 else (("Explore Part II", "part-two.html") if lesson in PART_TWO else ("Explore Part III", "part-three.html"))
            label = "← Course map" if direction == "previous" else "Course map →"
        link = page.new_tag("a", href=href)
        label_tag = page.new_tag("span")
        label_tag.string = label
        title_tag = page.new_tag("strong")
        title_tag.string = title
        link.extend([label_tag, title_tag])
        navigation.append(link)
    article.append(navigation)

    # A reused page shell may contain the previous lesson's glossary.
    for old in page.select(".glossary-toggle, #lesson-glossary, #lesson-terms"):
        old.decompose()
    glossary = BeautifulSoup(f'''<button class="glossary-toggle" type="button" data-glossary-toggle aria-label="Open lesson glossary" aria-expanded="false" aria-controls="lesson-glossary" title="Lesson glossary">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 5v15M12 5C8 2 4 3 2 4v15c3-1 6-1 10 1 4-2 7-2 10-1V4c-2-1-6-2-10 1Z"/></svg><span class="glossary-badge" aria-hidden="true">{len(ENCOUNTERED)}</span></button>
<aside id="lesson-glossary" class="glossary-panel" role="dialog" aria-labelledby="glossary-title" hidden><div class="glossary-header"><h2 id="glossary-title">Your lesson glossary</h2><button class="glossary-close" type="button" data-glossary-close aria-label="Close glossary">×</button><p class="glossary-intro">Terms introduced through Lesson {lesson}. Each is highlighted only at its first explanation.</p><label for="glossary-search">Find a term</label><input id="glossary-search" type="search" placeholder="e.g. init_chat_model" autocomplete="off"/><p class="glossary-count" data-glossary-count aria-live="polite"></p></div><ul class="glossary-list" data-glossary-list></ul></aside>''', "html.parser")
    page.body.append(glossary)
    data = page.new_tag("script", type="application/json", id="lesson-terms")
    data.string = json.dumps(list(ENCOUNTERED.values()), ensure_ascii=False).replace("<", "\\u003c")
    page.body.append(data)


def render(lesson):
    if lesson in ADVANCED_LESSONS:
        folder = "Part3" if lesson in PART_THREE else "Part2"
        path = ROOT / "code/Docs/Lessons" / folder / f'lesson{ADVANCED_LESSONS[lesson]["local"]}_final.md'
    else:
        path = DRAFTS / f"lesson{lesson}_final.md"
    markdown = path.read_text(encoding="utf-8")
    cards = []
    def substitute(match):
        cards.append(card(*match.groups(), len(cards) + 1))
        return f"\n\n@@RENDERED_SNIPPET_{len(cards)-1}@@\n\n"
    markdown = NOTE.sub(substitute, markdown)
    assert "```" not in markdown, f"Unannotated block in lesson {lesson}"
    body = mistune.create_markdown(plugins=["table"])(markdown)
    body = re.sub(r"<h1>.*?</h1>\n", "", body, count=1)
    body = re.sub(r"<h2>(.*?)</h2>", r'<h2 class="snippet-section">\1</h2>', body)
    for i, content in enumerate(cards):
        body = body.replace(f"<p>@@RENDERED_SNIPPET_{i}@@</p>", content)
    body = body.replace("../../../Part%20I%20Understanding%20the%20Basics/", "code/Part%20I%20Understanding%20the%20Basics/")
    body = body.replace("../../../Part%20II%20Connecting%20the%20dots/", "code/Part%20II%20Connecting%20the%20dots/")
    body = body.replace("../../../Part%20III%20Give%20the%20model%20something%20to%20read/", "code/Part%20III%20Give%20the%20model%20something%20to%20read/")
    page_path = ROOT / f"lesson-{lesson}.html"
    original = BeautifulSoup((page_path if page_path.exists() else ROOT / "lesson-6.html").read_text(encoding="utf-8"), "html.parser")
    if lesson in (7, 8):
        # Use the established document shell while keeping this page's title
        # and course navigation; older shells have unrelated condensed prose.
        template = BeautifulSoup((ROOT / "lesson-6.html").read_text(encoding="utf-8"), "html.parser")
        template.title.string = original.title.get_text()
        for selector in (".hero h1", ".hero .lede"):
            template.select_one(selector).string = original.select_one(selector).get_text()
        template.select_one(".eyebrow").clear()
        template.select_one(".eyebrow").append(f"PART I · OUT OF TIME · LESSON {lesson:02d}")
        description = original.find("meta", attrs={"name": "description"})
        if description:
            template.find("meta", attrs={"name": "description"})["content"] = description["content"]
        for link in template.select('a[href="lesson-5.html"], a[href="lesson-7.html"]'):
            next_lesson = lesson - 1 if link["href"] == "lesson-5.html" else lesson + 1
            link["href"] = f"lesson-{next_lesson}.html" if next_lesson <= 8 else "part-one.html"
            link.string = f"← Lesson {next_lesson}" if next_lesson < lesson else (f"Lesson {next_lesson} →" if next_lesson <= 8 else "Part I map →")
        original = template
        for label in original.select("footer p"):
            label.string = f"Part I · Out of Time · Lesson {lesson:02d}"
    if lesson in ADVANCED_LESSONS:
        entry = ADVANCED_LESSONS[lesson]
        part = "III" if lesson in PART_THREE else "II"
        part_title = "GIVE THE MODEL SOMETHING TO READ" if lesson in PART_THREE else "CONNECTING THE DOTS"
        original.title.string = f'Lesson {lesson} · {entry["title"]} · RAG to the Future'
        original.select_one(".hero h1").string = entry["title"]
        original.select_one(".hero .lede").string = entry["lead"]
        original.select_one(".hero .eyebrow").string = f'PART {part} · {part_title} · LESSON {entry["local"]:02d} / COURSE {lesson:02d}'
        original.find("meta", attrs={"name": "description"})["content"] = entry["lead"]
        for label in original.select("footer p"):
            label.string = f'Part {part} · {part_title.title()} · Lesson {entry["local"]:02d}'
    course_map = "part-one.html" if lesson <= 8 else ("part-two.html" if lesson in PART_TWO else "part-three.html")
    map_label = "Part I map" if lesson <= 8 else ("Part II map" if lesson in PART_TWO else "Part III map")
    # Update the header and footer as well as the navigation below the content.
    nav = original.select_one(".topbar nav")
    nav.clear()
    previous = f"lesson-{lesson-1}.html" if lesson > 1 else course_map
    following = f"lesson-{lesson+1}.html" if lesson < LAST_LESSON else course_map
    for href, label in [(previous, f"← Lesson {lesson-1}" if lesson > 1 else "← Course map"), ("#lesson", "Lesson"), (following, f"Lesson {lesson+1} →" if lesson < LAST_LESSON else "Course map →"), (course_map, map_label)]:
        link = original.new_tag("a", href=href)
        link.string = label
        nav.append(link)
    for link in original.select('footer a[href="part-one.html"], footer a[href="part-two.html"], footer a[href="part-three.html"]'):
        link["href"] = course_map
        link.string = "← " + map_label
    footer_links = original.select('footer a[href^="lesson-"]')
    for index, link in enumerate(footer_links):
        link["href"] = previous if index == 0 else following
        link.string = (f"← Lesson {lesson-1}" if lesson > 1 else "← Course map") if index == 0 else (f"Lesson {lesson+1} →" if lesson < LAST_LESSON else "Course map →")
    article = original.select_one("#lesson")
    article.clear()
    article["class"] = ["document"]
    article.attrs.pop("aria-labelledby", None)
    article.append(BeautifulSoup(body, "html.parser"))
    for table in article.select("table"):
        wrapper = original.new_tag("div", attrs={"class": "snippet-table", "tabindex": "0", "role": "region", "aria-label": "Lesson comparison table"})
        table.wrap(wrapper)
    add_learning_aids(original, article, lesson)
    for asset in ("lesson-code-explorer.css", "lesson-snippets.css", "lesson-glossary.css"):
        if not original.find("link", href=asset):
            original.head.append(original.new_tag("link", rel="stylesheet", href=asset))
    if not original.find("script", src="lesson-code-explorer.js"):
        original.body.append(original.new_tag("script", src="lesson-code-explorer.js", defer=True))
    # Theme assets belong in the head so the saved appearance is applied early.
    for old in original.find_all("link", href="theme-toggle.css"):
        old.decompose()
    original.head.append(original.new_tag("link", rel="stylesheet", href="theme-toggle.css"))
    if not original.find("script", src="theme-toggle.js"):
        original.head.append(original.new_tag("script", src="theme-toggle.js"))
    # Keep glossary initialisation after its data, including on repeated builds.
    for script in original.find_all("script", src="lesson-glossary.js"):
        script.decompose()
    original.body.append(original.new_tag("script", src="lesson-glossary.js", defer=True))
    apply_design(original, 1 if lesson <= 8 else 2 if lesson <= 16 else 3, lesson)
    page_path.write_text(str(original), encoding="utf-8")
    print(f"Lesson {lesson}: {len(cards)} explained snippets")


if __name__ == "__main__":
    for lesson in range(1, LAST_LESSON + 1):
        if lesson <= 8:
            prepare(lesson)
        render(lesson)
