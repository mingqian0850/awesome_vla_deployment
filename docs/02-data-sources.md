# Step one: what data do industry and research use?

[Home](../README.en.md) · [中文](zh/02-data-sources.md)

Reviewed: 2026-10-20. Define the capability before selecting capture signals. Egocentric describes a viewpoint, not the availability of robot action labels. These are representative documented routes, not an industry market-share survey or a requirement to buy hardware.

## Five data routes and their uses

| Type and public reference | Available observations or supervision | What does not follow |
| --- | --- | --- |
| [Ego-Exo4D](https://docs.ego-exo4d-data.org/): human multiview skills | Synchronized first-/third-person views and step, language and pose annotations; coverage depends on subset | Target-robot commands are absent; these are not directly robot actions |
| [EgoMimic](https://github.com/SimarKareer/EgoMimic): joint human/robot learning | Processing and training paths for Aria human data and teleoperated robot data | Ordinary video can train any robot without tracking or alignment |
| [UMI](https://umi-gripper.github.io/): handheld demonstrations | Camera images, tool trajectories and gripper opening; a smaller capture/execution interface gap | Direct transfer to arbitrary multifinger hands or whole-body movement |
| [AgiBot World](https://github.com/OpenDriveLab/AgiBot-World): robot manipulation data | Vision, state, action and task information according to the selected release | The public data is a particular G2 factory's deployment data or supplies full bipedal walking supervision |
| [GR-1 simulated teleoperation](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-Sim) | Simulated demonstrations with inspectable state, action and timestamp fields | Simulation success establishes production readiness; the card specifies CC-BY-NC-4.0 |

Routes can be combined. Interpret results without target-robot demonstrations under their specific method, inputs, tasks and evaluation; they do not establish deployment from arbitrary ego video. Check data, code and weight terms separately, and do not mix schemas or statistics across releases.

## What industry actually discloses

[Mercedes-Benz × Apollo](https://group.mercedes-benz.com/company/production/production-network/mbdfc-humanoid-robots.html) describes production workers teaching through teleoperation and AR, without a complete training-set release. [Atlas / TRI](https://bostondynamics.com/blog/large-behavior-models-atlas-find-new-footing/) describes VR teleoperation and training across platforms; this platform research does not establish a particular production workcell's stack.

A teleoperation disclosure does not establish camera models, action dimensions, capture hours or human/robot mixing ratios. Keep undisclosed fields unknown.

## Understand one episode

This is a suggested inspection structure, not an exact upstream schema. An episode is one bounded attempt and may succeed, fail or be interrupted.

| Field group | Questions to answer |
| --- | --- |
| Task and identity | Task, episode ID, capture session, object/SKU; how are boundaries and resets defined? |
| Observations | Camera names, image sizes, depth availability; how are occlusion and missing frames marked? |
| State | Measured joints/end-effector state or estimated poses? What is the joint order? |
| Action | Commands, future-state labels or retargeted references? Absolute/delta/velocity; units, frame and control mode? |
| Timing and calibration | Are acquisition and receipt times confused? How are camera, state and command delays aligned? |
| Process outcome | Are motion completion, product quality, equipment-test completion and human takeover recorded separately? |
| Lineage and split | Can raw data, processing versions, calibration and train/validation groups be traced? |

Separate measured signals, estimates, retargeted references, issued commands and execution feedback. An unknown force is not zero; next-frame state need not equal current action. Read the recorder and controller definitions before choosing training labels.

## Add signals according to the task

- Stationary pick-and-place: both arms, grippers, hand–eye/tool calibration, part and fixture state.
- Contact assembly: force/torque or tactile measurements as required, contact events and independent quality criteria; visual trajectories alone do not establish insertion quality.
- Move then manipulate: base pose, standing/parking error and arrival conditions.
- Coupled locomotion and manipulation: whole-body motion, foot contact, payload and controller tracking. A humanoid appearance does not establish this data coverage.

This is a requirements checklist; not every task needs every sensor.

## First assignment on an 8GB laptop

1. Open AgiBot World's data documentation/visualization entry or GR-1's web viewer. Select one format and one episode; do not download the complete dataset.
2. For image, state, action and timestamp, record source, shape, unit, frame and sample rate. Mark unresolved fields unknown.
3. Sketch a grasp-to-place interval, identify command/feedback delays and locate the completion criterion.
4. Compare EgoMimic human data, list missing robot fields, then inspect how UMI changes the capture interface.
5. Produce a one-page field dictionary and question list. No weights, training or robot are required; check shard sizes and access terms before downloading.

Continue: [collection checklist](../checklists/before-collecting-data.md) · [action conventions and training](01-data-and-training.md).
