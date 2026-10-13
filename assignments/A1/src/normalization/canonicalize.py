r"""
Ingredient normalisation & canonicalisation (Layer 3 and 4 of the pipeline).

    RAW phrase  ->  NER NAME span  ->  ingredient_normalized  ->  ingredient_canonical
                                                              \-> ingredient_family (extension only)

Design principles (see docs/DECISION_LOG.md, D5/D6)
--------------------------------------------------
* NON-DESTRUCTIVE. `coconut milk` must never become `milk`; `rice vinegar` must never
  become `rice`. A PROTECTED_COMPOUNDS guard enforces this at the family level.
* AUDITABLE. Every mapping that is not pure lowercase/whitespace is recorded with the
  rule that produced it, so `normalization_provenance` can be inspected.
* CONSERVATIVE BY DEFAULT. `ingredient_canonical` (used for the required Q2/Q3 outputs)
  merges only morphological variants and an explicit curated synonym table. It keeps
  `red onion` distinct from `onion`. The aggressive head-noun grouping lives in
  `ingredient_family` and is used for extension analysis only.
"""
from __future__ import annotations
import re, unicodedata

# ---------------------------------------------------------------- vocabularies

# Descriptor / preparation words stripped from the EDGES of a name span only.
PREP_WORDS = {
    "chopped", "finely", "roughly", "coarsely", "thinly", "thickly", "sliced", "diced",
    "minced", "grated", "shredded", "crushed", "peeled", "deseeded", "seeded", "cored",
    "trimmed", "halved", "quartered", "cubed", "crumbled", "mashed", "beaten", "whisked",
    "melted", "softened", "chilled", "cooled", "warmed", "drained", "rinsed", "washed",
    "picked", "torn", "shaved", "zested", "juiced", "squeezed", "pitted", "stoned",
    "podded", "shelled", "skinned", "boned", "butterflied", "scored", "toasted",
    "roasted", "cooked", "raw", "fresh", "freshly", "dried", "frozen", "tinned",
    "canned", "ground", "whole", "large", "small", "medium", "big", "little", "ripe",
    "unripe", "good", "quality", "best", "plus", "extra", "optional", "level", "heaped",
    "packed", "loosely", "firmly", "cut", "into", "chunks", "pieces", "sticks",
    "matchsticks", "wedges", "strips", "rings", "batons", "florets", "lengths",
    "removed", "reserved", "separated", "sifted", "sieved", "stirred", "mixed",
    "diagonally", "lengthways", "crossways", "roughly-chopped", "chopped-up",
}

# Container / measure nouns that leak into a NAME span on BBC phrasing
# (e.g. "400g can chopped tomatoes", "250g pack dried lasagne sheets").
CONTAINER_WORDS = {
    "can", "cans", "tin", "tins", "jar", "jars", "pack", "packs", "packet", "packets",
    "bunch", "bunches", "handful", "handfuls", "pinch", "pinches", "sprig", "sprigs",
    "clove", "cloves", "stick", "sticks", "slice", "slices", "rasher", "rashers",
    "bag", "bags", "bottle", "bottles", "tub", "tubs", "box", "boxes", "punnet",
    "sheet", "sheets", "ball", "balls", "block", "blocks", "head", "heads",
    "scoop", "scoops", "drizzle", "splash", "glug", "knob", "dash", "squeeze",
    "pot", "pots", "bar", "bars", "side", "piece", "pieces", "tube", "tubes",
    "carton", "cartons", "sachet", "sachets", "bulb", "bulbs", "quantity",
}

# Measurement units. The NER NAME span should not contain these, but strip
# defensively in case of a boundary error (e.g. "400g can chopped tomatoes").
UNIT_WORDS = {
    "g", "kg", "mg", "ml", "l", "cl", "dl", "oz", "lb", "lbs", "tsp", "tbsp", "tblsp",
    "teaspoon", "teaspoons", "tablespoon", "tablespoons", "cup", "cups", "pint", "pints",
    "quart", "quarts", "gallon", "gallons", "litre", "litres", "liter", "liters",
    "gram", "grams", "gramme", "grammes", "kilo", "kilos", "kilogram", "kilograms",
    "ounce", "ounces", "pound", "pounds", "inch", "inches", "cm", "mm",
}

