# Findings and recommendation

## Executive recommendation

Hand in Hand International's DIGITISE programme appears to create value for
participants who adopt digital practices. The key programme challenge is
therefore not only delivering training, but helping more women use the tools
after training.

I recommend testing an enhanced coaching model alongside the existing group
training. The pilot should be designed to answer three questions:

1. Does coaching increase digital adoption?
2. Does that adoption translate into higher enterprise income or online sales?
3. Can the intervention be delivered at a cost and scale the programme can sustain?

The central design finding is a constraint, not a result: **at the programme's
likely scale the evaluation can detect an intervention that closes most of the
adoption gap, but would be poorly positioned to distinguish a modest improvement
from no effect.** That should shape how ambitious the intervention is, before
anyone commits a cohort to it.

> This is an independent case study based on publicly available evidence. It is
> not an official Hand in Hand International evaluation or product
> recommendation, and is not affiliated with the organisation. No
> participant-level data was used.

---

## The evidence

From the DIGITISE cohort 1 endline report:¹

| Finding | Figure |
|---|---|
| Revenue difference, digital-trained vs. not | +$108 PPP/month |
| Trained participants reporting adoption | 49% |
| Adoption — men vs. women | 59% vs. 46% |
| Smartphone ownership — men vs. women | 92% vs. 75% |
| Kenya gender gap in daily mobile internet use² | 43% |

The available evidence suggests that participants who adopt digital practices
may experience stronger enterprise outcomes, but this project does not establish
that relationship using participant-level data. The +$108 figure comes from a
treatment/control comparison; the programme's headline 77% revenue growth is a
pre/post figure without a counterfactual and should not be read causally.

What is clear is where participants are lost. Among women who received training,
**approximately 54% did not report adopting the measured digital practices.**

```
Enrolled -> Trained in digital marketing -> Reported adopting digital practices -> Enterprise outcomes
                                         ^
                        ~54% of trained women not retained at this step
```

Every downstream benefit is gated on a step where more than half of the intended
beneficiaries drop out, and the shortfall is concentrated among women — who are
over 80% of participants and the programme's explicit target population. The
13-point gap sits inside a national 43% gap in mobile internet use, so this is a
structural headwind, not a quirk of one cohort.

## Hypothesis

We hypothesize that some participants who do not adopt digital practices face
confidence, device-use, or access barriers rather than a lack of interest in the
value of digital tools.

One-to-one coaching on the participant's own device may reduce those barriers
more effectively than group training alone. **This is a testable hypothesis, not
an established explanation of the adoption gap.**

The supporting evidence is indirect and thin: 75% smartphone ownership among
women means device access alone cannot explain 54% non-adoption, and one quoted
participant describes finding digital marketing difficult at first and manageable
with coaching.¹ That is enough to justify a test, not enough to justify skipping
one. Qualitative work with cohort 1 non-adopters would be a cheaper first step
than committing both remaining cohorts to an RCT.

## Defining the primary outcome

"Adoption" must be defined precisely before the pilot starts, or the primary
metric cannot be interpreted. Proposed definition — a participant counts as
having adopted if, in the 30 days before endline, they did at least two of:

- created or maintained a business page on a social or commerce platform
- listed one or more products or services online
- used digital marketing (posts, ads, promotions) for the business
- completed at least one digital transaction
- used a specified business tool consistently (e.g. a catalogue or payments app)

Each should be verified against something observable wherever possible — an
active page, a live listing — rather than self-report alone, since participants
receiving extra coaching attention have more reason to report favourably.

## Evaluation design

- **Unit of randomisation:** participant
- **Primary estimand:** intention-to-treat effect of being *offered* coaching
- **Primary outcome:** adoption of the predefined digital practices at endline
- **Secondary outcomes:** online sales, enterprise revenue, confidence measures, training retention
- **Timing:** endline, plus six-month follow-up
- **Allocation:** 1:1 within each cohort
- **Stratification:** cohort, sector, geography, baseline smartphone access
- **Analysis:** overall treatment effect plus pre-specified subgroup results
- **Missing data:** document non-response and compare attrition by arm

Randomising *within* each cohort rather than assigning cohort 2 to control and
cohort 3 to treatment is essential — otherwise any seasonal or delivery change
between cohorts is perfectly confounded with the treatment.

## Statistical sufficiency

Computed with `power.py` at α=0.05, 80% power, baseline 46%:

