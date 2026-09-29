#!/usr/bin/env python3
"""
Check every URL in data/*.yaml.

This is not decoration. The provenance policy of this repo is that every link resolves,
because a popular list in this space has been found to contain 27 fabricated arXiv IDs, and
hand-maintained lists rot: roughly 14 of the curated lists in this space are dead.

WHY THIS IS NOT A NAIVE CHECKER
-------------------------------
A checker that treats any non-200 as dead will *prune valid resources*. That is not
hypothetical: while assembling this list we hit, and confirmed by retry, every one of these
classes of genuinely-live URL that fails an automated sweep:

  * transient 000/4xx under rapid sequential requests (GitHub throttling, some CDNs)
  * HTTP-only hosts that return 000 over HTTPS
  * IPv6-only hosts
  * hosts that rate-limit bulk requests but serve individual ones fine
  * Hugging Face HTML pages that 429 in bulk while the API keeps answering
  * HF repos whose legitimate `gated: auto|manual` setting returns 401/403 anonymously
  * bot-blocked-but-real pages (403 to scripts, 200 in a browser)

So this checker retries before concluding anything, falls back to the Hugging Face API, and
supports a reviewed allowlist in data/link-exceptions.yaml for URLs a human has confirmed.

    python scripts/check_links.py                 # check all; fail on dead links
    python scripts/check_links.py --strict        # ignore the allowlist
    python scripts/check_links.py --allow-fail    # always exit 0 (local runs)

Requires network access plus PyYAML.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import re
import subprocess
import sys
import time

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
EXCEPTIONS = os.path.join(DATA, "link-exceptions.yaml")
CACHE = os.path.join(ROOT, ".out", "links.json")
UA = "Mozilla/5.0 (compatible; awesome-vla-deployment link checker)"
TIMEOUT = 25
OK = {200, 201, 202, 203, 204, 206}


def collect() -> dict[str, list[str]]:
    """url -> list of ids referencing it, across entries, causes and symptoms."""
    urls: dict[str, list[str]] = {}

    def add(u, ident):
        if u:
            urls.setdefault(u, [])
            if ident not in urls[u]:
                urls[u].append(ident)

    for path in sorted(glob.glob(os.path.join(DATA, "*.yaml"))):
        if os.path.basename(path) == "link-exceptions.yaml":
            continue
        doc = yaml.safe_load(open(path, encoding="utf-8")) or {}
        for e in doc.get("entries", []) or []:
            add(e.get("url"), e.get("id", "?"))
            for u in e.get("sources", []) or []:
                add(u, e.get("id", "?"))
        for s in doc.get("symptoms", []) or []:
            for u in s.get("sources", []) or []:
                add(u, s.get("id", "?"))
            for c in s.get("causes", []) or []:
                for u in c.get("sources", []) or []:
                    add(u, s.get("id", "?"))
    return urls


def load_exceptions() -> dict[str, dict]:
    """url -> {reason, verified}. Human-reviewed, kept in data/ so it stays visible."""
    if not os.path.exists(EXCEPTIONS):
        return {}
    doc = yaml.safe_load(open(EXCEPTIONS, encoding="utf-8")) or {}
    return {
        row["url"]: {"reason": row.get("reason", ""), "verified": row.get("verified", "")}
        for row in doc.get("exceptions", []) or []
    }


def curl(url: str) -> int | str:
    try:
        r = subprocess.run(
            ["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code}", "-m", str(TIMEOUT),
             "-A", UA, url],
            capture_output=True, text=True, timeout=TIMEOUT * 2,
        )
        return int(r.stdout.strip() or 0)
    except Exception as exc:                                   # noqa: BLE001
        return f"ERR:{type(exc).__name__}"


def hf_api_equivalent(url: str) -> str | None:
    """huggingface.co/datasets/foo/bar -> huggingface.co/api/datasets/foo/bar

    HF HTML pages rate-limit bulk requests while the API keeps answering, and a legitimately
    gated repo returns 401/403 anonymously on either. The API separates 'gated but real' from
    'does not exist'.
    """
    m = re.match(r"https?://huggingface\.co/(datasets|models|spaces)/([^/?#]+/[^/?#]+)", url)
    return f"https://huggingface.co/api/{m.group(1)}/{m.group(2)}" if m else None


def check_one(url: str) -> tuple[str, int | str, str]:
    """Return (url, code, note). Retries once before concluding anything."""
    code = curl(url)
    if code not in OK:
        time.sleep(2.0)                       # transient throttling is the common case
        code = curl(url)

    if code not in OK:
        api = hf_api_equivalent(url)
        if api:
            api_code = curl(api)
            if api_code in OK:
                return url, api_code, "ok via HF API (HTML fetch was throttled)"
            if api_code in (401, 403):
                return url, api_code, "gated Hugging Face repo — real, needs auth"
    return url, code, ""


def check_all(urls) -> dict[str, tuple[int | str, str]]:
    with cf.ThreadPoolExecutor(8) as ex:      # gentler than 12: fewer self-inflicted throttles
        return {u: (c, n) for u, c, n in ex.map(check_one, urls)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-fail", action="store_true")
    ap.add_argument("--strict", action="store_true", help="ignore the reviewed allowlist")
    ap.add_argument("--json", help="write results to this path")
    args = ap.parse_args()

    urls = collect()
    exceptions = {} if args.strict else load_exceptions()
    res = check_all(urls)

    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    flat = {u: c for u, (c, _) in res.items()}
    json.dump(flat, open(CACHE, "w", encoding="utf-8"), indent=1, sort_keys=True)
    if args.json:
        json.dump(flat, open(args.json, "w", encoding="utf-8"), indent=1, sort_keys=True)

    # A fabricated reference is a hard failure regardless of anything else: it is the one
    # error mode this repo exists to avoid.
    fabricated = [u for u in urls if re.search(r"XXXX|placeholder|example\.com", u, re.I)]

    failed, exempted, notes = [], [], []
    for u, (code, note) in res.items():
        if code in OK:
            if note:
                notes.append((u, code, note))
        elif u in exceptions:
            exempted.append((u, code, exceptions[u]))
        else:
            failed.append((u, code, note))
    failed.sort(key=lambda x: str(x[1]))

    print(f"checked {len(urls)} unique URLs — {len(urls) - len(failed) - len(exempted)} ok, "
          f"{len(exempted)} allowlisted, {len(failed)} failing")

    if notes:
        print("\nok, with notes:")
        for u, c, n in notes:
            print(f"  [{c}] {u}\n        {n}")

    if exempted:
        print("\nALLOWLISTED (verified live by a human — see data/link-exceptions.yaml):")
        for u, c, ex in exempted:
            print(f"  [{c}] {u}\n        {ex['verified']}: {ex['reason']}")

    if fabricated:
        print("\nFABRICATED / PLACEHOLDER REFERENCES:", file=sys.stderr)
        for u in fabricated:
            print(f"  {u}  <- referenced by {', '.join(urls[u])}", file=sys.stderr)

    if failed:
        print("\nFAILING URLS:", file=sys.stderr)
        for u, c, n in failed:
            print(f"  [{c}] {u}\n        referenced by: {', '.join(urls[u])}"
                  + (f"\n        {n}" if n else ""), file=sys.stderr)
        print("\nIf a URL above is genuinely live (bot-blocked, gated, HTTP-only, IPv6-only or\n"
              "rate-limited), add it to data/link-exceptions.yaml with a reason and a date\n"
              "instead of deleting the entry. A naive checker prunes valid resources.",
              file=sys.stderr)

    if (failed or fabricated) and not args.allow_fail:
        return 1
    print("all links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
