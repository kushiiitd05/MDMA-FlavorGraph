# R1 / D1: Fingerprints and Similarity Theory

**Research date:** 2026-09-03  
**Evidence labels:** **Established** = directly supported mathematically or empirically; **inferred** = derived from established results; **assumed** = proposed project convention; **unverified** = requires CGAS data. No master-roadmap files were edited.

## Commissioning Question

Which molecular fingerprints, similarity coefficients, random-background corrections, and ingredient set-to-set operators provide defensible E1-E3 baselines, especially when ingredient profiles differ in size by 10-100x, and what experiments resolve Q-C1, Q-C2, and Q-C3?

## Executive Findings

- **Established:** “Morgan fingerprint,” ECFP, and FCFP are related but not interchangeable names. Original Morgan connectivity refinement was devised for canonical graph identification; modern circular fingerprints iteratively hash atom-centred environments. RDKit describes its output as *similar to* ECFP/FCFP, not bit-identical to proprietary implementations. ECFP4 corresponds approximately to RDKit radius 2. [Morgan 1965](https://doi.org/10.1021/c160017a018), [Rogers & Hahn 2010](https://pubmed.ncbi.nlm.nih.gov/20426451/), [RDKit documentation](https://www.rdkit.org/docs/GettingStartedInPython.html#fingerprinting-and-molecular-similarity)
- **Established:** For binary fingerprints, Tanimoto is Jaccard and `1-T` is a metric. Dice is a monotone transform, `D=2T/(1+T)`, so it cannot change molecule-pair ranking; `1-Dice` is not generally a metric. Asymmetric Tversky is not a metric because it is not symmetric. [Kosub 2019](https://arxiv.org/abs/1612.02696), [IUPAC Tversky definition](https://goldbook.iupac.org/terms/view/11529)
- **Established:** Count-MinMax and dot-product Tanimoto are different. RDKit’s `SparseIntVect` Tanimoto uses componentwise minima, therefore MinMax/generalized Jaccard. For non-binary dot-product Tanimoto, `1-T_DP` is not metric, while `sqrt(1-T_DP)` is. [RDKit source](https://www.rdkit.org/docs/cppapi/SparseIntVect_8h_source.html), [Tripp et al. 2023](https://arxiv.org/abs/2306.14809)
- **Established:** Tanimoto has unavoidable bit-density and molecular-size effects. If fingerprints contain `p` and `q` on-bits, `T≤min(p,q)/max(p,q)`; molecules with strongly different complexities cannot score highly even with maximal containment. [Holliday et al. 2003](https://pubmed.ncbi.nlm.nih.gov/12767139/), [Wang et al. 2007](https://doi.org/10.1002/cmdc.200700050)
- **Established:** A universal raw Tanimoto threshold is statistically indefensible. Null similarity depends on fingerprint, folding, query bit count, molecular size, database composition, and database size. Query-conditioned empirical nulls are preferable. [Baldi & Nasr 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2914517/)
- **Inferred:** Mean, maximum, top-k, matching, and optimal transport estimate different notions of ingredient similarity. There is no mathematically universal “best aggregator.”
- **Unverified:** No primary study located directly compares these operators on food ingredient-compound profiles with 10-100x cardinality variation. That is absence of evidence, not evidence that their performances are equal.

## Fingerprint Taxonomy

| Family | Encoded object | Strength | Principal failure |
|---|---|---|---|
| MACCS | 166 public structural/property keys | Compact, interpretable control | Coarse; public definitions contain ambiguities and toolkit differences. RDKit returns 167 positions with bit 0 unused. [RDKit source](https://github.com/rdkit/rdkit/blob/master/rdkit/Chem/MACCSkeys.py) |
| RDKit/path | Hashed linear and optionally branched subgraphs over configurable path lengths | Captures extended paths and rings | Folding collisions; complexity/length dependence |
| Morgan/ECFP | Circular atom environments through radius `r` | Strong general 2D baseline; local interpretability | Locality, collisions, size bias |
| FCFP | Morgan iteration using pharmacophore-class atom invariants | Functional analogy across atom substitutions | Loses element-level specificity |
| Atom pair | `(atom type A, topological distance, atom type B)` | Long-range topology and molecular extent | Quadratic feature growth and size sensitivity. [Carhart et al. 1985](https://doi.org/10.1021/ci00046a002) |
| Topological torsion | Ordered atom-type sequences, conventionally four atoms | Intermediate local/path geometry | Sparse for small molecules; still 2D. [Nilakantan et al. 1987](https://doi.org/10.1021/ci00054a008) |
| 2D pharmacophore | Feature tuples plus binned graph distances | Functional similarity and scaffold hopping | Feature definitions and distance bins dominate |
| MHFP6 | Circular-substructure SMILES through diameter six, MinHashed | Compact approximate Jaccard and scalable ANN | MinHash approximation; representation-specific implementation |
| MAP4 | Pairs of radius-1/2 circular substructures plus topological distance, MinHashed | Combines local chemistry, distance, and size | Food-volatile superiority is unverified |
| 3D shape/pharmacophore | Conformer shape or spatial feature arrangements | Stereochemical and shape information unavailable in 2D | Protonation, conformer generation, alignment, and ensemble dependence |
| Reaction | Product-reactant feature difference or concatenated sides | Represents transformations rather than molecules | Requires reliable reaction sides, roles, balancing, and often atom mapping |

## Exact Circular-Fingerprint Mechanism

**Established:** For each atom, initialize an identifier from invariants such as atomic number, valence, charge, isotope, hydrogen count, and ring membership. At radius `r`, hash `(r, central previous ID, sorted[(bond invariant, neighbour previous ID)])`, update all atoms synchronously, collect identifiers, and remove structurally duplicate environments. ECFP preserves atom identity-oriented invariants; FCFP replaces these with functional classes such as donor, acceptor, aromatic, acidic, and basic. Presence fingerprints deduplicate features; count fingerprints retain multiplicity. [Rogers & Hahn](https://doi.org/10.1021/ci100050t)

Folding maps a large identifier space into `K` positions. **Inferred under uniform hashing:** for `h` unique features, expected occupied bits are `K[1-(1-1/K)^h]`; expected aliases are `h-K[1-(1-1/K)^h]`. Binary folding additionally saturates repeated occurrences; folded counts retain total multiplicity but still merge unrelated features. Collision-free or sparse representations therefore belong in the ablation. A 2024 study found collision-free Sort & Slice consistently improved supervised ECFP models across its tested tasks, but its training-set-dependent vocabulary must be learned inside each fold. [Dablander et al. 2024](https://doi.org/10.1186/s13321-024-00932-y)

## Similarity Mathematics

Let `c=|A∩B|`, `x=|A\B|`, and `y=|B\A|`.

| Measure | Formula | Interpretation and status |
|---|---|---|
| Tanimoto/Jaccard | `c/(c+x+y)` | Symmetric; `1-T` is a metric for sets/binary vectors |
| Dice | `2c/(2c+x+y)` | Same binary pair ranking as Tanimoto |
| Tversky | `c/(c+αx+βy)` | Directional when `α≠β`; containment-sensitive; nonmetric |
| Ochiai/cosine | `c/sqrt((c+x)(c+y))` | Geometric normalization; `1-C` nonmetric |
| MinMax | `Σ min(u_k,v_k)/Σ max(u_k,v_k)` | Generalized Jaccard for nonnegative counts |
| Soergel | `Σ|u_k-v_k|/Σmax(u_k,v_k)` | Equals `1-MinMax`; metric on nonnegative vectors |
| Dot Tanimoto | `u·v/(||u||²+||v||²-u·v)` | Equals binary Tanimoto only on 0/1 vectors |

**Implementation warning:** do not call both MinMax and dot Tanimoto simply “count Tanimoto.” RDKit sparse-count Tanimoto is MinMax. MinHash signatures must be compared by the fraction of equal permutation minima, not by ordinary featurewise Jaccard/cosine. [Manasse et al. 2010](https://www.microsoft.com/en-us/research/publication/consistent-weighted-sampling/), [MAP4 implementation](https://github.com/reymond-group/map4)

## Random-Pair Similarity and Standardization

For uniformly placed fixed-cardinality binary fingerprints of length `K`, `E[c]=pq/K` and the plug-in approximation is `E[T]≈(pq/K)/(p+q-pq/K)`. **Inferred:** this is not an exact expectation of the ratio and is unsuitable as the CGAS null because chemical features and folded bits are correlated.

**Recommended null:** preserve ingredient profile sizes and molecule document frequencies through bipartite degree-preserving edge swaps; optionally stratify by ingredient category, source database, and analytical method. For each observed pair compute its aggregator on `B` null realizations, report percentile and `p=(1+#null≥observed)/(B+1)`, and use conditional empirical CDFs when distributions are skewed. Z-scores are secondary. For maxima or database retrieval, condition on query and database size because extreme values rise with candidate count.

## Ingredient Set-to-Set Operators

For molecule kernel `k(a,b)` and normalized ingredient weights `w_a,v_b`:

- `S_mean=Σ_ab w_av_bk(a,b)` is the empirical kernel-mean inner product. **Established:** it is cardinality-normalized and positive semidefinite when `k` is, but true sparse correspondences are diluted; unequal cardinality changes estimator variance. [Smola et al. 2007](https://alex.smola.org/papers/2007/SmoGreSonSch07.pdf)
- `S_best(A→B)=Σ_a w_a max_b k(a,b)` rewards large target sets through an extreme-value effect. Symmetrization removes direction, not cardinality bias.
- Top-k reduces dilution but inherits candidate-pool bias; fixed `k` treats small sets differently, while fractional `k` changes the estimand.
- One-to-one optimal matching prevents unlimited feature reuse, but unequal cardinalities require dummy nodes or unmatched penalties. The resulting optimal-assignment function is not automatically a positive-definite kernel. [Vert 2008](https://arxiv.org/abs/0801.4061)
- Balanced optimal transport uses `S_OT=1-min_{π∈Π(w,v)}Σ_ab π_ab[1-k(a,b)]`. It accepts unequal set cardinalities and constrains reuse through marginal mass. Uniform weights remain annotation-dependent; every newly reported compound redistributes ingredient mass. Entropic Sinkhorn transport is faster but adds a regularization-dependent blur. [Cuturi 2013](https://papers.nips.cc/paper/4927-sinkhorn-distances-lightspeed-computation-of-optimal-transport)
- Kernel MMD compares distributions through `MMD²=E_Ak+E_Bk-2E_ABk`; use the unbiased off-diagonal estimator when measuring finite-sample discrepancy. Small profiles have higher estimator variance. [Gretton et al. 2012](https://jmlr.org/papers/volume13/gretton12a/gretton12a.pdf)

## Quantitative Evidence

**Established but domain-limited:** Riniker and Landrum compared 12 standard fingerprints plus two baselines over 88 protein-target datasets and seven evaluation measures; most standard fingerprints were highly correlated and not significantly separable, demonstrating strong benchmark dependence. [Riniker & Landrum 2013](https://pubmed.ncbi.nlm.nih.gov/23721588/)

MHFP6 was evaluated over the same 88-target framework; 2048-dimensional MHFP6 significantly exceeded 2048-bit ECFP4 for AUC, EF1, and EF5 and was reported comparable to 16,384-bit ECFP4 on much of that benchmark. [Probst & Reymond 2018](https://doi.org/10.1186/s13321-018-0321-8)

MAP4’s extended evaluation contained 17 MUV, 21 DUD, 50 ChEMBL, 30 mutated-peptide, and 30 scrambled-peptide targets and reported the best overall ranking across combined small-molecule/peptide tasks. This supports an ablation, not automatic adoption for food volatiles. [Capecchi et al. 2020](https://pubmed.ncbi.nlm.nih.gov/33431010/)

Reaction atom-pair difference fingerprints produced 97% external-test accuracy for a 50-class reaction classifier and recovered 48/50 expert classes with median cluster F-score 0.63. These results concern curated synthetic reactions, not incomplete cooking networks. [Schneider et al. 2015](https://pubmed.ncbi.nlm.nih.gov/25541888/)

## Decisions Recommended

**Primary E1:** report raw overlap, Jaccard, Ochiai, IDF-weighted MinMax, profile sizes, and degree-preserving-null percentile together. No single raw score becomes “chemical compatibility.”

**Primary E2:** RDKit Morgan radius 2, `includeChirality=True`, 2048-bit presence plus sparse unfolded counts; binary Tanimoto is the conventional headline molecule kernel, while sparse-count MinMax and 4096-bit variants measure multiplicity/collision sensitivity. Preserve `AdditionalOutput.bitInfoMap` for auditability. Current APIs are `GetMorganGenerator`, `GetRDKitFPGenerator`, `GetAtomPairGenerator`, and `GetTopologicalTorsionGenerator`, with `GetFingerprint`/`GetSparseCountFingerprint`; MACCS remains `MACCSkeys.GenMACCSKeys`. [RDKit fingerprint-generator API](https://www.rdkit.org/docs/source/rdkit.Chem.rdFingerprintGenerator.html)

**Primary ingredient aggregation:** balanced exact OT with normalized masses and cost `1-T`, accompanied by kernel mean as the simplest cardinality-normalized control. This is a recommended estimand choice, not an established empirical winner.

**Defer:** 3D similarity until conformer ensembles and protonation/stereo policy are frozen. Defer reaction fingerprints to explicitly represented transformations; RDKit supplies difference and structural reaction fingerprints, but they cannot infer unknown cooking chemistry. [RDKit reaction API](https://rdkit.org/docs/source/rdkit.Chem.rdChemReactions.html)

## Required Ablation Matrix

| Axis | Required settings |
|---|---|
| Molecular representation | MACCS; RDKit path; Morgan r=2 bit 2048/4096; Morgan sparse count; FCFP r=2; atom pair; torsion; MHFP6; MAP4 |
| Coefficient | Binary Tanimoto, Dice, Ochiai, Tversky `(0.1,0.9)/(0.9,0.1)`, count MinMax/Soergel |
| Aggregator | Mean/KME, directed max, symmetric max, top-1/5/10%, one-to-one matching, balanced OT; unbalanced OT exploratory |
| Weighting | Uniform presence, molecule-IDF, concentration, OAV where available |
| Confound control | Original data; cardinality-matched downsampling; source-count strata; degree-preserving null |
| Evaluation | Held-out recipe co-occurrence, cross-cuisine transfer, rank stability, cardinality-score slope, runtime; never train and evaluate on the same chemical score |

## Questions Resolved

- **Q-C1:** **Unverified in CGAS.** Annotation coverage is a credible confound, but it must be measured using source counts/provenance or sensitivity downsampling. Current evidence does not establish its magnitude in this dataset.
- **Q-C2:** **Mechanism answered, materiality unanswered.** Tanimoto is size-sensitive. Dice cannot change pairwise binary rankings, but nonlinear aggregation can change ingredient rankings; asymmetric Tversky and count MinMax can change both.
- **Q-C3:** **No universal winner.** Max/top-k are predictably target-cardinality-biased; mean/KME is cardinality-normalized but dilutes sparse matches; balanced OT is the strongest primary candidate, requiring direct ablation and coverage sensitivity tests.

## Linked Bibliography

[Morgan 1965](https://doi.org/10.1021/c160017a018); [Rogers & Hahn 2010](https://doi.org/10.1021/ci100050t); [Carhart et al. 1985](https://doi.org/10.1021/ci00046a002); [Nilakantan et al. 1987](https://doi.org/10.1021/ci00054a008); [Bajusz et al. 2015](https://doi.org/10.1186/s13321-015-0069-3); [Holliday et al. 2003](https://doi.org/10.1021/ci034001x); [Baldi & Nasr 2010](https://doi.org/10.1021/ci900503y); [Riniker & Landrum 2013](https://doi.org/10.1186/1758-2946-5-26); [Probst & Reymond 2018](https://doi.org/10.1186/s13321-018-0321-8); [Capecchi et al. 2020](https://doi.org/10.1186/s13321-020-00445-4); [Schneider et al. 2015](https://doi.org/10.1021/ci5006614); [Salim et al. 2003](https://doi.org/10.1021/ci025596j); [Whittle et al. 2004](https://doi.org/10.1021/ci049867x); [Gretton et al. 2012](https://jmlr.org/papers/v13/gretton12a.html); [Cuturi 2013](https://papers.nips.cc/paper/4927-sinkhorn-distances-lightspeed-computation-of-optimal-transport); [RDKit 2026.03 documentation](https://www.rdkit.org/docs/).
