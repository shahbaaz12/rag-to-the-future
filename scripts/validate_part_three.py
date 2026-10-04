"""Execute Part III with offline chat/embedding fixtures and real retrieval code.

Run from code/: uv run python ../scripts/validate_part_three.py
This checks pipeline behaviour, not hosted-model or semantic-embedding quality.
"""
import ast
import contextlib
import hashlib
import io
import json
import os
import re
from pathlib import Path
from unittest.mock import patch

import nbformat
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import Field

ROOT = Path(__file__).resolve().parents[1]


class OfflineEmbeddings(Embeddings):
    """Stable lexical vectors for exercising the real vector-store implementation."""
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text):
        vector = [0.0] * 256
        for word in re.findall(r"\b[\w-]+\b", text.lower()):
            if word in {"the", "a", "is", "in", "and", "to", "of", "what", "how", "does"}:
                continue
            index = int.from_bytes(hashlib.sha256(word.encode()).digest()[:2], "big") % 256
            vector[index] += 3 if word in {"grasshopper", "aerotherm", "e922", "rag"} else 1
        if not any(vector):
            vector[0] = 1
        return vector


class OfflineChat(BaseChatModel):
    lesson: int
    calls: list[list[str]] = Field(default_factory=list)

    @property
    def _llm_type(self):
        return "offline-rag-check"

    def with_structured_output(self, schema, **kwargs):
        def classify(prompt):
            text = str(prompt).split("Question: ")[-1].lower()
            route = "SUMMARY" if any(word in text for word in ["compare", "overview", "all products"]) else "DETAIL"
            return schema(route=route)
        return RunnableLambda(classify)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        texts = [message.text for message in messages]
        self.calls.append(texts)
        if texts[0].startswith("Rewrite the latest question"):
            answer = "Who helped the grasshopper in winter?"
        elif self.lesson == 1:
            answer = "Hello!" if texts[-1] == "Hello!" else "RAG retrieves text and adds it to the prompt before generation. [course-note-2]"
        elif self.lesson == 2:
            answer = "The ant helped the hungry grasshopper in winter. [The_Ant_and_the_Grasshopper.txt]"
        elif self.lesson == 3:
            answer = "E922 means a brush jam. Turn off the robot and remove hair or thread from the brush. [NEX-1008_Nexa_CleanBot_S2.txt]"
        elif "variant" in texts[-1].lower():
            answer = "AeroTherm Plus, HCL-101-P, adds humidity control."
        else:
            answer = "Climate Control contains AeroTherm X1 and BreezeSense V2."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=answer))])


def verify(lesson, scope):
    if lesson == 1:
        result = scope["result"]
        assert result["needs_retrieval"] and len(result["documents"]) == 2
        assert any(doc.metadata["source"] == "course-note-2" for doc in result["documents"])
        assert scope["greeting"]["documents"] == [] and not scope["greeting"]["needs_retrieval"]
        assert "Context:" in scope["model"].calls[0][0]
        assert "Context:" not in scope["model"].calls[1][0]
        assert set(result) == {"question", "documents", "answer", "needs_retrieval"}
    elif lesson == 2:
        assert len(scope["chat_history"]) == 4
        assert [message.type for message in scope["chat_history"]] == ["human", "ai", "human", "ai"]
        assert scope["first_turn"]["standalone_question"] == scope["first_turn"]["question"]
        assert scope["second_turn"]["question"] == "Who helped him?"
        assert scope["second_turn"]["standalone_question"] == "Who helped the grasshopper in winter?"
        for turn in [scope["first_turn"], scope["second_turn"]]:
            assert any(doc.metadata["source"] == "The_Ant_and_the_Grasshopper.txt" for doc in turn["documents"])
        assert len(scope["model"].calls) == 3
        assert scope["model"].calls[1][0].startswith("Rewrite")
        assert scope["model"].calls[-1][-1] == "Who helped him?"
    elif lesson == 3:
        assert scope["tokenize"]("E922 NEX-1008") == ["e922", "nex-1008"]
        assert scope["keyword_search"]("UNSEEN_CODE_ABCDEFG") == []
        assert any("E922" in doc.page_content for doc in scope["keyword_results"])
        a, b = scope["chunks"][:2]
        fused = scope["reciprocal_rank_fusion"]([a, b], [b])
        assert [doc.metadata["chunk_id"] for doc in fused] == [b.metadata["chunk_id"], a.metadata["chunk_id"]]
        for result in [scope["code_result"], scope["description_result"]]:
            ids = [doc.metadata["chunk_id"] for doc in result["documents"]]
            assert len(ids) == len(set(ids)) <= 3
            assert "NEX-1008_Nexa_CleanBot_S2.txt" in result["sources"]
        assert any("E922" in doc.page_content for doc in scope["code_result"]["documents"])
        assert "E922" in scope["model"].calls[0][0]
    else:
        assert len(scope["product_documents"]) == 20
        assert len(scope["variant_documents"]) == 26
        assert len(scope["summary_documents"]) == 10
        assert sum(doc.metadata["product_count"] for doc in scope["summary_documents"]) == 20
        detail, summary = scope["detail_result"], scope["summary_result"]
        assert detail["route"] == "DETAIL" and len(detail["documents"]) == 3
        assert any("humidity control" in doc.page_content and "HCL-101-P" in doc.page_content for doc in detail["documents"])
        assert summary["route"] == "SUMMARY" and len(summary["documents"]) == 10
        assert {doc.metadata["subcategory"] for doc in summary["documents"]} == {key[1] for key in scope["groups"]}
        whole_catalog = scope["ask_hierarchical_rag"]("Give an overview of all products in the catalog.")
        assert whole_catalog["route"] == "SUMMARY" and len(whole_catalog["documents"]) == 10
        assert all(doc.metadata["level"] == "summary" for doc in whole_catalog["documents"])


def main():
    entries = json.loads((ROOT / "part-three-lessons.json").read_text(encoding="utf-8"))
    for entry in entries:
        path = ROOT / "code/Part III Give the model something to read" / entry["filename"]
        book = nbformat.read(path, as_version=4)
        nbformat.validate(book)
        scope = {"__name__": "__main__"}
        model = OfflineChat(lesson=entry["local"])
        with contextlib.chdir(path.parent), contextlib.redirect_stdout(io.StringIO()), \
             patch.dict(os.environ, {"LANGSMITH_TRACING": "false", "LANGCHAIN_TRACING_V2": "false"}), \
             patch("dotenv.load_dotenv", return_value=False), \
             patch("langchain.chat_models.init_chat_model", return_value=model), \
             patch("langchain_openai.OpenAIEmbeddings", return_value=OfflineEmbeddings()), \
             patch("socket.create_connection", side_effect=AssertionError("Network access is disabled for this check")):
            for cell in book.cells:
                if cell.cell_type == "markdown":
                    assert all(not line.strip() or line.startswith("#") for line in cell.source.splitlines())
                else:
                    tree = ast.parse(cell.source)
                    assert not any(isinstance(node, ast.Try) for node in ast.walk(tree))
                    exec(compile(tree, f"{path.name}:{cell.id}", "exec"), scope)
            verify(entry["local"], scope)
        print(f"Part III lesson {entry['local']}: execution, retrieval and flow checks OK")
    print("All four notebooks passed offline. No provider API calls were made.")


if __name__ == "__main__":
    main()