STOP_EDGE = {"of", "the", "a", "an", "to", "for", "or", "and", "in", "on", "with",
             "about", "such", "as", "each", "few", "couple", "some", "any", "your",
             "our", "my", "use", "used", "we", "i", "you", "if", "see", "tip", "below",
             "taste", "serve", "serving", "garnish", "decorate", "dust", "dusting",
             "then", "either", "bought", "homemade", "etc", "also", "well", "works",
             "work", "left", "whole", "plus", "extra", "more", "less", "than",
             "but", "so", "very", "quite", "just", "only", "same", "other", "another",
             "this", "that", "these", "those", "one", "two", "three", "four", "five",
             "here", "there", "when", "while", "before", "after", "until", "ideally",
             "preferably", "roughly", "approx", "instructions", "instruction"}

# Words that must never be returned alone as an "ingredient".
NOT_INGREDIENTS = STOP_EDGE | CONTAINER_WORDS | PREP_WORDS | UNIT_WORDS | {
    "", "etc", "plus", "more", "less", "half", "quarter", "third", "piece", "pieces",
    "mixture", "mix", "amount", "size", "sized", "temperature", "room", "instructions",
    "instruction", "brand", "brands", "vary", "prefer", "preferred", "needed", "need",
    "required", "approx", "approximately", "roughly", "around", "per", "person",
    "people", "portion", "portions", "total", "weight", "thick", "thin", "long", "wide",
}

# Plurals that must NOT be de-pluralised (word ends in -s but is singular).
NO_SINGULARIZE = {
    "molasses", "watercress", "cress", "couscous", "hummus", "houmous", "asparagus",
    "swiss", "bass", "grass", "lemongrass", "peas", "greens", "oats", "grits",
    "gooseberries", "chips", "crisps", "sprouts", "brussels", "capers", "sultanas",
    "breadcrumbs", "cornflakes", "noodles", "pickles", "berries", "olives",
    "juice", "cheese", "mousse", "sauce", "mince", "rice", "molasse", "harissa",
}

# Curated synonym / variant table  (surface -> canonical).  Auditable and explicit.
SYNONYMS = {
    "scallion": "spring onion", "scallions": "spring onion", "green onion": "spring onion",
    "spring onions": "spring onion",
    "corn flour": "cornflour", "corn starch": "cornflour", "cornstarch": "cornflour",
    "bicarbonate of soda": "bicarbonate of soda", "baking soda": "bicarbonate of soda",
    "caster sugar": "caster sugar", "castor sugar": "caster sugar",
    "icing sugar": "icing sugar", "confectioners sugar": "icing sugar",
    "plain flour": "plain flour", "all-purpose flour": "plain flour",
    "all purpose flour": "plain flour",
    "aubergines": "aubergine", "eggplant": "aubergine",
    "courgettes": "courgette", "zucchini": "courgette",
    "coriander leaves": "coriander", "fresh coriander": "coriander", "cilantro": "coriander",
    "chile": "chilli", "chili": "chilli", "chilies": "chilli", "chillies": "chilli",
    "chilli pepper": "chilli", "red chillies": "red chilli",
    "prawns": "prawn", "shrimp": "prawn",
    "rocket": "rocket", "arugula": "rocket",
    "mangetout": "mangetout", "snow pea": "mangetout", "snow peas": "mangetout",
    "double cream": "double cream", "heavy cream": "double cream",
    "single cream": "single cream", "light cream": "single cream",
    "natural yogurt": "natural yogurt", "plain yogurt": "natural yogurt",
    "yoghurt": "yogurt", "greek yoghurt": "greek yogurt",
    "tomato puree": "tomato purée", "tomato paste": "tomato purée",
    "beef mince": "minced beef", "mince beef": "minced beef", "ground beef": "minced beef",
    "olive oil extra virgin": "extra virgin olive oil",
    "sunflower oil": "sunflower oil", "vegetable oil": "vegetable oil",
    "sea salt": "salt", "table salt": "salt", "flaky sea salt": "salt",
    "salt and pepper": "salt", "freshly ground black pepper": "black pepper",
    "ground black pepper": "black pepper", "black peppercorns": "black pepper",
    "unsalted butter": "butter", "salted butter": "butter",
    "self raising flour": "self-raising flour", "self-raising flour": "self-raising flour",
    "egg": "egg", "eggs": "egg", "free-range egg": "egg", "free range egg": "egg",
    "garlic clove": "garlic", "garlic cloves": "garlic",
    "streaky bacon": "bacon", "back bacon": "bacon",
    "chicken breasts": "chicken breast", "chicken thighs": "chicken thigh",
    "stock cube": "stock", "chicken stock cube": "chicken stock",
}

