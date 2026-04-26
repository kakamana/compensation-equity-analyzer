# Model Card — Compensation Equity Decomposition

## Intended use
Decision-aid for Total-Rewards and Legal teams: surface the **explained**, **unexplained**, and **interaction** components of any pay gap, drill down by role, and recommend the minimum adjustment budget required to close the unexplained component. Never an automated salary-change trigger.

## Method
- Two OLS fits (one per protected group) on `log(monthly_comp_aed)`.
- Threefold (Oaxaca) decomposition: `E + C + I = raw_gap`.
- Pooled-coefficient (Neumark 1988) variant reported alongside.
- Bootstrap 95% CI on the unexplained component (n = 1,000 resamples).

## Training data
Synthetic 5,000-employee org frame (see `data/data_card.md`). The generator injects a small, known unexplained gap so the decomposition has signal to recover.

## Controls
Numeric: `age`, `tenure_yrs`, `education_level`, `level`, `performance_rating`.
Categorical: `role`, `dept` (one-hot, drop-first).

## Metrics
| Metric | Target |
|--------|--------|
| `E + C + I` reconstructs raw gap | exact |
| 95% CI width on `C` | < ±1pt of mean comp |
| Per-role coverage | ≥ 80% headcount |
| Variant disagreement (A-ref / B-ref / Neumark) | < 30% on `C` |

## Limitations
- Synthetic data — real labor-market noise structure may differ.
- Linear-additive form of OLS — non-linear interactions are out of scope (would need quantile-regression or Machado-Mata).
- **Reverse-causality caveat:** because `role` and `level` can themselves be channels of unequal treatment, we report decompositions both with and without those controls and flag the difference.
- Gender encoded binary in synthetic data; real audits should generalize the protected attribute.

## Ethical considerations
- `decision_aid_disclaimer` returned on every API response.
- Per-role drill-down means recommendations are targeted, not blanket.
- Total-Rewards + Legal sign-off required before any compensation action.

## Retraining
- Annual headline; quarterly on a sub-population.

## Ownership
- On-call DS: Asad
- Runbook: `mlops/runbook.md`
