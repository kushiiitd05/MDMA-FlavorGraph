# CGAS / BIO544 — Assignment 1 Learning & Execution Map
**Course:** Computational Gastronomy, Monsoon 2026  
**Assignment:** A1  
**Status:** Separate assignment-only SSOT  
**Purpose:** Learn the minimum necessary concepts quickly, freeze decisions, then create one high-quality Claude Max master prompt to implement the assignment reproducibly.

---

# 0. Assignment Source of Truth

The uploaded assignment PDF is the only authoritative source for rubric requirements.

Core requirements:

## Q1 — Recipe corpus + NER
- Scrape **10,000 recipes**.
- Preserve raw data.
- Include:
  - recipe titles,
  - ingredient phrases,
  - cooking instructions,
  - other relevant details.
- Extract **ingredient names** from ingredient phrases using **Named Entity Recognition**.
- Store recipes in:
  - `Recipe ID — Ingredient Name` form.
- **Do not use/scrape RecipeDB.**

## Q2 — Basic corpus analysis
- Number of unique ingredients.
- Ingredient frequencies.
- Recipe-size distribution.
- Average recipe size.
- Cumulative recipe-size distribution.
- Properly labelled plots.

## Q3 — Frequency-rank distribution
- Plot ingredient frequency vs rank.
- Scale axes appropriately.
- Label axes properly.

## Q4–Q8 — Handwritten/scanned component
One scanned handwritten PDF covering:
- boiled egg vs boiled rice + daal nutrition,
- five uncommon/local ingredients,
- three science truth/myth statements,
- calorific-content measurement technique,
- eight narrow Computational Gastronomy technologies/products.

---

# 1. Working Philosophy

The implementation agent should **not jump directly to coding**.

The desired workflow is:

```text
READ ASSIGNMENT
      ↓
LEARN REQUIRED CONCEPTS
      ↓
RESEARCH / VERIFY CURRENT DETAILS
      ↓
FREEZE DESIGN DECISIONS
      ↓
PLAN OUTPUTS
      ↓
IMPLEMENT
      ↓
VALIDATE
      ↓
PACKAGE SUBMISSION
```

The final Claude Max prompt must explicitly instruct Claude to:

1. first study/research each required technical area,
2. summarize what it learned,
3. inspect the chosen data source,
4. freeze assumptions/definitions,
5. only then write code and execute the assignment,
6. validate every deliverable against the rubric.

---

# 2. A1 Learning Map — Fast, Not Deep

We only learn enough to:
- understand the assignment,
- make correct design choices,
- direct Claude properly,
- verify Claude's work.

```text
A1-L0  Rubric and deliverables
   ↓
A1-L1  Web scraping fundamentals
   ↓
A1-L2  Recipe data schema
   ↓
A1-L3  Ingredient phrase anatomy
   ↓
A1-L4  Ingredient NER
   ↓
A1-L5  Ingredient normalization
   ↓
A1-L6  Recipe–ingredient representation
   ↓
A1-L7  Ingredient frequency
   ↓
A1-L8  Recipe-size distribution
   ↓
A1-L9  CDF / CCDF
   ↓
A1-L10 Frequency-rank distribution
   ↓
A1-L11 Nutrition comparison
   ↓
A1-L12 Local/uncommon ingredients
   ↓
A1-L13 Nutrition myths / evidence reasoning
   ↓
A1-L14 Calorimetry
   ↓
A1-L15 Eight CGAS technologies
   ↓
DECISION FREEZE
   ↓
CLAUDE MAX MASTER PROMPT
   ↓
IMPLEMENT + VALIDATE + PACKAGE
```

---

# 3. A1-L0 — Rubric & Deliverable Map

Before implementation, create a checklist:

```text
Q1a raw recipe dataset
Q1b ingredient NER script/model/output
Q1c RecipeID–IngredientName file

Q2a unique ingredients + frequencies file
Q2b recipe-size distribution plot + mean size
Q2c cumulative recipe-size distribution plot

Q3a frequency-rank plot

Q4–Q8 handwritten scanned PDF
```

Naming should follow question numbers.

