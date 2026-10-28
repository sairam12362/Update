"""Live Simulation: one paired episode, then its stored KPIs and occupancy.

Both allocators face the same seed, traffic realisation and incumbent
trajectory, which is what makes the two columns comparable. A single episode
carries no paired test, so this page never prints significance markers.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st

from core import results as R
from core import sim
from spectrum.config import SimConfig
from ui import charts
from ui import components as C

#: (label, summary key, higher is better, unit)
KPI_ROWS = (
    ("QoS satisfaction", "qos_satisfaction_pct", True, "%"),
    ("Goodput", "goodput_mbps", True, "Mb/s"),
    ("Spectral efficiency", "spectral_efficiency_bps_hz", True, "b/s/Hz"),
    ("Deadline misses", "deadline_miss_pct", False, "%"),
    ("p99 delay", "p99_delay_ms", False, "ms"),
    ("Incumbent collisions", "collision_pct", False, "%"),
    ("Wasted vacancy", "wasted_vacancy_pct", False, "%"),
    ("Jain fairness", "jain_fairness", True, ""),
    ("Allocation waste", "allocation_waste_pct", False, "%"),
)

SERIES_METRICS = ("Goodput (Mb/s)", "In-budget UEs (%)", "Jain fairness", "Collisions")


def _configurator(level: str) -> None:
    registry = sim.allocator_registry()
    names = list(registry)
    agent = sim.load_agent()
    default_b = names.index(agent.name) if agent is not None and agent.name in names else len(names) - 1
    #: The baseline the benchmark compares against is M-LWDF, not the weakest rule.
    default_a = names.index("M-LWDF") if "M-LWDF" in names else 0

    with st.container(key="plate_config"):
        st.markdown(
            C.section_head(
                "Paired episode configuration",
                f"{level} regime, same seed, traffic realisation and incumbent trajectory",
            ),
            unsafe_allow_html=True,
        )
        left, swap, right = st.columns([1, 0.08, 1], vertical_alignment="bottom")
        with left:
            st.selectbox("Allocator A", names, index=default_a, key="live_name_a")
        with swap:
            st.markdown('<div class="swap">\u21c4</div>', unsafe_allow_html=True)
        with right:
            st.selectbox("Allocator B", names, index=default_b, key="live_name_b")

        slots_col, seed_col, run_col = st.columns([1.2, 0.8, 1.1], vertical_alignment="bottom")
        with slots_col:
            st.slider("Slots", 200, 2000, 600, step=100, key="live_slots")
        with seed_col:
            st.number_input("Seed", 0, 10_000, 42, step=1, key="live_seed")
        with run_col:
            run = st.button("Run paired episode", type="primary", key="live_run_button")

    if not run:
        return

    cfg = SimConfig(
        congestion=level,
        seed=int(st.session_state["live_seed"]),
        slots_per_episode=int(st.session_state["live_slots"]),
    )
    with st.spinner("Running paired episode…"):
        result_a = sim.simulate(registry[st.session_state["live_name_a"]], cfg, int(st.session_state["live_seed"]))
        result_b = sim.simulate(registry[st.session_state["live_name_b"]], cfg, int(st.session_state["live_seed"]))
    st.session_state["live_run"] = {
        "a": result_a,
        "b": result_b,
        "name_a": st.session_state["live_name_a"],
        "name_b": st.session_state["live_name_b"],
        "level": level,
        "slots": int(st.session_state["live_slots"]),
        "seed": int(st.session_state["live_seed"]),
    }


def _empty_state() -> None:
    st.markdown(
        '<div class="empty-state">No paired episode in this session. '
        "Running one compares two allocators on identical traffic and incumbent traces.</div>",
        unsafe_allow_html=True,
    )


def _comparison(run: dict) -> None:
    name_a, name_b = run["name_a"], run["name_b"]
    summary_a, summary_b = run["a"]["summary"], run["b"]["summary"]

    rows = []
    for label, key, higher_is_better, unit in KPI_ROWS:
        value_a, value_b = float(summary_a[key]), float(summary_b[key])
        delta = (value_b - value_a) if higher_is_better else (value_a - value_b)
        relative = (100.0 * delta / abs(value_a)) if value_a else None
        if relative is None:
            change = "\u2014"
        elif abs(relative) < 0.05:
            change = "0.0% equal"
        else:
            change = f"{relative:+.1f}% {'better' if relative > 0 else 'worse'}"
        suffix = "" if not unit else ("%" if unit == "%" else f" {unit}")
        rows.append(
            {
                "cells": [
                    C.esc(label),
                    f"{R.f3(value_a)}{suffix}",
                    f"{R.f3(value_b)}{suffix}",
                    change,
                ]
            }
        )

    columns = [
        {"label": "Metric", "width": "220px"},
        {"label": name_a, "num": True},
        {"label": name_b, "num": True},
        {"label": "Change, + better", "num": True},
    ]
    config = (
        f"{run['level']} regime · {run['slots']} slots · {run['slots'] * 0.5:.0f} ms simulated "
        f"· seed {run['seed']} · single episode, no paired test"
    )
    with st.container(key="plate_kpi"):
        st.markdown(
            C.section_head("Paired episode KPIs", config) + C.matrix_table(columns, rows),
            unsafe_allow_html=True,
        )


def _occupancy(run: dict) -> None:
    cfg: SimConfig = run["a"]["cfg"]
    window = min(240, cfg.slots_per_episode)
    with st.container(key="plate_occ"):
        st.markdown(
            C.section_head(
                "Spectrum occupancy",
                f"18 RBG × first {window} of {cfg.slots_per_episode} slots · muted, clean TX, collision",
            ),
            unsafe_allow_html=True,
        )
        figure = charts.occupancy_figure(run["a"], run["b"], cfg, run["name_a"], run["name_b"])
        st.pyplot(figure, width="stretch")


def _series(run: dict) -> None:
    with st.container(key="plate_series"):
        header, control = st.columns([3, 1.2], vertical_alignment="center")
        with header:
            st.markdown(
                C.section_head("Per-slot series", "20-slot rolling mean, shared axis"),
                unsafe_allow_html=True,
            )
        with control:
            metric = st.selectbox("Signal", SERIES_METRICS, index=0, key="live_series_metric", label_visibility="collapsed")
        figure = charts.series_figure(
            run["a"]["series"],
            run["b"]["series"],
            metric,
            run["name_a"],
            run["name_b"],
        )
        st.pyplot(figure, width="stretch")


def render(level: Optional[str]) -> None:
    regime_level = level or R.DEFAULT_LEVEL
    _configurator(regime_level)

    run = st.session_state.get("live_run")
    if run is None:
        _empty_state()
        return

    if run["level"] != regime_level:
        st.info(
            f"Showing the stored {run['level']} run. Selecting a regime does not rerun the episode."
        )
    _comparison(run)
    _occupancy(run)
    _series(run)
