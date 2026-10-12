# Troubleshooting

[Home](../README.en.md) · [中文](zh/troubleshooting.md)

Symptoms, checks and corrective actions. Check order is a diagnostic workflow, not a measured probability ranking.

- [Only the first subtask executes](#only-first-action)
- [The robot hesitates at rollout start](#stalls-at-start)
- [Motion alternates between bursts and pauses](#stutter-and-stop)
- [Later actions in a chunk are incorrect](#chunk-tail-garbage)
- [Instructions do not change behavior](#ignores-instruction)
- [A policy fails on a different robot](#fails-on-new-robot)
- [Simulation works but hardware does not](#sim-works-real-fails)
- [Success estimates vary between runs](#eval-numbers-not-trustworthy)
- [Configuration changes have no effect](#config-did-not-apply)
- [Normalization is skipped or incorrect](#normalization-silently-skipped)
- [Loss decreases but task success stays near zero](#fine-tune-zero-success)
- [Training produces NaNs or unexpected loss scales](#training-collapses-unexpectedly)

<a id="only-first-action"></a>
## Only the first subtask executes

### 1. The rollout loop consumes too few actions.

- **Check：** Log chunk shape and actual commands sent per inference.
- **Action：** Set execution depth explicitly and evaluate several depths.

### 2. The delta transform is applied twice.

- **Check：** Check dataset action semantics and the transform chain against reconstructed joint targets.
- **Action：** Apply the delta conversion exactly once; test the inverse conversion on recorded samples.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/issues/1047) · [↗ 2](https://github.com/Physical-Intelligence/openpi/pull/971)

### 3. The observation does not identify the current task phase.

- **Check：** Compare similar observations from different phases and their required actions.
- **Action：** Provide phase labels, history or another observable progress signal supported by the policy.

### 4. The state input is constant, mis-scaled or disconnected.

- **Check：** Inspect per-dimension statistics and change state inputs while holding images fixed.
- **Action：** Match state order, scaling and input mode to the checkpoint's actual configuration.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0_config.py)

### 5. Predictions barely change across observations.

- **Check：** Compare action chunks across distinct observations and multiple sampling seeds.
- **Action：** Inspect conditioning and trainable modules; evaluate a small controlled training run.

### 6. Idle episode starts dominate the reset state.

- **Check：** Plot action magnitude near each episode start.
- **Action：** Trim unintended idle spans while preserving timestamps and observation-action alignment.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/blob/main/examples/droid/README_train.md) · [↗ 2](https://arxiv.org/abs/2503.06669)

### 7. Later phases are absent from the policy's visited-state distribution.

- **Check：** Evaluate from intermediate states and inspect phase coverage.
- **Action：** Collect recovery demonstrations and later-phase starts, then reevaluate the full task.

### 8. Normalization compresses the effective action range.

- **Check：** Compare raw, normalized and decoded actions per dimension with the checkpoint statistics.
- **Action：** Compare compatible pretrained and recomputed statistics using the same evaluation protocol.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/issues/763) · [↗ 2](https://github.com/Physical-Intelligence/openpi/issues/692) · [↗ 3](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/training/config.py)

Additional sources: [↗ 1](https://mlanthology.org/corl/2025/jain2025corl-enabling/) · [↗ 2](https://arxiv.org/abs/2509.07953)

<a id="stalls-at-start"></a>
## The robot hesitates at rollout start

### 1. Recording includes an unintended idle prefix.

- **Check：** Inspect the first seconds of recorded actions and video.
- **Action：** Adjust recording boundaries and trim idle prefixes consistently.

### 2. The first observation is stale or incomplete.

- **Check：** Log capture time and validity of each sensor before the first inference.
- **Action：** Wait for synchronized valid inputs and warm up inference before enabling motion.

<a id="stutter-and-stop"></a>
## Motion alternates between bursts and pauses

### 1. Replanning and execution horizons are poorly matched.

- **Check：** Plot inference times, executed steps and action jumps at chunk boundaries.
- **Action：** Tune execution depth and validate how consecutive chunks are joined.

### 2. The command buffer empties before new actions arrive.

- **Check：** Compare remaining buffer time at inference launch with measured latency and jitter.
- **Action：** Use overlapping inference where supported and define a controller-approved timeout response.

### 3. Action meaning or control frequency differs from training.

- **Check：** Inspect absolute/delta conventions, units and command timestamps.
- **Action：** Match the policy's action contract and explicitly adapt the controller interface.

<a id="chunk-tail-garbage"></a>
## Later actions in a chunk are incorrect

### 1. Episode-tail padding contributes incorrect training targets.

- **Check：** Inspect targets and validity masks across an episode boundary.
- **Action：** Use the model's supported padding convention and mask invalid targets.

### 2. Future actions contain unresolved alternative behaviors.

- **Check：** Compare sampled chunks against distinct valid demonstration continuations.
- **Action：** Improve phase conditioning or shorten execution depth, then measure task success.

<a id="ignores-instruction"></a>
## Instructions do not change behavior

### 1. The prompt is dropped before tokenization.

- **Check：** Inspect the final text and token IDs passed to the policy.
- **Action：** Correct feature names and observation transforms, then test contrasting instructions.

### 2. A global instruction does not identify the active subtask.

- **Check：** Check whether identical inputs require different phase-dependent actions.
- **Action：** Use supported subtask labels or history and verify the labels reach the model.

### 3. The action predictor is weakly coupled to language.

- **Check：** Hold the scene fixed and request different visible targets over repeated trials.
- **Action：** Check data-task correlations and conditioning; evaluate language following separately from nominal success.

<a id="fails-on-new-robot"></a>
## A policy fails on a different robot

### 1. Statistics are missing or incompatible with the embodiment.

- **Check：** Inspect loaded mean/std or quantiles, units and per-dimension ranges.
- **Action：** Use compatible statistics and evaluate reuse versus recomputation; verify required fields exist.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md) · [↗ 2](https://huggingface.co/docs/lerobot/en/pi05)

### 2. Joint order or action dimensions differ.

- **Check：** Compare raw action/state vectors with the robot joint definition.
- **Action：** Map dimensions explicitly and test the mapping with the actuator disabled first.

### 3. Gripper polarity is inverted.

- **Check：** Inspect adapter conventions and verify open/close in a controlled low-risk test.
- **Action：** Store the convention with the action schema and transform it once at the interface.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

### 4. Camera viewpoint or calibration has changed.

- **Check：** Compare captured frames, intrinsics and extrinsics with the training setup.
- **Action：** Restore the expected view or collect adaptation data for the changed setup.

<a id="sim-works-real-fails"></a>
## Simulation works but hardware does not

### 1. Execution errors lead to unseen states.

- **Check：** Compare expert-state prediction with closed-loop rollouts.
- **Action：** Collect recovery and intervention data covering the visited failure states.

### 2. Visual or physical conditions differ from simulation.

- **Check：** Vary lighting, textures, friction and compliance independently where feasible.
- **Action：** Validate randomized simulation results against controlled real data.

### 3. Simulation omits deployment delay.

- **Check：** Measure real observation-to-command delay and inject it into simulation.
- **Action：** Correct the timing architecture and evaluate delay robustness.

<a id="eval-numbers-not-trustworthy"></a>
## Success estimates vary between runs

### 1. The evaluation sample is small.

- **Check：** Compute uncertainty intervals and inspect the number of independent trials.
- **Action：** Fix a trial protocol before comparison and report counts with intervals.

### 2. Initial conditions differ between runs.

- **Check：** Log object pose and task variant for every trial.
- **Action：** Use matched initial states and randomized condition order.

### 3. Temperature or calibration drifts during evaluation.

- **Check：** Repeat a reference condition at the beginning and end.
- **Action：** Interleave conditions and log thermal state and calibration checks.

<a id="config-did-not-apply"></a>
## Configuration changes have no effect

### 1. Weight loading does not restore the expected settings.

- **Check：** Print the constructed configuration after checkpoint loading.
- **Action：** Pass required settings explicitly for the pinned version and verify their runtime values.
- **Additional sources：** [↗ 1](https://huggingface.co/docs/lerobot/en/pi05)

### 2. The normalization mode differs from the reference recipe.

- **Check：** Inspect the effective ACTION, STATE and VISUAL mappings.
- **Action：** Match the checkpoint's expected transforms and document intentional differences.
- **Additional sources：** [↗ 1](https://huggingface.co/docs/lerobot/en/pi05)

### 3. A nested default overrides a command-line setting.

- **Check：** Compare parsed optimizer and trainer values with the intended values.
- **Action：** Use the version-correct parameter namespace and save the resolved configuration.

### 4. A checkpoint contains older statistics.

- **Check：** Compare loaded statistics with the newly computed dataset statistics.
- **Action：** Update statistics through the supported checkpoint or processor workflow and verify loading again.
- **Additional sources：** [↗ 1](https://huggingface.co/docs/lerobot/en/pi05)

<a id="normalization-silently-skipped"></a>
## Normalization is skipped or incorrect

### 1. Statistic keys do not match the feature lookup.

- **Check：** Use known non-identity statistics and check the actual normalized values as well as the inverse round trip.
- **Action：** Repair key mapping; a round trip alone cannot detect two identity no-ops.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/4415)

### 2. Merged quantile summaries are not full-dataset quantiles.

- **Check：** Compare saved bounds with raw-data quantiles and the fraction of values outside them.
- **Action：** Compute quantiles over the intended sample population; distinguish a conservative envelope from exact quantiles.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/4156) · [↗ 2](https://github.com/huggingface/lerobot/pull/3804) · [↗ 3](https://github.com/sawhney17/droid-quantile-repair)

### 3. Camera or feature names differ between data and robot configuration.

- **Check：** Compare every declared feature with the statistics file keys.
- **Action：** Align names before training and deployment; fail clearly when required statistics are missing.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/1095)

### 4. Migration rewrites a feature name incorrectly.

- **Check：** Inspect underscore and dot handling in migrated statistic keys.
- **Action：** Use the policy's declared feature names and an explicit migration mapping.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/4451)

<a id="fine-tune-zero-success"></a>
## Loss decreases but task success stays near zero

### 1. Adapter targets omit task-relevant modules.

- **Check：** Inspect actual trainable parameter names and counts.
- **Action：** Compare target coverage against a working reference and test a controlled adapter configuration.
- **Additional sources：** [↗ 1](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/12-VLA%E5%BE%AE%E8%B0%83%E5%AE%9E%E6%88%98.md) · [↗ 2](https://huggingface.co/docs/lerobot/en/smolvla)

### 2. An adapter directory is interpreted as a base model, or vice versa.

- **Check：** Inspect the loaded base checkpoint and adapter state separately.
- **Action：** Use the version-specific workflow for creating or resuming an adapter.
- **Additional sources：** [↗ 1](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/12-VLA%E5%BE%AE%E8%B0%83%E5%AE%9E%E6%88%98.md)

### 3. Several settings drifted from the reference configuration.

- **Check：** Diff the complete resolved configuration, including statistics and action horizons.
- **Action：** Establish a reference baseline and change one factor per comparison.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/issues/711)

<a id="training-collapses-unexpectedly"></a>
## Training produces NaNs or unexpected loss scales

### 1. Pretrained weights did not load correctly.

- **Check：** Inspect missing keys and compare loaded tensor values with the checkpoint.
- **Action：** Pin compatible dependencies and verify loading before restarting training.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/1406)

### 2. Near-zero action variance makes scaling unstable.

- **Check：** Inspect per-dimension variance and normalized-value ranges.
- **Action：** Handle constant dimensions explicitly and use a numerically appropriate denominator bound.
- **Additional sources：** [↗ 1](https://github.com/Physical-Intelligence/openpi/issues/814)

### 3. Compilation changes numerical behavior.

- **Check：** Repeat the same batch with compilation enabled and disabled.
- **Action：** Isolate the failing operation and use a verified compiler configuration.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/4178)

### 4. Resume did not restore adapters correctly.

- **Check：** Compare adapter values and trainable parameter counts before and after resume.
- **Action：** Restore model, adapter and optimizer state using a compatible checkpoint format.
- **Additional sources：** [↗ 1](https://github.com/huggingface/lerobot/issues/3459)
