r"""
RESEARCH EXTENSIONS (kept strictly separate from the required Q1-Q3 deliverables).

  E3  recipe-ingredient bipartite incidence matrix A (sparse CSR) + identity checks
  E4  cuisine-stratified analysis, reported only where N_c is adequate
  E5  human review gallery (random + deliberately hard cases)

Every count here is derived from OBSERVED text. No state, cuisine or ingredient is
invented; where the source has no label the value stays 'unavailable'.
"""
from __future__ import annotations
import csv, json, sys, pathlib, collections, random
import numpy as np
from scipy import sparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXT = ROOT / "outputs/extensions"; EXT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight", "font.size": 10,
    "axes.edgecolor": "#c9c9c4", "axes.linewidth": 0.8, "axes.titlecolor": INK,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e6e6e2", "grid.linewidth": 0.7,
    "figure.facecolor": "white", "axes.facecolor": "white"})

MIN_CUISINE_N = 30   # below this, cuisine statistics are unstable and are NOT plotted


def load():
    return [json.loads(l) for l in
            (ROOT / "data/processed/recipes_processed.jsonl").open(encoding="utf-8")]


# ------------------------------------------------------------------ E3 graph
def bipartite(recipes):
    ings = sorted({i for r in recipes for i in r["ingredients_canonical"]})
    idx = {g: k for k, g in enumerate(ings)}
    rid = [r["recipe_id"] for r in recipes]
    rows, cols = [], []
    for i, r in enumerate(recipes):
        for g in set(r["ingredients_canonical"]):
            rows.append(i); cols.append(idx[g])
    A = sparse.csr_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)),
                          shape=(len(recipes), len(ings)))
    row_sum = np.asarray(A.sum(1)).ravel()
    col_sum = np.asarray(A.sum(0)).ravel()
    sizes = np.array([len(set(r["ingredients_canonical"])) for r in recipes])
    freq = collections.Counter(i for r in recipes for i in set(r["ingredients_canonical"]))
    checks = {
        "shape_recipes_x_ingredients": list(A.shape),
        "all_entries_binary": bool(set(np.unique(A.data).tolist()) <= {1}),
        "row_sum_equals_recipe_size": bool(np.array_equal(row_sum, sizes)),
        "col_sum_equals_ingredient_frequency":
            bool(np.array_equal(col_sum, np.array([freq[g] for g in ings]))),
        "density": float(A.nnz / (A.shape[0] * A.shape[1])),
        "nnz_edges": int(A.nnz),
    }
    sparse.save_npz(EXT / "recipe_ingredient_incidence.npz", A.tocsr())
    (EXT / "recipe_ingredient_graph_meta.json").write_text(json.dumps(
        {"recipe_ids_order": rid[:5] + ["..."], "n_recipes": len(rid),
         "n_ingredients": len(ings), "sanity_checks": checks}, indent=2))
    (EXT / "graph_ingredient_index.csv").write_text(
        "column_index,ingredient\n" + "\n".join(f"{k},{g}" for g, k in idx.items()))
    print(f"[E3] incidence matrix {A.shape}, nnz={A.nnz}, checks={checks['row_sum_equals_recipe_size']}"
          f"/{checks['col_sum_equals_ingredient_frequency']}/{checks['all_entries_binary']}")
    return checks


