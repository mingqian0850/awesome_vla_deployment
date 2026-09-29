#!/usr/bin/env python3
"""
Generate README.md from data/*.yaml.

The YAML files are the single source of truth. README.md is a build artifact: CI re-runs
this script and fails if the committed README differs, so the two can never drift.

    python scripts/build_readme.py            # write README.md
    python scripts/build_readme.py --check    # exit 1 if README.md is out of date
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
HEAD = os.path.join(ROOT, "templates", "README.head.md")
FOOT = os.path.join(ROOT, "templates", "README.foot.md")
OUT = os.path.join(ROOT, "README.md")

MATURITY = {
    "production": "production",
    "research": "research",
    "toy": "toy",
    "abandoned": "abandoned",
}
MATURITY_NOTE = {
    "production": "runs on real hardware, maintained",
    "research": "works in a lab, expect to adapt it",
    "toy": "demo-grade, do not plan around it",
    "abandoned": "no commits for ~12 months, kept and dated on purpose",
}


def load():
    docs = []
    for path in sorted(glob.glob(os.path.join(DATA, "*.yaml"))):
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        doc["_file"] = os.path.basename(path)
        docs.append(doc)
    docs.sort(key=lambda d: d.get("order", 999))
    return docs


def anchor(text: str) -> str:
    keep = [c.lower() if c.isalnum() or c == " " or c == "-" else "" for c in text]
    return "".join(keep).strip().replace(" ", "-")


def stats(docs):
    counts = {}
    total = 0
    for d in docs:
        for e in d.get("entries", []) or []:
            total += 1
            counts[e.get("maturity", "unknown")] = counts.get(e.get("maturity", "unknown"), 0) + 1
    return total, counts


def render_entry(e) -> list[str]:
    name = e["name"]
    url = e.get("url")
    title = f"[{name}]({url})" if url else name
    meta = [f"`{e.get('type', '?')}`", f"`{e.get('maturity', '?')}`"]
    if e.get("license"):
        meta.append(f"`{e['license']}`")
    if e.get("verified"):
        meta.append(f"verified {e['verified']}")
    if e.get("tags"):
        meta.append(" ".join(f"#{t}" for t in e["tags"]))
    lines = [f"- **{title}** — {' · '.join(meta)}"]
    if e.get("what"):
        lines.append(f"  - *What it is:* {e['what'].strip()}")
    if e.get("why"):
        lines.append(f"  - *Why it matters here:* {e['why'].strip()}")
    if e.get("notes"):
        lines.append(f"  - *Note:* {e['notes'].strip()}")
    return lines


def render_symptom(s) -> list[str]:
    badge = []
    if s.get("severity"):
        badge.append(f"severity: {s['severity']}")
    if s.get("frequency"):
        badge.append(f"frequency: {s['frequency']}")
    lines = [f"### {s['symptom']}", ""]
    if badge:
        lines += ["`" + "` · `".join(badge) + "`", ""]
    for i, c in enumerate(s.get("causes", []), start=1):
        rank = c.get("rank", i)
        lines.append(f"**Cause {rank} — {c['cause'].strip()}**")
        lines.append("")
        if c.get("test"):
            lines.append(f"- **Test:** {c['test'].strip()}")
        if c.get("fix"):
            lines.append(f"- **Fix:** {c['fix'].strip()}")
        lines.append("")
    if s.get("sources"):
        lines.append("Sources: " + " · ".join(f"<{u}>" for u in s["sources"]))
        lines.append("")
    return lines


def build(docs) -> str:
    total, counts = stats(docs)
    with open(HEAD, encoding="utf-8") as f:
        head = f.read()
    with open(FOOT, encoding="utf-8") as f:
        foot = f.read()

    head = head.replace("{{TOTAL}}", str(total))
    head = head.replace(
        "{{MATURITY_LINE}}",
        " · ".join(f"{counts.get(k, 0)} {k}" for k in ("production", "research", "toy", "abandoned")),
    )

    out = [head.rstrip(), ""]

    # contents
    out.append("## Contents")
    out.append("")
    for d in docs:
        out.append(f"- [{d['section']}](#{anchor(d['section'])})")
        if d.get("symptoms"):
            for s in d["symptoms"]:
                out.append(f"  - [{s['symptom'][:72]}](#{anchor(s['symptom'])})")
    out.append("")

    for d in docs:
        out.append(f"## {d['section']}")
        out.append("")
        if d.get("description"):
            out.append(" ".join(d["description"].split()))
            out.append("")
        for e in d.get("entries", []) or []:
            out += render_entry(e)
        if d.get("entries"):
            out.append("")
        if d.get("symptoms"):
            out.append(
                "Read the causes in order. They are ranked by how often they turn out to be "
                "the answer, not by how interesting they are."
            )
            out.append("")
            for s in d["symptoms"]:
                out += render_symptom(s)
        out.append("")

    out.append(foot.rstrip())
    out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if README.md is out of date")
    args = ap.parse_args()

    docs = load()
    text = build(docs)

    if args.check:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != text:
            print("README.md is out of date. Run: python scripts/build_readme.py", file=sys.stderr)
            return 1
        print("README.md is up to date.")
        return 0

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    total, counts = stats(docs)
    print(f"wrote README.md — {total} entries ({counts}) from {len(docs)} data files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
