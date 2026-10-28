"""Page registry and navigation callbacks."""

from __future__ import annotations

from typing import Tuple

import streamlit as st

NAV_PAGES: Tuple[str, ...] = (
    "Overview",
    "Live Simulation",
    "Predictor",
    "Ablation",
    "Methodology",
)

DEFAULT_PAGE = "Overview"


def goto(page: str) -> None:
    """Runs as a button callback, so it is safe to write widget state."""
    if page in NAV_PAGES:
        st.session_state["page"] = page


def toggle(key: str) -> None:
    st.session_state[key] = not st.session_state.get(key, False)
