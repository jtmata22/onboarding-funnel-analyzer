"""Preset experiments, each rigged to demonstrate a specific failure mode.

Every scenario here produces a result that looks clean if you only read the
headline z-test, and falls apart under the right diagnostic. They exist to show
what the verdict engine catches — and why a single p-value is not a decision.
"""

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats


def _build(rows: list) -> pd.DataFrame:
    """rows: (group, segment, week, day, n_users, n_converted)"""
    frames = []
    uid = 0
    for group, segment, week, day, n, k in rows:
        activated = np.zeros(n, dtype=bool)
        activated[:k] = True
        frames.append(
            pd.DataFrame(
                {
                    "user_id": np.arange(uid, uid + n),
                    "group": group,
                    "segment": segment,
                    "week": week,
                    "day": day,
                    "activated": activated,
                }
            )
        )
        uid += n
    return pd.concat(frames, ignore_index=True)


@st.cache_data
def simpsons_paradox() -> dict:
    """Pooled lift is strongly positive; both segments are actually harmed.

    The treatment arm happens to contain far more desktop users, and desktop
    converts much better regardless of arm. The mix — not the change — drives
    the headline number.
    """
    rows = [
        ("Control", "Mobile", 1, 1, 8000, 800),    # 10.0%
        ("Control", "Desktop", 1, 1, 2000, 600),   # 30.0%
        ("Treatment", "Mobile", 1, 1, 2000, 180),  #  9.0%  (worse)
        ("Treatment", "Desktop", 1, 1, 8000, 2240),# 28.0%  (worse)
    ]
    df = _build(rows)
    return {
        "key": "simpsons",
        "title": "Simpson's paradox",
        "setup": (
            "A redesigned signup flow was rolled out. The pooled activation rate "
            "jumped from 14.0% to 24.2% — a +73% relative lift, p < 0.0001."
        ),
        "naive_read": "Huge, highly significant win. Ship it.",
        "the_trap": (
            "The treatment arm is 80% desktop while control is 80% mobile, and "
            "desktop converts ~3x better in both arms. Within mobile the treatment "
            "is worse (10.0% to 9.0%); within desktop it is also worse (30.0% to "
            "28.0%). The change harmed every actual user segment. The pooled lift "
            "is an artifact of the mix."
        ),
        "what_to_check": "Segment breakdown, and the segment mix per arm.",
        "df": df,
    }


@st.cache_data
def novelty_effect() -> dict:
    """Week 1 looks like a decisive win; by week 4 the effect is gone."""
    rows = []
    control_rate = 0.20
    treatment_by_week = [0.30, 0.26, 0.22, 0.195]
    n = 5000
    for week, t_rate in enumerate(treatment_by_week, start=1):
        rows.append(("Control", "All", week, week * 7, n, int(n * control_rate)))
        rows.append(("Treatment", "All", week, week * 7, n, int(n * t_rate)))
    df = _build(rows)
    return {
        "key": "novelty",
        "title": "Novelty effect",
        "setup": (
            "A new onboarding checklist launched. Pooled across four weeks, "
            "activation rose from 20.0% to 24.4% — a +22% lift, p < 0.0001."
        ),
        "naive_read": "Significant and large. Ship it.",
        "the_trap": (
            "The lift is entirely front-loaded. Week 1 was +50%; week 4 is -2.5%. "
            "Users engaged with the checklist because it was new, not because it "
            "works. Pooling across the whole run hides a decaying trend that has "
            "already crossed zero."
        ),
        "what_to_check": "Lift by week, not pooled lift.",
        "df": df,
    }


