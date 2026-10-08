# Part III · Lesson 5 — Choose a detail or the bigger picture

## What we are building

We are building a **catalog assistant that can answer a specific product question or compare several products**.

Until now, we used **k** to limit how many matching documents a search returns. For example, k=3 gives us up to three matches. That can be useful for a focused question, but those matches may leave out products we need for a comparison.

Imagine asking, “Compare all heaters.” Three matching passages might describe just one or two heaters. To compare all of them, the assistant needs information about every heater in the group. In our catalog, we will try the same kind of question: **“Compare all Climate Control products.”** We will also ask a specific question: **“Which AeroTherm X1 variant adds humidity control?”**

### The idea behind it

We prepare two views of the same catalog: **detailed records** for specific questions and **short summaries** for broader questions. The summaries let us include more products without sending every product's full instructions and specifications to the model.

The model reads the question and chooses which view to search. We are adding intelligence to the conditional graph design we already learned: the model chooses the route, and the graph follows the connections we define.

## The document we will search

We will use **Hierarchical_Product_Catalog.json**, a structured catalog containing **20 products and 26 variants**, organized into **10 category and subcategory groups**. It includes climate controls, security devices, office equipment, e-bikes, and home appliances.

The structure is **category → subcategory → product → variant**. For example: **Home Systems → Climate Control → AeroTherm X1 → Plus**. Each product has a description, specifications, setup and usage instructions, error information, and variants with their own prices and features.

Because these fields are already separated in the JSON file, we can turn them into product records, variant records, and group summaries directly. We keep the source filename and relevant product, variant, or group identifiers in each Document's **metadata**, so we can identify where a retrieved passage came from.

## Choose a detail or an overview

**Hierarchical retrieval** means choosing how much detail to read: a specific product's information for a focused question, or an overview of several products for a broad question. Here, we do that with two searchable indexes, saved as separate Chroma collections in the same database folder.

| Index | What it stores | What we retrieve |
|---|---|---|
| **DETAIL** | 20 full product Documents and 26 variant Documents. These include specifications, instructions, errors, and variant features. | Up to three matching Documents: **k=3**. Useful for “Which AeroTherm X1 variant adds humidity control?” |
| **SUMMARY** | 10 summaries, one per category and subcategory group. Each lists every product in that group with its name, ID, description, starting price, and number of variants. | All 10 summaries: **k=10** in this small example. Useful for “Compare all Climate Control products.” |

Both collections store **text, its embedding vector, and metadata**. The summary text is shorter, but still represents every product in the catalog. It does not include every specification or variant feature.

### How we build the two search paths

**DETAIL and SUMMARY are two retrieval paths.** We construct a collection and a retriever for each path. They share the same embedding model for searching and the same chat model for routing and answering.

For **DETAIL**, we turn each product and each variant into a separate Document, keeping their detailed fields. For **SUMMARY**, we group products by category and subcategory, then use Python to assemble a short overview of every product in each group. The chat model does not write these summaries.

We embed the Documents for each path and save them in their own Chroma collection. Then we create a retriever for each collection: the detail retriever requests three matches; the summary retriever requests all ten group summaries in this small catalog.

<!-- visual: catalog-indexes -->

**How does the application choose?**

1. The model reads the question and returns **DETAIL** for a specific product question or **SUMMARY** for a broad comparison or overview.
2. A conditional edge sends the question to the chosen retriever. The question is embedded and used to search that collection. The summary route requests every summary in this small catalog; similarity determines their order.
3. The answer node receives the original question and the retrieved **text**. For a Climate Control comparison, it uses the relevant products from the summaries. If a requested fact is missing, it should say so.

Our flow is **question → choose detail or summary → retrieve → answer**. Including every summary works for this small catalog; a larger one would need a way to select enough summaries without exceeding the model's context limit.

<div data-graph-preview="builder"></div>

## Build the catalog assistant

### Import the document and model helpers

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-01 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
```

**What happens here**

**Document** pairs a piece of text with metadata about its source.

**Chroma** is the vector database used in the supplied example. With persist_directory, it saves the indexed text, vectors, and source details to a local folder. We import separate helpers for embeddings and chat replies.

**Result:** The building blocks are available; importing them makes no provider request.

### Connect the two kinds of model

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-02 -->
```python
load_dotenv()
# Groq generates answers; OpenAI creates search embeddings.
model = init_chat_model(
    "openai/gpt-oss-120b", model_provider="groq", reasoning_effort="low",
)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

