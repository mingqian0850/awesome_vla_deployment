# Training monitoring: choose, connect and diagnose

[Home](../README.en.md) · [中文](zh/training-monitoring.md) · [Question index](decision-tables.md)

**Start with TensorBoard for local learning; use an existing W&B integration when your trainer provides one; evaluate MLflow when a team needs a shared, self-managed experiment service.** These are conditional recommendations. Tracking records and displays measurements; it cannot guarantee that a model fits in memory or automatically supply robot task success rates.

<a id="platform"></a>
## Which platform fits my situation?

| My situation | Choice | Minimum integration | What it provides / what remains |
| --- | --- | --- | --- |
| One computer, training and validation curves first | TensorBoard | Write events with `SummaryWriter`; launch a local dashboard | Recorded scalars, images and other events; manage configurations, data versions and run naming separately |
| My trainer already integrates W&B; I want run comparisons | Weights & Biases (W&B) | Enable the trainer integration and set a project; online service needs account/connection setup | Configurations, curves and recorded artifacts; an evaluator must still supply closed-loop metrics |
| Training machine is offline; records may be synced later | A W&B integration supporting offline mode, or local TensorBoard | For example, set LeRobot `wandb.mode="offline"` and retain its log directory | Offline W&B stores locally rather than appearing live in the cloud; use a local dashboard for immediate viewing |
| A team wants shared experiments, parameters and artifacts with managed service storage | MLflow Tracking | Configure a tracking URI and call logging APIs in the training code | Shared run records and artifacts; maintain service, storage and access, and integrate custom VLA metrics |
| I only need GPU activity and memory usage | System monitoring as a supplement | Inspect utilization, memory and processes on the training host | Does not replace loss, data provenance or task evaluation; utilization is not learning quality |

See the official [PyTorch TensorBoard API](https://docs.pytorch.org/docs/2.14/tensorboard.html), [W&B SDK](https://github.com/wandb/wandb/blob/dda9f931d389c9419171b01eb64ec7233f7d249a/README.md) and [MLflow Tracking concepts](https://mlflow.org/docs/latest/ml/tracking/). Also decide which environment should store any recorded videos, configurations and data samples.

<a id="integration"></a>
## Where do I enable an existing trainer integration?

Checked 2026-10-21. These are **configuration fields or argument fragments, not complete training commands**. Configure data, model, output paths and dependencies for your trainer. Recheck switches after changing versions.

| Framework and pinned revision | Actual location | Settings | Confirm before running |
| --- | --- | --- | --- |
| LeRobot `463202b` | `wandb` in `src/lerobot/configs/train.py`, defined in `configs/default.py` | `wandb.enable=True`, `wandb.project`; use `wandb.mode="offline"` when appropriate | Saved configuration enables logging and a first record appears; offline runs need not appear in the cloud |
| openpi `215abfb` | Training configuration in `src/openpi/training/config.py` | `wandb_enabled=True`; `log_interval` for logging; `save_interval` for checkpoints | Logging and checkpoints are separate; check whether the selected preset overrides defaults |
| GR00T `dac54b3` | `gr00t/experiment/launch_finetune.py`; configuration in `gr00t/configs/finetune_config.py` | Launch argument `--use-wandb`; config field `wandb_project` | Logging does not enable validation: this config defaults to `eval_strategy="no"`; configure validation data and evaluation separately |
| Your own PyTorch loop | Logging after optimizer updates, with separate validation logging | `SummaryWriter.add_scalar`, W&B `run.log`, or MLflow `log_metric` | Define step consistently; distributed logging needs explicit aggregation and duplicate-run handling |

Evidence: [LeRobot logging configuration](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/src/lerobot/configs/default.py), [openpi training configuration](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/training/config.py), [GR00T configuration](https://github.com/NVIDIA/Isaac-GR00T/blob/dac54b313160c201c450f97df0fd74ebd379c892/gr00t/configs/finetune_config.py) and [new-embodiment fine-tuning guide](https://github.com/NVIDIA/Isaac-GR00T/blob/dac54b313160c201c450f97df0fd74ebd379c892/getting_started/finetune_new_embodiment.md).

## Minimal local integration

Install `tensorboard` in an existing PyTorch environment and add this adapter to your training program. It accepts measured values; it neither launches training nor invents validation results. Converting a GPU loss into a Python scalar can synchronize execution, so log at selected intervals.

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

In another terminal on the training host:

```bash
tensorboard --logdir runs --host 127.0.0.1 --port 6006
```

Open `http://127.0.0.1:6006` locally. For remote training, the dashboard reads remote logs; forward its port or copy logs locally. No curves appear until the logging function is called. Call `writer.flush()` periodically and `writer.close()` at shutdown. Use separate directories for separate experiments to avoid merging their curves.

<a id="metrics"></a>
## What should I record beyond loss?

Names below are proposed logging labels, not promises that a trainer already emits them. Compute missing metrics in the relevant stage and log them explicitly.

| Metric or record | Source | What it tells you |
| --- | --- | --- |
| Training loss/components, learning rate, gradient norm | Training loop; identify pre/post-clipping norm | Numerical stability and whether updates occur; loss magnitudes across different models are not directly comparable |
| Validation loss and errors by arm/gripper/action dimension | Fixed validation set; identify normalization and units | Aggregate errors can hide an arm or gripper failure; evaluation settings must match for generative policies |
| Samples/second, update time, data waiting time | Training/data-loader timing | Compute versus decoding, disk or network bottlenecks; account for asynchronous CUDA timing |
| Peak GPU memory and utilization | Device statistics on the training host | Memory/throughput limits; distinguish process statistics from whole-device statistics |
| Commit, model/data revision, split, seed, configuration and normalization-statistics revision | Saved at experiment startup | Explaining run differences, reproducing experiments and restoring checkpoints |
| Successes/attempts, interventions, completion time and failure categories | Separate simulation/robot closed-loop evaluation | Whether fitting translates into task ability; record task distribution, equipment and protocol |

| Symptom | Inspect first | Next action |
| --- | --- | --- |
| NaN/Inf loss | Finite inputs, anomalous actions, learning rate, mixed precision and gradients | Preserve failing sample indices/configuration; reproduce the batch before changing data or optimization |
| Training loss falls while validation loss rises | Episode/scene separation, validation distribution and overfitting | Fix the validation protocol; compare earlier checkpoints and change interpretable factors individually |
| Low loss but robot failures | Action units/order, inference normalization, observation distribution and control delay | Compare training/inference inputs and outputs on the same sample, then locate closed-loop failures |
| Intermittent GPU activity and poor throughput | Data waiting, decoding, storage, workers and synchronous logging overhead | Time each stage before adjusting it; more workers are not always beneficial |
| First batch runs out of memory | Weights, optimizer, activations, batch and image/sequence sizes | Estimate memory components before reducing adjustable settings; changing trackers cannot solve this |
| Restart produces discontinuous curves or duplicate steps | Run ID, checkpoint step, optimizer and scheduler restoration | Align resume semantics and record the source checkpoint; do not portray a fresh run as continuous training |

<a id="practice"></a>
## Practice with 8GB VRAM and no training

Take existing TensorBoard logs or an exported metric table. Identify training loss, validation loss, learning rate, throughput and data revision. Mark missing fields as unrecorded rather than inferring success rates from curves. Inspect one demonstration using the [dataset acceptance table](dataset-format-decisions.md#acceptance). Neither exercise requires loading a large model.

Produce a one-page diagnostic record: observation, missing measurement and component to inspect next. Label artificial dashboard exercises as simulated data. Code here has static checks only; this repository has not run actual training or deployed a monitoring service for this page.
