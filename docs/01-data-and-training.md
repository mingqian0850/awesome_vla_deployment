# Data, action conventions and fine-tuning

[Home](../README.en.md) · [中文](zh/01-data-and-training.md)

To check whether your data can feed a trainer, see [formats and acceptance](dataset-format-decisions.md); for logging tools, see [training monitoring](training-monitoring.md).

## Define the task before recording

Write a task instruction, initial-state distribution and observable success condition. For example, “place the red block in the tray” needs a definition of which placements count, when the episode ends, and how unsuccessful attempts are labeled.

For a multi-stage task, inspect whether images and state distinguish the stages. If the same inputs require different actions, add supported history, phase labels or another progress signal. A global instruction can be sufficient when the policy already has enough state; per-subtask labels are not universally required.

## The data contract

| Field | Record explicitly |
| --- | --- |
| Cameras | Names, viewpoint, resolution, channel order and timestamp convention |
| State | Dimension order, units, frame and missing-value handling |
| Actions | Absolute/delta/velocity, joint or end-effector space, gripper polarity |
| Timing | Capture rate, control rate and observation-action alignment |
| Language | Episode instruction, optional subtask/event labels and boundaries |
| Episodes | Start/end, success/failure, operator intervention and reset state |
| Normalization | Mode, statistics source, keys and checkpoint association |

Replay an episode before collecting a large batch. Check unintended idle spans, invalid frames, joint jumps and episode-tail padding. Include task variations and recovery states in the coverage record. Episode count, duration and diversity describe different aspects of the dataset.

Use [the collection checklist](../checklists/before-collecting-data.md) and [log template](../templates/collection-log.csv).

## A normalization example

With a recorded joint value `x = 0.6`, mean `mu = 0.2` and standard deviation `sigma = 0.1`, z-score normalization gives:

```text
z = (x - mu) / sigma = 4
x_reconstructed = z * sigma + mu = 0.6
```

This is illustrative arithmetic. A model can require mean/std, quantiles, identity mapping or different transforms for different features. Check the constructed processor and the loaded statistics.

Test both the expected forward value and the inverse round trip. A round trip alone passes even when normalization and its inverse both silently return their input. For quantiles, averaging per-dataset quantiles does not produce the quantiles of the pooled dataset.

Statistics can come from a compatible pretrained embodiment or from the training data. Record the choice and evaluate it; do not silently replace checkpoint statistics. Sources: [openpi normalization](resources.md#openpi-norm-stats), [normalization diagnostics](troubleshooting.md#normalization-silently-skipped).

## Run one controlled training experiment

1. Pin model, code revision and dependencies. Read the matching configuration and action adapter.
2. Split evaluation episodes or conditions from training data. Avoid splitting adjacent frames from one episode across both sets.
3. Inspect the resolved configuration and loaded weights before training.
4. Record trainable parameter names/counts, batch size, precision, learning rate and step budget. For LoRA, record target modules as well as rank.
5. Train a pilot dataset and save weights, processor statistics and configuration together.
6. Evaluate multiple checkpoints using the same task protocol. Report both offline prediction error and closed-loop outcomes when available.

A decreasing loss shows better fit to a training objective. It does not establish correct instruction following, stable closed-loop control or generalization to a new camera position.

## Read an experiment result

| Observation | Next measurement |
| --- | --- |
| Loss is low, rollout fails | Inspect action semantics, effective configuration and visited failure states |
| Offline predictions are almost constant | Compare different observations and sampling seeds |
| Grasp pose is correct, gripper never closes | Check adapter polarity and output units |
| New objects cause failures | Separate object coverage, visual shift and instruction-following tests |
| Memory fails only during saving | Measure checkpoint-saving peak memory separately |

**Completion check:** another person can reconstruct the input/output contract, load the same artifacts and run the same evaluation from your record.

Next: [real-time inference](41-real-time-inference.md). More examples: [fine-tuning resources](resources.md#training-recipes).
