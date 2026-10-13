# References — Q4–Q8 (and pipeline methodology)

All sources below were actually retrieved and read during this assignment.
Nutrient figures in Q4 come from a live API query cached in `data/external/usda/`.

## Q4 — Nutrition data
1. **USDA FoodData Central, SR Legacy.** Retrieved 2026-09-08 via
   `https://api.nal.usda.gov/fdc/v1/food/{fdcId}`.
   - Egg, whole, cooked, hard-boiled — **FDC ID 173424**
   - Rice, white, long-grain, regular, enriched, cooked — **FDC ID 168878**
   - Pigeon peas (red gram), mature seeds, cooked, boiled, without salt — **FDC ID 172437**
   Raw responses: `data/external/usda/*.json`; derived table: `theory/Q4_nutrition_data.json`.
2. **Indian Food Composition Tables (IFCT) 2017**, T. Longvah *et al.*, National Institute of
   Nutrition, ICMR, Hyderabad. <https://www.nin.res.in/ebooks/IFCT2017.pdf> — used for the
   cereal/pulse amino-acid complementation argument (lysine vs methionine).
3. **FAO/WHO** protein quality evaluation (PDCAAS/DIAAS framework) — basis for the statement
   that egg protein is the reference-quality protein.

## Q5 — Uncommon ingredients
4. **Cucumis callosus (kachri)** — "Pharmacological and Therapeutic Potential of *Cucumis
   callosus*: a Novel Nutritional Powerhouse…", *Plant Foods for Human Nutrition*, 2023.
   PubMed 37698772. <https://link.springer.com/article/10.1007/s11130-023-01098-y>
5. **Momordica dioica (kartoli/spine gourd)** — "Nutritional Composition of *Momordica dioica*
   fruits", *J. Food Pharm. Sci.* <https://journal.ugm.ac.id/jfps/article/download/6452/5910>;
   and "Phytochemical, Phytotherapeutical and Pharmacological Study of *Momordica dioica*",
   PMC4145798.
6. **Hibiscus sabdariffa (gongura/ambaadi)** — "South Indian leafy vegetable Gongura
   (*Hibiscus sabdariffa* L.) as an important medicinal herb: a review", 2018.
7. **Buchanania lanzan (chironji/charoli)** — "Nutraceutical potential and phytochemical
   screening of *Buchanania lanzan*…", *J. Pharmacogn. Phytochem.* 2015; and "Chironji
   (*Buchanania lanzan*) Wonder Tree: Nutritional and Therapeutic Values", *IJCMAS* 9(2), 2020.
8. **Garcinia indica (kokum)** — "Evaluation of bioactive constituents of *Garcinia indica*
   (kokum) as a potential source of hydroxycitric acid, anthocyanin, and phenolic compounds",
   *LWT — Food Science and Technology*, 2022.

> ⚠ Q5 is a **personal/cultural** question. The shortlist above is research-backed but the
> student must confirm genuine family/regional familiarity before submitting.

## Q6 — Truth or myth
9. **Microwave / cooking-method nutrient retention:** Yuan G-F, Sun B, Yuan J, Wang Q-M.
   "Effects of different cooking methods on health-promoting compounds of broccoli."
   *Journal of Zhejiang University SCIENCE B*, 2009; **10(8):580–588.** PMC2722699.
   → vitamin C loss: boiling 33 %, stir-fry 24 %, **microwaving 16 %**, steaming ≈ 0 %;
     total aliphatic glucosinolates: **microwaving 60 % loss**, steaming ≈ unchanged.
10. **Refrigerated storage / ascorbate:** "Novel insights into ascorbate retention and
    degradation during the washing and post-harvest storage of spinach and other salad
    leaves", PMC5441274 → salad leaves lost **35–86 % ascorbate over 10 d at 4 °C**.
11. **Refrigerated storage / phenolics:** "Storage of Fruits and Vegetables in Refrigerator
    Increases their Phenolic Acids but Decreases the Total Phenolics, Anthocyanins and
    Vitamin C with Subsequent Loss of their Antioxidant Capacity", PMC5618087.
12. **GM crops:** National Academies of Sciences, Engineering, and Medicine (2016).
    ***Genetically Engineered Crops: Experiences and Prospects.*** Washington DC:
    The National Academies Press. <https://nap.nationalacademies.org/catalog/23395>
    (Human-health chapter: NCBI Bookshelf **NBK424534**.) → no substantiated evidence of a
    difference in human-health risk vs conventionally bred crops.
13. **WHO** — Food, genetically modified (Q&A): no adverse health effects reported from
    GM foods currently on the market; case-by-case assessment under **Codex Alimentarius**
    guidelines.

## Q7 — Calorimetry
14. Standard bomb-calorimetry method; **benzoic acid** as the certified calibration standard.
15. **Atwater general factors** (4/9/4 kcal g⁻¹ for protein/fat/carbohydrate, 2 kcal g⁻¹ for
    fibre) — FAO, *Food energy — methods of analysis and conversion factors*, FAO Food and
    Nutrition Paper 77, Rome, 2003.

## Methodology (Q1–Q3 pipeline)
16. **Diwan N., Batra P., Bagler G.** "Deep Learning Based Named Entity Recognition Models
    for Recipes." **arXiv:2402.17447** (2024).
    → tag set NAME/QUANTITY/UNIT/STATE/SIZE/TEMP/DF; **spaCy-transformer best at 95.9 %
    macro-F1**, ahead of Stanford NER 95.5 %, flair 95.0 %, BERT 94.0 %.
    *(Cited for methodology only. Their corpus is RecipeDB-derived, which this assignment
    forbids, so TASTEset is used as an independent substitute.)*
17. **TASTEset** — Wróblewska A. *et al.*, "TASTEset — Recipe Dataset and Food Entities
    Recognition Benchmark", **arXiv:2204.07775**. Data: <https://github.com/taisti/TASTEset>
    (**MIT licence**), 700 annotated ingredient blocks.
18. **schema.org/Recipe** structured-data vocabulary — the JSON-LD schema parsed from
    BBC Good Food pages. <https://schema.org/Recipe>
19. **spaCy v3.8** — Honnibal & Montani, industrial-strength NLP. <https://spacy.io>
