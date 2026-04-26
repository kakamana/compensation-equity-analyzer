"""Inference wrapper for the compensation-equity audit.

If the org-frame parquet exists in `data/processed/`, runs the decomposition
on the live data; otherwise regenerates the synthetic frame on-the-fly so
the API stays callable.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from . import models
from .data import PROCESSED, make_org_frame

PARQUET = PROCESSED / "org_frame.parquet"


def _load_frame() -> pd.DataFrame:
    if PARQUET.exists():
        return pd.read_parquet(PARQUET)
    return make_org_frame()


@lru_cache(maxsize=1)
def _cached_audit() -> dict:
    df = _load_frame()
    decomp = models.threefold_decomposition(df)
    boot = models.bootstrap_unexplained(df, n_boot=200)
    role_tbl = models.per_role_decomposition(df)
    recs = models.recommend_adjustments(df)

    by_role = []
    for _, r in role_tbl.iterrows():
        if r["suppressed"]:
            continue
        by_role.append(dict(
            role=str(r["role"]),
            n_m=int(r["n_m"]),
            n_f=int(r["n_f"]),
            raw_gap=float(r["raw_gap"]),
            explained=float(r["E"]),
            unexplained=float(r["C"]),
            interaction=float(r["I"]),
        ))

    recommendations = [
        f"Allocate AED {recs['total_monthly_uplift_aed']:.0f}/month "
        f"across {recs['n_employees_flagged']} employees to close the unexplained gap.",
        f"Top role to address: {next(iter(recs['by_role']), 'n/a')}.",
        f"Bootstrap 95% CI on the unexplained component: "
        f"[{boot['ci_low']:.4f}, {boot['ci_high']:.4f}] (log-AED).",
    ]

    return dict(
        raw_gap=float(decomp["raw_gap"]),
        explained=float(decomp["E"]),
        unexplained=float(decomp["C"]),
        interaction=float(decomp["I"]),
        unexplained_ci_low=float(boot["ci_low"]),
        unexplained_ci_high=float(boot["ci_high"]),
        by_role=by_role,
        recommendations=recommendations,
    )


def equity_audit(_payload: dict | None = None) -> dict:
    """Return the full equity audit. The payload is reserved for future filters."""
    return _cached_audit()
