"""s13 - Hotfix on PROD, backported to dev."""
from checks.common import SALES, Ctx, resolve, tmdl

SUM = tmdl.normalise_dax("SUM ( Sales[Quantity] )")


def run(c: Ctx) -> None:
    prod, dev = resolve("s13/prod"), resolve("s13/dev")
    if not c.check(prod is not None and dev is not None, "`s13/prod` and `s13/dev` exist"):
        return
    for name, rev in (("s13/prod", prod), ("s13/dev", dev)):
        tq = c.measure(SALES, "Total Quantity", rev=rev)
        c.check(tq is not None and tmdl.normalise_dax(tq.expression) == SUM, f"`{name}`: `Total Quantity` is `SUM` again")
        c.check(c.find_commit(rev, "Hotfix: Total Quantity back to SUM") is not None, f"`{name}` has the hotfix commit `Hotfix: Total Quantity back to SUM` (cherry-pick or merge it, don't retype it)")
    c.check(c.measure(SALES, "Order Count", rev=prod) is None, "`Order Count` (not released yet) didn't go to PROD")
    c.check(c.measure(SALES, "Order Count", rev=dev) is not None, "`Order Count` is still on dev")
