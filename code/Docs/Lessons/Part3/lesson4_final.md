# Part III · Lesson 4 — Choose a detail or the bigger picture

## A note from me

“Which AeroTherm variant adds humidity control?” needs a small detail. “Compare all Climate Control products” needs a broader view. Searching a few tiny fragments in the same way for both questions can hide the information we need.

Our supplied catalog already has a structure: **category → subcategory → product → variant**. Let’s use that structure instead of flattening every question into the same search.

## What we are building

We build two indexes. The detail index contains product and variant Documents. The summary index contains one complete overview per subcategory. The model classifies the question as DETAIL or SUMMARY, the graph retrieves at that level, and the model writes the answer.

This is a small hierarchical retrieval example. It is not GraphRAG over extracted entities and relationships, and it does not traverse every level of a tree. We are choosing between two useful information levels.

## What does global mean here?

A top-two search can miss most of a catalog. For this small dataset, our SUMMARY route includes **all** subcategory summaries. That gives a whole-catalog question coverage of all products represented in those summaries. Specific comparisons can use the relevant entries from that context.

Summaries still omit some details. If a question needs an exact specification, variant feature, or troubleshooting instruction, route it to DETAIL. A larger catalog would need a more deliberate way to gather and combine summaries; putting everything into one prompt will eventually become too large.

Run from the notebook directory. Live runs use GROQ_API_KEY and OPENAI_API_KEY. The product names, prices, and specifications are the supplied learning dataset, not current shopping advice.

### Import the document and model helpers

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-01 -->
```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
```

**What happens here**

Document pairs a piece of text with metadata about its source. InMemoryVectorStore keeps documents and their vectors in this Python process. We import separate helpers for embeddings and chat replies.

**Result:** The building blocks are available; importing them makes no provider request.

### Connect the two kinds of model

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-02 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-03 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-04 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-05 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-06 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-07 -->
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

### Build the two indexes and their retrievers

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-08 -->
```python
detail_documents = product_documents + variant_documents
detail_store = InMemoryVectorStore.from_documents(detail_documents, embeddings)
summary_store = InMemoryVectorStore.from_documents(summary_documents, embeddings)
detail_retriever = detail_store.as_retriever(search_kwargs={"k": 3})
# Include every summary for complete coverage of this small catalog.
summary_retriever = summary_store.as_retriever(search_kwargs={"k": len(summary_documents)})
```

**What happens here**

DETAIL searches up to three product or variant Documents. SUMMARY retrieves every subcategory summary; similarity determines their order, but the result includes the whole small catalog. This changes the reference's top-two summary search so a global answer does not silently omit groups.

**Result:** The two routes return the same Document type, while supplying different levels and amounts of context.

### Define the allowed route and working state

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-09 -->
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

RouteChoice reuses structured output from Part I. Literal limits the route to two labels. CatalogState keeps four fields: the question, chosen route, retrieved evidence, and answer. The fields use replacement, and each node returns only its updates.

**Result:** The graph has a clear record, and the model's classification has a small validated shape.

### Ask the model to classify the question

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-10 -->
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

Here the model makes the classification, unlike Lesson 1's keyword rule. The structured result gives us one route label. choose_route simply hands that stored label to the graph. A valid label can still be the wrong classification, so we return the route for inspection.

**Result:** The decision is separated from retrieval and answer generation.

### Retrieve at the selected level

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-11 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-12 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-13 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-14 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-15 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-16 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-17 -->
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

<!-- snippet: code/Part III Give the model something to read/4-hierarchical-rag.ipynb#p3-4-step-18 -->
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

Complete notebook: [4-hierarchical-rag.ipynb](../../../Part%20III%20Give%20the%20model%20something%20to%20read/4-hierarchical-rag.ipynb)

Further reading: [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) and [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings).
