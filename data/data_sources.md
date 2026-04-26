# Data Sources — H18 Compensation Equity

## Primary

| # | Source | URL | Fields used | License |
|---|--------|-----|-------------|---------|
| 1 | Synthetic org frame (`src/comp_equity/data.py`) | n/a | All 11 columns (see `data_card.md`) | MIT |

## Secondary / reference

| Source | URL | Use |
|--------|-----|-----|
| Mercer Total Remuneration Survey (UAE) | https://www.mercer.com/ | Sanity-check role × level pay bands |
| BLS National Compensation Survey | https://www.bls.gov/ncs/ | Cross-check tenure / education returns |
| WTW Compensation Data | https://www.wtwco.com/ | Industry benchmarks |
| UAE Federal Open Data | https://u.ae/en/information-and-services/open-data | Nationality-mix sanity check |

## Synthetic generation
`src/comp_equity/data.py::make_org_frame(seed=42, n=5000)` writes
`data/processed/org_frame.parquet`. Deterministic — no individual records.

## How to regenerate
```bash
python -m comp_equity.data
```

## Attribution
This project uses no third-party datasets. The methodology references Blinder (1973), Oaxaca (1973), and Neumark (1988) — see `docs/03_methodology.md`.