Recommended folders:

```text
A1/
├── README.md
├── requirements.txt
├── config/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
├── src/
│   ├── scrape/
│   ├── ner/
│   ├── normalize/
│   └── analysis/
├── outputs/
│   ├── Q1/
│   ├── Q2/
│   └── Q3/
├── handwritten/
├── logs/
└── backup/
```

---

# 4. A1-L1 — Web Scraping Fundamentals

Learn only these concepts:

## HTTP
A browser/script requests a URL and receives a response:
- status code,
- HTML,
- headers,
- possibly JSON.

## HTML / DOM
Webpages are structured trees of:
- tags,
- attributes,
- nested elements.

## `requests`
Downloads page content.

## BeautifulSoup
Parses HTML and lets us:
- find tags,
- inspect attributes,
- select elements,
- extract embedded structured data.

BeautifulSoup itself does **not** download pages.

## CSS selectors
Useful for extracting repeated page elements.

## JSON-LD
Many recipe pages expose structured recipe metadata in:

```html
<script type="application/ld+json">
```

Often contains Schema.org `Recipe` fields such as:
- `name`,
- `recipeIngredient`,
- `recipeInstructions`,
- `prepTime`,
- `cookTime`,
- `recipeYield`,
- `nutrition`.

Preferred strategy:
1. fetch page,
2. parse with BeautifulSoup,
3. check JSON-LD first,
4. fallback to HTML selectors only when needed.

## Pagination / discovery
Need a repeatable way to find 10,000 recipe URLs:
- category pages,
- pagination,
- sitemap,
- index pages.

## Respectful crawling
Before selecting a source:
- inspect `robots.txt`,
- inspect site terms,
- use delays/rate limits,
- identify yourself appropriately if required,
- avoid excessive concurrency,
- add retries/backoff.

## Resumability
10,000 recipes is not a small one-shot script.

Save progress:
- after every N pages,
- store visited URLs,
- store failures,
- allow restart without duplicating data.

## Deduplication
Check at minimum:
- canonical URL,
- recipe title + ingredient signature,
- duplicate content hashes if needed.

## Provenance
Every recipe should retain:
- source URL,
- source site,
- scrape timestamp.

---

# 5. A1-L2 — Raw Recipe Schema

Freeze schema **before scraping**.

Recommended raw record:

```yaml
recipe_id:
source_url:
source_site:
title:
ingredient_phrases:
instructions:
prep_time:
cook_time:
total_time:
yield:
cuisine:
category:
nutrition:
date_scraped:
raw_jsonld:
```

Important rule:

> Never overwrite or discard raw ingredient phrases after NER.

Keep raw and derived data separately.

---

# 6. A1-L3 — Ingredient Phrase Anatomy

Example:

```text
"2 cups finely chopped red onions"
```

Possible fields:

```text
quantity      = 2
unit          = cups
preparation   = finely chopped
modifier      = red
ingredient    = onions
```

A1 specifically wants the **ingredient name**.

Other examples:

```text
"1 tbsp extra-virgin olive oil"
→ olive oil

"3 cloves garlic, minced"
→ garlic

"salt to taste"
→ salt
```

---

# 7. A1-L4 — Named Entity Recognition

NER identifies spans belonging to semantic entity classes.

For this assignment, define:

```text
INGREDIENT
```

Example:

```text
2 cups finely chopped [red onions]INGREDIENT
```

## Terms to know
- token,
- entity span,
- start/end offset,
- BIO/IOB tagging.

Example BIO:

```text
red      B-INGREDIENT
onions   I-INGREDIENT
```

## Important warning
Generic English NER models usually target:
- person,
- organization,
- location,
- etc.

They are not automatically ingredient recognizers.

Potential strategies:
1. custom spaCy NER,
2. food-domain pretrained NER,
3. transformer token classification,
4. rules + NER hybrid.

## Evaluation
Create a manually labelled validation subset.

Measure:
- precision,
- recall,
- F1,
- boundary errors.

Do not claim NER works based on a few examples.

---

# 8. A1-L5 — Ingredient Normalization

NER extraction is not the same as canonicalization.

