"""Turn statistical results into a decision.

Two ideas are kept deliberately separate:

**Statistical sufficiency** — is the sample large enough to detect the effect we
said we cared about? This is a power question with an arithmetic answer.

**Operational confidence** — is the evidence strong enough to act on, given
guardrails, durability, and delivery cost? This is a judgment call that a small
p-value alone does not settle.

An earlier version of this file used a flat 1,000-per-arm floor for sufficiency.
That was wrong: sufficiency depends on the baseline rate and the target effect,
not on a fixed number. A 233-per-arm study can be perfectly adequate for a large
effect while 5,000 per arm is inadequate for a small one.
"""

from power import required_sample_size

SIGNIFICANCE_THRESHOLD = 0.05
DEFAULT_TARGET_LIFT = 0.05  # relative; override per context
DEFAULT_POWER = 0.80

# Vocabulary differs by context; the logic underneath does not.
PRODUCT_LABELS = {
    "act": "Ship to all users",
    "extend": "Extend the experiment",
    "stop": "Do not ship",
    "invalid": "Invalid experiment — do not ship",
}

PROGRAMME_LABELS = {
    "act": "Scale gradually",
    "extend": "Extend the evaluation",
    "stop": "Do not scale this intervention",
    "invalid": "Invalid evaluation — do not interpret",
}


def assess_sufficiency(
    baseline_rate: float,
    n_per_group: int,
    target_lift: float,
    power: float = DEFAULT_POWER,
) -> dict:
    """Is n large enough to detect target_lift at the stated power?"""
    if baseline_rate is None or not (0 < baseline_rate < 1):
        return {"checked": False, "adequate": True, "required": None}

    required = required_sample_size(baseline_rate, target_lift, power=power)
    return {
        "checked": True,
        "adequate": bool(n_per_group >= required),
        "required": required,
        "actual": n_per_group,
        "target_lift": target_lift,
    }


