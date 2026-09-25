"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  ["/", "Search"],
  ["/compare", "Ranking compare"],
  ["/documents", "Documents"],
  ["/evaluation", "Evaluation"],
  ["/performance", "Performance"],
  ["/admin", "Tenant"],
];

export function Nav() {
  const path = usePathname();
  return (
    <aside className="w-60 shrink-0 border-r border-zinc-800 bg-zinc-950 p-5 flex flex-col gap-6">
      <div>
        <div className="font-mono text-xs tracking-[0.2em] text-cyan-400">SEARCHOPS</div>
        <div className="text-sm text-zinc-400 mt-1">Retrieval engineering</div>
      </div>
      <nav className="flex flex-col gap-1">
        {LINKS.map(([href, label]) => {
          const active = path === href;
          return (
            <Link
              key={href}
              href={href}
              className={`px-3 py-2 rounded text-sm ${active ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-white"}`}
            >
              {label}
            </Link>
          );
        })}
      </nav>
      <p className="mt-auto text-xs text-zinc-600 font-mono">
        BM25 · dense · hybrid · rerank
      </p>
    </aside>
  );
}
