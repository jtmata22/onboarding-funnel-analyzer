"""Funnel math: step-by-step conversion, drop-off, and significance testing."""

import numpy as np
import pandas as pd
from scipy import stats

from data_loader import FUNNEL_STEPS


def funnel_table(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Users reaching >= each step, and step-over-step conversion / drop-off."""
    sub = df[df["group"] == group]
    n_total = len(sub)

    reached_counts = [
        (sub["furthest_step_idx"] >= i).sum() for i in range(len(FUNNEL_STEPS))
    ]

    table = pd.DataFrame(
        {
            "step": FUNNEL_STEPS,
            "users_reached": reached_counts,
            "pct_of_total": [c / n_total for c in reached_counts],
        }
    )
    table["step_conversion"] = table["users_reached"] / table["users_reached"].shift(1)
    table.loc[0, "step_conversion"] = 1.0
    table["drop_off"] = 1 - table["step_conversion"]
    return table


def activation_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("group")
        .agg(
            n_users=("user_id", "count"),
            activated=("activated", "sum"),
        )
        .assign(activation_rate=lambda d: d["activated"] / d["n_users"])
        .reset_index()
    )


def two_proportion_ztest(df: pd.DataFrame):
    """Z-test comparing Control vs Treatment activation rate."""
    summary = activation_summary(df).set_index("group")
    n1, x1 = summary.loc["Control", ["n_users", "activated"]]
    n2, x2 = summary.loc["Treatment", ["n_users", "activated"]]

    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    lift = (p2 - p1) / p1 if p1 > 0 else float("nan")

    return {
        "control_rate": p1,
        "treatment_rate": p2,
        "absolute_diff": p2 - p1,
        "relative_lift": lift,
        "z_score": z,
        "p_value": p_value,
    }


def step_dropoff_chi2(df: pd.DataFrame, step_idx: int):
    """Chi-square test on step-over-step drop-off between groups at a given step."""
    counts = []
    for group in ("Control", "Treatment"):
        sub = df[df["group"] == group]
        reached_prev = (sub["furthest_step_idx"] >= step_idx - 1).sum()
        reached_here = (sub["furthest_step_idx"] >= step_idx).sum()
        counts.append([reached_here, reached_prev - reached_here])

    chi2, p, _, _ = stats.chi2_contingency(np.array(counts), correction=True)
    return {"chi2": chi2, "p_value": p}


def time_to_activate_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[df["activated"]]
        .groupby("group")["days_to_activate"]
        .agg(median="median", mean="mean")
        .reset_index()
    )


# --------------------------------------------------------------- diagnostics --


def srm_check(df: pd.DataFrame, expected_ratio: float = 0.5) -> dict:
    """Sample Ratio Mismatch: did users actually split as intended?

    A failing SRM means the randomisation itself is broken, which invalidates
    every downstream result no matter how significant it looks.
    """
    counts = df["group"].value_counts()
    n_control = int(counts.get("Control", 0))
    n_treatment = int(counts.get("Treatment", 0))
    total = n_control + n_treatment
    if total == 0:
        return {"p_value": 1.0, "failed": False, "observed_split": float("nan")}

    expected = [total * expected_ratio, total * (1 - expected_ratio)]
    chi2, p = stats.chisquare([n_control, n_treatment], f_exp=expected)[:2]

    return {
        "n_control": n_control,
        "n_treatment": n_treatment,
        "observed_split": n_treatment / total,
        "chi2": float(chi2),
        "p_value": float(p),
        "failed": bool(p < 0.001),
    }


def segment_breakdown(df: pd.DataFrame, segment_col: str = "segment") -> pd.DataFrame:
    """Activation rate and lift within each segment."""
    rows = []
    for seg, sub in df.groupby(segment_col):
        seg_stats = two_proportion_ztest(sub)
        rows.append(
            {
                "segment": seg,
                "n": len(sub),
                "control_rate": seg_stats["control_rate"],
                "treatment_rate": seg_stats["treatment_rate"],
                "relative_lift": seg_stats["relative_lift"],
                "p_value": seg_stats["p_value"],
            }
        )
    return pd.DataFrame(rows).sort_values("segment").reset_index(drop=True)


def detect_simpsons_reversal(df: pd.DataFrame, segment_col: str = "segment") -> dict:
    """Flag when the aggregate lift disagrees in sign with every segment.

    This is Simpson's paradox: the pooled number points one way while each
    subgroup points the other, usually because the arms have different segment
    mixes. Shipping on the pooled number would be a mistake.
    """
    overall = two_proportion_ztest(df)
    segs = segment_breakdown(df, segment_col)

    overall_sign = np.sign(overall["relative_lift"])
    seg_signs = np.sign(segs["relative_lift"])
    reversed_all = bool(len(segs) > 0 and (seg_signs != overall_sign).all())

    harmed = segs[segs["relative_lift"] < 0]["segment"].tolist()

    mix = (
        df.groupby(["group", segment_col]).size().unstack(fill_value=0).pipe(
            lambda d: d.div(d.sum(axis=1), axis=0)
        )
    )

    return {
        "reversed": reversed_all,
        "overall_lift": overall["relative_lift"],
        "segments": segs,
        "harmed_segments": harmed,
        "segment_mix": mix,
    }


def weekly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Lift per week — the shape that reveals a novelty effect."""
    rows = []
    for week, sub in df.groupby("week"):
        wk = two_proportion_ztest(sub)
        rows.append(
            {
                "week": int(week),
                "control_rate": wk["control_rate"],
                "treatment_rate": wk["treatment_rate"],
                "relative_lift": wk["relative_lift"],
                "p_value": wk["p_value"],
            }
        )
    return pd.DataFrame(rows).sort_values("week").reset_index(drop=True)


def detect_novelty(df: pd.DataFrame, decay_threshold: float = 0.5) -> dict:
    """Flag when an early lift decays substantially by the final week."""
    trend = weekly_trend(df)
    if len(trend) < 2:
        return {"novelty_suspected": False, "trend": trend}

    first, last = trend.iloc[0]["relative_lift"], trend.iloc[-1]["relative_lift"]
    decayed = bool(first > 0 and last < first * decay_threshold)

    return {
        "novelty_suspected": decayed,
        "first_week_lift": first,
        "last_week_lift": last,
        "trend": trend,
    }


def peeking_series(df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative p-value and lift as the experiment accrues data.

    Shows what you would have concluded had you stopped on each given day —
    the reason repeated significance testing inflates the false positive rate.
    """
    rows = []
    for day in sorted(df["day"].unique()):
        sofar = df[df["day"] <= day]
        if sofar["group"].nunique() < 2:
            continue
        res = two_proportion_ztest(sofar)
        rows.append(
            {
                "day": int(day),
                "n_total": len(sofar),
                "relative_lift": res["relative_lift"],
                "p_value": res["p_value"],
            }
        )
    return pd.DataFrame(rows)


def detect_peeking_risk(series: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Would stopping early have flipped the conclusion?"""
    if series.empty:
        return {"would_have_flipped": False}

    crossed = series[series["p_value"] < alpha]
    final_p = series.iloc[-1]["p_value"]
    final_significant = bool(final_p < alpha)

    return {
        "would_have_flipped": bool(len(crossed) > 0 and not final_significant),
        "first_crossing_day": int(crossed.iloc[0]["day"]) if len(crossed) else None,
        "days_significant": int(len(crossed)),
        "final_p_value": float(final_p),
        "final_significant": final_significant,
    }
