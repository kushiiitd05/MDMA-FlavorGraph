# CGAS — Consolidated Research Synthesis and v4 Reconciliation

**File:** `research/CGAS_consolidated_research_synthesis_2026-09-04.md`
**Written:** 2026-09-04
**Scope of this file:** reconcile every source presently in `~/Desktop/CGAS` against the SSOT
(`computational_gastronomy_master_roadmap_v4.md`), state what is already incorporated, state what is
still missing, resolve the cross-track evidence tensions, and deliver a completed **§11 (Project A —
Model Ladder)**.
**Status of this file:** *reference material, not doctrine.* Under §139.4 nothing here is frozen until
it is restated in the SSOT with its uncertainty attached. Every change this file proposes to the SSOT is
tagged **`[v4 update]`** and carries a target anchor.
**Non-destructive guarantee:** no existing file was deleted, overwritten, or edited to produce this
document. It is additive only.

---

## C0. How to read this file

| If you want… | Read |
| --- | --- |
| what exists and what it is | **C1** corpus inventory |
| what R1–R5 already changed in the SSOT | **C2** incorporation audit |
| what is still missing | **C3** gap register `G1–G23` |
| where the five tracks agree or collide | **C4** evidence reconciliation `T1–T11` |
| the completed §11 | **C5** — paste-ready |
| every other proposed SSOT edit | **C6** write-back queue `U1–U19` |
| the merged question register | **C7** |
| what in here is *not* solid | **C8** uncertainty ledger |
| symbol/terminology collisions to fix in code | **C9** |
| whether the Level 0–11 dump is fully absorbed | **C10** |
| what to do next | **C11** |

**Evidence labels used throughout** (identical to R1–R5 and §139.5):
**established** = directly supported by a cited primary source · **inferred** = derived from established
results · **assumed** = a project convention chosen for now · **unverified** = requires CGAS data,
an audit, or an experiment. Where a claim in this file is not labelled, it is a statement *about the
CGAS documents themselves* and is verifiable by reading them.

---

## C1. Corpus inventory — everything read for this synthesis

| File | Size | Date | Role | Status |
| --- | --- | --- | --- | --- |
| `computational_gastronomy_master_roadmap_v4.md` | 187 KB / 7 560 lines | 3 Sep 2026 | **SSOT.** PART I §0–§127 (= v3.3 core) · PART II §128–§139 (addendum) · PART III §140–§148 (R1–R5 synthesis) | live |
| `computational_gastronomy_master_research_roadmap_v3_3.md` | 130 KB / 6 486 lines | 26 Aug 2026 | Predecessor | superseded by v4 PART I |
| `uptill_plan andlevel11_dump.txt` | 301 KB / 12 504 lines | 3 Sep 2026 | Raw session transcript: original brainstorm → Levels 0–11 taught in full → hand-off to Level 12 | source material |
| `research/R1_fingerprints_similarity.md` | 16 KB | 3 Sep 2026 | D1 — fingerprints, coefficients, nulls, set-to-set operators | complete |
| `research/R2_physchem_quantum_descriptors.md` | 17 KB | 3 Sep 2026 | D2 — descriptors, volatility, BDE, conceptual DFT, `P→θ` | complete |
| `research/R3_cooking_reaction_chemistry.md` | 36 KB | 3 Sep 2026 | D3 — reaction chemistry, kinetics, transport, extraction protocol | complete |
| `research/R4_structure_odor_sensory.md` | 29 KB | 3 Sep 2026 | D4 — structure→odour/taste/texture, inference boundary | complete |
| `research/R5_encoders_and_data_landscape.md` | 22 KB | 3 Sep 2026 | D5 — molecular/set encoders, FlavorGraph boundary, data & licence inventory | complete |

### C1.1 On "the Codex research reports"

`R1`–`R5` **are** the Codex-agent reports. v4 §140 records that they "were reconstructed on 3 September
2026 by five independent research agents after the earlier Claude background agents failed before
returning reports." No other agent output exists anywhere in `~/Desktop/CGAS`; the directory contains
exactly the eight files above. **[unverified]** — if a separate set of Codex reports exists outside this
directory, it was not in scope and has not been read.

### C1.2 What "§11" is taken to mean here

`§`-notation in this project addresses **SSOT section numbers**, and levels are written "Level *n*".
This file therefore completes **v4 §11 — PROJECT A — MODEL LADDER**, which is presently a 25-line stub
(one sentence per rung A0–A7) while every comparable ladder in the document (§96 B0–B6, §133.3 E0–E8,
§143 T0–T4, §145 sensory ladder) carries contracts, gates and caveats. See **C5**.
For completeness, **C10.2** separately certifies the state of *Level 11*, in case that reading was
intended: Level 11 is already frozen in §132 and needs no completion, only the write-backs listed in C6.

---

## C2. Incorporation audit — what R1–R5 already changed in the SSOT

### C2.1 The seven existing `[v4 update]` write-backs

Grep of the SSOT for `v4 update` returns exactly seven substantive anchors. This is the complete set of
PART I / PART II edits made after the research round:

| # | SSOT line | Section | Source | What it froze |
| --- | ---: | --- | --- | --- |
| 1 | 3025 | §64 Process-effect schema | R2/R3 | compact schema is a *view*, not the storage contract; lists the mandatory provenance/driver/missingness fields |
| 2 | 5152 | §111 Chemistry→sensory | R4 | structure supports bounded single-molecule prediction only; product-level `Y^sens` needs concentration + stereo + matrix + protocol |
| 3 | 6928 | §132.4 Tanimoto | R1 | `1−T` metric; Dice is a monotone transform; MinMax ≠ dot-product Tanimoto; no universal threshold |
| 4 | 6953 | §132.5 Set-to-set | R1 | aggregation is a required ablation axis; kernel mean + balanced OT primary; OT is a candidate, not a winner |
| 5 | 6969 | §132.6 Weighting ladder | R2/R4 | tiered OAV weight with missingness preserved; `OAV>1` ≠ character impact |
| 6 | 7068 | §133.3 Encoder ladder | R5 | named E5 checkpoints; pretraining scale is not evidence; non-circular positive definition; mandatory splits and audits |
| 7 | 7163 | §135.2 D2 brief | R2/R3 | "susceptible" ≠ "heat cleaves the bond"; BDE/QM gate plausibility only |

A byte-diff of v4 PART I against v3.3 confirms that **write-backs 1 and 2 are the only two edits made
anywhere in §0–§127**; the rest of PART I is v3.3 verbatim. That is the structural origin of most of the
gap register in C3.

### C2.2 What PART III (§140–§148) already carries

| SSOT section | Carries | From |
| --- | --- | --- |
| §140 | provenance, agent-failure history, evidence-label contract | — |
| §141 | the frozen `P → θ(x,t) → motifs → mechanism classes → Δchem/Δphys → sensory` chain; the three-value output contract | R2+R3 |
| §142 | E0/E1/E2 baseline stack; fingerprint/coefficient/aggregator as separate axes; Dice exclusion; no universal cutoff | R1 |
| §143 | compute tiers T0–T4; "no opaque structural-density scalar"; volatility field requirements; BDE boundary | R2 |
| §144 | ten retained mechanism families; "browning is not one pathway"; sparse evidence graph; censored non-detects; first seven curation cells | R3 |
| §145 | the six-rung admissible sensory target ladder; `Y^sens` stays factorised; Q-C7 partial pass; Q-L4 conditional | R4 |
| §146 | E5-must-beat-E2/E3 rule; FlavorGraph novelty boundary; registry/licensing rule; FoodAtlas addition | R5 |
| §147 | 15-row decision register (Q-C1…Q-L4) | all |
| §148 | seven-item next execution block | all |

**Assessment:** PART III is an accurate *executive* distillation. It is not a *complete* one — it
carries roughly the executive-findings layer of each report and drops the taxonomies, formulas, ablation
matrices, evaluation protocols, data inventories and bibliographies. Those are the C3 gaps.

---

## C3. Gap register — what is still missing from v4

Severity: **H** = blocks or corrupts a decision already scheduled in §148 · **M** = will corrupt a later
decision or a paper claim · **L** = completeness/curation.

