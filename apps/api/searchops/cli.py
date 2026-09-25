from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from searchops import db as database
from searchops.demo.catalog import EVAL_CASES, build_catalog
from searchops.demo.seed import ensure_demo_data
from searchops.evaluation.engine import EvaluationEngine


async def cmd_seed(provider: str | None = None) -> None:
    database.init_engine()
    await database.create_tables()
    assert database.SessionLocal is not None
    async with database.SessionLocal() as session:
        if provider:
            from searchops.config import get_settings
            get_settings().embedding_provider = provider
        await ensure_demo_data(session)
        print(f"Demo catalog seeded (provider={provider or 'default'}).")


async def reseed_catalog(session, tenant_id: str, provider: str) -> None:
    from sqlalchemy import delete
    from searchops.config import get_settings
    from searchops.ingestion.service import IngestionService
    from searchops.models import Chunk, Document
    
    get_settings().embedding_provider = provider
    # Delete existing chunks and docs for demo tenant
    await session.execute(delete(Chunk).where(Chunk.tenant_id == tenant_id))
    await session.execute(delete(Document).where(Document.tenant_id == tenant_id))
    await session.commit()
    
    service = IngestionService(session)
    for item in build_catalog():
        await service.ingest_text(
            tenant_id=tenant_id,
            title=item["title"],
            content=item["content"],
            source=item["source"],
            metadata=item["metadata"],
            document_id=item["id"],
        )
    await session.commit()


async def cmd_eval(provider: str | None = None, reseed: bool = False) -> None:
    database.init_engine()
    await database.create_tables()
    assert database.SessionLocal is not None
    async with database.SessionLocal() as session:
        from sqlalchemy import select
        from searchops.config import get_settings
        from searchops.models import Tenant

        if provider:
            get_settings().embedding_provider = provider

        await ensure_demo_data(session)
        tenant = (await session.execute(select(Tenant).where(Tenant.slug == "demo"))).scalar_one()
        
        if reseed and provider:
            print(f"Re-ingesting catalog with {provider} embeddings...")
            await reseed_catalog(session, tenant.id, provider)

        engine = EvaluationEngine(session)
        run = await engine.run(tenant.id)
        print(f"\n--- Benchmark Results (Provider: {provider or get_settings().embedding_provider}) ---")
        print(engine.render(run))
        
        root = Path(__file__).resolve().parents[3]
        evals_dir = root / "evals"
        evals_dir.mkdir(parents=True, exist_ok=True)
        
        provider_name = provider or get_settings().embedding_provider
        out_last = evals_dir / "last_run.json"
        out_provider = evals_dir / f"{provider_name}_run.json"
        
        payload = {
            "id": run.id,
            "provider": provider_name,
            "metrics": run.metrics,
        }
        out_last.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        out_provider.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote {out_last} and {out_provider}")


def export_catalog() -> None:
    root = Path(__file__).resolve().parents[3]
    raw = root / "data" / "raw" / "catalog.json"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(json.dumps(build_catalog(), indent=2), encoding="utf-8")
    evals = root / "evals" / "demo_cases.json"
    evals.parent.mkdir(parents=True, exist_ok=True)
    evals.write_text(json.dumps(EVAL_CASES, indent=2), encoding="utf-8")
    print(f"Wrote {raw} and {evals}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="searchops")
    sub = parser.add_subparsers(dest="command", required=True)
    
    seed_p = sub.add_parser("seed")
    seed_p.add_argument("--provider", choices=["hashed", "huggingface", "mock"], default=None)
    
    eval_p = sub.add_parser("eval")
    eval_p.add_argument("--provider", choices=["hashed", "huggingface", "mock"], default=None)
    eval_p.add_argument("--reseed", action="store_true", help="Re-embed and re-ingest before eval")
    
    sub.add_parser("export-catalog")
    args = parser.parse_args()
    if args.command == "seed":
        asyncio.run(cmd_seed(args.provider))
    elif args.command == "eval":
        asyncio.run(cmd_eval(args.provider, args.reseed))
    elif args.command == "export-catalog":
        export_catalog()


if __name__ == "__main__":
    main()
