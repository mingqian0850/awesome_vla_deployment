<div align="center">

# awesome-vla-deployment

**How to make a VLA policy actually run on a real robot.**

Not another paper index. Data collection, annotation, cleaning and sub-task segmentation;
training recipes with numbers; and the deployment engineering — latency, chunking,
quantisation, edge hardware, safety layers — that decides whether any of it works outside
the lab.

156 entries · 61 production · 82 research · 9 toy · 4 abandoned

</div>

---

> ### ⚠️ One list in this space should not be used
>
> [`keon/awesome-physical-ai`](https://github.com/keon/awesome-physical-ai) (433 stars) is the
> only curated list here with a literal `## Deployment` section, so search engines surface it
> first when you look for deployment material. **Its Deployment and Safety sections contain 27
> fabricated placeholder arXiv IDs** (`2505.XXXXX`, `2512.XXXXX`) attached to real-looking
> paper names. A `grep -c XXXXX` over the file returns 27; over 32 other READMEs in this space
> it returns 0. It last saw a commit in June 2026.
>
> It is listed in the [Landscape](#landscape--what-already-exists) section, dated and
> labelled, rather than quietly omitted — because you will find it, and you need to know.

## The problem this repo solves

If you are training a VLA model, the papers are not your bottleneck. Your bottleneck is that
the robot does the first motion of your chained task and then stops, that nobody has written
down which normalisation statistics broke the policy when you changed arms, and that the
only place your exact failure mode has ever been discussed is a Chinese blog post and a
closed GitHub issue.

So this repo is organised around **problems, not publications**. Every troubleshooting entry
is symptom → ranked candidate causes → a test you can run in under an hour → the fix. Where a
number appears, it names the hardware.

## What we do not do

To avoid duplicating work that already exists, we deliberately do not cover:

| Not here | Go here instead |
|---|---|
| Model architecture tutorials, paper summaries | [VLA-Handbook](https://github.com/sou350121/VLA-Handbook) (Chinese, 662★), [Awesome-VLA](https://github.com/yueen-ma/Awesome-VLA) |
| Beginner "what is embodied AI" curricula | [every-embodied](https://github.com/datawhalechina/every-embodied), [Xbotics Handbook](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook) (Chinese) |
| Paper-level curation of data cleaning / annotation | [AIDASLab](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation), [Awesome-Robot-Data-Engine](https://github.com/chang-xinhai/Awesome-Robot-Data-Engine) |
| Middleware and standards catalogues | [natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai) |

See the [Landscape](#landscape--what-already-exists) section for the full picture, including
which lists are dead.

## How to read the entries

Every entry carries a `maturity` that says how much you can trust it, and a `verified` date
that says when a human last opened the link.

| maturity | meaning |
|---|---|
| `production` | runs on real hardware, actively maintained |
| `research` | works in a lab, expect to adapt it |
| `toy` | demo-grade, do not plan around it |
| `abandoned` | no commits for ~12 months — **kept and dated on purpose**, because a graveyard is information |

## Provenance

1. Every URL is machine-checked. `scripts/check_links.py` runs on every push and weekly on a
   schedule; a dead link fails the build.
2. No fabricated references. Placeholder or unresolvable paper IDs are treated as a bug.
3. Numbers are attributed to named hardware and model. "Faster" without a number is rejected.
4. Negative results are wanted. "We tried INT8 and the policy broke" is a finding.
5. `verified` is a claim about a human having opened the link, not a timestamp bump.

## The written guides

The hand-written pages, where the parts that no link can give you live:

| Guide | What is in it |
|---|---|
| [The safety layer](docs/43-safety.md) | Why a learned policy cannot be a safety function, the six layers, and how ISO 12100 / 10218 / TS 15066 / 13849 map onto a VLA inference loop |
| [Real-time inference](docs/41-real-time-inference.md) | The latency budget arithmetic — feasibility condition, observation-age equation, and the three execution strategies |
| [The optimisation matrix](docs/40-optimization-matrix.md) | What to measure and how, so your numbers are comparable with someone else's |
| [Checklist: before collecting data](checklists/before-collecting-data.md) | The decisions that are cheap now and expensive later |
| [Checklist: before a policy drives anything](checklists/before-deploying.md) | Print it and tick it in front of the robot |

## Quick start

| You are... | Start at |
|---|---|
| about to collect your first dataset | [Data](#data--collection-annotation-cleaning-segmentation), then [Counter-evidence](#counter-evidence--what-did-not-work-and-what-stops-working) for how much data people actually needed |
| stuck: the policy does the first motion then stops | [Troubleshooting](#troubleshooting--symptom-to-root-cause-to-fix) |
| fine-tuning pi0.5 on your own arm | [Training](#training--frameworks-recipes-action-representations) and [Training recipes](#training-recipes--the-numbers) |
| deciding what hardware to buy | [Training recipes](#training-recipes--the-numbers) — the VRAM matrix is published |
| moving from a working demo to a real deployment | [Deployment](#deployment--inference-timing-optimisation-edge-integration) and [Real-time inference](docs/41-real-time-inference.md) |
| trying to get a number you can trust | [Evaluation](#evaluation) and [Optimisation matrix](docs/40-optimization-matrix.md) |
| looking for a number nobody has published | [Deployment benchmarks](#deployment-benchmarks--measured-not-cited) — documented gaps with reasons |
| about to conclude your data is the problem | [Counter-evidence](#counter-evidence--what-did-not-work-and-what-stops-working) — nine documented failures, including one where more data was explicitly not the fix |

---

## Contents

- [Landscape — what already exists](#landscape--what-already-exists)
- [Data — collection, annotation, cleaning, segmentation](#data--collection-annotation-cleaning-segmentation)
- [Training — frameworks, recipes, action representations](#training--frameworks-recipes-action-representations)
- [Training recipes — the numbers](#training-recipes--the-numbers)
- [Deployment — inference timing, optimisation, edge, integration](#deployment--inference-timing-optimisation-edge-integration)
- [Safety and runtime monitoring](#safety-and-runtime-monitoring)
- [Deployment benchmarks — measured, not cited](#deployment-benchmarks--measured-not-cited)
- [Evaluation](#evaluation)
- [Counter-evidence — what did not work, and what stops working](#counter-evidence--what-did-not-work-and-what-stops-working)
- [Troubleshooting — symptom to root cause to fix](#troubleshooting--symptom-to-root-cause-to-fix)
  - [The policy executes the first sub-task of a chained task, then stalls or](#the-policy-executes-the-first-sub-task-of-a-chained-task-then-stalls-or-repeats-it--regardless-of-the-initial-state)
  - [The robot hesitates or does not move at the beginning of a rollout, then](#the-robot-hesitates-or-does-not-move-at-the-beginning-of-a-rollout-then-behaves-normally)
  - [Motion is jerky, or the robot moves in short bursts with pauses between ](#motion-is-jerky-or-the-robot-moves-in-short-bursts-with-pauses-between-them)
  - [Only the first step or two of each predicted action chunk look correct; ](#only-the-first-step-or-two-of-each-predicted-action-chunk-look-correct-the-rest-is-wrong)
  - [Changing the language instruction has no effect on behaviour.](#changing-the-language-instruction-has-no-effect-on-behaviour)
  - [The policy works on the robot it was trained on and fails completely on ](#the-policy-works-on-the-robot-it-was-trained-on-and-fails-completely-on-a-different-arm-or-gripper)
  - [Excellent success rate in simulation, poor on hardware.](#excellent-success-rate-in-simulation-poor-on-hardware)
  - [Success rate moves by 20 points between evaluation runs with no code cha](#success-rate-moves-by-20-points-between-evaluation-runs-with-no-code-change)
  - [The policy behaves as if your configuration changes had no effect.](#the-policy-behaves-as-if-your-configuration-changes-had-no-effect)
  - [Training runs and loss decreases, but the policy behaves as if the data ](#training-runs-and-loss-decreases-but-the-policy-behaves-as-if-the-data-were-never-normalized--or-normalization-appears-to-do-nothing-at-all)
  - [Fine-tuning runs to completion and the loss decreases normally, but succ](#fine-tuning-runs-to-completion-and-the-loss-decreases-normally-but-success-rate-is-at-or-near-zero)
  - [Training collapses, produces NaNs, or the loss is orders of magnitude wr](#training-collapses-produces-nans-or-the-loss-is-orders-of-magnitude-wrong--with-no-obvious-change-to-the-data)

## Landscape — what already exists

Read this before adding anything. Most of the VLA space is already curated; this repo only exists because one specific slice is not. Linking to these instead of duplicating them is the difference between a useful list and noise. Star counts and last-commit dates are a 2026-09 snapshot.

- **[keon/awesome-physical-ai](https://github.com/keon/awesome-physical-ai)** — `list` · `abandoned` · `unknown` · verified 2026-09 · #trap #do-not-cite
  - *What it is:* 433 stars. The only curated list in this space with a literal `## Deployment` section (Quantization & Compression, Real-Time Control) plus `## Safety & Alignment`.
  - *Why it matters here:* DO NOT USE. It is the single most likely trap for a reader looking for deployment material.
  - *Note:* Verified on 2026-09-29: the Deployment and Safety sections contain 27 fabricated placeholder arXiv IDs of the form `2505.XXXXX` / `2512.XXXXX`, attached to real-looking names (BitVLA, QuaRT-VLA, RTC, ASIMOV, RoboGuard). `grep -c XXXXX` on this file returns 27; the same grep across 32 other READMEs in this space returns 0. The content reads as LLM-generated. Last commit 2026-06-24. Kept here, dated and labelled, because a reader will find it and needs to know.
- **[sou350121/VLA-Handbook](https://github.com/sou350121/VLA-Handbook)** — `list` · `production` · `unknown` · verified 2026-09 · #competitor #chinese #handbook #deployment
  - *What it is:* 662 stars, Chinese, updated daily by a cron pipeline. ~525 theory docs plus a deployment/ tree: hardware selection *with pricing*, ROS2 zero-copy/DDS tuning, edge deployment (GPTQ/AWQ, TensorRT-LLM, vLLM), agentic VLA layering with latency budgets, camera calibration, multimodal sync, UR5 ur_rtde realtime kernel, GELLO teleop, pi0 deployment, dexterous-hand CANFD/EtherCAT, sim2real.
  - *Why it matters here:* This is the closest thing to an existing occupant of our niche, and it proves the niche is real. It is 100% Chinese, which is exactly why an English-first equivalent is worth building. Read it if you read Chinese; it is strictly ahead of us on hardware specifics. Our differentiation is English reach, verified provenance, and measured numbers.
  - *Note:* Also distils 300+ Xiaohongshu posts, 165 English blogs, 135 LeRobot Discord threads and 200+ GitHub issues, including a GPU compatibility matrix (RTX50/Jetson), pi0 fine-tune traps, GR00T VRAM requirements, and convergence-failure root causes.
- **[jonyzhang2023/awesome-embodied-vla-va-vln](https://github.com/jonyzhang2023/awesome-embodied-vla-va-vln)** — `list` · `production` · verified 2026-09 · #papers #index
  - *What it is:* 3.5k stars. The largest paper index for VLA / VLN / VA / world-action models, organised by year, with Sim-to-Real, Benchmarks and Simulators sections.
  - *Why it matters here:* Use it to find papers. It has essentially no engineering content — its 'quantization' hits are paper titles, not tooling.
- **[GT-RIPL/Awesome-LLM-Robotics](https://github.com/GT-RIPL/Awesome-LLM-Robotics)** — `list` · `production` · verified 2026-09 · #papers #index #llm
  - *What it is:* 4.5k stars. LLM/VLM-for-robotics papers grouped by task.
  - *Why it matters here:* Background reading for the language side of VLA.
- **[YanjieZe/awesome-humanoid-robot-learning](https://github.com/YanjieZe/awesome-humanoid-robot-learning)** — `list` · `production` · verified 2026-09 · #humanoid #teleoperation #hardware
  - *What it is:* 2.8k stars. Humanoid papers with dedicated `## Teleoperation` and `## Hardware Design` sections.
  - *Why it matters here:* The teleoperation section is paper-level, but it is the best single index of teleoperation *systems* to start from.
- **[natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai)** — `list` · `production` · verified 2026-09 · #middleware #standards #ros2
  - *What it is:* 151 stars. `## Production Patterns / Reference Architectures` (ROS2, Isaac ROS, MoveIt2, Nav2, Open-RMF, DDS-Security, Foxglove, micro-ROS, ros2_control, Cyclone/FastDDS, MCAP, Zenoh, rosbag2), `## Safety & Robustness` (safe-RL, control barrier functions, RSS, formal verification), `## Governance` (ISO 10218, ISO/TS 15066, ISO 26262, UL 4600, EU AI Act), plus courses and hardware platforms.
  - *Why it matters here:* The strongest governance/standards coverage anywhere. But it never connects any of it to a running VLA inference loop: 0 TensorRT/ONNX/quantization, 0 e-stop/watchdog, 0 subtask, 0 data cleaning. That gap is our section 43.
- **[AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation)** — `list` · `research` · verified 2026-09 · #data #curation #papers
  - *What it is:* 220+ papers across Curation, Cleaning & Preprocessing; Annotation & Relabeling; Task Curation & Dataset Design; Real-World Capture & Robot-Free Collection; cross-embodiment augmentation; neural trajectories.
  - *Why it matters here:* This owns the paper-level data lifecycle. We link here rather than re-curating the same papers — our data docs are about reproducible pipelines and thresholds instead.
  - *Note:* Only ~11 stars. Treat 'well covered' as well-covered-in-content, not well-known.
- **[chang-xinhai/Awesome-Robot-Data-Engine](https://github.com/chang-xinhai/Awesome-Robot-Data-Engine)** — `list` · `research` · verified 2026-09 · #data #formats #papers
  - *What it is:* Large index (226 KB) covering collection, processing/curation, UMI, human and egocentric data, simulation, Formats/Infrastructure, and mixing/scaling.
  - *Why it matters here:* The best single reference for data-engine plumbing and format questions.
  - *Note:* Only ~3 stars.
- **[Ziteng-Wang/Awesome-Long-Horizon-Robot-Manipulation](https://github.com/Ziteng-Wang/Awesome-Long-Horizon-Robot-Manipulation)** — `list` · `research` · verified 2026-09 · #long-horizon #segmentation #papers
  - *What it is:* Taxonomy of long-horizon manipulation: mechanisms, Memory/Progress/Recovery, benchmarks.
  - *Why it matters here:* The best existing index for the long-horizon failure modes that dominate real deployments — and it has 0 stars, which tells you how under-served this area is.
- **[yueen-ma/Awesome-VLA](https://github.com/yueen-ma/Awesome-VLA)** — `list` · `production` · verified 2026-09 · #papers #index
  - *What it is:* 674 stars. Companion paper list to a TNNLS survey.
  - *Why it matters here:* Good orientation reading on model families.
- **[Denghaoyuan123/Awesome-RL-VLA](https://github.com/Denghaoyuan123/Awesome-RL-VLA)** — `list` · `research` · verified 2026-09 · #rl #post-training #papers
  - *What it is:* 863 stars. RL post-training for VLA models.
  - *Why it matters here:* Relevant once you have a working SFT policy and want to push success rate with online data.
- **[datawhalechina/every-embodied](https://github.com/datawhalechina/every-embodied)** — `list` · `production` · verified 2026-09 · #chinese #tutorial #beginner
  - *What it is:* Chinese, beginner-oriented hands-on curriculum — build an embodied robot from zero, no programming background assumed.
  - *Why it matters here:* The right link for someone starting from nothing. Not for someone already stuck.
- **[Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook)** — `list` · `production` · verified 2026-09 · #chinese #tutorial
  - *What it is:* Chinese, 21-lecture embodied-AI course.
  - *Why it matters here:* Structured Chinese curriculum covering the theory our docs assume.
- **[AlmondGod/action-diffusion-handbook](https://github.com/AlmondGod/action-diffusion-handbook)** — `list` · `research` · verified 2026-09 · #chinese #handbook #diffusion
  - *What it is:* Handbook focused on action diffusion and diffusion-transformer policies (ACT, Diffusion Policy, RDT-1B and friends).
  - *Why it matters here:* Complements VLA-Handbook on the action-representation side, which is where most 'it doesn't move' bugs live.
- **[fkromer/awesome-ros2 (abandoned)](https://github.com/fkromer/awesome-ros2)** — `list` · `abandoned` · verified 2026-09 · #ros2 #abandoned
  - *What it is:* 2.1k stars. ROS2 ecosystem index.
  - *Why it matters here:* Historically the ROS2 entry point. Useful as an archive; do not expect modern VLA integration guidance.
  - *Note:* No commits since 2023-08.
- **[kristery/Awesome-Imitation-Learning (abandoned)](https://github.com/kristery/Awesome-Imitation-Learning)** — `list` · `abandoned` · verified 2026-09 · #imitation-learning #abandoned
  - *What it is:* 611 stars. Classic imitation-learning index.
  - *Why it matters here:* Background on BC/DAgger lineage. Kept for the record, not recommended as a current reference.
  - *Note:* No commits since 2023-08.
- **[utn-air/Awesome-Robotics-Foundation-Model-How-To (abandoned)](https://github.com/utn-air/Awesome-Robotics-Foundation-Model-How-To)** — `list` · `abandoned` · verified 2026-09 · #abandoned #prior-art
  - *What it is:* Aimed at 'Training Pipeline and deployment' plus tools — conceptually the nearest predecessor to this repo.
  - *Why it matters here:* Worth reading as a cautionary example: the right idea, abandoned in 2024 at 7 stars. The lesson is that a list like this only survives if it is generated from data and checked by CI.
  - *Note:* No commits since 2024-06.
- **[Resources that do not exist (do not cite these)](https://github.com/mingqian0850/awesome_vla_deployment/issues)** — `gap` · `toy` · verified 2026-09 · #errata #non-existent #do-not-cite #trap
  - *What it is:* Names that circulate in search results, summaries, and generated text but resolve to nothing. Confirmed 404 with a direct request: `github.com/simpler-env/SimplerEnv-Plus` (there is no "SimplerEnv-Plus"; the project is SimplerEnv, and LIBERO-Plus is a separate thing), and `github.com/rr-learning/real-robot-challenge`.
  - *Why it matters here:* Recorded for the same reason `keon/awesome-physical-ai` is recorded: a reader will meet these names, and a plausible-looking dead end costs more time than an obviously missing one. "SimplerEnv-Plus" in particular is the kind of name that reads as a real successor and is easy to propagate into a citation list without checking. The general rule this repo enforces mechanically: **resolve it before you cite it.** `scripts/check_links.py` fails the build on an unresolvable URL, and `scripts/check_papers.py` verifies that an arXiv ID is the paper you claim it is, because a search snippet can attach arbitrary text to an identifier.


## Data — collection, annotation, cleaning, segmentation

The paper-level curation of this area is already done well elsewhere — see AIDASLab's list and Awesome-Robot-Data-Engine in the Landscape section. This section therefore focuses on the two things those lists do not give you: the collection systems themselves, and the reproducible decisions (thresholds, schemas, splits).

- **[LeRobot documentation](https://huggingface.co/docs/lerobot/index)** — `docs` · `production` · `Apache-2.0` · verified 2026-09 · #docs #teleoperation #calibration #format
  - *What it is:* First-party docs for the most widely used open robot-learning stack: hardware assembly, calibration, teleoperation, dataset format, training and rollout.
  - *Why it matters here:* The single most practical starting point in the field, and the reference implementation for the LeRobot dataset format everything else converts to or from.
- **[LeRobot — imitation learning on real robots](https://huggingface.co/docs/lerobot/en/il_robots)** — `docs` · `production` · verified 2026-09 · #docs #calibration #teleoperation
  - *What it is:* End-to-end walkthrough: build, calibrate, teleoperate, record, train, evaluate.
  - *Why it matters here:* Contains the operational detail (calibration procedure, teleoperation setup) that papers omit and that eats your first week.
- **[LeRobot — SO-101 assembly and calibration](https://huggingface.co/docs/lerobot/en/so101)** — `docs` · `production` · verified 2026-09 · #hardware #calibration #docs
  - *What it is:* Bill-of-materials-level build and calibration guide for the SO-101 arm.
  - *Why it matters here:* A worked example of the calibration discipline every learned policy depends on. The procedure generalises even if your arm is different.
- **[ALOHA / Mobile ALOHA](https://github.com/MarkFzp/mobile-aloha)** — `repo` · `research` · verified 2026-09 · #teleoperation #bimanual #hardware
  - *What it is:* Low-cost bimanual teleoperation and imitation learning platform; the origin of the widely copied leader-follower collection rig.
  - *Why it matters here:* The reference architecture for bimanual data collection. Cheap, replicable, and the hardware design has been reimplemented by many labs.
- **[Universal Manipulation Interface (UMI)](https://github.com/real-stanford/universal_manipulation_interface)** — `repo` · `research` · verified 2026-09 · #teleoperation #robot-free #hardware
  - *What it is:* Hand-held gripper with a camera that collects manipulation demonstrations in the wild, without a robot present; policy is deployed on a robot later.
  - *Why it matters here:* Decouples data volume from robot availability — the main practical bottleneck in collection. Its in-the-wild capture also gives the visual diversity that fixes overfitting to one table setup.
- **[Open-TeleVision](https://github.com/OpenTeleVision/TeleVision)** — `repo` · `research` · verified 2026-09 · #teleoperation #vr
  - *What it is:* VR-based immersive teleoperation with stereo streaming and active vision, for bimanual and humanoid platforms.
  - *Why it matters here:* Faster and more natural collection than leader-follower arms, and it records head/vision motion which is otherwise impossible to demonstrate.
- **[robot_teach (Open-Teach)](https://github.com/chiawenwang/robot_teach)** — `repo` · `research` · verified 2026-09 · #teleoperation #one-shot #vr
  - *What it is:* One-shot physical teaching: a single human demonstration from VR hand tracking produces a reusable policy.
  - *Why it matters here:* Interesting for data efficiency — worth knowing when the question is 'how few demonstrations can I get away with', which is most people's real constraint.
- **[robomimic](https://github.com/ARISE-Initiative/robomimic)** — `repo` · `production` · `MIT` · verified 2026-09 · #imitation-learning #data-quality #study
  - *What it is:* Framework for offline imitation learning from demonstration, with standard datasets, and the reference implementation of the 'What Matters in Learning from Offline Human Demonstrations' study.
  - *Why it matters here:* The most rigorous public evidence on which data-quality factors actually move success rate. Read it before assuming more data is the answer — number of demonstrations, operator quality and diversity often matter more than volume.
- **[robosuite](https://github.com/ARISE-Initiative/robosuite)** — `repo` · `production` · verified 2026-09 · #simulation
  - *What it is:* Modular simulation framework for robot manipulation, the sim backend behind robomimic.
  - *Why it matters here:* Useful for pre-flight checks and for generating targeted recovery data before spending robot time.
- **[MimicGen](https://github.com/NVlabs/MimicGen)** — `repo` · `research` · verified 2026-09 · #data-generation #simulation
  - *What it is:* Generates large-scale demonstration datasets from a small number of human demonstrations by transforming object poses and replanning.
  - *Why it matters here:* The most credible way to multiply scarce human demonstrations. Note the caveat that generated data inherits the failure modes of the source trajectories — it will not fix bad teleoperation.
- **[Open X-Embodiment](https://robotics-transformer-x.github.io/)** — `dataset` · `production` · verified 2026-09 · #dataset #cross-embodiment
  - *What it is:* Aggregated cross-embodiment robot manipulation dataset spanning many robots and labs, in RLDS format.
  - *Why it matters here:* The standard co-training corpus. Mostly useful as regularisation against overfitting a small in-house dataset, not as a task-specific training set.
- **[google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment)** — `repo` · `production` · verified 2026-09 · #dataset #rlds #tooling
  - *What it is:* Code and per-dataset documentation for loading Open X-Embodiment.
  - *Why it matters here:* The practical entry point — the project page alone will not get the data into your training loop.
- **[Robot Data Curation](https://arxiv.org/abs/2502.08623)** — `paper` · `research` · verified 2026-09 · #data-quality #filtering #paper
  - *What it is:* Studies how to curate robot demonstration data, including a practical demonstration-influence-style filtering approach.
  - *Why it matters here:* Gives you a defensible answer to 'should I throw away these episodes' instead of guessing.
- **[Curating Demonstrations using Online Experience](https://arxiv.org/abs/2503.03707)** — `paper` · `research` · verified 2026-09 · #data-quality #selection #paper
  - *What it is:* Uses online interaction experience to select which demonstrations are worth training on.
  - *Why it matters here:* Data selection driven by what the policy actually gets wrong, which is usually a much better signal than any offline heuristics.
- **[Enabling Long(er) Horizon Imitation for Manipulation Tasks by Modeling Subgoal Transitions](https://mlanthology.org/corl/2025/jain2025corl-enabling/)** — `paper` · `research` · verified 2026-09 · #long-horizon #subgoal #paper
  - *What it is:* Models transitions between subgoals to extend the effective horizon of imitation-learned manipulation policies.
  - *Why it matters here:* Directly addresses the failure where a chained policy executes the first sub-task and then stalls — which is the single most reported symptom in this space.
- **[RaC: Robot Learning for Long-Horizon Tasks by Scaling Recovery and Correction](https://arxiv.org/abs/2509.07953)** — `paper` · `research` · verified 2026-09 · #long-horizon #recovery #paper
  - *What it is:* Scales up recovery and correction data to make long-horizon policies robust to their own errors.
  - *Why it matters here:* The clearest statement of the thing practitioners learn the hard way: long-horizon failures are usually covariate shift, and the fix is recovery data — not more demonstrations of the happy path.
- **[Action-Only Scorers Fail on the Structural Defects That Degrade Imitation Policies](https://arxiv.org/abs/2606.05588)** — `paper` · `research` · verified 2026-09 · #data-quality #curation #metrics #structural-defects #negative-result
  - *What it is:* An empirical audit of demonstration-curation metrics, showing that scoring approaches based on the actions alone miss the structural defects that actually degrade imitation — non-Markovian structure, idleness, and spurious correlations.
  - *Why it matters here:* The academic confirmation of the argument this repo makes about dataset balance: **do not curate or reweight by action value.** If your quality signal is computed from the action distribution, it is provably blind to the defects that matter. Pair an action-based scorer with a structural one, or you will filter out good episodes and keep bad ones — and the metrics will look like they are working the whole time.
- **[Towards Balanced Behavior Cloning from Imbalanced Datasets](https://arxiv.org/abs/2508.06319)** — `paper` · `research` · verified 2026-09 · #balance #imbalance #behaviour-cloning #mixture #sub-task
  - *What it is:* Studies behaviour cloning on demonstration datasets with unequal numbers of demonstrations across behaviours and skills, and what rebalancing does to the learned policy.
  - *Why it matters here:* The right level at which to think about balance. Imbalance matters at the behaviour/skill/sub-task level, not the action-value level, and this quantifies how much an over-represented behaviour distorts the policy. Read it before deciding your dataset is imbalanced and reaching for resampling.
- **[OpenVLA's data balancing and mixture recipe over Open X-Embodiment](https://arxiv.org/abs/2406.09246)** — `paper` · `research` · verified 2026-09 · #mixture #balance #open-x-embodiment #recipe #openvla
  - *What it is:* Documents an explicit mixture recipe over Open X-Embodiment: reweighting to balance robot platform, task and scene distributions, removing dominant single-dataset biases, and stating exclusion criteria for unusable datasets.
  - *Why it matters here:* The most concrete published account of how to build a VLA training mixture. Note what it balances — platform, task, scene — and what it does not: the marginal action histogram. That is the answer to "how do I make my data distribution even", from the people who trained one of the most widely used open VLAs.
- **[AgiBot World — the 3-phase collection pipeline, and how the idle-frame defect was found](https://arxiv.org/abs/2503.06669)** — `paper` · `production` · verified 2026-09 · #pipeline #idle-frames #deployment-flywheel #annotation #industrial
  - *What it is:* 1M+ trajectories across 217 tasks with a standardised collection pipeline: pilot collection to validate feasibility and fix collection standards; skilled teleoperators collecting with local validity verification before upload; then cloud post-processing where annotators verify each episode against the phase-1 standards and add language annotation. A human-in-the-loop cycle then collects a small set, trains a policy, deploys it, and uses policy failures to find data defects.
  - *Why it matters here:* Two findings worth more than the dataset. First, **the excessive-idle-time defect was discovered by deploying a trained policy, not by inspecting the data** — industrial-scale confirmation that idle frames are a real failure cause and that auditing a dataset without a policy in the loop does not reliably find them. Second, it is a worked example of the deploy-find-defect-fix-collect flywheel, which is the operational shape every serious data effort eventually takes.
- **[Cutting dead frames from DROID — 500 hours of robot data in 32 seconds](https://www.eventual.ai/blog/cutting-dead-frames-from-droid)** — `blog` · `production` · verified 2026-09 · #idle-frames #trimming #scale #engineering
  - *What it is:* Engineering write-up on detecting and trimming idle frames across the whole DROID corpus at speed.
  - *Why it matters here:* A concrete, reproducible idleness pass at real scale. Useful as a design reference when your dataset is too large to inspect episode by episode, which is the situation where nobody bothers to trim at all.
- **[Daft — motion trimming for physical AI](https://docs.getdaft.io/en/stable/examples/motion-trimming-physical-ai/)** — `tool` · `production` · verified 2026-09 · #idle-frames #trimming #tool #recipe
  - *What it is:* A runnable example notebook for motion trimming of robot video data.
  - *Why it matters here:* Copy-paste starting point for building your own dead-frame trimming pass rather than writing the plumbing from scratch.
- **[lerobot-doctor — dataset quality diagnostics](https://github.com/jashshah999/lerobot-doctor)** — `tool` · `research` · verified 2026-09 · #tool #diagnostics #quality #lerobot #overlap
  - *What it is:* Community diagnostics tool for LeRobot datasets: idle time, anomalies, per-episode outliers.
  - *Why it matters here:* Overlaps deliberately with our own `scripts/diag_dataset.py` — and you should know that, because choosing between them is better than running neither. This one is a packaged quality report; ours adds the phase-aliasing test, the chunk-target validity check and the action-convention probe, which are the diagnostics specific to the chained-task failure this repo is organised around. Use both if you like; they answer different questions.
- **[LeRobot language columns and recipes — a shipping annotation schema, and pi0.5's joint subtask conditioning](https://github.com/huggingface/lerobot/blob/main/docs/source/language_and_recipes.mdx)** — `docs` · `production` · verified 2026-09 · #annotation #schema #subtask #pi05 #joint-conditioning #language
  - *What it is:* Two optional parquet columns beside the frames. `language_persistent` holds rows broadcast across every frame for state that remains active — styles `subtask`, `plan`, `memory`. `language_events` holds rows only on the exact frame an event was emitted — `interjection`, `vqa`, speech tool calls. Rows carry role/content/style/timestamp and, for view-dependent styles, a `camera` field that a validator enforces. A YAML recipe layer then turns rows into chat turns with weighted blends. Critically for pi0.5: `recipes/subtask_joint.yaml` supervises the assistant subtask with text cross-entropy on the low-level stream while action prediction stays active, which the docs state matches the joint setup from the pi0.5 paper, and `--policy.joint_subtask_conditioning=true` enables that conditioning at inference.
  - *Why it matters here:* **Read this before inventing your own annotation schema.** It is the only annotation schema that ships inside a real dataset format, and it separates persistent from event language — the distinction homegrown schemas get wrong, because a sub-task label is state that persists across frames while an interjection is a moment. It is also the concrete answer to the phase-aliasing fix: this is how a per-frame sub-task label actually reaches a pi0.5 action expert, and it means the hierarchical path is available if you are on LeRobot. Note the codebase split — openpi contains no subtask branch at all, so on openpi the route is the instruction string.
- **[LeRobot annotation pipeline — VLM auto-labelling that produces those columns](https://github.com/huggingface/lerobot/blob/main/docs/source/annotation_pipeline.mdx)** — `docs` · `production` · verified 2026-09 · #annotation #vlm #auto-labelling #subtask #pipeline
  - *What it is:* A VLM pipeline (`lerobot-annotate`) that generates the language columns: plan/subtask, memory, interjection and VQA modules, a served VLM by default via vLLM, optional dispatch to hosted jobs, a validator, and a cost estimate. Subtasks are produced by a two-step describe-then-segment flow over timestamped contact sheets — frames sampled at 0.5 s with the time burned into each image — with an explicit causal definition of an event boundary.
  - *Why it matters here:* The only end-to-end VLM auto-labelling pipeline from a major organisation, and the contact-sheet trick is the part worth stealing even if you build your own: segmenting a time-annotated strip of frames is a far easier VLM task than segmenting video, and it makes the model's boundary decision auditable by a human afterwards.
- **[lerobot-annotate — annotation UI](https://github.com/huggingface/lerobot-annotate)** — `repo` · `production` · verified 2026-09 · #annotation #ui #human-in-the-loop #subtask
  - *What it is:* A lightweight web UI for annotating LeRobot datasets.
  - *Why it matters here:* The human correction pass on top of automatic labels. Worth having because automatic sub-task boundaries are good enough to seed and not good enough to trust — and a boundary error inside a chained task is exactly the kind of label noise that teaches a policy the wrong phase.
- **[LeRobot — what makes a good dataset](https://huggingface.co/blog/lerobot-datasets)** — `blog` · `production` · verified 2026-09 · #collection #sop #checklist #camera #dataset-quality
  - *What it is:* The closest thing to a written collection SOP: at least two camera views, steady capture, stable lighting and exposure, the leader arm out of frame, only the follower and the objects moving, static background, at least 480x640 (720p preferred), around 30 FPS, `<modality>.<location>` naming, and task strings of 25-50 characters. It also enumerates the four failure modes seen in community datasets.
  - *Why it matters here:* Use it as your collection spec rather than writing one. The "only the follower and the objects move, leader arm out of frame" rule is the one most often broken, and it matters because a leader arm in view is a second, correlated copy of the action — the policy will happily learn to read it.
- **[HD-Space — staged collection for later-phase start states](https://arxiv.org/abs/2505.17389)** — `paper` · `research` · verified 2026-09 · #collection #intermediate-states #long-horizon #covariate-shift #recovery
  - *What it is:* Collects data in stages: roll out the current policy to reach later-phase start states, then collect demonstrations from there.
  - *Why it matters here:* The direct answer to "all my demonstrations start from the same initial state", which is the data-side cause of a policy that only ever performs the first motion. It gets you intermediate-state initialisation without hand-resetting the scene between every episode — the practical obstacle that stops teams from collecting this data at all.
- **[What Matters in Learning from Offline Human Demonstrations](https://arxiv.org/abs/2108.03298)** — `paper` · `research` · verified 2026-09 · #data-quality #study #checkpoint-selection #cameras #negative-result
  - *What it is:* The canonical study of demonstration-data quality. Two findings to carry into any dataset decision: the mixed-quality regime has more demonstrations than the proficient-human regime (300 versus 200) and still scores lower — more mixed-quality data loses to less good data — and the lowest-validation-loss checkpoint is between 10% and 100% worse than the best checkpoint. It also quantifies that dropping wrist cameras costs 10-45% relative success in some tasks.
  - *Why it matters here:* The empirical backing for the two habits this repo keeps recommending: prefer clean demonstrations over volume, and never select a checkpoint by validation loss. Both are quantified here rather than asserted.
- **[Data Scaling Laws in Imitation Learning for Robotic Manipulation](https://arxiv.org/abs/2410.18647)** — `paper` · `research` · verified 2026-09 · #data-scaling #diversity #collection #budget #environments
  - *What it is:* Over 40,000 demonstrations and 15,000 real rollouts. Generalisation scales roughly as a power law in the number of environments and objects, with saturation in demonstrations per object. Four collectors working for one afternoon reached about 90% success in novel environments with unseen objects.
  - *Why it matters here:* The most decision-relevant paper for spending a data budget: collect breadth, not depth. If you are choosing between more demonstrations in the same scene and fewer demonstrations across more scenes, this is the evidence that the second is worth more. It is also the counterweight to the reflex of extending an existing session.


## Training — frameworks, recipes, action representations

Where the second-largest gap is. There are good paper lists for VLA training, but almost nothing compares LoRA vs full fine-tuning vs frozen-backbone on cost, VRAM and success rate, and nothing publishes reproducible per-model hyperparameters. Entries marked `research` here are frameworks; the recipes you will have to read the source for.

- **[openpi (Physical Intelligence)](https://github.com/Physical-Intelligence/openpi)** — `repo` · `production` · `Apache-2.0` · verified 2026-09 · #framework #pi0 #pi05 #fine-tuning
  - *What it is:* Official open-source implementation of pi0, pi0-FAST and pi0.5, with fine-tuning configs, a training loop, and an inference runtime for real robots.
  - *Why it matters here:* The reference codebase if you are fine-tuning pi0.5. Its config files are the de-facto specification for normalisation statistics, action horizons and the discrete-state input convention — most 'the policy ignores the state' bugs trace back to a mismatch here.
- **[LeRobot (Hugging Face)](https://github.com/huggingface/lerobot)** — `repo` · `production` · `Apache-2.0` · verified 2026-09 · #framework #training #dataset-format
  - *What it is:* End-to-end stack: hardware, dataset format, teleoperation, training and rollout for ACT, Diffusion Policy, VQ-BeT, SmolVLA, pi0 and pi0.5.
  - *Why it matters here:* The lowest-friction path from a real robot to a trained policy, and the dataset format the rest of the ecosystem has converged on.
- **[NVIDIA Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)** — `repo` · `production` · verified 2026-09 · #framework #foundation-model #nvidia
  - *What it is:* GR00T N1 / N1.5 vision-language-action foundation models with fine-tuning and evaluation tooling.
  - *Why it matters here:* The main alternative foundation-model family to pi0. Check VRAM requirements before committing — they are widely reported as the deciding constraint.
- **[OpenVLA](https://github.com/openvla/openvla)** — `repo` · `research` · verified 2026-09 · #framework #discrete-actions #openvla
  - *What it is:* Open 7B vision-language-action model built on a Llama-2 backbone with discrete action tokens.
  - *Why it matters here:* Historically important and widely benchmarked. Its autoregressive discrete-action design has very different latency characteristics from flow-matching policies — relevant if your control rate is tight.
- **[OpenVLA-OFT](https://github.com/moojink/openvla-oft)** — `repo` · `research` · verified 2026-09 · #framework #fine-tuning #action-chunking
  - *What it is:* Optimised fine-tuning recipe for OpenVLA: parallel decoding, action chunking, continuous actions.
  - *Why it matters here:* Reports large throughput gains over vanilla OpenVLA fine-tuning. A useful worked example of how much the action head design, rather than the backbone, dominates inference cost.
- **[RDT-1B (RoboticsDiffusionTransformer)](https://github.com/thu-ml/RoboticsDiffusionTransformer)** — `repo` · `research` · verified 2026-09 · #framework #bimanual #diffusion
  - *What it is:* 1.2B diffusion-transformer foundation model for bimanual manipulation with a physically-interpretable unified action space.
  - *Why it matters here:* The main open bimanual foundation model outside the pi0/GR00T families. Its unified action space is worth studying if you are targeting cross-embodiment transfer.
  - *Note:* The obvious URL `thu-ml/RDT` is a 404. Use this one.
- **[Octo](https://github.com/octo-models/octo)** — `repo` · `research` · verified 2026-09 · #framework #small-model
  - *What it is:* Transformer policy trained on Open X-Embodiment, with flexible observation and action spaces.
  - *Why it matters here:* Smaller and cheaper to fine-tune than the 3B+ models. A reasonable choice when you have modest data and a modest GPU.
- **[FluxVLA](https://github.com/FluxVLA/FluxVLA)** — `repo` · `research` · verified 2026-09 · #framework #platform
  - *What it is:* All-in-one VLA engineering platform spanning data handling through deployment.
  - *Why it matters here:* An alternative to assembling openpi + LeRobot + your own glue. Read the docs before writing that glue — you may not need to.
- **[RLinf](https://github.com/RLinf/RLinf)** — `repo` · `research` · verified 2026-09 · #framework #rl #pi0 #worked-example
  - *What it is:* Reinforcement learning infrastructure for embodied models, including a documented Franka real-world pi0 SFT and deployment example.
  - *Why it matters here:* One of very few public, end-to-end worked examples that goes from fine-tuning to a specific real arm. Worth reading even if you do not use the framework.
- **[TRI-ML/vla_foundry](https://github.com/TRI-ML/vla_foundry)** — `repo` · `research` · verified 2026-09 · #framework #training
  - *What it is:* Toyota Research Institute's toolkit for training and evaluating VLA models.
  - *Why it matters here:* A second independent implementation to compare against when you suspect a bug in your own training loop.
- **[Isaiah-WU/Openpi_tool — pi05 fine-tuning and real-robot deployment](https://github.com/Isaiah-WU/Openpi_tool)** — `repo` · `research` · verified 2026-09 · #chinese #pi05 #fine-tuning #deployment #walkthrough
  - *What it is:* Chinese walk-through of pi0.5 fine-tuning and deployment on real hardware.
  - *Why it matters here:* Exactly the kind of content search engines bury and practitioners need. Chinese-language pi0.5 recipes are systematically better documented than English ones because the community around them is larger.
- **[dzj441/pi05XarmTutorial](https://github.com/dzj441/pi05XarmTutorial)** — `repo` · `research` · verified 2026-09 · #chinese #pi05 #fine-tuning #xarm
  - *What it is:* Tutorial for running pi0.5 on a UFactory xArm.
  - *Why it matters here:* A concrete worked example of adapting pi0.5 to an arm that is not in the pretraining mix — the exact situation where normalisation and action-space mismatches bite.
- **[Denghaoyuan123/DF-post-training](https://github.com/Denghaoyuan123/DF-post-training)** — `repo` · `research` · verified 2026-09 · #post-training #diffusion
  - *What it is:* Post-training recipes for diffusion-policy-style VLA models.
  - *Why it matters here:* Useful reference point on what post-training actually changes, and how much it costs.
- **[Humble2Full/lerobot-realman-vla](https://github.com/Humble2Full/lerobot-realman-vla)** — `repo` · `toy` · verified 2026-09 · #chinese #lerobot #port
  - *What it is:* LeRobot-based VLA pipeline applied to a RealMan arm.
  - *Why it matters here:* Another non-reference-embodiment port. Ports like this are where the undocumented assumptions in a codebase become visible.
- **[MicroAGI-Labs/XPolicyLab](https://github.com/MicroAGI-Labs/XPolicyLab)** — `repo` · `toy` · verified 2026-09 · #framework #multi-policy
  - *What it is:* Collection of policy implementations (including RDT-1B) under a common interface.
  - *Why it matters here:* Handy for comparing policy families without rewriting your training harness per model.


## Training recipes — the numbers

Every figure here is quoted from a primary source that was fetched and read, not recalled. Where the field does not publish a number, the field says so — a documented gap is a finding, and inventing a plausible figure would defeat the purpose of this repo. The honest summary: hardware requirements and hyperparameters ARE published; comparative success-rate numbers for LoRA vs full fine-tune vs frozen backbone are NOT. That second column is the most valuable empty space in this document.

- **[openpi — GPU / VRAM requirements](https://github.com/Physical-Intelligence/openpi)** — `docs` · `production` · verified 2026-09 · #vram #hardware #pi0 #pi05 #recipe
  - *What it is:* Quoted from the openpi README requirements table (single GPU, no model parallelism): Inference > 8 GB (RTX 4090); Fine-Tuning with LoRA > 22.5 GB (RTX 4090); Fine-Tuning full > 70 GB (A100 80GB / H100). Multi-GPU is supported via `fsdp_devices` in the training config to reduce per-GPU memory; multi-node is not supported.
  - *Why it matters here:* The most concrete public answer to "what hardware do I need" for pi0 / pi0.5. The practical decision it settles for most teams: LoRA fits on a single 24 GB consumer card, full fine-tuning does not — and the repo does not tell you what the success-rate difference is, which is exactly the number you need to make that call.
  - *Note:* Quoted verbatim from the README section 'Requirements'.
- **[openpi — normalisation statistics and when to reuse them](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)** — `docs` · `production` · verified 2026-09 · #normalization #q01 #q99 #statistics #gotcha
  - *What it is:* First-party documentation of normalisation statistics: they are computed over the training data and stored alongside the checkpoint, and can be reloaded for a new fine-tune via `AssetsConfig(assets_dir=..., asset_id=...)`. Pre-training statistics are provided per embodiment — `trossen` (ALOHA), `trossen_mobile`, `droid`, `franka`, `ur5e`, `ur5e_dual`, `arx`, `arx_mobile`, `fibocom_mobile`.
  - *Why it matters here:* This is the document that decides whether your fine-tune converges. It also corrects a widespread piece of advice: openpi does NOT say "always recompute the statistics". It says to **try both** reloading the pretrained statistics and computing fresh ones, and keep whichever works better — reloading can be *better* when your robot matches a pre-training embodiment, because the actions then land in a range the model finds familiar.
  - *Note:* Reusing pre-training statistics only works if your action space follows the same convention. See the action-space entry below before assuming it applies to you.
- **[openpi — action space and control frequency conventions](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)** — `docs` · `production` · verified 2026-09 · #action-space #gripper #control-frequency #porting
  - *What it is:* dim_0:dim_5 = left arm joint angles (radians), dim_6 = left gripper, dim_7:dim_12 = right arm joints, dim_13 = right gripper, dim_14:dim_15 = x-y base velocity (mobile only). 7-DoF robots such as Franka use the first 7 dimensions for joints and the 8th for the gripper. Gripper positions are in [0.0, 1.0] with 0.0 fully open and 1.0 fully closed. Control frequency is 20 Hz for UR5e and Franka, 50 Hz for ARX and Trossen (ALOHA).
  - *Why it matters here:* The single highest-yield thing to check when porting a policy to a new arm. Two traps hide here: the gripper convention is inverted relative to many drivers (0 = open, not closed), and a control-frequency mismatch silently changes the physical duration of a fixed-length action chunk.
- **[DROID action space is joint VELOCITY, not position](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)** — `docs` · `production` · verified 2026-09 · #action-space #velocity #droid #gotcha
  - *What it is:* "For DROID, we use the original DROID action configuration, with joint velocity actions in the first 7 dimensions and gripper actions in the 8th dimension + a control frequency of 15 Hz."
  - *Why it matters here:* A concrete instance of the general delta/absolute/velocity confusion, documented by the model authors. If you fine-tune on DROID data and deploy on a position-controlled arm — or the reverse — the policy will produce motion that is wrong in a way that looks like a bad model rather than a unit mismatch.
- **[LeRobot — pi0.5 fine-tuning recipe](https://huggingface.co/docs/lerobot/en/pi05)** — `docs` · `production` · verified 2026-09 · #recipe #pi05 #hyperparameters #frozen-vlm
  - *What it is:* Reference command, sized for a single 80 GB GPU: `--batch_size=64`, `--steps=30000`, `--policy.n_action_steps=10`, `--policy.gradient_checkpointing=true`, `--policy.dtype=bfloat16`, `--num_workers=8`, `--save_freq=5000`. A second variant sets `--policy.freeze_vision_encoder=true --policy.train_expert_only=true`.
  - *Why it matters here:* The most directly copyable pi0.5 recipe that exists. The docs state the tradeoff for the frozen variant explicitly — "less memory, at some cost in success rate" — which is unusually honest, and is the only public statement of that tradeoff I found.
- **[LeRobot — pi0 fine-tuning recipe](https://huggingface.co/docs/lerobot/en/pi0)** — `docs` · `production` · verified 2026-09 · #recipe #pi0 #hyperparameters
  - *What it is:* Reference command: `--batch_size=32`, `--steps=3000`, `--policy.compile_model=true`, `--policy.gradient_checkpointing=true`, `--policy.dtype=bfloat16`.
  - *Why it matters here:* Note the step count — 3000, an order of magnitude below the pi0.5 recipe's 30000. If you copy a step count between these two models you will either under-train or waste days.
- **[openpi — idle filter for DROID training](https://github.com/Physical-Intelligence/openpi/blob/main/examples/droid/README_train.md)** — `docs` · `production` · verified 2026-09 · #idle #filtering #sampling #droid
  - *What it is:* "By default, our openpi training recipe implements the same idle filter used to train all pi-DROID models... we filter any time steps for which the next chunk of actions would be largely idle." Implemented by pre-computing dataset indices (`compute_droid_nonidle_ranges.py`) and passing `filter_dict_path` in the training config.
  - *Why it matters here:* First-party confirmation that idle filtering is not a superstition — the model authors built it into the default recipe. This is the strongest available evidence for the episode-head idle hypothesis in the troubleshooting section, where a policy learns "at the reset state, do not move".
  - *Note:* The published index list is only valid for the `droid/1.0.1` dataset. For your own data, rerun the script — or compute the equivalent in `scripts/diag_dataset.py`, which reports episode-head idle contamination directly.
- **[Training-Time Action Conditioning for Efficient Real-Time Chunking](https://arxiv.org/abs/2512.05964)** — `paper` · `research` · verified 2026-09 · #rtc #async #training #latency
  - *What it is:* Trains the policy to accept an action prefix as conditioning, so that asynchronous execution joins smoothly instead of jumping. Exposed in LeRobot as `policy.rtc_training_max_delay`, set to the largest expected inference delay in controller steps.
  - *Why it matters here:* The difference between inference-time RTC, which patches over the chunk-boundary discontinuity, and training-time conditioning, which removes it. If you know your deployment latency at training time, this is the more principled fix.
- **[Full FT vs LoRA vs frozen vs last-layer, with numbers](https://arxiv.org/abs/2406.09246)** — `benchmark` · `research` · verified 2026-09 · #lora #full-finetune #comparison #success-rate #benchmark #frozen-vision
  - *What it is:* The one rigorous controlled comparison found, from the OpenVLA paper (Table 1), 33 rollouts per strategy on Franka-Tabletop. Success rate / trainable parameters / VRAM at batch 16: full fine-tune 69.7 ± 7.2 % / 7,188 M / 163 GB; LoRA rank 32 68.2 ± 7.5 % / 97.6 M (1.4 %) / 59.7 GB; LoRA rank 64 68.2 ± 7.8 % / 195 M / 60.5 GB; sandwich (vision encoder + embeddings + last layer) 62.1 ± 7.9 % / 914 M / 64.0 GB; frozen vision encoder 47.0 ± 6.9 % / 6,760 M / 156 GB; last layer only 30.3 ± 6.1 % / 465 M / 51.4 GB.
  - *Why it matters here:* Two conclusions that change how you configure a fine-tune. First, LoRA applied to all linear layers matches full fine-tuning at 1.4 % of the parameters and roughly a third of the memory — LoRA is not the problem people blame it for. Second, and more important: **which modules you update dominates how many.** Freezing the vision encoder costs about 22 points and training only the last layer costs about 39. If you are choosing between LoRA configurations, choose by which modules are in the target list, not by rank.
  - *Note:* The error bars overlap between full FT and LoRA rank 32, which is the honest reading: at 33 trials you cannot distinguish them. Both being ~68-70 % while frozen-vision is 47 % is the signal.
- **[LeRobot's default LoRA target list is the trap, not LoRA](https://github.com/huggingface/lerobot/issues/4415)** — `discussion` · `research` · verified 2026-09 · #lora #peft #target-modules #zero-success #trap #smolvla
  - *What it is:* LeRobot's default PEFT config targets only q/v projections inside the expert plus a handful of projection layers, and sets `modules_to_save` to an empty list — the vision tower and the language backbone are not in the target list. In a controlled SmolVLA / SO-101 experiment on an identical 3698-episode dataset, the default targets trained 742,656 parameters (0.16 %) and **every mid-training evaluation scored 0.0 %**, while full SFT was already at 60 % on its first evaluation. Expanding the target list (three q/v families plus fully training the five embodiment projections, rank 64, lr 3e-4) reached 94.0 / 84.0 / 98.0 % with 9,851,728 trainable parameters (2.1 %) — roughly 1/40 of full SFT's parameters at matched task performance.
  - *Why it matters here:* This is the highest-value practical finding in the training section, and it is a trap that looks like a data problem. A fine-tune that sits at 0 % success while the loss decreases normally is the signature, and the cause is a parameter budget you never chose deliberately. It also corrects a widespread misconception: the quantity to match across models is the trainable *fraction*, not the rank — the same rank 64 is 2.1 % of SmolVLA but roughly 0.58 % of pi0, because the two models have very different numbers of attention sites.
  - *Note:* Two command-surface details from the same source. Use `--peft.method_type` / `--peft.r` to attach a new adapter to a clean base; setting `--policy.use_peft=true` instead makes the framework treat `--policy.path` as an already-trained adapter directory, so pointing it at a base model reads a base model as an adapter. And the acceptance test is to read `num_learnable_params` out of the training log rather than trusting your CLI flags — without `--policy.freeze_vision_encoder=false --policy.train_expert_only=false`, SmolVLA reports about 100 M trainable instead of about 403 M.
- **[pi0.5 fine-tunes worse than pi0 on small single-arm datasets](https://github.com/Physical-Intelligence/openpi/issues/763)** — `discussion` · `research` · verified 2026-09 · #pi05 #loRA #quantile #normalization #small-dataset #action-range
  - *What it is:* Reported case: pi0.5 fine-tuned with LoRA on the same single-arm data as pi0 performed substantially worse (150k versus 80k steps, 4x A100 40 GB). Suspected contributors: quantile normalisation computed on a small dataset shrinking the effective action range; pi0.5's discretised state plus differing AdamW/EMA configuration; and LoRA applied to both backbones freezing too much. The reported fix was to disable quantile normalisation for small fine-tunes (`use_quantile_norm=False`), align batch size and learning rate with the `pi05_libero` recipe rather than the pi0 defaults, and consider full fine-tuning or expert-only training instead of LoRA everywhere.
  - *Why it matters here:* Directly relevant to the most common real symptom in this repo — a policy that produces small or hesitant motion. If quantile normalisation on a small dataset compresses the action range, then both the training targets and the decoded outputs are scaled down, and the robot moves less than it should while the loss looks healthy. Check this before concluding that your data is bad.
- **[pi0.5 at 1% on LIBERO: config drift, not the model](https://github.com/Physical-Intelligence/openpi/issues/711)** — `discussion` · `research` · verified 2026-09 · #pi05 #config-drift #libero #debugging
  - *What it is:* Reported case of pi0.5 scoring about 1 % on LIBERO against a much higher paper number. The diagnosis was configuration drift: LoRA, `discrete_state_input=False`, a non-standard action horizon, and hand-computed statistics that differed from the checkpoint's — plus ad-hoc learning-rate modifications.
  - *Why it matters here:* The recommended remedy generalises to every fine-tune in this space: use the shipped config verbatim first, confirm it reproduces, then change exactly one thing at a time. And diff your own `TrainConfig` field by field against the reference config rather than assuming your CLI flags produced the config you intended.
- **[How people actually decide a fine-tune is done](https://github.com/Physical-Intelligence/openpi)** — `discussion` · `research` · verified 2026-09 · #checkpoint #stopping-rule #training-length #protocol
  - *What it is:* Collected protocols, each read from its own source rather than recalled: OpenVLA-OFT uses an L1 action error threshold of about 0.01 with a plateau, evaluating every 50k steps — with the reported exception that on LIBERO-Goal, 50k steps beat 150k. GR00T reports open-loop MSE falling 87.5 → 25.4 → 13.2 → 10.0 at 500 / 1000 / 1500 / 2000 steps with no published target MSE. RDT-1B tracks `overall_avg_sample_mse`. LeRobot guidance is 5-10 epochs. openpi recipes use fixed step budgets.
  - *Why it matters here:* Nobody publishes a criterion, only conventions — and the LIBERO-Goal exception matters because it means "train longer" is not reliably better. The useful move is to write your own stopping rule down before you start, because the alternative is choosing the checkpoint whose number you liked, which is how a fine-tune's reported success rate becomes unreproducible.
- **[Run-to-run noise floors you should measure before comparing anything](https://github.com/NVIDIA/Isaac-GR00T)** — `discussion` · `research` · verified 2026-09 · #evaluation #noise #reproducibility #statistics
  - *What it is:* Reported noise levels: GR00T shows roughly 5-6% run-to-run variation, and about ±5% sampling noise at 100 episodes.
  - *Why it matters here:* A five-point noise floor means a five-point improvement is not a result. Measure your own floor by running the identical configuration twice before you compare two configurations — it is one of the cheapest experiments available and it prevents most of the false conclusions in this space.
- **[Predict long, execute short — the two horizon ablations, and why they are different knobs](https://arxiv.org/abs/2506.01844)** — `benchmark` · `research` · verified 2026-09 · #horizon #chunking #execution-depth #ablation #benchmark #rtc
  - *What it is:* SmolVLA is the only public ablation of **both** horizons on the same suite. Chunk size (prediction horizon), Table 12: 1 -> 50.0%, 10 -> 84.0%, 30 -> 78.5%, 50 -> 80.3%, 100 -> 74.5%. Execution depth (how many of the predicted steps you actually send), Table 13: 1 -> 80.3%, 10 -> 82.8%, 30 -> 70.8%, 50 -> 51.8%. Cross-policy convergence on the ratio: Diffusion Policy uses 16/8, RTC's real-world setting uses a prediction horizon of 50 with a minimum execution of 25, GR00T uses 40/16.
  - *Why it matters here:* Two practice-changing readings, and they contradict the two reflexes people have. **The chunk-size curve is an inverted U with a wide flat top between 10 and 50** — there is no magic number, but 1 and 100 are both clearly worse, so "as long as possible" and "one step at a time" are both wrong. **The execution-horizon curve is steeper** (80.3, 82.8, 70.8, 51.8), and executing the whole predicted chunk is the worst setting tested. So the rule is **predict long, execute short**: the prediction horizon is a capacity knob and the execution horizon is a responsiveness knob, and they trade off in opposite directions. The cross-policy ratio gives you a defensible default: `H ~= 2 * s`. And a corollary that is easy to get backwards — **if you adopt RTC, you extend the prediction horizon, not the execution horizon**; RTC's guidance needs a long enough chunk to have something to reconcile against (roughly 32 or more), while the execution horizon is exactly what it is trying to keep short.
  - *Note:* A caution about reading the paper past the tables: SmolVLA's own real-world setup executes the **full** chunk synchronously while its simulation evaluation re-observes every step. That is an internal inconsistency, not a recommendation — do not copy it.
- **[Three normalisation regimes inside one model family](https://arxiv.org/abs/2506.01844)** — `docs` · `production` · verified 2026-09 · #normalization #mean-std #z-score #quantile #pi0 #pi05 #smolvla
  - *What it is:* Within the pi/SmolVLA ecosystem: SmolVLA uses mean/std, pi0 uses z-score, and pi0.5 uses quantiles. Three different regimes, one family, and in practice one repository.
  - *Why it matters here:* Sharpens the advice that you must match the mode to the checkpoint: this is not a one-off mismatch between two projects, it is three live cases inside a single lineage. Combined with the finding that quantile is only marginally better than mean/std once the action convention is correct, the practical rule is: read the mode off the checkpoint and do not have an opinion about which is better.
- **[openpi's fsq_tokenizer.py is not the pi0 action tokenizer](https://github.com/Physical-Intelligence/openpi)** — `repo` · `production` · verified 2026-09 · #tokenizer #fast #fsq #vqbet #disambiguation #trap
  - *What it is:* `fsq_tokenizer.py` exists in the openpi tree but its own header states it is for RoboArena baselines. It is **not** the pi0 action tokenizer, which is FAST (DCT plus BPE). The distinct action-VQ alternative in this space is VQ-BeT, which reports roughly 5x faster inference than Diffusion Policy and does not use action chunking.
  - *Why it matters here:* A reader skimming the repository for "how does pi0 tokenise actions" will find this file and conclude the wrong thing. Recorded because it is cheap to state and expensive to discover — you would build a training pipeline around the wrong tokenizer before noticing.
- **[LeRobot relative-action support has a version floor](https://github.com/huggingface/lerobot/pull/2970)** — `docs` · `production` · verified 2026-09 · #versioning #relative-actions #flag #gotcha
  - *What it is:* `RelativeActionsProcessorStep` and the `--operation.relative_action` / `--policy.use_relative_actions` flags landed in PR #2970, merged 2026-04-01.
  - *Why it matters here:* On an older install you will find documentation for a feature your code does not have, which is a confusing failure mode: the flag is accepted-looking in the docs and absent in the source. Pin your revision and check the flag exists before following a tutorial — including this one. More generally, most of the practical knowledge in this repo is attached to a specific commit, and the entry-level `verified` date is not a version.


## Deployment — inference timing, optimisation, edge, integration

The reason this repo exists. Across 36 curated lists in this space, `watchdog|e-stop|deadman|velocity limit` returns roughly zero hits, no list reports which models actually export to ONNX/TensorRT/OpenVINO, and no list publishes measured latency/VRAM/success-rate deltas. This section is the start of that.

- **[LeRobot — Policy Deployment (lerobot-rollout)](https://huggingface.co/docs/lerobot/en/inference)** — `docs` · `production` · `Apache-2.0` · verified 2026-09 · #docs #rtc #chunking #async #subtask
  - *What it is:* First-party deployment documentation: execution strategies (base/sentry/highlight/ DAgger/episodic), Sync vs Real-Time Chunking with `execution_horizon`, `max_guidance_weight` and `prefix_attention_schedule`, cadence reporting, plus `/subtask` and `/autosteer` endpoints for runtime sub-task re-planning.
  - *Why it matters here:* Read this before designing your own inference loop — it already solves the common cases. What it does not cover is the rest of deployment: a keyword scan of the repo's inference and policy docs returns 0 hits for TensorRT, ONNX, quantization, Jetson, and safety/e-stop/watchdog. That gap is what the sections below fill.
- **[Real-Time Execution of Action Chunking Flow Policies (RTC)](https://neurips.cc/virtual/2025/loc/san-diego/poster/117747)** — `paper` · `research` · verified 2026-09 · #rtc #latency #chunking #async
  - *What it is:* Inference-time method for executing action chunks asynchronously, so the robot does not stall while the next chunk is being denoised.
  - *Why it matters here:* The core reference for the single most common real-robot timing problem. If your policy makes smooth predictions in open loop but stutters on hardware, the cause is usually that inference latency exceeds the chunk's execution time and you are re-planning from a stale observation.
- **[VLA-RAIL: A Real-Time Asynchronous Inference Linker for VLA Models and Robots](https://arxiv.org/abs/2512.24673)** — `paper` · `research` · verified 2026-09 · #async #latency #architecture
  - *What it is:* An asynchronous inference linker that decouples VLA inference from the robot control loop.
  - *Why it matters here:* A concrete design for the inference/control decoupling problem, including how to keep the control loop fed while a chunk is in flight.
- **[World Action Models in Real Time: An Empirical Study of Smooth Execution via Asynchronous Deployment](https://arxiv.org/abs/2608.01880)** — `paper` · `research` · verified 2026-09 · #async #empirical #smoothness
  - *What it is:* Empirical study of what actually makes asynchronous deployment produce smooth motion.
  - *Why it matters here:* An empirical rather than theoretical treatment — useful when you need to justify an architecture choice rather than a trick.
- **[HoloBrain-0 Technical Report](https://arxiv.org/abs/2602.12062)** — `paper` · `research` · verified 2026-09 · #sync #latency #analysis
  - *What it is:* Technical report that includes an analysis of the timing defects of synchronous inference executing full action chunks sequentially.
  - *Why it matters here:* A clean statement of the failure mode: with synchronous inference you either block the control loop or act on stale observations, and both show up as degraded task success rather than as an obvious bug.
- **[vla.cpp: A Unified Inference Runtime for Vision-Language-Action Models](https://arxiv.org/abs/2606.08094)** — `paper` · `research` · verified 2026-09 · #runtime #serving
  - *What it is:* A unified inference runtime targeting VLA models specifically.
  - *Why it matters here:* Relevant if you are considering writing your own serving layer — check whether this already covers your model family before doing so.
- **[EVA-Client](https://github.com/Noietch/EVA-CLIENT)** — `repo` · `research` · verified 2026-09 · #framework #deployment #evaluation #data-collection
  - *What it is:* Unified framework for deployment, evaluation and data collection on real robots — one policy, many robots.
  - *Why it matters here:* Directly targets the integration cost that dominates real projects. Its evaluation harness is as interesting as its deployment path, because most labs evaluate ad hoc.
- **[EVA-Client (paper)](https://arxiv.org/abs/2607.02646)** — `paper` · `research` · verified 2026-09 · #framework #paper
  - *What it is:* Paper describing the EVA-Client deployment/evaluation/data-collection framework.
  - *Why it matters here:* Explains the design rationale behind the framework above.
- **[robot-control-stack](https://github.com/RobotControlStack/robot-control-stack)** — `repo` · `research` · verified 2026-09 · #integration #sim2real #ros-free
  - *What it is:* ROS-free sim-to-real deployment stack for learned robot policies.
  - *Why it matters here:* A pragmatic option when ROS2 is more integration overhead than you need for a single-arm manipulation setup. Compare against a ROS2 path before committing either way.
- **[MiniVLA](https://github.com/Zhenxintao/MiniVLA)** — `repo` · `toy` · verified 2026-09 · #edge #tensorrt #small-model
  - *What it is:* Compact VLA targeting TensorRT edge deployment.
  - *Why it matters here:* One of the few projects that treats edge export as a first-class goal rather than an afterthought.
- **[EmbodiRun](https://github.com/BUAA-CI-LAB/EmbodiRun)** — `repo` · `toy` · verified 2026-09 · #runtime
  - *What it is:* Execution runtime for embodied policies.
  - *Why it matters here:* Early-stage, but worth tracking as the runtime layer of this stack matures.
- **[A Factory-Floor Deployment Case Study of VLA Pipelines for Industrial Packaging](https://arxiv.org/abs/2605.27461)** — `paper` · `research` · verified 2026-09 · #deployment #case-study #industrial #failures
  - *What it is:* Case study of deploying a VLA pipeline in an actual factory packaging task, written up as workflow, failures and lessons.
  - *Why it matters here:* Rare and valuable: most deployment literature reports successes on lab benches. A documented failure list from a production environment is worth more than ten benchmark tables when you are planning your own rollout.
- **[pi0 fine-tuning guide with domestic-arm deployment (Chinese)](https://zeeklog.com/p0de-wei-diao-ru-he-ji-yu-ge-chong-kai-yuan-shu-ju-ji-yi-ji-si-you-shu-ju-ji-wei-diao-openpi-han-wo-si-qi-yue-de-wei-diao-shi-jian-ji-openpizai-guo-chan-bi-shang-de-bu-shu-8)** — `blog` · `research` · verified 2026-09 · #chinese #pi0 #deployment #blog
  - *What it is:* Chinese write-up of fine-tuning openpi on open and private datasets, then deploying it on a domestic robot arm.
  - *Why it matters here:* Documents the adaptation steps for hardware outside the pretraining distribution — the case where most teams actually get stuck.
- **[LeRobot — Real-Time Chunking reference](https://github.com/huggingface/lerobot/blob/main/docs/source/rtc.mdx)** — `docs` · `production` · verified 2026-09 · #rtc #chunking #config #inference-delay
  - *What it is:* The configuration surface for RTC: `execution_horizon`, `max_guidance_weight`, `prefix_attention_schedule`, and `inference_delay`.
  - *Why it matters here:* Read this to learn what the parameters mean — and note the documented limitation: the docs state that `inference_delay` "should be calculated based on the inference latency of the policy" and do not tell you how. Measuring that number is the single highest-value hour you can spend before enabling RTC, and the how is in docs/41-real-time-inference.md.
- **[LeRobot — asynchronous inference (policy server / robot client)](https://github.com/huggingface/lerobot/blob/main/docs/source/async.mdx)** — `docs` · `production` · verified 2026-09 · #async #architecture #queue #reference
  - *What it is:* Reference implementation of the decoupled architecture: a policy server that runs inference continuously and a robot client that consumes chunks as they arrive.
  - *Why it matters here:* The cleanest existing template for the two-clock design in docs/41. Worth reading for the queue-merge policy alone, because that is where the subtle bugs live — whether to drop or blend a late chunk, and what the client does when the server goes quiet.
- **[LeRobot — rollout strategies and fleet operations](https://github.com/huggingface/lerobot/blob/main/docs/source/inference.mdx)** — `docs` · `production` · verified 2026-09 · #operations #rollout #dagger #hil #incident-capture
  - *What it is:* A single CLI exposing `base`, `sentry`, `highlight`, `episodic` and `dagger` execution strategies — autonomous runs, continuous fleet recording with Hub upload, a ring-buffer "save the last 30 seconds" incident capture, and human takeover with pedal input.
  - *Why it matters here:* The closest thing to a shipped operations control loop in a mainstream framework, and the most under-appreciated document in this stack. Most teams build incident capture from scratch, badly. If you adopt one thing from this repo, adopt the ring-buffer capture — the episodes where the policy fails are exactly the data you need, and they are the ones you will not think to record.
- **[LeRobot — human-in-the-loop data collection](https://github.com/huggingface/lerobot/blob/main/docs/source/hil_data_collection.mdx)** — `docs` · `production` · verified 2026-09 · #hil #corrections #dagger #recovery-data
  - *What it is:* Framework support for intervening during a rollout to collect correction data.
  - *Why it matters here:* The practical route to the recovery data that long-horizon policies need. Correction data from the policy's own failure states is the one thing that addresses covariate shift, and having it built into the rollout loop is what makes it actually happen rather than being planned and never collected.
- **[ros2_control — joint_trajectory_controller](https://control.ros.org/rolling/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html)** — `docs` · `production` · verified 2026-09 · #ros2 #interpolation #trajectory #limits
  - *What it is:* Spline interpolation (cubic/quintic) between trajectory points, at a configurable rate, with velocity and acceleration limits.
  - *Why it matters here:* This is where chunk interpolation actually lives, and it is the answer to a question most VLA write-ups skip entirely: a policy emits 10-50 discrete setpoints, but the servos want a continuous command. Push chunks here rather than commanding setpoints directly at the policy's rate. Choose the spline order deliberately — and note that interpolation also *hides* policy error, which is a feature until you are debugging.
- **[ros2_control — admittance_controller](https://control.ros.org/rolling/doc/ros2_controllers/admittance_controller/doc/userdoc.html)** — `docs` · `production` · verified 2026-09 · #ros2 #compliance #contact #force
  - *What it is:* Force/compliance control that lets an external force deviate from the commanded trajectory.
  - *Why it matters here:* The controller-layer answer to contact-rich tasks that a position-controlled learned policy cannot handle on its own. A policy trained on position trajectories will fight the environment; an admittance layer absorbs that. Worth knowing it exists before you conclude your policy needs to learn compliance.
- **[ros2_control — parallel_gripper_controller](https://control.ros.org/jazzy/doc/ros2_controllers/parallel_gripper_controller/doc/userdoc.html)** — `docs` · `production` · verified 2026-09 · #ros2 #gripper #interface
  - *What it is:* Standard gripper command interface for parallel grippers.
  - *Why it matters here:* Relevant to the gripper action-representation problem: normalised 0-1 versus metres versus effort is decided per project with no consensus, which is why gripper conventions are a recurring source of porting bugs. This gives you the controller-side interface to map onto.
- **[G-Levine/neural_controller](https://github.com/G-Levine/neural_controller)** — `repo` · `research` · verified 2026-09 · #ros2 #integration #real-time #bridge
  - *What it is:* Runs a learned policy as a ros2_control controller, alongside other controllers in the same controller manager.
  - *Why it matters here:* One of only two good open-source bridges between a learned policy and a real-time control framework. The architectural advantage is real: the policy becomes a peer of the trajectory controller rather than an external process racing it, which removes a whole class of timing bugs.
- **[Xbotics 具身智能教程 第13讲 — real-time VLA inference (Chinese)](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/13-VLA%E5%89%8D%E6%B2%BF.md)** — `blog` · `research` · verified 2026-09 · #chinese #latency #rtc #ttfa #derivation #deployment
  - *What it is:* A long-form Chinese lecture treating real-time inference as "the first deployment blocker". It defines the three latencies separately — time to first action, end-to-end perception-to-action latency, and chunk-boundary stall — then walks the RTC derivation with worked numbers from the paper: pi0.5 at 50 Hz with 5 denoising steps needs 76 ms per inference against a 20 ms control period, the prediction/execution/frozen regions and how they are sized, the ~28% inference cost of guidance (97 ms versus 76 ms), a rejection- sampling alternative measured at 223 ms, and the +100 ms / +200 ms latency-robustness results including temporal ensembling tripping a protective stop. It closes on the limitation RTC does not address: TTFA, the reaction latency of the frozen window.
  - *Why it matters here:* The most complete published decomposition of the VLA latency problem found in any language, and it is the reason the gap in this repo is narrower than we first claimed: the *framework* for decomposing the budget does exist, in Chinese, and it is good. What is still missing is filled-in, per-stage, measured numbers on a specific stack — which is what docs/40-optimization-matrix.md asks contributors to produce. Read this before reading the RTC paper; the derivation is clearer than the paper's.
  - *Note:* The chapter also argues the field needs three complementary layers rather than one fix — algorithms that change how chunks are generated and joined (RTC, FASTER, Legato), systems work that reduces single-inference cost, and learned/speculative methods that push average latency down once inference is already fast. The wider course is organised around the claim that embodied AI's difficulty is the whole system chain — perception, control, data, training, deployment, and failure feedback — and it applies a five-category failure framework per lecture with post-mortems: vision, action, timing, target pose, and data coverage. That is a **different axis from this repo's troubleshooting section**, which is organised by symptom. Ours answers "what do I see, and what is it"; theirs answers "which part of the system is implicated". Worth reading both, and worth knowing that a category that never appears in your own post-mortems is usually one you have not instrumented yet.
- **[FASTER: Rethinking Real-Time Flow VLAs](https://arxiv.org/abs/2603.19199)** — `paper` · `research` · verified 2026-09 · #ttfa #latency #flow-matching #denoising-schedule
  - *What it is:* Reconsiders the denoising schedule of flow-matching VLAs specifically to reduce reaction latency.
  - *Why it matters here:* Directly attacks the limit RTC leaves in place. Under a fixed denoising schedule, the action expert's N steps dominate latency and the reaction time is roughly `L + (s/2)·T_c` regardless of how smoothly chunks are joined. If your task is dynamic rather than merely long, this is the relevant axis, not chunk-boundary smoothness.
- **[Legato: Learning Native Continuation for Action Chunking Flow Policies](https://arxiv.org/abs/2602.12978)** — `paper` · `research` · verified 2026-09 · #chunking #continuation #training #latency
  - *What it is:* Learns the continuation of an action chunk natively, so a chunk can be extended instead of requiring a full re-inference.
  - *Why it matters here:* A learned route to the same goal as RTC's inference-time guidance: reduce how often you pay full inference cost, rather than patching the seams after the fact. Note the tradeoff against RTC — guidance is training-free and costs ~28% extra inference, while a learned continuation requires a training run but changes the cost structure itself.
- **[Delay-Aware Diffusion Policy](https://arxiv.org/abs/2512.07697)** — `paper` · `research` · verified 2026-09 · #delay #staleness #training #latency #diffusion
  - *What it is:* Trains a policy across a range of delays from zero up to the measured deployment delay, so the policy itself accounts for staleness.
  - *Why it matters here:* Attacks the staleness term in the latency budget at training time instead of masking it at the chunk seam. This is the counterpart to RTC: RTC makes the joint between chunks smooth while leaving the frozen window locked, whereas a delay-aware policy has seen delayed observations during training and can act sensibly on them. If your measured `d` is large and your task is dynamic, this is the more principled direction.
- **[Speculative Policy Orchestration: A Latency-Resilient Framework for Cloud-Robotic Manipulation](https://arxiv.org/abs/2603.19418)** — `paper` · `research` · verified 2026-09 · #network #cloud #command-starvation #safety #orchestration
  - *What it is:* A latency-resilient orchestration framework for cloud-hosted manipulation policies, naming the failure mode directly: network latency and jitter can destabilise the system, causing command starvation and unsafe physical execution.
  - *Why it matters here:* The clearest statement that over-the-network inference is a safety problem rather than a performance problem. Read it before deciding to put the policy on a server, and use its framing — command starvation — when you argue for a local fallback path.
- **[RoboECC: Multi-Factor-Aware Edge-Cloud Collaborative Deployment for VLA Models](https://arxiv.org/abs/2603.20711)** — `paper` · `research` · verified 2026-09 · #edge-cloud #split-inference #offload
  - *What it is:* Decides which parts of a VLA model run on the edge and which in the cloud, trading compute pressure against real-time requirements.
  - *Why it matters here:* Relevant when a single onboard device cannot host the whole model. The interesting part for deployment is the split point, because it determines what your robot can still do when the link degrades.
- **[ComVLA: Communication-Aware Split Inference for VLA Models in 6G-Connected Robotics](https://arxiv.org/abs/2609.07838)** — `paper` · `research` · verified 2026-09 · #split-inference #network #bandwidth #offload
  - *What it is:* Split inference that accounts for the communication link, targeting bandwidth-constrained connected robotics.
  - *Why it matters here:* The bandwidth-constrained half of the offload problem; complements RoboECC's compute-side view.
- **[Frame calibration worksheet](https://github.com/viam-devrel/pick-and-place/blob/main/setup/frame-calibration-worksheet.md)** — `docs` · `production` · verified 2026-09 · #calibration #checklist #worksheet #procedure
  - *What it is:* An actual fill-in-the-blanks worksheet for robot frame calibration, rather than API documentation.
  - *Why it matters here:* Rare and directly reusable: most calibration material is library documentation, which tells you how to call the function but not what a complete calibration record looks like. This is a checklist artifact, and it is the kind of thing that prevents the "checkpoint validated against which calibration" problem. Adapt it into checklists/calibrate-a-new-robot.md rather than copying it wholesale.
- **[ros2_control — mock components](https://control.ros.org/jazzy/doc/ros2_control/hardware_interface/doc/mock_components_userdoc.html)** — `docs` · `production` · verified 2026-09 · #ros2 #testing #hil #mock
  - *What it is:* Official mock hardware components that let you exercise controllers without a robot.
  - *Why it matters here:* The closest official tooling to hardware-in-the-loop testing for a policy, with an honest caveat: it tests controller plumbing, not the policy. Still worth using to validate your command path, limits and watchdog wiring before touching hardware — that is where the cheap bugs are.
- **[ros2_tracing](https://github.com/ros2/ros2_tracing)** — `repo` · `production` · verified 2026-09 · #ros2 #tracing #profiling #latency #measurement
  - *What it is:* Low-overhead tracing instrumentation for ROS 2, built on LTTng.
  - *Why it matters here:* The measurement tool for the latency budget this repo keeps asking you to fill in. Instrumenting a real control loop without perturbing it is genuinely hard; this is the maintained way to do it in ROS 2.
- **[NVIDIA TensorRT Developer Guide](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html)** — `docs` · `production` · verified 2026-09 · #tensorrt #export #operators #reference
  - *What it is:* Vendor reference for TensorRT: supported operators, precision modes, dynamic shapes and plugins.
  - *Why it matters here:* The constraint reference to consult *before* promising an export path. Most failed VLA exports fail on a specific unsupported operator or a dynamic-shape construct, and this is where you find out whether yours is supported rather than discovering it after writing the export script.


## Safety and runtime monitoring

The least-covered area in this field, and the reason docs/43-safety.md is written rather than linked. Detection research now exists; the software you would actually run does not. Where an entry here is a paper, treat it as the design reference for a component you still have to build.

- **[DGUV/IFA — collaborative robot safety (readable interpretation)](https://www.dguv.de/ifa/fachinfos/kollaborierende-roboter/index-2.jsp)** — `standard` · `production` · verified 2026-09 · #standards #iso-ts-15066 #iso-10218 #cobot #readable
  - *What it is:* A free, readable interpretation of ISO/TS 15066 and ISO 10218 from the German social accident insurance body's institute, which assesses these systems professionally. Includes concrete power-and-force limit tables.
  - *Why it matters here:* Every standards link in this space resolves to a paywalled catalogue page, which is useless when you are trying to work out what the standard actually requires. This is the readable entry point, and it is the right place to start before buying anything. If a human shares your robot's workspace, the power-and-force tables here are the numbers you need.
- **[ISO 21448 — Safety of the Intended Functionality (SOTIF)](https://www.bsigroup.com/en-GB/standards/iso-21448/)** — `standard` · `production` · verified 2026-09 · #standards #sotif #odd #safety-case #learned-components
  - *What it is:* The framework for unsafe behaviour with no component failure: the system worked as designed, but the design or its situational awareness was inadequate.
  - *Why it matters here:* The right lens for a learned policy, and the one most often missing. Functional-safety standards ask whether a system is safe when it *malfunctions*; a policy does not malfunction, it competently does the wrong thing in a situation the training data did not cover. "No fault occurred" and "someone was hurt" are compatible, and SOTIF is the framework written for that shape of problem. In practice it forces you to state your operational design domain and argue coverage, rather than assuming it.
- **[Hide-and-Seek in Trajectories: Discovering Failure Signals for VLA Runtime Monitoring](https://arxiv.org/abs/2605.30834)** — `paper` · `research` · verified 2026-09 · #monitoring #failure-detection #runtime #trajectories
  - *What it is:* Mines failure signals from the policy's own trajectories rather than requiring labelled failure data.
  - *Why it matters here:* The practical problem with supervised failure detection is that you never have a clean set of labelled failures — failures are rare, expensive, and labelled inconsistently. This attacks that directly, which is what makes it usable in a real project.
- **[SAFECAST: Robust Failure Detection for VLA Policies](https://arxiv.org/abs/2608.04246)** — `paper` · `research` · verified 2026-09 · #monitoring #failure-detection #calibration #distribution-shift
  - *What it is:* Failure detection with contrast-set training and calibration, targeting the shifts that break policies in the field: clutter, distractors, lighting changes, novel objects, reworded instructions.
  - *Why it matters here:* The listed shifts are exactly the ones that separate a lab demo from a deployment, and they are the ones an OOD monitor has to survive. Calibration matters here more than raw accuracy: a detector that fires constantly gets disabled by its operators, and then you have no monitor at all.
- **[RAFAIL: Relationship-Aware Failure Detection for Robotic Manipulation](https://arxiv.org/abs/2609.18324)** — `paper` · `research` · verified 2026-09 · #monitoring #failure-detection #latency #gpu-contention #semantic
  - *What it is:* Relationship-aware failure detection that trades VLM-based semantic checking against fast out-of-distribution scorers.
  - *Why it matters here:* Read this one first for a real deployment, because it treats the monitor as a component with its own cost. A semantic check requiring a VLM forward pass competes with your policy for the same GPU, and on a tight control loop that competition is not free — you are slowing the policy or delaying the monitor, and you should choose which deliberately. Most monitoring work assumes the monitor is free.
- **[Rewind-IL: Online Failure Detection and State Respawning for Imitation Learning](https://arxiv.org/abs/2604.16683)** — `paper` · `research` · verified 2026-09 · #monitoring #recovery #respawning #long-horizon #chunking
  - *What it is:* Online failure detection combined with state respawning, aimed at long-horizon action-chunked failures.
  - *Why it matters here:* The recovery half of graceful degradation, and the half almost everyone skips. A monitor with no bounded response is just a logging system; Rewind-IL pairs detection with a concrete action, which is what Layer 5 of docs/43-safety.md describes as scripted recovery primitives. Worth reading for the respawn semantics even if you implement the detection differently.
- **[NVIDIA Halos for robotics](https://developer.nvidia.com/blog/inside-nvidia-halos-for-robotics-a-full-stack-functional-safety-system-for-physical-ai/)** — `docs` · `production` · verified 2026-09 · #safety #architecture #functional-safety #vendor
  - *What it is:* Vendor architecture for a full-stack functional-safety system for physical AI.
  - *Why it matters here:* The most complete published architecture in this space, and useful as a reference structure even if you never adopt it. Note what it is: an architecture. There is still no reference implementation of a watchdog and limiter wrapping a learned policy — that is the gap docs/43-safety.md fills.
- **[Mender — open-source OTA updates with rollback](https://mender.io/)** — `tool` · `production` · verified 2026-09 · #ota #fleet #rollback #operations
  - *What it is:* Over-the-air update system with atomic rollback semantics.
  - *Why it matters here:* Relevant to the failure mode nobody plans for: you push a model update to the fleet, it regresses, and now you need to get back. Rollback semantics are the difference between a bad afternoon and a dead robot. Note the interaction with the checkpoint-to-calibration provenance gap — rolling back the model without rolling back the calibration is its own bug class.


## Deployment benchmarks — measured, not cited

Latency and quantisation numbers that named hardware actually produced. Every figure here was traced to a source that reports it, and every URL is machine-checked. **Read the comparability warning before using any row.** Different harnesses, camera counts, denoising step counts and warm-up paths make most cross-source VLA latency comparisons invalid. FlashRT's own benchmark table carries this warning explicitly, and it applies to NVIDIA's published numbers too. Entries with `type: gap` are measurements that still do not exist publicly. Writing that down is more useful than inventing a number.

- **[FlashRT — cross-source latency table (π0.5, GR00T N1.6)](https://github.com/flashrt-project/FlashRT/blob/main/docs/benchmark_comparison.md)** — `benchmark` · `research` · verified 2026-09 · #latency #benchmark #pi05 #groot #jetson
  - *What it is:* The only place found that tabulates *competing* published numbers side by side, with an explicit "only compare matching rows" warning. Reported rows: upstream openpi 714 ms on Jetson Thor and 244 ms on RTX 5090; Jetson AI Lab BF16 163 ms improving to TensorRT FP8 95 ms on Thor; FlashRT 51.51 ms (13.9x). Also a worked example of honest reporting that separates cold init (6.18 s), first inference (1.07 s) and steady state (18.39 ms p50).
  - *Why it matters here:* Resolves the question the feasibility arithmetic in docs/41-real-time-inference.md depends on: is the model fast enough for your control rate on the hardware you own. The ordering of magnitude — 714 ms down to 51 ms for the same model class — is the single most useful fact in this section, because it says the answer is mostly about the inference stack, not the model.
  - *Note:* FlashRT's README warns against comparing its RTX 4090 numbers with RTX 5090 or TensorRT rows. Heed that: the table is a map of what has been reported, not a controlled comparison.
- **[FlashRT — small-batch realtime inference engine](https://github.com/flashrt-project/FlashRT)** — `repo` · `research` · verified 2026-09 · #inference-engine #cuda #latency #pi05 #groot
  - *What it is:* Hand-written CUDA inference engine for latency-critical VLA at small batch (π0, π0.5, GR00T N1.6, π0-FAST).
  - *Why it matters here:* Small batch is exactly the VLA regime that large-batch-optimised serving stacks underserve — you infer for one robot, not a request queue. If your latency numbers look like the 714 ms row rather than the 51 ms row, the difference is the inference stack.
- **[NVIDIA Developer Forum — real measured π0.5 / GR00T latency on Thor and RTX 5090](https://forums.developer.nvidia.com/t/real-time-inference-on-thor-rtx-pi0-5-gr00t-n1-6-1-7-thor-23-hz-rtx-5090-50-80hz/368788)** — `discussion` · `production` · verified 2026-09 · #latency #jetson-thor #rtx5090 #pi05 #groot #measured
  - *What it is:* Developer thread with measured numbers: π0.5 44 ms (23 Hz) on AGX Thor and 17.58 ms (57 Hz) on RTX 5090; GR00T N1.6 45 ms / 13.08 ms; π0-FAST 8.1 ms per token on Thor versus 2.39 ms per token on 5090. An NVIDIA staff reply links the official TensorRT NVFP4 tutorial.
  - *Why it matters here:* The best single primary source of real π0.5 and GR00T latency on shipping hardware. It also gives you the number that decides a robot's architecture: 23 Hz on Thor means a 50 Hz control loop cannot be fed synchronously from the policy, so you need chunking or async execution regardless of anything else.
- **[Isaac GR00T — official deployment optimisation numbers](https://nvidia-isaac-gr00t.mintlify.app/deployment/optimization)** — `docs` · `production` · verified 2026-09 · #latency #tensorrt #torch-compile #jetson #orin #groot #measured
  - *What it is:* Vendor-published latencies for GR00T N1.6 across three regimes per GPU (PyTorch eager / torch.compile / TensorRT, ms): RTX 5090 58/37/31, H100 77/38/36, RTX 4090 82/44/43, Jetson Thor 117/105/92, Jetson Orin 300/199/173.
  - *Why it matters here:* Answers "what does torch.compile and TensorRT actually buy me, on which GPU" for a named model, from the vendor. Two things stand out: the compile win is large on GPUs and small on Thor (117 to 105 ms), and on Orin no stack gets you under 173 ms — which rules out synchronous 20 Hz control on that part and tells you the hardware is the constraint before you start optimising code.
- **[embodied-efficiency — the negative result that saves weeks](https://github.com/LaelaZorana/embodied-efficiency)** — `benchmark` · `research` · verified 2026-09 · #quantization #negative-result #cuda-graphs #latency #batch1
  - *What it is:* Four experiments on VLA inference optimisation. Finds CUDA graphs give ~5.9x, while weight-only INT8/INT4 quantisation (hand kernel, tensor-core rewrite, size sweep, torchao/Marlin) is **1.2-1.6x SLOWER than bf16 at batch 1**. Also makes the latency-versus-staleness trade explicit: bf16 plus CUDA graph costs 4.47 ms per action, while executing a whole 50-action chunk amortises to 0.089 ms per action but leaves the last action 49 control steps stale.
  - *Why it matters here:* The most valuable single result in this file. The default assumption — that low-bit quantisation buys latency — is wrong for a VLA sampler at batch 1, where it is a *memory footprint* lever only. Teams that skip this experiment spend weeks quantising, break their policy's action fidelity, and get slower inference. Read it before writing any quantisation code.
  - *Note:* The 0.089 ms/action figure is the honest statement of what open-loop chunk execution buys: it is not that inference got cheaper, it is that you stopped paying for it per step and accepted staleness instead. See docs/41-real-time-inference.md.
- **[Jetson-PI — onboard async VLA inference](https://github.com/PKU-SEC-Lab/Jetson-PI)** — `repo` · `research` · verified 2026-09 · #async #jetson #orin #control-frequency
  - *What it is:* Open-sourced asynchronous VLA inference running onboard a Jetson, reporting roughly an 8.66x improvement in effective control frequency on Orin.
  - *Why it matters here:* The concrete answer to the most common hardware complaint in this space — "the policy runs at 5 Hz and the arm wants 50 Hz". Rather than waiting for a faster model, it decouples inference rate from control rate, which is the same conclusion RTC reaches from the algorithmic side.
- **[Characterizing VLA Models across XPUs](https://arxiv.org/abs/2604.24447)** — `paper` · `research` · verified 2026-09 · #profiling #per-stage #xpu #context-cache #measured
  - *What it is:* Per-stage timing (ViT / LLM prefix / action expert) for VLA models across GPUs and edge parts, including context caching gains of 1.25x on RTX 4090 and 1.22x on Jetson Thor.
  - *Why it matters here:* The best hardware-heterogeneity study available: it tells you which stage dominates on which part, so you optimise the thing that is actually slow on your device instead of the thing that was slow on the authors' device. Stage breakdowns are also what you need to decide between caching, pruning, and a smaller encoder.
- **[FoldQuantVLA — native low-bit quantisation for VLAs](https://arxiv.org/abs/2609.24433)** — `paper` · `research` · verified 2026-09 · #quantization #low-bit #paper
  - *What it is:* Low-bit quantisation designed around VLA internals (consistent folding) rather than a ported LLM recipe.
  - *Why it matters here:* Complements the negative result above: if naive LLM quantisation fails on a VLA, this is the attempt to identify why and fix it, rather than concluding quantisation is useless for policies.
- **[Revisiting Open-Loop Execution in Robotics](https://arxiv.org/abs/2608.15938)** — `paper` · `research` · verified 2026-09 · #open-loop #reactivity #chunking
  - *What it is:* Argues the field over-corrected toward reactivity and quantifies what open-loop execution actually buys and costs.
  - *Why it matters here:* The counterweight to "always re-plan as fast as possible". Directly relevant when your asynchronous loop performs *worse* than plain open-loop chunk execution — which happens, and which the reactivity narrative does not predict.
- **[Optimizing ROS 2 Communication for Wireless Robotic Systems](https://arxiv.org/abs/2508.11366)** — `paper` · `research` · verified 2026-09 · #ros2 #dds #wireless #latency
  - *What it is:* Empirical study of ROS 2 throughput and latency over wireless links, including back-pressure when the offered rate exceeds link throughput, plus released DDS configuration tooling.
  - *Why it matters here:* The clearest published data on ROS 2-over-WiFi failure modes, and the explanation for the most confusing class of deployment bug: everything is smooth on Ethernet and drops frames on WiFi.
- **[GAP — a filled-in end-to-end latency budget](https://github.com/mingqian0850/awesome_vla_deployment/issues)** — `gap` · `toy` · verified 2026-09 · #gap #latency #budget #wanted
  - *What it is:* Narrower than it first appeared. The *framework* for decomposing the budget does exist — a Chinese lecture defines the three latencies separately (time to first action, end-to-end, chunk-boundary stall) and works through the RTC derivation with real numbers. What is missing is a **filled-in, measured** budget on a named stack: camera exposure, transport, host capture, resize and uint8 conversion, network RTT, preprocessing, ViT, LLM prefix, K denoising steps, postprocessing, queue merge, bus latency, servo/IK, actuator settling — measured, not enumerated.
  - *Why it matters here:* Both RTC's `inference_delay` and LeRobot's chunk thresholds *require* a per-step delay estimate, and both sets of docs tell you to compute it without telling you how. A measured example on one popular stack (pi0.5, three cameras, SO-101 or UR5e) would immediately become the reference this field lacks. Partial ingredients exist: Jetson-PI's per-module table, FlashRT's separated harness numbers, and the framework above.
  - *Note:* We deliberately narrowed this from "nobody publishes the framework" to "nobody publishes filled-in numbers", after finding the framework. An over-broad gap claim damages a curated index as much as a dead link does.
- **[GAP — checkpoint to calibration/config provenance](https://github.com/mingqian0850/awesome_vla_deployment/issues)** — `gap` · `toy` · verified 2026-09 · #gap #provenance #calibration #reproducibility #wanted
  - *What it is:* Still not published as tooling. Nothing records "this checkpoint was validated against this URDF, these camera intrinsics and extrinsics, and this safety-config revision". Experiment trackers follow weights, not the robot's physical configuration.
  - *Why it matters here:* The most consequential missing piece for reproducibility, and calibration drift is documented and real. Without it, "the model that worked last month" is unfalsifiable. `templates/deployment-manifest.yaml` in this repo is a starting point, not a solution.
- **[GAP — a supported export path with an action-parity check](https://github.com/mingqian0850/awesome_vla_deployment/issues)** — `gap` · `toy` · verified 2026-09 · #gap #onnx #tensorrt #export #parity #wanted
  - *What it is:* Still open. ONNX/TensorRT export is a feature request rather than a supported path in the mainstream framework, and recipes live in third-party forks.
  - *Why it matters here:* What is missing is not just the export but the **action-parity harness**: after exporting, compare action chunks against the reference implementation on a fixed batch of observations, and report max absolute deviation. Without that check, an export that silently degrades the policy looks like a policy regression.
- **[GAP — what the robot does during a network stall (operational, not academic)](https://github.com/mingqian0850/awesome_vla_deployment/issues)** — `gap` · `toy` · verified 2026-09 · #gap #network #safety #stall #wanted
  - *What it is:* Narrower than it first appeared. The academic treatment exists and names the failure mode precisely: a latency-resilient orchestration framework describes how network latency and jitter "can severely destabilize the system, causing command starvation and unsafe physical execution", and there is work on edge-cloud split inference and on deciding what runs where under compute pressure. What is still missing is the **operational** half: a post-mortem from a shipped robot reporting jitter distributions, dropped-frame rates, reconnect behaviour, and what the policy actually did during a two-second stall mid-chunk.
  - *Why it matters here:* This is a safety question disguised as a networking question. The answer should be a defined behaviour — decelerate to a stop along a safe path — and right now it is usually whatever the framework happens to do, which is frequently "keep executing the stale chunk". Papers tell you the problem is real; nobody tells you what their robot did.
  - *Note:* We deliberately rewrote this after finding the academic work. The original claim that the problem was undocumented was too broad, and an over-broad gap claim damages a curated index as much as a dead link does.


## Evaluation

Most labs evaluate ad hoc, then report point estimates from a handful of trials. These entries are the tools and the protocol material for producing numbers you can act on.

- **[allenai/vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)** — `repo` · `research` · verified 2026-09 · #evaluation #harness
  - *What it is:* A unified harness for evaluating VLA models across environments.
  - *Why it matters here:* Reduces the amount of bespoke evaluation plumbing you have to write, which is usually where evaluation rigour is lost.
- **[SimplerEnv](https://github.com/simpler-env/SimplerEnv)** — `repo` · `research` · verified 2026-09 · #evaluation #simulation #benchmark
  - *What it is:* Simulated environments designed to correlate with real-robot performance for manipulation policies.
  - *Why it matters here:* Useful as a cheap screening filter between training runs so you do not spend robot time on obviously bad checkpoints. Treat it as a screen, not as evidence of deployment readiness — the visual and contact fidelity gaps that matter on hardware are exactly what a simulator tends to miss.
- **[RoboCasa](https://github.com/robocasa/robocasa)** — `repo` · `research` · verified 2026-09 · #evaluation #simulation #benchmark
  - *What it is:* Large-scale simulation benchmark for everyday manipulation tasks in kitchen environments.
  - *Why it matters here:* Broad task coverage for pre-deployment sanity checks and for generating targeted recovery data.
- **[Statistical lower bounds on behavior-cloning success probability](https://arxiv.org/abs/2405.05439)** — `paper` · `research` · verified 2026-09 · #evaluation #statistics #confidence #trials
  - *What it is:* Derives statistically valid lower bounds on true success probability from a small number of trials (roughly 20-100).
  - *Why it matters here:* Turns "we got 7 out of 10" into a defensible statement. Most real-robot evaluations in this field report point estimates from trial counts that cannot support the comparisons being drawn, and this gives you the bound instead.
- **[PhAIL: A Real-Robot VLA Benchmark and Distributional Methodology](https://arxiv.org/abs/2605.29710)** — `paper` · `research` · verified 2026-09 · #evaluation #statistics #stopping #trials
  - *What it is:* A real-robot VLA benchmark that also proposes a distributional evaluation methodology. It states outright that N <= 25 trials without confidence intervals cannot resolve close comparisons.
  - *Why it matters here:* Answers the question every evaluation actually faces: when am I allowed to stop running trials. Pair it with the sequential and anytime-valid stopping work, which lets you stop as soon as the answer is determined instead of pre-committing to a fixed trial count and burning robot time on a difference that is already unambiguous.
  - *Note:* Our entry name previously read "Sequential / anytime-valid stopping rules for robot evaluation", which is a description of one contribution rather than the paper's identity. Renamed after scripts/check_papers.py compared it against the arXiv record — a small instance of exactly the mislabelling that script exists to catch.
- **[Near-optimal stopping in the 10-50 trial regime](https://arxiv.org/abs/2503.10966)** — `paper` · `research` · verified 2026-09 · #evaluation #statistics #small-sample #trials
  - *What it is:* Studies evaluation stopping specifically in the trial-count regime that real-robot manipulation work actually operates in.
  - *Why it matters here:* The 10-50 trial regime is where almost all published robot evaluations live, and it is precisely where naive statistics break down. This is the closest thing to a protocol for the situation you are actually in.
- **[A 25x gap between how LIBERO is evaluated in papers and its default config](https://arxiv.org/abs/2506.01844)** — `paper` · `research` · verified 2026-09 · #libero #evaluation #reproduction #protocol #trials
  - *What it is:* Papers reporting LIBERO results commonly run 500 trials per suite across 3 seeds. LIBERO's own default configuration ships `n_eval: 20`.
  - *Why it matters here:* If you reproduce a published number with the default settings and get something worse, this is a plausible reason before your training recipe is. It is also the clearest illustration of why an evaluation protocol has to be reported rather than assumed: the same benchmark, the same checkpoint, and a 25x difference in evidence.
- **[Score the Steps, Not Just the Goal — subgoal-level evaluation](https://arxiv.org/abs/2509.19524)** — `paper` · `research` · verified 2026-09 · #evaluation #subgoal #progress #statistics #per-phase
  - *What it is:* Uses a VLM to evaluate progress at the subgoal level, turning one bit of information per rollout into a progress curve.
  - *Why it matters here:* The highest-leverage change to a real-robot evaluation protocol in this list. A success rate from 30 trials is one number built from 30 bits, which is why it cannot resolve a five-point difference. A per-subgoal progress curve gives you many more observations per expensive trial — and it tells you *where* the policy fails, which is the thing you actually need in order to fix it. If you change one thing about how you evaluate, change this.
- **[Failure taxonomies for manipulation — five groups, five different label sets](https://arxiv.org/abs/2512.01946)** — `paper` · `research` · verified 2026-09 · #failure-taxonomy #evaluation #planning-vs-execution #diagnosis #gap
  - *What it is:* There is no community-standard failure taxonomy, and this is the evidence: several independent groups each invented their own. [Guardian](https://arxiv.org/abs/2512.01946) detects robotic planning and execution errors with VLMs and — importantly — separates the two, because planning errors and execution errors have different remedies. [Eval-Actions](https://arxiv.org/abs/2601.18723) scores fine-grained execution quality and, unusually, examines rater reliability. [ProTracer](https://arxiv.org/abs/2609.21369) diagnoses failures from proprioception alone, needing no extra camera or VLM compute — which matters when the monitor shares a GPU with the policy. [Visual Symbols](https://arxiv.org/abs/2512.02787) produces a human-readable failure representation that doubles as an annotation scheme. [REBOOT](https://arxiv.org/abs/2609.22591) supplies the recovery-side dataset and benchmark, on the hardest regime: precision assembly.
  - *Why it matters here:* Use these as starting points rather than inventing your own labels from scratch — but do not expect them to agree. The actionable part is Guardian's split: when a rollout fails, "it chose the wrong thing to do" and "it did the right thing badly" call for completely different fixes, and collapsing them into one failure count is how teams end up collecting more data when the problem was the instruction. This is also why this repo does not publish a single canonical taxonomy: the field does not have one, and pretending otherwise would be exactly the kind of unearned confidence the provenance policy exists to prevent.
- **[RoboTwin 2.0](https://robotwin-platform.github.io/)** — `benchmark` · `research` · verified 2026-09 · #benchmark #simulation #bimanual #domain-randomisation #robustness
  - *What it is:* A bimanual manipulation benchmark with strong domain randomisation.
  - *Why it matters here:* Fills the two weaknesses this repo keeps flagging in the popular sim benchmarks: LIBERO and SimplerEnv are largely single-arm and comparatively light on visual randomisation, so a policy can score well on them and still fail the first time the lighting changes. If you want a sim screen that has a chance of predicting deployment, bimanual coverage and randomisation strength are the two properties to select for.


## Counter-evidence — what did not work, and what stops working

A section no other list in this space has, and the one most likely to save you a month. Every entry is a negative result, a non-transfer report, or a documented regression — reported by the people who ran the experiment, with the numbers they gave. These belong in a deployment list for the same reason the provenance policy exists: the published record is heavily selected toward successes, so the failures are the scarce information. A warning that applies to this whole section: an entry here is not a claim that a method is bad. It is a claim that someone tried it, in a specific setting, and this is what happened.

- **[A working fine-tune degraded to unusable in weeks, with no code or data change](https://openvla-oft.github.io/)** — `blog` · `production` · verified 2026-09 · #drift #calibration #non-reproducibility #camera-pose #wear
  - *What it is:* The OpenVLA-OFT authors, explaining why one task performed far worse than harder ones: "we would observe over 90% success rate on this task with fine-tuned OpenVLA policies. However, due to distribution shifts, performance dropped quite significantly when we ran the tests again weeks later." They attribute it to "shifts in the wrist camera viewpoints and slight wear-and-tear in a few robot joints, which affected the dynamics", and note that the task ultimately had to be re-evaluated with all methods simultaneously "so that they all encounter the same train-test distribution shifts".
  - *Why it matters here:* The strongest evidence anywhere that a VLA deployment can silently rot. It is the reason `templates/deployment-manifest.yaml` exists: without binding a checkpoint to the camera pose, the calibration hash and the joint condition it was validated against, "the model that worked last month" is an unfalsifiable claim and you will spend that month retraining. Physical wear is a distribution shift, and it is not in any dataset.
- **[A good loss curve is not a working policy](https://docs.picknik.ai/how_to/vla/train_a_vla_policy/)** — `docs` · `production` · verified 2026-09 · #loss #evaluation #overfitting #validation #pitfall
  - *What it is:* An engineering runbook warning that the standard pi0.5 LoRA fine-tune "trains against your demonstrations with no held-out validation split and no rollouts in the loop, so it has no evaluation metric. Low loss means the model reproduces the demonstrations it was shown. It does not mean the policy completes the task, and because nothing is held out, overfitting does not show up in the curve."
  - *Why it matters here:* States plainly the thing that wastes the most time in this field: reading the loss as if it were a success rate. It is also the cleanest argument for instrumenting rollouts from the first day rather than after the loss looks good.
- **[Quadrupling the dataset did not fix a language-grounding failure](https://openvla-oft.github.io/)** — `blog` · `production` · verified 2026-09 · #negative-result #language-grounding #data-scaling #film
  - *What it is:* On the "put X into pot" task, the authors report that "simply doubling/quadrupling the dataset size did not solve the problem, as it only slightly improved language following ability. To achieve much better language grounding, we had to take additional measures", such as adding FiLM conditioning. They also state they did not actually need all 300 demonstrations they collected for satisfactory performance.
  - *Why it matters here:* Direct counter-evidence to the reflex answer of "collect more episodes". More data in the same distribution does not fix a conditioning failure — if the instruction is not being used, more examples of it not being used does not help. Diagnose which failure you have before spending weeks on collection.
- **[25 episodes explicitly was not enough](https://github.com/huggingface/lerobot/blob/main/docs/source/smolvla.mdx)** — `docs` · `production` · verified 2026-09 · #episode-count #data-size #negative-result #smolvla
  - *What it is:* The SmolVLA documentation reports a controlled comparison: "we recorded 50 episodes across 5 distinct cube positions... We tried similar dataset with 25 episodes, and it was not enough leading to a bad performance. So, the data quality and quantity is definitely a key." The same docs recommend about 50 episodes as a starting point.
  - *Why it matters here:* A rare published number where a *specific* demonstration count is documented as failing, rather than a vague recommendation to collect more. Combined with the maintainer guidance below, it gives you a defensible floor instead of a guess.
- **[50 episodes is a floor, not a target](https://github.com/huggingface/lerobot/issues/2378)** — `discussion` · `production` · verified 2026-09 · #episode-count #data-size #planning #pi05
  - *What it is:* Maintainer guidance on how much data a pi0.5 fine-tune needs: "~50 episodes is a reasonable start for a single-location PnP; go to 100-200 if you vary object/position." The docs state the same rule as "at least 50 episodes, with 10 episodes per location".
  - *Why it matters here:* Converts the collection question from "more is better" into a number you can plan against, and makes the key variable explicit: it is not the episode count, it is the number of distinct *conditions* you need to cover. Ten episodes per location is a much more useful planning rule than a total.
- **[The pi0 authors say it may not work for you](https://github.com/Physical-Intelligence/openpi)** — `docs` · `production` · verified 2026-09 · #non-transfer #expectations #pi0
  - *What it is:* From the openpi README: "pi0 was developed for our own robots, which differ from the widely used platforms such as ALOHA and DROID... we do not expect every such attempt to be successful. All this is to say: pi0 may or may not work for you."
  - *Why it matters here:* Worth citing when a fine-tune fails and the instinct is to blame your own data pipeline. The model authors state that transfer to a different platform is not guaranteed. It also justifies budgeting for a port as a research task rather than an engineering one.
- **[The policy reproduces the flaws in your demonstrations](https://openvla-oft.github.io/)** — `blog` · `production` · verified 2026-09 · #negative-result #data-quality #imitation #demonstrations
  - *What it is:* Reported case: "When using a diffusion-based fine-tuned VLA (pi0) to scoop pretzels, the robot fails because it inserts the spoon too deeply... pi0 generates this same behavior two times in twelve trials" — copied from suboptimal demonstrations in the training data.
  - *Why it matters here:* Imitation learning reproduces the data, including its mistakes. A behaviour that appears in a consistent fraction of rollouts is usually in your demonstrations, not in the model. This is the argument for watching your own teleoperation footage before assuming an optimisation problem.
- **[Sim benchmarks obscured the real deployment problems](https://openaccess.thecvf.com/content/CVPR2026W/MEIS/html/Liu_Bridging_the_Pretrain-to-Real_Gap_Alignment_Challenges_in_Deploying_Generalist_VLA_CVPRW_2026_paper.html)** — `paper` · `research` · verified 2026-09 · #sim-to-real #benchmark-critique #openvla #franka
  - *What it is:* A workshop paper on deploying a 7B OpenVLA on a real Franka Research 3, reporting that "the prevailing reliance on simulated benchmarks obscures the severe physical and algorithmic domain shifts encountered during real-world hardware deployment", and that making it work required deterministic decoding enforcement, strict thresholding from continuous to binary, geometric retargeting and LoRA.
  - *Why it matters here:* Peer-reviewed support for treating simulation results as a screening filter rather than evidence of deployment readiness — and a concrete list of the unglamorous fixes that real deployment actually needed.
- **[~100 demonstrations, and a concrete training target](https://github.com/openvla/openvla/issues/12)** — `discussion` · `research` · verified 2026-09 · #episode-count #action-token-accuracy #openvla #metrics
  - *What it is:* An OpenVLA author's guidance: "training dataset size: ~100 episodes", and "we usually train the model to ~95+% action token accuracy". The README repeats the roughly 100-demonstration figure and notes that out of the box the model only works well on domains from its training data.
  - *Why it matters here:* Gives an alternative to watching the loss: action-token accuracy on your own data is a concrete, checkable target with a stated value, and it is a much better early signal than the training loss.
- **[Pretraining is worth +26.6 points on the same task](https://arxiv.org/abs/2506.01844)** — `paper` · `research` · verified 2026-09 · #pretraining #smolvla #success-rate #benchmark
  - *What it is:* SmolVLA reports 51.7% success on SO100 without pretraining on community datasets, rising to 78.3% after pretraining on community-collected data — a +26.6 point absolute improvement. It was trained on fewer than 30k episodes drawn entirely from public datasets, roughly an order of magnitude less data than prior work, standardised at 30 FPS.
  - *Why it matters here:* Quantifies what you get from starting at a pretrained checkpoint rather than from scratch, which is the main argument for the fine-tuning approach this repo assumes. It also sets a realistic expectation for how far a small open model can go when the pretraining mixture matches your hardware.
- **[Position control beat velocity control, against the trend](https://arxiv.org/abs/2303.04137)** — `paper` · `production` · verified 2026-09 · #action-space #position #velocity #latency #negative-result #counter-evidence
  - *What it is:* The Diffusion Policy work reports that position control consistently outperformed velocity control "in contrast to the majority of recent behavior cloning work", and specifically that position control is **robust against latency** while velocity control is not.
  - *Why it matters here:* Direct counter-evidence for anyone planning a velocity or torque action space, and it interacts with two other entries in this repo. DROID ships joint **velocity** actions at 15 Hz, so copying its convention is not automatically wrong — but this result says the choice has a latency cost, and latency is the thing [docs/41](41-real-time-inference.md) is about. A velocity action space makes your policy more sensitive to exactly the staleness that chunked inference already introduces. Useful as the counterweight when someone proposes velocity actions for smoothness: the evidence points the other way.


## Troubleshooting — symptom to root cause to fix

Nothing comparable exists in English for VLA. Read the causes in order — they are ranked by how often they turn out to be the answer, not by how interesting they are. The `test` field is always something you can run in under an hour; run it before changing anything. Guessing at fixes here is how people lose weeks. Two scripts implement the tests referenced below: `scripts/diag_dataset.py` (data-side) and `scripts/diag_policy.py` (model-side).

Read the causes in order. They are ranked by how often they turn out to be the answer, not by how interesting they are.

### The policy executes the first sub-task of a chained task, then stalls or repeats it — regardless of the initial state.

`severity: high` · `frequency: extremely common`

**Cause 0 — The inference loop only consumes index 0 of the action chunk — a harness bug that is indistinguishable from a model failure.**

- **Test:** Read your own rollout loop before you touch the model. Print the shape of what the policy returns and the shape of what you send to the robot. A policy that returns a chunk of shape (H, action_dim) — for example GR00T returns (16, 7) — is trivially mis-consumed by a loop that indexes only the first row, and the resulting behaviour is a robot that performs one step of motion and then re-plans. From the outside that is the same symptom as every cause below it, so this costs five minutes to rule out and can save weeks of retraining.
- **Fix:** Decide the execution depth explicitly and write it down as a number, then verify the number of commands actually sent per inference against it. Be aware that the right depth is a tuned hyperparameter rather than a constant, and that published evidence points both ways: on one benchmark executing 16 steps beat executing fewer (90% to 96%), while for one model the full 50-step chunk was the worst setting tested — 51.8% against 82.8% at an execution depth of 10. So do not simply "execute everything"; sweep it, and treat the sweep as part of your evaluation rather than as plumbing.

**Cause 1 — The delta transform was applied twice, so the model is trained to predict a quantity that does not mean what anyone thinks it means.**

- **Test:** Print five consecutive `(state_t, action_{t:t+H})` pairs and check that `action_t - state_t` is small and centred. If it is roughly twice the size of the motion actually demonstrated, your data is already in delta form and you applied another delta transform on top. Measured on LIBERO: the actions are already `goal - current`, but `pi0_fast_libero` applies a delta transform again, so the model trains to predict `goal - 2*current`.
- **Fix:** Set `extra_delta_transform=False` when your dataset is already delta. **This is the largest single measured win in this entire repo**: LIBERO-10 goes from 60.5 +/- 1.0% to 84.7 +/- 1.7% with mean/std normalisation, and 75.1 +/- 1.5% to 85.9 +/- 0.6% with quantile, over 30k steps and three seeds, with no change to the model or the training code. Twenty-four points from a representation check that takes five minutes. The same experiment also settles a question people argue about: **once the action convention is correct, quantile normalisation is only marginally better than mean/std** (85.9 versus 84.7). The folklore gap between them is mostly this bug wearing a normalisation costume.
- **Source:** <https://github.com/Physical-Intelligence/openpi/issues/1047> · <https://github.com/Physical-Intelligence/openpi/pull/971>

**Cause 2 — Phase aliasing — the same observation requires different actions in different phases, and nothing in the input says which phase you are in.**

- **Test:** Take each frame, find its K nearest neighbours in state space, and measure how spread out those neighbours are along normalised episode time. A mean spread above ~0.10 means states recur across phases. Run `python scripts/diag_dataset.py <dataset> --n-phases 3`.
- **Fix:** Label every frame with its CURRENT sub-task and use that as the instruction, keeping the episodes intact. Then make sure the label actually reaches the policy — see the next cause. Reweighting or rebalancing the dataset cannot fix an unidentifiable input; the conditional distribution is genuinely multivalued and a flow-matching head will regress to the mean of the modes, which the robot shows as stalling.

**Cause 3 — A dead proprioceptive state channel — the policy is effectively vision-only.**

- **Test:** Print per-dimension mean/std of `observation.state`; a constant or all-zero dimension is dead. Then ablate the state at inference: replace it with zeros and with another frame's state, and measure how far the predicted action chunk moves relative to the natural cross-observation variation. `python scripts/diag_policy.py --dataset <ds> --config <cfg> --test ablate`.
- **Fix:** pi0.5 feeds the state as discretised tokens into the VLM rather than as a continuous input, so dim order, scale and the q01/q99 statistics must match the checkpoint. Note that this behaviour is *derived*, not fixed: in openpi, `discrete_state_input` defaults to `None` and is resolved as `discrete_state_input = pi05`, so pi0.5 turns it on and pi0 turns it off — but `pi05_libero` explicitly sets it to `False` because LIBERO has no proprioceptive state. That means two people with identical robots can get different behaviour depending on which recipe they copied — read the flag out of the config rather than assuming, and check it when a recipe transfer does not behave as expected. If enough state dimensions are dead or mis-scaled, the tokens are constant and the phase becomes unobservable. The mechanism is concrete: the state is binned into 256 buckets over the normalised [-1, 1] range, so bad normalisation statistics make every dimension saturate at bin 0 or bin 255 — turning the state into a *constant string* that carries no information at all while still being present in the input.
- **Source:** <https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0_config.py>

**Cause 4 — The action expert has collapsed to the unconditional mean action.**

- **Test:** Predict chunks for observations sampled across the whole episode. If the predictions barely differ between wildly different states, the conditioning is gone. `python scripts/diag_policy.py ... --test collapse`.
- **Fix:** Usually learning rate too high, too few steps for the frozen-VLM recipe, or action targets/normalisation wrong such that predicting the mean is the loss optimum. Check the chunk targets first: verify that `actions[t, k]` really is the action at frame `t+k` within the same episode, and that the flow-matching loss is masked on padded steps.

**Cause 5 — Idle frames at the head of every episode taught the policy to do nothing at the reset state.**

- **Test:** Compare the fraction of near-zero-action frames in the first ~10 frames of each episode against the rest of the episode.
- **Fix:** Drop or down-weight those frames and retrain. This is the cheapest fix in the whole document and it is frequently the answer — if the operator starts recording before touching the controller, every episode contributes a large, perfectly consistent 'at this state, do not move' sample. This is not a heuristic: the openpi training recipe ships an idle filter as a default, filtering "any time steps for which the next chunk of actions would be largely idle". There is also industrial-scale evidence for the failure mode itself: the AgiBot World pipeline discovered excessive idle time and inconsistent transitions **only after deploying a trained policy**, not by auditing the data, and had to add a post-processing step to remove idle frames. If a 1M-trajectory industrial pipeline found this by deploying rather than by inspecting, inspecting your dataset by eye will not find it either.
- **Source:** <https://github.com/Physical-Intelligence/openpi/blob/main/examples/droid/README_train.md> · <https://arxiv.org/abs/2503.06669>

**Cause 6 — Episode-head frames dominate and the policy never sees the later phases from its own state distribution (covariate shift).**

- **Test:** Open-loop check: put the robot or the recorded state back onto the expert trajectory, feed the expert observation, and see whether the predicted chunk reproduces the expert's continuation. If open loop is fine but closed loop stalls, the model is not the problem.
- **Fix:** Collect recovery and intermediate-start data: start the robot at the entrance state of every sub-task, including slightly off-expert states. This is the only thing that actually addresses compounding error.

**Cause 7 — Quantile normalisation computed on a small dataset has shrunk the effective action range, so the policy both trains on and emits scaled-down motion.**

- **Test:** Compare the q01/q99 spread of your actions against the range of motion your demonstrations actually contain, and check how much of the training data falls in the middle of the normalised range. Reported in openpi: pi0.5 fine-tuned with LoRA on the same single-arm data as pi0 performed substantially worse, with quantile normalisation on a small dataset named as a contributing cause.
- **Fix:** Note how this is wired: in openpi the flag is set as `use_quantile_norm=model_config.model_type != ModelType.PI0`, so quantile normalisation is hard-coded ON for pi0.5 and OFF for pi0 — you do not choose it, and the plot is easy to miss. The quantiles come from per-dimension running histograms (5,000 bins), so they are bin edges rather than exact percentiles, and the normalised values are **not clipped** — anything outside q01/q99 simply maps outside [-1, 1] and trains as-is. The reported fix for small fine-tunes is to disable it (`use_quantile_norm=False`, which requires patching the config), align batch size and learning rate with the shipped `pi05_libero` recipe rather than the pi0 defaults, and consider full fine-tuning or expert-only training rather than LoRA on both backbones. This cause is easy to miss because the loss looks healthy: the targets are scaled down consistently, so the model fits them well while emitting motion too small to do the task. It presents as hesitation or undershoot rather than as an obviously broken policy.
- **Source:** <https://github.com/Physical-Intelligence/openpi/issues/763> · <https://github.com/Physical-Intelligence/openpi/issues/692> · <https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/training/config.py>

Sources: <https://mlanthology.org/corl/2025/jain2025corl-enabling/> · <https://arxiv.org/abs/2509.07953>

### The robot hesitates or does not move at the beginning of a rollout, then behaves normally.

`severity: medium` · `frequency: common`

**Cause 1 — Near-zero actions recorded at the start of each episode (recording started before teleoperation began).**

- **Test:** Measure the mean action magnitude of the first N frames of each episode versus the episode median.
- **Fix:** Trim the head frames at dataset build time, or start recording only once motion begins. Also check the tail — operators often stop moving before stopping the recording.

**Cause 2 — Observation pipeline latency: the first inference runs on a stale or uninitialised observation.**

- **Test:** Log the timestamp of the observation that produced each action chunk and compare against the control-loop tick that consumed it.
- **Fix:** Prime the inference pipeline before enabling the controller, and discard the first chunk if its observation predates the start of the rollout.

### Motion is jerky, or the robot moves in short bursts with pauses between them.

`severity: high` · `frequency: common`

**Cause 1 — Re-planning every control step while only the first few steps of each predicted chunk are trustworthy.**

- **Test:** Compare `n_action_steps = 1` against executing the full chunk (or a majority of it). Measure both smoothness and task success.
- **Fix:** Execute more of each chunk, use temporal ensembling to blend overlapping chunks, or adopt RTC for asynchronous execution. See `data/deployment.yaml`.

**Cause 2 — Inference latency exceeds the wall-clock duration of the chunk being executed.**

- **Test:** Measure end-to-end inference latency (observation in, chunk out) and compare it to `chunk_size / control_fps`.
- **Fix:** Either increase the chunk horizon, shorten inference (quantisation, distillation, smaller visual encoder), or decouple inference from control asynchronously.

**Cause 3 — Action space mismatch between training and deployment — absolute versus delta, or a different control frequency.**

- **Test:** Correlate `action[t]` against `state[t+1] - state[t]` versus `state[t+1]`. Whichever correlates more strongly indicates the convention your data was recorded in.
- **Fix:** Match the convention the checkpoint was trained with, and confirm the training frame rate equals the deployment control rate. A chunk horizon is defined in frames, so a frequency mismatch silently changes its physical duration.

### Only the first step or two of each predicted action chunk look correct; the rest is wrong.

`severity: high` · `frequency: common`

**Cause 1 — Chunk targets are padded over the end of the episode and the loss is not masked there.**

- **Test:** Compute the mean valid fraction of each chunk target (frames near an episode end have partially invalid targets) and plot the loss as a function of chunk index k. If loss is low at k=0 and rises sharply, suspect the targets. `python scripts/diag_dataset.py <dataset> --chunk-size 50`.
- **Fix:** Mask the flow-matching loss on padded steps, and check what value the loader pads with. Repeating the last valid action is far less harmful than padding with zeros, which explicitly teaches 'stop moving' at the end of every chunk.

**Cause 2 — Genuine multimodality that the model is averaging along the horizon.**

- **Test:** Run the collapse test from the first symptom; if the k=0 action is also inflated or wrong, it is conditioning, not padding.
- **Fix:** Resolve the phase ambiguity first. Mode averaging is a symptom of an under-specified input, not a loss-function bug.

### Changing the language instruction has no effect on behaviour.

`severity: high` · `frequency: common`

**Cause 1 — The instruction never reaches the tokenizer — wrong key name or a prompt dropped in the observation transform.**

- **Test:** Ablate the prompt at inference (empty string, then a completely different instruction) and measure the change in predicted actions relative to the natural cross-observation variation.
- **Fix:** Fix the observation plumbing. Then verify that each training frame carries its own instruction rather than one global string for the whole episode.

**Cause 2 — One global instruction for a chained task, so the instruction cannot disambiguate phases even in principle.**

- **Test:** Check how many distinct instruction strings are in the dataset relative to the number of sub-tasks.
- **Fix:** Re-label per sub-task segment. This is the same root cause as the phase-aliasing symptom and the same fix.

**Cause 3 — Co-training or fine-tuning let the action expert drift away from the language-conditioned representation.**

- **Test:** Evaluate the fine-tuned policy on a paraphrased instruction set. If paraphrases fail but the exact training string works, the model has memorised the string rather than grounded it.
- **Fix:** Include instruction paraphrases in the fine-tuning data. See the pi0.5 knowledge-insulation approach if you are co-training on heterogeneous data.

### The policy works on the robot it was trained on and fails completely on a different arm or gripper.

`severity: high` · `frequency: common`

**Cause 1 — Normalisation statistics do not match the new embodiment — either the wrong ones are loaded, or the dataset's are missing.**

- **Test:** Two things to check. (a) openpi stores statistics alongside the checkpoint and lets you reload a per-embodiment set (`trossen`, `droid`, `franka`, `ur5e`, `arx`, ...) via `AssetsConfig`. Compare per-dimension q01/q99 of your actions and states against whichever set is being used. (b) For LeRobot datasets, check that `meta/stats.json` actually contains `q01` and `q99` — if it does not, training fails on the first batch with `ValueError: QUANTILES normalization mode requires q01 and q99 stats`.
- **Fix:** openpi's own guidance is to **try both** — reload the pretrained statistics and compute fresh ones — and keep whichever works better. Reloading can be *better* when your robot matches a pre-training embodiment, because the actions then land in a familiar range. The widely repeated advice to "always recompute" is stronger than what the model authors actually recommend. If you recompute, use `lerobot-edit-dataset --operation.type recompute_stats`, and note that recording aggregates quantiles from per-episode summaries into a conservative envelope (min for q <= 50, max for q > 50) rather than true dataset quantiles — which changes the normalised targets and therefore the loss scale.
- **Source:** <https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md> · <https://huggingface.co/docs/lerobot/en/pi05>

**Cause 2 — Action dimension or ordering differs, and the mismatch is being absorbed by padding.**

- **Test:** Print the raw action vector alongside the state vector for a few frames and check the joint ordering matches the URDF you are commanding.
- **Fix:** Fix the ordering explicitly and re-verify. Padded or permuted dimensions can train to a plausible-looking loss while producing physically wrong motion.

**Cause 3 — The gripper action polarity is inverted between model families, and nothing asserts it.**

- **Test:** Command a known gripper value and watch what the jaws do. In openpi the convention is `0 = open`, `1 = closed`; in OpenVLA it is the opposite, with a positive value meaning open. Both are verified in code, and neither framework asserts your convention at load time.
- **Fix:** Write the polarity down next to the action-space definition and assert it once at startup with a physical observation, not a code comment. The symptom is distinctive and easy to misread as a policy failure: the robot reaches the object correctly and then never grasps it, because it is closing the gripper when the policy meant to open.
- **Source:** <https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md>

**Cause 4 — Camera pose and intrinsics differ, so the visual conditioning is out of distribution.**

- **Test:** Hold the policy's view fixed and ablate the images; then compare the deployment camera pose against the recorded one.
- **Fix:** Match camera placement first — it is cheaper than retraining. If you cannot, collect a small amount of data on the new setup and fine-tune rather than expecting transfer.

### Excellent success rate in simulation, poor on hardware.

`severity: high` · `frequency: very common`

**Cause 1 — Covariate shift: the policy has never seen the states its own errors lead to.**

- **Test:** Open-loop teacher forcing on expert states. Good open-loop accuracy with bad closed-loop performance is the signature.
- **Fix:** Recovery data and intermediate-state initialisation, as in the first symptom. Also consider DAgger-style correction collection.

**Cause 2 — Simulation-only visual and dynamic fidelity gaps (lighting, textures, friction, compliance, latency).**

- **Test:** Evaluate on randomised visual conditions in sim; if performance collapses, you are measuring a visual shortcut rather than a policy.
- **Fix:** Domain randomisation, and more importantly real data. Note that sim evaluation is a screening tool, not a proxy for deployment readiness.

**Cause 3 — No latency model: the deployment loop is slower than the training loop assumed.**

- **Test:** Measure the real observation-to-action latency and re-run the evaluation with that delay injected in sim.
- **Fix:** Fix the timing architecture (see the stutter symptom) rather than retraining.

### Success rate moves by 20 points between evaluation runs with no code change.

`severity: medium` · `frequency: common`

**Cause 1 — Too few trials to distinguish the conditions.**

- **Test:** Compute a confidence interval on your current trial count. Twenty trials cannot resolve a ten-point difference.
- **Fix:** Pre-register the number of trials and the initial conditions. Randomise object poses across trials and report intervals, not point estimates.

**Cause 2 — Initial conditions are not controlled, so you are measuring the object placement distribution as much as the policy.**

- **Test:** Log the initial object pose per trial and check whether failures cluster in particular regions.
- **Fix:** Define a fixed, documented set of initial states and reuse it across every comparison. This also makes failures debuggable, because the same setup can be replayed.

**Cause 3 — Thermal or calibration drift over a long evaluation session.**

- **Test:** Run the same fixed condition at the start and end of the session and compare.
- **Fix:** Interleave conditions rather than running them in blocks, and re-check calibration between blocks.

### The policy behaves as if your configuration changes had no effect.

`severity: high` · `frequency: common`

**Cause 1 — `pretrained_path` loads weights only — the checkpoint's stored config values silently fall back to defaults.**

- **Test:** Print the effective policy config after loading, not the one you passed. LeRobot documents this explicitly for pi0.5: `--policy.pretrained_path` loads weights only, so `lerobot/pi05_libero_base`, which stores both `n_action_steps` and `empty_cameras`, falls back to `50` and `0` unless you pass them explicitly.
- **Fix:** Pass the values explicitly rather than relying on them being restored from the checkpoint, and verify by printing the constructed policy. The same class of bug affects any framework that separates "load weights" from "load config".
- **Source:** <https://huggingface.co/docs/lerobot/en/pi05>

**Cause 2 — Normalisation mapping default differs between the base checkpoint and your recipe.**

- **Test:** Check which mapping is in effect. LeRobot's pi0.5 example passes `--policy.normalization_mapping='{\"ACTION\": \"MEAN_STD\", \"STATE\": \"MEAN_STD\", \"VISUAL\": \"IDENTITY\"}'` explicitly, because pi0.5's own default is quantile — and the reference checkpoint the results were measured on used mean/std.
- **Fix:** Match the mapping to the checkpoint you are comparing against, and state which one you used when reporting results. Two runs with different mappings are not comparable.
- **Source:** <https://huggingface.co/docs/lerobot/en/pi05>

**Cause 3 — A CLI argument was silently overridden by a namespaced default, so the value you passed never reached the optimizer or the trainer.**

- **Test:** Print the constructed config after argument parsing and compare it against what you passed on the command line. LeRobot has nested optimizer settings where the path matters — a bare `--optimizer.lr` can be shadowed by the policy-namespaced form, so the learning rate that actually trains is not the one on your command line. Related traps in the same family: the launcher matters (`accelerate` rather than `torchrun`), and distributed data parallel does **not** reduce per-GPU memory the way people assume it does — it replicates the model, so it speeds up training without making the model fit.
- **Fix:** Treat the parsed config, not your command line, as the ground truth, and print it once at the start of every run. This is the same discipline as reading `num_learnable_params` instead of trusting your PEFT flags: in this ecosystem, the configuration you intended and the configuration that ran are frequently different, and nothing errors when they are.

**Cause 4 — Statistics cached inside an existing checkpoint override newly computed dataset statistics.**

- **Test:** Recompute the dataset statistics and check whether the loaded checkpoint's stored statistics changed.
- **Fix:** They will not — LeRobot states that statistics already saved inside an existing checkpoint are not affected by recomputing dataset stats. Start from a checkpoint without embedded statistics, or expect the stored ones to win.
- **Source:** <https://huggingface.co/docs/lerobot/en/pi05>

### Training runs and loss decreases, but the policy behaves as if the data were never normalized — or normalization appears to do nothing at all.

`severity: high` · `frequency: common`

**Cause 1 — Normalization is silently skipped because the statistics keys do not match, and the code returns the tensor unchanged instead of raising.**

- **Test:** Check which statistics keys the checkpoint actually carries. Multi-dataset checkpoints store them under dataset-prefixed keys such as `so100.buffer.action.mean`, while the lookup uses the bare key `action`. The processor's guard is `if norm_mode == IDENTITY or key not in self._tensor_stats: return tensor` — a silent return, not an error. A minimal check: load the policy, feed a fake action, and test whether the unnormalized output differs from the input.
- **Fix:** Do not assume normalization is happening because the pipeline contains a normalization step. Verify numerically on one batch — compare `unnormalize(normalize(a))` against `a` and assert the round trip. Reported on `lerobot/smolvla_base`, where normalization and unnormalization are both skipped, and independently confirmed by a third party.
- **Source:** <https://github.com/huggingface/lerobot/issues/4415>

**Cause 2 — Quantiles were aggregated across merged datasets by averaging per-source quantiles, which is mathematically invalid.**

- **Test:** Count what fraction of your training values fall outside the saved `q01`/`q99`. If it is far above the expected ~2%, the statistics are wrong. This has been measured on a published dataset: on `lerobot/droid_1.0.1`, the shipped action `q01`/`q99` leave between 12.18% and 79.03% of action values outside the per-dimension range, against roughly 2% for exact full-data bounds. On a merged dataset, 41.65% of state joint 1 and 42.12% of action joint 1 values fell outside the saved quantiles while `mean` differed by only 1e-7.
- **Fix:** Recompute quantiles over all frames rather than merging summaries; a repair tool exists for the DROID case. The reason this matters more than it sounds: everything outside `q01`/`q99` maps outside `[-1, 1]` after normalization, so for pi0.5 a large fraction of normal training samples have normalized targets outside the expected range — which changes the loss scale rather than producing an obvious error. **Status: mitigated, not solved.** The change that landed ([PR #3804](https://github.com/huggingface/lerobot/pull/3804), merged 2026-08-06) replaces the invalid weighted mean with a conservative min/max envelope — it deliberately *widens* `q01`/`q99` instead of computing them, which reduces the damage without producing correct quantiles. The stricter proposal that would have omitted the invalid aggregates ([PR #4172](https://github.com/huggingface/lerobot/pull/4172)) was **closed unmerged**, and the underlying issue ([#4156](https://github.com/huggingface/lerobot/issues/4156)) is **still open**. So do not read the fix as closure: an envelope is a bound, and it can still be wrong for your data.
- **Source:** <https://github.com/huggingface/lerobot/issues/4156> · <https://github.com/huggingface/lerobot/pull/3804> · <https://github.com/sawhney17/droid-quantile-repair>

**Cause 3 — The statistic key does not match the live camera or feature name, so a required entry is missing.**

- **Test:** Look for an assertion mentioning `infinity` at evaluation time. The legacy buffers are initialised to `+inf` precisely so that a missing statistic is loud — but only if the key is looked up at all.
- **Fix:** Make the camera names in your robot config match the feature names in the dataset's `meta/stats.json` exactly. This is the canonical mismatch: the data was recorded with one set of camera keys and the robot is configured with another.
- **Source:** <https://github.com/huggingface/lerobot/issues/1095>

**Cause 4 — A pipeline migration mangled a feature name containing an underscore.**

- **Test:** Print the feature keys the policy declares and compare them against the keys present in the statistics.
- **Fix:** An unconditional `replace(\"_\", \".\")` during normalization-statistics extraction turns `observation.environment_state` into `observation.environment.state`, which is then never found. The policy's declared feature keys must be treated as authoritative rather than re-derived from the string.
- **Source:** <https://github.com/huggingface/lerobot/issues/4451>

### Fine-tuning runs to completion and the loss decreases normally, but success rate is at or near zero.

`severity: high` · `frequency: common`

**Cause 1 — The PEFT target-module list excludes the vision tower and language backbone, so almost nothing task-relevant is being trained.**

- **Test:** Read `num_learnable_params` out of the training log rather than trusting the CLI flags you passed. In a controlled SmolVLA / SO-101 experiment using the default target list, only 742,656 parameters were trainable (0.16 %) and **every mid-training evaluation scored 0.0 %**, while full fine-tuning was already at 60 % on its first evaluation.
- **Fix:** Expand the target list rather than abandoning LoRA. Adding three q/v families and fully training the five embodiment projection layers (rank 64, lr 3e-4) reached 94.0 / 84.0 / 98.0 % with 9,851,728 trainable parameters (2.1 %) — about 1/40 of full fine-tuning's parameters at matched task performance. Match the trainable *fraction*, not the rank: the same rank 64 is 2.1 % of SmolVLA but roughly 0.58 % of pi0, because the models have very different numbers of attention sites.
- **Source:** <https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/12-VLA%E5%BE%AE%E8%B0%83%E5%AE%9E%E6%88%98.md> · <https://huggingface.co/docs/lerobot/en/smolvla>

**Cause 2 — An adapter flag silently changed the meaning of the model path, so you trained an adapter on top of an adapter — or read a base model as one.**

- **Test:** Check whether the loaded base model is the one you expect. In LeRobot, setting `--policy.use_peft=true` makes the framework interpret `--policy.path` as an already-trained adapter directory.
- **Fix:** Use `--peft.method_type` / `--peft.r` to attach a new adapter to a clean base, and verify the base checkpoint that actually got loaded.
- **Source:** <https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/12-VLA%E5%BE%AE%E8%B0%83%E5%AE%9E%E6%88%98.md>

**Cause 3 — Config drift: several settings differ from the reference recipe at once, and the combination is not the one that was validated.**

- **Test:** Diff your training config against the shipped reference config field by field, not by remembering which flags you passed.
- **Fix:** Use the shipped config verbatim first and confirm it reproduces the published number, then change exactly one thing at a time. This is the documented resolution of a reported pi0.5-at-1%-on-LIBERO case, where the drift was LoRA plus `discrete_state_input=False` plus a non-standard horizon plus hand-computed statistics that differed from the checkpoint's, plus ad-hoc learning-rate changes.
- **Source:** <https://github.com/Physical-Intelligence/openpi/issues/711>

### Training collapses, produces NaNs, or the loss is orders of magnitude wrong — with no obvious change to the data.

`severity: high` · `frequency: common`

**Cause 1 — The pretrained weights silently failed to load, because a dependency bump renamed the checkpoint keys.**

- **Test:** Compare the loss at step 0 against the loss you expect from a loaded pretrained model. A jump from around 0.5 to around 4.5 is the reported signature of pretrained weights not loading at all — you are training from scratch and the only clue is the loss scale.
- **Fix:** Pin the `transformers` version, or verify explicitly after loading that the weights are present and non-random. Do not rely on the loader to raise: the reported failure was silent. This is the general lesson for every framework in this space — assert that the checkpoint loaded rather than assuming it did.
- **Source:** <https://github.com/huggingface/lerobot/issues/1406>

**Cause 2 — Action standard deviation is zero or near-zero, so the normalised targets explode.**

- **Test:** Print per-dimension action std for your dataset before training. A zero or denormal value here produces a loss in the millions rather than a plausible-looking one.
- **Fix:** Add a small epsilon to the denominator. Suggested range from community reports is roughly 2e-5 to 2e-4 — large enough to avoid the explosion, small enough not to distort well-conditioned dimensions.
- **Source:** <https://github.com/Physical-Intelligence/openpi/issues/814>

**Cause 3 — Model compilation silently produces NaN through a miscompiled mask.**

- **Test:** If NaNs appear only with compilation enabled, disable it and rerun the same config.
- **Fix:** Turn compilation off to confirm, then either pin the compiler version or leave it off. The point is not that compilation is broken — it is that enabling it changes numerics, so it belongs in the diff when you bisect a NaN.
- **Source:** <https://github.com/huggingface/lerobot/issues/4178>

**Cause 4 — A resumed PEFT run silently discarded the adapters.**

- **Test:** After resuming, check the trainable parameter count again — it should match the run you resumed from.
- **Fix:** Re-verify the adapter state after every resume rather than assuming the framework restored it. Resuming is exactly where silent state loss hides, because the loss curve continues smoothly whether or not the adapters came back.
- **Source:** <https://github.com/huggingface/lerobot/issues/3459>


---

## Contributing

The most valuable contribution is **a failure you actually hit and how you fixed it** —
citations are cheap. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
# add an entry to data/*.yaml, then:
python scripts/build_readme.py    # regenerate this README
python scripts/check_links.py     # verify every URL resolves
```

`README.md` is generated. CI re-runs the generator and fails if the committed README differs,
so the README can never drift from the data. Do not edit it by hand.

Entry format and the provenance rules: [SCHEMA.md](SCHEMA.md).

## Related

- **[VLA-Handbook](https://github.com/sou350121/VLA-Handbook)** — the closest existing work,
  Chinese, 662★, updated daily. Strong on hardware specifics and ROS2/edge tuning. If you read
  Chinese, read it; this repo exists because there is no English equivalent.
- **[natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai)** — production
  patterns, ROS2 middleware, and the ISO/UL standards this repo maps onto VLA inference loops.
- **[AIDASLab](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation)** —
  paper-level data lifecycle: curation, cleaning, annotation, relabeling.

## License

MIT — see [LICENSE](LICENSE).
