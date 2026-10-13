r"""
Q1 — Frequent Item Set Mining (FISM) on the Assignment-1 recipe corpus.

The question says "implement any of the frequent item set mining algorithms", so
**Apriori is implemented here from scratch** - no mining library is used. The
implementation is the classical level-wise algorithm:

    L1  = frequent 1-itemsets (single scan)
    repeat for k = 2, 3, ...
        Ck  = candidate generation          F(k-1) x F(k-1) join on the shared
                                            (k-2)-prefix of sorted itemsets
        Ck  = downward-closure pruning       drop any candidate having an
                                            infrequent (k-1)-subset
        count Ck against the baskets
        Lk  = { c in Ck : support(c) >= min_support }

Correctness is not assumed: `exhaustive_counts()` independently enumerates every
itemset of size 1-3 that occurs at least once, by brute force, and
`verify_apriori()` asserts that Apriori's output is exactly the exhaustive
counts filtered at the same threshold.

Outputs
    Q1a  complete lists of item sets of size 1, 2 and 3
    Q1b  top-20 item sets of each size
    Q1c  support & confidence - definitions plus worked rules from this corpus
"""
from __future__ import annotations
import csv
import gzip
import itertools
import json
import pathlib
import sys
import time
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from corpus import load_baskets, corpus_stats  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "Q1"
OUT.mkdir(parents=True, exist_ok=True)

# Threshold for the demonstrated Apriori run. 0.1% of the corpus = 12 recipes.
# The COMPLETE lists required by Q1(a) are emitted separately at support >= 1,
# so this threshold only governs the mined/pruned result used to exercise the
# algorithm and to show its level-wise behaviour.
MIN_SUPPORT_FRACTION = 0.001


# --------------------------------------------------------------------- Apriori
def apriori(baskets: list[frozenset[int]], min_support: int, max_len: int = 3,
            log=print) -> tuple[dict[int, dict[tuple[int, ...], int]], list[dict]]:
    """
    Classical Apriori. `baskets` are frozensets of integer item ids.
    Returns ({k: {itemset_tuple: support_count}}, per-level statistics).
    """
    levels: dict[int, dict[tuple[int, ...], int]] = {}
    stats: list[dict] = []

    # ---- L1: one pass over the data
    t0 = time.time()
    c1: collections.Counter = collections.Counter()
    for b in baskets:
        c1.update(b)
    L1 = {(i,): s for i, s in c1.items() if s >= min_support}
    levels[1] = dict(sorted(L1.items(), key=lambda kv: (-kv[1], kv[0])))
    stats.append({"k": 1, "candidates": len(c1), "frequent": len(L1),
                  "seconds": round(time.time() - t0, 2)})
    log(f"  [apriori] k=1  candidates={len(c1):,}  frequent={len(L1):,}")

    # ---- L2, L3, ...
    for k in range(2, max_len + 1):
        prev = sorted(levels[k - 1])
        if not prev:
            break
        t0 = time.time()

        # candidate generation: join two (k-1)-itemsets sharing their first k-2 items
        candidates: set[tuple[int, ...]] = set()
        n_prev = len(prev)
        for a in range(n_prev):
            pa = prev[a]
            head = pa[:-1]
            for b in range(a + 1, n_prev):
                pb = prev[b]
                if pb[:-1] != head:
                    break                      # sorted: no further match shares the prefix
                candidates.add(pa + (pb[-1],))
        n_generated = len(candidates)

        # downward-closure pruning: every (k-1)-subset must itself be frequent
        prev_set = levels[k - 1].keys()
        candidates = {
            c for c in candidates
            if all(sub in prev_set for sub in itertools.combinations(c, k - 1))
        }
        n_pruned = n_generated - len(candidates)

        # counting pass
        counts: collections.Counter = collections.Counter()
        for bs in baskets:
            if len(bs) < k:
                continue
            for combo in itertools.combinations(sorted(bs), k):
                if combo in candidates:
                    counts[combo] += 1

        Lk = {c: s for c, s in counts.items() if s >= min_support}
        levels[k] = dict(sorted(Lk.items(), key=lambda kv: (-kv[1], kv[0])))
        stats.append({"k": k, "candidates_generated": n_generated,
                      "pruned_by_downward_closure": n_pruned,
                      "candidates_counted": len(candidates),
                      "frequent": len(Lk), "seconds": round(time.time() - t0, 2)})
        log(f"  [apriori] k={k}  generated={n_generated:,}  pruned={n_pruned:,}  "
            f"counted={len(candidates):,}  frequent={len(Lk):,}")
    return levels, stats


