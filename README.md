<div align="center">

# 🍲 MDMA · FlavorGraph

### Computational Gastronomy — BIO544 · IIIT Delhi · Monsoon 2026

*12,000 recipes, a trained ingredient NER model, and frequent-itemset mining, all from scratch.*

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-NER-09A3D5?logo=spacy&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-analysis-150458?logo=pandas&logoColor=white)
![Validation](https://img.shields.io/badge/A2%20validation-22%2F22%20PASS-2ea44f)

</div>

---

## ✨ Highlights

| | Work | One-line result |
|---|---|---|
| **A1** | [Recipe corpus + ingredient NER](assignments/A1) | **11,934** recipes scraped politely and resumably; ingredient NER reaches canonical **F1 0.895** (transformer + rules) on 206 hand-labelled phrases |
| **A2** | [Frequent itemsets + random controls](assignments/A2) | Apriori from scratch: **6,346 / 170,419 / 1,350,680** item sets of size 1/2/3, compared against size-controlled and frequency-controlled random cuisines |
| **Project** | [Mini-project research](project) | Process-aware flavour intelligence: research synthesis R1–R5 + the full project spec |

---

## 🥕 Assignment 1 — Recipe corpus, NER and distributions

```
sitemap → seeded URL sample → polite resumable crawl → validate → dedupe → stable Recipe IDs
        → per ingredient phrase: spaCy NER → rule fallback → normalise → canonicalise
        → Q1c (Recipe ID, Ingredient) → Q2 frequencies · recipe sizes · CDF → Q3 frequency–rank
```

| NER model (206 gold phrases) | surface F1 | canonical F1 |
|---|---:|---:|
| rule / dictionary baseline | 0.643 | 0.833 |
| spaCy CNN (TASTEset) | 0.636 | 0.853 |
| spaCy transformer (TASTEset) | 0.755 | 0.892 |
| **transformer + rules (final)** | **0.758** | **0.895** |

```bash
cd assignments/A1
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m spacy download en_core_web_sm && ./.venv/bin/python -m spacy download en_core_web_lg
./run_all.sh scrape   # stage 1: rebuild the raw corpus (~60 min, resumable)
./run_all.sh          # stages 2–9: NER, tables, figures, validation
```

> The raw scraped recipe text (~160 MB, `data/raw`, `data/processed`, `Q1a_raw_recipes.jsonl`) is **not** in this repo.
> `run_all.sh scrape` rebuilds it. Every graded table and figure derived from it is included under `outputs/`.

## 🧺 Assignment 2 — Frequent itemset mining

- Apriori (`src/fism.py`) over the A1 table: **N = 11,934** recipes, 115,197 recipe–ingredient memberships, mean recipe size **9.65**.
- Top-20 item sets per size, plus support and confidence, with association-rule evidence.
- Random-cuisine controls (`src/random_controls.py`):
  - size-controlled by replica (10 sets);
  - size-controlled by inverse transform (10×);
  - size **and** frequency controlled.
- 22 automated validation checks, all passing.

```bash
cd assignments/A2
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./run_all.sh          # reads ../A1/outputs/Q1/Q1c_recipe_ingredient.csv and regenerates every output
```

## 🔬 Mini-project — process-aware flavour intelligence

| File | What |
|---|---|
| [`Group17_MDMA_Mini_Project_Proposal_Brief.pdf`](project/Group17_MDMA_Mini_Project_Proposal_Brief.pdf) | Proposal brief |
| [`research/`](project/research) | R1 fingerprints & similarity · R2 physchem/quantum descriptors · R3 cooking reaction chemistry · R4 structure–odour · R5 encoders & data landscape · consolidated synthesis |
| [`computational_gastronomy_master_ssot_v15_0.md`](project/computational_gastronomy_master_ssot_v15_0.md) | Full research and build spec: CulinaryState-RAG and FlavorTwin |

---

## 📚 Course material

| Folder | Contents |
|---|---|
| [`lectures/`](lectures) | Week 1 intro · food pairing (Ahn et al.) · recipe & flavour (weeks 2–4) · CoSyLab food-pairing studies (weeks 3, 5) |
| [`notes/`](notes) | Class notes 1–3 · A1 learning and execution map |

Key papers (read them from the publishers):
- Ahn et al., *Flavor network and the principles of food pairing*, Scientific Reports 1:196 (2011).
- Jain, Rakhi & Bagler, *Analysis of food pairing in regional cuisines of India*, PLOS ONE (2015).
- Garg et al., *FlavorDB: a database of flavor molecules*, Nucleic Acids Research 46:D1210 (2018).

<div align="center">

**Team MDMA · Group 17** · IIIT Delhi

<sub>Recipe data: BBC Good Food (schema.org JSON-LD), used for coursework only. RecipeDB is not used. Slides belong to their instructors.</sub>

</div>