| ID | Gap | Evidence | Target | Sev |
| --- | --- | --- | --- | :-: |
| **G1** | **§11 Project A model ladder is a stub.** No input/output contract, no held-constant list, no mapping to RQ1–RQ5 / §12 tasks / §13 metrics, no gate per rung, no evidence-status contract, no A↔E ladder crosswalk, no negative-result definition. | §11 vs §96/§133.3/§143/§145 | §11 | **H** |
| **G2** | **§24 Molecular encoder** still presents RDKit / ChemBERTa / GNN as three neutral "options". R5 establishes that pretraining scale does not predict downstream gain and that E5 must beat E2/E3 on identical splits first. Anyone implementing from §24 alone will pick a transformer for the wrong reason. | R5 exec. findings; §146.1 | §24 | **H** |
| **G3** | **§102 pooling baselines** (mean / weighted / DeepSets / attention) carry no cardinality-bias analysis, no OT rung, and no "unknown concentration must not be encoded as zero" rule. | R1 set-operator section; R5 inferred failure modes | §102 | **H** |
| **G4** | **Two un-crosswalked ladders.** §96 gives FlavorTwin B0–B6; §133.3 gives E0–E8. They overlap but differ in rung count, ordering and naming (B2 recipe co-occurrence has no E-equivalent; E3 descriptor-space has no B-equivalent). Ablation tables will not line up. | §96 vs §133.3 | §96 | **H** |
| **G5** | **§10.2 process-effect scope is unreconciled with R3.** §10.2 says 15–30 ingredients × 4–8 processes with a nine-field YAML record. R3 specifies a 40 × 12 sparse design, a thirteen-block schema, a twelve-step extraction protocol, and estimates **1–4 usable paired papers per mainstream ingredient, 0–1 for long-tail**. §10.2 is not marked superseded and its YAML is now dangerously thin. | R3 §12–§14; §64 update | §10.2 | **H** |
| **G6** | **§65 FlavorTwin profile schema** has no provenance, licence, uncertainty, analytical-method or missingness fields, while §64 (Project A) now does. The two projects share infrastructure (§20) but not storage honesty. | R2 schema; R3 §12; R5 join plan | §65 | **H** |
| **G7** | **§48 data splitting** lists recipe / ingredient / process / pair / cuisine / source splits but not R5's mandatory **chemical scaffold-or-cluster split**, **ingredient cold-start split**, **time split**, or the rule *split at source-entity level before duplicate records from multiple databases can leak across folds*. | R5 "Decide now" + join plan | §48 | **H** |
| **G8** | **Internal contradiction, unmarked.** §135.3's brief states heat/mass transfer explains "why Maillard needs a dry surface above ~140–150 °C". R3 §6 explicitly instructs: *"reject universal folklore thresholds such as 'Maillard starts at 140 °C'"* and R3 §2.4 establishes that wet cooking does not prohibit Maillard chemistry. The commissioning framing survives in the SSOT next to the finding that refutes it. | R3 §2.4, §6 | §135.3 | **H** |
| **G9** | **Non-monotonicity is not written into the prediction targets.** §4.4 Level 4 ("specific molecules") and §64's direction fields assume a direction exists. R3 establishes that 2-AP accumulates *more* at 100 °C than at 120–140 °C and that acrylamide is formed and eliminated simultaneously. "Direction" is only defined inside a stated driver window. | R3 §2.3, §5.1 | §4.4, §64 | **H** |
| **G10** | **R1's fingerprint taxonomy is absent.** §132.2 names only Morgan/circular. Missing: MACCS (167 positions, bit 0 unused), RDKit path, FCFP, atom pair, topological torsion, 2D pharmacophore, MHFP6, MAP4, 3D, reaction fingerprints; the folding-collision expectation `K[1−(1−1/K)^h]`; Sort & Slice; and the full required ablation matrix. §142 compresses all of this to one table row. | R1 taxonomy + ablation matrix | §132.2, §142 | M |
| **G11** | **R2's minimum viable descriptor schema** (8 blocks: identity/provenance, 2D_core, reactive_motifs, volatility, 3D_optional, QM_optional, process_theta, quality) has no home in the SSOT. §143 gives compute tiers but not the field list. | R2 §"Minimum Viable Descriptor Schema" | new §64-adjacent | M |
| **G12** | **Release physics missing from §105.** The Clausius–Clapeyron relation, Henry-constant conventions (8 IUPAC variants; Sander compilation), and the three-phase headspace equation `C_a = n·K_aw / (V_w + K_ow·V_o + K_aw·V_a)` are the mechanism by which fat suppresses aroma. §105 ("physical profile — a missing but essential bridge") is the natural home and does not contain them. | R2 volatility section | §105 | M |
| **G13** | **§107 "what a process actually changes"** keeps unqualified chopping / boiling / roasting examples. R3's ten-family mechanism taxonomy, the heat/moisture PDEs, the thermal-exposure integral `Ω_j`, and the formation-minus-loss balance are not written back. | R3 §3, §4 | §107 | M |
| **G14** | **§92 training objectives A–E not reconciled with R5's positive-pair ruling.** R5 rules recipe co-occurrence, shared compounds and ontology-category membership **unsuitable as primary positives** when those same signals define evaluation. §92 Objective A (distil classical similarity) and Objective C (culinary context) are exactly those signals. They remain valid as *auxiliary/sanity* objectives — that demotion is not written down. | R5 Q-L2; §133.2 | §92 | M |
| **G15** | **Data landscape and licences.** §10.1 lists five CoSyLab resources. R5 verified thirteen more with identifiers, join keys and terms — and found **RecipeDB / FlavorDB / DietRx are CC BY-NC-SA 3.0, FooDB CC BY-NC 4.0, ReciFine CC BY-NC 4.0, VCF proprietary-subscription, Recipe1M+ research-access-only**. Non-commercial licensing is never stated in the SSOT, yet §47 plans a SaaS and §72 plans public demos. | R5 inventory | §10.1, §47, §72, §146.3 | **H** |
| **G16** | **Published-source inconsistencies found by R5 are not recorded.** FlavorGraph reports 147 179 total edges in one place and 164 531 ingredient-flavor edges in another; RecipeDB's paper gives both 20 262 and 23 548 ingredients. Both must be counted and checksummed before replication — §138.1 and the E4 baseline depend on it. | R5 FlavorGraph + RecipeDB rows | §138, §96-B4 | M |
| **G17** | **§49 confidence/uncertainty** predates the frozen three-value evidence contract (`unsupported` / `physically_possible` / `evidence_supported`, §141) and does not reference it. | §141 | §49 | M |
| **G18** | **Q-M1–Q-M4 have no research track.** R1–R5 covered chemistry (Q-C), process (Q-P) and learning (Q-L). The four statistics/methodology questions were never routed to an agent and do not appear in §147's register. Q-M4 (do embeddings re-encode frequency?) is now partly answerable via R5's hubness protocol, and nobody has noticed. | §137 vs §147 | §137, §147 | M |
| **G19** | **Q-P4 unaddressed.** "Can `θ` be recovered from recipe text at all?" was routed to a Level-13 experiment and no track touched it. R3 lists it among its own unanswered questions. It gates whether the process-effect model can ever run on real recipes rather than curated cells. | §137; R3 §16 | §137 | **H** |
| **G20** | **Dump 8.23 not frozen:** the distinction between a **recipe-level null** (distribution of `N_s(R)`) and a **cuisine-level null** (distribution of `N_s(C^{(b)})`), with the instruction to compute both and never conflate them. §122.1D and §122.1E each cover half of it without naming the distinction. | dump L8.23 | §122.1 | M |
| **G21** | **R4's evaluation apparatus absent.** The activity-cliff diagnostic `A_ab = d_sens/(d_chem+ε)`, the enantiomer/"Sell triplet" dedicated evaluation, the seven-step character-impact evidence ladder, the five absence rules, the panel model `y_spr = μ+α_s+β_p+γ_r+(αβ)_sp+ε`, and the ISO 8586/13299/13301/11036 protocol anchors are in R4 only. §13 (metrics) and §145 carry none of them. | R4 | §13, §145 | M |
| **G22** | **§53 Gate A/B not re-evaluated.** The gate decides which project is the primary paper. Q-P1 is still unanswered, but R3 now establishes the literature route is *sparse but viable* and R5 establishes the professor endpoints are *unaudited*. The gate's prior probabilities have shifted and the section does not say so. **[inferred]** | R3 §11; R5 endpoint section | §53 | M |
| **G23** | **No consolidated bibliography.** §75/§76 were verified 15 Aug 2026 and predate ~90 primary citations introduced by R1–R5 (Rogers & Hahn, Baldi & Nasr, Cuturi, Gretton, Deep Sets, Set Transformer, Hodge, Mottram, Knol, Cai, Ludikhuyze, Weemaes, Blanksby & Ellison, Keller, Lee, Pellegrino, ISO standards, FoodAtlas, ReGraph, …). | R1–R5 bibliographies | §75, §76 | L |

---

## C4. Evidence reconciliation — where the five tracks converge and where they collide

Each item states the tracks involved, the resolution, and whether the resolution is a **decision** (can
be frozen now) or an **experiment** (cannot).

### T1 — Set aggregation is the dominant axis, and nobody has measured it
**Tracks:** R1 (set-to-set operators), R5 (Deep Sets / Set Transformer failure modes), §132.5 worked example.
**Converge:** the aggregation choice moves the answer more than the molecule kernel does. §132.5's own
2×2 example gives `S_mean = 0.50` vs `S_sym = 0.85` on identical kernel values.
**Collide, mildly:** R1 nominates *balanced optimal transport* as the leading estimand; R5 warns that any
learned aggregator will over-select frequent, well-annotated molecules. These are compatible — R1 speaks
to the fixed-aggregator rung (E2/E3), R5 to the learned rung (E6).
**Resolution — decision:** aggregation is a first-class ablation axis at every rung, never an
implementation detail. Fixed order for the axis: kernel mean (cardinality-normalised control) · directed
max · symmetric max · top-1/5/10 % · one-to-one matching · balanced OT with cost `1−T`. Report
cardinality–score slope, rank stability, runtime and null percentile for each.
**Still experiment:** which aggregator wins on CGAS profile-size and source-count distributions. **[unverified]**

### T2 — Presence → concentration → OAV: partial, tiered, never global
**Tracks:** R2 (Q-C7 "not demonstrated"), R4 (Q-C7 "partial pass"), §132.6 (already updated).
**Converge exactly.** FlavorDB2 lists 25 595 molecules but only 2 254 linked to 936 ingredients; FooDB
stores concentration with quantified/detected/expected/predicted status but published completeness for
the CGAS ingredient × process × threshold join is absent from both.
**Resolution — decision:** the five-rung tiered weight of §132.6 is correct and should be replicated into
§102, §103 and §65, not left only in the Level-11 section. Missing concentration is **unknown**, encoded
as an explicit missingness indicator, never as zero and never as presence-1.
**Still experiment:** the field-level coverage audit (Q-C7 closure). **[unverified]**

