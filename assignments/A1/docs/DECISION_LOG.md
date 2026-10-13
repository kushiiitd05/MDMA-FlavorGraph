# Decision Log — CGAS / BIO544 Assignment 1

Concise record of every non-obvious choice: decision, alternatives, reason, evidence,
assumptions, consequence. Written *before/while* implementing, not retro-fitted.

---

## D1 — Recipe source: **BBC Good Food** (`bbcgoodfood.com`)

**Decision.** Scrape BBC Good Food recipe pages via its XML sitemaps.

**Alternatives considered & why rejected (all audited empirically, `robots.txt` fetched 2026-09-08):**

| Candidate | Finding | Verdict |
|---|---|---|
| RecipeDB | **Forbidden by the assignment.** | Excluded by rule |
| allrecipes.com, seriouseats.com, simplyrecipes.com | `robots.txt` carries a People Inc. notice: *"Use of any crawler … to data mine or scrape the content … is prohibited"*, and explicitly bars *"creating data sets containing People Inc. content"* | Rejected — ToS prohibits |
| taste.com.au | `robots.txt`: *"Collection of content … through automated means is prohibited unless you have express written permission"* | Rejected — ToS prohibits |
| tarladalal.com | Cloudflare returns "Sorry, you have been blocked" on `robots.txt` | Rejected — inaccessible |
| epicurious.com | Sample recipe URL returned HTTP 404; smaller/less consistent inventory | Rejected — unreliable |
| food.com | `User-agent: *` permits `/recipe/`; ~360 000 recipes. **But `recipeCuisine` is `null`** in its JSON-LD | Viable fallback; rejected as primary (no cuisine metadata) |
| vegrecipesofindia / hebbarskitchen | Permissive robots but only ~1–3 k recipes each | Too small for 10 000 |
| **bbcgoodfood.com** | `User-agent: *` → `Allow: /`; `/recipes/` not disallowed; 17 428 unique recipe URLs; complete schema.org JSON-LD | **Selected** |

**Evidence.** A seeded 60-URL random probe returned **60/60 HTTP 200 with a parsable
`Recipe` JSON-LD node** (median latency 0.70 s). Field coverage on that probe:
`recipeIngredient` 100 %, `recipeInstructions` 100 %, `nutrition` 97 %,
`recipeCategory` 97 %, `totalTime` 98 %, `recipeCuisine` **38 %**.

**Compliance notes.** `robots.txt` `User-agent: *` allows the recipe paths; the crawler
honours it programmatically (`urllib.robotparser`) before discovery starts. The site sets
`Content-signal: ai-train=no` — this corpus is used for **descriptive statistical
coursework analysis only**, not for training or fine-tuning any model, so that signal is
respected. Crawl is rate-limited (4 workers, ~0.6 s/worker delay, ≈3 rec/s) with
exponential backoff on 429/5xx.

**Assumption.** 17 428 URLs × ~100 % parse success comfortably exceeds the 10 000 target.

**Consequence.** Cuisine analysis is possible but only on the ~38 % of recipes that carry
a label; every cuisine statistic must report its own `N_c`. Cuisine is an **extension**,
never a rubric item.

---

## D2 — URL sampling policy: seeded uniform random sample

**Decision.** Draw 12 000 URLs uniformly at random *without replacement* from the
17 428-URL universe, `seed = 20260908`.

**Alternatives.** (a) Sequential sitemap walk — rejected: BBC sitemaps are grouped by
publication quarter, so the first 12 000 URLs would over-represent one era.
(b) Cuisine-stratified sampling with a per-cuisine cap — rejected: only 38 % of recipes
carry a cuisine label, so stratification is undefined for the majority, and the master
brief forbids artificially balancing cuisines without an analytical reason.

**Consequence.** The corpus is an unbiased random sample of BBC Good Food's recipe
inventory; `recipe_cuisine_raw` is preserved verbatim and its natural distribution is
reported as observed.

---

## D3 — Extraction hierarchy: JSON-LD first, HTML-selector fallback

**Decision.** `requests` → HTML → BeautifulSoup → `<script type="application/ld+json">`
→ locate the `@type: Recipe` node → fall back to CSS selectors only if that fails.

**Reason.** The HTTP response is an **HTML document**, not JSON; the structured recipe
data is embedded inside it as schema.org JSON-LD. Verified directly on sample pages.
JSON-LD is publisher-maintained and far more stable than CSS class names.

**Consequence.** `extraction_method` is recorded per record (`jsonld`,
`jsonld+html_fallback`, `html_fallback`) so provenance is auditable.

---

