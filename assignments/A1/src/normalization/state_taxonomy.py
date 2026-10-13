r"""
Observed-only state taxonomy for the ingredient/process extension.

WHY THIS EXISTS
---------------
The first version of the state analysis filtered states with `PREP_WORDS` - a list
written for a completely different job (stripping descriptor words off the EDGES of
an ingredient-name span). Reusing it as a semantic filter produced exactly the wrong
cut: it discarded 15 of 17 cooking transformations (`fried`, `boiled`, `caramelised`,
`grilled`, `baked`, `smoked` - 865 mentions alone) while keeping size words
(`large` = 3,782 mentions) as if they were process states.

WHAT THIS DOES INSTEAD
----------------------
Classifies an OBSERVED state string into a small, transparent taxonomy:

    PREPARATION   mechanical/knife work        chopped, diced, grated, peeled
    COOKING       thermal/chemical transform   fried, boiled, roasted, caramelised
    QUALITY       physical condition/grade     fresh, dried, frozen, ripe, raw
    SIZE          dimension                    small, medium, large, thick
    NOT_A_STATE   extraction noise             handful, heaped, ready-, low-
    UNCLASSIFIED  observed but not confidently classifiable

DESIGN RULES
------------
* The vocabulary below was read off the ACTUAL corpus (top observed states by
  frequency), not imported from an external food ontology.
* Classification is by HEAD WORD (last token), so "finely chopped", "roughly
  chopped" and "very finely chopped" all resolve to PREPARATION via `chopped`.
* Nothing is ever silently dropped. A state that matches nothing is returned as
  UNCLASSIFIED with its original text intact, so it stays auditable.
* Where a word is genuinely ambiguous we do NOT pretend otherwise - see AMBIGUOUS.
"""
from __future__ import annotations

PREPARATION = {
    "chopped", "sliced", "diced", "minced", "grated", "crushed", "peeled", "halved",
    "quartered", "deseeded", "seeded", "cored", "stoned", "pitted", "trimmed",
    "shredded", "beaten", "whisked", "cubed", "drained", "rinsed", "washed",
    "picked", "juiced", "zested", "squeezed", "separated", "flaked", "crumbled",
    "sifted", "sieved", "torn", "mashed", "blended", "pureed", "ground", "milled",
    "podded", "shelled", "skinned", "boned", "filleted", "butterflied", "scored",
    "scrubbed", "stripped", "unrolled", "rolled", "shaved", "julienned", "grated",
    # "cut into X" family - head word carries the shape
    "chunks", "pieces", "wedges", "cubes", "slices", "rings", "strips", "sticks",
    "batons", "florets", "matchsticks", "lengths", "ribbons", "rounds", "quarters",
    "halves", "removed", "discarded", "reserved", "dice", "cut", "sliced",
}

COOKING = {
    "fried", "stir-fried", "deep-fried", "shallow-fried", "boiled", "baked",
    "grilled", "griddled", "steamed", "roasted", "toasted", "poached", "blanched",
    "seared", "browned", "charred", "barbecued", "caramelised", "caramelized",
    "sauteed", "sautéed", "melted", "cooked", "smoked", "cured", "pickled",
    "fermented", "brined", "marinated", "infused", "reduced", "simmered",
    "parboiled", "part-baked", "pre-baked", "blind-baked", "warmed", "heated",
    # gerund forms seen in the corpus ("for deep frying", "for roasting")
    "frying", "boiling", "roasting", "baking", "grilling", "steaming", "poaching",
    "toasting", "searing", "browning", "smoking", "simmering",
}

QUALITY = {
    "fresh", "dried", "frozen", "ripe", "unripe", "raw", "chilled", "cold", "hot",
    "warm", "softened", "soft", "firm", "hard", "stale", "leftover", "salted",
    "unsalted", "sweetened", "unsweetened", "organic", "free-range", "mature",
    "strong", "mild", "plain", "dry", "wet", "skinless", "boneless", "seedless",
    "virgin", "wholemeal", "wholegrain", "refined", "smooth", "crunchy", "creamy",
    "natural", "pasteurised", "unpasteurised", "defrosted", "thawed", "rested",
}

SIZE = {
    "large", "small", "medium", "big", "thick", "thin", "fine", "coarse",
    "tiny", "jumbo", "baby", "extra-large", "king-size", "chunky", "wide", "narrow",
    "long", "short", "shallow",
    # NOTE: "little" is deliberately NOT here - "a little olive oil" is a quantity
    # word, so it belongs in NOT_A_STATE. "deep" is likewise omitted because
    # "deep frying" is a cooking method, not a dimension.
}

# Observed strings that are NOT ingredient states at all - they are quantity words,
# truncated compounds or extraction noise. Recorded explicitly (never silently
# dropped) so the state analysis can exclude them and still be audited.
NOT_A_STATE = {
    "handful", "handfuls", "heaped", "level", "rounded", "generous", "splash",
    "drizzle", "pinch", "dash", "knob", "glug", "squeeze", "sprinkling", "scoop",
    "ready-", "low-", "high-", "extra-", "semi-", "non-", "half-", "self-",
    "clear", "light", "dark", "extra", "virgin-", "good", "quality", "best",
    "value", "favourite", "optional", "assorted", "mixed", "each", "total",
    "little", "plus", "more", "less", "about", "approx", "such",
}

# Words whose category genuinely depends on context. We assign a best-effort
# category but flag them, rather than pretending the classification is certain.
AMBIGUOUS = {
    "ground": "PREPARATION",   # "ground cumin" (milled) vs "ground beef" (minced)
    "melted": "COOKING",       # thermal, but often just a preparation instruction
    "smoked": "COOKING",       # a curing process, but often a product grade
    "cooked": "COOKING",
    "softened": "QUALITY",     # butter left out to warm
    "whole": "QUALITY",        # "whole almonds" (uncut) vs "whole milk" (grade)
    "rolled": "PREPARATION",   # "rolled oats" is really a product name
    "mixed": "NOT_A_STATE",
}

_ORDER = (("PREPARATION", PREPARATION), ("COOKING", COOKING),
          ("QUALITY", QUALITY), ("SIZE", SIZE), ("NOT_A_STATE", NOT_A_STATE))


def classify_state(state_text: str) -> tuple[str, bool]:
    """
    Classify one OBSERVED state string.

    Returns (category, is_ambiguous). Category is one of
    PREPARATION / COOKING / QUALITY / SIZE / NOT_A_STATE / UNCLASSIFIED.
    The original `state_text` is never modified - callers keep it verbatim.
    """
    s = (state_text or "").strip().lower()
    if not s:
        return "UNCLASSIFIED", False
    toks = s.replace("/", " ").split()
    if not toks:
        return "UNCLASSIFIED", False

    head = toks[-1]
    if head in AMBIGUOUS:
        return AMBIGUOUS[head], True
    for name, vocab in _ORDER:
        if head in vocab:
            return name, False
    # a leading token can still carry the category ("cut into chunks" -> chunks
    # already handled; "fresh chopped" -> chopped handled; try any token)
    # Fall back to any token, but scan CATEGORIES in priority order rather than
    # tokens left-to-right: "deep frying" must resolve on "frying" (COOKING), not
    # on the leading "deep".
    for name, vocab in _ORDER:
        for t in toks:
            if t in vocab:
                return name, False
    for t in toks:
        if t in AMBIGUOUS:
            return AMBIGUOUS[t], True
    return "UNCLASSIFIED", False


# Categories that count as a genuine ingredient state for the process analysis.
STATE_CATEGORIES = ("PREPARATION", "COOKING", "QUALITY", "SIZE")
