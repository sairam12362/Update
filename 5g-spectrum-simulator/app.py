#!/usr/bin/env python
"""Spectrum Allocation Benchmark — Streamlit dashboard.

    streamlit run app.py

Presentation lives in ``ui/`` (tokens, components, figures), data access in
``core/``, and one module per page in ``views/``. No physics is implemented
here: every number comes from ``results/`` or from a live episode run through
``core.sim``.
"""
from __future__ import annotations

from typing import Optional, Tuple

import streamlit as st

from core import results as R
from spectrum.config import CONGESTION_REGIMES
from ui import components as C
from ui import theme
from ui.nav import DEFAULT_PAGE, NAV_PAGES
from views import ablation, live, methodology, overview, predictor

st.set_page_config(
    page_title="Spectrum Allocation Benchmark",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject()
st.session_state.setdefault("page", DEFAULT_PAGE)

SOURCES: Tuple[str, ...] = (
    "results/headline.csv",
    "results/ablation.csv",
    "results/kpi_by_regime.csv",
    "results/predictor_accuracy.csv",
)

SCOPE_OPTIONS: Tuple[str, ...] = ("All regimes", "Low", "Medium", "High", "Peak")
SINGLE_REGIME_OPTIONS: Tuple[str, ...] = ("Low", "Medium", "High", "Peak")
SCOPE_TO_LEVEL = {"Low": "low", "Medium": "medium", "High": "high", "Peak": "peak"}

#: Radio configuration shown in the header, from the SimConfig defaults.
HEADER_FIELDS: Tuple[Tuple[str, str], ...] = (
    ("band", "3.5 GHz"),
    ("carrier", "100 MHz"),
    ("SCS", "30 kHz"),
    ("RBG", "18"),
    ("slot", "0.5 ms"),
)


def _seed_count() -> int:
    frame = R.kpi()
    if frame is None or "seed" not in frame:
        return 8
    return int(frame["seed"].nunique())


def _scope_fields(selection: str, page: str) -> list:
    """The fields beside the regime selector, scoped to what the page reads."""
    seeds = _seed_count()
    tail = (
        ("episode", "1 seed, paired")
        if page == "Live Simulation"
        else ("seeds", f"{seeds} \u00d7 1000 slots")
    )
    level = SCOPE_TO_LEVEL.get(selection)
    if level is None:
        regimes = [CONGESTION_REGIMES[name] for name in R.LEVELS]
        ues = [regime.n_ue for regime in regimes]
        loads = [regime.load_multiplier for regime in regimes]
        duties = [regime.incumbent_duty_cycle for regime in regimes]
        return [
            ("UEs", f"{min(ues)}\u2013{max(ues)}"),
            ("load", f"\u00d7{min(loads):.2f}\u2013{max(loads):.2f}"),
            ("duty", f"{min(duties):.0%}\u2013{max(duties):.0%}"),
            tail,
        ]
    regime = CONGESTION_REGIMES[level]
    return [
        ("UEs", str(regime.n_ue)),
        ("load", f"\u00d7{regime.load_multiplier:.2f}"),
        ("incumbent duty", f"{regime.incumbent_duty_cycle:.0%}"),
        tail,
    ]


def _sidebar() -> str:
    with st.sidebar:
        st.markdown(C.brand_html(), unsafe_allow_html=True)
        with st.container(key="nav"):
            page = st.radio(
                "Navigation",
                NAV_PAGES,
                key="page",
                label_visibility="collapsed",
            )
        st.markdown(
            C.sources_html(SOURCES, R.artifacts_present()),
            unsafe_allow_html=True,
        )
    return page


def _scope_bar(page: str) -> Optional[str]:
    #: A live episode runs one regime, so "All regimes" is not offered there.
    single_regime_page = page == "Live Simulation"
    options = SINGLE_REGIME_OPTIONS if single_regime_page else SCOPE_OPTIONS
    with st.container(key="scope"):
        left, right = st.columns([0.36, 0.64], vertical_alignment="center")
        with left:
            selection = st.radio(
                "Regime",
                options,
                horizontal=True,
                index=2 if single_regime_page else 0,
                key=f"scope_{page}",
            )
        with right:
            st.markdown(
                C.scope_fields(_scope_fields(selection, page)),
                unsafe_allow_html=True,
            )
    return SCOPE_TO_LEVEL.get(selection)


def _page(page: str, level: Optional[str]) -> None:
    if page == "Overview":
        overview.render(level)
    elif page == "Live Simulation":
        live.render(level)
    elif page == "Predictor":
        predictor.render(level)
    elif page == "Ablation":
        ablation.render(level)
    else:
        methodology.render(level)


def main() -> None:
    page = _sidebar()
    st.markdown(C.page_header(page, HEADER_FIELDS), unsafe_allow_html=True)
    level = _scope_bar(page)

    with st.container(key="content"):
        _page(page, level)


if __name__ == "__main__":
    main()
