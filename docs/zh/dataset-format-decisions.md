# 数据格式：按训练器选择并验收

[首页](../../README.md) · [English](../dataset-format-decisions.md) · [问题索引](decision-tables.md)

**先确定训练器及版本，再确定数据格式。**“有 MP4/Parquet/HDF5 文件”“符合读取器 schema”“动作含义与机器人一致”是三件事。转换容器只能解决其中一部分；本页给出选择、字段契约与验收步骤。

<a id="target"></a>
## 我准备用哪个训练器？

以下实现核查于 2026-10-21；短提交号对应表后固定来源。升级后重新做一次样本加载检查。

| 目标 | 数据要满足什么 | 具体文件/配置 | 容易误判的地方 |
| --- | --- | --- | --- |
| LeRobot `463202b`，使用 v3 读取路径 | 特征 schema、分片索引、episode 边界与媒体可被该版本读取 | `meta/info.json` 定义特征、FPS 和路径；`meta/episodes/` 保存分片索引；该代码默认任务表是 `meta/tasks.parquet` | v3 分片可能含多个 episode，不能靠文件名猜边界。该版指南仍有 `tasks.jsonl` 表述，应按实际代码和文件版本读取 |
| GR00T `dac54b3` | GR00T 风格的 LeRobot **v2**，加模态元数据和匹配的数据配置 | `meta/modality.json`、`meta/info.json`、`meta/episodes.jsonl`、`meta/tasks.jsonl`；Parquet 状态/动作和对应 MP4 | 现有 v3 需先用该仓库 `scripts/lerobot_conversion/convert_v3_to_v2.py` 转换，再检查 GR00T 模态要求；不能默认原生支持 v3 |
| openpi `215abfb` 的 LeRobot 数据路径 | 与该实现固定的 LeRobot 依赖兼容，并接通输入映射和归一化 | `pyproject.toml` 固定 LeRobot `0cf8648...`；`src/openpi/training/config.py` 中的数据配置与 transforms；匹配的 norm stats | “都是 LeRobot”不保证能直接读；数据字段重打包与动作转换仍需要按 policy 配置 |
| robomimic 0.5 文档路径 | robomimic schema 的 HDF5；所选算法需要的观测/元数据齐全 | `data/demo_0/actions`、`data/demo_0/obs/<key>`，以及相应 `next_obs`、轨迹属性、环境元数据和 split | HDF5 只是容器；任意 HDF5 或只有视频文件都不等于兼容数据集 |
| 训练器明确要求 RLDS/TFDS | 按其 builder 的 episode/step 结构及 feature spec 生成数据 | 每步边界标记和指定的观测、动作、任务字段；TFDS builder 定义实际 schema | RLDS 不是改个扩展名；`is_last` 与 `is_terminal` 语义不同，也不自动等于任务成功 |
| 还没确定模型/embodiment | 保留原始流、校准、时钟、命令/状态、任务与 episode 元数据；准备可重复转换器 | 先完成下方样本契约，确定目标后导出 | 不应提前丢掉原始时间戳或把人体关节当机器人关节监督 |

