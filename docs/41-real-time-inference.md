# Real-time inference: the latency budget

> Most "the policy stutters on the real robot" problems are arithmetic, not modelling.

A VLA policy is not fast. pi0.5-scale models take on the order of tens to a few hundreds of
milliseconds per action chunk on a workstation GPU, and considerably more on embedded
hardware. A control loop wants a new command every few milliseconds. **Action chunking exists
to bridge that gap**, and understanding the arithmetic tells you which of the three execution
strategies you need before you write any code.

## 1. Three latencies, not one

Three different quantities get called "the latency", and conflating them is why two teams can
measure the same system and disagree. Name the one you mean.

| Metric | Definition | When it is the binding constraint |
|---|---|---|
| **Time to first action (TTFA)** | new observation arrives → the first *modifiable* action is dispatched | Dynamic tasks — ping-pong, conveyor sorting, anything where the opportunity window closes |
| **End-to-end latency** | sensor sampling → preprocessing → inference → postprocessing → dispatch | Control-loop feasibility and motion quality |
| **Chunk-boundary stall** | one chunk finishes while the next is not computed yet, so the robot waits | Every chunked policy, unless inference is decoupled from execution |

The third is what people report as "the robot moves in bursts and pauses". The first is what
actually limits you on fast tasks, and it stays invisible if you only measure the third. A
system can have zero chunk-boundary stall and still be too slow to react — see §5.

## 2. The notation

| Symbol | Meaning | Typical value |
|---|---|---|
| `f_c` | control frequency | 50 Hz |
| `T_c = 1/f_c` | control period | 20 ms |
| `H` | prediction horizon: action chunk length, in steps | 50 |
| `s` | execution horizon: steps actually executed per inference | ~H/2 |
| `L` | inference latency, observation captured → chunk returned | 76 ms |
| `d` | inference latency expressed in control steps, `L / T_c` | ~4 |
| `D_c = H / f_c` | wall-clock duration of one chunk | 1.0 s |

`L` is measured end to end, and the honest definition includes everything: camera exposure,
image transfer, preprocessing, tokenisation, denoising steps, and the trip back to the
actuator. Teams routinely quote the denoising loop alone and then wonder why the robot is
sluggish.

## 3. What `L` actually is, on real hardware

Before you measure your own, calibrate your expectations. These are reported figures, not a
controlled comparison — different harnesses, camera counts and denoising steps make most
cross-source VLA latency numbers non-comparable, and FlashRT's own benchmark table says so
explicitly. Treat the *order of magnitude* as the signal.

