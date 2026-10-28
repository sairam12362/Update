"""Ablation: which component actually moves the metrics."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from core import results as R
from ui import components as C


def _matrix(frame) -> None:
    columns = [{"label": "Allocator", "width": "320px"}]
    columns += [{"label": label, "num": True} for label, _ in R.AGGREGATE_METRICS]
    rows = [
        {
            "cells": [C.esc(row["label"]), *row["values"]],
            "strong": row["strong"],
            "badge": "strongest overall" if row["strong"] else None,
        }
        for row in R.aggregate_rows(frame)
    ]
    with st.container(key="plate_abl"):
        st.markdown(
            C.section_head(
                "Component decomposition, 5 configurations",
                "mean over 4 regimes × 8 seeds · aggregate, no paired test in this file",
            )
            + C.matrix_table(columns, rows),
            unsafe_allow_html=True,
        )


def _transition(frame) -> None:
    labels = [R.allocator_label(name) for name in frame["allocator"]]
    left, right = st.columns([1, 1], vertical_alignment="bottom")
    with left:
        before = st.selectbox("Before", labels, index=0, key="ablation_before")
    with right:
        after = st.selectbox("After", labels, index=1, key="ablation_after")

    row_before = frame.iloc[labels.index(before)]
    row_after = frame.iloc[labels.index(after)]

    rows = []
    for label, column in R.AGGREGATE_METRICS:
        value_before = float(row_before[column])
        value_after = float(row_after[column])
        absolute = value_after - value_before
        relative = (100.0 * absolute / abs(value_before)) if value_before else None
        rows.append(
            {
                "cells": [
                    C.esc(label),
                    R.f3(value_before),
                    R.f3(value_after),
                    f"{absolute:+.3f}",
                    R.signed_pct(relative) if relative is not None else "\u2014",
                ]
            }
        )

    columns = [
        {"label": "Metric", "width": "220px"},
        {"label": before, "num": True},
        {"label": after, "num": True},
        {"label": "\u0394 absolute", "num": True},
        {"label": "\u0394 %", "num": True},
    ]
    with st.container(key="plate_transition"):
        st.markdown(
            C.section_head("Substitution effect", "same aggregate table, two rows")
            + C.matrix_table(columns, rows),
            unsafe_allow_html=True,
        )


def render(level: Optional[str]) -> None:
    frame = R.ablation()
    if frame is None or frame.empty:
        st.info("results/ablation.csv is missing. Run `python evaluate.py --ablations`.")
        return
    _matrix(frame)
    _transition(frame)
