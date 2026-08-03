# Evidence, Assumptions, and Limitations

This file separates three very different kinds of claim, because conflating them
is how analysis becomes misleading:

1. **Published evidence** — figures reported by Hand in Hand International
2. **Evaluation assumptions** — my own inputs for designing the proposed pilot
3. **Generic simulator assumptions** — placeholder values for the demo mode,
   which have nothing to do with DIGITISE

---

## 1. Published evidence

All figures below come from Hand in Hand International's DIGITISE cohort 1
endline report, produced in partnership with Happel Foundation.¹

| Figure | Value | Type | Scope |
|---|---|---|---|
| Median enterprise revenue increase | 77% ($323 → $571/month) | Descriptive, pre/post | Cohort 1, all groups |
| Median monthly profit increase | 121% (+$156) | Descriptive, pre/post | Cohort 1, all groups |
| Revenue difference, digital-trained vs. not | +$108 PPP/month | Comparative (treatment vs. control) | Cohort 1 |
| Adoption of digital practices among trained | 49% | Descriptive | Cohort 1 treatment group |
| Adoption by gender | 59% men / 46% women | Descriptive | Cohort 1 treatment group |
| Smartphone ownership by gender | 92% men / 75% women | Descriptive | Cohort 1 treatment group |
| Enterprise survival rate | 91% | Descriptive | Cohort 1 |
| Reported improved quality of life | 95% | Self-reported | Cohort 1 |
| Programme total | 3,000 entrepreneurs, 80%+ women, three cohorts | Programme design | Full programme |
| Cohort 1 size | 1,000 entrepreneurs | Programme design | Cohort 1 |
| Kenya gender gap, daily mobile internet use | 43% | External | National (GSMA, 2024)² |

**Important qualifications on this evidence:**

- The +$108 PPP revenue difference is the one figure from a treatment/control
  comparison. The 77% and 121% growth figures are **pre/post across all
  participants**, with no counterfactual — they cannot be read as the causal
  effect of the programme, since businesses may have grown anyway.
- Adoption figures appear to be **self-reported at endline**. Self-report is
  vulnerable to social desirability bias, particularly from participants who
  received additional attention.
- The report does not define precisely which behaviours count as "adopting
  digital practices." This matters for interpretation and is addressed in
  FINDINGS.md.
- All figures are cohort 1 only. Cohort 2 and 3 results are due in early 2026.

---

## 2. Evaluation assumptions

These are **mine**, not Hand in Hand's. They are the inputs required to size the
pilot proposed in FINDINGS.md, and each is a point of failure if wrong.

| Assumption | Value | Basis | If wrong |
|---|---|---|---|
| Women in cohorts 2 and 3 | ~1,600 | Inferred: 3,000 total − 1,000 in cohort 1 = 2,000, of which 80%+ women | Directly changes power; the whole sizing table shifts |
| Participants per arm | ~800 | 1:1 allocation of the above | Same |
| Baseline adoption (women) | 46% | Cohort 1 observed value | If cohorts 2–3 differ, required sample changes |
| Target effect | +28% relative (46% → 59%) | Chosen to close the observed gender gap | A smaller target is not detectable at this scale — that is the central finding |
| Power | 80% | Planning convention | At 90% power required n rises ~30% |
| Significance level | 0.05, two-sided | Convention | — |
| Attrition | **Not modelled** | — | Real attrition reduces effective sample; 20% loss would meaningfully erode power |
| Cost per coaching session | **Not estimated** | No published figure available | Cost-effectiveness cannot be assessed without it |
| Follow-up window | Endline + 6 months | Chosen to detect decay | Shorter windows cannot distinguish durable from novelty effects |

**Assumptions I could not check.** Real enrolment numbers, actual cohort gender
splits, coaching delivery costs, and the operational definition of "adoption"
are all unavailable publicly. Any of them could change the recommendation.

---

## 3. Generic simulator assumptions

**The Demo mode page is a reusable demonstration, not the DIGITISE case study.**
Its SaaS-style funnel steps and rates do not represent Hand in Hand
International participants, programmes, or performance. They exist only to
demonstrate the funnel-analysis functionality on a conventional product.

Default Control funnel in `data_loader.py`:

| Step | Rate | Status |
|---|---|---|
| Signed Up | 100% | Definitional entry point |
| Verified Email | 72% | Loosely benchmarked — typical SaaS confirmation rates run ~60–80% |
| Completed Profile | 55% | **Placeholder** |
| Took First Key Action | 40% | **Placeholder**, shaped to reflect the common pattern that the largest drop-off sits at first meaningful action |
| Activated (returned day 7) | 27% | **Placeholder** |

The *shape* reflects a widely observed pattern. The *values* are illustrative.
**Nothing here should be cited as an industry benchmark.**

Other demo-only constructs: acquisition channel mix (Organic 40% / Paid 30% /
Referral 15% / Social 15%), time-to-activate as a gamma distribution (shape 2.2,
scale 1.8, +1 day), and the default treatment improving at every step — which is
deliberately optimistic and uncommon in reality.

Note that channel does **not** affect activation probability in the simulation,
so any channel differences visible on that page are sampling noise. Recognising
that is itself a useful exercise.

---

## 4. Scenario data

The four preset scenarios in `scenarios.py` are **constructed, not sampled** —
their counts are chosen so each failure mode is unambiguous and reproducible:

- **Simpson's paradox** — exact cell counts producing a genuine sign reversal
- **Novelty effect** — weekly rates hand-set to decay from +50% to −2.5%
- **Sample ratio mismatch** — a fixed 10,400 / 9,600 split
- **Peeking** — a true null effect (both arms 20%); the seed is searched at
  runtime for a run crossing p<0.05 mid-flight and ending non-significant

These are teaching cases, designed to be caught.

---

## 5. Statistical methodology

- Two-proportion z-test for differences in rates between arms
- Chi-square for step-level drop-off and for sample ratio mismatch
- Power and minimum detectable effect via the standard two-proportion formula
  (`power.py`), inverted by bisection for MDE
- **Statistical sufficiency is assessed against the target effect**, not a fixed
  sample floor. An earlier version used a flat 1,000-per-arm minimum, which was
  wrong — sufficiency depends on baseline rate and target effect. A 233-per-arm
  study can be adequate for a large effect while 5,000 is inadequate for a small one.
- SRM alarm at p < 0.001, deliberately strict since the check runs on every study
- Novelty flag when final-period effect < 50% of first-period effect. This is a
  heuristic that flags a pattern worth investigating, **not a formal test**

---

## 6. What this analysis does not do

- No participant-level data was used. Everything rests on published aggregates.
- No causal claim is made about the relationship between adoption and revenue.
  The two are associated in cohort 1; that association is not established as
  causal here, and should not be extrapolated linearly.
- Cross-arm interference, seasonality, multiple comparisons across metrics,
  non-independence from repeated observations, and survivorship bias are all
  unmodelled.
- Cost-effectiveness is not assessed, because no cost data is public.
- This is an **independent case study**, not an official Hand in Hand
  International evaluation, and carries no endorsement from the organisation.

¹ Hand in Hand International, *DIGITISE: Initial results for Hand in Hand's
business accelerator in Nairobi*, in partnership with Happel Foundation.
² GSMA, 2024, cited in the same report.
