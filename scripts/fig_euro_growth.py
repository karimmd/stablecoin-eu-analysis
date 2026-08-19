#!/usr/bin/env python3
# EUR stablecoin market growth trajectory.

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUT_DIR = Path(__file__).resolve().parent.parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Publication style
plt.style.use("default")
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 13,
    "axes.linewidth": 1.2,
    "grid.linewidth": 0.8,
})

# ── Load current observation from CSV ───────────────────────────────────────
import pandas as pd
df = pd.read_csv(DATA_DIR / "euro_stablecoin_market_data.csv")
status_cols = [col for col in df.columns if col.startswith("Status as of")]
snapshot_label = status_cols[0].replace("Status as of ", "") if status_cols else "data snapshot"
eur_active = df[
    (df["Peg Currency"] == "EUR") &
    (~df["Stablecoin Name"].str.contains("Total|Nine-Bank", na=False))
]
current_total_usd = eur_active["Market Cap (USD millions)"].sum()
current_total_eur = eur_active["Market Cap (EUR millions)"].sum()

if "2026" in snapshot_label:
    snapshot_year = 2026.33
    snapshot_tick_label = "Apr 2026"
    prior_anchor_year = 2025
    prior_anchor_value = 674.7
    scenario_end_year = 2027
    scenario_label = "Baseline scenario (2027)"
else:
    snapshot_year = 2025
    snapshot_tick_label = snapshot_label
    prior_anchor_year = None
    prior_anchor_value = None
    scenario_end_year = 2026
    scenario_label = "Baseline scenario (2026)"

# ── Historical data (published market snapshots) ────────────────────────────
# Sources: CoinGecko annual reports, STASIS announcements, industry summaries.
# These are approximate market-wide totals, not derivable from the current CSV.
years_hist = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
values_hist_usd = [0.5, 2.0, 5.0, 15.0, 50.0, 180.0, 458.0]
if prior_anchor_year is not None:
    years_hist.append(prior_anchor_year)
    values_hist_usd.append(prior_anchor_value)
years_hist.append(snapshot_year)
values_hist_usd.append(current_total_usd)
# Earlier values are reconstructed snapshots; the final value is the CSV anchor.

# ── Scenario projections (2025-2026) ────────────────────────────────────────
# Assumptions for baseline scenario:
#   1. MiCA enforcement drives institutional confidence from mid-2025
#   2. Nine-bank consortium launches in H2 2026 as announced
#   3. No major USD stablecoin de-pegging event in EU
# Conservative: slow growth, regulatory friction, USD dominance persists
# Baseline: MiCA takes effect, consortium launches on schedule
# Upper: accelerated institutional adoption + digital euro complementarity
scenario_years = [snapshot_year, scenario_end_year]
scenario_conservative = [current_total_usd, current_total_usd * 1.3]   # +30%
scenario_baseline = [current_total_usd, current_total_usd * 1.8]       # +80%
scenario_upper = [current_total_usd, current_total_usd * 2.8]          # +180%

# ── Build figure ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))

# Historical (observed) line
ax.plot(
    years_hist, values_hist_usd, linewidth=3, color="#27ae60", marker="o",
    markersize=9, markerfacecolor="#27ae60", markeredgecolor="white",
    markeredgewidth=2, label="Observed market cap (historical)", zorder=3,
)
ax.fill_between(years_hist, values_hist_usd, alpha=0.12, color="#27ae60", zorder=1)

# Scenario fan
ax.fill_between(
    scenario_years, scenario_conservative, scenario_upper,
    alpha=0.15, color="#f39c12", zorder=1,
)
ax.plot(
    scenario_years, scenario_baseline, linewidth=2.5, color="#f39c12",
    linestyle="--", marker="s", markersize=8, markerfacecolor="#f39c12",
    markeredgecolor="white", markeredgewidth=2,
    label=scenario_label, zorder=3,
)
ax.plot(
    scenario_years, scenario_conservative, linewidth=1.5, color="#e67e22",
    linestyle=":", marker="v", markersize=7,
    label="Conservative scenario", zorder=2,
)
ax.plot(
    scenario_years, scenario_upper, linewidth=1.5, color="#e67e22",
    linestyle=":", marker="^", markersize=7,
    label="Upper scenario", zorder=2,
)

# Vertical divider at the observation/projected boundary
ax.axvline(x=snapshot_year, color="gray", linestyle="-", linewidth=1.2, alpha=0.5)
ax.text(snapshot_year - 0.35, ax.get_ylim()[1] * 0.45, "Observed\nmarket\nsnapshots",
        fontsize=11, ha="right", va="top", style="italic", color="#27ae60")
