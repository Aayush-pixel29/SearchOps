import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))
from searchops.demo.catalog import EVAL_CASES, build_catalog

(ROOT / "data" / "raw" / "catalog.json").write_text(json.dumps(build_catalog(), indent=2), encoding="utf-8")
(ROOT / "evals" / "demo_cases.json").write_text(json.dumps(EVAL_CASES, indent=2), encoding="utf-8")
print("exported catalog and eval cases")
