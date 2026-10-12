# Entry schema

Every resource in `data/*.yaml` uses the same fields. `README.md` is **generated** from these
files by `scripts/build_readme.py` — never edit the README by hand.

```yaml
- id: lerobot-rtc                      # stable slug, unique across all files
  name: "LeRobot — Real-Time Chunking" # display name
  url: "https://github.com/huggingface/lerobot"
  type: repo                           # see Type values below
  what: "Async execution of action chunks; Sync vs RTC strategies."
  why: "Removes the stutter you get when you re-plan every control step."
  maturity: production                 # see Maturity values below
  verified: 2026-09                    # YYYY-MM, last time a human opened the link
  license: Apache-2.0
  tags: [latency, chunking, async]
  notes: "Optional. Gotchas, measured numbers, or a reason to distrust it."
  paper_title: "Optional. Exact published title. Declaring it enables a strict match"
               # against the arXiv API in scripts/check_papers.py.
  sources: ["Optional. Only if the entry summarises other work."]
```

## `type`

| value | meaning |
|---|---|
| `repo` | source code you can clone and run |
| `dataset` | a dataset |
| `paper` | paper / preprint |
| `tool` | a service, binary, or non-library product |
| `docs` | first-party documentation |
| `blog` | engineering write-up, post-mortem, case study |
| `video` | talk or recorded walkthrough |
| `discussion` | GitHub issue, forum thread, Discord distillation |
| `standard` | ISO/IEC/UL/ANSI standard or regulatory text |
| `list` | another curated list |
| `benchmark` | a measurement someone actually ran |
| `gap` | **a measurement nobody has published.** Deliberate: writing down that a number does not exist beats inventing one. Points at an issue the reader can fill in |

## `maturity`

This field is the point of the whole repo. Most lists conflate "a paper exists" with
"you can deploy this".

| value | meaning |
|---|---|
| `production` | someone runs it on real hardware; actively maintained |
| `research` | works in a lab; expect to adapt it |
| `toy` | demo-grade only; do not plan around it |
| `abandoned` | no commits for ~12 months. **Kept and dated, not silently dropped** |

## Provenance policy

1. **Every URL is machine-checked.** `scripts/check_links.py` runs in CI on every push and
   weekly on a schedule. A dead link fails the build.
   The checker is deliberately **not naive**: it retries transient failures, falls back to the
   Hugging Face API when HF HTML pages rate-limit in bulk, and honours a reviewed allowlist at
   `data/link-exceptions.yaml`. A checker that treats every non-200 as dead will prune valid
   resources — we confirmed seven distinct classes of genuinely-live URL that fail an automated
   sweep (bot-blocked, gated, HTTP-only, IPv6-only, rate-limited, transient, paywalled).
   **Never delete a resource to satisfy the checker; add an exception with a reason instead.**
2. **No fabricated references.** Every `paper` entry must resolve to a real arXiv/DOI/venue
   page. Placeholder or unresolvable IDs are treated as a bug.
   (This is not hypothetical: a 433-star "deployment" list in this space contains 27
   fabricated arXiv IDs — see the warning in the README.)
   **Verify paper identity against the arXiv API, never against a search-result snippet.** A
   snippet can attach arbitrary text to an ID, and a checker that only confirms HTTP 200 will
   cheerfully publish a mislabelled paper. `scripts/check_papers.py` enforces this: it resolves
   every arXiv ID and compares the real title against the entry. Declare `paper_title` on an
   entry to opt into a strict match; descriptive entry names are otherwise allowed and only
   warned about.
3. **Numbers are attributed.** Any latency / VRAM / success-rate figure must name the
   hardware and the model. "Faster" without a number is not accepted.
   **Grep the stem, then read the constructor.** When a flag name and its field name differ by
   a character, a one-character grep error produces a plausible, publishable, wrong fact. We
   hit this with `use_quantiles` versus `use_quantile`: the field is `use_quantile_norm`, and
   the dataclass default is `False`, but line 187 of the same file derives it as
   `model_type != ModelType.PI0` — so the default never survives construction. Grepping the
   wrong string inverts the diagnosis of a documented production bug, and nothing about the
   wrong answer looks wrong.
   **Check the state of the thing you are citing as the fix.** A merged PR, a closed unmerged
   PR, and an open issue are three different claims. We listed a closed-unmerged PR as the
   resolution of the quantile-aggregation bug; the change that actually landed is a mitigation,
   and the issue remains open. Read the state badge, not just the diff.
4. **Negative results are wanted.** "We tried INT8 on model X and the policy broke" is more
   valuable than another citation. Put it in `notes`.
5. **`verified` is a claim.** Bump it only when you actually opened the link.

## Adding an entry

```bash
$EDITOR data/deployment.yaml     # add your entry
python scripts/build_readme.py   # regenerate README.md
python scripts/check_links.py    # verify URLs
git commit -am "add: <thing>"
```

CI re-runs both. If `README.md` differs from the generated output, the build fails — this is
deliberate, so the README can never drift from the data.
