from __future__ import annotations

LAPTOPS = [
    ("laptop-acer-aspire-5", "Acer Aspire 5 14", 54990, 16, "Ryzen 5, 512GB SSD, lightweight 1.5kg programming laptop"),
    ("laptop-acer-swift-go", "Acer Swift Go 14", 72990, 16, "OLED display, Intel Core Ultra, thin aluminum chassis for coding"),
    ("laptop-lenovo-ideapad-slim", "Lenovo IdeaPad Slim 3", 47990, 8, "Budget Windows laptop, 15 inch, student programming"),
    ("laptop-lenovo-loq", "Lenovo LOQ 15", 79990, 16, "RTX graphics, 16GB RAM, under 80000 gaming plus coding machine"),
    ("laptop-hp-pavilion", "HP Pavilion 14", 62990, 16, "Silver 1.4kg laptop, 16GB RAM, good keyboard for Python development"),
    ("laptop-hp-victus", "HP Victus 15", 75990, 16, "Performance laptop under 80000 with dedicated GPU"),
    ("laptop-asus-vivobook-16", "ASUS Vivobook 16", 68990, 16, "Large screen coding laptop, 16GB RAM, lightweight for commuting"),
    ("laptop-asus-tuf", "ASUS TUF A15", 81990, 16, "Rugged laptop slightly over 80000, 16GB RAM, CUDA capable"),
    ("laptop-dell-inspiron", "Dell Inspiron 14", 59990, 8, "Office and light programming, 8GB RAM upgradeable"),
    ("laptop-dell-g15", "Dell G15", 84990, 16, "Gaming laptop above 80000, 16GB RAM, heavy chassis"),
    ("laptop-macbook-air-m1", "Refurbished MacBook Air M1", 74990, 8, "Lightweight Apple laptop for programming, fanless, 8GB unified memory"),
    ("laptop-macbook-air-m2", "MacBook Air M2", 99990, 16, "Premium lightweight laptop, 16GB, over 80000"),
    ("laptop-honor-magicbook", "Honor MagicBook X16", 51990, 16, "16GB RAM, 1.7kg, Windows coding laptop under 80000"),
    ("laptop-samsung-galaxy-book", "Samsung Galaxy Book4", 77990, 16, "AMOLED, light 1.4kg, 16GB RAM programming ultrabook"),
    ("laptop-msi-modern", "MSI Modern 14", 56990, 16, "Creator laptop, 16GB RAM, under 60000 for backend development"),
    ("laptop-lg-gram", "LG Gram 16", 119990, 16, "Ultra lightweight 1.2kg, expensive, 16GB RAM"),
    ("laptop-framework-13", "Framework Laptop 13", 94990, 16, "Repairable programming laptop, 16GB, modular ports"),
    ("laptop-thinkpad-e14", "Lenovo ThinkPad E14", 72990, 16, "Classic keyboard, 16GB RAM, best for long coding sessions under 80000"),
    ("laptop-yoga-slim", "Lenovo Yoga Slim 7", 78990, 16, "Metal ultrabook, 16GB, light 1.3kg, programming under 80000"),
    ("laptop-chromebook", "Acer Chromebook Plus", 32990, 8, "Not ideal for native programming, Linux limited, cheap"),
]

FRAMEWORKS = [
    ("fw-fastapi", "FastAPI", "Python async web framework with OpenAPI, Pydantic, high performance APIs"),
    ("fw-django", "Django", "Batteries-included Python web framework, ORM, admin, batteries for backend"),
    ("fw-flask", "Flask", "Minimal Python microframework, WSGI, extensions ecosystem"),
    ("fw-starlette", "Starlette", "ASGI toolkit underneath FastAPI, websockets and routing"),
    ("fw-litestar", "Litestar", "Typed Python ASGI framework alternative to FastAPI"),
    ("fw-express", "Express", "Node.js HTTP framework, middleware, JSON APIs"),
    ("fw-nestjs", "NestJS", "Opinionated TypeScript backend framework on Express or Fastify"),
    ("fw-spring", "Spring Boot", "Java backend framework, enterprise APIs, dependency injection"),
    ("fw-rails", "Ruby on Rails", "Convention over configuration web framework"),
    ("fw-laravel", "Laravel", "PHP backend framework with Eloquent ORM"),
    ("fw-nextjs", "Next.js", "React full-stack framework, App Router, server components"),
    ("fw-remix", "Remix", "React web framework focused on nested routing and forms"),
    ("fw-sveltekit", "SvelteKit", "Svelte application framework"),
    ("fw-axum", "Axum", "Rust async web framework on Tokio and Tower"),
    ("fw-actix", "Actix Web", "High performance Rust HTTP framework"),
]