**What happens here**

Keep GROQ_API_KEY and OPENAI_API_KEY in the code project's .env file. The chat model writes answers. OpenAIEmbeddings turns text into vectors for searching; it does not write an answer. Creating these objects is setup. Indexing documents and searching later make embedding requests.

**Result:** We have a chat model and an embedding model, with different jobs.

### Read the structured catalog

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-03 -->
```python
import json
from pathlib import Path

catalog_path = Path("../doc/products2/Hierarchical_Product_Catalog.json")
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
products = catalog["products"]
print("Products:", len(products))
```

**What happens here**

The JSON already separates product fields and variant records. We do not need to guess this structure from PDF text. The supplied catalog contains twenty products in ten subcategory groups.

**Result:** The hierarchy is available as ordinary Python dictionaries and lists.

### Build one detailed document per product

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-04 -->
```python
product_documents = []
for product in products:
    text = "\n".join([
        f"Product: {product['product_name']} ({product['product_id']})",
        f"Subcategory: {product['subcategory']}", product["description"],
        "Specifications: " + json.dumps(product["specifications"]),
        "Setup: " + " ".join(product["quick_start"]),
        "Usage: " + " ".join(product["how_to_use"]),
        "Errors: " + json.dumps(product["error_codes"]),
        "Variants: " + json.dumps(product["variants"]),
    ])
    product_documents.append(Document(page_content=text, metadata={
        "source": catalog_path.name, "level": "product",
        "product_id": product["product_id"], "subcategory": product["subcategory"],
    }))
```

**What happens here**

Each product becomes a readable Document with its specifications, setup, usage, errors, and variants. The metadata preserves its level and identity. We include the variant data here so an exact product question can still see its options.

**Result:** We have twenty detailed product Documents.

### Give each variant its own searchable document

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-05 -->
```python
variant_documents = []
for product in products:
    for variant in product["variants"]:
        text = (
            f"Parent: {product['product_name']} ({product['product_id']})\n"
            f"Variant: {variant['variant_name']} ({variant['variant_id']})\n"
            f"Price: {variant['price_usd']}\n{variant['description']}"
        )
        variant_documents.append(Document(page_content=text, metadata={
            "source": catalog_path.name, "level": "variant",
            "variant_id": variant["variant_id"], "parent_product_id": product["product_id"],
            "subcategory": product["subcategory"],
        }))
```

**What happens here**

A variant can match a precise feature question independently of the rest of its product. Its parent name and ID keep it connected to the hierarchy. We preserve the supplied variant description rather than ask a model to invent one.

**Result:** We have twenty-six variant Documents, each linked to its parent product.

### Group products by their place in the hierarchy

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-06 -->
```python
groups = {}
for product in products:
    key = (product["category"], product["subcategory"])
    groups.setdefault(key, []).append(product)
```

**What happens here**

The category and subcategory pair identifies a group. setdefault creates a list the first time we encounter that group; append adds its product. This is ordinary Python grouping, not another model call.

**Result:** All twenty products are organized into ten subcategory groups.

### Create a complete summary for each group

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-07 -->
```python
summary_documents = []
for (category, subcategory), group in groups.items():
    lines = [f"Category: {category}", f"Subcategory: {subcategory}", f"Products: {len(group)}"]
    for product in group:
        lines.append(
            f"{product['product_name']} ({product['product_id']}): {product['description']} "
            f"Starting price: {product['starting_price_usd']}. Variants: {len(product['variants'])}."
        )
    summary_documents.append(Document(page_content="\n".join(lines), metadata={
        "source": catalog_path.name, "level": "summary", "category": category,
        "subcategory": subcategory, "product_count": len(group),
    }))
```

**What happens here**

Every product in the group contributes its name, ID, description, starting price, and variant count. These summaries are assembled from known fields; they are not LLM-generated summaries. Detailed error codes and individual variant features remain in the detail index.

**Result:** Ten summary Documents collectively represent the complete twenty-product catalog.

