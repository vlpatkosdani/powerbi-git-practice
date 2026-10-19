"""s09 - Squash five commits into one."""
from checks.common import SALES, Ctx, git, resolve


def run(c: Ctx) -> None:
    new = c.commits(f"{c.base}..{c.head}", "--no-merges")
    c.check(len(new) == 1, f"`s09/squashed` has exactly one commit on top of `s09/shared` (found {len(new)})")
    c.check(not c.commits(f"{c.base}..{c.head}", "--merges"), "No merge commit")
    feat = resolve("s09/feature")
    c.check(feat is not None and not git("diff", feat, c.head),
            "Same result as `s09/feature`: `git diff` shows nothing")
    c.check(c.measure(SALES, "Margin per Unit") is not None, "`Margin per Unit` is there")
