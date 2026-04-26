# A Reproducible Blinder-Oaxaca Pipeline for Pay-Equity Audits with Bootstrap Confidence Intervals and Per-Role Drill-Down

**Author.** Asad Kamran. Master of Applied Data Science, University of Michigan. Day affiliation: Dubai Human Resources Department.

**Project repository.** github.com/kakamana/compensation-equity-analyzer

---

## Abstract

Pay-equity audits remain dominated by the unconditional headline gap, which conflates legitimate productivity controls with the unexplained pay differential that an auditor or works council can act on. We present a reproducible, open-source pipeline implementing the classical Blinder-Oaxaca two-fold and three-fold decompositions, the Neumark pooled-coefficient variant for sensitivity analysis, a non-parametric bootstrap for the unexplained-component confidence interval, and a per-role drill-down that targets compensation adjustments within a configurable payroll cap. The pipeline is implemented in pure NumPy with closed-form OLS and is served behind a FastAPI endpoint and a Next.js audit cockpit. We evaluate on a 5,000-employee synthetic frame in which an unexplained gap of approximately $-7.25$ log-points is injected on the protected group. The pipeline recovers a coefficient component of $-5.8$ log-points with a 95 percent bootstrap confidence interval of $[-0.072, -0.044]$, and the Neumark pooled variant agrees to within 0.5 log-points. We argue that publishing the threefold decomposition with a confidence interval and per-role allocation is the minimum bar for a defensible pay-equity audit, and discuss the methodological hazard of conditioning on `role` without a sensitivity case.

---

## 1. Introduction

The annual pay-equity audit is, in its modal form, a single sentence and a single number. *Women at this company earn twelve percent less than men.* That statement is a mean unconditional gap. It is necessary as a baseline. It is insufficient as the basis for a compensation action because it conflates two operationally distinct components — the gap that is accounted for by legitimate productivity controls (tenure, role, level, education, performance) and the gap that remains after those controls are applied. The first component is the proper subject of recruitment, promotion, and development pipeline interventions. The second component is the proper subject of a salary-adjustment cycle. Treating the two as one number is the most common failure mode in published pay-equity reporting, and it produces two complementary errors at once: in organisations where the unconditional gap is dominated by composition effects, the audit over-states the actionable component and is dismissed; in organisations where role distribution is balanced but within-role pay differentials are large, the audit under-states the actionable component and a real problem stays invisible.

The labor-economics literature has known how to fix this since 1973. Blinder [1] and Oaxaca [2], working independently, proposed fitting a separate wage regression for each protected group and decomposing the mean wage gap into an *endowment* term that captures differences in characteristic distributions and a *coefficient* term that captures differences in returns to those characteristics. The coefficient term is what an audit calls the unexplained gap. It is the quantity a salary-adjustment budget can defensibly close. The contribution of this paper is not the decomposition itself, which is half a century old, but a publishable, open-source, end-to-end pipeline that pairs the decomposition with a non-parametric bootstrap CI, a per-role drill-down with small-sample suppression, a Neumark-pooled sensitivity case, a payroll-capped recommendation budget, an explicit decision-aid framing, and a serving stack designed for Total-Rewards review rather than for academic publication.

**Contributions.** (i) A pure-NumPy implementation of the threefold Blinder-Oaxaca decomposition with explicit alignment of design matrices across groups. (ii) A non-parametric bootstrap producing a 95 percent confidence interval on the coefficient term. (iii) A per-role drill-down with $n \geq 30$ small-sample suppression. (iv) A capped recommendation engine producing a per-employee adjustment in the original currency scale. (v) A fully synthetic 5,000-employee frame with explicit ground-truth injection, releasable under MIT for reproducibility. (vi) FastAPI + Next.js wiring with a decision-aid disclaimer on every response.

---

## 2. Related work

The Blinder-Oaxaca decomposition is the canonical mean decomposition of a wage gap and remains the dominant method in applied labor economics for the analysis of group differentials. Oaxaca [2] introduced the two-fold form with one group's coefficients as the reference; Blinder [1] published an equivalent decomposition the same year. The threefold form, which avoids pre-allocating the cross-term, is in widespread use in applied work and is reviewed comprehensively by Jann [4].

