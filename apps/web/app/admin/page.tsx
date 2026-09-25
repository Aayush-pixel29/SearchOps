"use client";

import { useEffect, useState } from "react";
import { useToken } from "@/lib/auth";
import { API_URL } from "@/lib/api";

export default function AdminPage() {
  const { token } = useToken();
  const [info, setInfo] = useState<any>(null);
  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/admin/tenant`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setInfo);
  }, [token]);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl">Tenant</h1>
      <p className="text-sm text-zinc-400">All retrieval is scoped to this tenant_id. Isolation is enforced in SQL.</p>
      <pre className="bg-zinc-950 border border-zinc-800 rounded p-4 text-sm">{JSON.stringify(info, null, 2)}</pre>
    </div>
  );
}
