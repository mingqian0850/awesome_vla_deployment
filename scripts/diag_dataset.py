#!/usr/bin/env python3
"""
diag_dataset.py -- LeRobot dataset diagnostics for VLA (pi0.5 / openpi) fine-tuning.

Answers, from the DATA alone, the question:

    "Why does my policy only ever do the first motion of the chained task?"

It separates the two competing root causes:

  (H1) ALIASING  -- the same observation requires different actions in different
                    phases of the chained task, and nothing in the input tells the
                    policy which phase it is in.  => must add subtask labels /
                    phase conditioning, and split the chain into labeled segments.
  (H2) COLLAPSE  -- the information IS in the data, but the action expert is not
                    using it (dead state channel, wrong normalisation, frozen VLM,
                    LR too high, chunk targets broken).  => model/training fix.

Plus mechanical data bugs that look exactly like "only learned the first action":
  * dead / constant proprioceptive state dimensions
  * idle frames at the head of every episode  ("at the start state, do nothing")
  * chunk targets padded over the episode end (most supervised targets garbage)
  * delta vs absolute action mismatch with the pretrained normalisation stats

Usage:
    python diag_dataset.py /path/to/lerobot_dataset
    python diag_dataset.py /path/to/lerobot_dataset --n-phases 3 --emit-weights w.npy
    python diag_dataset.py --selftest          # no data needed; validates this tool

Only numpy + pyarrow are required. matplotlib is optional (plots).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field

import numpy as np

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as e:  # pragma: no cover
    raise SystemExit("pyarrow is required: pip install pyarrow") from e

EPS = 1e-8


# --------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------
def hr(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def sub(title: str) -> None:
    print("\n--- " + title + " " + "-" * max(0, 72 - len(title)))


def flag(cond: bool, msg: str, ok: str = "OK", bad: str = "!!") -> None:
    print(f"  [{ok if cond else bad}] {msg}")


def robust_norm(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Median/IQR normalisation. Returns (normalised, center, scale)."""
    c = np.median(x, axis=0)
    q1 = np.percentile(x, 1, axis=0)
    q99 = np.percentile(x, 99, axis=0)
    s = np.maximum(q99 - q1, EPS)
    return (x - c) / s, c, s


def sparkline(values: np.ndarray, width: int = 72) -> str:
    """ASCII plot so the report is readable without matplotlib."""
    blocks = "▁▂▃▄▅▆▇█"
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        return ""
    if v.size > width:
        idx = np.linspace(0, v.size, width + 1).astype(int)
        v = np.array([v[a:b].mean() if b > a else v[a] for a, b in zip(idx[:-1], idx[1:])])
    lo, hi = float(np.min(v)), float(np.max(v))
    if hi - lo < EPS:
        return blocks[0] * v.size
    q = ((v - lo) / (hi - lo) * (len(blocks) - 1)).round().astype(int)
    return "".join(blocks[i] for i in q)


def action_magnitude(action: np.ndarray) -> np.ndarray:
    """Per-frame motion magnitude, scale-free: ||a_t|| relative to the 99th percentile
    of ||a||. We deliberately do NOT normalise per dimension: dims that only ever see
    sensor noise have a tiny q99-q01 range and would fake a large normalised value."""
    n = np.linalg.norm(action, axis=1)
    return n / max(float(np.percentile(n, 99)), EPS)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > EPS else 0.0


# --------------------------------------------------------------------------------------
# data loading (LeRobot v2.0 / v2.1, read straight from parquet: version-proof)
# --------------------------------------------------------------------------------------
@dataclass
class Frames:
    """Flat, concatenated view of a LeRobot dataset's tabular columns."""
    action: np.ndarray                 # (N, da)
    state: np.ndarray | None           # (N, ds) or None
    episode_index: np.ndarray          # (N,)
    frame_index: np.ndarray            # (N,) index inside the episode
    index: np.ndarray                  # (N,) global frame index
    task_index: np.ndarray | None      # (N,)
    timestamp: np.ndarray | None       # (N,)
    ep_starts: np.ndarray = field(default_factory=lambda: np.zeros(0, int))
    ep_lengths: np.ndarray = field(default_factory=lambda: np.zeros(0, int))
    ep_ids: np.ndarray = field(default_factory=lambda: np.zeros(0, int))
    tasks: dict[int, str] = field(default_factory=dict)
    info: dict = field(default_factory=dict)
    custom: dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return int(self.action.shape[0])

    @property
    def fps(self) -> float:
        return float(self.info.get("fps", 0) or 0)


def _to_2d(col) -> np.ndarray:
    if pa.types.is_list(col.type) or pa.types.is_large_list(col.type) or pa.types.is_fixed_size_list(col.type):
        return np.stack([np.asarray(v, dtype=np.float64) for v in col.to_pylist()])
    return np.asarray(col.to_pylist(), dtype=np.float64).reshape(len(col), -1)


def _find_column(names: list[str], candidates: list[str]) -> str | None:
    for c in candidates:
        for n in names:
            if n == c or n.lower() == c.lower():
                return n
    return None


