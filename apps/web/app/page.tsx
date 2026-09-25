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
      <div className="border border-zinc-800 rounded p-4 text-sm text-zinc-500">
        Select a result to inspect why it ranked.
        {understanding && (
          <pre className="mt-4 text-xs text-zinc-400 overflow-auto">{JSON.stringify(understanding, null, 2)}</pre>
        )}
      </div>
    );
  }
  const rows = [
    ["Keyword", hit.keyword_score],
    ["Dense", hit.dense_score],
    ["Hybrid", hit.hybrid_score],
    ["Rerank", hit.rerank_score ?? 0],
    ["Final", hit.final_score],
  ];
  return (
    <div className="border border-zinc-800 rounded p-4 space-y-4">
      <div>
        <div className="text-xs uppercase tracking-wide text-zinc-500">Why this rank?</div>
        <h2 className="text-lg">{hit.title}</h2>
        <div className="font-mono text-xs text-zinc-500">{hit.document_id}</div>
      </div>
      {rows.map(([label, value]) => (
        <div key={String(label)}>
          <div className="flex justify-between text-xs mb-1">
            <span>{label}</span>
            <span className="font-mono">{Number(value).toFixed(4)}</span>
          </div>
          <div className="score-bar">
            <span style={{ width: `${Math.max(2, Math.min(100, Number(value) * 100))}%` }} />
          </div>
        </div>
      ))}
      <pre className="text-xs bg-zinc-950 p-3 rounded overflow-auto max-h-64">
        {JSON.stringify({ metadata: hit.metadata, explanation: hit.explanation, trace }, null, 2)}
      </pre>
    </div>
  );
}
