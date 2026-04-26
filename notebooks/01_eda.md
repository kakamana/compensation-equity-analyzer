# Notebook 01 — EDA: synthetic org frame

>>> `from comp_equity.data import make_org_frame; df = make_org_frame()`

## 1. Headcount pass
- Counts by `gender`, `nationality_group`, `dept`, `role`, `level`
- Cell-size table for `role × gender` — flag cells with n < 30

## 2. Comp distributions
- Histograms of `monthly_comp_aed` overall and by `gender`
- Log-scale comparison; box-plots by `role`

## 3. Univariate comp drivers
- Mean comp by `level`, by `tenure` decile, by `education_level`, by `performance_rating`

## 4. Raw gap by slice
- Mean (and median) comp gap M − F overall and within each `role`, `dept`, `level`
- The single number that motivates the project

## 5. Hypotheses for modeling
1. The unexplained gap is non-zero and concentrated in a small number of roles.
2. Tenure and level explain most (but not all) of the raw gap.
3. The Neumark-pooled and A-as-reference variants will agree to within 1 log-point.
