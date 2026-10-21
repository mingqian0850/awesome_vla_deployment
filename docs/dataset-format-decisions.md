# Dataset formats: choose by trainer and validate

[Home](../README.en.md) · [中文](zh/dataset-format-decisions.md) · [Question index](decision-tables.md)

**Choose the trainer and version before choosing a dataset format.** Having MP4/Parquet/HDF5 files, matching the reader schema and matching the robot's action semantics are separate requirements. Container conversion solves only part of this. This page covers selection, field contracts and acceptance checks.

<a id="target"></a>
## Which trainer will consume the data?

Implementations checked 2026-10-21; short revisions refer to the pinned sources below. Repeat sample-loading checks after upgrades.

| Target | Requirements | Files/configuration | Common mistake |
| --- | --- | --- | --- |
| LeRobot `463202b`, v3 reader path | Feature schema, shard indices, episode boundaries and media readable by that version | `meta/info.json` defines features, FPS and paths; `meta/episodes/` stores shard indices; this code defaults to `meta/tasks.parquet` for tasks | v3 shards can contain multiple episodes; filenames do not define boundaries. The guide still mentions `tasks.jsonl`; use actual reader code and dataset version |
| GR00T `dac54b3` | GR00T-flavored LeRobot **v2**, modality metadata and matching data configuration | `meta/modality.json`, `meta/info.json`, `meta/episodes.jsonl`, `meta/tasks.jsonl`; Parquet states/actions and corresponding MP4 | Existing v3 needs the repository's `scripts/lerobot_conversion/convert_v3_to_v2.py`, followed by modality checks; do not assume native v3 support |
| openpi `215abfb`, LeRobot data path | Compatibility with its pinned LeRobot dependency plus input mapping and normalization | `pyproject.toml` pins LeRobot `0cf8648...`; data configuration/transforms in `src/openpi/training/config.py`; matching norm stats | Sharing the LeRobot name is insufficient; field repacking and action conversion must match the policy configuration |
| robomimic 0.5 documented path | HDF5 with robomimic schema and the observations/metadata required by the algorithm | `data/demo_0/actions`, `data/demo_0/obs/<key>`, relevant `next_obs`, trajectory attributes, environment metadata and splits | HDF5 is a container; arbitrary HDF5 or videos alone are not compatible datasets |
| Trainer explicitly requiring RLDS/TFDS | Episodes/steps and feature specification defined by its builder | Step boundary markers and required observation, action and task fields; the TFDS builder defines the actual schema | RLDS is not a filename extension; `is_last` differs from `is_terminal`, and neither automatically means success |
| Model/embodiment undecided | Preserve raw streams, calibration, clocks, commands/states, tasks and episode metadata; make conversion reproducible | Establish the sample contract below before exporting to a chosen target | Do not discard original timestamps or treat human joints as robot-action supervision |

