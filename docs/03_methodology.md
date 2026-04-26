# Methodology — Blinder-Oaxaca Decomposition

Two OLS fits, one per group, then split the mean comp gap into a **part driven by differences in characteristics** (endowment) and a **part driven by differences in returns to those characteristics** (coefficient — the "unexplained" piece, often glossed as discrimination).

---

## 1. Setup

Let group $A$ and group $B$ be the two protected groups (e.g. men and women). For each group fit a linear model of log monthly compensation on a vector of controls $X$ (tenure, education, role one-hot, level, dept, performance):

$$
Y_g \;=\; X_g\,\beta_g \;+\; \varepsilon_g, \qquad g \in \{A, B\}.
$$

OLS gives $\hat\beta_A$ and $\hat\beta_B$, with sample means $\bar X_A,\bar X_B$ and $\bar Y_A,\bar Y_B$.

## 2. Twofold decomposition (Oaxaca 1973)

$$
\bar Y_A - \bar Y_B \;=\; \underbrace{(\bar X_A - \bar X_B)^\top \hat\beta_B}_{\text{endowment / explained}} \;+\; \underbrace{\bar X_A^\top (\hat\beta_A - \hat\beta_B)}_{\text{coefficient / unexplained}}.
$$

This is the **A-as-reference** form (group $B$'s coefficients used to value characteristic differences). The **B-as-reference** form symmetrically swaps the roles. Both are reported.

## 3. Threefold decomposition

$$
\bar Y_A - \bar Y_B \;=\; \underbrace{(\bar X_A - \bar X_B)^\top \hat\beta_B}_{E\;\text{endowment}} \;+\; \underbrace{\bar X_B^\top (\hat\beta_A - \hat\beta_B)}_{C\;\text{coefficient}} \;+\; \underbrace{(\bar X_A - \bar X_B)^\top (\hat\beta_A - \hat\beta_B)}_{I\;\text{interaction}}.
$$

`E + C + I` exactly equals the raw gap. The **interaction** term captures the joint effect of differing endowments and differing returns; it disappears in the twofold form because that form pre-allocates it to either side.

## 4. Pooled-coefficient (Neumark 1988) variant

Fit a single pooled OLS $\hat\beta^*$ on the union and decompose

$$
\bar Y_A - \bar Y_B \;=\; (\bar X_A - \bar X_B)^\top \hat\beta^* \;+\; \big[ \bar X_A^\top (\hat\beta_A - \hat\beta^*) - \bar X_B^\top (\hat\beta_B - \hat\beta^*) \big].
$$

We report Neumark alongside the classic A-as-reference for sensitivity.

## 5. Bootstrap CI on the unexplained gap

Resample the full frame with replacement $B = 1{,}000$ times; refit two OLS per draw; recompute the threefold decomposition; report the 2.5–97.5 percentile of the **C** component as the 95% CI on the unexplained gap.

## 6. Per-role drill-down

Repeat the decomposition within each `role`. Roles with fewer than 30 employees per group are suppressed and rolled up to "Other". The output is a per-role table sorted by **abs(unexplained component)** descending — the natural targeting list for Total-Rewards adjustments.

## 7. Recommendation engine

For each employee in group $B$ within a role with a positive unexplained gap, compute the per-employee adjustment

$$
\Delta_i \;=\; \exp\big(X_i^\top (\hat\beta_A - \hat\beta_B)\big) \cdot Y_i \;-\; Y_i,
$$

with `Y_i` in the original AED scale. The total recommended budget = $\sum_i \Delta_i$, broken down per role and capped at a configurable percentage of payroll.

## 8. References
- Blinder, *Wage Discrimination: Reduced Form and Structural Estimates*, JHR 1973.
- Oaxaca, *Male-Female Wage Differentials in Urban Labor Markets*, IER 1973.
- Neumark, *Employers' Discriminatory Behavior and the Estimation of Wage Discrimination*, JHR 1988.
- Jann, *The Blinder-Oaxaca decomposition for linear regression models*, Stata Journal 2008.
- Fortin, Lemieux, Firpo, *Decomposition Methods in Economics*, Handbook of Labor Economics 2011.