SEARCH_DOCS = [
    ("ir-bm25", "BM25 ranking", "Okapi BM25 is a probabilistic keyword ranking function using term frequency and IDF"),
    ("ir-tfidf", "TF-IDF", "Term frequency inverse document frequency classic vector space retrieval"),
    ("ir-dense", "Dense retrieval", "Bi-encoder embeddings map queries and documents into a vector space for cosine search"),
    ("ir-hybrid", "Hybrid search", "Fuse BM25 keyword scores with dense vector scores using alpha linear combination or RRF"),
    ("ir-rerank", "Cross-encoder reranking", "A cross-encoder scores query-document pairs jointly and reranks a candidate list"),
    ("ir-ndcg", "nDCG metric", "Normalized discounted cumulative gain evaluates ranking quality with graded relevance"),
    ("ir-mrr", "Mean Reciprocal Rank", "MRR is the average of 1/rank of the first relevant document"),
    ("ir-recall", "Recall at K", "Recall@K is the fraction of relevant documents retrieved in the top K"),
    ("ir-ann", "Approximate nearest neighbors", "HNSW and IVF indexes speed up vector search in pgvector and FAISS"),
    ("ir-chunking", "Document chunking", "Split long documents with overlap so embeddings stay semantically coherent"),
    ("ir-query-parse", "Query understanding", "Extract filters like price and RAM from natural language before retrieval"),
    ("ir-eval", "IR evaluation", "Offline evaluation needs labeled queries, relevant document ids, and ranking metrics"),
    ("ir-rag-limits", "Why RAG chat is not search", "A chatbot hides ranking failures. Search engineering inspects BM25 vs dense vs hybrid"),
    ("ir-colbert", "ColBERT", "Late interaction retrieval that keeps token-level vectors"),
    ("ir-splade", "SPLADE", "Learned sparse retrieval combining neural expansion with inverted indexes"),
]

INFRA = [
    ("db-postgres", "PostgreSQL", "Relational database, JSONB, full text search, pgvector extension for embeddings"),
    ("db-pgvector", "pgvector", "Postgres extension storing vectors and cosine/L2 distance operators"),
    ("db-redis", "Redis", "In-memory cache and data structure store, used for search result caching"),
    ("db-sqlite", "SQLite", "Embedded SQL database useful for tests and local fallback"),
    ("db-opensearch", "OpenSearch", "Distributed search engine with BM25 and kNN"),
    ("db-elasticsearch", "Elasticsearch", "Inverted index search platform, analyzers, aggregations"),
    ("db-qdrant", "Qdrant", "Vector database with payload filters"),
    ("db-milvus", "Milvus", "Scale-out vector database"),
    ("obs-otel", "OpenTelemetry", "Traces and metrics standard for observing search latency spans"),
    ("obs-prometheus", "Prometheus", "Metrics collection, histograms for p50 and p95 latency"),
]


