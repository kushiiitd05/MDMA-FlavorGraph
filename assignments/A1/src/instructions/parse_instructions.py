r"""
EXTENSION — instruction steps as ordered cooking events.

Each step is mapped to a tuple/JSON event:

    {step_id, action, ingredients, utensils, duration, temperature,
     input_state, output_state}

Method: dependency+POS parse (spaCy en_core_web_sm) to find imperative cooking
VERBS, matched against a curated cooking-action lexicon; utensils and durations
via lexicon/regex; ingredients by matching the recipe's OWN canonical ingredient
list against the step text (so nothing outside the recipe can be hallucinated).

Hard rule: a field is `null` unless the text actually states it. Nothing is
inferred - no default oven temperature, no assumed pan, no guessed duration.
"""
from __future__ import annotations
import json, re, sys, pathlib, collections
import spacy

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/extensions"; OUT.mkdir(parents=True, exist_ok=True)

ACTIONS = {
    "heat", "warm", "preheat", "boil", "simmer", "poach", "blanch", "steam", "fry",
    "stir-fry", "deep-fry", "shallow-fry", "saute", "sauté", "sear", "brown", "roast",
    "bake", "grill", "broil", "toast", "griddle", "barbecue", "caramelise", "caramelize",
    "reduce", "thicken", "melt", "chill", "cool", "freeze", "refrigerate", "rest",
    "prove", "proof", "knead", "roll", "fold", "whisk", "beat", "whip", "cream",
    "stir", "mix", "combine", "blend", "puree", "purée", "mash", "crush", "grind",
    "chop", "slice", "dice", "mince", "grate", "shred", "peel", "trim", "core",
    "deseed", "season", "sprinkle", "drizzle", "pour", "add", "tip", "scatter",
    "spoon", "spread", "layer", "assemble", "cover", "wrap", "marinate", "soak",
    "drain", "rinse", "strain", "sieve", "sift", "squeeze", "serve", "garnish",
    "transfer", "return", "remove", "set", "arrange", "press", "flip", "turn",
    "baste", "glaze", "dust", "coat", "dip", "skewer", "stuff", "fill", "top",
}
UTENSILS = {
    "pan", "frying pan", "saucepan", "casserole", "wok", "skillet", "griddle",
    "roasting tin", "baking tray", "baking sheet", "baking tin", "cake tin",
    "loaf tin", "tin", "tray", "dish", "ovenproof dish", "bowl", "mixing bowl",
    "food processor", "blender", "mixer", "whisk", "sieve", "colander", "grater",
    "knife", "board", "chopping board", "oven", "grill", "microwave", "steamer",
    "pressure cooker", "slow cooker", "air fryer", "ramekin", "jug", "plate",
    "muffin tin", "pie dish", "springform tin", "mandoline", "rolling pin", "spatula",
}
DUR = re.compile(r"\b(\d+(?:\s*[-–]\s*\d+)?)\s*(sec|secs|second|seconds|min|mins|minute|"
                 r"minutes|hr|hrs|hour|hours|day|days)\b", re.I)
TEMP = re.compile(r"\b(\d{2,3})\s*(?:°\s*C|C\b(?:/|\s|,|\.)|degrees?\s*C|"
                  r"gas\s*(?:mark\s*)?\d)|gas\s*(?:mark\s*)?(\d)\b", re.I)
STATE_CUE = re.compile(r"\buntil\s+([a-z][a-z \-]{2,30})", re.I)


def find_utensils(text: str) -> list[str]:
    t = text.lower()
    hits = [u for u in UTENSILS if re.search(rf"\b{re.escape(u)}\b", t)]
    # keep the most specific match only ("frying pan" beats "pan")
    return sorted({h for h in hits if not any(h != o and h in o for o in hits)})