# Multiword ingredients whose head noun must NOT absorb them at the family level.
PROTECTED_COMPOUNDS = {
    "coconut milk", "coconut cream", "coconut oil", "coconut water", "almond milk",
    "soy milk", "soya milk", "oat milk", "rice milk", "condensed milk", "evaporated milk",
    "buttermilk", "peanut butter", "almond butter", "nut butter", "cocoa butter",
    "rice vinegar", "wine vinegar", "cider vinegar", "balsamic vinegar", "malt vinegar",
    "sherry vinegar", "rice wine", "soy sauce", "fish sauce", "worcestershire sauce",
    "oyster sauce", "hot sauce", "tomato sauce", "olive oil", "sesame oil",
    "sunflower oil", "rapeseed oil", "vegetable oil", "groundnut oil", "truffle oil",
    "cream cheese", "goat cheese", "goats cheese", "blue cheese", "cottage cheese",
    "sour cream", "double cream", "single cream", "clotted cream", "ice cream",
    "baking powder", "chilli powder", "curry powder", "cocoa powder", "garlic powder",
    "onion powder", "mustard powder", "custard powder", "vanilla extract",
    "almond extract", "lemon juice", "lime juice", "orange juice", "apple juice",
    "spring onion", "red onion", "white onion", "black pepper", "white pepper",
    "cayenne pepper", "bell pepper", "red pepper", "green pepper", "yellow pepper",
    "brown sugar", "caster sugar", "icing sugar", "palm sugar", "vanilla sugar",
    "chicken stock", "beef stock", "vegetable stock", "fish stock",
    "olive tapenade", "tomato purée", "sesame seeds", "poppy seeds", "chia seeds",
    "green beans", "broad beans", "black beans", "kidney beans", "baked beans",
    "sweet potato", "new potato", "potato flour", "corn flour", "rice flour",
    "almond flour", "plain flour", "self-raising flour", "strong white flour",
    "bay leaf", "curry leaf", "lime leaf", "vine leaf", "gelatine leaf",
    "dark chocolate", "milk chocolate", "white chocolate", "chocolate chips",
    # --- modifier+base pairs where the leading modifier IS part of the product
    # identity, added after an audit showed the edge-stripper was destroying them
    # (e.g. "whole milk" -> "milk", "extra virgin olive oil" -> "virgin olive oil").
    # Deliberately small and explicit so every merge decision stays auditable.
    "whole milk", "semi-skimmed milk", "skimmed milk", "full-fat milk",
    "light brown sugar", "dark brown sugar", "light muscovado sugar",
    "dark muscovado sugar", "light soft brown sugar", "dark soft brown sugar",
    "light brown soft sugar", "demerara sugar", "golden caster sugar",
    "light soy sauce", "dark soy sauce",
    "extra virgin olive oil", "extra-virgin olive oil", "light olive oil",
    "mustard oil", "light cream cheese", "full-fat cream cheese",
    "gram flour", "chickpea flour", "wholemeal flour", "spelt flour",
    "hot smoked salmon", "cold smoked salmon", "smoked salmon",
    "fresh yeast", "dried yeast", "fast-action dried yeast",
    "ground almonds", "whole almonds", "flaked almonds",
    "smoked paprika", "sweet paprika", "smoked bacon",
}

# Hyphen-insensitive lookup for the guard above: "semi-skimmed milk" and
# "semi skimmed milk" must both resolve, and the LONGEST match must win.
_PROTECTED_NOHYPHEN = {c.replace("-", " "): c for c in
                       sorted(PROTECTED_COMPOUNDS, key=lambda x: len(x.split()))}

_FRAC = {"½": " 1/2 ", "¼": " 1/4 ", "¾": " 3/4 ", "⅓": " 1/3 ", "⅔": " 2/3 ",
         "⅛": " 1/8 ", "⅜": " 3/8 ", "⅝": " 5/8 ", "⅞": " 7/8 ", "⅕": " 1/5 "}


