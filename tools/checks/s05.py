"""s05 - pages.json conflict: two branches saved with different pages open, both merged."""
import json

from checks.common import Ctx, git, resolve

PAGES = "Contoso.Report/definition/pages/pages.json"
CHOICES = {"ReportSection": "Page 1", "ReportSection6f352b07e170306db197": "Page 2"}


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        raise ValueError(f"duplicate key(s): {', '.join(sorted(dupes))}")
    return dict(pairs)


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    bad = []
    for path in git("ls-tree", "-r", "--name-only", c.head, "--", "Contoso.Report").splitlines():
        if path.endswith(".json"):
            try:
                json.loads(c.file(path), object_pairs_hook=_no_duplicate_keys)
            except ValueError:
                bad.append(path)
    c.check(not bad, "All report JSON files are valid" + (f" (broken: {', '.join(bad[:3])})" if bad else ""))
    start = resolve("module/2-conflicts") or "origin/module/2-conflicts"
    merges = c.commits(f"{start}..{c.head}", "--merges") if c.is_ancestor(start, c.head) else []
    # --full-history: without it git simplifies away one side of the merge and finds one page commit.
    page_commits = git("rev-list", "--no-merges", "--full-history", f"{start}..{c.head}", "--", PAGES).split() if merges else []
    c.check(len(merges) >= 1 and len(page_commits) >= 2,
            "Both of your branches are merged into `s05/shared` (a merge commit, and a page commit from each branch)")
    try:
        active = json.loads(c.file(PAGES)).get("activePageName")
    except (TypeError, ValueError):
        active = None
    c.check(active in CHOICES, f"The report opens on Page 1 or Page 2 (found `{active}`)")
