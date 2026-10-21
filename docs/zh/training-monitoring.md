# 训练监控：选平台、接日志、读异常

[首页](../../README.md) · [English](../training-monitoring.md) · [问题索引](decision-tables.md)

**个人本地学习先用 TensorBoard；已有训练器带 W&B 集成时先用现成接口；团队需要自建统一实验记录时评估 MLflow。**这些是按使用条件给出的建议。监控平台负责记录与展示，不提供模型能否装进显存的保证，也不会自动得到机器人任务成功率。

<a id="platform"></a>
## 我的情况适合哪个平台？

| 我的情况 | 选择 | 最小接入方式 | 能看到什么 / 还缺什么 |
| --- | --- | --- | --- |
| 一台电脑，先看训练和验证曲线 | TensorBoard | 训练循环使用 `SummaryWriter` 写事件；启动本地面板 | 标量、图像等已记录信息；配置、数据版本和实验命名仍需自己管理 |
| 使用已集成 W&B 的训练器，想比较多次实验 | Weights & Biases（W&B） | 开启框架开关，指定项目；在线服务需账号与连接配置 | 汇总配置、曲线和记录的产物；闭环指标仍需评测程序写入 |
| 训练机不能联网，但以后可能同步记录 | 支持离线模式的 W&B 集成，或本地 TensorBoard | 例如 LeRobot 配置 `wandb.mode="offline"`；确认日志目录被保留 | 离线 W&B 先存本地，不等于云端实时可见；需要当场看曲线可用本地面板 |
| 团队希望统一保存实验、参数和产物，并管理服务存储 | MLflow Tracking | 配置 tracking URI，在训练代码调用记录 API | 团队运行记录与产物；需维护服务、存储和权限，并适配自定义 VLA 指标 |
| 只想确认 GPU 是否忙、显存是否接近满载 | 系统监控作为补充 | 在训练机器查看 GPU 利用率、显存和进程 | 不能替代 loss、数据版本或任务表现记录；高利用率不代表模型学对了 |

