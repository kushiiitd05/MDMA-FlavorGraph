# Technical Audit — CGAS / BIO544 Assignment 1
**Date:** 2026-09-08 · **Method:** every claim below was checked against the actual code,
data files and outputs. Nothing is asserted on the strength of `DECISION_LOG.md` or
`README_SUBMISSION.md` alone. Where a claim failed verification it is marked **DEFECT**.

---

# A. EXECUTIVE VERDICT

**Required rubric (Q1–Q3): CORRECT AND VERIFIED.** All 38 validation checks pass, every
reported number reconciles from raw files, and all descriptive statistics recompute
exactly. Nothing in the graded path is broken.

**Extensions: MOSTLY REAL, BUT ONE IS MATERIALLY WRONG.** The structured layer
(quantity / unit / state) genuinely exists in the output — this is not just a training
label. However the **process-state analysis layer is built on a filter that is wrong for
its purpose**, and the preparation/cooking-transformation taxonomy you asked for does not
exist at all.

**Critical gaps, ranked:**

| # | Gap | Severity |
|---|---|---|
| 1 | State filter reuses `PREP_WORDS`, which **drops** cooking transformations (`fried`, `boiled`, `caramelised`, `grilled`, `baked`, `smoked`) and **keeps** size words (`large` = 3,782 mentions) as if they were process states | **HIGH** — the E1 map is mislabelled |
| 2 | No PREPARATION / COOKING-TRANSFORMATION / PHYSICAL-QUALITY taxonomy | **HIGH** — explicitly requested, absent |
| 3 | STATE spans are attached to **every** NAME in a phrase, not the one they modify | **MEDIUM** — inflates multi-ingredient lines |
| 4 | Gold-set sampling code exists **nowhere in the repo** (was run inline) | **MEDIUM** — reproducibility gap |
| 5 | Quantity / unit / state are **never evaluated** — the 0.893 F1 measures NAME only | **MEDIUM** — accuracy of those fields is unknown |
| 6 | No per-mention `ingredient_process_states.csv`; state frequency is mention-count only, no recipe-frequency | **MEDIUM** |
| 7 | Instruction ingredient matching uses the **last token only** → `olive oil` matches "sunflower **oil**" | **MEDIUM** — false positives |
| 8 | `src/graph/` is an empty directory though README implies a module | **LOW** — cosmetic |
| 9 | LLM cost extrapolated from n=30 to "120,000" phrases; actual corpus is 116,699 | **LOW** — restate as ~44 h |

---

# B. DATASET / SOURCE ANSWERS

## Question A — Were we required to use a particular dataset?

**No.** Verbatim from the assignment PDF:

> "(a) Scrape (using libraries such as BeautifulSoup) any **10,000 recipes**. Submit the raw data."
> "*NOTE: You must NOT scrape/use data from RecipeDB.*"

So the requirement decomposes as:

```
REQUIRED      : 10,000 recipes, scraped, from a source that is NOT RecipeDB
NOT REQUIRED  : BBC Good Food, food.com, or any other named site
```

The word "any" is doing the work. The PDF names exactly one dataset — RecipeDB — and only
to **forbid** it.

## Question B — Is BBC Good Food mandated, or is it our choice?

**It is our choice.** It is a *source-selection decision*, not an assignment requirement.
It is defensible on four measured grounds, all recorded in `DECISION_LOG.md` D1 and
re-verified for this audit:

1. **17,428 unique recipe URLs** discovered — 1.74× headroom over the 10,000 target.
2. A seeded 60-URL probe returned **60/60** parseable `schema.org/Recipe` JSON-LD.
3. It carries `recipeCuisine`, which **food.com does not** (`null`) — this is what makes
   the cuisine extension possible at all.
4. Every alternative with more recipes was rejected on *compliance*, not convenience —
   see below.

## The four concepts you asked me not to conflate

```
1. Assignment requirement      -> "any 10,000 recipes, not RecipeDB"     (from the PDF)
2. Source-selection decision   -> "we chose BBC Good Food"               (our judgement)
3. robots.txt / site policy    -> "may a crawler fetch this path?"       (the site's rules)
4. Crawl compliance            -> "did our crawler actually obey?"       (our behaviour)
```

**What robots.txt does and does not tell us:**

| Question | Does robots.txt answer it? |
|---|---|
| What dataset does the assignment require? | **No.** Nothing to do with it. That is the PDF's job. |
| Is automated crawling permitted at all? | **Partly** — it expresses the site's stated wishes for crawlers. |
| Is a particular path disallowed? | **Yes** — this is precisely what it encodes. |
| Is our use compliant? | **Partly.** robots.txt covers *fetching*. What you may then *do* with the data is governed by terms of use and copyright, not robots.txt. |

**Verified live during this audit:**

