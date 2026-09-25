"use client";

import { useEffect, useState } from "react";
import { useToken } from "@/lib/auth";
import { API_URL } from "@/lib/api";

export default function EvaluationPage() {
  const { token } = useToken();
  const [run, setRun] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function latest() {
    if (!token) return;
    const res = await fetch(`${API_URL}/eval/runs`, { headers: { Authorization: `Bearer ${token}` } });
    const rows = await res.json();
    if (rows[0]) setRun(rows[0]);
  }

  useEffect(() => {
    latest();
  }, [token]);

  async function execute() {
    if (!token) return;
    setBusy(true);
    const res = await fetch(`${API_URL}/eval/run`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ top_k: 10 }),
    });
    setRun(await res.json());
    setBusy(false);
  }

  const metrics = run?.metrics || {};
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl">Evaluation</h1>
        <button onClick={execute} className="bg-cyan-500 text-zinc-950 px-4 py-2 rounded" disabled={!token || busy}>
          {busy ? "Running benchmark…" : "Run benchmark"}
        </button>
      </div>
      <p className="text-sm text-zinc-400">
        Metrics are computed from labeled demo queries. Empty table means the benchmark has not been run yet.
      </p>
      <table className="w-full text-sm font-mono">
        <thead className="text-zinc-500 text-left">
          <tr>
            <th className="py-2">Method</th>
            <th>Recall@5</th>
            <th>Recall@10</th>
            <th>MRR</th>
            <th>nDCG@10</th>
            <th>p95 ms</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(metrics).map(([method, row]: any) => (
            <tr key={method} className="border-t border-zinc-800">
              <td className="py-2">{method}</td>
              <td>{row.recall_at_5?.toFixed(3)}</td>
              <td>{row.recall_at_10?.toFixed(3)}</td>
              <td>{row.mrr?.toFixed(3)}</td>
              <td>{row.ndcg_at_10?.toFixed(3)}</td>
              <td>{row.p95_ms?.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {run?.table && <pre className="text-xs bg-zinc-950 p-4 rounded overflow-auto">{run.table}</pre>}
    </div>
  );
}
