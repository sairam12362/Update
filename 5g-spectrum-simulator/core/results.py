"""Benchmark artefacts: loading, formatting and derived statistics.

Every number the dashboard renders comes from ``results/*.csv``, which
``evaluate.py`` writes. Nothing in this module estimates or simulates a
result: if a file is missing the caller renders a missing-data state.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st

from spectrum.config import CONGESTION_REGIMES, CongestionRegime

RESULTS = Path("results")
ARTIFACTS = Path("artifacts")

#: Congestion regimes in ascending load order.
LEVELS: Tuple[str, ...] = ("low", "medium", "high", "peak")

#: Regime the detail strip shows when the scope is "All regimes".
DEFAULT_LEVEL = "high"

#: The strongest allocator overall, per README §12.3 and results/ablation.csv
#: (highest QoS satisfaction and lowest incumbent collisions of the five arms).
STRONGEST_ALLOCATOR = "M-LWDF + learned sensing"

#: (label, column) pairs for the all-regime aggregate matrix.
AGGREGATE_METRICS: Tuple[Tuple[str, str], ...] = (
    ("QoS %", "qos_satisfaction_pct"),
    ("Goodput Mb/s", "goodput_mbps"),
    ("Deadline misses %", "deadline_miss_pct"),
    ("Collisions %", "collision_pct"),
    ("Wasted vacancy %", "wasted_vacancy_pct"),
    ("Jain fairness", "jain_fairness"),
)

#: (row label, headline metric name, higher-is-better) for the regime strip.
STRIP_METRICS: Tuple[Tuple[str, str, bool], ...] = (
    ("QoS satisfaction", "QoS satisfaction (%)", True),
    ("Goodput", "Goodput (Mb/s)", True),
    ("Incumbent collisions", "Incumbent collisions (%)", False),
)

#: QoS per 5QI class, as written by evaluate.py into kpi_by_regime.csv.
CLASS_COLUMNS: Tuple[Tuple[str, str], ...] = (
    ("URLLC", "qos_URLLC_pct"),
    ("VoIP", "qos_VoIP_pct"),
    ("Live video", "qos_eMBB-Video_pct"),
    ("Best effort", "qos_BestEffort_pct"),
)

_CI_RE = re.compile(r"\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _read_csv(name: str) -> Optional[pd.DataFrame]:
    path = RESULTS / name
    if not path.exists():
        return None
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def headline() -> Optional[pd.DataFrame]:
    """Proposed vs best classical per metric per regime (paired statistics)."""
    return _read_csv("headline.csv")


@st.cache_data(show_spinner=False)
def ablation() -> Optional[pd.DataFrame]:
    """Five-arm component decomposition, aggregated over regimes and seeds."""
    return _read_csv("ablation.csv")


@st.cache_data(show_spinner=False)
def kpi() -> Optional[pd.DataFrame]:
    """Raw per-episode KPIs, nine allocators x four regimes x eight seeds."""
    return _read_csv("kpi_by_regime.csv")


@st.cache_data(show_spinner=False)
def predictor() -> Optional[pd.DataFrame]:
    """Energy detector / Bayes bound / learned GRU, per regime."""
    return _read_csv("predictor_accuracy.csv")


def artifacts_present() -> Dict[str, bool]:
    return {
        "policy.pt": (ARTIFACTS / "policy.pt").exists(),
        "predictor.pt": (ARTIFACTS / "predictor.pt").exists(),
    }


# ---------------------------------------------------------------------------
# Shared formatting
# ---------------------------------------------------------------------------
def f3(value: object) -> str:
    """Three-decimal measurement, or an em dash when undefined."""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "\u2014"
    if math.isnan(number):
        return "\u2014"
    return f"{number:,.3f}"


def signed_pct(value: object) -> str:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "\u2014"
    if math.isnan(number):
        return "\u2014"
    return f"{number:+.1f}%"


def fmt_p(value: object) -> str:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "\u2014"
    if math.isnan(number):
        return "\u2014"
    return f"{number:.4f}"


def parse_ci(text: object) -> Optional[Tuple[float, float]]:
    """``"[96.2, 99.4]"`` -> ``(96.2, 99.4)``."""
    if not isinstance(text, str):
        return None
    match = _CI_RE.search(text)
    if not match:
        return None
    return float(match.group(1)), float(match.group(2))


def allocator_label(name: str) -> str:
    """Tidy the allocator names written by evaluate.py for display."""
    label = str(name).replace(" (ablation)", "").strip()
    return label.replace("BC only / no RL", "BC only (no RL)")


def regime(level: str) -> CongestionRegime:
    return CONGESTION_REGIMES[level]


# ---------------------------------------------------------------------------
# Derived statistics
# ---------------------------------------------------------------------------
def improvement_range(df: Optional[pd.DataFrame], metric: str) -> Optional[Tuple[float, float]]:
    """Lowest and highest direction-adjusted improvement for one metric."""
    if df is None or df.empty:
        return None
    values = df.loc[df["metric"] == metric, "improvement_pct"].dropna()
    if values.empty:
        return None
    return float(values.min()), float(values.max())


def min_p_value(df: Optional[pd.DataFrame], metric: str) -> Optional[float]:
    if df is None or df.empty:
        return None
    values = df.loc[df["metric"] == metric, "p_value"].dropna()
    if values.empty:
        return None
    return float(values.min())


def headline_row(df: Optional[pd.DataFrame], level: str, metric: str) -> Optional[pd.Series]:
    if df is None or df.empty:
        return None
    subset = df[(df["congestion"] == level) & (df["metric"] == metric)]
    return None if subset.empty else subset.iloc[0]


def strip_rows(df: Optional[pd.DataFrame], level: str) -> List[dict]:
    """Three headline metrics for one regime, ready for the CI strip."""
    rows: List[dict] = []
    for label, metric, higher_is_better in STRIP_METRICS:
        row = headline_row(df, level, metric)
        if row is None:
            continue
        rows.append(
            {
                "label": label,
                "metric": metric,
                "proposed": float(row["proposed_mean"]),
                "proposed_ci": parse_ci(row["proposed_ci"]),
                "classical": float(row["classical_mean"]),
                "classical_ci": parse_ci(row["classical_ci"]),
                "comparator": allocator_label(row["best_classical"]),
                "improvement": row["improvement_pct"],
                "p_value": row["p_value"],
                "cliffs_delta": row["cliffs_delta"],
                "higher_is_better": higher_is_better,
            }
        )
    return rows


def aggregate_rows(df: Optional[pd.DataFrame]) -> List[dict]:
    """Five allocator configurations with the six aggregate metrics."""
    if df is None or df.empty:
        return []
    rows: List[dict] = []
    for _, record in df.iterrows():
        label = allocator_label(record["allocator"])
        rows.append(
            {
                "label": label,
                "values": [f3(record[column]) for _, column in AGGREGATE_METRICS],
                "strong": label == STRONGEST_ALLOCATOR,
            }
        )
    return rows


def class_rows(df: Optional[pd.DataFrame], level: Optional[str]) -> Tuple[List[str], List[dict]]:
    """Mean QoS per allocator per 5QI class, for one regime or all of them."""
    if df is None or df.empty:
        return [label for label, _ in CLASS_COLUMNS], []
    subset = df if level is None else df[df["congestion"] == level]
    if subset.empty:
        return [label for label, _ in CLASS_COLUMNS], []

    headers = [label for label, _ in CLASS_COLUMNS]
    rows: List[dict] = []
    for allocator, group in subset.groupby("allocator", sort=False):
        cells = []
        for _, column in CLASS_COLUMNS:
            series = group[column].dropna() if column in group else pd.Series(dtype=float)
            cells.append(f"{series.mean():.1f}" if not series.empty else "\u2014")
        rows.append({"label": allocator_label(allocator), "cells": cells})
    return headers, rows


def predictor_by_regime(df: Optional[pd.DataFrame], metric: str) -> Tuple[List[str], List[str], List[List[float]]]:
    """Estimator x regime matrix for one predictor metric."""
    if df is None or df.empty:
        return [], [], []
    pivot = df.pivot_table(index="estimator", columns="congestion", values=metric, sort=False)
    estimators = [str(e) for e in pivot.index]
    levels = [level for level in LEVELS if level in pivot.columns]
    values = [[float(pivot.loc[e, level]) if not pd.isna(pivot.loc[e, level]) else float("nan") for level in levels] for e in estimators]
    return estimators, levels, values


def predictor_average(df: Optional[pd.DataFrame], metric: str) -> Dict[str, float]:
    if df is None or df.empty:
        return {}
    return {str(k): float(v) for k, v in df.groupby("estimator", sort=False)[metric].mean().items()}
