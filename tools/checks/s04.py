"""s04 - Same measure edited on both branches, both merged into s04/shared."""
from checks.common import SALES, Ctx, resolve

EXPECTED = [
    "DIVIDE ( [Margin], [Sales Amount], 0 )",
]


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    for who, branch, subject in (("Anna", "s04/feature-a", "Margin %: show 0 instead of blank"),
                                 ("Ben", "s04/feature-b", "Margin %: inline calculation + Profitability folder")):
        ref = resolve(branch)
        merged = c.is_ancestor(ref, c.head) if ref else c.find_commit(c.head, subject) is not None
        c.check(merged, f"{who}'s branch (`{branch}`) is merged into `s04/shared`")
    c.measure_is(SALES, "Margin %", EXPECTED, {"displayFolder": "Profitability", "formatString": "0.00%;-0.00%;0.00%"})
    for other in ("Sales Amount", "Total Cost", "Margin", "Total Quantity"):
        c.check(c.measure(SALES, other) is not None, f"`{other}` untouched and still present")
