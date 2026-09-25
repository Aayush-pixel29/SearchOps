# Information Retrieval Evaluation & Benchmarking

SearchOps treats search as an empirical engineering discipline. The evaluation subsystem allows teams to measure ranking quality systematically across labeled evaluation queries using standard Information Retrieval (IR) metrics.

---

## 1. Metrics & Mathematical Definitions

Implemented in [`searchops/evaluation/metrics.py`](file:///d:/New%20folder%20(8)/searchops/apps/api/searchops/evaluation/metrics.py).

### A. Recall@K
The proportion of ground-truth relevant documents retrieved in the top-$K$ unique ranked results:

$$\text{Recall}@K = \frac{|\mathcal{R} \cap \mathcal{D}_{1..K}|}{|\mathcal{R}|}$$

Where $\mathcal{R}$ is the set of relevant document IDs and $\mathcal{D}_{1..K}$ is the ranked list of retrieved document IDs up to position $K$.

---

### B. Mean Reciprocal Rank (MRR)
Measures where the first relevant document appears in the ranked list:

$$\text{MRR} = \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\text{rank}_q}$$

Where $\text{rank}_q$ is the position of the first relevant document for query $q$ (or $0$ if no relevant document was retrieved).

---

### C. Normalized Discounted Cumulative Gain (nDCG@K)
Evaluates graded relevance with position discounts:

$$\text{DCG}@K = \sum_{i=1}^{K} \frac{2^{r_i} - 1}{\log_2(i + 1)}$$

$$\text{nDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$

Where $r_i \in \{0, 1, 2, 3\}$ is the graded relevance score of the document at rank $i$, and $\text{IDCG}@K$ is the ideal DCG obtained by sorting all relevance labels in descending order.

---

## 2. Benchmark Comparison (Measured Data)

Evaluated across the 8 labeled evaluation cases in `evals/demo_cases.json`:

### MiniLM Transformer Embeddings (`all-MiniLM-L6-v2`)
*Command: `python -m searchops.cli eval --provider huggingface --reseed`*

```
Method                 Recall@5  Recall@10      MRR    nDCG@10      p50      p95
--------------------------------------------------------------------------------
BM25                      0.766      0.859    1.000      0.870    18.1ms    25.7ms
Dense                     0.734      0.812    0.938      0.823    31.1ms    32.7ms
Hybrid                    0.734      0.859    1.000      0.876    44.8ms    79.8ms
Hybrid + Reranker         0.797      0.922    1.000      0.893    45.3ms    66.5ms
```

### Deterministic Hashed Embeddings (Baseline)
*Command: `python -m searchops.cli eval --provider hashed --reseed`*

```
Method                 Recall@5  Recall@10      MRR    nDCG@10      p50      p95
--------------------------------------------------------------------------------
BM25                      0.766      0.859    1.000      0.870    10.2ms    18.1ms
Dense                     0.531      0.703    0.581      0.537    13.5ms    17.2ms
Hybrid                    0.641      0.766    0.812      0.705    20.1ms    29.3ms
Hybrid + Reranker         0.672      0.781    0.938      0.792    18.5ms    19.2ms
```

---

## 3. Reproducing the Benchmark

To run benchmarks via the CLI:
```bash
cd apps/api

# Run with local sentence-transformers (MiniLM):
python -m searchops.cli eval --provider huggingface --reseed

# Run with deterministic hashed embeddings:
python -m searchops.cli eval --provider hashed --reseed
```

To run benchmarks via the Web Dashboard:
1. Open [http://localhost:3000/evaluation](http://localhost:3000/evaluation).
2. Click **Run benchmark**.
3. Inspect live Recall, MRR, nDCG, and p50/p95 latency bars across all 4 retrieval strategies.