TensorBoard 的 PyTorch 接口见[官方 API](https://docs.pytorch.org/docs/2.14/tensorboard.html)；W&B 的记录方式见[官方 SDK](https://github.com/wandb/wandb/blob/dda9f931d389c9419171b01eb64ec7233f7d249a/README.md)；MLflow 的 run、参数、指标和产物概念见[Tracking 文档](https://mlflow.org/docs/latest/ml/tracking/)。选择时还应确认日志中的视频、配置或数据样本应存放在哪个环境。

<a id="integration"></a>
## 已经选好训练框架，在哪里打开？

核查日期：2026-10-21。下表是**配置字段/参数片段，不是完整训练命令**；数据、模型、输出目录和依赖仍按所用训练器配置。更换版本需重新核对开关。

| 框架与固定版本 | 实际入口 | 应设置什么 | 开跑前确认 |
| --- | --- | --- | --- |
| LeRobot `463202b` | `src/lerobot/configs/train.py` 的 `wandb`，定义在 `configs/default.py` | `wandb.enable=True`、`wandb.project`；离线时 `wandb.mode="offline"` | 保存的配置确实开启日志；观察第一次记录是否生成。离线不要求云端出现 run |
| openpi `215abfb` | `src/openpi/training/config.py` 的训练配置 | `wandb_enabled=True`；`log_interval` 控制记录间隔；`save_interval` 控制检查点间隔 | 日志与检查点是两个机制；所选 preset 是否覆盖默认值 |
| GR00T `dac54b3` | `gr00t/experiment/launch_finetune.py`；配置在 `gr00t/configs/finetune_config.py` | 启动参数 `--use-wandb`；配置字段 `wandb_project` | 训练日志开启不等于验证开启：该配置默认 `eval_strategy="no"`；需另配验证数据和评测策略 |
| 自己写的 PyTorch 循环 | 每次完成 optimizer update 后的记录位置；验证循环另记 | `SummaryWriter.add_scalar`，或 W&B `run.log`，或 MLflow `log_metric` | 统一 step 的含义；分布式记录需明确各进程聚合方式，避免重复 run |

依据：[LeRobot 日志配置](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/src/lerobot/configs/default.py)、[openpi 训练配置](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/training/config.py)、[GR00T 训练配置](https://github.com/NVIDIA/Isaac-GR00T/blob/dac54b313160c201c450f97df0fd74ebd379c892/gr00t/configs/finetune_config.py)及[新 embodiment 微调说明](https://github.com/NVIDIA/Isaac-GR00T/blob/dac54b313160c201c450f97df0fd74ebd379c892/getting_started/finetune_new_embodiment.md)。

## 一个最小的本地接入例子

已有 PyTorch 环境时安装 `tensorboard`，在训练程序中加入下列适配函数。代码只接收真实测量值，不会启动训练，也不会凭空生成验证结果。GPU loss 转 Python 标量可能触发同步，按日志间隔记录即可。

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter(log_dir="runs/baseline-001")

def record_update(update_step, train_loss, learning_rate, val_loss=None):
    writer.add_scalar("loss/train", float(train_loss), update_step)
    writer.add_scalar("optimizer/lr", float(learning_rate), update_step)
    if val_loss is not None:
        writer.add_scalar("loss/validation", float(val_loss), update_step)

# Call record_update(...) with measured values after selected optimizer updates.
# Flush periodically; close the writer when training ends.
```

在训练机器的另一个终端运行：

```bash
tensorboard --logdir runs --host 127.0.0.1 --port 6006
```

本机浏览器打开 `http://127.0.0.1:6006`。远端训练时，面板读取的是远端日志；需要端口转发或把日志复制到本机。没有调用记录函数就不会有曲线。定期调用 `writer.flush()`，退出时调用 `writer.close()`。每次实验用不同目录，避免把两次运行误画成一条曲线。

<a id="metrics"></a>
## 不只看 loss：至少记录什么？

以下名称是建议的日志标签，不保证每个训练器已自动提供。缺失项需要从相应阶段计算并记录。

| 指标/记录 | 从哪里来 | 用于什么判断 |
| --- | --- | --- |
| 训练 loss、各损失分项、学习率、梯度范数 | 训练循环；注明梯度裁剪前后 | 数值稳定性、更新是否发生；不同模型的 loss 数值不可直接横比 |
| 验证 loss、按左右臂/夹爪/动作维度分解的误差 | 固定验证集，注明归一化前后及单位 | 总平均值可能掩盖一只手或夹爪的问题；生成式策略的评测设置须一致 |
| 每秒样本、每次更新耗时、数据等待时间 | 训练和数据加载计时 | 区分 GPU 计算、解码、磁盘或网络瓶颈；CUDA 异步计时需处理同步含义 |
| GPU 峰值显存、利用率 | 训练机器的设备统计 | 判断显存与吞吐瓶颈；注明进程统计还是整卡统计 |
| 代码提交、模型/数据版本、split、seed、配置、归一化统计版本 | 实验开始时保存 | 能否解释两次实验差别、复现实验或恢复检查点 |
| 成功次数/总次数、干预次数、完成时间、失败类型 | 独立的仿真/真机闭环评测 | 离线拟合是否转化为任务能力；注明任务分布、设备和评测协议 |

| 我看到的异常 | 先检查 | 下一步动作 |
| --- | --- | --- |
| loss 出现 NaN/Inf | 输入有限性、异常动作、学习率、混合精度及梯度 | 保存出错样本索引与配置；先复现该批次，再改数据或优化设置 |
| 训练 loss 降，验证 loss 升 | 数据划分是否按 episode/场景隔离，验证分布与过拟合 | 固定验证协议；比较早期检查点，调整数据/正则等因素时一次只改可解释项 |
| loss 很低，机器人仍失败 | 动作单位/顺序、推理时归一化、观测分布、控制延迟 | 先离线比对同一样本的训练与推理输入输出，再定位闭环失败 |
| GPU 时忙时闲、吞吐差 | 数据等待、视频解码、存储、worker、同步日志开销 | 用分段计时找瓶颈后调整；增加 worker 并非总有效 |
| 第一批就显存不足 | 权重、优化器、激活、batch、图像/序列长度 | 先估算内存组成，再缩减可调整项；仅换监控平台不会解决 |
| 重启后曲线断开或 step 重复 | run ID、检查点 step、优化器与调度器恢复状态 | 统一恢复语义；记录恢复来源，不把新训练伪装成连续实验 |

<a id="practice"></a>
## 8GB 显存、暂时不训练，怎么学？

用一份已有的 TensorBoard 日志或导出的指标表，标出训练 loss、验证 loss、学习率、吞吐和数据版本。缺失的项明确写“未记录”，不要从曲线猜测成功率。再抽取一条示教，按[数据格式检查表](dataset-format-decisions.md#acceptance)检查样本；两项练习都不需要加载大型模型。

练习产出是一页排查记录：观察到什么、还缺哪个测量、下一步检查哪个组件。若使用人工构造曲线学习面板操作，必须标为模拟数据。本页代码做静态检查，未在本仓库运行实际训练或部署监控服务。
