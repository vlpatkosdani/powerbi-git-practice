"""s11 - Update your branch with a merge, then fast-forward shared."""
from checks._update import commits, model
from checks.common import Ctx, git, remote_has, resolve


def run(c: Ctx) -> None:
    mine, ben = commits(c)
    merges = git("log", "--merges", "--format=%s", f"{c.base}..{c.head}")
    c.check("s11/shared" in merges, "There's a merge commit that brought `s11/shared` into your branch")
    if mine and ben:
        c.check(not c.is_ancestor(ben, mine), "Your commit kept its hash (nothing was rewritten)")
    c.check(remote_has("s11/feature"), "Your branch is on GitHub (a normal push, no force needed)")
    feat = resolve("s11/feature")
    c.check(feat is not None and git("rev-parse", feat) == c.head,
            "`s11/shared` and `s11/feature` point to the same commit (the merge back was a fast-forward)")
    model(c)
