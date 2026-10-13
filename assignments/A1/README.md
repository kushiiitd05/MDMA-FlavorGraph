# Computational Gastronomy (BIO544) — Assignment 1, Monsoon 2026

A reproducible pipeline that scrapes a 10,000+ recipe corpus, extracts ingredient
names with a trained **Named Entity Recognition** model, and produces every figure
and table the rubric asks for.

> **Data source: BBC Good Food** (`bbcgoodfood.com`), via its schema.org Recipe JSON-LD.
> **RecipeDB is not used anywhere** — the assignment forbids it, and an automated
> check (`C2` in the validation gate) verifies no RecipeDB record can enter the corpus.

---

## Quick start

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m spacy download en_core_web_sm
./.venv/bin/python -m spacy download en_core_web_lg

./run_all.sh scrape     # stage 1: URL discovery + crawl (~60 min, resumable)
./run_all.sh            # stages 2-9: everything else, from stored data
```

Stages 2–9 **never re-scrape**. `run_all.sh scrape` is resumable: interrupt it with
Ctrl-C and re-run — the visited-URL registry means no page is fetched twice.

---

## Where the graded files are

| Rubric item | File |
|---|---|
| **Q1(a)** raw data | `outputs/Q1/Q1a_raw_recipes.jsonl` (+ `.gz`), `outputs/Q1/Q1a_recipe_metadata.csv` |
| **Q1(b)** NER output | `outputs/Q1/Q1b_ingredient_ner_output.csv`, `outputs/Q1/Q1b_ner_evaluation.json` |
| **Q1(c)** Recipe ID — Ingredient Name | `outputs/Q1/Q1c_recipe_ingredient.csv` |
| **Q2(a)** unique ingredients + frequencies | `outputs/Q2/Q2a_unique_ingredients_frequency.csv` |
| **Q2(b)** recipe-size distribution + mean | `outputs/Q2/Q2b_recipe_size_distribution.png`, `outputs/Q2/Q2b_average_recipe_size.json` |
| **Q2(c)** cumulative distribution | `outputs/Q2/Q2c_recipe_size_cumulative_distribution.png` |
| **Q3(a)** frequency–rank distribution | `outputs/Q3/Q3a_frequency_rank_distribution.png` |
| **Q4–Q8** handwriting draft | `theory/Q4_Q8_draft.md`, `theory/references.md` |
| Validation report | `outputs/VALIDATION_REPORT.json` |

Everything in `outputs/extensions/` is **research extension work, not rubric material**.

---

## Pipeline

```
sitemap  ->  seeded random URL sample  ->  polite resumable crawl
                                              |
                                    recipes_raw.jsonl  (IMMUTABLE, keeps raw_jsonld)
                                              |
                     validate -> deduplicate -> stable Recipe IDs (R000001...)
                                              |
   per ingredient phrase:  strip parentheticals -> spaCy NER -> rule fallback
                           -> span trim -> normalise -> canonicalise -> sanity gate
                                              |
              ingredient_mentions.csv    Q1c_recipe_ingredient.csv
                                              |
                        Q2a frequencies | Q2b size | Q2c CDF | Q3 rank
```

The four representation layers are kept **separate and never overwrite each other**:

```
raw_phrase  ->  ingredient_surface  ->  ingredient_normalized
                                    ->  ingredient_canonical   (REQUIRED outputs)
                                    ->  ingredient_family      (extensions only)