# ----------------------------------------------------------------- brute force
def exhaustive_counts(baskets: list[frozenset[int]], max_len: int = 3
                      ) -> dict[int, collections.Counter]:
    """Every item set of size 1..max_len occurring at least once. Independent of Apriori."""
    out = {k: collections.Counter() for k in range(1, max_len + 1)}
    for b in baskets:
        sb = sorted(b)
        for k in range(1, max_len + 1):
            if len(sb) >= k:
                out[k].update(itertools.combinations(sb, k))
    return out


def verify_apriori(levels, exhaustive, min_support: int) -> dict:
    """Assert Apriori == exhaustive counts filtered at the same threshold."""
    report = {}
    for k, mined in levels.items():
        truth = {s: c for s, c in exhaustive[k].items() if c >= min_support}
        same_keys = set(mined) == set(truth)
        same_counts = all(mined[s] == truth[s] for s in mined) if same_keys else False
        report[f"k={k}"] = {
            "apriori_itemsets": len(mined),
            "bruteforce_itemsets": len(truth),
            "identical_sets": same_keys,
            "identical_support_counts": same_counts,
        }
        if not (same_keys and same_counts):
            raise AssertionError(f"Apriori disagrees with brute force at k={k}")
    return report


# --------------------------------------------------------------------- writing
def write_itemsets(path: pathlib.Path, counter, names: list[str], k: int,
                   n_recipes: int, gz: bool = False) -> int:
    """Write an item-set table sorted by descending support then alphabetically."""
    rows = sorted(counter.items(), key=lambda kv: (-kv[1], tuple(names[i] for i in kv[0])))
    opener = (lambda p: gzip.open(p, "wt", newline="", encoding="utf-8")) if gz else \
             (lambda p: open(p, "w", newline="", encoding="utf-8"))
    with opener(path) as fh:
        w = csv.writer(fh)
        w.writerow([f"item_{i+1}" for i in range(k)] +
                   ["itemset", "size", "support_count", "support_fraction"])
        for combo, cnt in rows:
            items = [names[i] for i in combo]
            w.writerow(items + [" | ".join(items), k, cnt, round(cnt / n_recipes, 8)])
    return len(rows)