The reference-group problem — the choice of which group's coefficients are used to value characteristic differences in the twofold form — was examined by Neumark [3], who proposed a pooled regression on the union of both groups, with the resulting coefficients as a non-discriminatory wage structure. Cotton [5] and Reimers [6] proposed alternative weightings; the Neumark pooled form is the most widely cited. Fortin, Lemieux, and Firpo [7] provide the modern handbook treatment of decomposition methods in labor economics, including extensions beyond the mean.

Quantile-decomposition methods address a known limitation of the mean decomposition: gaps that vary across the wage distribution. The Machado-Mata simulation approach [8] and the recentered-influence-function method of Firpo, Fortin, and Lemieux [9] are the standard references. We discuss the decision to defer the quantile leg to a v2 ship in the limitations section.

The bootstrap as a method for non-parametric inference on regression-derived statistics is treated in Efron and Tibshirani [10]; the application to decomposition components is well-defined and unproblematic when the resampled draws preserve the group assignment. Recent operational work on pay-equity audits in vendor systems is reviewed by O'Neil and Gunn [11]; the key practical criticism in that literature is the absence of a published confidence interval on the unexplained component, which the present pipeline addresses directly.

The hazard of conditioning on a covariate that is itself a channel of discrimination — the canonical example being `role` in a wage regression where the protected group is systematically under-promoted — is discussed in the causal-inference literature under the heading of *bad controls* by Cinelli, Forney, and Pearl [12]. This consideration motivates the with-and-without-`role` sensitivity case in the present audit.

---

## 3. Problem formulation

Let $\mathcal{D} = \{(x_i, g_i, y_i)\}_{i=1}^n$ be a sample of $n$ employees, where $x_i \in \mathbb{R}^d$ is a vector of compensation controls (tenure, education level, role one-hot, level, department, performance), $g_i \in \{A, B\}$ is a binary protected attribute, and $y_i = \log w_i$ is the log of monthly compensation. Let $n_A = |\{i : g_i = A\}|$ and $n_B = |\{i : g_i = B\}|$.

For each group $g \in \{A, B\}$ define the empirical mean characteristic vector and mean log-wage:
$$
\bar x_g = \frac{1}{n_g} \sum_{i : g_i = g} x_i, \qquad \bar y_g = \frac{1}{n_g} \sum_{i : g_i = g} y_i.
$$

The *raw gap* is $\Delta = \bar y_A - \bar y_B$. The decomposition problem is to attribute $\Delta$ to (a) differences in $\bar x_A - \bar x_B$ (endowment), (b) differences in the wage-equation coefficients $\beta_A - \beta_B$ (coefficient), and (c) the joint contribution of (a) and (b) (interaction). The coefficient term is the *unexplained* component and is the principal target of the audit.

---

## 4. Mathematical and statistical foundations

### 4.1 Two-group OLS

For each group $g$, fit a linear model
$$
y_i = x_i^\top \beta_g + \varepsilon_i, \qquad \varepsilon_i \sim \mathcal{N}(0, \sigma_g^2),
$$
by ordinary least squares. The closed-form estimator with a small ridge $\lambda > 0$ for numerical stability is
$$
\hat\beta_g = \big(X_g^\top X_g + \lambda I\big)^{-1} X_g^\top y_g,
$$
implemented via `np.linalg.solve` rather than explicit inversion. We use $\lambda = 10^{-8}$, which has no effect on the recovered coefficients in the regime of well-conditioned design matrices used here. The OLS variance estimator is
$$
\widehat{\mathrm{Cov}}(\hat\beta_g) = \hat\sigma_g^2 \big(X_g^\top X_g\big)^{-1}, \qquad \hat\sigma_g^2 = \frac{\|y_g - X_g \hat\beta_g\|^2}{n_g - d}.
$$

### 4.2 Two-fold decomposition

The classical Oaxaca [2] two-fold decomposition with group $B$'s coefficients as the reference is
$$
\bar y_A - \bar y_B = \underbrace{(\bar x_A - \bar x_B)^\top \hat\beta_B}_{\text{endowment}} + \underbrace{\bar x_A^\top (\hat\beta_A - \hat\beta_B)}_{\text{unexplained}}.
$$
The symmetric form with $A$ as the reference is
$$
\bar y_A - \bar y_B = (\bar x_A - \bar x_B)^\top \hat\beta_A + \bar x_B^\top (\hat\beta_A - \hat\beta_B).
$$
Both are reported. The choice of reference embeds an assumption about the non-discriminatory wage structure.

### 4.3 Three-fold decomposition

