# Robot pauses and inference choices

[Home](../README.en.md) · [中文](zh/deployment-decisions.md) · [Question index](decision-tables.md)

**When the process permits pauses, start with synchronous inference; the need for overlap depends on pause budgets, control mode and scene dynamics.** A pause here means waiting between policy action chunks. It does not mean stopping servo, balance or contact control. This page provides engineering decisions and acceptance checks, not permission to control a particular robot.

<a id="select"></a>
## Choose by condition

| My conditions | First approach | Required action | When to change approach |
| --- | --- | --- | --- |
| Static workcell; waiting between chunks is permitted; a validated waiting controller state exists | Synchronous observation → inference → selected execution steps → new observation | Keep low-level control running; measure pauses and complete process cycle time | Pauses exceed budget, objects slip while waiting, or observations are stale at execution |
| Pausing after placement is acceptable, but grasping, insertion or transport must continue | Select behavior by process stage | Define stage transitions and wait only in validated states | Stage recognition is unreliable or the allowed waiting pose cannot be reached reliably |
| Slowly changing scene, but chunk boundaries must not pause | Overlap inference and execution with a bounded action buffer | Measure remaining valid buffer, tail latency and chunk transitions; handle stale responses | Queue growth, stale actions, transition jumps or frequent depletion |
| Moving conveyor, moving objects or rapidly changing contact | Reduce perception-to-execution delay and committed execution length | Enforce observation-age limits and validate responses using fresh observations | Overlap is smooth but actions are stale; revise perception, model, compute or controller responsibilities |
| Humanoid walking, dynamic balance or continuous force control | Maintain suitable continuous low-level feedback; connect policy through the supported interface | Identify whether the output is a target, velocity or torque; validate watchdog and connection-loss behavior | Unknown interface timeout semantics must be resolved before treating pauses as acceptable |
| Remote GPU with network jitter | Local control and timeout handling with inference deadlines | Include transmission and queueing; identify requests and observation timestamps; reject stale responses | Deadlines remain unmet: revise local inference, execution strategy or process budget |

Asynchronous queues, action blending and RTC are distinct. A queue overlaps compute and execution; blending combines overlapping predictions; RTC-style methods also condition on committed actions. Enabling a queue does not implement the other two. See [real-time inference](41-real-time-inference.md) for the underlying mechanisms.

<a id="pause"></a>
## Pauses allowed: do these five things first

1. **Define the permission precisely.** Record stages where waiting is allowed, maximum single wait, acceptable cycle time, and whether objects can move, fall or remain under load. Measure unknown quantities.
2. **Identify the waiting interface.** Position holding, controlled stopping and compliant waiting depend on the controller. Repeating the last velocity or torque can continue motion; disconnecting control is not equivalent to stopping safely. Use supported, validated behavior; see [runtime protection](43-safety.md).
3. **Establish a synchronous loop.** Capture a timestamped observation, predict H actions, execute s selected steps (s ≤ H), then acquire another observation and infer again according to your timing definition. Low-level feedback remains independent and active.
4. **Log the full path.** Record observation acquisition, request dispatch, response arrival, first/last command delivery and the first command of the next chunk. Also record actual execution times when device feedback permits; dispatch is not physical execution.
5. **Inject slow responses and disconnections.** Start with replay or simulated interfaces to test waiting, timeouts and fresh observations after recovery, then verify through controlled device tests. Acceptance includes task success, pause budgets, action freshness and recovery without jumps.

Another implementation using overlap is not sufficient reason to add queues and concurrency. Change the synchronous baseline when measurements show which condition it fails.

<a id="budget"></a>
## Use measurements to explain stuttering

These are engineering quantities, **not universal framework parameter names**. Implement them in the relevant executor, request client and controller configuration.

| Quantity | Meaning and location | What it checks |
| --- | --- | --- |
| f, T=1/f | Policy command delivery rate and interval in the executor, not the servo inner-loop rate | Time covered by an action sequence |
| H, s | Prediction horizon and executed steps in model configuration and execution loop | A large H does not imply executing everything; larger s extends open-loop execution |
| L | Observation acquisition to usable actions, including preprocessing, queueing, network and postprocessing | Mean, p95/p99, observed maximum and tail-latency sources |
| B | Remaining valid buffered action time when a new request starts | Whether overlap lasts until the response; do not substitute the original full chunk length |
| A_max | Process-specific maximum observation age, checked at acceptance/execution | Whether a result has expired when received or used |
| P_max | Maximum extra waiting time for the current stage, used by the waiting state/watchdog | Whether a synchronous pause or buffer depletion is acceptable |

**Calculation only, not recommended settings:** f=50Hz gives T=20ms; H=10 but s=5 steps are executed; observation-to-first-available-action L=76ms. With immediate delivery, the five commands occur at 76, 96, 116, 136 and 156ms. The fifth therefore uses a 156ms-old observation. If the executor waits one time slot, captures again at 176ms and infers synchronously, the next chunk starts at 252ms. The boundary command gap is 96ms: 76ms beyond the ordinary 20ms interval.

A different overlapping design with B=100ms remaining at request time and L=76ms has only 24ms margin. A 130ms latency exceeds that buffer by 30ms. `L + unaccounted jitter/delivery margin < B` is a necessary budget check against depletion, **not a guarantee of freshness, continuous chunk transitions or robot stability**. Percentiles are not hard real-time guarantees; exceeding the budget still requires defined handling.

<a id="acceptance"></a>
## What should I inspect next?

| Symptom | Inspect first | Action and acceptance |
| --- | --- | --- |
| Fast average inference with occasional pauses | p99/maximum latency, network retransmission, first-call compilation, depletion timestamps | Separate warmup and steady state; address the slow stage or waiting behavior; deliberately slow responses must enter the expected state |
| Buffer never empties, but reactions become slower | Queue length, observation times, response order | Bound buffered duration and reject stale responses; age must not accumulate. Replacing committed actions requires continuity checks |
| Every new chunk causes a jump | Target difference at transition, frames/normalization, overlap meaning | Fix semantics before assessing transition methods; smoothing alone can add delay or change contact behavior |
| Waiting is permitted, but the object slips or insertion force keeps growing | Grasp/contact state and waiting control mode | This stage has not met the pause conditions; redefine stage/controller behavior and retest |
| Old actions execute after reconnection | Request IDs, acquisition times, recovery queue rules | Expired responses must not enter the queue; obtain fresh observations and follow the supported recovery procedure |

Record process and control mode, timestamp definitions, latency distribution, maximum measured pause, maximum measured observation age, timeout counts/responses and successes/attempts. Model inference FPS alone is insufficient.

## Implementation references and scope

Checked 2026-10-21: the budgets and decision tables are engineering analysis, without acceptance testing on a particular humanoid. The openpi [ALOHA simulation client guide](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/examples/aloha_sim/README.md) illustrates policy-service/client responsibilities. The pinned LeRobot [inference guide](https://github.com/huggingface/lerobot/blob/463202b1b005e8802343a282661eb26ef27a160c/docs/source/inference.mdx) documents that implementation's interfaces. Neither replaces the target robot's controller contract.
