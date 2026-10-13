# R3 / D3 — Cooking Reaction Chemistry, Kinetics, Heat/Mass Transfer, and Dataset Extraction

**Commissioned:** 2026-09-03  
**Scope:** Computational Gastronomy v4 process/state model  
**Status vocabulary:** **[E] established**, **[I] inferred from evidence**, **[A] proposed assumption/design choice**, **[U] unverified**

## 1. Commissioning Question

How should `T(S_t, P_t, θ_t)` represent cooking as a physically grounded transition from ingredient state to processed state, using reaction chemistry, enzyme activity, heat/mass transfer, and empirical raw-versus-processed measurements?

Specific roadmap questions:

- **Q-P2:** How many peer-reviewed raw-versus-processed GC-MS comparisons can realistically be extracted per ingredient?
- **Q-P3:** What is the minimum viable process-effect schema that remains honest about uncertainty?
- **Q-P5:** Which ten ingredient×process cells provide the most scientific leverage per unit of curation?

## 2. Executive Findings

1. **[E] A cooking method name is not a chemical cause.** The defensible causal chain is:

   \[
   P \rightarrow \theta(x,t)
   \rightarrow \text{accessible mechanism classes}
   \rightarrow \text{formation, depletion, transfer, or physical reorganization}
   \]

   where `θ` includes local temperature history, moisture/water activity, pH, oxygen exposure, fat phase, pressure, geometry, precursor concentrations, enzyme state, and heating/cooling rates.

2. **[E] “Browning” is not one reaction.** Maillard chemistry, caramelization, ascorbate degradation, lipid oxidation, pigment degradation, and enzymatic browning can occur together and share products such as carbonyls and furans. HMF, colour, or total pyrazines cannot individually identify a unique pathway.

3. **[E] Product abundance is often non-monotonic.** Formation and destruction occur simultaneously. Acrylamide and 2-acetyl-1-pyrroline can peak and then decline, so “hotter means more” is unsafe.

4. **[E] Wet cooking does not prohibit Maillard chemistry.** It generally limits exposed wet regions through evaporative cooling and dilution, but long time, concentrated boundary layers, pressure, pH, and precursor composition can still produce Maillard products below customary roasting temperatures.

5. **[E] Protein denaturation, collagen solubilization, and starch gelatinization are matrix-dependent transitions, not universal temperature switches.** Time, pH, ionic strength, hydration, cultivar/species, and prior treatment matter.

6. **[E] Cutting can initiate chemistry before heating.** Compartment disruption activates alliinase, myrosinase, LOX/HPL, and PPO systems. Heating subsequently changes both reaction rate and enzyme survival.

7. **[I] Existing literature can support a sparse process-effect graph, not a complete 30–50 ingredient × 8–12 process quantitative matrix.** Common ingredients may yield several usable paired studies; many long-tail ingredients will yield none.

8. **[E] RDKit reaction SMARTS and `RunReactants` can encode curated local transformations, but they do not predict cooking conditions, rates, competing pathways, transport, phase behavior, or yields.** They should implement mechanism templates after pathway selection, not act as the cooking simulator.

## 3. Process-Mechanism Taxonomy

| Transition family | Required drivers | Representative outcomes | Representation |
|---|---|---|---|
| Maillard/glycation | carbonyl precursor, available amino group, temperature-time, pH, `a_w` | Amadori/Heyns products, dicarbonyls, Strecker aldehydes, pyrazines, furans, melanoidins, acrylamide | Reaction network |
| Sugar thermal degradation/caramelization | sugars, temperature-time, water, acid/base conditions | dehydration, fragmentation, HMF/furfural, acids, condensates, colour | Reaction network |
| Lipid oxidation/decomposition | unsaturation, O₂, metals, antioxidants, heat, interfaces | hydroperoxides, aldehydes, ketones, alcohols, furans, acids | Radical network |
| Protein structural transition | protein identity, temperature-time, pH, salt | unfolding, aggregation, gelation, water expulsion | State transition |
| Collagen conversion | collagen maturity/crosslinks, temperature-time, water, pH | shrinkage, denaturation, solubilization, gelatin | State + hydrolysis |
| Starch transition | botanical source, water availability, temperature-time, shear | swelling, gelatinization, leaching, pasting, retrogradation | Phase/state transition |
| Enzymatic cutting chemistry | tissue disruption, substrate/enzyme colocation, O₂, pH, temperature | sulfur volatiles, isothiocyanates, C₆ aldehydes, quinones | Enzyme-gated reaction |
| Fermentation | inoculum/community, substrate, pH, temperature, salt, O₂, time | acids, ethanol, CO₂, esters, alcohols, carbonyls, proteolysis | Biological reaction network |
| Volatile/material transfer | partition coefficients, diffusion, convection, boiling, fat/protein binding | evaporation, steam stripping, leaching, retention, redistribution | Mass-transfer edges |
| Pigment/cell-wall change | pH, temperature-time, enzymes, ions | pheophytinization, anthocyanin state changes, pectin depolymerization, softening | Chemical + structural transition |

