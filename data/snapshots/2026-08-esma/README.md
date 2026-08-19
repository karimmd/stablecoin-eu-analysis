# ESMA Interim MiCA Register — primary source extract

**Downloaded:** 2026-08-13 from
https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica
(five CSV files: CASPS, EMTWP, ARTZZ, OTHER, NCASP).

**Why:** the manuscript previously sourced all register figures to `binar2026mica`, a Polish
consultancy blog summarising ESMA data. SKILLS.md §1.6 forbids aggregator pages as a source for
authorisation status. These are the register files themselves.

## Dated cohorts, reconstructed from `ac_authorisationNotificationDate`

Counts are DISTINCT LEIs, not rows (the CASP file carries one row per entity-service block).

| As of | Authorised CASPs | Notifying services beyond home state | Share |
|---|---:|---:|---:|
| 2025-11-30 | 107 | 85 | 79.4% |
| 2026-04-30 | **199** | **138** | **69.3%** |
| 2026-08-13 | 324 | 202 | 62.3% |

Other counts at 2026-08-13: EMT issuers 23 distinct LEIs (43 EMT white-paper rows);
**ART issuers 0**; other-crypto-asset white papers 972 rows; non-compliant entities listed 167.
EMT issuers authorised on or before 2026-04-30: **22**.

## Agreement and disagreement with the April 2026 consultancy summary

**Confirmed:** 199 CASPs; 23 home member states; Germany 53 (26.6%); zero ART issuers.

**Corrected:**
- Passporting was reported as "171 of 199" (85.9%). The register gives **138 of 199 (69.3%)**.
- EMT issuers were reported as 20. The register gives **22** as of 2026-04-30.
- The reported country list named Norway and Lithuania among the largest groups. Neither is in
  the top eight. **Cyprus (12) and Ireland (12) are, and were omitted.**

## Analytical note

The passporting share **declines** across the three dates (79.4% → 69.3% → 62.3%) even as the
absolute number rises. Early authorisations were dominated by firms seeking pan-EU reach; later
entrants are more often domestically focused. Any claim that "passporting is widespread and
increasing" is not supported by the register.
