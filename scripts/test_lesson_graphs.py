"""Topology and integration checks for graphs read from actual teaching code."""
import sys
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_topology import GraphReader, read_graphs
from lesson_graphs import CAPTIONS, add_graph_visuals, graph_svg
import ast

ROOT = Path(__file__).resolve().parents[1]


class TopologyTests(unittest.TestCase):
    def models(self, code):
        reader = GraphReader()
        for statement in ast.parse(code).body:
            reader.statement(statement, None, {})
        return [model for _, model in reader.completed]

    def test_explicit_join_and_distinct_parallel_exits(self):
        model = self.models('''
builder = StateGraph(State)
builder.add_node("left", work)
builder.add_node("right", work)
builder.add_node("finish", work)
builder.add_edge(START, "left")
builder.add_edge(START, "right")
builder.add_edge(["left", "right"], "finish")
builder.add_edge("finish", END)
builder.compile()
''')[0]
        self.assertEqual(model["joins"], [[["left", "right"], "finish"]])
        self.assertIn(["left", "finish", "wait for both"], model["edges"])
        self.assertIn(["right", "finish", "wait for both"], model["edges"])

    def test_literal_loops_branches_and_inline_compile(self):
        model = self.models('''
builder = StateGraph(State)
for name, function in [("search", search), ("done", done)]:
    builder.add_node(name, function)
builder.add_edge(START, "search")
builder.add_conditional_edges("search", choose, {"again": "search", "finish": "done"})
for final_node in ["done"]:
    builder.add_edge(final_node, END)
result = builder.compile(checkpointer=memory).invoke(input)
''')[0]
        self.assertEqual(model["nodes"], ["search", "done"])
        self.assertIn(["search", "search", "again"], model["edges"])
        self.assertIn(["done", "END", "next"], model["edges"])
        self.assertTrue(model["checkpoint"])

    def test_agent_tools_are_choices_not_a_fixed_chain(self):
        model = self.models('agent = create_agent(model=model, tools=[stock, price])')[0]
        self.assertEqual(model["kind"], "agent")
        self.assertIn(["model", "stock", "tool call"], model["edges"])
        self.assertIn(["price", "model", "tool result"], model["edges"])
        self.assertNotIn(["stock", "price", "next"], model["edges"])

    def test_every_published_construction_is_covered_and_rebuild_is_stable(self):
        counts = {"graph": 0, "agent": 0}
        keys = set()
        for lesson in range(1, 21):
            page = BeautifulSoup((ROOT / f"lesson-{lesson}.html").read_text(encoding="utf-8"), "html.parser")
            article = page.select_one("#lesson")
            originals = [node.get_text() for node in article.select(".code-explorer__source")]
            models = read_graphs(article)
            for _, model in models:
                counts[model["kind"]] += 1
                keys.add(f'{lesson}:{model["name"]}')
                known = {"START", "END", *model["nodes"]}
                self.assertTrue(all(source in known and target in known for source, target, _ in model["edges"]))
                svg = graph_svg(model, f"test-{lesson}", "Test graph")
                self.assertEqual(svg.count('class="graph-node'), len(known))
            add_graph_visuals(page, lesson)
            first = str(page)
            add_graph_visuals(page, lesson)
            self.assertEqual(first, str(page))
            self.assertEqual(originals, [node.get_text() for node in article.select(".code-explorer__source")])
            self.assertEqual(len(article.select("[data-lesson-graph]")), len(models) + (lesson == 9))
        self.assertEqual(counts, {"graph": 17, "agent": 3})
        self.assertEqual(keys, set(CAPTIONS))


if __name__ == "__main__":
    unittest.main()
