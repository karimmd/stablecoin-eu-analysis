#!/usr/bin/env python3
# EUR stablecoin scenario paths.
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 13, "axes.linewidth": 1.1})

def eur_series(path):
    d = pd.read_csv(path)
    a = d[(d["Peg Currency"] == "EUR") &
          (~d["Stablecoin Name"].str.contains("Total|Nine-Bank", na=False))]
    return a.set_index("Stablecoin Name")["Market Cap (USD millions)"]

apr = eur_series(DATA_DIR / "snapshots/2026-04/euro_stablecoin_market_data.csv")
nov = eur_series(DATA_DIR / "snapshots/2025-11/euro_stablecoin_market_data.csv")

ANCHOR = apr.sum()
nov_adj = nov.drop(labels=["EURS"], errors="ignore").sum()
MONTHS = 5.0
OBS_ANNUAL = (ANCHOR / nov_adj) ** (12.0 / MONTHS) - 1
YEARS = [2026, 2027, 2028, 2029, 2030]
FRACTIONS = {"Lower": 0.40, "Central": 0.70, "Upper": 1.00}

PROFILES = pd.DataFrame({
    "Group": ["Early adopters"] * 3 + ["Mainstream"] * 4 + ["Emerging"] * 3 + ["Conservative"] * 2,
    "S2026": [25, 20, 18, 12, 15, 10, 11, 8, 7, 7, 3, 2],
    "S2028": [40, 38, 35, 30, 32, 25, 27, 20, 18, 18, 10, 8],
    "S2030": [65, 62, 58, 50, 55, 45, 48, 40, 38, 38, 25, 20],
})
GROUPS = ["Early adopters", "Mainstream", "Emerging", "Conservative"]
COLORS = ["#2ecc71", "#f39c12", "#3498db", "#e74c3c"]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.6, 7.0), gridspec_kw={"hspace": 0.45})

# ── Panel A: market capitalisation ─────────────────────────────────────────
for (name, frac), c, lw, ls in zip(FRACTIONS.items(),
                                   ["#e67e22", "#d35400", "#e67e22"],
                                   [1.4, 2.6, 1.4], [":", "-", ":"]):
    r = OBS_ANNUAL * frac
    path = [ANCHOR * (1 + r) ** (y - YEARS[0]) for y in YEARS]
    ax1.plot(YEARS, path, linestyle=ls, linewidth=lw, color=c,
             marker="s" if name == "Central" else None, markersize=6,
             label=f"{name}: {r*100:.0f}% p.a.")
    if name == "Central":
        ax1.text(YEARS[-1], path[-1] * 1.06, f"${path[-1]/1000:.1f}B", ha="right",
                 fontsize=12, fontweight="bold", color="#2c3e50")
lo = [ANCHOR * (1 + OBS_ANNUAL * 0.40) ** (y - YEARS[0]) for y in YEARS]
hi = [ANCHOR * (1 + OBS_ANNUAL * 1.00) ** (y - YEARS[0]) for y in YEARS]
ax1.fill_between(YEARS, lo, hi, alpha=0.13, color="#f39c12")
ax1.scatter([2026], [ANCHOR], s=85, color="#1b5e20", zorder=6,
            edgecolor="white", linewidth=1.4)
ax1.annotate(f"observed\n${ANCHOR:.0f}M", xy=(2026, ANCHOR), xytext=(2026.45, ANCHOR * 3.1),
             fontsize=11, color="#1b5e20", fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#1b5e20", lw=1.2))
ax1.set_xticks(YEARS)
ax1.set_ylabel("Market cap (USD m)", fontsize=12.5, fontweight="bold")
ax1.set_title("(a) Market capitalisation scenarios", fontsize=13, fontweight="bold")
ax1.legend(fontsize=10.5, loc="upper left", framealpha=0.95)
ax1.grid(axis="y", alpha=0.28, linestyle="--"); ax1.set_axisbelow(True)

# ── Panel B: adoption-rate scenarios ───────────────────────────────────────
xs = [2026, 2028, 2030]
for g, c in zip(GROUPS, COLORS):
    v = PROFILES[PROFILES["Group"] == g][["S2026", "S2028", "S2030"]].mean().values
    ax2.plot(xs, v, marker="o", markersize=7, linewidth=2, linestyle="--", color=c, label=g)
    ax2.text(xs[-1] + 0.10, v[-1], f"{v[-1]:.0f}%", va="center",
             fontsize=11, fontweight="bold", color="#2c3e50")
ax2.set_xticks(xs); ax2.set_xlim(2025.6, 2030.95); ax2.set_ylim(0, 76)
ax2.set_ylabel("Adoption rate (%)", fontsize=12.5, fontweight="bold")
ax2.set_title("(b) Adoption-rate scenarios by country group", fontsize=13, fontweight="bold")
ax2.legend(fontsize=10, loc="upper left", ncol=2, framealpha=0.95)
ax2.grid(axis="y", alpha=0.28, linestyle="--"); ax2.set_axisbelow(True)

plt.tight_layout()
for ext in ("pdf", "png"):
    plt.savefig(OUT_DIR / f"fig_adoption.{ext}", format=ext, dpi=300, bbox_inches="tight")
plt.close()

print(f"observed anchor        : ${ANCHOR:,.2f}M (2026-04-29)")
print(f"composition-adj. base  : ${nov_adj:,.2f}M (2025-11-30, EURS excluded both dates)")
print(f"observed annual rate   : {OBS_ANNUAL*100:.1f}%")
for n, f in FRACTIONS.items():
    r = OBS_ANNUAL * f
    print(f"  {n:<8} {f:.2f}x -> {r*100:5.1f}% p.a. -> 2030 ${ANCHOR*(1+r)**4:,.0f}M")
print(f"[SAVED] {OUT_DIR/'fig_adoption.pdf'}")
