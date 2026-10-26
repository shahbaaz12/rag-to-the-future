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
from langgraph.errors import GraphRecursionError
from threading import Barrier
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]


class OfflineChat(BaseChatModel):
    lesson: int

    @property
    def _llm_type(self):
        return "offline-lesson-check"

    def bind_tools(self, tools, **kwargs):
        return self

    def answer(self, messages):
        if self.lesson == 3:
            return AIMessage(content="Thanks for letting me know. What time on Friday afternoon would you prefer? I will confirm availability.")
        if self.lesson == 4:
            results = [message for message in messages if isinstance(message, ToolMessage)]
            if not results:
                context = " ".join(message.text for message in messages)
                employee = "EMP102" if "EMP102" in context else "EMP101"
                return AIMessage(content="", tool_calls=[{
                    "name": "get_leave_balance", "args": {"employee_id": employee}, "id": "leave-1",
                }])
            remaining = json.loads(results[-1].content)["remaining"]
            return AIMessage(content=f"You have {remaining} paid leave days remaining.")
        if self.lesson == 5:
            results = [message for message in messages if isinstance(message, ToolMessage)]
            if not results:
                return AIMessage(content="", tool_calls=[{
                    "name": "find_routes", "args": {"origin": "Mumbai", "destination": "Goa"}, "id": "routes-1",
                }])
            if len(results) == 1:
                route_ids = json.loads(results[0].content)
                return AIMessage(content="", tool_calls=[
                    {"name": "get_route_details", "args": {"route_id": route_id}, "id": f"detail-{i}"}
                    for i, route_id in enumerate(route_ids)
                ])
            return AIMessage(content="The sample train costs INR 900 and fits INR 2000. The sample flight costs INR 4500 and exceeds it.")
        if self.lesson == 6:
            context = messages[0].text.split("Selected topics, in order: ", 1)[1].split(".", 1)[0]
            return AIMessage(content=f"Beginner explanation and practice for: {context}.")
        if self.lesson == 7:
            return AIMessage(content="1. Cook rice. 2. Cook peas and carrots. 3. Combine and serve for two.")
        return AIMessage(content="Offline response.")

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return ChatResult(generations=[ChatGeneration(message=self.answer(messages))])

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        for word in self.answer(messages).text.split():
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=word + " "))
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk


