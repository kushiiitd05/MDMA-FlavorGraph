r"""
Q1(b) + Q1(c) - extract ingredient names with NER and build the
(Recipe ID) - (Ingredient Name) table.

Pipeline per ingredient phrase (the staged design of §52 of the brief):

    raw phrase
       |-- preprocess_phrase()        strip editorial parentheticals
       |-- spaCy NER                  NAME / QUANTITY / UNIT / STATE spans
       |-- rule fallback              ONLY when NER returns no NAME span
       |-- split_enumeration()        "poppy seed and sesame seed" -> two names
       |-- trim_span()                repair over-long spans
       |-- normalize_surface()        -> ingredient_normalized
       |-- canonicalize()             -> ingredient_canonical   (REQUIRED outputs)
       |-- family()                   -> ingredient_family      (extensions only)
       `-- validate_batch()           grammatical sanity gate (brief §50)

Every layer is written to disk separately; the raw phrase is never overwritten.

Outputs
-------
  data/processed/ingredient_mentions.csv        rich mention-level table
  data/processed/recipes_processed.jsonl        recipe-level processed records
  outputs/Q1/Q1c_recipe_ingredient.csv          the REQUIRED simple table
"""
from __future__ import annotations
import csv, json, re, sys, pathlib, collections
import spacy, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/normalization"))
sys.path.insert(0, str(ROOT / "src/ner"))
from canonicalize import (normalize_surface, canonicalize, family,  # noqa: E402
                          trim_span, preprocess_phrase, PROTECTED_COMPOUNDS,
                          basic_clean, UNIT_WORDS, CONTAINER_WORDS)
from validate_names import (validate_batch, split_enumeration,  # noqa: E402
                            BARE_PART_WORDS)
import rule_baseline  # noqa: E402

CFG = yaml.safe_load((ROOT / "config/config.yaml").read_text())

# Model choice is EMPIRICAL: outputs/extensions/ner_evaluation.json ranks every
# candidate on the 206-phrase gold set drawn from our own corpus. The transformer
# NER wins (canonical F1 0.893 hybrid / 0.890 alone) over the CNN (0.873 / 0.858),
# the rule baseline (0.846) and a local qwen2.5:3b LLM (0.867 - at ~1.35 s/phrase,
# i.e. ~45 h for this corpus). Prefer the transformer; fall back to the CNN.
_TRF = ROOT / "data/interim/ner_trf/model-best"
_CNN = ROOT / "data/interim/ner_cnn/model-best"
MODEL = _TRF if _TRF.exists() else _CNN


# --------------------------------------------------------------- attachment
_SEG = re.compile(r",|;|\band\b|\bor\b", re.I)


def segment_bounds(text: str) -> list[tuple[int, int]]:
    """
    Split an ingredient line at coordination boundaries.

    "chopped onions and diced tomatoes" -> ["chopped onions", "diced tomatoes"]
    so that each modifier can be attached to the ingredient it actually modifies
    instead of being copied onto every name in the line.
    """
    cuts = [0] + [m.end() for m in _SEG.finditer(text)] + [len(text)]
    return [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]


def seg_index(pos: int, segs: list[tuple[int, int]]) -> int:
    for i, (a, b) in enumerate(segs):
        if a <= pos < b:
            return i
    return len(segs) - 1


def attach(mods: list[tuple[str, int]], names: list[tuple[str, int, int]],
           segs: list[tuple[int, int]]) -> dict[int, list[str]]:
    """
    Assign each modifier span to exactly one NAME span.

    Rule (deliberately simple and explainable):
      * one NAME in the line  -> every modifier attaches to it
        ("peeled and chopped potatoes" keeps BOTH modifiers)
      * otherwise             -> the NAME in the same coordination segment;
        failing that, the nearest preceding NAME; failing that, the nearest following.
    """
    out: dict[int, list[str]] = collections.defaultdict(list)
    if not names:
        return out
    if len(names) == 1:
        out[0] = [t for t, _ in mods]
        return out
    name_seg = [seg_index(a, segs) for _, a, _ in names]
    for text, pos in mods:
        sg = seg_index(pos, segs)
        cand = [i for i, s_ in enumerate(name_seg) if s_ == sg]
        if not cand:
            before = [i for i, (_, a, _) in enumerate(names) if a <= pos]
            cand = [before[-1]] if before else [0]
        out[cand[0]].append(text)
    return out


# --------------------------------------------------------------- alternations
_OR = re.compile(r"\bor\b", re.I)
_AND = re.compile(r"\band\b|,|;|\+|&", re.I)


