r"""
Corpus freeze: validate -> deduplicate -> assign stable Recipe IDs.

Duplicate policy (see docs/DECISION_LOG.md)
------------------------------------------
Three signals are checked, in this order:
  1. canonical_url          - exact duplicate page (same recipe served twice)
  2. content signature      - normalised title + sorted normalised ingredient
                              phrase multiset + step count
Recipes are NOT removed merely for sharing a title: BBC Good Food legitimately
has several distinct "Chocolate cake" recipes. A title collision is only treated
as a duplicate when the ingredient signature also matches.

Recipe IDs are deterministic: records are sorted by canonical_url and numbered
R000001..., so re-running on the same raw file always yields the same IDs.
"""
from __future__ import annotations
import json, re, sys, hashlib, pathlib, collections
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "config/config.yaml").read_text())


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (t or "").lower()).strip()


def sig(rec: dict) -> str:
    ings = sorted(re.sub(r"[^a-z0-9]", "", p.lower()) for p in rec["ingredient_phrases_raw"])
    key = norm_title(rec["title"]) + "|" + "|".join(ings) + f"|{rec['n_instruction_steps']}"
    return hashlib.sha1(key.encode()).hexdigest()


def valid(rec: dict) -> tuple[bool, str]:
    if not rec.get("title"):
        return False, "no_title"
    if not rec.get("source_url"):
        return False, "no_source_url"
    ings = rec.get("ingredient_phrases_raw") or []
    if len(ings) < 2:
        return False, "fewer_than_2_ingredient_phrases"
    if not rec.get("instruction_steps_raw"):
        return False, "no_instructions"
    for bad in CFG["source"]["forbidden_sources"]:          # hard guard: no RecipeDB
        if bad in (rec.get("source_url", "") + rec.get("source_site", "")).lower():
            return False, "forbidden_source"
    return True, "ok"


def main() -> int:
    raw = [json.loads(l) for l in (ROOT / CFG["paths"]["raw_jsonl"]).open(encoding="utf-8")]
    print(f"[corpus] raw records read: {len(raw)}")

    reasons = collections.Counter()
    kept = []
    for r in raw:
        ok, why = valid(r)
        reasons[why] += 1
        if ok:
            kept.append(r)
    print(f"[corpus] schema-valid: {len(kept)}   rejected: {dict(reasons)}")

    by_url, dup_url = {}, 0
    for r in kept:
        c = r["canonical_url"]
        if c in by_url:
            dup_url += 1
            continue
        by_url[c] = r
    print(f"[corpus] duplicate canonical_url removed: {dup_url}")

    by_sig, dup_sig, title_only = {}, 0, 0
    titles = collections.Counter(norm_title(r["title"]) for r in by_url.values())
    for r in sorted(by_url.values(), key=lambda x: x["canonical_url"]):
        s = sig(r)
        if s in by_sig:
            dup_sig += 1
            continue
        by_sig[s] = r
    final = sorted(by_sig.values(), key=lambda x: x["canonical_url"])
    title_only = sum(1 for t, n in titles.items() if n > 1)
    print(f"[corpus] duplicate content-signature removed: {dup_sig}")
    print(f"[corpus] distinct titles appearing >1x (KEPT - different recipes): {title_only}")

    for i, r in enumerate(final, 1):
        r["recipe_id"] = f"R{i:06d}"
        r["content_signature"] = sig(r)

    out = ROOT / "data/interim/recipes_clean.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    audit = {
        "raw_records": len(raw),
        "schema_valid": len(kept),
        "rejection_reasons": dict(reasons),
        "removed_duplicate_canonical_url": dup_url,
        "removed_duplicate_content_signature": dup_sig,
        "titles_shared_by_multiple_recipes_kept": title_only,
        "final_unique_valid_recipes": len(final),
        "target": CFG["scrape"]["target_valid_recipes"],
        "target_met": len(final) >= CFG["scrape"]["target_valid_recipes"],
    }
    (ROOT / "outputs/extensions/duplicate_audit.json").write_text(json.dumps(audit, indent=2))
    print(f"[corpus] FINAL unique valid recipes: {len(final)}  "
          f"(target {audit['target']}: {'MET' if audit['target_met'] else 'NOT MET'})")
    print(f"[corpus] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
