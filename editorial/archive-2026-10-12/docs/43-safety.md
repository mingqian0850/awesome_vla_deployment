# The safety layer

> **Why this page exists.** Across 36 curated lists in this space, a search for
> `watchdog OR e-stop OR deadman OR velocity limit` returns roughly zero hits. The best
> governance coverage anywhere ([natnew/awesome-physical-ai]) lists ISO 10218, ISO/TS 15066,
> ISO 26262 and UL 4600 — and never connects any of them to a running VLA inference loop.
> This is the gap. It is also the part where being wrong hurts someone.

> **Opinion.** The framing below is mine, and the parts that are opinion are marked. What is
> not opinion is the standards structure and the failure independence argument.

---

## 0. What exists, and what does not

We looked for a reference implementation of the thing this page describes. The result is
worth stating plainly, because it is the reason this page is written rather than linked:

| Exists | Does not exist |
|---|---|
| [NVIDIA Halos](https://developer.nvidia.com/blog/inside-nvidia-halos-for-robotics-a-full-stack-functional-safety-system-for-physical-ai/) — a full-stack functional-safety **architecture** for physical AI | A reference watchdog / deadman / slew-rate limiter wrapping a **learned policy** |
| ISO/IEC TR 5469 — **informative** guidance on AI functional safety | Any published **certified** example of a learned policy inside a PLd / SIL2 safety function |
| `ros2_control` mock components — test controller plumbing | A standard "action is too old → stop" contract. Neither ROS 2 nor `ros2_control` defines one |
| Generic ROS 2 heartbeat patterns | A measured limit/OOD supervisor around a VLA. The only quantified one found reports AUC 0.99 on drift and 91% of faults caught at 1% false positives |

So: the standards exist, the safety architecture exists, and the **software you would actually
write** does not. The rest of this page is that software, specified.

Two consequences worth internalising:

- **Nobody publishes this as a repo.** LeRobot and openpi contain no safety layer at all —
  a grep for watchdog, e-stop or velocity limiting returns nothing. If you deploy either
  framework as shipped, you have no independent stop path.
- **The missing "stale action" contract is a real bug class.** With no convention for what to
  do when a chunk expires, the default behaviour is whatever the framework does, which is
  frequently "keep executing the stale chunk". That is a safety-relevant default chosen by
  nobody.

---

## 1. The core claim: your policy is not a safety system

A learned policy **cannot** be a safety function in the sense the standards use the term.
ISO 13849 requires safety functions to achieve a Performance Level (PL a–e), derived from the
required risk reduction, and PL is earned through architectural properties — redundancy,
diagnostic coverage, deterministic behaviour, a quantified MTTFd. A 3-billion-parameter
network running on a GPU with nondeterministic kernels has none of those properties. You
cannot calculate its PL, and adding a confidence score does not change that.

The practical consequence, and the thing that makes this page concrete:

> **The safety layer must be a separate, simpler, independently-verified system that sits
> between the policy and the actuators. It must be able to stop the robot when the policy
> process is dead, hung, or producing nonsense.**

Everything below is the implementation of that sentence.

### Independence is not a formality

The single most common mistake in research lab deployments:

```python
# WRONG — the watchdog lives inside the thing it is supposed to watch
class PolicyNode:
    def __init__(self):
        self.model = load_vla()
        self.last_ok = time.time()

    def step(self):
        obs = self.get_obs()
        action = self.model.infer(obs)          # CUDA OOM here
        self.last_ok = time.time()              # ...never runs
        self.send(action)
```

If `infer` raises, hangs, or the CUDA context dies, the watchdog dies with it and the robot
is left holding whatever the last command was. **A watchdog in the same process as the
policy is not a watchdog.**

The safety layer must be a separate process (better: a separate host, or the robot
controller's own real-time loop) that:

- receives a **heartbeat** from the policy process,
- enforces limits on whatever commands arrive,
- and **stops motion on heartbeat loss** — not on a bad command, on *silence*.

Failing safe means failing to *stopped*, which means the default state must be "no motion".

## 2. Layers, outermost first

Design them as independent layers. Any one of them should be able to prevent an injury
without help from the others.

### Layer 0 — Hardware

- **Emergency stop in the power path.** A software "e-stop" button that sets a flag is not an
  e-stop. It must remove power or assert a hardware stop input to the drive, in a circuit that
  does not depend on your Python process, your GPU, or the network.
- **Enabling device / deadman** for any teleoperation or teach mode.
- **Physical workspace boundaries** where the risk assessment calls for them. Cheap, and
  effective in a way no software layer is.

### Layer 1 — Command-level limits

Clamp every command *after* the policy produces it and *before* the actuator receives it.

```python
# The limiter must be stateless and trivially auditable. No learned components.
class JointLimiter:
    def __init__(self, q_min, q_max, dq_max, ddq_max, dt):
        self.q_min, self.q_max = q_min, q_max          # from the URDF / datasheet
        self.dq_max, self.ddq_max = dq_max, ddq_max    # from the drive spec
        self.dt = dt
        self.prev_q = self.prev_dq = None

    def __call__(self, q_cmd):
        clipped = {}
        q = np.clip(q_cmd, self.q_min, self.q_max)
        if np.any(q != q_cmd):
            clipped["position"] = True

        if self.prev_q is not None:
            dq = (q - self.prev_q) / self.dt
            dq_c = np.clip(dq, -self.dq_max, self.dq_max)
            if np.any(dq_c != dq):
                clipped["velocity"] = True
            if self.prev_dq is not None:
                ddq = (dq_c - self.prev_dq) / self.dt
                ddq_c = np.clip(ddq, -self.ddq_max, self.ddq_max)
                if np.any(ddq_c != ddq):
                    clipped["accel"] = True
                dq_c = self.prev_dq + ddq_c * self.dt
            q = self.prev_q + dq_c * self.dt
            self.prev_dq = dq_c

        self.prev_q = q
        return (q, clipped) if clipped else q
```

Two notes that matter more than the code:

- **Derive the limits from the hardware, never from your data.** Clamping at, say, the 99th
  percentile of your demonstration actions bakes in the teleoperator's speed and gives you no
  safety guarantee at all — and it will quietly cripple the policy on fast motions.
- **A clip is a signal, not just a correction.** If the limiter is engaging, the policy is
  asking for something the robot cannot do, which almost always means the input was out of
  distribution. Log it and count it. A rising clip rate is the earliest warning you get that
  the policy has left its training distribution, and it appears *before* the task fails.

### Layer 2 — Temporal guards

The failure mode specific to learned policies: everything is fine, but *late*.

| Guard | Rule | Action on violation |
|---|---|---|
| Stale observation | `now - obs.timestamp > max_age` | stop issuing new motion; hold last safe command |
| Heartbeat | policy process has not checked in within `T` | stop motion |
| Inference overrun | `infer()` has exceeded its deadline | cancel, fall back to holding |
| Chunk starvation | no new chunk before the buffer empties | switch to a decelerate-to-stop trajectory |

`max_age` should come from the control period, not from a guess: if you control at 50 Hz and
you tolerate acting on two-period-old data, `max_age ≈ 40 ms`. Anything older and the robot is
executing a plan for a world that no longer exists.

### Layer 3 — Spatial

- **Workspace bounding**: clamp the commanded Cartesian pose to a box that excludes the
  operator, the fixture, and the camera mounts. Simpler and more reliable than collision
  checking against a reconstructed scene.
- **Self-collision and fixture collision**: use the robot's own collision model where the
  controller provides one. Learned policies have no notion of the table and will happily
  drive through it.
- **Never let the policy command a frame change** — no base-frame or tool-frame selection
  driven by model output.

### Layer 4 — Out-of-distribution detection

You cannot reliably detect OOD from the policy's own confidence, but you can detect the
*consequences*. These are cheap and genuinely useful:

- **Action jump**: `‖a_t − a_{t−1}‖` exceeding the hardware's ability to execute it.
- **Saturation rate**: the fraction of dimensions pinned at a limit.
- **Observation novelty**: distance from the training distribution in a low-dimensional
  embedding. Crude, and still catches "someone walked in front of the camera".
- **Clip rate** from Layer 1.

Treat these as a **degradation trigger**, not a stop: reduce speed, request help, or hand over
to a scripted recovery. Stopping mid-task can itself be the unsafe outcome.

**There is now a real research cluster here**, which was not true when this page was first
written. Four papers, and they answer different questions:

| Work | What it contributes |
|---|---|
| [Hide-and-Seek in Trajectories](https://arxiv.org/abs/2605.30834) | Mines failure signals from the policy's *own trajectories* rather than requiring labelled failures — relevant because you will never have a clean negative set |
| [SAFECAST](https://arxiv.org/abs/2608.04246) | Failure detection under exactly the deployment shifts that break policies in the field: clutter, distractors, lighting, novel objects, reworded instructions |
| [RAFAIL](https://arxiv.org/abs/2609.18324) | Relationship-aware detection that explicitly trades the latency of VLM-based semantic checking against fast OOD scorers |
| [Rewind-IL](https://arxiv.org/abs/2604.16683) | Detection *plus* state respawning — the recovery half of graceful degradation, for long-horizon action-chunked failures |

**RAFAIL is the one to read first for a real deployment**, because it is the only one that
treats the monitor as a component with its own cost. A semantic check that needs a VLM forward
pass competes with your policy for the same GPU, and on the latency arithmetic in
[docs/41](41-real-time-inference.md) that competition is not free: you are either slowing the
policy or delaying the monitor. Decide which, deliberately, rather than discovering it when
the guard fires late.

And note what these give you: **detection**. Recovery is Rewind-IL and Layer 5 below. A monitor
with no bounded response is a logging system.

### Layer 5 — Recovery and human takeover

- **Scripted recovery primitives** that are not learned: open the gripper, retreat along the
  last known-safe path, return to a home pose. A policy that is confused should be able to
  hand off to something that is not.
- **Human takeover must be reachable** and must be able to happen while the policy keeps
  running, or the human will be fighting the model for control. Design the arbitration
  explicitly: who owns the actuators right now, and how is that transferred.
- **Log everything** for the post-mortem: observations, actions, guard violations, timings.

## 3. Mapping the standards onto a VLA loop

You will not certify a research prototype, but you should know what the structure would be.
This is where [natnew/awesome-physical-ai] stops and this page continues.

| Standard | What it governs | Where it lands in this architecture |
|---|---|---|
| **ISO 12100** | Risk assessment methodology | The document that justifies *your* limits and layers. Do this first; the rest is downstream |
| **ISO 10218-1 / -2** | Industrial robot safety (robot / integration) | Layer 0 and the stopping-performance requirements. Defines the safety-rated stop categories your Layer 2 must implement |
| **ISO/TS 15066** | Collaborative operation: power-and-force limiting, speed-and-separation monitoring | If a human shares the workspace: Layer 1 (force/velocity caps) plus a separation monitor. Your Layer 4 novelty signal is *not* a substitute for SSM |
| **ISO 21448 (SOTIF)** | Safety of the intended functionality: the system worked as designed, but the design was inadequate | **The right lens for a learned policy, and the one most often missed.** See below |
| **ISO 13849-1** | Performance Level of safety-related control systems | Applies to your limiter and stopping circuit — and to nothing that contains a neural network |
| **IEC 61508 / IEC 62061** | Functional safety, SIL | Same boundary: the deterministic layers, not the policy |
| **ISO 26262 / UL 4600** | Automotive / autonomous-product safety cases | Relevant if you are building a safety *case* rather than a cell; UL 4600's argument-based approach is a more realistic fit for learned components than a PL calculation |

The mapping is the point: **every standard lands on Layers 0–3 and none of them lands on the
policy.** That is not a limitation of the standards; it is the correct reading of what a
learned policy is.

### Why SOTIF is the standard you are actually looking for

Functional-safety standards assume the system does what it was specified to do and ask whether
it is safe when it *malfunctions*. A learned policy does not malfunction. It does exactly what
it was trained to do, competently, in a situation the training data did not cover — and that
is where the harm comes from. "No fault occurred" and "someone was hurt" are compatible.

ISO 21448 exists for precisely this shape of problem: unsafe behaviour arising from
insufficient situational awareness or an inadequate specification, with no component failure
to point at. For a VLA deployment the mapping is direct:

- **Known unsafe scenarios** — failure modes you have already observed and can test for. These
  are your troubleshooting entries, and they belong in a test suite.
- **Unknown unsafe scenarios** — the policy will do something you did not anticipate, in a
  situation you did not collect. This is the residual, and it is what Layer 4 monitoring and
  Layer 5 recovery exist to bound. You will not eliminate it by collecting more data.
- **The validation problem** — SOTIF forces you to argue coverage rather than assume it. For a
  learned policy that argument is "here is the state distribution I demonstrated, and here is
  where I have evidence the policy degrades". If you cannot state that boundary, you do not
  have a safety case, you have a hope.

Practical consequence: **track your policy's operational design domain explicitly** — the
objects, poses, lighting, and clutter it was trained on — and treat departures from it as
first-class events, not as noise. A CBF or a velocity limiter does not know the difference
between "reaching for the cup" and "reaching for the operator's hand that looks a bit like a
cup". Only your Layer 4 monitor, plus a bounded authority limit, can act on that.

### Readable standards material

Every standards link above resolves to a paywalled catalogue page, which is useless when you
are trying to understand what the standard actually requires. Two free entry points:

- **DGUV/IFA on collaborative robots** — [dguv.de/ifa](https://www.dguv.de/ifa/fachinfos/kollaborierende-roboter/index-2.jsp).
  A readable interpretation of ISO/TS 15066 and ISO 10218 written by a body that assesses these
  systems for a living, including concrete power-and-force limit tables. Start here before
  buying the standards.
- **[natnew/awesome-physical-ai](https://github.com/natnew/awesome-physical-ai)** maintains the
  best index of the standards landscape itself (ISO 10218, ISO/TS 15066, ISO 26262, UL 4600, EU
  AI Act). It stops at the index; this page is the part that connects them to a running loop.

## 4. Checklist before a policy drives anything

- [ ] Risk assessment written down (ISO 12100) and the limits derived from it
- [ ] E-stop is in the power path and was *tested* under load
- [ ] Safety limiter runs in a different process from the policy
- [ ] Heartbeat loss → motion stops (verify by `kill -9` on the policy process, mid-motion)
- [ ] Stale-observation guard active, threshold derived from the control period
- [ ] Position / velocity / acceleration limits from hardware specs, not from dataset percentiles
- [ ] Clip rate and action-jump rate are logged and alarmed
- [ ] Scripted recovery primitives exist and are reachable
- [ ] Human takeover arbitration is explicit and was rehearsed
- [ ] Workspace bound excludes the operator, fixtures, and camera mounts
- [ ] Someone has stood next to the robot and watched a deliberate failure

The last item is not a joke. The only way to know the layers work is to break the policy on
purpose, in front of a person holding the e-stop, and watch what the robot does.

---

[VLA-Handbook]: https://github.com/sou350121/VLA-Handbook
[natnew/awesome-physical-ai]: https://github.com/natnew/awesome-physical-ai
