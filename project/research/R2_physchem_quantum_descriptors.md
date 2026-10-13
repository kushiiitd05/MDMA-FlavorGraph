# R2 / D2 Research Report

**Date:** 2026-09-03  
**Commissioning question:** Which molecular and process descriptors can make CGAS v4’s cooking transition model physically grounded, while limiting claims to supported mechanism classes and directional compound-class changes?

**Claim labels:** **Established** = directly supported; **Inferred** = project-level synthesis; **Assumed** = proposed approximation; **Unverified** = requires audit or experiment.

## Executive Findings

1. **Established:** Molecular descriptors are useful at different levels, but they are not interchangeable. Constitutional/topological descriptors encode composition and connectivity; WHIM, GETAWAY, and RDF encode one or more 3D conformations; quantum descriptors encode a specified electronic state and computational protocol.
2. **Established:** Vapour pressure at serving temperature, Henry constants, phase partitioning, concentration, and matrix effects are more directly connected to aroma release than boiling point alone. Boiling point is merely the temperature where saturation pressure reaches the specified external pressure.
3. **Established:** Bis-allylic lipid C-H bonds are substantially weaker than ordinary alkyl C-H bonds. This supports lipid-oxidation susceptibility and mechanism eligibility, but BDE is neither an activation barrier nor a yield predictor.
4. **Established:** HOMO/LUMO, hardness, electrophilicity, and Fukui functions may rank related reactants or sites under a consistent protocol. Their absolute values are method-, geometry-, charge-, and environment-dependent.
5. **Inferred:** xTB screening is operationally plausible for thousands of food molecules, but affordability for 2,000–25,000 molecules on one GPU is **unverified** until CGAS benchmarks its actual conformer and charge-state workload. Broad DFT optimization/frequency/BDE calculations should remain targeted.
6. **Established:** Temperature history, water activity, pH, oxygen, phase composition, and geometry interact. A process name such as “fry” cannot serve as the physical state.
7. **Unverified:** Existing public food databases contain concentrations or thresholds for some records, but no source found reports sufficient joined coverage of processed-food concentration plus matrix-appropriate threshold to replace presence weighting globally.

## Descriptor Taxonomy

| Level | Information | Recommended examples | Main limitation |
|---|---|---|---|
| 0D/constitutional | Formula-independent counts or composition | molecular mass, elemental counts, heavy atoms, heteroatoms, formal charge | Isomers can be indistinguishable |
| 1D/fragments | Ordered lists or fragment occurrence | functional-group counts, atom-centered fragments, reactive motifs | “0D/1D” terminology varies between descriptor systems |
| 2D/topological | Molecular graph | degree/connectivity indices, Wiener index, rings, aromatic fraction, E-state, fingerprints | No conformation, exposure, or matrix |
| Physicochemical | Bulk molecular behaviour | logP/logD, TPSA, H-bond counts, polarizability, vapour pressure, Henry constant | Predicted values inherit model domain and temperature assumptions |
| 3D/geometrical | A specified conformer or ensemble | surface/volume, WHIM, GETAWAY, RDF, inertia, 3D-MoRSE | Conformer generation and protonation can dominate |
| Electronic/QM | A specified electronic state | orbital energies, IP/EA, charges, bond orders, Fukui functions, dipole | Method-, state-, and environment-dependent |

