"""Synthetic org-frame generator for the compensation-equity audit.

Writes data/processed/org_frame.parquet with 5,000 employees and the schema
documented in data/data_card.md. Deterministic seed = 42.

A small unexplained gap is injected for the protected group so the
Blinder-Oaxaca decomposition has signal to recover.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW = DATA_DIR / "raw"
PROCESSED = DATA_DIR / "processed"

ROLES = [
    "Sales Executive", "Account Manager", "Software Engineer", "Data Analyst",
    "HR Business Partner", "Recruiter", "Finance Analyst", "Marketing Lead",
    "Operations Manager", "Customer Success", "Product Manager", "Designer",
]
DEPTS = ["Sales", "Engineering", "HR", "Finance", "Marketing", "Operations"]
ROLE_TO_DEPT = {
    "Sales Executive": "Sales", "Account Manager": "Sales",
    "Software Engineer": "Engineering", "Data Analyst": "Engineering",
    "HR Business Partner": "HR", "Recruiter": "HR",
    "Finance Analyst": "Finance",
    "Marketing Lead": "Marketing",
    "Operations Manager": "Operations", "Customer Success": "Operations",
    "Product Manager": "Engineering", "Designer": "Marketing",
}
NATIONALITY_GROUPS = ["Emirati", "South Asian", "Western", "Other"]
NATIONALITY_P = [0.12, 0.55, 0.15, 0.18]

# AED monthly base by role (level=3, mid)
ROLE_BASE_AED = {
    "Sales Executive": 14_000, "Account Manager": 18_000,
    "Software Engineer": 22_000, "Data Analyst": 17_000,
    "HR Business Partner": 19_000, "Recruiter": 12_000,
    "Finance Analyst": 18_000, "Marketing Lead": 21_000,
    "Operations Manager": 23_000, "Customer Success": 13_000,
    "Product Manager": 28_000, "Designer": 16_000,
}

# Injected unexplained gender gap multiplier on group F (after all explained factors)
INJECTED_F_MULT = 0.93   # ~ -7.25 log-points unexplained


def make_org_frame(n: int = 5_000, seed: int = 42) -> pd.DataFrame:
    """Generate a 5,000-employee synthetic compensation panel."""
    rng = np.random.default_rng(seed)

    age = rng.integers(22, 63, size=n)
    tenure_yrs = np.clip(rng.gamma(2.0, 2.0, size=n), 0.1, 30.0)
    education_level = rng.choice([1, 2, 3, 4, 5], size=n,
                                 p=[0.05, 0.15, 0.55, 0.20, 0.05])
    role = rng.choice(ROLES, size=n)
    dept = np.array([ROLE_TO_DEPT[r] for r in role])
    # Level skews lower; correlated with tenure
    level_raw = 1 + (tenure_yrs / 5.0) + rng.normal(0, 0.7, size=n)
    level = np.clip(np.round(level_raw).astype(int), 1, 7)

    gender = rng.choice(["M", "F"], size=n, p=[0.62, 0.38])
    nationality_group = rng.choice(NATIONALITY_GROUPS, size=n, p=NATIONALITY_P)
    performance_rating = rng.choice([1, 2, 3, 4, 5], size=n,
                                    p=[0.02, 0.10, 0.55, 0.28, 0.05])

    base = np.array([ROLE_BASE_AED[r] for r in role], dtype=float)
    level_mult = 1.0 + 0.18 * (level - 3)
    tenure_mult = 1.0 + 0.025 * tenure_yrs
    edu_mult = 1.0 + 0.04 * (education_level - 3)
    perf_mult = 1.0 + 0.06 * (performance_rating - 3)

    comp = base * level_mult * tenure_mult * edu_mult * perf_mult

    # Injected unexplained gap on group F
    f_mask = gender == "F"
    comp[f_mask] = comp[f_mask] * INJECTED_F_MULT

    # Multiplicative log-normal noise
    noise = rng.lognormal(mean=0.0, sigma=0.06, size=n)
    comp = comp * noise
    comp = np.clip(comp, 5_000.0, None).round(2)

    emp_id = [f"E-{i:05d}" for i in range(1, n + 1)]

    df = pd.DataFrame({
        "emp_id": emp_id,
        "age": age,
        "tenure_yrs": tenure_yrs.round(2),
        "education_level": education_level,
        "role": role,
        "level": level,
        "dept": dept,
        "gender": gender,
        "nationality_group": nationality_group,
        "monthly_comp_aed": comp,
        "performance_rating": performance_rating,
    })
    return df


def write_processed() -> Path:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df = make_org_frame()
    out = PROCESSED / "org_frame.parquet"
    df.to_parquet(out, index=False)
    return out


if __name__ == "__main__":
    out = write_processed()
    print(f"wrote 5,000 rows -> {out}")