@st.cache_data
def sample_ratio_mismatch() -> dict:
    """A 52/48 split when it should be 50/50 — the test is invalid."""
    rows = [
        ("Control", "All", 1, 1, 10400, 2080),    # 20.0%
        ("Treatment", "All", 1, 1, 9600, 2208),   # 23.0%
    ]
    df = _build(rows)
    return {
        "key": "srm",
        "title": "Sample ratio mismatch",
        "setup": (
            "An experiment reports activation up from 20.0% to 23.0%, a +15% "
            "relative lift with p < 0.0001 on 20,000 users."
        ),
        "naive_read": "Clean, well-powered win. Ship it.",
        "the_trap": (
            "The arms are 10,400 / 9,600 — a 52/48 split where 50/50 was intended. "
            "Under correct randomisation a split this skewed is essentially "
            "impossible (p < 0.00001). Something is dropping users from the "
            "treatment arm — a redirect failing, a logging gap, a bot filter. "
            "Whoever is missing is probably not missing at random, so the "
            "comparison is broken. The lift is uninterpretable, not wrong-but-close."
        ),
        "what_to_check": "The allocation check, before reading any result.",
        "df": df,
    }


@st.cache_data
def peeking(n_days: int = 28, daily_users_per_arm: int = 180) -> dict:
    """A true null effect that crosses p < 0.05 mid-flight, then reverts.

    Searches seeds for a run that would have looked significant to someone
    checking daily, and is not significant at the planned end date.
    """
    true_rate = 0.20
    chosen = None

    for seed in range(2000):
        rng = np.random.default_rng(seed)
        c = rng.binomial(daily_users_per_arm, true_rate, n_days)
        t = rng.binomial(daily_users_per_arm, true_rate, n_days)

        cum_c, cum_t = np.cumsum(c), np.cumsum(t)
        n_cum = np.arange(1, n_days + 1) * daily_users_per_arm

        p1, p2 = cum_c / n_cum, cum_t / n_cum
        p_pool = (cum_c + cum_t) / (2 * n_cum)
        se = np.sqrt(p_pool * (1 - p_pool) * (2 / n_cum))
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(se > 0, (p2 - p1) / se, 0.0)
        pvals = 2 * (1 - stats.norm.cdf(np.abs(z)))

        # a crossing well into the run is a more honest demonstration than one
        # on day 2, when nobody would have called it anyway
        mid_flight = pvals[6:21] < 0.05
        if mid_flight.any() and pvals[:6].min() >= 0.05 and pvals[-1] > 0.20:
            chosen = (c, t)
            break

    if chosen is None:  # pragma: no cover - search reliably finds a run
        rng = np.random.default_rng(0)
        chosen = (
            rng.binomial(daily_users_per_arm, true_rate, n_days),
            rng.binomial(daily_users_per_arm, true_rate, n_days),
        )

    c, t = chosen

    rows = []
    for day in range(n_days):
        week = day // 7 + 1
        rows.append(
            ("Control", "All", week, day + 1, daily_users_per_arm, int(c[day]))
        )
        rows.append(
            ("Treatment", "All", week, day + 1, daily_users_per_arm, int(t[day]))
        )
    df = _build(rows)

    return {
        "key": "peeking",
        "title": "Peeking",
        "setup": (
            f"A 4-week test with a true effect of exactly zero — both arms convert "
            f"at {true_rate:.0%}. The team checks the dashboard every morning."
        ),
        "naive_read": (
            "At some point mid-flight the p-value dips below 0.05 and the team "
            "declares a winner."
        ),
        "the_trap": (
            "There is no effect at all. Random noise crosses the 0.05 line at "
            "least once in most runs when you look every day; testing repeatedly "
            "drives the false positive rate far above the nominal 5%. By the "
            "planned end date the result is comfortably null. Stopping the moment "
            "a test turns significant is how teams ship nothing."
        ),
        "what_to_check": "The p-value trajectory, and a stopping rule fixed in advance.",
        "df": df,
    }


SCENARIOS = {
    "Simpson's paradox": simpsons_paradox,
    "Novelty effect": novelty_effect,
    "Sample ratio mismatch": sample_ratio_mismatch,
    "Peeking": peeking,
}
