"""s15 - Revert a bad commit without rewriting shared history."""
from checks.common import PRODUCT, SALES, Ctx, git


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    c.contains_base()
    bad = c.find_commit(c.base, "Tidy Total Quantity")
    c.check(bad is not None, "The bad commit is still in the shared history (nothing was rewritten)")
    if bad:
        msgs = git("log", "--format=%B", f"{c.base}..{c.head}")
        c.check(f"This reverts commit {bad}" in msgs, "A revert commit for 'Tidy Total Quantity' is on your branch")
    c.measure_is(SALES, "Total Quantity", ["SUM ( Sales[Quantity] )"], {"formatString": "#,0"})
    c.check(c.measure(SALES, "Order Count") is not None, "Earlier good change (`Order Count`) kept")
    c.check(c.measure(PRODUCT, "Product Count") is not None, "Later good change (`Product Count`) kept")
