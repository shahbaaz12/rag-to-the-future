"""Read graph construction from teaching snippets without executing lesson code."""
import ast


def value(node, environment):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return environment.get(node.id, {"START": "START", "END": "END"}.get(node.id, node.id))
    if isinstance(node, (ast.List, ast.Tuple)):
        return [value(item, environment) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {value(key, environment): value(item, environment) for key, item in zip(node.keys, node.values)}
    raise ValueError(f"Unsupported graph argument: {ast.dump(node)}")


def graph_model(name, schema, kind="graph"):
    return {"name": name, "schema": schema, "kind": kind, "nodes": [], "edges": [], "joins": [], "checkpoint": False}


def add_connection(model, call, environment):
    args = [value(arg, environment) for arg in call.args]
    if call.func.attr == "add_node":
        model["nodes"].append(args[0])
    elif call.func.attr == "add_edge":
        sources = args[0] if isinstance(args[0], list) else [args[0]]
        if isinstance(args[0], list):
            model["joins"].append([sources, args[1]])
        model["edges"].extend([[source, args[1], "wait for both" if len(sources) > 1 else "next"] for source in sources])
    else:
        for label, target in args[2].items():
            model["edges"].append([args[0], target, label])


def agent_model(name, call):
    keywords = {item.arg: item.value for item in call.keywords}
    tools = value(keywords.get("tools", ast.List(elts=[])), {})
    model = graph_model(name, "Conversation state", "agent")
    model["nodes"] = ["model"] + tools
    model["edges"] = [["START", "model", "input"], ["model", "END", "final reply"]]
    for tool in tools:
        model["edges"] += [["model", tool, "tool call"], [tool, "model", "tool result"]]
    model["checkpoint"] = "checkpointer" in keywords
    return model


class GraphReader:
    def __init__(self):
        self.builders = {}
        self.completed = []

    def statement(self, statement, figure, environment):
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(statement, ast.For):
            graph_calls = [node for node in ast.walk(statement) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self.builders]
            if not graph_calls:
                return
            for item in value(statement.iter, environment):
                local = dict(environment)
                targets = statement.target.elts if isinstance(statement.target, ast.Tuple) else [statement.target]
                values = item if isinstance(statement.target, ast.Tuple) else [item]
                local.update({target.id: assigned for target, assigned in zip(targets, values)})
                for child in statement.body:
                    self.statement(child, figure, local)
            return
        if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call):
            self.assignment(statement, figure)
        for call in (node for node in ast.walk(statement) if isinstance(node, ast.Call)):
            self.method(call, figure, environment)

    def assignment(self, statement, figure):
        call = statement.value
        if not isinstance(call.func, ast.Name) or not isinstance(statement.targets[0], ast.Name):
            return
        name = statement.targets[0].id
        if call.func.id == "StateGraph":
            self.builders[name] = graph_model(name, value(call.args[0], {}))
        elif call.func.id == "create_agent":
            self.completed.append((figure, agent_model(name, call)))

    def method(self, call, figure, environment):
        if not isinstance(call.func, ast.Attribute) or not isinstance(call.func.value, ast.Name):
            return
        model = self.builders.get(call.func.value.id)
        if model is None:
            return
        if call.func.attr in ("add_node", "add_edge", "add_conditional_edges"):
            if call.func.attr == "add_node" and isinstance(call.args[1], ast.Call):
                # ToolNode's internals do not change the registered node name.
                model["nodes"].append(value(call.args[0], environment))
            else:
                add_connection(model, call, environment)
        elif call.func.attr == "compile":
            model["checkpoint"] = any(item.arg == "checkpointer" for item in call.keywords)
            self.completed.append((figure, model))


def read_graphs(article):
    reader = GraphReader()
    for figure in article.select("figure.snippet-card"):
        source = figure.select_one(".code-explorer__source").get_text()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue  # Non-Python snippets are not graph builders.
        for statement in tree.body:
            reader.statement(statement, figure, {})
    return reader.completed
