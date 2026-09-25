"use client";

import { useState } from "react";
import { useToken } from "@/lib/auth";
import { API_URL } from "@/lib/api";

const METHODS = ["keyword", "dense", "hybrid", "hybrid_rerank"];
const LABELS: Record<string, string> = {
  keyword: "BM25",
  dense: "Dense",
  hybrid: "Hybrid",
  hybrid_rerank: "Hybrid + Reranker",
};

export default function ComparePage() {
  const { token } = useToken();
  const [q, setQ] = useState("best python backend framework");
  const [cols, setCols] = useState<Record<string, any>>({});
  const [busy, setBusy] = useState(false);

  async function run() {
    if (!token) return;
    setBusy(true);
    const next: Record<string, any> = {};
    for (const method of METHODS) {
      const res = await fetch(
        `${API_URL}/search?q=${encodeURIComponent(q)}&retrieval_method=${method}&top_k=5`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      next[method] = await res.json();
    }
    setCols(next);
    setBusy(false);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl">Ranking comparison</h1>
      <p className="text-sm text-zinc-400">Same query, four retrievers. This is the core demo.</p>
      <div className="flex gap-3">
        <input
          className="flex-1 bg-zinc-900 border border-zinc-700 rounded px-3 py-2 font-mono text-sm"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button onClick={run} className="bg-cyan-500 text-zinc-950 px-4 rounded" disabled={!token || busy}>
          {busy ? "Comparing…" : "Compare"}
        </button>
      </div>
      {Object.keys(cols).length > 0 && (
        <div className="grid grid-cols-4 gap-3">
          {METHODS.map((m) => (
            <div key={m} className="border border-zinc-800 rounded p-3">
              <div className="font-mono text-xs text-cyan-400 mb-2">{LABELS[m]}</div>
              <ol className="space-y-2 text-sm">
                {(cols[m].results || []).map((hit: any) => (
                  <li key={hit.chunk_id}>
                    <div className="font-medium">{hit.rank}. {hit.title}</div>
                    <div className="text-xs font-mono text-zinc-500">{hit.score.toFixed(3)}</div>
                  </li>
                ))}
              </ol>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
