import altair as alt
import pandas as pd
import streamlit as st

from analysis import (
    detect_novelty,
    detect_peeking_risk,
    detect_simpsons_reversal,
    funnel_table,
    peeking_series,
    segment_breakdown,
    srm_check,
    step_dropoff_chi2,
    time_to_activate_stats,
    two_proportion_ztest,
    weekly_trend,
)
from data_loader import FUNNEL_STEPS, load_funnel_data
from power import detectable_effect, mde_curve, required_sample_size, weeks_required
from scenarios import SCENARIOS
from verdict import decide

st.set_page_config(page_title="Onboarding Experiment Designer", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    .block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 1100px; }
    h1 { font-weight: 700; letter-spacing: -0.02em; }
    div[data-testid="stMetricValue"] { font-weight: 600; }
    button[kind="primary"] {
        background-color: #E8EAED; color: #0E1116; border: none; border-radius: 6px;
        font-weight: 600; padding: 0.55rem 1.5rem; box-shadow: none;
        transition: background-color 0.15s ease;
    }
    button[kind="primary"]:hover { background-color: #FFFFFF; color: #0E1116; border: none; }
    button[kind="primary"]:focus:not(:active) { color: #0E1116; border: none; }
    button[kind="secondary"] {
        border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); font-weight: 500;
    }
    hr { margin: 2rem 0; border-color: rgba(255,255,255,0.08); }
    </style>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "intro"


def _go(page):
    st.session_state.page = page


def _verdict_banner(result):
    color = {"ship": "success", "extend": "warning", "no-ship": "error"}[result["verdict"]]
    getattr(st, color)(f"**{result['headline']}** — {result['reason']}")
    for w in result.get("warnings", []):
        st.warning(w)


def _nav():
    cols = st.columns([1, 1, 1, 1, 4])
    cols[0].button("Home", on_click=_go, args=("intro",), use_container_width=True)
    cols[1].button("Design", on_click=_go, args=("designer",), use_container_width=True)
    cols[2].button("Scenarios", on_click=_go, args=("scenarios",), use_container_width=True)
    cols[3].button("Analyze", on_click=_go, args=("dashboard",), use_container_width=True)


# ------------------------------------------------------------------- intro --
def render_intro():
    st.title("Onboarding Experiment Designer")
    st.subheader(
        "Size an onboarding experiment before you run it, pressure-test it "
        "against the ways A/B tests lie, and get a defensible decision."
    )
    st.write(
        """
Most experiment tooling tells you what happened after the fact. The harder
questions come earlier: **how long do we need to run this**, and **is this test
even capable of detecting the effect we care about?** Those are power and
minimum-detectable-effect questions, and simulation is the right instrument for
them — not a substitute for production data.

This tool does three things:
"""
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. Design**")
        st.caption(
            "Given your baseline conversion, weekly traffic, and the lift you'd "
            "actually act on, how many users and how many weeks until you can "
            "call it."
        )
    with c2:
        st.markdown("**2. Pressure-test**")
        st.caption(
            "Four preset experiments, each rigged to look like a clean win while "
            "hiding a specific failure mode. Watch the verdict engine catch each one."
        )
    with c3:
        st.markdown("**3. Analyze**")
        st.caption(
            "Full funnel breakdown with step-level significance testing and an "
            "automated ship / extend / don't-ship recommendation."
        )

    st.write("")
    b1, b2, b3 = st.columns([2, 2, 4])
    b1.button(
        "Design an experiment", type="primary", on_click=_go, args=("designer",),
        use_container_width=True,
    )
    b2.button(
        "See the traps", on_click=_go, args=("scenarios",), use_container_width=True
    )


# ---------------------------------------------------------------- designer --
def render_designer():
    _nav()
    st.title("Design an experiment")
    st.caption(
        "Answer the pre-launch questions: what can this test detect, and how long "
        "until it can detect it."
    )

    c1, c2, c3, c4 = st.columns(4)
    baseline = c1.number_input(
        "Baseline conversion (%)", 0.5, 99.0, 27.0, step=0.5,
        help="Current activation rate of the step you're trying to move.",
    ) / 100
    weekly_traffic = c2.number_input(
        "Weekly eligible users", 100, 1_000_000, 4000, step=100,
        help="New users per week who will actually enter the experiment.",
    )
    target_lift = c3.number_input(
        "Lift you'd act on (% relative)", 1.0, 200.0, 10.0, step=1.0,
        help="The smallest improvement that would actually change your decision.",
    ) / 100
    power_pct = c4.select_slider("Power", [0.70, 0.80, 0.90, 0.95], value=0.80)

    alpha = 0.05
    n_needed = required_sample_size(baseline, target_lift, alpha, power_pct)
    wks = weeks_required(n_needed, weekly_traffic)

    st.write("")
    m1, m2, m3 = st.columns(3)
    m1.metric("Users needed per arm", f"{n_needed:,}")
    m2.metric("Total users needed", f"{2 * n_needed:,}")
    m3.metric("Weeks to run", f"{wks:.1f}")

    if wks > 8:
        st.error(
            f"At {weekly_traffic:,} users/week this test needs **{wks:.1f} weeks** to "
            f"detect a {target_lift:.0%} lift. That is likely too long to be useful. "
            "Either target a bigger effect, find more traffic, or pick a metric "
            "higher in the funnel with a larger base rate."
        )
    elif wks > 4:
        st.warning(
            f"**{wks:.1f} weeks** is a long but workable run. Fix the end date now "
            "and commit to it — stopping early is what the Peeking scenario is about."
        )
    else:
        st.success(
            f"**{wks:.1f} weeks** to detect a {target_lift:.0%} relative lift "
            f"({baseline:.1%} to {baseline * (1 + target_lift):.1%}) at "
            f"{power_pct:.0%} power."
        )

    st.divider()

    st.subheader("What can I detect, by week?")
    st.caption(
        "The smallest relative lift this test could detect if you stopped at each "
        "week. Anything below the curve is invisible to you — the experiment would "
        "return 'no significant difference' even if the effect were real."
    )

    curve = mde_curve(baseline, weekly_traffic, max_weeks=12, alpha=alpha, power=power_pct)
    curve_df = pd.DataFrame(curve, columns=["week", "mde"])

    line = (
        alt.Chart(curve_df)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("week:Q", title="Weeks running", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("mde:Q", title="Detectable relative lift", axis=alt.Axis(format="%")),
            tooltip=[
                alt.Tooltip("week:Q", title="Week"),
                alt.Tooltip("mde:Q", format=".1%", title="Detectable lift"),
            ],
        )
    )
    target_rule = (
        alt.Chart(pd.DataFrame({"y": [target_lift]}))
        .mark_rule(strokeDash=[6, 4], color="#E8EAED")
        .encode(y="y:Q")
    )
    st.altair_chart((line + target_rule).properties(height=340), use_container_width=True)
    st.caption(
        "Dashed line is the lift you said you'd act on. Where the curve drops below "
        "it is the earliest you could responsibly read the result."
    )

    st.divider()
    st.subheader("If you only have N weeks")
    fixed_weeks = st.slider("Weeks available", 1, 12, 4)
    n_avail = int(weekly_traffic * fixed_weeks / 2)
    mde_avail = detectable_effect(baseline, n_avail, alpha, power_pct)
    d1, d2 = st.columns(2)
    d1.metric("Users per arm", f"{n_avail:,}")
    d2.metric("Smallest detectable lift", f"{mde_avail:.1%}")
    if mde_avail > target_lift:
        st.warning(
            f"In {fixed_weeks} weeks you can only detect a {mde_avail:.1%} lift, but "
            f"you said you'd act on {target_lift:.0%}. This test is underpowered for "
            "the decision you want to make — a null result would tell you nothing."
        )


# --------------------------------------------------------------- scenarios --
def render_scenarios():
    _nav()
    st.title("Pressure-test the verdict")
    st.caption(
        "Four experiments that each look like a clean, significant win. Every one "
        "of them is a trap. Load one and see what the headline number hides."
    )

    choice = st.radio(
        "Load a scenario",
        list(SCENARIOS.keys()),
        horizontal=True,
        label_visibility="collapsed",
        key="scenario_choice",
    )
    scenario = SCENARIOS[choice]()
    df = scenario["df"]

    st.subheader(scenario["title"])
    st.write(scenario["setup"])

    ztest = two_proportion_ztest(df)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Control", f"{ztest['control_rate']:.1%}")
    k2.metric("Treatment", f"{ztest['treatment_rate']:.1%}", f"{ztest['relative_lift']:+.1%}")
    k3.metric("p-value", f"{ztest['p_value']:.2e}")
    k4.metric("Users", f"{len(df):,}")

    st.info(f"**The naive read:** {scenario['naive_read']}")

    # run every guardrail; each scenario trips a different one
    srm = srm_check(df)
    guardrails = {"srm": srm}
    if df["segment"].nunique() > 1:
        guardrails["simpsons"] = detect_simpsons_reversal(df)
    if df["week"].nunique() > 1:
        guardrails["novelty"] = detect_novelty(df)
    if df["day"].nunique() > 1:
        guardrails["peeking"] = detect_peeking_risk(peeking_series(df))

    result = decide(ztest, len(df) // 2, guardrails)
    _verdict_banner(result)

    with st.expander("What the tool caught, and why it matters", expanded=True):
        st.markdown(f"**The trap:** {scenario['the_trap']}")
        st.markdown(f"**What to check:** {scenario['what_to_check']}")

    st.divider()

    key = scenario["key"]

    if key == "simpsons":
        st.subheader("Segment breakdown")
        segs = guardrails["simpsons"]["segments"]
        st.dataframe(
            segs.style.format(
                {
                    "control_rate": "{:.1%}",
                    "treatment_rate": "{:.1%}",
                    "relative_lift": "{:+.1%}",
                    "p_value": "{:.4f}",
                }
            ),
            hide_index=True,
            width="stretch",
        )
        melted = segs.melt(
            id_vars="segment",
            value_vars=["control_rate", "treatment_rate"],
            var_name="arm",
            value_name="rate",
        ).replace({"control_rate": "Control", "treatment_rate": "Treatment"})
        st.altair_chart(
            alt.Chart(melted)
            .mark_bar()
            .encode(
                x=alt.X("segment:N", title="Segment"),
                y=alt.Y("rate:Q", title="Activation rate", axis=alt.Axis(format="%")),
                color=alt.Color("arm:N", title=""),
                xOffset="arm:N",
            )
            .properties(height=300),
            use_container_width=True,
        )
        st.subheader("Segment mix per arm — the actual cause")
        mix = guardrails["simpsons"]["segment_mix"]
        st.dataframe(mix.style.format("{:.1%}"), width="stretch")
        st.caption(
            "The arms are not comparable populations. Any pooled comparison between "
            "them is measuring the mix difference, not the treatment."
        )

    elif key == "novelty":
        st.subheader("Lift by week")
        trend = guardrails["novelty"]["trend"]
        st.dataframe(
            trend.style.format(
                {
                    "control_rate": "{:.1%}",
                    "treatment_rate": "{:.1%}",
                    "relative_lift": "{:+.1%}",
                    "p_value": "{:.4f}",
                }
            ),
            hide_index=True,
            width="stretch",
        )
        base = alt.Chart(trend)
        st.altair_chart(
            (
                base.mark_line(point=True, strokeWidth=2).encode(
                    x=alt.X("week:Q", title="Week", axis=alt.Axis(tickMinStep=1)),
                    y=alt.Y("relative_lift:Q", title="Relative lift", axis=alt.Axis(format="%")),
                )
                + base.mark_rule(strokeDash=[6, 4], color="#888").encode(
                    y=alt.datum(0)
                )
            ).properties(height=320),
            use_container_width=True,
        )
        st.caption(
            "Pooling these four weeks into one number reports a win. The trend says "
            "the effect is already gone."
        )

    elif key == "srm":
        st.subheader("Allocation check")
        a1, a2, a3 = st.columns(3)
        a1.metric("Control users", f"{srm['n_control']:,}")
        a2.metric("Treatment users", f"{srm['n_treatment']:,}")
        a3.metric("Split", f"{srm['observed_split']:.1%} / {1 - srm['observed_split']:.1%}")
        st.metric("SRM p-value", f"{srm['p_value']:.2e}")
        st.caption(
            "Run this check before reading any result. It is cheap, and it is the "
            "difference between a real finding and a plumbing bug."
        )

    elif key == "peeking":
        st.subheader("p-value over the life of the experiment")
        series = peeking_series(df)
        base = alt.Chart(series)
        st.altair_chart(
            (
                base.mark_line(strokeWidth=2).encode(
                    x=alt.X("day:Q", title="Day of experiment"),
                    y=alt.Y("p_value:Q", title="Cumulative p-value", scale=alt.Scale(domain=[0, 1])),
                    tooltip=[
                        "day",
                        alt.Tooltip("p_value:Q", format=".3f"),
                        alt.Tooltip("relative_lift:Q", format="+.1%"),
                    ],
                )
                + base.mark_rule(strokeDash=[6, 4], color="#E8555A").encode(y=alt.datum(0.05))
            ).properties(height=340),
            use_container_width=True,
        )
        risk = guardrails["peeking"]
        st.caption(
            f"Red line is p = 0.05. This experiment has a true effect of zero, yet it "
            f"dipped below the line on day {risk['first_crossing_day']} and stayed "
            f"significant for {risk['days_significant']} days total, ending at "
            f"p = {risk['final_p_value']:.3f}. Any team checking daily would have "
            "shipped a change that does nothing."
        )


# --------------------------------------------------------------- dashboard --
def render_dashboard():
    _nav()
    st.title("Analyze a funnel")
    st.caption(
        "Compares a Control onboarding flow against a Treatment (redesigned) flow "
        "and recommends whether to ship, extend the test, or roll it back."
    )

    with st.sidebar:
        st.header("Experiment setup")
        n_per_group = st.slider("Users per group", 500, 20000, 6000, step=500)

        st.subheader("Control flow step-through rates")
        control_probs = [
            st.slider(f"{step}", 0.0, 1.0, default, key=f"c_{i}")
            for i, (step, default) in enumerate(
                zip(FUNNEL_STEPS, [1.0, 0.72, 0.55, 0.40, 0.27])
            )
        ]

        st.subheader("Treatment flow step-through rates")
        treatment_probs = [
            st.slider(f"{step}", 0.0, 1.0, default, key=f"t_{i}")
            for i, (step, default) in enumerate(
                zip(FUNNEL_STEPS, [1.0, 0.80, 0.68, 0.50, 0.34])
            )
        ]

        seed = st.number_input("Random seed", value=42, step=1)

    df = load_funnel_data(
        n_per_group=n_per_group,
        control_probs=tuple(control_probs),
        treatment_probs=tuple(treatment_probs),
        seed=seed,
    )

    ztest = two_proportion_ztest(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control activation", f"{ztest['control_rate']:.1%}")
    col2.metric(
        "Treatment activation",
        f"{ztest['treatment_rate']:.1%}",
        f"{ztest['relative_lift']:+.1%} relative",
    )
    col3.metric("p-value", f"{ztest['p_value']:.4f}")
    col4.metric("Sample size / group", f"{n_per_group:,}")

    _verdict_banner(decide(ztest, n_per_group, {"srm": srm_check(df)}))

    st.divider()

    st.subheader("Funnel by step")
    funnel_c = funnel_table(df, "Control").assign(group="Control")
    funnel_t = funnel_table(df, "Treatment").assign(group="Treatment")
    funnel_all = pd.concat([funnel_c, funnel_t], ignore_index=True)

    st.altair_chart(
        alt.Chart(funnel_all)
        .mark_bar()
        .encode(
            x=alt.X("step:N", sort=FUNNEL_STEPS, title="Funnel step"),
            y=alt.Y("pct_of_total:Q", title="% of users reaching step", axis=alt.Axis(format="%")),
            color=alt.Color("group:N", title="Group"),
            xOffset="group:N",
            tooltip=[
                "group",
                "step",
                alt.Tooltip("users_reached:Q", title="Users"),
                alt.Tooltip("pct_of_total:Q", format=".1%", title="% of total"),
                alt.Tooltip("drop_off:Q", format=".1%", title="Drop-off from prior step"),
            ],
        )
        .properties(height=380),
        use_container_width=True,
    )

    left, right = st.columns(2)
    for col, table, label in ((left, funnel_c, "Control"), (right, funnel_t, "Treatment")):
        with col:
            st.markdown(f"**{label} — step detail**")
            st.dataframe(
                table[["step", "users_reached", "pct_of_total", "drop_off"]].style.format(
                    {"pct_of_total": "{:.1%}", "drop_off": "{:.1%}"}
                ),
                hide_index=True,
                width="stretch",
            )

    st.divider()

    st.subheader("Where is the drop-off significantly different?")
    step_rows = []
    for i, step in enumerate(FUNNEL_STEPS):
        if i == 0:
            continue
        test = step_dropoff_chi2(df, i)
        step_rows.append({"step": step, "chi2": test["chi2"], "p_value": test["p_value"]})
    step_df = pd.DataFrame(step_rows)
    step_df["significant (p<0.05)"] = step_df["p_value"] < 0.05
    st.dataframe(
        step_df.style.format({"chi2": "{:.2f}", "p_value": "{:.4f}"}),
        hide_index=True,
        width="stretch",
    )

    st.divider()

    st.subheader("Time to activate")
    tta = time_to_activate_stats(df)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(
            tta.style.format({"median": "{:.1f} days", "mean": "{:.1f} days"}),
            hide_index=True,
            width="stretch",
        )
    with c2:
        st.altair_chart(
            alt.Chart(df[df["activated"]])
            .mark_bar(opacity=0.7)
            .encode(
                x=alt.X("days_to_activate:Q", bin=alt.Bin(maxbins=30), title="Days to activate"),
                y=alt.Y("count():Q", title="Users"),
                color="group:N",
            )
            .properties(height=260),
            use_container_width=True,
        )

    st.divider()

    st.subheader("Activation rate by acquisition channel")
    by_channel = (
        df.groupby(["acquisition_channel", "group"])["activated"].mean().reset_index()
    )
    st.altair_chart(
        alt.Chart(by_channel)
        .mark_bar()
        .encode(
            x=alt.X("acquisition_channel:N", title="Channel"),
            y=alt.Y("activated:Q", title="Activation rate", axis=alt.Axis(format="%")),
            color="group:N",
            xOffset="group:N",
            tooltip=["acquisition_channel", "group", alt.Tooltip("activated:Q", format=".1%")],
        )
        .properties(height=300),
        use_container_width=True,
    )

    st.caption(
        "Baseline rates are documented in ASSUMPTIONS.md. Adjust the sliders to "
        "model a different onboarding design."
    )


PAGES = {
    "intro": render_intro,
    "designer": render_designer,
    "scenarios": render_scenarios,
    "dashboard": render_dashboard,
}
PAGES[st.session_state.page]()
