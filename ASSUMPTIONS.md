# Assumptions

Every number this tool generates comes from an assumption. This file states each
one, where it came from, and how sensitive the conclusions are to it. Where a
value is a placeholder rather than a benchmark, it says so explicitly.

## Funnel baseline rates

The default Control funnel in `data_loader.py`:

| Step | Step-through rate | Basis |
|---|---|---|
| Signed Up | 100% (entry) | Definitional — the funnel starts here |
| Verified Email | 72% | Mid-range of commonly reported SaaS email-confirmation rates (typically ~60–80% depending on whether verification gates product access). Directionally reliable; not a single published figure |
| Completed Profile | 55% | Placeholder. Profile completion varies enormously with how many fields are required and whether it is skippable |
| Took First Key Action | 40% | Placeholder, chosen to reflect the well-documented pattern that the largest onboarding drop-off usually sits at first meaningful action rather than at signup |
| Activated (returned day 7) | 27% | Placeholder. Compounds to ~27% end-to-end activation, which is in the plausible range for self-serve products but is not drawn from a specific source |

**How to read this:** the *shape* of the funnel — biggest losses at profile
completion and first key action — reflects a real and widely observed pattern.
The *specific* values are illustrative. Nothing in this repo should be cited as
an industry benchmark.

**Sensitivity:** the ship/no-ship verdict depends on the relative gap between
arms and the sample size, not on the absolute baseline. Changing the baseline
from 27% to 20% changes the required sample size (lower base rates need more
users) but does not change the direction of any conclusion.

## Treatment effect

The default Treatment funnel assumes improvement at every step (72%→80%,
55%→68%, 40%→50%, 27%→34%). This is deliberately optimistic — it is a
demonstration default so the dashboard shows a clear "ship" case on first load.
**A real redesign improving every single step is uncommon.** The scenarios page
exists specifically to counterbalance this optimism.

## Statistical thresholds

| Parameter | Value | Rationale |
|---|---|---|
| Significance level (α) | 0.05 | Two-sided. Convention, not law — a reversible UI change could justify a looser bar; an irreversible or trust-affecting change a tighter one |
| Power (1−β) | 80% default | Standard planning default. Means a 20% chance of missing a real effect of exactly the target size |
| Minimum sample per arm | 1,000 | Guardrail against calling a result on noise. Below this the tool refuses to recommend shipping regardless of p-value |
| Meaningful lift | ≥5% relative | **This is a product judgment, not a statistical one.** A statistically significant 1% lift on activation is usually not worth the engineering and maintenance cost. Set this to whatever your team would actually act on |
| SRM alarm | p < 0.001 | Deliberately strict. SRM checks run on every experiment, so a looser threshold produces constant false alarms |
| Novelty flag | final-week lift < 50% of first-week lift | Heuristic, not a test. Flags a decay pattern worth investigating rather than proving one |

## Time-to-activate

Modeled as a gamma distribution (shape 2.2, scale 1.8, shifted +1 day). Chosen
because it produces a right-skewed distribution with most activations in the
first few days and a long tail — the shape activation curves generally take. The
parameters are fitted to look plausible, not fitted to data.

## Acquisition channel mix

Organic 40% / Paid Search 30% / Referral 15% / Social 15%. Illustrative. In the
default simulation channel does **not** affect activation probability, so any
channel differences visible in the dashboard are sampling noise — which is
itself a useful thing to be able to recognise.

## Scenario data

The four preset scenarios in `scenarios.py` are **constructed, not sampled**.
Their counts are chosen exactly so each failure mode is unambiguous and
reproducible on every run:

- **Simpson's paradox** — exact cell counts producing a genuine sign reversal
  (treatment worse within both segments, better in aggregate)
- **Novelty effect** — treatment rates hand-set per week to decay from +50% to −2.5%
- **Sample ratio mismatch** — a fixed 10,400 / 9,600 split
- **Peeking** — a true null effect (both arms 20%); the seed is searched at
  runtime for a run that crosses p<0.05 mid-flight and ends non-significant

These are teaching cases. They are designed to be caught, and the diagnostics
catch them by construction.

## What this tool does not model

- Cross-arm interference (users influencing each other)
- Multiple comparisons across many simultaneous metrics
- Seasonality, day-of-week effects, or marketing campaigns landing mid-test
- Non-independence when one user has several sessions
- Survivorship bias from users who churn before the measurement window closes
- Cost of implementation — a 5% lift that takes two engineer-months may lose to
  a 3% lift that takes two days
