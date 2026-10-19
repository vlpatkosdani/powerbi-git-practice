"""s07 - Silent conflict: a renamed column still used under its old name."""
import subprocess

from checks.common import SALES, Ctx, resolve


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    for b in ("s07/anna", "s07/Ben"):
        r = resolve(b)
        c.check(r is not None and c.is_ancestor(r, c.head), f"`{b}` is merged into `s07/shared`")
    hits = subprocess.run(["git", "grep", "-nF", "[Net Price]", c.head, "--", "*.tmdl"],
                          capture_output=True, text=True).stdout.strip()
    c.check(not hits, "Nothing uses the old `[Net Price]` column any more" + (f":\n{hits[:400]}" if hits else ""))
    c.check("Net Unit Price" in (c.file(SALES) or ""), "The column is called `Net Unit Price`")
    m = c.measure(SALES, "Avg Net Price")
    c.check(m is not None and "NET UNIT PRICE" in m.expression.upper(), "`Avg Net Price` uses `Net Unit Price`")