Evidence: [LeRobot v3 guide](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/docs/source/lerobot-dataset-v3.mdx) and [reader path definitions](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/src/lerobot/datasets/utils.py); [GR00T data preparation](https://github.com/NVIDIA/Isaac-GR00T/blob/dac54b313160c201c450f97df0fd74ebd379c892/getting_started/data_preparation.md); [openpi dependency](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/pyproject.toml) and [training data workflow](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/README.md); [robomimic schema](https://robomimic.github.io/docs/datasets/overview.html); [RLDS structure](https://github.com/google-research/rlds/blob/b35dac3a6b73396b0cb8773095999c4b5d70947c/README.md).

<a id="contract"></a>
## What must each sample explain?

This is a cross-framework **semantic checklist**. The first column names concepts; datasets do not have to rename their fields to match it.

| Content | Minimum description | Inspection |
| --- | --- | --- |
| Episode and split | Attempt boundaries and training/validation membership | Do not randomly split frames from one continuous attempt across both; isolate objects, dates or workcells when needed |
| Time | Original acquisition times, clock sources, units, rates, missing-frame/resampling rules | Plot image, state and command timelines; identify fixed offsets and maximum alignment error |
| Vision | Camera names, image shapes, encoding, color order; intrinsics/extrinsics for geometry | Decode first/middle/last frames; check wrist-camera swaps and RGB/BGR order |
| Robot state | Per-dimension names, order, units, frames and measurement meaning | Compare values with simultaneous pose/video; vector length is insufficient |
| Action labels | Command versus measured state; absolute versus delta; position/velocity/torque; gripper convention | Trace capture code to the control interface; disclose proxy-label construction and errors if commands were not recorded |
| Language | Text or task IDs/mapping and their validity intervals | Decode IDs and check the current task; labels must follow process changes |
| Missing values and masks | Missing cameras, unused action dimensions and incomplete final horizons | Padding is not a true zero action; verify invalid targets are excluded from loss |
| Outcomes and provenance | End reason, success/failure, interventions, device/operator and processing version | Episode termination is not success; retain traceability between raw and cleaned samples |

**Example bimanual contract:** assume six joints and one gripper width per arm, giving 14 absolute target values. `[0:6]` is left-arm joint angles in rad, `[6:7]` left gripper width in m, `[7:13]` right-arm angles in rad, and `[13:14]` right gripper width in m. States may contain corresponding measurements, but measurements and commands are not interchangeable. A real robot may use seven-axis arms, dexterous hands or end-effector targets; do not copy the 14-dimensional assumption.

With batch size B=2 and prediction horizon H=8, this example may yield action targets `[2, 8, 14]` and single-time states `[2, 14]`. Images may be stored as HWC uint8 while the model expects CHW floats with particular normalization; inspect the transformed batch. Equal shapes do not establish equal units or semantics.

## GR00T modality mapping: split the vector correctly

For the 14-dimensional assumption above, the **action section** of `meta/modality.json` can describe these slices. This is a fragment, not a complete trainable dataset configuration; state, video, annotations, data columns and trainer configuration remain necessary.

```json
{
  "action": {
    "left_arm": {"start": 0, "end": 6},
    "left_gripper": {"start": 6, "end": 7},
    "right_arm": {"start": 7, "end": 13},
    "right_gripper": {"start": 13, "end": 14}
  }
}
```

`end` is exclusive. These four custom names must also match your modality configuration; editing JSON alone does not change model inputs. The format interprets concatenated `float32` state/action arrays through slice metadata.

Language requires agreement in three locations. In the pinned task-description example, the Parquet column is `annotation.human.task_description`, the annotation key in `modality.json` is `human.task_description`, and training `modality_keys` uses the full `annotation.human.task_description`. The integer value maps to text in `meta/tasks.jsonl`. Other datasets can use different annotation names; match their actual columns rather than blindly renaming them to this example.

<a id="convert"></a>
## What should I do with the data I already have?

| Available data | First useful step | Still required |
| --- | --- | --- |
| Ego MP4 only | Segment processes, annotate language, learn visual representations or action semantics | Robot-action supervision needs a source of usable action labels; video alone contains no robot commands |
| Human hand/body trajectories and ego video | Align clocks, calibrate frames, inspect trajectories, then study target-robot retargeting | Robot kinematics, reachability/contact constraints and target control representation; validate retargeted results separately |
| Video, robot-state CSV and command logs | Convert aligned samples into the target reader schema | Episodes, language, units, camera mapping, metadata and missing-value handling |
| LeRobot v3 intended for this GR00T revision | Run the referenced v3→v2 converter into a new directory | Recheck frame counts, boundaries, language columns, modality slices and actual training batches; preserve the original |
| Data loads but action dimensions differ | Compare action head, data configuration and actual controller interface | Semantically justified adaptation, padding/masks and normalization; arbitrary truncation or zeros are not a fix |
| Suspiciously good validation after processing | Episode/scene leakage and normalization-statistics provenance | Separate splits; fit new statistics on training data only; record provenance when using fixed pretrained statistics |

<a id="acceptance"></a>
## How do I validate before large conversion or training?

| Order | Action | Pass condition / response to failure |
| --- | --- | --- |
| 1. Pin the reader | Save trainer commit, dependency lock and dataset version; load an episode through the actual training data path | Opening Parquet with a generic tool is insufficient; inspect path/schema/version on failure |
| 2. Inspect media and time | Decode first/middle/last frames; compare state/command timestamps, task IDs and episode indices | No unexplained duplicates, missing frames or offsets; alignment error meets the task's timing budget |
| 3. Check semantics | Compare video/capture interfaces with each arm, gripper, unit and absolute/delta convention | Explain an action as an intended controller command; min/max checks alone are insufficient |
| 4. Inspect the transformed batch | Print keys, dtype, shape, finite values, decoded language and masks; sample first/last action chunks | No cross-episode concatenation; padding matches loss masks; normalization/denormalization recovers original values on checked samples |
| 5. Convert small and reopen | Convert a few complete episodes into a separate output directory, close and reopen the reader | Consistent counts, readable media and provenance; call LeRobot v3 writer `finalize()` before acceptance checks |

Passing these checks establishes initial data-interface acceptance, **not executable retargeting, learned task competence or validated robot deployment**. Record failing episode/frame IDs and consult [training diagnostics](training-monitoring.md#metrics) and [data foundations](01-data-and-training.md). No large dataset download or model training was performed for this page.