### T3 — The missing middle layer is *release*, not chemistry and not perception
**Tracks:** R2 (volatility, Henry, three-phase partition), R4 (matrix effects, static liquid-phase OAV is
at best an approximation to `c_i^effective(t)/T_i`).
**Converge:** both independently arrive at the same conclusion from opposite ends — R2 from physics, R4
from sensory measurement. Fat volume and oil affinity reduce equilibrium headspace concentration; fat
reduces nosespace release and perceived intensity.
**Resolution — decision:** insert an explicit **release layer** between `C^chem` and `Y^sens` in §111's
prediction chain, and give §105 the physics (G12). Without it, `G_θ(z^chem, z^phys, context)` has no
mechanism for the single best-documented matrix effect in the corpus.

### T4 — Mechanism gating is agreed; rate and yield are not
**Tracks:** R2 (BDE / motifs / conceptual-DFT gate plausibility), R3 (condition-gated mechanism classes),
§141 and §135.2 (already updated).
**Converge:** a reactive motif plus an available driver window makes a mechanism class *eligible*.
Neither track supports rate or yield from structure.
**Resolution — decision:** already frozen in §141's three-value output contract. What is missing is that
§107 and §4.4 still speak as if a process implies an effect (G9, G13).

### T5 — "More heat → more product" is false, and the SSOT still implies it
**Tracks:** R3 only, but it is decisive. 2-AP accumulation was **highest at 100 °C**, not 120–140 °C,
because depletion accelerates faster than formation; acrylamide requires formation *and* elimination terms;
sucrose loss and colour development in caramelisation have similar lag phases but different rates.
**Resolution — decision:** every direction label in §64 and every Level-4 target in §4.4 must be scoped
to a stated driver window, and the schema must be able to represent *non-monotone* and *peak-then-decline*.
This is a schema change, not a caveat.

### T6 — Pretrained molecular encoders have not earned inclusion
**Tracks:** R5 (Chemprop; the 2025 25-model × 25-dataset benchmark preprint finding almost no consistent
gain over ECFP), §133.3 and §146.1 (already updated), §24 (**not** updated — G2).
**Resolution — decision:** E5 is a *candidate set*, not a component. Selection happens only after E2/E3
are beaten on identical source-, scaffold/cluster-, time- and ingredient-cold-start splits.
**Note the asymmetry:** this is written correctly in PART II/III and incorrectly in PART I. A reader
following §54's week-by-week roadmap into §24 gets the pre-research framing.

### T7 — Circularity: §92's objectives need demotion, not deletion
**Tracks:** R5 (Q-L2 primary positive = the same canonical molecule or ingredient-state observed
independently through different sources/views), §133.2 (circularity rule already frozen).
**Collide with PART I:** §92 Objective A distils classical similarity and Objective C uses culinary
context. Both are, in R5's terms, unsuitable as *primary* positives because the same signals define
evaluation.
**Resolution — decision:** keep A and C as **sanity/auxiliary** objectives explicitly excluded from the
headline claim, exactly as §133.2 already permits distillation "as a sanity check … before being asked to
exceed it". Raw→processed matched observations supervise a **transition vector**, never invariance.
Negatives matched on category, recipe frequency, compound-set size, source count and cuisine exposure.

### T8 — The novelty boundary is now precise and should be quoted, not paraphrased
**Tracks:** R5 (FlavorGraph: ingredient + flavor-compound + drug-compound nodes; Recipe1M co-occurrence /
NPMI edges; FlavorDB + HyperFoods chemical edges; metapath2vec + skip-gram; auxiliary 881-bit
PubChem/CACTVS fingerprint reconstruction; only 416 of 6 653 ingredients had compound links; clustering
NMI 0.309 on the linked subset; **no scientific gold standard for its pairing recommendations**).
**Resolution — decision:** §3.2, §70 and §71 should name the exclusion explicitly rather than saying
"not novel enough by itself". CGAS's defensible frontier: process-conditioned ingredient state · explicit
molecule-set aggregation · concentration/OAV-aware weighting · reaction and transport mechanisms ·
provenance-aware uncertainty · independent process or sensory evaluation.
**Opportunity, [inferred]:** FlavorGraph's own lack of a pairing gold standard is itself a publishable
gap — an independently-evaluated pairing benchmark is a contribution CGAS can make cheaply.

### T9 — A universal Maillard threshold survives inside the SSOT
**Tracks:** R3 vs §135.3. See G8. Also relevant: R3 establishes DSC transition values are matrix-specific
(Baltic herring myosin 39.59 °C, sarcoplasmic 51.67 °C, connective 63.16 °C, actin 74.40 °C — explicitly
non-transferable), and enzyme inactivation `E_a` ranges from 60.5 to 164 kJ/mol *for the same enzyme
family across matrices*.
**Resolution — decision:** strike the threshold framing from §135.3 with a correction marker (never a
deletion, per §139.2) and replace it with the surface-drying energy-balance explanation.

### T10 — Frequency bias has a measurement protocol now
**Tracks:** §93 (frequency debiasing, mandatory before any embedding claim), §121 (frequency vs category),
R5 (hubness `N_k(x) = Σ_q 1[x ∈ kNN(q)]`, Spearman association with degree, recipe frequency, `|F_i|`,
source count; retrieval reported by frequency decile).
**Resolution — decision:** Q-M4 was previously routed only to "§93 debiasing check". It now has a
concrete, citable protocol. Route Q-M4 to the R5 hubness audit and make the frequency-decile retrieval
table a required output of every learned rung.

### T11 — Coverage confound is stated in three places and measured in none
**Tracks:** §124.1 "coverage confound", §131.6 (Q-C1), R1 (source-count strata + cardinality-matched
downsampling + degree-preserving null), R5 (per-source mapping coverage, collision/orphan counts,
compound-set-size distributions, source overlap must be *published*).
**Converge on method:** `observed profile size = true chemistry × annotation coverage`. The fix is not a
normalisation choice; it is a measurement — record source count, study count, method and provenance per
ingredient, then re-run under cardinality-matched downsampling.
**Resolution — decision:** the coverage audit is a *deliverable of §138.1*, not a later refinement,
because §138.2's similarity sensitivity pass is uninterpretable without it.

---

## C5. §11 COMPLETED — PROJECT A: MODEL LADDER

> **`[v4 update — §11, R1–R5 reconciled]`** The following replaces §11 in full. The A0–A7 rung names and
> ordering are unchanged from v3.3; everything else is new. Nothing in §12–§14 is contradicted.

### 11.0 What this ladder is, and what it is not

The ladder is **an ablation design, not a build plan**. Each rung adds exactly one mechanism to the rung
below it, holds everything else fixed, and is evaluated on the same split with the same metrics. A rung
exists so that the *next* rung's gain can be attributed. A rung that cannot be evaluated separately does
not belong on the ladder.

Three ladders now exist in this document and they are orthogonal:

| Ladder | Axis | Owner | Rungs |
| --- | --- | --- | --- |
| **A0–A7** (this section) | system composition for Project A | CulinaryState-RAG | what the system is allowed to know |
| **B0–B6** (§96) / **E0–E8** (§133.3) | representation for Project B | FlavorTwin | how an ingredient is encoded |
| **T0–T4** (§143) | compute expenditure | shared | how much chemistry we pay for |

A-rungs consume representations; they do not define them. See the crosswalk in 11.8.

### 11.1 Fixed experimental frame — identical across A0–A7

Any difference between rungs other than the one named is a confound. The following are frozen for the
whole ladder:

- **Split.** Recipe-level and process-level splits per §48, *plus* R5's additions (G7): source hold-out,
  ingredient cold-start, time. Splits are assigned at source-entity level **before** any de-duplication
  join, so that the same recipe or the same study arriving through two databases cannot straddle folds.
- **Task suite.** The same §12 Task 1–9 instances, same prompts, same decoding parameters, same seed set.
- **Backbone LLM.** One frozen instruction-tuned model for A0–A6. Changing the backbone is a separate
  experiment, never a rung.
- **Evidence-status contract.** Every process-effect claim any rung emits is labelled `unsupported` /
  `physically_possible` / `evidence_supported` (§141). A rung that emits an unlabelled chemical claim
  fails regardless of its accuracy.
- **Numerical restraint.** No rung emits a concentration, percentage or yield unless it comes from a
  measured record or a calibrated kinetic/transport model with stated initial conditions (§10.3, §141).
- **Reporting.** ≥3 seeds, uncertainty intervals, calibration (Brier/ECE) wherever a rung emits a
  probability, and per-task error breakdown by §67 categories.

### 11.2 The rungs

Notation: `S_t` current food state (§63, §106) · `P_t, θ_t` process and its drivers (§25, R2 `θ`) ·
`R_t` recipe context (§62) · `U` user context (§61) · `G(·)` relevance gate (§7) · `E` retrieved evidence.

---

#### A0 — LLM only
**Input:** recipe text + question. **Adds:** nothing.
**Tests:** how much of the benchmark is solvable from parametric knowledge alone.
**Why it must exist:** if A0 already scores high on a task, that task does not discriminate and should be
dropped from the headline table, not kept as an easy win.
**May not claim:** any chemistry. A0's chemical statements are recorded as `unsupported` by construction
and are a *measurement of the hallucination rate*, which is itself a result worth reporting.
**Gate to A1:** task suite runs end-to-end; per-task A0 scores logged as the floor.

---