```
urllib.robotparser.can_fetch('*',                              /recipes/…) = True
urllib.robotparser.can_fetch('CGAS-BIO544-AcademicResearchBot', /recipes/…) = True
robots.txt line 51:  Content-signal: search=yes, ai-train=no
robots.txt line 52:  Allow: /
```

This is why sources were rejected: **Allrecipes / Serious Eats / Simply Recipes** carry a
People Inc. notice in `robots.txt` prohibiting scraping *and* "creating data sets
containing People Inc. content"; **taste.com.au** prohibits automated collection outright.
Those are policy prohibitions, so no amount of polite crawling makes them acceptable.
BBC Good Food's `Allow: /` is the opposite signal.

## Is the "not used for training" compliance statement supported? — **YES, verified**

The site sets `ai-train=no`. Our claim is that the corpus is used for descriptive
coursework analysis, not model training. Checked in code:

- `src/ner/prepare_tasteset.py` line 98: `pd.read_csv(ROOT / "data/external/TASTEset.csv")`
  — the **only** training input. No BBC text reaches any training routine.
- BBC text appears in exactly two modules: `src/ner/evaluate.py` and `src/ner/llm_extract.py`.

**One precision I want to state rather than gloss:** those two modules use BBC text for
**evaluation and model selection**, which is not training or fine-tuning — no gradients,
no weights updated — but it *is* using the scraped content to choose between models. That
is a fair and standard reading of `ai-train=no`, and it is worth saying out loud in a viva
rather than claiming the corpus was never used for anything model-related.

---

# C. NER FLOW DIAGRAM (corrected to match the actual code)

```
BBC Good Food recipe page
   │  scrape.py::build_record()  — JSON-LD first, HTML-selector fallback
   ▼
ingredient_phrases_raw[]                        116,699 phrases   (RAW LAYER, immutable)
   │
   │  extract_ingredients.py::main()
   ▼
preprocess_phrase()            canonicalize.py  — strips "(…)" editorial asides
   │
   ▼
spaCy transformer NER          data/interim/ner_trf/model-best   (distilroberta-base)
   │                           labels: NAME · QUANTITY · UNIT · STATE
   ▼
entity spans ──────────────┬── NAME  ──► ingredient path (below)
                           ├── QUANTITY ─► quantity_raw   (first span only)
                           ├── UNIT     ─► unit_raw       (first span only)
                           └── STATE    ─► processing_state (ALL spans, "|"-joined)
   │
   ▼ (NAME only)
rule_baseline.extract()        rule_baseline.py — FALLBACK, only if NER returned no NAME
   │                                              (fired on 632 of 123,017 = 0.5%)
   ▼
split_enumeration()            validate_names.py — "poppy seed and sesame seed" → 2 names
   ▼
trim_span()                    canonicalize.py  — cuts "made with", "such as", tails, parts
   ▼
normalize_surface()            canonicalize.py  → ingredient_normalized
   ▼
canonicalize()                 canonicalize.py  → ingredient_canonical   ◄── REQUIRED LAYER
   ▼
family()                       canonicalize.py  → ingredient_family      (extension only)
   ▼
validate_batch()               validate_names.py — grammatical gate, batch, post-hoc
   │                            rejected 212 of 6,977 candidate names (2,641 mentions, 2.1%)
   ▼
ingredient_mentions.csv (123,017)  ──►  Q1c_recipe_ingredient.csv (118,541)
                                        │
                                        └──►  Q2a freq · Q2b size · Q2c CDF · Q3 rank
```

Two corrections to how this was previously described:
- The **validation gate runs after canonicalisation, in one batch over unique names** — not
  inline per phrase. That is why it can use POS tagging cheaply.
- The **rule fallback is a NAME-only fallback**, not a general hybrid. It never touches
  quantity, unit or state.

---

# D. MODEL COMPARISON TABLE (verified from `outputs/extensions/ner_evaluation.json`)

n = 206 gold phrases. Precision and recall **are** available — reported here in full.

| Approach | can-P | can-R | **can-F1** | exact-set | TP | FP | FN | surf-F1 |
|---|---|---|---|---|---|---|---|---|
| **hybrid: transformer + rule fallback** | 0.881 | 0.904 | **0.893** | 0.869 | 208 | 28 | 22 | 0.758 |
| transformer NER alone | 0.881 | 0.900 | 0.890 | 0.864 | 207 | 28 | 23 | 0.755 |
| hybrid: CNN + rule fallback | 0.881 | 0.865 | 0.873 | 0.850 | 199 | 27 | 31 | 0.645 |
| hybrid: CNN + **LLM** fallback | 0.881 | 0.865 | 0.873 | 0.850 | 199 | 27 | 31 | 0.654 |
| local LLM (qwen2.5:3b) | 0.869 | 0.865 | 0.867 | 0.859 | 199 | 30 | 31 | 0.665 |
| CNN NER alone | 0.877 | 0.839 | 0.858 | 0.825 | 193 | 27 | 37 | 0.636 |
| rule/dictionary baseline (control) | 0.812 | 0.883 | 0.846 | 0.830 | 203 | 47 | 27 | 0.643 |

