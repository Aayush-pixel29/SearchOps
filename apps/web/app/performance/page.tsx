"use client";

import { useEffect, useState } from "react";
import { useToken } from "@/lib/auth";
import { API_URL } from "@/lib/api";

export default function PerformancePage() {
  const { token } = useToken();
  const [snap, setSnap] = useState<any>(null);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/metrics`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setSnap);
  }, [token]);

  const lat = snap?.latencies_ms || {};
  return (
    <div className="space-y-6">
      <h1 className="text-2xl">Performance</h1>
      <p className="text-sm text-zinc-400">
        Cache hit rate and percentiles are measured in this process. They are empty until searches run.
      </p>
      <div className="grid grid-cols-3 gap-4">
        <Card label="Cache hit rate" value={fmtRate(snap?.cache_hit_rate)} />
        <Card label="Search p50" value={fmtMs(lat.search?.p50)} />
        <Card label="Search p95" value={fmtMs(lat.search?.p95)} />
      </div>
      <table className="w-full text-sm font-mono">
        <thead className="text-left text-zinc-500">
          <tr>
            <th className="py-2">Span</th>
            <th>count</th>
            <th>p50</th>
            <th>p95</th>
            <th>mean</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(lat).map(([name, row]: any) => (
            <tr key={name} className="border-t border-zinc-800">
              <td className="py-2">{name}</td>
              <td>{row.count}</td>
              <td>{fmtMs(row.p50)}</td>
              <td>{fmtMs(row.p95)}</td>
              <td>{fmtMs(row.mean)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Card({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-zinc-800 rounded p-4">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="text-2xl font-mono mt-1">{value}</div>
    </div>
  );
}

function fmtMs(v: number | null | undefined) {
  return v == null ? "—" : `${v.toFixed(1)} ms`;
}
function fmtRate(v: number | null | undefined) {
  return v == null ? "—" : `${(v * 100).toFixed(1)}%`;
}
