"""Shared context + helpers for scenario checkers (stdlib only)."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tmdl  # noqa: E402

SALES = "Contoso.SemanticModel/definition/tables/Sales.tmdl"
PRODUCT = "Contoso.SemanticModel/definition/tables/Product.tmdl"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def git_ok(*args: str) -> bool:
    return subprocess.run(["git", *args], capture_output=True).returncode == 0


def resolve(name: str) -> str | None:
    """A branch, tag or commit as given, else its origin/ copy, else None."""
    for r in (name, f"origin/{name}"):
        if git_ok("rev-parse", "--verify", "-q", f"{r}^{{commit}}"):
            return r
    return None


def resolve_remote_first(name: str) -> str | None:
    """Like resolve(), but prefer origin/<name>: Start scenario rebuilds the starting
    branches on GitHub, so a local copy can be stale."""
    for r in (f"origin/{name}", name):
        if git_ok("rev-parse", "--verify", "-q", f"{r}^{{commit}}"):
            return r
    return None


def remote_has(branch: str) -> bool:
    return git_ok("rev-parse", "--verify", "-q", f"refs/remotes/origin/{branch}")


@dataclass
class Ctx:
    head: str             # commit sha of the PR head
    base: str             # ref of the PR base, e.g. origin/s04/shared
    pr_body: str = ""
    results: list[tuple[bool, str]] = field(default_factory=list)

    # --- recording -------------------------------------------------------
    def check(self, ok: bool, msg: str) -> bool:
        self.results.append((bool(ok), msg))
        return bool(ok)

    def info(self, msg: str) -> None:
        self.results.append((None, msg))  # type: ignore[arg-type]

    # --- repo access at the PR head -------------------------------------
    def file(self, path: str, rev: str | None = None) -> str | None:
        rev = rev or self.head
        if not git_ok("cat-file", "-e", f"{rev}:{path}"):
            return None
        return git("show", f"{rev}:{path}")

    def measure(self, path: str, name: str, rev: str | None = None):
        text = self.file(path, rev)
        if text is None:
            return None
        with tempfile.NamedTemporaryFile("w", suffix=".tmdl", delete=False, encoding="utf-8") as fh:
            fh.write(text)
        return tmdl.get_measure(Path(fh.name), name)

    def commits(self, rng: str, *extra: str) -> list[str]:
        out = git("rev-list", *extra, rng)
        return out.split() if out else []

    def is_ancestor(self, a: str, b: str) -> bool:
        return git_ok("merge-base", "--is-ancestor", a, b)

    def find_commit(self, rev: str, subject: str) -> str | None:
        out = git("log", "--format=%H", "--fixed-strings", f"--grep={subject}", rev)
        return out.split()[0] if out else None

    # --- common checks ---------------------------------------------------
    def no_conflict_markers(self) -> bool:
        hits = subprocess.run(
            ["git", "grep", "-nE", r"^(<<<<<<<|>>>>>>>)( |$)|^=======$", self.head, "--", "*.tmdl", "*.json", "*.pbir"],
            capture_output=True, text=True,
        ).stdout.strip()
        return self.check(not hits, "No leftover conflict markers" + ("" if not hits else f":\n```\n{hits[:800]}\n```"))

    def pushed(self, branch: str) -> bool:
        """origin/<branch> exists and is exactly the commit being checked."""
        return remote_has(branch) and git("rev-parse", f"origin/{branch}") == git("rev-parse", self.head)

    def contains_base(self) -> bool:
        return self.check(self.is_ancestor(self.base, self.head),
                          f"Your branch contains the latest `{self.base.removeprefix('origin/')}` (merged or rebased on top of it)")

    def measure_is(self, path: str, name: str, accepted: list[str], props: dict[str, str] | None = None) -> bool:
        m = self.measure(path, name)
        if not self.check(m is not None, f"Measure `{name}` exists"):
            return False
        ok = tmdl.normalise_dax(m.expression) in {tmdl.normalise_dax(a) for a in accepted}
        self.check(ok, f"`{name}` expression is the agreed one (found `{m.expression}`)")
        for k, v in (props or {}).items():
            self.check(m.properties.get(k) == v, f"`{name}` {k} is `{v}` (found `{m.properties.get(k)}`)")
        return ok