The CNN+LLM row has **byte-identical TP/FP/FN to CNN+rules** (199/27/31), which is the
hard evidence behind the "LLM fallback changed F1 by 0.000" claim. Verified.

**Model identity verified** from `data/interim/ner_trf/model-best/meta.json`:
pipeline `['transformer','ner']`, encoder `distilroberta-base`, labels
`['NAME','QUANTITY','STATE','UNIT']`, in-domain TASTEset dev `ents_f = 0.9521`
(per-entity: QUANTITY 0.981, UNIT 0.985, NAME 0.931, STATE 0.882).

## Why the transformer won — stated at the right strength

**Correct claim:** *the transformer NER was the best of the seven approaches we
empirically evaluated on our own recipe-domain gold set.* Not "transformers are the best
NLP models".

The measured mechanism is visible in the numbers. Every model has near-identical
**precision** (0.877–0.881); they differ almost entirely in **recall**
(CNN 0.839 → transformer 0.900). The transformer is not making fewer wrong guesses — it is
**finding ingredients the CNN misses**. That is what subword-aware contextual embeddings
buy you here:

1. **Unseen/rare words.** The CNN's `en_core_web_lg` vectors have no entry for
   `cavolo nero`, `ají amarillo`, `sohphlang`; they become OOV. distilroberta's BPE
   decomposes them into known subwords and can still emit a NAME span.
2. **UK-vs-US domain shift.** TASTEset is US English; our corpus is UK English
   ("rashers", "double cream", "mangetout"). Both models trained on the *same* data and
   scored nearly the same in-domain (95.2 vs 95.6 dev F1) — but on our gold set the
   transformer scores 0.890 vs 0.858. **The transformer's advantage is transfer, not
   in-domain fit.** That is the single most interesting finding in the evaluation.
3. **Boundary decisions need right-hand context.** "150g cheddar grated" has no comma;
   deciding that NAME ends before "grated" requires looking rightward. Self-attention sees
   the whole phrase at once; the CNN sees a fixed window.

**Why the hybrid adds only +0.003.** The rule fallback fires on **632 of 123,017 mentions
(0.5%)** — only when NER returns *no* NAME at all. It is a safety net for near-empty
phrases, not a general improvement. Being honest: this gain is one extra true positive
(207→208) on 206 phrases and is **not statistically meaningful on its own**. It is kept
because it cannot hurt (it only fires where the alternative is nothing), not because it
was shown to be better.

---

# E. GOLD-SET EXPLANATION — verified

**A gold set is a manually annotated evaluation dataset**: for each input we record the
answer a human considers correct, then compare model predictions against it. It is used
**only for measuring**, never for training.

**These are ingredient phrases, not recipes.** Confirmed: `data/interim/gold_eval.jsonl`
has 206 lines, each one ingredient line such as
`{"id": 0, "text": "2 thyme sprigs, leaves stripped", "gold_names": ["thyme"]}`.

```
206 ingredient phrases  (NOT 206 recipes)
  = 150 drawn uniformly at random, seed 20260908, from the deduplicated set of
        unique ingredient phrases in OUR scraped BBC corpus
  + 56  deliberately difficult phrases: 8 strata × 7 sampled each
        {parenthetical, >90 chars, ≥2 commas, numeric range, unicode fraction,
         no leading quantity, contains " or ", compound head
         (milk|vinegar|sauce|oil|cream|powder|butter)}
  = 206   (150 + 56 = 206 exactly; the de-duplication step removed no overlaps)
```

**On "261": there is no 261 anywhere in this project.** I grepped the whole tree. The only
hits are unrelated: a `tok2vec_loss` value of 261.73 in a spaCy `meta.json`, and the
literal strings "261", "1,261" inside a spaCy vocabulary file. **The gold set is 206.**

**Drawn from our own corpus: verified.** The candidates were sampled from
`data/raw/recipes_raw.jsonl` (BBC Good Food), not from TASTEset or any external set. This
matters: TASTEset is US English, so evaluating on TASTEset would have hidden exactly the
domain shift that turned out to be the deciding factor between the CNN and the transformer.

**DEFECT 4 — the sampling script is not in the repo.** The 150+56 draw was executed inline
in a shell heredoc. `grep -rln "gold_candidates" src/` returns nothing. The *artifacts*
(`gold_candidates.jsonl`, `gold_annotations.tsv`, `gold_eval.jsonl`) are all present and
the seed is recorded, but the code that produced them is not. This must be committed as
`src/ner/build_gold_set.py` for the sampling to be reproducible.

