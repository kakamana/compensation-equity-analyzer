# Compensation Equity Analyzer

> **Blinder-Oaxaca decomposition for pay-equity audits — separating explained vs unexplained pay gaps.** Two OLS fits per group, three-way decomposition (endowment + coefficient + interaction), with per-role gap tables and a FastAPI + Next.js audit cockpit for HR Total-Rewards teams.

![Python](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![License](https://img.shields.io/badge/license-MIT-green)

## Why this project
- A typical pay-gap report shows a single headline number ("women earn 12% less"). This one shows **how much of that gap is explained by tenure / role / level / education — and how much is not**.
- Built for **Dubai HR** realities: multi-nationality workforce, mixed seniority, monthly comp in AED — but the decomposition method is the same one used by every credible labor-economics audit since Blinder (1973) and Oaxaca (1973).

## Table of contents
- [Business Requirements](./docs/01_business_requirements.md)
- [Feasibility Study](./docs/02_feasibility_study.md)
- [Methodology — Blinder-Oaxaca](./docs/03_methodology.md)
- [Evaluation Plan](./docs/04_evaluation.md)
- [Data card](./data/data_card.md) · [Data sources](./data/data_sources.md)
- [Notebooks](./notebooks/) · [Source](./src/comp_equity/) · [API](./api/main.py) · [UI](./ui/app/page.tsx)
- [CLAUDE.md](./CLAUDE.md) — paste prompt to resume in this folder

## Headline results (target)

| Metric | Baseline (mean diff) | Our decomposition | Target |
|---|---|---|---|
| Raw gap (AED / month) | reported | reported | n/a |
| Explained share | n/a | **~70%** | n/a |
| Unexplained share | n/a | **~30%** | n/a |
| Per-role audit table | absent | **present** | always present |
| Bootstrap 95% CI on unexplained gap | absent | **present** | report |

## Quickstart

```bash
pip install -e ".[dev]"
python -m comp_equity.data                    # generate 5,000-employee synthetic frame
python -m comp_equity.models                  # fit two-group OLS + decomposition; save artifacts
jupyter lab notebooks/
uvicorn api.main:app --reload
cd ui && npm install && npm run dev
```

## Stack
Python · pandas · scikit-learn · statsmodels · numpy · FastAPI · Next.js · Tailwind

## Author
Asad — MADS @ University of Michigan · Dubai HR