## 4. Core Formulas

Local heat transfer:

\[
\rho c_p\frac{\partial T}{\partial t}
=\nabla\cdot(k\nabla T)+\dot q
\]

A surface energy balance must include convection, radiation/contact heating, and evaporation:

\[
-k\nabla T\cdot n
=h(T_s-T_\infty)+q''_{\mathrm{rad/contact}}-\dot m''_{\mathrm{evap}}L_v
\]

Moisture transport can begin with:

\[
\frac{\partial X}{\partial t}
=\nabla\cdot(D_{\mathrm{eff}}\nabla X)
\]

For a calibrated reaction:

\[
k(T)=A\exp\left(-\frac{E_a}{RT}\right), \qquad
r_j=k_j(T)\,f_j(C,pH,a_w,O_2,\text{phase})
\]

A local thermal-reaction exposure is therefore:

\[
\Omega_j(x)=\int_0^{t_f}
A_j e^{-E_{a,j}/RT(x,t)}
f_j(C(x,t),pH(x,t),a_w(x,t),O_2(x,t))\,dt
\]

For products that are both formed and destroyed:

\[
\frac{dC_P}{dt}=r_{\mathrm{formation}}-r_{\mathrm{consumption}}
-r_{\mathrm{volatilization}}-r_{\mathrm{leaching}}
\]

**[E] Consequence:** air temperature or oil temperature alone cannot determine reaction extent. The model needs at least estimated surface/core temperature histories and moisture state.

## 5. Reaction and Transformation Chemistry

### 5.1 Maillard Network

