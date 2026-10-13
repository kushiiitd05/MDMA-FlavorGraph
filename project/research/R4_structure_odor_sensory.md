# R4 / D4: Structure-to-Sensory Prediction

**Evidence cutoff:** 2026-09-03  
**Status key:** **[E] Established** by cited evidence; **[I] Inferred** from evidence; **[A] Assumed** for project design; **[U] Unverified** or not yet adequately tested.

## Commissioning Question

How far can molecular structure or an ingredient’s compound list predict odor, taste, texture, and the final sensory target \(Y^{sens}\)? Specifically:

- **Q-C7:** Do concentration or odor-activity-value data exist at sufficient coverage to move beyond presence weighting?
- **Q-L4:** Can \(Y^{sens}\) be predicted from \(C^{chem}\) well enough to constitute a defensible secondary contribution?

## Executive Findings

1. **[E] Molecular structure contains predictive sensory signal, but the mapping is probabilistic and non-smooth.** Olfaction uses combinatorial receptor codes: one receptor responds to several odorants and one odorant activates several receptors. Small structural or concentration changes can change the code. Human receptor polymorphism adds person-specific variation. [Malnic et al.](https://pubmed.ncbi.nlm.nih.gov/10089886/), [Mainland et al.](https://www.nature.com/articles/nn.3598)

2. **[E] Stereochemistry is a hard failure mode for ordinary 2D graph models.** Carvone enantiomers have distinct mint/caraway qualities, and alpha-ionone enantiomer threshold ratios varied over four orders of magnitude across 63 people. [Geithe et al.](https://pubmed.ncbi.nlm.nih.gov/28656349/), [Polak et al.](https://pubmed.ncbi.nlm.nih.gov/2914071/)

3. **[E] Modern models can predict standardized single-molecule odor descriptors.** POM achieved test AUROC \(0.894\,[0.888,0.902]\) on roughly 5,000 GS/LF molecules and 138 labels versus \(0.850\,[0.838,0.860]\) for its tuned fingerprint baseline. Its prospective experiment used 400 purchased odorants, 55 descriptors and at least 15 trained assessors; panel test-retest correlation was \(r=0.80\). [Lee et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11898014/)

4. **[E] “Human-level POM” is task-specific, not universal olfactory simulation.** The comparison was model versus median assessor against the trained-panel mean under intensity-controlled, mostly single-molecule conditions. Concentration was not an input, some low-intensity or contaminated samples were excluded, roughly 45% of validation structures were withheld, and original training code/model state was unavailable.

5. **[E] Ingredient compound presence is not sensory contribution.** GC-O/AEDA identifies odor-active chromatographic regions; measured concentrations and matrix-matched thresholds permit OAV calculation; recombination and omission tests are needed to establish character impact. A yogurt study, for example, reduced its system to 14 significant aroma-active compounds using GC-MS/O, AEDA, OAV, recombination, and omission. [Han et al.](https://pubmed.ncbi.nlm.nih.gov/39089036/)

6. **[E] Mixture behavior is nonlinear at receptor level, but perceptual descriptor profiles may often be approximately linear.** Competitive binding and antagonism produce suppression and normalization at receptors. A 2026 **non-peer-reviewed preprint** nevertheless found that nearly all 432 tested mixtures were explained by averaging 144 component-stimulus profiles; session-controlled measurements reduced apparent nonlinearity. Both findings can coexist because receptor activity is not identical to descriptor-space output. [Reddy et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5915184/), [Pellegrino et al. preprint](https://pubmed.ncbi.nlm.nih.gov/42465471/)

7. **Q-C7 verdict: [E/I] Partial yes, global no.** Existing threshold and concentration evidence supports OAV weighting for selected foods and compounds, but not as a universal replacement for presence weighting. Missing thresholds must remain “unknown,” not zero.

8. **Q-L4 verdict: [I] Conditional yes.** \(Y^{sens}\) can be a secondary contribution if restricted initially to panel-mean, standardized targets and if \(C^{chem}\) includes concentrations, matrix, process state, stereochemistry, and measurement protocol. Finished-dish sensory perception cannot presently be inferred reliably from a presence-only compound list.

## Causal Taxonomy

**[A] Recommended causal chain**

\[
\text{structure/stereo}
\rightarrow \text{receptor activities}
\rightarrow \text{single-compound quality and threshold}
\rightarrow \text{matrix release}
\rightarrow \text{mixture interactions}
\rightarrow \text{oral/nasal dynamics}
\rightarrow Y^{sens}_{person,protocol}
\]

A suitable project formulation is:

\[
Y^{sens}_{p,t} =
F\!\left(
\{x_i,c_i,a_i(t)\},
S_t,M,T,pH,a_w,fat,O_2,
route,panel_p,protocol
\right)+\epsilon
\]

Here \(x_i\) is structure including stereochemistry, \(c_i\) is concentration, \(a_i(t)\) is effective activity or delivered vapor concentration, \(S_t\) is process-derived structural state, and \(M\) is matrix.

### Odor Targets

- Detection or odorlessness.
- Detection threshold and dose-response slope.
- Suprathreshold intensity.
- Descriptor profile and perceptual similarity.
- Pleasantness.
- Elemental versus configural mixture perception.
- Orthonasal versus retronasal delivery and temporal persistence.

### Taste Targets

- Molecular sweet, bitter, sour, salty, or umami membership.
- Detection/recognition threshold and concentration-response intensity.
- Receptor activation where experimentally known.
- Mixture effects, aftertaste, temperature, pH, ionic state, and saliva-conditioned perception.

### Texture Targets

- Mechanical: hardness, fracture force/strain, toughness, cohesiveness.
- Rheological: \(G'\), \(G''\), yield stress, apparent viscosity, thixotropy.
- Structural: moisture gradients, porosity, particle size, crystallinity, gel-network connectivity.
- Oral: lubrication, adhesiveness, creaminess, crispness, acoustic emissions, breakdown rate.

## Mechanisms And Formulas

**[I] Minimal competitive receptor model**

\[
r_j =
R_{\max,j}
\frac{\sum_i e_{ij}c_i/K_{ij}}
{1+\sum_i c_i/K_{ij}}
\]

The denominator produces competition; a strongly binding component with low efficacy \(e_{ij}\) can suppress another agonist. More complex mechanisms allow inverse agonism, multiple sites, facilitation, and synergy. This receptor equation is not itself a perceptual mixture model. [Singh et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6511041/)

**[E] Odor activity value**

\[
OAV_i=\frac{c_i}{T_i}
\]

\(c_i\) and threshold \(T_i\) must share compatible units, phase, matrix, temperature, route, and threshold definition. \(OAV_i>1\) marks a plausible contributor, not causal proof; \(OAV_i<1\) is not evidence of irrelevance in mixtures.

**[E] AEDA**

If serial dilution factor is \(R\) and the final detection step is \(R^P\), the recommended assessor-level estimate is:

\[
FD_i=R^{P+0.5}
\]

FD is a semi-quantized potency ranking of an extract, not an absolute food concentration. Precision depends on dilution spacing and assessor threshold variance. [van Ruth et al.](https://pubs.acs.org/doi/abs/10.1021/jf010933u)

**[E] Oscillatory rheology**

\[
G'=\frac{\sigma_0}{\gamma_0}\cos\delta,\qquad
G''=\frac{\sigma_0}{\gamma_0}\sin\delta,\qquad
\tan\delta=\frac{G''}{G'}
\]

These are meaningful only within the linear viscoelastic region and at reported temperature, frequency, and strain.

**[E] Herschel-Bulkley flow**

\[
\tau=\tau_0+K\dot{\gamma}^{\,n},
\qquad
\eta_{\mathrm{app}}=\tau/\dot{\gamma}
\]

A single viscosity value without shear rate, temperature, and shear history is not a transferable texture descriptor.

## Quantitative Model Evidence

| Resource | Verified evidence | Interpretation and boundary |
|---|---|---|
| **DREAM Olfaction Challenge** | 476 molecules, 49 participants, 4,884 molecular features; 338 train, 69 leaderboard, 69 hidden test; 21 outputs. Population correlations: intensity \(r=0.78\), pleasantness \(r=0.71\), mean over 19 semantic descriptors \(r=0.55\). [Keller et al.](https://www-cs.stanford.edu/people/marinka/papers/olfaction-science17.pdf) | **[E]** Strong evidence that population averages are more predictable than individual ratings. It is a small-molecule, controlled-stimulus benchmark, not food prediction. |
| **POM** | Approximately 5,000 GS/LF molecules, 138 labels, 256-dimensional embedding; 80/20 split; AUROC 0.894. Prospective 400-compound acquisition with 55-label trained-panel protocol. | **[E]** Best evidence here for general single-molecule odor-quality screening. Descriptor imbalance, proprietary source labels, exclusions, and unavailable original model code constrain reproducibility. |
| **OpenPOM** | `curated_GS_LF_merged_4983.csv`; five-fold CV and ten-model ensemble per fold; repository reports AUROC 0.8872; MIT-licensed implementation. [Official repository](https://github.com/BioMachineLearning/openpom) | **[E]** Usable open replication, not the original POM model or an independent prospective validation. |
| **Pyrfume** | Standardized subject/stimulus/molecule/behavior archives with processing scripts and provenance; Python, R, and REST access are documented. [Hamel et al.](https://doi.org/10.1038/s41597-024-04051-z), [official archive](https://github.com/pyrfume/pyrfume-data) | **[E]** Integration layer, not one homogeneous dataset. Repository-level licensing and source-dataset rights must be checked per archive; do not merge labels without source controls. |
| **Uni-Mol2 olfaction study** | **Preprint, not peer reviewed.** On 11 enantiomer pairs, OpenPOM produced identical within-pair predictions; the 3D model distinguished structures but chose the correct enantiomer for only 19/34 differential labels, 55.9%. [Han et al.](https://arxiv.org/abs/2608.25893) | **[E, provisional]** 3D/stereo awareness is necessary but plainly insufficient. Aggregate QSOR metrics can conceal near-chance activity-cliff behavior. |

A useful activity-cliff diagnostic is:

\[
A_{ab}=\frac{d_{\mathrm{sens}}(a,b)}
{d_{\mathrm{chem}}(a,b)+\varepsilon}
\]

**[A]** Enantiomer pairs and near-neighbor “Sell triplets” should receive dedicated evaluation rather than disappearing inside aggregate AUROC.

## Thresholds, GC-O, And Character Impact

**[E]** ISO 13301 specifies 3-AFC threshold estimation with uncertainty and emphasizes the dose-response slope, assessor sensitivity, and experimental conditions. It does not make thresholds matrix-invariant. [ISO 13301:2018](https://www.iso.org/standard/68901.html)

**[E]** Flavornet contains 738 odorants admitted through supra-threshold quantitative GC-O evidence, but explicitly marks estimated missing fields. It is curated evidence, not complete concentration coverage. [Flavornet](https://flavornet.org/)

**[E]** A 2025 study assembled thresholds for 716 volatile compounds and 31,459 aroma-contribution records. Its held-out results were macro-F1 0.732/weighted-F1 0.912 for contribution classification and \(R^2=0.94\), RMSE 0.44 for threshold prediction. These are paper-specific validation results; matrix-specific generalization remains unproved. [Li et al.](https://pubmed.ncbi.nlm.nih.gov/41295332/)

**[A] Required evidence ladder**

1. Analytical identification with confidence and stereochemistry.
2. Quantification using suitable standards.
3. GC-O detection of the eluting region.
4. AEDA/FD prioritization.
5. Matrix-matched OAV with uncertainty.
6. Aroma recombination.
7. Omission or addition tests establishing causal sensory impact.

Skipping from step 1 to “character-impact compound” is not defensible.

## Mixtures And Matrix Effects

- **[E] Suppression/masking:** one component reduces receptor response, perceived intensity, or recognizability of another.
- **[E] Synergy/hyperadditivity:** mixture response exceeds a specified additive or competitive baseline.
- **[E] Configural perception:** the mixture acquires a quality not readily decomposed by assessors into component identities.
- **[I] Reconciliation:** receptor-level antagonism may coexist with approximate linear averaging in descriptor space because neural decoding, normalization, language, and panel averaging intervene.
- **[U]** Whether the 2026 linear-average result transfers to heated, fatty, viscous, chemically reacting foods is unknown. Its authors tested controlled odorant mixtures, and the work remains a preprint.

Matrix variables affect partitioning and oral delivery. Fat can reduce nosespace release and perceived intensity, viscosity changes retronasal release and flavor intensity, and texture/odor cues can alter perceived creaminess or thickness. Therefore static liquid-phase OAV is at best an approximation to \(c_i^{effective}(t)/T_i\).

## Taste Evidence

| Resource | Verified scope | Limitation |
|---|---|---|
| **SuperSweet** | More than 8,000 carbohydrates, proteins, D-amino acids, and candidate artificial sweeteners in the 2011 release. [Ahmed et al.](https://academic.oup.com/nar/article/39/suppl_1/D377/2508623) | Similarity expansion means database membership is not uniformly equivalent to sensory confirmation; current maintenance status is **[U]**. |
| **BitterDB 2024** | 2,250 bitter compounds, 682 associated with at least one T2R, 1,783 ligand-receptor associations, 66 species, and 509 peptides. [Ziaikin et al.](https://academic.oup.com/nar/article/53/D1/D1645/7899525) | Species and evidence types differ; receptor activation does not directly specify human bitterness intensity. |
| **VirtualTaste** | Sweet train/test 1,608/403; bitter 1,289/323; sour 1,214/133. External AUROC: 0.95, 0.96, 0.99 respectively. [Fritz et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8262722/) | Curated structural classification with oversampling; no concentration, food matrix, mixture, temporal intensity, or aftertaste prediction. |
| **FART** | 15,025 curated molecules from six sources; parallel sweet/bitter/sour/umami/undefined classification; reported accuracy above 91%; code and data released. [Zimmermann et al.](https://doi.org/10.1038/s41538-025-00474-z), [repository](https://github.com/fart-lab/fart) | Class imbalance and source-derived labels make accuracy insufficient alone; no finished-food validation. |
| **UmamiPredict** | Balanced 868-compound set: 439 umami, 429 non-umami; combined LightGBM accuracy 96.55%. [Sharma et al.](https://pubmed.ncbi.nlm.nih.gov/41046313/) | Small, balanced molecule/peptide benchmark; external food-matrix transfer is **[U]**. |
| **SuperNatural 3.0** | Searchable predicted sweet, bitter, sour, salty, and umami annotations. [Banerjee et al.](https://academic.oup.com/nar/article/51/D1/D654/6833249) | Most taste fields are model predictions, not human observations; never use them as independent ground truth for another model. |

## Sensory Lexicons And Reliability

**[E]** ISO 13299 provides the framework for developing product-specific sensory profiles; ISO 8586 covers assessor selection, training, and performance validation. Texture terminology and evaluation order are treated separately in ISO 11036. [ISO 13299](https://www.iso.org/standard/58042.html), [ISO 8586](https://www.iso.org/standard/76667.html), [ISO 11036](https://www.iso.org/standard/76668.html)

A panel model should retain assessor and replicate structure:

\[
y_{spr}=\mu+\alpha_s+\beta_p+\gamma_r+
(\alpha\beta)_{sp}+\epsilon_{spr}
\]

Report assessor discrimination, repeatability, agreement, panel-mean test-retest/ICC, and confidence intervals. Model performance should be compared with this empirical reliability ceiling.

**[E]** Individual variation is signal, not merely noise: OR polymorphisms altered in-vitro function for 63% of examined receptors, and guaiacol-associated genotype explained measurable intensity and valence variation. Thus a panel-mean model and an individual model are different targets.

## Texture And Process State

**[E]** Instrumental TPA “hardness,” “cohesiveness,” and related values depend on specimen geometry, probe, and deformation and are not intrinsic material properties. [Peleg](https://pubmed.ncbi.nlm.nih.gov/30714161/)

**[E]** Instrument-sensory mappings are product-specific. For ten commercial French-fries products, compression correlations with sensory attributes were \(r=0.64\)–0.90, while one cutting probe produced only \(r=0.03\)–0.49. [Li et al.](https://pubmed.ncbi.nlm.nih.gov/31955416/)

**[E]** Process variables interact mechanistically. Milk heated at \(80^\circ\mathrm{C}\) for 30 minutes at pH 6.8 produced yogurt with higher \(G'\), firmer texture, greater water-holding capacity, and a more compact network than pH 6.4, 7.2, or unheated controls. [Mahomud et al.](https://pubmed.ncbi.nlm.nih.gov/33897033/)

**[E]** Oral-condition measurements matter: in commercial spreads, sensory “body” correlated with apparent viscosity measured at \(37^\circ\mathrm{C}\) and \(50\,s^{-1}\), while particle structure, fat composition, and tribology explained other attributes. [Principato et al.](https://pubmed.ncbi.nlm.nih.gov/38952176/)

**[I]** Texture therefore requires a process-state representation containing moisture distribution, temperature history, \(a_w\), pH, fat/solid fractions, porosity, particle size, protein/starch network state, rheology, tribology, and acoustics. Volatile compound lists contain essentially none of this information.

## Exact Inference Boundary

| Available input | Defensible inference | Not defensible |
|---|---|---|
| Molecular structure with stereo | Physicochemical descriptors; probabilistic odor labels, odorlessness, threshold estimate, taste-class probability, possible receptor candidates | Actual concentration, delivered intensity, character impact, food texture, final mixture quality, universal human response |
| Structure without stereo | Ordinary QSOR/QSAR screening | Enantiomer-specific odor/taste; OpenPOM-like 2D models necessarily collapse graph-identical enantiomers |
| Ingredient compound presence list | Candidate sensory repertoire, descriptor enrichment, overlap and hypothesis generation | Ranking contributions, OAV, absence claims, final aroma, taste intensity, texture, liking |
| Quantified composition plus matrix metadata | Approximate OAV, release modeling, candidate key-odorant ranking | Causal character impact without GC-O/recombination/omission; individual response |
| Chemistry plus process-state and trained-panel labels | Product-specific panel-mean \(Y^{sens}\) prediction is testable | Universal perception, consumer liking, cultural preference, or arbitrary out-of-domain dishes |

**Absence rules:** no database entry means unknown, not absent; no GC-MS peak means not detected under that method, not chemically absent; no GC-O detection means not detected by that panel at that dilution; \(OAV<1\) is not proof of no mixture contribution; a low model probability is not proof of odorlessness.

## Q-C7 Evaluation

**Verdict: partial pass, with a mandatory coverage audit.**

FlavorDB2 reports 25,595 molecules, but only 2,254 are linked to 936 natural ingredients. It exposes threshold-related fields “where available,” yet neither its paper nor official documentation supplies a verified field-level threshold completeness count. [FlavorDB2 paper](https://arxiv.org/abs/2205.05451), [official documentation](https://cosylab.iiitd.edu.in/flavordb2/how_to_use)

Therefore:

- **[E]** Enough measured threshold/OAV evidence exists for selected compounds and food systems to improve on binary presence.
- **[U]** Coverage across the actual CGAS ingredient-compound universe is unknown until audited.
- **[I]** Coverage is insufficient for universal OAV weighting because concentrations, matrices, stereochemistry, threshold definitions, and process stages are sparse or heterogeneous.
- **[A]** Adopt a tiered weight: same-matrix measured OAV; other-matrix OAV with uncertainty; measured concentration plus predicted threshold; predicted concentration and threshold; presence-only fallback. Preserve missingness explicitly.

## Q-L4 Evaluation

**Verdict: conditional pass as a secondary, scoped contribution.**

A defensible claim would be:

> Given quantified chemistry, matrix/process state, and a fixed sensory protocol, predict the trained-panel mean for a bounded odor, taste, and texture lexicon on held-out ingredients and processes.

An indefensible claim would be:

> Predict how a finished dish tastes from the structures or presence of its known compounds.

POM, DREAM, VirtualTaste, and FART establish learnable structure-sensory signal. They do not establish end-to-end dish prediction. \(C^{chem}\) must therefore distinguish presence, concentration, uncertainty, analytical method, stereochemistry, matrix phase, and sampling time.

## Recommended Decisions

1. Define \(Y^{sens}\) as separate odor, taste, texture, temporal, and hedonic vectors; do not collapse them into one “flavor score.”
2. Preserve isomeric SMILES/InChI, concentration units, matrix, temperature, route, analytical method, and provenance.
3. Use OpenPOM or another structure model as an auxiliary molecular prior, never as sensory ground truth.
4. Treat OAV as an evidence-weighted feature with uncertainty, not a deterministic contribution coefficient.
5. Separate texture modeling from volatile-chemistry modeling, joining them only through process state and oral release.
6. Keep panel-mean and individual-response targets distinct.
7. Version every lexicon and map synonyms hierarchically while retaining original labels.
8. Do not use predicted taste/odor database fields as labels when evaluating another predictor.

## Experiments Required

1. Audit FlavorDB2, Flavornet, Pyrfume, and project records by InChIKey/stereoisomer for concentration, threshold, matrix, method, and unit coverage.
2. Reproduce OpenPOM and taste baselines under scaffold, source-dataset, stereoisomer-pair, ingredient, and process-held-out splits.
3. Run same-session component and mixture profiling to test linear averaging against OAV-weighted and receptor-competition baselines.
4. Validate candidate character-impact compounds through quantitative GC-MS/O, AEDA, recombination, and omission.
5. Collect synchronized sensory, rheology, tribology, acoustic, moisture, and process-state measurements.
6. Compare every model against presence-only, measured-OAV, process-only, and panel-reliability baselines.

## Honest \(Y^{sens}\) Target Hierarchy

1. **Ready now:** molecular odorousness and broad odor/taste descriptor probabilities within domain.
2. **Ready with uncertainty:** molecular detection-threshold estimates and candidate aroma-contribution ranking.
3. **Feasible after audit:** OAV-weighted ingredient aroma priors using measured concentrations.
4. **Feasible research target:** standardized panel-mean odor/taste profiles from quantified final-product chemistry.
5. **Feasible but data-intensive:** texture profiles from process state plus rheology, mechanics, acoustics, and tribology.
6. **Experimental frontier:** temporal multisensory flavor during mastication and swallowing.
7. **Not currently defensible:** individual liking or universal dish perception from molecular structure or ingredient lists alone.

## Evaluation Protocol

- Use blinded, randomized, replicated sessions and trained assessors under ISO 8586/13299.
- Measure thresholds using ISO 13301-compatible 3-AFC designs with error bounds.
- Hold out chemical scaffolds, stereochemical pairs, data sources, ingredients, and process regimes.
- Use macro-AUPRC and per-label calibration for imbalanced descriptors; AUROC is secondary.
- Use MAE/RMSE, concordance, rank correlation, and calibrated intervals for intensity/threshold regression.
- Evaluate sensory profiles with centered cosine similarity and per-attribute error against panel test-retest ceilings.
- Evaluate key-compound ranking using GC-O/OAV candidates and blinded omission outcomes.
- Report failure by concentration, matrix, chemical distance, stereochemistry, descriptor frequency, and assessor reliability.
- Require statistically supported improvement over presence-only and simple OAV baselines before claiming Q-L4 success.

## Open Questions

**Answered**

- **[E]** Is receptor coding combinatorial? Yes.
- **[E]** Are structure-odor relations smooth? No; stereochemical and near-neighbor cliffs exist.
- **[E]** Can single-molecule population-average descriptors be predicted? Yes, within bounded datasets and protocols.
- **[E]** Does compound presence establish sensory importance? No.
- **[E]** Can texture be inferred from volatile lists? No.

**Unanswered**

- **[U]** Exact CGAS concentration and matrix-compatible threshold coverage.
- **[U]** Generalization of POM-like models to cooked-food headspace and retronasal perception.
- **[U]** Whether descriptor averaging remains dominant in reacting, viscous, multiphase foods.
- **[U]** Reliable stereochemical perception prediction beyond a small set of known pairs.
- **[U]** The attainable reliability-normalized ceiling for product-level \(Y^{sens}\).

## Three Feasible Unsolved Questions

1. **Can matrix-conditioned dynamic OAV predict retronasal sensory trajectories better than static liquid-phase OAV?** Measure liquid concentration, headspace/nosespace release, fat, viscosity, saliva dilution, and temporal panel ratings.

2. **Can stereo-aware 3D models predict within-enantiomer-pair descriptor and threshold differences rather than merely distinguish conformers?** Build a dedicated dose-response benchmark with paired chemistry, identical protocols, and assessor-genotype metadata where feasible.

3. **Can process-state trajectories predict texture and flavor release better than endpoint TPA?** Model \(T(t)\), \(a_w(t)\), pH, moisture gradients, porosity, network formation, rheology, tribology, and acoustics against temporal trained-panel profiles.

## Linked Bibliography

- [Malnic et al., *Combinatorial receptor codes for odors*](https://pubmed.ncbi.nlm.nih.gov/10089886/)
- [Mainland et al., *The missense of smell*](https://www.nature.com/articles/nn.3598)
- [Polak et al., *Sensory evidence for olfactory receptors with opposite chiral selectivity*](https://pubmed.ncbi.nlm.nih.gov/2914071/)
- [Geithe et al., *Structural determinants of an enantiomer-selective carvone binding pocket*](https://pubmed.ncbi.nlm.nih.gov/28656349/)
- [Keller et al., *Predicting human olfactory perception from chemical features*](https://www-cs.stanford.edu/people/marinka/papers/olfaction-science17.pdf)
- [Lee et al., *A Principal Odor Map Unifies Diverse Tasks in Olfactory Perception*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11898014/)
- [OpenPOM official repository](https://github.com/BioMachineLearning/openpom)
- [Hamel et al., *Pyrfume: A window to the world’s olfactory data*](https://doi.org/10.1038/s41597-024-04051-z)
- [Han et al., *A General-Purpose Molecular Foundation Model Transfers Across Diverse Olfactory Tasks*, preprint](https://arxiv.org/abs/2608.25893)
- [ISO 13301:2018](https://www.iso.org/standard/68901.html)
- [van Ruth et al., *Aroma Extract Dilution Analysis: Precision and Optimal Experimental Design*](https://pubs.acs.org/doi/abs/10.1021/jf010933u)
- [Reddy et al., *Antagonism in olfactory receptor neurons*](https://pmc.ncbi.nlm.nih.gov/articles/PMC5915184/)
- [Singh et al., *Competitive binding predicts nonlinear olfactory-receptor responses*](https://pmc.ncbi.nlm.nih.gov/articles/PMC6511041/)
- [Pellegrino et al., *Odors Smell Like Their Components*, preprint](https://pubmed.ncbi.nlm.nih.gov/42465471/)
- [Grover et al., *FlavorDB2*](https://arxiv.org/abs/2205.05451)
- [Li et al., *Predictive Models of Odor Contribution and Thresholds*](https://pubmed.ncbi.nlm.nih.gov/41295332/)
- [Ahmed et al., *SuperSweet*](https://academic.oup.com/nar/article/39/suppl_1/D377/2508623)
- [Ziaikin et al., *BitterDB: 2024 update*](https://academic.oup.com/nar/article/53/D1/D1645/7899525)
- [Fritz et al., *VirtualTaste*](https://pmc.ncbi.nlm.nih.gov/articles/PMC8262722/)
- [Zimmermann et al., *A chemical language model for molecular taste prediction*](https://doi.org/10.1038/s41538-025-00474-z)
- [ISO 13299:2016](https://www.iso.org/standard/58042.html), [ISO 8586:2023](https://www.iso.org/standard/76667.html), [ISO 11036:2020](https://www.iso.org/standard/76668.html)
- [Peleg, *The Instrumental Texture Profile Analysis Revisited*](https://pubmed.ncbi.nlm.nih.gov/30714161/)
- [Mahomud et al., *Milk pH at heating and yogurt gel properties*](https://pubmed.ncbi.nlm.nih.gov/33897033/)
- [Principato et al., *Rheology, oral tribology, and sensory perception of spreads*](https://pubmed.ncbi.nlm.nih.gov/38952176/)