def load_lerobot(root: str, extra_columns: list[str] | None = None, max_episodes: int | None = None) -> Frames:
    info_path = os.path.join(root, "meta", "info.json")
    if not os.path.isfile(info_path):
        raise SystemExit(f"not a LeRobot dataset (missing meta/info.json): {root}")
    with open(info_path) as f:
        info = json.load(f)

    shards = sorted(glob.glob(os.path.join(root, "data", "**", "*.parquet"), recursive=True))
    if not shards:
        raise SystemExit(f"no data parquet found under {root}/data")
    if info.get("codebase_version", "").startswith("v3"):
        print("  note: this looks like a LeRobot v3 layout; the v2 flat-column assumptions may"
              " not hold. Verify the reported frame/episode counts against meta/info.json.")

    wanted = ["action", "observation.state", "episode_index", "frame_index", "index",
              "task_index", "timestamp"] + list(extra_columns or [])

    tables = []
    for path in shards:
        t = pq.read_table(path, columns=None)
        names_here = [f.name for f in t.schema]
        if not any(n == "action" or n.lower() == "action" for n in names_here):
            continue                      # e.g. a video-only shard
        keep = [f.name for f in t.schema if f.name in wanted]
        t = t.select(keep)
        # normalise naming for our internal use
        ren = {}
        for c in keep:
            low = c.lower()
            if low in ("episode_index", "frame_index", "index", "task_index", "timestamp"):
                ren[c] = low
        if ren:
            t = t.rename_columns([ren.get(f.name, f.name) for f in t.schema])
        tables.append(t)

    tbl = pa.concat_tables(tables, promote_options="default")
    names = [f.name for f in tbl.schema]

    act_name = _find_column(names, ["action", "actions"])
    if act_name is None:
        raise SystemExit(f"no 'action' column; found: {names}")

    # restore the global frame order so that frames of one episode are contiguous; a
    # sharded dataset read in filename order is not guaranteed to satisfy this
    order = None
    if "index" in names:
        order = np.argsort(np.asarray(tbl.column("index").to_pylist(), dtype=np.int64), kind="stable")
    if order is not None:
        tbl = pa.Table.from_arrays([tbl.column(i).take(pa.array(order)) for i in range(tbl.num_columns)],
                                   names=tbl.schema.names)
        names = [f.name for f in tbl.schema]

    out = {}
    out["action"] = _to_2d(tbl.column(act_name))

    st_name = _find_column(names, ["observation.state", "observation/state", "state", "proprio"])
    out["state"] = _to_2d(tbl.column(st_name)) if st_name else None

    for k in ("episode_index", "frame_index", "index", "task_index"):
        out[k] = np.asarray(tbl.column(k).to_pylist(), dtype=np.int64) if k in names else None
    out["timestamp"] = np.asarray(tbl.column("timestamp").to_pylist(), dtype=np.float64) if "timestamp" in names else None

    # custom columns (e.g. a hand-added 'phase' / 'subtask' column)
    custom = {}
    for c in extra_columns or []:
        if c in names:
            custom[c] = _to_2d(tbl.column(c)) if pa.types.is_list(tbl.column(c).type) else np.asarray(tbl.column(c).to_pylist())

    if out["episode_index"] is None:                     # synthesise from episode boundaries
        out["episode_index"] = np.zeros(len(out["action"]), dtype=np.int64)

    ep = out["episode_index"]
    if max_episodes is not None:
        keep = ep < max_episodes
        out = {k: (v[keep] if isinstance(v, np.ndarray) and v.shape[:1] == ep.shape else v) for k, v in out.items()}
        custom = {k: v[keep] for k, v in custom.items()}
        ep = out["episode_index"]

    ep_ids = np.unique(ep)
    starts, lengths = [], []
    for e in ep_ids:
        idx = np.flatnonzero(ep == e)
        starts.append(int(idx[0]))
        lengths.append(len(idx))

    # tasks
    tasks = {}
    tj = os.path.join(root, "meta", "tasks.jsonl")
    if os.path.isfile(tj):
        with open(tj) as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line)
                    tasks[int(d.get("task_index", len(tasks)))] = str(d.get("task", ""))

    return Frames(
        action=out["action"], state=out["state"], episode_index=ep,
        frame_index=out["frame_index"] if out["frame_index"] is not None else np.zeros(len(ep), int),
        index=out["index"] if out["index"] is not None else np.arange(len(ep)),
        task_index=out["task_index"], timestamp=out["timestamp"],
        ep_starts=np.array(starts, int), ep_lengths=np.array(lengths, int), ep_ids=ep_ids,
        tasks=tasks, info=info, custom=custom,
    )


# --------------------------------------------------------------------------------------
# phase / subtask segmentation
# --------------------------------------------------------------------------------------
def build_phases(fr: Frames, args) -> tuple[np.ndarray, dict[int, list[str]]]:
    """Return (phase_id per frame, labels). Tries, in order:
       1. an explicit phases JSON
       2. a custom per-frame column (--phase-column)
       3. task_index changing *within* an episode (subtask-labelled data!)
       4. uniform split into --n-phases by normalised episode time (diagnostic only)
    """
    n = fr.n
    phase = np.zeros(n, dtype=np.int64)

    if args.phases_json:
        with open(args.phases_json) as f:
            spec = json.load(f)
        labels = {}
        for ep_s, segs in spec.items():
            e = int(ep_s)
            lo = fr.ep_starts[np.searchsorted(fr.ep_ids, e)]
            for pid, seg in enumerate(segs):
                a, b = int(seg[0]), int(seg[1])
                lab = seg[2] if len(seg) > 2 else f"p{pid}"
                m = (fr.episode_index == e) & (fr.frame_index >= a) & (fr.frame_index < b)
                phase[m] = pid
                labels[pid] = lab
        return phase, labels

    col = args.phase_column
    if col and col in fr.custom:
        raw = fr.custom[col].reshape(-1)
        uniq = {v: i for i, v in enumerate(sorted(set(raw.tolist())))}
        phase = np.array([uniq[v] for v in raw.tolist()], dtype=np.int64)
        return phase, {i: str(v) for v, i in uniq.items()}

    if fr.task_index is not None and not args.no_auto_subtask:
        # a task change inside one episode means the data is already sub-task segmented
        multi = 0
        for s, L in zip(fr.ep_starts, fr.ep_lengths):
            if len(np.unique(fr.task_index[s:s + L])) > 1:
                multi += 1
        if multi > 0:
            print(f"  (auto) detected subtask segmentation via task_index in {multi} episodes")
            uniq = {v: i for i, v in enumerate(sorted(set(fr.task_index.tolist())))}
            phase = np.array([uniq[v] for v in fr.task_index.tolist()], dtype=np.int64)
            labs = {i: fr.tasks.get(v, f"task{v}") for v, i in uniq.items()}
            return phase, labs

    if args.n_phases and args.n_phases > 1:
        k = args.n_phases
        for s, L in zip(fr.ep_starts, fr.ep_lengths):
            t = fr.frame_index[s:s + L] / max(L - 1, 1)
            phase[s:s + L] = np.clip((t * k).astype(int), 0, k - 1)
        return phase, {i: f"time-quartile-{i}" for i in range(k)}

    return phase * 0, {0: "whole-episode (no phase info)"}