## Annotation schema — what is actually in the files

`data/interim/gold_annotations.tsv` — **two columns, tab-separated, no header**:

```
0	thyme
1	baking potatoes
2	chickpeas
33	mixed spice|ginger|nutmeg          ← "|" separates multiple ingredients in one phrase
192	red onion|white onion|spring onions
```

`data/interim/gold_eval.jsonl` — the merged evaluation file:
`{"id": int, "text": <raw phrase>, "gold_names": [str, …]}`

**There is no gold quantity, no gold unit, no gold state column. They do not exist.**

## What is actually being evaluated — the single most important caveat

**Ingredient NAME only.** The gold set annotates nothing else, so:

- The rubric's mandatory requirement (Q1b, ingredient-name extraction) **is** measured. Good.
- The **accuracy of `quantity_raw`, `unit_raw` and `processing_state` on our corpus is
  unmeasured.** The only evidence for those is TASTEset dev-set F1 (QUANTITY 0.981,
  UNIT 0.985, STATE 0.882) — which is **in-domain US English**, and we already proved
  in-domain scores mispredict our-domain performance for NAME. So those three numbers
  should be quoted as *TASTEset dev performance*, never as "our extraction accuracy".

Anyone claiming "our quantity extraction is 98% accurate" would be overstating the evidence.

---

# F. FEATURE EXTRACTION TABLE — what is *actually* in the output

Decisive test: fill rates measured directly over all 123,017 rows of
`data/processed/ingredient_mentions.csv`.

| Feature | Extracted? | Method | Stored where | Fill rate | Evaluated? |
|---|---|---|---|---|---|
| ingredient name (surface) | **YES** | transformer NER `NAME` + rule fallback | `ingredient_surface` | 100% | **YES** (gold set) |
| ingredient normalized | **YES** | `normalize_surface()` | `ingredient_normalized` | 100% | indirectly |
| **canonical ingredient** | **YES** | `canonicalize()` | `ingredient_canonical` | 100% | **YES** (canonical F1) |
| ingredient family | YES | `family()` head-noun + protected compounds | `ingredient_family` | 100% | no |
| **quantity** | **YES** | NER `QUANTITY`, first span | `quantity_raw` | **85.6%** | **NO** |
| **unit** | **YES** | NER `UNIT`, first span | `unit_raw` | **68.4%** | **NO** |
| **processing state** | **YES (raw)** | NER `STATE`, all spans "\|"-joined | `processing_state` | **49.3%** | **NO** |
| physical / quality state | **NOT SEPARATED** | conflated into `STATE` at training time | — | — | no |
| freshness state | **NOT IMPLEMENTED** | — | — | — | — |
| size modifier | **NOT SEPARATED** | falls inside `STATE` (`large`, `small`) | — | — | — |
| temperature modifier | **NOT IMPLEMENTED** in ingredient phrases | (only in instructions, 15.3% of steps) | — | — | — |
| state **category** (prep/cook/quality) | **NOT IMPLEMENTED** | — | — | — | — |
| extraction method | YES | recorded per mention | `extraction_method` | 100% | — |
| NER/rule agreement | YES | genuine agreement signal | `agrees_with_rule_baseline` | 100% (86.2% true) | — |
| numeric confidence | **NOT IMPLEMENTED** | spaCy NER emits no per-span probability | — | — | — |
| normalisation provenance | YES | rule names applied | `normalization_provenance` | 100% | — |

**So: quantity, unit and state are genuinely extracted and stored, not merely training
labels.** That part of the documentation holds up.

## TASTEset tag-mapping table — verified against `src/ner/prepare_tasteset.py`

| TASTEset entity | Our mapped label | Implemented? | Reaches final output? |
|---|---|---|---|
| FOOD | NAME | **YES** | **YES** — `ingredient_surface` |
| COLOR | NAME (merged, adjacent spans joined) | **YES** | **YES** — inside the name, e.g. "red chilli" |
| PART | NAME (merged) | **YES** | **YES** — e.g. "chicken breast" |
| QUANTITY | QUANTITY | **YES** | **YES** — `quantity_raw`, 85.6% |
| UNIT | UNIT | **YES** | **YES** — `unit_raw`, 68.4% |
| PROCESS | STATE | **YES** | **YES** — `processing_state`, 49.3% |
| PHYSICAL_QUALITY | STATE (**merged with PROCESS**) | **YES** | **YES — but indistinguishable from PROCESS** |
| TASTE | *dropped* | n/a | **NO** |
| PURPOSE | *dropped* | n/a | **NO** |

The consequential line is **PHYSICAL_QUALITY → STATE**. TASTEset keeps "chopped" (PROCESS)
and "fresh"/"large" (PHYSICAL_QUALITY) apart; we deliberately merged them to train one
label. That merge is *recoverable in principle* by retraining with the labels kept
separate — but as things stand, the information is gone from the output.

