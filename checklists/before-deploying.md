# Checklist: before a policy drives anything

Short version of [docs/43-safety.md](../docs/43-safety.md). Print it. Tick it in front of the
robot, not at your desk.

## Independence — the one that matters most

- [ ] The **safety limiter runs in a different process** from the policy
- [ ] **Heartbeat loss stops motion.** Test it: `kill -9` the policy process mid-motion and
      watch what the robot does
- [ ] **E-stop is in the power path** and was tested under load
- [ ] If the GPU hangs, the robot stops — verify, do not assume

## Limits

- [ ] Position / velocity / acceleration limits derived from the **hardware spec or URDF**,
      not from dataset percentiles
- [ ] Workspace bound excludes the operator, fixtures and camera mounts
- [ ] Self-collision and table/fixture collision handled by the controller's own model
- [ ] The policy cannot change the control frame

## Time

- [ ] Stale-observation guard active, threshold derived from the control period
- [ ] Inference overrun has a defined behaviour (hold, not continue)
- [ ] Chunk starvation has a defined behaviour (decelerate to stop, not freeze)
- [ ] Latency measured end to end, **p99 not mean**
- [ ] Feasibility margin `D_c / L` computed and above your jitter budget
      ([arithmetic](../docs/41-real-time-inference.md))
- [ ] **Execution horizon swept, not assumed.** The best-controlled public measurement
      (n=500 paired episodes per horizon, p<=0.005) peaks at an execution horizon of **10-15**
      and falls to **34% at a fully open-loop 50** — a halving of success. Do not execute the
      whole predicted chunk by default, and check the offline-selectability result if you would
      rather not spend robot time finding the number

## Observability

- [ ] Clip rate and action-jump rate logged and alarmed
- [ ] Observation novelty monitored
- [ ] Every cycle logs: observation timestamp, inference start/end, command sent
- [ ] A failed rollout can be reconstructed from the logs afterwards

## Recovery

- [ ] Scripted (non-learned) recovery primitives exist: open gripper, retreat, go home
- [ ] Human takeover arbitration is explicit, and was rehearsed
- [ ] Someone has stood next to the robot and watched a **deliberate** policy failure

## Reproducibility

- [ ] Checkpoint, calibration file, config and code revision are bound together in one
      manifest — `templates/deployment-manifest.yaml`
- [ ] You know which robot and which camera pose this checkpoint was trained for
- [ ] You can answer "what changed since the version that worked last month"
