"use client";

import { useEffect, useState } from "react";
import { useToken } from "@/lib/auth";
import { API_URL } from "@/lib/api";

export default function DocumentsPage() {
  const { token } = useToken();
  const [docs, setDocs] = useState<any[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("knowledge");

  async function load() {
    if (!token) return;
    const res = await fetch(`${API_URL}/documents`, { headers: { Authorization: `Bearer ${token}` } });
    setDocs(await res.json());
  }

  useEffect(() => {
    load();
  }, [token]);

  async function upload() {
    if (!token) return;
    await fetch(`${API_URL}/documents`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ title, content, metadata: { category } }),
    });
    setTitle("");
    setContent("");
    load();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl">Indexed documents</h1>
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2">
          <input className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <input className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2" placeholder="category" value={category} onChange={(e) => setCategory(e.target.value)} />
          <textarea className="w-full h-40 bg-zinc-900 border border-zinc-700 rounded px-3 py-2" placeholder="Content (txt/md/json ingested via API)" value={content} onChange={(e) => setContent(e.target.value)} />
          <button onClick={upload} className="bg-cyan-500 text-zinc-950 px-4 py-2 rounded">Ingest</button>
        </div>
        <div className="text-sm space-y-1 max-h-[70vh] overflow-auto">
          <div className="text-zinc-500 font-mono text-xs">{docs.length} documents</div>
          {docs.map((d) => (
            <div key={d.id} className="border-b border-zinc-800 py-2">
              <div>{d.title}</div>
              <div className="font-mono text-xs text-zinc-500">{d.id}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
