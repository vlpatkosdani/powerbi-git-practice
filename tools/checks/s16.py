"""s16 - Revert a merge commit."""
from checks.common import SALES, Ctx, git, resolve


def run(c: Ctx) -> None:
    merges = git("log", "--merges", "--format=%H", f"{c.base}..{c.head}").split()
    if c.check(bool(merges), "The feature was merged into `s16/shared` with a merge commit"):
        msgs = git("log", "--format=%B", f"{c.base}..{c.head}")
        c.check(any(f"This reverts commit {m}" in msgs for m in merges), "A revert commit undoes the merge")
    c.check(c.measure(SALES, "Order Count") is None, "`Order Count` is gone")
    c.check(c.measure(SALES, "Average Order Value") is None, "`Average Order Value` is gone")
    sa = c.measure(SALES, "Sales Amount")
    c.check(sa is not None and "NET PRICE" in sa.expression.upper(), "`Sales Amount` uses `Net Price` again")
    feat = resolve("s16/feature-bad")
    c.check(feat is not None and c.is_ancestor(feat, c.head),
            "Git still sees the feature as merged, so merging it again says `Already up to date.`")
