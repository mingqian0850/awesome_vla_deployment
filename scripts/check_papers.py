#!/usr/bin/env python3
"""
Verify that arXiv references are the papers we say they are.

WHY THIS EXISTS
---------------
`check_links.py` proves a URL resolves. It cannot prove the URL points at the paper the entry
claims. That gap is real and was hit while assembling this list: a search-result snippet
attached an unrelated phrase to an arXiv ID, and the attribution was only settled by querying
the arXiv API directly. **A link checker that only confirms HTTP 200 will happily publish a
mislabelled paper** — which is a provenance failure of exactly the kind this repo exists to
avoid, and worse than a dead link because it looks correct.

WHAT IT CHECKS
--------------
  * every arXiv ID in data/ resolves to a real record
  * if an entry declares `paper_title`, it must match the real title (hard failure)
  * otherwise the entry `name` is compared against the real title and low overlap is reported
    as a warning, with both titles printed so a human can judge

Descriptive entry names are fine and expected ("Full FT vs LoRA vs frozen, with numbers" for
the OpenVLA paper). That is why low overlap is a warning, not a failure. Declaring
`paper_title` is how an entry opts into the strict check.

    python scripts/check_papers.py                # verify; fail on title mismatch / bad ID
    python scripts/check_papers.py --allow-fail   # always exit 0
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
API = "http://export.arxiv.org/api/query?id_list={ids}&max_results={n}"
NS = {"a": "http://www.w3.org/2005/Atom"}

STOP = {
    "a", "an", "the", "of", "for", "and", "or", "to", "in", "on", "with", "via", "from",
    "towards", "toward", "using", "is", "are", "as", "at", "by", "into", "without", "their",
}


def normalize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {w for w in words if w not in STOP and len(w) > 2}


def arxiv_id(url: str) -> str | None:
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z-]+/\d{7})", url)
    return m.group(1) if m else None


def collect() -> dict[str, list[dict]]:
    """arxiv id -> list of {name, paper_title, ident, file}."""
    found: dict[str, list[dict]] = {}

    def add(url, name, paper_title, ident, fname):
        aid = arxiv_id(url or "")
        if aid:
            found.setdefault(aid, []).append(
                {"name": name, "paper_title": paper_title, "id": ident, "file": fname}
            )

    for path in sorted(glob.glob(os.path.join(DATA, "*.yaml"))):
        fname = os.path.basename(path)
        if fname == "link-exceptions.yaml":
            continue
        doc = yaml.safe_load(open(path, encoding="utf-8")) or {}
        for e in doc.get("entries", []) or []:
            add(e.get("url"), e.get("name", ""), e.get("paper_title"), e.get("id", "?"), fname)
            for u in e.get("sources", []) or []:
                add(u, e.get("name", ""), e.get("paper_title"), e.get("id", "?"), fname)
        for s in doc.get("symptoms", []) or []:
            for u in s.get("sources", []) or []:
                add(u, s.get("symptom", ""), None, s.get("id", "?"), fname)
            for c in s.get("causes", []) or []:
                for u in c.get("sources", []) or []:
                    add(u, c.get("cause", ""), None, s.get("id", "?"), fname)
    return found


def fetch_titles(ids: list[str], batch: int = 20) -> dict[str, str]:
    """Real titles from the arXiv API. Batched, because one request per ID is rude."""
    out: dict[str, str] = {}
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        url = API.format(ids=",".join(chunk), n=len(chunk))
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                root = ET.fromstring(r.read())
        except Exception as exc:                                # noqa: BLE001
            print(f"  warning: arXiv API batch failed ({exc}); retrying individually",
                  file=sys.stderr)
            root = None
        if root is None:
            for one in chunk:
                try:
                    with urllib.request.urlopen(API.format(ids=one, n=1), timeout=45) as r:
                        for entry in ET.fromstring(r.read()).findall("a:entry", NS):
                            t = entry.find("a:title", NS)
                            if t is not None and t.text:
                                out[one] = " ".join(t.text.split())
                except Exception:                               # noqa: BLE001
                    pass
            continue
        for entry in root.findall("a:entry", NS):
            idel = entry.find("a:id", NS)
            tit = entry.find("a:title", NS)
            if idel is None or tit is None or not idel.text:
                continue
            aid = arxiv_id(idel.text) or idel.text.rsplit("/", 1)[-1]
            out[aid] = " ".join((tit.text or "").split())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-fail", action="store_true")
    ap.add_argument("--min-overlap", type=float, default=0.20,
                    help="token-overlap warning threshold for undeclared names")
    args = ap.parse_args()

    refs = collect()
    ids = sorted(refs)
    if not ids:
        print("no arXiv references found.")
        return 0

    print(f"resolving {len(ids)} unique arXiv IDs via the arXiv API...")
    titles = fetch_titles(ids)

    missing, mismatches, weak = [], [], []
    for aid in ids:
        real = titles.get(aid)
        if not real:
            missing.append(aid)
            continue
        for ref in refs[aid]:
            if ref["paper_title"]:
                if normalize(ref["paper_title"]) - normalize(real) or \
                   normalize(real) - normalize(ref["paper_title"]):
                    mismatches.append((aid, ref, real))
                continue
            claimed, actual = normalize(ref["name"]), normalize(real)
            if not claimed or not actual:
                continue
            overlap = len(claimed & actual) / max(len(claimed), 1)
            if overlap < args.min_overlap:
                weak.append((aid, ref, real, overlap))

    print(f"  {len(ids) - len(missing)} resolved, {len(missing)} unresolved")

    # Double-counting check. Listing the same work twice as two different rows inflates the
    # index and is a real error we made once: the robomimic "What Matters" study appeared in
    # two sections under two URLs. Sharing a source URL across entries is usually legitimate
    # (one README can support several distinct facts), so this reports for review rather
    # than failing.
    dup_ids = {aid: {r["id"] for r in rows} for aid, rows in refs.items()}
    dup_ids = {a: s for a, s in dup_ids.items() if len(s) > 1}
    seen_names: dict[str, list[str]] = {}
    for path in sorted(glob.glob(os.path.join(DATA, "*.yaml"))):
        if os.path.basename(path) == "link-exceptions.yaml":
            continue
        doc = yaml.safe_load(open(path, encoding="utf-8")) or {}
        for e in doc.get("entries", []) or []:
            seen_names.setdefault((e.get("name") or "").strip(), []).append(e.get("id", "?"))
    dup_names = {n: v for n, v in seen_names.items() if n and len(v) > 1}

    if dup_ids or dup_names:
        print("\nPOSSIBLE DOUBLE-COUNTING (review; one source can legitimately back "
              "several entries):")
        for aid, ident in sorted(dup_ids.items()):
            print(f"  arXiv {aid} is referenced by {len(ident)} entries: {', '.join(sorted(ident))}")
        for name, ident in sorted(dup_names.items()):
            print(f"  duplicate entry name {name!r}: {', '.join(ident)}")

    if missing:
        print("\nUNRESOLVED ARXIV IDS:", file=sys.stderr)
        for aid in missing:
            users = ", ".join({r["id"] for r in refs[aid]})
            print(f"  {aid}  referenced by: {users}", file=sys.stderr)

    if mismatches:
        print("\nDECLARED paper_title DOES NOT MATCH THE REAL TITLE:", file=sys.stderr)
        for aid, ref, real in mismatches:
            print(f"  [{aid}] {ref['id']} ({ref['file']})\n"
                  f"        claimed: {ref['paper_title']}\n"
                  f"        actual : {real}", file=sys.stderr)

    if weak:
        print(f"\nLOW NAME/Title overlap (warning, {len(weak)} — descriptive names are fine):")
        for aid, ref, real, ov in weak:
            print(f"  [{aid}] {ref['id']}  overlap={ov:.2f}\n"
                  f"        entry name : {ref['name'][:88]}\n"
                  f"        real title : {real[:88]}")

    if missing or mismatches:
        if not args.allow_fail:
            return 1
    print("\nall arXiv references resolve to real records."
          + (" Declared titles match." if not mismatches else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
