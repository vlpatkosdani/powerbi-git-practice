"""s12 - Cherry-pick only the approved commit from dev to uat."""
from checks.common import PRODUCT, SALES, Ctx, resolve


def run(c: Ctx) -> None:
    c.no_conflict_markers()
    c.contains_base()
    new = c.commits(f"{c.base}..{c.head}", "--no-merges")
    c.check(len(new) == 1, f"Exactly one commit promoted (found {len(new)})")
    c.measure_is(SALES, "Average Price", ["DIVIDE ( [Sales Amount], [Total Quantity] )"],
                 {"formatString": "#,0.00"})
    c.check(c.measure(SALES, "Order Count") is None, "`Order Count` (still in testing) stayed on dev")
    sa = c.measure(SALES, "Sales Amount")
    c.check(sa is not None and "NET PRICE" in sa.expression.upper(),
            "`Sales Amount` experiment (not approved) stayed on dev")
    if new:
        from checks.common import git
        msg = git("log", "-1", "--format=%B", new[0])
        if "cherry picked from commit" in msg:
            c.info("Bonus: you used `cherry-pick -x`, so the commit records where it came from.")
        else:
            c.info("Tip: `git cherry-pick -x <sha>` adds a 'cherry picked from' line - handy for audit.")
    optional_part(c)


def optional_part(c: Ctx) -> None:
    """Going further: the release branch with a half-approved commit (s12/opt-*), only if you did it."""
    rel, uat = resolve("s12/opt-release"), resolve("s12/opt-uat")
    if not (rel and uat):
        return
    c.info("Going further (`s12/opt-release`):")
    new = c.commits(f"{uat}..{rel}", "--no-merges")
    c.check(len(new) == 2, f"`s12/opt-release` has two commits on top of `s12/opt-uat` (found {len(new)})")
    c.check(c.measure(SALES, "Order Count", rev=rel) is not None, "`Order Count` (approved) is on the release branch")
    c.check(c.measure(PRODUCT, "Product Count", rev=rel) is not None, "`Product Count` (approved) is on the release branch")
    c.check(c.measure(SALES, "Average Price", rev=rel) is None, "`Average Price` (not approved) stayed on dev")
    tc, base_tc = c.measure(SALES, "Total Cost", rev=rel), c.measure(SALES, "Total Cost", rev=uat)
    c.check(tc is not None and base_tc is not None and tc.properties.get("formatString") == base_tc.properties.get("formatString"),
            "The `Total Cost` format change (not approved) stayed on dev")
