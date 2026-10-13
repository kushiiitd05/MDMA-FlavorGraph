# Computational Gastronomy (BIO544) — Assignment 2

**Validation: 22 / 22 checks PASS** (`outputs/VALIDATION_REPORT.json`)
Everything is regenerated from the Assignment-1 deliverable by `./run_all.sh`.

---

## Where each graded item is

| Question | Marks | File |
|---|---|---|
| **1(a)** complete item sets of size 1, 2, 3 | 5 | `outputs/Q1/Q1a_itemsets_size1.csv` (6,346)<br>`outputs/Q1/Q1a_itemsets_size2.csv` (170,419)<br>`outputs/Q1/Q1a_itemsets_size3.csv.gz` (1,350,680) |
| **1(b)** top 20 item sets of each size | 3 | `outputs/Q1/Q1b_top20_itemsets.csv` · `.json` |
| **1(c)** define support & confidence | 2 | `outputs/Q1/Q1c_support_confidence.md`<br>evidence: `outputs/Q1/Q1c_association_rules.csv` |
| **2(a)** size-controlled by replica, 10 sets | 5 | `outputs/Q2/Q2a_recipe_size_distribution.png` |
| **2(b)** size-controlled by inverse transformation, 10× | 5 | `outputs/Q2/Q2b_recipe_size_distribution.png` |
| **3(a)** size + frequency controlled — size distribution | 5 | `outputs/Q3/Q3a_recipe_size_distribution.png` |
| **3(b)** size + frequency controlled — frequency-rank | 5 | `outputs/Q3/Q3b_frequency_rank_distribution.png` |

The FISM algorithm itself is `src/fism.py`; the random controls are
`src/random_controls.py`. **Files are named with their question numbers**, as the
rubric requires.

---

## The corpus

| | |
|---|---|
| Source | `../A1/outputs/Q1/Q1c_recipe_ingredient.csv` — the graded A1 deliverable |
| Recipes | **11,934** |
| Unique ingredients | **6,346** |
| (recipe, ingredient) memberships | 115,197 |
| Mean recipe size | 9.6528 (min 1, max 38) |

**One judgement call, stated plainly.** The question says "the data of 10,000
recipes … obtained for Assignment 1". A1 was required to collect *at least*
10,000 and delivered **11,934**, so the whole A1 corpus is used and every count
here is reported against **N = 11,934** rather than an arbitrary 10,000-recipe
subset. Nothing was discarded.

**Membership is binary** — a recipe is a *set* of distinct ingredients. The A1
table already satisfies this and the loader asserts it at every run (check C3).

---

## Q1 — Frequent item set mining

**Apriori is implemented from scratch** in `src/fism.py`. No mining library is
used anywhere in this submission.

```
L1 = frequent 1-itemsets                       (one pass)
for k = 2, 3:
    Ck = join F(k-1) x F(k-1) on the shared (k-2)-prefix
    Ck = prune candidates having any infrequent (k-1)-subset   [downward closure]
    count Ck over the baskets
    Lk = { c in Ck : support(c) >= min_support }
```

Running at `min_support = 0.1% = 12 recipes`:

| k | candidates generated | pruned by downward closure | counted | frequent |
|---|---|---|---|---|
| 1 | 6,346 | — | 6,346 | 833 |
| 2 | 346,528 | 0 | 346,528 | 7,689 |
| 3 | 629,234 | **544,495 (86.5%)** | 84,739 | 12,807 |

**Correctness is verified, not assumed.** `exhaustive_counts()` independently
brute-forces every item set of size 1–3 occurring at least once, and
`verify_apriori()` asserts Apriori's output is exactly that enumeration filtered
at the same threshold. It matches at every level (check C5).

### 1(a) — complete lists

Emitted at **support ≥ 1**, i.e. every item set that actually occurs:

| size | item sets | file |
|---|---|---|
| 1 | 6,346 | `Q1a_itemsets_size1.csv` |
| 2 | 170,419 | `Q1a_itemsets_size2.csv` |
| 3 | 1,350,680 | `Q1a_itemsets_size3.csv.gz` — gzipped; 45 MB plain |

Columns: `item_1 … item_k`, `itemset`, `size`, `support_count`,
`support_fraction`. The mined (frequent) subsets at the stated threshold are
also given as plain CSVs, `Q1a_apriori_frequent_size{1,2,3}.csv`.
`Q1_summary.json` tabulates the counts at eight different thresholds.

### 1(b) — top 20 of each size

