# Business Requirements — Compensation Equity Analyzer

## 1. Problem Statement
Total-Rewards leaders need to publish a credible pay-equity audit each year. The single-number "raw gap" is inadequate: regulators and employees both want to know **how much of any observed gap is explained by legitimate factors** (tenure, role, level, education, performance) and **how much remains unexplained** after controlling for those factors. Target user: HR Total-Rewards & Compensation team within a multi-nationality employer.

## 2. Stakeholders
| Role | Interest | Success criterion |
|------|----------|-------------------|
| Chief People Officer | Defensible pay-equity narrative | Threefold decomposition published annually |
| Total-Rewards lead | Identify unexplained gaps for adjustment | Per-role unexplained-gap table |
| Diversity & Inclusion | Subgroup pay parity | Unexplained gap ≤ 2% of mean comp |
| Legal / Compliance | Audit trail | Documented features, fits, and CIs |
| Employees / Works council | Transparency | Public methodology + summary results |

## 3. Business Objectives
1. Publish the **threefold decomposition** (endowment + coefficient + interaction) for the headline gender gap.
2. Provide a **per-role drill-down** so that compensation actions are targeted, not blanket.
3. Report a **bootstrap 95% CI** around the unexplained-gap component.
4. Recommend the **minimum salary adjustments** required to bring the unexplained gap inside the gate.

## 4. KPIs
| KPI | Definition | Target | Baseline |
|-----|-----------|--------|----------|
| Unexplained gap (% of mean comp) | β-driven gap component / mean(comp) | ≤ 2% | – |
| Per-role coverage | Roles with ≥ 30 employees per group | ≥ 80% of headcount | – |
| Bootstrap CI width | 95% CI on unexplained gap | < ±1pt | – |
| Annual audit published | Y/N | Yes | No |

## 5. Scope
**In scope:** active permanent employees with monthly comp in AED; gender as the headline protected attribute; tenure, role, level, education, performance as controls.
**Out of scope:** equity / RSU / bonus pools (separate project); part-time and contractor populations; future-pay projections.

## 6. Constraints & Assumptions
- **PII / privacy:** comp values stored at employee-level but published only in aggregate.
- **Transparency:** the decomposition method and feature list are documented and shipped with each annual report.
- **Legal:** every adjustment recommendation is checked by Total-Rewards + Legal before action.

## 7. Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Mis-specification of controls leads to over-attributing the gap as "explained" | Medium | High | Sensitivity sweep on feature subset in `docs/04_evaluation.md` §5 |
| Small per-role sample → unstable per-role decompositions | High | Medium | Suppress roles with n<30 per group; report aggregate only |
| Reverse-causality (role itself is a channel of discrimination) | High | High | Report both with and without `role` as control; flag the difference |
| Public mis-interpretation of the unexplained gap | Medium | Medium | Plain-English glossary in published report; UI tooltips |

## 8. Timeline
- **Week 1** — Synthetic data generator + baseline OLS per group
- **Week 2** — Threefold decomposition + bootstrap CIs + per-role drill-down
- **Week 3** — FastAPI + Next.js waterfall UI
- **Week 4** — Recommendation engine for adjustments; methodology doc finalization
- **Week 5** — Content (Medium / LinkedIn); ship
