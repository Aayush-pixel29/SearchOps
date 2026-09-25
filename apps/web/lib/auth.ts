"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

export function useToken() {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    const existing = localStorage.getItem("searchops_token");
    if (existing) {
      setToken(existing);
      return;
    }
    fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "demo@searchops.dev",
        password: "demo-password",
        tenant_slug: "demo",
      }),
    })
      .then(async (r) => {
        if (!r.ok) throw new Error(await r.text());
        return r.json();
      })
      .then((data) => {
        localStorage.setItem("searchops_token", data.access_token);
        setToken(data.access_token);
      })
      .catch((e) => setError(String(e)));
  }, []);
  return { token, error };
}
