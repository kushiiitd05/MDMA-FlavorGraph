# Q1(c) — Support and confidence in item-set mining &nbsp;&nbsp;[2 marks]

All figures below are computed from this submission's own corpus:
**N = 11,934 recipes** (the Assignment-1 deliverable), where each recipe is a
*transaction* and each ingredient is an *item*.

---

## Support — a property of an ITEM SET

**Support of an item set `X` is the fraction (equivalently, the number) of
transactions that contain every item in `X`.** It measures how *common* a
combination is.

```
support_count(X) = | { R ∈ D : X ⊆ R } |

support(X)       = support_count(X) / |D|
```

where `D` is the set of all transactions (recipes) and `|D| = N = 11,934`.

**Worked example from this corpus**

| Item set X | support_count(X) | support(X) |
|---|---|---|
| {garlic} | 3,459 | 3,459 / 11,934 = **0.2898** |
| {butter} | 3,440 | **0.2882** |
| {egg} | 2,793 | **0.2340** |
| {butter, egg} | 1,572 | 1,572 / 11,934 = **0.1317** |
| {butter, egg, plain flour} | 719 | **0.0602** |

So *butter and egg occur together in 13.17% of all recipes.*

An item set is called **frequent** when `support(X) ≥ min_support`, a threshold
fixed in advance. This submission uses `min_support = 0.1% = 12 recipes` for the
mined Apriori run.

**Why support is the quantity Apriori prunes on.** Support is *anti-monotone*
(downward-closed): adding an item can never increase support, so

```
X ⊆ Y   ⟹   support(X) ≥ support(Y)
```

Therefore if any subset of a candidate is infrequent, the candidate cannot be
frequent and is discarded without being counted. In this run that pruned
**544,495 of 629,234** candidate 3-item sets — 86.5% — before a single pass over
the data. Verified in the corpus: `support({butter, egg}) = 1,572 ≤ min(3,440, 2,793)`.

---

## Confidence — a property of an ASSOCIATION RULE

**Confidence of a rule `X → Y` is the fraction of the transactions containing `X`
that also contain `Y`.** It measures how *reliable* the implication is — a
conditional probability estimate, `P(Y | X)`.

```
confidence(X → Y) = support(X ∪ Y) / support(X)
                  = support_count(X ∪ Y) / support_count(X)
                  ≈ P(Y | X)
```

**Worked example from this corpus**

```
rule:  self-raising flour → egg

support_count({self-raising flour, egg}) = 630
support_count({self-raising flour})      = 775

confidence = 630 / 775 = 0.8129
```

**81.3% of recipes that use self-raising flour also use egg** — a strong baking rule.

---

## The three distinctions that matter

**1. Support describes a set; confidence describes a directed rule.**
`{A, B}` has one support. The pair yields *two* rules, `A → B` and `B → A`.

**2. Confidence is NOT symmetric.** Same item set, same support, very different
confidences, because the denominators differ:

| Rule | Computation | Confidence |
|---|---|---|
| self-raising flour → egg | 630 / 775 | **0.8129** |
| egg → self-raising flour | 630 / 2,793 | **0.2256** |

Knowing a recipe uses self-raising flour tells you a great deal about egg; the
reverse tells you little, because egg is common in its own right.

**3. Support is anti-monotone; confidence is not.** This is exactly why Apriori
mines frequent item sets by support first, and only then generates rules and
filters them by confidence.

---

## A caveat worth one extra line

High confidence alone can mislead when the consequent is simply very common.
`butter → egg` has confidence 0.4570, which looks respectable — but egg already
appears in 23.4% of all recipes anyway. **Lift** corrects for this:

```
lift(X → Y) = confidence(X → Y) / support(Y)
```

| Rule | Confidence | support(Y) | Lift |
|---|---|---|---|
| self-raising flour → egg | 0.8129 | 0.2340 | **3.47** |
| butter → egg | 0.4570 | 0.2340 | 1.95 |
| garlic → olive oil | 0.4545 | 0.2644 | 1.72 |

Lift > 1 means the two co-occur more than independence would predict. All 80
rules computed from this corpus, with support, confidence and lift, are in
`Q1c_association_rules.csv`.