## D4 — Raw layer is immutable

`data/raw/recipes_raw.jsonl` stores the complete record **including the verbatim
`raw_jsonld` document**. No NER or normalisation output is ever written back into it.
Layering: `RAW → NER spans → normalised surface → canonical ingredient`, each preserved
in its own column/file. Missing fields are `null`; nothing is imputed.

---

## D5 — NER approach: spaCy NER trained on **TASTEset**

**Decision.** Train a spaCy NER model on TASTEset (github.com/taisti/TASTEset, **MIT
licence**), and use its `NAME` entity as the Q1(b) ingredient-name extractor.

**Reason / evidence.** Diwan, Batra & Bagler, *"Deep Learning Based Named Entity
Recognition Models for Recipes"* (arXiv:2402.17447 — from the group that runs this course)
compared Stanford NER, flair, BERT and spaCy-transformer on recipe ingredient phrases and
found **spaCy-transformer best (95.9 % macro-F1)**, ahead of Stanford NER (95.5 %),
flair (95.0 %) and BERT (94.0 %). Their tag set is `NAME / QUANTITY / UNIT / STATE /
SIZE / TEMP / DF`. **Their training data is RecipeDB-derived, which this assignment
forbids**, so TASTEset is used instead as an independent, openly-licensed substitute
(700 annotated ingredient blocks → 3 766 individual labelled phrases).

**Tag mapping.** `FOOD→NAME`, `QUANTITY→QUANTITY`, `UNIT→UNIT`,
`PROCESS→STATE`, `PHYSICAL_QUALITY→STATE`; `COLOR/TASTE/PURPOSE/PART` dropped (sparse).

**Assumption & its mitigation.** TASTEset is US-English; BBC Good Food is UK-English
("rashers", "double cream", "coriander"). This domain shift is *measured*, not assumed
away: a human-checked gold set drawn from **our own scraped corpus** is used for the
decisive evaluation.

---

## D6 — Frozen statistical definitions

| Quantity | Definition | Note |
|---|---|---|
| Ingredient frequency `f_i` | `#{R : i ∈ R}` — number of **distinct recipes** containing canonical ingredient `i` | An ingredient appearing twice in one recipe counts once. `mention_frequency` computed separately, never mixed in. |
| Recipe size `s_R` | number of **unique canonical ingredients** in recipe `R` | Raw ingredient-line count kept separately for diagnostics. |
| Mean `μ_s` | `(1/N) Σ_R s_R` | Computed over all recipes directly, never by averaging cuisine means. |
| CDF | `F(s) = P(S ≤ s)` | The primary Q2(c) deliverable. |
| CCDF | `F̄(s) = P(S ≥ s)` | Supplementary, explicitly labelled as such. |
| Rank | **Competition ranking** ("1224"): tied frequencies share the minimum rank | Ties broken for *display order only* by alphabetical name; no invented "importance" score. |

---

## D7 — Distributional claims

Recipe-size normality is **not** assumed; the empirical distribution is plotted and its
skew/kurtosis reported. Any normal overlay is labelled as a diagnostic fit, not data.
For frequency–rank, log–log linearity alone is **not** treated as evidence of Zipf/power
law; the plot is presented descriptively.

---

## D8 — Model selection was decided by measurement, not assumption

A 206-phrase gold set was drawn from **our own scraped corpus** (150 uniform-random +
56 deliberately hard: parentheticals, ranges, unicode fractions, alternations, compound
names, quantity-less lines, very long lines) and hand-annotated. Two metrics were scored:
**surface-set** F1 (did it find the right strings) and **canonical-set** F1 (did the
recipe end up with the right ingredient set) — the latter is decisive because it is what
Q1(c)/Q2/Q3 actually depend on.

| Approach | surface F1 | **canonical F1** | exact-set acc. |
|---|---|---|---|
| **hybrid: transformer NER + rule fallback** | 0.758 | **0.893** | 0.869 |
| spaCy transformer NER (distilroberta, TASTEset) | 0.755 | 0.890 | 0.864 |
| hybrid: CNN NER + rule fallback | 0.645 | 0.873 | 0.850 |
| hybrid: CNN NER + local-LLM fallback | 0.654 | 0.873 | 0.850 |
| local LLM (qwen2.5:3b via Ollama, JSON-constrained) | 0.665 | 0.867 | 0.859 |
| spaCy CNN NER (tok2vec + `en_core_web_lg`, TASTEset) | 0.636 | 0.858 | 0.825 |
| rule/dictionary baseline (control) | 0.643 | 0.846 | 0.830 |