Possible outputs:

```text
red onion
onions
fresh onion
onion
```

may need to map to:

```text
onion
```

Internal pipeline:

```text
raw phrase
   ↓
NER surface span
   ↓
normalized form
   ↓
canonical ingredient
```

Keep all three internally.

Possible normalization:
- lowercase,
- punctuation cleanup,
- lemmatization,
- remove preparation words,
- synonym table,
- plural normalization.

Do not over-normalize:
- `red wine` ≠ `wine vinegar`
- `coconut milk` ≠ `milk`
- `black pepper` ≠ `peppercorn sauce`

---

# 9. A1-L6 — Recipe–Ingredient Representation

Required assignment structure:

```text
RecipeID,IngredientName
```

Example:

```text
R000001,onion
R000001,tomato
R000001,cumin
R000002,rice
R000002,lentil
```

Computationally this is a recipe–ingredient bipartite edge list.

Useful internal columns:

```text
recipe_id
raw_phrase
extracted_name
canonical_name
source_url
```

---

# 10. A1-L7 — Ingredient Frequency

Freeze definition.

Recommended primary definition:

\[
f_i=
\#\{\text{recipes containing ingredient }i\}
\]

This is **recipe frequency**.

Different from:

\[
\text{raw mention count}.
\]

If one ingredient is mentioned twice inside one recipe, recipe frequency normally counts that recipe once.

Output:

```text
ingredient,frequency
onion,3560
garlic,2981
...
```

---

# 11. A1-L8 — Recipe Size

For recipe `R`:

\[
s_R=
\text{number of canonical ingredients in recipe }R
\]

Recommended:
- count unique canonical ingredient entities,
- document the definition.

Average:

\[
\bar{s}
=
\frac{1}{N}\sum_R s_R
\]

Also calculate internally:
- median,
- min,
- max,
- quantiles.

Required plot:
- recipe size on x-axis,
- number/proportion of recipes on y-axis.

---

# 12. A1-L9 — Cumulative Distribution

CDF:

\[
F(s)=P(S\le s)
\]

means:

> fraction of recipes having size less than or equal to `s`.

CCDF:

\[
P(S\ge s)
\]

means:

> fraction of recipes with size at least `s`.

Assignment says "cumulative distribution"; default should be CDF unless course notes clearly indicate CCDF.

Final prompt should instruct Claude to:
- inspect course examples if available,
- otherwise use a properly labelled CDF,
- optionally provide CCDF as supplementary analysis.

---

# 13. A1-L10 — Frequency-Rank Distribution

Sort ingredients by descending frequency:

\[
f_{(1)}\ge f_{(2)}\ge\cdots
\]

Assign:

```text
rank 1 → most frequent ingredient
rank 2 → second most frequent
...
```

Plot:

\[
rank \text{ vs } frequency
\]

Important:
- test linear and log/log visualizations,
- choose scale appropriate to distribution,
- label axes clearly,
- do not claim "power law" or "Zipf's law" only because the plot looks roughly straight.

---

# 14. A1-L11 — Nutrition Comparison

Compare:
- boiled egg,
- boiled rice + daal.

Need a fair comparison basis:
- per 100 g, or
- clearly defined serving.

Compare:
- calories,
- protein,
- carbohydrates,
- fat,
- fiber,
- selected micronutrients.

State:
- serving assumptions,
- data source,
- whether values are cooked-food values.

---

# 15. A1-L12 — Five Uncommon / Local Ingredients

For each:

```text
local / vernacular name
English/common name
seasonal use
nutrition
source
```

"Uncommon" is contextual:
- uncommon nationally/globally,
- but known locally/familially.

Prefer ingredients the student genuinely knows from family/local food culture.

---

# 16. A1-L13 — Truth / Myth Reasoning

Statements:
1. microwaving destroys nutritional value,
2. refrigeration destroys nutritional value,
3. genetic modification is bad.

Answer pattern:

```text
Claim
↓
Mechanism
↓
Scientific evidence
↓
Context / exceptions
↓
Verdict
```

Avoid absolute yes/no claims where evidence is conditional.

