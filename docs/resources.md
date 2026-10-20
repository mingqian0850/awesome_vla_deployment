# Resource catalog

[Home](../README.en.md) · [中文](zh/resources.md)

Descriptions refer to the linked sources and recorded versions. A research result is not an independently reproduced deployment.

## Contents

- [Data collection and preparation](#data)
- [Models and training frameworks](#training)
- [Fine-tuning and configuration](#training-recipes)
- [Deployment and runtime](#deployment)
- [Latency and optimization measurements](#benchmarks)
- [Evaluation](#evaluation)
- [Reported failure cases](#counter-evidence)
- [Runtime monitoring and protection](#safety)
- [License references](#licensing)
- [Further learning](#learning-resources)

<a id="data"></a>
## Data collection and preparation

Record, inspect and prepare robot demonstrations.

<a id="lerobot-docs"></a>
### [LeRobot documentation](https://huggingface.co/docs/lerobot/index)

docs · hardware use reported · Apache-2.0

Official documentation covering robot assembly, calibration, teleoperation, datasets, training and rollout.

<a id="lerobot-il-robots"></a>
### [LeRobot — imitation learning on real robots](https://huggingface.co/docs/lerobot/en/il_robots)

docs · hardware use reported

An end-to-end imitation-learning walkthrough: assemble, calibrate, record, train and evaluate.

<a id="lerobot-so101"></a>
### [LeRobot — SO-101 assembly and calibration](https://huggingface.co/docs/lerobot/en/so101)

docs · hardware use reported

SO-101 hardware assembly and calibration instructions.

<a id="aloha"></a>
### [ALOHA / Mobile ALOHA](https://github.com/MarkFzp/mobile-aloha)

repo · research

A bimanual leader-follower teleoperation and imitation-learning platform.

<a id="umi"></a>
### [Universal Manipulation Interface (UMI)](https://github.com/real-stanford/universal_manipulation_interface)

repo · research

A camera-equipped handheld gripper captures demonstrations without the deployment robot present.

<a id="open-television"></a>
### [Open-TeleVision](https://github.com/OpenTeleVision/TeleVision)

repo · research

VR teleoperation with stereo streaming and active vision for bimanual and humanoid robots.

<a id="robot-teach"></a>
### [robot_teach (Open-Teach)](https://github.com/chiawenwang/robot_teach)

repo · research

Uses VR hand-tracking demonstrations to build reusable manipulation policies.

<a id="robomimic"></a>
### [robomimic](https://github.com/ARISE-Initiative/robomimic)

repo · hardware use reported · MIT

Offline imitation-learning framework with demonstration datasets and training/evaluation pipelines.

<a id="robosuite"></a>
### [robosuite](https://github.com/ARISE-Initiative/robosuite)

repo · hardware use reported

Modular simulation framework for robot manipulation, also used by robomimic.

<a id="mimicgen"></a>
### [MimicGen](https://github.com/NVlabs/MimicGen)

repo · research

Expands a small set of demonstrations through object-pose transformations and motion replanning.

<a id="open-x-embodiment"></a>
### [Open X-Embodiment](https://robotics-transformer-x.github.io/)

dataset · hardware use reported

Cross-embodiment manipulation datasets from multiple robots and laboratories, distributed using RLDS.

<a id="open-x-embodiment-repo"></a>
### [google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment)

repo · hardware use reported

Code and per-dataset documentation for loading Open X-Embodiment.

<a id="data-curation-paper"></a>
### [Robot Data Curation](https://arxiv.org/abs/2502.08623)

paper · research

Studies filtering and selecting robot demonstrations using their influence on policy learning.

<a id="curating-online-experience"></a>
### [Curating Demonstrations using Online Experience](https://arxiv.org/abs/2503.03707)

paper · research

Uses online interaction experience to select demonstrations for training.

<a id="subgoal-transitions"></a>
### [Enabling Long(er) Horizon Imitation for Manipulation Tasks by Modeling Subgoal Transitions](https://mlanthology.org/corl/2025/jain2025corl-enabling/)

paper · research

Models transitions between subgoals for longer-horizon imitation learning.

<a id="rac-recovery"></a>
### [RaC: Robot Learning for Long-Horizon Tasks by Scaling Recovery and Correction](https://arxiv.org/abs/2509.07953)

paper · research

Studies recovery and correction data for long-horizon policies that encounter their own execution errors.

<a id="action-only-scorers-fail"></a>
### [Action-Only Scorers Fail on the Structural Defects That Degrade Imitation Policies](https://arxiv.org/abs/2606.05588)

paper · research

Audits action-only data-quality scores against defects such as idle frames, ambiguous state and spurious correlations.

<a id="balanced-bc-imbalanced"></a>
### [Towards Balanced Behavior Cloning from Imbalanced Datasets](https://arxiv.org/abs/2508.06319)

paper · research

Studies behavior cloning when behaviors and skills have unequal representation in the dataset.

<a id="openvla-mixture-recipe"></a>
### [OpenVLA's data balancing and mixture recipe over Open X-Embodiment](https://arxiv.org/abs/2406.09246)

paper · research

Documents OpenVLA dataset mixing, reweighting and exclusions across robot, task and scene distributions.

<a id="agibot-world-pipeline"></a>
### [AgiBot World — data collection pipeline](https://arxiv.org/abs/2503.06669)

paper · hardware use reported

AgiBot World describes pilot collection, operator validation, annotation and failure-driven data refinement.

<a id="eventual-dead-frames"></a>
### [Cutting dead frames from DROID — 500 hours of robot data in 32 seconds](https://www.eventual.ai/blog/cutting-dead-frames-from-droid)

blog · hardware use reported

Engineering example of detecting and trimming idle frames in DROID data.

<a id="daft-motion-trimming"></a>
### [Daft — motion trimming for physical AI](https://docs.getdaft.io/en/stable/examples/motion-trimming-physical-ai/)

tool · hardware use reported

Example notebook for trimming robot-video segments using motion information.

<a id="lerobot-doctor"></a>
### [lerobot-doctor — dataset quality diagnostics](https://github.com/jashshah999/lerobot-doctor)

tool · research

Community diagnostics for idle periods, anomalies and outlying episodes in LeRobot datasets.

<a id="lerobot-language-schema"></a>
### [LeRobot — language annotation schema](https://github.com/huggingface/lerobot/blob/main/docs/source/language_and_recipes.mdx)

docs · hardware use reported

Defines persistent and event language columns, recipe-based conditioning and joint subtask supervision; exact fields depend on the pinned version.

<a id="lerobot-annotation-pipeline"></a>
### [LeRobot annotation pipeline — VLM auto-labelling that produces those columns](https://github.com/huggingface/lerobot/blob/main/docs/source/annotation_pipeline.mdx)

docs · hardware use reported

VLM-assisted annotation pipeline for plans, subtasks, memory and events, with validation and cost estimation.

<a id="lerobot-annotation-ui"></a>
### [lerobot-annotate — annotation UI](https://github.com/huggingface/lerobot-annotate)

repo · hardware use reported

Web interface for annotating LeRobot datasets.

<a id="lerobot-good-dataset"></a>
### [LeRobot — what makes a good dataset](https://huggingface.co/blog/lerobot-datasets)

blog · hardware use reported

Collection guidance covering camera views, lighting, frame rate, feature naming and task descriptions.

<a id="hd-space"></a>
### [HD-Space — staged collection for later-phase start states](https://arxiv.org/abs/2505.17389)

paper · research

Collects later-stage demonstrations by using an existing policy to reach intermediate start states.

<a id="robomimic-what-matters"></a>
### [What Matters in Learning from Offline Human Demonstrations](https://arxiv.org/abs/2108.03298)

paper · research

Studies demonstration quality, camera observations and checkpoint evaluation in offline imitation learning.

<a id="data-scaling-laws"></a>
### [Data Scaling Laws in Imitation Learning for Robotic Manipulation](https://arxiv.org/abs/2410.18647)

paper · research

Studies how manipulation generalization changes with environment, object and demonstration diversity.

<a id="egomimic-data"></a>
### [EgoMimic — human and robot data processing](https://github.com/SimarKareer/EgoMimic)

repo · research

Processing and training code for tracked human Aria demonstrations and teleoperated robot data.

**Use conditions：** Human and robot observations require alignment; this is not arbitrary video-to-robot conversion.

<a id="ego-exo4d-skills"></a>
### [Ego-Exo4D — human skill understanding](https://docs.ego-exo4d-data.org/)

dataset · research

Synchronized human ego/exo observations and skill annotations for activity understanding.

**Use conditions：** No target-robot command labels; check subset annotations and access terms.

<a id="agibot-world-data"></a>
### [AgiBot World — released data and visualization](https://github.com/OpenDriveLab/AgiBot-World)

repo · research

Official entry point for robot manipulation data, visualization and released learning components.

**Use conditions：** Pin the data release; do not identify it with a G2 factory dataset or full bipedal locomotion data.

<a id="gr1-teleop-sim-data"></a>
### [GR-1 — simulated tabletop teleoperation](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-Sim)

dataset · research

Simulated GR-1 demonstrations with a browsable state/action schema.

**Use conditions：** CC-BY-NC-4.0 according to the dataset card; simulation data is not real production evidence.

<a id="training"></a>
## Models and training frameworks

Implementations for policy training and inference.

<a id="openpi"></a>
### [openpi (Physical Intelligence)](https://github.com/Physical-Intelligence/openpi)

repo · hardware use reported · Apache-2.0

Official implementation of pi0, pi0-FAST and pi0.5 with training configurations and robot inference tools.

<a id="lerobot"></a>
### [LeRobot (Hugging Face)](https://github.com/huggingface/lerobot)

repo · hardware use reported · Apache-2.0

Robot-learning stack covering hardware, datasets, teleoperation, policy training and rollout.

<a id="isaac-gr00t"></a>
### [NVIDIA Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)

repo · hardware use reported

NVIDIA vision-language-action models with fine-tuning and evaluation tooling.

<a id="openvla"></a>
### [OpenVLA](https://github.com/openvla/openvla)

repo · research

A 7B vision-language-action model using a language-model backbone and discrete action tokens.

<a id="openvla-oft"></a>
### [OpenVLA-OFT](https://github.com/moojink/openvla-oft)

repo · research

OpenVLA fine-tuning recipe using parallel decoding, action chunking and continuous actions.

<a id="rdt-1b"></a>
### [RDT-1B (RoboticsDiffusionTransformer)](https://github.com/thu-ml/RoboticsDiffusionTransformer)

repo · research

Diffusion-transformer model for bimanual manipulation with a unified physical action representation.

<a id="octo"></a>
### [Octo](https://github.com/octo-models/octo)

repo · research

Transformer policy trained on Open X-Embodiment with flexible observation and action spaces.

<a id="fluxvla"></a>
### [FluxVLA](https://github.com/FluxVLA/FluxVLA)

repo · research

Engineering platform connecting VLA data processing, training and deployment.

<a id="rlinf"></a>
### [RLinf](https://github.com/RLinf/RLinf)

repo · research

Reinforcement-learning infrastructure with embodied-model training and real-robot examples.

<a id="vla-foundry"></a>
### [TRI-ML/vla_foundry](https://github.com/TRI-ML/vla_foundry)

repo · research

Toyota Research Institute toolkit for VLA training and evaluation.

<a id="openpi-tool"></a>
### [Isaiah-WU/Openpi_tool — pi05 fine-tuning and real-robot deployment](https://github.com/Isaiah-WU/Openpi_tool)

repo · research

Chinese tutorials and tools for pi0.5 fine-tuning and real-robot deployment.

<a id="pi05-xarm-tutorial"></a>
### [dzj441/pi05XarmTutorial](https://github.com/dzj441/pi05XarmTutorial)

repo · research

Tutorial for deploying pi0.5 on a UFactory xArm.

<a id="df-post-training"></a>
### [Denghaoyuan123/DF-post-training](https://github.com/Denghaoyuan123/DF-post-training)

repo · research

Post-training recipes for diffusion-based VLA policies.

<a id="lerobot-realman"></a>
### [Humble2Full/lerobot-realman-vla](https://github.com/Humble2Full/lerobot-realman-vla)

repo · demo

LeRobot-based learning and deployment pipeline for a RealMan arm.

<a id="xpolicylab"></a>
### [MicroAGI-Labs/XPolicyLab](https://github.com/MicroAGI-Labs/XPolicyLab)

repo · demo

Multiple robot-policy implementations exposed through a shared interface.

<a id="training-recipes"></a>
## Fine-tuning and configuration

Action representations, statistics, adapters and checkpoint handling.

<a id="openpi-requirements"></a>
### [openpi — GPU / VRAM requirements](https://github.com/Physical-Intelligence/openpi)

docs · hardware use reported

openpi documents GPU memory requirements for inference, LoRA and full fine-tuning; practical use also depends on configuration and overhead.

**Use conditions：** The recorded single-GPU table gives >8 GB for inference, >22.5 GB for LoRA and >70 GB for full fine-tuning. Check the source revision and leave room for data, optimizer and saving overhead.

<a id="openpi-norm-stats"></a>
### [openpi — normalisation statistics and when to reuse them](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

docs · hardware use reported

Normalization statistics are stored with checkpoints; matching embodiment statistics can be reused or compared against newly computed statistics.

<a id="openpi-action-space"></a>
### [openpi — action space and control frequency conventions](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

docs · hardware use reported

Documents robot-specific joint ordering, gripper conventions and control frequencies; read the configuration for the actual embodiment.

<a id="droid-action-space"></a>
### [DROID — action representation](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

docs · hardware use reported

DROID uses seven joint-velocity actions plus a gripper action at 15 Hz in the cited openpi configuration.

<a id="lerobot-pi05-recipe"></a>
### [LeRobot — pi0.5 fine-tuning recipe](https://huggingface.co/docs/lerobot/en/pi05)

docs · hardware use reported

Reference pi0.5 fine-tuning configuration covering batch size, steps, precision, checkpointing and expert-only variants.

<a id="lerobot-pi0-recipe"></a>
### [LeRobot — pi0 fine-tuning recipe](https://huggingface.co/docs/lerobot/en/pi0)

docs · hardware use reported

Reference pi0 fine-tuning configuration with compilation, gradient checkpointing and BF16 settings.

<a id="openpi-idle-filter"></a>
### [openpi — idle filter for DROID training](https://github.com/Physical-Intelligence/openpi/blob/main/examples/droid/README_train.md)

docs · hardware use reported

DROID training recipe filters timesteps whose subsequent action chunks are largely idle.

<a id="rtc-training"></a>
### [Training-Time Action Conditioning for Efficient Real-Time Chunking](https://arxiv.org/abs/2512.05964)

paper · research

Trains action-prefix conditioning for RTC; maximum expected inference delay is expressed in controller steps.

<a id="openvla-ft-comparison"></a>
### [OpenVLA — fine-tuning strategy comparison](https://arxiv.org/abs/2406.09246)

benchmark · research

OpenVLA compares full fine-tuning, LoRA and partial freezing under a shared evaluation protocol, including memory and trainable parameters.

<a id="lerobot-lora-target-trap"></a>
### [SmolVLA — LoRA target modules](https://github.com/huggingface/lerobot/issues/4415)

discussion · research

A SmolVLA experiment reports that LoRA target-module coverage changed rollout success substantially; rank alone does not define the adapter.

<a id="pi05-small-dataset-quantile"></a>
### [pi0.5 fine-tunes worse than pi0 on small single-arm datasets](https://github.com/Physical-Intelligence/openpi/issues/763)

discussion · research

A reported small-data pi0.5 regression involves normalization and training settings; the suggested changes require controlled comparison.

Additional sources: [↗ 1](https://github.com/Physical-Intelligence/openpi/issues/763) · [↗ 2](https://github.com/Physical-Intelligence/openpi/issues/692)

<a id="pi05-config-drift"></a>
### [pi0.5 — configuration-drift report](https://github.com/Physical-Intelligence/openpi/issues/711)

discussion · research

A low LIBERO result was associated with differences in adapters, state input, horizons and statistics from the reference configuration.

<a id="checkpoint-selection"></a>
### [Checkpoint evaluation protocols](https://github.com/Physical-Intelligence/openpi)

discussion · research

Examples of checkpoint selection using validation errors, fixed budgets and rollout evaluation; metrics are not interchangeable across frameworks.

<a id="evaluation-noise-floor"></a>
### [Evaluation variability](https://github.com/NVIDIA/Isaac-GR00T)

discussion · research

Reported evaluation variation illustrates the need to measure run-to-run and finite-sample uncertainty on the actual setup.

<a id="horizon-ablations"></a>
### [SmolVLA — prediction and execution horizons](https://arxiv.org/abs/2506.01844)

benchmark · research

SmolVLA separately studies prediction horizon and executed steps; these are distinct parameters with task-dependent effects.

<a id="normalization-three-regimes"></a>
### [Normalization modes](https://arxiv.org/abs/2506.01844)

docs · hardware use reported

Model families and recipes use different normalization modes; inspect the constructed configuration rather than inferring it from the model name.

<a id="fsq-tokenizer-trap"></a>
### [openpi — FSQ and FAST tokenizers](https://github.com/Physical-Intelligence/openpi)

repo · hardware use reported

openpi's fsq_tokenizer.py serves RoboArena baselines. FAST is a distinct DCT/BPE action tokenizer used by FAST model variants.

<a id="lerobot-relative-action-floor"></a>
### [LeRobot relative-action support has a version floor](https://github.com/huggingface/lerobot/pull/2970)

docs · hardware use reported

Relative-action processors and flags require a compatible LeRobot revision; the recorded implementation arrived through PR #2970.

<a id="vram-boundary-counterevidence"></a>
### [LoRA — practical memory limits](https://github.com/Physical-Intelligence/openpi/issues/379)

discussion · research

User reports show a nominal LoRA memory requirement can still exceed a 24 GB GPU in specific configurations.

<a id="fine-tune-cost-anchor"></a>
### [Fine-tuning cost example](https://docs.picknik.ai/how_to/vla/train_a_vla_policy/)

blog · hardware use reported

A documented fine-tuning run provides a historical cost example; billing depends on provider, hardware, duration and current rates.

<a id="multi-gpu-not-auto-scaled"></a>
### [Distributed training configuration](https://github.com/huggingface/lerobot/blob/main/docs/source/multi_gpu_training.mdx)

docs · hardware use reported

Distributed training does not automatically rescale learning rate or step count; DDP normally replicates model state per device.

<a id="demos-is-the-wrong-unit"></a>
### [Demonstration volume and coverage](https://github.com/huggingface/lerobot/blob/main/docs/source/il_robots.mdx)

docs · research

Record episode count together with duration, control frequency and task coverage; equal episode counts can represent different amounts of data.

<a id="aalto-execution-horizon"></a>
### [Execution-horizon paired comparison](https://aaltodoc.aalto.fi/items/711175d6-6d75-4751-af72-b055bd8cd4db/full)

benchmark · research

A paired-trial study compares execution horizons; its optimum is specific to the tested checkpoints and tasks.

<a id="openvla-demo-replay"></a>
### [OpenVLA — LIBERO demonstration replay](https://arxiv.org/abs/2406.09246)

paper · hardware use reported

OpenVLA authors replayed LIBERO demonstrations and removed episodes that did not satisfy the task success criterion.

<a id="checkpoint-write-oom"></a>
### [Checkpoint-saving memory failure](https://github.com/moojink/openvla-oft/issues/118)

discussion · research

A training run can run out of memory during checkpoint saving even when ordinary training steps fit.

<a id="deployment"></a>
## Deployment and runtime

Connect policy inference to observation and robot control.

<a id="eapn-execution-aligned-replanning"></a>
### [EAPN — execution-aligned asynchronous replanning](https://arxiv.org/abs/2610.06090)

paper · research

Aligns correlated noise and committed actions across replanning steps to improve action-chunk continuation.

**Use conditions：** Preprint; the implementation and hardware results have not been reproduced in this repository.

<a id="rephrase-before-you-act"></a>
### [Rephrase Before You Act — instruction normalization for a frozen VLA](https://arxiv.org/abs/2610.10526)

paper · research

Distills instruction-rephrasing rules from training-task evaluations and rewrites input instructions for a frozen policy.

**Use conditions：** Evaluate whether rewriting preserves user intent. Linked code artifacts were inspected, but reuse licensing and end-to-end reproduction remain unverified.

Additional sources: [↗ 1](https://sttawm.github.io/rephrase-before-you-act/) · [↗ 2](https://github.com/sttawm/phrase-rl)

<a id="ogam-runtime-monitor"></a>
### [OGAM — object-grounded attention monitoring](https://arxiv.org/abs/2610.05878)

paper · research

Compares object-grounded attention against successful reference episodes to trigger early stopping; requires attention access and calibration data.

**Use conditions：** Needs object masks and successful reference/calibration episodes. Reported stopping performance is protocol-specific, not a general safety guarantee.

<a id="lerobot-rtc-modes"></a>
### [LeRobot — guided vs trained RTC and checkpoint delay limits](https://github.com/huggingface/lerobot/blob/main/docs/source/rtc.mdx)

docs · research · Apache-2.0

Documents guided RTC and trained prefix conditioning. Trained mode requires a compatible checkpoint trained with a positive maximum delay.

**Use conditions：** For trained mode, execution_horizon and inference.queue_threshold must cover the checkpoint maximum training delay; the execution horizon must not exceed chunk_size minus that delay. Pin code and documentation together.

<a id="lerobot-inference"></a>
### [LeRobot — Policy Deployment (lerobot-rollout)](https://huggingface.co/docs/lerobot/en/inference)

docs · hardware use reported · Apache-2.0

Official deployment guide for rollout strategies, execution horizons and runtime subtask interfaces.

<a id="rtc"></a>
### [Real-Time Execution of Action Chunking Flow Policies (RTC)](https://neurips.cc/virtual/2025/loc/san-diego/poster/117747)

paper · research

Conditions asynchronously generated action chunks on committed actions to improve continuity during execution.

<a id="vla-rail"></a>
### [VLA-RAIL: A Real-Time Asynchronous Inference Linker for VLA Models and Robots](https://arxiv.org/abs/2512.24673)

paper · research

Decouples model inference from the robot control loop through an asynchronous linker.

<a id="world-action-models-real-time"></a>
### [World Action Models in Real Time: An Empirical Study of Smooth Execution via Asynchronous Deployment](https://arxiv.org/abs/2608.01880)

paper · research

Empirical study of smooth motion under asynchronous deployment of world-action models.

<a id="holobrain-0"></a>
### [HoloBrain-0 Technical Report](https://arxiv.org/abs/2602.12062)

paper · research

Technical report including timing limitations of synchronous full-chunk execution.

<a id="vla-cpp"></a>
### [vla.cpp: A Unified Inference Runtime for Vision-Language-Action Models](https://arxiv.org/abs/2606.08094)

paper · research

Inference runtime designed for vision-language-action models.

<a id="eva-client"></a>
### [EVA-Client](https://github.com/Noietch/EVA-CLIENT)

repo · research

Framework for deployment, evaluation and data collection across robot platforms.

<a id="eva-client-paper"></a>
### [EVA-Client (paper)](https://arxiv.org/abs/2607.02646)

paper · research

Paper describing the EVA-Client robot deployment and evaluation framework.

<a id="robot-control-stack"></a>
### [robot-control-stack](https://github.com/RobotControlStack/robot-control-stack)

repo · research

ROS-independent stack for deploying learned policies from simulation to robots.

<a id="minivla"></a>
### [MiniVLA](https://github.com/Zhenxintao/MiniVLA)

repo · demo

Compact VLA implementation targeting TensorRT edge inference.

<a id="embodirun"></a>
### [EmbodiRun](https://github.com/BUAA-CI-LAB/EmbodiRun)

repo · demo

Execution runtime for embodied policies.

<a id="factory-floor-case-study"></a>
### [A Factory-Floor Deployment Case Study of VLA Pipelines for Industrial Packaging](https://arxiv.org/abs/2605.27461)

paper · research

Industrial packaging deployment case study describing VLA workflows and observed failures.

<a id="pi0-deploy-notes"></a>
### [pi0 fine-tuning guide with domestic-arm deployment (Chinese)](https://zeeklog.com/p0de-wei-diao-ru-he-ji-yu-ge-chong-kai-yuan-shu-ju-ji-yi-ji-si-you-shu-ju-ji-wei-diao-openpi-han-wo-si-qi-yue-de-wei-diao-shi-jian-ji-openpizai-guo-chan-bi-shang-de-bu-shu-8)

blog · research

Chinese walkthrough of openpi fine-tuning and deployment on a robot arm.

<a id="lerobot-rtc-docs"></a>
### [LeRobot — Real-Time Chunking reference](https://github.com/huggingface/lerobot/blob/main/docs/source/rtc.mdx)

docs · hardware use reported

Reference for RTC execution horizon, guidance weight, prefix attention and inference delay.

<a id="lerobot-async"></a>
### [LeRobot — legacy asynchronous inference (pinned reference)](https://github.com/huggingface/lerobot/blob/7e60cd26f7f8a38bb8df8fc5e2966a93f1364f47/docs/source/async.mdx)

docs · archived reference

Policy-server and robot-client implementation for asynchronous inference and action delivery.

**Use conditions：** Historical PolicyServer/RobotClient documentation. Current main retired this legacy module in favor of remote inference under rollout; use matching code and documentation versions.

Additional sources: [↗ 1](https://github.com/huggingface/lerobot/blob/main/docs/source/inference.mdx)

<a id="lerobot-rollout"></a>
### [LeRobot — rollout strategies and fleet operations](https://github.com/huggingface/lerobot/blob/main/docs/source/inference.mdx)

docs · hardware use reported

Rollout modes supporting autonomous operation, recording, incident capture and human intervention.

<a id="lerobot-hil"></a>
### [LeRobot — human-in-the-loop data collection](https://github.com/huggingface/lerobot/blob/main/docs/source/hil_data_collection.mdx)

docs · hardware use reported

Collects human corrections during policy execution.

<a id="ros2-control-trajectory"></a>
### [ros2_control — joint_trajectory_controller](https://control.ros.org/rolling/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html)

docs · hardware use reported

Interpolates joint trajectories; limit enforcement depends on the complete controller and hardware configuration.

<a id="ros2-control-admittance"></a>
### [ros2_control — admittance_controller](https://control.ros.org/rolling/doc/ros2_controllers/admittance_controller/doc/userdoc.html)

docs · hardware use reported

Admittance controller that adjusts commanded motion in response to measured forces.

<a id="ros2-control-gripper"></a>
### [ros2_control — parallel_gripper_controller](https://control.ros.org/jazzy/doc/ros2_controllers/parallel_gripper_controller/doc/userdoc.html)

docs · hardware use reported

Standard command interface for parallel grippers.

<a id="neural-controller"></a>
### [G-Levine/neural_controller](https://github.com/G-Levine/neural_controller)

repo · research

Integrates a learned policy into a ros2_control controller manager.

<a id="xbotics-ch13"></a>
### [Xbotics 具身智能教程 第13讲 — real-time VLA inference (Chinese)](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/13-VLA%E5%89%8D%E6%B2%BF.md)

blog · research

Chinese lesson on first-action latency, chunk stalls and real-time chunking, with worked examples.

<a id="faster"></a>
### [FASTER: Rethinking Real-Time Flow VLAs](https://arxiv.org/abs/2603.19199)

paper · research

Studies denoising schedules for reducing flow-policy reaction latency.

<a id="legato"></a>
### [Legato: Learning Native Continuation for Action Chunking Flow Policies](https://arxiv.org/abs/2602.12978)

paper · research

Learns native continuation of action chunks instead of regenerating an entire plan each time.

<a id="delay-aware-diffusion"></a>
### [Delay-Aware Diffusion Policy](https://arxiv.org/abs/2512.07697)

paper · research

Trains diffusion policies under a range of delays to account for stale observations.

<a id="speculative-policy-orchestration"></a>
### [Speculative Policy Orchestration: A Latency-Resilient Framework for Cloud-Robotic Manipulation](https://arxiv.org/abs/2603.19418)

paper · research

Cloud-robot policy orchestration addressing network delay, jitter and command starvation.

<a id="roboecc"></a>
### [RoboECC: Multi-Factor-Aware Edge-Cloud Collaborative Deployment for VLA Models](https://arxiv.org/abs/2603.20711)

paper · research

Studies how to divide VLA computation between edge devices and the cloud.

<a id="comvla"></a>
### [ComVLA: Communication-Aware Split Inference for VLA Models in 6G-Connected Robotics](https://arxiv.org/abs/2609.07838)

paper · research

Communication-aware split inference for bandwidth-constrained robot systems.

<a id="viam-calibration-worksheet"></a>
### [Frame calibration worksheet](https://github.com/viam-devrel/pick-and-place/blob/main/setup/frame-calibration-worksheet.md)

docs · hardware use reported

Worksheet for recording robot coordinate-frame calibration.

<a id="ros2-control-mock"></a>
### [ros2_control — mock components](https://control.ros.org/jazzy/doc/ros2_control/hardware_interface/doc/mock_components_userdoc.html)

docs · hardware use reported

Mock hardware components for exercising controllers without a physical robot.

<a id="ros2-tracing"></a>
### [ros2_tracing](https://github.com/ros2/ros2_tracing)

repo · hardware use reported

ROS 2 tracing tools built on LTTng for measuring execution and communication events.

<a id="tensorrt-dev-guide"></a>
### [NVIDIA TensorRT Developer Guide](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html)

docs · hardware use reported

TensorRT reference for operators, precision, dynamic shapes and plugins.

<a id="benchmarks"></a>
## Latency and optimization measurements

Reported measurements under specified hardware and protocols.

<a id="flashrt-benchmark-table"></a>
### [FlashRT — cross-source latency table (π0.5, GR00T N1.6)](https://github.com/flashrt-project/FlashRT/blob/main/docs/benchmark_comparison.md)

benchmark · research

Cross-source VLA latency results; compare only rows with matching hardware, model and timing boundaries.

**Use conditions：** Reported speedups across different timing boundaries are not directly comparable. Separate initialization, first inference and steady state.

<a id="flashrt"></a>
### [FlashRT — small-batch realtime inference engine](https://github.com/flashrt-project/FlashRT)

repo · research

CUDA inference engine for small-batch VLA policies, including pi0, pi0.5 and GR00T N1.6.

<a id="nvidia-forum-thor-rtx"></a>
### [NVIDIA Developer Forum — real measured π0.5 / GR00T latency on Thor and RTX 5090](https://forums.developer.nvidia.com/t/real-time-inference-on-thor-rtx-pi0-5-gr00t-n1-6-1-7-thor-23-hz-rtx-5090-50-80hz/368788)

discussion · hardware use reported

Developer measurements for pi0.5 and GR00T on Jetson Thor and RTX 5090; results belong to the reported configurations.

<a id="groot-optimization-docs"></a>
### [Isaac GR00T — official deployment optimisation numbers](https://nvidia-isaac-gr00t.mintlify.app/deployment/optimization)

docs · hardware use reported

Vendor measurements comparing eager PyTorch, compilation and TensorRT for GR00T N1.6 on several GPUs.

<a id="embodied-efficiency"></a>
### [embodied-efficiency — batch-1 optimization experiments](https://github.com/LaelaZorana/embodied-efficiency)

benchmark · research

An experiment reports weight-only INT8/INT4 slower than BF16 at batch size 1; also examines CUDA graphs and action staleness.

<a id="jetson-pi"></a>
### [Jetson-PI — onboard async VLA inference](https://github.com/PKU-SEC-Lab/Jetson-PI)

repo · research

Onboard asynchronous VLA inference on Jetson; effective control frequency and inference frequency are different metrics.

<a id="xpu-characterization"></a>
### [Characterizing VLA Models across XPUs](https://arxiv.org/abs/2604.24447)

paper · research

Breaks VLA latency into vision, language-prefix and action-expert stages across GPU and edge devices.

<a id="foldquantvla"></a>
### [FoldQuantVLA — native low-bit quantisation for VLAs](https://arxiv.org/abs/2609.24433)

paper · research

Low-bit quantization designed for VLA internals using consistent folding.

<a id="open-loop-revisited"></a>
### [Revisiting Open-Loop Execution in Robotics](https://arxiv.org/abs/2608.15938)

paper · research

Studies the task-performance trade-off between open-loop execution and frequent replanning.

<a id="ros2-wireless"></a>
### [Optimizing ROS 2 Communication for Wireless Robotic Systems](https://arxiv.org/abs/2508.11366)

paper · research

Measures ROS 2 latency and throughput over wireless links, including back-pressure and DDS configuration.

<a id="evaluation"></a>
## Evaluation

Task protocols, sample counts and failure analysis.

<a id="vla-eval-harness"></a>
### [allenai/vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)

repo · research

Unified harness for evaluating VLA policies across environments.

<a id="simplerenv"></a>
### [SimplerEnv](https://github.com/simpler-env/SimplerEnv)

repo · research

Simulation environments for studying manipulation-policy transfer to real robots.

<a id="robocasa"></a>
### [RoboCasa](https://github.com/robocasa/robocasa)

repo · research

Kitchen manipulation simulation tasks for evaluating general-purpose robot behavior.

<a id="eval-statistical-bounds"></a>
### [Statistical lower bounds on behavior-cloning success probability](https://arxiv.org/abs/2405.05439)

paper · research

Statistical methods for lower bounds on behavior-cloning success probability from limited trials.

<a id="phail-benchmark"></a>
### [PhAIL: A Real-Robot VLA Benchmark and Distributional Methodology](https://arxiv.org/abs/2605.29710)

paper · research

Real-robot VLA benchmark with distributional evaluation and uncertainty reporting.

<a id="eval-optimal-stopping"></a>
### [Near-optimal stopping in the 10-50 trial regime](https://arxiv.org/abs/2503.10966)

paper · research

Studies evaluation stopping rules when only a small number of robot trials is available.

<a id="libero-reproduction-gap"></a>
### [LIBERO — evaluation-budget differences](https://arxiv.org/abs/2506.01844)

paper · research

Compares paper-level trial budgets with LIBERO configuration defaults; the same benchmark name does not imply the same protocol.

<a id="score-the-steps"></a>
### [Score the Steps, Not Just the Goal — subgoal-level evaluation](https://arxiv.org/abs/2509.19524)

paper · research

Uses a VLM to assess subgoal progress rather than only the final task outcome.

<a id="failure-taxonomy-cluster"></a>
### [Failure taxonomies for manipulation — five groups, five different label sets](https://arxiv.org/abs/2512.01946)

paper · research

Resources covering planning errors, execution quality, proprioceptive diagnosis, interpretable failure labels and recovery benchmarks.

<a id="robotwin2"></a>
### [RoboTwin 2.0](https://robotwin-platform.github.io/)

benchmark · research

Bimanual manipulation benchmark with domain randomization.

<a id="evaluation-resolution"></a>
### [Evaluation sample-size example](https://github.com/Physical-Intelligence/openpi)

discussion · research

A reported checkpoint received different success estimates at 10 and 50 trials; report sample size and uncertainty together.

<a id="libero-three-numbers"></a>
### [Three different 'official' LIBERO evaluation protocols](https://arxiv.org/abs/2506.01844)

paper · research

Distinguishes LIBERO initial states, default evaluation count and paper-level repeated-trial protocols.

<a id="counter-evidence"></a>
## Reported failure cases

Observed limitations in particular tasks and configurations.

<a id="language-grounding-gap"></a>
### [Language-grounding interventions](https://arxiv.org/abs/2610.06235)

paper · research

Changing a valid target instruction while holding the scene fixed can reveal a policy that follows scene correlations rather than the requested target.

**Use conditions：** Findings apply to the tested policies and protocol; the source reports both simulation and real-robot experiments.

<a id="oft-hardware-drift"></a>
### [OpenVLA-OFT — hardware drift report](https://openvla-oft.github.io/)

blog · hardware use reported

OpenVLA-OFT authors report degradation after wrist-camera pose changes and joint wear, despite unchanged code and training data.

<a id="picknik-loss-curve"></a>
### [PickNik — training loss and rollout evaluation](https://docs.picknik.ai/how_to/vla/train_a_vla_policy/)

docs · hardware use reported

A training runbook explains that low demonstration loss without held-out evaluation does not establish closed-loop task success.

<a id="oft-more-data-did-not-fix-it"></a>
### [OpenVLA-OFT — language-grounding data experiment](https://openvla-oft.github.io/)

blog · hardware use reported

In a reported OpenVLA-OFT task, doubling or quadrupling demonstrations did not resolve language grounding; conditioning changes were also needed.

<a id="lerobot-25-episodes-failed"></a>
### [SmolVLA — demonstration-count comparison](https://github.com/huggingface/lerobot/blob/main/docs/source/smolvla.mdx)

docs · hardware use reported

SmolVLA documentation reports poor performance with 25 episodes in a cube task and a better result with 50; this is a task-specific comparison.

<a id="lerobot-50-is-a-floor"></a>
### [LeRobot — demonstration coverage guidance](https://github.com/huggingface/lerobot/issues/2378)

discussion · hardware use reported

LeRobot guidance discusses starting with about 50 demonstrations for a fixed-location task and increasing coverage as objects or positions vary.

<a id="pi0-authors-hedge"></a>
### [openpi — embodiment-transfer limitations](https://github.com/Physical-Intelligence/openpi)

docs · hardware use reported

openpi documents embodiment differences between its training robots and other platforms; successful transfer is not guaranteed.

<a id="oft-copies-bad-demos"></a>
### [OpenVLA-OFT — demonstration-quality report](https://openvla-oft.github.io/)

blog · hardware use reported

A reported scooping experiment shows a learned policy reproducing excessive insertion depth present in suboptimal demonstrations.

<a id="sim-benchmarks-hid-the-problem"></a>
### [OpenVLA — Franka deployment case study](https://openaccess.thecvf.com/content/CVPR2026W/MEIS/html/Liu_Bridging_the_Pretrain-to-Real_Gap_Alignment_Challenges_in_Deploying_Generalist_VLA_CVPRW_2026_paper.html)

paper · research

A real Franka Research 3 deployment of OpenVLA required decoding, gripper-threshold and geometric adaptations beyond simulation evaluation.

<a id="openvla-100-demos"></a>
### [OpenVLA — fine-tuning data guidance](https://github.com/openvla/openvla/issues/12)

discussion · research

OpenVLA authors describe approximately 100 demonstrations for a fine-tuning setup; token accuracy remains separate from rollout success.

<a id="smolvla-pretraining-payoff"></a>
### [SmolVLA — pretraining comparison](https://arxiv.org/abs/2506.01844)

paper · research

The SmolVLA paper reports higher SO100 task success after community-data pretraining under its experimental protocol.

<a id="position-beats-velocity"></a>
### [Diffusion Policy — position and velocity control](https://arxiv.org/abs/2303.04137)

paper · hardware use reported

Diffusion Policy reports position control outperforming velocity control in its tested tasks, with different sensitivity to latency.

<a id="safety"></a>
## Runtime monitoring and protection

Monitoring methods and engineering references; research monitors are not safety certification.

<a id="dguv-ifa-cobot"></a>
### [DGUV/IFA — collaborative robot safety (readable interpretation)](https://www.dguv.de/ifa/fachinfos/kollaborierende-roboter/index-2.jsp)

standard · hardware use reported

DGUV/IFA information on collaborative-robot hazards and protective measures; applicability depends on the system and task.

<a id="iso-21448-sotif"></a>
### [ISO 21448 — Safety of the Intended Functionality (SOTIF)](https://www.bsigroup.com/en-GB/standards/iso-21448/)

standard · hardware use reported

SOTIF is a road-vehicle standard on hazards from functional insufficiency; it is conceptual background, not a general robot certification rule.

**Use conditions：** Scope is road vehicles; do not present this reference as a required standard for every robot.

<a id="hide-and-seek-trajectories"></a>
### [Hide-and-Seek in Trajectories: Discovering Failure Signals for VLA Runtime Monitoring](https://arxiv.org/abs/2605.30834)

paper · research

Studies failure signals in policy trajectories for runtime monitoring.

<a id="safecast"></a>
### [SAFECAST: Robust Failure Detection for VLA Policies](https://arxiv.org/abs/2608.04246)

paper · research

Studies calibrated failure detection under visual and instruction distribution shifts.

<a id="rafail"></a>
### [RAFAIL: Relationship-Aware Failure Detection for Robotic Manipulation](https://arxiv.org/abs/2609.18324)

paper · research

Combines relational semantic checks with faster out-of-distribution signals for manipulation failure detection.

<a id="rewind-il"></a>
### [Rewind-IL: Online Failure Detection and State Respawning for Imitation Learning](https://arxiv.org/abs/2604.16683)

paper · research

Combines online failure detection with state respawning in imitation-learning tasks.

<a id="nvidia-halos"></a>
### [NVIDIA Halos for robotics](https://developer.nvidia.com/blog/inside-nvidia-halos-for-robotics-a-full-stack-functional-safety-system-for-physical-ai/)

docs · hardware use reported

Vendor architecture for functional safety in physical-AI systems; individual components do not certify a complete deployment.

<a id="mender-ota"></a>
### [Mender — open-source OTA updates with rollback](https://mender.io/)

tool · hardware use reported

Software update infrastructure with rollback support.

<a id="licensing"></a>
## License references

Check source data, code, weights and dependencies separately.

<a id="pi0-license-contradiction"></a>
### [pi0/pi0.5 — recorded license-metadata discrepancy](https://huggingface.co/api/models/lerobot/pi05_base)

docs · hardware use reported

A recorded discrepancy between model-card metadata and documentation for pi0/pi0.5 weights; consult the applicable license files for the chosen revision.

**Use conditions：** The recorded check is historical. Resolve metadata/documentation discrepancies using the actual license and model revision before reuse.

<a id="verify-license-from-api"></a>
### [Hugging Face — license metadata](https://huggingface.co/api/models/lerobot/pi05_base)

docs · hardware use reported

Hub API metadata helps locate declared model and dataset licenses; metadata is not a substitute for the actual license terms.

<a id="dataset-license-spectrum"></a>
### [Dataset license references](https://huggingface.co/api/datasets/RogerQi/PH2D)

gap · research

Dataset licenses differ across source data, derived data and redistribution; examine each component of a training mixture.

<a id="learning-resources"></a>
## Further learning

Courses, handbooks and topic indexes.

<a id="vla-handbook"></a>
### [sou350121/VLA-Handbook](https://github.com/sou350121/VLA-Handbook)

list · hardware use reported · unknown

Chinese handbook on VLA models, robot hardware and deployment.

<a id="awesome-embodied-vla-va-vln"></a>
### [jonyzhang2023/awesome-embodied-vla-va-vln](https://github.com/jonyzhang2023/awesome-embodied-vla-va-vln)

list · hardware use reported

Index of vision-language-action, vision-action and vision-language-navigation research.

<a id="gt-ripl-awesome-llm-robotics"></a>
### [GT-RIPL/Awesome-LLM-Robotics](https://github.com/GT-RIPL/Awesome-LLM-Robotics)

list · hardware use reported

Index of language-model applications in robotics.

<a id="awesome-humanoid-robot-learning"></a>
### [YanjieZe/awesome-humanoid-robot-learning](https://github.com/YanjieZe/awesome-humanoid-robot-learning)

list · hardware use reported

Index of humanoid robot learning, teleoperation and hardware research.

<a id="awesome-physical-ai-natnew"></a>
### [natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai)

list · hardware use reported

Index of physical-AI middleware, system architecture and related standards.

<a id="aidaslab-data-curation"></a>
### [AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation)

list · research

Paper index on robot data collection, cleaning, annotation and augmentation.

<a id="awesome-robot-data-engine"></a>
### [chang-xinhai/Awesome-Robot-Data-Engine](https://github.com/chang-xinhai/Awesome-Robot-Data-Engine)

list · research

Resources on robot data collection, processing, formats and mixing.

<a id="awesome-long-horizon-robot-manipulation"></a>
### [Ziteng-Wang/Awesome-Long-Horizon-Robot-Manipulation](https://github.com/Ziteng-Wang/Awesome-Long-Horizon-Robot-Manipulation)

list · research

Resources on long-horizon manipulation, memory, progress and recovery.

<a id="awesome-vla-yueen-ma"></a>
### [yueen-ma/Awesome-VLA](https://github.com/yueen-ma/Awesome-VLA)

list · hardware use reported

VLA paper index accompanying a survey.

<a id="awesome-rl-vla"></a>
### [Denghaoyuan123/Awesome-RL-VLA](https://github.com/Denghaoyuan123/Awesome-RL-VLA)

list · research

Resources on reinforcement-learning post-training of VLA models.

<a id="every-embodied"></a>
### [datawhalechina/every-embodied](https://github.com/datawhalechina/every-embodied)

list · hardware use reported

Chinese beginner course with hands-on embodied-robot projects.

<a id="xbotics-handbook"></a>
### [Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook)

list · hardware use reported

Chinese course spanning perception, control, data, training and deployment.

<a id="action-diffusion-handbook"></a>
### [AlmondGod/action-diffusion-handbook](https://github.com/AlmondGod/action-diffusion-handbook)

list · research

Handbook covering action diffusion and related robot-policy architectures.
