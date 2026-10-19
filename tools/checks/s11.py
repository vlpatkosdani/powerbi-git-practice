"""s11 - Update your branch with a merge, then fast-forward shared."""
from checks._update import commits, model
from checks.common import Ctx, git, resolve


def run(c: Ctx) -> None:
    mine, ben = commits(c)
    # The merge's first parent is your branch, the second is s11/shared (not the other way round).
    merges = c.commits(f"{c.base}..{c.head}", "--merges")
    right_way = bool(mine and ben) and any(
        c.is_ancestor(mine, f"{m}^1") and c.is_ancestor(ben, f"{m}^2") for m in merges)
    c.check(right_way, "There's a merge commit that brought `s11/shared` into your branch")
    if mine and ben:
        c.check(not c.is_ancestor(ben, mine), "Your commit kept its hash (nothing was rewritten)")
    c.check(c.pushed("s11/feature"), "Your branch is on GitHub (a normal push, no force needed)")
    feat = resolve("s11/feature")
    c.check(feat is not None and git("rev-parse", feat) == c.head,
            "`s11/shared` and `s11/feature` point to the same commit (the merge back was a fast-forward)")
    model(c)