---

# 17. A1-L14 — Calorific Content

Core technique:
**bomb calorimetry**

Concept:
1. known mass of food is combusted,
2. released heat warms surrounding water/calorimeter,
3. temperature rise is measured,
4. heat released is calculated.

Important distinction:
- gross combustion energy,
- metabolizable energy used in nutrition labels.

---

# 18. A1-L15 — Eight Narrow CGAS Technologies

Need narrow product concepts, not generic:
- "AI food app",
- "smart kitchen",
- "recipe chatbot".

Candidate directions:

1. Process-conditioned flavor substitution engine.
2. State-aware cooking mistake recovery assistant.
3. Long-tail regional ingredient identifier.
4. Aroma-aware doneness/end-point predictor.
5. Cuisine-authenticity pair/triplet analyzer.
6. Nutritionally constrained recipe transformation system.
7. Evidence-grounded cooking-process substitution engine.
8. Leftover-state recovery / food-waste recipe planner.

Final answers should be 1–3 lines each.

---

# 19. Decision Freeze Before Master Prompt

The final master prompt must not be written until these are fixed:

## D1 — Recipe source
Need:
- not RecipeDB,
- access permitted,
- ≥10,000 unique recipes feasible,
- stable HTML/JSON-LD,
- ingredient + instruction completeness.

## D2 — Scraping strategy
- URL discovery,
- JSON-LD first,
- HTML fallback,
- rate limit,
- retries,
- resumability.

## D3 — Raw schema
Freeze fields.

## D4 — NER strategy
Choose:
- pretrained/custom/hybrid,
- labelled subset size,
- evaluation plan.

## D5 — Canonicalization
Freeze rules.

## D6 — Frequency definition
Recommended:
- number of recipes containing ingredient.

## D7 — Recipe size
Recommended:
- unique canonical ingredients per recipe.

## D8 — CDF convention
Default:
- CDF unless course context indicates otherwise.

## D9 — Rank plot
Freeze:
- raw and log/log exploratory,
- one clearly labelled submission plot.

## D10 — Q4–Q8 evidence plan
Freeze trustworthy sources and final handwritten wording.

---

# 20. Claude Max Master Prompt — Required Behaviour

The later prompt must tell Claude:

```text
DO NOT IMMEDIATELY CODE.

STEP 1
Read the assignment and restate every deliverable.

STEP 2
Research/study:
- scraping,
- candidate data source,
- JSON-LD,
- NER,
- ingredient normalization,
- recipe-size statistics,
- rank distributions,
- nutrition evidence,
- calorimetry.

STEP 3
Produce a short design report:
- assumptions,
- chosen source,
- NER plan,
- schemas,
- metric definitions,
- file tree,
- validation plan.

STEP 4
Freeze design.

STEP 5
Implement reproducibly.

STEP 6
Run validations.

STEP 7
Generate final files matching rubric.

STEP 8
Create a final submission checklist.
```

Claude should act like:
- researcher,
- data engineer,
- NLP engineer,
- analyst,
- verifier.

Not merely a code generator.

---

# 21. Validation Gate

Before submission, verify:

```text
>= 10,000 unique valid recipes
0 RecipeDB records
stable RecipeIDs
source URL for every recipe
raw ingredient phrases preserved
instructions preserved
duplicate rate checked
NER manually evaluated
RecipeID–Ingredient file valid
ingredient frequencies reproducible
recipe-size distribution reproducible
average recipe size reproducible
CDF labelled
frequency-rank plot labelled/scaled
all required Q1–Q3 files exist
Q4–Q8 handwritten scanned PDF prepared
backup exists
```

---

# 22. Our Immediate Study Order

We will now study each block **briefly**, not like the main research roadmap.

Current position:

\[
\boxed{\text{A1-L1 — Web Scraping}}
\]

Then:

```text
A1-L2 Recipe schema
A1-L3 Ingredient phrase anatomy
A1-L4 NER
...
```

After all blocks are understood well enough to direct implementation:

\[
\boxed{\text{WRITE FINAL CLAUDE MAX MASTER PROMPT}}
\]