#### A1 — LLM + generic recipe RAG
**Adds:** retrieval over an undifferentiated recipe corpus with generic chunking.
**Tests:** whether retrieval alone closes the gap — the null hypothesis for the entire project.
**Deliberately weak:** uses the generic 500-token chunking that §40 forbids for the real system. A1 is the
strawman that §40's chunking argument must beat; it is not an implementation target.
**May not claim:** state awareness. A1 has no notion of *when* in the procedure the question is asked.
**Gate to A2:** A1 − A0 measured per task. If A1 ≈ A7 on some task, that task is a retrieval task and is
reported as such rather than as evidence for state modelling.

---

#### A2 — + structured recipe state
**Adds:** the §62/§63 state representation and the step-indexed state graph; recipe-aware chunking (§40).
**Tests:** **RQ1 / H1** — does explicit state tracking improve current-state and next-action reasoning?
**Primary tasks:** Task 1 (current state), Task 2 (next action). Secondary: Task 3.
**Primary metrics:** state accuracy, state-transition consistency, exact match, macro-F1 (§13).
**Data prerequisite:** structured recipes with resolved entities (§43 identity resolution). Cannot run on
free text alone.
**Known failure mode to report, not hide:** state extraction error propagates. Report Task-1 accuracy
*conditioned on* extraction correctness, and report the extraction error rate separately.
**May not claim:** anything about chemistry or process effects — A2 has no effect knowledge.
**Gate to A3:** H1 is either supported or refuted with intervals. A refutation here is a legitimate paper
result and changes the emphasis of §14's minimum publishable unit; it does not stop the ladder.

---

#### A3 — + process-effect lookup
**Adds:** retrieval from the curated process-effect evidence set (§10.2 as revised, §64, §144) —
**lookup only, no prediction**. If the (ingredient, process, driver-window) cell has no record, the system
must answer "no evidence for this cell", not interpolate.
**Tests:** **RQ2 / H2**, first half — does *grounded* effect knowledge improve transformation-sensitive
answers and explanations?
**Primary tasks:** Task 3 (transformation explanation), Task 8 (process comparison).
**Primary metrics:** direction accuracy, evidence support, citation correctness, factual consistency (§13).
**Data prerequisite:** the R3 first-ten curation cells (§144.3) at minimum. **This rung is the reason the
curation work exists.**
**The coverage measurement that makes A3 honest:** report *answer rate* alongside accuracy. A3 will
decline to answer often — R3 estimates 1–4 usable paired papers per mainstream ingredient and 0–1 for
long-tail ingredients, so the evidence graph is sparse by construction (**[inferred]**, not a bibliometric
result). A high-accuracy, low-coverage A3 is the expected and publishable outcome.
**May not claim:** generalisation. A3 is a lookup table with a language interface.
**Gate to A4:** coverage and accuracy reported separately; the sparsity of the evidence graph quantified
on real curated data rather than estimated.

---

#### A4 — + process-effect predictor
**Adds:** `T_φ(S_t, P_t, θ_t) → ΔS` (§112, §4.4) for cells with no direct record, gated by mechanism
plausibility (§141, R2 motif gates, R3 mechanism families).
**Tests:** **RQ2 / H2**, second half — does *prediction* extend the grounded gain to unseen cells?
**Output resolution ladder (§4.4), each with its own admissibility rule:**

| Level | Target | Admissible when |
| --- | --- | --- |
| 1 Physical | texture/moisture/colour direction | process-state features present |
| 2 Sensory | odour/taste/texture direction, factorised (§145) | matrix + protocol stated; never a single "flavour score" |
| 3 Chemical mechanism | which mechanism class is eligible | motif + driver window both present |
| 4 Specific molecules | which compound classes rise/fall | **direction is defined only inside a stated driver window** — formation and destruction co-occur, and products can peak then decline (T5) |

**Primary metrics:** macro-F1 over effect classes, direction accuracy, calibrated confidence, Brier/ECE.
**Split requirement:** held-out **ingredient × process cells**, not held-out records. A model that has
seen `garlic × sauté` may not be evaluated on `garlic × sauté` at a different temperature and be reported
as generalising.
**May not claim:** yields, concentrations, rates. `E_a` values are matrix-specific and non-portable
(R3 §9: HMF 90.2 kJ/mol in milk vs 139.9 kJ/mol in tomato; LOX 60.5–164 kJ/mol by matrix).
**Gate to A5:** A4 − A3 measured on held-out cells; the non-monotone cases (2-AP, acrylamide) present in
the test set and reported separately, since they are where a naive predictor fails.

---

#### A5 — + user context
**Adds:** `U` (§61) — equipment, skill, time, dietary and cultural constraints — into the decision
formulation of §8.
**Tests:** **RQ3 / H3** — does context increase feasible-action rate without destroying recipe intent?
**Primary tasks:** Task 4 (process substitution), Task 5 (equipment adaptation), Task 6 (ingredient adaptation).
**Primary metrics:** constraint satisfaction rate, invalid recommendation rate, plus an explicit
**intent-preservation** score — the trade-off is the finding, so both halves must be reported together.
**May not claim:** nutritional or health benefit. §45's boundary holds: constraints are handled, health
claims are not made.
**Gate to A6:** feasibility gain and intent loss both quantified.

---

#### A6 — + relevance gate
**Adds:** `G(S_t, P_t, R_t, Q_u) → {0,1}` or a probability (§7); deep process-effect retrieval and the
A4 predictor fire only when the gate opens.
**Tests:** **RQ5 / H5** — does selective routing preserve quality while cutting unnecessary calls?
**Primary task:** Task 9 (chemistry relevance) plus the *cost* dimension of every other task.
**Primary metrics:** gate precision/recall against annotated query categories; **quality retained vs calls
saved**, reported as a curve, not a point; cost per query (retrievals, predictor invocations, latency).
**Implementation order (§7):** rule-based → classifier → learned. Report all three; the rule-based gate is
the baseline the learned gate must beat, exactly as E2 is for E5.
**Asymmetric error rule:** a false negative (chemistry needed, gate closed) is worse than a false positive
(chemistry not needed, gate opened). Weight and report them separately; do not summarise the gate with F1.
**May not claim:** efficiency without the quality curve alongside it.
**Gate to A7:** the quality/cost frontier is drawn.

---

#### A7 — full system
**Adds:** nothing new — A2 ⊕ A3 ⊕ A4 ⊕ A5 ⊕ A6 composed, plus the recovery module (§9).
**Tests:** **RQ4 / H4** via Task 7 (mistake recovery), and the composition question: are the rung gains
additive, redundant or antagonistic?
**Primary metrics:** target-state preservation, feasibility, expert acceptability (§13); state-distance
correctness for recovery.
**Mandatory leave-one-out ablation:** A7 minus state, minus effects, minus context, minus gate. Additive
gains are the expected story; **redundancy or interference is the more interesting one** and must be
reported if found.
**May not claim:** that the system "understands cooking". The claim ceiling is the §12 task suite under
the §48 splits, with the §141 evidence contract.

---

### 11.3 Rung → research question → task → metric map

| Rung | Adds | RQ / H | Primary §12 tasks | Primary §13 metrics | Hard prerequisite |
| --- | --- | --- | --- | --- | --- |
| A0 | — | floor | all | all | none |
| A1 | generic RAG | retrieval null | all | Recall@K, MRR, nDCG | recipe corpus |
| A2 | structured state | RQ1 / H1 | 1, 2 | state accuracy, transition consistency | §43 entity resolution |
| A3 | effect lookup | RQ2 / H2a | 3, 8 | direction accuracy, evidence support, **answer rate** | §144.3 curated cells |
| A4 | effect predictor | RQ2 / H2b | 3, 8 (unseen cells) | macro-F1, Brier/ECE | held-out cell split |
| A5 | user context | RQ3 / H3 | 4, 5, 6 | constraint satisfaction, invalid-rate, intent preservation | §61 schema |
| A6 | relevance gate | RQ5 / H5 | 9 + cost of all | gate P/R, quality-vs-cost curve | annotated query categories |
| A7 | full + recovery | RQ4 / H4 | 7 + all | target-state preservation, expert acceptability | all above |

### 11.4 What each rung is forbidden to claim

A single table, because ablation papers fail here more often than they fail at measurement:

| Rung | Forbidden claim |
| --- | --- |
| A0 | any chemistry (its chemical output is a hallucination-rate measurement) |
| A1 | state awareness; procedure understanding |
| A2 | anything about process effects |
| A3 | generalisation beyond curated cells |
| A4 | rates, yields, concentrations; portability of any `E_a` |
| A5 | health, nutrition or safety benefit |
| A6 | efficiency without the paired quality curve |
| A7 | culinary understanding; anything outside the §12 suite under §48 splits |

### 11.5 Decision-gate coupling (§53)

The ladder is robust to the Gate A / Gate B outcome, and that is deliberate:

- **Gate A** (process data rich): A3 and A4 carry the paper; the curated evidence set is the contribution.
- **Gate B** (process data sparse, flavour/recipe data good): A2, A5, A6 carry the paper; A3/A4 are
  reported at low coverage and **the sparsity itself is a finding** — R3's evidence-shape result is the
  citable justification. **[inferred]** Given R3's coverage estimate and the still-unaudited endpoints
  (Q-P1), Gate B currently looks more likely than v3.3 assumed; this does not change the ladder, only the
  section of it that becomes the headline.

### 11.6 Minimum publishable subset of the ladder

Against §14: **A0, A1, A2, A3, A7** is a complete paper. A4 (learned predictor), A6 (learned gate) and
vision-based state estimation remain the stretch items §14 already names. A5 is cheap and should be kept
because RQ3 is the one question no prior work in §3.1 addresses.

### 11.7 Failure definitions — decided in advance

