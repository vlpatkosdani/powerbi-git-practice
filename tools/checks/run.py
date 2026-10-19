"""Grade a scenario.

On a push:          python tools/checks/run.py --event push --head-ref s04/shared [--head-sha SHA]
On a pull request:  python tools/checks/run.py --event pr --head-ref s08/feature --base-ref s08/shared

Writes a markdown report to --out and prints `result=<passed|failed|skipped>`
(also appended to $GITHUB_OUTPUT when running in Actions).
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from checks.common import Ctx, git_ok  # noqa: E402


def find(event: str, head_ref: str, base_ref: str | None):
    """Return (scenario, base) for a graded step, or (None, None).

    Each graded step has `via`: "push" steps are checked when their head branch is
    pushed, "pr" steps when a pull request head -> base is opened or updated."""
    cfg = json.loads((TOOLS / "scenarios.json").read_text(encoding="utf-8"))
    for s in cfg["scenarios"]:
        for g in s["graded"]:
            if g.get("via", "pr") != event or not re.match(g["head"], head_ref):
                continue
            if event == "pr" and g["base"] != base_ref:
                continue
            return s, g["base"]
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", choices=["push", "pr"], default="pr")
    ap.add_argument("--head-ref", required=True)
    ap.add_argument("--base-ref", help="required for --event pr")
    ap.add_argument("--head-sha", default="HEAD")
    ap.add_argument("--pr-body-file")
    ap.add_argument("--out", default=os.path.join(os.environ.get("RUNNER_TEMP", tempfile.gettempdir()), "grade-report.md"))
    a = ap.parse_args()

    scenario, base_ref = find(a.event, a.head_ref, a.base_ref)
    if scenario is None:
        result, lines = "skipped", [f"`{a.head_ref}` isn't a graded step ({a.event}), nothing to check."]
    elif not (TOOLS / "checks" / f"{scenario['id']}.py").exists():
        result, lines = "skipped", [f"No checker for **{scenario['id']}** yet (status: {scenario['status']})."]
    else:
        base = f"origin/{base_ref}" if git_ok("rev-parse", "--verify", "-q", f"origin/{base_ref}") else base_ref
        body = Path(a.pr_body_file).read_text(encoding="utf-8") if a.pr_body_file else ""
        ctx = Ctx(head=a.head_sha, base=base, pr_body=body)
        importlib.import_module(f"checks.{scenario['id']}").run(ctx)
        failed = [r for r in ctx.results if r[0] is False]
        result = "failed" if failed else "passed"
        icon = {True: "✅", False: "❌", None: "💡"}
        lines = [f"### {scenario['id']} · {scenario['title']}", ""]
        lines += [f"- {icon[ok]} {msg}" for ok, msg in ctx.results]
        lines += ["", "**Passed, nice work!** Re-run Start scenario any time to practise it again."
                  if result == "passed" else
                  "**Not there yet.** Fix the ❌ items and push again. The check re-runs automatically."]

    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"result={result}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"result={result}\n")
    return 1 if result == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