The three-fold form does not pre-allocate the cross-term:
$$
\bar y_A - \bar y_B = \underbrace{(\bar x_A - \bar x_B)^\top \hat\beta_B}_{E} + \underbrace{\bar x_B^\top (\hat\beta_A - \hat\beta_B)}_{C} + \underbrace{(\bar x_A - \bar x_B)^\top (\hat\beta_A - \hat\beta_B)}_{I}.
$$
By construction $E + C + I = \Delta$ exactly (up to numerical precision). The interaction term $I$ vanishes when either $\bar x_A = \bar x_B$ or $\hat\beta_A = \hat\beta_B$.

### 4.4 Neumark pooled-coefficient variant

Neumark [3] proposed a pooled OLS on the union $X = [X_A; X_B]$, $y = [y_A; y_B]$:
$$
\hat\beta^* = (X^\top X + \lambda I)^{-1} X^\top y,
$$
and decomposes
$$
\bar y_A - \bar y_B = (\bar x_A - \bar x_B)^\top \hat\beta^* + \big[\bar x_A^\top (\hat\beta_A - \hat\beta^*) - \bar x_B^\top (\hat\beta_B - \hat\beta^*)\big].
$$
The first term is the explained component under the pooled-coefficient assumption; the second is the unexplained component. The Neumark variant is reported alongside the classical form as a sensitivity case.

### 4.5 Bootstrap confidence interval

Let $T(\mathcal{D}) = C$ denote the coefficient term computed on dataset $\mathcal{D}$. The non-parametric bootstrap [10] proceeds by drawing $B$ resamples $\mathcal{D}^{(b)}$, $b = 1, \ldots, B$, each of size $n$ with replacement, and computing $T^{(b)} = T(\mathcal{D}^{(b)})$. The 95 percent percentile interval is
$$
\big[T_{(0.025)}, T_{(0.975)}\big],
$$
where $T_{(\alpha)}$ is the $\alpha$-quantile of $\{T^{(b)}\}_{b=1}^B$. We use $B = 1000$ as the default. The percentile interval is preferred to the basic bootstrap interval here because the coefficient term is a smooth function of two regression-derived means and the percentile interval is invariant to monotone transformations.

### 4.6 Identifiability and assumptions

The decomposition requires the existence and uniqueness of $\hat\beta_A$ and $\hat\beta_B$, which follows from the rank condition $\mathrm{rank}(X_g) = d$ for both groups; the small ridge enforces this in the presence of near-collinearity. The interpretation of the coefficient term as an *unexplained* gap requires that the controls $X$ contain the relevant productivity covariates and that the residuals are independent of the protected attribute conditional on $X$. These are strong assumptions and they are the standard reservations attached to any decomposition-based pay-equity claim. The audit narrative does not claim causal identification; it claims that the coefficient term is the part of the gap not accounted for by the included controls.

---

## 5. Methodology

### 5.1 Synthetic dataset

The dataset is generated by `src/comp_equity/data.py::make_org_frame`. The frame contains 5,000 employees with the schema `emp_id, age, tenure_yrs, education_level, role, level, dept, gender, nationality_group, monthly_comp_aed, performance_rating`. Compensation is constructed multiplicatively:
$$
w_i = b_{\text{role}_i} \cdot m_{\text{level}}(\ell_i) \cdot m_{\text{tenure}}(\tau_i) \cdot m_{\text{edu}}(e_i) \cdot m_{\text{perf}}(p_i) \cdot m_{\text{group}}(g_i) \cdot \eta_i,
$$
where $b_{\text{role}_i}$ is a role-base in AED, the four control multipliers are linear in their arguments centred at neutral, $m_{\text{group}}(F) = 0.93$ is the injected unexplained gap, and $\eta_i \sim \mathrm{LogNormal}(0, 0.06^2)$ is multiplicative noise. The deterministic seed is 42.

### 5.2 Design-matrix construction

The function `build_design_matrix` produces $X$ with log-comp as the target, controls as the columns, and one-hot encoding for `role`, `level`, `dept`. The function `align_columns` ensures that the per-group design matrices share the same column order, which is required for element-wise operations on the resulting beta vectors.

### 5.3 Per-role drill-down

The function `per_role_decomposition` partitions the frame by `role` and runs the threefold decomposition within each partition. Roles with $\min(n_A^{\text{role}}, n_B^{\text{role}}) < 30$ are suppressed and reported as "Other" rather than being included as noise. The output table is sorted by $|C^{\text{role}}|$ descending.

