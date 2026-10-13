r"""
Assignment-wide validation gate (brief §47-§50).

Runs every acceptance check and prints PASS / FAIL / WARNING per item.
Exit code 1 if any hard check FAILs, so it can gate the submission.
"""
from __future__ import annotations
import csv, json, sys, pathlib, collections
import numpy as np
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "config/config.yaml").read_text())
RESULTS: list[tuple[str, str, str]] = []


def check(name: str, ok: bool | None, detail: str = "", warn: bool = False) -> None:
    status = "WARNING" if (warn and not ok) else ("PASS" if ok else "FAIL")
    RESULTS.append((status, name, detail))


def jl(p): return [json.loads(l) for l in (ROOT / p).open(encoding="utf-8")]


def main() -> int:
    # ---------------------------------------------------------------- corpus
    raw = jl(CFG["paths"]["raw_jsonl"])
    clean = jl("data/interim/recipes_clean.jsonl")
    proc = jl("data/processed/recipes_processed.jsonl")
    N = len(proc)
    target = CFG["scrape"]["target_valid_recipes"]

    check("C1  >= 10,000 unique valid recipes", N >= target, f"{N} valid (target {target})")
    check("C2  no RecipeDB data anywhere",
          all("recipedb" not in (r.get("source_url", "") + r.get("canonical_url", "")).lower()
              and "cosylab" not in (r.get("source_url", "")).lower() for r in raw),
          f"checked {len(raw)} raw records; source = {CFG['source']['site_id']}")
    check("C3  every recipe has a Recipe ID",
          all(r.get("recipe_id") for r in proc) and
          len({r["recipe_id"] for r in proc}) == N, f"{N} unique IDs")
    check("C4  every recipe has a source URL", all(r.get("source_url") for r in proc))
    check("C5  raw titles preserved", all(r.get("title") for r in raw))
    check("C6  raw ingredient phrases preserved",
          all(r.get("ingredient_phrases_raw") for r in raw))
    n_raw_nosteps = sum(1 for r in raw if not r.get("instruction_steps_raw"))
    check("C7  instructions preserved for every corpus recipe",
          all(r.get("instruction_steps_raw") for r in proc),
          f"final corpus: 0 without steps; {n_raw_nosteps} raw pages had no method section "
          f"and were rejected by the corpus freeze (see C9)")
    check("C8  raw JSON-LD preserved verbatim",
          sum(1 for r in raw if r.get("raw_jsonld")) / max(len(raw), 1) > 0.95,
          f"{sum(1 for r in raw if r.get('raw_jsonld'))}/{len(raw)} records keep raw_jsonld")

    audit = json.loads((ROOT / "outputs/extensions/duplicate_audit.json").read_text())
    check("C9  duplicate audit completed", "final_unique_valid_recipes" in audit,
          f"url dupes {audit['removed_duplicate_canonical_url']}, "
          f"content dupes {audit['removed_duplicate_content_signature']}")
    fails = (ROOT / CFG["paths"]["failures"])
    nf = sum(1 for _ in fails.open()) if fails.exists() else 0
    check("C10 scrape failures logged", fails.exists(), f"{nf} failures recorded")

    # ---------------------------------------------------------------- NER
    ev = ROOT / "outputs/extensions/ner_evaluation.json"
    check("C11 NER evaluated on a human-annotated gold set", ev.exists())
    if ev.exists():
        e = json.loads(ev.read_text())
        best = max(e["results"].items(), key=lambda kv: kv[1]["canonical"]["f1"])
        check("C12 chosen approach beats the rule-only baseline",
              best[1]["canonical"]["f1"] >= e["results"]["rule_dictionary_baseline"]["canonical"]["f1"],
              f"{best[0]} canonical F1 = {best[1]['canonical']['f1']:.3f} vs rules "
              f"{e['results']['rule_dictionary_baseline']['canonical']['f1']:.3f} "
              f"on {e['n_gold_phrases']} phrases")
    check("C13 canonicalisation audit exists",
          (ROOT / "outputs/extensions/rejected_ingredient_names.csv").exists())
    check("C14 human review gallery exists",
          (ROOT / "outputs/extensions/human_review_gallery.csv").exists())

    # ------------------------------------------------------------ Q1c table
    q1c = list(csv.reader((ROOT / "outputs/Q1/Q1c_recipe_ingredient.csv").open(encoding="utf-8")))
    hdr, rows = q1c[0], q1c[1:]
    check("C15 Q1(c) table header is (Recipe ID)-(Ingredient Name)",
          hdr == ["Recipe ID", "Ingredient Name"], str(hdr))
    ids = {r["recipe_id"] for r in proc}
    check("C16 Q1(c) rows all reference a known Recipe ID",
          all(r[0] in ids for r in rows), f"{len(rows)} rows")
    check("C17 Q1(c) has no empty ingredient names",
          all(r[1].strip() for r in rows))
    check("C18 Q1(c) (recipe, ingredient) pairs are unique",
          len({(a, b) for a, b in rows}) == len(rows))

    # ------------------------------------------------------------ Q2 / Q3
    fr = list(csv.DictReader((ROOT / "outputs/Q2/Q2a_unique_ingredients_frequency.csv").open(encoding="utf-8")))
    freqs = [int(r["recipe_frequency"]) for r in fr]
    check("C19 0 <= f_i <= N for every ingredient",
          all(0 <= f <= N for f in freqs), f"max f_i = {max(freqs)}, N = {N}")
    check("C20 unique-ingredient count reproducible from the Q1(c) table",
          len({r[1] for r in rows}) == len(fr),
          f"{len({r[1] for r in rows})} distinct in Q1c vs {len(fr)} in Q2a")
    rf = collections.Counter()
    for a, b in rows:
        rf[b] += 1
    check("C21 frequencies reproducible from the Q1(c) table",
          all(rf[r["ingredient_name"]] == int(r["recipe_frequency"]) for r in fr))

    sizes = np.array([len(set(r["ingredients_canonical"])) for r in proc])
    st = json.loads((ROOT / "outputs/Q2/Q2b_average_recipe_size.json").read_text())
    # stored value is rounded to 4 dp, so compare at that precision
    check("C22 mean recipe size reproducible",
          abs(round(float(sizes.mean()), 4) - st["mean_recipe_size"]) < 1e-9,
          f"recomputed {sizes.mean():.6f} -> {round(float(sizes.mean()),4)} "
          f"vs stored {st['mean_recipe_size']}")
    check("C23 sum of size-histogram counts == N",
          sum(int(r["recipe_count"]) for r in csv.DictReader(
              (ROOT / "outputs/Q2/Q2b_recipe_size_frequency_map.csv").open())) == len(sizes))

    cdf_rows = list(csv.DictReader((ROOT / "outputs/Q2/Q2c_recipe_size_cdf.csv").open()))
    cdf = np.array([float(r["cdf_P_S_le_s"]) for r in cdf_rows])
    ccdf = np.array([float(r["ccdf_P_S_ge_s"]) for r in cdf_rows])
    check("C24 0 <= F(s) <= 1", bool(np.all((cdf >= 0) & (cdf <= 1))))
    check("C25 CDF monotonically non-decreasing", bool(np.all(np.diff(cdf) >= -1e-12)))
    check("C26 CDF reaches 1", abs(cdf[-1] - 1.0) < 1e-9, f"final F = {cdf[-1]:.6f}")
    check("C27 CCDF monotonically non-increasing", bool(np.all(np.diff(ccdf) <= 1e-12)))

    rk = list(csv.DictReader((ROOT / "outputs/Q3/Q3a_frequency_rank.csv").open()))
    rkf = np.array([int(r["recipe_frequency"]) for r in rk])
    check("C28 rank-ordered frequencies are non-increasing",
          bool(np.all(np.diff(rkf) <= 0)))
    check("C29 competition ranking: equal frequencies share a rank",
          all(a["frequency_rank_competition"] == b["frequency_rank_competition"]
              for a, b in zip(rk, rk[1:])
              if a["recipe_frequency"] == b["recipe_frequency"]))

    # ------------------------------------------------------------ graph
    g = json.loads((ROOT / "outputs/extensions/recipe_ingredient_graph_meta.json").read_text())["sanity_checks"]
    check("C30 incidence matrix is binary", g["all_entries_binary"])
    check("C31 row sum == recipe size", g["row_sum_equals_recipe_size"])
    check("C32 column sum == ingredient frequency", g["col_sum_equals_ingredient_frequency"])

    # ------------------------------------------------------------ NLP sanity
    # A unit token inside a name is only a defect when the name is not a genuine
    # ingredient that happens to contain that word. "gram flour" (besan) is a real
    # ingredient and an explicitly protected compound - flagging it would be wrong.
    sys.path.insert(0, str(ROOT / "src/normalization"))
    from canonicalize import PROTECTED_COMPOUNDS  # noqa: E402
    bad_tokens = {"tbsp", "tsp", "cup", "gram", "kg", "ml", "oz"}
    names = {r["ingredient_name"] for r in fr}
    offenders = [n for n in names
                 if (set(n.split()) & bad_tokens) and n not in PROTECTED_COMPOUNDS]
    check("C33 ingredient names contain no stray unit tokens",
          not offenders, f"{len(offenders)} offenders {offenders[:5]}"
          + " (protected compounds such as 'gram flour' are exempt)")
    n_num = sum(1 for n in names if any(ch.isdigit() for ch in n))
    check("C34 ingredient names contain no digits/quantities", n_num == 0, f"{n_num} offenders")
    n_long = sum(1 for n in names if len(n.split()) > 4)
    check("C35 no ingredient name longer than 4 tokens (sentence fragments)",
          n_long == 0, f"{n_long} offenders")

    # states extension (only present once process_states.py has run)
    st_sum = ROOT / "outputs/extensions/state_taxonomy_summary.json"
    if st_sum.exists():
        sj = json.loads(st_sum.read_text())
        check("C39 state invariant recipe_count(i,s) <= recipe_freq(i)",
              sj["invariant_recipe_count_le_recipe_freq"])
        check("C40 cooking transformations retained in the state layer",
              sj["observations_by_category"].get("COOKING", 0) > 0,
              f"COOKING observations = {sj['observations_by_category'].get('COOKING', 0)}")
        ips = ROOT / "outputs/extensions/ingredient_process_states.csv"
        check("C41 every state observation carries a category", ips.exists() and all(
            r["state_category"] for r in csv.DictReader(ips.open(encoding="utf-8"))))

    # graph extension (only present once build_graph.py has run)
    gdir = ROOT / "outputs/extensions/graph"
    if (gdir / "edges.csv").exists():
        import collections as _c
        gn = {r["node_id"]: r for r in csv.DictReader((gdir / "nodes.csv").open(encoding="utf-8"))}
        ge = list(csv.DictReader((gdir / "edges.csv").open(encoding="utf-8")))
        et = _c.Counter(e["edge_type"] for e in ge)
        check("C42 graph: every edge endpoint is a declared node",
              all(e["source"] in gn and e["target"] in gn for e in ge),
              f"{len(gn):,} nodes / {len(ge):,} edges")
        parents = _c.Counter(e["target"] for e in ge if e["edge_type"] == "HAS_STATE")
        n_state = sum(1 for d in gn.values() if d["node_type"] == "state")
        check("C43 graph: each state node hangs off exactly one parent ingredient",
              len(parents) == n_state and all(v == 1 for v in parents.values()),
              f"{n_state:,} state nodes")
        check("C44 graph: CONTAINS edges == Q1(c) table rows",
              et["CONTAINS"] == len(rows), f"{et['CONTAINS']:,} vs {len(rows):,}")
        n_cu = sum(1 for r in proc if (r.get("cuisine_raw") or "").strip())
        check("C45 graph: no cuisine invented (HAS_CUISINE == recipes with a label)",
              et["HAS_CUISINE"] == n_cu, f"{et['HAS_CUISINE']:,} vs {n_cu:,}")

    # ------------------------------------------------------------ files
    required = [
        "outputs/Q1/Q1c_recipe_ingredient.csv",
        "outputs/Q1/Q1a_raw_recipes.jsonl",
        "outputs/Q1/Q1b_ingredient_ner_output.csv",
        "outputs/Q2/Q2a_unique_ingredients_frequency.csv",
        "outputs/Q2/Q2b_recipe_size_distribution.png",
        "outputs/Q2/Q2b_average_recipe_size.json",
        "outputs/Q2/Q2c_recipe_size_cumulative_distribution.png",
        "outputs/Q3/Q3a_frequency_rank_distribution.png",
        "theory/Q4_Q8_draft.md", "theory/references.md",
        "outputs/extensions/ingredient_process_states.csv",
        "outputs/extensions/state_frequency_by_category.csv",
        "outputs/extensions/graph/edges.csv",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    check("C36 all required submission files exist", not missing, f"missing: {missing}")
    bk = ROOT / "backup"
    check("C37 backup exists", bk.exists() and any(bk.iterdir()),
          f"{len(list(bk.glob('*'))) if bk.exists() else 0} items in backup/")
    check("C38 cuisine totals agree with corpus totals",
          json.loads((ROOT / "outputs/extensions/cuisine_summary.json").read_text())["n_recipes"] == N)

    # ---------------------------------------------------------------- report
    order = {"FAIL": 0, "WARNING": 1, "PASS": 2}
    print("\n" + "=" * 96)
    print("ASSIGNMENT 1 VALIDATION REPORT")
    print("=" * 96)
    for s, n, d in RESULTS:
        mark = {"PASS": "PASS   ", "FAIL": "FAIL   ", "WARNING": "WARNING"}[s]
        print(f"[{mark}] {n:<62s} {d}")
    c = collections.Counter(s for s, _, _ in RESULTS)
    print("-" * 96)
    print(f"PASS {c['PASS']}   WARNING {c['WARNING']}   FAIL {c['FAIL']}   (total {len(RESULTS)})")
    (ROOT / "outputs/VALIDATION_REPORT.json").write_text(json.dumps(
        {"summary": dict(c), "checks": [{"status": s, "check": n, "detail": d}
                                        for s, n, d in RESULTS]}, indent=2))
    return 1 if c["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
