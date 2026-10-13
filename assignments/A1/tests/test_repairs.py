r"""
Targeted validation for the repair pass.

Purpose (per the repair brief §23): demonstrate that the system preserves INGREDIENT
IDENTITY while capturing OBSERVED preparation/cooking state - not to produce a fancy
benchmark. Run:  ./.venv/bin/python tests/test_repairs.py
"""
from __future__ import annotations
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/normalization"))
sys.path.insert(0, str(ROOT / "src/ner"))
sys.path.insert(0, str(ROOT / "src/instructions"))

import spacy                                            # noqa: E402
import extract_ingredients as E                         # noqa: E402
from canonicalize import preprocess_phrase              # noqa: E402
from validate_names import split_enumeration            # noqa: E402
from state_taxonomy import classify_state               # noqa: E402
from parse_instructions import match_ingredients        # noqa: E402

_nlp = None


def pipeline(phrase: str) -> list[tuple[str, list[str]]]:
    """Run the real extraction path and return [(canonical, [states]), ...]."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(str(ROOT / "data/interim/ner_trf/model-best"))
    doc = _nlp(preprocess_phrase(phrase))
    text = doc.text
    names = [(e.text, e.start_char, e.end_char) for e in doc.ents if e.label_ == "NAME"]
    states = [(e.text, e.start_char) for e in doc.ents if e.label_ == "STATE"]
    exp = []
    for t, a, b in names:
        parts = split_enumeration(t)
        if len(parts) <= 1:
            exp.append((t, a, b)); continue
        cur = a
        for pt in parts:
            j = text.find(pt, cur, b); j = a if j < 0 else j
            exp.append((pt, j, j + len(pt))); cur = j + len(pt)
    segs = E.segment_bounds(text)
    st = E.attach(states, exp, segs)
    out = []
    for k, (n, a, b) in enumerate(exp):
        r = E.resolve(E.expand_protected(text, a, b))
        if r:
            out.append((r[1], [x.lower() for x in st.get(k, [])]))
    return out


FAILS: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{('  ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def identity(phrase: str, expect: str) -> None:
    got = pipeline(phrase)
    canon = [c for c, _ in got]
    check(f"identity: {phrase!r} -> {expect!r}", expect in canon, f"got {canon}")


def state_case(phrase: str, ing: str, expect_states: set[str]) -> None:
    got = dict(pipeline(phrase))
    have = set(got.get(ing, []))
    check(f"state: {phrase!r} -> {ing} + {sorted(expect_states)}",
          ing in got and expect_states <= have, f"got {ing in got and sorted(have)}")


def main() -> int:
    print("\n=== 1. INGREDIENT IDENTITY MUST SURVIVE (no collapse to a generic parent) ===")
    for p, e in [("2 tbsp sunflower oil", "sunflower oil"),
                 ("2 tbsp mustard oil", "mustard oil"),
                 ("2 tbsp olive oil", "olive oil"),
                 ("1 tbsp sesame oil", "sesame oil"),
                 ("2 tbsp extra virgin olive oil", "extra virgin olive oil"),
                 ("400ml coconut milk", "coconut milk"),
                 ("1 tbsp rice vinegar", "rice vinegar"),
                 ("2 tbsp balsamic vinegar", "balsamic vinegar"),
                 ("100g almond flour", "almond flour"),
                 ("150g gram flour", "gram flour"),
                 ("1 sweet potato", "sweet potato"),
                 ("100g dark chocolate", "dark chocolate"),
                 ("200ml whole milk", "whole milk"),
                 ("100g light brown sugar", "light brown sugar"),
                 ("100g dark brown sugar", "dark brown sugar"),
                 ("500ml chicken stock", "chicken stock")]:
        identity(p, e)

    print("\n  -- and must NOT become the bare parent --")
    for p, bad in [("2 tbsp sunflower oil", "oil"), ("2 tbsp mustard oil", "oil"),
                   ("400ml coconut milk", "milk"), ("1 tbsp rice vinegar", "vinegar"),
                   ("100g almond flour", "flour")]:
        canon = [c for c, _ in pipeline(p)]
        check(f"{p!r} does NOT collapse to {bad!r}", bad not in canon, f"got {canon}")

    print("\n=== 2. STATE IS CAPTURED AND ATTACHED TO THE RIGHT INGREDIENT ===")
    state_case("chopped onions", "onion", {"chopped"})
    state_case("diced tomatoes", "tomato", {"diced"})
    state_case("fried onions", "onion", {"fried"})
    state_case("boiled potatoes", "potato", {"boiled"})
    state_case("2 large fresh chopped onions", "onion", {"large", "fresh", "chopped"})
    state_case("peeled and chopped potatoes", "potato", {"peeled", "chopped"})

    print("\n  -- coordination: each state on its OWN ingredient --")
    got = dict(pipeline("chopped onions and diced tomatoes"))
    check("coordination: onion gets 'chopped' only",
          "chopped" in got.get("onion", []) and "diced" not in got.get("onion", []),
          f"onion={got.get('onion')}")
    check("coordination: tomato gets 'diced' only",
          "diced" in got.get("tomato", []) and "chopped" not in got.get("tomato", []),
          f"tomato={got.get('tomato')}")

    print("\n=== 3. TAXONOMY: cooking transformations are NOT discarded ===")
    for s, exp in [("chopped", "PREPARATION"), ("finely chopped", "PREPARATION"),
                   ("diced", "PREPARATION"), ("grated", "PREPARATION"),
                   ("fried", "COOKING"), ("boiled", "COOKING"), ("baked", "COOKING"),
                   ("grilled", "COOKING"), ("steamed", "COOKING"),
                   ("caramelised", "COOKING"), ("roasted", "COOKING"),
                   ("fresh", "QUALITY"), ("dried", "QUALITY"), ("frozen", "QUALITY"),
                   ("raw", "QUALITY"), ("ripe", "QUALITY"),
                   ("large", "SIZE"), ("small", "SIZE"), ("medium", "SIZE")]:
        got, _ = classify_state(s)
        check(f"taxonomy: {s!r} -> {exp}", got == exp, f"got {got}")

    print("\n=== 4. INSTRUCTION MATCHING: longest match, no last-token guessing ===")
    check("'olive oil' step resolves to olive oil",
          match_ingredients("heat the olive oil in a pan",
                            ["olive oil", "sunflower oil", "onion"]) == ["olive oil"])
    check("'sunflower oil' step does NOT resolve to olive oil",
          match_ingredients("heat the sunflower oil in a pan",
                            ["olive oil", "sunflower oil", "onion"]) == ["sunflower oil"])
    check("ambiguous bare 'oil' with two oils -> no guess",
          match_ingredients("add the oil", ["olive oil", "sunflower oil"]) == [])
    check("unambiguous bare 'oil' with one oil -> resolves",
          match_ingredients("add the oil", ["olive oil", "onion"]) == ["olive oil"])

    print("\n" + "=" * 70)
    print(f"RESULT: {'ALL CHECKS PASS' if not FAILS else f'{len(FAILS)} FAILURE(S)'}")
    for f in FAILS:
        print("   FAILED:", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
