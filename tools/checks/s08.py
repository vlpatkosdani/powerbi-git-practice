"""s08 - A pull request, reviewed and merged on GitHub."""
from checks.common import SALES, Ctx, git


def run(c: Ctx) -> None:
    c.check(c.find_commit(c.head, "Total Cost format + Demo page layout") is not None,
            "Your commit is on `s08/shared` on GitHub")
    merges = git("log", "--merges", "--format=%s", f"{c.base}..{c.head}")
    c.check("Merge pull request" in merges, "It got there through a merged pull request")
    tc = c.measure(SALES, "Total Cost")
    c.check(tc is not None and tc.properties.get("formatString") == "#,0", "`Total Cost` has 0 decimals")
    c.info("The PR description and checklist can't be checked from here. Have a look at the PR yourself.")
