"""s17 - Undo local commits with reset, get one back with reflog."""
from checks.common import SALES, Ctx, git, remote_has, resolve


def run(c: Ctx) -> None:
    subjects = git("log", "--reverse", "--format=%s", f"{c.base}..{c.head}").splitlines()
    c.check(subjects == ["Add Order Count", "Add Average Price"],
            f"`s17/feature` has `Add Order Count` and `Add Average Price`, nothing else (found {subjects})")
    ap = c.find_commit(c.head, "Add Average Price")
    if ap:
        files = git("show", "--name-only", "--format=", ap).splitlines()
        c.check(files == [SALES], "`Add Average Price` only changes `Sales.tmdl`")
    sa = c.measure(SALES, "Sales Amount")
    c.check(sa is not None and "NET PRICE" in sa.expression.upper(), "`Sales Amount` still uses `Net Price`")
    exp = resolve("s17/experiment")
    c.check(exp is not None and c.find_commit(exp, "Sales Amount: try Unit Price") is not None,
            "`s17/experiment` has the commit you got back from the reflog")
    c.check(not remote_has("s17/feature"), "Nothing was pushed")
