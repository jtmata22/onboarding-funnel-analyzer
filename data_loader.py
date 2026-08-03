"""Synthetic onboarding funnel data.

Generates two cohorts of new users — a Control flow (the existing
onboarding) and a Treatment flow (a proposed change, e.g. fewer steps,
a progress indicator, better copy) — and simulates each user's path
through the funnel. Swap this out for a real warehouse query later;
the rest of the app only depends on the DataFrame shape returned here.
"""

import numpy as np
import pandas as pd
import streamlit as st

FUNNEL_STEPS = [
    "Signed Up",
    "Verified Email",
    "Completed Profile",
    "Took First Key Action",
    "Activated (Returned Day 7)",
]


@st.cache_data(ttl=1)
def load_funnel_data(
    n_per_group: int = 6000,
    control_probs: tuple = (1.0, 0.72, 0.55, 0.40, 0.27),
    treatment_probs: tuple = (1.0, 0.80, 0.68, 0.50, 0.34),
    seed: int = 42,
) -> pd.DataFrame:
    """Simulate per-user progression through the onboarding funnel.

    control_probs / treatment_probs are the probability a user who
    reached step i also reaches step i+1 (conditional, not cumulative).
    """
    rng = np.random.default_rng(seed)
    rows = []

    for group, probs in (("Control", control_probs), ("Treatment", treatment_probs)):
        n = n_per_group
        reached_step = np.zeros(n, dtype=int)
        still_in = np.ones(n, dtype=bool)

        for i, p in enumerate(probs):
            advance = still_in & (rng.random(n) < p)
            reached_step[advance] = i
            still_in = advance

        # time-to-activate (days), only meaningful for users who activated
        activated = reached_step == (len(probs) - 1)
        days_to_activate = np.where(
            activated,
            rng.gamma(shape=2.2, scale=1.8, size=n).round(1) + 1,
            np.nan,
        )

        channel = rng.choice(
            ["Organic", "Paid Search", "Referral", "Social"],
            size=n,
            p=[0.4, 0.3, 0.15, 0.15],
        )

        rows.append(
            pd.DataFrame(
                {
                    "user_id": [f"{group[:1]}-{i}" for i in range(n)],
                    "group": group,
                    "furthest_step_idx": reached_step,
                    "furthest_step": [FUNNEL_STEPS[i] for i in reached_step],
                    "activated": activated,
                    "days_to_activate": days_to_activate,
                    "acquisition_channel": channel,
                }
            )
        )

    return pd.concat(rows, ignore_index=True)