| Size 1 | Size 2 | Size 3 |
|---|---|---|
| garlic (3,459) | butter \| egg (1,572) | butter \| egg \| plain flour (719) |
| butter (3,440) | garlic \| olive oil (1,572) | garlic \| olive oil \| onion (565) |
| olive oil (3,155) | butter \| plain flour (1,189) | butter \| egg \| self-raising flour (537) |
| egg (2,793) | garlic \| onion (1,185) | butter \| egg \| golden caster sugar (489) |
| onion (2,039) | egg \| plain flour (1,006) | butter \| egg \| icing sugar (485) |

The structure is interpretable: a **baking cluster** (butter–egg–flour–sugar) and
a **savoury-base cluster** (garlic–olive oil–onion) separate cleanly without
being asked to.

### 1(c) — support and confidence

Full answer in `Q1c_support_confidence.md`. In short:

```
support(X)        = |{R : X ⊆ R}| / N              property of an ITEM SET
confidence(X→Y)   = support(X ∪ Y) / support(X)    property of a RULE  ≈ P(Y|X)
```

Worked from this corpus: `self-raising flour → egg` has
confidence 630/775 = **0.8129**, while the reverse rule `egg → self-raising flour`
has 630/2,793 = **0.2256** — same item set, same support, very different
confidence, because **confidence is directional and support is not**. Support is
also anti-monotone, which is what makes Apriori's pruning valid; confidence is
not. 80 rules with support, confidence and lift are in `Q1c_association_rules.csv`.

---

## Q2 — Size-controlled random control

### 2(a) replica method, 10 sets
For each real recipe of size *n*, one random recipe of exactly size *n* is built
by drawing *n* distinct ingredients **uniformly** from the cuisine's basket.
Repeated independently 10 times → 119,340 random recipes.

**Result:** all 10 random cuisines reproduce the recipe-size distribution
**exactly** — necessarily so, since sizes are copied. Asserted in check C14, and
visible in the figure as the dashed random lines sitting exactly on the original.

### 2(b) inverse transformation, 10×
Sizes are **sampled**, not copied:

```
F(s) = P(S ≤ s)   draw u ~ U(0,1)   return the smallest s with F(s) ≥ u
```

119,340 recipes (10× the original) generated this way.

**Result:** mean recipe size **9.6528 → 9.6375**, total variation distance
between the two size distributions **0.0047**. The match is close but — unlike
2(a) — not exact, because the sizes are now random draws. That difference
between the two methods is the point of asking for both.

---

## Q3 — Size *and* ingredient-frequency controlled

Sizes replicated as in 2(a); ingredients now drawn with probability
**proportional to their frequency in the original cuisine**, without replacement.
10 independent sets.

- **3(a)** size distribution reproduced exactly (check C15).
- **3(b)** the frequency-rank curve is reproduced to a **2.9% mean relative error
  over the top 200 ranks**.

The 3(b) figure also plots the Q2 size-only control for contrast, where the same
error is **87.7%** — a flat line that misses the heavy tail entirely.

> **Preserving ingredient frequency reproduces the observed rank distribution;
> controlling recipe size alone does not.** A 30-fold difference in error on the
> same corpus — the course's central claim about randomised controls,
> demonstrated on our own data.

---

## Sampling method

Weighted sampling **without replacement** uses the Efraimidis–Spirakis
exponential key: draw `Eᵢ ~ Exp(1)` per item, form `kᵢ = Eᵢ / wᵢ`, keep the *k*
smallest keys. This gives successive weighted sampling without replacement
exactly, and vectorises. Uniform sampling is the same routine with equal
weights. Recipes are grouped by size so `argpartition` returns exactly the *k*
smallest keys per row — taking the first *k* of a larger partition would be
wrong, since `argpartition` does not order within the partition.

All randomness is seeded: `SEED = 20261006` in `src/corpus.py`.

---

## Reproducing

```bash
./run_all.sh          # ~40 s end to end
```

Stages: corpus check → Q1 mining → Q2/Q3 controls → figures → backup → validation.
The environment is the Assignment-1 virtualenv, symlinked as `.venv` (numpy +
matplotlib only; see `requirements.txt`).

**Backups.** `src/package.py` writes gzipped copies of every result plus
SHA-256 checksums to `backup/`, with `backup/MANIFEST.latest.json`.

---

## Layout

```
A2/
├── README_SUBMISSION.md
├── run_all.sh · requirements.txt
├── src/
│   ├── corpus.py            loads the A1 table, asserts binary membership
│   ├── fism.py              Q1 — Apriori from scratch + brute-force verification
│   ├── random_controls.py   Q2 + Q3 — the three randomised controls
│   ├── plots.py             Q2 + Q3 figures
│   ├── package.py           backups + checksums
│   └── validate.py          22-check validation gate
├── outputs/{Q1,Q2,Q3}/      GRADED DELIVERABLES
├── outputs/VALIDATION_REPORT.json
├── data/random_controls.json
└── backup/
```
