# Real-time inference: timing and action queues

[Home](../README.en.md) · [中文](zh/41-real-time-inference.md)

Choose for your conditions first: [robot pauses and inference choices](deployment-decisions.md). This page explains the timing mechanisms.

## Three measurements

| Metric | Start → end |
| --- | --- |
| Time to first responsive action | A new event is observed → dispatch of an action that can reflect it |
| Observation-to-command latency | Sensor capture → preprocessing, inference, decoding and command delivery |
| Chunk-boundary stall | The previous action buffer empties → a usable new command arrives |

A loop can have no visible stalls while acting on old observations. Record all three when the task needs timely reactions.

## Define the timing model

Let `f_c` be controller frequency, `T_c = 1/f_c` its period, `H` the predicted steps and `s <= H` the steps executed from a plan. Let `L` be the measured duration from the observation's capture to its first command becoming available. Specify whether `L` includes transfer, queueing and actuator-interface delay.

```text
Prediction duration:    H * T_c
Executed duration:      s * T_c
Observation age at k:   L + k * T_c
```

The age equation assumes evenly spaced commands from one observation, indexed from `k = 0`. Additional queueing or transport must be included. It is not a stability guarantee.

## Synchronous and overlapping execution

**Serial synchronous execution** runs inference, executes a chunk, then starts the next inference. It incurs an inference pause between chunks unless a controller explicitly supplies another behavior. Merely having `L < H*T_c` does not remove that pause.

**Overlapping execution** starts a new inference while valid commands remain in the buffer. If `B` seconds of executable commands remain at launch, a necessary no-starvation condition for that refill is:

```text
refill latency + scheduling/transport jitter < B
```

This is a buffer condition, not sufficient proof of long-run stability, smoothness or safe motion. The scheduler, replacement policy and timestamps also matter. Repeated slow inference can still exhaust the buffer.

**RTC** additionally conditions the new action chunk on committed actions to improve joining. An asynchronous worker alone does not provide that conditioning. Guided and trained RTC have different checkpoint and configuration requirements; see [LeRobot RTC modes](resources.md#lerobot-rtc-modes).

**Temporal ensembling** blends predictions for overlapping timesteps. It may reduce discontinuities, but can also average incompatible paths or increase compute demand. Evaluate it under the measured delay distribution.

## Worked example

Illustrative values: `f_c = 50 Hz`, `T_c = 20 ms`, `H = 10`, `s = 5`, `L = 76 ms`.

- The predicted chunk spans 200 ms; the five executed steps span 100 ms.
- Action `k = 4` uses an observation at least `76 + 4*20 = 156 ms` old.
- If a refill begins with 100 ms of valid commands remaining, a 76 ms refill leaves 24 ms for additional jitter. If the measured refill takes 120 ms, that buffer is insufficient.
- A serial implementation still pauses for inference between chunks.

Increasing `H` can extend the available plan, but executing further into it also increases observation age. Tune `H` and `s` separately under task evaluation. Do not copy an example horizon as a hardware requirement.

## Instrument one rollout

Log capture time, observation assembly, inference start/end, queue insertion/replacement, and command dispatch/receipt. Use one clock domain or record synchronization uncertainty.

Report warm-up separately from steady state, latency p50/p95/p99 with sample count, buffer starvation count and oldest executed observation age. Record the effective controller rate as well as inference rate.

On timeout or stale input, invoke a response validated for the robot and task. Continuing the last velocity forever, freezing a torque command, opening a loaded gripper and cutting power can each introduce different hazards; use the controller's documented response instead of a universal fallback.

**Exercise:** draw a 500 ms timeline showing observations, inference intervals and consumed commands. Mark which actions remain changeable when a new event occurs.

References: [RTC](resources.md#rtc), [LeRobot asynchronous inference](resources.md#lerobot-async), [latency measurements](resources.md#benchmarks). Continue with [optimization and evaluation](40-optimization-matrix.md).
