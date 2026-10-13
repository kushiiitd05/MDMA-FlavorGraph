# R5 / D5: Learned Molecular and Set Encoders, Food Data/API Landscape

**Commissioned:** 2026-09-03  
**Scope:** Molecular encoders, ingredient-level set representations, contrastive objectives, FlavorGraph novelty boundary, and a verified food-data acquisition strategy. The v4 roadmap was read for alignment but not edited.

**Evidence labels:** **Established** = directly supported by a primary source; **Inferred** = project-specific deduction; **Assumed** = proposed design assumption; **Unverified** = not established from accessible primary material.

## Commissioning Question

Can pretrained molecular encoders and learned set models improve ingredient, pairing, and process-state representations beyond ECFP/Tanimoto and descriptor baselines without learning recipe frequency, source coverage, or the evaluation labels themselves; and which food databases can legally and technically support that experiment?

## Executive Findings

- **Established:** Large chemical pretraining corpora do not guarantee stronger downstream models. Chemprop found fingerprints competitive or superior on small datasets; a 2025 preprint comparing 25 pretrained models across 25 datasets found almost no consistent gain over ECFP except a fingerprint-based method. [Chemprop study](https://arxiv.org/abs/1904.01561), [2025 benchmark preprint](https://arxiv.org/abs/2508.06199)
- **Decision:** Q-L1 remains empirical. ECFP/Tanimoto and descriptor baselines are mandatory; no transformer or GNN should be selected from MoleculeNet results alone.
- **Established:** ChemBERTa, MoLFormer, SELFormer, GROVER, and Uni-Mol were pretrained primarily on PubChem, ZINC, ChEMBL, or generated conformers, not food mixtures, concentrations, cooking transformations, or sensory outcomes.
- **Inferred:** The largest risk is not encoder capacity but supervision quality: sparse and uneven ingredient-compound coverage, false negatives, co-occurrence circularity, source leakage, and frequency/degree bias.
- **Established:** FlavorGraph already combines recipe co-occurrence, ingredient-compound links, metapath2vec, and 881-bit chemical-fingerprint reconstruction. “Food embeddings combining recipe and chemical data” is therefore not novel. [FlavorGraph paper](https://www.nature.com/articles/s41598-020-79422-8)
- **Decision:** CGAS novelty should be process-conditioned ingredient states, explicit molecular/set aggregation, independently evaluated sensory/process tasks, uncertainty, and controls against frequency and annotation coverage.
- **Established:** There is no universal join key across the surveyed food resources. PubChem CID/InChIKey can anchor molecules; FoodOn can anchor food concepts; source-local identifiers and provenance must remain preserved.
- **Unverified:** The professor endpoints, their shared identifiers, schemas, reuse terms, and presence of ingredient-level before/after process states have not been inspected.

## Encoder Taxonomy and Verified Releases

| Family | Representation and pretraining | Verified release | Main limitation for CGAS |
|---|---|---|---|
| Mol2Vec | Morgan substructure identifiers treated as words; skip-gram; molecule vector commonly sums token vectors. [Paper](https://doi.org/10.1021/acs.jcim.7b00616) | Official archived artifact [`examples/models/model_300dim.pkl`](https://github.com/samoturk/mol2vec/blob/master/examples/models/model_300dim.pkl), 300-dimensional | Fixed radius/tokenization; archived implementation; no food semantics |
| ChemBERTa | RoBERTa MLM over SMILES; original work used up to 77M PubChem molecules. [ChemBERTa](https://arxiv.org/abs/2010.09885) ChemBERTa-2 compares MLM with multitask regression. [ChemBERTa-2](https://arxiv.org/abs/2209.01712) | `DeepChem/ChemBERTa-77M-MLM`, `DeepChem/ChemBERTa-77M-MTR`; 5M/10M variants also listed. [Official collection](https://huggingface.co/DeepChem/models) | The 77M-MLM page has no model card; license/provenance detail is incomplete |
| MoLFormer | MLM with linear attention and rotary positions; paper scales to 1.1B PubChem+ZINC molecules. [Paper](https://arxiv.org/abs/2106.09553) | Canonical page `ibm-research/MoLFormer-XL-both-10pct`; its example still uses the legacy `ibm/...` alias; Apache-2.0, 46.8M parameters. [Model](https://huggingface.co/ibm-research/MoLFormer-XL-both-10pct) | This checkpoint used 10% of each corpus; canonicalization removed stereochemistry and sequences over 202 tokens |
| SELFormer | RoBERTa MLM over SELFIES from about 2M ChEMBL molecules. [Paper](https://doi.org/10.1088/2632-2153/acdb30) | Repository download expected at `data/pretrained_models/SELFormer`; no stable registry identifier verified. [Official code](https://github.com/HUBioDataLab/SELFormer) | SELFIES syntactic validity does not establish chemical plausibility or predictive superiority |
| D-MPNN / Chemprop | Directed bond messages avoid immediate reverse-edge propagation; supervised property model, optionally combined with descriptors. | Current official software is Chemprop v2, MIT; no universal pretrained checkpoint. [Repository](https://github.com/chemprop/chemprop) | Must train per task; version defaults differ; small-data overfitting remains possible |
| AttentiveFP | Graph attention plus recurrent atom/message and molecular readout. [Paper](https://doi.org/10.1021/acs.jmedchem.9b00959) | No stable author-issued general checkpoint verified | Attention maps are not causal explanations; not pretrained food representations |
| GROVER | Transformer-style node and directed-edge message passing; contextual atom/bond and graph-motif self-supervision; 10M molecules, large model about 100M parameters. [Paper](https://arxiv.org/abs/2007.02835) | Official `GROVER_base` and `GROVER_large` download links. [Repository](https://github.com/tencent-ailab/grover) | Old environment and documented nondeterminism; reported gains are protocol-specific |
| Uni-Mol | SE(3)-aware 3D transformer; masked atoms plus coordinate/distance recovery; 209M generated conformations and 3M pockets. [Paper](https://openreview.net/forum?id=6K2RM6wVqKu) | [`mol_pre_no_h_220816.pt`](https://github.com/deepmodeling/Uni-Mol/releases/download/v0.1/mol_pre_no_h_220816.pt); pocket model `pocket_pre_220816.pt`. [Official repository](https://github.com/deepmodeling/Uni-Mol) | Requires conformers; generated conformers inject method bias and do not represent food mixture environments |

## Theory and Mechanisms

\[
T(A,B)=\frac{|A\cap B|}{|A|+|B|-|A\cap B|}
\]
\[
h^{t+1}_{vw}=\tau\!\left(h^0_{vw}+W_m\sum_{u\in N(v)\setminus\{w\}}h^t_{uv}\right)\quad\text{(D-MPNN)}
\]
\[
z_i=\rho\!\left(\sum_{m\in F_i}w_{im}\,\phi([e_m,q_{im}])\right)\quad\text{(weighted Deep Set)}
\]
\[
\mathcal L_i=-\log\frac{\exp(s(z_i,z_i^+)/\tau)}{\exp(s(z_i,z_i^+)/\tau)+\sum_j\exp(s(z_i,z_j^-)/\tau)}
\]

**Established:** Deep Sets characterizes permutation-invariant functions using a transform, symmetric aggregation, and output map under its theorem’s domain/continuity conditions. [Deep Sets](https://proceedings.neurips.cc/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html) Set Transformer adds pairwise interactions and pooling by multihead attention; inducing-point attention changes \(O(n^2)\) self-attention to \(O(nm)\). [Set Transformer](https://proceedings.mlr.press/v97/lee19d)

**Inferred failure modes:** Mean pooling erases cardinality and dilutes rare potent compounds; sum pooling entangles profile size with signal; max pooling ignores accumulation; unweighted presence treats trace and dominant compounds equally. Attention can over-select frequent or well-annotated molecules, and its weights must not be interpreted as causal sensory importance. `q_im` should therefore contain concentration/OAV where available, detection status, source confidence, process state, and missingness indicators. Unknown concentration must not be encoded as zero.

## Contrastive Positives, Negatives, and Hubness

**Q-L2 decision:** Use *the same canonical ingredient-state or molecule observed independently through different sources/views* as the primary positive. Alternate valid molecular encodings may supervise molecular invariance; independently curated records may supervise entity alignment. Recipe co-occurrence, shared compounds, and ontology-category membership are unsuitable as primary positives when those same signals define evaluation.

Matched raw→processed observations should supervise a transformation vector, not be collapsed as positives. Pairing labels should come from independent sensory studies, panels, or a separately held-out corpus. Negatives must be matched on ingredient category, recipe frequency, compound-set size, source count, and cuisine exposure; an unobserved pairing is not automatically a true negative. InfoNCE and false-negative concerns are grounded in [CPC](https://arxiv.org/abs/1807.03748) and [Debiased Contrastive Learning](https://arxiv.org/abs/2007.00224).

**Established:** High-dimensional nearest-neighbour spaces can develop hubs, measured by \(N_k(x)=\sum_q\mathbf1[x\in kNN(q)]\). [Hubness study](https://www.jmlr.org/papers/v11/radovanovic10a.html) **Inferred:** FlavorGraph-style random walks add degree bias, while recipe corpora add frequency bias. Audit \(N_k\) skewness and its Spearman association with graph degree, recipe frequency, \(|F_i|\), and number of contributing sources; report retrieval by frequency decile and cold-start status.

## FlavorGraph: Architecture and Novelty Boundary

**Established:** FlavorGraph contains ingredient, flavor-compound, and drug-compound nodes. Ingredient-ingredient edges derive from Recipe1M co-occurrence/NPMI; chemical edges derive from FlavorDB and HyperFoods. It learns 300-dimensional embeddings using food-specific metapaths plus random walks, skip-gram negative sampling, and an auxiliary binary-cross-entropy task reconstructing 881-bit PubChem/CACTVS fingerprints for compound nodes. Only 416 of 6,653 ingredients were reported to have flavor-compound links; 1,114,285 walks were generated with average length 46.36. Its clustering NMI was 0.309 on the chemically linked ingredient subset, while pairing and novel food-compound recommendations lacked a scientific gold-standard evaluation. [Paper](https://www.nature.com/articles/s41598-020-79422-8), [code](https://github.com/lamypark/FlavorGraph)

**Data warning:** The publication reports 111,355 ingredient-ingredient and 35,440 ingredient-compound edges and 147,179 total edges, but elsewhere gives 164,531 ingredient-flavor edges. These are internally inconsistent. The released files must be counted and checksummed before replication.

**Q-L3 answered:** FlavorGraph already covers static heterogeneous food/chemical embeddings, recipe context, fingerprint supervision, cosine pairing retrieval, vector arithmetic, and food-compound link prediction. It does **not** establish process-conditioned molecular transitions, concentration/OAV-aware set encoding, reaction mechanisms, uncertainty-aware provenance, before/after chemistry, or independently validated sensory compatibility. Those are CGAS’s defensible boundary.

## Verified Data and API Inventory

| Resource | Access, identifiers, and join keys | Terms/status and principal risks |
|---|---|---|
| [RecipeDB](https://academic.oup.com/database/article/doi/10.1093/database/baaa077/6006228) | Web interface; 118,171 recipes, 268 processes and 23,548 ingredients in the paper’s overview; generic ingredient and USDA mappings | Site data CC BY-NC-SA 3.0; no public stable API/schema verified. Paper contains a 20,262 versus 23,548 ingredient-count discrepancy |
| [FlavorDB](https://academic.oup.com/nar/article/46/D1/D1210/4559748) | Per-record JSON/SDF/Mol2; 25,595 molecules, 2,254 mapped to 936 ingredients; PubChem CID is molecular primary key | Data CC BY-NC-SA 3.0. Ingredient IDs and FlavorDB2 migration stability require professor confirmation |
| [DietRx](https://cosylab.iiitd.edu.in/dietrx/faq) | Official FAQ reports 2,337 foods, 6,992 chemicals, 20,550 genes; diseases use MEDIC/MeSH/OMIM | CC BY-NC-SA 3.0; food/compound key schema and API unverified; inferred links must not be treated as measured effects |
| [Foodoscope](https://www.foodoscope.com/about) | Commercial site claims 118K+ recipes, 1,000+ ingredients, 2,400+ molecules and REST APIs | Endpoint schema, stable IDs, rate limits, export rights, model-training rights, and licence **unverified** |
| [FooDB](https://foodb.ca/schema) | Downloads and API demo; food `public_id`, compound `FDBxxxxxx`; PubChem, ChEBI, HMDB, CAS, InChIKey and structures available | CC BY-NC 4.0; concentration records require units, method, tissue/part, and source handling. Full API availability should be tested |
| [VCF](https://www.vcf-online.nl/VcfHome.cfm) | Subscription search using CAS, FEMA and FLAVIS; official site reports v16.10, >13,300 compounds and 182,000+ occurrences | Proprietary subscription, reportedly weekly updates; bulk/API and derivative-model rights **unverified** |
| [Flavornet](https://flavornet.org/) | Static browser covering 738 odorants, GC-O evidence, retention indices, CAS and descriptors | Page dates to 2004; no API, bulk licence, or maintenance commitment found |
| [GoodScents](https://www.thegoodscentscompany.com/search.html) | Search by name, CAS, EINECS, FEMA, FLAVIS, JECFA and descriptors | No public API/bulk licence verified; use only as a reference until written terms are obtained |
| [Pyrfume](https://pmc.ncbi.nlm.nih.gov/articles/PMC11557823/) | Python/R/REST access; archives connect stimuli, subjects and behaviour; PubChem CID crosswalk | Dataset-level licences vary and must be propagated; [official data repository](https://github.com/pyrfume/pyrfume-data) and [versioned Zenodo record](https://doi.org/10.5281/zenodo.13820408) |
| [PubChem](https://pubchem.ncbi.nlm.nih.gov/docs) | CID, SID and AID; PUG-REST, PUG-View and FTP; CID/InChIKey should anchor molecular joins | Active. NCBI imposes no blanket restriction on its records, but depositor-specific rights/provenance can apply |
| [FoodOn](https://github.com/FoodOntology/foodon) | `FOODON:nnnnnnnn`, OWL/PURL and ontology browsers; suitable for food, part and process concepts | CC BY 4.0 and maintained; ontology mappings do not themselves prove chemical identity or equivalence |
| [FoodAtlas](https://www.nature.com/articles/s41538-025-00680-9) | 1,430 foods, 3,610 chemicals and 48,474 quantitative food-chemical associations; FoodOn IDs, PubChem CIDs, source references and concentration metadata; current [official code](https://github.com/AI-Institute-Food-Systems/foodatlas) exposes a REST-backed graph platform | Published in 2026; code is Apache-2.0, but incorporated source licences still apply. Its extraction pipeline reported F1 = 0.67, so extracted associations require provenance-aware validation rather than treatment as ground truth |
| [Recipe1M+](https://arxiv.org/abs/1810.06553) | Over 1M recipes and about 13M images; registration/download; internal recipe and vocabulary IDs | Official code states research access for universities/research institutions. No standard open data licence verified |
| [ReciFine](https://aclanthology.org/2026.findings-eacl.210/) | HF CSV: 2,231,142 recipes, 97M+ silver entity mentions, ten entity types; ReciFineGold has 500 recipes | CC BY-NC 4.0; derived from RecipeNLG, with source URLs rather than canonical food IDs. [Dataset card](https://huggingface.co/datasets/nuhuibrahim/recifine) |
| [ReGraph](https://arxiv.org/html/2608.06917v1) | 10,000 Recipe1M recipes, 318,773 entities and 391,051 relations; ingredient/action/tool nodes; `targ`, `dest`, `followed_by` | August 2026 preprint; test 1,500 human-validated, training semi-automatic. Dataset/code access and data licence remain **unverified**; paper says release is forthcoming |

## Professor Endpoint Audit Implications

Require machine-readable schema/version, authentication, pagination, rate/export limits, permitted storage, commercial and model-training rights, update/deletion semantics, and record-level provenance. Request at least 50 representative records from every endpoint and test uniqueness, referential integrity, orphan rates, and whether IDs are genuinely shared across RecipeDB, FlavorDB, DietRx, and Foodoscope.

For ingredients, audit species/cultivar, anatomical part, raw/processed state, synonyms and FoodOn mapping. For compounds, require CID, full stereochemical InChIKey, structure, salt/mixture status and source. For observations, require concentration plus unit/basis, threshold, LOD/LOQ, analytical method, citation and confidence. For processing, audit explicit input/output entities and \(\theta=(T,t,a_w,pH,O_2,\text{fat},\text{geometry})\). **Q-P1 remains unanswered:** a process label alone is insufficient evidence of a molecular or sensory transition.

## Decisions Recommended Versus Experiments Required

**Decide now:** preserve E0–E3; freeze molecular weights at E5; begin set learning only at E6; use FlavorGraph as a named baseline; separate chemical identity from food identity/state; preserve source-local IDs and licences; prohibit random-only splits; prohibit co-occurrence-trained models from claiming success on co-occurrence reconstruction.

**Experiments required:** E2 versus each E5 checkpoint on identical source-, scaffold/cluster-, time-, and ingredient-cold-start splits; mean/sum/max/OAV/attention pooling ablation; cross-source positive-definition ablation; frequency and hubness audit; with/without provenance-confidence features; conformer sensitivity for Uni-Mol; and an explicit source-transfer test where an entire database is held out. Report multiple seeds, uncertainty intervals, AUPRC/calibration for imbalanced classification, and Recall/nDCG plus frequency-stratified retrieval.

## Open Questions Status

- **Q-L1:** **Unanswered.** Current evidence rejects assuming pretrained encoders beat ECFP; only the controlled CGAS bake-off resolves it.
- **Q-L2:** **Answered provisionally.** Primary positive = independently observed same canonical molecule or ingredient-state; process deltas and pairing are separate objectives.
- **Q-L3:** **Answered.** FlavorGraph’s scope and exclusion boundary are specified above.
- **Professor endpoint:** **Unanswered.** Availability is not evidence of stable shared IDs, before/after states, concentrations, or reuse permission.
- **Absence-of-evidence note:** No public API/licence found for several resources does not prove none exists; it means no authoritative public specification was verified in this audit.

## Model Ladder E0–E5

| Level | Model | Gate |
|---|---|---|
| **E0** | Exact shared-compound count \(n_{ij}\) | Data/provenance sanity baseline |
| **E1** | Jaccard, Ochiai and IDF-weighted overlap | Tests profile-size and ubiquitous-compound effects |
| **E2** | ECFP + Tanimoto + fixed set-to-set aggregation | Mandatory structural baseline for Q-L1 |
| **E3** | RDKit/Mordred descriptor distance + fixed aggregation | Tests whether simple physicochemistry explains gains |
| **E4** | node2vec/metapath2vec, including FlavorGraph replication | Shallow graph/context baseline; audit degree/frequency leakage |
| **E5** | Frozen ChemBERTa-2, MoLFormer, Mol2Vec, SELFormer, GROVER, Uni-Mol or frozen D-MPNN representation + the same fixed aggregator | Must beat E2/E3 on identical splits before E6 or fine-tuning |

## Data Acquisition and Join Plan

1. **Contract gate:** obtain licences/terms and professor API specifications before bulk acquisition or model training.
2. **Immutable landing:** snapshot raw files/responses with source URL, retrieval date, version, licence, checksum and request parameters.
3. **Molecule registry:** standardize without discarding originals; retain stereochemistry, charge, isotope and mixture status; map CID, InChIKey, CAS/FEMA/FLAVIS/FDB IDs with `exact/ambiguous/rejected` confidence.
4. **Food registry:** internal immutable UUID plus FoodOn ID, taxon, part, cultivar, form and process state; never merge “onion,” “onion powder,” and “fried onion” solely by lexical similarity.
5. **Observation layer:** represent ingredient-compound links as sourced observations carrying concentration, units, method, condition, evidence and licence, not timeless binary facts.
6. **Join QA:** publish per-source mapping coverage, collision/orphan counts, ambiguity queues, compound-set-size distributions and source overlap. Fit models only after split assignment at the source entity level to prevent duplicate leakage.

**Bibliography:** [ChemBERTa](https://arxiv.org/abs/2010.09885); [ChemBERTa-2](https://arxiv.org/abs/2209.01712); [MoLFormer](https://arxiv.org/abs/2106.09553); [SELFIES](https://arxiv.org/abs/1905.13741); [SELFormer](https://doi.org/10.1088/2632-2153/acdb30); [Mol2Vec](https://doi.org/10.1021/acs.jcim.7b00616); [D-MPNN/Chemprop](https://arxiv.org/abs/1904.01561); [AttentiveFP](https://doi.org/10.1021/acs.jmedchem.9b00959); [GROVER](https://arxiv.org/abs/2007.02835); [Uni-Mol](https://openreview.net/forum?id=6K2RM6wVqKu); [Deep Sets](https://proceedings.neurips.cc/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html); [Set Transformer](https://proceedings.mlr.press/v97/lee19d); [FlavorGraph](https://www.nature.com/articles/s41598-020-79422-8); [RecipeDB](https://academic.oup.com/database/article/doi/10.1093/database/baaa077/6006228); [FlavorDB](https://academic.oup.com/nar/article/46/D1/D1210/4559748); [FoodAtlas](https://www.nature.com/articles/s41538-025-00680-9); [Pyrfume](https://pmc.ncbi.nlm.nih.gov/articles/PMC11557823/); [Recipe1M+](https://arxiv.org/abs/1810.06553); [ReciFine](https://aclanthology.org/2026.findings-eacl.210/); [ReGraph](https://arxiv.org/abs/2608.06917).
