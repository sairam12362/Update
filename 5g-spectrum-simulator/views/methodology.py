"""Methodology: parameters, traffic classes, the parity contract, provenance."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from core import results as R
from spectrum.config import CONGESTION_REGIMES, PARAMETER_PROVENANCE, TRAFFIC_CLASSES, SimConfig
from ui import components as C

OBSERVATION_FIELDS = (
    ("buffer_status", "bytes queued per UE"),
    ("head_of_line_delay", "age of the oldest queued packet"),
    ("qos_params", "5QI delay budget, error rate, priority"),
    ("cqi_reported", "aged and quantised channel quality"),
    ("sensing_bit", "hard output of one shared energy detector"),
    ("p_busy", "detector confidence, identical for every allocator"),
)

EXCLUDED_FIELDS = (
    ("incumbent.active", "true occupancy, consumed only by the physics and collision accounting"),
    ("incumbent.sojourn_draws", "the Markov transition matrix and sojourn samples"),
    ("channel.true_sinr", "unquantised, undelayed SINR"),
)

PHYSICAL_LAYER = (
    ("carrier frequency", "3.5 GHz (FR1 band n78)"),
    ("bandwidth", "100 MHz"),
    ("subcarrier spacing", "30 kHz"),
    ("resource block groups", "18 (273 PRB, RBG size 16)"),
    ("slot duration", "0.5 ms"),
    ("BS EIRP", "46 dBm, wide-area class"),
    ("cell radius", "350 m, UEs 35–350 m"),
    ("path loss", "TR 38.901 UMa NLOS, 5 dB log-normal shadowing"),
    ("link adaptation", "TS 38.214 table 2 at 10% BLER"),
    ("CQI report", "2 slots old, period 4 slots, 1 dB error"),
    ("HARQ", "3 retransmissions, 2.5 dB chase combining"),
    ("incumbent", "two-state semi-Markov per subband, mean ON 42 slots"),
    ("energy detector", "P_d = 0.85, P_fa = 0.12"),
)


def _traffic_table() -> str:
    columns = [
        {"label": "Class", "width": "150px"},
        {"label": "5QI", "num": True},
        {"label": "Delay budget", "num": True},
        {"label": "Error rate", "num": True},
        {"label": "Nominal rate", "num": True},
        {"label": "Priority", "num": True},
        {"label": "Population", "num": True},
    ]
    rows = [
        {
            "cells": [
                C.esc(tc.name),
                str(tc.five_qi),
                f"{tc.delay_budget_ms:.0f} ms",
                f"{tc.error_rate:.0e}",
                f"{tc.nominal_rate_mbps:g} Mb/s",
                str(tc.priority_level),
                f"{tc.population_share:.0%}",
            ]
        }
        for tc in TRAFFIC_CLASSES
    ]
    return C.matrix_table(columns, rows)


def _regime_table() -> str:
    columns = [
        {"label": "Regime", "width": "150px"},
        {"label": "UEs", "num": True},
        {"label": "Load ×", "num": True},
        {"label": "Incumbent duty", "num": True},
    ]
    rows = [
        {
            "cells": [
                C.esc(name),
                str(regime.n_ue),
                f"{regime.load_multiplier:.2f}",
                f"{regime.incumbent_duty_cycle:.0%}",
            ]
        }
        for name, regime in CONGESTION_REGIMES.items()
    ]
    return C.matrix_table(columns, rows)


def _provenance_table() -> str:
    columns = [{"label": "Parameter", "width": "46%"}, {"label": "Source"}]
    rows = [{"cells": [C.esc(key), C.esc(value)]} for key, value in PARAMETER_PROVENANCE.items()]
    return C.matrix_table(columns, rows)


def render(level: Optional[str]) -> None:
    physical, traffic, parity, provenance = st.tabs(
        ["Physical layer", "Traffic classes", "Information parity", "Provenance"]
    )

    with physical:
        with st.container(key="plate_radio"):
            st.markdown(
                C.section_head("Radio and incumbent parameters") + C.kv_table(PHYSICAL_LAYER),
                unsafe_allow_html=True,
            )
        with st.container(key="plate_regimes"):
            st.markdown(
                C.section_head("Congestion regimes") + _regime_table(),
                unsafe_allow_html=True,
            )

    with traffic:
        with st.container(key="plate_traffic"):
            st.markdown(
                C.section_head("5QI bearers", "TS 23.501 Table 5.7.4-1") + _traffic_table(),
                unsafe_allow_html=True,
            )

    with parity:
        st.markdown(
            '<div class="bench-plate prose">'
            "<p>Every allocator receives one frozen <code>Observation</code> object. The incumbent's "
            "true state is not a field of it: it is consumed only inside the physics and the "
            "collision accounting, and <code>tests/test_information_parity.py</code> asserts this "
            "mechanically, including a replay test that re-feeds recorded observations with no "
            "environment attached.</p></div>",
            unsafe_allow_html=True,
        )
        left, right = st.columns(2, vertical_alignment="top")
        with left:
            with st.container(key="plate_observed"):
                st.markdown(
                    C.section_head("Observed by every allocator")
                    + C.kv_table(OBSERVATION_FIELDS, key_width="38%"),
                    unsafe_allow_html=True,
                )
        with right:
            with st.container(key="plate_environment"):
                st.markdown(
                    C.section_head("Environment only")
                    + C.kv_table(EXCLUDED_FIELDS, key_width="42%"),
                    unsafe_allow_html=True,
                )

    with provenance:
        with st.container(key="plate_provenance"):
            st.markdown(
                C.section_head("Parameter provenance", "each constant traced to its specification")
                + _provenance_table(),
                unsafe_allow_html=True,
            )
