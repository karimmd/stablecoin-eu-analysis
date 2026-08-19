# stablecoin-eu-analysis

Data and analysis code for the study *Distributed Autonomy under MiCA: Stablecoins as
Socio-Technical Infrastructures for the Eurozone's Integration Paradox*.

This repository is the reproducibility mirror for the manuscript. It contains the dated market
snapshots, the primary-source register extract, and the scripts that produce every data figure and
derived statistic reported in the paper.

---

## Contents

```
data/
  euro_stablecoin_market_data.csv          working issuer-level dataset (Table 1)
  european_country_regulatory_status.csv   authorised CASPs by home member state
  snapshots/
    2025-11/                               market snapshot, accessed 30 Nov 2025
    2026-04/                               market snapshot, accessed 29 Apr 2026
    2026-08-esma/                          ESMA Interim MiCA Register extract, 13 Aug 2026
scripts/
  fig_market_share.py                      market concentration and jurisdiction split
  fig_euro_growth.py                       composition change between the two snapshots
  fig_regulatory.py                        authorised CASPs by home member state
  fig_adoption.py                          observed growth rate underlying the scenario table
figures/                                   created on first run; receives the generated PDF/PNG
```

## Reproducing the figures

Requires Python 3 with `pandas` and `matplotlib`.

```bash
python3 scripts/fig_market_share.py
python3 scripts/fig_euro_growth.py
python3 scripts/fig_regulatory.py
```

Each script resolves its own paths, reads from `data/`, and writes PDF and PNG into
`figures/`, which it creates on first run. Rendered figures are not committed here; they live with
the manuscript.

The scripts are identical to those used to produce the figures in the paper except for the output
directory, which points at `figures/` rather than at the manuscript's source tree. No computation,
input data, or plotting parameter differs.

## Values the figures and the manuscript must agree on

| Quantity | Value |
|---|---|
| Total EUR-denominated stablecoin capitalisation (29 Apr 2026) | USD 675.5M |
| Share of the global stablecoin market | 0.21% |
| Herfindahl–Hirschman Index | 4568 |
| Top-three share | 90.7% |
| Issued from an EU-authorised entity | 94.0% |
| Issued from outside the EU authorisation perimeter | 6.0% |

Between the two snapshots (30 Nov 2025 → 29 Apr 2026), aggregate EUR capitalisation was
effectively flat (+0.1%) while EU-authorised issuance grew 46.3% and third-country or
non-authorised issuance fell 60.5%. The segment recomposed rather than grew. Two dates are not a
trend; the interval is five months; and EURS left the CoinMarketCap category during the window,
which is a composition change rather than a redemption.

## Data sources and provenance

**Market data.** Capitalisation figures are from CoinMarketCap on the two access dates above.
Issuer-level attributes — legal issuer, authorisation status, home member state, ultimate parent
location — were verified individually against national registers and issuer disclosures. The
`Verification Note` column in `euro_stablecoin_market_data.csv` records the source consulted for
each attribute.

Jurisdiction is coded by the **legal entity that issues the token**, not by the location of its
corporate parent. EURC, the largest euro stablecoin in the segment, is issued by a French
electronic money institution owned by a US parent; it is coded France. The two codings give very
different pictures of the segment, and the distinction is part of the paper's argument rather than
a data-cleaning choice.

**Register data.** Supervisory counts come from the ESMA Interim MiCA Register files themselves,
not from any secondary summary. `data/snapshots/2026-08-esma/README.md` documents the
download, how the dated cohorts were reconstructed from `ac_authorisationNotificationDate`, and
where the register contradicts a widely circulated consultancy summary of the same data. Counts
are distinct LEIs, not rows.

## Scope

The conceptual framework figure in the manuscript carries no data and has no generating script.
Everything numeric in the paper is produced by the scripts here.

This repository mirrors the analysis layer only. It is not the manuscript source tree, and nothing
is built or run from it as part of preparing the paper.