### Prepare stable IDs for the detail documents

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-08 -->
```python
detail_documents = product_documents + variant_documents
detail_ids = [
    f"product:{doc.metadata['product_id']}" for doc in product_documents
] + [
    f"variant:{doc.metadata['variant_id']}" for doc in variant_documents
]
```

**What happens here**

We combine the product and variant Documents into one detail collection. Each gets a stable Chroma ID based on its existing product or variant ID. The prefixes keep the two kinds of ID distinct.

**Result:** We have one ID for each detail Document, in the same order.

### Save the detail collection in Chroma

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-08-detail -->
```python
detail_store = Chroma.from_documents(
    documents=detail_documents,
    embedding=embeddings,
    ids=detail_ids,
    collection_name="detail_documents",
    persist_directory="./chroma_db",
)
```

**What happens here**

Chroma embeds the detail Documents and saves their text, vectors, and metadata in the detail_documents collection. Stable IDs update the same entries when we rerun this cell with the same catalog. The collection is saved to disk.

**Result:** The detail collection is available now and can be reopened after a restart.

### Save the summary collection in Chroma

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-08-summary -->
```python
summary_store = Chroma.from_documents(
    documents=summary_documents,
    embedding=embeddings,
    ids=[f"{doc.metadata['category']}:{doc.metadata['subcategory']}" for doc in summary_documents],
    collection_name="summary_documents",
    persist_directory="./chroma_db",
)
```

**What happens here**

The summaries go into a separate named collection in the same Chroma folder. Each summary uses its category and subcategory as a stable ID. Separating the collections lets us choose the information level before searching.

**Result:** The same database folder contains separate detail and summary collections.

### Choose how much text each route retrieves

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-08-retrievers -->
```python
detail_retriever = detail_store.as_retriever(search_kwargs={"k": 3})
# Include every summary for complete coverage of this small catalog.
summary_retriever = summary_store.as_retriever(search_kwargs={"k": len(summary_documents)})
```

**What happens here**

DETAIL returns up to three matching product or variant Documents. For SUMMARY, len(summary_documents) is ten, so the retriever returns all ten group summaries. Similarity determines their order. The graph will choose which retriever to use.

**Result:** Both routes return Documents, with a different level and amount of context.

### Define the allowed route and working state

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-09 -->
```python
from typing import Literal
from typing_extensions import TypedDict
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class RouteChoice(BaseModel):
    route: Literal["DETAIL", "SUMMARY"]

class CatalogState(TypedDict):
    question: str
    route: str
    documents: list[Document]
    answer: str
```

**What happens here**

RouteChoice reuses structured output from Part I. Literal limits the route to two labels.

**CatalogState** keeps four fields: the question, chosen route, retrieved evidence, and answer. The fields use replacement, and each node returns only its updates.

**Result:** The graph has a clear record, and the model's classification has a small validated shape.

### Ask the model to classify the question

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-10 -->
```python
route_model = model.with_structured_output(RouteChoice)

def classify_question(state: CatalogState) -> dict:
    prompt = (
        "Choose DETAIL for a specific product, variant, specification, error, or setup question. "
        "Choose SUMMARY for a comparison, overview, or list across products or categories.\n"
        "Question: " + state["question"]
    )
    choice = route_model.invoke(prompt)
    return {"route": choice.route}

def choose_route(state: CatalogState) -> str:
    return state["route"]
```

**What happens here**

The model reads our routing instructions and the question, then returns one route label. choose_route hands that stored label to the graph. The model can still choose the wrong route, so we keep the route in the result for inspection.

**Result:** The decision is separated from retrieval and answer generation.

### Retrieve at the selected level

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-11 -->
```python
def retrieve_detail(state: CatalogState) -> dict:
    return {"documents": detail_retriever.invoke(state["question"])}

def retrieve_summary(state: CatalogState) -> dict:
    return {"documents": summary_retriever.invoke(state["question"])}
```

**What happens here**

Both nodes return only documents. The detail route selects specific candidates; the summary route supplies every overview in this small dataset. Neither node writes an answer.

**Result:** The generation node receives Documents regardless of which route ran.

### Label context with its level and identity

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-12 -->
```python
def catalog_context(documents: list[Document]) -> str:
    passages = []
    for document in documents:
        meta = document.metadata
        label = meta.get("variant_id", meta.get("product_id", meta["subcategory"]))
        passages.append(f"[{label}; {meta['level']}; {meta['source']}]\n{document.page_content}")
    return "\n\n".join(passages)
```

