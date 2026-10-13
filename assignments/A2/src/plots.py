r"""
Figures for Q2 and Q3.

  Q2a  recipe-size distribution: original vs 10 replica-based random cuisines
  Q2b  recipe-size distribution: original vs the inverse-transform cuisine (10x)
  Q3a  recipe-size distribution: original vs 10 size+frequency random cuisines
  Q3b  frequency-rank distribution: original vs the 10 frequency-controlled
       cuisines, with the Q2 uniform control drawn alongside for contrast

Axes are labelled, every series is in the legend, and the frequency-rank plot
uses log-log scaling because ingredient popularity spans several orders of
magnitude.
"""
from __future__ import annotations
import json
import pathlib
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "random_controls.json"
Q2 = ROOT / "outputs" / "Q2"
Q3 = ROOT / "outputs" / "Q3"
for d in (Q2, Q3):
    d.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 10, "axes.titlesize": 12, "axes.labelsize": 11,
    "axes.edgecolor": "#c9c9c4", "axes.linewidth": 0.8,
    "axes.titlecolor": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e6e6e2", "grid.linewidth": 0.7,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def hist_to_xy(h: dict, normalise: bool = False):
    xs = np.array(sorted(int(k) for k in h), dtype=int)
    ys = np.array([h[str(x)] for x in xs], dtype=float)
    if normalise:
        ys = ys / ys.sum()
    return xs, ys


def plot_size(original, randoms, path, title, sub, random_label,
              normalise=False, random_color=ORANGE):
    ox, oy = hist_to_xy(original, normalise)
    fig, ax = plt.subplots(figsize=(8.6, 5.0))

    ax.bar(ox, oy, width=0.8, color=BLUE, alpha=0.28, zorder=2,
           label=f"Original cuisine (N = {int(sum(original.values())):,})"
           if not normalise else "Original cuisine")
    ax.plot(ox, oy, color=BLUE, lw=2.6, marker="o", ms=4, zorder=3)

    # Random series are drawn ON TOP and DASHED, so that where they agree with
    # the original the blue line still shows through the gaps. A solid overlay
    # would hide the very agreement the figure exists to demonstrate.
    for i, h in enumerate(randoms):
        rx, ry = hist_to_xy(h, normalise)
        ax.plot(rx, ry, color=random_color, lw=1.3, alpha=0.9, zorder=5,
                linestyle=(0, (4, 3)),
                label=random_label if i == 0 else None)

    ax.set_xlabel("Recipe size, $s$  (number of ingredients in a recipe)")
    ax.set_ylabel("Fraction of recipes" if normalise else "Number of recipes")
    ax.set_title(title, fontsize=12)
    ax.set_xlim(0, min(max(ox) + 1, 42))
    ax.grid(axis="y", zorder=0)
    ax.legend(frameon=False, fontsize=9.5)
    ax.text(0.985, 0.60, sub, transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color=MUTED,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fcfcfb", ec="#e6e6e2"))
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path.name}")


def plot_freq_rank(original, freq_sets, uniform_sets, path):
    fig, ax = plt.subplots(figsize=(8.6, 5.4))

    def pos(a):
        a = np.asarray(a, dtype=float)
        a = a[a > 0]
        return np.arange(1, len(a) + 1), a

    for i, f in enumerate(uniform_sets):
        rx, ry = pos(f)
        ax.plot(rx, ry, color=AQUA, lw=1.0, alpha=0.65, zorder=2,
                label="Q2 control — size-controlled only (uniform draw), 10 sets"
                if i == 0 else None)
    for i, f in enumerate(freq_sets):
        rx, ry = pos(f)
        ax.plot(rx, ry, color=ORANGE, lw=1.0, alpha=0.75, zorder=3,
                label="Q3 control — size + ingredient-frequency controlled, 10 sets"
                if i == 0 else None)
    ox, oy = pos(original)
    ax.plot(ox, oy, color=BLUE, lw=2.4, zorder=5, label="Original cuisine")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Rank of ingredient, $r$  (1 = most frequently used)   [log scale]")
    ax.set_ylabel("Frequency  (number of recipes containing it)   [log scale]")
    ax.set_title("Q3(b)  Ingredient frequency–rank distribution: original cuisine "
                 "vs randomised controls", fontsize=12)
    ax.grid(which="both", zorder=0)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.text(0.985, 0.97,
            "Preserving ingredient frequency reproduces the\n"
            "observed rank curve; controlling size alone does not.",
            transform=ax.transAxes, ha="right", va="top", fontsize=9.5, color=INK,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fcfcfb", ec="#e6e6e2"))
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path.name}")


def main() -> int:
    d = json.loads(DATA.read_text())
    orig_hist = d["original"]["size_hist"]
    n = d["n_recipes"]

    print("[plots] Q2")
    plot_size(
        orig_hist, d["q2a"]["size_hists"], Q2 / "Q2a_recipe_size_distribution.png",
        "Q2(a)  Recipe-size distribution — original cuisine vs 10 size-controlled "
        "random cuisines",
        f"Size-controlled by replica:\neach random recipe copies the size\n"
        f"of one real recipe.\n\nN = {n:,} recipes per set\n"
        f"{d['n_sets']} independent random sets\nmean size = "
        f"{d['original']['mean_size']:.3f}",
        "Random cuisines (10 sets, uniform ingredient draw)")

    plot_size(
        orig_hist, [d["q2b"]["size_hist"]], Q2 / "Q2b_recipe_size_distribution.png",
        "Q2(b)  Recipe-size distribution — original cuisine vs inverse-transform "
        "random cuisine",
        f"Sizes drawn by inverse transform\nfrom the empirical CDF.\n\n"
        f"original N = {n:,}\ngenerated N = {d['q2b']['n_recipes']:,}  "
        f"({d['inverse_multiplier']}×)\nmean {d['original']['mean_size']:.3f} → "
        f"{d['q2b']['mean_size']:.3f}",
        f"Inverse-transform cuisine ({d['q2b']['n_recipes']:,} recipes)",
        normalise=True)

    print("[plots] Q3")
    plot_size(
        orig_hist, d["q3"]["size_hists"], Q3 / "Q3a_recipe_size_distribution.png",
        "Q3(a)  Recipe-size distribution — original cuisine vs 10 size- and "
        "frequency-controlled random cuisines",
        f"Size-controlled by replica;\ningredients drawn with probability\n"
        f"proportional to their frequency.\n\nN = {n:,} recipes per set\n"
        f"{d['n_sets']} independent random sets",
        "Random cuisines (10 sets, frequency-weighted draw)")

    plot_freq_rank(d["original"]["freq_rank"], d["q3"]["freq_ranks"],
                   d["q2a"]["freq_ranks"], Q3 / "Q3b_frequency_rank_distribution.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
