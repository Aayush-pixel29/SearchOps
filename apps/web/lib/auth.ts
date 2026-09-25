"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

export function useToken() {
  const [token, setToken] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function authenticate() {
      try {
        const existing = localStorage.getItem("searchops_token");
        if (existing) {
          setToken(existing);
          return;
        }
        const res = await fetch(`${API_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: "demo@searchops.dev",
            password: "demo-password",
            tenant_slug: "demo",
          }),
        });
        if (!res.ok) {
          const errText = await res.text();
          throw new Error(errText);
        }
        const data = await res.json();
        localStorage.setItem("searchops_token", data.access_token);
        setToken(data.access_token);
        setError("");
      } catch (e: any) {
        localStorage.removeItem("searchops_token");
        setError(e?.message || String(e));
      }
    }
    authenticate();
  }, []);

  return { token, error };
}
