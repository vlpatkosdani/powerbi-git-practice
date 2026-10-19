"""s14 - Tag what you deploy, then answer a question from the tags."""
from checks.common import SALES, Ctx, git, git_ok


def run(c: Ctx) -> None:
    for tag in ("v1.0.0", "v1.1.0"):
        if c.check(git_ok("rev-parse", "--verify", "-q", f"refs/tags/{tag}"), f"Tag `{tag}` exists"):
            c.check(git("cat-file", "-t", f"refs/tags/{tag}") == "tag", f"`{tag}` is an annotated tag (it has a message)")
    old, new = c.measure(SALES, "Total Cost", rev="v1.0.0"), c.measure(SALES, "Total Cost", rev="v1.1.0")
    c.check(old is not None and "1.05" not in old.expression, "`v1.0.0`: `Total Cost` without the handling cost")
    c.check(new is not None and "1.05" in new.expression, "`v1.1.0`: `Total Cost` includes the 5% handling cost")
    c.check(new is not None and c.measure(SALES, "Order Count", rev="v1.1.0") is not None,
            "`v1.1.0` is on the deployed commit, after `Add Order Count`")
    log = c.file("CHANGELOG.md")
    if c.check(log is not None, "`CHANGELOG.md` is committed on `s14/prod`"):
        c.check("Total Cost" in log, "The changelog names `Total Cost` as the reason")
