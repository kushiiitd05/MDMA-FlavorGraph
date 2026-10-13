r"""
Reproducible construction of the 206-phrase NER gold set.

This code originally ran inline in a shell session and was not committed, so the
gold set could not be regenerated. It is reproduced here exactly.

IMPORTANT PROVENANCE NOTE
-------------------------
The gold set was drawn WHILE the crawl was still running, from the first
`SOURCE_RECORDS` (= 1502) records of `data/raw/recipes_raw.jsonl`. That snapshot size
was recovered by matching the 8 stratum pool sizes recorded in the original run log
(paren=1090, long=108, comma_multi=164, range=195, frac=545, no_qty=1457, or_alt=967,
compound=1504) - all eight match exactly at N=1502, and the rebuild then reproduces
the committed candidate file byte-for-byte (`--check`). Re-running the
same seed over the finished 11,983-record corpus would select a *different* sample.
To reproduce the committed gold set byte-for-byte the script therefore replays the
original snapshot size. `--full-corpus` draws a fresh sample from the whole corpus
instead (useful for an independent second evaluation, NOT for reproducing this one).

Design of the sample (see docs/DECISION_LOG.md):
    150 phrases drawn uniformly at random from the deduplicated set of unique
        ingredient phrases  -> an unbiased estimate of everyday performance
  +  56 phrases drawn 7 each from 8 difficulty strata
        -> stress-tests the known failure modes rather than hiding them
  = 206 phrases  (150 + 56; the de-duplication step removed no overlaps)

Annotation lives in `data/interim/gold_annotations.tsv` (id <TAB> name[|name...]),
produced by hand. This script only rebuilds the *candidates*; it never invents labels.
"""
from __future__ import annotations
import argparse, json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEED = 20260908
SOURCE_RECORDS = 1502          # corpus snapshot the committed gold set came from
N_RANDOM = 150
PER_STRATUM = 7


def strata(uniq: list[str]) -> dict[str, list[str]]:
    """The 8 difficulty strata, in the exact order used originally (order matters:
    the RNG is consumed stratum by stratum)."""
    return {
        "paren":       [p for p in uniq if "(" in p],
        "long":        [p for p in uniq if len(p) > 90],
        "comma_multi": [p for p in uniq if p.count(",") >= 2],
        "range":       [p for p in uniq if re.search(r"\d+\s*-\s*\d+", p)],
        "frac":        [p for p in uniq if any(c in p for c in "½¼¾⅓⅔")],
        "no_qty":      [p for p in uniq if not re.match(r"^\s*[\d½¼¾⅓⅔]", p)],
        "or_alt":      [p for p in uniq if re.search(r"\bor\b", p)],
        "compound":    [p for p in uniq if re.search(
            r"\b(milk|vinegar|sauce|oil|cream|powder|butter)\b", p)],
    }


def build(n_records: int | None) -> list[str]:
    rows = [json.loads(l) for l in (ROOT / "data/raw/recipes_raw.jsonl").open(encoding="utf-8")]
    if n_records is not None:
        rows = rows[:n_records]
    phrases = [p.strip() for r in rows for p in r["ingredient_phrases_raw"] if p.strip()]
    uniq = sorted(set(phrases))
    print(f"[gold] source records: {len(rows)}   phrases: {len(phrases)}   unique: {len(uniq)}")

    rng = random.Random(SEED)
    rand = rng.sample(uniq, N_RANDOM)
    hard: list[str] = []
    for name, pool in strata(uniq).items():
        take = rng.sample(pool, min(PER_STRATUM, len(pool)))
        hard += take
        print(f"  {name:12s} pool={len(pool):5d} take={len(take)}")
    sel = list(dict.fromkeys(rand + hard))       # order-preserving de-duplication
    print(f"[gold] {N_RANDOM} random + {len(hard)} hard -> {len(sel)} unique candidates")
    return sel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full-corpus", action="store_true",
                    help="sample from the whole corpus instead of the original snapshot")
    ap.add_argument("--out", default="data/interim/gold_candidates.jsonl")
    ap.add_argument("--check", action="store_true",
                    help="verify the rebuild matches the committed file, write nothing")
    a = ap.parse_args()

    sel = build(None if a.full_corpus else SOURCE_RECORDS)
    lines = [json.dumps({"id": i, "text": p}, ensure_ascii=False) for i, p in enumerate(sel)]

    target = ROOT / a.out
    if a.check:
        if not target.exists():
            print("[gold] CHECK FAIL: committed file missing"); return 1
        # compare CONTENT, not byte serialisation: the committed file was written
        # with default json.dumps (ensure_ascii=True), so "purée" is escaped there
        # and literal here. Identical data, different encoding of the same data.
        old = [json.loads(x) for x in target.read_text(encoding="utf-8").splitlines() if x.strip()]
        new = [json.loads(x) for x in lines]
        same = old == new
        print(f"[gold] CHECK {'PASS - rebuild reproduces the committed gold set exactly'
                              if same else 'FAIL'}  ({len(old)} committed, {len(new)} rebuilt)")
        return 0 if same else 1

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[gold] wrote {target}")

    # merge with the hand annotations to rebuild gold_eval.jsonl
    ann = ROOT / "data/interim/gold_annotations.tsv"
    if ann.exists():
        gold = {}
        for line in ann.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            i, names = line.rstrip("\n").split("\t")
            gold[int(i)] = [n.strip() for n in names.split("|") if n.strip()]
        missing = [i for i in range(len(sel)) if i not in gold]
        if missing:
            print(f"[gold] WARNING: {len(missing)} candidates have no annotation: {missing[:10]}")
        out = ROOT / "data/interim/gold_eval.jsonl"
        out.write_text("\n".join(
            json.dumps({"id": i, "text": p, "gold_names": gold.get(i, [])},
                       ensure_ascii=False) for i, p in enumerate(sel)) + "\n",
            encoding="utf-8")
        print(f"[gold] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
