#!/usr/bin/env python3
# Authorised crypto-asset service providers by home member state.
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 13, "axes.linewidth": 1.1})

df = pd.read_csv(DATA_DIR / "european_country_regulatory_status.csv")
agg = df[df["Country"] == "EU/EEA Aggregate"]
cty = df[df["Country"] != "EU/EEA Aggregate"].copy()
cty["n"] = cty["Licensed Issuers"].astype(int)
cty = cty.sort_values("n")

total = int(agg["Licensed Issuers"].iloc[0]) if not agg.empty else cty["n"].sum()

# EU-authorised euro-stablecoin issuance is concentrated in a few states; mark the
# states that host an authorised EUR stablecoin issuer as a secondary encoding.
HOSTS = {"Germany", "France", "Malta", "Netherlands", "Luxembourg"}
def is_agg(c): return str(c).startswith("Other")
colors = ["#bdc3c7" if is_agg(c) else ("#27ae60" if c in HOSTS else "#95a5a6")
          for c in cty["Country"]]

fig, ax = plt.subplots(figsize=(6.6, 7.0))
bars = ax.barh(cty["Country"], cty["n"], color=colors, edgecolor="#2c3e50", linewidth=0.9)
for b, c in zip(bars, cty["Country"]):
    if is_agg(c):
        b.set_hatch("//")
for b, n in zip(bars, cty["n"]):
    ax.text(n + total * 0.012, b.get_y() + b.get_height() / 2,
            f"{n}  ({n/total*100:.0f}%)", va="center", fontsize=11.5, fontweight="bold",
            color="#2c3e50")

ax.set_xlabel("Authorised CASPs (distinct entities)", fontsize=13, fontweight="bold")
ax.set_xlim(0, max(cty["n"]) * 1.34)
ax.grid(axis="x", alpha=0.28, linestyle="--"); ax.set_axisbelow(True)
ax.tick_params(axis="y", labelsize=12)
ax.set_title(f"Authorised CASPs by home member state\n"
             f"ESMA register cohort, 30 April 2026 (n = {total})",
             fontsize=13.5, fontweight="bold", pad=12)

from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#27ae60", label="Hosts an authorised EUR issuer"),
                   Patch(color="#95a5a6", label="No authorised EUR issuer"),
                   Patch(facecolor="#bdc3c7", hatch="//", edgecolor="#2c3e50",
                         label="Aggregate of remaining states")],
          loc="center right", fontsize=10, framealpha=0.95)

plt.tight_layout()
for ext in ("pdf", "png"):
    plt.savefig(OUT_DIR / f"fig_regulatory.{ext}", format=ext, dpi=300, bbox_inches="tight")
plt.close()
print(f"CASP total {total}; states {len(cty)}")
print(cty[["Country", "n"]].to_string(index=False))
print(f"[SAVED] {OUT_DIR/'fig_regulatory.pdf'}")
