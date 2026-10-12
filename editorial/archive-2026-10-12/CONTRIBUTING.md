# Contributing

The most useful contribution is **a failure you actually hit and how you fixed it.**
Citations are cheap; that is not.

## The three things worth adding

1. **A troubleshooting entry** (`data/failure-modes.yaml`). Format: symptom → candidate root
   causes ranked by how often they turn out to be the answer → a one-step test that
   distinguishes them → the fix. If you hit something and burned a day on it, that day is
   worth more to the next person than any paper.
2. **A measured number.** Which model, which hardware, what latency/VRAM/success-rate, and
   what you changed. Negative results especially — "quantising this model broke the policy"
   is a real finding.
3. **A resource** (`data/*.yaml`) that a practitioner would use but search engines bury.
   Chinese-language write-ups, engineering blog posts, and GitHub issue threads are
   systematically under-indexed and disproportionately valuable.

## Rules

- **One entry, one PR** is easiest to review but not required.
- **Do not hand-edit `README.md`.** It is generated. Edit `data/*.yaml` and run
  `python scripts/build_readme.py`.
- **Every URL must resolve.** Run `python scripts/check_links.py` before pushing. CI enforces
  it. A PR with a dead link will not merge.
- **Do not invent references.** No placeholder IDs, no "arXiv:XXXX.XXXXX", no paper titles you
  have not opened. This repo exists partly because a popular list in this space fabricated 27
  arXiv IDs; that failure mode is the one thing we will not tolerate.
- **Mark maturity honestly.** If you have only run it in sim, it is `research`, not
  `production`. If nobody has touched it in a year, mark it `abandoned` and keep it — the
  graveyard is information.
- **Opinions are welcome and must be labelled.** Put them in a doc under `docs/` and start the
  section with `> **Opinion.**`. Say what would change your mind.

## What we deliberately do not cover

To avoid duplicating work that already exists:

- Model architecture tutorials and paper summaries → [VLA-Handbook], [Awesome-VLA].
- Beginner "what is embodied AI" curricula → [every-embodied], [Xbotics Handbook].
- Paper-level curation of data cleaning/annotation → [AIDASLab's list], [Awesome-Robot-Data-Engine].

Link to those instead. We cover **how to make it run on a real robot**.

## Review

A maintainer checks three things: does the link resolve, is the `maturity` honest, and would
this have saved someone a day. That is the whole bar.

[VLA-Handbook]: https://github.com/sou350121/VLA-Handbook
[Awesome-VLA]: https://github.com/yueen-ma/Awesome-VLA
[every-embodied]: https://github.com/datawhalechina/every-embodied
[Xbotics Handbook]: https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook
[AIDASLab's list]: https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation
[Awesome-Robot-Data-Engine]: https://github.com/chang-xinhai/Awesome-Robot-Data-Engine