**Chosen: hybrid transformer NER + rule fallback.** Consequences:
1. The ordering **transformer > CNN > rules** independently reproduces the finding of
   arXiv:2402.17447 that spaCy-transformer is the strongest recipe-NER architecture.
2. Every NER variant beats the rule-only control, so the NER component **earns its place**
   rather than being included because the rubric names it.
3. **The local LLM did NOT win.** Ollama *was* installed and benchmarked (Apple M5, Metal,
   qwen2.5:3b, `format:json`, temperature 0, a system prompt forbidding invention). It
   scored **0.867 canonical F1 — below the transformer's 0.890** — while costing
   **1.35 s/phrase**, i.e. **≈45 h for the ~120 000 ingredient phrases** in this corpus,
   versus ~10 min for the spaCy pipeline. Using it as a fallback behind the CNN changed
   the canonical F1 by **0.000**. It is therefore **benchmarked and rejected for bulk
   extraction** on measured accuracy *and* cost — not assumed either way.
   Evidence: `outputs/extensions/ner_evaluation.json`, `outputs/extensions/llm_runtime.json`.

---

## D9 — Post-NER sanity gate (brief §50)

Round-2 error analysis showed the residual failure mode was **over-long NER spans**
("pork loin steak trimmed of fat", "beef fillet ask your butcher") and **editorial
parentheticals** ("(we used puy lentils)", "(3-4 medium beets)") leaking in as spurious
ingredients. Three fixes, applied identically to every extractor so the comparison stays fair:

1. `preprocess_phrase()` — strip parenthetical asides before extraction. **Canonical F1
   0.840 → 0.880.**
2. `split_enumeration()` — "poppy seed and sesame seed" becomes two names.
3. `validate_batch()` — a mostly *grammatical* gate: ≤4 tokens, must contain a NOUN/PROPN,
   must not open with DET/ADP/PRON/CCONJ, no residual conjunction, not a bare part-word
   ("zest", "half").

Two deliberate design choices, both forced by auditing what the gate actually removed:

* **Tag the name inside a carrier sentence, never bare.** A first version tagged the
  candidate name on its own and rejected anything with no NOUN/PROPN. Auditing the
  rejection file showed it was deleting **`avocado`, `panko`, `risotto`, `haggis`,
  `pectin`, `chicory`** — spaCy reads a bare one-word noun phrase as an *imperative
  VERB*. Tagging `"I added the {name} to the pan."` and reading the POS of the inner
  span fixes every one of these. Rejected names fell **511 → 212** and ~**8 500
  genuine ingredient mentions were recovered**.
* **Test the opening word on whitespace tokens, not spaCy tokens.** spaCy splits
  `all-butter` into `all`/DET + `-` + `butter`, so a POS-based "starts with a
  determiner" rule condemned **`all-butter shortcrust pastry`**, `all-bran`,
  `after-dinner mint`, `no-soak prune`. A plain string test on the first
  whitespace-delimited token keeps them.
* `with`/`plus` are **not** treated as enumeration markers — they occur in genuine
  product names (`passata with onion`, `tomato with basil`). Only `and`/`or` are.

Every rejected string is written to `outputs/extensions/rejected_ingredient_names.csv`
with its reason — nothing is dropped silently. Final gate rejections: 212 of 6 977
candidate names (2 641 of 125 658 mentions, 2.1 %).

Earlier round-1 fix, for the record: TASTEset annotates `COLOR` and `PART` as entities
*separate* from `FOOD`, so an unmapped model returned "chilli" for "red chilli" and
"chicken" for "chicken breast". Mapping `COLOR`/`PART` → `NAME` and merging adjacent NAME
spans (265 merges) lifted canonical F1 from **0.751 → 0.840**.

---

## D10 — Repair pass (post-audit)

`docs/AUDIT.md` verified the Q1–Q3 path against the actual files and found it correct,
but identified real defects in the ingredient/process **extension**. Repairs below.
The required rubric path was not redesigned; the corpus was not re-scraped and the NER
model was not retrained.

### R1 — the state filter was wrong for its purpose *(the main defect)*

`extensions.py` filtered states with `PREP_WORDS`, a list written for stripping
descriptor words off the **edges of a NAME span**. Used as a semantic filter it made
exactly the wrong cut:

| | before |
|---|---|
| **discarded** | `fried`, `boiled`, `caramelised`, `grilled`, `baked`, `steamed`, `smoked` (865 mentions) — **15 of 17** cooking transformations |
| **kept as "process states"** | `large` (3,782 mentions), `small`, `medium` |