def alternative_groups(text: str, names: list[tuple[str, int, int]]) -> list[int]:
    """
    Group NAME spans that are ALTERNATIVES of one another.

    "olive oil or sunflower oil" offers a choice - a cook uses ONE of them - so the
    line contributes ONE ingredient slot, not two. "salt and pepper" is two
    co-ingredients. Two consecutive spans are alternatives when the text between
    them contains a standalone "or" and no "and"/","/"&" separator.

    Returns a group index per span; index 0 of each group is the PRIMARY.
    """
    groups, g = [], 0
    for i, (_, a, _b) in enumerate(names):
        if i == 0:
            groups.append(0); continue
        between = text[names[i - 1][2]:a]
        if _OR.search(between) and not _AND.search(between):
            groups.append(g)              # same slot: an alternative
        else:
            g += 1
            groups.append(g)
    return groups


# --------------------------------------------------------- part-word recovery
_PART_OF = re.compile(
    r"\b(zest|juice|peel|rind|leaves|leaf|stalks?|flesh|skin|seeds?|kernels?|"
    r"fillets?|breasts?|thighs?|legs?|shoulders?|loins?|racks?|wings?)\b"
    r"(?:\s+and\s+\w+)?"          # "zest and juice of 1 orange" binds BOTH parts
    r"\s+(?:of|from)\s+(?:[\d\s½¼¾⅓⅔/.,-]*)([a-zA-Z][a-zA-Z\- ]{2,25})", re.I)


def recover_part_parent(text: str, part: str) -> str | None:
    """
    "zest of 1 lemon" -> "lemon zest".

    A part word alone ("zest", "fillet") names no ingredient, but the phrase very
    often states its parent. 456 phrases in this corpus use the "<part> of <parent>"
    construction, so the parent is recoverable rather than lost. Returns None when
    the phrase does not actually state a parent - nothing is guessed.
    """
    for m in _PART_OF.finditer(text):
        if m.group(1).lower().rstrip("s") != part.lower().rstrip("s"):
            continue
        parent = " ".join(m.group(2).lower().split()[:2]).strip(" -")
        parent = re.sub(r"\b(large|small|medium|ripe|fresh|unwaxed|juicy)\b", " ", parent)
        parent = " ".join(parent.split())
        if parent and parent not in ("the", "a", "an", "half", "one"):
            return f"{parent} {part.lower()}"
    return None


def expand_protected(text: str, start: int, end: int, max_left: int = 3) -> str:
    """
    Grow a NAME span leftwards if doing so completes a known protected compound.

    The NER sometimes leaves a product-defining modifier outside the NAME span and
    does not tag it as STATE either, so the information is lost entirely:
    "100g light brown sugar" gave NAME="brown sugar" and no STATE, dropping "light"
    (light vs dark brown sugar are different products). Only an EXPLICIT protected
    compound can trigger the expansion, so this never invents a longer name.
    """
    span = text[start:end]
    left = text[:start].split()
    for k in range(1, min(max_left, len(left)) + 1):
        cand = " ".join(left[-k:] + [span])
        if cand.replace("-", " ").lower() in _PROT_NOHYPH:
            return cand
    return span


_PROT_NOHYPH = {c.replace("-", " ") for c in PROTECTED_COMPOUNDS}


def resolve(span_text: str):
    """NAME span -> (normalized, canonical, family, provenance). None if rejected."""
    t = trim_span(span_text)
    norm, prov = normalize_surface(t)
    if not norm:
        return None
    canon, cprov = canonicalize(norm)
    fam, fprov = family(canon)
    return norm, canon, fam, prov + cprov + fprov


