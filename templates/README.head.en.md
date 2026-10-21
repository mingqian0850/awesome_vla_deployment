# VLA Learning and Deployment

**From a robot demonstration to an evaluated closed-loop policy.**

[中文](README.md) · English

A vision-language-action (VLA) model predicts actions from images, task instructions and optional robot state. This repository provides foundational concepts, data and fine-tuning workflows, deployment guides, checklists and {{TOTAL}} resources.

## Look up a concrete problem

| My question | Go directly to | What the page provides |
| --- | --- | --- |
| My robot can pause: synchronous or asynchronous inference? | [Pauses and inference](docs/deployment-decisions.md) | Conditions, waiting behavior, latency budgets and acceptance checks |
| Which training monitor should I use, and how do I diagnose loss? | [Training monitoring](docs/training-monitoring.md) | TensorBoard / W&B / MLflow, framework switches, metrics and diagnosis |
| Which dataset format do I need, and how do I convert my data? | [Dataset formats](docs/dataset-format-decisions.md) | Version compatibility, field semantics, a bimanual example and reader checks |

[Full question index](docs/decision-tables.md). Match your conditions, then find the action, configuration location and acceptance criteria; sources identify the implementation version.

## Start learning

| Stage | Read | Practice output |
| --- | --- | --- |
| 1. Understand inputs and outputs | [Foundations and the first data flow](docs/00-start-here.md) | An observation-to-execution diagram and a sample with known shapes and units |
| 2. Prepare data and fine-tune | [Data, action conventions and training](docs/01-data-and-training.md) | A data inspection record and reproducible training configuration |
| 3. Connect inference and control | [Real-time inference](docs/41-real-time-inference.md) | Latency logs, action-queue timing and timeout behavior |
| 4. Measure optimization | [Optimization and evaluation](docs/40-optimization-matrix.md) | Baseline and modified results under the same protocol |
| 5. Check operating conditions | [Runtime protection](docs/43-safety.md) | Validated limits, timeout responses and handover behavior |

## Reference and practice

- [Step one: capture routes and reading a demonstration](docs/02-data-sources.md): five data routes and an exercise without training.

- [Resource catalog](docs/resources.md): data, models, fine-tuning, deployment, evaluation and further courses.
- [Troubleshooting](docs/troubleshooting.md): checks and actions for 12 common symptoms.
- [Before collecting data](checklists/before-collecting-data.md).
- [Before deployment](checklists/before-deploying.md).
- [Collection log template](templates/collection-log.csv) · [Deployment manifest](templates/deployment-manifest.yaml).

Prerequisites: reading and writing Python, understanding tensor shapes and training versus validation, and basic joint position, velocity and coordinate frames. Start with existing data and offline inference.
