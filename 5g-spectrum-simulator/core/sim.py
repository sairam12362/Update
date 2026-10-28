"""Simulation access for the Live Simulation page.

The episode loop is the same one ``evaluate.py`` uses; it lives here so the
dashboard does not own any physics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import streamlit as st

from spectrum.baselines import build_classical
from spectrum.config import SimConfig
from spectrum.env import SpectrumEnv

ARTIFACTS = Path("artifacts")


@st.cache_resource(show_spinner=False)
def load_agent():
    """The trained NeuroSpectrum allocator, or None when artifacts are absent."""
    policy = ARTIFACTS / "policy.pt"
    if not policy.exists():
        return None
    from spectrum.agent import NeuroSpectrumAllocator

    predictor = ARTIFACTS / "predictor.pt"
    return NeuroSpectrumAllocator.load(policy, predictor if predictor.exists() else None)


def allocator_registry() -> Dict[str, object]:
    registry: Dict[str, object] = {a.name: a for a in build_classical()}
    agent = load_agent()
    if agent is not None:
        registry[agent.name] = agent
    return registry


def simulate(allocator, cfg: SimConfig, seed: int) -> Dict[str, object]:
    """Run one episode and return its summary, per-slot series and occupancy."""
    env = SpectrumEnv(cfg, seed=seed)
    allocator.reset(cfg)  # type: ignore[attr-defined]
    obs = env.observe()
    grid = np.full((cfg.slots_per_episode, cfg.n_rbg), -1, dtype=np.int64)
    truth = np.zeros((cfg.slots_per_episode, cfg.n_subbands), dtype=np.int64)
    series: List[Dict] = []
    for slot in range(cfg.slots_per_episode):
        assignment = allocator.allocate(obs)  # type: ignore[attr-defined]
        grid[slot] = assignment
        obs, _reward, done, info = env.step(assignment)
        truth[slot] = info["_truth_incumbent"]
        series.append(
            {
                "slot": slot,
                "Goodput (Mb/s)": info["useful_bits"] / cfg.slot_duration_s / 1e6,
                "Collisions": info["collisions"],
                "In-budget UEs (%)": 100.0 * info["qos_fraction"],
                "Jain fairness": info["jain"],
            }
        )
        if done:
            break
    return {
        "summary": env.episode_summary(),
        "series": pd.DataFrame(series),
        "grid": grid,
        "truth": truth,
        "ue_class": env.traffic.ue_class.copy(),
        "cfg": cfg,
    }