def main() -> int:
    if not MODEL.exists():
        print(f"[ner] ERROR: model not found at {MODEL}"); return 1
    nlp = spacy.load(str(MODEL))
    print(f"[ner] model: {MODEL.relative_to(ROOT)}")
    recipes = [json.loads(l) for l in (ROOT / "data/interim/recipes_clean.jsonl").open(encoding="utf-8")]
    print(f"[ner] recipes: {len(recipes)}")

    # flatten every ingredient phrase so spaCy can batch them
    flat, index = [], []
    for r in recipes:
        for i, p in enumerate(r["ingredient_phrases_raw"]):
            flat.append(preprocess_phrase(p))
            index.append((r["recipe_id"], i, p))
    print(f"[ner] ingredient phrases: {len(flat)}")

    mentions = []
    stats = collections.Counter()
    for doc, (rid, idx, raw) in zip(
            nlp.pipe(flat, batch_size=64, n_process=1), index):
        text = doc.text
        name_ents = [(e.text, e.start_char, e.end_char)
                     for e in doc.ents if e.label_ == "NAME"]
        qty_ents = [(e.text, e.start_char) for e in doc.ents if e.label_ == "QUANTITY"]
        unit_ents = [(e.text, e.start_char) for e in doc.ents if e.label_ == "UNIT"]
        state_ents = [(e.text, e.start_char) for e in doc.ents if e.label_ == "STATE"]
        method = "ner"
        if not name_ents:                              # hybrid fallback
            name_ents = [(n, text.find(n) if text.find(n) >= 0 else 0,
                          (text.find(n) if text.find(n) >= 0 else 0) + len(n))
                         for n in rule_baseline.extract(text)]
            method = "rule_fallback" if name_ents else "none"

        # genuine agreement signal (NOT a fabricated probability):
        rule_names = rule_baseline.extract(text)
        rule_canon = {c for n in rule_names if (res := resolve(n)) for c in [res[1]]}

        # expand enumerations inside one NAME span, keeping character offsets so
        # modifiers can still be attached to the right sub-name
        expanded: list[tuple[str, int, int]] = []
        for t_, a_, b_ in name_ents:
            parts = split_enumeration(t_)
            if len(parts) <= 1:
                expanded.append((t_, a_, b_))
                continue
            cur = a_
            for pt in parts:
                j = text.find(pt, cur, b_)
                j = a_ if j < 0 else j
                expanded.append((pt, j, j + len(pt)))
                cur = j + len(pt)

        alt_g = alternative_groups(text, expanded)
        segs = segment_bounds(text)
        st_by = attach(state_ents, expanded, segs)
        qt_by = attach(qty_ents, expanded, segs)
        un_by = attach(unit_ents, expanded, segs)

        seen_in_phrase = set()
        seen_groups: set[int] = set()
        recovered_parents: set[str] = set()
        for k, (n, _a, _b) in enumerate(expanded):
            n = expand_protected(text, _a, _b)
            res = resolve(n)
            if res and res[0] in BARE_PART_WORDS:      # "zest" -> "lemon zest"
                rec = recover_part_parent(text, res[0])
                if rec:
                    r2 = resolve(rec)
                    if r2:
                        res = r2
                        # "zest of 1 lemon" must not also yield a bare "lemon"
                        recovered_parents.add(rec.rsplit(" ", 1)[0].strip())
                        stats["part_parent_recovered"] += 1
            if not res:
                stats["rejected_span"] += 1
                continue
            norm, canon, fam, prov = res
            if canon in recovered_parents:
                stats["parent_absorbed_into_part"] += 1
                continue
            grp = alt_g[k] if k < len(alt_g) else k
            is_primary = grp not in seen_groups
            seen_groups.add(grp)
            if canon in seen_in_phrase:
                continue
            seen_in_phrase.add(canon)
            my_states = st_by.get(k, [])
            mentions.append({
                "recipe_id": rid,
                "ingredient_index": idx,
                "raw_phrase": raw,
                "ingredient_surface": n,
                "ingredient_normalized": norm,
                "ingredient_canonical": canon,
                "ingredient_family": fam,
                "quantity_raw": (qt_by.get(k) or [None])[0],
                "unit_raw": (un_by.get(k) or [None])[0],
                "processing_state": "|".join(
                    dict.fromkeys(x.lower() for x in my_states)) or None,
                "alternative_group": grp,
                "is_primary_alternative": is_primary,
                "extraction_method": method,
                "agrees_with_rule_baseline": canon in rule_canon,
                "normalization_provenance": "|".join(dict.fromkeys(prov)),
            })
            stats[method] += 1
        if not expanded:
            stats["phrase_no_ingredient"] += 1

    # ------------------------------------------------------- sanity gate §50
    # Corpus evidence for the gate: how often is a string an ENTIRE ingredient line?
    solo = collections.Counter()
    for r in recipes:
        for p_ in r["ingredient_phrases_raw"]:
            c = basic_clean(p_)
            t = [w for w in c.split()
                 if w not in UNIT_WORDS and w not in CONTAINER_WORDS and len(w) > 1]
            # a whole ingredient line that reduces to <=3 content tokens is
            # evidence that that string can stand alone as an ingredient
            if 1 <= len(t) <= 3:
                solo[" ".join(t)] += 1
    cand = sorted({m["ingredient_canonical"] for m in mentions})
    verdict = validate_batch(cand, corpus_solo=solo)
    bad = {n: r for n, (ok_, r) in verdict.items() if not ok_}
    before = len(mentions)
    mentions = [m for m in mentions if m["ingredient_canonical"] not in bad]
    rej = collections.Counter(bad.values())
    print(f"[gate] candidate names: {len(cand)}  rejected: {len(bad)}  {dict(rej)}")
    print(f"[gate] mentions dropped: {before - len(mentions)} of {before}")
    (ROOT / "outputs/extensions/rejected_ingredient_names.csv").parent.mkdir(
        parents=True, exist_ok=True)
    with (ROOT / "outputs/extensions/rejected_ingredient_names.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["rejected_name", "gate_reason"])
        for n, r in sorted(bad.items()):
            w.writerow([n, r])

    print(f"[ner] mentions extracted: {len(mentions)}   {dict(stats)}")
    agree = sum(m["agrees_with_rule_baseline"] for m in mentions)
    print(f"[ner] NER/rule agreement: {agree}/{len(mentions)} = {100*agree/len(mentions):.1f}%")

    # ---------------------------------------------------------- mention table
    cols = list(mentions[0].keys())
    out_m = ROOT / "data/processed/ingredient_mentions.csv"
    out_m.parent.mkdir(parents=True, exist_ok=True)
    with out_m.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(mentions)
    print(f"[ner] wrote {out_m}")

    # ---------------------------------------------------------- REQUIRED Q1(c)
    # FROZEN CONVENTION (docs/DECISION_LOG.md D11): for the REQUIRED Q1(c)/Q2/Q3
    # outputs an "A or B" line contributes ONE ingredient - the primary (first)
    # alternative - because a cook makes one choice. Every alternative is still
    # kept in ingredient_mentions.csv, tagged with its alternative_group.
    by_recipe: dict[str, list[str]] = collections.defaultdict(list)
    by_recipe_all: dict[str, list[str]] = collections.defaultdict(list)
    for m in mentions:
        if m["ingredient_canonical"] not in by_recipe_all[m["recipe_id"]]:
            by_recipe_all[m["recipe_id"]].append(m["ingredient_canonical"])
        if not m["is_primary_alternative"]:
            continue
        if m["ingredient_canonical"] not in by_recipe[m["recipe_id"]]:
            by_recipe[m["recipe_id"]].append(m["ingredient_canonical"])
    n_alt = sum(1 for m in mentions if not m["is_primary_alternative"])
    print(f"[ner] alternative (non-primary) mentions excluded from Q1c/Q2/Q3: {n_alt:,}")

    out_q1c = ROOT / "outputs/Q1/Q1c_recipe_ingredient.csv"
    out_q1c.parent.mkdir(parents=True, exist_ok=True)
    n_rows = 0
    with out_q1c.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Recipe ID", "Ingredient Name"])
        for r in recipes:
            for ing in by_recipe.get(r["recipe_id"], []):
                w.writerow([r["recipe_id"], ing]); n_rows += 1
    print(f"[ner] wrote {out_q1c}  ({n_rows} rows)")

    # ---------------------------------------------------------- processed recipes
    mby = collections.defaultdict(list)
    for m in mentions:
        mby[m["recipe_id"]].append(m)
    out_p = ROOT / "data/processed/recipes_processed.jsonl"
    with out_p.open("w", encoding="utf-8") as f:
        for r in recipes:
            ms = mby.get(r["recipe_id"], [])
            f.write(json.dumps({
                "recipe_id": r["recipe_id"],
                "title": r["title"],
                "source_url": r["source_url"],
                "canonical_url": r["canonical_url"],
                "cuisine_raw": r["cuisine_raw"],
                "category_raw": r["category_raw"],
                "total_time_raw": r["total_time_raw"],
                "yield_raw": r["yield_raw"],
                "nutrition_raw": r["nutrition_raw"],
                "n_ingredient_phrases": r["n_ingredient_phrases"],
                "n_instruction_steps": r["n_instruction_steps"],
                "instruction_steps_raw": r["instruction_steps_raw"],
                "ingredient_phrases_raw": r["ingredient_phrases_raw"],
                "ingredients_canonical": by_recipe.get(r["recipe_id"], []),
                "ingredients_canonical_incl_alternatives": by_recipe_all.get(r["recipe_id"], []),
                "ingredients_family": list(dict.fromkeys(m["ingredient_family"] for m in ms)),
                "mentions": ms,
            }, ensure_ascii=False) + "\n")
    print(f"[ner] wrote {out_p}")

    n_empty = sum(1 for r in recipes if not by_recipe.get(r["recipe_id"]))
    print(f"[ner] recipes with zero extracted ingredients: {n_empty}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
