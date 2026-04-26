"""Design-matrix construction for the Blinder-Oaxaca decomposition."""
from __future__ import annotations

import numpy as np
import pandas as pd

NUMERIC = ["age", "tenure_yrs", "education_level", "level", "performance_rating"]
CATEGORICAL = ["role", "dept"]


def build_design_matrix(
    df: pd.DataFrame,
    numeric: list[str] | None = None,
    categorical: list[str] | None = None,
    drop_first: bool = True,
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Return (X with intercept, y = log_comp, feature_names)."""
    numeric = numeric or NUMERIC
    categorical = categorical or CATEGORICAL

    parts = [df[numeric].copy()]
    for col in categorical:
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=drop_first)
        parts.append(dummies)
    X = pd.concat(parts, axis=1).astype(float)
    X.insert(0, "const", 1.0)

    y = np.log(df["monthly_comp_aed"].astype(float))
    feature_names = list(X.columns)
    return X, y, feature_names


def align_columns(
    XA: pd.DataFrame, XB: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ensure both group design matrices share the same columns (zero-fill missing)."""
    cols = sorted(set(XA.columns) | set(XB.columns))
    return XA.reindex(columns=cols, fill_value=0.0), XB.reindex(columns=cols, fill_value=0.0)
