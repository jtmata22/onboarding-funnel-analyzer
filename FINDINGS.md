# Findings and recommendation

**Question:** Hand in Hand International's DIGITISE programme proved digital
marketing training raises entrepreneur revenue. It did not close the gap in who
actually adopts the tools. What should cohorts 2 and 3 do about it, and can that
be tested rigorously at the programme's scale?

**Short answer:** Run a one-to-one digital coaching intervention against the
current group-training baseline, targeted at women. The programme has just
enough participants to detect an intervention that closes most of the gender gap
— and nowhere near enough to detect a modest one. That constraint should drive
the design: build the intervention to be decisive, not incremental.

---

## What the data shows

From the DIGITISE cohort 1 endline report:¹

| Finding | Figure |
|---|---|
| Revenue gain from digital marketing training | +$108 PPP/month vs. untrained |
| Trained participants who actually adopted digital practices | 49% |
| Adoption — men vs. women | 59% vs. 46% |
| Smartphone ownership — men vs. women | 92% vs. 75% |
| Kenya gender gap in daily mobile internet use² | 43% |

The training works for the people who use it. **The bottleneck is adoption, not
efficacy.** Slightly over half of trained entrepreneurs never adopted the
practices at all, and the shortfall is concentrated among women — who are over
80% of the programme's participants and its explicit target population.

Framed as a funnel, the drop-off is unambiguous:

```
Enrolled  ->  Trained in digital marketing  ->  Adopted digital practices  ->  Revenue gain
                                            ^
                                     54% of women lost here
```

Every downstream benefit is gated on a step where more than half of the intended
beneficiaries fall out. The 13-point gender gap in adoption (46% vs. 59%) sits
inside a national 43% gap in mobile internet use — so this is a headwind the
programme is pushing against, not a quirk of one cohort.

## Hypothesis

> Women's lower adoption is driven primarily by **confidence and access
> barriers** — not by lower interest or lower perceived value. A one-to-one
> coaching format that provides individual practice on the participant's own
> device will raise adoption among women substantially more than the current
> group training format.

Two pieces of evidence point at confidence rather than interest. Catherine, a
secondhand shop entrepreneur in the programme, describes the pattern directly:
having a smartphone, finding posting difficult at first, and getting there with
coaching.¹ And the 75% smartphone ownership figure among women means device
access explains only part of the 54% non-adoption — most women who did not adopt
*did* own a smartphone.

## Recommended experiment

| Parameter | Value |
|---|---|
| Population | Women in cohorts 2 and 3 (~1,600 of ~2,000 participants) |
| Control | Current group-based digital marketing training |
| Treatment | Group training + three one-to-one coaching sessions on own device |
| Primary metric | Adoption of digital practices at endline (binary) |
| Baseline | 46% |
| Allocation | 50/50, ~800 per arm |
| Guardrail metrics | Course completion, revenue, coach hours per participant |

### What this test can and cannot detect

Computed with this repo's `power.py` at α=0.05, 80% power:

| Target relative lift | Adoption | Needed per arm | Feasible at ~800/arm? |
|---|---|---|---|
| +10% | 46% → 51% | 1,849 | **No** — needs more women than the programme has |
| +15% | 46% → 53% | 821 | Marginal |
| +20% | 46% → 55% | 460 | Yes |
| +28% (closes the gender gap) | 46% → 59% | 228 | Yes, comfortably |

At 800 per arm the smallest detectable effect is **+15.2% relative (about 7
percentage points)**. Closing the gender gap entirely would be a +28% relative
lift, which this design detects at essentially 100% power.

**This is the central design finding.** The programme can prove a gap-closing
intervention works. It cannot prove a modest one works — a 5-point improvement
would return "no significant difference" even if entirely real. So a
half-measure is not worth testing here: it would consume both remaining cohorts
and produce an uninterpretable null. Either commit to an intervention intensive
enough to plausibly move adoption by 7+ points, or skip the RCT and measure
adoption observationally.

Sequencing note: cohorts 2 and 3 run consecutively. Randomising *within* each
cohort rather than assigning cohort 2 to control and cohort 3 to treatment is
essential — otherwise any seasonal or delivery change between cohorts is
perfectly confounded with the treatment.

## Risks I would flag before running this

1. **Coaching time is the real cost, and it is not free.** Three sessions across
   800 women is roughly 2,400 coach-hours. If the result is positive, the
   scaling question is immediately "can we afford this per participant?" I would
   log coach hours per participant as a guardrail from day one, so the endline
   answer is a cost-per-adoption figure and not just a p-value.

2. **Sector confound.** The cohort 1 report found retail and service businesses
   benefit more from e-commerce than agricultural ones, and cohorts 2 and 3
   already target e-commerce training by sector. If sector mix differs between
   arms, that alone can produce or mask an effect — this is the Simpson's paradox
   case in the tool. Stratify randomisation by sector, and report adoption within
   sector, not just pooled.

3. **Novelty in coaching.** Attention from a coach can lift short-term behaviour
   that fades once it stops. Adoption measured immediately at endline may
   overstate durable effect. The planned 12-month cohort 1 follow-up is the right
   instrument for this; I would measure adoption at endline *and* at 6 months.

4. **Self-reported adoption.** "Adopted digital practices" is likely
   self-reported, and participants who received extra coaching attention have
   more reason to report favourably. Where possible, verify against something
   observable — an active business page, a listing on an e-commerce platform.

5. **Underpowered subgroup questions.** Splitting 800 per arm by sector or by
   smartphone ownership drops each cell well below what the power table above
   supports. Subgroup results here are hypothesis-generating for cohort 3, not
   findings.

## What I would watch after launch

- **Adoption rate by arm, weekly** — but on a fixed endline read, not a rolling
  significance test. The Peeking scenario in this tool is exactly the failure
  mode to avoid here, and with a single cohort there is no second chance.
- **Allocation balance (SRM)** from week one. With coach scheduling driving
  assignment, drift out of 50/50 is a live risk, not a theoretical one.
- **Coach hours per participant**, to convert any positive result into
  cost-per-additional-adopter.
- **Revenue at endline**, as the confirmatory outcome. Adoption is the
  intermediate metric; the programme's actual goal is income. Cohort 1 gives the
  link between them (+$108 PPP/month), so an adoption gain of *n* points implies
  a predictable revenue gain — worth stating in advance and checking after.
- **Whether the gap closes or merely shifts.** If coaching lifts everyone equally
  and the 13-point gender gap survives, the intervention has improved the
  programme without solving the problem it was chosen for. That distinction
  should be reported explicitly, not buried in an average.

---

### Honest limitations of this analysis

- I did not have participant-level DIGITISE data. All figures above are the
  published cohort-1 aggregates; the power calculations are my own, computed
  against those aggregates using this repo's `power.py`.
- The hypothesis about confidence-versus-interest is inferred from a smartphone
  ownership figure and a single quoted participant. It is a starting hypothesis,
  not an established finding, and qualitative work with non-adopters from cohort
  1 would be the cheaper first step before committing both remaining cohorts to
  an RCT.
- Participant counts for cohorts 2 and 3 are inferred from the programme total
  (3,000 across three cohorts, 1,000 in cohort 1, over 80% women). Real
  enrolment numbers would change the power table.

¹ Hand in Hand International, *DIGITISE: Initial results for Hand in Hand's
business accelerator in Nairobi*, in partnership with Happel Foundation.
² GSMA, 2024, cited in the same report.
