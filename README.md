# VLA 学习与部署

**从一条机器人示教，到可评测的闭环策略。**

中文 · [English](README.en.md)

VLA（Vision-Language-Action，视觉语言动作模型）根据图像、任务指令及可选机器人状态预测动作。本仓库提供基础概念、数据与微调流程、部署教程、检查表和 168 条资源。

## 按具体问题查表

| 我现在的问题 | 直接查阅 | 文档提供什么 |
| --- | --- | --- |
| 真机允许卡顿，该用同步还是异步？ | [停顿与推理方式](docs/zh/deployment-decisions.md) | 条件选择、等待行为、延迟预算和验收步骤 |
| 用什么平台监控训练，loss 异常怎么办？ | [训练监控](docs/zh/training-monitoring.md) | TensorBoard / W&B / MLflow、框架开关、指标与排查 |
| 数据要什么格式，已有数据如何转换？ | [数据格式](docs/zh/dataset-format-decisions.md) | 版本兼容、字段语义、双臂样本和加载验收 |

[查看完整问题索引](docs/zh/decision-tables.md)。先匹配自己的条件，再查方案、配置位置与通过条件；来源用于核对实现版本。

## 开始学习

| 阶段 | 阅读内容 | 动手产出 |
| --- | --- | --- |
| 1. 理解输入输出 | [基础概念与第一条数据流](docs/zh/00-start-here.md) | 画出观测到执行的路径，读懂一个样本的形状与单位 |
| 2. 准备数据与微调 | [数据、动作约定与训练](docs/zh/01-data-and-training.md) | 一份数据检查记录和可复现的训练配置 |
| 3. 连接推理与控制 | [实时推理](docs/zh/41-real-time-inference.md) | 延迟记录、动作队列时序图与超时行为 |
| 4. 测量优化效果 | [优化与评测](docs/zh/40-optimization-matrix.md) | 同一协议下的基线与改进结果 |
| 5. 检查运行条件 | [运行防护](docs/zh/43-safety.md) | 限位、超时与接管的验证记录 |

## 查阅与实践

- [第一步：采什么数据、如何读懂一条示教](docs/zh/02-data-sources.md)：五类采集路线与无需训练的阅读练习。

- [资源目录](docs/zh/resources.md)：数据、模型、微调、部署、评测与延伸课程。
- [排错手册](docs/zh/troubleshooting.md)：12 类常见现象的检查与处理步骤。
- [采集前检查表](checklists/zh/before-collecting-data.md)。
- [部署前检查表](checklists/zh/before-deploying.md)。
- [采集日志模板](templates/collection-log.csv) · [部署配置模板](templates/deployment-manifest.yaml)。

基础要求：能读写 Python，理解张量形状、训练与验证的区别，了解关节位置、速度和坐标系。第一步可以从已有数据和离线推理开始。

## 参与维护

提交内容和双语更新方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。许可证：[MIT](LICENSE)。
