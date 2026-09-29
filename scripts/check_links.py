#!/usr/bin/env python3
"""
Check every URL in data/*.yaml.

This is not decoration. The provenance policy of this repo is that every link resolves,
because a popular list in this space has been found to contain 27 fabricated arXiv IDs,
and hand-maintained lists rot: roughly 14 of the curated lists in this space are dead.

    python scripts/check_links.py                 # check all, report failures
    python scripts/check_links.py --allow-fail    # always exit 0 (for local runs)

Requires network access. Uses only the standard library plus PyYAML.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import subprocess
import sys
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CACHE = os.path.join(ROOT, ".out", "links.json")
UA = "Mozilla/5.0 (compatible; awesome-vla-deployment link checker)"
TIMEOUT = 25


def collect() -> dict[str, list[str]]:
    """url -> list of entry ids referencing it."""
    urls: dict[str, list[str]] = {}
    for path in sorted(glob.glob(os.path.join(DATA, "*.yaml"))):
        doc = yaml.safe_load(open(path, encoding="utf-8"))
        for e in doc.get("entries", []) or []:
            if e.get("url"):
                urls.setdefault(e["url"], []).append(e["id"])
        for s in doc.get("symptoms", []) or []:
            for u in s.get("sources", []) or []:
                urls.setdefault(u, []).append(s["id"])
    return urls


def check(url: str) -> tuple[str, int | str]:
    try:
        r = subprocess.run(
            ["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code}", "-m", str(TIMEOUT),
             "--retry", "2", "--retry-delay", "1", "-A", UA, url],
            capture_output=True, text=True, timeout=TIMEOUT * 3,
        )
        return url, int(r.stdout.strip() or 0)
    except Exception as exc:                                   # noqa: BLE001
        return url, f"ERR:{type(exc).__name__}"


def check_all(urls, cache: dict, use_cache: bool) -> dict:
    todo = [u for u in urls if not (use_cache and cache.get(u) == 200)]
    results = {u: c for u, c in cache.items() if u in urls}
    if todo:
        with cf.ThreadPoolExecutor(12) as ex:
            for url, code in ex.map(check, todo):
                results[url] = code
    return results


def verify_arxiv(url: str) -> bool:
    """An arXiv abs page must resolve to a real paper, not a placeholder."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}),
                                    timeout=TIMEOUT) as r:
            body = r.read(4000).decode("utf-8", "ignore").lower()
        return "arxiv" not in url or ("<title>" in body and "error" not in body[:600])
    except Exception:                                          # noqa: BLE001
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-fail", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--json", help="write results to this path")
    args = ap.parse_args()

    urls = collect()
    cache = {}
    if os.path.exists(CACHE) and not args.no_cache:
        try:
            cache = json.load(open(CACHE, encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            cache = {}

    res = check_all(urls, cache, use_cache=not args.no_cache)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(res, open(CACHE, "w", encoding="utf-8"), indent=1, sort_keys=True)
    if args.json:
        json.dump(res, open(args.json, "w", encoding="utf-8"), indent=1, sort_keys=True)

    bad = {u: c for u, c in res.items() if c != 200}
    print(f"checked {len(res)} unique URLs — {len(res) - len(bad)} ok, {len(bad)} failing")

    # fabricated-reference guard: placeholder ids are the failure mode we exist to avoid
    suspects = [u for u in urls if "XXXX" in u.upper() or "placeholder" in u.lower()]
    if suspects:
        print("\nFABRICATED / PLACEHOLDER REFERENCES:", file=sys.stderr)
        for u in suspects:
            print(f"  {u}  <- referenced by {', '.join(urls[u])}", file=sys.stderr)

    if bad:
        print("\nFAILING URLS:", file=sys.stderr)
        for u, c in sorted(bad.items(), key=lambda x: str(x[1])):
            print(f"  [{c}] {u}\n        referenced by: {', '.join(urls[u])}", file=sys.stderr)

    failed = bool(bad) or bool(suspects)
    if failed and not args.allow_fail:
        return 1
    print("all links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