Replaced by `src/normalization/state_taxonomy.py`: an **observed-only** taxonomy
(PREPARATION / COOKING / QUALITY / SIZE, plus NOT_A_STATE and UNCLASSIFIED),
classified by **head word** so "finely chopped", "roughly chopped" and "very finely
chopped" all resolve through `chopped`. The vocabulary was read off the corpus's own
top observed states, not imported from an external ontology. Genuinely ambiguous words
(`ground`, `smoked`, `melted`, `whole`) are flagged `category_is_ambiguous` rather than
being asserted with false confidence. **After: 3,780 COOKING observations retained
(previously ~0).** Nothing is silently dropped — NOT_A_STATE and UNCLASSIFIED rows are
still written to `ingredient_process_states.csv`.

### R2 — canonicalisation destroyed product identity

The edge-stripper removed leading modifiers that *are* the product's identity:
`whole milk`→`milk`, `light brown sugar`→`brown sugar`, `gram flour`→`flour` ("gram" is
also a unit word), and `extra virgin olive oil`→`virgin olive oil` — a form that does not
exist. It was also asymmetric: `dark brown sugar` survived while `light brown sugar` did not.

Two fixes: (a) a **protected-compound guard** in `normalize_surface()` that returns the
longest matching protected compound untouched, hyphen-insensitively; (b)
`expand_protected()` in `extract_ingredients.py`, which grows a NAME span leftwards
**only** when doing so completes an explicitly listed compound — so it can never invent a
longer name. `sunflower oil`, `mustard oil`, `olive oil`, `sesame oil`, `coconut milk`,
`rice vinegar`, `almond flour`, `gram flour`, `sweet potato` all remain distinct
canonical ingredients; none collapses to a bare parent.

### R3 — states attached to the wrong ingredient

Every STATE span in a line was copied onto **every** NAME in that line. Now the line is
split at coordination boundaries (`,` `;` `and` `or`) and each modifier attaches to the
NAME in its own segment, falling back to the nearest preceding NAME.
A line with a single NAME still receives all modifiers, so `peeled and chopped potatoes`
correctly keeps both. Verified: `chopped onions and diced tomatoes` →
`onion + chopped`, `tomato + diced`. Quantity and unit now attach by the same rule
instead of the first span winning for every ingredient.

### R4 — instruction ingredient matching

Matching used the **last token** of each canonical name, so a step saying
"sunflower oil" resolved to *every* oil in the recipe. Replaced with longest-phrase
matching over consumed character spans, plus a head-noun fallback allowed **only** when
exactly one ingredient in that recipe has the head noun. Ambiguous bare "oil" with two
oils present now returns nothing rather than guessing.

### R5 — gold-set reproducibility

The 150+56 sampling ran inline and was never committed. Recovered as
`src/ner/build_gold_set.py`. The gold set was drawn mid-crawl; the snapshot size was
identified by matching the eight stratum pool sizes in the original run log — all eight
match at **N = 1502 records**, and `--check` confirms the rebuild reproduces the committed
206 candidates exactly.

### R6 — frequency definitions kept distinct

`state_frequency_by_category.csv` reports `mention_count` **and** `recipe_count` side by
side with the denominator named (`ingredient_recipe_frequency`). The asserted invariant is
`recipe_count(i,s) ≤ recipe_freq(i)`. We deliberately do **not** assert
`Σ_s recipe_count(i,s) = recipe_freq(i)`, because one mention can carry several states
("large fresh chopped onions" → SIZE + QUALITY + PREPARATION), so the categories are
neither mutually exclusive nor exhaustive.

### Effect on the required Q1–Q3 outputs — small, as intended

| | before | after |
|---|---|---|
| recipes (N) | 11,934 | **11,934** (unchanged) |
| unique canonical ingredients | 6,765 | 6,614 |
| mean recipe size | 9.933 | 9.950 |
| SD | 4.111 | 4.119 |
| median / skewness | 9 / 0.792 | 9 / 0.783 |
| NER canonical F1 (best) | 0.8927 | 0.8946 |
| exact-set accuracy | 0.8689 | 0.8689 (unchanged) |
| validation checks | 38/38 | **41/41** (3 state-layer checks added) |

The F1 change (**+0.0019**) is one extra true positive on 206 phrases and is **not
statistically meaningful** — the repair was made for correctness, not for the metric.

---

## D11 — "A **or** B" is one ingredient slot, not two

**Problem found.** `split_enumeration` treated `and` and `or` identically, so
`6 tbsp light olive oil or sunflower oil` produced **two** ingredients. Measured:
**4,617 ingredient lines are alternations**, creating **4,989 spurious mentions**
(4.1% inflation) and affecting **29.4% of all recipes**. This inflated recipe size
(Q2b), ingredient frequency (Q2a) and the rank plot (Q3).