# --------------------------------------------------------------------------------------
# analyses
# --------------------------------------------------------------------------------------
def sec_meta(fr: Frames, args) -> None:
    hr("0. DATASET OVERVIEW")
    print(f"  fps                 : {fr.fps}")
    print(f"  robot_type          : {fr.info.get('robot_type')}")
    print(f"  codebase_version    : {fr.info.get('codebase_version')}")
    print(f"  episodes            : {len(fr.ep_ids)}")
    print(f"  frames              : {fr.n}")
    print(f"  action dim          : {fr.action.shape[1]}")
    print(f"  state dim           : {fr.state.shape[1] if fr.state is not None else 'NONE'}")
    if fr.fps:
        print(f"  episode length      : mean {fr.ep_lengths.mean():.1f} frames "
              f"= {fr.ep_lengths.mean() / fr.fps:.2f} s   (min {fr.ep_lengths.min()}, max {fr.ep_lengths.max()})")
    feats = fr.info.get("features", {})
    a_names = feats.get("action", {}).get("names")
    s_names = feats.get("observation.state", {}).get("names")
    if a_names:
        print(f"  action names        : {a_names}")
    if s_names:
        print(f"  state names         : {s_names}")
    print(f"  chunk size under test: H={args.chunk_size}"
          + (f"  ({args.chunk_size / fr.fps:.2f} s at {fr.fps} fps)" if fr.fps else ""))


def sec_state(fr: Frames) -> None:
    hr("1. PROPRIOCEPTIVE STATE SANITY   (a dead state channel => the policy is blind to phase)")
    if fr.state is None:
        print("  !! NO observation.state COLUMN. The policy has no proprioception at all.")
        print("     pi0.5 feeds the state as discrete tokens into the VLM; without it the")
        print("     action expert must infer the phase from vision alone.")
        return
    s = fr.state
    std = s.std(axis=0)
    lo, hi = s.min(axis=0), s.max(axis=0)
    names = fr.info.get("features", {}).get("observation.state", {}).get("names") or [f"d{i}" for i in range(s.shape[1])]
    print(f"  {'dim':<18}{'min':>12}{'max':>12}{'mean':>12}{'std':>12}   note")
    dead = []
    for i in range(s.shape[1]):
        note = ""
        if std[i] < 1e-6:
            note = "CONSTANT  <-- dead channel"
            dead.append(i)
        elif np.all(np.abs(s[:, i]) < 1e-6):
            note = "ALL ZERO  <-- dead channel"
            dead.append(i)
        print(f"  {str(names[i]):<18}{lo[i]:>12.4f}{hi[i]:>12.4f}{s[:, i].mean():>12.4f}{std[i]:>12.4f}   {note}")
    n_nan = int(np.isnan(s).sum())
    flag(n_nan == 0, f"NaNs in state: {n_nan}")
    flag(not dead, f"dead state dims: {dead if dead else 'none'}", ok="OK", bad="!!")
    if dead:
        print(f"     -> {len(dead)}/{s.shape[1]} state dims carry NO information.")
        print("        With pi0.5's discrete state tokenisation those dims become constant")
        print("        tokens; if enough dims are dead the phase is unidentifiable.")


def sec_action(fr: Frames, args) -> None:
    hr("2. ACTION SANITY + DELTA-vs-ABSOLUTE CONVENTION")
    a = fr.action
    print(f"  NaNs in action: {int(np.isnan(a).sum())}")
    lo, hi = np.percentile(a, 1, axis=0), np.percentile(a, 99, axis=0)
    print(f"  {'dim':>4}{'q01':>12}{'q99':>12}{'std':>12}{'|a|==0 frac':>14}")
    zero_frac = []
    for i in range(a.shape[1]):
        zf = float(np.mean(np.abs(a[:, i]) < 1e-6))
        zero_frac.append(zf)
        print(f"  {i:>4}{lo[i]:>12.4f}{hi[i]:>12.4f}{a[:, i].std():>12.4f}{zf:>14.3f}")
    print(f"  overall fraction of exactly-zero action entries: {np.mean(np.abs(a) < 1e-6):.3f}")
    print("     (a large value means long idle / dwell stretches dominate the target distribution)")

    if fr.state is None:
        return
    sub("delta vs absolute (heuristic: which correlates better with the *next* state)")
    ds = min(a.shape[1], fr.state.shape[1])
    r_delta, r_abs = [], []
    for s0, L in zip(fr.ep_starts, fr.ep_lengths):
        if L < 3:
            continue
        sl = slice(s0, s0 + L - 1)
        dstate = fr.state[s0 + 1:s0 + L, :ds] - fr.state[s0:s0 + L - 1, :ds]
        for d in range(ds):
            r_delta.append(corr(a[sl, d], dstate[:, d]))
            r_abs.append(corr(a[sl, d], fr.state[s0 + 1:s0 + L, d]))
    if r_delta:
        md, ma = float(np.nanmean(np.abs(r_delta))), float(np.nanmean(np.abs(r_abs)))
        print(f"  mean |corr(action_t, state_(t+1) - state_t)| = {md:.3f}   <- DELTA actions")
        print(f"  mean |corr(action_t, state_(t+1))           | = {ma:.3f}   <- ABSOLUTE actions")
        if md > ma * 1.25:
            print("  => data looks like DELTA (relative) actions.")
            print("     Check that the checkpoint's normalisation stats were computed on YOUR")
            print("     dataset, and that the delta is taken w.r.t. the same reference frame")
            print("     (t vs t+1, same joint ordering) as the pretrained config.")
        elif ma > md * 1.25:
            print("  => data looks like ABSOLUTE joint/task-space actions.")
        else:
            print("  => inconclusive; verify by hand on one episode.")
    print("  NOTE: pi0/pi0.5 normalise with per-dataset q01/q99 quantiles. Reusing")
    print("        pretrained stats on a new embodiment silently squashes small motions")
    print("        into the middle of the range -> the policy looks frozen.")


def sec_episodes(fr: Frames, args) -> None:
    hr("3. EPISODE LENGTHS & CHUNK TARGET VALIDITY   (padded chunk targets = broken supervision)")
    L = fr.ep_lengths
    print(f"  lengths: min {L.min()}  p25 {np.percentile(L, 25):.0f}  median {np.median(L):.0f} "
          f" p75 {np.percentile(L, 75):.0f}  max {L.max()}")
    H = args.chunk_size
    vf = []
    for s, ln in zip(fr.ep_starts, L):
        for f in range(ln):
            vf.append(min(H, ln - f) / H)
    vf = np.array(vf) if vf else np.zeros(fr.n)
    print(f"  chunk horizon H={H}, mean valid fraction of each chunk target = {vf.mean():.3f}")
    print(f"  frames whose chunk is >20% padding: {np.mean(vf < 0.8):.1%}")
    print(f"  frames whose chunk is >50% padding: {np.mean(vf < 0.5):.1%}   <- these supervise garbage")
    flag(vf.mean() > 0.9, f"mean chunk validity {vf.mean():.3f} (>0.90 desirable)")
    if vf.mean() <= 0.9:
        print("     -> The last H frames of every episode have partially invalid targets.")
        print("        Verify (a) that your loader MASKS the flow-matching loss on padded")
        print("        steps, and (b) what value it pads with (repeating the last action is")
        print("        far less harmful than zeros, which teach 'stop moving').")
        print(f"        With episodes of ~{int(np.median(L))} frames and H={H}, "
              f"{1 - vf.mean():.0%} of supervised steps are padding.")
    print("\n  fraction of supervised chunk steps that are IN-RANGE (not padding), by chunk index k:")
    curve = np.array([np.mean([(f + k) < ln for ln in L for f in range(ln)]) for k in range(H)])
    print("    k=0 " + sparkline(curve) + f" k={H - 1}")
    print(f"    k=0: {curve[0]:.3f}   k={H // 2}: {curve[H // 2]:.3f}   k={H - 1}: {curve[-1]:.3f}")
    if curve[0] < 0.98:
        print("    -> even k=0 has padding: some frames sit at the very end of an episode.")