| Outcome | Reading |
| --- | --- |
| A2 ≈ A1 | state representation adds nothing → RQ1 refuted; report it, pivot emphasis to RQ2/RQ5 |
| A3 ≈ A2 | either the evidence set is too sparse to bite, or the tasks are not transformation-sensitive → diagnose with the answer-rate table before concluding |
| A4 < A3 on held-out cells | predictor is worse than declining to answer → keep the lookup, report the negative result, do not ship the predictor |
| A6 loses quality with cost | gate is mis-specified → report the frontier, keep A7 ungated |
| gains non-additive in A7 | the mechanisms are redundant → the most interesting available result; investigate rather than suppress |

### 11.8 A-ladder ↔ representation-ladder crosswalk

A-rungs consume whatever ingredient representation the Project-B ladder has certified. The dependency is
one-directional and minimal:

| A-rung | Minimum representation it needs | Rung in §96 / §133.3 |
| --- | --- | --- |
| A0–A2 | none (text + structured state) | — |
| A3 | molecule identity and provenance only | E0 |
| A4 | molecule identity + motifs + driver window; optionally descriptor distance | E0 + T0 (§143), optionally E3 |
| A5–A6 | unchanged | — |
| A7 | as A4; process-conditioned `z_{i,t}` is a **stretch**, not a prerequisite | E8 (stretch) |

**Frozen consequence:** Project A never blocks on Level 12. A learned encoder is an enhancement to A4,
not a dependency of it. This is what keeps the two projects independently publishable (§20).

### 11.9 §11 gate checklist

- [ ] Can state, per rung, the single mechanism it adds and the single thing it is forbidden to claim.
- [ ] Can name the split that makes A4 an honest generalisation test.
- [ ] Can explain why A3 reports answer rate next to accuracy.
- [ ] Can explain why the gate's false negatives and false positives are weighted differently.
- [ ] Can state the outcome that would refute H1, and what the paper becomes if it is refuted.

---

## C6. Write-back queue — every other proposed `[v4 update]`

Each entry is paste-ready and follows §139.2 (**append and mark, never delete**). Ordered by severity,
then by SSOT position. `U1` is C5 above.

---

### U1 — §11 · Project A model ladder · **H** · sources R1–R5 + §12/§13/§48/§53/§141
Replace §11 in full with **C5** of this file.

---

### U2 — §24 · Molecular encoder options · **H** · source R5

> **`[v4 update — R5, distilled in §146.1]`** Options A/B/C are not equivalent candidates. Fingerprints
> plus a fixed aggregator (Option A) are the **mandatory baseline**; a SMILES transformer or GNN
> (Options B/C) may enter the system only after beating that baseline on identical source-,
> scaffold/cluster-, time- and ingredient-cold-start splits. Pretraining corpus size is not evidence of
> downstream quality: a 2025 benchmark of 25 pretrained models across 25 datasets found almost no
> consistent gain over ECFP, and Chemprop found fingerprints competitive or superior on small datasets.
> Every named checkpoint (ChemBERTa-2, MoLFormer, Mol2Vec, SELFormer, GROVER, Uni-Mol, frozen D-MPNN)
> was pretrained on PubChem/ZINC/ChEMBL or generated conformers — never on food mixtures,
> concentrations, cooking transformations or sensory outcomes. See §133.3 for the ladder that governs
> selection.

---

### U3 — §102 · Molecule-set aggregation · **H** · sources R1, R5

> **`[v4 update — R1/R5, distilled in §142]`** Baselines A–D are a required **ablation axis**, not a
> menu. Mean pooling erases cardinality and dilutes rare potent compounds; sum pooling entangles profile
> size with signal; max pooling ignores accumulation; unweighted presence treats trace and dominant
> compounds identically. Add two rungs: **kernel mean** (`S_mean = Σ_ab w_a v_b k(a,b)`, cardinality-
> normalised and PSD when `k` is) as the simplest control, and **balanced optimal transport**
> (`S_OT = 1 − min_π Σ_ab π_ab[1 − k(a,b)]`) as the leading estimand candidate. Directed max, symmetric
> max, top-k and one-to-one matching are controls; one-to-one optimal assignment is not automatically a
> PSD kernel. Report cardinality–score slope, rank stability, runtime and degree-preserving-null
> percentile for every aggregator. **Unknown concentration is a missingness indicator, never zero.**
> Attention weights are model parameters, not sensory importance — the caution already in this section
> extends to every learned aggregator.

---

### U4 — §10.2 · Process-effect evidence set · **H** · source R3

> **`[v4 update — R3, distilled in §144]`** The scope above is superseded in three ways.
> **(a) Design:** 40 ingredients across starch staples, legumes, meats/fish, dairy/egg, Alliums/Brassicas,
> other vegetables, fruits, nuts/seeds and fermentation substrates × 12 standardised states
> (raw-intact, cut/rested, boiled, steamed, pressure-cooked, roasted/baked, pan-sautéed, deep-fried,
> microwaved, sous-vide, fermented, chilled/reheated). The matrix is **sparse by design**; inapplicable
> cells are marked explicitly, never imputed.
> **(b) Yield:** plan for roughly **1–4 usable directly-paired papers per mainstream ingredient and 0–1
> for many long-tail ingredients** (**[inferred]** — a planning estimate from a scoped search, not a
> bibliometric census; the exact count per ingredient is **[unverified]** until the Q-P2 systematic search
> runs). A dense 240–600-cell quantitative matrix cannot be assumed.
> **(c) Record:** the nine-field YAML above is a *view*. The storage contract is §64 as revised plus R3's
> thirteen blocks: provenance · ingredient identity · initial state · ordered process sequence · geometry ·
> thermal drivers · chemical drivers · observation (with LOD/LOQ and censoring) · analytical method ·
> matched contrast · mechanism claim · quality flags · licensing. Non-detects are **censored
> observations, not zeros**. Boiling cells must account for cooking liquor, condensate, lid state and
> water ratio, or mark them explicitly unmeasured — "vanished" must never be recorded as "destroyed".
> The twelve-step extraction protocol and the first ten curation cells are in R3 §13–§14 and §144.3.

---

### U5 — §65 · FlavorTwin profile schema · **H** · sources R2, R3, R5

> **`[v4 update — R2/R3/R5]`** This schema is a *view*. Project B's storage contract carries the same
> honesty fields as Project A's (§64): for every ingredient-compound link, an **observation** record with
> source and licence, analytical method, concentration with units/basis, LOD/LOQ and censoring status,
> threshold and its matrix/route/definition, stereochemistry, process state, evidence tier and explicit
> missingness. Ingredient-compound links are **sourced observations, not timeless binary facts**.
> Molecule anchor: PubChem CID + full stereochemical InChIKey. Food anchor: internal immutable ID +
> FoodOn, with taxon, part, cultivar, form and process state. "onion", "onion powder" and "fried onion"
> are never merged by lexical similarity.

---

### U6 — §48 · Data splitting · **H** · source R5

> **`[v4 update — R5]`** Add four mandatory split axes to the six above: **chemical scaffold or cluster**
> split (molecular generalisation), **ingredient cold-start** split (unseen ingredient), **time** split
> (dataset-version drift), and **source hold-out** (an entire database withheld, as an explicit
> source-transfer test). Random-only splits are prohibited. **Split assignment happens at source-entity
> level before de-duplication joins**, so that duplicated records arriving from multiple databases cannot
> leak across folds. A model trained on co-occurrence may not claim success on co-occurrence
> reconstruction (§133.2).

---

### U7 — §10.1 / §47 / §72 · Licensing reality · **H** · source R5

> **`[v4 update — R5, distilled in §146.3]`** Licence terms are a **design constraint, not paperwork**.
> Verified: RecipeDB, FlavorDB and DietRx site data are **CC BY-NC-SA 3.0**; FooDB is **CC BY-NC 4.0**;
> ReciFine is **CC BY-NC 4.0**; VCF is a **proprietary subscription** with unverified bulk/API and
> derivative-model rights; Recipe1M+ states research access for universities/research institutions with
> no standard open licence verified; Flavornet and GoodScents have **no verified public API or bulk
> licence**; FoodOn is CC BY 4.0; PubChem imposes no blanket restriction but depositor-specific rights can
> apply; FoodAtlas code is Apache-2.0 while its incorporated source licences still apply.
> **Consequences:** (i) the §47 SaaS and any §72 public demo cannot be built on NC-licensed data without
> separate permission; (ii) model-training rights are a distinct grant from data-access rights and must be
> asked for explicitly in the §42 professor audit; (iii) every landed record keeps its source licence
> field. Absence of a found licence is **not** permission — it is an unanswered question.

---

### U8 — §135.3 · Correction of the Maillard threshold framing · **H** · source R3

> **`[v4 update — R3, correction]`** The phrase "why Maillard needs a dry surface above ~140–150 °C while
> the interior sits at ~100 °C" was the **commissioning framing and is superseded**. R3 establishes:
> (i) universal folklore thresholds such as "Maillard starts at 140 °C" are rejected; (ii) wet cooking
> does not prohibit Maillard chemistry — long time, concentrated boundary layers, pressure, pH and
> precursor composition can produce Maillard products well below roasting temperatures; (iii) the correct
> mechanism is an **energy balance**: a wet surface spends incoming energy on evaporation and stays near
> the local wet-bulb/boiling condition until surface moisture flux declines, after which contact,
> convective or radiative heating raises it above the interior. Store local time–temperature–moisture
> exposure and report increasing plausibility, never a threshold crossing.

---

### U9 — §4.4 and §64 · Direction is window-scoped, and can be non-monotone · **H** · source R3

