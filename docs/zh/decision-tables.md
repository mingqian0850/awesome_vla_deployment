# 按具体问题查表

[首页](../../README.md) · [English](../decision-tables.md)

先找与你相同的条件，再读取对应方案、配置位置和验收方法。没有测量结果的条件填“未知”，不要直接归入“满足”。本版覆盖部署停顿、训练监控、数据格式三组问题；不是所有机器人通用的配置文件。

## 我现在遇到什么问题？

| 我的问题或条件 | 直接查哪里 | 看完应能完成什么 |
| --- | --- | --- |
| 真机允许动作之间停顿，是否还要异步推理？ | [允许停顿](deployment-decisions.md#pause) | 判断同步方案是否足够，明确等待时控制器的行为 |
| 只允许在部分工序停顿 | [按工序选择](deployment-decisions.md#select) | 区分可等待阶段与必须连续执行的阶段 |
| 动作块之间卡一下，但平均推理速度不慢 | [连续执行与预算](deployment-decisions.md#budget) | 测量缓冲耗尽、尾延迟和观测年龄 |
| 用远端 GPU 推理，网络偶尔慢 | [部署选择表](deployment-decisions.md#select) | 把网络计入延迟并验证超时行为 |
| TensorBoard、W&B、MLflow 应该选哪个？ | [监控平台选择](training-monitoring.md#platform) | 按本地学习、已有集成、团队服务选择 |
| 已有 LeRobot、openpi 或 GR00T 训练代码，在哪开监控？ | [框架配置](training-monitoring.md#integration) | 找到已核查版本的开关和日志间隔 |
| loss 下降了，怎么知道训练是否有用？ | [指标及异常处理](training-monitoring.md#metrics) | 同时检查验证数据、动作误差和闭环评测 |
| 数据该做成 LeRobot、RLDS 还是 HDF5？ | [目标训练器决定格式](dataset-format-decisions.md#target) | 先锁定读取器版本，再确定转换目标 |
| 我已有 LeRobot v3，能直接用于 GR00T 吗？ | [版本兼容表](dataset-format-decisions.md#target) | 识别 v2 转换和模态元数据要求 |
| 我只有 ego 视频，能直接训练机器人动作吗？ | [现有数据如何处理](dataset-format-decisions.md#convert) | 区分视频语义数据与机器人动作监督 |
| 数据能读进来，但担心左右手、单位或时间错了 | [样本契约与验收](dataset-format-decisions.md#contract) | 检查字段语义、时间对齐及动作切片 |
| 只有 8GB 显存，暂时不训练 | [不训练的练习](training-monitoring.md#practice) | 用现有日志和小样本完成一次排查 |

## 一条可执行答案应该包含什么？

| 字段 | 示例 |
| --- | --- |
| 条件 | 静态工位、底层控制独立运行、工序允许等待下一块动作 |
| 建议 | 先建立同步推理基线 |
| 具体动作 | 设置执行步数、定义等待状态、测量端到端推理延迟 |
| 通过条件 | 实测停顿和观测年龄满足工序预算；超时进入已验证的控制状态 |
| 不适用条件 | 平衡控制依赖该输出；场景变化快；工序不能等待 |
| 证据 | 官方实现的固定版本，或明确标为工程推导的计算 |

表中的工程建议需由自己的数据与设备验证。实现支持情况附版本与来源；数值示例只用于演算。排查仍不能解决时，记录机器人控制模式、训练器版本、数据版本、配置与测量值，再查[排错手册](troubleshooting.md)。
