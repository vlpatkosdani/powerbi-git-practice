"""s05 - pages.json conflict: two branches saved with different pages open, both merged."""
import json

from checks.common import Ctx, git, resolve

PAGES = "Contoso.Report/definition/pages/pages.json"
CHOICES = {"ReportSection": "Page 1", "ReportSection6f352b07e170306db197": "Page 2"}


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    bad = []
    for path in git("ls-tree", "-r", "--name-only", c.head, "--", "Contoso.Report").splitlines():
        if path.endswith(".json"):
            try:
                json.loads(c.file(path))
            except ValueError:
                bad.append(path)
    c.check(not bad, "All report JSON files are valid" + (f" (broken: {', '.join(bad[:3])})" if bad else ""))
    start = resolve("module/2-conflicts") or "origin/module/2-conflicts"
    merges = c.commits(f"{start}..{c.head}", "--merges") if c.is_ancestor(start, c.head) else []
    c.check(len(merges) >= 1, "Your two branches are merged into `s05/shared` (there's a merge commit)")
    try:
        active = json.loads(c.file(PAGES)).get("activePageName")
    except (TypeError, ValueError):
        active = None
    c.check(active in CHOICES, f"The report opens on Page 1 or Page 2 (found `{active}`)")
