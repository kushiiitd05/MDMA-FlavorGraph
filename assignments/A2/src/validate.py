r"""
Validation gate for Assignment 2.

Checks every claim the submission makes. Exit code 1 if any hard check FAILs.
"""
from __future__ import annotations
import csv
import json
import pathlib
import sys
import collections

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from corpus import load_baskets, corpus_stats, A1_TABLE  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS: list[tuple[str, str, str]] = []


def check(name: str, ok, detail: str = "") -> None:
    RESULTS.append(("PASS" if ok else "FAIL", name, detail))


def main() -> int:
    baskets, names, index = load_baskets()
    st = corpus_stats(baskets)
    n = st["n_recipes"]

    # ---------------------------------------------------------- corpus
    check("C1  Assignment-1 source table present", A1_TABLE.exists(), str(A1_TABLE))
    check("C2  corpus has >= 10,000 recipes", n >= 10000, f"{n:,} recipes")
    check("C3  membership is binary (no repeated ingredient in a recipe)",
          all(len(b) == len(set(b)) for b in baskets),
          f"{st['n_memberships']:,} memberships")
    check("C4  ingredient vocabulary non-trivial", st["n_unique_ingredients"] > 1000,
          f"{st['n_unique_ingredients']:,} unique ingredients")

    # ---------------------------------------------------------- Q1
    q1 = json.loads((ROOT / "outputs/Q1/Q1_summary.json").read_text())
    ver = q1["apriori_vs_bruteforce"]
    check("C5  Apriori output == independent brute-force enumeration",
          all(v["identical_sets"] and v["identical_support_counts"] for v in ver.values()),
          ", ".join(f"{k}: {v['apriori_itemsets']:,}" for k, v in ver.items()))
    comp = q1["complete_itemset_counts_support_ge_1"]
    check("C6  complete size-1 list == vocabulary size",
          comp["size_1"] == st["n_unique_ingredients"], f"{comp['size_1']:,}")

    # independently recount the 1-itemsets from the A1 table
    c1 = collections.Counter(i for b in baskets for i in b)
    row1 = list(csv.DictReader((ROOT / "outputs/Q1/Q1a_itemsets_size1.csv").open()))
    check("C7  size-1 supports reproducible from the A1 table",
          all(int(r["support_count"]) == c1[r["item_1"]] for r in row1),
          f"{len(row1):,} rows checked")
    check("C8  support_fraction == support_count / N",
          all(abs(float(r["support_fraction"]) - int(r["support_count"]) / n) < 1e-6
              for r in row1))

    # monotonicity: a 2-itemset can never out-support its own items
    pairs = list(csv.DictReader((ROOT / "outputs/Q1/Q1a_itemsets_size2.csv").open()))
    bad = [p for p in pairs[:20000]
           if int(p["support_count"]) > min(c1[p["item_1"]], c1[p["item_2"]])]
    check("C9  downward closure holds: support(pair) <= support(each item)",
          not bad, f"{len(pairs):,} pairs, first 20k checked")

    top = json.loads((ROOT / "outputs/Q1/Q1b_top20_itemsets.json").read_text())
    check("C10 top-20 lists present for sizes 1, 2 and 3",
          all(len(top[f"size_{k}"]) == 20 for k in (1, 2, 3)))
    check("C11 top-20 sorted by descending support",
          all(all(top[f"size_{k}"][i]["support_count"] >= top[f"size_{k}"][i + 1]["support_count"]
                  for i in range(19)) for k in (1, 2, 3)))

    rules = list(csv.DictReader((ROOT / "outputs/Q1/Q1c_association_rules.csv").open()))
    check("C12 every confidence lies in (0, 1]",
          all(0 < float(r["confidence"]) <= 1 for r in rules), f"{len(rules)} rules")
    check("C13 confidence == support(X u Y) / support(X)",
          all(abs(float(r["confidence"]) - float(r["support_XuY"]) / float(r["support_X"]))
              < 1e-3 for r in rules))

    # ---------------------------------------------------------- Q2 / Q3
    d = json.loads((ROOT / "data/random_controls.json").read_text())
    orig = {int(k): v for k, v in d["original"]["size_hist"].items()}

    def same_hist(h):
        return {int(k): v for k, v in h.items()} == orig

    check("C14 Q2(a) all 10 random cuisines reproduce the size distribution exactly",
          all(same_hist(h) for h in d["q2a"]["size_hists"]),
          f"{len(d['q2a']['size_hists'])} sets, size-controlled by replica")
    check("C15 Q3 all 10 random cuisines reproduce the size distribution exactly",
          all(same_hist(h) for h in d["q3"]["size_hists"]),
          f"{len(d['q3']['size_hists'])} sets")

    q2b = {int(k): v for k, v in d["q2b"]["size_hist"].items()}
    check("C16 Q2(b) generated 10x the original recipe count",
          sum(q2b.values()) == 10 * n, f"{sum(q2b.values()):,} vs {10*n:,}")
    dmean = abs(d["q2b"]["mean_size"] - d["original"]["mean_size"])
    check("C17 Q2(b) mean recipe size matches the original (within 0.05)",
          dmean < 0.05,
          f"{d['original']['mean_size']:.4f} -> {d['q2b']['mean_size']:.4f} "
          f"(|diff| = {dmean:.4f})")

    sizes = sorted(set(orig) | set(q2b))
    po = np.array([orig.get(s, 0) for s in sizes], float); po /= po.sum()
    pg = np.array([q2b.get(s, 0) for s in sizes], float); pg /= pg.sum()
    tvd = 0.5 * np.abs(po - pg).sum()
    check("C18 Q2(b) size distribution close to original (total variation < 0.01)",
          tvd < 0.01, f"total variation distance = {tvd:.5f}")

    # frequency-rank agreement
    fo = np.array(d["original"]["freq_rank"], float)
    k = 200

    def mre(fr):
        f = np.array(fr, float)
        m = fo[:k] > 0
        return float(np.mean(np.abs(f[:k][m] - fo[:k][m]) / fo[:k][m]))

    e_freq = float(np.mean([mre(f) for f in d["q3"]["freq_ranks"]]))
    e_unif = float(np.mean([mre(f) for f in d["q2a"]["freq_ranks"]]))
    check("C19 Q3(b) frequency-controlled control reproduces the rank curve (<10% error)",
          e_freq < 0.10, f"mean relative error over top {k} ranks = {e_freq:.3%}")
    check("C20 Q3(b) size-only control does NOT reproduce it (the contrast)",
          e_unif > 5 * e_freq,
          f"size-only error {e_unif:.1%} vs frequency-controlled {e_freq:.1%}")

    # ---------------------------------------------------------- files
    required = [
        "outputs/Q1/Q1a_itemsets_size1.csv",
        "outputs/Q1/Q1a_itemsets_size2.csv",
        "outputs/Q1/Q1a_itemsets_size3.csv.gz",
        "outputs/Q1/Q1b_top20_itemsets.csv",
        "outputs/Q1/Q1c_support_confidence.md",
        "outputs/Q1/Q1c_association_rules.csv",
        "outputs/Q2/Q2a_recipe_size_distribution.png",
        "outputs/Q2/Q2b_recipe_size_distribution.png",
        "outputs/Q3/Q3a_recipe_size_distribution.png",
        "outputs/Q3/Q3b_frequency_rank_distribution.png",
        "README_SUBMISSION.md",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    check("C21 every required question-numbered file exists", not missing,
          f"missing: {missing}" if missing else f"{len(required)} files")
    bk = ROOT / "backup"
    check("C22 backup exists", bk.exists() and any(bk.iterdir()),
          f"{len(list(bk.glob('*')))} items" if bk.exists() else "none")

    # ---------------------------------------------------------- report
    print("\n" + "=" * 92)
    print("ASSIGNMENT 2 VALIDATION REPORT")
    print("=" * 92)
    for s, nme, det in RESULTS:
        print(f"[{s}] {nme:<64s} {det}")
    c = collections.Counter(s for s, _, _ in RESULTS)
    print("-" * 92)
    print(f"PASS {c['PASS']}   FAIL {c['FAIL']}   (total {len(RESULTS)})")
    (ROOT / "outputs/VALIDATION_REPORT.json").write_text(json.dumps(
        {"summary": dict(c),
         "checks": [{"status": s, "check": nm, "detail": d} for s, nm, d in RESULTS]},
        indent=2))
    return 1 if c["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
