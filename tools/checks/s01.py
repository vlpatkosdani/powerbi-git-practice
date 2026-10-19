"""s01 - PBIP, .gitignore and the first commits (on main)."""
from checks.common import SALES, Ctx, git


def run(c: Ctx) -> None:
    leaked = git("log", "--all", "--format=%h", "--", "*cache.abf", "*localSettings.json")
    c.check(not leaked, "`cache.abf` and `localSettings.json` were never committed")
    c.check(c.find_commit(c.head, "Added Avg Age measure") is not None, "`Added Avg Age measure` is committed")
    c.measure_is(SALES, "Avg Age", ["AVERAGE ( Customer[Age] )"])
    committed = git("log", "--format=%h", "-S", "Double Margin", c.head, "--", SALES)
    c.check(c.measure(SALES, "Double Margin") is None and not committed, "`Double Margin` was discarded, never committed")
    bg = c.find_commit(c.head, "Background color for the Demo table")
    if c.check(bg is not None, "`Background color for the Demo table` is committed"):
        files = git("show", "--name-only", "--format=", bg).splitlines()
        c.check(bool(files) and all(f.startswith("Contoso.Report/") for f in files),
                "The background color commit only changed report files")
