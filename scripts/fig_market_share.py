#!/usr/bin/env python3
# Global stablecoin market distribution and EUR breakdown.

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Publication style
plt.style.use("default")
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 12,
    "axes.linewidth": 1.2,
    "grid.linewidth": 0.8,
})

# ── Load data from CSV ──────────────────────────────────────────────────────
df = pd.read_csv(DATA_DIR / "euro_stablecoin_market_data.csv")
status_cols = [col for col in df.columns if col.startswith("Status as of")]
snapshot_label = status_cols[0].replace("Status as of ", "") if status_cols else "data snapshot"

# Separate EUR stablecoins (active only, exclude consortium and totals)
eur_active = df[
    (df["Peg Currency"] == "EUR") &
    (~df["Stablecoin Name"].str.contains("Total|Nine-Bank", na=False))
].copy()

# USD comparators for global market context
usdt_row = df[df["Stablecoin Name"] == "USDT"].iloc[0]
usdc_row = df[df["Stablecoin Name"] == "USDC"].iloc[0]
total_market_rows = df[df["Stablecoin Name"] == "Total Stablecoin Market"]

total_eur = eur_active["Market Cap (USD millions)"].sum()
if not total_market_rows.empty:
    total_global = total_market_rows.iloc[0]["Market Cap (USD millions)"]
    other_stablecoins = total_global - usdt_row["Market Cap (USD millions)"] - usdc_row["Market Cap (USD millions)"] - total_eur
else:
    other_rows = df[df["Stablecoin Name"].isin(["Other Stablecoins", "Other USD Stablecoins"])]
    other_stablecoins = other_rows.iloc[0]["Market Cap (USD millions)"] if not other_rows.empty else 0
    total_global = usdt_row["Market Cap (USD millions)"] + usdc_row["Market Cap (USD millions)"] + other_stablecoins + total_eur

# ── Compute concentration metrics ───────────────────────────────────────────
eur_caps = eur_active.sort_values("Market Cap (USD millions)", ascending=False)
eur_values = eur_caps["Market Cap (USD millions)"].values
eur_names = eur_caps["Stablecoin Name"].values
eur_issuers = eur_caps["Issuer"].values

total_eur_check = eur_values.sum()
top3_sum = eur_values[:3].sum()
top3_pct = top3_sum / total_eur_check * 100

# HHI (Herfindahl-Hirschman Index), scaled to 0-10000
shares_pct = (eur_values / total_eur_check) * 100
hhi = sum(s ** 2 for s in shares_pct)

# EU-authorised vs non-EU issuance share.
# NOTE (2026-08-13): the "Country" column records the JURISDICTION OF AUTHORISATION, not the
# location of the ultimate parent. These differ for EURC, whose MiCA issuer is a French EMI
# (Circle Mint Europe SAS, ACPR reg. 17788) owned by a US parent. Ownership is carried
# separately in the "Ultimate Parent Location" column and is marked on the chart by hatching.
eu_countries = {"Malta", "France", "Luxembourg", "Germany", "Netherlands", "Ireland",
                "Italy", "Spain", "Belgium", "Austria", "Netherlands (Consortium)"}
eur_caps["EU_Authorised"] = eur_caps["Country"].isin(eu_countries)
eur_caps["Foreign_Parent"] = ~eur_caps["Ultimate Parent Location"].isin(eu_countries)
eu_share = eur_caps.loc[eur_caps["EU_Authorised"], "Market Cap (USD millions)"].sum()
non_eu_share = eur_caps.loc[~eur_caps["EU_Authorised"], "Market Cap (USD millions)"].sum()
foreign_owned_eu_auth = eur_caps.loc[
    eur_caps["EU_Authorised"] & eur_caps["Foreign_Parent"], "Market Cap (USD millions)"].sum()

# ── Figure: Two-panel ───────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 7))
gs = fig.add_gridspec(1, 2, wspace=0.35)

# === Panel A: Global market pie chart ===
ax1 = fig.add_subplot(gs[0, 0])

global_labels = [
    f"USDT\n({usdt_row['Market Cap (USD millions)']/total_global*100:.1f}%)",
    f"USDC\n({usdc_row['Market Cap (USD millions)']/total_global*100:.1f}%)",
    f"Other stablecoins\n({other_stablecoins/total_global*100:.1f}%)",
    f"EUR Stablecoins\n({total_eur/total_global*100:.2f}%)",
]
global_values = [
    usdt_row["Market Cap (USD millions)"],
    usdc_row["Market Cap (USD millions)"],
    other_stablecoins,
    total_eur,
]
global_colors = ["#e74c3c", "#3498db", "#95a5a6", "#27ae60"]

wedges, texts, autotexts = ax1.pie(
    global_values,
    labels=global_labels,
    autopct="%1.2f%%",
    colors=global_colors,
    startangle=90,
    textprops={"fontsize": 11, "weight": "bold"},
    wedgeprops={"edgecolor": "white", "linewidth": 2},
)
for at in autotexts:
    at.set_color("white")
    at.set_fontsize(11)
    at.set_weight("bold")

ax1.set_title(
    f"Global Stablecoin Market Share\n(Total: ${total_global/1000:.1f}B, {snapshot_label})",
    fontsize=13, weight="bold", pad=20,
)

