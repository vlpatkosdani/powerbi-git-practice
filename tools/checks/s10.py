"""s10 - Rebase your branch, then fast-forward shared."""
from checks._update import commits, model
from checks.common import Ctx, git, resolve


def run(c: Ctx) -> None:
    mine, ben = commits(c)
    c.check(not c.commits(f"{c.base}..{c.head}", "--merges"), "One straight line: no merge commits")
    if mine and ben:
        c.check(c.is_ancestor(ben, mine), "Your commit sits on top of Ben's (it was rebased)")
    feat = resolve("s10/feature")
    c.check(feat is not None and git("rev-parse", feat) == c.head,
            "`s10/shared` and `s10/feature` point to the same commit (the merge back was a fast-forward)")
    model(c)
