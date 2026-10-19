"""s02 - A feature branch with one measure, pushed."""
from checks.common import SALES, Ctx, remote_has


def run(c: Ctx) -> None:
    c.measure_is(SALES, "Double Margin", ["[Margin] * 2"], {"formatString": "#,0.00"})
    c.check(c.measure(SALES, "Double Margin", rev=c.base) is None, "`main` doesn't have `Double Margin`")
    c.check(remote_has("s02/feature-double-margin"), "Your branch is on GitHub")
