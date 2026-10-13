r"""
Package the REQUIRED deliverables into outputs/Q1..Q3 with question-numbered names,
then create checksummed backups (brief §44-§46).

Required-vs-extension separation is physical: everything a grader needs is in
outputs/Q1, outputs/Q2, outputs/Q3; research extras live only in outputs/extensions.
"""
from __future__ import annotations
import csv, gzip, hashlib, json, shutil, sys, pathlib, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parents[2]


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    q1 = ROOT / "outputs/Q1"; q1.mkdir(parents=True, exist_ok=True)

    # --- Q1(a) raw data (gzipped: the uncompressed JSONL is large) -------------
    src = ROOT / "data/raw/recipes_raw.jsonl"
    dst = q1 / "Q1a_raw_recipes.jsonl"
    shutil.copy2(src, dst)
    with dst.open("rb") as f_in, gzip.open(q1 / "Q1a_raw_recipes.jsonl.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"[pkg] Q1a raw: {dst} ({dst.stat().st_size/1e6:.1f} MB)")

    # human-readable metadata view of the raw corpus
    recs = [json.loads(l) for l in (ROOT / "data/interim/recipes_clean.jsonl").open(encoding="utf-8")]
    with (q1 / "Q1a_recipe_metadata.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["recipe_id", "title", "source_url", "cuisine_raw", "category_raw",
                    "prep_time_raw", "cook_time_raw", "total_time_raw", "yield_raw",
                    "n_ingredient_phrases", "n_instruction_steps", "date_scraped"])
        for r in recs:
            w.writerow([r["recipe_id"], r["title"], r["source_url"], r["cuisine_raw"],
                        r["category_raw"], r["prep_time_raw"], r["cook_time_raw"],
                        r["total_time_raw"], r["yield_raw"], r["n_ingredient_phrases"],
                        r["n_instruction_steps"], r["date_scraped"]])

    # --- Q1(b) NER output -----------------------------------------------------
    shutil.copy2(ROOT / "data/processed/ingredient_mentions.csv",
                 q1 / "Q1b_ingredient_ner_output.csv")
    shutil.copy2(ROOT / "outputs/extensions/ner_evaluation.json",
                 q1 / "Q1b_ner_evaluation.json")
    print("[pkg] Q1b NER output + evaluation copied")

    # --- backups with checksums ----------------------------------------------
    bk = ROOT / "backup"; bk.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    manifest = {"created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "files": []}
    to_back = [
        ("raw_corpus", ROOT / "data/raw/recipes_raw.jsonl"),
        ("processed_corpus", ROOT / "data/processed/recipes_processed.jsonl"),
        ("ingredient_mentions", ROOT / "data/processed/ingredient_mentions.csv"),
        ("Q1c_table", ROOT / "outputs/Q1/Q1c_recipe_ingredient.csv"),
        ("Q2a_frequency", ROOT / "outputs/Q2/Q2a_unique_ingredients_frequency.csv"),
        ("Q3a_frequency_rank", ROOT / "outputs/Q3/Q3a_frequency_rank.csv"),
    ]
    for name, p in to_back:
        if not p.exists():
            print(f"[pkg] WARN missing {p}"); continue
        out = bk / f"{name}.{stamp}{p.suffix}.gz"
        with p.open("rb") as fi, gzip.open(out, "wb") as fo:
            shutil.copyfileobj(fi, fo)
        manifest["files"].append({
            "name": name, "source": str(p.relative_to(ROOT)),
            "backup": str(out.relative_to(ROOT)),
            "source_bytes": p.stat().st_size, "source_sha256": sha256(p),
            "backup_bytes": out.stat().st_size})
        print(f"[pkg] backed up {name} -> {out.name}")

    (bk / f"MANIFEST.{stamp}.json").write_text(json.dumps(manifest, indent=2))
    (bk / "MANIFEST.latest.json").write_text(json.dumps(manifest, indent=2))
    print(f"[pkg] manifest written ({len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