def decide(
    ztest_result: dict,
    n_per_group: int,
    guardrails: dict = None,
    baseline_rate: float = None,
    target_lift: float = DEFAULT_TARGET_LIFT,
    labels: dict = None,
) -> dict:
    """guardrails may contain: srm, simpsons, novelty, peeking (all optional)."""
    guardrails = guardrails or {}
    labels = labels or PRODUCT_LABELS
    warnings = []

    # -- invalidating: randomisation itself is broken -------------------------
    srm = guardrails.get("srm")
    if srm and srm.get("failed"):
        return {
            "verdict": "no-ship",
            "headline": labels["invalid"],
            "reason": (
                f"Sample ratio mismatch: the arms split "
                f"{srm['n_control']:,} / {srm['n_treatment']:,} "
                f"({srm['observed_split']:.1%} treatment) when 50/50 was intended "
                f"(p={srm['p_value']:.2e}). Units are being lost from one arm "
                "non-randomly, so the comparison is not valid. Fix assignment and "
                "rerun — do not interpret the difference."
            ),
            "warnings": warnings,
            "sufficiency": None,
        }

    p_value = ztest_result["p_value"]
    lift = ztest_result["relative_lift"]
    diff = ztest_result["absolute_diff"]

    sufficiency = assess_sufficiency(baseline_rate, n_per_group, target_lift)
    significant = p_value < SIGNIFICANCE_THRESHOLD
    meaningful = lift is not None and lift >= target_lift

    # -- overriding: the pooled number contradicts every segment --------------
    simpsons = guardrails.get("simpsons")
    if simpsons and simpsons.get("reversed"):
        harmed = ", ".join(simpsons["harmed_segments"])
        return {
            "verdict": "no-ship",
            "headline": f"{labels['stop']} — pooled result reverses by segment",
            "reason": (
                f"The pooled difference is {simpsons['overall_lift']:+.1%}, but the "
                f"treatment performs worse within every segment ({harmed}). The "
                "headline number is driven by a different segment mix between arms, "
                "not by the intervention. Acting on it would harm every real group."
            ),
            "warnings": warnings,
            "sufficiency": sufficiency,
        }

    # -- cautionary: effect is decaying --------------------------------------
    novelty = guardrails.get("novelty")
    if novelty and novelty.get("novelty_suspected"):
        return {
            "verdict": "extend",
            "headline": f"{labels['extend']} — effect is decaying",
            "reason": (
                f"Period 1 difference was {novelty['first_week_lift']:+.1%}; by the "
                f"final period it is {novelty['last_week_lift']:+.1%}. That decay is "
                "consistent with a novelty effect rather than a durable improvement. "
                "Extend follow-up and judge on the stabilised periods, not the "
                "pooled average."
            ),
            "warnings": warnings,
            "sufficiency": sufficiency,
        }

    # -- overriding: an early stop would have reversed the call ---------------
    peek = guardrails.get("peeking")
    if peek and peek.get("would_have_flipped"):
        return {
            "verdict": "extend",
            "headline": f"{labels['extend']} — do not stop on an interim look",
            "reason": (
                f"This study crossed p<0.05 on day {peek['first_crossing_day']} and "
                f"was significant on {peek['days_significant']} days, but ends at "
                f"p={peek['final_p_value']:.3f}. Repeated interim testing inflates "
                "the false positive rate well above the nominal 5%, so an early stop "
                "would have declared a winner that the full run does not support. "
                "Read the result at the pre-registered end date."
            ),
            "warnings": warnings,
            "sufficiency": sufficiency,
        }

    # -- statistical sufficiency ---------------------------------------------
    # Power governs how a *null* is read. Once an effect has been detected at the
    # required size, prospective power is moot — the study evidently could see it.
    # Applying the gate to a significant result would be post-hoc power, which is
    # not a meaningful quantity.
    underpowered_null = (
        sufficiency["checked"] and not sufficiency["adequate"] and not significant
    )
    if underpowered_null:
        return {
            "verdict": "extend",
            "headline": f"{labels['extend']} — underpowered for the target effect",
            "reason": (
                f"No significant difference (p={p_value:.4f}), but this design cannot "
                f"support that conclusion: detecting a {target_lift:.0%} relative "
                f"change from a {baseline_rate:.0%} baseline needs about "
                f"{sufficiency['required']:,} per arm at {DEFAULT_POWER:.0%} power, "
                f"and this has {n_per_group:,}. The null does not distinguish "
                "'no effect' from 'not enough data'."
            ),
            "warnings": warnings,
            "sufficiency": sufficiency,
        }

    # -- standard decision ----------------------------------------------------
    if diff < 0 and significant:
        verdict, headline = "no-ship", labels["stop"]
        reason = (
            "The treatment significantly reduced the primary outcome "
            f"({lift:+.1%} relative change, p={p_value:.4f}). Revert or redesign."
        )
    elif significant and meaningful:
        verdict, headline = "ship", labels["act"]
        reason = (
            f"Treatment raised the primary outcome by {lift:+.1%} relative "
            f"(p={p_value:.4f}), clearing both the significance bar and the "
            f"{target_lift:.0%} threshold set in advance. Confirm delivery cost and "
            "durability before committing."
        )
    elif significant and not meaningful:
        verdict, headline = "extend", labels["extend"]
        reason = (
            f"The change ({lift:+.1%}) is statistically significant (p={p_value:.4f}) "
            f"but below the {target_lift:.0%} threshold set in advance. Statistically "
            "real is not the same as worth doing — weigh it against delivery cost."
        )
    else:
        verdict, headline = "extend", labels["extend"]
        if sufficiency["checked"]:
            reason = (
                f"No statistically significant difference (p={p_value:.4f}) despite "
                f"adequate power ({n_per_group:,} per arm vs. "
                f"{sufficiency['required']:,} required). This is meaningful evidence "
                f"against an effect as large as {target_lift:.0%}, not merely absent "
                "evidence."
            )
        else:
            reason = (
                f"No statistically significant difference (p={p_value:.4f}). "
                "Collect more signal before making a call."
            )

    return {
        "verdict": verdict,
        "headline": headline,
        "reason": reason,
        "warnings": warnings,
        "sufficiency": sufficiency,
    }