# ------------------------------------------------------------------ E4 cuisine
def cuisine(recipes):
    lab = collections.Counter()
    by = collections.defaultdict(list)
    for r in recipes:
        c = (r.get("cuisine_raw") or "").strip()
        if not c:
            lab["unavailable"] += 1
            continue
        lab[c] += 1
        by[c].append(len(set(r["ingredients_canonical"])))

    N = len(recipes)
    labelled = N - lab["unavailable"]
    rows = []
    for c, sz in sorted(by.items(), key=lambda kv: -len(kv[1])):
        a = np.array(sz)
        rows.append({"cuisine_raw": c, "N_c": len(a),
                     "mean_recipe_size": round(float(a.mean()), 3),
                     "sd_recipe_size": round(float(a.std(ddof=0)), 3),
                     "median": float(np.median(a)), "min": int(a.min()), "max": int(a.max()),
                     "statistically_adequate_N": len(a) >= MIN_CUISINE_N})
    with (EXT / "cuisine_recipe_size_stats.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # top ingredients per adequately-sampled cuisine
    top_rows = []
    for c in [r["cuisine_raw"] for r in rows if r["statistically_adequate_N"]]:
        cnt = collections.Counter()
        n_c = 0
        for r in recipes:
            if (r.get("cuisine_raw") or "").strip() == c:
                n_c += 1
                for g in set(r["ingredients_canonical"]):
                    cnt[g] += 1
        for rank, (g, n) in enumerate(cnt.most_common(15), 1):
            top_rows.append({"cuisine_raw": c, "N_c": n_c, "rank": rank,
                             "ingredient": g, "recipe_frequency": n,
                             "fraction_of_cuisine_recipes": round(n / n_c, 4)})
    if top_rows:
        with (EXT / "cuisine_top_ingredients.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(top_rows[0].keys())); w.writeheader(); w.writerows(top_rows)

    ok = [r for r in rows if r["statistically_adequate_N"]][:10]
    if ok:
        fig, ax = plt.subplots(figsize=(9, 4.8))
        names = [r["cuisine_raw"] for r in ok][::-1]
        means = [r["mean_recipe_size"] for r in ok][::-1]
        sds = [r["sd_recipe_size"] for r in ok][::-1]
        ns = [r["N_c"] for r in ok][::-1]
        ax.barh(names, means, xerr=sds, color=BLUE, height=0.66,
                error_kw=dict(ecolor=MUTED, lw=1, capsize=3))
        for i, (m, sd, n) in enumerate(zip(means, sds, ns)):
            ax.text(m + sd + 0.35, i, f"N={n}", va="center", fontsize=8, color=MUTED)
        ax.set_xlim(0, max(m + sd for m, sd in zip(means, sds)) + 2.4)
        gm = float(np.mean([len(set(r["ingredients_canonical"])) for r in recipes]))
        ax.axvline(gm, color=ORANGE, lw=1.6, ls="--")
        ax.text(gm, len(names) - 0.4, f" corpus mean = {gm:.2f}", color=ORANGE, fontsize=9)
        ax.set_xlabel("Mean recipe size (unique canonical ingredients)  ±1 SD")
        ax.set_title(f"Extension E4 — recipe size by cuisine "
                     f"(only cuisines with N ≥ {MIN_CUISINE_N})", fontsize=11)
        ax.grid(axis="x", zorder=0)
        fig.savefig(EXT / "cuisine_recipe_size.png"); plt.close(fig)

    summary = {
        "n_recipes": N,
        "n_with_cuisine_label": labelled,
        "cuisine_label_coverage": round(labelled / N, 4),
        "n_distinct_cuisine_labels": len(by),
        "min_N_for_reporting": MIN_CUISINE_N,
        "n_cuisines_meeting_min_N": sum(1 for r in rows if r["statistically_adequate_N"]),
        "note": ("cuisine_raw is preserved exactly as BBC Good Food supplies it; no cuisine "
                 "label was inferred or fabricated. Recipes without a label are counted as "
                 "'unavailable' and excluded from cuisine statistics, never imputed."),
        "WARNING": ("The global corpus mean is computed from ALL recipes directly, NOT by "
                    "averaging cuisine means."),
    }
    (EXT / "cuisine_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[E4] cuisine coverage {labelled}/{N} = {100*labelled/N:.1f}%, "
          f"{summary['n_cuisines_meeting_min_N']} cuisines with N>={MIN_CUISINE_N}")
    return summary


# ------------------------------------------------------------------ E5 gallery
def gallery(recipes, n=90):
    rng = random.Random(20260908)
    ms = [m for r in recipes for m in r["mentions"]]
    pick = rng.sample(ms, min(60, len(ms)))
    hard = [m for m in ms if len(m["raw_phrase"]) > 80 or "(" in m["raw_phrase"]
            or " or " in m["raw_phrase"]]
    pick += rng.sample(hard, min(30, len(hard)))
    with (EXT / "human_review_gallery.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["raw_phrase", "ingredient_surface", "ingredient_normalized",
                    "ingredient_canonical", "ingredient_family", "quantity_raw",
                    "unit_raw", "processing_state", "extraction_method",
                    "agrees_with_rule_baseline", "normalization_provenance",
                    "REVIEWER_VERDICT_ok_or_error"])
        for m in pick:
            w.writerow([m["raw_phrase"], m["ingredient_surface"], m["ingredient_normalized"],
                        m["ingredient_canonical"], m["ingredient_family"], m["quantity_raw"],
                        m["unit_raw"], m["processing_state"], m["extraction_method"],
                        m["agrees_with_rule_baseline"], m["normalization_provenance"], ""])
    print(f"[E5] review gallery: {len(pick)} rows")


def main() -> int:
    recipes = load()
    print(f"[ext] recipes: {len(recipes)}")
    # NOTE: the ingredient/process-state analysis (formerly E1/E2 here) now lives in
    # src/analysis/process_states.py, which uses the observed-state taxonomy instead
    # of the PREP_WORDS filter that wrongly discarded cooking transformations.
    checks = bipartite(recipes)
    cu = cuisine(recipes)
    gallery(recipes)
    (EXT / "extensions_summary.json").write_text(json.dumps(
        {"graph_sanity_checks": checks, "cuisine": cu}, indent=2))
    print("[ext] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