**Decision (user-confirmed).** For the REQUIRED Q1(c)/Q2/Q3 outputs an alternation
contributes **one** ingredient — the **primary** (first) branch — because a cook makes
one choice, so recipe size should describe the dish as actually cooked. Every
alternative is still written to `ingredient_mentions.csv` with `alternative_group` and
`is_primary_alternative`, so nothing is lost and the convention is auditable.

**Implementation.** `alternative_groups()` in `extract_ingredients.py`: two consecutive
NAME spans are alternatives when the text between them contains a standalone `or` and
**no** `and`/`,`/`&`. So `salt and pepper` stays two ingredients while
`cavolo nero or kale` becomes one slot with one alternative.

## D12 — the sanity gate was deleting real ingredients

Three separate defects, each found by reading `rejected_ingredient_names.csv`:

1. **G2 vs. bare food nouns.** `en_core_web_sm` tags isolated lowercase food words as
   ADJ/VERB. The existing carrier-sentence trick ("I added the *X* to the pan") rescues
   many (avocado, panko, risotto) but **not all** — `rosemary`, `couscous`, `houmous`,
   `nougat` and `cannelloni` stay ADJ even inside the carrier. **`rosemary` was being
   deleted from a corpus where it appears in 352 recipes (rank 64).**
   *Fix:* a last-resort corpus-evidence override — if a string appears at least once as
   an **entire ingredient line** (quantity/unit/container words removed), it is a noun.
   Measured on this corpus: all 19 tested true adjectives (`golden`, `double`, `soft`,
   `smoked`, `sweet`, …) score **0**; `rosemary` scores 85 and `couscous` 75. Direct
   corpus evidence beats a generic English tagger on food vocabulary.

2. **Part words had no parent.** `zest`, `juice`, `peel`, `fillet` alone name no
   ingredient and were rejected — but **456 phrases** state the parent explicitly
   ("zest of 1 lemon"). *Fix:* `recover_part_parent()` reconstructs `lemon zest`,
   `lemon juice`, `orange zest`; a bare parent mention from the same phrase is then
   suppressed so `zest of 1 lemon` does not also yield a stray `lemon`.
   **Convention:** a part/cut word **with** a parent is ingredient identity
   (`chicken breast` ≠ `chicken thigh`, `cod fillet`); **alone** it is rejected.
   A cut such as `fillet` is an **anatomical portion, not a SIZE** — it belongs to the
   ingredient's name, never to the state taxonomy.

3. **"all" is a legitimate product prefix.** `all butter shortcrust pastry` and
   `all purpose seasoning` were rejected as clause fragments. *Fix:* `all` disqualifies
   only when the **next** word is also a function word (`all the innard`).

## D13 — heterogeneous connection graph (extension)

`src/graph/` was an empty directory. It now holds a **Cuisine — Recipe — Ingredient —
State** graph. Node types: `cuisine`, `recipe`, `ingredient`, `state`. Edge types:

| edge | meaning |
|---|---|
| `recipe → cuisine` `HAS_CUISINE` | only where the source states one; never inferred |
| `recipe → ingredient` `CONTAINS` | primary alternatives only, identical to Q1(c) |
| `ingredient → state` `HAS_STATE` | **the state is a SUB-PART of its parent ingredient** |
| `recipe → state` `USES_STATE` | which processed form that recipe used |

The `HAS_STATE` edge is the point: `onion::fried` hangs **off** `onion` rather than
competing with it as a top-level node, so the canonical vocabulary that Q1(c)/Q2/Q3 use
stays intact and the states refine it.

Exports: `nodes.csv`, `edges.csv`, `cgas_graph.graphml.gz` (Gephi/Cytoscape) and a
`cuisine × ingredient` projection scored by **lift** = `P(ingredient|cuisine) ÷
P(ingredient)`, so corpus staples such as olive oil never dominate every cuisine.

Two figures. A force-directed layout was tried for the cuisine map and **rejected**:
the cuisines' characteristic-ingredient sets are near-disjoint, so spring layout packed
a dozen disconnected stars into overlapping balls. Deterministic radial small-multiples
are reproducible and legible, which matters more here than looking organic.

Graph identities are asserted in the validation gate (C42–C45), including
`CONTAINS edges == Q1(c) rows` and `HAS_CUISINE == recipes carrying a label`.
**Q1(c)/Q2/Q3 do not depend on the graph.**
