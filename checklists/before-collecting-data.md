# Before collecting data

[Home](../README.en.md) · [中文](zh/before-collecting-data.md)

## Task and coverage

- [ ] Task instruction, episode end and success/failure criteria are defined.
- [ ] Object, pose, lighting and initial-state variations are recorded in a coverage plan.
- [ ] Multi-stage tasks have enough observable state, history or supported phase labels to identify progress.
- [ ] Evaluation episodes or conditions are separated from training.
- [ ] Reset procedure and operator intervention labels are defined.

## Data contract

- [ ] The capture route is explicit: human video, tracked demonstration, handheld tool, robot teleoperation or simulation.
- [ ] Measurements, estimates, retargeted references, commands and feedback are distinct; unknown values are not zero.
- [ ] Process completion and product quality are separate; unsupported contact measurements remain unknown.

- [ ] State/action dimensions, joint ordering, units and coordinate frames are written down.
- [ ] Absolute/delta/velocity actions and gripper polarity are confirmed.
- [ ] Camera names, views, intrinsics, extrinsics and image format are recorded.
- [ ] Capture and control rates are recorded; resampling and synchronization are explicit.
- [ ] Calibration files and revisions are saved with the session.
- [ ] Normalization mode and statistics source are recorded; missing features fail clearly.

## Recording quality

- [ ] Inspect unintended idle spans at episode starts and ends.
- [ ] Check missing frames, timestamp jumps and observation/action alignment.
- [ ] Check image exposure, focus and viewpoint consistency.
- [ ] Label unsuccessful or interrupted episodes instead of mixing them silently.
- [ ] Replay demonstrations and verify task outcomes where the environment supports replay.
- [ ] Inspect tail padding and target masks across episode boundaries.

## Pilot before scaling

- [ ] Log episode count, duration, distinct conditions and outcome distribution.
- [ ] Train and evaluate a pilot dataset before collecting the full batch.
- [ ] Inspect per-dimension statistics and dead state channels.
- [ ] Check model, dataset and third-party asset license terms separately.

Use the [collection log](../templates/collection-log.csv). Optional diagnostic: `python scripts/diag_dataset.py /path/to/lerobot_dataset` (NumPy and PyArrow required). Continue with [data and training](../docs/01-data-and-training.md).
