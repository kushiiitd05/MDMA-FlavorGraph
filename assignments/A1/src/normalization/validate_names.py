r"""
NLP sanity gate for extracted ingredient names (brief §50).

An extracted "ingredient name" must not be a quantity, a unit, punctuation noise,
an instruction fragment or a full sentence. Rather than a hand-written blacklist,
the gate is mostly *grammatical* and therefore generalises:

  G1  length      - 1..4 tokens. Error analysis showed spans of 5+ tokens are
                    over-run NER boundaries ("pork loin steak trimmed of fat",
                    "beef fillet ask your butcher"), essentially never real names.
  G2  headedness  - must contain at least one NOUN or PROPN (spaCy POS). Rejects
                    "according", "glutinous", "across the grain".
                    IMPORTANT: the name is tagged INSIDE A CARRIER SENTENCE
                    ("I added the <name> to the pan."). Tagged bare, a one-word
                    noun phrase is read as an imperative VERB - spaCy labels
                    "avocado", "panko", "risotto", "haggis", "pectin" all VERB in
                    isolation and NOUN in context. Without the carrier this gate
                    silently deleted common ingredients.
  G3  no clause   - must not open with a determiner/preposition/pronoun/conjunction
                    ("all the innard", "from ready rolled puff pastry"). NOTE: a
                    VERB tag anywhere is deliberately NOT a rejection criterion -
                    spaCy mis-tags rare and loan words ("ají" -> VERB), and those
                    long-tail regional ingredients are exactly what we must keep.
  G4  no conjunction - "and"/"or" mean an enumeration; those are SPLIT upstream,
                    so anything still containing one is malformed. "with"/"plus"
                    are NOT rejected - they are common in genuine product names
                    ("passata with onion", "tomato with basil").
  G5  not a bare part-word - "zest", "juice", "half" alone name no ingredient.

Names failing the gate are dropped and written to an audit file, never silently.
"""
from __future__ import annotations
import re, functools

# Part / cut words. A part word WITH a parent is ingredient identity
# ("chicken breast", "lemon zest", "salmon fillet"); a part word ALONE names no
# ingredient and is rejected - but extract_ingredients.recover_part_parent() first
# tries to recover the parent from the phrase ("zest of 1 lemon" -> "lemon zest").
# Animal cuts are listed here for the same reason: "fillet" alone is meaningless,
# but "cod fillet" and "chicken thigh" are distinct ingredients, not sizes.
BARE_PART_WORDS = {
    "fillet", "fillets", "breast", "breasts", "thigh", "thighs", "loin", "loins",
    "shoulder", "rack", "racks", "chop", "chops", "cutlet", "cutlets", "wing",
    "wings", "drumstick", "drumsticks", "rasher", "rashers", "shank", "shanks",
    "zest", "juice", "peel", "rind", "skin", "stalk", "stalks", "leaf", "leaves",
    "sprig", "sprigs", "top", "tops", "flesh", "half", "quarter", "third", "piece",
    "pieces", "slice", "slices", "strip", "strips", "chunk", "chunks", "wedge",
    "wedges", "handful", "splash", "drizzle", "sprinkling", "squirt", "mugful",
    "glass", "shot", "portion", "selection", "mixture", "mix", "combination",
    "amount", "quantity", "choice", "topping", "decoration", "extra", "rest",
}
CONJ = re.compile(r"\b(?:and|or)\b", re.I)
# Checked against the first WHITESPACE-delimited token, not the first spaCy token:
# spaCy splits "all-butter" into all/DET + -/PUNCT + butter/NOUN, which would wrongly
# condemn "all-butter shortcrust pastry".
BAD_OPENING_WORDS = {
    "the", "a", "an", "this", "that", "these", "those", "from", "of", "with", "to",
    "in", "on", "for", "by", "at", "and", "or", "but", "if", "as", "than", "then",
    "your", "our", "my", "its", "their", "it", "they", "we", "you", "each",
    "any", "some", "both", "either", "neither", "such", "about", "into", "onto",
}
MAX_TOKENS = 4
CARRIER = "I added the {} to the pan."


