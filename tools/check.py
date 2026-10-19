"""Check a scenario on your own machine, no GitHub needed.

    python tools/check.py s06

Looks at your local branches (or their origin/ copy), runs the same kind of
checks as the GitHub workflow, and prints what passed. Python 3.9+, no packages.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
os.chdir(TOOLS.parent)
from checks.common import Ctx, git, resolve  # noqa: E402

MARK = {True: "[ok]", False: "[x] ", None: "[i] "}


def main() -> int:
    cfg = json.loads((TOOLS / "scenarios.json").read_text(encoding="utf-8"))
    scenarios = {s["id"]: s for s in cfg["scenarios"]}
    sid = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if sid not in scenarios:
        print("Usage: python tools/check.py <scenario id>, one of: " + ", ".join(scenarios))
        return 2
    s, local = scenarios[sid], scenarios[sid]["local"]
    head = resolve(local["head"])
    if head is None:
        print(f"Branch `{local['head']}` not found. Did you do the Start or Prepare steps of {sid}?")
        print("If the branch lives on GitHub, run `git fetch origin` first.")
        return 1
    base = resolve(local.get("base", local["head"]))
    if base is None:
        print(f"Branch `{local['base']}` not found. Run `git fetch origin` and try again.")
        return 1
    ctx = Ctx(head=git("rev-parse", head), base=base)
    importlib.import_module(f"checks.{sid}").run(ctx)

    print(f"{sid} · {s['title']}  (checking {head})\n")
    for ok, msg in ctx.results:
        print(f"  {MARK[ok]} {msg}")
    failed = [r for r in ctx.results if r[0] is False]
    print("\nAll good, nice work!" if not failed else f"\n{len(failed)} item(s) not there yet. Fix them and run the check again.")
    return 1 if failed else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