```

---

## Research extensions (not rubric material)

Everything below lives in `outputs/extensions/` and **nothing in Q1–Q3 depends on it**.

| Layer | What it adds |
|---|---|
| Ingredient + state | `ingredient_process_states.csv` — one row per observed state, classified into **PREPARATION / COOKING / QUALITY / SIZE** (plus NOT_A_STATE and UNCLASSIFIED, so nothing is silently dropped). The taxonomy vocabulary is read off this corpus, not imported from an ontology. |
| State frequencies | `state_frequency_by_category.csv` — **mention_count and recipe_count side by side**, with the denominator named. Asserted invariant: `recipe_count(i,s) ≤ recipe_freq(i)`; states are *not* mutually exclusive, so they deliberately do not sum. |
| Processed vocabulary | `processed_ingredient_frequency_rank.csv` — the `onion::chopped` layer, kept **alongside** the canonical ingredient, never substituted into Q1(c)/Q2/Q3. |
| Connection graph | `graph/` — a **Cuisine → Recipe → Ingredient → State** graph (30,246 nodes / 200,996 edges). The `HAS_STATE` edge makes a processed form a **child of its parent ingredient**, so `onion::fried` refines `onion` instead of competing with it. Exports: `nodes.csv`, `edges.csv`, `cgas_graph.graphml.gz`. |
| Cuisine analysis | recipe-size stats per cuisine (N ≥ 30 only) and a `cuisine × ingredient` map scored by **lift**, so staples like olive oil never look "characteristic" of everything. |
| Instruction events | 39,354 steps → structured `{action, ingredients, utensils, duration, temperature, output_state}`; a field is `null` unless the text states it. |

---

## Frozen definitions

| Quantity | Definition |
|---|---|
| Ingredient frequency `f_i` | number of **distinct recipes** containing canonical ingredient `i` (an ingredient repeated within one recipe counts once). `mention_frequency` is computed separately and never mixed in. |
| Recipe size `s_R` | number of **unique canonical ingredients** in recipe `R` |
| Mean `μ_s` | `(1/N) Σ_R s_R`, computed over all recipes directly — never by averaging cuisine means |
| CDF | `F(s) = P(S ≤ s)` — the Q2(c) deliverable |
| CCDF | `F̄(s) = P(S ≥ s)` — supplementary, in `outputs/extensions/`, explicitly labelled |
| Rank | **competition ranking** ("1224"); ties share the minimum rank. Display order breaks ties alphabetically. No invented "importance" score. |
| Alternations | `A or B` is **one** ingredient slot — the primary (first) branch counts for Q1(c)/Q2/Q3, because a cook makes one choice. Every alternative is kept in `ingredient_mentions.csv` under `alternative_group`. |
| Part / cut words | A part word **with** a parent is ingredient identity (`chicken breast`, `lemon zest`, `cod fillet`); **alone** it is rejected. A cut such as `fillet` is an anatomical **portion, not a SIZE**. |

Recipe-size normality is **not assumed** — skewness and kurtosis are reported.
Log–log linearity of the rank plot is **not** claimed as Zipf/power-law evidence.

---

## Layout

```
A1/
├── config/config.yaml          all parameters + frozen definitions
├── data/
│   ├── external/               TASTEset (MIT), cached USDA FDC responses
│   ├── raw/                    recipes_raw.jsonl  <- IMMUTABLE
│   ├── interim/                clean corpus, NER training data, gold eval set
│   └── processed/              mentions, processed recipes, instruction events
├── src/
│   ├── scraping/               discover_urls.py, scrape.py
│   ├── parsing/                build_corpus.py       (validate/dedup/IDs)
│   ├── ner/                    prepare_tasteset.py, extract_ingredients.py,
│   │                           rule_baseline.py, evaluate.py,
│   │                           build_gold_set.py, llm_extract.py
│   ├── normalization/          canonicalize.py, validate_names.py,
│   │                           state_taxonomy.py
│   ├── instructions/           parse_instructions.py
│   ├── analysis/               analyze.py, extensions.py, process_states.py,
│   │                           q4_nutrition.py
│   ├── graph/                  build_graph.py, plot_graph.py
│   └── validation/             validate_all.py, package_submission.py
├── outputs/{Q1,Q2,Q3}/         REQUIRED SUBMISSION
├── outputs/extensions/         RESEARCH EXTENSIONS
│   └── graph/                  Cuisine-Recipe-Ingredient-State graph
├── theory/                     Q4–Q8 draft + references
├── docs/DECISION_LOG.md        every non-obvious choice, with evidence
├── docs/AUDIT.md               verification of claims against the actual files
├── backup/                     gzipped checksummed backups + manifest
├── tests/test_repairs.py       targeted identity / state / attachment checks
└── logs/                       crawl log, failure log, training logs
```

---

## Compliance

`robots.txt` for `bbcgoodfood.com` allows `/` for `User-agent: *`; the crawler checks
this programmatically before discovery begins. Crawling is rate-limited (4 workers,
~0.6 s per-worker delay, ≈3 requests/s) with exponential backoff on 429/5xx. The site
sets `Content-signal: ai-train=no`; this corpus is used for **descriptive statistical
coursework analysis only** — no model is trained or fine-tuned on the scraped content.
(The NER model is trained on TASTEset, an independent MIT-licensed dataset.)

Sources rejected on compliance grounds are documented in `docs/DECISION_LOG.md` (D1).
