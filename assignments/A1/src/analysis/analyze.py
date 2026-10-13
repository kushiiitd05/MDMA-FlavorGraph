r"""
Q2 and Q3 - corpus analysis and the required figures.

Frozen definitions (docs/DECISION_LOG.md, D6):
    f_i   = #{R : i in R}                  ingredient RECIPE frequency
    s_R   = |unique canonical ingredients in R|
    mu_s  = (1/N) sum_R s_R                computed over ALL recipes directly
    F(s)  = P(S <= s)                      CDF   (the Q2(c) deliverable)
    Fbar  = P(S >= s)                      CCDF  (supplementary, labelled as such)
    rank  : competition ranking ("1224") - tied frequencies share the minimum rank
"""
from __future__ import annotations
import csv, json, sys, pathlib, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
Q1, Q2, Q3 = ROOT / "outputs/Q1", ROOT / "outputs/Q2", ROOT / "outputs/Q3"
EXT = ROOT / "outputs/extensions"
for d in (Q1, Q2, Q3, EXT):
    d.mkdir(parents=True, exist_ok=True)

# validated categorical slots (see dataviz reference palette)
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


def load():
    rows = [json.loads(l) for l in (ROOT / "data/processed/recipes_processed.jsonl").open(encoding="utf-8")]
    return rows


# --------------------------------------------------------------------- Q2(a)
def q2a(recipes) -> tuple[dict, list]:
    recipe_freq = collections.Counter()
    mention_freq = collections.Counter()
    for r in recipes:
        for ing in set(r["ingredients_canonical"]):
            recipe_freq[ing] += 1
        for m in r["mentions"]:
            mention_freq[m["ingredient_canonical"]] += 1

    N = len(recipes)
    # competition ranking: sort by (-freq, name); tied freqs share the minimum rank
    items = sorted(recipe_freq.items(), key=lambda kv: (-kv[1], kv[0]))
    ranks, prev_f, prev_r = [], None, 0
    for i, (ing, f) in enumerate(items, start=1):
        r_ = prev_r if f == prev_f else i
        ranks.append(r_); prev_f, prev_r = f, r_

    out = Q2 / "Q2a_unique_ingredients_frequency.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "ingredient_name", "recipe_frequency",
                    "fraction_of_recipes", "mention_frequency"])
        for (ing, f), rk in zip(items, ranks):
            w.writerow([rk, ing, f, round(f / N, 6), mention_freq[ing]])
    print(f"[Q2a] unique canonical ingredients: {len(recipe_freq)}   -> {out}")

    summary = {
        "n_recipes": N,
        "n_unique_canonical_ingredients": len(recipe_freq),
        "n_total_mentions": int(sum(mention_freq.values())),
        "frequency_definition": "f_i = number of distinct recipes containing ingredient i",
        "top_20": [{"rank": rk, "ingredient": ing, "recipe_frequency": f,
                    "fraction_of_recipes": round(f / N, 4)}
                   for (ing, f), rk in list(zip(items, ranks))[:20]],
    }
    return summary, list(zip(items, ranks))


