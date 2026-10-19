"""s06 - Delete vs edit: keep the table, with all three files."""
import re

from checks.common import Ctx, resolve

DEF = "Contoso.SemanticModel/definition"
CE = f"{DEF}/tables/Currency Exchange.tmdl"


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    for b in ("s06/feature-a", "s06/feature-b"):
        r = resolve(b)
        c.check(r is not None and c.is_ancestor(r, c.head), f"`{b}` is merged into `s06/shared`")
    c.check(c.file(CE) is not None, "The `Currency Exchange` table is still in the model")
    c.check(c.measure(CE, "Avg Exchange Rate") is not None, "`Avg Exchange Rate` is in `Currency Exchange`")
    ref = re.search(r"^ref table 'Currency Exchange'\s*$", c.file(f"{DEF}/model.tmdl") or "", re.M)
    c.check(ref is not None, "`model.tmdl` still references the table (`ref table 'Currency Exchange'`)")
    c.check("Currency Exchange" in (c.file(f"{DEF}/relationships.tmdl") or ""), "The relationship to `Currency Exchange` is still there")