**[E] Foundational sequence:** reducing carbonyl + amino group → glycosylamine/Schiff base → Amadori product for aldoses or Heyns product for ketoses → enolization, dehydration and fragmentation → reactive α-dicarbonyls → Strecker products, heterocycles, and polymers. This structure originates in [Hodge’s experimental scheme](https://doi.org/10.1021/jf60015a004).

A simplified pathway is:

\[
\mathrm{R{-}CHO+R'NH_2 \rightleftharpoons R{-}CH{=}NR'+H_2O}
\]

\[
\mathrm{Amadori/Heyns}
\rightarrow
\{\mathrm{glyoxal,\ methylglyoxal,\ 3\!-\!deoxyglucosone,\ furfurals,\ reductones}\}
\]

\[
\alpha\text{-dicarbonyl}+\text{amino acid}
\rightarrow
\text{Strecker aldehyde}+CO_2+\alpha\text{-aminoketone}
\]

Condensation of α-aminoketones produces dihydropyrazines and then pyrazines. Isotope/model-system work shows that pyrazine substituents can also incorporate Strecker aldehydes and aldol-condensation products; precursor ratio and water alter the product pattern ([Adams et al.](https://doi.org/10.1021/jf0726785)).

**2-acetyl-1-pyrroline (2-AP):** **[E]** In a glucose/proline model, multiresponse kinetics identified glyoxal formation as rate-determining. Accumulation was highest at 100°C rather than 120–140°C because depletion accelerated at higher temperature ([Cai et al.](https://doi.org/10.1016/j.foodres.2024.114591)). This is direct evidence for formation-minus-loss modeling.

**HMF:** **[E]** HMF can arise through amino-carbonyl chemistry or sugar dehydration without amino compounds; it is therefore a heat-history indicator, not a Maillard-specific marker. In milk heated at 90–140°C, apparent formation `E_a` was 90.2 kJ/mol ([Claeys et al.](https://doi.org/10.1017/S0022029901004745)); in tomato products heated at 80–120°C it was 139.9 kJ/mol ([study](https://doi.org/10.1021/jf990120u)). The difference demonstrates matrix dependence.

**Acrylamide:** **[E]** Asparagine and reducing carbonyls generate acrylamide through early Maillard intermediates and decarboxylated Schiff-base chemistry ([Mottram et al.](https://doi.org/10.1038/419448a); [Stadler et al.](https://doi.org/10.1038/419449a)). In a low-moisture asparagine/glucose model, formation, elimination, and competing Maillard reactions were required; the competing Maillard rate had a maximum near `a_w = 0.82`, but this value is specific to that model, not a universal optimum ([Knol et al.](https://doi.org/10.1021/bp060389f)).

### 5.2 Caramelization

**[E]** Caramelization is amine-independent sugar degradation involving hydrolysis where applicable, enolization, dehydration, fragmentation, isomerization, oxidation/reduction, and condensation. Its products overlap with Maillard chemistry.

Concentrated neutral sucrose containing 16.32% water showed temperature-dependent degradation, HMF formation, and colour development over 100–160°C. Colour and sucrose loss had similar lag phases but different rates, proving that sucrose disappearance alone did not explain colour ([Quintas et al.](https://doi.org/10.1016/j.jfoodeng.2007.03.036)).

**Project rule:** assign “caramelization contribution” only where an amine-free control, precursor accounting, isotope evidence, or strongly supported sugar-only mechanism exists.

### 5.3 Lipid Oxidation and Thermal Degradation

\[
LH \rightarrow L^\bullet
\]

\[
L^\bullet+O_2\rightarrow LOO^\bullet
\]

\[
LOO^\bullet+LH\rightarrow LOOH+L^\bullet
\]

\[
LOOH\rightarrow LO^\bullet/LOO^\bullet
\rightarrow \text{aldehydes, ketones, alcohols, acids, furans}
\]

**[E]** Unsaturation, oxygen, heme/transition metals, hydroperoxide history, antioxidants, interfaces, and temperature jointly control the network. Hexanal is commonly associated with linoleate-derived oxidation but is not pathway-exclusive.

In beef brisket, roasting at 180°C versus boiling to matched core temperatures produced more aldehydes and pyrazines; hexanal increased with final core temperature, while boiling removed more fat and nucleotide compounds ([Utama et al.](https://doi.org/10.5713/ajas.17.0217)). Raw/cooked chicken work also found genotype-dependent PUFA loss and VOC production, showing that substrate composition can rival method effects ([Mancinelli et al.](https://doi.org/10.1016/j.psj.2020.10.030)).

### 5.4 Proteins and Collagen

**[E]** Denaturation is unfolding and association, not a single bond-cleavage reaction. Muscle proteins differ in thermal stability, and apparent transitions shift with species, pH, ionic strength, heating rate, and matrix.

Baltic herring DSC peaks were assigned at 39.59°C for myosin, 51.67°C for sarcoplasmic proteins, 63.16°C for connective tissue, and 74.40°C for actin ([study](https://doi.org/10.3390/foods10040829)); these values must not be transferred as universal meat thresholds.

Collagen conversion comprises helix denaturation/shrinkage followed by time-dependent solubilization or hydrolysis. Rabbit longissimus cooked at 77°C for one hour showed `75.3 ± 8.1%` collagen solubility, but temperature, animal age, muscle, and crosslink density limit transferability ([study](https://pubmed.ncbi.nlm.nih.gov/22063936/)).

### 5.5 Starch

**[E]** Gelatinization requires heat plus sufficient mobile water. It includes loss of crystalline order, granule swelling, amylose leaching, and viscosity development. These events need not coincide.

Wheat starch showed disruption of ordered structure at 50°C, below its DSC onset; time effects were stronger at 54–75% water than at 23–44% ([Wang et al.](https://pubmed.ncbi.nlm.nih.gov/30744867/)). A 2026 potato study measured DSC ranges of 62.3–74.0°C for isolated starch and 67.1–76.8°C for potato flour, with non-starch components restricting swelling and moderating retrogradation ([Aghajanzadeh et al.](https://doi.org/10.1016/j.foodchem.2026.149741)).

Retrogradation is post-cooking reassociation, initially dominated by amylose and later by amylopectin. It requires a storage-temperature/time state and cannot be inferred from the cooking endpoint alone.

### 5.6 Cutting Enzymes and Thermal Inactivation

| System | Cutting reaction | Heat behavior |
|---|---|---|
| Alliinase | alliin → allylsulfenic acid + pyruvate + NH₃; sulfenic acids condense to allicin | Garlic alliinase is thermolabile; purified-enzyme optimum was about 33°C ([study](https://pubmed.ncbi.nlm.nih.gov/17262455/)). Alliin itself also thermally degrades with reported `E_a = 142.494 kJ/mol` in 60–89°C solutions ([study](https://doi.org/10.1016/j.foodchem.2016.12.011)). |
| LOX/HPL | PUFA + O₂ → hydroperoxides → C₆/C₉ aldehydes/alcohols | Tomato showed multiple LOX/HPL fractions rather than simple first-order loss ([Anthon and Barrett](https://doi.org/10.1016/S0308-8146(02)00424-7)). Green-bean LOX yielded `E_a = 160.7 ± 8.1` or `164 ± 4.7 kJ/mol` depending fitting method ([study](https://doi.org/10.1046/j.1365-2621.2001.00472.x)); lupin seed/flakes gave 60.5/78.0 kJ/mol ([study](https://doi.org/10.1016/j.lwt.2015.11.052)). |
| Myrosinase | glucosinolate + water → unstable aglycone + glucose/sulfate → isothiocyanate, nitrile, or related product | Broccoli inactivation occurred over 30–60°C and required a consecutive-step model ([Ludikhuyze et al.](https://doi.org/10.1021/jf980964y)). Water content from 10–90% substantially altered inactivation rates ([Oliviero et al.](https://doi.org/10.1016/j.foodchem.2014.04.099)). |
| PPO | phenol + O₂ → quinone → polymeric brown products | Thermal resistance is commodity- and isoenzyme-specific: reported apparent `E_a` includes 64.22 kJ/mol for elephant-foot-yam PPO and 151.0 kJ/mol for sapota PPO ([yam](https://pubmed.ncbi.nlm.nih.gov/28720966/); [sapota](https://pubmed.ncbi.nlm.nih.gov/28098357/)). |

**[E] Conclusion:** “enzyme inactive above temperature X” is unacceptable without ingredient, assay, time, hydration, pH, and kinetic model.

### 5.7 Fermentation

Fermentation is a community-driven, open reaction network:

\[
\text{sugars}\rightarrow
\{\text{lactate, acetate, ethanol, CO₂, glycerol}\}
\]

\[
\text{amino acids/fatty acids}\rightarrow
\{\text{higher alcohols, aldehydes, acids, esters, sulfur compounds}\}
\]

In cassava starter experiments, yeast/LAB composition changed volatile outcomes; pH fell from 6.0 to 4.0–5.0 within 24 h, one co-culture reached 4.5 g/L lactic acid, and 22 volatiles were detected after 48 h ([Freire et al.](https://pubmed.ncbi.nlm.nih.gov/28455064/)). Twelve sourdough communities formed distinct volatile/acid clusters according to yeast and homo- or heterofermentative LAB dominance ([Warburton et al.](https://doi.org/10.1016/j.foodres.2022.111885)).

**Project implication:** fermentation state requires organism/community, inoculum, substrate, salt, oxygen, temperature, pH trajectory, and duration. “Fermented” alone is not a transferable process descriptor.

## 6. Dry Surfaces Versus Wet Interiors

**[E]** A wet surface spends incoming energy on evaporation. Its temperature can remain near the local wet-bulb or boiling condition until surface moisture flux declines. Once the surface dries, evaporation weakens and contact, convective, or radiative heating can raise it substantially above the interior.

A wet interior is constrained by:

- high effective heat capacity;
- latent heat and internal evaporation;
- slower conduction over distance;
- reactant dilution;
- migration of water and soluble precursors.

A pan-contact zone can nevertheless receive higher heat flux than oven air despite a lower nominal setpoint. Pressure, dissolved solutes, oil contact, crust porosity, and geometry shift all temperature histories.

**Decision:** reject universal folklore thresholds such as “Maillard starts at 140°C.” Store local time-temperature-moisture exposure and report only that a pathway becomes increasingly plausible under the measured conditions.

## 7. Volatile Loss During Boiling

A minimal component balance is:

\[
\frac{dn_{i,\mathrm{food}}}{dt}
=r_{i,\mathrm{form}}-r_{i,\mathrm{consume}}
-k_La(C_i-C_i^*)V-r_{i,\mathrm{leach}}
\]

**[E]** Apparent volatile decline can represent evaporation, steam stripping, dissolution into water, matrix binding, chemical conversion, or analytical partition changes. Protein and lipid matrices alter gas/matrix partition coefficients in compound-dependent ways ([interlaboratory study](https://pubmed.ncbi.nlm.nih.gov/20474045/)).

In 15 Brassica cultivars, cooking generally lowered major volatile abundance but increased isothiocyanates in many cultivars; all samples had first been frozen, creating an explicit pre-treatment confound ([Wieczorek and Jeleń](https://doi.org/10.3390/molecules24030391)).

**Decision:** boiling datasets must measure or explicitly mark unmeasured cooking liquor, condensate, lid state, water ratio, and headspace. “Vanished” must not mean “chemically destroyed.”

## 8. pH Effects on Colour and Softening

**[E] Chlorophyll:** heating broccoli juice converted chlorophylls to pheophytins with first-order apparent kinetics. Reported `E_a` values were `71.04 ± 4.89` and `67.11 ± 6.82 kJ/mol` for chlorophyll a/b degradation and `105.49 ± 4.74 kJ/mol` for subsequent pheophytin decomposition ([Weemaes et al.](https://doi.org/10.1021/jf980663o)). Acid released during cooking can therefore accelerate olive-green pheophytin formation.

**[E] Cell walls:** vegetable tissues in one cross-commodity experiment softened rapidly above pH 5 and below pH 3 but were relatively firm near pH 4. Neutral/alkaline conditions were associated with pectin β-elimination; strong acidity promoted hydrolysis and divalent-ion removal ([Fuchigami](https://doi.org/10.4327/jsnfs.36.219)). Common beans cooked faster in 0.1 M sodium bicarbonate, with pectin solubilization identified as the rate-limiting structural process ([study](https://pubmed.ncbi.nlm.nih.gov/29579956/)).

**Decision:** pH effects are non-monotonic and ion-dependent. Store pH trajectory, buffer/acid identity, calcium/magnesium, and tissue type.

## 9. Quantitative Evidence: Safe Use of Kinetics

| Target | Reported conditions | Apparent parameter | Interpretation |
|---|---|---:|---|
| HMF in milk | 90–140°C | 90.2 kJ/mol | Matrix-specific lumped formation |
| HMF in tomato products | 80–120°C | 139.9 kJ/mol | Demonstrates non-transferability |
| Browning in ascorbate/amino-acid models | 120–150°C, weak alkaline | 90.13–93.38 kJ/mol | Colour-model parameter, not universal Maillard `E_a` |
| Alliin thermolysis | 60–89°C solution | 142.494 kJ/mol | Substrate degradation, not alliinase inactivation |
| Green-bean LOX inactivation | non-isothermal food geometry | 160.7–164 kJ/mol | Depends on model-fitting method |
| Lupin LOX inactivation | seed versus de-oiled flake | 60.5 versus 78.0 kJ/mol | Matrix structure changes kinetics |
| PPO inactivation | yam versus sapota | 64.22 versus 151.0 kJ/mol | Wide commodity variability |
| Chlorophyll a/b degradation | broccoli juice, >60°C | 67–71 kJ/mol | Pigment-specific |
| Pheophytin degradation | broccoli juice | 105.49 kJ/mol | Different step, different sensitivity |

**[E] Rule:** store `E_a`, pre-exponential/reference rate, model form, temperature interval, matrix, pH, water state, confidence interval, and assay endpoint together. An isolated activation energy is not portable.

## 10. RDKit, Reaction SMARTS, Fingerprints, and Networks

**[E] Capabilities:** RDKit reaction SMARTS can encode atom-mapped reactant/product templates, and `RunReactants` enumerates products matching those templates. RDKit also provides reaction validation/sanitization and structural or reactant-minus-product difference fingerprints ([RDKit Book](https://www.rdkit.org/docs/RDKit_Book.html); [reaction API](https://rdkit.org/docs/source/rdkit.Chem.rdChemReactions.html)).

**Recommended use:**

- Encode curated elementary or lumped transformations such as carbonyl–amine condensation, amino-acid decarboxylation, oxidation, dehydration, or hydrolysis.
- Require atom mapping and provenance for every template.
- Run `Validate`, reaction sanitization, product sanitization, duplicate removal, and mass/charge checks.
- Use reaction difference fingerprints to cluster transformations and retrieve analogues.
- Store reactions as directed hyperedges because many transformations consume or produce multiple species.
- Retain class-level and unknown-product nodes where structures are unresolved.

**Do not use it to:**

- infer whether reactants coexist in the same phase;
- determine enzyme survival or tissue compartment disruption;
- model oxygen, water activity, heat transfer, radical propagation, equilibrium, or reaction rate;
- enumerate “all compounds produced by roasting”;
- infer yield from template match count.

**[I] Best architecture:** RDKit supplies the structural transformation layer after a condition-gated mechanism selector. Reaction fingerprints describe *what changed structurally*, while `θ` and empirical evidence estimate whether that edge is accessible.

## 11. Q-P2 — Realistic Paired-Study Coverage

**Established lower bounds from this scoped search, not a systematic census:**

| Ingredient family | Direct paired evidence found | Important warning |
|---|---|---|
| Rice | At least three raw/cooked GC-MS studies, covering 10, 26, and 27 varieties | Extraction method and cultivar reverse some apparent directions |
| Brassica vegetables | One study covering 15 cultivars raw/cooked | Samples were frozen before analysis |
| Beef | Multiple wet/dry cooking studies, including matched core temperatures | Muscle, ageing, fat, and endpoint differ |
| Chicken | At least one raw/cooked VOC study over four strains | Genotype and antioxidant status matter |
| Goat | One raw/grill/sous-vide/microwave study | One meat system cannot establish universal process effects |
| Pufferfish | One raw/boiled/steamed/microwaved/roasted comparison | Species-specific aquatic matrix |
| Fermented cabbage | One unheated/boiled/stir-fried comparison with 47 detected volatiles | Fermentation history is an additional process |

Rice demonstrates the harmonization problem sharply: one ten-variety HS-SPME study reported higher 2-AP after cooking ([Routray et al.](https://doi.org/10.3390/foods10081917)), while a 26-variety solvent-extraction study reported losses of 43.97–81.94% ([Zhao et al.](https://doi.org/10.1016/j.foodres.2022.111078)). These are not safely poolable without resolving method, variety, mass basis, and cooking protocol.

**Answer:** **[I]** plan for roughly **1–4 usable direct papers per mainstream ingredient in an initial curated pass and 0–1 for many long-tail ingredients**. Rice, meat, coffee, cocoa, and major Brassicas may exceed that. This is a planning estimate, not a bibliometric result. A dense 240–600-cell matrix cannot presently be assumed.

**[U]** The exact count per ingredient remains unanswered until a reproducible systematic search and duplicate-experiment audit is performed. No single authoritative open dataset covering the requested complete matrix was verified in this search; that is absence of confirmation, not proof that none exists.

## 12. Q-P3 — Minimum Honest Process-Effect Schema

| Block | Required fields |
|---|---|
| Provenance | paper/dataset DOI or accession, table/figure/file, curator, extraction date |
| Ingredient | scientific/common name, cultivar/breed, tissue/cut, maturity, origin, storage, batch |
| Initial state | raw/intact/cut/frozen/dried/fermented; moisture, `a_w`, pH, fat, salt; missingness flags |
| Process sequence | ordered unit operations, method label, medium, equipment, lid/atmosphere, pressure |
| Geometry | mass, thickness/diameter, surface area if known, whole/minced/pureed |
| Thermal drivers | source/setpoint, measured surface/core trajectory, duration, heating/cooling rates |
| Chemical drivers | initial/final pH, moisture/`a_w`, O₂ exposure, oil identity/uptake, precursor measurements |
| Observation | compound identifier, chemical class, concentration or peak area, basis, LOD/LOQ, censoring |
| Analytical method | extraction, fibre/solvent, GC column, MS mode, internal standard, RI, library, calibration |
| Contrast | matched raw comparator, same biological lot, processed/raw ratio or direction, uncertainty |
| Mechanism claim | formed, depleted, transferred, released, unknown; mechanism class; evidence tier |
| Quality flags | biological/technical replicates, randomization, cooking-liquor accounting, confounders |
| Licensing | article/data licence separately; do not infer reuse rights |

Use InChIKey plus original reported name; preserve stereochemistry and isomer uncertainty. Apply MSI-style identity levels: authenticated standard, putatively annotated compound, putative class, or unknown feature ([MSI chemical-analysis standard](https://doi.org/10.1007/s11306-007-0082-2)). Validate EI spectra and retention indices against an authoritative library such as [NIST Chemistry WebBook](https://doi.org/10.18434/T4D303).

## 13. Extraction Protocol for 30–50 Ingredients × 8–12 Processes

1. **[A] Matrix design:** start with 40 ingredients across starch staples, legumes, meats/fish, dairy/egg, Alliums/Brassicas, other vegetables, fruits, nuts/seeds, and fermentation substrates. Use 12 standardized states: raw-intact, cut/rested, boiled, steamed, pressure-cooked, roasted/baked, pan-sautéed, deep-fried, microwaved, sous-vide, fermented, and chilled/reheated. Treat the matrix as sparse; mark inapplicable cells explicitly.

2. **Search:** query ingredient scientific/common names with raw/fresh/control plus boiled, cooked, roasted, baked, fried, steamed, GC-MS, GC×GC, GC-O, PTR-MS, metabolomics, volatile, aroma, and supplementary data. Search references and cited-by records, then repositories.

3. **Include:** peer-reviewed experiments with a raw or pre-process comparator from the same study; sufficiently described process; compound-resolved results; and recoverable sample basis. Keep unmatched processed-only papers in a separate mechanism-evidence table.

4. **Exclude from quantitative pooling:** narrative compound lists, database-only assertions, unresolvable relative percentages, missing comparator, incompatible tissues, or process conditions too vague to reconstruct.

5. **Double extraction:** two curators independently enter protocol and analyte rows; reconcile ingredient identity, units, signs, and comparator matching. Preserve source values before transformations.

6. **Normalize cautiously:** calculate processed/raw change only for matched quantified measurements on the same basis. Keep wet-weight, dry-weight, total-serving, headspace area, and internal-standard ratios distinct. Model non-detects as censored intervals rather than zeros.

7. **Mass balance:** for boiling, collect food, cooking liquor, and where feasible condensate/headspace. For frying, measure oil uptake and analyte transfer to oil. Record yield/mass loss so concentration by dehydration is not mistaken for formation.

8. **Analytical core:** paired HS-SPME-GC-MS plus solvent extraction for volatile retention versus total extract; alkane retention indices; authentic standards for priority odorants; targeted LC-MS for acrylamide, HMF, Amadori markers, sugars, amino acids, and organic acids.

9. **Physical core:** log surface and core temperature, mass every defined interval, initial/final moisture and pH, geometry, medium temperature, ambient pressure, and oil/water ratio.

10. **Replication:** **[A]** use at least three independent biological lots, randomize process order, include pooled QC and blanks, and separate biological from injection replicates.

11. **Data release:** preserve vendor files and convert copies to open MS formats; publish sample metadata and processed tables through [MetaboLights](https://www.ebi.ac.uk/metabolights/) or [Metabolomics Workbench](https://www.metabolomicsworkbench.org/tools/MWRestAPIv1.0.pdf).

12. **Model output:** each cell produces observed deltas, uncertainty, mechanism-supported edges, unsupported hypotheses, and explicit missing drivers. It must not emit invented product concentrations.

## 14. Q-P5 — First Ten High-Leverage Cells

| Priority | Cell | Why it is high leverage | Primary measurements |
|---:|---|---|---|
| 1 | Rice × absorption boiling | Contradictory 2-AP evidence; starch retention and lipid oxidation | 2-AP, aldehydes, water loss, starch state |
| 2 | Potato × deep-frying | Couples heat/mass transfer, starch, oil uptake, Maillard and acrylamide | surface/core `T`, moisture profile, sugars, Asn, acrylamide, pyrazines |
| 3 | Potato × boiling | Wet control for the same precursor matrix | starch gelatinization, leaching, HMF/acrylamide non-detect limits |
| 4 | Broccoli × steaming | Myrosinase/ESP survival without immersion leaching | glucosinolates, ITCs/nitriles, enzyme activity, chlorophyll |
| 5 | Broccoli × boiling | Separates inactivation from leaching and volatile stripping | food + liquor mass balance, ITCs, sulfur VOCs, chlorophyll |
| 6 | Garlic × crush/rest then heat | Directly tests compartment disruption and alliinase timing | alliin, allicin, polysulfides, alliinase activity |
| 7 | Beef × roasting | Dense interaction of protein, lipid oxidation, Maillard, oxygen, and dry surface | aldehydes, pyrazines, Strecker products, TBARS, surface/core zones |
| 8 | Beef × boiling | Matched wet-process control for cell 7 | volatiles in meat/liquor, collagen solubility, nucleotides |
| 9 | Wheat dough × sourdough fermentation then baking | Links microbial precursors to crust Maillard products | acids, sugars, amino acids, fermentation VOCs, crust/crumb pyrazines/HMF/acrylamide |
| 10 | Cabbage × lactic fermentation | Provides a nonthermal transition and a substrate for later cooking | community, pH trajectory, acids, sulfur compounds, esters |

**[A]** Use the same cultivar/batch across paired wet/dry cells where possible. Analyze surface and interior separately for roasted/fried samples.

## 15. Recommended Decisions Versus Required Experiments

**Decisions recommended now**

- Represent cooking as condition-gated mechanism classes plus transport and physical-state transitions.
- Store process labels and causal drivers separately.
- Permit qualitative directions (`forms`, `depletes`, `transfers`, `released`, `unknown`) before quantitative yields.
- Model competing formation and loss.
- Keep analytical observation, mechanistic interpretation, and sensory consequence as separate layers.
- Use RDKit templates only for curated structural transformations.
- Preserve source-specific kinetics; never create a universal Maillard, enzyme, starch, or collagen threshold.
- Treat raw-versus-processed literature as a sparse evidence graph.

**Experiments required before stronger claims**

- Systematic Q-P2 paper census for the first ten ingredients.
- Matched surface/core kinetics with measured `a_w` and pH trajectories.
- Food/liquor/condensate mass balance during boiling.
- Cross-method HS-SPME versus solvent-extraction study for 2-AP and sulfur compounds.
- Enzyme activity time courses before cutting, after resting, and during heating.
- External validation of any reaction-template mechanism selector on held-out ingredient/process cells.
- Replicate OAV measurements using matrix-appropriate thresholds; GC-MS abundance alone does not establish sensory importance.

## 16. Open Questions

**Answered**

- **Q-P2:** literature supports a sparse matrix; estimated first-pass yield is 1–4 usable direct papers for many mainstream ingredients and 0–1 for long-tail ingredients, with exact counts still requiring audit.
- **Q-P3:** the minimum schema must capture provenance, ingredient state, ordered process, geometry, thermal and chemical drivers, analytical method, matched contrast, identity confidence, mechanism confidence, and confounders.
- **Q-P5:** the first ten cells are specified above, emphasizing matched wet/dry controls, cutting enzymes, fermentation, starch, meat, and high-value hazards/aromas.

**Unanswered or unverified**

- Exact recoverable paper count for every target ingredient.
- Whether the professor’s processing endpoint contains measured before/after compounds or only labels.
- Whether enough absolute concentration and OAV data exist for cross-study quantitative learning.
- How reliably recipe prose can recover local surface temperature, `a_w`, oxygen, and precursor states.
- Whether reaction fingerprints improve process-effect generalization beyond descriptor and precursor baselines.

## 17. Linked Bibliography

- Hodge, “Dehydrated Foods, Chemistry of Browning Reactions in Model Systems” (1953), [DOI](https://doi.org/10.1021/jf60015a004).
- Mottram, Wedzicha & Dodson, “Acrylamide is formed in the Maillard reaction” (2002), [DOI](https://doi.org/10.1038/419448a).
- Stadler et al., “Acrylamide from Maillard reaction products” (2002), [DOI](https://doi.org/10.1038/419449a).
- Knol et al., “Kinetics of acrylamide formation/elimination reactions as affected by water activity” (2007), [DOI](https://doi.org/10.1021/bp060389f).
- Claeys, Ludikhuyze & Hendrickx, HMF/lactulose/furosine kinetics in milk (2001), [DOI](https://doi.org/10.1017/S0022029901004745).
- Cai et al., 2-acetyl-1-pyrroline kinetic model (2024), [DOI](https://doi.org/10.1016/j.foodres.2024.114591).
- Adams et al., pyrazine formation from amino acids and dicarbonyls (2008), [DOI](https://doi.org/10.1021/jf0726785).
- Quintas, Brandão & Silva, caramelization colour kinetics (2007), [DOI](https://doi.org/10.1016/j.jfoodeng.2007.03.036).
- Utama et al., boiled versus oven-roasted beef brisket (2018), [DOI](https://doi.org/10.5713/ajas.17.0217).
- Mancinelli et al., raw/cooked chicken VOC and oxidation study (2021), [DOI](https://doi.org/10.1016/j.psj.2020.10.030).
- Wang et al., water-dependent wheat-starch gelatinization (2019), [PubMed](https://pubmed.ncbi.nlm.nih.gov/30744867/).
- Aghajanzadeh et al., potato starch/flour gelatinization and retrogradation (2026), [DOI](https://doi.org/10.1016/j.foodchem.2026.149741).
- Ludikhuyze et al., broccoli myrosinase inactivation kinetics (1999), [DOI](https://doi.org/10.1021/jf980964y).
- Oliviero et al., water-content effects on broccoli myrosinase (2014), [DOI](https://doi.org/10.1016/j.foodchem.2014.04.099).
- Anthon & Barrett, tomato LOX/HPL thermal inactivation (2003), [DOI](https://doi.org/10.1016/S0308-8146(02)00424-7).
- Weemaes et al., broccoli chlorophyll degradation kinetics (1999), [DOI](https://doi.org/10.1021/jf980663o).
- Fuchigami, pH-dependent vegetable maceration (1983), [DOI](https://doi.org/10.4327/jsnfs.36.219).
- Wieczorek & Jeleń, raw/cooked Brassica volatiles (2019), [DOI](https://doi.org/10.3390/molecules24030391).
- Routray et al., raw/cooked rice 2-AP and VOC profiling (2021), [DOI](https://doi.org/10.3390/foods10081917).
- Zhao et al., boiling effects across 26 japonica rice varieties (2022), [DOI](https://doi.org/10.1016/j.foodres.2022.111078).
- Warburton, Silcock & Eyres, sourdough cultures and bread volatiles (2022), [DOI](https://doi.org/10.1016/j.foodres.2022.111885).
- Sumner et al., MSI chemical-analysis reporting standard (2007), [DOI](https://doi.org/10.1007/s11306-007-0082-2).
- [RDKit 2026.03.5 reaction documentation](https://www.rdkit.org/docs/RDKit_Book.html).
- [NIST Chemistry WebBook SRD 69](https://doi.org/10.18434/T4D303).
- [MetaboLights official repository](https://www.ebi.ac.uk/metabolights/).
- [Metabolomics Workbench REST specification](https://www.metabolomicsworkbench.org/tools/MWRestAPIv1.0.pdf).
