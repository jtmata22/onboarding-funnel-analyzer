"""Experiment sizing: power, minimum detectable effect, and runtime.

These are the questions that have to be answered *before* an experiment starts:
how many users do we need, what is the smallest effect this test can actually
detect, and how many weeks of traffic is that. Simulation is the right tool for
these — they are questions about the design of the test, not about the data.
"""

import math

import numpy as np
from scipy import stats


def required_sample_size(
    baseline_rate: float,
    relative_mde: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Users needed *per group* to detect a relative lift of `relative_mde`.

    Two-sided test of two independent proportions.
    """
    p1 = baseline_rate
    p2 = baseline_rate * (1 + relative_mde)
    if not (0 < p1 < 1) or not (0 < p2 < 1) or p1 == p2:
        return 0

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    return math.ceil(numerator / (p2 - p1) ** 2)


def detectable_effect(
    baseline_rate: float,
    n_per_group: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Smallest *relative* lift detectable with `n_per_group` users.

    Inverts required_sample_size by bisection, since the treatment rate appears
    in the variance term.
    """
    if n_per_group <= 0 or not (0 < baseline_rate < 1):
        return float("nan")

    lo, hi = 1e-5, (1.0 / baseline_rate) - 1 - 1e-9
    if hi <= lo:
        return float("nan")

    for _ in range(80):
        mid = (lo + hi) / 2
        needed = required_sample_size(baseline_rate, mid, alpha, power)
        if needed > n_per_group:
            lo = mid
        else:
            hi = mid
    return hi


def weeks_required(
    n_per_group: int, weekly_eligible_users: int, traffic_allocation: float = 1.0
) -> float:
    """Weeks of traffic needed to fill both arms."""
    usable = weekly_eligible_users * traffic_allocation
    if usable <= 0:
        return float("inf")
    return (2 * n_per_group) / usable


def achieved_power(
    baseline_rate: float, relative_mde: float, n_per_group: int, alpha: float = 0.05
) -> float:
    """Power actually achieved at a given sample size and true effect."""
    p1 = baseline_rate
    p2 = baseline_rate * (1 + relative_mde)
    if not (0 < p2 < 1) or n_per_group <= 0 or p1 == p2:
        return float("nan")

    se = math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / n_per_group)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    return float(stats.norm.cdf(abs(p2 - p1) / se - z_alpha))


def mde_curve(
    baseline_rate: float,
    weekly_eligible_users: int,
    max_weeks: int = 12,
    alpha: float = 0.05,
    power: float = 0.80,
) -> np.ndarray:
    """(week, detectable relative lift) for weeks 1..max_weeks."""
    rows = []
    for week in range(1, max_weeks + 1):
        n_per_group = int(weekly_eligible_users * week / 2)
        rows.append((week, detectable_effect(baseline_rate, n_per_group, alpha, power)))
    return np.array(rows)
