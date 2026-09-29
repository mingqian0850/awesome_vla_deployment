#!/usr/bin/env python3
"""
diag_policy.py -- is the pi0.5 action expert actually USING its inputs?

For the symptom "no matter what the initial state is, it always performs the first
motion of the chain", the decisive question is not data balance at all. It is:

    Does the predicted action chunk change when the observation changes?

Three tests:

  collapse  -- predict chunks for observations sampled across the whole episode. If the
               output barely varies between wildly different states, the conditioning has
               collapsed (the action expert regressed to the unconditional mean).
  ablate    -- knock out one input at a time (state / each image / prompt) and measure how
               far the prediction moves, in units of the NATURAL cross-observation
               variation. Sensitivity below the sampling-noise floor == that input is dead.
  openloop  -- teacher forcing: expert observations in, predicted chunk vs the expert's
               actual continuation, per chunk index, against two dumb baselines (constant
               mean action, repeat-the-current-action). If the model cannot beat "repeat
               the current action" on expert states, the failure is in training/data, not
               in closed-loop drift.

WHY THE NOISE FLOOR MATTERS: flow matching samples stochastically. Repeating the SAME
observation shows the run-to-run spread; any input sensitivity below it is noise.

Usage:
    python diag_policy.py --dataset /path/to/lerobot --config pi05_myrobot \\
        --checkpoint /path/to/ckpt --test all
    python diag_policy.py --dataset /path/to/lerobot --config pi05_myrobot --show-obs
    python diag_policy.py --selftest        # no openpi / no data needed; validates the tests

The only function you are likely to need to adapt for your openpi config is `build_obs`.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

EPS = 1e-8


def hr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def sub(t):
    print("\n--- " + t + " " + "-" * max(0, 72 - len(t)))


# --------------------------------------------------------------------------------------
# observation construction -- THE ONE FUNCTION YOU MAY NEED TO ADAPT
# --------------------------------------------------------------------------------------
def build_obs(frame: dict, image_keys: list[str], prompt: str) -> dict:
    """dataset frame -> openpi observation dict.

    openpi's `policy.infer` accepts the raw repo naming convention:
        {"observation.images.<cam>": uint8 HWC, "observation.state": float32 (ds,),
         "prompt": str}
    If your config uses another convention ("observation/image", "state", or openpi's
    internal "base_0_rgb"/"wrist_0_rgb" keys) change ONLY this function and verify with
    --show-obs.
    """
    obs = {}
    for k in image_keys:
        if k in frame:
            obs[k] = np.asarray(frame[k])
    if "observation.state" in frame:
        obs["observation.state"] = np.asarray(frame["observation.state"], dtype=np.float32)
    obs["prompt"] = prompt
    return obs


class OpenpiAdapter:
    """policy.infer(obs) -> (H, da). Adapt here if your openpi version differs."""

    def __init__(self, args):
        from openpi.policies import policy_config
        from openpi.training import config as _config

        cfg = _config.get_config(args.config)
        if args.checkpoint:
            cfg = cfg.replace(checkpoint_dir=args.checkpoint) if hasattr(cfg, "replace") else cfg
        self.policy = policy_config.create_trained_policy(cfg, args.checkpoint or cfg.checkpoint_dir)

    def infer(self, obs: dict) -> np.ndarray:
        out = self.policy.infer(obs)
        a = np.asarray(out["actions"] if isinstance(out, dict) else out, dtype=np.float64)
        return a.reshape(-1, a.shape[-1]) if a.ndim > 2 else a


# --------------------------------------------------------------------------------------
# dataset access
# --------------------------------------------------------------------------------------
def load_dataset(root: str, max_frames: int):
    try:
        from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
    except Exception:
        try:
            from lerobot.datasets.lerobot_dataset import LeRobotDataset
        except Exception as e:
            raise SystemExit(
                "lerobot is required to decode frames/videos. Install lerobot, or build the "
                "`frames` list yourself (see FakeAdapter/selftest below for the expected shape)."
            ) from e

    ds = LeRobotDataset(repo_id=root.rstrip("/").split("/")[-1], root=root)
    meta = ds.meta
    fps = getattr(meta, "fps", 30)
    image_keys = [k for k in meta.features if k.startswith("observation.images")]
    ep_key = "episode_index" if "episode_index" in meta.features else None

    n = len(ds)
    step = max(1, n // max(1, max_frames))
    frames, actions, states, eps, fids = [], [], [], [], []
    for i in range(0, n, step):
        try:
            fr = ds[i]
        except Exception:
            continue
        frames.append({k: np.asarray(fr[k]) for k in image_keys + ["observation.state"] if k in fr})
        actions.append(np.asarray(fr["action"], dtype=np.float64))
        states.append(np.asarray(fr.get("observation.state", [0.0]), dtype=np.float64))
        eps.append(int(fr[ep_key]) if ep_key else i)
        fids.append(int(fr.get("frame_index", i)))
    if not actions:
        raise SystemExit("could not read any frames from the dataset")
    ei, fi = np.array(eps), np.array(fids)
    lens = {int(e): int(fi[ei == e].max() + 1) for e in np.unique(ei)}
    return frames, np.stack(actions), np.stack(states), ei, fi, lens, image_keys, fps


def norm_scale(a: np.ndarray) -> float:
    """One scalar action scale so every printed number is interpretable."""
    return float(np.percentile(np.linalg.norm(a - a.mean(axis=0), axis=1), 90)) + EPS


# --------------------------------------------------------------------------------------
# TEST 1 -- conditional collapse
# --------------------------------------------------------------------------------------
def test_collapse(ad, frames, a_gt, ei, fi, lens, prompt, args):
    hr("TEST 1. CONDITIONAL COLLAPSE -- does the output depend on the observation?")
    n = len(frames)
    t_norm = np.array([fi[i] / max(lens.get(int(ei[i]), 1) - 1, 1) for i in range(n)])
    order = np.argsort(t_norm)
    pick = order[np.linspace(0, len(order) - 1, min(args.n_samples, len(order))).astype(int)]
    groups = np.where(t_norm[pick] < 0.34, 0, np.where(t_norm[pick] < 0.67, 1, 2))

    P = np.stack([ad.infer(build_obs(frames[i], ad.image_keys, prompt)) for i in pick])
    scale = norm_scale(a_gt)
    dev_rel = float(np.linalg.norm(P - P.mean(axis=0), axis=(1, 2)).mean()) / scale

    # Phase discrimination: how much of the DATA's phase-to-phase action difference does
    # the model reproduce? ratio ~1 => it separates the phases as well as the data does;
    # ratio ~0 => it emits the same behaviour for phases that require different actions.
    # This is scale-free and cannot divide by zero (uninformative pairs are skipped).
    ug = sorted(set(groups.tolist()))
    disc = {}
    for gi in range(len(ug)):
        for gj in range(gi + 1, len(ug)):
            mi = groups == ug[gi]
            mj = groups == ug[gj]
            dm = float(np.mean([np.linalg.norm(P[a] - P[b])
                                for a in np.flatnonzero(mi) for b in np.flatnonzero(mj)]))
            gt_i, gt_j = a_gt[pick][mi].mean(axis=0), a_gt[pick][mj].mean(axis=0)
            dd = float(np.linalg.norm(gt_i - gt_j))
            if dd > 0.05 * scale:                      # only judge phases the data separates
                disc[(int(ug[gi]), int(ug[gj]))] = (dm, dd, dm / dd)
    disc_min = min((v[2] for v in disc.values()), default=float("nan"))

    print(f"  dataset action scale p90||a-mean||                 : {scale:.4f}")
    print(f"  predicted chunks deviate from their own mean by     : {dev_rel:.3f} x scale")
    print(f"  {'phase pair':<14}{'model spread':>14}{'data spread':>13}{'reproduced':>12}")
    for (gi, gj), (dm, dd, r) in disc.items():
        print(f"  {f'{gi} vs {gj}':<14}{dm:>14.4f}{dd:>13.4f}{r:>11.2f}x")
    print(f"  worst phase pair reproduces only {disc_min:.2f}x of the required difference"
          if disc else "  (no phase pair is separated in the data; nothing to judge)")

    sub("verdict")
    collapsed = dev_rel < 0.05
    phase_blind = (not collapsed) and (disc and disc_min < 0.25)
    if collapsed:
        print("  !! THE PREDICTION IS ESSENTIALLY CONSTANT ACROSS ALL OBSERVATIONS.")
        print("     The action expert has collapsed to (near) the unconditional mean action.")
        print("     That alone produces 'it always replays the same first motion'.")
        print("     Suspects: LR too high / too few steps for the frozen-VLM recipe, a dead")
        print("     state or image channel (TEST 2), or wrong action targets/normalisation so")
        print("     that predicting the mean is the loss optimum.")
    elif phase_blind:
        print(f"  !! The output moves between frames but FAILS to separate phases that the data")
        print(f"     clearly separates (worst pair reproduces only {disc_min:.2f}x of the gap).")
        print("     The policy is reading nuisance variation instead of the phase. TEST 2")
        print("     shows which input it is actually reading.")
    else:
        print("  -> The output tracks the phase-to-phase action difference in the data.")
        print("     Conditioning works; look at closed-loop execution / chunking instead.")
    return {"scale": scale, "dev_rel": dev_rel, "disc_min": disc_min,
            "collapsed": collapsed, "phase_blind": bool(phase_blind)}


# --------------------------------------------------------------------------------------
# TEST 2 -- input ablation
# --------------------------------------------------------------------------------------
def test_ablate(ad, frames, a_gt, states, ei, fi, lens, prompt, args):
    hr("TEST 2. INPUT ABLATION -- which inputs does the policy actually read?")
    print("  sensitivity = ||a_ablated - a_base|| / ||a_base - a_mean||  (per sample, then")
    print("  averaged). Near 0 => that input is IGNORED.\n")

    n = len(frames)
    pick = np.linspace(0, n - 1, min(args.n_samples, n)).astype(int)
    other = np.roll(pick, 1)

    base, floor = [], []
    for i in pick:
        obs = build_obs(frames[i], ad.image_keys, prompt)
        reps = [ad.infer(obs) for _ in range(max(1, args.repeats))]
        base.append(reps[0])
        if len(reps) > 1:
            floor.append(float(np.mean([np.linalg.norm(r - reps[0]) for r in reps[1:]])))
    B = np.stack(base)
    bdev = np.linalg.norm(B - B.mean(axis=0), axis=(1, 2))
    scale = norm_scale(a_gt)
    if float(np.mean(bdev)) < 0.02 * scale:
        print("  !! The base predictions are already almost constant (TEST 1 fires).")
        print("     Sensitivities below are measured against a floored denominator and are")
        print("     not meaningful until the collapse itself is fixed. Fix that first.")
    denom = np.maximum(bdev, 0.05 * scale)
    noise = float(np.mean(floor) / np.mean(denom)) if floor else 0.0
    print(f"  sampling-noise floor (same obs, {args.repeats} run(s)) : {noise:.4f}"
          f"   <- below this everything is noise")

    s_mean = states.mean(axis=0)
    variants: dict[str, dict] = {
        "state -> zeros": {i: np.zeros_like(states[i]) for i in pick},
        "state -> dataset mean": {i: s_mean.astype(np.float32) for i in pick},
        "state -> other frame's": {i: states[o] for i, o in zip(pick, other)},
        "prompt -> empty string": {i: "" for i in pick},
        "prompt -> other instruction": {i: (args.other_prompt or "put the object on the shelf")
                                        for i in pick},
    }
    for k in ad.image_keys:
        if k in frames[pick[0]]:
            variants[f"{k} -> zeros"] = {i: np.zeros_like(np.asarray(frames[i][k])) for i in pick}
            variants[f"{k} -> other frame's"] = {i: np.asarray(frames[o][k]) for i, o in zip(pick, other)}

    print(f"\n  {'ablation':<40}{'sensitivity':>13}{'vs noise':>11}")
    res = {}
    for name, vals in variants.items():
        ratios = []
        for j, i in enumerate(pick):
            obs = build_obs(frames[i], ad.image_keys, prompt)
            if name.startswith("state"):
                obs["observation.state"] = np.asarray(vals[i], dtype=np.float32)
            elif name.startswith("prompt"):
                obs["prompt"] = vals[i]
            else:
                key = name.split(" -> ")[0]
                obs[key] = vals[i]
            ratios.append(float(np.linalg.norm(ad.infer(obs) - B[j])) / denom[j])
        s = float(np.mean(ratios))
        res[name] = s
        ignored = s < max(2 * noise, 0.05)
        vs = "     n/a" if noise <= 0 else f"{s / noise:>8.1f}x"
        print(f"  {name:<40}{s:>13.4f}{vs}" + ("   <-- IGNORED" if ignored else ""))

    sub("verdict")
    dead = [k for k, v in res.items() if v < max(2 * noise, 0.05)]
    if any(k.startswith("state") for k in dead):
        print("  !! The policy ignores the proprioceptive state.")
        print("     For pi0.5 that normally means the state tokenisation/normalisation does")
        print("     not match the checkpoint (zeros/wrong dims fed, q01-q99 stats from the")
        print("     wrong dataset), or the state pathway is effectively frozen. With a dead")
        print("     state channel AND ambiguous images the phase is unobservable, and the")
        print("     action expert can only emit one behaviour -- exactly your symptom.")
    if any(k.startswith("prompt") for k in dead):
        print("  !! The policy ignores the instruction, so it cannot know which sub-task it")
        print("     is in unless the images disambiguate it. Confirm the prompt reaches the")
        print("     tokenizer, and that each frame carries its CURRENT sub-task instruction")
        print("     rather than one global instruction for the whole chain.")
    if not dead:
        print("  -> Every input moves the prediction above the noise floor; conditioning is")
        print("     intact. Look at TEST 3 and at the chunking / inference configuration.")
    return res, noise


# --------------------------------------------------------------------------------------
# TEST 3 -- open-loop teacher forcing
# --------------------------------------------------------------------------------------
def test_openloop(ad, frames, a_gt, ei, fi, lens, prompt, args):
    hr("TEST 3. OPEN-LOOP TEACHER FORCING -- can it predict the expert's continuation?")
    print("  Expert observations in; predicted chunk vs the expert's real next H actions,")
    print("  against two dumb baselines. Losing to them means essentially nothing was")
    print("  learned about the action distribution.\n")

    n = len(frames)
    H = args.chunk_size
    scale = norm_scale(a_gt)
    pick = np.linspace(0, n - 1, min(args.n_samples, n)).astype(int)
    gt_mean = a_gt.mean(axis=0)
    em = np.zeros(H)
    ec = np.zeros(H)
    er = np.zeros(H)
    cnt = np.zeros(H)

    for i in pick:
        e, f = int(ei[i]), int(fi[i])
        L = lens.get(e, 10 ** 9)
        pred = ad.infer(build_obs(frames[i], ad.image_keys, prompt))
        for k in range(H):
            if f + k >= L or i + k >= n or ei[i + k] != e:
                break
            gt = a_gt[i + k]
            em[k] += np.linalg.norm(pred[k] - gt)
            ec[k] += np.linalg.norm(gt_mean - gt)
            er[k] += np.linalg.norm(a_gt[i] - gt)
            cnt[k] += 1
    cnt = np.maximum(cnt, 1)
    em, ec, er = em / cnt, ec / cnt, er / cnt

    print(f"  {'k':>4}{'model':>12}{'constant-mean':>16}{'repeat-current':>16}{'model/scale':>13}")
    for k in sorted(set(list(range(0, H, max(1, H // 10))) + [H - 1])):
        print(f"  {k:>4}{em[k]:>12.4f}{ec[k]:>16.4f}{er[k]:>16.4f}{em[k] / scale:>13.3f}")
    print(f"\n  mean over k: model {em.mean():.4f}  constant {ec.mean():.4f}  repeat {er.mean():.4f}")
    print(f"  model / scale = {em.mean() / scale:.3f}   (0 = perfect, 1 = a typical action)")
    print(f"  error growth k=0 -> k={H - 1}: {em[0]:.4f} -> {em[H - 1]:.4f} "
          f"({em[H - 1] / max(em[0], EPS):.2f}x)")

    sub("verdict")
    worse = em.mean() >= min(ec.mean(), er.mean())
    if worse:
        print("  !! NO BETTER THAN A CONSTANT / REPEATED ACTION even on expert states. This")
        print("     is not closed-loop drift: the action expert has not learned the action")
        print("     distribution. Check, in order:")
        print("       - chunk targets: is actions[t, k] really the action at frame t+k?")
        print("       - is the flow-matching loss masked on padded steps?")
        print("       - are the normalisation stats recomputed on YOUR dataset?")
        print("       - LR / step count / which modules are frozen")
    elif em[0] * 1.5 < em[H - 1]:
        print("  !! Error grows sharply with chunk index: k=0 is roughly right and the rest")
        print("     decays. Either the chunk targets beyond k=0 are broken, or the model is")
        print("     averaging modes. Cross-check with TEST 1.")
    else:
        print("  -> It reproduces the expert's continuation on expert states. If closed-loop")
        print("     execution still stops after the first sub-task, the cause is covariate")
        print("     shift: collect recovery / intermediate-start data (start the robot at the")
        print("     entrance state of EVERY sub-task, including slightly off-expert states),")
        print("     and execute a longer chunk (n_action_steps) with temporal ensembling.")
    return {"per_k": em, "worse_than_baseline": worse}


# --------------------------------------------------------------------------------------
# self-test: fake policies with known behaviour, to validate the thresholds
# --------------------------------------------------------------------------------------
class FakeAdapter:
    """mode: 'healthy' | 'state_blind' | 'collapsed'."""

    def __init__(self, mode: str, phase_of_frame, action_of_phase, image_of_phase):
        self.mode, self.phase_of_frame = mode, phase_of_frame
        self.action_of_phase, self.image_of_phase = action_of_phase, image_of_phase
        self.image_keys = ["observation.images.cam"]

    def infer(self, obs: dict) -> np.ndarray:
        H, da = 8, 4
        if self.mode == "collapsed":
            return np.tile(np.array([0.10, 0.0, -0.05, 0.0]), (H, 1))
        img = np.asarray(obs[self.image_keys[0]], dtype=np.float64).ravel() / 255.0
        ph_img = int(np.argmin([np.linalg.norm(img - self.image_of_phase[p]) for p in (0, 1, 2)]))
        if self.mode == "state_blind":
            ph = ph_img
        else:                                   # healthy: read the state
            st = np.asarray(obs["observation.state"], dtype=np.float64)
            ph = int(np.clip(round(float(st[0]) * 2), 0, 2))
        return np.tile(self.action_of_phase[ph], (H, 1))


def selftest(args) -> int:
    hr("SELF-TEST: fake policies with known behaviour")
    rng = np.random.default_rng(0)
    n_ep, length = 12, 60
    action_of_phase = {0: np.array([0.08, 0.0, 0.0, 0.0]),
                       1: np.array([0.0, 0.0, 0.07, 0.0]),
                       2: np.array([0.0, 0.0, -0.05, -0.06])}
    # images: phase 0 and phase 2 look IDENTICAL (aliased), phase 1 is distinct
    image_of_phase = {0: np.full(16, 0.30), 1: np.full(16, 0.75), 2: np.full(16, 0.30)}

    frames, a_gt, states, ei, fi, lens, phase = [], [], [], [], [], {}, []
    for e in range(n_ep):
        lens[e] = length
        for f in range(length):
            ph = min(2, f * 3 // length)
            st = np.array([ph / 2.0, float(e), 0.0, 0.0])
            frames.append({"observation.images.cam": (image_of_phase[ph] * 255).astype(np.uint8).reshape(4, 4, 1),
                           "observation.state": st.astype(np.float32)})
            a_gt.append(action_of_phase[ph] + rng.normal(0, 0.004, 4))
            states.append(st)
            ei.append(e)
            fi.append(f)
            phase.append(ph)
    a_gt, states = np.stack(a_gt), np.stack(states)
    ei, fi = np.array(ei), np.array(fi)
    phase = np.array(phase)
    args.n_samples, args.repeats, args.chunk_size = 12, 1, 8

    ok = True

    def check(cond, msg):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")
        ok &= bool(cond)

    import contextlib
    import io
    buf = io.StringIO()

    sub("healthy policy: conditioning must NOT be flagged")
    with contextlib.redirect_stdout(buf):
        ad_h = FakeAdapter("healthy", phase, action_of_phase, image_of_phase)
        c = test_collapse(ad_h, frames, a_gt, ei, fi, lens, "do the task", args)
        ab, noise_h = test_ablate(ad_h, frames, a_gt, states, ei, fi, lens, "do the task", args)
        ol = test_openloop(ad_h, frames, a_gt, ei, fi, lens, "do the task", args)
    check(not c["collapsed"], f"healthy: not collapsed (dev_rel={c['dev_rel']:.3f})")
    check(not c["phase_blind"], f"healthy: separates phases (disc_min={c['disc_min']:.2f}x)")
    check(ab["state -> zeros"] > 0.5, f"healthy: state matters (sens={ab['state -> zeros']:.3f})")
    check(not ol["worse_than_baseline"], "healthy: beats the dumb baselines in open loop")

    sub("collapsed policy: must be flagged as constant output")
    with contextlib.redirect_stdout(buf):
        ad_c = FakeAdapter("collapsed", phase, action_of_phase, image_of_phase)
        c2 = test_collapse(ad_c, frames, a_gt, ei, fi, lens, "do the task", args)
        ol2 = test_openloop(ad_c, frames, a_gt, ei, fi, lens, "do the task", args)
    check(c2["collapsed"], f"collapsed: constant-output alarm fired (dev_rel={c2['dev_rel']:.3f})")
    check(ol2["worse_than_baseline"], "collapsed: loses to the dumb baselines")

    sub("state-blind policy: the state ablation must be flagged as IGNORED")
    with contextlib.redirect_stdout(buf):
        ad_s = FakeAdapter("state_blind", phase, action_of_phase, image_of_phase)
        ab2, noise_s = test_ablate(ad_s, frames, a_gt, states, ei, fi, lens, "do the task", args)
        c3 = test_collapse(ad_s, frames, a_gt, ei, fi, lens, "do the task", args)
    thresh = max(2 * noise_s, 0.05)
    check(ab2["state -> zeros"] < thresh,
          f"state-blind: state flagged IGNORED (sens={ab2['state -> zeros']:.4f} < {thresh})")
    check(ab2["observation.images.cam -> zeros"] >= thresh,
          f"state-blind: image NOT flagged ignored (sens={ab2['observation.images.cam -> zeros']:.3f})")
    check(ab2["observation.images.cam -> zeros"] > 10 * ab2["state -> zeros"],
          "state-blind: image sensitivity dominates state sensitivity")
    check(c3["phase_blind"], f"state-blind: phase-blindness detected (disc_min={c3['disc_min']:.2f}x)")

    print(f"\n  overall: {'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


# --------------------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser(description="Is the pi0.5 action expert using its inputs?")
    p.add_argument("--selftest", action="store_true", help="validate the tests with fake policies; no data needed")
    p.add_argument("--dataset", help="LeRobot dataset root")
    p.add_argument("--config", help="openpi config name, e.g. pi05_myrobot")
    p.add_argument("--checkpoint")
    p.add_argument("--prompt", default=None, help="instruction (default: the dataset's task)")
    p.add_argument("--other-prompt", help="prompt used by the 'prompt -> other instruction' ablation")
    p.add_argument("--image-keys", help="comma-separated camera keys to use")
    p.add_argument("--test", default="all", choices=["all", "collapse", "ablate", "openloop"])
    p.add_argument("--n-samples", type=int, default=12)
    p.add_argument("--repeats", type=int, default=3, help="same-obs repeats for the noise floor")
    p.add_argument("--chunk-size", type=int, default=50)
    p.add_argument("--show-obs", action="store_true", help="print one observation dict and exit")
    args = p.parse_args()

    if args.selftest:
        return selftest(args)
    if not args.dataset or not args.config:
        p.print_help()
        return 2

    frames, a_gt, states, ei, fi, lens, image_keys, fps = load_dataset(args.dataset, args.n_samples * 4)
    prompt = args.prompt or "perform the task"
    print(f"loaded {len(frames)} sampled frames, {len(lens)} episodes, fps={fps}")
    print(f"image keys found: {image_keys}")

    if args.show_obs:
        hr("OBSERVATION DICT FROM build_obs() -- align this with your openpi config")
        for k, v in build_obs(frames[0], args.image_keys.split(",") if args.image_keys else image_keys,
                              prompt).items():
            print(f"  {k:<36} {type(v).__name__:<10} shape={getattr(v, 'shape', None)} "
                  f"dtype={getattr(v, 'dtype', None)}")
        return 0

    ad = OpenpiAdapter(args)
    ad.image_keys = args.image_keys.split(",") if args.image_keys else image_keys
    print(f"using image keys: {ad.image_keys}")

    if args.test in ("all", "collapse"):
        test_collapse(ad, frames, a_gt, ei, fi, lens, prompt, args)
    if args.test in ("all", "ablate"):
        test_ablate(ad, frames, a_gt, states, ei, fi, lens, prompt, args)
    if args.test in ("all", "openloop"):
        test_openloop(ad, frames, a_gt, ei, fi, lens, prompt, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
