import numpy as np
import matplotlib.pyplot as plt

CORE_NAME = "BETA"
CORE_VERSION = "1.1-beta"

MAX_CONCURRENT = 7  # hard facilities limit: no more than 7 processes active simultaneously

DEFAULT_CONFIG = {
    "cycle_length": 320,
    "resolution": 2400,
    "environment_load": 5.5,
    "base_operator_mass": 22.0,
    "boost_power":  3.0,
    "bg_color": "#361A8B",
    "axis_color": "#FFFFFF",
}




def operator_capacity(t, config):
    base = config["base_operator_mass"]
    boost = config["boost_power"]

    if t < 10:
        return base + boost
    if t < 20:
        progress = (t - 10) / 10.0
        bonus = boost * (1.0 - progress)
        return base + bonus
    return base


def cycle_background(t, config):
    env = config["environment_load"]

    if t < 10:
        return 0.0
    if t < 20:
        progress = (t - 10) / 10.0
        return env * progress
    return env


def visual_wave(t, start, life, amp=1.0):
    y = np.full_like(t, np.nan, dtype=float)
    mask = (t >= start) & (t <= start + life)

    if np.any(mask):
        phase = (t[mask] - start) / life
        y[mask] = amp * np.sin(2 * np.pi * phase)

    return y


def hidden_influence(phase, mass, life):
    phase = np.asarray(phase, dtype=float)

    density = mass / life
    floor_ratio = 1.0 - np.exp(-6.0 * density)
    floor_ratio = np.clip(floor_ratio, 0.08, 0.92)
    floor = mass * floor_ratio

    edge = 0.35 - 0.25 * floor_ratio
    edge = np.clip(edge, 0.05, 0.35)

    infl = np.full_like(phase, floor, dtype=float)

    left = phase < edge
    if np.any(left):
        x = phase[left] / edge
        infl[left] = mass - (mass - floor) * x

    right = phase > (1.0 - edge)
    if np.any(right):
        x = (phase[right] - (1.0 - edge)) / edge
        infl[right] = floor + (mass - floor) * x

    return infl


def process_load_at_time(t, process):
    start = process["start"]
    life = process["life"]
    mass = process["mass"]

    if t < start or t > start + life:
        return 0.0

    phase = (t - start) / life
    return float(hidden_influence(phase, mass, life))


def total_load_at_time(t, processes, config):
    total = cycle_background(t, config)
    for p in processes:
        total += process_load_at_time(t, p)
    return total


def score_start(candidate_process, candidate_start, scheduled_processes, config, dt=1.0):
    temp = dict(candidate_process)
    temp["start"] = candidate_start

    t0 = candidate_start
    t1 = candidate_start + candidate_process["life"]

    if t1 > config["cycle_length"]:
        return np.inf, np.inf, np.inf, np.inf, np.inf

    times = np.arange(t0, t1 + dt, dt)

    loads = []
    overload_sum = 0.0
    overload_points = 0
    concurrent_violation_points = 0

    for t in times:
        load = total_load_at_time(t, scheduled_processes + [temp], config)
        cap = operator_capacity(t, config)
        loads.append(load)

        if load > cap:
            overload_sum += (load - cap)
            overload_points += 1

        # count processes (already scheduled + candidate) active at this moment
        active_count = sum(
            1 for p in scheduled_processes
            if p["start"] <= t <= p["start"] + p["life"]
        ) + 1  # +1 for the candidate itself
        if active_count > MAX_CONCURRENT:
            concurrent_violation_points += (active_count - MAX_CONCURRENT)

    loads = np.array(loads)
    peak_load = float(loads.max())
    mean_load = float(loads.mean())

    overload_penalty = overload_sum * 10000.0
    concurrent_penalty = concurrent_violation_points * 10000.0
    urgency = candidate_process.get("urgency", 0.0)
    delay_penalty = urgency * candidate_start * 20.0

    score = overload_penalty + concurrent_penalty + peak_load * 100.0 + mean_load + delay_penalty
    return score, peak_load, mean_load, overload_points, concurrent_violation_points


