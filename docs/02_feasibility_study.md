# Feasibility Study — Compensation Equity Analyzer

## 1. Data feasibility

### Synthetic dataset
- **Generator:** `src/comp_equity/data.py::make_org_frame()` — 5,000 employees with `emp_id, age, tenure_yrs, education_level, role, level, dept, gender, nationality_group, monthly_comp_aed, performance_rating`.
- **Why synthetic:** real comp data is highly sensitive; the public Glassdoor / BLS aggregates do not give the row-level granularity needed for a decomposition.
- **Demonstration:** the generator injects a small **unexplained gap** component for the protected group so the decomposition has signal to recover.

### Real-world equivalent
- Internal HRIS extract: same schema; one row per active employee on the audit date.
- Industry benchmarks (Mercer, WTW, Korn Ferry) for sanity-checking role-level pay distributions.

## 2. Technical feasibility
- **Algorithmic shortlist**
  - Two OLS fits (one per group) — main
  - Pooled-coefficient (Neumark) variant — sensitivity
  - Quantile regression decomposition (Machado-Mata) — stretch
- **Compute:** 1 CPU, fitting under 5 seconds on 5,000 rows.
- **Serving:** FastAPI + two `statsmodels` OLS pickles (~tens of KB).

## 3. Economic feasibility
| Line item | Monthly cost |
|-----------|--------------|
| 1× small container | ~$8 |
| Storage | ~$1 |
| MLflow (self-hosted) | $0 |
| **Total** | **~$9 / mo** |

**Value:** a defensible annual pay-equity audit avoids both regulatory penalties and the much larger cost of misdirected compensation adjustments.

## 4. Operational feasibility
- **Refresh cadence:** annual headline; quarterly on a sub-population sample.
- **Monitoring:** drift on the per-role gap distribution year-over-year.
- **Human-in-the-loop:** Total-Rewards + Legal sign-off on every recommendation.

## 5. Ethical / legal feasibility
- **Decomposition is a decision aid, not an automated adjustment trigger.**
- **Reverse-causality caveat:** because role / level can themselves be channels of discrimination, the audit reports two configurations — with and without these controls — and flags the difference.
- **PII:** employee-level comp never leaves the warehouse; only group-level decomposition outputs are surfaced via the API.

## 6. Recommendation
**Go.** Method is well-understood (Blinder 1973, Oaxaca 1973), tooling is open, infra cost is trivial, and the decomposition output gives Total-Rewards a defensible narrative far beyond the headline raw gap.
