"""Execute Part II notebooks offline with a deterministic chat-model fixture.

From code/: uv run python ../scripts/validate_part_two.py
The real graph, tools, checkpoints, streams, and interrupts execute. The fixture
replaces provider calls and does not validate a hosted model's answer quality.
"""
import contextlib
import io
import json
import os
from pathlib import Path
from unittest.mock import patch

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
import nbformat

ROOT = Path(__file__).resolve().parents[1]


class OfflineChat(BaseChatModel):
    lesson: int

    @property
    def _llm_type(self):
        return "offline-lesson-check"

    def bind_tools(self, tools, **kwargs):
        return self

    def answer(self, messages):
        if self.lesson in (4, 5):
            results = [message for message in messages if isinstance(message, ToolMessage)]
            if not results:
                return AIMessage(content="", tool_calls=[{
                    "name": "check_stock_service", "args": {"item": "laptop"}, "id": "stock-1",
                }])
            if self.lesson == 5 and len(results) == 1:
                return AIMessage(content="", tool_calls=[{
                    "name": "get_price_service", "args": {"item": "laptop"}, "id": "price-1",
                }])
            return AIMessage(content="12 laptops available; two cost 109998 rupees." if self.lesson == 5 else "12 laptops available.")
        history = " ".join(message.text for message in messages if isinstance(message, HumanMessage))
        return AIMessage(content="Ada is learning about LLMs and LangGraph." if "Ada" in history else "No name has been supplied.")

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return ChatResult(generations=[ChatGeneration(message=self.answer(messages))])

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        for word in self.answer(messages).text.split():
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=word + " "))
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk


def verify(lesson, scope):
    if lesson == 1:
        assert [message.text for message in scope["response"]["messages"]] == ["Starting Message", "Step 1 completed.", "Step 2 completed."]
    elif lesson == 2:
        assert scope["sequential_result"]["value"] == 6
        logs = scope["parallel_result"]["logs"]
        assert len(logs) == 3 and "finish" in logs[-1].lower(), logs
        assert scope["conditional_graph"].invoke({"value": 1, "logs": []})["value"] == 4
        assert scope["conditional_graph"].invoke({"value": 5, "logs": []})["value"] == 6
        assert scope["loop_result"]["value"] == 3
        assert len(scope["loop_result"]["logs"]) == 3
    elif lesson == 3:
        assert [message.type for message in scope["response"]["messages"]] == ["human", "ai"]
    elif lesson in (4, 5):
        messages = scope["response"]["messages"]
        tools = [message for message in messages if isinstance(message, ToolMessage)]
        assert [message.content for message in tools] == (["12"] if lesson == 4 else ["12", "54999"])
        assert messages[-1].type == "ai" and not messages[-1].tool_calls
        # The branch also handles a reply that does not request any tools.
        with patch.object(OfflineChat, "answer", return_value=AIMessage(content="Hello.")):
            direct = scope["graph"].invoke({"messages": [HumanMessage("Hello")]})
        assert [message.type for message in direct["messages"]] == ["human", "ai"]
    elif lesson == 6:
        saved = scope["graph"].get_state(scope["user1_config"]).values["messages"]
        other = scope["graph"].get_state(scope["user2_config"]).values["messages"]
        assert len(saved) == 4 and len(other) == 2
        assert "Ada" in saved[-1].text and "Ada" not in other[-1].text
    elif lesson == 7:
        events = list(scope["graph"].stream({"messages": [HumanMessage("Hello")]}, stream_mode="updates"))
        assert len(events) == 1 and "chatbot" in events[0]
        chunks = list(scope["graph"].stream({"messages": [HumanMessage("Hello")]}, stream_mode="messages"))
        assert len(chunks) > 1 and all(metadata["langgraph_node"] == "chatbot" for _, metadata in chunks)
        assert "No name" in "".join(message.text for message, _ in chunks)
    elif lesson == 8:
        assert scope["paused"]["__interrupt__"]
        assert scope["approved_response"]["approved"] is True
        assert scope["rejected_response"]["approved"] is False
        assert scope["approved_response"]["result"] != scope["rejected_response"]["result"]
        # An ambiguous text value must not become approval through truthiness.
        config = {"configurable": {"thread_id": "invalid-decision-check"}}
        scope["graph"].invoke({"request": "Demo", "approved": False, "result": ""}, config)
        try:
            scope["graph"].invoke(scope["Command"](resume="False"), config)
        except ValueError:
            pass
        else:
            raise AssertionError("String approval should be rejected")


if __name__ == "__main__":
    entries = json.loads((ROOT / "part-two-lessons.json").read_text(encoding="utf-8"))
    for entry in entries:
        local = entry["local"]
        path = ROOT / "code/Part II Connecting the dots" / entry["filename"]
        book = nbformat.read(path, as_version=4)
        nbformat.validate(book)
        scope = {"__name__": "__lesson_check__"}
        output = io.StringIO()
        # Do not load API keys or enable telemetry while validating local logic.
        with patch.dict(os.environ, {"LANGSMITH_TRACING": "false", "LANGCHAIN_TRACING_V2": "false"}), patch("dotenv.load_dotenv", return_value=False), patch("langchain.chat_models.init_chat_model", return_value=OfflineChat(lesson=local)), contextlib.redirect_stdout(output):
            for cell in book.cells:
                if cell.cell_type == "code":
                    exec(compile(cell.source, f"{path.name}:{cell.id}", "exec"), scope)
            verify(local, scope)
        print(f"Part II lesson {local}: top-to-bottom execution and flow checks OK")
    print("All eight notebooks passed offline. No provider API calls were made.")