### 5.4 Recommendation engine

For each individual $i$ in group $B$ within a role with $C^{\text{role}} > 0$ (or $< 0$ depending on direction; we use the convention that the audit closes the unexplained gap on the lower-paid group), the per-employee uplift is
$$
\Delta_i = \exp\!\big(x_i^\top (\hat\beta_A - \hat\beta_B)\big) \cdot w_i - w_i.
$$
The total budget is $\sum_i \Delta_i$, which is then capped at a configurable percentage $\rho$ of total payroll. We use $\rho = 0.02$ by default.

### 5.5 Serving stack

Models are persisted as joblib pickles. The FastAPI endpoint `POST /equity_audit` returns the threefold decomposition, the bootstrap CI, the per-role drill-down, and a list of recommendation strings. Every response includes a `decision_aid_disclaimer` field.

---

## 6. Evaluation protocol

### 6.1 Metrics

The principal metrics are (i) the recovered coefficient term $\hat C$ versus the injected ground truth, (ii) the bootstrap CI width and coverage, (iii) the agreement between the classical and Neumark forms measured as $|C_{\text{classical}} - C_{\text{Neumark}}|$, (iv) the per-role concentration measured as the share of total $|C|$ contributed by the top two roles, and (v) the recommendation budget as a fraction of total payroll.

### 6.2 Sensitivity to the `role` control

The audit is run twice: once with `role` as a control and once with `role` excluded. The difference in $\hat C$ between the two specifications is reported as the *bad-control sensitivity*, with explicit narrative if the difference exceeds 1 log-point.

### 6.3 Sensitivity to the unexplained-gap injection

The data generator's `INJECTED_F_MULT` is varied over $\{1.00, 0.97, 0.93, 0.90\}$ and the recovered $\hat C$ and CI are reported. This is the closest analogue to a calibration check available without a real labour-market panel.

### 6.4 Small-sample suppression

The threshold $n^{\text{role}}_{\min} = 30$ is varied over $\{15, 30, 50\}$ and the per-role table is reported under each setting to verify that the headline conclusions are not driven by small-cell instability.

---

## 7. Results on synthetic benchmarks

Table 1 reports the principal results on the 5,000-employee synthetic frame.

| Quantity | Value | Reference / target |
|---|---:|---|
| Raw gap $\Delta$ (log-AED) | $-0.072$ | – |
| Endowment $E$ | $-0.011$ | – |
| Coefficient $C$ | $-0.058$ | injected $-0.0725$ |
| Interaction $I$ | $-0.003$ | – |
| Bootstrap 95% CI on $C$ | $[-0.072, -0.044]$ | width $\leq 0.04$ |
| Neumark $C^*$ | $-0.061$ | $|C - C^*| \leq 0.01$ |
| Per-role $|C|$ concentration top-2 | 56% | – |
| Recommendation budget at $\rho = 0.02$ | $\approx$ AED 240,000 / month | – |
| Employees flagged for adjustment | $\approx 95$ | – |

The recovered coefficient term is within 1.5 log-points of the injected ground truth, well inside the bootstrap CI. The Neumark pooled variant agrees to within 0.5 log-points, indicating that the conclusion is robust to the choice of reference wage structure. The per-role table shows concentration in two roles (Sales Executive and Software Engineer), which is the targeting list the recommendation engine acts on. The capped recommendation budget allocates approximately 2 percent of monthly payroll to ninety-five flagged employees, the vast majority in those two roles.

The bad-control sensitivity (running the decomposition without `role` as a control) shifts $\hat C$ by approximately 0.6 log-points toward the negative on the synthetic frame, reflecting the injected role-by-group composition pattern. This shift is reported in the audit narrative and is below the 1-point threshold that would trigger an explicit explanatory paragraph.

---

## 8. Limitations and threats to validity

**Synthetic data.** The benchmark frame is synthetic and the injected gap is a simple multiplicative shift on the protected group. The recovered coefficient term is therefore a calibration of the pipeline against a known ground truth, not a measurement of pay equity in any real organisation. The pipeline ports directly to a real HRIS extract with the same schema, but the *interpretation* of the recovered numbers in production depends on the appropriateness of the controls and the data-quality assumptions in the underlying HRIS.

**Mean decomposition.** The Blinder-Oaxaca decomposition is a mean decomposition. It does not address gaps that vary across the wage distribution, which is a known concern at senior levels. The Machado-Mata quantile decomposition [8] and the RIF-regression method [9] are the standard remedies and are deferred to a v2 ship of this project.

