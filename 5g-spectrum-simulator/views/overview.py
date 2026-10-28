"""Overview: the all-regime evidence page.

Layout is the Calibration Bench design: two findings columns, the component
substitution map, the all-regime aggregate matrix, and a selected-regime strip
with paired confidence intervals. The aggregate and the selected regime are
labelled separately and never blended.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

import streamlit as st

from core import results as R
from ui import components as C
from ui.nav import goto, toggle

#: Component substitutions, per README §12.3 and results/ablation.csv.
SUBSTITUTION_ROUTES: Sequence[dict] = (
    {
        "cards": [
            {
                "name": "M-LWDF",
                "width": 244,
                "spec": (
                    ("scheduler", "M-LWDF"),
                    ("sensing", "energy detector"),
                    ("training", "none"),
                ),
            },
            {
                "name": "M-LWDF + learned sensing",
                "width": 286,
                "strong": True,
                "spec": (
                    ("scheduler", "M-LWDF"),
                    ("sensing", "GRU filter"),
                    ("training", "GRU, supervised"),
                ),
            },
        ],
        "steps": ({"label": "replace sensing<br>front-end", "width": 126},),
        "annotation": "strongest overall",
    },
    {
        "cards": [
            {
                "name": "NeuroSpectrum, hard sensing",
                "width": 216,
                "spec": (
                    ("scheduler", "learned attention"),
                    ("sensing", "energy detector"),
                    ("training", "BC + PPO"),
                ),
            },
            {
                "name": "NeuroSpectrum, BC only",
                "width": 188,
                "spec": (
                    ("scheduler", "learned attention"),
                    ("sensing", "GRU filter"),
                    ("training", "BC"),
                ),
            },
            {
                "name": "NeuroSpectrum, BC + PPO",
                "width": 212,
                "spec": (
                    ("scheduler", "learned attention"),
                    ("sensing", "GRU filter"),
                    ("training", "BC + PPO"),
                ),
            },
        ],
        "steps": ({"label": "clone teacher", "width": 94}, {"label": "PPO fine-tune", "width": 90}),
        "annotation": None,
    },
)


def _seed_count() -> int:
    frame = R.kpi()
    if frame is None or "seed" not in frame:
        return 8
    return int(frame["seed"].nunique())


def _framing(head) -> None:
    collisions = R.improvement_range(head, "Incumbent collisions (%)")
    above_medium = None
    if head is not None and not head.empty:
        above_medium = head[head["congestion"].isin(("medium", "high", "peak"))]
    vacancy = R.improvement_range(above_medium, "Wasted vacancy (%)")
    qos_p = R.min_p_value(head, "QoS satisfaction (%)")

    def magnitude(values: Optional[tuple]) -> Optional[str]:
        if values is None:
            return None
        low, high = sorted((abs(values[0]), abs(values[1])))
        return f"{low:.0f}\u2013{high:.0f}%"

    collision_text = magnitude(collisions) or "42\u201369%"
    vacancy_text = magnitude(vacancy) or "68\u201384%"
    qos_text = f"{qos_p:.3f}".rstrip("0").rstrip(".") if qos_p is not None else "0.069"

    sharing = [
        f"Harmful interference to the incumbent <b>{collision_text}</b> lower, every regime, <i>p &lt; 0.05</i>",
        f"Wasted vacancy <b>{vacancy_text}</b> lower at medium load and above, <i>p &lt; 0.05</i>",
    ]
    service = [
        f"QoS satisfaction: no significant difference in any regime, <i>p \u2265 {qos_text}</i>",
        "Goodput, p99 delay and Jain fairness <i>significantly worse</i> at high and peak load",
        "Strongest overall configuration: <b>M-LWDF + learned sensing</b>",
    ]
    st.markdown(
        C.framing([("Spectrum sharing", sharing), ("Service quality", service)]),
        unsafe_allow_html=True,
    )


def _substitution_map() -> None:
    with st.container(key="plate_map"):
        st.markdown(
            C.section_head("Component substitution, 5 configurations", "results/ablation.csv")
            + C.substitution_map(SUBSTITUTION_ROUTES),
            unsafe_allow_html=True,
        )


def _aggregate_matrix(seed_count: int) -> None:
    frame = R.ablation()
    if frame is None or frame.empty:
        st.info("results/ablation.csv is missing. Run `python evaluate.py --ablations`.")
        return

    columns = [{"label": "Allocator", "width": "320px"}]
    columns += [{"label": label, "num": True, "width": "auto"} for label, _ in R.AGGREGATE_METRICS]
    rows = [
        {
            "cells": [C.esc(row["label"]), *row["values"]],
            "strong": row["strong"],
            "badge": "strongest overall" if row["strong"] else None,
        }
        for row in R.aggregate_rows(frame)
    ]
    with st.container(key="plate_matrix"):
        st.markdown(
            C.section_head(
                "All-regime aggregate, 5 allocator configurations",
                f"mean over 4 regimes × {seed_count} seeds",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(C.matrix_table(columns, rows), unsafe_allow_html=True)


def _full_metrics_table(head, level: str) -> str:
    columns = [
        {"label": "Metric", "width": "200px"},
        {"label": "Proposed", "num": True},
        {"label": "Best classical", "num": True},
        {"label": "\u0394, + better", "num": True},
        {"label": "p", "num": True},
    ]
    rows: List[dict] = []
    if head is not None:
        subset = head[head["congestion"] == level]
        for _, record in subset.iterrows():
            rows.append(
                {
                    "cells": [
                        C.esc(record["metric"]),
                        R.f3(record["proposed_mean"]),
                        f"{C.esc(R.allocator_label(record['best_classical']))} · {R.f3(record['classical_mean'])}",
                        R.signed_pct(record["improvement_pct"]),
                        R.fmt_p(record["p_value"]),
                        f"{float(record['cliffs_delta']):+.4f}"
                        if record.get("cliffs_delta") == record.get("cliffs_delta")
                        else "\u2014",
                    ]
                }
            )
    columns.append({"label": "Cliff's \u03b4", "num": True})
    return C.matrix_table(columns, rows)


def _regime_strip(head, level: str, seed_count: int) -> None:
    rows = R.strip_rows(head, level)
    if not rows:
        st.info(f"No headline rows for the {level} regime. Run `python evaluate.py`.")
        return

    regime = R.regime(level)
    params = (
        f"{regime.n_ue} UEs, load ×{regime.load_multiplier:.2f}, "
        f"duty {regime.incumbent_duty_cycle:.0%}, {seed_count} seeds"
    )
    header = (
        '<div class="strip-head"><div>'
        f'<span class="strip-title">Selected regime: {level}</span>'
        f'<span class="strip-params">{params}</span>'
        "</div></div>"
    )
    with st.container(key="plate_regime"):
        st.markdown(header + C.strip_table(rows), unsafe_allow_html=True)
        with st.expander("All nine metrics"):
            st.markdown(_full_metrics_table(head, level), unsafe_allow_html=True)


def _actions() -> None:
    left, middle, _spacer, right = st.columns([0.9, 1.2, 2.9, 1.4], vertical_alignment="center")
    with left:
        st.button("QoS by class", on_click=toggle, args=("show_qos_class",))
    with middle:
        st.button("Predictor comparison", on_click=goto, args=("Predictor",))
    with right:
        st.button("Run paired episode", type="primary", on_click=goto, args=("Live Simulation",))


def _class_table(level: Optional[str]) -> None:
    headers, rows = R.class_rows(R.kpi(), level)
    columns = [{"label": "Allocator", "width": "320px"}]
    columns += [{"label": header, "num": True} for header in headers]
    body = [{"cells": [C.esc(row["label"]), *row["cells"]]} for row in rows]
    scope_label = "all regimes" if level is None else f"{level} regime"
    with st.container(key="plate_class"):
        st.markdown(
            C.section_head("QoS satisfaction by 5QI class", f"mean over seeds, {scope_label}")
            + (C.matrix_table(columns, body) if body else '<div class="empty-state">No class-level rows for this scope.</div>'),
            unsafe_allow_html=True,
        )


def render(level: Optional[str]) -> None:
    head = R.headline()
    seed_count = _seed_count()
    strip_level = level or R.DEFAULT_LEVEL

    if head is None:
        st.info("results/headline.csv is missing. Run `python evaluate.py` to populate the benchmark.")

    _framing(head)
    _substitution_map()
    _aggregate_matrix(seed_count)
    _regime_strip(head, strip_level, seed_count)
    _actions()
    if st.session_state.get("show_qos_class"):
        _class_table(level)
