"""Blinder-Oaxaca decomposition implemented from two OLS fits.

Fits one OLS per group (default groups = M / F on `gender`), then computes:

- twofold (A-as-reference, B-as-reference)
- threefold (E + C + I)
- per-role drill-down
- bootstrap 95% CI on the unexplained component

A pure-numpy OLS is used so the module has no dependency on statsmodels at
inference time; statsmodels is still useful for richer summary tables.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .data import make_org_frame
from .features import align_columns, build_design_matrix

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# OLS
# ---------------------------------------------------------------------------
@dataclass
class OLSFit:
    feature_names: list[str]
    beta: np.ndarray          # (k,)
    cov: np.ndarray           # (k, k)
    sigma2: float
    n: int

    def predict(self, X: np.ndarray | pd.DataFrame) -> np.ndarray:
        Xv = X.values if isinstance(X, pd.DataFrame) else X
        return Xv @ self.beta


def fit_ols(X: pd.DataFrame, y: pd.Series | np.ndarray) -> OLSFit:
    """Closed-form OLS via the normal equations with a tiny ridge for stability."""
    Xv = X.values.astype(float)
    yv = np.asarray(y, dtype=float)
    k = Xv.shape[1]
    XtX = Xv.T @ Xv + 1e-8 * np.eye(k)
    Xty = Xv.T @ yv
    beta = np.linalg.solve(XtX, Xty)
    resid = yv - Xv @ beta
    n = Xv.shape[0]
    sigma2 = float((resid @ resid) / max(n - k, 1))
    cov = sigma2 * np.linalg.inv(XtX)
    return OLSFit(feature_names=list(X.columns), beta=beta, cov=cov,
                  sigma2=sigma2, n=n)


def fit_two_group_ols(
    df: pd.DataFrame,
    group_col: str = "gender",
    group_a: str = "M",
    group_b: str = "F",
) -> tuple[OLSFit, OLSFit, list[str]]:
    """Fit one OLS per group on a shared, aligned design matrix."""
    X, y, _ = build_design_matrix(df)
    a_mask = (df[group_col] == group_a).values
    b_mask = (df[group_col] == group_b).values
    XA, XB = X.loc[a_mask], X.loc[b_mask]
    XA, XB = align_columns(XA, XB)
    yA, yB = y[a_mask], y[b_mask]
    return fit_ols(XA, yA), fit_ols(XB, yB), list(XA.columns)


# ---------------------------------------------------------------------------
# Decomposition
# ---------------------------------------------------------------------------
def _means(X: pd.DataFrame) -> np.ndarray:
    return X.values.astype(float).mean(axis=0)


def threefold_decomposition(
    df: pd.DataFrame,
    group_col: str = "gender",
    group_a: str = "M",
    group_b: str = "F",
) -> dict:
    """Full threefold (E + C + I) decomposition of mean log-comp gap A − B."""
    ols_a, ols_b, feat = fit_two_group_ols(df, group_col, group_a, group_b)

    X, y, _ = build_design_matrix(df)
    a_mask = (df[group_col] == group_a).values
    b_mask = (df[group_col] == group_b).values
    XA, XB = X.loc[a_mask], X.loc[b_mask]
    XA, XB = align_columns(XA, XB)

    xa = _means(XA)
    xb = _means(XB)
    ya = float(np.asarray(y[a_mask], dtype=float).mean())
    yb = float(np.asarray(y[b_mask], dtype=float).mean())
    raw_gap = ya - yb

    # Make sure betas align to the shared column order
    # (fit_two_group_ols already aligned, so feat order is shared)
    ba = ols_a.beta
    bb = ols_b.beta

    E = float((xa - xb) @ bb)
    C = float(xb @ (ba - bb))
    I = float((xa - xb) @ (ba - bb))

    # Twofold variants
    twofold_A_ref = dict(
        endowment=float((xa - xb) @ bb),
        unexplained=float(xa @ (ba - bb)),
    )
    twofold_B_ref = dict(
        endowment=float((xa - xb) @ ba),
        unexplained=float(xb @ (ba - bb)),
    )

    return dict(
        raw_gap=raw_gap,
        mean_y_a=ya,
        mean_y_b=yb,
        E=E, C=C, I=I,
        sum_EC_I=E + C + I,
        twofold_A_reference=twofold_A_ref,
        twofold_B_reference=twofold_B_ref,
        feature_names=feat,
        n_a=ols_a.n, n_b=ols_b.n,
    )


def neumark_pooled(
    df: pd.DataFrame,
    group_col: str = "gender",
    group_a: str = "M",
    group_b: str = "F",
) -> dict:
    """Pooled-coefficient (Neumark 1988) variant of the decomposition."""
    X, y, _ = build_design_matrix(df)
    pooled = fit_ols(X, y)
    bp = pooled.beta

    ols_a, ols_b, _ = fit_two_group_ols(df, group_col, group_a, group_b)
    a_mask = (df[group_col] == group_a).values
    b_mask = (df[group_col] == group_b).values
    XA, XB = X.loc[a_mask], X.loc[b_mask]
    XA, XB = align_columns(XA, XB)
    xa = _means(XA)
    xb = _means(XB)

    explained = float((xa - xb) @ bp)
    unexplained = float(xa @ (ols_a.beta - bp) - xb @ (ols_b.beta - bp))
    return dict(explained=explained, unexplained=unexplained,
                pooled_n=pooled.n)


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------
def bootstrap_unexplained(
    df: pd.DataFrame,
    n_boot: int = 1_000,
    seed: int = 42,
    group_col: str = "gender",
) -> dict:
    rng = np.random.default_rng(seed)
    n = len(df)
    samples = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        sub = df.iloc[idx].reset_index(drop=True)
        try:
            d = threefold_decomposition(sub, group_col=group_col)
            samples.append(d["C"])
        except np.linalg.LinAlgError:
            continue
    arr = np.array(samples, dtype=float)
    return dict(
        point=float(np.median(arr)),
        ci_low=float(np.quantile(arr, 0.025)),
        ci_high=float(np.quantile(arr, 0.975)),
        n_draws=int(arr.size),
    )


# ---------------------------------------------------------------------------
# Per-role drill-down
# ---------------------------------------------------------------------------
def per_role_decomposition(
    df: pd.DataFrame,
    min_per_group: int = 30,
) -> pd.DataFrame:
    rows = []
    for role, sub in df.groupby("role"):
        ca = (sub["gender"] == "M").sum()
        cb = (sub["gender"] == "F").sum()
        if min(ca, cb) < min_per_group:
            rows.append(dict(role=role, n_m=int(ca), n_f=int(cb),
                             raw_gap=np.nan, E=np.nan, C=np.nan, I=np.nan,
                             suppressed=True))
            continue
        try:
            d = threefold_decomposition(sub)
            rows.append(dict(role=role, n_m=int(ca), n_f=int(cb),
                             raw_gap=d["raw_gap"], E=d["E"], C=d["C"], I=d["I"],
                             suppressed=False))
        except np.linalg.LinAlgError:
            rows.append(dict(role=role, n_m=int(ca), n_f=int(cb),
                             raw_gap=np.nan, E=np.nan, C=np.nan, I=np.nan,
                             suppressed=True))
    out = pd.DataFrame(rows)
    out["abs_C"] = out["C"].abs()
    return out.sort_values("abs_C", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------
def recommend_adjustments(
    df: pd.DataFrame,
    payroll_cap_pct: float = 0.02,
) -> dict:
    """Estimate per-role adjustment budget to close the unexplained gap.

    Per-employee uplift = exp(X_i^T (beta_A - beta_B)) * Y_i  -  Y_i, applied to
    group B in roles where the per-role unexplained component is positive.
    """
    ols_a, ols_b, feat = fit_two_group_ols(df)
    X, _, _ = build_design_matrix(df)
    XA, XB = X.loc[df["gender"] == "M"], X.loc[df["gender"] == "F"]
    XA, XB = align_columns(XA, XB)

    diff = ols_a.beta - ols_b.beta
    # In log scale; convert to multiplicative uplift
    uplift_log = XB.values @ diff
    base_comp = df.loc[df["gender"] == "F", "monthly_comp_aed"].values
    uplift_aed = (np.exp(uplift_log) - 1.0) * base_comp
    uplift_aed = np.clip(uplift_aed, 0.0, None)

    per_role_table = per_role_decomposition(df)
    positive_C_roles = set(per_role_table.loc[per_role_table["C"] > 0, "role"])
    role_for_b = df.loc[df["gender"] == "F", "role"].values
    role_mask = np.array([r in positive_C_roles for r in role_for_b])
    uplift_aed = uplift_aed * role_mask

    payroll = float(df["monthly_comp_aed"].sum())
    cap = payroll * payroll_cap_pct
    total = float(uplift_aed.sum())
    scale = 1.0 if total <= cap else cap / max(total, 1e-9)
    uplift_capped = uplift_aed * scale

    by_role = (
        pd.Series(uplift_capped, index=role_for_b)
        .groupby(level=0).sum().sort_values(ascending=False).round(2).to_dict()
    )

    return dict(
        total_monthly_uplift_aed=round(float(uplift_capped.sum()), 2),
        n_employees_flagged=int((uplift_capped > 0).sum()),
        by_role=by_role,
        payroll_cap_pct=payroll_cap_pct,
        applied_scale=scale,
    )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def save(obj, name: str) -> Path:
    path = MODEL_DIR / name
    joblib.dump(obj, path)
    return path


def load(name: str):
    return joblib.load(MODEL_DIR / name)


def fit_and_save(df: pd.DataFrame | None = None) -> dict:
    df = df if df is not None else make_org_frame()
    ols_a, ols_b, feat = fit_two_group_ols(df)
    decomp = threefold_decomposition(df)
    pooled = neumark_pooled(df)
    save(asdict(ols_a), "comp_ols_a.pkl")
    save(asdict(ols_b), "comp_ols_b.pkl")
    decomp_out = {k: v for k, v in decomp.items() if k != "feature_names"}
    decomp_out["neumark_pooled"] = pooled
    with open(MODEL_DIR / "decomposition.json", "w") as fh:
        json.dump(decomp_out, fh, indent=2, default=float)
    return decomp_out


if __name__ == "__main__":
    out = fit_and_save()
    print(json.dumps(out, indent=2, default=float))
