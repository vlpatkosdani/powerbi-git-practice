"""Tiny TMDL helper used by the scenario setup scripts and the checkers.

It understands just enough TMDL for the exercises: tables, measures (single-
or multi-line expressions) and their properties. It is NOT a full TMDL parser.
Stdlib only, so it runs on a bare GitHub Actions runner.

CLI (used by tools/setup/*.sh):
    python tools/tmdl.py set-measure <file> "<measure>" --expr "<dax>" [--prop key=value ...]
    python tools/tmdl.py add-measure <file> "<measure>" --expr "<dax>" [--prop key=value ...] [--after "<measure>"]
    python tools/tmdl.py remove-measure <file> "<measure>"
"""
from __future__ import annotations

import argparse
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

MEASURE_RE = re.compile(r"^\tmeasure\s+('(?:[^']|'')+'|[^\s=]+)\s*=\s*(.*)$")
OBJECT_RE = re.compile(r"^\t(measure|column|partition|hierarchy|calculationGroup)\b")
PROP_RE = re.compile(r"^\t\t([A-Za-z]+):\s*(.*)$")


def _unquote(name: str) -> str:
    if name.startswith("'") and name.endswith("'"):
        return name[1:-1].replace("''", "'")
    return name


def _quote(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return "'" + name.replace("'", "''") + "'"


@dataclass
class Measure:
    name: str
    expression: str
    properties: dict[str, str] = field(default_factory=dict)
    start: int = 0       # line index of the "measure" line
    prop_start: int = 0  # first property line (end of the expression)
    prop_end: int = 0    # end of the property lines (exclusive)
    end: int = 0         # end of the whole object incl. changedProperty/annotation blocks (exclusive)


def read_lines(path: Path) -> list[str]:
    # Accept files exactly as Power BI Desktop saves them on Windows.
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").split("\n")


def _write(path: Path, lines: list[str]) -> None:
    """Write back with the file's original line endings and BOM, so a one-line
    change stays a one-line diff."""
    raw = path.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    data = eol.join(lines).encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)


def parse_measures(lines: list[str]) -> list[Measure]:
    measures: list[Measure] = []
    i = 0
    while i < len(lines):
        m = MEASURE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        name, first = _unquote(m.group(1)), m.group(2).strip()
        start = i
        i += 1
        expr_lines = [first] if first else []
        props: dict[str, str] = {}
        # Multi-line expression: deeper-indented lines before the first property.
        while i < len(lines) and lines[i].startswith("\t\t") and not PROP_RE.match(lines[i]):
            expr_lines.append(lines[i].strip())
            i += 1
        prop_start = i
        while i < len(lines) and lines[i].startswith("\t\t"):
            pm = PROP_RE.match(lines[i])
            if pm:
                props[pm.group(1)] = pm.group(2).strip()
            i += 1
        prop_end = i
        # Desktop writes blocks like "changedProperty = ..." / "annotation ..." after a
        # blank line, still indented under the measure. They belong to it.
        j = i
        while j < len(lines):
            k = j
            while k < len(lines) and lines[k].strip() == "":
                k += 1
            if k < len(lines) and k > j and lines[k].startswith("\t\t"):
                j = k
                while j < len(lines) and lines[j].startswith("\t\t"):
                    j += 1
            else:
                break
        end = j
        expr = " ".join(x for x in expr_lines if x and x != "```")
        measures.append(Measure(name, expr, props, start, prop_start, prop_end, end))
    return measures


def get_measure(path: Path, name: str) -> Measure | None:
    for m in parse_measures(read_lines(path)):
        if m.name == name:
            return m
    return None


def normalise_dax(expr: str) -> str:
    """Whitespace- and case-insensitive comparison form for DAX expressions."""
    return re.sub(r"\s+", "", expr).lower()


def _render(name: str, expr: str, props: dict[str, str]) -> list[str]:
    out = [f"\tmeasure {_quote(name)} = {expr}"]
    for k, v in props.items():
        out.append(f"\t\t{k}: {v}")
    return out


def set_measure(path: Path, name: str, expr: str | None, props: dict[str, str]) -> None:
    """Change a measure in place, touching only the lines that change."""
    lines = read_lines(path)
    m = next((x for x in parse_measures(lines) if x.name == name), None)
    if m is None:
        sys.exit(f"measure {name!r} not found in {path}")
    prop_lines = lines[m.prop_start:m.prop_end]
    for k, v in props.items():
        for idx, line in enumerate(prop_lines):
            pm = PROP_RE.match(line)
            if pm and pm.group(1) == k:
                prop_lines[idx] = f"\t\t{k}: {v}"
                break
        else:
            # new property: put it before lineageTag, like Desktop does
            pos = next((idx for idx, l in enumerate(prop_lines) if l.startswith("\t\tlineageTag:")), len(prop_lines))
            prop_lines.insert(pos, f"\t\t{k}: {v}")
    head = [f"\tmeasure {_quote(name)} = {expr}"] if expr else lines[m.start:m.prop_start]
    lines[m.start:m.prop_end] = head + prop_lines
    _write(path, lines)


def add_measure(path: Path, name: str, expr: str, props: dict[str, str], after: str | None = None) -> None:
    lines = read_lines(path)
    measures = parse_measures(lines)
    props.setdefault("lineageTag", str(uuid.uuid4()))
    block = _render(name, expr, props) + [""]
    anchor = next((m for m in measures if m.name == after), None) if after else (measures[-1] if measures else None)
    if after and anchor is None:
        sys.exit(f"measure {after!r} not found in {path}")
    if anchor:
        insert_at = anchor.end
    else:
        # no measures yet: after the table's own properties (first blank line)
        insert_at = next(i for i, l in enumerate(lines) if i > 0 and l.strip() == "")
    if insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1
    lines[insert_at:insert_at] = block
    _write(path, lines)


def remove_measure(path: Path, name: str) -> None:
    lines = read_lines(path)
    for m in parse_measures(lines):
        if m.name == name:
            end = m.end + 1 if m.end < len(lines) and lines[m.end].strip() == "" else m.end
            del lines[m.start:end]
            _write(path, lines)
            return
    sys.exit(f"measure {name!r} not found in {path}")


def _main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["set-measure", "add-measure", "remove-measure"])
    ap.add_argument("file", type=Path)
    ap.add_argument("measure")
    ap.add_argument("--expr")
    ap.add_argument("--prop", action="append", default=[])
    ap.add_argument("--after", help="add-measure: insert after this measure (default: after the last one)")
    a = ap.parse_args()
    props = dict(p.split("=", 1) for p in a.prop)
    if a.cmd == "set-measure":
        set_measure(a.file, a.measure, a.expr, props)
    elif a.cmd == "add-measure":
        if not a.expr:
            sys.exit("--expr is required for add-measure")
        add_measure(a.file, a.measure, a.expr, props, a.after)
    else:
        remove_measure(a.file, a.measure)


if __name__ == "__main__":
    _main()