# ---------------------------------------------------------------- primitives
def strip_accents_keep(s: str) -> str:
    """NFKC-normalise but keep é/ü etc (purée, jalapeño stay intact)."""
    return unicodedata.normalize("NFKC", s)


def basic_clean(s: str) -> str:
    s = strip_accents_keep(s)
    for k, v in _FRAC.items():
        s = s.replace(k, v)
    s = re.sub(r"\([^)]*\)", " ", s)          # drop parenthetical notes
    s = s.replace("®", " ").replace("™", " ")
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"[^a-zA-ZÀ-ſ'\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def singularize(w: str) -> str:
    if w in NO_SINGULARIZE or len(w) <= 3:
        return w
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith(("ches", "shes", "sses", "xes", "zes")):
        return w[:-2]
    if w.endswith("oes") and len(w) > 4:
        return w[:-2]
    if w.endswith("ves") and len(w) > 4:
        return w[:-3] + "f"          # loaves -> loaf, halves -> half(ish)
    if w.endswith("s") and not w.endswith(("ss", "us", "is")):
        return w[:-1]
    return w


def normalize_surface(span: str) -> tuple[str | None, list[str]]:
    """
    Clean a NER NAME span into `ingredient_normalized`.
    Returns (normalized_or_None, provenance_rules_applied).
    """
    prov: list[str] = []
    s = basic_clean(span)
    if not s:
        return None, ["empty_after_clean"]

    # PROTECTED-COMPOUND GUARD (added in the repair pass).
    # If the cleaned span ends in a known protected compound, return that compound
    # untouched. Without this the edge-stripper removed leading modifiers that are
    # part of the product's identity: "whole milk" -> "milk", "light brown sugar"
    # -> "brown sugar", "extra virgin olive oil" -> "virgin olive oil" (a form that
    # does not even exist), "gram flour" -> "flour" ("gram" is also a unit word).
    # Longest suffix wins, so "extra virgin olive oil" beats "olive oil".
    _t = s.replace("-", " ").split()
    for _i in range(len(_t)):
        _cand = " ".join(_t[_i:])
        if _cand in _PROTECTED_NOHYPHEN:
            return _PROTECTED_NOHYPHEN[_cand], ["protected_compound"]
    if s != span.strip().lower():
        prov.append("basic_clean")

    toks = s.split()
    # strip container words anywhere (they are never the ingredient)
    t2 = [w for w in toks if w not in CONTAINER_WORDS and w not in UNIT_WORDS
          and len(w) > 1]
    if len(t2) != len(toks):
        prov.append("strip_container_unit")
    if not t2:
        # the span was nothing but container/unit words ("pack cup") - not an ingredient
        return None, prov + ["only_container_unit_words"]
    toks = t2

    # strip prep/descriptor & stopwords from the EDGES only (never mid-phrase)
    changed = True
    while changed and toks:
        changed = False
        while toks and (toks[0] in PREP_WORDS or toks[0] in STOP_EDGE):
            toks.pop(0); changed = True; prov.append("strip_edge_left")
        while toks and (toks[-1] in PREP_WORDS or toks[-1] in STOP_EDGE):
            toks.pop(); changed = True; prov.append("strip_edge_right")
    if not toks:
        return None, prov + ["all_tokens_stripped"]

    toks = [singularize(w) for w in toks]
    prov.append("singularize")
    out = " ".join(toks).strip(" -'")
    if not out or out in NOT_INGREDIENTS or len(out) < 2:
        return None, prov + ["rejected_not_ingredient"]
    return out, sorted(set(prov))


def canonicalize(normalized: str) -> tuple[str, list[str]]:
    """Apply the curated synonym table. Conservative: keeps `red onion` != `onion`."""
    if normalized in SYNONYMS:
        return SYNONYMS[normalized], ["synonym_table"]
    sing = " ".join(singularize(w) for w in normalized.split())
    if sing in SYNONYMS:
        return SYNONYMS[sing], ["synonym_table_singular"]
    return normalized, []


