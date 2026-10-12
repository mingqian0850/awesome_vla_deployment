# Optimization and evaluation

[Home](../README.en.md) · [中文](zh/40-optimization-matrix.md)

## Establish a baseline

Run the original checkpoint and record task success, trial count, inference latency and memory. Keep the task, initial states, camera inputs, control frequency and action semantics fixed when comparing a change.

| Measurement | Include |
| --- | --- |
| Latency | Timing boundary, p50/p95/p99, sample count |
| Task outcome | Success criterion, successes/trials, uncertainty interval |
| Memory | Peak use during initialization, steady state and saving where relevant |
| Configuration | Model/code revision, dtype, batch size, image shape, camera count, horizons and denoising steps |
| Device | GPU model, power mode, temperature and driver/runtime versions |
| Failures | Missed grasps, stalls, wrong targets, guard interventions and other task-specific categories |

Separate cold initialization, first inference and warmed-up inference. Report preprocessing and end-to-end observation-to-command time in addition to model-only time.

## Change one factor

Examples include compilation, CUDA graphs, precision, image processing, denoising steps or execution depth. For each change:

1. Reuse the reference inputs and compare the action outputs.
2. Record latency and memory under the same timing boundary.
3. Run matched task trials, interleaving conditions to reduce drift.
4. Inspect failure types and action continuity, not only average success.

For stochastic policies, control sampling where possible and characterize repeated-run variation. A speedup and preserved offline action similarity do not by themselves establish preserved closed-loop performance.

## Export and quantization

An exported graph may run, run with changed outputs, or fail on an operator, dynamic shape or control-flow construct. Keep the error and configuration in the experiment record.

For a fixed observation batch, compare per-dimension absolute action errors and relevant task tolerances. Inspect the action head and inverse normalization. Cosine similarity alone can conceal an important magnitude or small-motion error.

Low-bit weights do not guarantee lower latency at batch size 1. Operator coverage, conversion overhead and memory traffic matter; [embodied-efficiency](resources.md#embodied-efficiency) records one negative result.

## Read a success rate

`9/10` and `90/100` both equal 90%, but have different uncertainty. Report the numerator, denominator, initial-state protocol and an interval method. For correlated episodes, repeated robot resets or multiple tasks, state the unit treated as independent.

Distinguish overall completion from subtask completion, instruction following and intervention rate. Run a paired instruction test: keep the scene fixed and change the requested visible target. This measures behavior hidden by a single nominal task instruction.

## Experiment worksheet

| Field | Baseline | Modified |
| --- | --- | --- |
| Checkpoint + revision | | |
| Task + initial states | | |
| Single changed factor | Reference | |
| Timing boundary | | |
| Warm-up / measured samples | | |
| Latency p50 / p95 / p99 | | |
| Peak memory | | |
| Successes / trials + interval | | |
| Interventions / failure types | | |
| Action deviation | | |

**Completion check:** someone can tell whether the change improved speed, memory, task performance or only one of these.

References: [measurement resources](resources.md#benchmarks), [evaluation protocols](resources.md#evaluation), [reported failure cases](resources.md#counter-evidence).
