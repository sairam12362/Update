"""Matplotlib figures in the Calibration Bench palette.

Light paper canvases, ink marks, no hue: allocators are told apart by line
style and direct labels, not by colour.
"""
from __future__ import annotations

from typing import Dict

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

from spectrum.config import SimConfig
from ui.theme import TOKENS

PAPER = TOKENS["paper"]
BENCH = TOKENS["bench"]
INK = TOKENS["ink"]
HAIR = TOKENS["hair"]


def _blank(figsize, nrows: int = 1, ncols: int = 1):
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, facecolor=PAPER)
    return fig, axes


def occupancy_figure(res_a: Dict, res_b: Dict, cfg: SimConfig, name_a: str, name_b: str):
    """Two stacked 18-RBG waterfalls: idle, clean transmission, collision."""
    window = min(240, cfg.slots_per_episode)
    #: Column width in slots; 4 slots keeps a 240-slot window legible.
    step = max(1, window // 60)
    fig, axes = _blank((11.6, 3.9), 2, 1)
    fig.subplots_adjust(left=0.075, right=0.995, top=0.86, bottom=0.14, hspace=0.62)
    cmap = ListedColormap([PAPER, "#C4C1C1", INK])

    for ax, res, title in ((axes[0], res_a, name_a), (axes[1], res_b, name_b)):
        ax.set_facecolor(PAPER)
        grid = res["grid"][:window]
        truth = res["truth"][:window]
        occupied = np.repeat(truth, cfg.rbgs_per_subband, axis=1)
        state = np.where(grid < 0, 0, np.where(occupied == 1, 2, 1))
        # Collapse `step` slots per column; a collision anywhere in the bin wins.
        bins = (state.shape[0] // step) * step
        image = state[:bins].reshape(bins // step, step, state.shape[1]).max(axis=1)
        ax.imshow(
            image.T,
            aspect="auto",
            origin="lower",
            interpolation="nearest",
            cmap=cmap,
            vmin=0,
            vmax=2,
        )
        for spine in ax.spines.values():
            spine.set_color(HAIR)
        ax.set_title(title, fontsize=9, color=INK, loc="left", pad=6)
        ax.tick_params(colors="#6E7276", labelsize=8, length=0)
        # The grid stores `step` slots per column; label the axis in real slots.
        ticks = list(range(0, image.shape[0], max(1, image.shape[0] // 5)))
        ax.set_xticks(ticks, [str(tick * step) for tick in ticks])
        ax.set_xlabel("slot", color="#6E7276", fontsize=8, labelpad=2)

    axes[0].set_ylabel("RBG", color="#6E7276", fontsize=8, labelpad=2)
    return fig


def series_figure(series_a: pd.DataFrame, series_b: pd.DataFrame, metric: str, name_a: str, name_b: str, window: int = 20):
    """Per-slot KPI, rolling-mean smoothed, shared axis, direct labels."""
    fig, ax = _blank((11.6, 2.5))
    fig.subplots_adjust(left=0.065, right=0.995, top=0.86, bottom=0.22)
    ax.set_facecolor(PAPER)

    for series, name, style, width in ((series_a, name_a, (0, (4, 3)), 1.2), (series_b, name_b, "solid", 1.6)):
        smoothed = series[metric].rolling(window, min_periods=1).mean()
        ax.plot(series["slot"], smoothed, linestyle=style, linewidth=width, color=INK, label=name)
        ax.annotate(
            name[:18],
            xy=(series["slot"].iloc[-1], smoothed.iloc[-1]),
            xytext=(3, 0),
            textcoords="offset points",
            fontsize=7,
            color="#6E7276",
            va="center",
            annotation_clip=False,
        )

    ax.grid(axis="y", color=HAIR, linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(HAIR)
    ax.tick_params(colors="#6E7276", labelsize=8, length=0)
    ax.set_xlabel("slot", color="#6E7276", fontsize=8)
    ax.set_ylabel(metric, color="#6E7276", fontsize=8)
    legend = ax.legend(frameon=False, fontsize=8, loc="upper left", ncol=2)
    for text in legend.get_texts():
        text.set_color(INK)
    return fig


def predictor_figure(df: pd.DataFrame, metric: str = "accuracy"):
    """Grouped bars: estimator x regime for one scoring metric."""
    pivot = df.pivot_table(index="congestion", columns="estimator", values=metric, sort=False)
    regimes = [r for r in ("low", "medium", "high", "peak") if r in pivot.index]
    pivot = pivot.loc[regimes]

    fig, ax = _blank((11.6, 2.6))
    fig.subplots_adjust(left=0.06, right=0.995, top=0.84, bottom=0.22)
    ax.set_facecolor(PAPER)

    estimators = list(pivot.columns)
    shading = {"light": "#D8D5D5", "mid": "#8E8C8C", "dark": INK}
    fills = list(shading.values())[-len(estimators):]
    width = 0.8 / max(len(estimators), 1)
    x = np.arange(len(regimes))

    for index, estimator in enumerate(estimators):
        offset = (index - (len(estimators) - 1) / 2) * width
        ax.bar(x + offset, pivot[estimator].to_numpy(), width * 0.92, color=fills[index], label=str(estimator))

    ax.set_xticks(x, [r for r in regimes])
    ax.grid(axis="y", color=HAIR, linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(HAIR)
    ax.tick_params(colors="#6E7276", labelsize=8, length=0)
    ax.set_ylabel(metric.replace("_", " "), color="#6E7276", fontsize=8)
    ax.set_ylim(0, max(1.0, float(np.nanmax(pivot.to_numpy())) * 1.15))
    legend = ax.legend(
        frameon=False,
        fontsize=8,
        ncol=len(estimators),
        loc="lower left",
        bbox_to_anchor=(0, 1.01),
        handlelength=1.2,
        columnspacing=1.4,
    )
    for text in legend.get_texts():
        text.set_color(INK)
    return fig