def match_ingredients(low: str, recipe_ings: list[str]) -> list[str]:
    """
    Longest-match ingredient resolution.

    The first version matched on the LAST TOKEN of each canonical name, so a step
    saying "sunflower oil" resolved to *every* oil in the recipe - "olive oil"
    included. Here the full canonical phrase is matched, longest first, and the
    characters it consumes are blocked so a shorter overlapping name cannot also
    fire ("olive oil" consumes the "oil").

    A bare head-noun fallback ("oil" -> "olive oil") is allowed ONLY when exactly
    one of the recipe's ingredients has that head noun, i.e. when it is unambiguous.
    """
    taken: list[tuple[int, int]] = []
    found: list[str] = []

    def free(a: int, b: int) -> bool:
        return all(b <= x or a >= y for x, y in taken)

    for g in sorted(set(recipe_ings), key=lambda x: -len(x)):
        for m in re.finditer(rf"\b{re.escape(g)}\b", low):
            if free(m.start(), m.end()):
                taken.append((m.start(), m.end()))
                found.append(g)
                break

    # unambiguous head-noun fallback
    heads = collections.Counter(g.split()[-1] for g in set(recipe_ings))
    for g in sorted(set(recipe_ings), key=lambda x: -len(x)):
        if g in found:
            continue
        h = g.split()[-1]
        if len(g.split()) == 1 or heads[h] != 1:
            continue
        for m in re.finditer(rf"\b{re.escape(h)}\b", low):
            if free(m.start(), m.end()):
                taken.append((m.start(), m.end()))
                found.append(g)
                break
    return sorted(set(found))


def parse_step(doc, step_id: int, recipe_ings: list[str]) -> dict:
    text = doc.text
    actions = [t.lemma_.lower() for t in doc
               if t.pos_ in ("VERB", "NOUN") and t.lemma_.lower() in ACTIONS]
    actions = list(dict.fromkeys(actions))
    low = text.lower()
    ings = match_ingredients(low, recipe_ings)
    d = DUR.search(text)
    tm = TEMP.search(text)
    st = STATE_CUE.search(text)
    return {
        "step_id": step_id,
        "text": text,
        "actions": actions or None,
        "ingredients": ings or None,
        "utensils": find_utensils(text) or None,
        "duration": (f"{d.group(1)} {d.group(2)}" if d else None),
        "temperature": (tm.group(0).strip() if tm else None),
        "output_state": (st.group(1).strip() if st else None),
    }


def main(limit: int | None = None) -> int:
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    recipes = [json.loads(l) for l in
               (ROOT / "data/processed/recipes_processed.jsonl").open(encoding="utf-8")]
    if limit:
        recipes = recipes[:limit]
    print(f"[instr] recipes: {len(recipes)}")

    flat, ix = [], []
    for r in recipes:
        for i, s in enumerate(r["instruction_steps_raw"] or [], 1):
            flat.append(s); ix.append((r["recipe_id"], i, r["ingredients_canonical"]))
    print(f"[instr] steps: {len(flat)}")

    out = collections.defaultdict(list)
    stats = collections.Counter()
    for doc, (rid, sid, ings) in zip(nlp.pipe(flat, batch_size=256), ix):
        ev = parse_step(doc, sid, ings)
        out[rid].append(ev)
        for k in ("actions", "ingredients", "utensils", "duration", "temperature", "output_state"):
            if ev[k]:
                stats[k] += 1
        stats["steps"] += 1

    p = ROOT / "data/processed/instruction_events.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for rid, evs in out.items():
            f.write(json.dumps({"recipe_id": rid, "events": evs}, ensure_ascii=False) + "\n")

    n = stats["steps"]
    cov = {k: round(stats[k] / n, 4) for k in
           ("actions", "ingredients", "utensils", "duration", "temperature", "output_state")}
    act = collections.Counter(a for evs in out.values() for e in evs for a in (e["actions"] or []))
    ut = collections.Counter(u for evs in out.values() for e in evs for u in (e["utensils"] or []))
    (OUT / "instruction_event_summary.json").write_text(json.dumps({
        "n_recipes": len(recipes), "n_steps": n,
        "field_coverage_fraction_of_steps": cov,
        "top_30_actions": act.most_common(30),
        "top_20_utensils": ut.most_common(20),
        "policy": "A field is null unless the step text states it. Nothing is inferred.",
    }, indent=2))
    print(f"[instr] coverage: {cov}")
    print(f"[instr] top actions: {act.most_common(10)}")
    print(f"[instr] wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