def family(canonical: str) -> tuple[str, list[str]]:
    """
    EXTENSION ONLY. Aggressive head-noun grouping (`red onion` -> `onion`),
    guarded by PROTECTED_COMPOUNDS so `coconut milk` / `rice vinegar` never collapse.
    """
    if canonical in PROTECTED_COMPOUNDS:
        return canonical, ["protected_compound"]
    toks = canonical.split()
    if len(toks) == 1:
        return canonical, []
    # a compound whose *suffix* is protected also stays intact
    for i in range(len(toks)):
        if " ".join(toks[i:]) in PROTECTED_COMPOUNDS:
            return " ".join(toks[i:]), ["protected_suffix"]
    head = toks[-1]
    if head in NOT_INGREDIENTS or len(head) < 3:
        return canonical, ["head_rejected"]
    return head, ["head_noun"]


# ---------------------------------------------------------------- span trimming
# Cues at which a NER NAME span has over-run into non-ingredient text.
# Derived from error analysis round 1 (outputs/extensions/ner_error_analysis.json).
_TRIM_AT = re.compile(
    r"\b(?:made\s+with|such\s+as|weighing|soaked|blended|topped|either|bought|"
    r"depending|following|broken\s+into|cut\s+in|cut\s+into|torn\s+into|"
    r"crumble|squeezed|stripped|reserved|removed|about)\b", re.I)
# Trailing prepositional tails: "anchovies in oil", "tuna in brine", "peaches in syrup"
_TRIM_TAIL = re.compile(r"\s+(?:in|from|for|on|at|by|to)\s+.*$", re.I)
# Plant-part suffixes that are not part of the ingredient identity, unless the
# whole compound is a protected one (bay leaf, curry leaf, lime leaf...).
_PART_SUFFIX = ("leaves", "leaf", "stems", "stem", "stalks", "stalk",
                "sprigs", "sprig", "crusts", "crust", "tops", "fronds")

# Descriptor adjectives that precede the true ingredient name and are not part of it.
LEAD_QUALIFIERS = {
    "hot", "mild", "fortified", "unsweetened", "sweetened", "reduced-fat", "low-fat",
    "full-fat", "half-fat", "fat-free", "light", "extra-thick", "organic", "free-range",
    "free", "range", "skinless", "boneless", "bone-in", "baby", "back", "stale",
    "slightly", "assorted", "mixed-up", "ready-roasted", "pre-baked", "leftover",
    "cold", "hot", "warm", "lukewarm", "room", "best-quality", "good-quality",
    "value", "economy", "budget", "posh", "fancy", "everyday", "basic",
    "steamed", "thick", "thin", "soft", "neutral", "tart", "crustless", "rounded",
}


def preprocess_phrase(phrase: str) -> str:
    """
    Applied to a raw ingredient phrase BEFORE entity extraction.

    Parenthetical text on BBC Good Food is almost always an editorial aside
    ("(optional)", "(we used puy lentils)", "(see tip, below)", "(3-4 medium
    beets)") rather than an additional ingredient. Error analysis round 2 showed
    it was the single largest source of spurious ingredient mentions, so it is
    removed up front for every extractor alike (NER and rule baseline), keeping
    the comparison fair. The raw phrase itself is never modified on disk.
    """
    return re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", " ", phrase)).strip()


def trim_span(span: str) -> str:
    """Repair an over-long NER NAME span before normalisation. Never extends a span."""
    parts = [x.strip(" ,;:-") for x in _TRIM_AT.split(span)]
    # a cue at the very start leaves an empty head - fall through to the next segment
    s = next((x for x in parts if x), span).strip(" ,;:-")
    low = s.lower().strip()
    # keep protected compounds exactly as they are
    if low in PROTECTED_COMPOUNDS:
        return s
    if _TRIM_TAIL.search(s):
        cand = _TRIM_TAIL.sub("", s).strip(" ,;:-")
        if cand and cand.lower() not in NOT_INGREDIENTS and len(cand.split()) >= 1:
            s = cand
    toks = s.split()
    # strip plant-part suffix unless the compound is protected
    while len(toks) > 1 and toks[-1].lower().strip(",") in _PART_SUFFIX:
        if " ".join(w.lower() for w in toks) in PROTECTED_COMPOUNDS:
            break
        toks.pop()
    # strip leading qualifier adjectives
    while len(toks) > 1 and toks[0].lower() in LEAD_QUALIFIERS:
        if " ".join(w.lower() for w in toks) in PROTECTED_COMPOUNDS:
            break
        toks.pop(0)
    return " ".join(toks).strip(" ,;:-") or span
