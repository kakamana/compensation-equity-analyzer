# Evaluation Plan — Compensation Equity Analyzer

## 1. Decomposition recovery test (synthetic ground-truth)
Because we control the data-generating process, we know the **true** unexplained gap that was injected. Verify that the threefold decomposition's `C` component recovers it within the 95% bootstrap CI.

| Quantity | Injected (truth) | Recovered (point) | Recovered (95% CI) | Pass? |
|---|---|---|---|---|
| Unexplained gap (log AED) | – | – | – | – |
| Endowment | – | – | – | – |
| Interaction | – | – | – | – |

## 2. Sensitivity sweep
Re-run with the following control sets and report how the unexplained component moves:
- (a) tenure + age only
- (b) (a) + education
- (c) (b) + level + dept
- (d) (c) + role
- (e) (d) + performance_rating

The **(c) → (d)** delta is informative: if controlling for `role` shrinks the unexplained component sharply, that suggests role allocation itself may be a channel of unequal treatment.

## 3. A-as-reference vs B-as-reference vs Neumark-pooled
Report the unexplained component under all three variants. Disagreement > 30% is flagged for review.

## 4. Per-role coverage
% of headcount covered by roles with ≥ 30 employees per group. Target: ≥ 80%.

## 5. Bootstrap CI width
95% CI on the unexplained component. Target: width < ±1pt of mean comp.

## 6. Edge-case checks
- Drop the largest role → does the headline decomposition change > 25%?
- Inject a 5% measurement-error shock on `monthly_comp_aed` → confirm CI widens but point estimate is stable.
- Re-balance the synthetic data to 50/50 group ratio → confirm the unexplained component is invariant.

## 7. Business impact
- Total recommended adjustment budget vs current annual payroll.
- Number of employees flagged for adjustment.
- Average adjustment per flagged employee.
- Time-to-close estimate at a given monthly adjustment cap.

## 8. Deployment readiness checklist
- [ ] Threefold decomposition recovers injected truth within 95% CI
- [ ] Per-role table with ≥ 80% headcount coverage
- [ ] Sensitivity sweep table populated
- [ ] Recommendation engine output is non-empty and within payroll cap
- [ ] `mlops/model_card.md` documents controls and reverse-causality caveat
