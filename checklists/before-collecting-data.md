# Checklist: before collecting data

Most datasets are expensive to collect and hard to fix afterwards. These are the decisions
that are cheap now and expensive later.

## Design

- [ ] **Instruction granularity decided.** One instruction per episode, or one per sub-task?
      For anything chained, per-sub-task — otherwise the policy cannot tell which phase it is
      in, and it will execute the first motion and stall
      ([why](../README.md#troubleshooting--symptom-to-root-cause-to-fix)).
- [ ] **Object and pose randomisation plan written down.** State coverage is driven by the
      number of *distinct trajectories*, not the number of frames.
- [ ] **Target count per sub-task set**, in trajectories — 30–50 independent demonstrations per
      sub-task is a common floor, not frames.
- [ ] **Reset strategy defined.** Who resets what, to which state, and is that state recorded?
- [ ] **Success criterion defined** before recording, so failed episodes are labelled rather
      than silently mixed in.

## Recording hygiene

- [ ] **Recording starts after motion begins.** Otherwise every episode contributes a stretch
      of near-zero actions at the reset state, and the policy learns to hesitate at exactly the
      state where every rollout starts.
- [ ] **Recording stops before the operator releases.** Same problem at the tail.
- [ ] **Calibration performed and logged** immediately before the session. Record the
      calibration file hash alongside the data — a policy trained on miscalibrated data cannot
      be distinguished from a bad policy.
- [ ] **Frame rate is fixed and matches the intended deployment control rate.** A chunk horizon
      is defined in frames; a frequency mismatch silently changes its physical duration.
- [ ] **Exposure locked.** Auto-exposure varies frame timing by tens of milliseconds.
- [ ] **Camera poses recorded** (or at least photographed and documented). Reproducing the
      viewpoint later is otherwise guesswork.

## Per-session log

Keep this alongside the data. It is the difference between "our dataset is 200 episodes" and a
dataset you can reason about.

| field | why |
|---|---|
| date, operator | operator quality is a real variable in the data |
| task / sub-task | needed for per-phase sampling and for labelling |
| object identities + poses | randomisation coverage and failure clustering |
| camera + calibration hash | reproducibility |
| lighting conditions | a common source of unexplained variance |
| anomalies | "the gripper slipped on 6 episodes" |
| outcome per episode | success / failure / operator intervention |

A `templates/collection-log.csv` is provided.

## Before you scale up

- [ ] **Train on the first ~20% and evaluate.** Finding out that your camera was out of focus,
      or that your task is ambiguous, after collecting 500 episodes is the most expensive
      mistake in this document.
- [ ] **Run the dataset diagnostic** on the pilot data:
      `python scripts/diag_dataset.py <dataset>`. It reports dead state dimensions, idle
      episode heads, chunk-target padding, action convention, and — most importantly — phase
      aliasing, which is the thing you cannot fix later by reweighting.
