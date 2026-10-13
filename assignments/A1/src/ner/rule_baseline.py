r"""
Deterministic rule/dictionary baseline for ingredient-name extraction.

This is the CONTROL condition for model selection (see the evaluation report).
It is *not* NER - it is a hand-written parser - and exists purely so that the
NER model's benefit can be measured rather than assumed.

Strategy: strip a leading quantity+unit, split on alternation/enumeration
markers, cut the phrase at the first preparation/purpose cue, and return
whatever noun material remains.
"""
from __future__ import annotations
import re, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "normalization"))
from canonicalize import UNIT_WORDS, CONTAINER_WORDS, PREP_WORDS, basic_clean  # noqa: E402

_FRAC = "½¼¾⅓⅔⅛⅜⅝⅞⅕"
# leading quantity: "2", "1 1/2", "400g", "3 x 400g", "1½", "2-3", "&frac12;"
_QTY = re.compile(
    rf"^\s*(?:&frac\d+;|[\d{_FRAC}][\d{_FRAC}\s/.,\-–x×]*)\s*"
    rf"(?:{'|'.join(sorted(UNIT_WORDS, key=len, reverse=True))})?\b\s*", re.I)
# cues after which the rest of the phrase is preparation / purpose, not ingredient
_CUT = re.compile(
    r"\b(?:to serve|to garnish|to decorate|to taste|to finish|for (?:the|deep|frying|greasing|dusting|drizzling|rubbing|shaping)"
    r"|plus extra|plus more|see tip|see tips|if you|we used|you'?ll|optional)\b", re.I)
_SPLIT = re.compile(r"\s+or\s+|\s*,\s*|\s+and\s+", re.I)


def extract(phrase: str) -> list[str]:
    s = re.sub(r"\([^)]*\)", " ", phrase)
    s = _CUT.split(s)[0]
    out: list[str] = []
    for chunk in _SPLIT.split(s):
        c = _QTY.sub("", chunk)
        c = basic_clean(c)
        toks = [w for w in c.split()
                if w not in UNIT_WORDS and w not in CONTAINER_WORDS and len(w) > 1]
        # drop trailing preparation words
        while toks and toks[-1] in PREP_WORDS:
            toks.pop()
        while toks and toks[0] in PREP_WORDS:
            toks.pop(0)
        if toks:
            out.append(" ".join(toks))
    return out


if __name__ == "__main__":
    for t in ["2 tbsp finely chopped fresh coriander", "400g can chopped tomatoes",
              "1 red or white onion or 4 spring onions, chopped", "salt to taste"]:
        print(f"{t!r:50s} -> {extract(t)}")