ax.text(snapshot_year + 0.35, ax.get_ylim()[1] * 0.3, "Scenarios\n(listed below)",
        fontsize=11, ha="left", va="top", style="italic", color="#f39c12")

# Key annotations (observed milestones only)
milestones_obs = [
    (2018, 0.5, "EURS launch"),
    (2023, 180.0, "EURCV launch\n(institutional entry)"),
    (snapshot_year, current_total_usd, f"${current_total_usd:.0f}M\n({snapshot_tick_label})"),
]
for yr, val, lbl in milestones_obs:
    ax.annotate(
        lbl, xy=(yr, val),
        xytext=(yr + 0.3, val * 2.0 if val < 50 else val * 1.5),
        fontsize=10, weight="bold", ha="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#d5f4e6", alpha=0.8, edgecolor="#27ae60"),
        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.2),
    )

# Scenario assumptions box
assumptions = (
    "Scenarios:\n"
    f"  Baseline: MiCA enforced, consortium scales by {scenario_end_year}\n"
    "  Conservative: regulatory friction, slow adoption\n"
    "  Upper: accelerated institutional + digital euro synergy"
)
ax.text(
    0.98, 0.02, assumptions, transform=ax.transAxes,
    fontsize=9, verticalalignment="bottom", horizontalalignment="right",
    multialignment="left",
    bbox=dict(boxstyle="round", facecolor="#fff9e6", alpha=0.9, edgecolor="#f39c12", linewidth=1.5),
    family="monospace",
)

# Formatting
ax.set_xlabel("Year", fontsize=14, weight="bold", labelpad=10)
ax.set_ylabel("Market Capitalization (USD Millions)", fontsize=14, weight="bold", labelpad=10)
xticks = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, snapshot_year, scenario_end_year]
xticklabels = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", snapshot_tick_label, str(scenario_end_year)]
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels, fontsize=12)
ax.set_yscale("log")
ax.set_ylim(0.2, 5000)
ax.grid(True, alpha=0.3, linestyle="--", which="both")
ax.set_axisbelow(True)

# Phase shading
ax.axvspan(2018, 2022.5, alpha=0.04, color="gray")
ax.axvspan(2022.5, snapshot_year, alpha=0.04, color="green")
ax.axvspan(snapshot_year, scenario_end_year + 0.5, alpha=0.04, color="#f39c12")

phase_legend = [
    mpatches.Patch(facecolor="gray", alpha=0.2, label="Niche phase (2018-2022)"),
    mpatches.Patch(facecolor="green", alpha=0.2, label="Institutional entry (2023-2024)"),
    mpatches.Patch(facecolor="#f39c12", alpha=0.2, label=f"Scenario period ({snapshot_tick_label}-{scenario_end_year})"),
]
line_legend = ax.legend(loc="upper left", fontsize=11, framealpha=0.95, edgecolor="black")
ax.add_artist(line_legend)
ax.legend(handles=phase_legend, loc="center left", fontsize=11, framealpha=0.95, edgecolor="black")

plt.tight_layout()

# ── Save ─────────────────────────────────────────────────────────────────────
output_pdf = OUT_DIR / "fig_euro_growth.pdf"
output_png = OUT_DIR / "fig_euro_growth.png"
plt.savefig(output_pdf, format="pdf", dpi=300, bbox_inches="tight")
plt.savefig(output_png, format="png", dpi=300, bbox_inches="tight")
plt.close()

# ── Print summary ────────────────────────────────────────────────────────────
print("=" * 80)
print("FIGURE: EUR STABLECOIN MARKET GROWTH TRAJECTORY")
print("Evidence classification: MIXED (observed historical + analytical scenario)")
print("=" * 80)
print(f"\nCSV anchor ({snapshot_label}): ${current_total_usd:.1f}M USD / EUR {current_total_eur:.1f}M")
print(f"\nHistorical trajectory (observed/constructed):")
for yr, val in zip(years_hist, values_hist_usd):
    print(f"  {yr}: ${val:>8.1f}M")
print(f"\nScenario projections for {scenario_end_year}:")
print(f"  Conservative: ${scenario_conservative[1]:.0f}M (+{(scenario_conservative[1]/current_total_usd-1)*100:.0f}%)")
print(f"  Baseline:     ${scenario_baseline[1]:.0f}M (+{(scenario_baseline[1]/current_total_usd-1)*100:.0f}%)")
print(f"  Upper:        ${scenario_upper[1]:.0f}M (+{(scenario_upper[1]/current_total_usd-1)*100:.0f}%)")
print(f"\n[SAVED] {output_pdf}")
print(f"[SAVED] {output_png}")
print("=" * 80)
