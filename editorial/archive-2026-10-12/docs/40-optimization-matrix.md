# The optimisation matrix: what to measure, and how

> Every curated list in this space has an "efficiency" section that is a table of paper
> citations. None reports whether an export path actually exists for a given model, or what
> quantisation did to task success rate. The consequence is that choosing an inference
> optimisation is folklore.
>
> This page is the protocol. `data/benchmarks.yaml` holds the results, including the entries
> marked as gaps — measurements nobody has published.

## Why success rate, not latency

Latency is easy to measure and almost meaningless on its own. A policy at 8 ms per chunk that
fails the task is not better than one at 80 ms that succeeds. Every row in the matrix should
carry, at minimum:

- **latency** (p50/p95/p99) and
- **success rate** (with trial count) and
- **what the task was.**

A speedup with no success rate is not a result.

## The measurement protocol

### 1. Fix the measurement boundary, and state it

"Latency" means different things to different people, and this is the main reason public
numbers disagree. Pick one and say which:

| boundary | includes | typical value |
|---|---|---|
| Model only | denoising loop | the smallest, most quoted, least useful number |
| Chunk | preprocessing + tokenisation + denoising + decode | what you should report by default |
| End to end | + camera capture + transfer + command delivery | what the control loop actually experiences |

Report the **chunk** boundary as the headline and the **end-to-end** boundary alongside it.
If you can only measure one, measure end-to-end — it is the number that decides whether your
control rate is achievable.

### 2. Report the tail, not the mean

`p50 / p95 / p99`, always. Real-time failures live in the tail; a 100 ms mean with a 400 ms
p99 produces a robot that stutters regularly while the dashboard looks healthy.

State the sample count. A p99 from 30 samples is noise.

### 3. State the confounders

These change latency by more than most optimisations do:

- action horizon and denoising step count
- dtype (fp32 / bf16 / fp16 / int8)
- batch size (1 at inference, but check)
- whether images are resident on the GPU or copied per step
- input resolution and the number of camera streams
- `torch.compile` / CUDA graphs / warm-up state — **discard the first N iterations**
- power and thermal state of the device (a laptop GPU throttles; a Jetson in a sealed
  enclosure throttles harder)

### 4. For quantisation, run the A/B properly

Quantisation results are only comparable within one setup:

1. Same checkpoint, same task, same initial-state set.
2. **Interleave** the conditions (A,B,A,B…) rather than running them in blocks — otherwise you
   are measuring thermal drift.
3. Report success rate **with trial count**, and the latency gained.
4. Report failures by mode, not just count. "Success dropped 8 points, and every new failure
   was a missed grasp" is a finding; "success dropped 8 points" is not.
5. Check the **action head** specifically. Flow-matching and diffusion policies output
   continuous, often small-magnitude values; quantisation noise that is invisible in a
   language model's logits can dominate a delta action. This is a hypothesis worth testing
   explicitly, and it is the kind of negative result this repo most wants.

### 5. For export, report the blocker

An ONNX/TensorRT/OpenVINO attempt has three outcomes, and the third is the valuable one:

- **Works** — report latency, and whether the exported graph is numerically equivalent to the
  reference (compare action chunks on a fixed batch of observations; a cosine similarity and a
  max absolute deviation are enough).
- **Works but differs** — report how much, and whether the difference matters for the task.
- **Fails** — report the exact operator, dynamic-shape construct or control-flow pattern that
  blocked it. `torch.export` and TensorRT error messages are searchable; someone else hitting
  the same wall will find your issue.

## Submitting a row

Open a PR adding an entry to `data/benchmarks.yaml`. Copy this template:

```yaml
- id: latency-pi05-rtx4090
  name: "pi0.5 latency on RTX 4090 (batch 1)"
  url: "<link to your write-up, script or issue>"
  type: benchmark
  what: >
    Chunk-boundary latency p50 78 ms / p95 96 ms / p99 140 ms over 500 samples.
    pi0.5 base, action horizon 50, 10 denoising steps, bf16, two 720p cameras resident
    on GPU, torch.compile after 20 warm-up iterations.
  why: >
    First public number for this model on consumer hardware; implies a feasibility margin of
    ~12x at 50 Hz with H=50, so synchronous execution is safe on this setup.
  maturity: research
  verified: 2026-09
  tags: [latency, pi05, rtx4090, benchmark]
```

Two rules, and they are the whole point of this repo:

- **Do not report a number you did not measure.** If you are quoting someone, set the source
  URL to their measurement and say so in `notes`.
- **Report the confounders.** An unattributed number is worse than no number, because someone
  will plan around it.
