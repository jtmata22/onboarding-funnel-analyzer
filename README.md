# Onboarding Experiment Designer

A Streamlit tool for designing onboarding experiments before they run, stress-testing
them against the ways A/B tests mislead, and turning results into a defensible
ship / extend / don't-ship recommendation.

**Start here: [FINDINGS.md](FINDINGS.md)** — the actual recommendation this tool was
built to produce. The app is how I got there.

## Why this exists

Most experiment tooling reports what happened after the fact. The harder questions
come earlier, and they are the ones that sink experiments:

- How long do we need to run this?
- Is this test even capable of detecting the effect we care about?
- If it comes back null, will that mean "no effect" or "not enough users"?

Those are power and minimum-detectable-effect questions. Simulation is the correct
instrument for them — not a stand-in for production data, but the only way to answer
a question about a test that has not run yet.

## What it does

**1. Design** — Given a baseline conversion rate, weekly traffic, and the smallest
lift you'd actually act on, it returns users needed per arm, weeks to run, and a
curve of what's detectable at each week. If the test can't detect what you care
about in the time you have, it says so before you spend the traffic.

**2. Pressure-test** — Four preset experiments, each engineered to look like a clean,
significant win while hiding a specific failure mode:

| Scenario | The headline | What's actually true |
|---|---|---|
| Simpson's paradox | +73% lift, p < 0.0001 | Treatment is worse in *both* segments; the arms have different mixes |
| Novelty effect | +22% lift, p < 0.0001 | Week 1 was +50%, week 4 is −2.5%. The effect is already gone |
| Sample ratio mismatch | +15% lift, p < 0.0001 | Split is 52/48, not 50/50. Randomisation is broken; result is uninterpretable |
| Peeking | Significant mid-flight | True effect is exactly zero. Daily checking manufactured the signal |

The verdict engine catches each one and overrides the headline result. A significant
p-value does not earn a ship recommendation if the randomisation failed or the pooled
number reverses by segment.

**3. Analyze** — Full funnel breakdown: step-by-step conversion and drop-off,
chi-square testing at each step to locate where flows diverge, time-to-activate,
and activation by acquisition channel.

## Where the problem came from: Hand in Hand International

Hand in Hand International's DIGITISE programme trains small business owners in
Nairobi (over 80% women) in digital marketing and e-commerce. Their cohort 1 results
are a real instance of exactly the problem this tool is built for: entrepreneurs who
received digital marketing training earned **$108 PPP more per month**, but only
**49%** of trained participants adopted digital practices — and adoption among women
was **46% vs. 59%** for men, inside a broader 43% gender gap in Kenyan mobile
internet use.¹

That is an onboarding funnel with a measurable, gendered drop-off:

```
Enrolled -> Trained -> Adopted digital practices -> Revenue gain
                    ^
             54% of women lost here
```

[FINDINGS.md](FINDINGS.md) works that problem end to end: hypothesis, the experiment
I'd run for cohorts 2 and 3, what it can and cannot detect at the programme's actual
scale, the risks I'd flag, and what I'd monitor after launch.

The sizing finding is the interesting one — at ~800 women per arm the programme can
detect an intervention that closes most of the gender gap, but **cannot** detect a
modest one (a 10% relative lift would need 1,849 per arm, more women than remain in
the programme). That constraint should drive the intervention design, and it is
invisible without running the numbers first.

## Documentation

- **[FINDINGS.md](FINDINGS.md)** — the recommendation: hypothesis, experiment design,
  power analysis, risks, post-launch monitoring
- **[ASSUMPTIONS.md](ASSUMPTIONS.md)** — every baseline rate and threshold, where it
  came from, and what is a benchmark vs. a placeholder

## Tech stack

Python · Streamlit · pandas · numpy · scipy · Altair

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Project structure

```
app.py             Streamlit UI: intro, designer, scenarios, funnel dashboard
power.py           Sample size, minimum detectable effect, runtime
scenarios.py       The four rigged experiments
analysis.py        Funnel math, z-test, chi-square, SRM, segment and trend diagnostics
verdict.py         Guardrails and the ship / extend / no-ship decision
data_loader.py     Synthetic funnel generator
FINDINGS.md        The recommendation
ASSUMPTIONS.md     Documented assumptions and their sources
```

## Methodology

- Significance: p < 0.05, two-sided
- Power: 80% default, adjustable
- Minimum sample per arm before any ship recommendation: 1,000
- Meaningful lift: ≥5% relative — a product judgment, not a statistical one
- SRM alarm: p < 0.001

All thresholds are documented in [ASSUMPTIONS.md](ASSUMPTIONS.md) and adjustable in
`verdict.py`.

¹ Hand in Hand International, *DIGITISE: Initial results for Hand in Hand's business
accelerator in Nairobi*, in partnership with Happel Foundation. GSMA 2024 for the
mobile internet gap figure.
