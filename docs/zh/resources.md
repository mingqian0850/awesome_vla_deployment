# 资源目录

[首页](../../README.md) · [English](../resources.md)

条目描述对应所链接来源及其记录版本。研究结果不等于已独立复现的部署方案。

## 目录

- [数据采集与准备](#data)
- [模型与训练框架](#training)
- [微调与配置](#training-recipes)
- [部署与运行](#deployment)
- [延迟与优化测量](#benchmarks)
- [评测](#evaluation)
- [已报告的失败案例](#counter-evidence)
- [运行监测与防护](#safety)
- [许可资料](#licensing)
- [延伸学习](#learning-resources)

<a id="data"></a>
## 数据采集与准备

采集、检查并整理机器人示教。

<a id="lerobot-docs"></a>
### [LeRobot documentation](https://huggingface.co/docs/lerobot/index)

文档 · 有真机使用记录 · Apache-2.0

官方文档，涵盖组装、标定、遥操作、数据集、训练和策略执行。

<a id="lerobot-il-robots"></a>
### [LeRobot — imitation learning on real robots](https://huggingface.co/docs/lerobot/en/il_robots)

文档 · 有真机使用记录

端到端模仿学习流程：组装、标定、采集、训练与评测。

<a id="lerobot-so101"></a>
### [LeRobot — SO-101 assembly and calibration](https://huggingface.co/docs/lerobot/en/so101)

文档 · 有真机使用记录

SO-101 机械臂的硬件组装与标定说明。

<a id="aloha"></a>
### [ALOHA / Mobile ALOHA](https://github.com/MarkFzp/mobile-aloha)

代码仓库 · 研究阶段

双臂主从遥操作与模仿学习平台。

<a id="umi"></a>
### [Universal Manipulation Interface (UMI)](https://github.com/real-stanford/universal_manipulation_interface)

代码仓库 · 研究阶段

通过带相机的手持夹爪采集示教，采集时无需部署机器人在场。

<a id="open-television"></a>
### [Open-TeleVision](https://github.com/OpenTeleVision/TeleVision)

代码仓库 · 研究阶段

面向双臂和人形机器人的 VR 遥操作，包含立体视频传输与主动视觉。

<a id="robot-teach"></a>
### [robot_teach (Open-Teach)](https://github.com/chiawenwang/robot_teach)

代码仓库 · 研究阶段

利用 VR 手部跟踪示教构建可复用的操作策略。

<a id="robomimic"></a>
### [robomimic](https://github.com/ARISE-Initiative/robomimic)

代码仓库 · 有真机使用记录 · MIT

离线模仿学习框架，提供示教数据集及训练、评测流程。

<a id="robosuite"></a>
### [robosuite](https://github.com/ARISE-Initiative/robosuite)

代码仓库 · 有真机使用记录

模块化机器人操作仿真框架，也是 robomimic 使用的仿真环境之一。

<a id="mimicgen"></a>
### [MimicGen](https://github.com/NVlabs/MimicGen)

代码仓库 · 研究阶段

通过物体位姿变换与动作重规划扩充少量示教。

<a id="open-x-embodiment"></a>
### [Open X-Embodiment](https://robotics-transformer-x.github.io/)

数据集 · 有真机使用记录

汇集多种机器人和实验室的跨形态操作数据，采用 RLDS 格式。

<a id="open-x-embodiment-repo"></a>
### [google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment)

代码仓库 · 有真机使用记录

加载 Open X-Embodiment 的代码及各子数据集说明。

<a id="data-curation-paper"></a>
### [Robot Data Curation](https://arxiv.org/abs/2502.08623)

论文 · 研究阶段

研究根据示教对策略学习的影响进行筛选和整理。

<a id="curating-online-experience"></a>
### [Curating Demonstrations using Online Experience](https://arxiv.org/abs/2503.03707)

论文 · 研究阶段

利用在线交互经验选择训练示教。

<a id="subgoal-transitions"></a>
### [Enabling Long(er) Horizon Imitation for Manipulation Tasks by Modeling Subgoal Transitions](https://mlanthology.org/corl/2025/jain2025corl-enabling/)

论文 · 研究阶段

通过建模子目标之间的转移，支持更长时程的模仿学习。

<a id="rac-recovery"></a>
### [RaC: Robot Learning for Long-Horizon Tasks by Scaling Recovery and Correction](https://arxiv.org/abs/2509.07953)

论文 · 研究阶段

研究恢复与纠正数据，帮助长时程策略应对自身执行误差。

<a id="action-only-scorers-fail"></a>
### [Action-Only Scorers Fail on the Structural Defects That Degrade Imitation Policies](https://arxiv.org/abs/2606.05588)

论文 · 研究阶段

检查仅根据动作计算的数据质量分数能否发现空闲帧、状态歧义和伪相关等缺陷。

<a id="balanced-bc-imbalanced"></a>
### [Towards Balanced Behavior Cloning from Imbalanced Datasets](https://arxiv.org/abs/2508.06319)

论文 · 研究阶段

研究行为、技能样本数量不平衡时的行为克隆。

<a id="openvla-mixture-recipe"></a>
### [OpenVLA's data balancing and mixture recipe over Open X-Embodiment](https://arxiv.org/abs/2406.09246)

论文 · 研究阶段

记录 OpenVLA 在机器人、任务和场景分布上的数据混合、重加权与排除规则。

<a id="agibot-world-pipeline"></a>
### [AgiBot World — data collection pipeline](https://arxiv.org/abs/2503.06669)

论文 · 有真机使用记录

AgiBot World 描述试采集、操作员校验、标注及根据执行失败改进数据的流程。

<a id="eventual-dead-frames"></a>
### [Cutting dead frames from DROID — 500 hours of robot data in 32 seconds](https://www.eventual.ai/blog/cutting-dead-frames-from-droid)

技术文章 · 有真机使用记录

在 DROID 数据中检测并裁剪空闲帧的工程实例。

<a id="daft-motion-trimming"></a>
### [Daft — motion trimming for physical AI](https://docs.getdaft.io/en/stable/examples/motion-trimming-physical-ai/)

工具 · 有真机使用记录

利用运动信息裁剪机器人视频片段的示例 notebook。

<a id="lerobot-doctor"></a>
### [lerobot-doctor — dataset quality diagnostics](https://github.com/jashshah999/lerobot-doctor)

工具 · 研究阶段

用于检查 LeRobot 数据集空闲时段、异常与离群 episode 的社区工具。

<a id="lerobot-language-schema"></a>
### [LeRobot — language annotation schema](https://github.com/huggingface/lerobot/blob/main/docs/source/language_and_recipes.mdx)

文档 · 有真机使用记录

定义持续生效和事件级语言字段、配方化条件输入及联合子任务监督；具体字段需匹配固定的软件版本。

<a id="lerobot-annotation-pipeline"></a>
### [LeRobot annotation pipeline — VLM auto-labelling that produces those columns](https://github.com/huggingface/lerobot/blob/main/docs/source/annotation_pipeline.mdx)

文档 · 有真机使用记录

利用 VLM 生成计划、子任务、记忆与事件标注，并提供校验和成本估算。

<a id="lerobot-annotation-ui"></a>
### [lerobot-annotate — annotation UI](https://github.com/huggingface/lerobot-annotate)

代码仓库 · 有真机使用记录

用于标注 LeRobot 数据集的网页界面。

<a id="lerobot-good-dataset"></a>
### [LeRobot — what makes a good dataset](https://huggingface.co/blog/lerobot-datasets)

技术文章 · 有真机使用记录

数据采集指南，涵盖相机视角、光照、帧率、特征命名与任务描述。

<a id="hd-space"></a>
### [HD-Space — staged collection for later-phase start states](https://arxiv.org/abs/2505.17389)

论文 · 研究阶段

先用已有策略到达中间状态，再从这些状态采集后续阶段示教。

<a id="robomimic-what-matters"></a>
### [What Matters in Learning from Offline Human Demonstrations](https://arxiv.org/abs/2108.03298)

论文 · 研究阶段

研究离线模仿学习中的示教质量、相机观测与检查点评测。

<a id="data-scaling-laws"></a>
### [Data Scaling Laws in Imitation Learning for Robotic Manipulation](https://arxiv.org/abs/2410.18647)

论文 · 研究阶段

研究操作策略的泛化能力如何随环境、物体与示教多样性变化。

<a id="egomimic-data"></a>
### [EgoMimic — human and robot data processing](https://github.com/SimarKareer/EgoMimic)

代码仓库 · 研究阶段

追踪的人类 Aria 示教与机器人遥操作数据的处理及训练代码。

**使用条件：** 人类和机器人观测需要对齐，不是任意视频到机器人动作的转换。

<a id="ego-exo4d-skills"></a>
### [Ego-Exo4D — human skill understanding](https://docs.ego-exo4d-data.org/)

数据集 · 研究阶段

用于技能理解的同步人类第一／第三视角观测与活动标注。

**使用条件：** 没有目标机器人控制命令标签；检查子集标注和访问条款。

<a id="agibot-world-data"></a>
### [AgiBot World — released data and visualization](https://github.com/OpenDriveLab/AgiBot-World)

代码仓库 · 研究阶段

机器人操作数据、可视化与已发布学习组件的官方入口。

**使用条件：** 固定数据版本；不能等同于 G2 工厂数据集或完整双足行走数据。

<a id="gr1-teleop-sim-data"></a>
### [GR-1 — simulated tabletop teleoperation](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-Sim)

数据集 · 研究阶段

可浏览 state/action 字段的 GR-1 仿真示教。

**使用条件：** 数据卡标注 CC-BY-NC-4.0；仿真数据不是真实生产证据。

<a id="training"></a>
## 模型与训练框架

用于策略训练与推理的实现。

<a id="openpi"></a>
### [openpi (Physical Intelligence)](https://github.com/Physical-Intelligence/openpi)

代码仓库 · 有真机使用记录 · Apache-2.0

pi0、pi0-FAST 与 pi0.5 的官方实现，包含训练配置和机器人推理工具。

<a id="lerobot"></a>
### [LeRobot (Hugging Face)](https://github.com/huggingface/lerobot)

代码仓库 · 有真机使用记录 · Apache-2.0

覆盖硬件、数据集、遥操作、策略训练与执行的机器人学习工具栈。

<a id="isaac-gr00t"></a>
### [NVIDIA Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)

代码仓库 · 有真机使用记录

NVIDIA 的视觉语言动作模型及其微调、评测工具。

<a id="openvla"></a>
### [OpenVLA](https://github.com/openvla/openvla)

代码仓库 · 研究阶段

使用语言模型主干和离散动作 token 的 7B 视觉语言动作模型。

<a id="openvla-oft"></a>
### [OpenVLA-OFT](https://github.com/moojink/openvla-oft)

代码仓库 · 研究阶段

采用并行解码、动作分块与连续动作的 OpenVLA 微调配方。

<a id="rdt-1b"></a>
### [RDT-1B (RoboticsDiffusionTransformer)](https://github.com/thu-ml/RoboticsDiffusionTransformer)

代码仓库 · 研究阶段

面向双臂操作的扩散 Transformer，使用统一的物理动作表示。

<a id="octo"></a>
### [Octo](https://github.com/octo-models/octo)

代码仓库 · 研究阶段

在 Open X-Embodiment 上训练的 Transformer 策略，支持灵活的观测与动作空间。

<a id="fluxvla"></a>
### [FluxVLA](https://github.com/FluxVLA/FluxVLA)

代码仓库 · 研究阶段

连接 VLA 数据处理、训练与部署的工程平台。

<a id="rlinf"></a>
### [RLinf](https://github.com/RLinf/RLinf)

代码仓库 · 研究阶段

提供具身模型训练与真实机器人示例的强化学习基础设施。

<a id="vla-foundry"></a>
### [TRI-ML/vla_foundry](https://github.com/TRI-ML/vla_foundry)

代码仓库 · 研究阶段

Toyota Research Institute 的 VLA 训练与评测工具集。

<a id="openpi-tool"></a>
### [Isaiah-WU/Openpi_tool — pi05 fine-tuning and real-robot deployment](https://github.com/Isaiah-WU/Openpi_tool)

代码仓库 · 研究阶段

用于 pi0.5 微调与真机部署的中文教程和工具。

<a id="pi05-xarm-tutorial"></a>
### [dzj441/pi05XarmTutorial](https://github.com/dzj441/pi05XarmTutorial)

代码仓库 · 研究阶段

将 pi0.5 部署到 UFactory xArm 的教程。

<a id="df-post-training"></a>
### [Denghaoyuan123/DF-post-training](https://github.com/Denghaoyuan123/DF-post-training)

代码仓库 · 研究阶段

基于扩散的 VLA 策略后训练配方。

<a id="lerobot-realman"></a>
### [Humble2Full/lerobot-realman-vla](https://github.com/Humble2Full/lerobot-realman-vla)

代码仓库 · 演示阶段

基于 LeRobot 的 RealMan 机械臂学习与部署流程。

<a id="xpolicylab"></a>
### [MicroAGI-Labs/XPolicyLab](https://github.com/MicroAGI-Labs/XPolicyLab)

代码仓库 · 演示阶段

通过统一接口提供多种机器人策略实现。

<a id="training-recipes"></a>
## 微调与配置

动作表示、统计量、适配器与检查点处理。

<a id="openpi-requirements"></a>
### [openpi — GPU / VRAM requirements](https://github.com/Physical-Intelligence/openpi)

文档 · 有真机使用记录

openpi 记录推理、LoRA 与全量微调的显存要求；实际占用还受配置和额外开销影响。

**使用条件：** 历史单 GPU 表给出推理 >8 GB、LoRA >22.5 GB、全量微调 >70 GB。需核对来源版本，并为数据、优化器和保存操作预留空间。

<a id="openpi-norm-stats"></a>
### [openpi — normalisation statistics and when to reuse them](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

文档 · 有真机使用记录

归一化统计量与检查点一起保存；可复用匹配机器人形态的统计量，并与重新计算的结果对比。

<a id="openpi-action-space"></a>
### [openpi — action space and control frequency conventions](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

文档 · 有真机使用记录

记录不同机器人的关节顺序、夹爪约定和控制频率；需要读取实际机器人形态的配置。

<a id="droid-action-space"></a>
### [DROID — action representation](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

文档 · 有真机使用记录

所引用的 openpi 配置中，DROID 使用七维关节速度加一维夹爪动作，控制频率为 15 Hz。

<a id="lerobot-pi05-recipe"></a>
### [LeRobot — pi0.5 fine-tuning recipe](https://huggingface.co/docs/lerobot/en/pi05)

文档 · 有真机使用记录

pi0.5 微调参考配置，包含 batch size、步数、精度、梯度检查点及仅训练专家的变体。

<a id="lerobot-pi0-recipe"></a>
### [LeRobot — pi0 fine-tuning recipe](https://huggingface.co/docs/lerobot/en/pi0)

文档 · 有真机使用记录

pi0 微调参考配置，包含编译、梯度检查点和 BF16 设置。

<a id="openpi-idle-filter"></a>
### [openpi — idle filter for DROID training](https://github.com/Physical-Intelligence/openpi/blob/main/examples/droid/README_train.md)

文档 · 有真机使用记录

DROID 训练配方过滤后续动作块大部分为空闲动作的时间步。

<a id="rtc-training"></a>
### [Training-Time Action Conditioning for Efficient Real-Time Chunking](https://arxiv.org/abs/2512.05964)

论文 · 研究阶段

为 RTC 训练动作前缀条件输入；最大预期推理延迟以控制步数表示。

<a id="openvla-ft-comparison"></a>
### [OpenVLA — fine-tuning strategy comparison](https://arxiv.org/abs/2406.09246)

测量或基准 · 研究阶段

OpenVLA 在同一评测协议下比较全量微调、LoRA 与部分冻结，并报告显存和可训练参数量。

<a id="lerobot-lora-target-trap"></a>
### [SmolVLA — LoRA target modules](https://github.com/huggingface/lerobot/issues/4415)

讨论记录 · 研究阶段

一项 SmolVLA 实验报告 LoRA 目标模块的覆盖范围显著影响执行成功率；仅设置 rank 不能完整定义适配器。

<a id="pi05-small-dataset-quantile"></a>
### [pi0.5 fine-tunes worse than pi0 on small single-arm datasets](https://github.com/Physical-Intelligence/openpi/issues/763)

讨论记录 · 研究阶段

一例小数据 pi0.5 性能退化涉及归一化与训练设置；建议修改仍需通过受控对比验证。

补充来源: [↗ 1](https://github.com/Physical-Intelligence/openpi/issues/763) · [↗ 2](https://github.com/Physical-Intelligence/openpi/issues/692)

<a id="pi05-config-drift"></a>
### [pi0.5 — configuration-drift report](https://github.com/Physical-Intelligence/openpi/issues/711)

讨论记录 · 研究阶段

一例 LIBERO 低成功率与适配器、状态输入、动作步数和统计量偏离参考配置有关。

<a id="checkpoint-selection"></a>
### [Checkpoint evaluation protocols](https://github.com/Physical-Intelligence/openpi)

讨论记录 · 研究阶段

使用验证误差、固定预算和 rollout 评测选择检查点的实例；不同框架的指标不能直接互换。

<a id="evaluation-noise-floor"></a>
### [Evaluation variability](https://github.com/NVIDIA/Isaac-GR00T)

讨论记录 · 研究阶段

已报告的评测波动说明，需要在实际配置上测量运行间差异及有限样本不确定性。

<a id="horizon-ablations"></a>
### [SmolVLA — prediction and execution horizons](https://arxiv.org/abs/2506.01844)

测量或基准 · 研究阶段

SmolVLA 分别研究预测步数与实际执行步数；它们是不同参数，影响取决于任务。

<a id="normalization-three-regimes"></a>
### [Normalization modes](https://arxiv.org/abs/2506.01844)

文档 · 有真机使用记录

不同模型与配方使用不同归一化方式；应检查最终配置，不能只凭模型名称推断。

<a id="fsq-tokenizer-trap"></a>
### [openpi — FSQ and FAST tokenizers](https://github.com/Physical-Intelligence/openpi)

代码仓库 · 有真机使用记录

openpi 的 fsq_tokenizer.py 用于 RoboArena 基线；FAST 是另一种基于 DCT/BPE 的动作 tokenizer，用于 FAST 模型变体。

<a id="lerobot-relative-action-floor"></a>
### [LeRobot relative-action support has a version floor](https://github.com/huggingface/lerobot/pull/2970)

文档 · 有真机使用记录

相对动作处理器与参数需要兼容的 LeRobot 版本；记录中的实现由 PR #2970 引入。

<a id="vram-boundary-counterevidence"></a>
### [LoRA — practical memory limits](https://github.com/Physical-Intelligence/openpi/issues/379)

讨论记录 · 研究阶段

用户报告显示，在特定配置下，满足名义 LoRA 显存要求的 24 GB GPU 仍可能溢出。

<a id="fine-tune-cost-anchor"></a>
### [Fine-tuning cost example](https://docs.picknik.ai/how_to/vla/train_a_vla_policy/)

技术文章 · 有真机使用记录

一项微调记录提供历史成本示例；实际账单取决于服务商、硬件、时长和当前价格。

<a id="multi-gpu-not-auto-scaled"></a>
### [Distributed training configuration](https://github.com/huggingface/lerobot/blob/main/docs/source/multi_gpu_training.mdx)

文档 · 有真机使用记录

分布式训练不会自动调整学习率或步数；DDP 通常在每张设备上复制模型状态。

<a id="demos-is-the-wrong-unit"></a>
### [Demonstration volume and coverage](https://github.com/huggingface/lerobot/blob/main/docs/source/il_robots.mdx)

文档 · 研究阶段

同时记录 episode 数量、时长、控制频率与任务覆盖；相同 episode 数量可能对应不同数据量。

<a id="aalto-execution-horizon"></a>
### [Execution-horizon paired comparison](https://aaltodoc.aalto.fi/items/711175d6-6d75-4751-af72-b055bd8cd4db/full)

测量或基准 · 研究阶段

一项配对试验研究比较不同执行步数；最佳值仅对应所测检查点与任务。

<a id="openvla-demo-replay"></a>
### [OpenVLA — LIBERO demonstration replay](https://arxiv.org/abs/2406.09246)

论文 · 有真机使用记录

OpenVLA 作者回放 LIBERO 示教，并剔除不满足任务成功标准的 episode。

<a id="checkpoint-write-oom"></a>
### [Checkpoint-saving memory failure](https://github.com/moojink/openvla-oft/issues/118)

讨论记录 · 研究阶段

正常训练步的显存足够时，保存检查点仍可能发生显存溢出。

<a id="deployment"></a>
## 部署与运行

连接策略推理、观测与机器人控制。

<a id="eapn-execution-aligned-replanning"></a>
### [EAPN — execution-aligned asynchronous replanning](https://arxiv.org/abs/2610.06090)

论文 · 研究阶段

在重规划之间对齐相关噪声与已承诺动作，改善动作块的连续性。

**使用条件：** 预印本；本仓库未复现其实现与硬件结果。

<a id="rephrase-before-you-act"></a>
### [Rephrase Before You Act — instruction normalization for a frozen VLA](https://arxiv.org/abs/2610.10526)

论文 · 研究阶段

根据训练任务评测归纳指令改写规则，再为冻结的策略改写输入指令。

**使用条件：** 需评测改写是否保留用户意图。已查看所链接代码资料，但复用许可与端到端复现仍未验证。

补充来源: [↗ 1](https://sttawm.github.io/rephrase-before-you-act/) · [↗ 2](https://github.com/sttawm/phrase-rl)

<a id="ogam-runtime-monitor"></a>
### [OGAM — object-grounded attention monitoring](https://arxiv.org/abs/2610.05878)

论文 · 研究阶段

将对象级注意力与成功参考轨迹比较以触发提前停止；需要访问注意力及校准数据。

**使用条件：** 需要对象掩码和成功参考、校准轨迹。停止性能只对应论文实验协议，不是通用安全保证。

<a id="lerobot-rtc-modes"></a>
### [LeRobot — guided vs trained RTC and checkpoint delay limits](https://github.com/huggingface/lerobot/blob/main/docs/source/rtc.mdx)

文档 · 研究阶段 · Apache-2.0

说明 guided RTC 与训练式前缀条件输入；trained 模式要求兼容且训练最大延迟为正的检查点。

**使用条件：** trained 模式下，execution_horizon 与 inference.queue_threshold 必须覆盖检查点的最大训练延迟；执行步数不得超过 chunk_size 减去该延迟。代码与文档需固定为匹配版本。

<a id="lerobot-inference"></a>
### [LeRobot — Policy Deployment (lerobot-rollout)](https://huggingface.co/docs/lerobot/en/inference)

文档 · 有真机使用记录 · Apache-2.0

官方部署指南，介绍执行策略、执行步数与运行时子任务接口。

<a id="rtc"></a>
### [Real-Time Execution of Action Chunking Flow Policies (RTC)](https://neurips.cc/virtual/2025/loc/san-diego/poster/117747)

论文 · 研究阶段

生成异步动作块时以已承诺的动作为条件，改善执行连续性。

<a id="vla-rail"></a>
### [VLA-RAIL: A Real-Time Asynchronous Inference Linker for VLA Models and Robots](https://arxiv.org/abs/2512.24673)

论文 · 研究阶段

通过异步连接层将模型推理与机器人控制循环解耦。

<a id="world-action-models-real-time"></a>
### [World Action Models in Real Time: An Empirical Study of Smooth Execution via Asynchronous Deployment](https://arxiv.org/abs/2608.01880)

论文 · 研究阶段

研究世界动作模型在异步部署下的动作平滑性。

<a id="holobrain-0"></a>
### [HoloBrain-0 Technical Report](https://arxiv.org/abs/2602.12062)

论文 · 研究阶段

技术报告，包含同步执行完整动作块时的时序限制分析。

<a id="vla-cpp"></a>
### [vla.cpp: A Unified Inference Runtime for Vision-Language-Action Models](https://arxiv.org/abs/2606.08094)

论文 · 研究阶段

为视觉语言动作模型设计的推理运行时。

<a id="eva-client"></a>
### [EVA-Client](https://github.com/Noietch/EVA-CLIENT)

代码仓库 · 研究阶段

跨机器人平台的部署、评测与数据采集框架。

<a id="eva-client-paper"></a>
### [EVA-Client (paper)](https://arxiv.org/abs/2607.02646)

论文 · 研究阶段

介绍 EVA-Client 机器人部署与评测框架的论文。

<a id="robot-control-stack"></a>
### [robot-control-stack](https://github.com/RobotControlStack/robot-control-stack)

代码仓库 · 研究阶段

不依赖 ROS 的学习策略部署栈，连接仿真与真实机器人。

<a id="minivla"></a>
### [MiniVLA](https://github.com/Zhenxintao/MiniVLA)

代码仓库 · 演示阶段

面向 TensorRT 边缘推理的紧凑型 VLA 实现。

<a id="embodirun"></a>
### [EmbodiRun](https://github.com/BUAA-CI-LAB/EmbodiRun)

代码仓库 · 演示阶段

具身策略的执行运行时。

<a id="factory-floor-case-study"></a>
### [A Factory-Floor Deployment Case Study of VLA Pipelines for Industrial Packaging](https://arxiv.org/abs/2605.27461)

论文 · 研究阶段

工业包装场景的 VLA 部署案例，记录工作流程与实际失败情况。

<a id="pi0-deploy-notes"></a>
### [pi0 fine-tuning guide with domestic-arm deployment (Chinese)](https://zeeklog.com/p0de-wei-diao-ru-he-ji-yu-ge-chong-kai-yuan-shu-ju-ji-yi-ji-si-you-shu-ju-ji-wei-diao-openpi-han-wo-si-qi-yue-de-wei-diao-shi-jian-ji-openpizai-guo-chan-bi-shang-de-bu-shu-8)

技术文章 · 研究阶段

关于 openpi 微调与机械臂部署的中文教程。

<a id="lerobot-rtc-docs"></a>
### [LeRobot — Real-Time Chunking reference](https://github.com/huggingface/lerobot/blob/main/docs/source/rtc.mdx)

文档 · 有真机使用记录

RTC 执行步数、引导权重、前缀注意力与推理延迟的配置参考。

<a id="lerobot-async"></a>
### [LeRobot — legacy asynchronous inference (pinned reference)](https://github.com/huggingface/lerobot/blob/7e60cd26f7f8a38bb8df8fc5e2966a93f1364f47/docs/source/async.mdx)

文档 · 历史参考

通过策略服务器与机器人客户端实现异步推理和动作传输。

**使用条件：** 历史 PolicyServer/RobotClient 文档。当前 main 已移除该旧模块，改用 rollout 下的远程推理；代码与文档必须匹配版本。

补充来源: [↗ 1](https://github.com/huggingface/lerobot/blob/main/docs/source/inference.mdx)

<a id="lerobot-rollout"></a>
### [LeRobot — rollout strategies and fleet operations](https://github.com/huggingface/lerobot/blob/main/docs/source/inference.mdx)

文档 · 有真机使用记录

支持自主执行、记录、事件片段保存及人工介入的 rollout 模式。

<a id="lerobot-hil"></a>
### [LeRobot — human-in-the-loop data collection](https://github.com/huggingface/lerobot/blob/main/docs/source/hil_data_collection.mdx)

文档 · 有真机使用记录

在策略执行过程中采集人工纠正数据。

<a id="ros2-control-trajectory"></a>
### [ros2_control — joint_trajectory_controller](https://control.ros.org/rolling/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html)

文档 · 有真机使用记录

插值执行关节轨迹；限位是否生效取决于完整的控制器与硬件配置。

<a id="ros2-control-admittance"></a>
### [ros2_control — admittance_controller](https://control.ros.org/rolling/doc/ros2_controllers/admittance_controller/doc/userdoc.html)

文档 · 有真机使用记录

根据测得的外力调整指令运动的导纳控制器。

<a id="ros2-control-gripper"></a>
### [ros2_control — parallel_gripper_controller](https://control.ros.org/jazzy/doc/ros2_controllers/parallel_gripper_controller/doc/userdoc.html)

文档 · 有真机使用记录

平行夹爪的标准控制接口。

<a id="neural-controller"></a>
### [G-Levine/neural_controller](https://github.com/G-Levine/neural_controller)

代码仓库 · 研究阶段

将学习策略接入 ros2_control 控制器管理器。

<a id="xbotics-ch13"></a>
### [Xbotics 具身智能教程 第13讲 — real-time VLA inference (Chinese)](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/13-VLA%E5%89%8D%E6%B2%BF.md)

技术文章 · 研究阶段

介绍首动作延迟、动作块停顿和实时分块的中文课程，包含计算示例。

<a id="faster"></a>
### [FASTER: Rethinking Real-Time Flow VLAs](https://arxiv.org/abs/2603.19199)

论文 · 研究阶段

研究降低流模型策略反应延迟的去噪调度。

<a id="legato"></a>
### [Legato: Learning Native Continuation for Action Chunking Flow Policies](https://arxiv.org/abs/2602.12978)

论文 · 研究阶段

学习动作块的原生延续，减少每次都重新生成完整计划的需要。

<a id="delay-aware-diffusion"></a>
### [Delay-Aware Diffusion Policy](https://arxiv.org/abs/2512.07697)

论文 · 研究阶段

在多种延迟下训练扩散策略，使其考虑观测陈旧问题。

<a id="speculative-policy-orchestration"></a>
### [Speculative Policy Orchestration: A Latency-Resilient Framework for Cloud-Robotic Manipulation](https://arxiv.org/abs/2603.19418)

论文 · 研究阶段

处理网络延迟、抖动与动作队列耗尽的云端机器人策略编排。

<a id="roboecc"></a>
### [RoboECC: Multi-Factor-Aware Edge-Cloud Collaborative Deployment for VLA Models](https://arxiv.org/abs/2603.20711)

论文 · 研究阶段

研究如何在边缘设备和云端之间分配 VLA 计算。

<a id="comvla"></a>
### [ComVLA: Communication-Aware Split Inference for VLA Models in 6G-Connected Robotics](https://arxiv.org/abs/2609.07838)

论文 · 研究阶段

针对带宽受限机器人系统的通信感知分割推理。

<a id="viam-calibration-worksheet"></a>
### [Frame calibration worksheet](https://github.com/viam-devrel/pick-and-place/blob/main/setup/frame-calibration-worksheet.md)

文档 · 有真机使用记录

用于记录机器人坐标系标定的工作表。

<a id="ros2-control-mock"></a>
### [ros2_control — mock components](https://control.ros.org/jazzy/doc/ros2_control/hardware_interface/doc/mock_components_userdoc.html)

文档 · 有真机使用记录

在没有实体机器人时测试控制器的模拟硬件组件。

<a id="ros2-tracing"></a>
### [ros2_tracing](https://github.com/ros2/ros2_tracing)

代码仓库 · 有真机使用记录

基于 LTTng 的 ROS 2 跟踪工具，用于测量执行和通信事件。

<a id="tensorrt-dev-guide"></a>
### [NVIDIA TensorRT Developer Guide](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html)

文档 · 有真机使用记录

TensorRT 算子、精度、动态形状与插件的参考文档。

<a id="benchmarks"></a>
## 延迟与优化测量

特定硬件与实验协议下报告的测量结果。

<a id="flashrt-benchmark-table"></a>
### [FlashRT — cross-source latency table (π0.5, GR00T N1.6)](https://github.com/flashrt-project/FlashRT/blob/main/docs/benchmark_comparison.md)

测量或基准 · 研究阶段

VLA 延迟汇总；只有硬件、模型和计时范围一致的行才能直接比较。

**使用条件：** 不同计时范围下报告的加速比不可直接比较；应区分初始化、首次推理和稳态。

<a id="flashrt"></a>
### [FlashRT — small-batch realtime inference engine](https://github.com/flashrt-project/FlashRT)

代码仓库 · 研究阶段

面向小批量 VLA 的 CUDA 推理引擎，涵盖 pi0、pi0.5 和 GR00T N1.6。

<a id="nvidia-forum-thor-rtx"></a>
### [NVIDIA Developer Forum — real measured π0.5 / GR00T latency on Thor and RTX 5090](https://forums.developer.nvidia.com/t/real-time-inference-on-thor-rtx-pi0-5-gr00t-n1-6-1-7-thor-23-hz-rtx-5090-50-80hz/368788)

讨论记录 · 有真机使用记录

开发者报告的 pi0.5、GR00T 在 Jetson Thor 与 RTX 5090 上的实测；结果仅对应原帖配置。

<a id="groot-optimization-docs"></a>
### [Isaac GR00T — official deployment optimisation numbers](https://nvidia-isaac-gr00t.mintlify.app/deployment/optimization)

文档 · 有真机使用记录

厂商提供的 GR00T N1.6 多 GPU 测量，比较原生 PyTorch、编译和 TensorRT。

<a id="embodied-efficiency"></a>
### [embodied-efficiency — batch-1 optimization experiments](https://github.com/LaelaZorana/embodied-efficiency)

测量或基准 · 研究阶段

一组实验报告 batch size 为 1 时仅权重量化的 INT8/INT4 比 BF16 更慢，并分析 CUDA Graph 与动作信息陈旧程度。

<a id="jetson-pi"></a>
### [Jetson-PI — onboard async VLA inference](https://github.com/PKU-SEC-Lab/Jetson-PI)

代码仓库 · 研究阶段

在 Jetson 本机运行异步 VLA；有效控制频率与模型推理频率是不同指标。

<a id="xpu-characterization"></a>
### [Characterizing VLA Models across XPUs](https://arxiv.org/abs/2604.24447)

论文 · 研究阶段

按视觉编码、语言前缀和动作专家分解 VLA 延迟，比较 GPU 与边缘设备。

<a id="foldquantvla"></a>
### [FoldQuantVLA — native low-bit quantisation for VLAs](https://arxiv.org/abs/2609.24433)

论文 · 研究阶段

利用一致性折叠为 VLA 内部结构设计低比特量化。

<a id="open-loop-revisited"></a>
### [Revisiting Open-Loop Execution in Robotics](https://arxiv.org/abs/2608.15938)

论文 · 研究阶段

研究开环执行与频繁重规划对任务表现的影响。

<a id="ros2-wireless"></a>
### [Optimizing ROS 2 Communication for Wireless Robotic Systems](https://arxiv.org/abs/2508.11366)

论文 · 研究阶段

测量无线网络中的 ROS 2 延迟、吞吐与背压，并提供 DDS 配置工具。

<a id="evaluation"></a>
## 评测

任务协议、样本量与失败分析。

<a id="vla-eval-harness"></a>
### [allenai/vla-evaluation-harness](https://github.com/allenai/vla-evaluation-harness)

代码仓库 · 研究阶段

在多种环境中评测 VLA 策略的统一框架。

<a id="simplerenv"></a>
### [SimplerEnv](https://github.com/simpler-env/SimplerEnv)

代码仓库 · 研究阶段

用于研究操作策略向真实机器人迁移的仿真环境。

<a id="robocasa"></a>
### [RoboCasa](https://github.com/robocasa/robocasa)

代码仓库 · 研究阶段

用于评测通用机器人行为的厨房操作仿真任务。

<a id="eval-statistical-bounds"></a>
### [Statistical lower bounds on behavior-cloning success probability](https://arxiv.org/abs/2405.05439)

论文 · 研究阶段

根据有限试验计算行为克隆成功概率下界的统计方法。

<a id="phail-benchmark"></a>
### [PhAIL: A Real-Robot VLA Benchmark and Distributional Methodology](https://arxiv.org/abs/2605.29710)

论文 · 研究阶段

真实机器人 VLA 基准，包含分布评测与不确定性报告方法。

<a id="eval-optimal-stopping"></a>
### [Near-optimal stopping in the 10-50 trial regime](https://arxiv.org/abs/2503.10966)

论文 · 研究阶段

研究机器人试验次数较少时的评测停止规则。

<a id="libero-reproduction-gap"></a>
### [LIBERO — evaluation-budget differences](https://arxiv.org/abs/2506.01844)

论文 · 研究阶段

比较论文中的试验数量与 LIBERO 默认配置；使用相同基准名称不代表评测协议相同。

<a id="score-the-steps"></a>
### [Score the Steps, Not Just the Goal — subgoal-level evaluation](https://arxiv.org/abs/2509.19524)

论文 · 研究阶段

利用 VLM 评估子目标进展，而不仅记录最终任务结果。

<a id="failure-taxonomy-cluster"></a>
### [Failure taxonomies for manipulation — five groups, five different label sets](https://arxiv.org/abs/2512.01946)

论文 · 研究阶段

涵盖规划错误、执行质量、本体感觉诊断、可解释失败标签和恢复基准的资料。

<a id="robotwin2"></a>
### [RoboTwin 2.0](https://robotwin-platform.github.io/)

测量或基准 · 研究阶段

包含域随机化的双臂操作基准。

<a id="evaluation-resolution"></a>
### [Evaluation sample-size example](https://github.com/Physical-Intelligence/openpi)

讨论记录 · 研究阶段

同一检查点在 10 次和 50 次试验下得到不同成功率估计；应同时报告样本量与不确定性。

<a id="libero-three-numbers"></a>
### [Three different 'official' LIBERO evaluation protocols](https://arxiv.org/abs/2506.01844)

论文 · 研究阶段

区分 LIBERO 初始状态集合、默认评测次数与论文中的多轮试验协议。

<a id="counter-evidence"></a>
## 已报告的失败案例

特定任务与配置中观测到的限制。

<a id="language-grounding-gap"></a>
### [Language-grounding interventions](https://arxiv.org/abs/2610.06235)

论文 · 研究阶段

固定场景、改变合法的目标指令，可以发现策略是否依赖场景关联而没有服从目标变化。

**使用条件：** 结论适用于所测策略与实验协议；来源包含仿真和真机实验。

<a id="oft-hardware-drift"></a>
### [OpenVLA-OFT — hardware drift report](https://openvla-oft.github.io/)

技术文章 · 有真机使用记录

OpenVLA-OFT 作者报告：代码和训练数据不变，腕部相机位置变化与关节磨损仍会导致性能下降。

<a id="picknik-loss-curve"></a>
### [PickNik — training loss and rollout evaluation](https://docs.picknik.ai/how_to/vla/train_a_vla_policy/)

文档 · 有真机使用记录

训练手册指出：没有独立评测时，示教损失较低不能证明闭环任务成功。

<a id="oft-more-data-did-not-fix-it"></a>
### [OpenVLA-OFT — language-grounding data experiment](https://openvla-oft.github.io/)

技术文章 · 有真机使用记录

在 OpenVLA-OFT 的一个任务中，示教数量增加到两倍或四倍仍未解决语言接地问题，还需要调整条件输入机制。

<a id="lerobot-25-episodes-failed"></a>
### [SmolVLA — demonstration-count comparison](https://github.com/huggingface/lerobot/blob/main/docs/source/smolvla.mdx)

文档 · 有真机使用记录

SmolVLA 文档报告一个方块任务中 25 条示教表现较差、50 条更好；该结论来自特定任务。

<a id="lerobot-50-is-a-floor"></a>
### [LeRobot — demonstration coverage guidance](https://github.com/huggingface/lerobot/issues/2378)

讨论记录 · 有真机使用记录

LeRobot 建议固定位置任务可从约 50 条示教起步；物体或位置变化后，应增加覆盖范围。

<a id="pi0-authors-hedge"></a>
### [openpi — embodiment-transfer limitations](https://github.com/Physical-Intelligence/openpi)

文档 · 有真机使用记录

openpi 说明训练机器人与其他平台存在形态差异，迁移成功并无保证。

<a id="oft-copies-bad-demos"></a>
### [OpenVLA-OFT — demonstration-quality report](https://openvla-oft.github.io/)

技术文章 · 有真机使用记录

一项舀取实验显示，策略会重复低质量示教中过深插入的动作。

<a id="sim-benchmarks-hid-the-problem"></a>
### [OpenVLA — Franka deployment case study](https://openaccess.thecvf.com/content/CVPR2026W/MEIS/html/Liu_Bridging_the_Pretrain-to-Real_Gap_Alignment_Challenges_in_Deploying_Generalist_VLA_CVPRW_2026_paper.html)

论文 · 研究阶段

将 OpenVLA 部署到真实 Franka Research 3 时，除仿真评测外，还需处理解码、夹爪阈值和几何适配。

<a id="openvla-100-demos"></a>
### [OpenVLA — fine-tuning data guidance](https://github.com/openvla/openvla/issues/12)

讨论记录 · 研究阶段

OpenVLA 作者描述了一种约 100 条示教的微调配置；动作 token 准确率与实际任务成功率仍需分开测量。

<a id="smolvla-pretraining-payoff"></a>
### [SmolVLA — pretraining comparison](https://arxiv.org/abs/2506.01844)

论文 · 研究阶段

SmolVLA 论文在其 SO100 实验协议下报告，使用社区数据预训练后任务成功率提高。

<a id="position-beats-velocity"></a>
### [Diffusion Policy — position and velocity control](https://arxiv.org/abs/2303.04137)

论文 · 有真机使用记录

Diffusion Policy 在所测任务中报告位置控制优于速度控制，两者对延迟的敏感程度不同。

<a id="safety"></a>
## 运行监测与防护

监测方法与工程资料；研究监测器不等于安全认证。

<a id="dguv-ifa-cobot"></a>
### [DGUV/IFA — collaborative robot safety (readable interpretation)](https://www.dguv.de/ifa/fachinfos/kollaborierende-roboter/index-2.jsp)

标准资料 · 有真机使用记录

DGUV/IFA 关于协作机器人危险与防护措施的资料；适用性取决于具体系统和任务。

<a id="iso-21448-sotif"></a>
### [ISO 21448 — Safety of the Intended Functionality (SOTIF)](https://www.bsigroup.com/en-GB/standards/iso-21448/)

标准资料 · 有真机使用记录

SOTIF 是针对道路车辆功能不足风险的标准；在此作为概念背景，不是通用机器人认证规则。

**使用条件：** 适用范围为道路车辆，不应将该资料表述为所有机器人的必需标准。

<a id="hide-and-seek-trajectories"></a>
### [Hide-and-Seek in Trajectories: Discovering Failure Signals for VLA Runtime Monitoring](https://arxiv.org/abs/2605.30834)

论文 · 研究阶段

研究策略轨迹中可用于运行时监测的失败信号。

<a id="safecast"></a>
### [SAFECAST: Robust Failure Detection for VLA Policies](https://arxiv.org/abs/2608.04246)

论文 · 研究阶段

研究视觉和指令分布变化下经过校准的失败检测。

<a id="rafail"></a>
### [RAFAIL: Relationship-Aware Failure Detection for Robotic Manipulation](https://arxiv.org/abs/2609.18324)

论文 · 研究阶段

结合关系语义检查与较快的分布外信号，检测操作失败。

<a id="rewind-il"></a>
### [Rewind-IL: Online Failure Detection and State Respawning for Imitation Learning](https://arxiv.org/abs/2604.16683)

论文 · 研究阶段

在模仿学习任务中结合在线失败检测与状态重置。

<a id="nvidia-halos"></a>
### [NVIDIA Halos for robotics](https://developer.nvidia.com/blog/inside-nvidia-halos-for-robotics-a-full-stack-functional-safety-system-for-physical-ai/)

文档 · 有真机使用记录

面向物理 AI 系统的厂商功能安全架构；单个组件不能证明整个部署已通过认证。

<a id="mender-ota"></a>
### [Mender — open-source OTA updates with rollback](https://mender.io/)

工具 · 有真机使用记录

支持版本回滚的软件更新基础设施。

<a id="licensing"></a>
## 许可资料

分别检查源数据、代码、权重与依赖的许可。

<a id="pi0-license-contradiction"></a>
### [pi0/pi0.5 — recorded license-metadata discrepancy](https://huggingface.co/api/models/lerobot/pi05_base)

文档 · 有真机使用记录

记录了 pi0/pi0.5 权重模型卡元数据与文档的许可表述差异；应查阅所用版本的实际许可文件。

**使用条件：** 此处保留历史核验结果。复用前应根据实际许可证和模型版本解决元数据与文档的冲突。

<a id="verify-license-from-api"></a>
### [Hugging Face — license metadata](https://huggingface.co/api/models/lerobot/pi05_base)

文档 · 有真机使用记录

Hub API 元数据可帮助定位模型和数据集声明的许可证，但不能代替实际许可条款。

<a id="dataset-license-spectrum"></a>
### [Dataset license references](https://huggingface.co/api/datasets/RogerQi/PH2D)

资料缺口 · 研究阶段

数据集对原始数据、衍生数据和再分发的许可不同，需要分别检查训练混合中的每个组成部分。

<a id="learning-resources"></a>
## 延伸学习

课程、手册与主题索引。

<a id="vla-handbook"></a>
### [sou350121/VLA-Handbook](https://github.com/sou350121/VLA-Handbook)

资料索引 · 有真机使用记录 · unknown

介绍 VLA 模型、机器人硬件和部署的中文手册。

<a id="awesome-embodied-vla-va-vln"></a>
### [jonyzhang2023/awesome-embodied-vla-va-vln](https://github.com/jonyzhang2023/awesome-embodied-vla-va-vln)

资料索引 · 有真机使用记录

视觉语言动作、视觉动作与视觉语言导航研究索引。

<a id="gt-ripl-awesome-llm-robotics"></a>
### [GT-RIPL/Awesome-LLM-Robotics](https://github.com/GT-RIPL/Awesome-LLM-Robotics)

资料索引 · 有真机使用记录

语言模型在机器人领域的应用索引。

<a id="awesome-humanoid-robot-learning"></a>
### [YanjieZe/awesome-humanoid-robot-learning](https://github.com/YanjieZe/awesome-humanoid-robot-learning)

资料索引 · 有真机使用记录

人形机器人学习、遥操作与硬件研究索引。

<a id="awesome-physical-ai-natnew"></a>
### [natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai)

资料索引 · 有真机使用记录

物理 AI 中间件、系统架构与相关标准索引。

<a id="aidaslab-data-curation"></a>
### [AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation](https://github.com/AIDASLab/Awesome-VLA-Data-Collection-Synthesis-Curation)

资料索引 · 研究阶段

机器人数据采集、清洗、标注与增强的论文索引。

<a id="awesome-robot-data-engine"></a>
### [chang-xinhai/Awesome-Robot-Data-Engine](https://github.com/chang-xinhai/Awesome-Robot-Data-Engine)

资料索引 · 研究阶段

机器人数据采集、处理、格式与混合的资料索引。

<a id="awesome-long-horizon-robot-manipulation"></a>
### [Ziteng-Wang/Awesome-Long-Horizon-Robot-Manipulation](https://github.com/Ziteng-Wang/Awesome-Long-Horizon-Robot-Manipulation)

资料索引 · 研究阶段

长时程操作、记忆、进度与恢复机制的资料索引。

<a id="awesome-vla-yueen-ma"></a>
### [yueen-ma/Awesome-VLA](https://github.com/yueen-ma/Awesome-VLA)

资料索引 · 有真机使用记录

与综述配套的 VLA 论文索引。

<a id="awesome-rl-vla"></a>
### [Denghaoyuan123/Awesome-RL-VLA](https://github.com/Denghaoyuan123/Awesome-RL-VLA)

资料索引 · 研究阶段

VLA 模型强化学习后训练资料。

<a id="every-embodied"></a>
### [datawhalechina/every-embodied](https://github.com/datawhalechina/every-embodied)

资料索引 · 有真机使用记录

包含具身机器人动手项目的中文入门课程。

<a id="xbotics-handbook"></a>
### [Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook)

资料索引 · 有真机使用记录

涵盖感知、控制、数据、训练与部署的中文课程。

<a id="action-diffusion-handbook"></a>
### [AlmondGod/action-diffusion-handbook](https://github.com/AlmondGod/action-diffusion-handbook)

资料索引 · 研究阶段

介绍动作扩散及相关机器人策略架构的手册。
