r"""
EXTENSION — heterogeneous connection graph:  Cuisine — Recipe — Ingredient — State.

This is research-extension work. The required Q1(c)/Q2/Q3 outputs do NOT depend on
it, and the plain binary recipe-ingredient incidence matrix used for the rubric
sanity checks still lives in src/analysis/extensions.py.

NODE TYPES
  cuisine:<name>              a recipeCuisine label, exactly as the source gave it
  recipe:<recipe_id>          one scraped recipe
  ingredient:<canonical>      a canonical ingredient  (the Q1c/Q2/Q3 vocabulary)
  state:<canonical>::<state>  an observed processed form, e.g. onion::finely chopped

EDGE TYPES
  recipe   -HAS_CUISINE->  cuisine       (only where the source states one)
  recipe   -CONTAINS->     ingredient    (primary alternatives only, as Q1c does)
  ingredient -HAS_STATE->  state         **the state is a SUB-PART of its ingredient**
  recipe   -USES_STATE->   state         which processed form that recipe used

The ingredient -> state edge is what makes a processed form a child of its parent
ingredient rather than a competing top-level node: `onion::fried` hangs off `onion`,
so the canonical vocabulary stays intact and the states refine it.

Nothing here is inferred. A recipe with no cuisine label simply has no HAS_CUISINE
edge; it is never assigned one.
"""
from __future__ import annotations
import csv, gzip, json, sys, pathlib, collections
import networkx as nx

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/extensions/graph"; OUT.mkdir(parents=True, exist_ok=True)


def load():
    recipes = [json.loads(l) for l in
               (ROOT / "data/processed/recipes_processed.jsonl").open(encoding="utf-8")]
    states = list(csv.DictReader(
        (ROOT / "outputs/extensions/ingredient_process_states.csv").open(encoding="utf-8")))
    return recipes, states


def main() -> int:
    recipes, state_rows = load()
    print(f"[graph] recipes={len(recipes):,} state observations={len(state_rows):,}")

    G = nx.DiGraph()
    ing_recipes = collections.defaultdict(set)
    cui_recipes = collections.defaultdict(set)

    for r in recipes:
        rid = f"recipe:{r['recipe_id']}"
        G.add_node(rid, node_type="recipe", label=r["title"][:80])
        cu = (r.get("cuisine_raw") or "").strip()
        if cu:                                    # never invented when absent
            cn = f"cuisine:{cu}"
            G.add_node(cn, node_type="cuisine", label=cu)
            G.add_edge(rid, cn, edge_type="HAS_CUISINE", weight=1)
            cui_recipes[cu].add(r["recipe_id"])
        for ing in r["ingredients_canonical"]:
            inn = f"ingredient:{ing}"
            if inn not in G:
                G.add_node(inn, node_type="ingredient", label=ing)
            G.add_edge(rid, inn, edge_type="CONTAINS", weight=1)
            ing_recipes[ing].add(r["recipe_id"])

    # ingredient -> state (state is a CHILD of its ingredient), and recipe -> state
    kept = {"PREPARATION", "COOKING", "QUALITY", "SIZE"}
    st_recipes = collections.defaultdict(set)
    for s in state_rows:
        if s["state_category"] not in kept:
            continue
        ing, st = s["canonical_ingredient"], s["state_text"]
        inn, stn = f"ingredient:{ing}", f"state:{ing}::{st}"
        if inn not in G:
            G.add_node(inn, node_type="ingredient", label=ing)
        if stn not in G:
            G.add_node(stn, node_type="state", label=f"{ing}::{st}",
                       parent_ingredient=ing, state_text=st,
                       state_category=s["state_category"])
            G.add_edge(inn, stn, edge_type="HAS_STATE", weight=0)
        G[inn][stn]["weight"] += 1
        rid = f"recipe:{s['recipe_id']}"
        if rid in G:
            G.add_edge(rid, stn, edge_type="USES_STATE", weight=1)
        st_recipes[(ing, st)].add(s["recipe_id"])

    types = collections.Counter(d["node_type"] for _, d in G.nodes(data=True))
    etypes = collections.Counter(d["edge_type"] for _, _, d in G.edges(data=True))
    print(f"[graph] nodes {G.number_of_nodes():,}  {dict(types)}")
    print(f"[graph] edges {G.number_of_edges():,}  {dict(etypes)}")

    # ------------------------------------------------------------ exports
    with (OUT / "nodes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["node_id", "node_type", "label", "parent_ingredient",
                    "state_text", "state_category"])
        for n, d in G.nodes(data=True):
            w.writerow([n, d.get("node_type"), d.get("label", ""),
                        d.get("parent_ingredient", ""), d.get("state_text", ""),
                        d.get("state_category", "")])
    with (OUT / "edges.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["source", "target", "edge_type", "weight"])
        for a, b, d in G.edges(data=True):
            w.writerow([a, b, d["edge_type"], d.get("weight", 1)])

    # GraphML (Gephi / Cytoscape), gzipped - the full graph is large
    with gzip.open(OUT / "cgas_graph.graphml.gz", "wb") as f:
        nx.write_graphml(G, f)
    print(f"[graph] wrote nodes.csv, edges.csv, cgas_graph.graphml.gz")

    # ------------------------------------------- cuisine x ingredient projection
    # "lift" = P(ingredient | cuisine) / P(ingredient) - how CHARACTERISTIC an
    # ingredient is of a cuisine, rather than merely how common it is overall.
    N = len(recipes)
    rows = []
    MIN_C = 30
    for cu, rset in cui_recipes.items():
        if len(rset) < MIN_C:
            continue
        cnt = collections.Counter()
        for r in recipes:
            if (r.get("cuisine_raw") or "").strip() == cu:
                for ing in set(r["ingredients_canonical"]):
                    cnt[ing] += 1
        for ing, c in cnt.items():
            if c < 5:
                continue
            p_ic = c / len(rset)
            p_i = len(ing_recipes[ing]) / N
            rows.append({"cuisine": cu, "n_cuisine_recipes": len(rset),
                         "ingredient": ing, "recipes_with_ingredient": c,
                         "p_ingredient_given_cuisine": round(p_ic, 4),
                         "p_ingredient_overall": round(p_i, 4),
                         "lift": round(p_ic / p_i, 3) if p_i else None})
    rows.sort(key=lambda r: (r["cuisine"], -r["lift"]))
    with (OUT / "cuisine_ingredient_projection.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"[graph] cuisine x ingredient projection: {len(rows):,} rows "
          f"({len({r['cuisine'] for r in rows})} cuisines with N>={MIN_C})")

    (OUT / "graph_summary.json").write_text(json.dumps({
        "node_counts": dict(types), "edge_counts": dict(etypes),
        "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges(),
        "edge_semantics": {
            "HAS_CUISINE": "recipe -> cuisine, only where the source states one",
            "CONTAINS": "recipe -> canonical ingredient (primary alternatives only)",
            "HAS_STATE": "ingredient -> its processed form; the state is a SUB-PART "
                         "of the ingredient, never a competing top-level node",
            "USES_STATE": "recipe -> the processed form it used",
        },
        "note": "Extension only. Q1(c)/Q2/Q3 do not depend on this graph.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
