<div align="center">

# awesome-vla-deployment

**How to make a VLA policy actually run on a real robot.**

Not another paper index. Data collection, annotation, cleaning and sub-task segmentation;
training recipes with numbers; and the deployment engineering — latency, chunking,
quantisation, edge hardware, safety layers — that decides whether any of it works outside
the lab.

{{TOTAL}} entries · {{MATURITY_LINE}}

</div>

---

> ### ⚠️ One list in this space should not be used
>
> [`keon/awesome-physical-ai`](https://github.com/keon/awesome-physical-ai) (433 stars) is the
> only curated list here with a literal `## Deployment` section, so search engines surface it
> first when you look for deployment material. **Its Deployment and Safety sections contain 27
> fabricated placeholder arXiv IDs** (`2505.XXXXX`, `2512.XXXXX`) attached to real-looking
> paper names. A `grep -c XXXXX` over the file returns 27; over 32 other READMEs in this space
> it returns 0. It last saw a commit in June 2026.
>
> It is listed in the [Landscape](#landscape--what-already-exists) section, dated and
> labelled, rather than quietly omitted — because you will find it, and you need to know.

## The problem this repo solves

If you are training a VLA model, the papers are not your bottleneck. Your bottleneck is that
the robot does the first motion of your chained task and then stops, that nobody has written
down which normalisation statistics broke the policy when you changed arms, and that the
only place your exact failure mode has ever been discussed is a Chinese blog post and a
closed GitHub issue.

So this repo is organised around **problems, not publications**. Every troubleshooting entry
is symptom → ranked candidate causes → a test you can run in under an hour → the fix. Where a
number appears, it names the hardware.

## What we do not do

To avoid duplicating work that already exists, we deliberately do not cover:

| Not here | Go here instead |
|---|---|
| Model architecture tutorials, paper summaries | [VLA-Handbook](https://github.com/sou350121/VLA-Handbook) (Chinese, 662★), [Awesome-VLA](https://github.com/yueen-ma/Awesome-VLA) |
| Beginner "what is embodied AI" curricula | [every-embodied](https://github.com/datawhalechina/every-embodied), [Xbotics Handbook](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook) (Chinese) |
| Paper-level curation of data cleaning / annotation | [AIDASLab](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation), [Awesome-Robot-Data-Engine](https://github.com/chang-xinhai/Awesome-Robot-Data-Engine) |
| Middleware and standards catalogues | [natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai) |

See the [Landscape](#landscape--what-already-exists) section for the full picture, including
which lists are dead.

## How to read the entries

Every entry carries a `maturity` that says how much you can trust it, and a `verified` date
that says when a human last opened the link.

| maturity | meaning |
|---|---|
| `production` | runs on real hardware, actively maintained |
| `research` | works in a lab, expect to adapt it |
| `toy` | demo-grade, do not plan around it |
| `abandoned` | no commits for ~12 months — **kept and dated on purpose**, because a graveyard is information |

## Provenance

1. Every URL is machine-checked. `scripts/check_links.py` runs on every push and weekly on a
   schedule; a dead link fails the build.
2. No fabricated references. Placeholder or unresolvable paper IDs are treated as a bug.
3. Numbers are attributed to named hardware and model. "Faster" without a number is rejected.
4. Negative results are wanted. "We tried INT8 and the policy broke" is a finding.
5. `verified` is a claim about a human having opened the link, not a timestamp bump.

## The written guides

The hand-written pages, where the parts that no link can give you live:

| Guide | What is in it |
|---|---|
| [The safety layer](docs/43-safety.md) | Why a learned policy cannot be a safety function, the six layers, and how ISO 12100 / 10218 / TS 15066 / 13849 map onto a VLA inference loop |
| [Real-time inference](docs/41-real-time-inference.md) | The latency budget arithmetic — feasibility condition, observation-age equation, and the three execution strategies |
| [The optimisation matrix](docs/40-optimization-matrix.md) | What to measure and how, so your numbers are comparable with someone else's |
| [Checklist: before collecting data](checklists/before-collecting-data.md) | The decisions that are cheap now and expensive later |
| [Checklist: before a policy drives anything](checklists/before-deploying.md) | Print it and tick it in front of the robot |

## Quick start

| You are... | Start at |
|---|---|
| about to collect your first dataset | [Data](#data--collection-annotation-cleaning-segmentation), then [Counter-evidence](#counter-evidence--what-did-not-work-and-what-stops-working) for how much data people actually needed |
| stuck: the policy does the first motion then stops | [Troubleshooting](#troubleshooting--symptom-to-root-cause-to-fix) |
| fine-tuning pi0.5 on your own arm | [Training](#training--frameworks-recipes-action-representations) and [Training recipes](#training-recipes--the-numbers) |
| deciding what hardware to buy | [Training recipes](#training-recipes--the-numbers) — the VRAM matrix is published |
| moving from a working demo to a real deployment | [Deployment](#deployment--inference-timing-optimisation-edge-integration) and [Real-time inference](docs/41-real-time-inference.md) |
| trying to get a number you can trust | [Evaluation](#evaluation) and [Optimisation matrix](docs/40-optimization-matrix.md) |
| looking for a number nobody has published | [Deployment benchmarks](#deployment-benchmarks--measured-not-cited) — documented gaps with reasons |
| about to conclude your data is the problem | [Counter-evidence](#counter-evidence--what-did-not-work-and-what-stops-working) — nine documented failures, including one where more data was explicitly not the fix |

---

