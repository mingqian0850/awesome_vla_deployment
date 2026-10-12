# Before deployment

[Home](../README.en.md) · [中文](zh/before-deploying.md)

## Configuration and interfaces

- [ ] The loaded checkpoint, adapters, processor statistics and effective configuration are identified.
- [ ] Joint order, units, action mode, control frequency and gripper convention match the controller.
- [ ] Camera names, viewpoint and calibration match the recorded configuration.
- [ ] Prediction horizon and execution depth are recorded separately.
- [ ] Offline commands have been inspected before enabling actuators.

## Protection and timing

- [ ] Hardware/controller protective functions and access procedures are verified for this setup.
- [ ] Position, velocity, acceleration and workspace limits match the hardware and task.
- [ ] An appropriate independent component detects lost heartbeat or policy failure.
- [ ] Stale observations, inference overrun and empty queues each have a validated response.
- [ ] Stop and restart conditions account for gravity, load, contact and unexpected motion.
- [ ] End-to-end delay, jitter and remaining command-buffer time are measured.
- [ ] Consecutive action chunks join without unvalidated discontinuities.
- [ ] Human takeover has explicit control ownership and has been rehearsed under controlled conditions.

## Evaluation and records

- [ ] Task success, trial count, initial conditions and uncertainty are reported.
- [ ] Wrong-target behavior, interventions and partial completion are logged separately.
- [ ] Logs capture timestamps, dispatched commands and guard events.
- [ ] Recovery behavior has preconditions and is tested for the actual task.
- [ ] Model weights, code, data and third-party asset licenses are checked separately.
- [ ] A versioned deployment manifest identifies all artifacts needed to reproduce the setup.

Use the [deployment manifest](../templates/deployment-manifest.yaml). Empty fields are intentional: fill them with measurements and validated configuration. Review [runtime protection](../docs/43-safety.md) and [timing](../docs/41-real-time-inference.md).
