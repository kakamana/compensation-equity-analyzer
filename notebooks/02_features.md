# Notebook 02 — Feature Engineering

>>> `from comp_equity.features import build_design_matrix`

## 1. Target
`log_comp = log(monthly_comp_aed)` — log-linear is the standard form for OLS-based decomposition.

## 2. Controls
- Numeric: `age`, `tenure_yrs`, `education_level`, `level`, `performance_rating`
- Categorical (one-hot, drop-first): `role`, `dept`

## 3. Design matrix
>>> `X, y, feature_names = build_design_matrix(df)` — verify shape, no NaN, drop-first dummies in place.

## 4. Group split
>>> `XA, yA = X[df.gender == "M"], y[df.gender == "M"]`
>>> `XB, yB = X[df.gender == "F"], y[df.gender == "F"]`

## 5. Sanity checks
- Each group has all role / dept levels represented.
- VIF on numeric controls (multicollinearity).
- Mean of each control by group — these are the $\bar X_A, \bar X_B$ that will drive the endowment term.
