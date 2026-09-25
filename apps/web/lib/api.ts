export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type SearchHit = {
  document_id: string;
  chunk_id: string;
  title: string;
  content: string;
  source: string;
  score: number;
  rank: number;
  retrieval_method: string;
  keyword_score: number;
  dense_score: number;
  hybrid_score: number;
  rerank_score: number | null;
  final_score: number;
  metadata: Record<string, unknown>;
  explanation: Record<string, unknown>;
};

export async function api<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}