def main() -> int:
    print("[Q1] loading Assignment-1 corpus")
    baskets_names, names, index = load_baskets()
    st = corpus_stats(baskets_names)
    n = st["n_recipes"]
    print(f"      recipes={n:,}  ingredients={st['n_unique_ingredients']:,}  "
          f"mean size={st['mean_recipe_size']:.4f}")

    baskets = [frozenset(index[i] for i in b) for b in baskets_names]
    min_support = max(1, round(MIN_SUPPORT_FRACTION * n))
    print(f"[Q1] Apriori min_support = {MIN_SUPPORT_FRACTION:.3%} of {n:,} "
          f"= {min_support} recipes")

    # ---------------- Apriori (the implemented FISM algorithm)
    levels, apriori_stats = apriori(baskets, min_support, max_len=3)

    # ---------------- independent brute-force enumeration (complete lists)
    print("[Q1] exhaustive enumeration of all item sets of size 1-3 (support >= 1)")
    t0 = time.time()
    exh = exhaustive_counts(baskets, max_len=3)
    print(f"      sizes: 1 -> {len(exh[1]):,}   2 -> {len(exh[2]):,}   "
          f"3 -> {len(exh[3]):,}   [{time.time()-t0:.1f}s]")

    # ---------------- correctness check
    check = verify_apriori(levels, exh, min_support)
    print("[Q1] Apriori verified against brute force:",
          all(v["identical_sets"] and v["identical_support_counts"] for v in check.values()))

    # ---------------- Q1(a) complete lists
    n1 = write_itemsets(OUT / "Q1a_itemsets_size1.csv", exh[1], names, 1, n)
    n2 = write_itemsets(OUT / "Q1a_itemsets_size2.csv", exh[2], names, 2, n)
    n3 = write_itemsets(OUT / "Q1a_itemsets_size3.csv.gz", exh[3], names, 3, n, gz=True)
    print(f"[Q1a] complete lists written: size1={n1:,}  size2={n2:,}  size3={n3:,} (gzipped)")

    # the mined (frequent) sets at the stated threshold, as plain CSVs
    for k in (1, 2, 3):
        write_itemsets(OUT / f"Q1a_apriori_frequent_size{k}.csv",
                       collections.Counter(levels.get(k, {})), names, k, n)

    # ---------------- Q1(b) top 20 of each size
    top_payload = {}
    with (OUT / "Q1b_top20_itemsets.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["size", "rank", "itemset", "support_count", "support_fraction"])
        for k in (1, 2, 3):
            rows = sorted(exh[k].items(),
                          key=lambda kv: (-kv[1], tuple(names[i] for i in kv[0])))[:20]
            top_payload[f"size_{k}"] = []
            for r, (combo, cnt) in enumerate(rows, 1):
                label = " | ".join(names[i] for i in combo)
                w.writerow([k, r, label, cnt, round(cnt / n, 6)])
                top_payload[f"size_{k}"].append(
                    {"rank": r, "itemset": label, "support_count": cnt,
                     "support_fraction": round(cnt / n, 6)})
    (OUT / "Q1b_top20_itemsets.json").write_text(json.dumps(top_payload, indent=2))
    print("[Q1b] top-20 tables written")

    # ---------------- Q1(c) support & confidence, with rules from this corpus
    def sup(items: tuple[int, ...]) -> int:
        return exh[len(items)][tuple(sorted(items))]

    rules = []
    for pair, pair_sup in sorted(exh[2].items(), key=lambda kv: -kv[1])[:40]:
        a, b = pair
        for ante, cons in ((a, b), (b, a)):
            rules.append({
                "rule": f"{names[ante]} -> {names[cons]}",
                "support_count_XuY": pair_sup,
                "support_XuY": round(pair_sup / n, 6),
                "support_X": round(sup((ante,)) / n, 6),
                "support_Y": round(sup((cons,)) / n, 6),
                "confidence": round(pair_sup / sup((ante,)), 4),
                "lift": round((pair_sup / n) / ((sup((ante,)) / n) * (sup((cons,)) / n)), 3),
            })
    rules.sort(key=lambda r: -r["confidence"])
    with (OUT / "Q1c_association_rules.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rules[0].keys()))
        w.writeheader()
        w.writerows(rules)
    print(f"[Q1c] {len(rules)} association rules written (top-40 pairs, both directions)")

    # ---------------- summary
    summary = {
        "corpus": st,
        "membership_convention": "binary (a recipe is a SET of distinct ingredients)",
        "algorithm_implemented": "Apriori (level-wise, from scratch - no mining library)",
        "min_support_fraction": MIN_SUPPORT_FRACTION,
        "min_support_count": min_support,
        "apriori_levels": apriori_stats,
        "apriori_frequent_counts": {f"size_{k}": len(v) for k, v in levels.items()},
        "complete_itemset_counts_support_ge_1": {
            "size_1": len(exh[1]), "size_2": len(exh[2]), "size_3": len(exh[3])},
        "itemsets_by_threshold": {
            f"support_ge_{t}": {f"size_{k}": sum(1 for v in exh[k].values() if v >= t)
                                for k in (1, 2, 3)}
            for t in (1, 2, 5, 10, 12, 20, 50, 100)},
        "apriori_vs_bruteforce": check,
        "top_rule_by_confidence": rules[0],
    }
    (OUT / "Q1_summary.json").write_text(json.dumps(summary, indent=2))
    print("[Q1] summary written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