> **`[v4 update — R3]`** Prediction Level 4 ("specific molecules") and every direction field in §64 must
> be scoped to a stated driver window. Formation and destruction proceed simultaneously
> (`dC_P/dt = r_form − r_consume − r_volatilisation − r_leaching`), so abundance is frequently
> **non-monotone in temperature and time**: 2-acetyl-1-pyrroline accumulated highest at 100 °C rather than
> 120–140 °C because depletion accelerated faster than formation, and acrylamide requires simultaneous
> formation and elimination terms. The schema must be able to express *rises, falls, peaks-then-declines,
> unknown* — a two-valued direction field is insufficient. "Hotter means more" is prohibited as a default.

---

### U10 — §137 / §147 · Route the unrouted questions · **H** · sources §137, R3, R5

> **`[v4 update]`** Q-M1–Q-M4 were never handed to a research track and are absent from §147's register.
> Route them now: **Q-M1** (recipe- vs pair-weighted aggregation) and **Q-M3** (`Gain_X` of an extended
> null lattice) close inside the §138.1 replication — they are code, not literature. **Q-M2** (`β1`
> survival under controls) closes with the §125 conditional model on real data. **Q-M4** (do embeddings
> re-encode frequency?) now has a citable protocol: R5's hubness audit — `N_k(x) = Σ_q 1[x ∈ kNN(q)]`,
> its skewness, and its Spearman association with graph degree, recipe frequency, `|F_i|` and source
> count, plus retrieval reported by frequency decile. **Q-P4** (can `θ` be recovered from recipe text at
> all?) remains unaddressed by every track and is a **hard gate on Project A's real-recipe deployment**:
> if `θ` cannot be recovered, A4 runs only on curated cells and §11.5's Gate-B reading becomes the
> paper. Promote Q-P4 to the same priority tier as Q-P1.

---

### U11 — §132.2 / §142 · Full fingerprint taxonomy and the folding arithmetic · M · source R1

> **`[v4 update — R1]`** The molecule representation ladder names only circular fingerprints. The
> defensible ablation set is: **MACCS** (RDKit returns 167 positions, bit 0 unused; public key
> definitions contain toolkit-dependent ambiguities) · **RDKit path** · **Morgan/ECFP** (radius 2 ≈ ECFP4)
> · **FCFP** (pharmacophore-class invariants) · **atom pair** · **topological torsion** · **2D
> pharmacophore** · **MHFP6** · **MAP4** · 3D shape/pharmacophore (deferred until conformer and
> protonation policy is frozen) · reaction fingerprints (deferred to explicitly represented
> transformations). RDKit describes its circular output as *similar to* ECFP/FCFP, not bit-identical.
> **Folding arithmetic (inferred, uniform hashing):** for `h` unique features into `K` positions, expected
> occupied bits are `K[1 − (1 − 1/K)^h]` and expected aliases `h − K[1 − (1 − 1/K)^h]`; binary folding
> additionally saturates repeats. Collision-free/sparse representations therefore belong in the ablation;
> Sort & Slice improved supervised ECFP models across its 2024 tasks but its vocabulary is training-set
> dependent and must be learned **inside each fold**. Benchmark dependence is established: 12 standard
> fingerprints over 88 targets were largely inseparable, so no fingerprint may be adopted on reputation.
> Current API surface: `GetMorganGenerator`, `GetRDKitFPGenerator`, `GetAtomPairGenerator`,
> `GetTopologicalTorsionGenerator` with `GetFingerprint` / `GetSparseCountFingerprint`; preserve
> `AdditionalOutput.bitInfoMap` for auditability.

---

### U12 — new subsection under §64 · Minimum viable descriptor schema · M · source R2

> **`[v4 update — R2]`** Molecule-level storage contract, eight blocks:
> `identity/provenance` canonical SMILES, InChIKey, stereochemistry, charge, tautomer, source,
> measured-vs-predicted flag ·
> `2D_core` formula, mass, elements, HBD/HBA, TPSA, logP/logD, rotatable bonds, rings, aromaticity,
> unsaturation, functional groups ·
> `reactive_motifs` reducing carbonyls, amines, sulfur motifs, ester/glycosidic bonds, allylic and
> **bis-allylic H counts**, antioxidant motifs ·
> `volatility` vapour-pressure value + model + **temperature**, `ΔH_vap`, boiling point + pressure, Henry
> constant with **convention/units/T**, oil-water or measured food-matrix partition ·
> `3D_optional` conformer method/energy/rank; ensemble **mean and spread** for WHIM, GETAWAY, RDF, area,
> volume, inertia ·
> `QM_optional` method/version, geometry, solvent, charge/multiplicity, HOMO/LUMO, ΔSCF IP/EA, `μ,η,ω`,
> Fukui values, charges, Wiberg orders, dipole, polarizability ·
> `process_theta` surface/core temperature traces, `a_w`, pH, oxygen exposure, fat amount/composition,
> geometry, time, pressure, airflow/agitation ·
> `quality` uncertainty, applicability domain, missingness **reason**, units, temperature, source record,
> calculation failure.
> Do not collapse "structural density" into one opaque scalar (§143). Store the "softness" convention
> explicitly — definitions differ by a factor of two.

---

### U13 — §105 · Release physics · M · source R2

> **`[v4 update — R2]`** The physical profile is where aroma **release** lives, and release — not
> composition — is what reaches the nose. Add: vapour pressure must always carry its temperature, via
> `ln(P₂/P₁) = −(ΔH_vap/R)(1/T₂ − 1/T₁)`; Henry constants must carry convention, units, solvent and
> temperature (the current Sander compilation holds 46 434 values for 10 173 species across eight
> IUPAC-recognised conventions — canonicalise one, retain the original); and the ideal three-phase
> equilibrium `C_a = n_total·K_aw / (V_w + K_ow·V_o + K_aw·V_a)` explains why adding oil, or increasing
> oil affinity, **lowers** equilibrium headspace concentration. **[assumed]** — this ideal form ignores
> emulsion interfaces, protein binding, starch encapsulation, diffusion and non-equilibrium release;
> experimental food-matrix studies confirm the direction but not the magnitude. Boiling point alone is a
> weak volatility descriptor; it is merely where saturation pressure meets external pressure.

---

### U14 — §107 · What a process actually changes · M · source R3

> **`[v4 update — R3, distilled in §141/§144]`** Replace the informal chopping/boiling/roasting examples
> with the mechanism-family view: a process name is not a chemical cause; the chain is
> `P → θ(x,t) → accessible mechanism classes → formation / depletion / transfer / physical
> reorganisation`. The ten retained families are in §144.1. Local drivers obey
> `ρc_p ∂T/∂t = ∇·(k∇T) + q̇` with a surface balance
> `−k∇T·n = h(T_s − T_∞) + q″_rad/contact − ṁ″_evap·L_v`, moisture by
> `∂X/∂t = ∇·(D_eff ∇X)`, and mechanism accessibility by the local thermal-reaction exposure
> `Ω_j(x) = ∫ A_j e^{−E_a,j/RT(x,t)} f_j(C, pH, a_w, O₂) dt`. Consequence: **air or oil temperature alone
> cannot determine reaction extent**; at minimum, estimated surface and core temperature histories plus
> moisture state are required. Cutting initiates chemistry before heating (alliinase, LOX/HPL, myrosinase,
> PPO); "enzyme inactive above X °C" is inadmissible without ingredient, assay, time, hydration, pH and
> kinetic model.

---

### U15 — §92 · Objective demotion · M · source R5

> **`[v4 update — R5, consistent with §133.2]`** Objectives A (distil classical similarity) and C
> (culinary context) are **auxiliary/sanity objectives and may never be the primary training signal when
> the same quantity defines evaluation**. The primary non-circular positive is *the same canonical
> molecule or ingredient-state observed independently through different sources or views*; alternate
> valid molecular encodings supervise molecular invariance; independently curated records supervise entity
> alignment. Matched raw→processed observations supervise a **transition vector**, not invariance —
> collapsing them as positives destroys exactly the signal Project B claims. Pairing labels must come from
> independent sensory studies or a separately held-out corpus. Negatives must be matched on ingredient
> category, recipe frequency, compound-set size, source count and cuisine exposure; **an unobserved
> pairing is not a true negative**.

---

### U16 — §96 · Ladder crosswalk and the FlavorGraph replication warning · M · sources R5, §133.3

> **`[v4 update — R5]`** B0–B6 and E0–E8 (§133.3) are the same axis at different resolutions. Crosswalk:
> B0→E0 · B1→E1 · **B2 (recipe co-occurrence / NPMI) has no E-rung and is an *evaluation* signal, not a
> representation rung — moving it into training triggers the §133.2 circularity rule** · B3→E2 (+E3 for
> descriptor space, which B-numbering omits) · B4→E4 · B5→E5–E7 · B6→E8.
> **Before replicating B4/E4:** FlavorGraph's published counts are internally inconsistent (147 179 total
> edges in one place, 164 531 ingredient-flavor edges in another) and RecipeDB's paper gives both 20 262
> and 23 548 ingredients. Count and checksum the released files first. Also note the scale of the chemical
> signal actually available to it: **only 416 of 6 653 ingredients had flavor-compound links**, and its
> clustering NMI of 0.309 is on that linked subset alone, with no scientific gold standard for its pairing
> recommendations.

---

### U17 — §13 and §145 · Sensory evaluation apparatus · M · source R4

