"""Shared checks for s10 (rebase) and s11 (merge): the result is the same, the history isn't."""
from checks.common import SALES, Ctx


def model(c: Ctx) -> None:
    c.check(c.measure(SALES, "Order Count") is not None, "`Order Count` is there")
    tc = c.measure(SALES, "Total Cost")
    c.check(tc is not None and tc.properties.get("formatString") == "#,0", "Ben's change: `Total Cost` has 0 decimals")
    sa = c.measure(SALES, "Sales Amount")
    c.check(sa is not None and sa.properties.get("displayFolder") == "Sales", "Ben's change: `Sales Amount` is in the `Sales` folder")


def commits(c: Ctx):
    mine = c.find_commit(c.head, "Add Order Count")
    ben = c.find_commit(c.head, "Sales Amount: Sales folder")
    c.check(mine is not None, "Your commit `Add Order Count` is on the shared branch")
    c.check(ben is not None and c.find_commit(c.head, "Total Cost: no decimals") is not None,
            "Both of Ben's commits are on the shared branch")
    return mine, ben
