"use client";

import { useState } from "react";
import { useToken } from "@/lib/auth";
import { API_URL, SearchHit } from "@/lib/api";

const METHODS = ["keyword", "dense", "hybrid", "hybrid_rerank"];

export default function SearchPage() {
  const { token, error } = useToken();
  const [q, setQ] = useState("lightweight laptops for programming under ₹80,000");
  const [method, setMethod] = useState("hybrid_rerank");
  const [data, setData] = useState<any>(null);
  const [selected, setSelected] = useState<SearchHit | null>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    if (!token) return;
    setBusy(true);
    setSelected(null);
    const res = await fetch(
      `${API_URL}/search?q=${encodeURIComponent(q)}&retrieval_method=${method}&top_k=10`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    const json = await res.json();
    setData(json);
    setBusy(false);
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-medium">Search playground</h1>
        <p className="text-zinc-400 text-sm mt-1">
          Inspect keyword, dense, hybrid, and reranked retrieval. Scores are real, not decorative.
        </p>
      </header>
      {error && <p className="text-red-400 text-sm">{error} — start the API on :8000</p>}
      <div className="flex gap-3">
        <input
          className="flex-1 bg-zinc-900 border border-zinc-700 rounded px-3 py-2 font-mono text-sm"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <select
          className="bg-zinc-900 border border-zinc-700 rounded px-2"
          value={method}
          onChange={(e) => setMethod(e.target.value)}
        >
          {METHODS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <button
          onClick={run}
          disabled={!token || busy}
          className="bg-cyan-500 text-zinc-950 font-medium px-4 rounded disabled:opacity-40"
        >
          {busy ? "Running" : "Search"}
        </button>
      </div>
      {data && (
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <div className="text-xs font-mono text-zinc-500">
              method={data.retrieval_method} cache={String(data.cache_hit)} alpha={data.alpha}
            </div>
            {data.results?.map((hit: SearchHit) => (
              <button
                key={hit.chunk_id}
                onClick={() => setSelected(hit)}
                className="w-full text-left border border-zinc-800 rounded p-3 hover:border-cyan-700"
              >
                <div className="flex justify-between text-sm">
                  <span className="font-medium">
                    #{hit.rank} {hit.title}
                  </span>
                  <span className="font-mono text-cyan-400">{hit.score.toFixed(3)}</span>
                </div>
                <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{hit.content}</p>
              </button>
            ))}
          </div>
          <Inspector hit={selected} understanding={data.query_understanding} trace={data.trace} />
        </div>
      )}
    </div>
  );
}

function Inspector({ hit, understanding, trace }: { hit: SearchHit | null; understanding: any; trace: any }) {
  if (!hit) {
    return (
      <div className="border border-zinc-800 bg-zinc-900/40 rounded-lg p-5 text-sm text-zinc-400 space-y-4">
        <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs uppercase tracking-wider">
          <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          Ranking Inspector
        </div>
        <p>Select any search result on the left to inspect exactly why it ranked, its score decomposition, and metadata influence.</p>
        {understanding && (
          <div className="mt-4 pt-4 border-t border-zinc-800/80">
            <div className="text-xs text-zinc-500 font-mono uppercase mb-2">Query Understanding Extraction</div>
            <pre className="text-xs bg-zinc-950 p-3 rounded font-mono text-zinc-300 overflow-auto border border-zinc-800/60">
              {JSON.stringify(understanding, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  }

  const isRankOne = hit.rank === 1;
  const rows = [
    { label: "BM25 / Keyword Score", value: hit.keyword_score, color: "bg-blue-500" },
    { label: "Dense Semantic Cosine", value: hit.dense_score, color: "bg-purple-500" },
    { label: "Hybrid Alpha-Fusion", value: hit.hybrid_score, color: "bg-cyan-500" },
    { label: "Reranker Output", value: hit.rerank_score ?? 0, color: "bg-emerald-500" },
    { label: "Final Composite Score", value: hit.final_score, color: "bg-amber-400" },
  ];

  const rerankExp = (hit.explanation?.rerank as Record<string, any>) || {};

  return (
    <div className="border border-zinc-800 bg-zinc-900/50 rounded-lg p-5 space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded ${isRankOne ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "bg-zinc-800 text-zinc-300"}`}>
              {isRankOne ? "🏆 #1 Top Ranked Result" : `Rank #${hit.rank}`}
            </span>
            <span className="text-xs text-zinc-500 font-mono">{hit.document_id}</span>
          </div>
          <h2 className="text-lg font-semibold text-white mt-1.5">{hit.title}</h2>
        </div>
        <div className="text-right">
          <div className="text-xs text-zinc-400">Composite Score</div>
          <div className="text-xl font-mono font-bold text-cyan-400">{hit.final_score.toFixed(4)}</div>
        </div>
      </div>

      {/* Why this result ranked #1 / explanation block */}
      <div className="bg-zinc-950/80 border border-zinc-800 rounded-md p-3.5 space-y-2">
        <div className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold flex items-center gap-1.5">
          <span>⚡</span> Why this result ranked {isRankOne ? "#1" : `#${hit.rank}`}:
        </div>
        <ul className="text-xs text-zinc-300 space-y-1.5 list-disc list-inside">
          <li>
            <span className="text-zinc-400">Lexical match:</span> BM25 scored{" "}
            <span className="font-mono text-blue-400 font-semibold">{hit.keyword_score.toFixed(3)}</span> based on exact query token overlap.
          </li>
          <li>
            <span className="text-zinc-400">Vector semantics:</span> Dense cosine similarity reached{" "}
            <span className="font-mono text-purple-400 font-semibold">{hit.dense_score.toFixed(3)}</span>.
          </li>
          {rerankExp.term_overlap !== undefined && (
            <li>
              <span className="text-zinc-400">Rerank heuristic:</span> Term overlap {(rerankExp.term_overlap * 100).toFixed(0)}% with a +{(rerankExp.metadata_boost || 0).toFixed(2)} metadata category/attribute boost.
            </li>
          )}
        </ul>
      </div>

      {/* Score Bars */}
      <div className="space-y-3">
        <div className="text-xs font-mono uppercase text-zinc-500 tracking-wider">Score Decomposition</div>
        {rows.map((r) => (
          <div key={r.label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-zinc-400">{r.label}</span>
              <span className="font-mono text-zinc-200 font-medium">{Number(r.value).toFixed(4)}</span>
            </div>
            <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full ${r.color} transition-all duration-300`}
                style={{ width: `${Math.max(2, Math.min(100, Number(r.value) * 100))}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Trace / Metadata Details */}
      <details className="text-xs border border-zinc-800/80 rounded bg-zinc-950 p-3">
        <summary className="cursor-pointer text-zinc-400 font-mono hover:text-white">
          Raw Metadata & Pipeline Trace ({Object.keys(hit.metadata || {}).length} fields)
        </summary>
        <pre className="mt-3 text-[11px] font-mono text-zinc-300 overflow-auto max-h-56 leading-relaxed">
          {JSON.stringify({ metadata: hit.metadata, explanation: hit.explanation, trace }, null, 2)}
        </pre>
      </details>
    </div>
  );
}