> **`[v4 update — R4]`** Add to the metric set: **macro-AUPRC and per-label calibration** for imbalanced
> descriptors (AUROC is secondary); MAE/RMSE, concordance, rank correlation and calibrated intervals for
> intensity/threshold regression; centred cosine plus per-attribute error for sensory profiles, scored
> **against the panel's own test–retest ceiling**, not against 1.0. Hold out chemical scaffolds,
> **stereochemical pairs**, data sources, ingredients and process regimes. Report failure stratified by
> concentration, matrix, chemical distance, stereochemistry, descriptor frequency and assessor reliability.
> Use the activity-cliff diagnostic `A_ab = d_sens(a,b) / (d_chem(a,b) + ε)` and give enantiomer pairs a
> dedicated evaluation — aggregate AUROC conceals near-chance behaviour on exactly the cases that matter
> (a 3D model distinguished 11 enantiomer pairs structurally yet chose the correct enantiomer for only
> 19/34 differential labels, 55.9 %). Panel structure `y_spr = μ + α_s + β_p + γ_r + (αβ)_sp + ε` must be
> retained rather than averaged away. Protocol anchors: ISO 8586 (assessors), ISO 13299 (profiling),
> ISO 13301 (3-AFC thresholds), ISO 11036 (texture).
> **Five absence rules, frozen:** no database entry = unknown, not absent · no GC-MS peak = not detected
> *under that method* · no GC-O detection = not detected *by that panel at that dilution* · `OAV < 1` is
> not proof of no mixture contribution · a low model probability is not proof of odourlessness.
> **Character impact requires the full ladder:** identification → quantification → GC-O detection →
> AEDA/FD → matrix-matched OAV → recombination → omission. Jumping from step 1 to "character-impact
> compound" is not defensible.

---

### U18 — §49 and §122.1 · Two smaller freezes · M · sources §141, dump L8.23

> **`[v4 update — §141 cross-reference]`** §49's confidence scheme is subordinate to the frozen
> three-value evidence status: `unsupported` / `physically_possible` / `evidence_supported`. Model
> confidence and evidence status are **different quantities** and are reported separately; a
> high-confidence `unsupported` claim is a failure, not a hedge.

> **`[v4 update — dump L8.23]`** Distinguish the two null distributions explicitly and compute both:
> the **recipe-level null** (distribution of `N_s(R)` over many random recipes — tells us about recipe
> behaviour, tested in §122.1E) and the **cuisine-level null** (distribution of `N_s(C^{(b)})` over many
> whole random cuisines — tells us about uncertainty in the cuisine mean, tested in §122.1B/D). They
> answer different questions and must never be conflated or reported under one symbol.

---

### U19 — §75 / §76 · Bibliography refresh · L · sources R1–R5

> **`[v4 update]`** §76's links were verified 15 August 2026 and predate the research round. R1–R5
> introduce roughly ninety primary citations with DOIs, spanning fingerprint theory, set-kernel and
> optimal-transport theory, descriptor and conceptual-DFT definitions, cooking kinetics, sensory
> standards, encoder releases and the data/licence landscape. Rather than duplicate them, §76 should point
> to the per-report **Linked Bibliography** sections, which are the maintained lists.

---

### C6.1 Gap → write-back traceability

| Gap | Closed by | Gap | Closed by |
| --- | --- | --- | --- |
| G1 | U1 (= C5) | G13 | U14 |
| G2 | U2 | G14 | U15 |
| G3 | U3 | G15 | U7 |
| G4 | U16 | G16 | U16 |
| G5 | U4 | G17 | U18 |
| G6 | U5 | G18 | U10 |
| G7 | U6 | G19 | U10 |
| G8 | U8 | G20 | U18 |
| G9 | U9 | G21 | U17 |
| G10 | U11 | G22 | **C5 §11.5** (no separate write-back — the gate coupling is stated inside the completed §11) |
| G11 | U12 | G23 | U19 |
| G12 | U13 | | |

---

## C7. Merged open-question register (§137 × §147 + new)

Status vocabulary: **closed** = decided and frozen · **method-bound** = closure route is fully specified,
execution pending · **open** = no route yet.

| ID | Question | Status | Closure route | Owner rung/section |
| --- | --- | --- | --- | --- |
| Q-C1 | Is `\|F_i\|` confounded by annotation coverage? | method-bound | source-count/provenance audit + cardinality-matched downsampling + degree-preserving null | §138.1, T11 |
| Q-C2 | Does Tanimoto size bias change ingredient conclusions? | mechanism closed, materiality method-bound | coefficient × representation ablation at E2 | §142 |
| Q-C3 | Which set aggregator is least biased? | method-bound, **no universal winner** | aggregator × weighting × cardinality ablation | T1, U3 |
| Q-C4 | Which descriptors have documented flavour links? | conditionally closed | volatility/partition/concentration/threshold are direct; the rest are predictive-only → descriptor-family ablation with held-out processes | U12, U13 |
| Q-C5 | Can BDE/reactivity predict mechanism class? | closed **for plausibility gating only** | validate gates against measured time courses | §141, U14 |
| Q-C6 | Is xTB/DFT affordable at 2 k–25 k molecules on one GPU? | **open — [unverified]** | benchmark 100–300 stratified molecules on the actual CPU/GPU workflow before approving Tier 2 | §143 |
| Q-C7 | Is concentration/OAV coverage sufficient? | **partial pass** | field-level concentration/threshold/matrix audit by InChIKey | T2, §145 |
| Q-P1 | Does the professor's processing endpoint hold ingredient-level before/after states? | **open — highest-value external unknown** | endpoint inspection: schema, terms, ≥50 representative records, before/after fields | §42, §68 |
| Q-P2 | How many paired raw-vs-processed studies exist per ingredient? | feasibility inferred, census open | systematic search for the first ten ingredients | U4, §144.3 |
| Q-P3 | Minimum honest process-effect schema? | **closed** | implement §64 + §144 storage contract | U4 |
| Q-P4 | Can `θ` be recovered from recipe text at all? | **open — promoted to Q-P1 tier (U10)** | Level-13 extraction experiment; gates A4 on real recipes | §11.5, U10 |
| Q-P5 | Which ten ingredient × process cells give most leverage? | **closed (provisional panel)** | confirm feasibility, access and analytical budget | §144.3 |
| Q-M1 | Recipe- vs pair-weighted cuisine aggregation | method-bound *(newly routed)* | sensitivity analysis inside §138.1 | U10 |
| Q-M2 | Does `β1` survive frequency/category/profile-size controls? | method-bound *(newly routed)* | §125 conditional model on real data | U10 |
| Q-M3 | Does an extended null lattice add explanatory gain? | method-bound *(newly routed)* | §123.4 `Gain_X` | U10 |
| Q-M4 | Do learned embeddings re-encode ingredient frequency? | method-bound *(newly routed, now has a protocol)* | R5 hubness audit `N_k` + frequency-decile retrieval + §93 debiasing | U10, T10 |
| Q-L1 | Does a pretrained encoder beat ECFP+Tanimoto here? | **open — evidence currently says do not assume** | identical-split E2/E3 vs E5 bake-off | U2, §146.1 |
| Q-L2 | Non-circular positive-pair definition? | **answered provisionally** | cross-source positive-definition ablation | U15 |
| Q-L3 | What exactly does FlavorGraph already do? | **closed** | cite and replicate as E4/B4, after checksumming | U16 |
| Q-L4 | Can `Y^sens` be predicted from `C^chem` well enough to be a secondary contribution? | **conditional** | bounded panel-mean experiment after the Q-C7 audit | §145, U17 |
| **Q-N1** *(new)* | Do the published counts in FlavorGraph and RecipeDB reconcile against the released files? | open | count + checksum before any replication | U16 |
| **Q-N2** *(new)* | Which sources' licences permit model training and public demo, and which do not? | open | written terms per source; explicit ask in the §42 audit | U7 |
| **Q-N3** *(new)* | Does the release layer (`K_aw`, `K_ow`, matrix) improve sensory prediction over composition alone? | open | ablate release features in the Q-L4 experiment | T3, U13 |
| **Q-N4** *(new)* | Are the A-rung gains additive, redundant or antagonistic? | open | §11.7 leave-one-out ablation at A7 | §11 |
| Q-S1–Q-S4 | trivia · spoilage/e-nose · Ayurveda · video/audio | **parked, unchanged** | §46, §74, §94, §27–28 | — |

---

## C8. Uncertainty ledger — what in this file is *not* solid

Everything below is flagged so that no reader can mistake it for a result. Ordered by how much damage a
wrong assumption would do.