[Mordred](https://pmc.ncbi.nlm.nih.gov/articles/PMC5801138/) implements more than 1,800 2D/3D descriptors. The [RDKit descriptor API](https://rdkit.org/docs/source/rdkit.Chem.rdMolDescriptors.html) provides WHIM, GETAWAY, and RDF calculations but requires a 3D conformer; its documentation also warns that published DRAGON WHIM values cannot always be reproduced exactly.

For centered coordinates \(X\) and atomic weights \(W\), WHIM begins from \(C_W=X^\top WX/\sum_iw_i\); eigenvalues describe weighted spatial extent, shape, and symmetry ([original WHIM paper](https://doi.org/10.1016/0169-7439(95)80026-6)). GETAWAY combines molecular-influence leverages \(H=X(X^\top X)^{-1}X^\top\), geometry, graph distances, and atomic weighting ([Consonni et al.](https://doi.org/10.1021/ci015504a)). RDF descriptors use terms such as \(\mathrm{RDF}(r)=\sum_{i<j}w_iw_j e^{-\beta(r-r_{ij})^2}\), producing a rotation/translation-invariant weighted distance distribution ([Hemmer et al.](https://doi.org/10.1016/S0924-2031(99)00014-4)).

**Recommendation:** Do not create an opaque “structural density” scalar. Store heavy-atom count, bond count, ring density, unsaturation, bis-allylic-H count, van der Waals volume, and graph density separately.

## Volatility And Matrix Physics

**Established:** At approximately constant vaporization enthalpy,

\[
\ln\frac{P_2^{sat}}{P_1^{sat}}
=-\frac{\Delta H_{vap}}{R}\left(\frac1{T_2}-\frac1{T_1}\right).
\]

Thus vapour pressure must be associated with temperature. The [NIST Chemistry WebBook](https://webbook.nist.gov/) provides critically sourced phase and vapour-pressure data; for example, its [limonene record](https://webbook.nist.gov/cgi/cbook.cgi?ID=C138863&Mask=E8F&Units=SI) reports a normal boiling point near 451 K and \(\Delta H_{vap}\) values around 46 kJ mol\(^{-1}\), depending on temperature and source.

Henry constants require convention, units, solvent, and temperature. The current [Sander compilation](https://www.henrys-law.org/henry/index.html) contains 46,434 values for 10,173 species and notes eight IUPAC-recognized conventions. CGAS should canonicalize one convention while retaining the original.

**Inferred ideal three-phase approximation:** If \(K_{aw}=C_a/C_w\) and \(K_{ow}=C_o/C_w\),

\[
C_a=\frac{n_{\mathrm{total}}K_{aw}}
 {V_w+K_{ow}V_o+K_{aw}V_a}.
\]

This explains why increasing oil volume or oil affinity can reduce equilibrium headspace concentration. It does not represent emulsion interfaces, protein binding, starch encapsulation, diffusion, or nonequilibrium release. Experimental food-matrix studies confirm that oil/water partition and matrix composition alter volatile release ([Guth and Rusu](https://doi.org/10.1016/j.foodchem.2007.12.015); [Tamaru et al.](https://doi.org/10.1016/j.foodchem.2017.06.127)).

## Bond And Mechanism Layer

Representative gas-phase homolytic C-H BDEs are approximately: methane 105, primary alkyl 101, secondary alkyl 99, tertiary alkyl 97, mono-allylic 88, and bis-allylic 75 kcal mol\(^{-1}\) (439, 423, 414, 406, 368, and 314 kJ mol\(^{-1}\)). Values are molecule- and protocol-specific; the alkyl values come from critically evaluated measurements ([Blanksby and Ellison](https://pubmed.ncbi.nlm.nih.gov/12693923/)), while lipid calculations and experiments support roughly 88 versus 75 kcal mol\(^{-1}\) for mono- versus bis-allylic sites ([Pratt et al.](https://doi.org/10.1021/jp0650782)).

\[
LH+X^\bullet\rightarrow L^\bullet+XH,\qquad
\Delta H\approx \mathrm{BDE}(L-H)-\mathrm{BDE}(X-H)
\]

\[
L^\bullet+O_2\rightarrow LOO^\bullet;\quad
LOO^\bullet+LH\rightarrow LOOH+L^\bullet
\]

Hydroperoxide decomposition can then produce aldehydes, ketones, alcohols, acids, and secondary radicals. PUFA oxidizability correlated with the number of bis-allylic positions under controlled oxygenated conditions ([Cosgrove et al.](https://doi.org/10.1007/BF02533996)). **Limitation:** lower BDE supports easier H abstraction; it does not mean heat directly cleaves the bond or determine oxidation rate without initiators, oxygen transport, antioxidants, phase, and temperature.

| Bond/motif availability | Physical drivers | Eligible mechanism class | Directional compound classes |
|---|---|---|---|
| Bis-allylic C-H in PUFA | oxygen, heat/light, radicals, low antioxidant capacity | lipid autoxidation | hydroperoxides rise first; carbonyls/acids may later rise |
| Reducing carbonyl + amino group | temperature, time, pH, intermediate mobility | Maillard/Strecker families | Amadori products, Strecker aldehydes, pyrazines/furans may rise |
| Ester/glycosidic/peptide bond + water | temperature, water, acid/base or enzymes | hydrolysis | free acids, sugars, amino acids may rise |
| Sulfur amino-acid/thiamine motifs | heat, carbonyl partners, pH | sulfur degradation/condensation | thiols, sulfides, thiazoles and related volatiles may rise |
| Terpene unsaturation/allylic sites | oxygen, heat, light, acidity | oxidation/isomerization | oxygenated terpenes and rearranged products may rise |

These are **mechanism-class gates**, not assertions that every listed compound forms.

## Quantum Descriptors

Using vertical energies at one geometry: \(I=E(N-1)-E(N)\), \(A=E(N)-E(N+1)\), \(\mu=-(I+A)/2\), \(\eta=(I-A)/2\), and \(\omega=\mu^2/(2\eta)\) ([Parr–Pearson](https://doi.org/10.1021/ja00364a005); [electrophilicity definition](https://doi.org/10.1021/ja983494x)). “Softness” conventions differ by a factor of two; CGAS must store the exact definition rather than only a field name.

Condensed Fukui functions derive from population differences: \(f_k^+=q_k(N+1)-q_k(N)\), \(f_k^-=q_k(N)-q_k(N-1)\), and \(f_k^0=[q_k(N+1)-q_k(N-1)]/2\). They indicate candidate sites for nucleophilic, electrophilic, and radical interaction, respectively ([Yang and Parr](https://pmc.ncbi.nlm.nih.gov/articles/PMC390758/); [xTB documentation](https://xtb-docs.readthedocs.io/en/latest/sp.html)). Population method, conformer, protonation, and unrestricted-state quality must be retained.

**Decision:** Use HOMO/LUMO gaps only as protocol-consistent screening features. Use \(\Delta\)SCF IP/EA for important cases; do not interpret approximate Kohn–Sham orbital energies as universally accurate experimental IP/EA values.

## Process \(P\rightarrow\theta\)

Replace \(P=[\text{method, medium, nominal temperature, duration, size}]\) with trajectories:

\[
\theta(x,t)=\{T_{\mathrm{surface}},T_{\mathrm{core}},a_w,\mathrm{pH},
pO_2,\phi_{\mathrm{fat}},S/V,L,k_m,h,\text{reactant activities}\}.
\]

For mechanism \(m\), use relative thermal exposure

\[
D_m=\int_0^{t_f}\exp\!\left[\frac{E_{a,m}}R
\left(\frac1{T_{\mathrm{ref}}}-\frac1{T(t)}\right)\right]dt,
\quad k=Ae^{-E_a/RT}.
\]

Consequently \(Q_{10}(T)=\exp[(E_a/R)(1/T-1/(T+10))]\); it is not a universal constant. Reported Maillard activation energies around 90–150 kJ mol\(^{-1}\) are condition-specific ([Ajandouz et al.](https://doi.org/10.1016/j.foodchem.2007.09.062)).

Water activity is \(a_w=p/p_0=\mathrm{ERH}/100\), not moisture content ([FDA](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-technical-guides/water-activity-aw-foods); [ISO 18787](https://www.iso.org/standard/63379.html)). pH changes protonation, nucleophilicity, catalysis, and pathways; neither pH nor \(a_w\) has a universal monotonic effect. Surface and core must remain separate: frying experiments report dry surfaces approaching oil temperature while wet cores remain near 101–103 °C ([Farid](https://doi.org/10.1016/j.cep.2008.03.004)).

**Recommended transition output:** `unsupported`, `physically_possible`, or `evidence_supported`, plus the expected direction of affected compound classes. Numerical yields require calibrated kinetics, initial concentrations, transport parameters, or measurements.

## Q-C4–Q-C7 Evaluation

| Question | Verdict |
|---|---|
| **Q-C4: Which descriptors have documented links to flavour?** | **Answered conditionally.** Vapour pressure, Henry/phase partition, concentration, threshold, and matrix retention have direct physical relevance. Size, polarity, topology, and electronic descriptors can be predictive but are not individually causal; a 476-molecule/49-subject challenge obtained population-level correlations of 0.78 for intensity, 0.71 for pleasantness, and 0.55 for semantic descriptors using multivariate molecular features ([Keller et al.](https://cs.stanford.edu/people/marinka/papers/olfaction-science17.pdf)). |
| **Q-C5: Can BDE/reactivity predict mechanism class?** | **Yes, with boundaries.** It can gate susceptible bonds, H-abstraction direction, and oxidation propensity. It cannot determine rates, product branching, sensory importance, or yield alone. |
| **Q-C6: Is xTB/DFT affordable for 2k–25k molecules on one GPU?** | **Unverified.** [GFN2-xTB](https://pubmed.ncbi.nlm.nih.gov/30741547/) is designed for fast broad-element structure/property calculations, and official [xTB GPU documentation](https://xtb-docs.readthedocs.io/en/latest/development.html) supports NVHPC builds. Published documentation does not establish GPU throughput for CGAS-sized molecules. Benchmark CPU job parallelism versus GPU on a stratified sample; reserve DFT for selected reactions and validation. |
| **Q-C7: Is concentration/OAV coverage sufficient?** | **Not demonstrated.** FlavorDB2 lists 25,595 molecules but only 2,254 linked to 936 natural ingredients ([database paper](https://arxiv.org/abs/2205.05451)). [FooDB’s schema](https://foodb.ca/schema) stores quantified/detected/expected/predicted status and concentration fields, but published completeness for CGAS ingredient-process-threshold joins is absent. This is absence of coverage evidence, not evidence that usable records do not exist. OAV \(=C/T\) is a screening measure; recombination/omission remains necessary because mixture interactions can invalidate simple rankings ([roasted-chicken study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10900400/)). |

## Minimum Viable Descriptor Schema

`identity/provenance`: canonical SMILES, InChIKey, stereochemistry, charge, tautomer, source, measured/predicted flag.  
`2D_core`: formula, mass, elements, HBD/HBA, TPSA, logP/logD, rotatable bonds, rings, aromaticity, unsaturation, functional groups.  
`reactive_motifs`: reducing carbonyls, amines, sulfur motifs, ester/glycosidic bonds, allylic and bis-allylic H counts, antioxidant motifs.  
`volatility`: vapour-pressure value/model and temperature, \(\Delta H_{vap}\), boiling point and pressure, Henry convention/units/T, oil-water or measured food-phase partition.  
`3D_optional`: conformer method/energy/rank; ensemble mean and spread for WHIM, GETAWAY, RDF, area, volume, and inertia.  
`QM_optional`: method/version, geometry, solvent, charge/multiplicity, HOMO/LUMO, \(\Delta\)SCF IP/EA, \(\mu,\eta,\omega\), Fukui values, charges, Wiberg orders, dipole, polarizability.  
`process_theta`: surface/core temperature traces, \(a_w\), pH, oxygen exposure, fat amount/composition, geometry, time, pressure, airflow/agitation.  
`quality`: uncertainty, applicability domain, missingness reason, units, temperature, source record, and calculation failure.

## Compute Tiers And Decisions

- **Tier 0, all molecules:** validated identifiers, provenance, measured-property lookup, compact 0D/1D/2D descriptors, reactive motifs.
- **Tier 1, relevant molecules:** conformer ensembles and selected 3D descriptors; retain mean, spread, and conformer protocol.
- **Tier 2, screening subset:** GFN2-xTB optimization/properties and selected charged-state calculations. Run the hardware benchmark before scaling.
- **Tier 3, targeted chemistry:** DFT geometry, frequencies, \(\Delta\)SCF, BDEs, and selected barriers for representative reaction families, not the entire database.
- **Tier 4, validation:** headspace GC-MS/GC-O, concentrations, matrix-specific thresholds, kinetic measurements, recombination and omission tests.

**Recommended decisions:** adopt \(P\rightarrow\theta\); implement mechanism gates; treat BDE and QM features as conditional evidence; make temperature, phase, units, method, and uncertainty mandatory; retain presence weighting outside validated concentration/OAV subsets.

**Experiments required:** benchmark 100–300 stratified molecules on the actual CPU/GPU environment; audit concentration-threshold joins by ingredient and process; validate lipid-oxidation and Maillard gates against measured time courses; compare single-conformer against ensemble 3D features; calibrate headspace release in representative water-, oil-, starch-, and protein-rich matrices.

**Answered:** Descriptor roles, volatility hierarchy, bond-level oxidation rationale, conceptual-DFT definitions, and the required physical process state.  
**Unanswered:** Actual GPU throughput, CGAS-wide concentration/OAV completeness, transferable kinetic parameters, matrix-specific partition coverage, and whether 3D/QM descriptors improve held-out predictions enough to justify their cost.