def sec_idle(fr: Frames, args) -> None:
    hr("4. IDLE / DWELL FRAMES   ('at the start state, do nothing' is a fixed point)")
    mag = action_magnitude(fr.action)
    idle = mag < args.idle_thresh
    print(f"  idle = ||a_t|| < {args.idle_thresh} x p99(||a||)   ->  overall idle frames: {idle.mean():.1%}")

    head = np.zeros(fr.n, bool)
    for s, ln in zip(fr.ep_starts, fr.ep_lengths):
        head[s:s + min(args.head_frames, ln)] = True
    h_frac = idle[head].mean() if head.any() else 0.0
    b_frac = idle[~head].mean() if (~head).any() else 0.0
    print(f"  first {args.head_frames} frames of each episode : idle {h_frac:.1%}")
    print(f"  all other frames              : idle {b_frac:.1%}")
    if b_frac > 0:
        print(f"  ratio head/rest = {h_frac / max(b_frac, EPS):.2f}x")
    contaminated = (h_frac > max(2 * b_frac, 0.10)) and (h_frac > b_frac + 0.05)
    flag(not contaminated,
         (f"episode-head idle contamination is low (head {h_frac:.1%} vs rest {b_frac:.1%})"
          if not contaminated else
          f"EPISODE-HEAD IDLE CONTAMINATION (head {h_frac:.1%} vs rest {b_frac:.1%})"))
    if contaminated:
        print("     -> Every episode starts with a stretch of near-zero actions (operator")
        print("        starts recording before touching the controller). The policy therefore")
        print("        learns 'at the reset state, DO NOTHING', which is the single most")
        print("        common cause of 'it only replays the first motion / it stalls'.")
        print(f"        Fix: drop or down-weight the first ~{args.head_frames} frames of each")
        print("        episode (or start recording only once motion begins).")

    sub("mean normalised |action| vs normalised episode time")
    nb = 24
    prof = np.zeros(nb)
    cnt = np.zeros(nb)
    for s, ln in zip(fr.ep_starts, fr.ep_lengths):
        t = (fr.frame_index[s:s + ln] / max(ln - 1, 1) * (nb - 1)).round().astype(int)
        for b in range(nb):
            m = (t == b) & (fr.frame_index[s:s + ln] > 0)
            if m.any():
                prof[b] += mag[s:s + ln][m].mean()
                cnt[b] += 1
    prof = prof / np.maximum(cnt, 1)
    print("   t=0.0 " + sparkline(prof) + " t=1.0")
    print(f"   max/min of profile = {prof.max() / max(prof.min(), EPS):.2f}x")
    if prof.max() / max(prof.min(), EPS) > 3:
        print("     -> Motion magnitude is very unevenly distributed over the episode.")
        print("        The low-motion stretch is over-represented in the loss; the")
        print("        high-motion stretch (usually the actual task phases) is starved.")
        print("        => rescale sampling per phase (see section 8), do NOT resample by")
        print("           action value.")


