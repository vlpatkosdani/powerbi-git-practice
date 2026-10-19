"""s03 - Merge a feature branch back into develop."""
from checks.common import SALES, Ctx, resolve


def run(c: Ctx) -> None:
    feat = resolve("s03/feature-order-measures")
    c.check(feat is not None and c.is_ancestor(feat, c.head), "The feature branch is merged into `s03/develop`")
    for subject in ("Add Order Count", "Add Average Price"):
        on_feat = feat is not None and c.find_commit(feat, subject) is not None
        c.check(on_feat and c.find_commit(c.head, subject) is not None,
                f"`{subject}` was committed on the feature branch and is now on `s03/develop`")
    c.measure_is(SALES, "Order Count", ["DISTINCTCOUNT ( Sales[Order Number] )"])
    c.measure_is(SALES, "Average Price", ["DIVIDE ( [Sales Amount], [Total Quantity] )"])
