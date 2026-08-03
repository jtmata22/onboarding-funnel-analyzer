# Digital Adoption Experiment Designer

Designing the evaluation that would test an intervention against the digital
adoption gap in Hand in Hand International's DIGITISE programme — and working out
what that evaluation could and could not conclude at the programme's actual scale.

**Start with [FINDINGS.md](FINDINGS.md)** — the recommendation. The app is how I
got there.

## Background

I worked on this as an **Operations Intern at Hand in Hand International**, where
I also led a CRM system migration. The adoption-gap analysis and the coaching
recommendation come out of that work.

The original analysis drew on internal programme data. **This public version was
rebuilt using only figures published in the cohort 1 endline report** — no
internal or participant-level data appears anywhere in this repository. Shared
with permission.

> Views are my own. This is not an official Hand in Hand International
> publication or evaluation.

## The problem

Hand in Hand International's DIGITISE programme trains small business owners in
Nairobi — over 80% women — in digital marketing and e-commerce. Cohort 1 results
show participants who received digital training earning **$108 PPP more per
month** than those who did not.

But only **49%** of trained participants reported adopting digital practices at
all, and among women that was **46% against 59% for men** — inside a national
43% gender gap in daily mobile internet use.¹

```
Enrolled -> Trained -> Reported adopting digital practices -> Enterprise outcomes
                    ^
   ~54% of trained women not retained at this step
```

**The bottleneck is adoption, not training.** Every downstream benefit is gated
on a step where more than half the intended beneficiaries drop out.

## The recommendation

Test an enhanced one-to-one coaching model alongside existing group training,
sized to answer three questions: does coaching increase adoption, does adoption
translate into enterprise income, and can it be delivered at a sustainable cost.

The design finding that matters most is a constraint. At ~800 women per arm:

| Target change | Adoption | Needed per arm | Feasible? |
|---|---|---|---|
| +10% relative | 46% → 51% | 1,849 | No — more than the programme has |
| +28% relative (closes the gap) | 46% → 59% | 233 | Yes, comfortably |

The evaluation can detect an intervention that closes most of the gap, but is
**poorly positioned to distinguish a modest improvement from no effect**. A
half-measure would consume both remaining cohorts and return an uninterpretable
null. That constraint should drive how ambitious the intervention is — and it is
invisible without running the numbers first.

Full reasoning, evaluation design, decision framework, and risks in
[FINDINGS.md](FINDINGS.md).

## What the app does

**1. Design** — Is the study adequately powered for the effect worth acting on?
Supports a fixed-cohort programme setting (the DIGITISE case) and a continuous
traffic setting (generic products). Reports minimum detectable effect and states
plainly what a null result would and would not mean.

**2. Pressure-test** — Four preset experiments, each engineered to look like a
clean, significant win while hiding a specific failure mode:

| Scenario | The headline | What's actually true |
|---|---|---|
| Simpson's paradox | +73%, p < 0.0001 | Worse in *both* segments; arms have different mixes |
| Novelty effect | +22%, p < 0.0001 | Period 1 +50%, period 4 −2.5%. Effect already gone |
| Sample ratio mismatch | +15%, p < 0.0001 | 52/48 split. Randomisation broken; result uninterpretable |
| Peeking | Significant mid-flight | True effect is zero. Daily checking manufactured the signal |

The decision engine catches each and overrides the headline. A small p-value does
not earn a recommendation if randomisation failed or the pooled number reverses
by segment.

**3. Demo mode** — A generic SaaS funnel analyser demonstrating the same
machinery on a conventional product funnel. **Illustrative only — its email
verification, profile completion and day-7 activation steps have nothing to do
with DIGITISE**, and the page says so.

## Two ideas kept separate

The decision engine distinguishes:

- **Statistical sufficiency** — is the sample large enough to detect the target
  effect? Arithmetic, answered by `power.py` against the baseline rate and target,
  *not* a fixed sample floor.
- **Operational confidence** — is the evidence strong enough to scale, given
  guardrails, durability, and delivery cost? A judgment a p-value does not settle.

Conflating them is why an earlier version of this repo simultaneously claimed
800 participants per arm was sufficient (in the findings) and underpowered (in
the app). Sufficiency depends on baseline and target effect — a 233-per-arm study
can be adequate for a large effect while 5,000 is inadequate for a small one.

## Documentation

- **[FINDINGS.md](FINDINGS.md)** — executive recommendation, evidence, hypothesis,
  evaluation design, outcome definitions, decision framework, risks, monitoring
- **[ASSUMPTIONS.md](ASSUMPTIONS.md)** — published evidence vs. my evaluation
  assumptions vs. generic simulator placeholders, kept strictly separate, plus
  methodology and limitations

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
app.py             Streamlit UI: intro, design, scenarios, demo mode
power.py           Sample size, minimum detectable effect, runtime
scenarios.py       The four rigged experiments
analysis.py        Rate comparisons, SRM, segment and trend diagnostics
verdict.py         Sufficiency, guardrails, and the decision framework
data_loader.py     Synthetic funnel generator (demo mode only)
FINDINGS.md        The recommendation
ASSUMPTIONS.md     Evidence, assumptions, and limitations
```

## Tech stack

Python · Streamlit · pandas · numpy · scipy · Altair

¹ Hand in Hand International, *DIGITISE: Initial results for Hand in Hand's
business accelerator in Nairobi*, in partnership with Happel Foundation. GSMA
2024 for the mobile internet gap.