| Target relative change | Adoption | Needed per arm | Feasible at ~800/arm? |
|---|---|---|---|
| +10% | 46% → 51% | 1,849 | No — exceeds available participants |
| +15% | 46% → 53% | 821 | Marginal |
| +20% | 46% → 55% | 460 | Yes |
| +28% (closes the gap) | 46% → 59% | 233 | Yes, comfortably |

At 800 per arm the smallest detectable effect is **+15.2% relative (about 7
percentage points)**.

At the assumed sample size, the programme may be able to detect an intervention
that closes most of the observed adoption gap, but it would be poorly positioned
to distinguish a modest improvement from no effect. So a half-measure is not
worth testing here: it would consume both remaining cohorts and return an
uninterpretable null. Either design the intervention to plausibly move adoption
by 7+ points, or measure adoption observationally and skip the RCT.

Note this figure ignores attrition. A 20% loss to follow-up would push the
detectable effect meaningfully higher, and should be built into the sizing before
anything is committed.

## Decision framework

The intervention should be considered successful only if it:

- increases digital adoption by at least 7 percentage points;
- does not reduce training completion or participant satisfaction;
- shows evidence of downstream enterprise value;
- has a feasible delivery cost per additional adopter;
- does not widen inequalities by sector, geography, device access, or baseline ability.

| Outcome | Programme decision |
|---|---|
| Adoption improves and delivery cost is feasible | Scale gradually |
| Adoption improves but delivery cost is high | Redesign delivery model |
| Adoption improves only temporarily | Extend follow-up and refine coaching |
| No meaningful effect with adequate power | Do not scale this intervention |
| Evidence is inconclusive | Extend evaluation |

## Risks I would flag before running this

1. **Coaching time is the real cost, and it is not free.** Three sessions across
   800 women is roughly 2,400 coach-hours. If the result is positive, the
   immediate question is whether that is affordable per participant. Log coach
   hours from day one so the endline answer is a cost-per-additional-adopter
   figure, not just a p-value.

2. **Sector confound.** Cohort 1 found retail and service businesses benefit more
   from e-commerce than agricultural ones, and cohorts 2–3 already target
   e-commerce training by sector. If sector mix differs between arms, that alone
   can produce or mask an effect — the Simpson's paradox case in the tool.
   Stratify by sector and report within-sector results.

3. **Novelty in coaching.** Attention from a coach can lift short-term behaviour
   that fades once it stops. Adoption measured at endline may overstate durable
   effect; the six-month follow-up is what distinguishes them.

4. **Self-reported adoption.** See the outcome definition above — verification
   against observable artefacts matters most in the arm receiving extra attention.

5. **Underpowered subgroup questions.** Splitting 800 per arm by sector or device
   access drops each cell well below what the power table supports. Subgroup
   results are hypothesis-generating for the next cohort, not findings.

6. **Equity risk.** An intervention requiring a personal smartphone may work best
   for women who already have one — improving the average while widening the gap
   among the most excluded. Report adoption by baseline device access explicitly.

## What I would monitor

- **Allocation balance (SRM)** from week one. With coach scheduling driving
  assignment, drift out of 1:1 is a live operational risk.
- **Adoption by arm**, read at the pre-registered endline — not on a rolling
  significance test. The Peeking scenario is exactly the failure mode to avoid,
  and with a fixed cohort there is no second chance.
- **Coach hours per participant**, to convert any positive result into
  cost-per-additional-adopter.
- **Enterprise revenue at endline and follow-up**, measured directly. An adoption
  increase would be an encouraging intermediate outcome, but revenue should be
  measured separately rather than inferred mechanically from adoption.
- **Whether the gap closes or merely shifts.** If coaching lifts everyone equally
  and the 13-point gender gap survives, the intervention improved the programme
  without solving the problem it was chosen for. That distinction should be
  reported explicitly, not buried in an average.

## Limitations

- No participant-level DIGITISE data was available. All figures are published
  cohort 1 aggregates; the power calculations are my own, computed against those
  aggregates using `power.py`.
- Participant counts for cohorts 2 and 3 are inferred from programme totals.
  Real enrolment figures would change the sizing table.
- The confidence-versus-interest hypothesis rests on indirect evidence and is
  offered as testable, not established.
- Delivery cost is central to the recommendation and could not be estimated —
  no public figure exists.
- Attrition is not modelled.

Full source-by-source breakdown in [ASSUMPTIONS.md](ASSUMPTIONS.md).

¹ Hand in Hand International, *DIGITISE: Initial results for Hand in Hand's
business accelerator in Nairobi*, in partnership with Happel Foundation.
² GSMA, 2024, cited in the same report.
