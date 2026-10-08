"""Execute Part III with offline chat/embedding fixtures and real retrieval code.

Run from code/: uv run python ../scripts/validate_part_three.py
This checks pipeline behaviour, not hosted-model or semantic-embedding quality.
"""
import ast
import contextlib
import hashlib
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import nbformat
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import Field

ROOT = Path(__file__).resolve().parents[1]


class OfflineEmbeddings(Embeddings):
    """Stable lexical vectors for exercising the real vector-store implementation."""
    def __init__(self):
        self.document_calls = 0

    def embed_documents(self, texts):
        self.document_calls += 1
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
        length = math.sqrt(sum(value * value for value in vector))
        return [value / length for value in vector]


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
    if lesson == 0:
        assert len(scope['reader'].pages) == 11
        assert len(scope['chunks']) > len(scope['documents'])
        assert len(scope['stored_vector']) == 256  # Offline fixture dimensions.
        assert scope['saved_record']['ids'] == scope['chunk_ids'][:1]
        for name, page in [('grasshopper_matches', 4), ('lion_matches', 5), ('crow_matches', 8)]:
            matches = scope[name]
            assert len(matches) == 3
            assert any(doc.metadata['page'] == page for doc, _ in matches)
            distances = [distance for _, distance in matches]
            assert distances == sorted(distances)
            assert all(-1e-5 <= distance <= 2.00001 for distance in distances)
        assert scope['reopened_matches']
        # Check the reported distance against the cosine calculation on actual saved vectors.
        embeddings = scope['embeddings']
        query = embeddings.embed_query('a mouse helping a lion')
        doc, distance = scope['vector_store'].similarity_search_with_score('a mouse helping a lion', k=1)[0]
        vector = scope['vector_store'].get(ids=[doc.id], include=['embeddings'])['embeddings'][0]
        expected = 1 - sum(a * b for a, b in zip(query, vector))
        assert abs(distance - expected) < 1e-5
        calls = embeddings.document_calls
        guard_cell = next(cell for cell in scope['notebook_cells'] if cell.id == 'p3-pdf-step-07')
        exec(guard_cell.source, scope)
        assert embeddings.document_calls == calls, 'Repeated setup must reuse the indexed PDF'
    elif lesson == 1:
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


def check_saved_collections(lesson, scope, embeddings, database_root):
    if lesson == 1:
        return []
    if lesson == 0:
        groups = [(scope['vector_store'], 'classic_fables_cosine', scope['chunks'], scope['chunk_ids'])]
    elif lesson in (2, 3):
        groups = [(scope["vector_store"], "fables" if lesson == 2 else "hybrid", scope["chunks"],
                   [doc.metadata["chunk_id"] for doc in scope["chunks"]])]
    else:
        groups = [
            (scope["detail_store"], "detail_documents", scope["detail_documents"], scope["detail_ids"]),
            (scope["summary_store"], "summary_documents", scope["summary_documents"],
             [f"{doc.metadata['category']}:{doc.metadata['subcategory']}" for doc in scope["summary_documents"]]),
        ]
    manifest = []
    for store, collection, documents, ids in groups:
        assert sorted(store.get()["ids"]) == sorted(ids)
        # Repeat indexing through the real Chroma API: stable IDs must not duplicate entries.
        repeated = Chroma.from_documents(
            documents=documents, embedding=embeddings, ids=ids, collection_name=collection,
            persist_directory=str(database_root / "chroma_db"),
            client_settings=Settings(anonymized_telemetry=False),
        )
        assert sorted(repeated.get()["ids"]) == sorted(ids)
        manifest.append({"collection": collection, "ids": sorted(ids), "first_id": ids[0],
                         "text": documents[0].page_content, "metadata": documents[0].metadata})
    return manifest


def reopen_saved_collections(database_root):
    manifest = json.loads((database_root / "manifest.json").read_text(encoding="utf-8"))
    embeddings = OfflineEmbeddings()
    with patch("socket.create_connection", side_effect=AssertionError("Network access is disabled for this check")):
        for entry in manifest:
            store = Chroma(
                collection_name=entry["collection"], embedding_function=embeddings,
                persist_directory=str(database_root / "chroma_db"),
                client_settings=Settings(anonymized_telemetry=False),
            )
            assert sorted(store.get()["ids"]) == entry["ids"]
            saved = store.get(ids=[entry["first_id"]])
            assert saved["documents"] == [entry["text"]]
            assert saved["metadatas"] == [entry["metadata"]]
            hits = store.similarity_search(entry["text"], k=2)
            assert hits and all(hit.id in entry["ids"] for hit in hits)
            assert embeddings.document_calls == 0, "Reopening must not re-embed documents"
            print(f"Chroma {entry['collection']}: reopened in a new process; saved text, metadata and search OK")


def main(database_root):
    class IsolatedChroma(Chroma):
        """Use real disk storage while keeping validation out of the lesson's database."""
        def __init__(self, *args, **kwargs):
            kwargs["persist_directory"] = str(database_root / "chroma_db")
            kwargs["client_settings"] = Settings(anonymized_telemetry=False)
            super().__init__(*args, **kwargs)

    entries = json.loads((ROOT / "part-three-lessons.json").read_text(encoding="utf-8"))
    manifest = []
    for entry in entries:
        path = ROOT / "code/Part III Give the model something to read" / entry["filename"]
        book = nbformat.read(path, as_version=4)
        nbformat.validate(book)
        fixture_lesson = {'first_rag': 1, 'pdf_retrieval': 0, 'conversational': 2, 'hybrid': 3, 'hierarchical': 4}[entry['kind']]
        scope = {"__name__": "__main__", 'notebook_cells': book.cells}
        model = OfflineChat(lesson=fixture_lesson)
        embeddings = OfflineEmbeddings()
        with contextlib.chdir(path.parent), contextlib.redirect_stdout(io.StringIO()), \
             patch.dict(os.environ, {"LANGSMITH_TRACING": "false", "LANGCHAIN_TRACING_V2": "false", "ANONYMIZED_TELEMETRY": "false"}), \
             patch("dotenv.load_dotenv", return_value=False), \
             patch("langchain.chat_models.init_chat_model", return_value=model), \
             patch("langchain_openai.OpenAIEmbeddings", return_value=embeddings), \
             patch("langchain_chroma.Chroma", IsolatedChroma), \
             patch("socket.create_connection", side_effect=AssertionError("Network access is disabled for this check")):
            for cell in book.cells:
                if cell.cell_type == "markdown":
                    assert all(not line.strip() or line.startswith("#") for line in cell.source.splitlines())
                else:
                    tree = ast.parse(cell.source)
                    assert not any(isinstance(node, ast.Try) for node in ast.walk(tree))
                    exec(compile(tree, f"{path.name}:{cell.id}", "exec"), scope)
            verify(fixture_lesson, scope)
            manifest.extend(check_saved_collections(fixture_lesson, scope, embeddings, database_root))
        print(f"Part III lesson {entry['local']}: execution, retrieval and flow checks OK")
    (database_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        database_root = Path(sys.argv[1])
        if len(sys.argv) > 2 and sys.argv[2] == "--reopen":
            reopen_saved_collections(database_root)
        else:
            main(database_root)
    else:
        # Separate processes release Chroma's Windows file handles before cleanup.
        with tempfile.TemporaryDirectory(prefix="airag-chroma-check-") as database_root:
            subprocess.run([sys.executable, __file__, database_root], check=True)
            subprocess.run([sys.executable, __file__, database_root, "--reopen"], check=True)
        print("All five notebooks and Chroma persistence checks passed offline. No provider API calls were made.")