def verify(lesson, scope):
    case = TestCase()
    if lesson == 1:
        messages = scope["response"]["messages"]
        assert [message.content for message in messages] == [
            "Starting Message", "Step 1 completed.", "Step 2 completed.",
        ]
        assert all(isinstance(message, HumanMessage) for message in messages)
        another = scope["graph"].invoke({"messages": ["Another start"]})
        assert [message.content for message in another["messages"]] == [
            "Another start", "Step 1 completed.", "Step 2 completed.",
        ]
    elif lesson == 2:
        assert scope["pizza_result"]["total"] == 540
        assert scope["pizza_result"]["status"] == "Confirmed at INR 540"
        for items in ([], ["Unknown pizza"]):
            with case.assertRaises(ValueError):
                scope["pizza_graph"].invoke({**scope["pizza_input"], "items": items})
        # Swapping calculation and discount loses the discount.
        reversed_state = {**scope["pizza_input"], **scope["apply_coupon"](scope["pizza_input"])}
        reversed_state.update(scope["calculate_total"](reversed_state))
        assert reversed_state["total"] == 600

        trip = scope["trip_result"]
        assert len(trip["messages"]) == 4
        assert all(word in trip["report"] for word in ("Planning", "Weather", "Flights", "Hotels"))
        # The barrier requires all three lookups to be active together.
        barrier = Barrier(3)
        with patch("time.sleep", side_effect=lambda seconds: barrier.wait(timeout=5)):
            joined = scope["trip_graph"].invoke(scope["trip_input"])
        assert len(joined["messages"]) == 4 and joined["report"].count("Goa") == 4
        assert scope["trip_input"]["messages"] == []

        for text, category, handler in (
            ("Urgent: the site is down", "urgent", "urgent_handler"),
            ("My bill is incorrect", "billing", "billing_handler"),
            ("How do I change my name?", "general", "general_handler"),
            ("Urgent: my bill is incorrect", "urgent", "urgent_handler"),
        ):
            trace = io.StringIO()
            with contextlib.redirect_stdout(trace):
                ticket = scope["ticket_graph"].invoke({"text": text, "type": "", "response": ""})
            assert ticket["type"] == category and ticket["response"]
            assert trace.getvalue().splitlines() == [f"classify -> {category}", handler]

        assert scope["otp_result"]["tries"] == 2 and scope["otp_result"]["status"] == "verified"
        assert scope["locked_result"]["tries"] == 3 and scope["locked_result"]["status"] == "locked"
        for entries, attempts in ((["123456"], 1), (["000000", "111111", "123456"], 3)):
            result = scope["otp_graph"].invoke({**scope["otp_input"], "entries": entries})
            assert result["tries"] == attempts and result["verified"] is True
            assert result["status"] == "verified"
        assert scope["otp_input"]["tries"] == 0
        # Reproduce the optional missing-limit experiment with a fresh graph.
        unbounded = scope["StateGraph"](scope["OtpState"])
        for name in ("ask_otp", "verify", "success", "locked"):
            unbounded.add_node(name, scope[name])
        unbounded.add_edge(scope["START"], "ask_otp")
        unbounded.add_edge("ask_otp", "verify")
        unbounded.add_conditional_edges(
            "verify", lambda state: "correct" if state["verified"] else "retry",
            {"correct": "success", "retry": "ask_otp", "locked": "locked"},
        )
        unbounded.add_edge("success", scope["END"])
        unbounded.add_edge("locked", scope["END"])
        with case.assertRaises(GraphRecursionError):
            unbounded.compile().invoke(scope["locked_input"], {"recursion_limit": 6})
    elif lesson == 3:
        assert scope["response"]["status"] == "draft ready"
        assert scope["response"]["email"] == scope["email_input"]["email"]
        assert scope["response"]["tone"] == "friendly and concise"
        assert scope["response"]["draft"]
    elif lesson in (4, 5):
        messages = scope["response"]["messages"]
        tools = [message for message in messages if isinstance(message, ToolMessage)]
        if lesson == 4:
            assert len(tools) == 1 and json.loads(tools[0].content)["remaining"] == 6
            assert scope["response"]["employee_id"] == "EMP101"
            assert scope["response"]["status"] == "answered"
            other = scope["graph"].invoke({**scope["leave_input"], "employee_id": "EMP102"})
            other_tool = next(message for message in other["messages"] if isinstance(message, ToolMessage))
            assert json.loads(other_tool.content)["remaining"] == 12
        else:
            assert len(tools) == 3 and tools[0].name == "find_routes"
            assert json.loads(tools[0].content) == ["TRAIN-01", "FLIGHT-01"]
            assert {json.loads(message.content)["price"] for message in tools[1:]} == {900, 4500}
            assert scope["response"]["budget"] == 2000
            assert scope["response"]["status"] == "answered"
        assert messages[-1].type == "ai" and not messages[-1].tool_calls
        # The branch also handles a reply that does not request any tools.
        with patch.object(OfflineChat, "answer", return_value=AIMessage(content="Hello.")):
            initial = scope["leave_input"] if lesson == 4 else scope["travel_input"]
            direct = scope["graph"].invoke({**initial, "messages": [HumanMessage("Hello")]})
        assert [message.type for message in direct["messages"]] == ["human", "ai"]
    elif lesson == 6:
        first = scope["saved_student1"]
        second = scope["saved_student2"]
        assert len(first["messages"]) == 8 and first["topics"] == ["lists", "tuples"]
        assert len(second["messages"]) == 4 and second["topics"] == ["loops", "functions"]
        current = scope["graph"].get_state(scope["student1_config"]).values
        assert current["topics"] == ["dictionaries"] and len(current["messages"]) == 10
        assert current["student_id"] == "student1" and current["level"] == "beginner"
        assert scope["graph"].get_state(scope["student2_config"]).values["topics"] == ["loops", "functions"]
        assert len(scope["merged"]) == 1 and scope["merged"][0].text == "Corrected explanation."
    elif lesson == 7:
        events = list(scope["graph"].stream(scope["recipe_input"], stream_mode="updates"))
        assert [list(event)[0] for event in events] == ["prepare_request", "write_recipe"]
        assert set(events[0]["prepare_request"]) == {"request", "status"}
        assert set(events[1]["write_recipe"]) == {"recipe", "status"}
        chunks = list(scope["graph"].stream(scope["recipe_input"], stream_mode="messages"))
        assert len(chunks) > 1 and all(metadata["langgraph_node"] == "write_recipe" for _, metadata in chunks)
        assert "rice" in "".join(message.text for message, _ in chunks)
    elif lesson == 8:
        assert scope["paused"]["__interrupt__"]
        payload = scope["paused"]["__interrupt__"][0].value
        assert payload["order_id"] == "ORD-102" and payload["amount_inr"] == 5000
        assert scope["approved_response"]["approved"] is True
        assert scope["rejected_response"]["approved"] is False
        assert scope["approved_response"]["status"] == "refund processed"
        assert scope["rejected_response"]["status"] == "refund rejected"
        assert scope["approved_response"]["amount"] == 5000
        # An ambiguous text value must not become approval through truthiness.
        config = {"configurable": {"thread_id": "invalid-decision-check"}}
        scope["graph"].invoke(scope["refund_input"], config)
        pending = scope["graph"].get_state(config)
        assert pending.values["status"] == "awaiting review" and pending.next == ("review",)
        with case.assertRaises(ValueError):
            scope["graph"].invoke(scope["Command"](resume="False"), config)


if __name__ == "__main__":
    entries = json.loads((ROOT / "site/part-two-lessons.json").read_text(encoding="utf-8"))
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