依据：[LeRobot v3 指南](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/docs/source/lerobot-dataset-v3.mdx)及[读取工具中的路径定义](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/src/lerobot/datasets/utils.py)；[GR00T 数据准备](https://github.com/NVIDIA/Isaac-GR00T/blob/dac54b313160c201c450f97df0fd74ebd379c892/getting_started/data_preparation.md)；[openpi 依赖](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/pyproject.toml)与[训练数据流程](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/README.md)；[robomimic schema](https://robomimic.github.io/docs/datasets/overview.html)；[RLDS 结构](https://github.com/google-research/rlds/blob/b35dac3a6b73396b0cb8773095999c4b5d70947c/README.md)。

<a id="contract"></a>
## 每条数据到底需要说明什么？

这是跨框架的**语义检查表**。左栏是概念名，不要求把所有数据集改成同名字段。

| 内容 | 最少说明什么 | 检查动作 |
| --- | --- | --- |
| Episode 与 split | 哪一段是一条尝试，何时开始/结束，属于训练还是验证 | 同一连续尝试不能随机拆帧泄漏进两侧；必要时再按工件、日期或工位隔离 |
| 时间 | 原始采集时间、时钟来源、单位、采样率、丢帧/重采样规则 | 画图像、状态、命令的时间线；确认固定时间偏移和最大对齐误差 |
| 视觉 | 相机名、图像形状、编码、颜色顺序；涉及几何时还有内外参 | 解码首/中/末帧；确认左右腕相机没有交换、RGB/BGR 没反 |
| 机器人状态 | 每一维的名称、顺序、单位、坐标系与测量含义 | 将数值与同一时刻姿态/视频对照；不要仅检查向量长度 |
| 动作标签 | 命令还是测量状态；绝对值还是增量；位置/速度/力矩；夹爪约定 | 跟踪采集代码到控制接口；没有命令记录时必须说明代理标签如何构造及误差 |
| 语言 | 文本或任务 ID 与映射表；指令对应的时间区间 | 解出几条 ID 看是否描述当前任务；工序改变时不能仍沿用错误标签 |
| 缺失与有效掩码 | 缺相机、未使用动作维度、末尾不足 H 步如何处理 | padding 不等于真实零动作；验证 loss 是否正确忽略无效目标 |
| 成功/失败与来源 | 结束原因、任务结果、干预、设备/操作者、处理版本 | episode 结束不等于成功；保留清洗前后样本的追溯关系 |

**双臂示例契约：**假设每臂 6 个关节加一个夹爪开度，动作共 14 维；这里假设它们是绝对目标。`[0:6]` 左臂关节 rad、`[6:7]` 左夹爪 m、`[7:13]` 右臂关节 rad、`[13:14]` 右夹爪 m。状态可以记录对应的实际测量值，但状态与命令不能互相冒充。实际机器人可能是 7 轴臂、灵巧手或末端位姿输出，不能照抄 14 维。

若 batch size B=2、动作预测长度 H=8，则此示例训练目标可为 `[2, 8, 14]`，单时刻状态为 `[2, 14]`。图像存储可能是 HWC uint8，模型入口可能要求 CHW 浮点与特定归一化；必须在转换后检查真实 batch。维度相同不代表单位或语义相同。

## GR00T 的模态映射：如何把向量拆对？

在上述 14 维假设下，`meta/modality.json` 的 **action 部分**可以表达为下面的片段；这是局部示例，不是可直接训练的完整文件。state、video、annotation、数据列和训练配置仍须配齐。

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

`end` 不包含在切片内。自定义的四个名称还必须与自己的 modality config 对应；只改 JSON 不会自动改变模型输入。该格式用拼接的 `float32` 状态/动作配合切片定义解释各部分。

语言字段也需要三处一致。以该版本示例的任务描述为例：Parquet 列为 `annotation.human.task_description`，`modality.json` 的 annotation 下为 `human.task_description`，训练配置 `modality_keys` 使用完整的 `annotation.human.task_description`。数值索引再映射到 `meta/tasks.jsonl` 的文本。其他数据集可能采用不同的 annotation 名称，应匹配实际列，而不是统一强改成示例名。

<a id="convert"></a>
## 根据手头数据决定下一步

| 我现在有的数据 | 可以先做什么 | 还必须补什么 |
| --- | --- | --- |
| 只有 ego MP4 | 工序切分、语言标注、视觉表征或动作语义学习 | 若要监督机器人动作，还需可用的动作标签来源；视频本身没有机器人命令 |
| 人体手/身体轨迹与 ego 视频 | 对齐时钟、标定坐标、检查轨迹，再研究目标机器人的重定向 | 机器人运动学、可达性/接触约束及目标控制表示；重定向结果需另行验证 |
| 视频 + 机器人状态 CSV + 命令日志 | 写转换器把时间对齐后的样本导入目标读取器 schema | episode、语言、单位、相机映射、元数据及缺失值策略 |
| 已有 LeRobot v3，要接此版本 GR00T | 运行上表对应的 v3→v2 转换工具；输出到新目录 | 转换后检查帧数、边界、语言列、模态切片和实际训练 batch；保留原数据 |
| 能加载，但动作维度不匹配 | 对照模型 action head、数据配置与真实控制接口 | 语义明确的适配、padding/mask 和归一化；不能靠随意截断或补零“修好” |
| 数据处理后验证结果异常好 | 查 episode/场景泄漏与归一化统计来源 | 训练/验证分开；重新拟合的统计只用训练划分；使用预训练固定统计时记录来源 |

<a id="acceptance"></a>
## 开始大规模转换或训练前怎么验收？

| 顺序 | 具体做什么 | 通过条件 / 不通过如何处理 |
| --- | --- | --- |
| 1. 锁定读取器 | 保存训练器提交、依赖锁、数据版本；用真正的训练数据加载路径读取一个 episode | 不是仅用通用 Parquet 工具打开；失败先查路径/schema/版本 |
| 2. 检查媒体与时间 | 解码首、中、末帧；比较状态/命令时间、任务 ID 与 episode 索引 | 无无法解释的重复、丢帧或偏移；误差需满足任务定义的时间预算 |
| 3. 核对语义 | 对照视频与采集接口，逐维检查左右臂、夹爪、单位和绝对/增量 | 能把一条动作解释成目标控制命令；仅检查 min/max 不足以确认 |
| 4. 查看转换后 batch | 打印 keys、dtype、shape、有限值、语言解码、有效 mask；抽查首尾动作块 | 无跨 episode 拼接；边界 padding 与 loss mask 一致；抽查归一化/反归一化可恢复原值 |
| 5. 小规模重复读取 | 在独立输出目录转换少量完整 episodes，然后关闭并重新打开读取器 | 统计计数一致、媒体可读、来源可追溯；LeRobot v3 写入结束调用其 `finalize()` 后再验收 |

通过以上检查表示数据接口经过初步验收，**不表示重定向可执行、模型已学会任务或真机部署已通过**。记录失败样本的 episode/frame ID，再查[训练监控](training-monitoring.md#metrics)与[数据基础](01-data-and-training.md)。本页未下载大规模数据或运行模型训练。