def sec_alias(fr: Frames, args) -> dict:
    hr("5. STATE ALIASING / CONDITIONAL MULTIMODALITY   <-- the core test")
    print("  For each frame we find its K nearest neighbours in proprioceptive state space.")
    print("  If states that look identical require DIFFERENT actions, no amount of")
    print("  balancing fixes it: flow matching averages the modes and the robot stalls.")
    print("  A low R^2 for 'state -> action' means the phase information is NOT in the state.")

    if fr.state is None:
        print("  skipped (no state column). Repeat this test on VISUAL features: encode the")
        print("  camera images with a frozen VLM/DINOv2 and run the same kNN analysis there.")
        return {"r2_now": float("nan"), "score": np.zeros(fr.n), "ts_mean": float("nan"),
                "near_var": float("nan"), "aliased": False, "n_flagged": 0}

    Xn, _, _ = robust_norm(fr.state)
    An, _, _ = robust_norm(fr.action)
    n = fr.n
    rng = np.random.default_rng(0)
    S = min(args.subsample, n)
    idx = np.sort(rng.choice(n, S, replace=False))
    X, A = Xn[idx], An[idx]

    t_norm = np.zeros(n)
    for s, ln in zip(fr.ep_starts, fr.ep_lengths):
        t_norm[s:s + ln] = fr.frame_index[s:s + ln] / max(ln - 1, 1)
    T = t_norm[idx]

    K = min(args.knn, S - 1)
    dk = np.zeros(S)      # distance to K-th neighbour
    av = np.zeros(S)      # mean conditional action variance over the neighbourhood
    ts = np.zeros(S)      # spread of normalised episode time over the neighbourhood
    B = 512
    for i0 in range(0, S, B):
        i1 = min(i0 + B, S)
        d2 = ((X[i0:i1, None, :] - X[None, :, :]) ** 2).sum(-1)
        d2[np.arange(i1 - i0), np.arange(i0, i1)] = np.inf
        nn = np.argpartition(d2, K, axis=1)[:, :K]
        dk[i0:i1] = np.sqrt(np.take_along_axis(d2, nn[:, -1:], 1)).ravel()
        av[i0:i1] = A[nn].var(axis=1).mean(axis=1)
        ts[i0:i1] = T[nn].std(axis=1)

    d_med = float(np.median(dk))
    print(f"  sampled {S} frames, K={K} neighbours")
    print(f"  median distance to K-th neighbour (normalised state units): {d_med:.4f}")
    print(f"  mean neighbourhood action variance: {av.mean():.4f}")
    print(f"  mean neighbourhood episode-time spread (std, 0..1): {ts.mean():.4f}")

    # per-frame alias score: neighbours that are visually/state-wise indistinguishable but
    # occur at very different points of the episode => the phase is not identifiable
    a_glob = An.var(axis=0).mean()
    per_frame_var = av
    aliased_frac = float(np.mean((ts > 0.15) & (per_frame_var > 0.4 * a_glob)))
    print(f"  global action variance (all frames)      : {a_glob:.4f}")
    print(f"  frames whose near neighbours span >0.15 of the episode AND ask for")
    print(f"  materially different actions             : {aliased_frac:.1%}")

    sub("conditional action variance vs state distance  (should DROP as distance -> 0)")
    edges = [0, .25, .5, 1, 2, 4, 8, np.inf]
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (dk >= lo * d_med) & (dk < hi * d_med)
        if m.sum() >= 10:
            rows.append((f"{lo:g}-{hi:g}x d_med", int(m.sum()), float(av[m].mean()), float(ts[m].mean())))
    print(f"  {'distance bin':<16}{'n':>8}{'action var':>14}{'time spread':>14}")
    for lab, c, v, t in rows:
        print(f"  {lab:<16}{c:>8}{v:>14.4f}{t:>14.4f}")
    near_var = rows[0][2] if rows else float("nan")
    far_var = rows[-1][2] if rows else float("nan")
    ratio = far_var / max(near_var, EPS) if rows else float("nan")
    print(f"  variance ratio far/near = {ratio:.2f}x")
    print("     (<1.5x means the required action does NOT become more predictable as the")
    print("      states get closer -- the classic signature of an aliased phase)")

    ts_mean = float(ts.mean())
    aliased = (ts_mean > 0.10) or (aliased_frac > 0.15)
    if ts_mean > 0.10:
        print(f"  !! States RECUR at very different points of the episode (mean neighbour time")
        print(f"     spread {ts_mean:.3f}). The same observation occurs in multiple phases.")
        print("     => The phase MUST be supplied as an explicit input (sub-task label /")
        print("        instruction change / phase token). A flow-matching action expert")
        print("        cannot represent 'do A here in phase 1 and B here in phase 3': it")
        print("        regresses to the mean of A and B, which the robot shows as stalling")
        print("        or as replaying only the first motion.")
    elif aliased_frac > 0.15:
        print(f"  !  {aliased_frac:.1%} of frames have near neighbours demanding materially")
        print("     different actions without a large time spread: genuinely multimodal")
        print("     (stochastic human demos), or unresolved near-aliasing.")

    sub("how much does the state tell us about the action?  (ridge probe, held-out episodes)")
    r2_now = ridge_r2(Xn, An, fr, lag=0)
    r2_mid = ridge_r2(Xn, An, fr, lag=min(args.chunk_size - 1, max(1, args.chunk_size // 2)))
    print(f"  state_t -> action_t         R^2 = {r2_now:+.3f}")
    print(f"  state_t -> action_(t+{min(args.chunk_size - 1, max(1, args.chunk_size // 2))})      R^2 = {r2_mid:+.3f}")
    print("  (R^2 is a coarse indicator: if only part of the chain is aliased it is diluted.")
    print("   The neighbourhood time-spread detector above is the primary test.)")
    if r2_now < 0.15:
        print("  !! The state explains almost none of the action variance.")
        print("     => The phase information is missing from the input. Sub-task labels /")
        print("        phase conditioning / instruction changes are mandatory; re-sampling")
        print("        weights cannot help.")
    elif r2_now > 0.5:
        print("  -> The state is informative. If the trained policy still ignores it, the")
        print("     fault is on the model/training side (dead state channel in the")
        print("     checkpoint, wrong normalisation stats, frozen VLM, LR too high, or")
        print("     chunk targets broken). Run diag_policy.py for the ablation test.")

    # per-frame alias score, used for the report and for weight emission
    score = np.zeros(n)
    score[idx] = ts
    return {"r2_now": r2_now, "r2_mid": r2_mid, "score": score, "ts_mean": ts_mean,
            "near_var": float(near_var), "far_var": float(far_var), "var_ratio": float(ratio),
            "aliased_frac": aliased_frac, "aliased": bool(aliased), "a_glob": float(a_glob)}


def ridge_r2(Xn: np.ndarray, An: np.ndarray, fr: Frames, lag: int = 0) -> float:
    """Fit ridge state -> action with a lagged target, train on early episodes, test on late ones."""
    n = fr.n
    src = np.arange(n)
    tgt = src + lag
    valid = np.zeros(n, bool)
    for s, ln in zip(fr.ep_starts, fr.ep_lengths):
        valid[s:s + max(ln - lag, 0)] = True
    src, tgt = src[valid], tgt[valid]
    if src.size < 200:
        return float("nan")
    n_ep = len(fr.ep_ids)
    cut = max(1, int(n_ep * 0.8))
    train_eps = set(fr.ep_ids[:cut].tolist())
    is_tr = np.array([fr.episode_index[t] in train_eps for t in src])
    if is_tr.sum() < 100 or (~is_tr).sum() < 50:
        is_tr = np.arange(src.size) < src.size * 0.8
    X = np.concatenate([Xn[src], np.ones((src.size, 1))], axis=1)
    Y = An[tgt]
    Xtr, Ytr = X[is_tr], Y[is_tr]
    Xte, Yte = X[~is_tr], Y[~is_tr]
    lam = 1e-3 * Xtr.shape[0]
    A = Xtr.T @ Xtr + lam * np.eye(X.shape[1])
    try:
        W = np.linalg.solve(A, Xtr.T @ Ytr)
    except np.linalg.LinAlgError:
        return float("nan")
    pred = Xte @ W
    sse = ((Yte - pred) ** 2).sum()
    sst = ((Yte - Yte.mean(axis=0)) ** 2).sum()
    return float(1 - sse / max(sst, EPS))


def sec_phases(fr: Frames, args, phase: np.ndarray, labels: dict) -> None:
    hr("6. PHASE / SUBTASK BALANCE   (this is the 'uniform distribution' that actually matters)")
    ids = np.unique(phase)
    print(f"  {len(ids)} phase(s): {[labels.get(int(i), str(i)) for i in ids]}")
    print(f"  {'phase':<26}{'frames':>9}{'share':>9}{'traj.':>8}{'frames/traj':>13}{'idle':>8}")
    mag = action_magnitude(fr.action)
    rows = []
    for p in ids:
        m = phase == p
        cnt = int(m.sum())
        eps = 0
        for s, ln in zip(fr.ep_starts, fr.ep_lengths):
            if (phase[s:s + ln] == p).any():
                eps += 1
        idle = float((mag[m] < args.idle_thresh).mean()) if cnt else 0.0
        rows.append((int(p), labels.get(int(p), str(p)), cnt, cnt / fr.n, eps, cnt / max(eps, 1), idle))
        print(f"  {str(labels.get(int(p), p))[:25]:<26}{cnt:>9}{cnt / fr.n:>9.1%}{eps:>8}"
              f"{cnt / max(eps, 1):>13.1f}{idle:>8.1%}")
    shares = np.array([r[3] for r in rows])
    if len(rows) > 1:
        print(f"\n  frame-count imbalance max/min = {shares.max() / max(shares.min(), EPS):.2f}x")
        tr = np.array([r[4] for r in rows])
        print(f"  distinct-trajectory imbalance  = {tr.max() / max(tr.min(), EPS):.2f}x  "
              f"(counts={tr.tolist()})")
        print("     State COVERAGE is driven by the number of distinct trajectories, not by")
        print("     frame counts. Duplicating a rare phase's frames adds no new states;")
        print("     collecting more independent demonstrations of it does.")
        if (tr.min() < 30).any():
            print(f"  !! the sparsest phase has only {tr.min()} trajectories; aim for >=30-50")
            print("     independent trajectories per sub-task, with object/pose randomisation.")


def sec_weights(fr: Frames, args, phase: np.ndarray, alias_score: np.ndarray, r2: float) -> None:
    hr("7. SUGGESTED SAMPLING WEIGHTS   (stratified, NOT action-histogram flattening)")
    n = fr.n
    w = np.ones(n)
    ids, counts = np.unique(phase, return_counts=True)
    for p, c in zip(ids, counts):
        if len(ids) > 1:
            w[phase == p] = n / (len(ids) * c)

    n_bound = 0
    if args.boundary_k > 0 and len(ids) > 1:
        for s, ln in zip(fr.ep_starts, fr.ep_lengths):
            seg = phase[s:s + ln]
            chg = np.flatnonzero(np.diff(seg) != 0)
            for c in chg:
                lo = max(0, c + 1 - args.boundary_k)
                hi = min(ln, c + 1 + args.boundary_k)
                w[s + lo:s + hi] *= args.boundary_boost
                n_bound += hi - lo

    if args.drop_head_frames > 0:
        m = np.zeros(n, bool)
        for s, ln in zip(fr.ep_starts, fr.ep_lengths):
            m[s:s + min(args.drop_head_frames, ln)] = True
        w[m] = 0.0
        print(f"  zeroed the first {args.drop_head_frames} frames of each episode "
              f"({m.mean():.1%} of the dataset)")

    w = np.clip(w, 0, args.max_weight_ratio)
    w = w / max(w.mean(), EPS)
    print(f"  base = per-phase inverse frequency  (max/min before clip = "
          f"{np.max(n / (len(ids) * counts)) / max(np.min(n / (len(ids) * counts)), EPS):.2f}x)")
    print(f"  boundary boost x{args.boundary_boost} within +-{args.boundary_k} frames of a "
          f"phase switch  ({n_bound} frames touched)")
    print(f"  final weights: min {w.min():.3f}  mean {w.mean():.3f}  max {w.max():.3f}")
    print("  Effective epochs per phase (before / after):")
    for p, c in zip(ids, counts):
        before = c / n
        after = w[phase == p].sum() / w.sum()
        print(f"    {str(labels_global.get(int(p), p))[:24]:<26} {before:>7.1%} -> {after:>7.1%}")

    eff = float((w.sum() ** 2) / max((w ** 2).sum(), EPS))
    print(f"  effective sample size = {eff:.0f} of {n} frames ({eff / n:.1%})")
    if eff / n < 0.5:
        print("  !! heavy reweighting: consider collecting data instead of reweighting.")

    if args.emit_weights:
        np.save(args.emit_weights, w.astype(np.float32))
        print(f"  wrote per-frame weights -> {args.emit_weights}  (aligned with the dataset 'index' column)")
    if args.drop_head_frames > 0 and args.emit_mask:
        np.save(args.emit_mask, (w > 0).astype(np.uint8))
        print(f"  wrote keep-mask        -> {args.emit_mask}")

    sub("how to consume these weights")
    print("  openpi / lerobot do not accept per-frame weights out of the box. Two options:")
    print("  1. Materialise the effect offline: build a resampled dataset with the")
    print("     multinomial counts implied by w (use --emit-weights and sample with")
    print("     probability w/sum(w)), writing a NEW LeRobot dataset. Simple, works with")
    print("     any training loop; keep the resample factor modest (<=2x the mean).")
    print("  2. Add a weighted loss: in openpi's Pi0 loss, multiply the per-sample flow-")
    print("     matching loss by a weight tensor loaded from this file before the mean.")
    print("  Do NOT flatten the action-value histogram itself: it destroys the (o,a)")
    print("  pairing and teaches actions that are dynamically impossible.")


labels_global: dict = {}
LAST: dict = {}
_CHECK_OK = [True]


def check(cond, msg: str) -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")
    _CHECK_OK[0] &= bool(cond)


def sec_verdict(alias: dict) -> None:
    hr("8. VERDICT / NEXT ACTION")
    r2 = alias.get("r2_now", float("nan"))
    if alias.get("aliased"):
        print("  *** ALIASING CONFIRMED by the state-space test (section 5). ***")
        print("      The same observation appears in more than one phase of the chain.")
        print("      No reweighting can fix this. Fix the CONDITIONING, not the balance:")
        print("        a) split every episode into sub-task segments and label each frame")
        print("           with its CURRENT sub-task; keep the episodes intact;")
        print("        b) make the sub-task label REACH the policy. Two routes, and they")
        print("           live in DIFFERENT codebases -- check which one you are on:")
        print("           - LeRobot implements pi0.5's joint subtask conditioning. Store")
        print("             labels in the `language_persistent` / `language_events` columns,")
        print("             train with `recipes/subtask_joint.yaml`, and enable")
        print("             `--policy.joint_subtask_conditioning=true` at inference. The docs")
        print("             state this matches the joint setup from the pi0.5 paper.")
        print("           - openpi (Physical Intelligence's release) has NO subtask branch:")
        print("             a search for 'subtask' across the repo returns nothing and the")
        print("             README documents a flow-matching head only. There, the route is")
        print("             the instruction string -- the action expert is conditioned on the")
        print("             prompt, so put the CURRENT sub-task in it rather than one global")
        print("             sentence for the whole chain.")
        print("        c) only then apply per-phase sampling weights (section 7).")
        print()
    print("  Read the sections above in this order and stop at the first !! :")
    print("   1. dead state dims / no state column        -> fix the data pipeline first")
    print("   2. episode-head idle frames                 -> trim, retrain, re-evaluate")
    print("   3. chunk target validity <= 0.9             -> fix masking/padding")
    r2s = "n/a" if (r2 is None or np.isnan(r2)) else f"{r2:+.3f}"
    print(f"   4. state -> action R^2 < 0.15   (yours: {r2s})  -> ALIASING: add per-frame")
    print("      sub-task labels, condition on them, and keep the episodes intact")
    print("   5. R^2 high but the policy still ignores state -> run diag_policy.py")
    print("      (conditional-collapse / state-ablation test)")
    print("\n  On 'separating chained tasks': keep the episodes intact. Label the")
    print("  sub-task segments and sample per-phase. Cutting the chain into K independent")
    print("  datasets gives each sub-policy an entrance-state distribution that no longer")
    print("  matches its training distribution, which trades one failure for another.")


# --------------------------------------------------------------------------------------
# self-test: build a synthetic LeRobot dataset with KNOWN pathologies and verify the report
# --------------------------------------------------------------------------------------
def write_synthetic(root: str, n_ep: int = 24, length: int = 150, ds: int = 7, fps: int = 30,
                    alias: bool = True, idle_head: bool = True) -> None:
    """Chained 3-phase task with, when `alias`, deliberate state aliasing between phase 0
    and phase 2 (identical state trajectory, different actions), plus idle episode heads
    and one constant (dead) state dimension."""
    os.makedirs(os.path.join(root, "meta", "episodes", "chunk-000"), exist_ok=True)
    os.makedirs(os.path.join(root, "data", "chunk-000"), exist_ok=True)
    rng = np.random.default_rng(7)
    a_names = [f"j{i}" for i in range(ds - 1)] + ["gripper"]
    info = {
        "codebase_version": "v2.1", "robot_type": "synthetic", "total_episodes": n_ep,
        "total_frames": n_ep * length, "total_tasks": 1, "total_videos": 0, "total_chunks": 1,
        "chunks_size": 1000, "fps": fps, "splits": {"train": f"0:{n_ep}"},
        "data_path": "data/chunk-{episode_chunk:03d}/episode_{episode_index:06d}.parquet",
        "video_path": "videos/chunk-{episode_chunk:03d}/{video_key}/episode_{episode_index:06d}.mp4",
        "features": {
            "action": {"dtype": "float32", "shape": [ds], "names": a_names},
            "observation.state": {"dtype": "float32", "shape": [ds], "names": a_names},
            "episode_index": {"dtype": "int64", "shape": [1], "names": None},
            "frame_index": {"dtype": "int64", "shape": [1], "names": None},
            "index": {"dtype": "int64", "shape": [1], "names": None},
            "task_index": {"dtype": "int64", "shape": [1], "names": None},
            "timestamp": {"dtype": "float32", "shape": [1], "names": None},
        },
    }
    with open(os.path.join(root, "meta", "info.json"), "w") as f:
        json.dump(info, f, indent=2)
    with open(os.path.join(root, "meta", "tasks.jsonl"), "w") as f:
        f.write(json.dumps({"task_index": 0, "task": "pick the block and put it in the box then close the lid"}) + "\n")

    ep_rows, gidx = [], 0
    for e in range(n_ep):
        seg = length // 3
        state = np.zeros((length, ds))
        act = np.zeros((length, ds))
        s = np.array([0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 1.0]) + rng.normal(0, 0.01, ds)
        s_start = s.copy()
        phase0_states = []                                # the phase-0 state trajectory

        def jitter(sig):
            return rng.normal(0, sig, ds)

        for t in range(length):
            if idle_head and t < 8:                       # operator not moving yet
                a = jitter(0.0005)
            elif t < seg:                                 # phase 0: approach  -> +x
                a = np.array([0.06, 0.0, -0.01, 0, 0, 0, 0.0]) + jitter(0.004)
            elif t < 2 * seg:                             # phase 1: lift & carry -> +z
                a = np.array([0.0, 0.0, 0.05, 0, 0, 0, 0.0]) + jitter(0.004)
            else:                                         # phase 2: place & close -> gripper
                a = np.array([0.0, 0.0, -0.04, 0, 0, 0, -0.05]) + jitter(0.004)
            act[t] = a
            state[t] = s
            if t < seg:
                phase0_states.append(s.copy())
            s = s + a
            if alias and t == 2 * seg - 1:
                # ALIASING: phase 2 restarts from the EXACT phase-0 initial state and then
                # re-walks the phase-0 state trajectory, while requiring different actions.
                s = s_start.copy()
        if alias:
            for i in range(length - 2 * seg):
                state[2 * seg + i] = phase0_states[min(i, len(phase0_states) - 1)]
        state[:, 5] = 0.0                                 # dead state dim
        act[:, 5] = 0.0
        ep_rows.append({"episode_index": e, "length": length, "task_index": 0})
        tbl = pa.table({
            "action": pa.array(act.astype(np.float32).tolist(), type=pa.list_(pa.float32(), ds)),
            "observation.state": pa.array(state.astype(np.float32).tolist(), type=pa.list_(pa.float32(), ds)),
            "episode_index": pa.array(np.full(length, e), type=pa.int64()),
            "frame_index": pa.array(np.arange(length), type=pa.int64()),
            "index": pa.array(np.arange(gidx, gidx + length), type=pa.int64()),
            "task_index": pa.array(np.zeros(length), type=pa.int64()),
            "timestamp": pa.array(np.arange(length) / fps, type=pa.float32()),
        })
        pq.write_table(tbl, os.path.join(root, "data", "chunk-000", f"episode_{e:06d}.parquet"))
        gidx += length

    meta = pa.table({
        "episode_index": pa.array([r["episode_index"] for r in ep_rows], type=pa.int64()),
        "length": pa.array([r["length"] for r in ep_rows], type=pa.int64()),
        "dataset_from_index": pa.array(np.arange(n_ep) * length, type=pa.int64()),
        "dataset_to_index": pa.array((np.arange(n_ep) + 1) * length, type=pa.int64()),
    })
    pq.write_table(meta, os.path.join(root, "meta", "episodes", "chunk-000", "file-000.parquet"))


def selftest(args) -> int:
    hr("SELF-TEST: synthetic chained-task dataset with known pathologies")
    tmp = tempfile.mkdtemp(prefix="vla_diag_selftest_")
    print(f"  writing synthetic LeRobot v2.1 dataset to {tmp}")
    write_synthetic(tmp)
    args.root = tmp
    args.n_phases = 3
    rc = run(args, _selftest=True)
    sub("control: a HEALTHY dataset must NOT trip the aliasing alarm")
    ctl = os.path.join(tmp, "control")
    write_synthetic(ctl, alias=False, idle_head=False)
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fr_c = load_lerobot(ctl)
        pg, pl = build_phases(fr_c, args)
        res_c = sec_alias(fr_c, args)
    check(not res_c["aliased"],
          f"no false positive on the control (time spread {res_c['ts_mean']:.3f}, "
          f"R^2 {res_c['r2_now']:+.3f})")
    check(res_c["ts_mean"] < LAST["alias"]["ts_mean"],
          f"control separation is discriminative "
          f"({res_c['ts_mean']:.3f} < {LAST['alias']['ts_mean']:.3f})")

    sub("explicit --phases-json segmentation + --emit-weights")
    pj = os.path.join(tmp, "phases.json")
    with open(pj, "w") as f:
        json.dump({str(e): [[0, 50, "reach"], [50, 100, "carry"], [100, 150, "place"]]
                   for e in range(24)}, f)
    args.phases_json = pj
    args.emit_weights = os.path.join(tmp, "w.npy")
    args.drop_head_frames = 8
    with contextlib.redirect_stdout(buf):
        fr2 = load_lerobot(tmp)
        ph2, lab2 = build_phases(fr2, args)
        sec_weights(fr2, args, ph2, LAST["alias"]["score"], LAST["alias"]["r2_now"])
    check(len(lab2) == 3 and lab2[0] == "reach", "phases-json labels loaded")
    check(len(np.unique(ph2)) == 3, "phases-json produced 3 segments")
    wfile = np.load(args.emit_weights)
    check(wfile.shape[0] == fr2.n, f"weights written with one entry per frame ({wfile.shape[0]})")
    head_masked = np.zeros(fr2.n, bool)
    for st, ln in zip(fr2.ep_starts, fr2.ep_lengths):
        head_masked[st:st + 8] = True
    check(np.all(wfile[head_masked] == 0.0), "drop-head-frames zeroed the episode heads")

    ok = bool(_CHECK_OK[0]) and rc == 0
    print(f"\n  overall: {'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------
def run(args, _selftest: bool = False) -> int:
    fr = load_lerobot(args.root, extra_columns=[args.phase_column] if args.phase_column else None,
                      max_episodes=args.max_episodes)
    phase, labels = build_phases(fr, args)
    labels_global.clear()
    labels_global.update(labels)

    sec_meta(fr, args)
    sec_state(fr)
    sec_action(fr, args)
    sec_episodes(fr, args)
    sec_idle(fr, args)
    alias = sec_alias(fr, args)
    LAST.update(alias=alias, fr=fr)
    sec_phases(fr, args, phase, labels)
    sec_weights(fr, args, phase, alias["score"], alias["r2_now"])
    sec_verdict(alias)

    if _selftest:
        hr("SELF-TEST: assertions on the synthesised dataset")
        std = fr.state.std(axis=0)
        check(std[5] < 1e-6, "dead state dim 5 detected")
        mag_idle = action_magnitude(fr.action)
        check(std[0] > 1e-3, "live state dims still reported as live")
        mag = mag_idle
        head = np.zeros(fr.n, bool)
        for s, ln in zip(fr.ep_starts, fr.ep_lengths):
            head[s:s + 8] = True
        check(mag[head].mean() < 0.4 * mag[~head].mean(), "episode-head idle stretch detected")
        H = args.chunk_size
        vf = []
        for ln in fr.ep_lengths:
            for f in range(ln):
                vf.append(min(H, ln - f) / H)
        check(np.mean(vf) < 0.95, "chunk padding over episode end detected")
        check(not np.isnan(alias["r2_now"]), "ridge probe produced a finite R^2")
        check(alias["r2_now"] < 0.5,
              f"aliasing degrades state->action R^2 (got {alias['r2_now']:+.3f})")
        check(alias["aliased"], f"aliasing ALARM fired (neighbour time spread {alias['ts_mean']:.3f})")
        check(alias["ts_mean"] > 0.10, "phase recurrence detected in state-space neighbourhoods")
        check(len(np.unique(phase)) == 3, "3 phases reconstructed from --n-phases")
        check(alias["score"].shape[0] == fr.n, "per-frame alias score returned")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="LeRobot dataset diagnostics for chained-task VLA fine-tuning")
    p.add_argument("root", nargs="?", help="path to the LeRobot dataset root")
    p.add_argument("--selftest", action="store_true", help="generate a synthetic dataset and validate this tool")
    p.add_argument("--chunk-size", type=int, default=50, help="action chunk horizon H (pi0.5 default 50)")
    p.add_argument("--n-phases", type=int, default=0, help="assume K equal-length phases per episode")
    p.add_argument("--phases-json", help='explicit segmentation: {"0": [[0,50,"reach"],[50,90,"grasp"]], ...}')
    p.add_argument("--phase-column", help="name of a per-frame phase/subtask column in the dataset")
    p.add_argument("--no-auto-subtask", action="store_true", help="disable task_index-change detection")
    p.add_argument("--subsample", type=int, default=20000, help="frames used for the kNN aliasing test")
    p.add_argument("--knn", type=int, default=16)
    p.add_argument("--idle-thresh", type=float, default=0.05)
    p.add_argument("--head-frames", type=int, default=10, help="frames considered 'episode head'")
    p.add_argument("--drop-head-frames", type=int, default=0, help="zero the weights of these head frames")
    p.add_argument("--boundary-k", type=int, default=8, help="frames around a phase switch to boost")
    p.add_argument("--boundary-boost", type=float, default=2.0)
    p.add_argument("--max-weight-ratio", type=float, default=6.0)
    p.add_argument("--emit-weights", help="write per-frame weights to this .npy path")
    p.add_argument("--emit-mask", help="write the keep-mask to this .npy path")
    p.add_argument("--max-episodes", type=int, default=None)
    args = p.parse_args()

    if args.selftest:
        return selftest(args)
    if not args.root:
        p.print_help()
        return 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
