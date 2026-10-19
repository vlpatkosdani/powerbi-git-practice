"""s04 - Same measure edited on both branches, both merged into s04/shared."""
from checks.common import SALES, Ctx

EXPECTED = [
    "DIVIDE ( [Margin], [Sales Amount], 0 )",
]


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    anna = c.find_commit(c.head, "Margin %: show 0 instead of blank")
    c.check(anna is not None, "Anna's branch (`s04/feature-a`) is merged into `s04/shared`")
    Ben = c.find_commit(c.head, "Margin %: inline calculation + Profitability folder")
    c.check(Ben is not None, "Ben's branch (`s04/feature-b`) is merged into `s04/shared`")
    c.measure_is(SALES, "Margin %", EXPECTED, {"displayFolder": "Profitability", "formatString": "0.00%;-0.00%;0.00%"})
    for other in ("Sales Amount", "Total Cost", "Margin", "Total Quantity"):
        c.check(c.measure(SALES, other) is not None, f"`{other}` untouched and still present")
