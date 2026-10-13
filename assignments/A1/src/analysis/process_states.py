r"""
EXTENSION — canonical ingredient + observed preparation/cooking state.

This replaces the first version of the state analysis, which filtered states with
`PREP_WORDS` (a list written for stripping words off the edges of a NAME span).
That filter discarded 15 of 17 cooking transformations - `fried`, `boiled`,
`caramelised`, `grilled`, `baked`, `smoked` (865 mentions) - while keeping SIZE words
such as `large` (3,782 mentions) as if they were process states.

WHAT THIS PRODUCES
------------------
  ingredient_process_states.csv    one row per (mention, observed state)
  state_frequency_by_category.csv  per (ingredient, state): mention AND recipe counts
  ingredient_state_map.json        canonical ingredient -> observed states, by category
  processed_ingredient_frequency_rank.csv    "onion::chopped" vocabulary + rank

DEFINITIONS (deliberately explicit - these are different quantities)
--------------------------------------------------------------------
  mention_count(i,s) = number of ingredient MENTIONS of i carrying state s
  recipe_count(i,s)  = number of DISTINCT RECIPES containing i in state s
  recipe_freq(i)     = number of distinct recipes containing i          (Q2a definition)

  Invariant we DO assert:      recipe_count(i,s) <= recipe_freq(i)   for every s
  Invariant we DO NOT assert:  sum_s recipe_count(i,s) == recipe_freq(i)
      - because one mention can legitimately carry several states
        ("large fresh chopped onions" -> SIZE + QUALITY + PREPARATION),
        so the state categories are neither mutually exclusive nor exhaustive.

The canonical ingredient is NEVER replaced by "ingredient::state". The processed
vocabulary is a SEPARATE derived layer; Q1(c)/Q2/Q3 continue to use the canonical
ingredient alone.
"""
from __future__ import annotations
import csv, json, sys, pathlib, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/normalization"))
from state_taxonomy import classify_state, STATE_CATEGORIES  # noqa: E402

EXT = ROOT / "outputs/extensions"; EXT.mkdir(parents=True, exist_ok=True)

# --- presentation caps (NOT statistical thresholds) ---------------------------
# These control how much is *displayed*, never what is computed. The complete
# per-ingredient map is always written to ingredient_state_map.json; the small
# preview file exists only because a 2,600-entry JSON is unreadable by hand.
PREVIEW_N = 25        # ingredients in the human-readable preview map
PLOT_PANELS = 6       # panels in the figure
PLOT_STATES = 8       # states shown per panel
MIN_STATES_FOR_PREVIEW = 3   # an ingredient needs >=3 distinct observed states to
                             # be worth previewing (otherwise the preview fills up
                             # with high-frequency ingredients that are never
                             # modified, e.g. vanilla extract with 1 state)
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
INK, MUTED = "#0b0b0b", "#52514e"
CAT_COLOR = {"PREPARATION": BLUE, "COOKING": ORANGE, "QUALITY": AQUA, "SIZE": VIOLET}
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight", "font.size": 10,
    "axes.edgecolor": "#c9c9c4", "axes.linewidth": 0.8, "axes.titlecolor": INK,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e6e6e2", "grid.linewidth": 0.7,
    "figure.facecolor": "white", "axes.facecolor": "white"})


