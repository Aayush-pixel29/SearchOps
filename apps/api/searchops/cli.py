from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from searchops import db as database
from searchops.demo.catalog import EVAL_CASES, build_catalog
from searchops.demo.seed import ensure_demo_data
from searchops.evaluation.engine import EvaluationEngine


async def cmd_seed() -> None:
    database.init_engine()
    await database.create_tables()
    assert database.SessionLocal is not None
    async with database.SessionLocal() as session:
        await ensure_demo_data(session)
        print("Demo catalog seeded.")


async def cmd_eval() -> None:
    database.init_engine()
    await database.create_tables()
    assert database.SessionLocal is not None
    async with database.SessionLocal() as session:
        await ensure_demo_data(session)
        from sqlalchemy import select

        from searchops.models import Tenant

        tenant = (await session.execute(select(Tenant).where(Tenant.slug == "demo"))).scalar_one()
        engine = EvaluationEngine(session)
        run = await engine.run(tenant.id)
        print(engine.render(run))
        out = Path(__file__).resolve().parents[2] / "evals" / "last_run.json"
        # parents[2] from searchops/cli.py is apps/api; go to repo root
        root = Path(__file__).resolve().parents[3]
        out = root / "evals" / "last_run.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"id": run.id, "metrics": run.metrics}, indent=2), encoding="utf-8")
        print(f"\nWrote {out}")


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
    sub.add_parser("seed")
    sub.add_parser("eval")
    sub.add_parser("export-catalog")
    args = parser.parse_args()
    if args.command == "seed":
        asyncio.run(cmd_seed())
    elif args.command == "eval":
        asyncio.run(cmd_eval())
    elif args.command == "export-catalog":
        export_catalog()


if __name__ == "__main__":
    main()