| # | Claim | Label | Why it is uncertain | What would settle it |
| --- | --- | --- | --- | --- |
| 1 | 1–4 usable paired papers per mainstream ingredient, 0–1 long-tail | **inferred** | R3 states this explicitly as a planning estimate from a scoped search, **not** a bibliometric census | the Q-P2 systematic search over the first ten ingredients |
| 2 | Balanced OT is the leading ingredient-set aggregator | **unverified** | R1 nominates it as an *estimand choice*; no primary study compares these operators on food ingredient-compound profiles with 10–100× cardinality variation. Absence of evidence, not evidence of equality | the Q-C3 ablation on real profile-size and source-count distributions |
| 3 | xTB is affordable for the CGAS molecule scale on one GPU | **unverified** | GFN2-xTB is designed for fast broad-element work and GPU builds exist, but no published throughput for CGAS-sized workloads | benchmark 100–300 stratified molecules on the actual workflow |
| 4 | Gate B is now more likely than Gate A | **inferred** | rests on R3's sparse-evidence finding plus the fact that Q-P1 is unaudited; a rich professor endpoint would flip it immediately | Q-P1 endpoint inspection |
| 5 | Concentration/OAV coverage is insufficient for global weighting | **inferred from two tracks** | R2 and R4 both report *absence of published completeness figures*, not measured insufficiency | the Q-C7 field-level audit |
| 6 | Perceptual descriptor profiles may be approximately linear in mixtures | **[E] but preprint-dependent** | the 432-mixture linear-averaging result is a **non-peer-reviewed preprint**, and its transfer to heated, fatty, viscous, reacting foods is explicitly unknown | replication in food matrices; T3/Q-N3 |
| 7 | The 3D/stereo olfaction result (19/34, 55.9 %) | **[E, provisional]** | preprint; small enantiomer-pair set | a dedicated dose-response enantiomer benchmark |
| 8 | The three-phase headspace equation | **assumed (ideal form)** | ignores emulsion interfaces, protein binding, starch encapsulation, diffusion and non-equilibrium release | calibrated headspace release in water-, oil-, starch- and protein-rich matrices |
| 9 | FoodAtlas associations | **provenance-bearing candidate, not ground truth** | its extraction pipeline reported F1 ≈ 0.67 and upstream licences are mixed | provenance-aware validation per record |
| 10 | Any transferred `E_a`, DSC transition or enzyme-inactivation temperature | **matrix-specific, non-portable** | R3 documents 60.5–164 kJ/mol for one enzyme family across matrices, and 90.2 vs 139.9 kJ/mol for HMF in milk vs tomato | measure in the target matrix, or do not use |
| 11 | "R1–R5 are the Codex research reports" | **inferred** | v4 §140 says five independent agents produced them after Claude agents failed; the word "Codex" appears nowhere in the corpus | user confirmation |
| 12 | "§11" means SSOT §11, not Level 11 | **assumed** | `§` addresses SSOT sections throughout this project and levels are written "Level *n*"; §11 is also the only stub-shaped section that matches "unfinished" | user confirmation — C10.2 covers the alternative reading |
| 13 | Everything in C5 (§11 completion) | **proposal, not doctrine** | it is a design synthesis, not an empirical result; §139.4 governs | acceptance into the SSOT with a version bump |

**Two standing rules this file obeys, restated because they are easy to violate in synthesis work:**
"I did not find X" is never written as "X does not exist" (§77, §139.5), and a project recommendation is
never converted into an empirical result (§140).

---

## C9. Terminology and symbol collisions to fix before code

Found while reconciling; each will silently corrupt an implementation.

| Collision | The two meanings | Rule |
| --- | --- | --- |
| `f_i` vs `df_m` | ingredient recipe-frequency vs molecule document-frequency | never share a symbol; §131.5 |
| `n_ij` vs `O_ij` vs `q_ij` | chemical overlap vs culinary co-occurrence vs cuisine-scoped co-occurrence count | §130.3/§130.4 |
| "count Tanimoto" | RDKit sparse-count Tanimoto is **MinMax**; dot-product Tanimoto is a different function whose `1−T` is not a metric (`√(1−T)` is) | name the exact function in code; R1 |
| `x_i^inc` vs `f_m` | ingredient × molecule incidence vs molecule × structural-feature fingerprint | different axes entirely; §132.3 |
| "softness" | conceptual-DFT definitions differ by a factor of two | store the definition, not just the field name; R2 |
| "profile" | classical compound-incidence profile `F_i^classical` vs the multi-block ingredient profile of §99 | §99's terminology freeze already covers it — enforce it |
| "process" | a label vs the driver set `θ(x,t)` | §64 update + §141; a label is never a cause |
| MinHash comparison | MinHash signatures compare by fraction of equal permutation minima, **not** featurewise Jaccard/cosine | R1 implementation warning |
| Model confidence vs evidence status | two independent axes | U18 |

---

## C10. Corpus coverage audit

### C10.1 The Level 0–11 dump

The transcript teaches Levels 0–11 and hands off to Level 12. Mapping of its subsections to the SSOT:

| Dump | Content | Canonicalised in | Complete? |
| --- | --- | --- | --- |
| 0.1–0.13 | food as chemical/physical/sensory/nutritional/biological/cultural/geographic/sustainability object; molecule, biomolecule, flavour compound, volatility, taste ≠ flavour | §2.1 layers A–J, §44, §99–§105 | yes |
| L1–L6 blocks | computational gastronomy definition, fundamental units, what a process is, two meanings of food processing, food state, flavour profile | §1, §2, §4, §99–§106 | yes |
| 7.1–7.21 | notation freeze, `n_ij`, `N_s(R)`, `N_s(C)`, worked calculation, pair normalisation, graph/matrix interpretation, what classical overlap aliases away, three things never to confuse | §80, §131.2 | yes |
| 8.1–8.25 | null models, monkey cuisines, recipe-size preservation, `ΔN_s`, `Z`, `p_emp`, M₀/M_F/M_C/M_FC, ablation framing, Indian-cuisine result | §81–§83, §121–§127 | yes, **except 8.23** → **G20 / U18** |
| 9.1–9.21 | `χ_i` term-by-term, frequency ≠ contribution, intra-category randomisation and its sign, pair-level `O_ij` vs `n_ij`, authenticity, five quantities, culinary fingerprint | §130 | yes |
| 10.1–10.26 | multi-hot `x_i^inc`, `n_ij = x_iᵀx_j`, `W = XXᵀ`, Jaccard/Ochiai, IDF, chance-adjusted overlap, two frequencies, annotation coverage, why baselines precede encoders | §131 | yes |
| 11.1–11.34 | SMILES/graph/descriptors/fingerprints ladder, Morgan circularity, bit meaning, Tanimoto, set-to-set aggregation, abundance, structure ≠ perception, molecule vs ingredient encoder, process-conditioned aggregation | §132 | yes, **extended by** U11 |

**Verdict:** the dump is materially absorbed. Its one unfrozen item is the recipe-level vs cuisine-level
null distinction (U18). Nothing else in the transcript changes a design decision that the SSOT does not
already carry.

### C10.2 Level 11 status *(in case "§11" meant Level 11)*

Level 11 is **frozen** at §132 and needs no completion: the ladder (§132.2), the two-binary-vector
warning (§132.3), Tanimoto with the R1 update (§132.4), set-to-set aggregation with the R1 update
(§132.5), the weighting ladder with the R2/R4 update (§132.6), structure ≠ perception (§132.7),
molecule-encoder ≠ ingredient-encoder including the process-conditioned consequence (§132.8), and the
gate checklist (§132.9). Its outstanding work is exactly **U11** (fingerprint taxonomy + folding
arithmetic) and **U3** (aggregation ablation into §102). Level 12 is the open gate, §133.

### C10.3 v3.3 → v4 delta

A byte-level diff confirms v4 PART I is v3.3 verbatim apart from the header block and the two write-backs
at §64 and §111. Everything genuinely new in v4 lives in PART II (§128–§139) and PART III (§140–§148).
**Implication:** PART I is now the least current part of the SSOT while remaining the part a new reader is
most likely to read first. §139's reading order (§128 → §129 → §140 → §147 → §148) mitigates this, and
the C6 write-backs are the durable fix.

---

## C11. Next execution block — delta against §148

§148's seven items stand. This synthesis adds sequencing constraints and three items:

**Unchanged and still first:**
1. §138.1 classical E0/E1 replication with the §80/§130 toy examples as unit tests.
2. Professor endpoint inspection, Q-P1 first.
3. R3 systematic paper census for the first ten cells.
4. Identity/provenance/concentration/threshold/matrix/licence audit.
5. R1 E2 representation × coefficient × aggregator ablation.
6. xTB benchmark before Tier 2; then E2/E3 vs frozen E5 on identical splits.
7. E6/Level 12 only after the classical, data and leakage gates pass.

**Added by this synthesis:**

- **N1 — fold the coverage audit into item 1, not after it.** Item 5's similarity sensitivity pass is
  uninterpretable without per-ingredient source counts (T11). Collect them during the replication.
- **N2 — count and checksum FlavorGraph and RecipeDB releases before item 5.** Two published-count
  inconsistencies are on record (Q-N1, U16); an E4/B4 baseline built on the wrong numbers poisons every
  comparison above it.
- **N3 — ask for licence and model-training rights in the same conversation as Q-P1.** They are separate
  grants (Q-N2, U7), and the answer constrains §47 and §72 regardless of how Q-P1 resolves.

**Sequencing constraint that is easy to get wrong:** items 2 and 3 are independent and should run in
parallel. Item 3's outcome is what makes Gate B survivable if item 2 disappoints, and item 3 is the
long-pole task — waiting on the endpoint before starting the census wastes the only work that is entirely
under our control.

---

## C12. Bottom line

- **Incorporated already:** the executive layer of all five reports, seven targeted write-backs, and the
  whole of PART III. Levels 7–11 are genuinely frozen. The process-transition architecture, the evidence
  status contract, the sensory inference boundary and the novelty boundary are all correctly stated.
- **Still missing:** §11 was a stub (now drafted, **C5**); PART I is otherwise unchanged from v3.3 and
  therefore contradicts PART II/III in three places that matter (§24 encoder framing, §10.2 evidence
  scope, §48 splits); licensing is an unstated constraint on the SaaS and demo plans; four statistics
  questions and Q-P4 were never routed; and one folklore threshold survives inside §135.3 next to the
  finding that refutes it.
- **The single highest-value unknown is unchanged:** Q-P1. The single most under-rated one is **Q-P4** —
  if `θ` cannot be recovered from recipe text, Project A runs on curated cells only, and §11.5's Gate-B
  reading becomes the paper.
- **Nothing here is frozen** until it is restated in the SSOT under §139 with its uncertainty attached.
