"""Predictor: energy detector vs learned GRU vs the Bayes-optimal bound."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from core import results as R
from ui import charts
from ui import components as C

#: (label, column, decimals) for the estimator matrix.
PREDICTOR_METRICS = (
    ("Accuracy", "accuracy"),
    ("Precision", "precision"),
    ("Recall", "recall"),
    ("F1", "f1"),
    ("AUC", "auc"),
    ("Missed detections", "miss_rate"),
    ("False alarms", "false_alarm_rate"),
)


def _estimator_key(averages: dict, needle: str) -> Optional[str]:
    for key in averages:
        if needle.lower() in key.lower():
            return key
    return None


def _stats(frame) -> None:
    accuracy = R.predictor_average(frame, "accuracy")
    precision = R.predictor_average(frame, "precision")
    misses = R.predictor_average(frame, "miss_rate")

    learned = _estimator_key(accuracy, "learned")
    energy = _estimator_key(accuracy, "energy")

    def point(values: dict, key: Optional[str]) -> str:
        if key is None or key not in values:
            return "\u2014"
        return f"{values[key]:.1%}"

    def delta(values: dict) -> str:
        if learned is None or energy is None or learned not in values or energy not in values:
            return ""
        difference = 100 * (values[learned] - values[energy])
        word = "lower" if difference < 0 else "higher"
        return f"{difference:+.1f} pts {word} than the energy detector"

    stats = C.stat_plates(
        [
            {"label": "Accuracy", "value": point(accuracy, learned), "note": delta(accuracy)},
            {"label": "Precision", "value": point(precision, learned), "note": delta(precision)},
            {"label": "Missed detections", "value": point(misses, learned), "note": delta(misses)},
        ]
    )
    with st.container(key="plate_stats"):
        st.markdown(
            C.section_head("Estimator quality", "mean over 4 regimes and 8 seeds") + stats,
            unsafe_allow_html=True,
        )


def _matrix(frame, metric: str) -> None:
    estimators, levels, values = R.predictor_by_regime(frame, metric)
    columns = [{"label": "Estimator", "width": "300px"}]
    columns += [{"label": level, "num": True} for level in levels]
    rows = [
        {"cells": [C.esc(estimator), *[f"{value:.4f}" if value == value else "\u2014" for value in series]]}
        for estimator, series in zip(estimators, values)
    ]
    with st.container(key="plate_pred"):
        st.markdown(
            C.section_head("Estimator metrics by regime", "results/predictor_accuracy.csv")
            + C.matrix_table(columns, rows),
            unsafe_allow_html=True,
        )


def render(level: Optional[str]) -> None:
    frame = R.predictor()
    if frame is None or frame.empty:
        st.info("results/predictor_accuracy.csv is missing. Run `python evaluate.py` to populate it.")
        return

    _stats(frame)

    controls, _spacer = st.columns([1.2, 3.8], vertical_alignment="center")
    with controls:
        metric_label = st.selectbox(
            "Metric", [label for label, _ in PREDICTOR_METRICS], index=0, key="predictor_metric"
        )
    metric = dict(PREDICTOR_METRICS)[metric_label]

    _matrix(frame, metric)

    with st.container(key="plate_figure"):
        st.markdown(
            C.section_head(f"{metric_label} by congestion regime", "bars are raw means per estimator"),
            unsafe_allow_html=True,
        )
        st.pyplot(charts.predictor_figure(frame, metric), width="stretch")
