# Notebook 03 — Modeling: Blinder-Oaxaca

## 1. Two OLS fits
>>> `from comp_equity.models import fit_two_group_ols`
>>> `ols_a, ols_b = fit_two_group_ols(df)`

## 2. Threefold decomposition
>>> `from comp_equity.models import threefold_decomposition`
>>> `decomp = threefold_decomposition(ols_a, ols_b, df)` — `decomp["E"]`, `decomp["C"]`, `decomp["I"]`

## 3. Bootstrap CI on `C`
>>> `from comp_equity.models import bootstrap_unexplained`
>>> `lo, hi = bootstrap_unexplained(df, n_boot=1000, seed=42)`

## 4. Per-role table
>>> `from comp_equity.models import per_role_decomposition`
>>> `tbl = per_role_decomposition(df)` — sorted by `abs(C)` desc

## 5. Persist
>>> `models.save(ols_a, "comp_ols_a.pkl"); models.save(ols_b, "comp_ols_b.pkl")`
>>> `json.dump(decomp, open(MODEL_DIR/"decomposition.json", "w"))`