# === Panel B: EUR stablecoin horizontal bar ===
ax2 = fig.add_subplot(gs[0, 1])

y_pos = np.arange(len(eur_names))
bar_colors, bar_hatches = [], []
for country, foreign in zip(eur_caps["Country"].values, eur_caps["Foreign_Parent"].values):
    is_eu = country in eu_countries
    bar_colors.append("#27ae60" if is_eu else "#3498db")
    bar_hatches.append("//" if (is_eu and foreign) else "")

bars = ax2.barh(y_pos, eur_values, color=bar_colors, edgecolor="#1b5e20", linewidth=1.2)
for bar, h in zip(bars, bar_hatches):
    if h:
        bar.set_hatch(h)

for i, (bar, value) in enumerate(zip(bars, eur_values)):
    pct = (value / total_eur_check) * 100
    ax2.text(
        value + 5, bar.get_y() + bar.get_height() / 2,
        f"${value:.1f}M ({pct:.1f}%)",
        va="center", fontsize=10, weight="bold",
    )

labels = [f"{n}\n({iss})" for n, iss in zip(eur_names, eur_issuers)]
ax2.set_yticks(y_pos)
ax2.set_yticklabels(labels, fontsize=10, weight="bold")
ax2.set_xlabel("Market Capitalization (USD Millions)", fontsize=12, weight="bold")
ax2.set_title(
    f"EUR Stablecoin Ecosystem (Total: ${total_eur_check:.0f}M, {snapshot_label})\n"
    f"Top 3 = {top3_pct:.1f}%  |  HHI = {hhi:.0f}  |  "
    f"EU-authorised: {eu_share/total_eur_check*100:.1f}%  vs  Non-EU: {non_eu_share/total_eur_check*100:.1f}%\n"
    f"(of EU-authorised issuance, {foreign_owned_eu_auth/total_eur_check*100:.1f}% is foreign-owned)",
    fontsize=12, weight="bold", pad=20,
)
ax2.set_xlim(0, max(eur_values) * 1.3)
ax2.grid(axis="x", alpha=0.3, linestyle="--")
ax2.set_axisbelow(True)
ax2.invert_yaxis()

# EU / Non-EU legend
eu_patch = mpatches.Patch(color="#27ae60", label="EU-authorised issuer")
fo_patch = mpatches.Patch(facecolor="#27ae60", hatch="//", edgecolor="#1b5e20",
                          label="EU-authorised, foreign-owned parent")
non_eu_patch = mpatches.Patch(color="#3498db", label="Non-EU issuer")
ax2.legend(handles=[eu_patch, fo_patch, non_eu_patch], loc="lower right", fontsize=10)

plt.tight_layout()

# ── Save ─────────────────────────────────────────────────────────────────────
output_pdf = OUT_DIR / "fig_market_share.pdf"
output_png = OUT_DIR / "fig_market_share.png"
plt.savefig(output_pdf, format="pdf", dpi=300, bbox_inches="tight")
plt.savefig(output_png, format="png", dpi=300, bbox_inches="tight")
plt.close()

# ── Print summary ────────────────────────────────────────────────────────────
print("=" * 75)
print("FIGURE: GLOBAL STABLECOIN MARKET & EUR BREAKDOWN")
print("Evidence classification: OBSERVED EMPIRICAL EVIDENCE")
print("=" * 75)
print(f"\nData snapshot: {snapshot_label}")
print(f"Global market total: ${total_global:,.0f}M")
print(f"EUR stablecoin total: ${total_eur_check:,.1f}M ({total_eur_check/total_global*100:.2f}% of global)")
print(f"\nIssuer concentration:")
print(f"  Top-1 (EURC): {eur_values[0]:.1f}M ({eur_values[0]/total_eur_check*100:.1f}%)")
print(f"  Top-3: ${top3_sum:.1f}M ({top3_pct:.1f}%)")
print(f"  Top-5: ${eur_values[:5].sum():.1f}M ({eur_values[:5].sum()/total_eur_check*100:.1f}%)")
print(f"  HHI: {hhi:.0f} (0-10000 scale; {'highly' if hhi > 2500 else 'moderately' if hhi > 1500 else 'un-'} concentrated)")
print(f"\nJurisdiction of authorisation vs ownership:")
print(f"  EU-authorised issuance: ${eu_share:.1f}M ({eu_share/total_eur_check*100:.1f}%)")
print(f"  Non-EU issuance:        ${non_eu_share:.1f}M ({non_eu_share/total_eur_check*100:.1f}%)")
print(f"  Of which EU-authorised but foreign-owned: ${foreign_owned_eu_auth:.1f}M "
      f"({foreign_owned_eu_auth/total_eur_check*100:.1f}%)")
print(f"\nPer-coin breakdown:")
for name, cap, iss in zip(eur_names, eur_values, eur_issuers):
    print(f"  {name:<12} ({iss:<20}): ${cap:>8.2f}M ({cap/total_eur_check*100:>5.1f}%)")
print(f"\n[SAVED] {output_pdf}")
print(f"[SAVED] {output_png}")
print("=" * 75)
