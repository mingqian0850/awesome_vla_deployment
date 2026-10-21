# Look up a concrete problem

[Home](../README.en.md) · [中文](zh/decision-tables.md)

Match your conditions, then read the proposed action, configuration location and acceptance check. Record unmeasured conditions as unknown rather than satisfied. This edition covers deployment pauses, training monitoring and dataset formats; it is not a universal robot configuration.

## What problem do I have?

| Question or condition | Go directly to | What you should be able to do |
| --- | --- | --- |
| My robot can pause between actions. Do I need asynchronous inference? | [Pauses allowed](deployment-decisions.md#pause) | Decide whether synchronous inference is sufficient and define controller behavior while waiting |
| Pauses are allowed only during certain process stages | [Choose by stage](deployment-decisions.md#select) | Separate waiting stages from continuous execution stages |
| Action chunks stutter despite acceptable average inference speed | [Continuous execution and budgets](deployment-decisions.md#budget) | Measure buffer depletion, tail latency and observation age |
| A remote GPU sometimes responds slowly | [Deployment choices](deployment-decisions.md#select) | Include network delay and validate timeout behavior |
| Should I choose TensorBoard, W&B or MLflow? | [Monitoring platforms](training-monitoring.md#platform) | Choose for local learning, an existing integration or a team service |
| Where do I enable logging in LeRobot, openpi or GR00T? | [Framework configuration](training-monitoring.md#integration) | Find verified switches and logging intervals |
| Loss is decreasing. Is training actually useful? | [Metrics and symptoms](training-monitoring.md#metrics) | Inspect validation data, action errors and closed-loop evaluation |
| Should my dataset use LeRobot, RLDS or HDF5? | [Start with the target trainer](dataset-format-decisions.md#target) | Pin the reader before choosing a conversion target |
| Can GR00T directly consume my LeRobot v3 dataset? | [Compatibility table](dataset-format-decisions.md#target) | Identify the v2 conversion and modality metadata requirements |
| Can I train robot actions directly from ego video alone? | [Convert what you have](dataset-format-decisions.md#convert) | Distinguish video semantics from robot-action supervision |
| Data loads, but are arm order, units and timing correct? | [Sample contract and acceptance](dataset-format-decisions.md#contract) | Check field meaning, alignment and action slices |
| I have 8GB VRAM and am not training yet | [Practice without training](training-monitoring.md#practice) | Inspect existing logs and small samples |

## What makes an answer actionable?

| Field | Example |
| --- | --- |
| Conditions | Static workcell, independent low-level controller, process permits waiting for another chunk |
| Recommendation | Establish a synchronous inference baseline |
| Action | Set execution length, define the waiting state, measure end-to-end inference latency |
| Acceptance | Measured pauses and observation age meet the process budgets; timeouts enter a validated controller state |
| Does not apply when | Balance depends on this output, the scene changes quickly, or the process cannot wait |
| Evidence | A pinned official implementation or a calculation explicitly identified as engineering analysis |

Validate engineering recommendations with your own data and equipment. Implementation claims include versions and sources; numerical examples are calculations only. If a problem remains, record controller mode, trainer version, dataset version, configuration and measurements before consulting [troubleshooting](troubleshooting.md).