| Setup | Reported latency | Source |
|---|---|---|
| π0.5, upstream openpi, Jetson Thor | 714 ms | [FlashRT benchmark table](https://github.com/flashrt-project/FlashRT/blob/main/docs/benchmark_comparison.md) |
| π0.5, upstream openpi, RTX 5090 | 244 ms | same |
| π0.5, Jetson AI Lab BF16 → TensorRT FP8, Thor | 163 ms → **95 ms** | same |
| π0.5, FlashRT engine | **51.51 ms** (13.9×) | same |
| π0.5, AGX Thor | 44 ms (23 Hz) | [NVIDIA dev forum](https://forums.developer.nvidia.com/t/real-time-inference-on-thor-rtx-pi0-5-gr00t-n1-6-1-7-thor-23-hz-rtx-5090-50-80hz/368788) |
| π0.5, RTX 5090 | 17.58 ms (57 Hz) | same |
| GR00T N1.6, TensorRT, Orin → 4090 → H100 | 173 → 43 → 36 ms | [GR00T optimisation docs](https://nvidia-isaac-gr00t.mintlify.app/deployment/optimization) |

Three things follow, and they are worth more than the individual numbers:

1. **The same model spans 714 ms to 51 ms.** The dominant variable is the inference stack, not
   the model and not the task. If your latency looks like the top row, the answer is the
   runtime, not a smaller checkpoint.
2. **23 Hz on Thor means a 50 Hz control loop cannot be fed synchronously.** Chunking or
   asynchronous execution is not an optimisation at that point; it is the only way the
   architecture works.
3. **On Jetson Orin, no stack in the vendor table gets below 173 ms.** The hardware is the
   binding constraint before your code is. Decide that before you spend a month profiling.

## 4. The feasibility condition

> **You can re-plan before the buffer empties iff `L < D_c`.**

With `L = 100 ms` and `D_c = 1.0 s` you have a 10× margin and a straightforward synchronous
loop works. With `L = 100 ms` and `H = 10` at 50 Hz (`D_c = 200 ms`), you have a 2× margin and
any jitter eats it. With `L > D_c` the buffer starves every cycle and no amount of tuning the
policy will help.

The margin is also your robustness budget. Wi-Fi jitter, a thermal-throttled GPU, or one slow
frame can consume it. **Aim for `L < D_c / 3` unless you have a specific reason not to.**

## 5. The observation-age equation — the part people miss

Chunk k is computed from an observation taken at time `t_0`, but action `k` is executed at
`t_0 + L + k·T_c`. So:

> **age(k) = L + k · T_c**

The **last** action of the chunk is executed on information that is `L + (H−1)·T_c` old.

With `L = 100 ms`, `H = 50`, `T_c = 20 ms`:

```
age(0)  = 100 ms          the first action is already 100 ms stale
age(49) = 100 + 980 = 1080 ms   the last action acts on information over a second old
```

This is why executing an entire chunk open-loop works well on slow, quasi-static tasks and
fails on anything dynamic or contact-rich. It is also why "just increase H" is not a free
fix: it improves the feasibility margin from §2 while making the staleness worse. The two
pressures pull in opposite directions, and the correct `H` is where they balance — which
depends on how fast your task evolves, not on a default from a config file.

## 6. Three execution strategies

### Synchronous (execute the whole chunk, then re-plan)

- **Requires** `L < D_c` with margin.
- **Good for**: slow manipulation, fixed-base arms, tasks where the world does not move.
- **Fails as**: visible stop-start motion when `L ≈ D_c`, and a discontinuity at each chunk
  boundary, because chunk *n+1* was computed without knowing what chunk *n* actually executed.

Measured, in the RTC paper's own setting: pi0.5 at 50 Hz control with 5 denoising steps takes
**76 ms per inference** while the controller consumes an action every 20 ms. One inference
therefore occupies about four control steps (`d ≈ 4`, and closer to 6 once you add 10–20 ms of
LAN communication). The action queue can only drain smoothly because a single inference
produced an entire chunk — so the moment a chunk runs out before the next one lands, you get a
visible stall at every boundary.

### Temporal ensembling (blend overlapping chunks)

- Compute a new chunk every control step (or every few), and average the predictions that
  cover the current timestep, weighting older predictions less.
- **Good for**: smoothing chunk-boundary discontinuities; cheap to implement on top of a
  synchronous loop.
- **Costs**: `H×` the inference compute if you re-plan every step. It also averages across
  predictions made from different observations, which blurs fast motion.
- **This one can fail badly under latency.** In the RTC paper's latency-robustness test,
  injecting +100 ms of extra delay (`d ≈ 11`) made temporal ensembling trip a protective stop,
  while synchronous inference degraded gracefully and RTC was almost unaffected. Averaging two
  paths that have diverged produces a trajectory that goes *between* them — which, in the
  walk-through-the-middle test, means straight into the obstacle.
- **Note**: averaging is exactly the operation a multimodal policy dislikes. If your policy is
  already averaging modes, ensembling makes it worse.

### Asynchronous / RTC

- Keep inference running continuously in a separate process or thread, and let the control loop
  consume whatever is ready. RTC goes further and conditions the new chunk on the actions
  already committed to, so the new plan joins smoothly instead of jumping — conceptually
  in-painting: the already-executed prefix is fixed, the in-flight window is partly constrained,
  the future is free.
- **Good for**: eliminating chunk-boundary stalls, which is the failure mode most people
  actually have.
- **Costs**: **inference is about 28% slower** (97 ms versus 76 ms in the RTC paper) because
  guidance needs an extra backward pass. Comparable rejection-sampling approaches are far worse
  — one published comparison measured 223 ms per round, about 2.3× RTC, needing an extra weak
  policy checkpoint and still performing worse at high latency.
- **Implementation detail that is easy to get wrong**: the inference thread should estimate the
  *next* delay conservatively, taking the maximum of the last few measurements. If you
  underestimate `d`, the frozen region expires before the new chunk arrives and the whole
  three-region partition is invalid. Overestimating costs you a little responsiveness;
  underestimating costs you correctness.

### The half RTC does not solve

This is the part that is easy to miss when you read the RTC headline: **it addresses chunk
smoothness, not reaction time.** The `d` frozen steps are locked. If the object moves or the
grasp fails during that window, those actions cannot change. On a fast task the bottleneck is
not smoothness, it is **TTFA** — how long until you can emit an action that reflects what you
just saw.

Roughly, for an asynchronous policy with execution horizon `s`:

```
reaction time ≈ L + (s / 2) · T_c
```

where the `s/2` is the expected position of the event within the execution window. With
`L = 76 ms`, `s = 10`, `T_c = 20 ms` that is roughly 176 ms. On a task where the opportunity
window is a few hundred milliseconds, most of your budget is gone before you can respond at
all — and no amount of chunk-smoothing helps, because the limit is the denoising loop itself.

The published attacks on that number are algorithmic, not systems-level: reschedule the
denoising steps so the action expert stops dominating latency
([FASTER](https://arxiv.org/abs/2603.19199)), or learn the continuation so a chunk can be
extended without a full re-inference ([Legato](https://arxiv.org/abs/2602.12978)). Worth
reading before you assume a faster GPU is the answer — but **measure your own TTFA first**,
because if you have never measured it you do not know whether you have this problem.

## 7. Measure it properly

Instrument five timestamps on every cycle and log them as a series:

| # | Timestamp | Why |
|---|---|---|
| 1 | camera frame captured | exposure time is latency; a 30 ms exposure is 30 ms |
| 2 | observation assembled in the policy process | reveals transfer/copy cost |
| 3 | inference started | queueing delay between 2 and 3 is invisible otherwise |
| 4 | chunk returned | `L` |
| 5 | command reaches the actuator | the middleware/transport cost |

**Report p50, p95 and p99 — never the mean.** Real-time failures live in the tail. A 100 ms
mean with a 400 ms p99 will stutter regularly, and the mean will look fine.

Then compute, for every cycle: the feasibility margin `D_c − L`, and the age of the oldest
executed action. If either crosses a threshold, the problem is the timing architecture, not
the model.

## 8. Pitfalls that show up as "the model is bad"

- **Queueing observations.** If the policy lags and you enqueue frames, you build a backlog and
  the robot acts on ever-older data, then behaves as if it is lagging the world by seconds.
  **Always drop stale observations; never queue them.**
- **Inferring over the network without measuring jitter.** Wi-Fi inference works beautifully in
  a demo and fails during a demo. If you must, measure p99 and consider a local fallback policy.
- **Camera exposure and auto-exposure.** Auto-exposure can vary frame timing by tens of
  milliseconds. Lock exposure for a fixed control rate.
- **Image resize on the CPU.** A per-frame CPU resize and colour conversion can cost more than
  the denoising loop on a small model.
- **Middleware buffering.** Default ROS2 QoS settings can buffer or silently drop messages. Set
  the queue depth deliberately and check what your subscriber actually receives.
- **Python GIL and the control loop.** A control loop and an inference client in one Python
  process will contend. Separate processes are not premature optimisation here.
- **Fixing timing by retraining.** If the staleness arithmetic says you are executing
  second-old plans, no amount of data fixes it. Fix the architecture first, then evaluate the
  model on its own merits.

## 9. Quick reference

```
Feasibility:        L  <  D_c / 3          (D_c = H / f_c)
Oldest action age:  L + (H - 1) * T_c
Chunk duration:     D_c = H / f_c
```

Worked example — `L = 80 ms`, `f_c = 50 Hz`, `H = 50`:

```
D_c            = 50 / 50          = 1.000 s
margin         = 1.000 / 0.080    = 12.5x        -> synchronous is fine
oldest age     = 0.080 + 49*0.020 = 1.060 s      -> only OK if the task is quasi-static
```

The same model on hardware with `L = 400 ms` and `H = 50`:

```
margin         = 1.000 / 0.400    = 2.5x         -> jitter will eat this
```

At `H = 10` it becomes `0.200 / 0.400 = 0.5×` — the buffer starves every cycle. At that point
the choice is: raise `H`, cut `L` (quantisation, distillation, smaller visual encoder), or go
asynchronous. Anything else is guessing.

---

## Sources

- Three-latency decomposition, the RTC derivation and worked numbers, the 28% guidance cost,
  the 223 ms rejection-sampling comparison, and the latency-robustness results:
  [Xbotics 具身智能教程 第13讲](https://github.com/Xbotics-Embodied-AI-club/Xbotics-Embodied-AI-Handbook/blob/main/docs/part3-end-to-end/13-VLA%E5%89%8D%E6%B2%BF.md)
  (Chinese), which works through [RTC](https://neurips.cc/virtual/2025/loc/san-diego/poster/117747).
- Real-hardware latency figures and the GR00T optimisation table: see
  [Deployment benchmarks](../README.md#deployment-benchmarks--measured-not-cited).
- The batch-1 quantisation negative result and the latency-versus-staleness trade:
  [embodied-efficiency](https://github.com/LaelaZorana/embodied-efficiency).
