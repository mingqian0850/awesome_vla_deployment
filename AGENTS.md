# Repository maintenance instructions

- Maintain the Chinese default README and English README as equal learner entry points.
- Pair every learner guide/checklist with its counterpart; translate explanations, exercises, limitations and troubleshooting steps. Preserve original project names, paper titles and code identifiers when useful for lookup.
- Put selection rationale, source comparisons, publishing decisions and audit narratives in `editorial/`. Store concise reviewable summaries, not private reasoning traces.
- Do not link editorial records from learner READMEs, guides or checklists. The directory remains versioned and is not confidential storage.
- Keep technical prerequisites, failure modes, release limitations and relevant license caveats in learner content, in both languages.
- Edit `data/*.yaml` and templates for generated pages; run `python scripts/build_readme.py`.
- Validate with `build_readme.py --check`, `check_docs.py`, `test_build_readme.py`, `check_links.py` and `check_papers.py` under `scripts/` before publishing.
- Preserve archived source material and stable resource IDs. Record deliberate moves out of the learner catalog in the editorial migration record.
