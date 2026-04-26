# Data Card — H18 Compensation Equity

## Dataset composition

| Layer | Source | Rows × cols | Purpose |
|-------|--------|-------------|---------|
| Synthetic org frame | `src/comp_equity/data.py::make_org_frame()` | 5,000 × 11 | Reproducible employee-level audit panel |

## Fields

| Field | Type | Range / values |
|---|---|---|
| `emp_id` | str | E-00001 … E-05000 |
| `age` | int | 22 – 62 |
| `tenure_yrs` | float | 0.1 – 30.0 |
| `education_level` | int (1–5) | 1=HS, 2=Diploma, 3=Bachelor, 4=Master, 5=PhD |
| `role` | str | one of 12 roles |
| `level` | int (1–7) | 1=Junior … 7=VP |
| `dept` | str | one of 6 departments |
| `gender` | str | "M", "F" |
| `nationality_group` | str | Emirati / South Asian / Western / Other |
| `monthly_comp_aed` | float | log-normal around role+level mean |
| `performance_rating` | int (1–5) | discrete |

## Generative process
- Comp baseline by `role × level` drawn from a published Mercer-style band, scaled to AED.
- Multiplicative effects: `1 + 0.025 × tenure_yrs`, `1 + 0.04 × (education_level - 3)`, `1 + 0.06 × (performance_rating - 3)`.
- **Injected unexplained gap:** group `F` is multiplied by `0.93` on top of all explained factors. The decomposition should recover ~7 log-points unexplained.
- Noise: log-normal with σ = 0.06.

## Known biases
- Synthetic only — no real labor-market noise structure.
- Role allocation is uniform by gender; in reality role choice is itself a discrimination channel (we discuss this caveat in `docs/03_methodology.md`).

## PII
None. All identifiers are synthetic.

## Splits
None — the audit fits on the full frame; bootstrap CIs come from row-level resampling.

## Reproducing
```bash
python -m comp_equity.data
```
Deterministic seed = 42.

## Licensing
- MIT (this repo).