def main() -> int:
    mentions = list(csv.DictReader(
        (ROOT / "data/processed/ingredient_mentions.csv").open(encoding="utf-8")))
    print(f"[states] mentions: {len(mentions):,}")

    recipe_freq = collections.Counter()
    for rid, ing in {(m["recipe_id"], m["ingredient_canonical"]) for m in mentions}:
        recipe_freq[ing] += 1

    rows = []
    mention_ct = collections.Counter()          # (ing, state) -> mentions
    recipe_set = collections.defaultdict(set)   # (ing, state) -> {recipe_id}
    cat_ct = collections.Counter()
    n_with_state = 0

    for m in mentions:
        ing = m["ingredient_canonical"]
        raw_states = [s.strip() for s in (m["processing_state"] or "").split("|") if s.strip()]
        if raw_states:
            n_with_state += 1
        for s in raw_states:
            cat, amb = classify_state(s)
            cat_ct[cat] += 1
            rows.append({
                "recipe_id": m["recipe_id"],
                "ingredient_index": m["ingredient_index"],
                "raw_phrase": m["raw_phrase"],
                "ingredient_surface": m["ingredient_surface"],
                "canonical_ingredient": ing,
                "state_text": s,                       # verbatim, never rewritten
                "state_category": cat,
                "category_is_ambiguous": amb,
                "extraction_method": m["extraction_method"],
            })
            if cat in STATE_CATEGORIES:
                mention_ct[(ing, s, cat)] += 1
                recipe_set[(ing, s, cat)].add(m["recipe_id"])

    with (EXT / "ingredient_process_states.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"[states] state observations: {len(rows):,} on {n_with_state:,} mentions "
          f"({100*n_with_state/len(mentions):.1f}% of mentions carry >=1 state)")
    print(f"[states] by category: {dict(cat_ct.most_common())}")

    # ---------------------------------------------------- frequency table
    freq_rows = []
    for (ing, s, cat), mc in mention_ct.items():
        rc = len(recipe_set[(ing, s, cat)])
        freq_rows.append({
            "canonical_ingredient": ing, "state_text": s, "state_category": cat,
            "mention_count": mc, "recipe_count": rc,
            "ingredient_recipe_frequency": recipe_freq[ing],
            "pct_of_ingredient_recipes": round(100 * rc / recipe_freq[ing], 2),
        })
    freq_rows.sort(key=lambda r: (-r["ingredient_recipe_frequency"],
                                  r["canonical_ingredient"], -r["recipe_count"]))
    with (EXT / "state_frequency_by_category.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(freq_rows[0].keys())); w.writeheader(); w.writerows(freq_rows)

    # invariant: recipe_count(i,s) <= recipe_freq(i)   (NOT a summation identity)
    viol = [r for r in freq_rows if r["recipe_count"] > r["ingredient_recipe_frequency"]]
    print(f"[states] invariant recipe_count(i,s) <= recipe_freq(i): "
          f"{'PASS' if not viol else f'FAIL ({len(viol)})'}")

    # ---------------------------------------------------- per-ingredient map
    # Build the map for EVERY ingredient that has at least one observed state.
    by_ing: dict[str, dict] = collections.defaultdict(
        lambda: collections.defaultdict(dict))
    for r in freq_rows:
        by_ing[r["canonical_ingredient"]][r["state_category"]][r["state_text"]] = \
            r["recipe_count"]

    def entry(ing: str) -> dict:
        byc = by_ing[ing]
        return {
            "canonical_ingredient": ing,
            "total_recipe_frequency": recipe_freq[ing],
            "n_distinct_observed_states": sum(len(v) for v in byc.values()),
            "states_by_category": {c: dict(sorted(byc[c].items(), key=lambda kv: -kv[1]))
                                   for c in STATE_CATEGORIES if byc.get(c)},
        }

    NOTE = ("counts are DISTINCT RECIPES containing that ingredient in that state; "
            "states are NOT mutually exclusive (one mention can carry SIZE + QUALITY "
            "+ PREPARATION at once), so they do not sum to total_recipe_frequency")

    full = sorted((entry(i) for i in by_ing),
                  key=lambda e: (-e["total_recipe_frequency"], e["canonical_ingredient"]))
    (EXT / "ingredient_state_map.json").write_text(json.dumps(
        {"note": NOTE, "n_ingredients_with_states": len(full),
         "ingredients": full}, indent=2))

    # Small hand-readable preview. Ranked by how much state information the
    # ingredient actually carries, not purely by how common the ingredient is -
    # the earlier version ranked by frequency alone and so kept
    # "vanilla extract" (1 state) while dropping "carrot" (145 states).
    prev = sorted((e for e in full
                   if e["n_distinct_observed_states"] >= MIN_STATES_FOR_PREVIEW),
                  key=lambda e: -e["n_distinct_observed_states"])[:PREVIEW_N]
    (EXT / "ingredient_state_map_preview.json").write_text(json.dumps(
        {"note": NOTE,
         "selection": f"top {PREVIEW_N} ingredients by number of distinct observed "
                      f"states (>= {MIN_STATES_FOR_PREVIEW}); this is a DISPLAY cap "
                      f"only - the full map is in ingredient_state_map.json",
         "ingredients": prev}, indent=2))
    print(f"[states] state map: {len(full):,} ingredients (full) / "
          f"{len(prev)} (preview)")

    # ---------------------------------------------------- processed vocabulary
    proc = collections.defaultdict(set)
    for (ing, s, cat), _ in mention_ct.items():
        proc[f"{ing}::{s}"] |= recipe_set[(ing, s, cat)]
    pf = sorted(((k, len(v)) for k, v in proc.items()), key=lambda kv: (-kv[1], kv[0]))
    with (EXT / "processed_ingredient_frequency_rank.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["rank", "processed_ingredient", "recipe_frequency"])
        for i, (k, n) in enumerate(pf, 1):
            w.writerow([i, k, n])
    print(f"[states] processed-ingredient entries: {len(pf):,}")

    # ---------------------------------------------------- figure
    show = [e["canonical_ingredient"] for e in
            sorted(full, key=lambda e: -e["total_recipe_frequency"])
            if e["n_distinct_observed_states"] >= MIN_STATES_FOR_PREVIEW][:PLOT_PANELS]
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    for ax, ing in zip(axes.ravel(), show):
        rs = sorted([r for r in freq_rows if r["canonical_ingredient"] == ing],
                    key=lambda r: -r["recipe_count"])[:PLOT_STATES][::-1]
        ax.barh([r["state_text"] for r in rs], [r["pct_of_ingredient_recipes"] for r in rs],
                color=[CAT_COLOR.get(r["state_category"], MUTED) for r in rs], height=0.68)
        ax.set_title(f"{ing}  (in {recipe_freq[ing]:,} recipes)", fontsize=10, color=INK)
        ax.set_xlabel("% of that ingredient's recipes", fontsize=9)
        ax.grid(axis="x", zorder=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=CAT_COLOR[c]) for c in STATE_CATEGORIES]
    fig.legend(handles, list(STATE_CATEGORIES), loc="lower center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Extension — observed states of the six most frequent ingredients, "
                 "coloured by category\n(states are not mutually exclusive, so they do "
                 "not sum to 100%)", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(EXT / "ingredient_process_state_distributions.png"); plt.close(fig)

    # frequency-rank of the PROCESSED vocabulary, alongside (never replacing) the
    # required canonical-ingredient rank plot in outputs/Q3
    import numpy as np
    pfr = np.array([n for _, n in pf])
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.plot(np.arange(1, len(pfr) + 1), pfr, color=AQUA, lw=1.8)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Rank of processed ingredient, $r$  (log scale)")
    ax.set_ylabel("Recipe frequency  (log scale)")
    ax.set_title("Extension — frequency–rank of PROCESSED ingredients "
                 f"(ingredient::state, {len(pfr):,} entries)", fontsize=11)
    ax.grid(which="both", zorder=0)
    for i in (0, 1, 4, 19):
        if i < len(pf):
            ax.annotate(pf[i][0], (i + 1, pfr[i]), xytext=(6, 4),
                        textcoords="offset points", fontsize=7.5, color=MUTED)
    fig.savefig(EXT / "processed_ingredient_frequency_rank.png"); plt.close(fig)

    (EXT / "state_taxonomy_summary.json").write_text(json.dumps({
        "state_observations": len(rows),
        "mentions_with_at_least_one_state": n_with_state,
        "fraction_of_mentions_with_state": round(n_with_state / len(mentions), 4),
        "observations_by_category": dict(cat_ct.most_common()),
        "distinct_state_strings": len({r["state_text"] for r in rows}),
        "distinct_states_kept_for_analysis": len({(r["state_text"]) for r in freq_rows}),
        "ingredients_with_at_least_one_state": len(by_ing),
        "categories_used_for_analysis": list(STATE_CATEGORIES),
        "invariant_recipe_count_le_recipe_freq": not viol,
        "note": ("NOT_A_STATE and UNCLASSIFIED observations are written to "
                 "ingredient_process_states.csv but excluded from the frequency "
                 "tables. Nothing is silently discarded."),
    }, indent=2))
    print("[states] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
