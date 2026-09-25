# Brag Plan: SearchOps

## What is this app?
SearchOps is an open-source retrieval and ranking engineering platform that replaces black-box RAG chatbots with an inspectable, multi-stage retrieval pipeline (BM25, Dense Cosine, Hybrid α-Fusion, and Candidate Reranking) backed by real Information Retrieval evaluation metrics (Recall@10, MRR, nDCG@10).

## The angle
"Stop treating search as a prompt." RAG chatbots hide retrieval failures behind hallucinations. SearchOps turns retrieval engineering into an inspectable, measurable science with stage-by-stage score decomposition and automated benchmarks.

## Hook (first 2-3 seconds)
"Generic RAG chatbots hide retrieval failures."
A glowing terminal query enters: `"show me lightweight laptops for coding under ₹80,000"`

## Key moments (the middle)
1. **Multi-Retriever Comparison**: Side-by-side candidate generation across BM25 Lexical, Dense Vector Cosine, and Hybrid α-Fusion.
2. **"Why this result ranked #1" Inspector**: Score decomposition visualizer breaking down BM25 (45%), Vector Cosine (55%), and Reranker metadata boosts.
3. **Reproducible IR Benchmark**: Side-by-side benchmark table revealing Recall@10 = 0.922 and nDCG@10 = 0.893 on MiniLM transformer embeddings.

## Outro / punchline
"Built for AI & Search Engineers. SearchOps — Ingest. Retrieve. Rank. Evaluate."
GitHub: `github.com/Aayush-pixel29/SearchOps`

## Tone
- Preset: `polished`
- Creative direction: Modern, high-energy technical launch showcase for AI/ML engineers and tech recruiters.
- Pacing: Confident, fast-in with generous visual holds on real UI, metrics, and score bars.

## Format: landscape — 1920x1080 @ 30fps
## Duration: 20.0 seconds

## Visual identity (from SearchOps)
- Background: `#09090b` (Zinc-950)
- Surface: `#18181b` (Zinc-900)
- Accent: `#22d3ee` (Cyan-400), `#818cf8` (Indigo-400), `#fbbf24` (Amber-400)
- Text: `#f4f4f5` (Zinc-100), `#a1a1aa` (Zinc-400)
- Font: Inter / JetBrains Mono

## Storyboard

### Scene 1 — The Hook (0.0s – 3.5s)
- **Visual**: Bold headline: "Stop building black-box RAG chatbots." Subtitle: "Search is an engineering discipline."
- **Motion**: Cyan glow pulse; typing animation: `"lightweight laptops for programming under ₹80,000"`.

### Scene 2 — Multi-Retriever Pipeline (3.5s – 8.0s)
- **Visual**: 4 competing engines pop in:
  - ⚡ **Keyword (BM25)** — Exact token IDF
  - 🧠 **Dense Cosine** — MiniLM 384d semantic vectors
  - ⚖️ **Hybrid Fusion** — $\alpha \cdot \text{Dense} + (1-\alpha) \cdot \text{BM25}$
  - 🎯 **Reranker** — Cross-Encoder & attribute boost
- **Motion**: Flow diagram connects into composite top-ranked hits.

### Scene 3 — The Inspector: "Why This Result Ranked #1" (8.0s – 13.5s)
- **Visual**: Real SearchOps UI view. `#1 Top Ranked Result: ASUS ZenBook 14 OLED (Score: 0.938)`.
- **Motion**: Animated score decomposition bars fill up:
  - BM25 Score: 0.812 (Blue)
  - Dense Cosine: 0.840 (Purple)
  - Hybrid Fusion: 0.829 (Cyan)
  - Reranker: 0.938 (Gold)

### Scene 4 — Empirical IR Evaluation (13.5s – 17.5s)
- **Visual**: Automated benchmark matrix:
  - MiniLM Recall@10: **0.922** (92.2%)
  - MiniLM nDCG@10: **0.893**
  - MRR: **1.000**
  - p50 Latency: **45.3 ms**
- **Motion**: Numbers count up to target values with green achievement indicators.

### Scene 5 — Outro & Open Source (17.5s – 20.0s)
- **Visual**: SearchOps logo + GitHub repository URL:
  `github.com/Aayush-pixel29/SearchOps`
- **Punchline**: "Retrieval Engineering Platform · 100% Open Source"