def build_catalog() -> list[dict]:
    docs: list[dict] = []
    for doc_id, title, price, ram, desc in LAPTOPS:
        docs.append(
            {
                "id": doc_id,
                "title": title,
                "content": f"{title}. {desc}. Price INR {price}. RAM {ram}GB. Category laptop.",
                "source": "demo-catalog",
                "metadata": {
                    "category": "laptop",
                    "price": price,
                    "ram_gb": ram,
                    "language": "en",
                    "tags": ["laptop", "hardware", "programming"],
                    "popularity": max(5, 100 - price // 1500),
                },
            }
        )
    for doc_id, title, desc in FRAMEWORKS:
        docs.append(
            {
                "id": doc_id,
                "title": title,
                "content": f"{title} is a backend or full-stack framework. {desc}",
                "source": "demo-catalog",
                "metadata": {
                    "category": "framework",
                    "language": "en",
                    "tags": ["software", "backend"],
                    "popularity": 70,
                },
            }
        )
    for doc_id, title, desc in SEARCH_DOCS:
        docs.append(
            {
                "id": doc_id,
                "title": title,
                "content": desc,
                "source": "demo-catalog",
                "metadata": {
                    "category": "search",
                    "language": "en",
                    "tags": ["information-retrieval", "ml"],
                    "popularity": 60,
                },
            }
        )
    for doc_id, title, desc in INFRA:
        docs.append(
            {
                "id": doc_id,
                "title": title,
                "content": desc,
                "source": "demo-catalog",
                "metadata": {
                    "category": "database",
                    "language": "en",
                    "tags": ["infra", "data"],
                    "popularity": 55,
                },
            }
        )
    extra_langs = [
        ("lang-python", "Python", "Python is a language for backend APIs, data, and ML tooling including FastAPI"),
        ("lang-typescript", "TypeScript", "Typed JavaScript used in Next.js dashboards and NestJS backends"),
        ("lang-rust", "Rust", "Systems language with Axum and Actix web frameworks"),
        ("lang-go", "Go", "Language for high concurrency backend services"),
        ("sec-jwt", "JWT authentication", "JSON Web Tokens bind a user identity to a tenant_id for API authorization"),
        ("sec-tenancy", "Multi-tenant search", "Every query must filter documents by tenant_id to prevent leakage"),
        ("ml-embeddings", "Text embeddings", "Dense vectors from hashed n-grams or transformer models enable semantic search"),
        ("ml-cosine", "Cosine similarity", "Cosine of two L2-normalized vectors is a standard dense retrieval score"),
        ("prod-cache", "Search caching", "Redis stores query+filter+top_k keys so repeated searches skip retrieval"),
        ("prod-fusion", "Score fusion", "Normalize BM25 and cosine then mix with configurable alpha"),
    ]
    for doc_id, title, desc in extra_langs:
        docs.append(
            {
                "id": doc_id,
                "title": title,
                "content": desc,
                "source": "demo-catalog",
                "metadata": {
                    "category": "knowledge",
                    "language": "en",
                    "tags": ["engineering"],
                    "popularity": 40,
                },
            }
        )
    return docs


EVAL_CASES = [
    {
        "id": "case-python-backend",
        "query": "best python backend framework",
        "relevant_documents": ["fw-fastapi", "fw-django", "fw-flask", "fw-litestar"],
        "relevance_labels": {"fw-fastapi": 3, "fw-django": 3, "fw-flask": 2, "fw-litestar": 2, "fw-starlette": 1},
    },
    {
        "id": "case-laptops",
        "query": "lightweight laptops for programming under 80000 with 16GB RAM",
        "relevant_documents": [
            "laptop-acer-swift-go",
            "laptop-hp-pavilion",
            "laptop-asus-vivobook-16",
            "laptop-thinkpad-e14",
            "laptop-yoga-slim",
            "laptop-samsung-galaxy-book",
            "laptop-honor-magicbook",
            "laptop-msi-modern",
        ],
        "relevance_labels": {
            "laptop-thinkpad-e14": 3,
            "laptop-yoga-slim": 3,
            "laptop-acer-swift-go": 3,
            "laptop-samsung-galaxy-book": 3,
            "laptop-asus-vivobook-16": 2,
            "laptop-hp-pavilion": 2,
            "laptop-honor-magicbook": 2,
            "laptop-msi-modern": 2,
            "laptop-lenovo-loq": 1,
        },
    },
    {
        "id": "case-hybrid",
        "query": "hybrid search bm25 dense fusion",
        "relevant_documents": ["ir-hybrid", "ir-bm25", "ir-dense", "prod-fusion"],
        "relevance_labels": {"ir-hybrid": 3, "prod-fusion": 3, "ir-bm25": 2, "ir-dense": 2, "ir-rerank": 1},
    },
    {
        "id": "case-metrics",
        "query": "how to evaluate ranking with ndcg and mrr",
        "relevant_documents": ["ir-ndcg", "ir-mrr", "ir-recall", "ir-eval"],
        "relevance_labels": {"ir-ndcg": 3, "ir-mrr": 3, "ir-eval": 2, "ir-recall": 2},
    },
    {
        "id": "case-vector-db",
        "query": "postgres pgvector embeddings cosine search",
        "relevant_documents": ["db-postgres", "db-pgvector", "ir-dense", "ml-embeddings"],
        "relevance_labels": {"db-pgvector": 3, "db-postgres": 3, "ir-dense": 2, "ml-embeddings": 2, "ml-cosine": 1},
    },
    {
        "id": "case-cache",
        "query": "redis cache repeated search queries",
        "relevant_documents": ["db-redis", "prod-cache"],
        "relevance_labels": {"db-redis": 3, "prod-cache": 3},
    },
    {
        "id": "case-rerank",
        "query": "cross encoder reranker for search results",
        "relevant_documents": ["ir-rerank", "ir-hybrid"],
        "relevance_labels": {"ir-rerank": 3, "ir-hybrid": 1, "ir-colbert": 1},
    },
    {
        "id": "case-tenancy",
        "query": "tenant isolation for search api",
        "relevant_documents": ["sec-tenancy", "sec-jwt"],
        "relevance_labels": {"sec-tenancy": 3, "sec-jwt": 2},
    },
]