def find_best_start(candidate_process, scheduled_processes, config, step=1):
    latest_start = int(config["cycle_length"] - candidate_process["life"])

    if latest_start < 0:
        score, peak, mean, overload_points, concurrent_points = score_start(candidate_process, 0, scheduled_processes, config)
        return 0, score, peak, mean

    safe_candidates = []
    unsafe_best = None

    for start in range(0, int(latest_start) + 1, int(step)):
        score, peak, mean, overload_points, concurrent_points = score_start(
            candidate_process, start, scheduled_processes, config
        )

        row = (start, score, peak, mean, overload_points, concurrent_points)

        if overload_points == 0 and concurrent_points == 0:
            safe_candidates.append(row)

        if unsafe_best is None or score < unsafe_best[1]:
            unsafe_best = row

    if safe_candidates:
        start, score, peak, mean, _, _ = safe_candidates[0]
        return start, score, peak, mean

    if unsafe_best is not None:
        start, score, peak, mean, _, _ = unsafe_best
        return start, score, peak, mean

    score, peak, mean, _, _ = score_start(candidate_process, 0, scheduled_processes, config)
    return 0, score, peak, mean


def build_schedule(processes=None, config=None):
    processes = [dict(p) for p in (processes or DEFAULT_PROCESSES)]
    config = dict(DEFAULT_CONFIG if config is None else config)

    processes_sorted = sorted(
        processes,
        key=lambda p: p["mass"] * p["life"],
        reverse=True
    )

    scheduled = []
    report_lines = []

    for p in processes_sorted:
        best_start, best_score, best_peak, best_mean = find_best_start(
            p, scheduled, config, step=1
        )

        p_scheduled = dict(p)
        p_scheduled["start"] = best_start
        scheduled.append(p_scheduled)

        report_lines.append(
            f'{p["name"]:>16} | life={p["life"]:>3} | mass={p["mass"]:>4.1f} '
            f'| start={best_start:>3} | peak≈{best_peak:>6.2f} | mean≈{best_mean:>6.2f}'
        )

    return scheduled, report_lines, config


def capacity_report(scheduled, config):
    times = np.arange(0, int(config["cycle_length"]) + 1, 1)

    max_active = 0
    worst_load = 0.0
    overloads = []
    concurrent_violations = []

    for t in times:
        active = [
            p for p in scheduled
            if p["start"] <= t <= p["start"] + p["life"]
        ]

        load = total_load_at_time(t, scheduled, config)
        capacity = operator_capacity(t, config)

        max_active = max(max_active, len(active))
        worst_load = max(worst_load, load)

        if load > capacity:
            overloads.append((t, len(active), round(load, 2), round(capacity, 2)))

        if len(active) > MAX_CONCURRENT:
            concurrent_violations.append((t, len(active)))

    return {
        "max_active": max_active,
        "peak_total_load": round(worst_load, 2),
        "base_operator_mass": config["base_operator_mass"],
        "boost_power": config["boost_power"],
        "environment_load": config["environment_load"],
        "overloads": overloads,
        "concurrent_violations": concurrent_violations,
    }


def plot_schedule(scheduled, config, visual_profile="exponential"):
    from profiles import PROFILES, visual_amplitude
    profile = PROFILES[visual_profile]
    print("VISUAL PROFILE:", visual_profile, profile)
    print("scheduled len =", len(scheduled))

    cycle_length = float(config["cycle_length"])
    resolution = int(config["resolution"])

    t = np.linspace(0, cycle_length, resolution)

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor(config["bg_color"])
    ax.set_facecolor(config["bg_color"])

    left_pad = cycle_length * 0.04
    right_pad = cycle_length * 0.04
    ax.set_xlim(-left_pad, cycle_length + right_pad)

    ax.axhline(0, color=config["axis_color"], lw=2)

    for p in scheduled:
        amp = visual_amplitude(p["mass"], profile)
        lw = 2.0        
        y = visual_wave(t, p["start"], p["life"], amp=amp)
        print("AMP TEST:", p["name"], p["mass"], amp)

        ax.plot(
            t, y,
            color=p["color"],
            lw=lw, 
            solid_capstyle="round"
        )

    plt.tight_layout()
    return fig


def run_scheduler(processes):
    scheduled, report_lines, config = build_schedule(processes=processes)
    report = capacity_report(scheduled, config)
    return scheduled, report_lines, report, config