---

# G. PROCESS-STATE GAP ANALYSIS — the main finding of this audit

## What exists and works

`outputs/extensions/ingredient_state_map.json` (top-12 ingredients),
`processed_state_frequency.csv` (17,765 rows), `processed_ingredient_frequency_rank.csv`.
The content is semantically sensible:

```json
{"canonical_ingredient": "garlic", "total_state_observations": 4133,
 "states": {"crushed": 1324, "finely chopped": 501, "unspecified": 460,
            "chopped": 257, "large": 250, "finely grated": 241, "sliced": 184, …}}
```

So **PART 15 and PART 17 are implemented** — `onion::chopped`-style processed vocabulary
and a frequency-rank plot for it both exist.

## DEFECT 1 — the state filter is wrong for its purpose *(HIGH)*

`src/analysis/extensions.py:60`:

```python
states = [s for s in states if any(w in PREP_WORDS for w in s.split())]
```

`PREP_WORDS` was written in `canonicalize.py` for a **completely different job** — stripping
descriptor words off the *edges of a name span*. Reusing it to decide "is this a process
state?" produces exactly the wrong cut. Measured:

| Cooking transformation | survives the filter? |
|---|---|
| roasted, toasted | yes (2 of 17) |
| **fried, boiled, caramelised, grilled, baked, steamed, poached, sautéed, browned, blanched, smoked, pickled, fermented, cured** | **NO — silently discarded (15 of 17)** |

Meanwhile `large` (**3,782 mentions**) and `small` are *kept* and presented as process
states. And `smoked` — **865 mentions** — is thrown away entirely.

Net effect: **1,196 of 3,061 distinct observed states are dropped**, and the ones that
survive are skewed toward preparation and size. The file is named
`processed_state_frequency.csv` but does not faithfully represent process states. *This is
the single thing in the project whose label most overstates what it contains.*

## DEFECT 2 — no PREPARATION / COOKING / QUALITY taxonomy *(HIGH)*

PART 16 asked explicitly that `chopped` (preparation), `fried` (cooking transformation) and
`fresh` (physical quality) not be collapsed. **There is no `state_category` field anywhere
in the project.** Not implemented.

## DEFECT 3 — state→ingredient attribution *(MEDIUM)*

`extract_ingredients.py:84` collects **all** STATE spans in a phrase; line 116 writes that
same joined string onto **every** NAME extracted from that phrase. For
`"1 iceberg or romano lettuce finely chopped"` both names correctly get "finely chopped" —
but for a phrase where only one of two ingredients is modified, the state is duplicated
onto the wrong one. The current data cannot distinguish these cases.

## DEFECT 6 — denominators *(MEDIUM)*

`processed_state_frequency.csv` counts **mentions**; `processed_ingredient_frequency_rank.csv`
counts **recipes**. Both are internally consistent and the column names do say which — but
they sit side by side in one folder inviting exactly the confusion PART 18 warns about, and
there is no per-state **recipe** frequency at all.

## Also missing

- `outputs/extensions/ingredient_process_states.csv` (the per-mention file specified in
  PART 32) — **does not exist**.
- Per-state `recipe_frequency` alongside `mention_frequency` (PART 33) — **does not exist**.

---

# H. REQUIRED vs EXTENSION MATRIX

## Tier 1 — mandatory rubric · all VERIFIED

| Rubric | Status | Evidence |
|---|---|---|
| Q1(a) ≥10,000 recipes + raw data | **IMPLEMENTED** | 11,934 valid; `12,000 = 11,983 + 17` reconciles exactly |
| Q1(b) NER ingredient-name extraction | **IMPLEMENTED** | transformer NER, canonical F1 0.893 on 206-phrase gold set |
| Q1(c) Recipe ID — Ingredient Name | **IMPLEMENTED** | 118,541 rows = Σ recipe sizes (identity verified) |
| Q2(a) unique ingredients + frequencies | **IMPLEMENTED** | 6,765; distinct-in-Q1c == rows-in-Q2a |
| Q2(b) size distribution + average | **IMPLEMENTED** | mean 9.9330, SD 4.1111 — recomputed exactly |
| Q2(c) cumulative distribution | **IMPLEMENTED** | CDF labelled `F(s)=P(S≤s)`; CCDF separate file, labelled `P(S≥s)` |
| Q3(a) frequency–rank | **IMPLEMENTED** | competition ranking verified: 0 tied-rank violations |
| Q4–Q8 draft | **IMPLEMENTED** (Q5 needs you) | USDA-sourced Q4 table; Q5 flagged for personalisation |

## Full checklist against the original master prompt

