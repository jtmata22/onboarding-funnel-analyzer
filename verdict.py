"""Turn the stats into a ship / extend / don't-ship recommendation.

Guardrails run first and can override a significant result. A test with a
broken split or a segment-level reversal does not get a ship recommendation
just because the pooled p-value is small.
"""

MIN_SAMPLE_PER_GROUP = 1000
SIGNIFICANCE_THRESHOLD = 0.05
MEANINGFUL_LIFT_THRESHOLD = 0.05  # 5% relative lift in activation rate


def decide(ztest_result: dict, n_per_group: int, guardrails: dict = None) -> dict:
    """guardrails may contain: srm, simpsons, novelty, peeking (all optional)."""
    guardrails = guardrails or {}
    warnings = []

    # -- invalidating: randomisation itself is broken -------------------------
    srm = guardrails.get("srm")
    if srm and srm.get("failed"):
        return {
            "verdict": "no-ship",
            "headline": "Invalid experiment — do not ship",
            "reason": (
                f"Sample ratio mismatch: the arms split "
                f"{srm['n_control']:,} / {srm['n_treatment']:,} "
                f"({srm['observed_split']:.1%} treatment) when 50/50 was intended "
                f"(p={srm['p_value']:.2e}). Users are being lost from one arm "
                "non-randomly, so the comparison is not valid. Fix the assignment "
                "pipeline and rerun — do not interpret the lift."
            ),
            "warnings": warnings,
        }

    p_value = ztest_result["p_value"]
    lift = ztest_result["relative_lift"]
    diff = ztest_result["absolute_diff"]

    underpowered = n_per_group < MIN_SAMPLE_PER_GROUP
    significant = p_value < SIGNIFICANCE_THRESHOLD
    meaningful = lift is not None and lift >= MEANINGFUL_LIFT_THRESHOLD

    # -- overriding: the pooled number contradicts every segment --------------
    simpsons = guardrails.get("simpsons")
    if simpsons and simpsons.get("reversed"):
        harmed = ", ".join(simpsons["harmed_segments"])
        return {
            "verdict": "no-ship",
            "headline": "Do not ship — pooled result reverses by segment",
            "reason": (
                f"The pooled lift is {simpsons['overall_lift']:+.1%}, but the "
                f"treatment performs worse within every segment ({harmed}). "
                "The headline number is driven by a different segment mix between "
                "arms, not by the change itself. Shipping this would harm every "
                "real group of users."
            ),
            "warnings": warnings,
        }

    # -- cautionary: effect is decaying --------------------------------------
    novelty = guardrails.get("novelty")
    if novelty and novelty.get("novelty_suspected"):
        return {
            "verdict": "extend",
            "headline": "Extend — lift is decaying",
            "reason": (
                f"Week 1 lift was {novelty['first_week_lift']:+.1%}; by the final "
                f"week it is {novelty['last_week_lift']:+.1%}. That decay pattern "
                "is consistent with a novelty effect rather than a durable "
                "improvement. Run longer and judge on the stabilised weeks, not "
                "the pooled average."
            ),
            "warnings": warnings,
        }

    peek = guardrails.get("peeking")
    if peek and peek.get("would_have_flipped"):
        warnings.append(
            f"This test crossed p<0.05 on day {peek['first_crossing_day']} "
            f"({peek['days_significant']} days significant in total) but ends at "
            f"p={peek['final_p_value']:.3f}. Stopping early would have produced a "
            "false positive."
        )

    # -- standard decision ----------------------------------------------------
    if underpowered:
        verdict, headline = "extend", "Extend the experiment"
        reason = (
            f"Each group has ~{n_per_group:,} users, below the "
            f"{MIN_SAMPLE_PER_GROUP:,} needed to trust the result. "
            "Keep running before deciding."
        )
    elif diff < 0 and significant:
        verdict, headline = "no-ship", "Do not ship"
        reason = (
            "The new onboarding flow significantly reduced activation "
            f"({lift:+.1%} relative change, p={p_value:.4f}). Revert or redesign."
        )
    elif significant and meaningful:
        verdict, headline = "ship", "Ship to all users"
        reason = (
            f"Treatment lifted activation by {lift:+.1%} relative "
            f"(p={p_value:.4f}), which is both statistically significant and "
            "large enough to matter."
        )
    elif significant and not meaningful:
        verdict, headline = "extend", "Extend the experiment"
        reason = (
            f"The lift ({lift:+.1%}) is statistically significant (p={p_value:.4f}) "
            f"but below the {MEANINGFUL_LIFT_THRESHOLD:.0%} bar for a meaningful "
            "product change. Confirm it's worth the engineering cost before shipping."
        )
    else:
        verdict, headline = "extend", "Extend the experiment"
        reason = (
            f"No statistically significant difference yet (p={p_value:.4f}). "
            "Collect more signal before making a call."
        )

    return {
        "verdict": verdict,
        "headline": headline,
        "reason": reason,
        "warnings": warnings,
    }