# --------------------------------------------------------------------- Q2(b)
def q2b(recipes) -> dict:
    sizes = np.array([len(set(r["ingredients_canonical"])) for r in recipes])
    sizes = sizes[sizes > 0]
    N = len(sizes)
    mu, sd = float(sizes.mean()), float(sizes.std(ddof=0))
    med = float(np.median(sizes))
    from scipy import stats as st
    skew, kurt = float(st.skew(sizes)), float(st.kurtosis(sizes))

    cnt = collections.Counter(int(s) for s in sizes)
    xs = sorted(cnt)
    ys = [cnt[x] for x in xs]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(xs, ys, width=0.82, color=BLUE, edgecolor="white", linewidth=0.6, zorder=3)
    ax.axvline(mu, color=ORANGE, lw=2, zorder=4)
    ax.annotate(f"mean recipe size  $\\bar{{s}}$ = {mu:.2f}",
                xy=(mu, max(ys) * 0.94), xytext=(8, 0), textcoords="offset points",
                color=ORANGE, fontweight="bold", va="top")
    ax.set_xlabel("Recipe size, $s$  (number of unique ingredients in a recipe)")
    ax.set_ylabel("Number of recipes")
    ax.set_title(f"Q2(b)  Recipe-size distribution — BBC Good Food corpus (N = {N:,} recipes)")
    ax.grid(axis="y", zorder=0)
    ax.set_xlim(0, min(max(xs) + 1, 45))
    ax.text(0.985, 0.72,
            f"N = {N:,}\nmean = {mu:.2f}\nmedian = {med:.0f}\nSD = {sd:.2f}\n"
            f"min = {sizes.min()}   max = {sizes.max()}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color=MUTED,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fcfcfb", ec="#e6e6e2"))
    fig.savefig(Q2 / "Q2b_recipe_size_distribution.png")
    plt.close(fig)

    with (Q2 / "Q2b_recipe_size_frequency_map.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["recipe_size", "recipe_count", "fraction_of_recipes"])
        for x in xs:
            w.writerow([x, cnt[x], round(cnt[x] / N, 6)])

    stats = {
        "n_recipes": int(N),
        "definition_recipe_size": "number of unique canonical ingredients in the recipe",
        "mean_recipe_size": round(mu, 4), "std_dev": round(sd, 4),
        "median": med, "min": int(sizes.min()), "max": int(sizes.max()),
        "q1": float(np.percentile(sizes, 25)), "q3": float(np.percentile(sizes, 75)),
        "p05": float(np.percentile(sizes, 5)), "p95": float(np.percentile(sizes, 95)),
        "skewness": round(skew, 4), "excess_kurtosis": round(kurt, 4),
        "note": ("Distribution is right-skewed, NOT assumed Gaussian; "
                 "skewness/kurtosis reported so the reader can judge."),
    }
    (Q2 / "Q2b_average_recipe_size.json").write_text(json.dumps(stats, indent=2))
    print(f"[Q2b] mean={mu:.3f} sd={sd:.3f} median={med} N={N}  skew={skew:.2f}")
    return {"sizes": sizes, **stats}


# --------------------------------------------------------------------- Q2(c)
def q2c(sizes) -> None:
    N = len(sizes)
    xs = np.arange(sizes.min(), sizes.max() + 1)
    cdf = np.array([(sizes <= x).sum() / N for x in xs])
    ccdf = np.array([(sizes >= x).sum() / N for x in xs])

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.step(xs, cdf, where="post", color=BLUE, lw=2, zorder=3)
    ax.fill_between(xs, cdf, step="post", color=BLUE, alpha=0.12, zorder=2)
    for q, lab, ha, dx in ((0.5, "median", "right", -8), (0.9, "90th pct", "left", 8)):
        x_ = xs[np.searchsorted(cdf, q)]
        ax.plot([x_, x_], [0, q], color=ORANGE, lw=1.2, ls="--", zorder=4)
        ax.plot([xs[0], x_], [q, q], color=ORANGE, lw=1.2, ls="--", zorder=4)
        ax.annotate(f"{lab}: s = {x_}", (x_, q), xytext=(dx, -14), ha=ha,
                    textcoords="offset points", fontsize=9, color=ORANGE)
    ax.set_xlabel("Recipe size, $s$  (number of unique ingredients)")
    ax.set_ylabel("Cumulative fraction of recipes,  $F(s) = P(S \\leq s)$")
    ax.set_title(f"Q2(c)  Cumulative distribution (CDF) of recipe size  (N = {N:,})")
    ax.set_ylim(0, 1.02); ax.set_xlim(0, min(sizes.max() + 1, 45))
    ax.grid(zorder=0)
    fig.savefig(Q2 / "Q2c_recipe_size_cumulative_distribution.png")
    plt.close(fig)

    # supplementary CCDF - explicitly labelled, never confused with the CDF
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.step(xs, ccdf, where="post", color=AQUA, lw=2, zorder=3)
    ax.set_xlabel("Recipe size, $s$  (number of unique ingredients)")
    ax.set_ylabel("$\\bar{F}(s) = P(S \\geq s)$")
    ax.set_title(f"Supplementary  Complementary CDF (CCDF) of recipe size  (N = {N:,})")
    ax.set_ylim(0, 1.02); ax.grid(zorder=0)
    fig.savefig(EXT / "recipe_size_ccdf_supplementary.png")
    plt.close(fig)

    with (Q2 / "Q2c_recipe_size_cdf.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["recipe_size", "count_at_size", "cdf_P_S_le_s", "ccdf_P_S_ge_s"])
        c = collections.Counter(int(s) for s in sizes)
        for x, a, b in zip(xs, cdf, ccdf):
            w.writerow([int(x), c.get(int(x), 0), round(float(a), 6), round(float(b), 6)])
    print(f"[Q2c] CDF written (monotone={bool(np.all(np.diff(cdf) >= -1e-12))}, ends at {cdf[-1]:.4f})")


# --------------------------------------------------------------------- Q3
def q3(freq_ranked, n_recipes: int) -> None:
    freqs = np.array([f for (_, f), _ in freq_ranked])
    ranks = np.array([r for _, r in freq_ranked])
    ordinal = np.arange(1, len(freqs) + 1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    ax.plot(ordinal, freqs, color=BLUE, lw=1.8, zorder=3)
    ax.set_xlabel("Rank of ingredient (1 = most frequent)")
    ax.set_ylabel("Recipe frequency, $f_i$")
    ax.set_title("Linear axes")
    ax.grid(zorder=0)

    ax = axes[1]
    ax.plot(ordinal, freqs, color=BLUE, lw=1.8, zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Rank of ingredient, $r$  (log scale)")
    ax.set_ylabel("Recipe frequency, $f_i$  (log scale)")
    ax.set_title("Logarithmic axes (log–log)")
    ax.grid(which="both", zorder=0)
    # stagger label offsets so the top ranks do not collide
    # label a few widely-separated ranks so annotations cannot collide
    for i, (dx, dy) in zip((0, 4, 29, 199, 1499),
                           ((4, 9), (4, -14), (4, 9), (4, -14), (4, 9))):
        if i < len(freqs):
            ax.annotate(freq_ranked[i][0][0], (ordinal[i], freqs[i]), xytext=(dx, dy),
                        textcoords="offset points", fontsize=8, color=MUTED)

    fig.suptitle(f"Q3(a)  Ingredient frequency–rank distribution — "
                 f"{len(freqs):,} unique canonical ingredients across "
                 f"N = {n_recipes:,} recipes",
                 fontsize=12, color=INK, y=1.02)
    fig.savefig(Q3 / "Q3a_frequency_rank_distribution.png")
    plt.close(fig)

    with (Q3 / "Q3a_frequency_rank.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["display_order", "frequency_rank_competition", "ingredient_name",
                    "recipe_frequency"])
        for o, ((ing, f), rk) in zip(ordinal, freq_ranked):
            w.writerow([int(o), int(rk), ing, int(f)])
    print(f"[Q3] frequency-rank written ({len(freqs)} ingredients, "
          f"non-increasing={bool(np.all(np.diff(freqs) <= 0))})")


def main() -> int:
    recipes = load()
    print(f"[analysis] recipes loaded: {len(recipes)}")
    summary, freq_ranked = q2a(recipes)
    st = q2b(recipes)
    q2c(st["sizes"])
    q3(freq_ranked, len(recipes))
    summary["recipe_size"] = {k: v for k, v in st.items() if k != "sizes"}
    (ROOT / "outputs/Q2/Q2_summary.json").write_text(json.dumps(summary, indent=2))
    print("[analysis] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