| Item | Status |
|---|---|
| raw recipe preservation (incl. verbatim JSON-LD) | **IMPLEMENTED** — 11,983/11,983 keep `raw_jsonld` |
| cuisine metadata | **IMPLEMENTED** — 58.5% coverage, 72 labels, never imputed |
| NER (ingredient name) | **IMPLEMENTED** |
| quantity | **IMPLEMENTED** (85.6%) — **but never evaluated** |
| unit | **IMPLEMENTED** (68.4%) — **but never evaluated** |
| processing state | **PARTIALLY IMPLEMENTED** — extracted; analysis layer filtered wrongly |
| physical state | **PARTIALLY IMPLEMENTED** — merged into STATE, not separable |
| quality modifier | **NOT IMPLEMENTED** as a distinct field |
| freshness state | **NOT IMPLEMENTED** |
| temperature (ingredient phrase) | **NOT IMPLEMENTED** |
| canonical ingredient | **IMPLEMENTED** |
| processed ingredient (`ing::state`) | **IMPLEMENTED** — but inherits Defect 1 |
| recipe–ingredient graph | **IMPLEMENTED** — CSR matrix; row/col-sum identities verified |
| instruction event extraction | **IMPLEMENTED** — 39,354 steps, real structured JSON |
| cooking actions | **IMPLEMENTED** — 98.4% of steps |
| utensils | **IMPLEMENTED** — 76.3% |
| time (instructions) | **IMPLEMENTED** — 54.4% |
| temperature (instructions) | **IMPLEMENTED** — 15.3% (honest: most steps state none) |
| `input_state` in instruction events | **NOT IMPLEMENTED** |
| cuisine analysis | **IMPLEMENTED** — 21 cuisines with N≥30 |
| process-state frequency | **PARTIALLY IMPLEMENTED** — mention-only, wrong filter |
| process-state rank | **PARTIALLY IMPLEMENTED** — same defect |
| human review gallery | **IMPLEMENTED** — 90 rows with blank verdict column |
| confidence routing | **NOT IMPLEMENTED** — no numeric confidence exists; only a binary NER/rule agreement flag |
| local LLM benchmark | **IMPLEMENTED** — benchmarked and rejected on evidence |
| state taxonomy (prep/cook/quality) | **NOT IMPLEMENTED** |
| gold-set sampling code in repo | **NOT IMPLEMENTED** |

## Tier 2 vs Tier 3 classification of the gaps

**Tier 2 — worth doing (genuine research value, low risk to the rubric):**
1. Fix the state filter + add the PREPARATION/COOKING/QUALITY taxonomy (Defects 1, 2)
2. Emit `ingredient_process_states.csv` per mention, with `state_category` (PART 32)
3. Add per-state **recipe** frequency alongside mention frequency (PART 33)
4. Commit `src/ner/build_gold_set.py` (Defect 4)
5. Tighten instruction ingredient matching to full-phrase, not last-token (Defect 7)

**Tier 3 — only if genuinely wanted:**
6. Retrain NER keeping PROCESS and PHYSICAL_QUALITY as *separate* labels — this is the
   principled fix for Defect 2, but costs a retrain and a re-run, and the taxonomy in (1)
   recovers most of the value without it.
7. Annotate gold quantity/unit/state so those fields become measurable (Defect 5).
8. `input_state` in instruction events.
9. Numeric per-span confidence (needs spaCy beam parsing).

**Not worth doing:** confidence routing (no confidence signal exists to route on);
LLM bulk extraction (measured worse and ~44 h).

---

# I. ACTION PLAN

**KEEP unchanged** — the entire Q1–Q3 required path, the scraper, the corpus, the NER
model and its evaluation, the graph, cuisine analysis, and the Q4–Q8 draft. Nothing in the
graded path needs to change, and I do not propose touching it.

**FIX (defects in existing extension code):**
1. Replace the `PREP_WORDS` state filter with a purpose-built state lexicon.
2. Correct the mislabelling: what the file currently reports is not "process state".
3. Tighten instruction ingredient matching (full canonical phrase, longest-match).

**IMPLEMENT (missing, requested):**
4. `STATE_TAXONOMY`: PREPARATION / COOKING_TRANSFORMATION / PHYSICAL_QUALITY / SIZE,
   built only from states actually observed in our data.
5. `outputs/extensions/ingredient_process_states.csv` — per mention, with `state_category`.
6. Per-state **recipe** frequency and **mention** frequency, side by side, denominators named.
7. `src/ner/build_gold_set.py` — the sampling code, seeded, reproducing the existing 206.

**VALIDATE:** add checks that (a) every state in the map carries a category, (b) no state
word is silently dropped without appearing in a rejection audit, (c) per-state recipe
frequency ≤ ingredient recipe frequency, (d) the regenerated gold set matches the committed
one byte-for-byte.

