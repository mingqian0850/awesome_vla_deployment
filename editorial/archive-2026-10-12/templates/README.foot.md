---

## Contributing

The most valuable contribution is **a failure you actually hit and how you fixed it** —
citations are cheap. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
# add an entry to data/*.yaml, then:
python scripts/build_readme.py    # regenerate this README
python scripts/check_links.py     # verify every URL resolves
```

`README.md` is generated. CI re-runs the generator and fails if the committed README differs,
so the README can never drift from the data. Do not edit it by hand.

Entry format and the provenance rules: [SCHEMA.md](SCHEMA.md).

## Related

- **[VLA-Handbook](https://github.com/sou350121/VLA-Handbook)** — the closest existing work,
  Chinese, 662★, updated daily. Strong on hardware specifics and ROS2/edge tuning. If you read
  Chinese, read it; this repo exists because there is no English equivalent.
- **[natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai)** — production
  patterns, ROS2 middleware, and the ISO/UL standards this repo maps onto VLA inference loops.
- **[AIDASLab](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation)** —
  paper-level data lifecycle: curation, cleaning, annotation, relabeling.

## License

MIT — see [LICENSE](LICENSE).