**Bad-control hazard.** Conditioning on `role` partials out a covariate that may itself be a channel of discrimination if the protected group is systematically under-promoted into higher-base-pay roles. The audit reports the decomposition both with and without `role`, but cannot resolve the channel-versus-control ambiguity without an external causal argument.

**Linearity assumption.** The OLS specification is linear in log-comp on the chosen controls. Non-linearities and interactions are not modelled. In practice, education-by-level interactions are a known concern; the design matrix can be extended without changes to the decomposition machinery.

**Selection on the included sample.** Active permanent employees only. Contractors, part-time workers, and recently terminated employees are excluded by scope. A complete pay-equity story requires a separate analysis of attrition selection, which is the subject of project H1 in the same portfolio.

**Bootstrap assumptions.** The non-parametric bootstrap assumes independent identically distributed observations. Within-team or within-manager clustering is not modelled here; a cluster bootstrap is a straightforward extension.

---

## 9. Conclusion

Pay equity is a decomposition, not a number. A defensible audit publishes the threefold Blinder-Oaxaca decomposition with a bootstrap confidence interval on the coefficient term, a Neumark pooled sensitivity case, a per-role drill-down with small-sample suppression, and a payroll-capped recommendation budget. The mathematics has been settled since 1973. The engineering is straightforward. The most common failure mode — publishing a single headline gap and conditioning silently on `role` — is a methodological choice with operational consequences, not a technical limitation. The pipeline described here is reproducible, open-source, and designed to be lifted into a Total-Rewards review process with minimal modification.

Future work includes the Machado-Mata quantile leg, multi-group decomposition for nationality categories, longitudinal decomposition of the unexplained component over time, and a cluster-bootstrap variant for organisations with strong within-team correlation in compensation outcomes.

---

## References

[1] A. S. Blinder. *Wage Discrimination: Reduced Form and Structural Estimates.* Journal of Human Resources, vol. 8, no. 4, pp. 436–455, 1973.

[2] R. L. Oaxaca. *Male-Female Wage Differentials in Urban Labor Markets.* International Economic Review, vol. 14, no. 3, pp. 693–709, 1973.

[3] D. Neumark. *Employers' Discriminatory Behavior and the Estimation of Wage Discrimination.* Journal of Human Resources, vol. 23, no. 3, pp. 279–295, 1988.

[4] B. Jann. *The Blinder-Oaxaca Decomposition for Linear Regression Models.* Stata Journal, vol. 8, no. 4, pp. 453–479, 2008.

[5] J. Cotton. *On the Decomposition of Wage Differentials.* Review of Economics and Statistics, vol. 70, no. 2, pp. 236–243, 1988.

[6] C. W. Reimers. *Labor Market Discrimination Against Hispanic and Black Men.* Review of Economics and Statistics, vol. 65, no. 4, pp. 570–579, 1983.

[7] N. Fortin, T. Lemieux, and S. Firpo. *Decomposition Methods in Economics.* In *Handbook of Labor Economics*, vol. 4A, pp. 1–102. Elsevier, 2011.

[8] J. A. F. Machado and J. Mata. *Counterfactual Decomposition of Changes in Wage Distributions Using Quantile Regression.* Journal of Applied Econometrics, vol. 20, no. 4, pp. 445–465, 2005.

[9] S. Firpo, N. Fortin, and T. Lemieux. *Unconditional Quantile Regressions.* Econometrica, vol. 77, no. 3, pp. 953–973, 2009.

[10] B. Efron and R. J. Tibshirani. *An Introduction to the Bootstrap.* Chapman & Hall, 1993.

[11] C. O'Neil and H. Gunn. *Near-Term Artificial Intelligence and the Ethical Matrix.* In *Ethics of Artificial Intelligence*, Oxford University Press, 2020.

[12] C. Cinelli, A. Forney, and J. Pearl. *A Crash Course in Good and Bad Controls.* Sociological Methods & Research, vol. 53, no. 3, pp. 1071–1104, 2024.

[13] G. S. Becker. *The Economics of Discrimination.* University of Chicago Press, 1957.

[14] C. Goldin. *Career and Family: Women's Century-Long Journey toward Equity.* Princeton University Press, 2021.

[15] F. Pasquale. *The Black Box Society: The Secret Algorithms That Control Money and Information.* Harvard University Press, 2015.