**REGENERATE:** extensions only. The required Q1–Q3 outputs are unaffected and will be
re-verified by the existing 38-check gate.

---

# Viva answers (short form)

1. **Why BBC Good Food?** 17,428 recipe URLs (1.74× headroom), 60/60 clean JSON-LD in a
   seeded probe, and it carries `recipeCuisine` — food.com does not.
2. **Was it required?** No. The PDF requires "any 10,000 recipes" and forbids only
   RecipeDB. BBC Good Food is our choice.
3. **What has robots.txt to do with it?** It tells us whether a crawler may fetch a path —
   nothing about which dataset the assignment wants. It ruled *out* Allrecipes, Serious
   Eats, Simply Recipes and taste.com.au, whose robots.txt prohibits scraping. BBC Good
   Food answers `Allow: /` and `can_fetch('*', /recipes/) = True`.
4. **What is NER?** Labelling spans of text with entity types. In a recipe line
   `2 cups finely chopped red onions` → QUANTITY `2`, UNIT `cups`, STATE `finely chopped`,
   NAME `red onions`.
5. **What does ours extract?** NAME (100%), QUANTITY (85.6%), UNIT (68.4%), STATE (49.3%) —
   all present in `ingredient_mentions.csv`. TASTE and PURPOSE were dropped at training.
6. **Why transformer?** Best of the seven approaches *we measured on our own gold set* —
   0.890 vs CNN 0.858. The gain is almost entirely **recall** (0.900 vs 0.839): subword
   tokenisation handles rare/UK terms the CNN's vectors treat as OOV. It also transferred
   better despite a slightly *lower* in-domain dev score.
7. **Why hybrid?** The rule fallback fires on 0.5% of mentions where NER returns nothing.
   +0.003 F1 — one extra true positive; kept because it cannot hurt, not because it is
   proven better.
8. **Why didn't the LLM win?** qwen2.5:3b scored 0.867 vs 0.890, at 1.35 s/phrase
   (≈44 h for 116,699 phrases vs ~4 min). As a fallback it changed F1 by exactly 0.000 —
   identical TP/FP/FN. Benchmarked, then rejected on evidence.
9. **What is the gold set?** 206 manually annotated ingredient **phrases** from our own
   corpus, used only for evaluation.
10. **Why 150 + 56?** 150 uniform-random (seed 20260908) for an unbiased estimate, plus 56
    from 8 difficulty strata (7 each) to stress-test known failure modes. 150+56 = 206.
    There is no 261 in this project.
11. **What does F1 measure?** Per phrase, gold and predicted ingredient names are compared
    as **sets**; TP/FP/FN are summed over all 206 (micro-average). Canonical F1 0.893
    (P 0.881, R 0.904; TP 208, FP 28, FN 22). Exact-set accuracy 0.869 = the fraction of
    phrases where the predicted set matched the gold set *exactly* — a stricter, all-or-nothing
    measure. **Name only** — quantity/unit/state are not evaluated.
12. **What is canonicalisation?** Mapping surface forms to one vocabulary entry
    (`onions`, `finely chopped fresh red onions` → `red onion`) via edge-stripping,
    singularisation and a curated synonym table — with a protected-compound guard so
    `coconut milk` never becomes `milk` and `rice vinegar` never becomes `rice`.
13. **Canonical vs processed ingredient?** Canonical = `onion` (drives Q1c/Q2/Q3).
    Processed = `onion::chopped` (extension vocabulary, kept strictly alongside, never
    substituted into the required outputs).
14. **What process states do we extract?** Raw STATE spans on 49.3% of mentions — but the
    *analysis* layer currently filters them with the wrong word list, dropping `fried`,
    `boiled`, `caramelised`, `smoked` while keeping `large`. Being fixed.
15. **Quantities and units?** Yes — stored, 85.6% and 68.4%. Their accuracy on our corpus
    is **unmeasured**; only TASTEset in-domain figures exist.
16. **Instructions parsed?** Yes, as an **extension** — 39,354 steps → structured events
    (actions 98.4%, utensils 76.3%, duration 54.4%, temperature 15.3%). The *rubric* only
    requires ingredient-section NER.
17. **Ingredient frequency?** `f_i` = number of **distinct recipes** containing canonical
    ingredient `i`. Repeats within one recipe count once. Mention frequency is a separate column.
18. **Recipe size?** Number of **unique canonical ingredients** per recipe.
    Mean 9.933, SD 4.111, median 9, IQR 7–12, range 1–38, skew 0.79 — right-skewed,
    explicitly not assumed Gaussian.
19. **Frequency–rank plot?** Ingredients sorted by descending `f_i`, rank on x, frequency
    on y, shown linear and log–log. Heavy-tailed. **We do not claim Zipf or a power law** —
    that needs a statistical test we did not run.
