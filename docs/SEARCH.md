# Search & Ranking Mechanics

SearchOps implements a multi-stage retrieval and ranking pipeline designed to combine lexical precision with semantic density and candidate reranking.

---

## 1. Retrieval Algorithms

### A. Lexical Keyword Retrieval (BM25)
Implemented in [`searchops/retrieval/keyword.py`](file:///d:/New%20folder%20(8)/searchops/apps/api/searchops/retrieval/keyword.py).
SearchOps uses the Robertson-Spärck Jones BM25 scoring algorithm with standard parameterization ($k_1 = 1.5, b = 0.75$):

$$\text{IDF}(q_i) = \ln\left( \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1 \right)$$

$$\text{BM25}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left( 1 - b + b \cdot \frac{|D|}{\text{avgdl}} \right)}$$

- **Tokenization**: Lowercase normalization, alphanumeric regex extraction, and stopword preservation.
- **Corpus Weighting**: Titles are weighted and concatenated with chunk body text.

---

### B. Dense Vector Retrieval (Cosine Similarity)
Implemented in [`searchops/retrieval/dense.py`](file:///d:/New%20folder%20(8)/searchops/apps/api/searchops/retrieval/dense.py) and [`searchops/providers/embeddings.py`](file:///d:/New%20folder%20(8)/searchops/apps/api/searchops/providers/embeddings.py).

Query and document chunk embeddings are normalized vectors $\mathbf{u}, \mathbf{v} \in \mathbb{R}^d$. The dense retrieval score is computed via Cosine Similarity:

$$\text{Cosine}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

Supported embedding providers:
1. **`hashed`** *(Default)*: Fast, deterministic 384-dimensional signed hashed n-grams. Zero network dependencies.
2. **`huggingface`**: Local transformer inference using `sentence-transformers/all-MiniLM-L6-v2` with mean pooling and L2 normalization.
3. **`openai`**: `text-embedding-3-small` via OpenAI Embeddings API.
4. **`gemini`**: `text-embedding-004` via Google GenAI REST API.

---

### C. Linear Hybrid Fusion ($\alpha$-Blending)
Implemented in [`searchops/ranking/fusion.py`](file:///d:/New%20folder%20(8)/searchops/apps/api/searchops/ranking/fusion.py).

1. Retrieve candidate lists from both BM25 and Dense retrievers.
2. Form the union of retrieved chunks by `chunk_id`.
3. Compute min-max normalization independently across candidates for the current query:

$$\hat{s}_{\text{dense}} = \frac{s_{\text{dense}} - \min(S_{\text{dense}})}{\max(S_{\text{dense}}) - \min(S_{\text{dense}}) + \epsilon}$$

$$\hat{s}_{\text{BM25}} = \frac{s_{\text{BM25}} - \min(S_{\text{BM25}})}{\max(S_{\text{BM25}}) - \min(S_{\text{BM25}}) + \epsilon}$$

4. Compute the convex linear combination:

$$\text{Score}_{\text{hybrid}} = \alpha \cdot \hat{s}_{\text{dense}} + (1 - \alpha) \cdot \hat{s}_{\text{BM25}}$$

- Default parameter: $\alpha = 0.6$ (configurable per request or globally via `HYBRID_ALPHA`).

---

### D. Multi-Factor Candidate Reranking
Implemented in [`searchops/ranking/rerank.py`](file:///d:/New%20folder%20(8)/searchops/apps/api/searchops/ranking/rerank.py).

The top $K$ hybrid candidates are reranked using a multi-factor scoring function or cross-encoder:

$$\text{Score}_{\text{rerank}} = 0.70 \cdot \text{Score}_{\text{hybrid}} + 0.25 \cdot \text{Overlap}(Q, D) + \text{Boost}_{\text{title}} + \text{Boost}_{\text{metadata}}$$

- **`HeuristicReranker`**: Computes exact term overlap ratio, adds a $+0.08$ boost for query terms in document titles, and $+0.05$ for matching target category attributes.
- **`CrossEncoderReranker`**: Neural cross-attention reranking using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Fault-Tolerant Fallback**: If an error occurs during reranking (e.g. out of memory or missing weights), the system logs the event and falls back to hybrid ranking without failing the user request.

---

## 2. Metadata Filtering & Query Understanding

Filters are parsed from the query or supplied via query parameters:
- `category`: Exact match or containment.
- `price_min` / `price_max`: Numerical range filtering on product catalogs.
- `ram_gb`: Exact hardware attribute filtering.
- `language`, `source`, `tags`: Faceted taxonomy filtering.
- `date_from` / `date_to`: Temporal bounding.

All filters are executed against tenant-isolated records in SQL storage before candidate scoring.
