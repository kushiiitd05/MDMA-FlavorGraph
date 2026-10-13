# SUBMISSION GUIDE — Computational Gastronomy (BIO544) Assignment 1

**Corpus:** 11,934 unique valid recipes scraped from **BBC Good Food** (target: 10,000).
**RecipeDB was not used** — verified automatically (validation check C2).
**Validation: 45 / 45 checks PASS** (`outputs/VALIDATION_REPORT.json`).

---

## 1. Files to submit, by question number

### Q1 — corpus, NER, recipe–ingredient table

| Rubric | Marks | File |
|---|---|---|
| **Q1(a)** Scrape 10,000 recipes, submit raw data | 5 | `outputs/Q1/Q1a_raw_recipes.jsonl.gz` (11,983 raw records, 82.7 MB uncompressed — includes verbatim `raw_jsonld`)<br>`outputs/Q1/Q1a_recipe_metadata.csv` (human-readable index) |
| **Q1(b)** NER script + ingredient-name extraction | 8 | Script: `src/ner/extract_ingredients.py` (+ `src/ner/prepare_tasteset.py`, `src/normalization/`)<br>Output: `outputs/Q1/Q1b_ingredient_ner_output.csv` (123,598 mentions)<br>Evidence: `outputs/Q1/Q1b_ner_evaluation.json` |
| **Q1(c)** (Recipe ID)—(Ingredient Name) | 2 | `outputs/Q1/Q1c_recipe_ingredient.csv` (115,197 rows) |

### Q2 — corpus analysis

| Rubric | Marks | File |
|---|---|---|
| **Q2(a)** unique ingredients + frequencies | 2 | `outputs/Q2/Q2a_unique_ingredients_frequency.csv` — **6,346 unique ingredients** |
| **Q2(b)** recipe-size distribution + average | 3 | `outputs/Q2/Q2b_recipe_size_distribution.png` — **mean s̄ = 9.653**<br>`outputs/Q2/Q2b_average_recipe_size.json`, `Q2b_recipe_size_frequency_map.csv` |
| **Q2(c)** cumulative distribution | 5 | `outputs/Q2/Q2c_recipe_size_cumulative_distribution.png`, `Q2c_recipe_size_cdf.csv` |

### Q3 — frequency–rank

| Rubric | Marks | File |
|---|---|---|
| **Q3(a)** frequency–rank distribution | 5 | `outputs/Q3/Q3a_frequency_rank_distribution.png` (linear + log–log panels), `Q3a_frequency_rank.csv` |

### Q4–Q8 — handwritten, one scanned PDF

| Rubric | Marks | Prepare from |
|---|---|---|
| Q4 boiled egg vs rice + daal | 2 | `theory/Q4_Q8_draft.md` §Q4 (+ `theory/Q4_nutrition_data.json`, USDA FoodData Central) |
| Q5 five uncommon ingredients | 5 | `theory/Q4_Q8_draft.md` §Q5 — ⚠ **must be personalised, see §3 below** |
| Q6 truth or myth (×3) | 3 | `theory/Q4_Q8_draft.md` §Q6 |
| Q7 calorific content (5–8 lines) | 2 | `theory/Q4_Q8_draft.md` §Q7 |
| Q8 eight CGAS technologies | 8 | `theory/Q4_Q8_draft.md` §Q8 |

Citations for all of the above: `theory/references.md`.

---

## 2. Headline numbers

| Quantity | Value |
|---|---|
| Recipes scraped / valid after dedup | 11,983 / **11,934** |
| Scrape failures | 17 (all HTTP 404 dead sitemap URLs) — `logs/scrape_failures.jsonl` |
| Ingredient phrases processed | 116,699 |
| Ingredient mentions extracted | 123,598 |
| **Unique canonical ingredients** | **6,346** |
| **Mean recipe size s̄** | **9.653** (SD 3.951, median 9, IQR 7–12, min 1, max 38) |
| Distribution shape | right-skewed (skewness 0.76, excess kurtosis 1.19) — **not** assumed Gaussian |
| Most frequent ingredients | garlic 3,459 · butter 3,440 · olive oil 3,155 · egg 2,793 · onion 2,039 |
| NER accuracy (gold set, n=206) | **canonical-set F1 0.895** (P 0.885, R 0.904), exact-set accuracy 0.869 |

---

## 3. What still needs a human — before you submit

1. **Q5 must be personalised.** The question asks for ingredients *you or your parents or
   grandparents* know. `theory/Q4_Q8_draft.md` §Q5 gives a **research-backed shortlist**
   (kachri, kartoli, bathua, gongura, chironji) with sources, clearly marked
   `STUDENT MUST CONFIRM`. Replace any entry you cannot personally vouch for with a real
   ingredient from your own family/region, keeping the same four columns.
2. **Handwrite Q4–Q8** from the draft and **scan them into one PDF**, named with the
   question numbers. Keep Q7 to 5–8 lines and Q8 to exactly eight items of 1–3 lines.
3. **Optional but recommended:** spot-check `outputs/extensions/human_review_gallery.csv`
   (90 ingredient phrases with their extracted output and a blank verdict column) so you
   can speak to the NER quality if asked in a viva.
4. **Optional:** review `data/interim/gold_annotations.tsv` — the 206-phrase gold standard
   the NER was scored against — and adjust any annotation you disagree with, then re-run
   `./.venv/bin/python src/ner/evaluate.py`.

---

## 4. Reproducing everything

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m spacy download en_core_web_sm
./.venv/bin/python -m spacy download en_core_web_lg

./run_all.sh scrape   # OPTIONAL: re-crawl from scratch (~70 min, resumable)
./run_all.sh          # stages 1-9 from the stored raw corpus -> regenerates every file above
```

**Note on model weights.** The two trained NER models (~1.4 GB) are **not included in this
archive**. `run_all.sh` detects they are missing and retrains both from TASTEset
automatically — deterministically, with `seed 20260908`, in about 10 minutes. Everything
needed to do so *is* shipped: `data/external/TASTEset.csv`, the prepared
`data/interim/ner_corpus/*.spacy`, and the two spaCy configs in `config/`.
The scraped corpus itself (`data/raw/recipes_raw.jsonl`) **is** included, so no
re-crawling is ever required.

Environment, versions and seeds: `outputs/REPRODUCIBILITY.json`.
Every design decision with its evidence: `docs/DECISION_LOG.md`.
Backups with SHA-256 checksums: `backup/MANIFEST.latest.json`.