20. **What remains incomplete?** The state taxonomy and the state filter; per-state recipe
    frequency; evaluation of quantity/unit/state; the gold-set sampling script; and
    `input_state` in instruction events.

---

# RESOLUTION (post-repair)

Every defect this audit raised has been closed, plus three found afterwards by
reading `rejected_ingredient_names.csv` and the state map. Verified by 45 automated
checks (`outputs/VALIDATION_REPORT.json`) and 47 targeted tests (`tests/test_repairs.py`).

| # | Defect | Status |
|---|---|---|
| 1 | State filter reused `PREP_WORDS`, discarding 15/17 cooking transformations | **FIXED** — `state_taxonomy.py`; COOKING now 3,787 observations (was ~0) |
| 2 | No PREPARATION / COOKING / QUALITY / SIZE taxonomy | **FIXED** — observed-only, head-word driven, ambiguity flagged |
| 3 | STATE copied onto every NAME in a line | **FIXED** — coordination-segment attachment |
| 4 | Gold-set sampling code not in repo | **FIXED** — `build_gold_set.py`; `--check` reproduces the 206 exactly (snapshot N=1502 recovered from the run log) |
| 5 | quantity/unit/state never evaluated | **STILL OPEN** — the 0.895 F1 measures NAME only. Stated explicitly in README_SUBMISSION rather than papered over. |
| 6 | No per-mention state file; mention-only frequencies | **FIXED** — `ingredient_process_states.csv`, `state_frequency_by_category.csv` (mention **and** recipe counts) |
| 7 | Instruction matching used last token | **FIXED** — longest-phrase match; refuses to guess when ambiguous |
| 8 | `src/graph/` empty | **FIXED** — Cuisine–Recipe–Ingredient–State graph, 30,246 nodes / 200,996 edges |
| 9 | LLM cost extrapolated to "120,000" phrases | **FIXED** — corpus is 116,699 phrases; restated as ≈44 h |

**Found after the audit, during repair:**

| Defect | Evidence | Status |
|---|---|---|
| Canonicalisation destroyed product identity (`whole milk`→`milk`, `light brown sugar`→`brown sugar`, `gram flour`→`flour`, `extra virgin olive oil`→`virgin olive oil`) — and asymmetrically, `dark brown sugar` survived | measured on the frequency table | **FIXED** — protected-compound guard + `expand_protected()` |
| `A or B` counted as two ingredients | 4,617 lines, 4,989 spurious mentions, 29.4% of recipes | **FIXED** — primary-only for Q1(c)/Q2/Q3; alternatives retained under `alternative_group` |
| Gate deleted real ingredients: `rosemary` (352 recipes, rank 64), `couscous`, `houmous`, `nougat`, `cannelloni` | `en_core_web_sm` tags them ADJ even inside the carrier sentence | **FIXED** — corpus-evidence override (19/19 true adjectives score 0; rosemary 85) |
| Bare part words discarded although 456 phrases state the parent | `zest of 1 lemon` | **FIXED** — `recover_part_parent()`; 197 recoveries |
| `all butter shortcrust pastry` rejected as a clause fragment | `all` in `BAD_OPENING_WORDS` | **FIXED** — `all` disqualifies only before another function word |
| `ingredient_state_map.json` showed 15 of 2,707 ingredients, ranked by *frequency* not state-richness (kept `vanilla extract` with 1 state, dropped `carrot` with 145) | hardcoded `most_common(15)` | **FIXED** — full map emitted; preview ranked by state count; all caps are now named constants documented as **presentation limits, not statistical thresholds** |

**One correction to this audit's own text:** it stated the carrier-sentence fix "was
never implemented". That was wrong — `validate_names.py` does tag inside
`"I added the {} to the pan."` The accurate finding is that the carrier is
**insufficient**, not absent: it rescues avocado/panko/risotto but not rosemary or
couscous, which is why the corpus-evidence override was added on top of it.

## Final corpus figures

| | |
|---|---|
| recipes | 11,934 |
| ingredient phrases | 116,699 |
| mentions | 123,598 (4,253 non-primary alternatives excluded from Q1c/Q2/Q3) |
| Q1(c) rows | 115,197 |
| unique canonical ingredients | 6,346 |
| mean recipe size | 9.653 (SD 3.951, median 9, IQR 7–12, skew 0.76) |
| NER canonical F1 | 0.895 (P 0.885, R 0.904), exact-set 0.869 |
| state observations | PREPARATION 44,174 · QUALITY 10,942 · SIZE 8,805 · COOKING 3,787 · UNCLASSIFIED 7,738 · NOT_A_STATE 3,880 |
| graph | 30,246 nodes / 200,996 edges |
| cuisine coverage | 6,977 / 11,934 (58.5%), 21 cuisines with N ≥ 30 |
| validation | 45 / 45 PASS |