**What happens here**

All Documents come from the same catalog filename, so the file alone would not identify a result well. We add the variant ID, product ID, or subcategory name and its level. This makes a cited detail distinguishable from a cited overview.

**Result:** The model sees readable text with inspectable source labels.

### Generate an answer using that context

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-13 -->
```python
def generate_catalog_answer(state: CatalogState) -> dict:
    instruction = (
        "Use only the context. If it lacks the needed detail, say you could not find enough information. "
        "Cite the bracketed source labels.\nContext:\n" + catalog_context(state["documents"])
    )
    answer = model.invoke([SystemMessage(instruction), HumanMessage(state["question"])]).text
    return {"answer": answer}
```

**What happens here**

The model receives the question and evidence at the selected level. It is asked to acknowledge missing detail instead of filling it from elsewhere. Retrieval coverage and correct answer generation are separate concerns; we can inspect both in the final state.

**Result:** The answer is returned while the route and source Documents remain available.

### Register the classification, retrieval, and answer nodes

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-14 -->
```python
builder = StateGraph(CatalogState)
builder.add_node("route", classify_question)
builder.add_node("detail", retrieve_detail)
builder.add_node("summary", retrieve_summary)
builder.add_node("generate", generate_catalog_answer)
```

**What happens here**

Each function has one visible responsibility. Two retrieval nodes allow the graph to select the information level explicitly.

**Result:** The graph is ready to connect.

### Connect the two retrieval routes

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-15 -->
```python
builder.add_edge(START, "route")
builder.add_conditional_edges(
    "route", choose_route, {"DETAIL": "detail", "SUMMARY": "summary"},
)
builder.add_edge("detail", "generate")
builder.add_edge("summary", "generate")
builder.add_edge("generate", END)
graph = builder.compile()
```

**What happens here**

Only the selected retrieval branch runs. Both branches lead to generation, so we have one shared answer function. There is no retry loop or hidden parent traversal in this example.

**Result:** A question follows route, one retrieval node, generation, and END.

### Run a question with fresh state

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-16 -->
```python
def ask_hierarchical_rag(question: str) -> CatalogState:
    return graph.invoke({
        "question": question, "route": "", "documents": [], "answer": "",
    })
```

**What happens here**

Each call starts with no route, evidence, or answer from a previous question. The returned state contains all four fields after the graph finishes.

**Result:** We can inspect the selected level alongside the answer.

### Ask for a specific variant feature

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-17 -->
```python
detail_result = ask_hierarchical_rag("Which AeroTherm X1 variant adds humidity control?")
print("Route:", detail_result["route"])
print("Answer:", detail_result["answer"])
for document in detail_result["documents"]:
    print(document.metadata)
```

**What happens here**

This should use DETAIL. The supplied AeroTherm Plus variant, HCL-101-P, adds humidity control. Check that the retrieved product or variant text actually contains that fact. Correct-looking wording without that evidence would not establish successful retrieval.

**Result:** We can inspect specific product and variant identities in the retrieved metadata.

### Ask for a view across products

<!-- snippet: code/Part III Give the model something to read/5-hierarchical-rag.ipynb#p3-4-step-18 -->
```python
summary_result = ask_hierarchical_rag("Compare all Climate Control products.")
print("Route:", summary_result["route"])
print("Summary documents:", len(summary_result["documents"]))
print("Answer:", summary_result["answer"])
```

**What happens here**

This should use SUMMARY. The supplied Climate Control group includes AeroTherm X1 and BreezeSense V2. The route includes all ten group summaries, so it also has coverage for a broader catalog question. The model should focus its comparison on the requested subcategory.

**Result:** We can see the broader retrieval level and confirm that every summary was included.

## Check your understanding

1. Why keep separate detail and summary indexes?
2. Why do we include every summary for a global question here?
3. What information is omitted from a summary?
4. Does a valid route label guarantee a correct classification?

## Where we go next

You now have four ways to assemble useful evidence. The remaining Part III lessons are still planned; evaluation and larger retrieval workflows can build on these examples.

Complete notebook: [5-hierarchical-rag.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/5-hierarchical-rag.ipynb)

Further reading: [LangChain Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma), [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