@functools.lru_cache(maxsize=1)
def _nlp():
    import spacy
    return spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])


def split_enumeration(span: str) -> list[str]:
    """'poppy seed and sesame seed' -> ['poppy seed', 'sesame seed']."""
    parts = re.split(r"\s+(?:and|or)\s+|\s*,\s*|\s*/\s*", span)
    return [p.strip() for p in parts if p.strip()]


def validate_batch(names: list[str],
                   corpus_solo: dict[str, int] | None = None
                   ) -> dict[str, tuple[bool, str]]:
    """
    Return {name: (is_valid, reason)} for a batch of candidate names.

    `corpus_solo` maps a string to the number of times it appears as an ENTIRE
    ingredient line in our own corpus (quantity/unit/container words removed).
    It is the LAST resort in G2, applied only after the carrier sentence has failed.
    The carrier rescues many bare nouns (avocado, panko, risotto), but not all:
    `rosemary`, `couscous`, `houmous`, `nougat` and `cannelloni` are tagged ADJ even
    inside "I added the ... to the pan." Standing alone as a complete
    ingredient line is direct corpus evidence of nounhood that no generic English
    tagger can override: measured on this corpus, every one of 19 true adjectives
    (golden, double, soft, smoked, sweet, ...) scores 0, while rosemary scores 85
    and couscous 75.
    """
    solo = corpus_solo or {}
    out: dict[str, tuple[bool, str]] = {}
    todo = []
    for n in names:
        toks = n.split()
        if not toks:
            out[n] = (False, "G0_empty")
        elif len(toks) > MAX_TOKENS:
            out[n] = (False, "G1_too_long")
        elif CONJ.search(n):
            out[n] = (False, "G4_conjunction")
        elif len(toks) == 1 and toks[0] in BARE_PART_WORDS:
            out[n] = (False, "G5_bare_part_word")
        else:
            todo.append(n)
    # G3 first: a pure string test, no tagging needed
    # "all" is deliberately NOT in BAD_OPENING_WORDS: it opens genuine UK/US product
    # names ("all butter shortcrust pastry", "all purpose seasoning"). It is only a
    # clause fragment when the NEXT word is also a function word ("all the innard").
    tag_me = []
    for n in todo:
        w = n.split()
        if w[0].lower() == "all":
            if len(w) < 2 or w[1].lower() in BAD_OPENING_WORDS:
                out[n] = (False, "G3_clause_fragment")
            else:
                tag_me.append(n)
        elif w[0].lower() in BAD_OPENING_WORDS:
            out[n] = (False, "G3_clause_fragment")
        else:
            tag_me.append(n)

    # G2 with a carrier sentence so the tagger sees a noun-phrase context
    carriers = [CARRIER.format(n) for n in tag_me]
    lo, hi = CARRIER.index("{}"), len(CARRIER) - CARRIER.index("{}") - 2
    for name, doc in zip(tag_me, _nlp().pipe(carriers, batch_size=512)):
        inner = [t for t in doc if t.idx >= lo and t.idx + len(t.text) <= len(doc.text) - hi]
        pos = [t.pos_ for t in inner]
        if any(p in ("NOUN", "PROPN") for p in pos):
            out[name] = (True, "ok")
        elif solo.get(name, 0) >= 1:
            # Corpus evidence beats the tagger. The carrier sentence above rescues
            # many bare nouns (avocado, panko, risotto) but NOT all of them:
            # "rosemary", "couscous", "houmous", "nougat" and "cannelloni" are still
            # tagged ADJ even inside "I added the ... to the pan."  Standing alone as
            # a complete ingredient line is direct evidence of nounhood.
            out[name] = (True, "ok_corpus_evidence_overrides_G2")
        else:
            out[name] = (False, "G2_no_noun_head")
    return out
