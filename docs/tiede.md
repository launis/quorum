# Epistemic Anchoring in Stochastic Large Language Models: A Neurosymbolic Architecture for Verifiable Argumentation and Reproducible Evaluation

**Quorum Research Collective**

*arXiv preprint: cs.AI / cs.CL / cs.DS*

---

### Abstract

Autoregressive Large Language Models (LLMs) operate as stochastic token probability generators whose unconstrained inference paths are fundamentally susceptible to hallucinations, semantic drift, error compounding, and epistemic instability. This paper presents the **Quorum** architecture: a formal neurosymbolic computational framework that transforms unconstrained stochastic generative processes into a deterministically supervised, epistemically anchored state machine. The theoretical foundation comprises:

> 1. Propositional epistemic atomization via the six-tuple Linked Atom Graph (LAG) propositional frame,
> 2. Wave-based topological execution over a Cognitive Directed Acyclic Graph (Cognitive DAG),
> 3. Topological Directed Atom (TDA) poset wave scheduling governed by an orthogonal two-tier epistemic firewall (deterministic physical citation provenance and role-asymmetric Popperian falsification),
> 4. Interactive diagnostic argument surgery, Assumption-Based Truth Maintenance Systems (ATMS), and Toulmin warrant reachability under counterfactual premise retractions,
> 5. Pure stateless baseline argument causal cohesion evaluation via the 0-token Cumulative Guttman Invariant (Guttman, 1944) over unperturbed graph topologies, and
> 6. An orthogonal multi-factor BARS evaluation matrix combining asymmetric Popperian falsification, event-sourced state projection, and continuous piecewise power-curve damping.

We formalize this framework through two core architectural principles (confluent wave scheduling under Kahn partial ordering and epistemic warrant reachability under discrete ATMS graph surgery) and two mathematically verified system properties (decoupled epistemic error suppression separating physical citation provenance from semantic entailment, and monotonic Lipschitz score stability). The framework is empirically validated through two controlled pairwise audit trials across organizational policy and strategic foresight domains ($T = 2$ paired trials, 4 full workflow executions, $N = 110$ common proposition atoms per trial), demonstrating high inter-run stability (observed raw agreement $95.45\%$ and $98.18\%$; Cohen's $\kappa = 0.9064$ and $\kappa = 0.9633$; pooled mean $\bar{\kappa} = 0.9348$; mean Shannon entropy $\bar{H} \le 0.0455$) under unconstrained native stochastic frontier sampling (provider default entropy without greedy clamping), with zero system crashes or Dead Letter Queue (DLQ) drops. Furthermore, across a controlled 5-configuration component ablation benchmark ($N = 220$ proposition atom frames), Quorum elevates evaluative test–retest reliability from $\kappa = 0.2146$ (unconstrained prompt-based LLM judge) to $\kappa = 0.9453$ ($P_o = 97.27\%$ in the ablation benchmark harness; and $\bar{\kappa} = 0.9348$, $P_o = 96.82\%$ in physical production trials), eliminates unanchored chimera citations from $20.7\%$ to $0.0\%$ under an offline benchmark stress test with 19.7% candidate attack pressure ($\text{Specificity}_{\text{lex}} = 1.000$), and eradicates the $8.6\%$ criterion omission rate observed in monolithic step evaluation. In pilot human expert calibration, Neyman–Pearson error governance bounds the False Omission Rate to $\widehat{\text{FOR}} = 13.33\%$ (decoupling $3.33\%$ inflectional firewall rejections from $10.00\%$ diffuse omissions), while Kahn wave precondition short-circuiting and a $40\%$ penalty ceiling ($P_{\max} = 0.40$) enforce structural Lipschitz score stability. We report these initial findings transparently from two paired experimental runs, noting that broader multi-corpus evaluations are required for population-level statistical generalization. Finally, we synthesize Quorum's positioning across the landscape of reasoning architectures, retrieval frameworks, and cognitive governance paradigms.

---

## 1. Introduction and Problem Formulation

An autoregressive language model is formally defined as a conditional probability distribution over a discrete vocabulary $\mathcal{V}$:

$$P(Y \mid X; \theta) = \prod_{t=1}^{T} P(y_t \mid y_{<t}, X; \theta), \quad y_t \in \mathcal{V} \tag{1}$$

where $X = (x_1, \dots, x_N)$ is an input prompt sequence and $\theta \in \mathbb{R}^D$ represents the static model weights. Although modern frontier models produce syntactically fluent discourse, their epistemic utility in high-stakes reasoning is bounded by three structural failures:

> 1. **Aleatoric Uncertainty and Calibration Divergence:** The distribution $P(Y \mid X; \theta)$ models statistical token co-occurrence frequencies across training corpora rather than objective truth values ($\mathcal{T} \neq \mathcal{P}$). The model generates statistically plausible assertions that lack empirical backing.
> 2. **Conflation of Association with Causation:** Autoregressive attention captures symmetric correlation $P(A \mid B)$ but cannot distinguish a genuine causal mechanism $B \to A$ from confounding background factors ($C \to A \land C \to B$) or reverse causation ($A \to B$).
> 3. **Superlinear Error Cascade:** In unconstrained multi-step inference, a minute semantic drift at step $t$ conditions the distribution at step $t+1$, causing errors to compound exponentially across generative trajectories—formalizing exposure bias and compositional error cascades in autoregressive models (Ross & Bagnell, 2010; Dziri et al., 2023):
> 
> 
> $$\mathbb{E}\left[\|\hat{y}_{t+k} - y^*_{t+k}\|\right] \sim \mathcal{O}\left(e^{\lambda_{\text{casc}} k}\right), \quad \lambda_{\text{casc}} > 0 \tag{2}$$
> 
> 

The Quorum architecture addresses these vulnerabilities by stripping the LLM of autonomous state transitions. The generative model is restricted to a stateless, constrained propositional sensor, while the control logic, state progression, and evidentiary evaluation are enforced by an external, mathematically validated neurosymbolic engine.

### Research Questions and Empirical Scope

To systematically investigate the operational efficacy and architectural contributions of this neurosymbolic design, this paper addresses three fundamental research questions:

* **RQ1 (Evidentiary Anchoring & Replication Reliability):** To what extent does an orthogonal multi-gate lexical firewall combined with parallel Best-of-3 ensembling suppress chimera citations and improve test–retest reproducibility ($\kappa$) relative to unconstrained LLM-as-a-judge baselines? *(Evaluated in Sections 4.1, 6, 8.2, 8.4, and 8.5; Tables 2, 6, and 7)*
* **RQ2 (Decomposition & Attention Integrity):** How does propositional atomization (Linked Atom Graph 6-tuple) and deterministic single-token UUID aliasing mitigate attention degradation (lost-in-the-middle criterion drops) and Byte-Pair Encoding tokenization boundary perturbations across extended context windows? *(Evaluated in Sections 2.1, 3.1, 8.1, and 8.5; Tables 3 and 7)*
* **RQ3 (Structural Causality & Human Agency Discrimination):** Can a 0-token Cumulative Guttman Invariant on mined argument graphs combined with an orthogonal Human Agency & Collaboration Matrix ($\mathcal{M}_{\text{HACM}}$) reliably differentiate substantive reasoning from passive human delegation and surface rhetorical fluency? *(Evaluated in Sections 4.2, 5.4, 8.3, and 8.4; Tables 1, 3, 4, and 6)*

---

## 2. Epistemic Atomization and the Linked Atom Graph (LAG)

### 2.1. Ontological Disambiguation and the Atomization Morphism

*Ontological Partition (Discourse Claims vs. Rubric Criteria):* To establish formal mathematical precision, Quorum explicitly distinguishes between two structurally distinct propositional collections that operate across different pipeline phases:

1. **Dynamic Discourse Graph Claims ($\mathcal{V}_{\text{claim}}$):** In Phase 1 Cognitive DAG execution, an unstructured natural language input or discourse history $\mathcal{D} \in \Sigma^*$ is dynamically decomposed via the mining morphism $\alpha_{\text{mine}}: \Sigma^* \to \mathcal{V}_{\text{claim}}$ into a variable set of minimal, mutually independent empirical assertions:
   $$\mathcal{V}_{\text{claim}} = \{ v_1, v_2, \dots, v_n \} \tag{3}$$
   These mined assertions form the node set of the directed proposition graph $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$, exhibiting discourse-dependent graph cardinality across runs ($|\mathcal{V}_{\text{claim}}| \in [141, 252]$ across the three-document trial payload, well within the combined ceiling $N_{\max}^{\text{payload}} = 300$; Section 8.1, Section 8.3).
2. **Fixed Evaluative Rubric Criteria ($\mathcal{A}_{\text{rubric}}$):** In Phase 1 matrix evaluation, the discourse is evaluated against a pre-compiled, design-time curated benchmark schema consisting of fixed Behaviorally Anchored Rating Scale (BARS) criteria:
   $$\mathcal{A}_{\text{rubric}} = \bigcup_{m=1}^D \mathcal{A}_m, \quad |\mathcal{A}_{\text{rubric}}| = N = 110 \tag{4}$$
   totaling exactly $N = 110$ immutable criteria across the five evaluated matrices ($25 + 5 + 25 + 25 + 30 = 110$; Table 3).

**Definition 1 (Evaluated Propositional Frame).** Every evaluated rubric proposition $a_i \in \mathcal{A}_{\text{rubric}}$ is formally tested against discourse $\mathcal{D}$ as an immutable six-tuple:

$$a_i = \langle \tau_i, \mathcal{C}_i, \sigma_i, \pi_i, \lambda_i, \tau_{\text{val}, i} \rangle \tag{5}$$

* $\tau_i \in \mathcal{L}_{\text{prop}}$ is the declarative target hypothesis formulated in formal logic with unambiguous truth-evaluable acceptance criteria.
* $\mathcal{C}_i \subset \Sigma^*$ is the spatial and contextual bounding box isolating the exact text span in $\mathcal{D}$ extracted to substantiate $\tau_i$.
* $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ is the speaker attribution index, separating human supervisory intent from model-generated synthetic drafts.
* $\pi_i \in \{+1, -1\}$ is the evidentiary polarity index: $\pi_i = +1$ denotes a positive capability claim (demonstrating analytical competence), whereas $\pi_i = -1$ designates an asymmetric anti-pattern detector (identifying cognitive failure modes, fallacies, or uncritical adoption).
* $\lambda_i \in \{0, 1\}$ is the physical citation and speaker provenance index, governed by an uncompromising null hypothesis parameterized by lexical strictness $\zeta_{\text{lex}} \in [0, 100]$ (operationally bound to unified workflow strictness $\zeta_{\text{lex}} = \zeta$):

$$\lambda_i = \begin{cases} 1, & \text{Lex}(\mathcal{C}_i, \mathcal{D}; \zeta_{\text{lex}}) \;\land\; \text{Prov}(\mathcal{C}_i, \sigma_i) \\ 0, & \text{otherwise} \end{cases} \tag{6}$$

* $\tau_{\text{val}, i} \in \{0, 1\}$ is the discrete semantic rubric validation decision emitted by the model's structured reasoning trace $\mathcal{T}_i$ and confirmed via parallel Best-of-3 ensemble consensus:

$$\tau_{\text{val}, i} = \begin{cases} 1, & \text{Decision}(\mathcal{T}_i) = \text{PASS} \;\land\; \text{Triangulate}(\mathcal{T}_i, \mathcal{C}_i) \\ 0, & \text{otherwise} \end{cases} \tag{6b}$$

where $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \zeta_{\text{lex}})$ evaluates the deterministic lexical verification cascade (collapsing to exact normalized substring containment $\text{find}(\text{Norm}_{\text{NFKC}}(\mathcal{C}_i), \text{Norm}_{\text{NFKC}}(\mathcal{D})) \neq -1$ at $\zeta_{\text{lex}} \ge 100$, and incorporating bounded morphological stem-sequence verification for agglutinative inflections at $\zeta_{\text{lex}} < 100$), $\text{Norm}_{\text{NFKC}}(\cdot)$ denotes post-hoc Unicode NFKC/NFD compatibility decomposition and formatting strip, $\text{Prov}(\cdot)$ enforces structured XML speaker isolation, $\mathcal{T}_i$ denotes the model's structured reasoning trace (Chain-of-Thought output containing explicit syntactic anchors and validation decisions, formalized in Section 4.1.1 Gate 4), and $\text{Triangulate}(\mathcal{T}_i, \mathcal{C}_i)$ validates internal CoT consistency against syntactic anchors and enforces the Contradiction Ban.

*The Syntactic Provenance vs. Semantic Entailment Boundary:* An exact substring match $\text{find}(\mathcal{C}_i, \mathcal{D}) \neq -1$ provides *physical provenance*—irrefutable proof that citation $\mathcal{C}_i$ physically exists within document $\mathcal{D}$ and was neither fabricated nor spliced across disparate paragraphs. However, deterministic string matching is semantically blind: it verifies the syntactic existence of character sequences, not that proposition $\tau_i$ semantically follows from $\mathcal{C}_i$ ($\mathcal{C}_i \models \tau_i$). Because natural language discourse is inherently open-ended and pragmatic, universal automated verification of semantic entailment over unrestricted natural language exhibits an intrinsic semantic entailment gap (formally bounded by Rice's theorem on the undecidability of non-trivial semantic properties in computational systems; Rice, 1953; Turing, 1936). Pre-compiling propositions $\tau_i$ as typed Behaviorally Anchored Rating Scale (BARS) rubrics within a centralized declarative schema defines the target hypotheses rigorously, but does not eliminate the semantic gap between a real quotation and its purported interpretation. Consequently, Quorum structures epistemic defense across two orthogonal layers:
1. **Deterministic Physical Grounding (Type I Defense):** Eliminates fabricated and chimera citations with mathematical certainty ($\lambda_i = 0$ if $\mathcal{C}_i \notin \mathcal{D}$), bounding citation fabrication error to the physical substring collision floor $\epsilon_{\text{lexical}} \to 0$.
2. **Adversarial Neurosymbolic Entailment (Type II Defense):** Constrains semantic misattribution ($\mathcal{C}_i \in \mathcal{D}$ but $\mathcal{C}_i \not\models \tau_i$) through role-asymmetric Popperian falsification ($\pi_i = -1$), syntactic anchor triangulation, and downstream Argumentative SCM (A-SCM) reachability pruning, ensuring that residual semantic drift is bounded by parallel Best-of-3 ensemble consensus rather than conflated with lexical string matching.

*Symbolic Interface Grounding and Subword Entropy Suppression:* In physical persistence, propositions $a_i \in \mathcal{A}_{\text{rubric}}$ and discourse nodes $v_j \in \mathcal{V}_{\text{claim}}$ are addressed via high-entropy 128-bit identifiers ($\mathcal{I}_{\text{UUID}}$, specifically UUIDv4 hexadecimal strings). Directly exposing multi-token hexadecimal strings to autoregressive prompt contexts induces subword tokenization fragmentation (5–10 Byte-Pair Encoding subwords per identifier), triggering attention diffusion, positional degradation over extended contexts, and character transposition hallucinations during decoding. To isolate the generative sensor from persistent storage mechanics, the neurosymbolic boundary executes an ephemeral bijective alias morphism:

$$\mu: \mathcal{I}_{\text{UUID}} \longleftrightarrow \mathcal{V}_{\text{alias}}, \quad \mathcal{V}_{\text{alias}} = \{a_0, a_1, \dots, a_{n-1}\}$$

This morphism compresses each propositional target into an atomic single-token Attention Anchor ($a_k$). Concurrently, the generation grammar enforces constrained decoding via dynamic finite categorical vocabularies, restricting output logits strictly to the closed support $\mathcal{V}_{\text{alias}}$. Upon receipt, the runtime executes deterministic $\mathcal{O}(1)$ reverse hydration $\mu^{-1}(a_k)$, triggering an immediate validation failure if an unmapped alias is generated. This preserves single-token attention fidelity while guaranteeing mathematical referential integrity across the proposition graph.

### 2.2. Linked Atom Graph Structure and Root Node Typology

The mined discourse claims $\mathcal{V}_{\text{claim}}$ are structured into a directed, attributed multi-graph $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{dep}}, \mathcal{E}_{\text{temp}}, \mathcal{E}_{\text{causal}})$, where edge sets define logical dependency, temporal order, and inferred causal transmission.

To avoid misclassifying legitimate foundational axioms, $\mathcal{G}_{\text{LAG}}$ partitions root nodes ($\text{InDegree}(v) = 0$) and isolated claims into distinct epistemic categories:

1. **Active Exogenous Boundary Axioms ($\mathcal{V}_{\text{axiom}}$):** Primitive operational constraints or historical baseline premises ($U_i$) that require no internal textual ancestors ($\text{InDegree}(v) = 0$), but serve as active antecedents for downstream inferences ($v \to u$), satisfying $\text{OutDegree}(v) \ge 1$. Consequently, its total graph degree is $\text{deg}(v) = \text{InDegree}(v) + \text{OutDegree}(v) \ge 1$, which naturally excludes it from the isolated concept ratio $r_{\text{iso}}$ without requiring heuristic whitelisting.
2. **Topologically Isolated Propositions ($\mathcal{V}_{\text{isolated}}$):** Nodes lacking both internal ancestors and inferential descendants ($\text{InDegree}(v) = 0 \land \text{OutDegree}(v) = 0$, $\text{deg}(v) = 0$). In natural discourse, these subsume two semantically distinct categories:
   - *Standalone Scoping Context ($\mathcal{V}_{\text{scoping}}$)*: Legitimate institutional background, introductory framing, or statutory scope recitals stated by the author that are not formally mobilized as causal premises for subsequent claims.
   - *Unjustified Orphan Claims ($\mathcal{V}_{\text{orphan}}$)*: Standalone normative or empirical assertions asserted without supporting evidence, warrants, or inferential descendants.

*Stateless Invariant Law:* Because the Pure Stateless Causal Cohesion Evaluator (Section 4.2.1) computes topological invariants in 0 tokens without semantic introspection of proposition text, it cannot distinguish between benign scoping context and unjustified orphan assertions. Consequently, all degree-zero nodes are counted in $r_{\text{iso}}$, necessitating a calibrated tolerance ceiling ($r^{\max}_{L3}$) at higher BARS tiers to accommodate legitimate scoping discourse.

---

## 3. Cognitive Directed Acyclic Graph (Cognitive DAG) Architecture

High-level cognitive transformations—ingress filtering, atomic decomposition, causal graph mining, matrix evaluation, falsification, and executive synthesis—are executed across an immutable, acyclic orchestration network:

$$\mathcal{G}_{\text{DAG}} = (\mathcal{V}_{\text{cog}}, \mathcal{E}_{\text{dep}}) \tag{7}$$

where $\mathcal{V}_{\text{cog}}$ represents typed computational operators and $\mathcal{E}_{\text{dep}}$ represents strict state and data dependencies.

```
           +-----------------------------+
           |   Primary Input Documents   |
           +--------------+--------------+
                          |
                          v
           +-----------------------------+
           |    Ingress Sanitization     |
           |   & Two-Pass Atomizer (LAG) |
           +--------------+--------------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
     +-----------------+     +-----------------+
     | Argument ATMS   |     | Poset Atom DAG  |
     | Engine (Surgery)|     | (TDA Scheduling)|
     | (Warrant Audit) |     | (Anchor λ ∈ {0,1}|
     +--------+--------+     +--------+--------+
              |                       |
              +-----------+-----------+
                          |
                          v
           +-----------------------------+
           | Two-Factor Orthogonal       |
           | Matrix Scoring Engine       |
           +--------------+--------------+
                          |
                          v
           +-----------------------------+
           | Asymmetric Popperian        |
           | Falsification & Bias Guard  |
           +--------------+--------------+
                          |
                          v
           +-----------------------------+
           | Epistemically Anchored      |
           | Synthesis (Dumb Painter)    |
           +-----------------------------+

```

### 3.1. Wave-Based Topological Execution

Because $\mathcal{G}_{\text{DAG}}$ is acyclic, Kahn’s topological sort partitions $\mathcal{V}_{\text{cog}}$ into discrete, parallel computational waves $\mathcal{W}_0, \mathcal{W}_1, \dots, \mathcal{W}_{J-1}$:

$$\mathcal{W}_0 = \{ v \in \mathcal{V}_{\text{cog}} \mid \text{InDegree}(v) = 0 \} \tag{8}$$

$$\mathcal{W}_{j+1} = \left\{ v \in \mathcal{V}_{\text{cog}} \setminus \bigcup_{l=0}^j \mathcal{W}_l \;\middle|\; \text{Parents}(v) \subseteq \bigcup_{l=0}^j \mathcal{W}_l \right\} \tag{9}$$

Operators within wave $\mathcal{W}_j$ are executed concurrently as isolated asynchronous coroutines. Each operator $v \in \mathcal{W}_j$ evaluates an invariant deterministic function over immutable typed records:

$$\Phi_v: \prod_{u \in \text{Parents}(v)} \mathcal{O}_u \times \mathcal{S}_{\text{global}} \to \mathcal{O}_v \tag{10}$$

---

## 4. Topological Directed Atom (TDA) Scheduling and Structural Argument Truth Maintenance

### 4.1. Topological Directed Atom (TDA) Poset Scheduling and Verification

*Nomenclature Demarcation and Scope Calibration:* To prevent terminological confusion with *Topological Data Analysis* (TDA in applied mathematics and machine learning, which studies persistent homology, simplicial complexes, and Betti numbers $\beta_k$ over metric point clouds; Carlsson, 2009; Edelsbrunner & Harer, 2010), we explicitly clarify that in Quorum, the acronym **TDA** designates **Topological Directed Atoms** (and their associated dependency argumentation). The term *topological* is employed strictly in its foundational computer science and order-theoretic sense: Kahn's topological sorting (Kahn, 1962) on finite directed acyclic graphs inducing an Alexandroff topology and a specialization poset ($\mathcal{G}_{\text{LAG}}$). Quorum asserts no claims of computing algebraic homology groups or metric simplicial filtrations. Rather, TDA in Quorum denotes the **order-theoretic scheduling, exact lexical provenance, and cycle-free verification** of propositional claims:

1. **Strict Lexical Grounding:** Proposition truth values are grounded directly in verbatim source evidence. Unanchored assertions fail closed ($\lambda_i = 0$).
2. **Cycle Elimination and Poset Acyclicity:** Circular reasoning chains ($a_1 \implies a_2 \implies \dots \implies a_1$) violate epistemic partial order invariants. Rather than invoking homological machinery, circularities and phantom dependencies are detected prior to wave evaluation via Tarjan's strongly connected components and Johnson's elementary cycle enumeration algorithm (Tarjan, 1972; Johnson, 1975). Nodes participating in directed cycles are immediately quarantined, and any downstream nodes left unresolved after Kahn wave exhaustion are deterministically clamped to `BLOCKED`, enforcing strict directed acyclicity across the proposition graph.

### 4.1.1. Deterministic Physical Provenance Verification and Defense Against Fabricated Evidence

A foundational failure mode in contemporary LLM evaluation (including LLM-as-a-Judge [Zheng et al., 2023], G-Eval [Liu et al., 2023], and Self-RAG [Asai et al., 2024]) is **Second-Order Hallucination** (*Quis custodiet ipsos custodes?*). If a secondary LLM is queried to determine whether a document entails a proposition ($P(\text{Entail} \mid \mathcal{D}, \tau_i)$), the verifier is itself an autoregressive stochastic sampler susceptible to sycophancy, confirmation bias, and the synthesis of *chimera quotes* (stitching isolated words across disparate paragraphs into a fabricated sentence).

To defend against unanchored evidence and citation fabrications, Quorum strips the generative model of judicial authority. Rather than allowing the LLM to self-certify its outputs, evidence verification is structured across two orthogonal layers: physical citation provenance and exact lexical containment are verified **exclusively through a compiled deterministic lexical verification engine**, while semantic entailment is audited through role-asymmetric Popperian falsification and downstream A-SCM reachability:

1. **Gate 1: Post-Hoc Lexical Verification with Dual Normalization Invariant:**
   While raw input text is preserved under conservative Canonical Composition (NFC) during initial ingress to maintain typographical provenance, the post-hoc verifier applies Unicode Compatibility Decomposition (NFKC) and canonical decomposition (NFD) symmetrically to both the source corpus $\mathcal{D}$ and the candidate extraction $\mathcal{C}_i$. An invariant bidirectional index map $\mathcal{M}_{\text{idx}}: \mathbb{N} \to \mathbb{N}$ maps normalized character indices back to original source byte positions. The candidate quote $\mathcal{C}_i$ is validated via exact $O(N)$ containment:
   
   $$\text{find}(\text{Norm}_{\text{NFKC}}(\mathcal{C}_i), \text{Norm}_{\text{NFKC}}(\mathcal{D})) \neq -1$$
   
   If matched, the exact verbatim string is sliced from the original immutable text, preventing case-folding or formatting drifts from fabricating false evidence. This two-tier normalization design ensures that typographical variations (specifically non-breaking spaces U+00A0 and en-spaces U+2002) do not induce false negative citation rejections during post-hoc auditing.

2. **Gate 2: Entropy Gate & Contiguity Guard (Chimera Quote Defense):**
   * *Entropy Gate (< 10 chars):* Short quotes under 10 characters (specifically isolated buzzwords) are strictly forbidden from approximate matching; 100% exact substring containment is unconditionally required.
   * *Contiguity Guard (< 30 chars):* Short phrases enforce strict contiguous character sequence matching via partial string edit ratio, strictly prohibiting token reordering or word skipping.
   * *Token-Set Evaluation ($\ge 30$ chars):* Longer spans evaluate token-set overlap to tolerate minor word-order permutations or morphological case conjugations. However, to prevent bag-of-words chimera stitching across disparate paragraphs, token-set overlap does *not* confer standalone acceptance: it is strictly constrained by Gate 5's downstream morphological stem-sequence alignment and unbroken longest-common-substring coverage verification.
   * *Safety Ceiling (> 1000 chars):* Quotes exceeding 1000 characters trigger an immediate verification rejection to prevent prompt injection and quote stuffing.

3. **Gate 3: Cross-Speaker Provenance Boundary Guard:**
   Discourse is segmented into structured provenance capsules: `<user_payload>` for human supervisor inputs, `<ai_draft_context>` for model drafts, and `<assignment_context>` for task instructions. When evaluating human capability ($\sigma_i = \text{USER}$), candidate quotes must reside strictly inside `<user_payload>`:
   
   $$\text{Prov}(\mathcal{C}_i, \sigma_i) = \mathbb{I}\left( \text{Lex}(\mathcal{C}_i, \mathcal{D}_{\text{speaker}}; \zeta) = 1 \right)$$
   
   If an LLM quotes the AI assistant's draft to substantiate a human competence claim, the verifier rejects the claim on provenance boundary violation, mathematically preventing cross-speaker competence contamination.

4. **Gate 4: Reasoning Trace Triangulation:**
   The model's structured schema requires an explicit reasoning trace $\mathcal{T}_i$ specifying an exact syntactic anchor (`[2. SYNTACTIC ANCHOR: "..."]`) and decision (`[5. VALIDATION DECISION: PASS/FAIL]`). Deterministic triangulation asserts three consistency invariants:
   * *Contradiction Ban:* If $\mathcal{T}_i$ concludes `FAIL`, but quote $\mathcal{C}_i$ is populated, the atom is rejected for logical contradiction.
   * *Empty Anchor Ban:* If $\mathcal{T}_i$ declares `[2. SYNTACTIC ANCHOR: NONE]`, unanchored extraction fails closed.
   * *Hallucinated Anchor Ban:* The anchor string parsed from the trace must physically exist in the source document; fabricated anchors trigger immediate rejection. Formally, this gate evaluates the *syntactic anchor* (`[2. SYNTACTIC ANCHOR: "..."]`)—a localized 2–5 word invariant lexical pivot extracted in the model's Chain-of-Thought—using strict Tier 1 normalized substring containment ($\text{find}(\text{Norm}_{\text{NFKC}}(\text{anchor}), \text{Norm}_{\text{NFKC}}(\mathcal{D})) \neq -1$). This guarantees that the physical sentence locus exists in $\mathcal{D}$. Concurrently, Gate 5 evaluates the full candidate quotation $\mathcal{C}_i$ spanning that locus using the parameterized predicate $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \zeta_{\text{lex}})$, permitting bounded morphological stem-sequence verification and edit-distance relaxation when $\zeta_{\text{lex}} < 100$.

5. **Gate 5: Piecewise-Stratified Lexical Strictness Schedule and Morphological Stemming Cascade:**
   Under Quorum's lexical strictness parameter $\zeta_{\text{lex}} \in [0, 100]$ (operationally bound to unified workflow strictness $\zeta_{\text{lex}} = \zeta$), the lexical predicate $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \zeta_{\text{lex}})$ executes a calibrated four-tier deterministic cascade when $\zeta_{\text{lex}} < 100$: (i) exact NFKC/NFD substring containment, (ii) length-stratified edit similarity against a nominal baseline threshold $\tau_{\text{base}} = 75.0\%$ scaled by piecewise tier multipliers $m(\zeta_{\text{lex}})$ ($\tau_{\text{tier}}(\zeta_{\text{lex}}) = \tau_{\text{base}} \times m(\zeta_{\text{lex}})$: $\times 0.80 \implies 60.0\%$ for $\zeta_{\text{lex}} < 30$, $\times 0.90 \implies 67.5\%$ for $\zeta_{\text{lex}} \in [30, 50)$, $\times 1.00 \implies 75.0\%$ for $\zeta_{\text{lex}} \in [50, 85)$, and $\times 1.02 \implies 76.5\%$ for $\zeta_{\text{lex}} \in [85, 100)$), (iii) multilingual morphological stem-sequence verification engine to accommodate grammatical case inflections in highly agglutinative languages (including Finnish), and (iv) contiguous longest-common-substring coverage verification (requiring $\ge 70\%$ unbroken contiguous substring containment). Whereas the downstream scoring exponent $\gamma(\zeta_{\text{score}})$ in Equation (18) is continuous and piecewise linear, the upstream lexical threshold $\tau_{\text{tier}}(\zeta_{\text{lex}})$ operates as a piecewise-stratified step function with a $23.5\text{ pp}$ step discontinuity from $76.5\%$ at $\zeta_{\text{lex}} = 99.9$ to $100.0\%$ at $\zeta_{\text{lex}} \ge 100$. This discrete step jump is an intentional architectural phase transition rather than an interpolation omission: while downstream score aggregation smoothly penalizes capability point clustering via power curves over continuous ratios $\rho \in [0, 1]$, upstream lexical verification acts as a local categorical gatekeeper ($\lambda \in \{0, 1\}$). Continuous linear interpolation across string edit thresholds (e.g., demanding $\ge 95\%$ edit similarity at $\zeta = 98$) is ill-posed because Levenshtein distance is not scale-invariant—arbitrarily penalizing short, valid inflected phrases while tolerating substantial semantic alterations in long quotations. Crucially, in highly agglutinative languages (specifically Finnish, where words undergo complex multi-morpheme case inflections), Tier 3 morphological Snowball stemming handles grammatical variations reliably across $\zeta < 100$. Setting $\zeta = 100$ (Absolute Zero-Trust Forensic Mode) represents a qualitative epistemic shift where all automated linguistic inference, stemming, and approximate fallbacks are completely deactivated, enforcing uncompromising character-for-character physical substring containment.

*Interaction of Gate 2 and Gate 5 Across Strictness Regimes:* The interaction between Gate 2 and Gate 5 is strictly hierarchical and conditioned on $\zeta_{\text{lex}}$:
* **At $\zeta_{\text{lex}} \ge 100$ (Absolute Zero-Trust):** Gate 5 imposes an uncompromising exact-match filter (threshold $\tau_{\text{tier}} = 100.0$). If exact normalized containment (Gate 1) fails, Gate 5 immediately aborts with falsification ($\lambda_i = 0$), completely bypassing all approximate branches in Gate 2 and Gate 5 (stemming and longest-common-substring). In this regime, zero token reordering, character substitution, or word stitching is tolerated.
* **At $\zeta_{\text{lex}} < 100$ (Calibrated Multi-Tier Cascades):** When an extraction is not an exact substring, Gate 2 and Gate 5 cooperate as a multi-tier defense against chimera quotes. For short phrases ($< 30$ chars), Gate 2 enforces strict contiguous substring alignment. For longer phrases ($\ge 30$ chars), while Gate 2 permits token-set overlap to accommodate surface inflection and token reordering, Gate 5 requires that the citation also satisfy contiguous morphological stem-sequence alignment or achieve $\ge 70\%$ unbroken longest-common-substring coverage. This ensures that bag-of-words overlap cannot stitch disjoint sentences into a false continuous quote.
* **Operational Strictness in Empirical Trials:** Production audit runs were executed at baseline strictness $\zeta = 0$ ($\gamma(0) = 1.00$), whereas ablation stress tests evaluated the impact of the lexical firewall up to $\zeta = 100$ (see Sections 8.3 and 8.5).

Under this five-gate architecture, propositional grounding does not rely on unconstrained LLM self-evaluation. An atom $\tau_i$ achieves physical citation anchoring ($\lambda_i = 1$) if and only if all five deterministic verification gates succeed, bounding the probability of accepting a fabricated or spliced citation by the physical string collision rate $\epsilon_{\text{lexical}} \to 0$.

### 4.2. Argumentative Structural Dependency Models (A-SCM) and Truth Maintenance

*Ontological Scope and the Enthymeme Boundary:* Unlike physical systems where variables $\mathbf{V}$ represent empirical data-generating mechanisms, natural discourse is inherently pragmatic, elliptical, and enthymematic (Toulmin, 1958; Grice, 1975). Human authors routinely omit common-sense warrants and intermediate mechanisms, while language models trained on autoregressive prediction behave as "causal parrots" conflating associative correlation with causation (Zečević et al., 2023). Therefore, Quorum does not claim that textual analysis discovers objective physical causality. Instead, Quorum formalizes the **Argumentative Structural Causal Model (A-SCM)**, evaluating the *internal explanatory sufficiency and structural evidentiary rigor* of the authored thesis.

**Definition 2 (Argumentative Structural Causal Model).** An authored discourse is modeled as a five-tuple:

$$\mathcal{M}_{\text{arg}} = \langle \mathbf{U}, \mathbf{V}, \mathbf{W}, \mathbf{F}, P(\mathbf{U}) \rangle \tag{11}$$

where $\mathbf{V} = \{V_1, \dots, V_n\}$ represents explicit propositional claims grounded in verbatim text ($\lambda = 1$), $\mathbf{W}$ represents explicit Toulmin warrants (backing and explanatory transmission mechanisms), $\mathbf{U} = \{U_{\text{enthymeme}}, U_{\text{context}}\}$ represents unstated background assumptions and latent conversational confounders, and $\mathbf{F} = \{f_1, \dots, f_m\}$ defines structural argument dependencies:

$$V_i = f_i(\mathbf{PA}_i, \mathbf{W}_i, U_i), \quad \mathbf{PA}_i \subseteq \mathbf{V} \setminus \{ V_i \} \tag{12}$$

**Definition 3 (Context-Bounded Sliding-Window Proposition Linking, $\Phi_{\text{link}}$).** Constructing the Argument DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$ directly from unconstrained discourse via exhaustive pairwise comparison requires an intractable $\mathcal{O}(N^2)$ LLM context overhead. Quorum executes graph discovery through a two-tier neurosymbolic pipeline:
1. *Lexically Anchored Proposition Atomization ($\mathcal{V}_{\text{claim}}$):* Two-pass atomic decomposition extracts candidate propositions grounded in verbatim citations satisfying physical provenance verification ($\lambda_i = 1$).
2. *Sliding-Window Dependency Prediction ($\mathcal{E}_{\text{deps}}$):* Propositions are partitioned into sequential chunk packets and scanned through a sliding window of width $W_{\text{win}}$ chunks with step overlap $O_{\text{win}}$. Within each window, atoms are assigned deterministic, short attention anchors ($a_0, a_1$) to eliminate token bloat and prevent system UUID hallucinations. The model predicts directed causal dependencies ($X \xrightarrow{\mathbf{W}_{XY}} Y$) along with explicit Toulmin backing warrants and expected precondition states.
3. *Defensive Invariant Enforcement:* Hallucinated or out-of-window aliases are dropped fail-fast by the service layer, immediate self-dependencies ($X \to X$) are pruned, and directed cycles are detected prior to wave execution via Johnson's elementary cycle algorithm in an isolated worker thread. If cycles are detected, participating nodes are flagged with `cycle_detected = True`, immediately clamping downstream argument cohesion to the Novice floor ($L_1$).
4. *Sliding-Window Horizon Truncation of Long-Range Dependencies:* Because proposition linking evaluates chunk packets within a finite sliding window ($W_{\text{win}} = 4$ chunks, step overlap $O_{\text{win}} = 2$ chunks, $M_{\text{win}} \le 20$ atoms), dependency discovery operates within a localized observation horizon ($\Delta_{\max} \le M_{\text{win}} = 20$ proposition atoms). In extended policy and foresight documents ($|\mathcal{V}_{\text{claim}}| \in [141, 252]$ atoms), long-range deductive dependencies linking foundational introductory axioms directly to terminal executive conclusions cannot co-occur in the same sliding window without continuous intermediate mentions. Consequently, foundational axioms lacking local descendants within their initial window remain at $\text{OutDegree}(v) = 0$, structurally contributing to the isolated concept ratio $r_{\text{iso}}$. In prospective iterations, this horizon bound is mitigated by pinning identified root axioms ($\text{InDegree}(v) = 0$) into a persistent Global Context Anchor header prepended across all subsequent sliding windows.

*Epistemic Demarcation: The Two-Pillar Causal Architecture:* To resolve the foundational question of how computational systems evaluate causality in natural language discourse without circular re-prompting or conflating baseline grading with counterfactual stress-testing, Quorum establishes a decoupled **Two-Pillar Causal Architecture**:

1. **Pillar 1: Pure Stateless Baseline Evaluation (Section 4.2.1):** Generates the 0-token evaluative BARS score for the causal reasoning matrix $\mathcal{M}_{\text{Causal}}$ across hierarchical competence Tiers $L_1 \dots L_5$ (Equation 13). It evaluates static, unperturbed macroscopic topological invariants ($|\mathcal{V}_{\text{claim}}|$, $r_{\text{iso}}$, $r_{\text{LCC}}$, $r_{\text{conv}}$, acyclicity) under the Cumulative Guttman Invariant, functioning as a robust low-pass filter against stochastic extraction variance.
2. **Pillar 2: Discrete ATMS Truth Maintenance & Counterfactual Surgery (Algorithm 1):** Operates on compiled graph instances to perform interactive counterfactual stress-testing (Rungs 2/3), forward wave precondition enforcement, backward root-cause isolation ($RC$), prescriptive remediation (actionable premise repair recommendations), and secondary fault dampening (fair fault-attribution scoring breakdowns).

*Quiescent Baseline vs. Active Counterfactual Dynamics:* In a clean baseline evaluation pass where all extracted discourse claims are validly grounded and acyclic, Algorithm 1 operates in its quiescent baseline state: $S^* = S_{\text{init}}$, $\text{Cascade} = \emptyset$, and $RC = \emptyset$. Its active perturbation dynamics are engaged conditionally: (i) dynamically when upstream processing errors or cycle defects occur during execution, (ii) prescriptively to deduplicate downstream cascading penalties, or (iii) interactively within the supervisory interface when an auditor simulates counterfactual premise retractions ($X \gets \text{RETRACTED}$) to audit warrant independence.

*Operationalization of Premise Perturbation via Discrete Graph Surgery & Truth Maintenance:* In Assumption-Based Truth Maintenance Systems (ATMS; Doyle, 1979; de Kleer, 1986), retracting or invalidating a premise $X$ is evaluated graph-theoretically by isolating the premise ($X \gets \text{RETRACTED}$) and severing incoming support edges in the dependency graph $\mathcal{G}_{\text{pruned}}$.

A foundational question in NLP argumentation is: *Which computational system physically evaluates the downstream consequences of this structural intervention in discourse?* If a secondary LLM is re-prompted to judge whether claim $Y$ survives without premise $X$, the pipeline relapses into second-order stochasticity and confirmation bias.

In Quorum, once $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$ is compiled, structural interventions and downstream cascades are **NOT executed via LLM prompts or statistical regression**. Conditional on the compiled graph instance $\mathcal{G}_{\text{LAG}}$, the extracted discourse is evaluated via **deterministic graph surgery and Assumption-Based Truth Maintenance Systems (ATMS)** (Doyle, 1979; de Kleer, 1986) evaluated over formal computational argumentation graphs (Dung, 1995), formalized in Algorithm 1 as the Unified Formal Specification:

```
Algorithm 1: Discrete Structural Argument Surgery & Truth Maintenance (ATMS)
================================================================================
Input  : Argument DAG G = (V, E, W), retracted node X in V, counterfactual state x* in {FAILED, BLOCKED},
         gate semantics mode in {CONJUNCTIVE_AND, DISJUNCTIVE_OR}
Output : Perturbed state mapping S*, Reachability Cascade Reach(X), Root Causes RC,
         Node Root Causes RC_node, Warrant/Edge Root Causes RC_edge
================================================================================
Helper Functions:
  BrokenSupport(v, E_ref) := { P in Parents(v, E_ref) | S*[P] != expected_status(P, v) or lambda(W_{Pv}) == 0 }
  expected_status(P', C)  := EdgeCondition(P', C).expected_state (defaults to PASSED)
--------------------------------------------------------------------------------
1: S* <- InitialStateMap(V)                          // Base status from lexical grounding Gate
2: S*[X] <- x*                                       // Clamp intervened node to counterfactual state
3: Queue Q <- [ X ]
4: Visited Vis <- { X }
5: Cascade <- []
6: while Q is not empty do
7:     curr <- Q.pop_front()
8:     for each child C in Children(curr, E) do
9:         if C not in Vis then
10:            // Evaluate Precondition & Warrant Gate under active topology semantics:
11:            if mode == CONJUNCTIVE_AND then
12:                // Deductive Reachability Gate: All antecedents and supporting warrants must be valid
13:                survives_gate <- forall P' in Parents(C, E):
14:                                 (S*[P'] == expected_status(P', C) and lambda(W_{P'C}) == 1)
15:            else
16:                // Corroborative Warrant Redundancy: Alternative valid warrant shields C
17:                survives_gate <- exists P' in Parents(C, E)
18:                                 such that S*[P'] == expected_status(P', C) and lambda(W_{P'C}) == 1
19:            end if
20:            if not survives_gate then
21:                S*[C] <- BLOCKED                      // (or N_A on precondition mismatch)
22:                Vis.add(C)
23:                Cascade.append(C)
24:                Q.push_back(C)
25:            end if
26:        end if
27:    end for
28: end while
29: RC_node <- { v in V | S*[v] in {FAILED, BLOCKED} and BrokenSupport(v, E) == emptyset }
30: RC_edge <- { (P', v) in E | S*[v] == BLOCKED and S*[P'] == PASSED and (lambda(W_{P'v}) == 0 or S*[P'] != expected_status(P', v)) }
31: RC <- RC_node union { v in V | exists P' in Parents(v, E) such that (P', v) in RC_edge }
32: return (S*, Cascade, RC, RC_node, RC_edge)
================================================================================
```

*Algorithmic Guarantees and Dual-Engine Physical Pipeline Mapping of Algorithm 1:*
1. **Zero Second-Order LLM Calls & Linear Complexity Bound:** Lines 6–28 operate in deterministic linear time $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ over in-memory adjacency lists in compiled code. While Lines 13–19 present explicit quantifier scans over $\text{Parents}(C, E)$ for declarative mathematical readability, standard operational implementations (specifically Quorum's `TopologicalEvaluator`) enforce $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ linear complexity by maintaining an integer degree counter $\text{active\_valid\_parents}[C]$ initialized in $\mathcal{O}(|\mathcal{E}|)$ and decremented in $\mathcal{O}(1)$ time per failed incoming edge. In `CONJUNCTIVE_AND` mode, child $C$ short-circuits upon the first invalid parent ($\text{active\_valid\_parents}[C] < \text{InDegree}(C)$); in `DISJUNCTIVE_OR` mode, $C$ transitions to `BLOCKED` if and only if all corroborating parents fail ($\text{active\_valid\_parents}[C] == 0$), guaranteeing that each edge $(P, C) \in \mathcal{E}$ is traversed at most once. No stochastic LLM sampling occurs during perturbation evaluation.
2. **Equivalence to Pearl/ATMS Edge Severing on DAGs:** In structural causal models (Pearl, 2000), an intervention $do(X = x^*)$ severs incoming arrows to $X$. In Algorithm 1, clamping the state $S^*[X] \gets x^*$ (Line 2) and propagating reachability forward strictly to descendants along directed paths in $E$ is algebraically identical to explicit edge deletion, because in an acyclic graph (DAG), no directed path exists from any descendant $C \in \text{Descendants}(X)$ back to $X$ ($\text{Descendants}(X) \cap \text{Parents}(X) = \emptyset$). Backward fault attribution (Lines 29–31) evaluates parent failure and warrant grounding over the original dependency graph $E$ ($\text{BrokenSupport}(v, E) = \emptyset$), mirroring the production causal discovery engine where a node is categorized in $\text{RC}_{\text{node}}$ if and only if none of its true inbound parents in $E$ possess invalid state or broken inferential warrants.
3. **Deductive Reachability Gating and Dual-Role Wave Pruning:** Lines 11–15 enforce strict `CONJUNCTIVE_AND` precondition semantics during forward reachability evaluation. Every antecedent $P' \in \text{Parents}(C)$ is a necessary condition: child $C$ survives if and only if every antecedent satisfies its expected status *and* its supporting inferential warrant is physically grounded in the discourse ($\lambda(W_{P'C}) = 1$). If any parent enters a blocked or failed state or possesses an unverified warrant, child $C$ deterministically short-circuits to `BLOCKED`. 

   *Architectural Demarcation of Dual-Role Wave Pruning:* We explicitly disambiguate how this short-circuiting mechanism operates across Quorum's two distinct DAG execution domains:
   - **(a) Mined Argument DAG ($\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$ in Algorithm 1):** Because all discourse propositions $v \in \mathcal{V}_{\text{claim}}$ are extracted in Pass 1 and linked in Pass 2, Algorithm 1 executes purely in-memory in **0 additional LLM tokens** ($\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$, $< 1.0\text{ ms}$). Here, short-circuiting prunes child nodes from the *epistemic validity reachability set*—accumulating them into $\text{Cascade}$ to quantify argument collapse and isolate root causes ($RC$) without further computation. Zero subsequent LLM verification passes are dispatched over $\mathcal{G}_{\text{LAG}}$.
   - **(b) Rubric Evaluation Poset ($\mathcal{A}_{\text{rubric}}$ in `EnrichedDagExecutor`):** Concurrently, the identical Kahn wave short-circuiting primitive in `TopologicalEvaluator` is deployed during matrix evaluation over fixed BARS criteria ($a_i \in \mathcal{A}_{\text{rubric}}$). When an antecedent rubric criterion fails its expected status (specifically Novice Level 1 baseline failure), dependent child criteria are transitioned to `ExecutionStatus.N_A` or `BLOCKED` prior to wave dispatch, **completely pruning child nodes from generative LLM sensor evaluation batches** (`ExtractiveSensorService.evaluate_atom_boolean_batch`), thereby eliminating redundant API tokens and inference latency.
4. **Harmonized Backward Fault Attribution & Dual Root Cause Isolation:** Lines 29–31 execute backward graph traversal across inbound dependencies of evaluated argument structures over the original edge graph $E$. To prevent the logical edge case where downstream blocked nodes are misclassified as independent root causes due to inferential edge failures, blame attribution is harmonized with the forward reachability gate via:
   $$\text{BrokenSupport}(v, E) := \left\{ P' \in \text{Parents}(v, E) \;\middle\vert{}\; S^*[P'] \neq \text{expected\_status}(P', v) \;\lor\; \lambda(W_{P'v}) == 0 \right\}$$
   The engine cleanly decomposes root causes into two mutually exclusive, strictly typed sets:
   - *(a) Node Root Causes ($\text{RC}_{\text{node}}$):* Validating claims that failed intrinsic physical grounding or were directly intervened upon ($S^*[v] \in \{\text{FAILED}, \text{BLOCKED}\}$) with zero broken parent supports ($\text{BrokenSupport}(v, E) = \emptyset$).
   - *(b) Warrant/Edge Root Causes ($\text{RC}_{\text{edge}}$):* Identifying inferential transmission breakdowns where parent premises are valid ($S^*[P'] = \text{PASSED}$), but the connecting inferential warrant lacks physical lexical grounding ($\lambda(W_{P'v}) = 0$) or violates expected precondition states, transitioning child $v$ to `BLOCKED`.
   This ensures downstream consequences are never conflated with independent claim errors, and authors are not penalized for ungrounded warrants as if they had asserted false propositions.
5. **Corroborative Redundancy & Counterfactual Surgery:** Lines 16–19 formalize corroborative warrant redundancy (`DISJUNCTIVE_OR`), where alternative valid evidentiary warrants preserve claim truth values. Because satisfying $S^*[P'] == \text{expected\_status}(P', C)$ already excludes any compromised parent in $\text{Vis}$ (since $\forall v \in \text{Vis}, S^*[v] \in \{\text{FAILED}, \text{BLOCKED}\}$), checking `Parents(C, E)` guarantees that only currently valid, uncompromised parent warrants can corroborate child $C$. In production runtime architecture, real-time forward DAG evaluation over rubric criteria ($\mathcal{A}_{\text{rubric}}$) and interactive counterfactual simulation over discourse graphs ($\mathcal{G}_{\text{LAG}}$) are cleanly decoupled: the forward wave scheduler in `EnrichedDagExecutor` maintains strict single responsibility over real-time sensor batch evaluation and mutation invariance, while interactive counterfactual surgery (Algorithm 1) is partitioned to dedicated simulation services operating on transient in-memory graph clones in 0 tokens.
6. **Dynamic Multi-Parent Cascade Resolution:** In `DISJUNCTIVE_OR` mode, child node $C$ is added to $\text{Vis}$ and $Q$ if and only if all corroborating parent paths collapse (`survives_gate == false`). If $C$ survives an initial parent failure due to an alternative valid parent, it remains outside $\text{Vis}$, ensuring that if subsequent upstream failures in the same wave sever its remaining warrants, $C$ is correctly re-evaluated, transitioned to `BLOCKED`, and propagated downstream without graph traversal leaks.
7. **Instance-Conditional Determinism vs. Stochastic Extraction Non-Isomorphism:** We formalize a strict architectural boundary: Algorithm 1's computational determinism and polynomial time bounds $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ are strictly *conditional on a compiled graph instance* $\mathcal{G}_{\text{LAG}} = (\mathcal{V}, \mathcal{E})$. When extracting discourse graphs from unconstrained natural text via frontier autoregressive decoders, verbatim quote overlap between independent stochastic runs is bounded ($25.3\%–31.9\%$; Section 8.6, Point 5), meaning separate runs yield distinct node sets $\mathcal{V}_1 \neq \mathcal{V}_2$ and non-isomorphic micro-topologies ($\mathcal{G}_1 \not\simeq \mathcal{G}_2$). Consequently, executing Algorithm 1 across Run 1 versus Run 2 operates on disjoint node universes and yields distinct run-specific root-cause sets $RC_1 \neq RC_2$. Node-level premise retraction and root-cause isolation provide rigorous, deterministic local explainability for an individual compiled run, whereas end-to-end stability across runs is guaranteed at the macro-topological invariant level ($r_{\text{iso}}$, acyclicity, and Guttman cohesion $\mathcal{C}_{\text{causal}}$) via topological low-pass filtering.

*Scope Demarcation (Discrete ATMS Truth Maintenance vs. Observational Do-Calculus):* As defined above, Quorum evaluates discrete computational argumentation graphs and Assumption-Based Truth Maintenance Systems (Doyle, 1979; de Kleer, 1986; Dung, 1995) rather than observational statistical distributions or backdoor adjustments. Algorithm 1 deterministically audits whether an author's conclusions retain surviving physical warrants ($\mathbf{W}$) or experience justification collapse when antecedent premises are retracted.

This maps structurally to the epistemic demands of the Three Rungs of Argument Rigor:
* **Rung 1 (Associative Co-occurrence & Fluff):** Unidirectional linguistic correlation lacking explicit warrants ($\mathbf{W} = \emptyset$). Listing co-occurring industry trends without causal transmission mechanisms incurs severe passive delegation penalties.
* **Rung 2 (Intervention Audit & Warrant Isolation):** Simulating structural interventions by pruning parent dependencies. The audit evaluates whether the text explicitly defines operational mechanisms $\mathbf{W}_{XY}$ isolating the claim from common-cause confounding ($U_{XY}$).
* **Rung 3 (Counterfactual Stress-Testing):** Evaluating counterfactual boundary transitions. The audit examines whether the author subjected proposed strategies to "what-if" boundary conditions, failure thresholds, negative externalities, and resource exhaustion scenarios.

### 4.2.1. Pure Stateless Causal Cohesion Evaluation and the 0-Token Cumulative Guttman Invariant

In contemporary multi-agent reasoning systems, assessing whether an authored discourse forms a coherent, non-trivial argument is routinely delegated to secondary LLM evaluation passes (specifically LLM-as-a-Judge prompting with subjective instructions including *"Rate the causal coherence from 1 to 5"*; Zheng et al., 2023). This practice introduces stochastic scoring variance, circular hallucinations, token cost explosions, and prompt-injection vulnerability.

Quorum eliminates stochastic judge prompts for argument cohesion through the **Pure Stateless Causal Cohesion Evaluator**, a deterministic compute engine that evaluates macro-argument structure directly from the topology of the mined Argument DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$:

1. **The Cumulative Guttman Invariant and Multi-Factor Topological Predicates:** Structural argument cohesion is formalized as a strictly cumulative, monotonic scale (Guttman, 1944) across Behaviorally Anchored Rating Scale (BARS) Tiers 1–5 ($L_1 \subset L_2 \subset L_3 \subset L_4 \subset L_5$). To eliminate graph-theoretic degeneracies where fragmented subgraphs trivially pass degree-based filters, Quorum defines three orthogonal topological metrics over $\mathcal{G}_{\text{LAG}}$:

   * *Weakly Connected Components & Largest Component Ratio ($r_{\text{LCC}}$):* Let $\text{WCC}(\mathcal{G}_{\text{LAG}}) = \{\mathcal{C}_1, \dots, \mathcal{C}_k\}$ be the set of weakly connected components in the underlying undirected projection of $\mathcal{G}_{\text{LAG}}$, with largest weakly connected component $\mathcal{V}_{\text{LCC}} = \arg\max_{\mathcal{C} \in \text{WCC}} |\mathcal{V}(\mathcal{C})|$. The macro-reachability component ratio is defined as:
     $$r_{\text{LCC}} = \begin{cases} 1.0, & |\mathcal{V}_{\text{claim}}| \le 1 \\ \frac{|\mathcal{V}_{\text{LCC}}|}{|\mathcal{V}_{\text{claim}}|}, & |\mathcal{V}_{\text{claim}}| > 1 \end{cases}$$
   * *Isolated Concept Fraction ($r_{\text{iso}}$):* The fraction of propositions possessing degree zero ($\text{InDegree}(v) + \text{OutDegree}(v) = 0$):
     $$r_{\text{iso}} = \frac{|\{v \in \mathcal{V}_{\text{claim}} \mid \text{InDegree}(v) + \text{OutDegree}(v) = 0\}|}{|\mathcal{V}_{\text{claim}}|}$$
   * *Branch Convergence Ratio ($r_{\text{conv}}$):* The fraction of claims synthesizing multi-premise warrants ($\text{InDegree}(v) \ge 2$), measuring convergent evidentiary branches:
     $$r_{\text{conv}} = \frac{|\{v \in \mathcal{V}_{\text{claim}} \mid \text{InDegree}(v) \ge 2\}|}{|\mathcal{V}_{\text{claim}}|}$$

   *Dual-Track Evaluation Architecture (Continuous UI Telemetry vs. Discrete Guttman Invariants):* Structural argument evaluation operates across two cleanly decoupled tracks:
   1. *Continuous UI Telemetry Scalar:* For human reporting, dashboards, and Server-Driven UI (SDUI) diagnostic cards, structural logical cohesion is computed as a continuous scalar metric $\text{cohesion\_score} \in [0, 1]$:
   $$\text{cohesion\_score} = \begin{cases} 1.0, & |\mathcal{V}_{\text{claim}}| = 0 \\ \left(1.0 - r_{\text{iso}}\right) \cdot \left(\frac{1}{2}\right)^{\mathbb{I}(\text{cycle\_detected})}, & |\mathcal{V}_{\text{claim}}| > 0 \end{cases}$$
   where the factor $(1/2)^{\mathbb{I}(\text{cycle\_detected})}$ visibly penalizes directed cycle defects in continuous dashboard telemetry, halving the displayed scalar score even when discrete grading is clamped to the Novice floor.
   2. *Discrete BARS Guttman Tier Invariants ($L_1 \dots L_5$):* In contrast to continuous scalar reporting, discrete qualification across Behaviorally Anchored Rating Scale (BARS) tiers is governed by strictly cumulative, monotonic Boolean predicates. Because directed acyclicity $(\neg \text{cycle\_detected})$ is enforced as a strict prerequisite at Level 2 (and inherited monotonically by $L_3 \dots L_5$), $\mathbb{I}(\text{cycle\_detected}) \equiv 0$ for all candidate acyclic graphs eligible to pass higher tiers, identically collapsing the scalar score to $\text{cohesion\_score} \equiv 1.0 - r_{\text{iso}}$. To eliminate algebraic redundancy between $\text{cohesion\_score} \ge \theta_{Lk}$ and $r_{\text{iso}} \le r^{\max}_{Lk}$ (where $r_{\text{iso}} \le r^{\max}_{Lk}$ strictly dominates $1.0 - r_{\text{iso}} \ge \theta_{Lk}$), the hierarchical BARS predicates are formalized directly through non-redundant structural invariant bounds:
   $$\begin{aligned}
   L_1 &= (|\mathcal{V}_{\text{claim}}| \ge 1) \quad (\text{Novice floor requires non-empty discourse graph}) \\
   L_2 &= L_1 \;\land\; (|\mathcal{V}_{\text{claim}}| \ge 2) \;\land\; (\neg \text{cycle\_detected}) \;\land\; (r_{\text{iso}} \le 1.0 - \theta_{L2}) \;\land\; (r_{\text{LCC}} \ge r^{\min}_{\text{LCC}, L2}) \\
   L_3 &= L_2 \;\land\; (|\mathcal{V}_{\text{claim}}| \ge 5) \;\land\; (r_{\text{iso}} \le r^{\max}_{L3}) \;\land\; (r_{\text{LCC}} \ge r^{\min}_{\text{LCC}, L3}) \\
   L_4 &= L_3 \;\land\; (|\mathcal{V}_{\text{claim}}| \ge 10) \;\land\; (r_{\text{iso}} \le r^{\max}_{L4}) \;\land\; (r_{\text{LCC}} \ge r^{\min}_{\text{LCC}, L4}) \;\land\; (r_{\text{conv}} \ge r^{\min}_{\text{conv}, L4}) \\
   L_5 &= L_4 \;\land\; (|\mathcal{V}_{\text{claim}}| \ge 15) \;\land\; (r_{\text{iso}} \le r^{\max}_{L5}) \;\land\; (r_{\text{LCC}} \ge r^{\min}_{\text{LCC}, L5})
   \end{aligned} \tag{13}$$

   In the system configuration, thresholds are parameterized as:
   * $\theta_{L2} = 0.30 \implies 1.0 - \theta_{L2} = 0.70$ and $r^{\min}_{\text{LCC}, L2} = 0.35$ (minimum cohesion and component core for Level 2 emerging chains),
   * $r^{\max}_{L3} = 0.20$ (baseline production default; satisfying $r^{\max}_{L3} \le 1.0 - \theta_{L3} = 0.50$, dominating continuous thresholding) and $r^{\min}_{\text{LCC}, L3} = 0.50$ (maximum 20% isolated claims and 50% majority component for Level 3 Toulmin warrant grounding; in exploratory cross-genre sensitivity analysis [Section 8.3], a calibrated configuration $r^{\max}_{L3} = 0.30$ accommodates legitimate standalone scoping context [$\mathcal{V}_{\text{scoping}}$] in strategic discourse where background framing premises lacking downstream causal edges [$\text{OutDegree}(v) = 0$] are counted in $r_{\text{iso}}$ under the 0-token stateless evaluation law),
   * $r^{\max}_{L4} = 0.15$ (satisfying $r^{\max}_{L4} \le 1.0 - \theta_{L4} = 0.30$), $r^{\min}_{\text{LCC}, L4} = 0.70$, and $r^{\min}_{\text{conv}, L4} = 0.05$ (requiring branch convergence and multi-premise synthesis for Level 4),
   * $r^{\max}_{L5} = 0.05$ (satisfying $r^{\max}_{L5} \le 1.0 - \theta_{L5} = 0.15$) and $r^{\min}_{\text{LCC}, L5} = 0.85$ (maximum 5% isolated claims and 85% unified macro-reachability for Level 5 mastery).

   *Graph-Theoretic Invariant Proof: Defense Against Dyad Fragmentation:* We formalize why enforcing the orthogonal component threshold $r_{\text{LCC}} \ge r^{\min}_{\text{LCC}, Lk}$ in Equation (13) is mathematically necessary. Suppose an authored text produces a completely fragmented discourse graph consisting of $k = n/2$ disjoint, unconnected pairs ($v_1 \to v_2, \; v_3 \to v_4, \dots$). Under a naive degree-zero formulation ($1 - r_{\text{iso}}$), every node possesses $\text{deg}(v) = 1 > 0$, yielding $r_{\text{iso}} = 0.0$ and $\mathbb{I}(\text{cycle\_detected}) = 0$. Consequently, a collection of disconnected two-node islands would trivially achieve a perfect raw $\text{cohesion\_score} = 1.00$ and potentially pass higher tiers if cohesion were evaluated without reachability gates, despite possessing zero global reachability, zero macro-coherence, and zero multi-premise synthesis. By enforcing $r_{\text{LCC}} \ge r^{\min}_{\text{LCC}, Lk}$ as an independent Boolean conjunct at every level $L_2 \dots L_5$, the largest component size is bounded by $|\mathcal{V}_{\text{LCC}}| = 2$, yielding $r_{\text{LCC}} = 2/n \to 0$ as $n$ grows. For any non-trivial discourse ($n \ge 6$), $r_{\text{LCC}} \le 0.33 < r^{\min}_{\text{LCC}, L2} = 0.35$, which immediately fails Level 2 ($L_2 = \text{False}$) and deterministically clamps the fragmented discourse to the Novice floor ($L_1$), proving absolute mathematical defense against dyad fragmentation without double-penalizing component size in the scalar cohesion score.

   *Decoupling of Baseline Guttman Scoring from Perturbation Dynamics:* Under Quorum's Two-Pillar Causal Architecture (Section 4.2), baseline Guttman scoring evaluates the invariant topological properties of the unperturbed base graph in 0 additional tokens, preserving test–retest stability. Conversely, Algorithm 1 acts as a decoupled diagnostic operator $\mathcal{T}_{X, x^*}$ for interactive counterfactual surgery, automated sensitivity audits, and cascading fault isolation.

2. **The 0-Token Evaluation Contract and Token Boundary Demarcation:** We explicitly delineate the token boundaries of the causal pipeline. While upstream proposition extraction and sliding-window dependency linking operate as LLM-assisted cognitive steps (consuming bounded input and output tokens during Phase 1 DAG execution), the subsequent macro-argument evaluation and counterfactual graph surgery consume strictly **zero additional LLM tokens ($0\text{ tokens consumed}$)**. Instead of prompting an external LLM judge to subjectively rate coherence, the Pure Stateless Causal Cohesion Evaluator computes structural graph invariants (connected component ratio, acyclicity, isolated concept fraction $r_{\text{iso}}$) in linear time $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ and projects them deterministically into BARS Tiers 1–5 via the Cumulative Guttman Invariant (Equation 13). This completely insulates qualitative scoring from the stochastic token volatility, prompt injection risks, and cost explosions of secondary LLM-as-a-judge passes.

3. **Cycle Defect Quarantine:** If the topological cycle detector detects directed cycles ($\mathcal{C}_{\text{cycle}} \neq \emptyset$), the graph violates DAG partial order invariants. The evaluator flags a structural cycle defect (`cycle_detected = True`), immediately failing Level 2 ($L_2 = \text{False}$) and clamping the argument cohesion score to the Novice floor ($l = 1$).

4. **Idempotent Graph Fusion and Concurrency Guards:** In multi-step or multi-model executions, redundant evaluations of identical causal sources are prevented via idempotent graph fusion guards, guaranteeing deterministic, replayable scoring.

5. **Multi-Document Ingress Scope, Dynamic Input Roles, and the Deliverable Subgraph Invariant:** Enterprise workflows evaluate submissions composed of arbitrary dynamic input documents defined through workflow metadata (`expected_inputs: list[ExpectedInput]`). Rather than imposing rigid, static document triads or fixed file keys, Quorum classifies input documents dynamically through orthogonal, typed schema predicates:
   * Candidate Deliverables (`is_endorsed_deliverable = True`, or non-conversational, non-assignment input keys by positive set resolution),
   * Conversational Steering & Dialogue History (`is_chat_history = True`),
   * Reference Instructions & Prompt Assignments (`is_assignment = True`).

   While the composite proposition graph $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$ is mined across the full concatenated multi-document payload to discover end-to-end provenance across inputs, evaluating structural argument cohesion ($\mathcal{M}_{\text{Causal}}$) requires formal deliverable subgraph induction to avoid construct validity confounding:
   * *The Construct Validity Confound of Concatenated Ingress:* In unpartitioned evaluation, conversational steering turns (specifically prompt formatting directives or conversational clarifications), authorial reflection documents, and contextual assignments do not form dense deductive chains with deliverable arguments, emerging predominantly as degree-zero nodes ($\text{InDegree}(v) + \text{OutDegree}(v) = 0$). When pooled into a single global denominator, an operator who engages in thorough supervisory steering or self-reflection generates more non-deliverable nodes, artificially distorting global $r_{\text{iso}}$ ($52.48\%$ in Pair A, $23.6\%–26.6\%$ in Pair B) and conflating conversational framing with substantive argument structure.
   * *Deliverable Subgraph Induction and Denominator Invariant:* Because Ingress Gate 3 tracks source document provenance for each extracted proposition atom via `source_input_key` and parses structured `<ai_context_directive document="{input_key}">` boundaries, the 0-token Pure Stateless Causal Cohesion Evaluator evaluates deliverable cohesion ($r_{\text{iso}}^{\text{deliv}}, r_{\text{LCC}}^{\text{deliv}}, r_{\text{conv}}^{\text{deliv}}$) strictly over the **induced deliverable subgraph** $\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$. Normalizing metric denominators strictly to deliverable node cardinality $N_{\text{deliv}} = |\mathcal{V}_{\text{deliverable}}|$ isolates the substantive topology of the candidate deliverable, preventing supervisory dialogue volume and authorial reflection text from contaminating deliverable argument cohesion.
   * *Intrinsic Isolated Claims vs. Threshold Calibration:* Inducing $\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$ separates non-deliverable dialogue noise from the author's substantive argument, exposing the true structural drivers of residual claim isolation: **sliding-window horizon truncation** ($\Delta_{\max} \le 20$ atoms across distant chapters; see Definition 3 and Section 10) and **standalone introductory scoping axioms** ($\mathcal{V}_{\text{scoping}}$). Calibrating the Level 3 tolerance ceiling to $r^{\max}_{L3} = 0.30$ accommodates legitimate foundational scoping context and attention horizon bounds on substantive merit, while empirical case-specific node reductions are analyzed in Section 8.3.
   * *Exogenous Boundary Axiom:* Cross-document dependencies ($X_{\text{dialogue}} \xrightarrow{\mathbf{W}} Y_{\text{deliverable}}$) linking supervisory dialogue directives to deliverable assertions are preserved: when inducing $\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$, $X_{\text{dialogue}}$ is treated as an *exogenous boundary axiom* ($\mathcal{V}_{\text{axiom}}$). Deliverable node $Y$ receives a valid incoming warrant ($\text{InDegree}_{\text{cross}}(Y) > 0$), meaning $Y$ receives incoming evidential support and is **not classified as an isolated claim**, while $X$ is not included in $\mathcal{V}_{\text{deliverable}}$ nor counted in the deliverable denominator $N_{\text{deliv}}$, cleanly preventing conversational dialogue volume from deflating deliverable argument cohesion.
   * *0-Token Cross-Document Steering Coupling Ratio ($\kappa_{\text{steer}}$):* Concurrently, the engine evaluates human–AI collaboration through an orthogonal 0-token metric:
     $$\kappa_{\text{steer}} = \begin{cases} 0.0, & |\text{Root}(\mathcal{G}[\mathcal{V}_{\text{deliverable}}])| = 0 \\ \frac{|\{ Y \in \text{Root}(\mathcal{G}[\mathcal{V}_{\text{deliverable}}]) \mid \exists X \in \mathcal{V}_{\text{dialogue}}: X \xrightarrow{\mathbf{W}} Y \}|}{|\text{Root}(\mathcal{G}[\mathcal{V}_{\text{deliverable}}])|}, & |\text{Root}(\mathcal{G}[\mathcal{V}_{\text{deliverable}}])| > 0 \end{cases} \tag{13b}$$
     measuring the fraction of the candidate deliverable's foundational root claims that are explicitly anchored by upstream supervisory human dialogue directives.

---

## 5. Two-Factor Orthogonal Matrix Scoring and Asymmetric Falsification

### 5.1. BARS Criteria Weighting and Division-by-Zero Protection

Evaluation matrices implement Behaviorally Anchored Rating Scales (BARS) distributed across five hierarchical tiers $l \in \{1, \dots, 5\}$ with natural weight function $w(l) = l$. Across the evaluated rubric matrices, every pre-compiled criterion $a_i \in \mathcal{A}_{\text{rubric}}$ ($N = 110$) resolves to a discrete status $\omega(a_i) \in \{ \text{PASSED}, \text{FAILED}, \text{DLQ} \}$ through the formal piecewise transfer function:

$$\omega(a_i) = \begin{cases} 
\text{DLQ}, & \text{if processing exception } \xi_i = 1 \\ 
\text{PASSED}, & \text{if } \xi_i = 0 \;\land\; [(\pi_i = +1 \;\land\; \lambda_i = 1 \;\land\; \tau_{\text{val}, i} = 1) \;\lor\; (\pi_i = -1 \;\land\; \neg(\lambda_i = 1 \;\land\; \tau_{\text{val}, i} = 1))] \\ 
\text{FAILED}, & \text{if } \xi_i = 0 \;\land\; [(\pi_i = +1 \;\land\; (\lambda_i = 0 \;\lor\; \tau_{\text{val}, i} = 0)) \;\lor\; (\pi_i = -1 \;\land\; \lambda_i = 1 \;\land\; \tau_{\text{val}, i} = 1)] 
\end{cases} \tag{14}$$

where $\xi_i \in \{0, 1\}$ indicates unresolvable processing exceptions (routing to Dead-Letter Queue). Equation (14) formalizes the asymmetric epistemic polarity of the rubric: for positive capability criteria ($\pi_i = +1$), discovering verified physical citation evidence ($\lambda_i = 1$) that semantically satisfies the rubric criteria under parallel Best-of-3 ensemble consensus ($\tau_{\text{val}, i} = 1$) yields $\omega(a_i) = \text{PASSED}$, incrementing achieved tier hits $h_l$ in Equation (15). If the citation fails physical verification ($\lambda_i = 0$) or the model's reasoning concludes that the cited evidence falls short of the strict rubric threshold ($\tau_{\text{val}, i} = 0$), the atom resolves to $\text{FAILED}$. Conversely, for negative anti-pattern criteria ($\pi_i = -1$), finding no verified violation citation ($\neg(\lambda_i = 1 \land \tau_{\text{val}, i} = 1)$) confirms clean performance ($\omega(a_i) = \text{PASSED}$, accruing zero capability points), whereas verifying both physical evidence and semantic confirmation of an anti-pattern ($\lambda_i = 1 \land \tau_{\text{val}, i} = 1$) confirms a violation ($\omega(a_i) = \text{FAILED}$, registering a penalty deduction $p_k$ in Equation 17).

For positive capability atoms ($\pi_i = +1$), achieved points $A$ and effective maximum points $M$ are computed over all tiers up to the matrix's maximum scale tier $L_{\max}^{(m)}$ ($L_{\max}^{(m)} = 5$ for standard BARS rubrics; $L_{\max}^{(m)} = 6$ for the six-tier Bloom cognitive taxonomy $\mathcal{M}_{\text{Bloom}}$):

$$A = \sum_{l=1}^{L_{\max}^{(m)}} l \cdot h_l, \quad M = \sum_{l=1}^{L_{\max}^{(m)}} l \cdot (t_l - d_l) \tag{15}$$

where $h_l$ is passed hits, $t_l$ is total criteria count, and $d_l$ is DLQ exceptions at tier $l$. The weighted linear ratio $\rho$ is safeguarded against division-by-zero singularities:

$$\rho = \begin{cases} \frac{A}{M}, & M > 0 \\ 0.0, & M \le 0 \end{cases} \tag{16}$$

### 5.2. Asymmetric Popperian Falsification Multiplier

Negative anti-pattern atoms ($\pi_i = -1$) act as non-additive gatekeeping falsifiers. If an anti-pattern violation is confirmed ($\omega(a_i) = \text{FAILED}$ relative to clean performance), a penalty deduction $p_k \in (0, 1)$ is registered. The composite multiplier is formed multiplicatively over the set of confirmed violations:

$$\Pi_{\text{penalty}} = \begin{cases} \max\left( 1 - P_{\max}, \; \prod_{k=1}^{K_{\text{pen}}} (1 - p_k) \right), & K_{\text{pen}} > 0 \\ 1.0, & K_{\text{pen}} = 0 \end{cases} \tag{17}$$

where $K_{\text{pen}}$ is the count of confirmed anti-pattern violations and $P_{\max} = 0.40$ is the hard-coded ceiling capping total cumulative deductions at $40\%$. This $P_{\max} = 0.40$ ceiling is intentionally coupled with Kahn wave precondition short-circuiting (Section 4.2, Guarantee 3b): non-fatal cognitive anti-patterns ($\pi_i = -1$) are bounded multiplicatively ($\Pi_{\text{penalty}} \ge 0.60$) to preserve Lipschitz score stability, whereas non-negotiable regulatory or domain prerequisites are encoded as Level 1 baseline preconditions whose failure deterministically clamps dependent upper-tier criteria ($L_2 \dots L_5$) to `BLOCKED` or `N_A`, restricting the positive capability ratio $\rho$ directly.

### 5.3. Continuous Piecewise Power-Curve Damping

To penalize performance clustering at trivial lower tiers ($l \in \{1, 2\}$), the system maps user strictness $\zeta_{\text{score}} \in [0, 100]$ to a damping exponent $\gamma(\zeta_{\text{score}}) \in [1.00, 2.20]$ via continuous piecewise linear interpolation (where $\zeta_{\text{score}}$ is operationally bound to unified workflow strictness $\zeta_{\text{score}} = \zeta_{\text{lex}} = \zeta$):

$$\gamma(\zeta_{\text{score}}) = \begin{cases} 1.00, & \zeta_{\text{score}} \le 0 \\ 1.00 + \left(\frac{\zeta_{\text{score}}}{50}\right) \cdot 0.25, & 0 < \zeta_{\text{score}} \le 50 \\ 1.25 + \left(\frac{\zeta_{\text{score}} - 50}{35}\right) \cdot 0.45, & 50 < \zeta_{\text{score}} \le 85 \\ 1.70 + \left(\frac{\zeta_{\text{score}} - 85}{15}\right) \cdot 0.50, & 85 < \zeta_{\text{score}} \le 100 \\ 2.20, & \zeta_{\text{score}} > 100 \end{cases} \tag{18}$$

The final mapped score across the range $[S_{\min}, S_{\max}]$ is calculated as:

$$\text{Score}(\rho; \zeta_{\text{score}}) = \begin{cases} S_{\min} + \left( \rho^{\gamma(\zeta_{\text{score}})} \cdot \Pi_{\text{penalty}} \right) \cdot (S_{\max} - S_{\min}), & M > 0 \\ S_{\min}, & M \le 0 \end{cases} \tag{19}$$

*Mathematical Property 1 (Score Monotonicity and Lipschitz Stability):* Continuous power-curve damping is an architectural design choice formulated to eliminate the "cliff-edge failure" characteristic of discrete zero-trust gates (where a single missing token triggers a discontinuous score collapse). From an analytical standpoint, the scoring function exhibits two key mathematical properties for any calibrated exponent $\gamma \ge 1.0$ and penalty multiplier $\Pi_{\text{penalty}} \in (0, 1]$:
1. **Monotonicity:** $\frac{\partial \text{Score}}{\partial \rho} = \gamma \rho^{\gamma - 1} \Pi_{\text{penalty}} (S_{\max} - S_{\min}) \ge 0$ everywhere on $[0, 1]$. Validating an additional capability atom monotonically improves or maintains total score.
2. **Lipschitz Stability:** Because $\frac{\partial^2 \text{Score}}{\partial \rho^2} \ge 0$, the maximum rate of change is attained at the upper boundary $\rho = 1$, yielding the optimal Lipschitz constant $K_L = \gamma \Pi_{\text{penalty}} (S_{\max} - S_{\min})$. By the Mean Value Theorem, $|\text{Score}(\rho_1) - \text{Score}(\rho_2)| \le K_L |\rho_1 - \rho_2|$, ensuring that bounded evidence noise cannot trigger unbounded diagnostic volatility.

```
             POWERCURVE SCORING DAMPING
                         |
           +-------------+-------------+
           |                           |
           v                           v
  CAPABILITY RATIO (ρ)       ANTI-PATTERNS (π = -1)
  BARS Tiers 1-5             Multiplicative Malus:
  A = ∑ l · h_l              Π_penalty = ∏(1 - p_k)
  M = ∑ l · (t_l - d_l)      Max deduction = 40%
           |                           |
           +-------------+-------------+
                         |
                         v
              DAMPING: Score ∝ ρ^γ(ζ)
              γ(ζ) ∈ [1.00, 2.20]

```

### 5.4. Multi-Matrix Orthogonal Scoring Space, Polarity Mechanics, and Two-Tier Governance

While Equations (14)–(19) formulate the scoring kernel for an individual Behaviorally Anchored Rating Scale (BARS) matrix, Quorum's neurosymbolic evaluation engine is not bounded by a single evaluative lens. The platform implements a **Holistic Multi-Matrix Audit**, wherein an arbitrary set of process-, structural-, and domain-specific matrices are scheduled concurrently within the cognitive graph ($\mathcal{G}_{\text{DAG}}$) under Zero-Code Domain Extensibility.

#### 5.4.1. Two-Tier Scoring Hierarchy: Sovereign Kernel vs. Macro Governance

To preserve mathematical purity and prevent cross-phase architectural pollution, Quorum enforces a strict separation of concerns through a two-tier scoring hierarchy:

1. **Tier A: Sovereign Intra-Matrix Scoring Kernel:**
   Equation (19) represents the sovereign intra-matrix scoring kernel. It computes a pure mathematical evaluation bounded strictly by the evaluated matrix prompt block's scale extrema $[S_{\min}, S_{\max}]$. The kernel operates exclusively on atomic criteria within that single matrix, computing weighted capability ratio $\rho$ and intra-matrix anti-pattern falsification multiplier $\Pi_{\text{penalty}}$ under continuous strictness damping $\gamma(\zeta)$. The kernel returns an immutable scoring record containing the normalized score, per-level breakdown, and structured explainable AI (XAI) audit trace. The intra-matrix kernel does not access external workflow state, execute database lookups, or apply macro-level penalties.

2. **Tier B: Macro-Workflow Governance and Multi-Matrix Aggregation:**
   Multi-matrix scoring consolidation and workflow-level penalty governance are decoupled into the post-execution governance pipeline:
   * **Commensurate Normalization:** Each evaluated matrix block projects its raw score into a normalized $[0.0, 100.0]$ scale via linear min-max projection:
     $$\text{Normalized\_Score}_m = \left( \frac{S_m - S_{\min}^{(m)}}{S_{\max}^{(m)} - S_{\min}^{(m)}} \right) \times 100.0$$
   * **Macro-Workflow Penalty Governance:** The consolidated global score is calculated as the unweighted arithmetic mean of normalized matrix scores across all $D$ evaluated matrices, subjected to workflow-level deduction penalties:
     $$\text{average\_score} = \frac{1}{D} \sum_{d=1}^D \text{Normalized\_Score}_d \tag{20}$$
     $$\text{effective\_penalty} = \min(\text{total\_penalty}, P_{\max})$$
     $$\text{global\_score} = \text{round}\left( \max(0.0, \; \text{average\_score} \times (1.0 - \text{effective\_penalty})), \; 1 \right)$$
     where $P_{\max} = 0.40$ (40% maximum cumulative workflow deduction). Workflow penalties encompass three sovereign modalities: security prompt injection penalty ($P_{\text{security}}$), post-hoc rationalization penalty ($P_{\text{post\_hoc}}$), and behavioral passivity penalty ($P_{\text{passivity}}$).
   * **Observer Protocol for Behavioral Passivity:** Behavioral passivity detection is decoupled from intra-matrix scoring math. The passivity observer inspects aggregated matrix outputs. If an evaluation resolves to its mathematical floor ($S_{\min}$) with zero positive capability assertions verified above baseline, the protocol triggers a passivity flag. When observed, the macro-governance layer applies the configured passivity penalty ($P_{\text{passivity}}$) at Tier B aggregation.

#### 5.4.2. Holistic Multi-Matrix Audit in Orthogonal Vector Space ($\mathbf{\Psi}$)

Restricting AI evaluation to a single diagnostic dimension produces structural blind spots. If auditing is confined strictly to the final artifact ($\sigma_i = \text{ASSISTANT}$), fluent autoregressive prose can achieve high marks even if the human operator acted as a completely passive passenger. Conversely, analyzing only conversational interaction ($\sigma_i = \text{USER}$) risks an **Illusion of Control**, wherein concise, confident prompting yields an epistemically hollow, Rung 1 deliverable.

Quorum formalizes holistic evaluation as a $D$-dimensional orthogonal matrix vector $\mathcal{M} = (\mathcal{M}_1, \mathcal{M}_2, \dots, \mathcal{M}_D)$, where each matrix $\mathcal{M}_d$ interrogates discourse $\mathcal{D}$ from a distinct epistemic stance anchored to an XML-isolated speaker capsule ($\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$):

$$\mathbf{\Psi}(\mathcal{D}; \zeta) = \begin{bmatrix} \text{Score}_{\mathcal{M}_1}\left(\rho_1, \Pi_{\text{penalty}}^{(1)}; \zeta\right) \\ \text{Score}_{\mathcal{M}_2}\left(\rho_2, \Pi_{\text{penalty}}^{(2)}; \zeta\right) \\ \vdots \\ \text{Score}_{\mathcal{M}_D}\left(\rho_D, \Pi_{\text{penalty}}^{(D)}; \zeta\right) \end{bmatrix} \in \prod_{d=1}^D \left[ S_{\min}^{(d)}, S_{\max}^{(d)} \right] \tag{21}$$

In a comprehensive audit workflow, execution graph $\mathcal{G}_{\text{DAG}}$ partitions evaluation across three cross-validating epistemic layers executed concurrently via asynchronous coroutines within the same Kahn topological wave $\mathcal{W}_j$:

1. **Human Agency & Collaboration Matrix ($\mathcal{M}_{\text{HACM}}, \sigma_i = \text{USER}$):** Targets the `<user_payload>` capsule, evaluating cognitive steering responsibility, boundary definition, adversarial challenging of AI drafts, and iterative refinement.
2. **Epistemic & Causal Architecture Matrix ($\mathcal{M}_{\text{Causal}}, \sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$):** Evaluates the macro-topological proposition graph $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$ mined across the multi-document submission payload ($\mathcal{D}_{\text{dialogue}} \circ \mathcal{D}_{\text{deliverable}} \circ \mathcal{D}_{\text{reflection}}$). Under the Capsule-Partitioned Subgraph Invariant (Section 4.2.1), deliverable argument coherence, reachability ($r_{\text{LCC}}^{\text{deliv}}$), isolated claim ratio ($r_{\text{iso}}^{\text{deliv}}$), and multi-premise convergence ($r_{\text{conv}}^{\text{deliv}}$) are evaluated over the induced deliverable subgraph $\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$ (with supervisory dialogue inputs treated as exogenous boundary axioms $\mathcal{V}_{\text{axiom}}$), paired with the orthogonal Cross-Capsule Steering Coupling Ratio ($\kappa_{\text{steer}}$), all computed in 0 tokens under the Cumulative Guttman Invariant (paired with substantive Toulmin warrant criteria in $\mathcal{M}_{\text{Toulmin}}$ which strictly isolate `<ai_draft_context>` with $\sigma_i = \text{ASSISTANT}$, and interactive ATMS counterfactual stress testing).
3. **Domain Substance Matrix ($\mathcal{M}_{\text{Domain}}, \sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$):** Evaluates specialized task constraints—spanning legal claim management, strategic foresight, and statutory compliance—using the identical mathematical scoring kernel.

While the macro-governance layer computes a commensurate scalar average for high-level governance, the declarative presentation pipeline preserves vector $\mathbf{\Psi}(\mathcal{D}; \zeta)$ intact, exposing the **Agency-to-Outcome Divergence**:

$$\Delta_{\text{agency-outcome}} = \left\vert{} \hat{S}(\mathcal{M}_{\text{HACM}}) - \hat{S}(\mathcal{M}_{\text{outcome}}) \right\vert{} \tag{22}$$

where $\hat{S}(\cdot) \in [0, 1]$ represents the normalized matrix score. In multi-matrix audit workflows where $D > 2$ matrices are active, the substantive outcome term $\hat{S}(\mathcal{M}_{\text{outcome}})$ is formalized as the unweighted arithmetic mean across all active non-agency substantive/structural matrices:

$$\hat{S}(\mathcal{M}_{\text{outcome}}) = \frac{1}{D - 1} \sum_{d \neq \text{HACM}} \hat{S}(\mathcal{M}_d)$$

(specifically averaging the substantive deliverable evaluation matrices $\mathcal{M}_{\text{Toulmin}}, \mathcal{M}_{\text{Causal}}, \mathcal{M}_{\text{Transp}}, \text{ and } \mathcal{M}_{\text{Bloom}}$ in the empirical benchmark). In workflows configured with a dedicated Studio presentation profile, $\hat{S}(\mathcal{M}_{\text{outcome}})$ optionally evaluates targeted pairwise divergence against a specific designated target block $\hat{S}(\mathcal{M}_{\text{target}})$ (e.g. `variance_target_block`). An elevated divergence $\Delta_{\text{agency-outcome}}$ diagnoses either uncritical automation complacency (high outcome without human agency) or ineffective steering (active dialogue failing to materialize as structural deliverable quality).

#### 5.4.3. Matrix-Specific Polarity Mechanics and Classical Theoretical Grounding

Within every matrix $\mathcal{M}_d$, positive capability assertions ($\pi_i = +1$) and negative anti-pattern falsifiers ($\pi_i = -1$) enforce a **two-sided lexical proof burden** grounded in **contrastive pair enforcement** (acceptable demonstration vs. rejected distractor):

1. **Positive Capability Assertions ($\pi_i = +1$):**
   * *Epistemic Role:* Measures constructive cognitive and professional competence across hierarchical BARS levels $l \in \{1, \dots, 5\}$.
   * *Evidentiary Proof Burden:* The default state is unproven ($h_l = 0$). An assertion is accepted ($\omega(a_i) = \text{PASSED}$) only if the sensor extracts an exact verbatim quote $\mathcal{C}_i$ from target speaker $\sigma_i$ matching the positive anchor, avoiding the negative distractor, and passing all five deterministic physical validation gates ($\lambda_i = 1$).
   * *Mathematical Impact:* Accrues additively into weighted capability ratio $\rho = A / M$ (Equations 15–16) and is softened via piecewise power-curve damping $\rho^{\gamma(\zeta)}$ (Equation 18).

2. **Negative Anti-Pattern Assertions ($\pi_i = -1$, Inverse Polarity):**
   * *Epistemic Role:* Acts as a Popperian gatekeeper, actively searching for cognitive shortcuts, argumentation fallacies, uncritical delegation, and superficial fluency.
   * *Evidentiary Proof Burden (Defense Against Hallucinated Penalties):* The default state is clean performance ($\Pi_{\text{penalty}} = 1.0$). The LLM cannot penalize by stochastic estimation: deduction $p_k \in (0, 1)$ triggers only if the sensor extracts an exact verbatim citation passing all five physical validation gates ($\lambda_i = 1$) proving the violation occurred. If lexical grounding fails ($\lambda_i = 0$), the penalty is dropped.
   * *Mathematical Impact & Decoupled Inverse Badging:* Verified anti-patterns deduct from the matrix score multiplicatively via $\Pi_{\text{penalty}} = \max(1 - P_{\max}, \prod_{k=1}^{K_{\text{pen}}} (1 - p_k))$ (Equation 17), capped at $P_{\max} = 0.40$. Crucially, anti-pattern assertions do not award positive capability points ($A = 0$ pts). In the presentation and tabular export tiers, passing an anti-pattern displays as clean performance ($0\text{ pts}$, unviolated) rather than misleadingly awarding positive score points (which would falsely conflate the mere absence of error with positive competence), while verified violations are badged distinctly with dedicated numeric indicators.
   * *Atomic Export Invariant & Empirical Hit Distribution:* Tabular exports project evaluated atoms $1:1$ without synthetic record aggregation. Matrix summary tables format the empirical hit distribution ($k/N$ ratio) per BARS tier, while dynamic causal graph propositions are mapped transparently under an explicit causal reasoning module.

In the system evaluation design, assertions are anchored to classical theoretical literature across two mutually exclusive rubric tracks:

**Table 1:** Theoretical Grounding, BARS Competence Continuum, and Negative Falsification Rubrics Across Orthogonal Evaluative Stances.

| Matrix Category & Speaker ($\sigma_i$) | Rubric Track | Classical Theoretical Grounding | Positive Capability Assertions ($\pi_i = +1$, BARS Tiers $l \in \{1, \dots, 5\}$) | Negative Anti-Pattern Falsifiers ($\pi_i = -1$, Malus Multiplier $\Pi_{\text{penalty}}$) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Human Agency & Collaboration (HACM)**<br><br>$\sigma_i = \text{USER}$ | **Track A**<br>(Developmental) | **Sheridan & Verplank (1978)** (*Levels of Automation*),<br><br>**Parasuraman et al. (2000)**,<br><br>**Kahneman (2011)** (*System 1 vs. 2*),<br><br>**Buçinca et al. (2021)** (*Cognitive Forcing*) | **L1–L2:** Foundational task framing and contextual bounding.<br><br>**L3:** Explicit boundary constraints, persona assignment, and criteria setting.<br><br>**L4:** Active adversarial challenging of AI drafts and error correction.<br><br>**L5:** Metacognitive steering, hypothesis forcing, and sovereign synthesis direction. | **Automation Bias & Passive Delegation:**<br><br>• Unconstrained "do this for me" task abdication.<br><br>• Blind rubber-stamping of first-draft outputs.<br><br>• Relinquishing critical verification responsibility.<br><br>• Vacuous conversational prompts lacking steering content. |
| **2. Argumentative & Causal Structure (A-SCM & Toulmin Alignment)**<br><br>$\mathcal{M}_{\text{Toulmin}}: \sigma_i = \text{ASSISTANT}$<br>$\mathcal{M}_{\text{Causal}}: \sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track B**<br>(Error Radar) | **Pearl (2009)** / **Pearl & Mackenzie (2018)** (*Causal Hierarchy & Ladder of Causation*),<br><br>**Stephen Toulmin (1958)** (*Claim, Grounds, Warrant, Backing, Rebuttal*) | **Structural Graph Integration ($\mathcal{M}_{\text{Causal}}$, 0-Token Invariants):**<br>• **L1–L2:** Baseline non-empty graph ($|\mathcal{V}_{\text{claim}}| \ge 2$), directed acyclicity, component core ($r_{\text{LCC}} \ge 0.35$).<br>• **L3:** Core premise linking ($r_{\text{LCC}} \ge 0.50$), bounded isolated nodes ($r_{\text{iso}} \le 0.20$).<br>• **L4:** High reachability ($r_{\text{LCC}} \ge 0.70$) and convergent multi-premise synthesis ($r_{\text{conv}} \ge 0.05$).<br>• **L5:** Unified macro-reachability ($r_{\text{LCC}} \ge 0.85$) and deep interconnectedness ($r_{\text{iso}} \le 0.05$).<br><br>*(Note: Substantive Toulmin warrants [$\mathbf{W}_{XY}$] on the candidate deliverable [$\sigma_i = \text{ASSISTANT}$], confounder interventions [$U$], and counterfactual stress tests are evaluated through $\mathcal{M}_{\text{Toulmin}}$ and ATMS Algorithm 1).* | **Pseudo-Causality & Structural Collapse:**<br><br>• Conflating correlation with causation (bare trend listing).<br><br>• Orphan claims ($\mathcal{A}_{\text{orphan}}$) lacking evidentiary grounds or warrants ($\mathbf{W} = \emptyset$).<br><br>• Circular causal loops (`CYCLIC_DEPENDENCY_DETECTED`).<br><br>• Unqualified optimism omitting boundary exceptions (*Missing Rebuttal*). |
| **3. Critical Thinking & Epistemic Rigor**<br><br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track A & B**<br>(Hybrid) | **Bloom (1956)** / **Anderson & Krathwohl (2001)** (*Cognitive Taxonomy Revision*),<br><br>**Karl Popper (1959)** (*Empirical Falsifiability*) | **L1–L2 (Remember/Understand):** Nomenclature definition and baseline summarization.<br><br>**L3 (Apply/Analyze):** Deconstructing latent assumptions and identifying structural tensions.<br><br>**L4 (Evaluate):** Source critique, evidence weighting, and defining empirical falsification conditions.<br><br>**L5 (Create):** Synthesizing novel, empirically testable explanatory frameworks. | **Epistemic Immunization & Cognitive Biases:**<br><br>• Confirmation bias (discarding disconfirming evidence).<br><br>• Unfalsifiable tautologies and evasive non-committal prose.<br><br>• Substituting substantive depth with rhetorical buzzwords (*Jargon Load*). |
| **4. Domain & Task-Specific Substance**<br><br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track B**<br>(Substantive) | **Smith & Kendall (1963)** (*BARS Anchoring*) integrated with substantive domain theory (specifically: contract law, service recovery, or strategic foresight) | **L1–L2:** Addressing baseline factual parameters of the case or scenario.<br><br>**L3:** Proportionate response formulating standard operational remedies.<br><br>**L4:** Balancing legal/financial liability against stakeholder equity; root-cause remediation.<br><br>**L5:** Proactive systemic risk containment and strategic value creation. | **Substantive Professional Errors:**<br><br>• Defensive externalization or ignoring stakeholder grievances.<br><br>• Premature unhedged admission of legal/financial liability.<br><br>• Vacuous apologies lacking concrete operational action plans.<br><br>• Naive linear trend extrapolation presented as foresight. |

*Table 1 Note: Table 1 summarizes Bloom's cognitive domain into a 5-tier conceptual BARS continuum with L1–L2 grouped; in operational evaluation (Section 5.1, Table 3), $\mathcal{M}_{\text{Bloom}}$ is instantiated across all six discrete cognitive levels $L_1 \dots L_6$ with 5 atoms per tier, totaling 30 atoms.*

#### 5.4.4. Design-Time Human Curation and Empirical Scope Boundaries

The rigorous mapping above demonstrates why Quorum matrices are compiled through **Design-Time Human Curation** rather than unconstrained runtime LLM generation:

1. **Bounding Semantic Drift and the Entailment Gap:** As established in Section 2.1, general semantic entailment ($\mathcal{C}_i \models \tau_i$) over unrestricted text is fundamentally undecidable by purely computational means (Rice's Theorem). Pre-compiling closed BARS rubrics with explicit contrastive pairs converts open-ended generation into a bounded verification task, constraining the hypothesis space. Residual semantic ambiguity is systematically bounded by role-asymmetric Popperian falsification and isolated via causal graph reachability pruning (see Section 2.1).
2. **Psychometric Invariance and Regulatory Auditability:** Because evaluation matrices exist as versioned, immutable schema entities, every execution is scored against an identical Lipschitz-stable benchmark (Equation 19), guaranteeing longitudinal repeatability across evaluation cohorts.
3. **Classical Theories as Cognitive Compilers:** Domain architects need not invent evaluative dimensions ad-hoc in the evaluation design interface. Sheridan–Verplank, Toulmin, Pearl, Bloom / Anderson–Krathwohl, Popper, and Kahneman provide an established five-tier competence continuum ($\pi_i = +1$) and a canonical error taxonomy ($\pi_i = -1$). Domain experts map specialized terminology directly into these established structures, after which automated schema verification suites guarantee lexical anchorability and prevent overfitting.

```
      CLASSICAL THEORIES                 BARS MATRIX ARCHITECTURE
+----------------------------+       +----------------------------------+
| Bloom (Remember / Describe)| ----> | Tiers 1-2 (π = +1):              |
| Pearl Rung 1 (Association) |       | Baseline Recall & Association    |
+----------------------------+       +----------------------------------+
| Toulmin (Claim-Data-Warrant| ----> | Tier 3 (π = +1):                 |
| Sheridan-Verplank (Steer)  |       | Explicit Mechanism (W_XY)        |
+----------------------------+       +----------------------------------+
| Pearl Rung 2-3 (Intervene  | ----> | Tiers 4-5 (π = +1):              |
| & Counterfactual)          |       | Boundaries, Stress Tests & Risks |
+----------------------------+       +----------------------------------+
| Popper (Falsification)     | ----> | Anti-Patterns (π = -1):          |
| Kahneman (System 1 Bias)   |       | Passivity, Jargon & Fallacies    |
+----------------------------+       +----------------------------------+
```

*Empirical Scope Boundary and Prospective Cross-Domain Validation:* While the empirical evaluation in Section 8 examines a five-matrix audit configuration across two real-world human–AI interaction cases (the Remote Work policy reform case and the Strategic Foresight / Sitra megatrends case), Quorum's data-driven matrix engine is architecturally domain-agnostic. In ongoing research and prospective validation campaigns, this multi-matrix space ($\mathbf{\Psi}$) is systematically applied to enterprise contract review, regulatory compliance audits, and multi-agent software engineering workflows across diverse organizational cohorts and foundation model families.

---

## 6. Architectural Principles and Verified Mathematical Properties

*Epistemic Calibration and System Scope:* To preserve strict scientific integrity and avoid theoretical inflation, we explicitly partition the formal framework into two practical categories:
1. **Architectural Principles:** Structural design invariants inherited from established computer science (referential transparency, pure computational pipelines, and discrete topological DAG scheduling) that govern deterministic asynchronous orchestration.
2. **Mathematically Verified System Properties:** Analytical properties of our verification and scoring pipelines (lexical error suppression bounds, Lipschitz score stability, and topological reachability) that guarantee numerical and epistemic predictability.

### Architectural Principle 1: Confluent Neurosymbolic Wave Scheduling

**Architectural Principle 1 (Wave Confluence under Kahn Ordering and Pure Computations).** *Let $\mathcal{G}_{\text{DAG}} = (\mathcal{V}_{\text{cog}}, \mathcal{E}_{\text{dep}})$ be a finite directed acyclic graph partitioned into $J$ disjoint topological waves $\mathcal{W}_0, \mathcal{W}_1, \dots, \mathcal{W}_{J-1}$ via Kahn's partial ordering (Kahn, 1962). Let each node operator $\Phi_v: \prod_{u \in \text{Parents}(v)} \mathcal{O}_u \times \mathcal{S}_{\text{global}} \to \mathcal{O}_v$ be a pure compute function executing over immutable, validated typed records with zero shared memory side-effects. By the referential transparency of pure functions over acyclic directed graphs and Kahn partial ordering (establishing wave confluence analogously to the Church–Rosser theorem for confluent evaluation orders; Church & Rosser, 1936; and Kahn process networks; Kahn, 1974), any arbitrary asynchronous resolution order or coroutine scheduling permutation $\varpi \in \text{Perm}(\mathcal{W}_j)$ within concurrent execution groups converges deterministically to the identical unique wave state snapshot $\mathcal{O}_{\mathcal{W}_j}$, and the global system pipeline terminates at an invariant fixed-point state $\mathcal{S}^* = (\Phi_{\mathcal{W}_{J-1}} \circ \dots \circ \Phi_{\mathcal{W}_0})(\mathcal{S}_0)$.*

*Architectural Context & Contribution:* Confluence of pure functions over immutable inputs in acyclic topologies is a classic foundational result in theoretical computer science (Church & Rosser, 1936; Kahn, 1974). We do not claim wave confluence as a novel mathematical discovery. Rather, Quorum's real-world contribution is the **strict architectural enforcement of referential transparency within a distributed LLM runtime**:
1. Operators communicate exclusively via immutable, strongly typed record contracts.
2. Cognitive engines adhere to the Pure Compute Engine Law (100% computational pipelines with zero shared locks, event listeners, or mutable globals).
3. Concurrency throttling is cleanly decoupled into dynamic HTTP semaphore pools, preventing runtime deadlocks while guaranteeing bit-level deterministic state reproduction across re-executions.
4. State transitions across topological waves are persisted as an immutable event-sourced stream ($e_t \in \mathcal{E}_{\text{trace}}$). The global context state $\mathcal{S}_t$ is reconstituted purely through deterministic event projection $\mathcal{S}_{t+1} = \text{Project}(\mathcal{S}_t, e_t)$, completely eliminating in-place mutation of global state, enforcing typed record structures, and guaranteeing deterministic execution replay and verifiable audit trails under regulatory transparency standards (specifically EU AI Act Articles 12–15).

---

### Architectural Property 1: Decoupled Epistemic Error Suppression via Physical Grounding and Role Asymmetry

**Property 1 (Decoupled Epistemic Error Suppression and Score Inflation Bounds).** *Let an ensemble of $M$ frontier LLM evaluators—whether drawn from parallel sampling of a single model distribution ($\bar{\rho}_{\text{intra}} \approx 1$) or a heterogeneous multi-model committee ($\bar{\rho}_{\text{inter}} \ge \rho_{\min} > 0$) due to shared pretraining corpora (Common Crawl, Wikipedia)—exhibit non-zero pairwise error correlation $\text{Cov}(X_i, X_j) = \rho_{ij} > 0$. While democratic majority voting hits an asymptotic error floor governed by effective sample size $M_{\text{eff}} \le 1/\bar{\rho}$, Quorum decouples epistemic error suppression into two orthogonal frontiers: deterministic Physical Lexical Grounding ($\lambda \in \{0, 1\}$) at the atom level, and Role-Asymmetric Popperian Falsification ($\pi = -1$) at the matrix level. The atom-level false acceptance probability on a capability claim $a_i \in \mathcal{A}_{\text{rubric}}$ ($\pi_i = +1$) is strictly bounded by the sum of physical substring collision tolerances and stochastic semantic misattribution rates:*

$$P(\text{Atom False Accept}_i) \le P(H_{\text{fab}}) \cdot \epsilon_{\text{lexical}} + P(H_{\text{mis}}) \cdot \beta_{\text{sem}} \approx P(H_{\text{mis}}) \cdot \beta_{\text{sem}} \tag{23}$$

*where $H_{\text{fab}}$ denotes extrinsic citation fabrication ($\mathcal{C}_i \notin \mathcal{D}$), $H_{\text{mis}}$ denotes intrinsic semantic misattribution ($\mathcal{C}_i \in \mathcal{D} \land \mathcal{C}_i \not\models \tau_i$), $\epsilon_{\text{lexical}} \to 0$ is the combinatorial substring collision rate, and $\beta_{\text{sem}} = P(\text{Gate 4 Passes} \land \text{Bo3 Consensus} \mid H_{\text{mis}})$ is the stochastic Type II miss rate of the joint reasoning trace triangulation and ensemble voting gate. Furthermore, system-level score inflation resulting from residual semantic drift is bounded multiplicatively on the deterministic plug-in score evaluated at the expected capability ratio $\text{Score}(\mathbb{E}[\rho]; \zeta)$ and in stochastic score expectation $\mathbb{E}[\text{Score}(\rho; \zeta)]$ by the Popperian anti-pattern penalty multiplier $\Pi_{\text{penalty}}$:*

$$\text{Score}(\mathbb{E}[\rho]; \zeta) \le S_{\min} + \left( \left(\rho_{\text{clean}} + \rho_{\text{mis}} \cdot \beta_{\text{sem}}\right)^{\gamma(\zeta)} \cdot \Pi_{\text{penalty}} \right) \cdot (S_{\max} - S_{\min}) \tag{24a}$$

$$\mathbb{E}[\text{Score}(\rho; \zeta)] \le \text{Score}(\mathbb{E}[\rho]; \zeta) + \frac{1}{2}\gamma(\gamma - 1)\mu_\rho^{\gamma - 2}\text{Var}(\rho) \cdot \Pi_{\text{penalty}} (S_{\max} - S_{\min}) + \mathcal{O}\left(\mathbb{E}[(\rho - \mu_\rho)^3]\right) \tag{24b}$$

*Analytical Verification & Derivation:*

1. **Failure of Democratic Consensus under Correlated Priors (Epistemic Bias vs. Aleatoric Noise):** Let $X_1, \dots, X_M \in \{0, 1\}$ be binary error indicators for model evaluators on a deceptive prompt. Due to overlapping pretraining distributions and shared inductive biases, the average pairwise correlation across models is strictly non-zero: $\bar{\rho} \ge \rho_{\min} > 0$. The effective sample size of democratic ensembling is bounded asymptotically:

$$M_{\text{eff}} = \frac{M}{1 + (M-1)\bar{\rho}} \implies \lim_{M \to \infty} M_{\text{eff}} = \frac{1}{\bar{\rho}} < \infty \tag{25}$$

If the prompt triggers a shared pretraining attractor where individual error probability $p > 0.5$, democratic voting inverts: $P(\text{Consensus Error}) \to 1$ as $M \to \infty$. Thus, model ensembling alone cannot guarantee epistemic reliability.

*The Aleatoric vs. Epistemic Ensembling Duality:* We explicitly distinguish between **Aleatoric Decoding Noise** (stochastic token sampling jitter around decision thresholds under non-zero temperature, where $\rho_{\text{aleatoric}} < 1$) and **Epistemic Model Bias** (systematic conceptual hallucinations and pretraining blindspots, where $\bar{\rho}_{\text{epistemic}} \to 1$). While drawing multiple parallel samples from the *same* foundation model (single-model Best-of-3) successfully dampens aleatoric decoding variance, it exhibits $\bar{\rho}_{\text{intra}} \approx 1$ for systematic epistemic errors: if a model suffers from an inherent semantic blindspot ($p > 0.5$), voting repeatedly from the same model simply solidifies the error. For this fundamental reason, **Quorum never relies on LLM voting or generative self-consensus to guarantee epistemic truth**. Rather, epistemic integrity is guaranteed by non-generative, orthogonal verification: the deterministic physical lexical firewall ($\lambda \in \{0, 1\}$), role-asymmetric Popperian polarity ($\pi = -1$), and topological ATMS graph surgery (Algorithm 1). This theoretical bound is empirically corroborated in Ablation Configuration 2 (Section 8.5, Table 7), where disabling the lexical firewall under Best-of-3 voting permits a 20.7% chimera acceptance rate.

2. **Two-Tier Error Decomposition (Orthogonal Epistemic Dimensions):** An erroneous system acceptance occurs when a proposition $\tau_i$ is marked as valid despite lacking true evidentiary support in document $\mathcal{D}$. This error decomposes into two mutually exclusive and collectively exhaustive hypotheses:
* **Extrinsic Citation Fabrication ($H_{\text{fab}}$):** The extractor generates an invalid or spliced citation $\mathcal{C}_i \notin \mathcal{D}$ (Type I Hallucination / Chimera quote).
* **Intrinsic Semantic Misattribution ($H_{\text{mis}}$):** The extractor provides a verbatim authentic quote $\mathcal{C}_i \in \mathcal{D}$ from the authorized speaker, but the quote does not semantically entail proposition $\tau_i$ ($\mathcal{C}_i \not\models \tau_i$; Type II Non-Entailment).

By the Law of Total Probability:

$$P(\text{Atom False Accept}_i) = P(H_{\text{fab}}) \cdot P(\text{Accept} \mid H_{\text{fab}}) + P(H_{\text{mis}}) \cdot P(\text{Accept} \mid H_{\text{mis}}) \tag{26}$$

3. **Deterministic Physical Lexical Firewall ($\lambda \in \{0, 1\}$):** Regardless of LLM consensus or inter-model correlation $\bar{\rho}$, every extracted claim must satisfy the strict lexical grounding predicate:

$$\lambda_i = \mathbb{I}\left( \text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1 \right) \in \{0, 1\} \tag{27}$$

where $\mathcal{C}_i$ is the exact textual citation and $\mathcal{D}$ is the raw immutable source document evaluated through the five-gate deterministic verification cascade. For fabricated citations ($H_{\text{fab}}$), acceptance requires a random character collision across finite document length $|\mathcal{D}|$, yielding:

$$P(\text{Accept} \mid H_{\text{fab}}) = P(\lambda_i = 1 \mid H_{\text{fab}}) \le \epsilon_{\text{lexical}} \approx |\mathcal{D}| \cdot \left(\frac{1}{|\Sigma|}\right)^L \to 0$$

where $|\Sigma|$ is the alphabet size and $L$ is the minimum entropy string length ($L \ge 10$). Hence, physical fabrication is deterministically eradicated by physical string verification.

Conversely, for semantic misattributions ($H_{\text{mis}}$), the citation physically exists in the text ($\mathcal{C}_i \in \mathcal{D}$). Consequently, the deterministic string matcher unconditionally confirms physical existence:

$$P(\lambda_i = 1 \mid H_{\text{mis}}) = 1.0$$

The lexical firewall proves physical provenance, but remains mathematically agnostic to semantic entailment.

4. **Atom-Level Semantic Defense vs. Matrix-Level Popperian Multiplier:** To prevent semantic misattributions ($H_{\text{mis}}$) from corrupting evaluation, Quorum enforces defense across two distinct architectural tiers:
* *Atom-Level Semantic Verification ($\beta_{\text{sem}}$):* At the individual criterion level $a_i$ ($\pi_i = +1$), an authentic quotation $\mathcal{C}_i \in \mathcal{D}$ that fails to semantically entail $\tau_i$ is defended by: (i) Gate 4 Reasoning Trace Triangulation (asserting physical anchor existence, non-empty grounding, and absence of internal logical contradictions), (ii) explicit contrastive distractor rubrics (penalizing superficial mentions), and (iii) parallel Best-of-3 ensemble consensus voting ($k \ge 2$ of $3$). Formally:
  $$P(\text{Accept} \mid H_{\text{mis}}) = P(\lambda_i = 1 \mid H_{\text{mis}}) \cdot P(\text{Gate 4} \land \text{Bo3 Passes} \mid H_{\text{mis}}) = 1.0 \cdot \beta_{\text{sem}}$$
  Substituting into Equation (26) yields the atom-level bound in Equation (23): $P(\text{Atom False Accept}_i) \le P(H_{\text{fab}}) \cdot \epsilon_{\text{lexical}} + P(H_{\text{mis}}) \cdot \beta_{\text{sem}} \approx P(H_{\text{mis}}) \cdot \beta_{\text{sem}}$.
* *Matrix-Level Popperian Falsification ($\Pi_{\text{penalty}}$):* Negative anti-pattern criteria ($\pi_k = -1$) operate as non-additive matrix gatekeepers. They do not evaluate positive citations individually to flip $\omega(a_i)$, but rather search the document for global cognitive failure modes (specifically vacuous apologies, passive delegation, and jargon loading; Table 1). When verified ($\lambda_k = 1$), each anti-pattern applies a multiplicative deduction $p_k \in (0, 1)$ via $\Pi_{\text{penalty}} = \max(1 - P_{\max}, \prod_{k=1}^{K_{\text{pen}}} (1 - p_k))$ (Equation 17). Consequently, if an author achieves unearned capability points $\rho_{\text{mis}}$ through superficial verbatim phrasing that slips past $\beta_{\text{sem}}$, the presence of associated anti-patterns actively suppresses overall score inflation via Equation (24a), capping cumulative deductions at $P_{\max} = 40\%$.
* *Jensen's Inequality, Convex Power Damping, and Expectation Bounds:* In Section 5.3 (Mathematical Property 1), the damping transformation $g(\rho) = \rho^{\gamma(\zeta)}$ is proved to have a non-negative second derivative $\frac{\partial^2 g}{\partial \rho^2} = \gamma(\gamma - 1)\rho^{\gamma - 2} \ge 0$ on $\rho \in [0, 1]$ for all $\gamma(\zeta) \ge 1.0$, establishing that $g(\rho)$ is convex (and strictly convex whenever $\zeta > 0 \implies \gamma(\zeta) > 1.0$). By Jensen's Inequality, for any random capability ratio $R \in [0, 1]$ with $\mathbb{E}[R] \le \rho_{\text{clean}} + \rho_{\text{mis}}\beta_{\text{sem}}$, the expectation satisfies $\mathbb{E}[g(R)] \ge g(\mathbb{E}[R])$. Consequently, substituting $\mathbb{E}[R]$ into $g(\cdot)$ bounds the deterministic plug-in score evaluated at the expected ratio, $\text{Score}(\mathbb{E}[\rho]; \zeta)$ (Equation 24a). For the expectation of the stochastic score $\mathbb{E}[\text{Score}(\rho; \zeta)]$, the upper bound is formalized via the second-order Taylor expansion envelope established in Equation (24b), where $\mu_\rho = \mathbb{E}[\rho] \le \rho_{\text{clean}} + \rho_{\text{mis}}\beta_{\text{sem}}$. In Quorum's empirical production trials under Best-of-3 ensemble consensus, extraction variance is tightly suppressed ($\text{Var}(\rho) < 0.001$, mean Shannon entropy $\bar{H} \le 0.0455$), ensuring that the Jensen dispersion gap $\frac{1}{2}\gamma(\gamma-1)\mu_\rho^{\gamma-2}\text{Var}(\rho)$ is negligible ($< 0.08\%$ score points) and that the deterministic plug-in bound and the stochastic expectation tightly coincide.

*Theoretical Significance and Analytical Parameterization of $\beta_{\text{sem}}$:* Quorum rejects the naive fallacy of "deterministic semantic omniscience"—deterministic lexical matching cannot magically prove semantic entailment ($\mathcal{C}_i \models \tau_i$). Rather, Quorum cleanly decouples the problem: (i) eliminating unanchored and fabricated evidence ($P \le \epsilon_{\text{lexical}} \to 0$) via deterministic verification gates, while (ii) bounding residual semantic misattribution to the stochastic consensus error parameter $\beta_{\text{sem}} \in [0, 1]$ and damping matrix score inflation via $\Pi_{\text{penalty}}$. While unconstrained generation exhibits substantial error rates on adversarial benchmarks (Nie et al., 2020; Thorne et al., 2018), structured negative prompting over closed BARS rubrics suppresses the Type II miss rate $\beta_{\text{sem}}$ through multi-turn reasoning trace triangulation and contrastive pair enforcement. Empirically, expert calibration bounds this parameter to a tight low-single-digit point estimate $\hat{\beta}_{\text{sem}} = 2.50\%$ (95% Wilson CI $[0.44\%, 12.88\%]$; see Section 8.5.1, Table 7b). For parametric sensitivity analysis in Equation (24a), evaluating score behavior across operational regimes $\beta_{\text{sem}} \in [0.01, 0.05]$ demonstrates that score inflation is bounded to $<2.1\%$ under baseline damping; furthermore, downstream consequence propagation is structurally contained via topological A-SCM reachability pruning (Algorithm 1).

---

### Architectural Property 2: Discrete ATMS Reachability and Cascade Fault Isolation

**Property 2 (Warrant Independence and Cascade Fault Isolation).** *Let an Argumentative Discourse SCM be compiled into an explicit discrete argument DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{claim}}, \mathcal{E}_{\text{deps}})$, where explicit claims $\mathbf{V}$ and operational warrants $\mathbf{W}$ are grounded in text ($\lambda = 1$). Assume latent conversational enthymemes $U_{\text{enthymeme}}$ act as potential unstated confounders. If a discrete premise retraction $X \gets \text{RETRACTED}$ alters dependent claim validity via deterministic reachability $\text{Reach}(\mathcal{G}_{\text{pruned}}, X) \cap \{Y\} \neq \emptyset$, while the reverse perturbation leaves antecedent truth invariant $X \notin \text{Reach}(\mathcal{G}_{\text{pruned}}, Y)$, and the text provides an explicit physical warrant $\mathbf{W}_{XY}$, then the directed argumentative dependency $X \xrightarrow{\mathbf{W}_{XY}} Y$ is structurally sound, self-contained, and shielded from enthymemic confounding.*

*Topological Derivation & System Mechanics:*

1. **Discrete Graph Surgery via Dual-Engine Truth Maintenance:** Rather than attempting observational density estimation via statistical do-calculus, discourse graph surgery and truth maintenance are evaluated deterministically through decoupled dual-engine mechanics:
   * **Forward Wave Scheduling and Reachability:** Enforces Kahn topological wave execution under strict `CONJUNCTIVE_AND` precondition rules. Retracting an upstream premise ($X \gets \text{RETRACTED}$) or observing an antecedent precondition mismatch severs forward validity, deterministically cascading downstream reachability $\text{Reach}(\mathcal{G}_{\text{pruned}}, X)$ into `BLOCKED` or `N_A` states without LLM invocation.
   * **Backward Blame Attribution and Root Cause Isolation:** Operates on the mined argument graph by traversing inbound causal dependency edges via bounded breadth-first search. When downstream failures occur, the engine isolates upstream root causes ($\text{BlameParents}(X) = \emptyset$) from secondary cascade consequences ($\text{BlameParents}(Y) = \{ X \}$), preventing double-penalization.

2. **Topological Asymmetry and Reachability:** Let $\text{Reach}(\mathcal{G}, v)$ denote the set of all nodes reachable via directed paths from $v$. The invariant $X \notin \text{Reach}(\mathcal{G}_{\text{pruned}}, Y)$ proves that premise $X$ is topologically upstream from outcome $Y$:

$$(X \notin \text{Reach}(\mathcal{G}_{\text{pruned}}, Y)) \implies X \notin \text{Descendants}(Y) \tag{28}$$

No backward causal flow exists in the authored discourse. Concurrently, $Y \in \text{Reach}(\mathcal{G}_{\text{pruned}}, X)$ confirms that $Y$ is structurally downstream from $X$:

$$(Y \in \text{Reach}(\mathcal{G}_{\text{pruned}}, X)) \implies X \in \text{Ancestors}(Y) \tag{29}$$

3. **Enthymemic Confounder Isolation via Grounded Warrants:** Suppose an unstated assumption $U_{\text{enthymeme}}$ creates a spurious correlation $X \leftarrow U_{\text{enthymeme}} \to Y$ (a rhetorical leap where the author omitted mediating operational steps). Under the discrete premise retraction $X \gets \text{RETRACTED}$, the path through $X$ is severed. If the author omitted explicit warrants ($\mathbf{W}_{XY} = \emptyset$), the causal discovery engine detects that:

$$\text{BlameParents}(Y) = \{ X \} \implies \text{Status}(Y) \gets \text{BLOCKED} \tag{30}$$

and the audit flags an ungrounded argumentative leap (Rung 1).

Conversely, if the author explicitly stated and grounded the operational warrant $\mathbf{W}_{XY}$ ($\lambda(\mathbf{W}_{XY}) = 1$), the active transmission mechanism establishes an independent verifiable edge $X \xrightarrow{\mathbf{W}_{XY}} Y$. In discrete graph surgery, the warrant $\mathbf{W}_{XY}$ provides the deterministic transmission mechanism, shielding the claim from unstated enthymemes and confirming Rung 2/3 explanatory rigor.

4. **Boundary Remark (Intra-Instance Cascade Isolation vs. Baseline Scoring Invariance):** Property 2 governs *intra-instance structural soundness and cascade fault isolation* conditional on an individual compiled DAG realization, rather than asserting cross-run micro-topological isomorphism ($\mathcal{G}_1 \simeq \mathcal{G}_2$; see Section 4.2 Guarantee 7 and Section 8.6 Point 5). Baseline scoring evaluates unperturbed macro-topology in 0 tokens (Pillar 1), while Property 2 proves that counterfactual stress-testing and failure isolation deterministically uncover root causes without second-order stochastic prompting, with inter-run stability guaranteed at the macro-invariant level ($\bar{\kappa} = 0.9348$).

---

## 7. Full-Stack System Architecture and Error Suppression Pipeline

### 7.1. Multi-Tier Software Architecture

The Quorum platform operationalizes its theoretical invariants across a modular three-tier software architecture:

1. **Neurosymbolic Execution Runtime:** A strictly typed computation engine managing asynchronous Kahn wave scheduling, two-pass epistemic atomization, topological poset evaluation, backward fault attribution, pure argument causal cohesion evaluation, and constrained synthesis. An abstraction layer unifies context window management, prompt compilation, key-value cache isolation, and constrained decoding across diverse foundation model APIs (spanning Google Vertex AI/AI Studio, Anthropic Claude, OpenAI, and DeepSeek). State persistence integrates relational and document store repositories, verified by formal regression and guardrail test suites.

2. **Declarative Projection Tier:** To prevent client-side semantic inference or presentation drift, the system transforms evaluated matrix vectors $\mathbf{\Psi}(\mathcal{D}; \zeta)$, causal multigraphs $\mathcal{G}_{\text{LAG}}$, and explainable AI variance diagnostics into structured, declarative presentation payloads composed of typed, immutable visual blocks ("Dumb Painter" architectural pattern).

3. **Reactive Presentation & Governance Interface:** A cross-platform interactive client providing real-time execution monitoring, dynamic rubric compilation, audit report generation, and formal compliance tracking engineered in alignment with international regulatory transparency standards (specifically EU AI Act auditability requirements).

### 7.2. Four-Stage Cascade Suppression Pipeline and Two-Tier Verification

Unlike standard unconstrained LLM pipelines where intermediate hallucinations cascade unchecked, Quorum forces state through a four-stage suppression barrier:

$$\mathcal{S}_{\text{out}} = (\Phi_{\text{synth}} \circ \Phi_{\text{score}} \circ \Phi_{\text{fals}} \circ \Phi_{\text{TDA}} \circ \Phi_{\text{ingress}})(\mathcal{S}_{\text{in}} + \xi) \tag{31}$$

where $\xi$ represents stochastic semantic noise.

```
            Raw Stochastic Prompt
                      |
                      v
        +-----------------------------------------------+
        | Barrier 1: Ingress Layer                      |
        | - Strips prompt injection                     |
        | - Indexes agency (σ_i)                        |
        +-----------------------+-----------------------+
                                |
                                v
        +-----------------------------------------------+
        | Barrier 2: TDA Grounding                      |
        | - Null hypothesis (λ = 0)                     |
        | - Drops hallucinations                        |
        +-----------------------+-----------------------+
                                |
                                v
        +-----------------------------------------------+
        | Barrier 3: Asymmetric Falsification & Bo3     |
        | - Asymmetric Malus (π = -1)                   |
        | - Single-Model Bo3 Ensemble                   |
        | - Multiplicative Penalty (Π_penalty)          |
        +-----------------------+-----------------------+
                                |
                                v
        +-----------------------------------------------+
        | Barrier 4: Aggregation & Lipschitz Damp       |
        | - Commensurate Normalization                  |
        | - Macro Scoring Governance (P_max = 0.40)     |
        | - Power curve damping (γ(0)=1.0, γ(50)=1.25)  |
        +-----------------------+-----------------------+
                                |
                                v
                    Deterministic Final State

```

* **Barrier 1 (Ingress Sanitization & Capsule Isolation, $\Phi_{\text{ingress}}$):** Strips prompt injection payloads, applies Unicode Canonical Composition (NFC) while strictly confining whitespace collapsing to horizontal ASCII whitespace (`[ \t]+`) to preserve semantic and typographical markers, and fences speaker attribution indices $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$.
* **Barrier 2 (TDA Grounding & Poset Verification, $\Phi_{\text{TDA}}$):** Enforces the lexical null hypothesis ($\lambda_i = 0$ on verification failure) across the five-gate deterministic cascade and quarantines cyclic or unanchored dependencies.
* **Barrier 3 (Asymmetric Falsification & Best-of-3 Consensus, $\Phi_{\text{fals}}$):** Evaluates high-entropy propositions via a parallel Best-of-3 ensemble (majority voting with $k \ge 2$ of $3$) with Popperian null-hypothesis tie-breaking and multiplicative anti-pattern deductions ($\Pi_{\text{penalty}}$). While single-model Best-of-3 acts as an aleatoric filter suppressing stochastic token sampling jitter under native non-zero temperature, systematic pretraining blindspots are defended by deterministic physical lexical grounding ($\lambda_i \in \{0, 1\}$) and ATMS graph surgery (Algorithm 1).
* **Barrier 4 (Lipschitz Damping & Constrained Synthesis, $\Phi_{\text{score}} \circ \Phi_{\text{synth}}$):** Applies piecewise power-curve damping $\rho^{\gamma(\zeta)}$ (operating at linear baseline $\gamma(0) = 1.00$ in the empirical audit trials to capture unattenuated raw distributions, with calibrated enterprise default $\gamma(50) = 1.25$), enforces the 40% macro penalty cap ($P_{\max} = 0.40$), and restricts the terminal synthesis engine to rendering verified graph state without introducing unanchored claims.

To balance verification rigor with FinOps token economics, Quorum implements a **Two-Tier Verification Strategy**: live production DAG waves execute single-model Best-of-3 ensembles to suppress aleatoric decoding jitter within assigned model configurations, while computationally intensive cross-provider variance benchmarking and simultaneous heterogeneous multi-model ensembling (routing across Gemini, Claude, and OpenAI GPT-4o to expand effective sample size $M_{\text{eff}}$) are managed via dedicated offline evaluation and production roadmap protocols (see Section 10 for detailed FinOps token allocation and scaling trade-offs). Furthermore, to prevent cross-tenant memory leakage in distributed worker pools, bijective alias mappings $\mu$ are instantiated per execution job and serialized across worker boundaries via immutable alias manifest snapshots.

---

## 8. Empirical Validation: Paired Variance Audits and Reproducibility Benchmark

To evaluate the empirical stability, epistemic determinism, and inter-run reproducibility of the Quorum runtime, we conducted two controlled pairwise audit trials ($T = 2$ paired trials, comprising four independent full-scale workflow executions: Pair A and Pair B) evaluating genuine human–AI interaction and authorial AI-steering across two distinct real-world domains:
1. **Organizational Remote & Hybrid Work Policy Reform (Trial Pair A):** Evaluating human–AI interaction in an operational policy drafting task across two independent execution runs (Run A1 vs. Run A2), and
2. **Strategic Foresight on Megatrends / Sitra Case (Trial Pair B):** Evaluating human–AI interaction in an executive foresight assignment grounded in national innovation foresight themes across two independent execution runs (Run B1 vs. Run B2).

In both evaluation trials, the audited materials comprised the exact same three core authorial artifacts:
* **Multi-Turn Supervisory Dialogue:** The raw conversational interaction transcript between the human author and the generative AI assistant,
* **Generated Candidate Deliverable:** The final substantive policy memorandum or strategic foresight report produced through human–AI collaboration, and
* **Authorial Reflection Document:** The author's personal meta-cognitive reflection detailing intentionality, prompt engineering strategies, and critical evaluation of the AI's contributions.

In both cases, Quorum evaluated whether the author actively steered the AI or engaged in passive delegation, while validating factual provenance, Toulmin argumentation structure, and argument causal cohesion under unconstrained stochastic LLM sampling.

*Methodological Scope and Disclosure of Preliminary Sample Size:* In accordance with rigorous scientific reporting standards, we state explicitly as an empirical fact that the quantitative results presented herein are derived from **two paired end-to-end evaluation trials** ($T = 2$ paired trials, $N = 110$ common proposition atoms per trial, yielding $220$ atom-level paired observations across four complete executions: Trial Pair A on the Remote Work Policy Case [Run A1 vs. Run A2] and Trial Pair B on the Strategic Foresight / Sitra Case [Run B1 vs. Run B2]). While both trials demonstrate high statistical agreement ($\kappa > 0.90$) and zero pipeline failures, we emphasize that this represents a preliminary empirical verification of runtime stability; a broader, large-scale empirical campaign across diverse organizational cohorts, varied prompting regimes, and heterogeneous foundation model families (including Claude, OpenAI, and DeepSeek) is strictly required to establish general population-level bounds.

### 8.1. Experimental Protocol, Input Isolation, and Model Configuration

Each execution audited these three core authorial artifacts through the *Targeted AI Steering & Argumentation Audit* workflow (8 DAG steps, evaluating $N = 110$ propositional atoms across five orthogonal evaluative and structural matrices). 

To assess the system under realistic non-zero entropy conditions, the pipeline was bound to Google's frontier reasoning model deployed under the model identifier `gemini-3.8-flash` (Google DeepMind, 2026), configured with active thinking-budget allocations (2,048 tokens for balanced steps, 4,096 tokens for deep evaluators, and 8,192 tokens for reasoning steps) under default production sampling parameters:
* Unconstrained native sampling entropy: in modern reasoning architectures with active thinking budgets (including `gemini-3.8-flash`), explicit caller-specified temperature parameters are deprecated or constrained by the provider API; the pipeline executed strictly under Google's unconstrained native stochastic sampling policy (provider default $T \approx 1.0$, with zero greedy decoding or artificial temperature clamping),
* Dynamic cognitive thinking budgets: 0 tokens (fast), 2,048 tokens (balanced), 4,096 tokens (deep), 8,192 tokens (reasoning), and 2,048 tokens (synthesis),
* Dynamic token context windows: up to 65,536 tokens per step.

*Context-Bounded Sliding-Window Proposition Linking Parameters:* In accordance with Definition 3 (Section 4.2), proposition extraction and causal dependency linking ($\Phi_{\text{link}}$) were executed under the following standardized production configuration:
* Proposition extraction chunk packet size: $K_{\text{packet}} = 50$ paragraph blocks per extraction window,
* Sliding window width: $W_{\text{win}} = 4$ proposition chunks,
* Sliding window step overlap: $O_{\text{win}} = 2$ proposition chunks,
* Intra-window attention ceiling: $M_{\text{win}} = 20$ proposition atoms per LLM sliding window (oversized chunks exceeding $M_{\text{win}}$ were deterministically pre-subdivided prior to window generation),
* Maximum constituent claim ceiling: $N_{\max} = 100$ extracted claims represents a per-document baseline quota that flexibly reallocates within the combined aggregate ceiling $N_{\max}^{\text{payload}} = 300$ proposition nodes across the trial's multi-document payload ($\mathcal{D}_{\text{dialogue}}, \mathcal{D}_{\text{deliverable}}, \mathcal{D}_{\text{reflection}}$; Section 8.1). This dynamic quota allows extensive multi-turn conversational histories—such as $\mathcal{D}_{\text{dialogue}}$ in Pair B yielding 217 conversational steering premises—to expand beyond 100 nodes without truncation, provided the combined submission payload remains within $N_{\max}^{\text{payload}} \le 300$ ($28 + 217 + 7 = 252 \le 300$). Because the mining morphism $\alpha_{\text{mine}}$ and sliding-window dependency linker ($\Phi_{\text{link}}$) operate across the concatenated multi-document submission payload ($\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$), the mined graphs studied under $\mathcal{M}_{\text{Causal}}$ yield $|\mathcal{V}_{\text{claim}}| \in [141, 252]$ proposition nodes (Table 4)—exceeding the single-artifact baseline quota $N_{\max} = 100$. Furthermore, sliding windows bridging document transitions allow $\Phi_{\text{link}}$ to discover inter-document evidentiary dependencies (specifically supervisory user prompts grounding deliverable arguments), producing giant connected components that span across artifact boundaries ($|\mathcal{V}_{\text{LCC}}| = 178$ nodes / $71.20\%$ in Pair B).

*Deterministic Stride Whitespace Perturbation and Two-Tier KV-Cache Dynamics:* In cloud-hosted LLM APIs, automatic prefix caching (specifically Google AI Studio KV-cache reuse) operates over common prompt prefixes. In Quorum's Four-Layer Clean Stack, the static prompt prefix (Layers 1–3: system directives, theory context, and BARS rubrics comprising >800,000 characters) is intentionally cache-eligible to optimize throughput and cost, as reflected in our empirical telemetry (71.4% prompt cache hit rate across runs). However, to guarantee that the generative model does not retrieve cached attention keys for the evaluated discourse itself, all input documents (Layer 4) underwent deterministic stride whitespace perturbation across runs (alternating U+00A0 No-Break Space in Run 1 and U+2002 En Space in Run 2 across a 50-character stride, which alters Byte-Pair Encoding token boundaries and forces distinct SHA-256 cache hashes). Because Ingress Sanitization ($\Phi_{\text{ingress}}$) utilizes Unicode NFC rather than NFKC, these non-breaking whitespace codepoints were physically preserved in the prompt payload sent to the LLM, breaking Byte-Pair Encoding (BPE) token sequence identity at the document tail while preserving 100% semantic invariance. Consequently, the observed inter-run reliability ($\bar{\kappa} = 0.9348$) demonstrates Quorum's epistemic resilience not merely under unconstrained native stochastic sampling (default non-zero entropy), but under concurrent adversarial tokenization boundary perturbations.

### 8.2. Algorithmic Inter-Run Stability and Test–Retest Agreement Statistics

Algorithmic inter-run stability and test–retest consistency were evaluated using percent raw self-consistency ($P_o$), Cohen’s unweighted kappa ($\kappa_{\text{Cohen}}$; Cohen, 1960) with nominal asymptotic standard error (SE), cluster-bootstrapped standard error and percentile confidence intervals (CI; Field & Welsh, 2007; Cameron & Miller, 2015), Fleiss’ generalized multi-rater kappa ($\kappa_{\text{Fleiss}}$; Fleiss, 1971), and mean Shannon entropy ($\bar{H}$). Across both trials, binary atom-level decisions ($\omega(a_i) \in \{\text{PASSED}, \text{FAILED}\}$) were evaluated over $N = 110$ identical proposition atoms. For $R = 2$ binary runs per item, mean binary Shannon entropy ($\bar{H} = \frac{1}{N}\sum_{i=1}^N H_2(\hat{p}_i)$ in base-2 bits) reduces algebraically to the raw disagreement rate $1 - P_o$, providing independent non-redundant dispersion information when generalized to $R \ge 3$ replicate evaluations.

| Reliability Metric | Pair A: Remote Work Policy Case (Run A1 vs. Run A2) | Pair B: Strategic Foresight / Sitra Case (Run B1 vs. Run B2) | Combined Mean ($T = 2$) |
| :--- | :---: | :---: | :---: |
| **Execution Runs** | Run A1 / Run A2 | Run B1 / Run B2 | 4 complete runs |
| **Common Proposition Atoms ($N$)** | 110 | 110 | 220 atom observations |
| **Observed Raw Agreement ($P_o$)** | **95.45%** (105 / 110) | **98.18%** (108 / 110) | **96.82%** |
| **Expected Chance Agreement ($P_e$)** | 51.45% | 50.40% | 50.93% |
| **Cohen’s Kappa ($\kappa_{\text{Cohen}}$)** | **0.9064** | **0.9633** | **0.9348** |
| **Naive Asymptotic SE (Fleiss)** | 0.0409 | 0.0257 | 0.0241 |
| **Naive Asymptotic 95% CI** | $[0.8262, 0.9866]$ | $[0.9130, 1.0000]$ | $[0.8875, 0.9821]$ |
| **Cluster-Bootstrapped SE ($\text{SE}_{\text{cluster}}$)** | **0.0469** | **0.0284** | **0.0275** |
| **Cluster-Bootstrapped 95% CI** | $[0.8212, 1.0000]$ | $[0.8946, 1.0000]$ | $[0.8784, 0.9868]$ |
| **SE Inflation Factor ($\text{Deff}^{1/2}$)** | 1.15× | 1.10× | 1.14× |
| **Fleiss’ Kappa ($\kappa_{\text{Fleiss}}$)** | 0.9063 | 0.9633 | 0.9348 |
| **Landis & Koch (1977) Classification** | *Almost Perfect Agreement* | *Almost Perfect Agreement* | *Almost Perfect Agreement* |
| **Measurement Construct** | Test–Retest Precision | Test–Retest Precision | *Stochastic Self-Consistency* |
| **Mean Shannon Entropy ($\bar{H}^\dagger$)** | 0.0455 | 0.0182 | 0.0318 |
| **Marginal Decision Bias** | $-0.0273$ | $-0.0182$ | **$-0.0227$** |
| **Dead Letter Queue (DLQ) / Crashes** | 0 / 110 (0.0%) | 0 / 110 (0.0%) | **0 / 220 (0.0%)** |

**Table 2:** Statistical reliability, inter-run agreement, and entropy metrics across two independent paired empirical evaluation trials (Pair A: Remote & Hybrid Work Policy; Pair B: Strategic Foresight / Sitra) under unconstrained native stochastic frontier inference. Marginal decision bias $d_{\text{bias}} = (n_{\text{PASS}}^{(R_2)} - n_{\text{PASS}}^{(R_1)}) / N$ reflects net directional retest shift ($-2.27\%$ combined). To account for intra-cluster correlation across batched sensor payloads, cluster-bootstrapped standard errors and percentile confidence intervals were estimated across $K = 10$ step clusters ($B = 10,000$ iterations), confirming stability ($\kappa \ge 0.8784$) well above the *Almost Perfect Agreement* threshold. For $R = 2$ binary replicates, mean binary Shannon entropy algebraically equals the raw disagreement rate ($\bar{H} \equiv 1 - P_o = 0.0318$); see Appendix A.1 for full mathematical derivations and variance proofs.

Both independent pairwise trials yielded Cohen's $\kappa > 0.90$ (Cohen, 1960; Fleiss, 1971), landing firmly within the highest empirical reliability tier (*Almost Perfect Agreement*, $\kappa \ge 0.81$; Landis & Koch, 1977) under both nominal asymptotic formulas and cluster-robust bootstrap bounds ($[0.8784, 0.9868]$). Furthermore, stratifying reliability strictly by rubric polarity confirms that even when isolating positive capability criteria requiring physical citation extraction ($N_{\text{pos}} = 57$), reproducibility remains well within the highest Landis & Koch tier with pooled mean $\bar{\kappa}_{\text{pos}} = 0.8558$ ($\kappa_{\text{pos}}^{(A)} = 0.8326, \kappa_{\text{pos}}^{(B)} = 0.8790 > 0.81$; see Appendix A.2). We emphasize the foundational psychometric distinction between **algorithmic test–retest stability** (intra-system self-consistency across stochastic inference passes on identical documents) and **external construct validity** (concordance with human expert consensus). While human annotators and domain experts frequently exhibit substantial inter-rater variance on complex qualitative discourse analysis ($0.60 \le \kappa \le 0.80$; Artstein & Poesio, 2008; Landis & Koch, 1977) due to subjective ambiguity, Quorum's observed stability ($\bar{\kappa} = 0.9348$) does not imply superior cognitive judgment over human experts. Rather, it demonstrates that the neurosymbolic architecture successfully suppresses the stochastic token volatility inherent in unconstrained autoregressive generation (native non-zero sampling entropy), guaranteeing repeatable execution trajectories over identical source documents.

### 8.3. Granular Matrix and Rubric Agreement Breakdown

To verify that stability is preserved uniformly across diverse cognitive dimensions rather than concentrated in trivial baseline assertions, agreement was stratified across the five evaluated rubric matrices and five normalized difficulty quintiles (0–100% scale).

| Evaluative Matrix / Rubric Module | Matrix Notation | Scale | Atoms | Pair A (Remote Work Case) | Pair B (Strategic Foresight / Sitra Case) | Combined Consistency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Toulmin Argumentation Model** | $\mathcal{M}_{\text{Toulmin}}$ | 1–5 | 25 | 100.0% (25/25) | 100.0% (25/25) | **100.0% (50/50)** |
| **Argument Causal Cohesion (A-SCM)** | $\mathcal{M}_{\text{Causal}}$ | 1–5 | 5 | 100.0% (5/5) | 100.0% (5/5) | **100.0% (10/10)** |
| **Transparency & Explainability** | $\mathcal{M}_{\text{Transp}}$ | 1–5 | 25 | 88.0% (22/25) | 100.0% (25/25) | **94.0% (47/50)** |
| **AI Steering & Agency (HACM)** | $\mathcal{M}_{\text{HACM}}$ | 1–5 | 25 | 100.0% (25/25) | 96.0% (24/25) | **98.0% (49/50)** |
| **Cognitive Depth (Bloom Taxonomy)** | $\mathcal{M}_{\text{Bloom}}$ | 1–6 | 30 | 93.3% (28/30) | 96.7% (29/30) | **95.0% (57/60)** |
| **Total / Global** | — | — | **110** | **95.45%** | **98.18%** | **96.82% (213/220)** |

**Table 3:** Rubric-stratified consistency breakdown across matrices for Pair A (Remote Work Policy Case) and Pair B (Strategic Foresight / Sitra Case). Toulmin argumentation and pure topological causal cohesion achieved 100% deterministic reproducibility across all runs. *Note on $\mathcal{M}_{\text{Causal}}$:* The 5 evaluated atoms represent the five ordinal benchmark tiers ($L_1 \dots L_5$) of the Cumulative Guttman BARS scale computed from topological graph invariants, rather than individual graph edges.

Stratifying atom consistency by normalized difficulty reveals balanced epistemic resilience across both baseline and mastery levels:
* **Top Mastery / Critical Rigor (81–100%):** 97.6% consistency (41 / 42 evaluations concordant; Pair A: 21/21, Pair B: 20/21).
* **High Standard (61–80%):** 97.6% consistency (41 / 42 concordant; Pair A: 20/21, Pair B: 21/21).
* **Mid Standard (41–60%):** 95.2% consistency (40 / 42 concordant; Pair A: 19/21, Pair B: 21/21).
* **Low Standard (21–40%):** 97.6% consistency (41 / 42 concordant; Pair A: 20/21, Pair B: 21/21).
* **Baseline Viable (0–20%):** 96.2% consistency (50 / 52 concordant; Pair A: 25/26, Pair B: 25/26).

*Empirical Graph Topology Dynamics and Cross-Case Macro-Guttman Stability:* To verify that the 100% agreement observed on the 5 causal cohesion atoms ($\mathcal{M}_{\text{Causal}}$) reflects genuine structural stability rather than an artifact of coarse aggregation, we audited the physical proposition graph telemetry ($\mathcal{G}_{\text{LAG}}$) across two distinct empirical evaluation cases: (1) the operational Remote & Hybrid Work Policy case (Pair A) and (2) the dense Strategic Foresight / Sitra megatrend case (Pair B):

| Empirical Evaluation Case & Trial Pair | Global Nodes ($|\mathcal{V}|$) | Global Edges ($|\mathcal{E}|$) | Global $r_{\text{iso}}$ | Global $r_{\text{LCC}}$ | Deliverable Nodes ($|\mathcal{V}_{\text{deliv}}|$) | Deliverable Isolated ($r_{\text{iso}}^{\text{deliv}}$) | Deliverable LCC ($r_{\text{LCC}}^{\text{deliv}}$) | Steering Coupling ($\kappa_{\text{steer}}$) | BARS Levels Passed | BARS Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Remote Work Policy Case (R1)** | 141 | 40 | 52.48% (74/141) | 38.30% (54/141) | 22 | 50.00% (11/22) | 40.91% (9/22) | 27.27% (3/11) | Level 1, Level 2 | 1.8 / 5.0 |
| **Remote Work Policy Case (R2)** | 147 | 45 | 52.38% (77/147) | 39.46% (58/147) | 23 | 47.83% (11/23) | 43.48% (10/23) | 27.27% (3/11) | Level 1, Level 2 | 1.8 / 5.0 |
| **Remote Work Pairwise Delta ($\Delta$)** | +4.26% | +12.50% | **-0.10%** | **+1.16%** | +4.55% | **-2.17%** | **+2.57%** | 0.00% (Identical) | 100% Concordant | 0.0 (Identical) |
| **Strategic Foresight / Sitra Case (R1)** | 252 | 140 | 26.59% (67/252) | 68.65% (173/252) | 28 | 28.57% (8/28) | 64.29% (18/28) | 37.50% (3/8) | Level 1, Level 2 | 1.8 / 5.0 |
| **Strategic Foresight / Sitra Case (R2)** | 250 | 142 | 23.60% (59/250) | 71.20% (178/250) | 29 | 27.59% (8/29) | 65.52% (19/29) | 37.50% (3/8) | Level 1, Level 2 | 1.8 / 5.0 |
| **Strategic Foresight Pairwise Delta ($\Delta$)** | -0.79% | +1.43% | **-2.99%** | **+2.55%** | +3.57% | **-0.98%** | **+1.23%** | 0.00% (Identical) | 100% Concordant | 0.0 (Identical) |

**Table 4:** Empirical proposition graph topology dynamics and cross-case macro-Guttman stability across evaluation cases (Pair A: Remote Work Policy; Pair B: Strategic Foresight / Sitra), reporting both global unpartitioned graph metrics and induced deliverable subgraph metrics ($\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$). In both cases, macro-topological invariants remain stable within tight deltas across stochastic runs, and directed acyclicity is preserved ($0\text{ cycles}$).

*(Quiescent Baseline State of Algorithm 1 and Interaction with Final Matrix Scores):* Across all four baseline evaluation runs (Runs A1, A2, B1, B2), the proposition graphs were strictly acyclic ($\text{Directed Cycles} = 0$) and all extracted claims satisfied initial lexical verification. Consequently, during baseline scoring, Algorithm 1 remained in its quiescent baseline state ($|\text{Cascade}| = 0, |RC| = 0, d_{\max} = 0$) as formalized in Section 4.2. Baseline BARS scores evaluate unperturbed macro-topological invariants in 0 tokens, while Algorithm 1 acts as a decoupled diagnostic operator for interactive counterfactual surgery and root-cause isolation.

*(Controlled Counterfactual Premise Retraction & ATMS Stress-Testing Telemetry):* To empirically validate Algorithm 1 in active operation and verify Property 2 on real-world proposition graphs, we executed a systematic counterfactual perturbation benchmark across the four compiled graphs. For each compiled graph instance, we simulated the discrete retraction ($X \gets \text{RETRACTED}$) of the primary root causal premise ($X_{\text{root}} = \arg\max_{v: \text{InDegree}(v)=0} \text{OutDegree}(v)$) under both strict precondition scheduling (`CONJUNCTIVE_AND`) and corroborative warrant redundancy (`DISJUNCTIVE_OR`):

| Evaluation Case & Run | Intervened Root Premise ($X_{\text{root}}$) | Mode | Cascade Size ($|\text{Cascade}|$) | % of Graph Blocked | Max Cascade Depth ($d_{\max}$) | Root Causes ($|RC|$) | Execution Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Remote Work Policy (R1)** | Primary Policy Foundation ($X_1, \text{deg}^+=4$) | `CONJUNCTIVE_AND`<br>`DISJUNCTIVE_OR` | 11<br>4 | 7.80%<br>2.84% | 3<br>2 | 1 ({$X_1$})<br>1 ({$X_1$}) | 0.42 ms<br>0.38 ms |
| **Remote Work Policy (R2)** | Primary Policy Foundation ($X_1, \text{deg}^+=5$) | `CONJUNCTIVE_AND`<br>`DISJUNCTIVE_OR` | 13<br>5 | 8.84%<br>3.40% | 3<br>2 | 1 ({$X_1$})<br>1 ({$X_1$}) | 0.45 ms<br>0.41 ms |
| **Strategic Foresight (R1)** | Megatrend Driver Premise ($X_1, \text{deg}^+=6$) | `CONJUNCTIVE_AND`<br>`DISJUNCTIVE_OR` | 24<br>9 | 9.52%<br>3.57% | 5<br>3 | 1 ({$X_1$})<br>1 ({$X_1$}) | 0.88 ms<br>0.81 ms |
| **Strategic Foresight (R2)** | Megatrend Driver Premise ($X_1, \text{deg}^+=6$) | `CONJUNCTIVE_AND`<br>`DISJUNCTIVE_OR` | 22<br>8 | 8.80%<br>3.20% | 5<br>3 | 1 ({$X_1$})<br>1 ({$X_1$}) | 0.85 ms<br>0.79 ms |

**Table 4b:** Controlled counterfactual premise retraction and ATMS graph surgery telemetry across evaluation cases under systematic root premise invalidation ($X_{\text{root}} \gets \text{RETRACTED}$). In all trials, Algorithm 1 executed deterministically in $<1.0\text{ ms}$ (0 additional LLM tokens), correctly isolating the root cause ($|RC| = 1$), while corroborative warrant redundancy (`DISJUNCTIVE_OR`) dampened cascade propagation by an average of $62.5\%$ relative to strict `CONJUNCTIVE_AND`.

This cross-case comparison demonstrates four key neurosymbolic properties:
1. *Discourse-Sensitive Topological Discrimination:* The structural graph miner does not produce uniform, synthetic artifacts. The dense Strategic Foresight deliverable (Pair B) yielded twice the edge density ($0.56$ vs. $0.29$ edges/node), nearly double the largest connected component reachability ($70.0\%$ vs. $38.9\%$), and significantly higher raw connectivity ($75\%$ vs. $48\%$) compared to the operational Remote Work policy memorandum (Pair A), proving that topological extraction faithfully mirrors the underlying rhetorical density and argument integration of the evaluated discourse.
2. *Cross-Run Topological Invariant Invariance:* Within each respective evaluation case, topological invariants exhibited remarkable stability across runs. In the Remote Work policy case (Pair A), the isolated concept ratio was within **0.10%** across runs ($52.48\%$ vs. $52.38\%$), with largest component reachability within **1.16%** ($38.30\%$ vs. $39.46\%$) and identical raw cohesion of $0.48$. In the Strategic Foresight / Sitra case (Pair B), raw cohesion remained stable within $0.03$ ($0.7341$ vs. $0.7640$) and component reachability within $2.55\%$ ($68.65\%$ vs. $71.20\%$). In both cases, directed acyclicity was preserved ($0\text{ cycles}$).
3. *Topological Sensitivity vs. Ordinal Quantization in $\mathcal{M}_{\text{Causal}}$ and Capsule-Partitioned Invariant Recovery:* While Table 3 documents 100.0% (10/10) inter-run agreement across the five discrete BARS ordinal tiers of $\mathcal{M}_{\text{Causal}}$, we transparently note the effect of ordinal step-function quantization. In our audited baseline runs, the Level 3 unanchored claim ceiling was set conservatively to $r_{\text{iso}} \le 20.0\%$ ($r^{\max}_{L3} = 0.20$). Under concatenated ingress pooling ($\mathcal{D}_{\text{dialogue}} \circ \mathcal{D}_{\text{deliverable}} \circ \mathcal{D}_{\text{reflection}}$), Pair B exhibited global $r_{\text{iso}} \in [23.6\%, 26.6\%]$ primarily due to non-deductive conversational framing turns and reflective self-assessments, failing Level 3 despite possessing nearly double the edge density and a 28-percentage-point higher structural cohesion than Pair A. Consequently, the unpartitioned discrete Guttman progression halted at Level 2 for both cases ($1.80 / 5.0$). 

   While our initial exploratory sensitivity calibration relaxed the unanchored ceiling to $r^{\max}_{L3} = 0.30$ ($r^{\min}_{\text{LCC}, L3} = 0.50$) to allow Strategic Foresight to pass Level 3 ($2.60 / 5.0$), as formalized in Section 4.2.1 (Item 5), relaxing thresholds masks the underlying construct validity confound rather than solving it. In live empirical verification under the formal **Capsule-Partitioned Subgraph Invariant** over the induced deliverable subgraph $\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$ (treating incoming dialogue directives as exogenous boundary axioms $\mathcal{V}_{\text{axiom}}$), the physical extraction cleanly partitions the 252 total graph nodes in Pair B Run 1 into 28 substantive deliverable nodes ($\mathcal{D}_{\text{deliverable}}$), 217 conversational steering premises ($\mathcal{D}_{\text{dialogue}}$), and 7 authorial reflection assertions ($\mathcal{D}_{\text{reflection}}$). This purges 59 non-deliverable isolated nodes, collapsing isolated concept counts in the deliverable from 67 down to exactly 8 authentic isolated assertions ($r_{\text{iso}}^{\text{deliv}} = 8 / 28 = 28.57\%$, logical cohesion score $0.7143$). Under the conservative baseline ceiling ($r^{\max}_{L3} = 0.20$), the deliverable is robustly grounded at Level 2 ($1.80 / 5.0$), while under calibrated scoping tolerance ($r^{\max}_{L3} = 0.30$) accommodating foundational framing premises ($\mathcal{V}_{\text{scoping}}$) and sliding-window attention horizon bounds ($\Delta_{\max} \le 20$ atoms across distant chapters; Section 4.2 Definition 3 and Section 10), it deterministically achieves Level 3 ($2.60 / 5.0$) on substantive merit rather than conversational dilution. Concurrently, reporting the 0-token Cross-Capsule Steering Coupling Ratio ($\kappa_{\text{steer}} = 37.50\%$) provides a direct, unconfounded measure of human–AI collaboration without contaminating substantive deliverable topology.
4. *Empirical Validation of Corroborative Warrant Redundancy (Property 2):* The counterfactual stress-testing telemetry in Table 4b empirically corroborates Property 2. Under strict `CONJUNCTIVE_AND` scheduling, invalidating a single root premise cascades widely, blocking up to $9.52\%$ of downstream claims ($24$ claims in Sitra R1). In contrast, under `DISJUNCTIVE_OR`, alternative grounded warrants preserve validity, dampening the cascade to $3.57\%$ ($9$ claims)—a $62.5\%$ reduction in secondary failure propagation. This quantitatively demonstrates the fault-isolation capability of multi-warrant Toulmin argumentation in compiled enterprise text.
5. *Deterministic Continuous Strictness Scaling & Sensitivity Re-Projection:* Across all runs in both cases under the baseline production run configuration, satisfying Tiers $L_1$ and $L_2$ accumulated an achieved weighted point sum of $A = 1 \cdot 1 + 1 \cdot 2 = 3.0$ out of a theoretical maximum $M = \sum_{j=1}^5 j = 15.0$, yielding an uncalibrated point ratio of $\rho = 3.0 / 15.0 = 0.20$. Because the audited production workflow executed at baseline strictness $\zeta = 0$ (default uncalibrated strictness level), the unified scoring engine applied a linear scaling exponent $\gamma(0) = 1.00$ ($\text{Score} = 1.0 + (0.20)^{1.00} \cdot (5.0 - 1.0) = 1.80 / 5.0$).

To evaluate system behavior across continuous strictness regimes, we re-project the frozen execution traces across the full parameter space $\zeta \in [0, 100]$ in 0 additional tokens:

| Strictness Level ($\zeta$) | Regime Label | Damping Exponent ($\gamma$) | Evaluated BARS Score ($1–5$) | Normalized Score (%) | Kappa ($\bar{\kappa}$) Invariance |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$\zeta = 0$** | Free / Linear Baseline (Audited Runs) | $\gamma = 1.0000$ | **1.80 / 5.0** | 20.0% | **0.9348** (Invariant) |
| **$\zeta = 50$** | Normal Balanced Damping | $\gamma = 1.2500$ | **1.53 / 5.0** | 13.4% | **0.9348** (Invariant) |
| **$\zeta = 70$** | Calibrated Production Default | $\gamma = 1.5071$ | **1.35 / 5.0** | 8.8% | **0.9348** (Invariant) |
| **$\zeta = 85$** | Strict Governance | $\gamma = 1.7000$ | **1.26 / 5.0** | 6.5% | **0.9348** (Invariant) |
| **$\zeta = 100$** | Absolute Zero-Trust | $\gamma = 2.2000$ | **1.12 / 5.0** | 2.9% | **0.9348** (Invariant) |

**Table 5:** Deterministic continuous strictness scaling and sensitivity re-projection across the full parameter space $\zeta \in [0, 100]$ in 0 additional tokens.

*Dual Proof of Inter-Run Kappa Invariance across Strictness Regimes:* The test–retest reliability metric $\bar{\kappa} = 0.9348$ remains 100% invariant across strictness levels $\zeta \in [0, 100]$ due to two mathematically rigorous mechanisms:
1. *Downstream Metric Invariance ($\zeta_{\text{score}}$):* At the evaluative aggregation tier, the continuous piecewise power-curve damping transformation $\rho^{\gamma(\zeta_{\text{score}})}$ is strictly monotonic on the weighted capability ratio $\rho \in [0, 1]$ (Equation 18). It modulates score conservatism and terminal BARS ratings without altering the discrete upstream proposition truth assignments $\omega(a_i) \in \{\text{PASSED}, \text{FAILED}\}$.
2. *Upstream Evidentiary Invariance ($\zeta_{\text{lex}}$):* At the lexical verification tier (Equation 6), while Gate 5 permits approximate edit-distance matching, stemming, and longest-common-substring safety nets when $\zeta_{\text{lex}} < 100$, an automated post-hoc audit of all 54 verified positive citations extracted across Trial Pairs A and B reveals that **100% of candidate citations achieved Tier 1 exact normalized substring containment** ($\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1$). Because zero citations relied on fuzzy fallback, morphological stemming, or coverage thresholds, re-evaluating the deterministic lexical verification cascade across the entire parameter space $\zeta_{\text{lex}} \in \{0, 50, 70, 85, 100\}$ rejects zero citations. Consequently, the discrete proposition assignment vector $\boldsymbol{\omega}(\zeta)$ and Cohen's kappa $\bar{\kappa}(\zeta) = 0.9348$ remain identically invariant across both downstream score damping and upstream lexical verification (see Appendix A.2 for the complete census of all 59 extracted physical citations and exact $2 \times 2$ contingency matrices).

This dual result mathematically and empirically proves that continuous strictness modifies metric conservatism without perturbing underlying evidentiary classification stability.

### 8.4. Root Cause Decomposition of Evaluation Disagreements

Across both trials (220 paired atom evaluations), exactly **7 disagreement instances** occurred (Pair A: 5, Pair B: 2), representing an overall disagreement rate of $3.18\%$. Deterministic root cause triage categorized each disagreement into one of four mutually exclusive failure classes:

| Disagreement Root Cause Class | Operational Mechanism | Pair A (Remote Work) | Pair B (Strategic Foresight / Sitra) | Combined Total | Proportion (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Retrieval Gap (Citation Variance)** | Stochastic beam decoding in one run failed to isolate a continuous verbatim text span matching the BARS rubric, triggering the deterministic lexical null hypothesis ($\lambda_i = 0$).* | 4 | 2 | **6** | **85.7%** |
| **Reasoning Gap (Threshold Margin)** | Both runs extracted valid citation anchors ($\lambda_i = 1$), but model reasoning traces diverged on whether the cited evidence satisfied strict rubric criteria ($\tau_{\text{val}, i}^{(R_1)} = 1 \neq \tau_{\text{val}, i}^{(R_2)} = 0$). | 1 | 0 | **1** | **14.3%** |
| **Contextual Override** | External policy or manual override discrepancies. | 0 | 0 | **0** | **0.0%** |
| **Technical / DLQ Error** | Schema serialization failure, token overflow, or runtime crash. | 0 | 0 | **0** | **0.0%** |
| **Total** | — | **5** | **2** | **7** | **100.0%** |

**Table 6:** Root cause taxonomy of evaluation disagreements across the Remote Work Policy (Pair A) and Strategic Foresight / Sitra (Pair B) trials. Over 85% of variance stems from stochastic citation extraction under unconstrained native sampling entropy, which is safely quarantined by the closed-world lexical null hypothesis ($\lambda = 0$) rather than silently hallucinated. *(Polarity Note on Anti-Pattern Criteria: For negative anti-pattern criteria [$\pi_i = -1$], citation extraction variance operates in the inverse direction: passing requires the absence of grounded violation citations [$\lambda_i = 0$]. In Pair A, 1 of the 4 retrieval-gap disagreements represents an anti-pattern citation extracted in Run A2 but missed in Run A1, transitioning the atom from clean PASSED in A1 to violated FAILED in A2; see Appendix A.2).*

*Macro Score Drift and Qualitative Form-to-Content Disparity:* On the macro level ($0–100$ normalized score space), the Mean Absolute Delta (MAD) across all matrix blocks was $3.99$ points in Pair A (Remote Work Policy Case) and $3.05$ points in Pair B (Strategic Foresight / Sitra Case), with zero waterfall sequence disruptions across the DAG execution waves. Concurrently, qualitative examination of the supervisory dialogue across both empirical audits documented a pronounced *Form-to-Content Disparity*: while the human operators formulated concise prompts devoid of clichés (mechanical phrase load $0.00 / 2.0$), cognitive steering authenticity remained low ($1.47–1.52 / 3.0$), indicating routine delegation where the AI's initial associative draft was accepted without counterfactual testing or boundary constraints. The Human Agency & Collaboration Matrix ($\mathcal{M}_{\text{HACM}}$) exposed this divergence across both cases, demonstrating that surface conciseness does not guarantee substantive analytical rigor.

### 8.5. Component Ablation Study across 220 Atom Evaluations

To rigorously disentangle the marginal contributions of each constituent defense mechanism within the Quorum runtime, we evaluated a component ablation study across five experimental configurations. To maintain mathematical and methodological consistency, all five configurations were evaluated across the identical 220 proposition atom frames ($N = 220$ across the Pair A Remote Work Policy case and Pair B Strategic Foresight / Sitra case, 110 common proposition atoms per trial) via a dedicated offline benchmark evaluation harness. Methodologically, Configuration 1 establishes the neurosymbolic benchmark baseline on standardized homogeneous proposition frames ($52.7\%$ pass rate, $116 / 220$ atoms, $\kappa = 0.9453$, $P_o = 97.27\%$), which is reconciled with the $57.7\%$ pass rate ($127 / 220$ atoms, pooled $\bar{\kappa} = 0.9348$) of the physical production pipeline in Tables 2–6 (see Appendix A.3). Configuration 2 isolates the marginal effect of the lexical verification firewall by accepting raw propositional claims without substring rejection under a standardized in-silico benchmark stress test (auditing candidate citations for chimera artifacts under 19.7% candidate attack pressure across 29 candidate chimera citations empirically harvested from unconstrained exploratory decodes of frontier models during prompt development [21 synthetic fabrications and 8 paraphrased retrieval gaps], $\zeta = 100$). Configuration 3 isolates the effect of ensemble voting ($k=1$ single-pass inference) while evaluating resilience against simulated transient API drops ($0.9\%$ injected drop rate). Configurations 4 (unconstrained prompt without null hypothesis) and 5 (monolithic step-level evaluation) evaluate prompt structure alterations; in Configuration 5, criterion omissions ($8.6\%$) and unanchored chimera citations ($19.1\%$) are audited via exact lexical matching of free-form generated text against the source deliverables:

1. **Configuration 1 (Full Quorum Architecture):** The complete neurosymbolic runtime comprising parallel Best-of-3 ensemble voting ($k=3$), multi-gate physical lexical firewall verification, proposition-level epistemic atomization, and Popperian null hypothesis enforcement ($\lambda_i = 0$ upon citation absence).
2. **Configuration 2 (Quorum without Lexical Firewall):** Best-of-3 ensemble consensus retained ($k=3$), but with the lexical verification firewall disabled—accepting raw propositional claims without deterministic substring anchoring, while auditing for unanchored chimera citations via exact lexical matching.
3. **Configuration 3 (Quorum Single-Pass):** Full multi-gate lexical firewall and null hypothesis rules active, but executed as a single-pass inference ($k=1$), disabling parallel Best-of-3 ensemble majority voting to assess vulnerability to aleatoric decision jitter and transient upstream API drops.
4. **Configuration 4 (Atom-level Unconstrained LLM-as-a-Judge):** Single-pass atom-level evaluation ($k=1$) without lexical firewall anchoring or Popperian null hypothesis constraints, modeling standard atomized prompt-based grading under unconstrained native entropy.
5. **Configuration 5 (Monolithic Step-Level LLM-as-a-Judge):** A single monolithic prompt evaluating all step criteria simultaneously without propositional atomization or lexical grounding, modeling the standard vanilla LLM-as-a-judge paradigm and attention degradation (*lost-in-the-middle*).

| Experimental Configuration | Evaluated Atoms ($N$) | Observed Agreement ($P_o$) [Live Consistency] | Cohen’s Kappa ($\kappa$) [Live Consistency] | 95% Confidence Interval (CI) | Injected Stress Test: Chimera Interception Rate (%)* [19.7% Offline Attack Pressure] | Pass Rate (%) [Benchmark] | Injected Stress Test: DLQ Fault Rate (%)* [0.9% Offline Fault Drops] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Full Quorum (Bo3 + Lexical Firewall)** | 220 | 97.27% | 0.9453 | [0.9022, 0.9885] (Cluster: [0.8776, 0.9920]) | 0.0% | 52.7% | 0.0% |
| **2. Quorum without Lexical Firewall** | 220 | 85.91% | 0.6931 | [0.5929, 0.7932] (Cluster: [0.5801, 0.7988]) | 20.7% | 63.6% | 0.0% |
| **3. Quorum Single-Pass (k=1 + Lexical Firewall)** | 220 | 85.00% | 0.7058 | [0.6133, 0.7984] (Cluster: [0.5895, 0.8109]) | 0.0% | 46.4% | 0.9%* |
| **4. Atom-level Unconstrained LLM-as-a-Judge** | 220 | 63.18% | 0.2146 | [0.0786, 0.3505] (Cluster: [0.0381, 0.3805]) | 19.6% | 62.7% | 0.0% |
| **5. Monolithic Step-Level LLM-as-a-Judge** | 220 | 65.00% | 0.3000 | [0.1739, 0.4261] (Cluster: [0.1343, 0.4635]) | 19.1% | 50.0% | 8.6% |

**Table 7:** Component ablation benchmark study across 220 proposition atom evaluations ($N = 220$) evaluating the marginal contributions of the multi-gate lexical firewall, Best-of-3 ensemble consensus, atomic proposition decomposition, and Popperian falsification against monolithic vanilla LLM-as-a-judge baselines under the standardized offline benchmark harness. While observed agreement ($P_o$) and Cohen's kappa ($\kappa$) quantify live decision reproducibility across stochastic model decodes, injected stress tests evaluate mechanistic defense capacity under an offline harness deliberately injecting 29 candidate chimera citations (19.7% candidate attack pressure) and 2 simulated API drops (0.9% fault pressure). In live physical production runs, all extracted citations (59/59) satisfied Tier 1 exact substring containment (0.0% live chimera rate) and zero DLQ errors occurred. Cluster-adjusted 95% CIs are estimated via hierarchical two-stage cluster bootstrap ($K = 10, B = 2,000$); see Appendix A.1 for bootstrap proofs and Appendix A.3 for ontological pass rate reconciliation.

The comparative data in Table 7 establishes four decisive architectural findings:

* **Elimination of Chimera Quotations via Lexical Anchoring:** Disabling the lexical firewall under the standardized benchmark harness (Configuration 2) precipitates a sharp deterioration in evidentiary integrity, yielding a **20.7% chimera quotation acceptance rate** ($29 / 140$) among passed atoms when evaluating the 19.7% candidate attack pressure. Under unanchored generation, frontier models produce synthetic, approximate, or outright fabricated verbatim citations that do not exist in the source deliverable. When the firewall is bypassed, these 29 injected chimera candidates in the diagnostic harness pool are unconditionally accepted, artificially inflating the benchmark pass rate by **$+10.9$ percentage points** (from $52.7\%$ in Configuration 1 to $63.6\%$ in Configuration 2). In contrast, across all live physical production runs (Appendix A.2), 100% of candidate citations ($59/59$) satisfied Tier 1 exact substring containment ($0.0\%$ live chimera rate). Enforcing the deterministic multi-gate lexical firewall (Configuration 1) completely intercepts these candidates ($0.0\%$ chimera rate, achieving $\text{Specificity}_{\text{lex}} = 1.000$), mathematically proving that Popperian null hypothesis falsification ($\lambda_i = 0$) is essential for high-stakes discourse auditing.
* **Precision–Recall Trade-Off of the Lexical Firewall and Chimera Dissection:** While the lexical firewall achieves perfect physical specificity ($\text{Specificity}_{\text{lex}} = 1.000$, driving citation fabrication error to $\epsilon_{\text{lexical}} \to 0$ and eliminating all 29 chimera citations), enforcing strict normalized substring matching ($\lambda_i = 1$) introduces a non-trivial **Sensitivity (Recall) cost**. In classical diagnostic classification, unanchored rejections decompose into two distinct evidentiary classes: (i) *True Negatives ($TN_{\text{chimera}}$)*, where the author lacked the underlying competency and the unconstrained model hallucinated evidence; and (ii) *False Negatives ($FN_{\text{chimera}}$)*, where the author genuinely demonstrated the target competence in the source deliverable, but the generative sensor committed a *Retrieval Gap*—paraphrasing the text, condensing disparate clauses, or introducing minor syntactic alterations that failed Tier 1 exact substring containment. A blinded forensic audit of the 29 firewall-rejected chimera claims in Configuration 2 categorized $21 / 29$ ($72.41\%$) as True Negatives (successfully intercepting fabricated assertions, specifically non-existent quantitative SLA metrics or unstated legal risk frameworks) and $8 / 29$ ($27.59\%$) as False Negatives (valid authorial reasoning penalized strictly by verbatim quote extraction failure). This $27.59\%$ extraction recall penalty directly explains the baseline pass rate reduction from $63.6\%$ to $52.7\%$ in Table 7 and corroborates the finding in Table 6, where $85.7\%$ ($6/7$) of stochastic inter-run disagreements originated from Retrieval Gaps rather than reasoning divergence. Quorum resolves this Pareto trade-off by strictly prioritizing evidentiary integrity: in high-stakes compliance and executive auditing, admitting zero fabricated evidence ($\text{Spec} = 1.000$) is paramount, while extraction recall is systematically recovered in production through multi-turn iterative re-prompting and bounded morphological stem-sequence verification ($\zeta_{\text{lex}} < 100$).
* **Empirical Sensitivity of Gate 5 Multi-Tier Verification across Strictness Regimes:** To empirically validate Gate 5's multi-tier approximate matching cascade and evaluate its ability to recover valid authorial citations without leaking fabrications, we evaluated the offline diagnostic pool of 29 candidate chimera citations (21 synthetic hallucinations and 8 paraphrased retrieval gaps) across the full lexical strictness spectrum $\zeta_{\text{lex}} \in \{100, 85, 50, 30, 0\}$:

| Strictness ($\zeta_{\text{lex}}$) | Lexical Multiplier | Nominal Threshold ($\tau_{\text{tier}}$) | Recovered Retrieval Gaps (TP / 8) | Leaked Fabrications (FP / 21) | Lexical Specificity ($\text{Spec}_{\text{lex}}$) | Extraction Recall ($\text{Sens}_{\text{gap}}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\zeta = 100$** | $1.00$ | $100.0\%$ (Exact Only) | $0 / 8$ ($0.0\%$) | **$0 / 21$ ($0.0\%$)** | **$1.000$** | $0.0\%$ |
| **$\zeta = 85$** | $1.02$ | $76.5\%$ | $3 / 8$ ($37.5\%$) | **$0 / 21$ ($0.0\%$)** | **$1.000$** | $37.5\%$ |
| **$\zeta = 50$** | $1.00$ | $75.0\%$ | $5 / 8$ ($62.5\%$) | **$0 / 21$ ($0.0\%$)** | **$1.000$** | $62.5\%$ |
| **$\zeta = 30$** | $0.90$ | $67.5\%$ | $6 / 8$ ($75.0\%$) | **$0 / 21$ ($0.0\%$)** | **$1.000$** | $75.0\%$ |
| **$\zeta = 0$** | $0.80$ | $60.0\%$ | $7 / 8$ ($87.5\%$) | **$0 / 21$ ($0.0\%$)** | **$1.000$** | $87.5\%$ |

Across the entire continuous parameter space down to $\zeta = 0$, **zero fabrications leak through** ($0 / 21$ False Positives, preserving $\text{Specificity}_{\text{lex}} = 1.000$). Because fabricated citations assert non-existent concepts whose stems are entirely absent from the source document, their morphological content stem alignment fails and their contiguous LCS remains far below the $70\%$ safety net. Concurrently, extraction recall on valid authorial citations with minor inflectional or punctuation variance increases from $0.0\%$ at $\zeta = 100$ to $87.5\%$ ($7 / 8$ True Positives recovered) at $\zeta = 0$ via Stage 3 morphological stem-sequence verification. The single unrecovered citation represents an extensive, non-contiguous semantic paraphrase that is correctly rejected by contiguity invariants. This sensitivity profile empirically validates Gate 5's multi-tier design, proving that calibrated lexical strictness recovers legitimate authorial reasoning while maintaining an impenetrable firewall against hallucinated evidence.
* **Aleatoric Noise and Fault Mitigation via Best-of-3 Consensus:** Transitioning from single-pass inference ($k=1$, Configuration 3) to parallel Best-of-3 majority consensus ($k=3$, Configuration 1) elevates Cohen's kappa from $\kappa = 0.7058$ to $\kappa = 0.9453$ ($+0.2395$ kappa gain in the benchmark harness; and $\bar{\kappa} = 0.9348$ in physical production trials), shifting system reliability from substantial agreement into the highest *Almost Perfect Agreement* tier ($\kappa \ge 0.81$). Relative to the unconstrained atom-level baseline ($\kappa = 0.2146$, Configuration 4), Full Quorum achieves an overall $+0.7307$ kappa elevation. Beyond filtering stochastic decoding jitter near rubric decision boundaries, Best-of-3 provides critical fault tolerance against transient upstream API failures: under simulated transient provider rate-limit and connection drops (modeling in-silico $0.9\%$ drop pressure), Configuration 3 produces a **0.9% Dead Letter Queue (DLQ) rate** ($2 / 220$), whereas the Best-of-3 consensus absorber seamlessly masks isolated single-call drops, maintaining a pristine **0.0% DLQ error rate**. We explicitly note that in live physical deployment, parallel $k=3$ dispatching induces $3\times$ higher instantaneous burst concurrency than native $k=1$, necessitating centralized token-bucket rate smoothing and concurrency management, whereas in physical production audits (Table 6) zero DLQ errors occurred under either case.
* **Attention Integrity via Propositional Atomization:** Monolithic step-level evaluation (Configuration 5) demonstrates catastrophic attention degradation across long context windows: **8.6% of evaluation criteria are completely omitted or dropped** from unstructured LLM responses due to lost-in-the-middle phenomena. Observed agreement collapses to $65.00\%$ ($\kappa = 0.3000$). Decomposing complex qualitative rubrics into discrete, independent propositional atoms (Linked Atom Graph 6-tuple) with explicit Boolean evaluation guarantees complete evaluative coverage and eradicates attention dropouts.
* **Failure of Unconstrained Prompting Baselines:** The atom-level unconstrained configuration (Configuration 4, $k=1$, no firewall) achieves the poorest overall reliability ($\kappa = 0.2146$, $P_o = 63.18\%$), confirming that natural-language prompt instructions alone, absent neurosymbolic grounding and consensus voting, fail to establish reproducible evaluative state in stochastic language models.

### 8.5.1. Pilot External Construct Validity and Human Calibration Audit

While the empirical trials in Section 8.1–8.4 demonstrate high algorithmic test–retest reproducibility ($\bar{\kappa} = 0.9348$) across independent stochastic sampling runs, high reliability in psychometric measurement is a necessary but insufficient condition for construct validity. An automated evaluator can execute with perfect deterministic consistency while embedding systematic inductive biases or hallucinated alignments.

To empirically evaluate external construct validity against human expert ground truth ($\kappa_{\text{human-Quorum}}$) and calibrate the system's semantic error envelope, we conducted a blinded, stratified pilot calibration audit across $N = 70$ discrete proposition criteria evaluations drawn from Trial Pairs A and B. The audit was conducted by an independent expert evaluator with domain expertise in executive management auditing and Toulmin argument analysis, who inspected the source deliverables and conversational histories blind to automated model scores.

The pilot calibration audit evaluated two stratified sample cohorts:
1. **Passed Capability Criteria Cohort ($N = 40$):** Randomly sampled positive capability criteria evaluated as $\omega(a_i) = \text{PASSED}$ ($\lambda_i = 1 \land \tau_{\text{val}, i} = 1$). The human expert independently verified whether the source citation $\mathcal{C}_i$ genuinely entailed the target BARS hypothesis $\tau_i$ ($\mathcal{C}_i \models \tau_i$). Out of 40 passed atoms, 39 were confirmed as True Positives ($TP = 39$), and exactly 1 was categorized as a Type I Semantic Misattribution ($FP = 1$, where a verbatim quotation describing operational schedule adjustments was incorrectly credited with fulfilling a strategic change-management criterion). This bounds the empirical semantic misattribution error rate to $\hat{\beta}_{\text{sem}} = 1 / 40 = 2.50\%$ (95% Wilson score CI $[0.44\%, 12.88\%]$), establishing an empirical Positive Predictive Value of $\text{PPV} = 97.50\%$ (95% Wilson CI $[87.12\%, 99.56\%]$).
2. **Failed Capability Criteria Cohort ($N = 30$):** Randomly sampled positive capability criteria evaluated as $\omega(a_i) = \text{FAILED}$ ($\lambda_i = 0 \lor \tau_{\text{val}, i} = 0$), stratified across BARS Levels 1–5. The human expert performed an exhaustive manual search across the source deliverables to determine whether the author genuinely exhibited the target competency. Out of 30 failed atoms, 26 were Confirmed True Negatives ($TN = 26, \text{NPV} = 86.67\%$, 95% Wilson CI $[70.32\%, 94.69\%]$), confirming genuine authorial omission of required structures (such as formal Bayesian uncertainty bounds, complete Toulmin rebuttals, or counterfactual falsification tests). Exactly 4 atoms were categorized as False Negatives, establishing an empirical row-conditional False Omission Rate of $\widehat{\text{FOR}} = 4 / 30 = 13.33\%$ (95% Wilson CI $[5.31\%, 29.68\%]$), decomposing into:
   * **Firewall Rejection Penalty ($\text{FOR}_{\text{rejection}}$):** $1 / 30$ ($3.33\%$) where the candidate quote demonstrated the competency but was rejected by Tier 1 exact substring containment due to minor grammatical case inflection in Finnish, and
   * **Sensor Retrieval Omission ($\text{FOR}_{\text{omission}}$):** $3 / 30$ ($10.00\%$) where the generative sensor failed to extract an existing quotation distributed across diffuse multi-sentence context.

| Automated Quorum Decision | Human Expert: True Positive (Ground Truth Valid) | Human Expert: True Negative (Ground Truth Invalid) | Total Audited | Empirical Rate & 95% Wilson CI |
| :--- | :---: | :---: | :---: | :---: |
| **Quorum PASSED ($\omega = \text{PASSED}$)** | **39** (True Positive, $TP$) | **1** (Type I Semantic Misattribution, $FP$) | $N = 40$ | $\text{PPV} = 97.50\%$ ($[87.12\%, 99.56\%]$)<br>$\hat{\beta}_{\text{sem}} = 2.50\%$ ($[0.44\%, 12.88\%]$) |
| **Quorum FAILED ($\omega = \text{FAILED}$)** | **4** (Type II False Negative, $FN$)* | **26** (True Negative, $TN$) | $N = 30$ | $\widehat{\text{FOR}} = 13.33\%$ ($[5.31\%, 29.68\%]$)<br>$\text{NPV} = 86.67\%$ ($[70.32\%, 94.69\%]$) |

**Table 7b:** Confusion matrix of the pilot human expert calibration audit ($N = 70$ stratified criteria evaluations across Trial Pairs A and B). Over 86% of negative capability evaluations reflect genuine authorial omission rather than citation rejection, bounding the row-conditional False Omission Rate on rejected capability atoms to $\widehat{\text{FOR}} = 13.33\%$ ($\text{NPV} = 86.67\%$). Inverting these row-conditional pilot sample estimates via Bayes' theorem under the physical production positive pass rate ($q = 29 / 114 = 25.44\%$) projects a population-level False Negative Rate of $\text{FNR}_{\text{pop}} = 28.61\%$ (with population specificity $\text{Spec}_{\text{pop}} = 99.02\%$), which closely matches the $27.59\%$ extraction recall penalty (retrieval gap) independently measured in the offline ablation benchmark (Section 8.5).  
*\*Note on False Omissions: $1/30$ ($3.33\%$) resulted from lexical firewall rejection of minor inflectional variance ($\text{FOR}_{\text{rejection}}$); $3/30$ ($10.00\%$) resulted from sensor retrieval omissions on diffuse multi-sentence context ($\text{FOR}_{\text{omission}}$).*

These pilot findings establish that Quorum's high test–retest reliability ($\bar{\kappa} = 0.9348$) is coupled with high empirical precision ($\text{PPV} = 97.50\%$) and physical specificity ($\text{Specificity}_{\text{lex}} = 1.000$). Architecturally, this decomposition clarifies the division of labor across Quorum's recovery mechanisms: while Gate 5 morphological stem-sequence verification ($\zeta_{\text{lex}} < 100$) directly resolves inflectional firewall rejections ($\text{FOR}_{\text{rejection}} = 3.33\%$), diffuse multi-sentence extraction omissions ($\text{FOR}_{\text{omission}} = 10.00\%$) are addressed at the sensor layer through multi-turn iterative re-prompting within Gate 2's $1,000$-character contiguous span ceiling. However, because this pilot calibration was conducted by a single senior expert auditor over an initial sample ($N = 70$), population-level construct validity and multi-rater inter-annotator concordance ($\kappa_{\text{human-Quorum}}$) require expansion in our planned multi-rater study ($N \ge 110$ across multiple independent raters; Section 8.6 Point 4).

### 8.6. Methodological Threats to Validity and Empirical Generalization Agenda

While the observed inter-run reliability ($\bar{\kappa} = 0.9348$) provides strong empirical support for Quorum’s neurosymbolic architecture, we emphasize the specific limitations of this preliminary validation:
1. **Limited Sample Cardinality and Multi-Level Clustering Hierarchy:** The quantitative results reflect exactly two pairwise evaluation trials ($T = 2$ paired trials, 4 full workflow runs). In evaluating statistical confidence, clustering operates at two distinct hierarchical tiers: (i) *Meso-level clustering* (the step/batch level, where multiple criteria share the same LLM decoding context and document sections) is explicitly modeled and bounded via the non-parametric cluster bootstrap ($K = 10$ step clusters across trials, yielding $\text{SE}_{\text{cluster}} = 0.0275$ and 95% CI $[0.8784, 0.9868]$ in Table 2). In the offline component ablation benchmark (Table 7), where error rates are stratified uniformly across steps, meso-level clustering is evaluated via two-stage hierarchical resampling (Stage 1: step cluster resampling; Stage 2: within-cluster atom resampling) with a conservative truncation floor ($\text{SE} \ge \text{SE}_{\text{nominal}}$) to prevent single-stage bootstrap contraction artifacts under small $K$ and $\rho_{\text{ICC}} \le 0$. (ii) Conversely, *macro-level clustering* (the document level, $T = 2$) cannot be non-parametrically bootstrapped because resampling from an empirical support of only two document clusters yields a mathematically degenerate distribution of only three discrete configurations (Cameron & Miller, 2015). Consequently, while inter-trial independence is preserved via variance pooling, establishing population-level asymptotic bounds over the document universe strictly requires expanding to $T \ge 20$ paired trials across diverse organizational, legal, and technical document genres.
2. **Single Foundation Model Family:** The trials were executed using Google Gemini 3.8 Flash (`gemini-3.8-flash`; Google DeepMind, 2026). While the Two-Tier Verification Architecture is provider-agnostic, cross-model inter-rater reliability across distinct model architectures (specifically Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o, and DeepSeek-V3) must be systematically quantified to measure inter-provider epistemic alignment.
3. **Task Domain and Genre Generalization:** While our empirical trials validate human–AI interaction across both operational organizational policy reform (the Remote Work policy case) and executive strategic foresight (the Strategic Foresight / Sitra case), broader empirical generalization requires extending this evaluation protocol to formal legal contracts, clinical protocol verification, and automated software architecture documentation.
4. **Construct Validity, Neyman–Pearson Asymmetric Error Governance, and Multi-Rater Generalization:** The empirical trials establish high algorithmic test–retest reproducibility ($\bar{\kappa} = 0.9348$) under stochastic frontier sampling, suppressing aleatoric token decoding noise. In measurement theory, reliability is a necessary but insufficient condition for construct validity. Quorum governs the trade-off between sensitivity and precision through **Neyman–Pearson decision theory under asymmetric error costs**: in high-stakes regulatory auditing and enterprise governance (e.g., EU AI Act Articles 12–15), Type I errors (accepting fabricated, hallucinated, or ungrounded evidence, $\alpha$) carry unbounded legal liability and compliance forfeiture. Quorum therefore consciously locks physical citation specificity to $\text{Specificity}_{\text{lex}} = 1.000$ ($\alpha \to 0$), accepting a bounded Type II false rejection cost ($\text{FNR}_{\text{pop}} = 28.61\%$, $\widehat{\text{FOR}} = 13.33\%$; matching the $27.59\%$ retrieval gap in Section 8.5). This trade-off is continuously tunable: relaxing lexical strictness ($\zeta_{\text{lex}} < 100$) recovers $87.5\%$ ($7/8$) of inflectional and formatting retrieval gaps at $\zeta = 0$ (Section 8.5). While our pilot calibration audit in Section 8.5.1 (Table 7b) established high precision ($\text{PPV} = 97.50\%$, $\hat{\beta}_{\text{sem}} = 2.50\%$, 95% Wilson CI $[0.44\%, 12.88\%]$), these estimates reflect a pilot calibration sample ($N = 70$) assessed by a single senior expert auditor. Population-level construct validity, multi-rater concordance ($\kappa_{\text{human-Quorum}}$), and generalized semantic calibration across heterogeneous enterprise genres will be formally quantified in our planned multi-rater study ($N \ge 110$ across independent expert raters).
5. **Micro-Structural Graph Variance vs. Macro-Topological Stability:** In natural language discourse, exact graph isomorphism ($\mathcal{G}_1 \simeq \mathcal{G}_2$) across stochastic sampling runs is neither achievable nor ontologically meaningful, as autoregressive decoders introduce lexical paraphrasing when isolating proposition boundaries (observed verbatim quote Jaccard overlap was $25.3\%–31.9\%$; claim text overlap was $2.5\%–7.2\%$). As formalized in Section 4.2 (Guarantee 7) and Section 6 (Property 2), discrete ATMS root-cause surgery operates deterministically conditional on a single compiled graph instance $\mathcal{G}_{\text{LAG}}$, providing local execution explainability. Macro-evaluative stability across stochastic runs is preserved because the 0-token Cumulative Guttman Invariant (Section 4.2.1) functions as a topological low-pass filter, yielding tight inter-run cohesion deltas ($\le 0.0299$) and perfect BARS agreement ($\kappa = 1.00$ on $\mathcal{M}_{\text{Causal}}$). Future empirical trials will incorporate graph-edit distance (GED) bounds and kernel-based graph similarity metrics to systematically quantify micro-structural variance across model architectures.
6. **In-Silico Component Ablation vs. Direct Live-Ablation Re-runs:** While Configuration 1 in the component ablation study incorporates physical execution trace baselines, Configurations 2–5 and the transient fault stress test evaluate system defenses via a standardized offline benchmark harness. This harness injects controlled perturbations—including candidate citations evaluated against a frozen diagnostic pool of 29 candidate chimera citations (19.7% candidate attack pressure) empirically harvested from unconstrained frontier LLM decodes (21 synthetic hallucinations, 8 paraphrased retrieval gaps), simulated 0.9% API drops, and prompt structure alterations—across the identical 220 atom frames to isolate marginal component contributions without incurring the multi-thousand-dollar API expenditure of running full live factorial re-executions across all 5 configurations. While the harness faithfully models the production verification pipeline and reproduces the observed inter-run reliability ($\kappa = 0.9453$ in harness vs. $\bar{\kappa} = 0.9348$ in physical trials), future multi-site empirical trials should evaluate full-scale live-API factorial ablations across external foundation models.
7. **Sliding-Window Horizon Truncation of Macro-Discourse Dependencies:** As defined in Section 4.2 (Definition 3), proposition dependency discovery is bounded by a localized sliding window ($\Delta_{\max} \le M_{\text{win}} = 20$ proposition atoms) to avoid $\mathcal{O}(N^2)$ context bloat and lost-in-the-middle attention degradation. In extended documents ($|\mathcal{V}_{\text{claim}}| \in [141, 252]$ atoms), long-range dependencies between introductory axioms and terminal recommendations cannot be formed without intervening mentions, contributing to residual isolated concept counts ($r_{\text{iso}}^{\text{deliv}} \in [27.59\%, 50.00\%]$; Table 4). While Deliverable Subgraph Induction (Section 4.2.1) and calibrated scoping tolerance ($r^{\max}_{L3} = 0.30$) successfully isolate substantive deliverable assertions from dialogue noise, resolving remaining chapter-spanning horizon truncation requires extending the architecture with persistent Global Context Anchors (Section 4.2 Definition 3; Table 8).

---

## 9. Synthesis: Quorum’s Positioning in the Research Landscape

```
           NEUROSYMBOLIC & FORMAL
                     ^
                     |   * QUORUM ARCHITECTURE
                     |     - Kahn Wave DAG
                     |     - LAG 6-tuple
                     |     - ATMS graph surgery
                     |     - Popperian Penalty
                     |
   * FActScore       |   * Tree/Graph of Thoughts
     (Atom Check)    |     (Heuristic Search)
                     |
  <------------------+------------------>
  VERIFICATION-BOUND |   PROMPT-DRIVEN
                     |
   * Standard RAG    |   * Chain-of-Thought
     (k-NN Vectors)  |     (Linear Prompting)
                     |
                     |   * ReAct / Reflexion
                     |     (Trial Loops)
                     v
           STOCHASTIC & EMPIRICAL

```

### 9.1. Comparison with Reasoning and Orchestration Frameworks

* **Chain-of-Thought (CoT) (Wei et al., 2022) and Self-Consistency (Wang et al., 2023):** CoT relies entirely on the autoregressive distribution to maintain reasoning consistency, causing early errors to cascade exponentially (Equation 2). Self-Consistency attempts to mitigate this by sampling multiple CoT paths from a single model and taking a majority vote. However, as proven in Equation (25), single-model sampling under correlated epistemic priors ($\bar{\rho}_{\text{intra}} \approx 1$) merely amplifies systematic hallucinations when $p > 0.5$. Quorum restricts ensembling to aleatoric jitter suppression while enforcing epistemic soundness via non-generative symbolic invariants ($\lambda \in \{0, 1\}$, $\pi = -1$, and ATMS graph surgery).
* **Tree of Thoughts (ToT) (Yao et al., 2023b) and Graph of Thoughts (GoT) (Besta et al., 2024):** ToT and GoT structure thoughts into search graphs (BFS/DFS). However, their nodes remain unstructured natural language strings, and state pruning relies on LLM self-evaluation. Quorum’s nodes are strictly typed computational operators producing validated structured records, and state termination is mathematically guaranteed.
* **ReAct (Yao et al., 2023a) and Reflexion (Shinn et al., 2023):** Reflexion implements heuristic self-correction loops. However, recent empirical work (Huang et al., 2024) proves that LLMs cannot reliably self-correct without external deterministic ground truth. Quorum replaces circular self-reflection with external, asymmetric Popperian falsification.
* **Declarative Pipeline Compilers (DSPy) (Khattab et al., 2024):** DSPy optimizes declarative prompt modules through automated parameter tuning and teleprompter demonstrations. While DSPy optimizes pipeline prompt strings, its execution DAG lacks formal truth maintenance or discrete causal graph surgery. Quorum structures orchestration into Kahn topological waves over typed schema invariants with zero prompt-scraping or unvalidated string handoffs.

### 9.2. Comparison with Retrieval and Factuality Verification

* **Standard RAG (Lewis et al., 2020) and Self-RAG (Asai et al., 2024):** Standard RAG retrieves passage chunks via embedding similarity ($k$-NN), which introduces irrelevant context and fails on fine-grained logic. Quorum rejects chunk-level vector retrieval, deploying the epistemic atomization morphism $\alpha(\mathcal{D}) \to \mathcal{A}$ to evaluate discrete propositions against an absolute lexical null hypothesis.
* **FActScore (Min et al., 2023) and RARR (Gao et al., 2023):** FActScore decomposes text into atomic facts, but evaluates them symmetrically as binary factual counters. Quorum structures atoms into the six-tuple $a_i = \langle \tau_i, \mathcal{C}_i, \sigma_i, \pi_i, \lambda_i, \tau_{\text{val}, i} \rangle$, tracking speaker attribution, evidentiary polarity, physical provenance, and semantic rubric validation within a coherent multigraph.

### 9.3. Cross-Paradigm Architectural Comparison

| Dimension | Standard RAG / CoT | ReAct / Reflexion | Quorum Engine |
| --- | --- | --- | --- |
| **Orchestration** | Linear Sequence | Heuristic Loop | **Kahn Wave DAG** |
| **State Verify** | None (Generative) | Self-Reflection | **Typed Invariants** |
| **Grounding** | k-NN Dense Vector | Tool Output | **Lexical Null $H_0$** |
| **Causal Logic** | None (Spurious) | Trial-and-Error | **A-SCM & Truth Maint.** |
| **Scoring** | LLM-as-a-Judge | Heuristic | **Lipschitz BARS** |
| **Falsification** | None | Reranking | **Asymmetric Malus** |
| **Termination** | Max Length | Max Iterations | **Proved Acyclic** |
| **Agency Audit** | None | None | **HACM Tracking** |

---

## 10. Operational Considerations and Deployment Trade-Offs

1. **Computational Overhead, FinOps Allocation, and Heterogeneous Multi-Model Scaling:** Parallel ensemble verification and deterministic lexical verification (Architectural Property 1) increase inference token consumption relative to unverified single-pass sampling. In Quorum, FinOps resource allocation, verification rigor, and architectural scaling are governed by a partitioned strategy:
   * **Operational DAG Execution (Aleatoric Stabilization):** In baseline execution, high-entropy proposition atoms are evaluated using a single-pass Best-of-3 ensemble executed with the step's assigned model configuration, dispatching parallel calls via asynchronous coroutines with majority voting ($k \ge 2$ of $3$) and Popperian Null Hypothesis tie-breaking. This acts strictly as an aleatoric low-pass filter to dampen stochastic token decoding variance around decision thresholds under non-zero temperature. To prevent combinatorial token explosions, atoms are evaluated in batched sensor payloads, resulting in only 5–15 discrete LLM calls per full workflow execution (costing approximately $1.80–$3.05 per run in frontier flash models). Furthermore, Argument Causal Cohesion (A-SCM) is evaluated under a 0-token computational contract in pure graph logic, avoiding speculative counterfactual branch expansions.
   * **Offline Cross-Model Variance Benchmarking:** Comprehensive multi-provider parameter stability and alignment testing across diverse foundation model families (including Gemini, Claude, OpenAI, and DeepSeek) is conducted in dedicated offline evaluation workers, establishing baseline cross-architecture divergence metrics without burdening real-time execution pipelines.
   * **Simultaneous Heterogeneous Multi-Model Production Roadmap:** In actual production deployment, the platform will actively benchmark **simultaneous heterogeneous multi-model ensembling** within live execution waves. Rather than querying the same foundation model three times (which limits epistemic diversity against systematic pretraining blindspots as formalized in Section 6), the live voting branches will be concurrently routed across independent model families (specifically Google Gemini 3.8 Flash [`gemini-3.8-flash`; Google DeepMind, 2026], Anthropic Claude 3.5 Sonnet, and OpenAI GPT-4o). By tapping into distinct pretraining distributions, tokenizers, and alignment philosophies ($\bar{\rho}_{\text{inter}} \ll 1$), this multi-provider deployment expands the effective ensemble sample size $M_{\text{eff}}$ per Equation (25). The production trial will empirically benchmark whether the resulting gains in epistemic robustness justify the associated wall-clock synchronization latency (bounded by the slowest provider), cross-API failure modes, and heterogeneous FinOps token costs.
2. **Exogenous Axiom Misattribution and Provenance Friction:** In sparse strategic corpora, separating genuine exogenous axioms (primitive operational constraints requiring no internal textual ancestors) from unanchored orphan claims relies on explicit document bounding. If an author introduces implicit domain premises or industry-standard baseline axioms without physical citations in the source text, the closed-world lexical null hypothesis flags them as unverified orphans ($\lambda_i = 0$). While this behavior mathematically adheres to Toulmin's requirement for explicit evidentiary warrants, it introduces provenance friction in domains where shared common-sense assumptions are standard practice, necessitating explicit axiomatic white-listing or input provenance declaration.
3. **Rigid BARS Scoring and Perceived Excess Punitive Calibration:** Calibrated BARS power-curve damping ($\gamma = 1.25 \dots 1.5071$, corresponding to $\zeta \in [50, 70]$) yields conservative capability scores under enterprise zero-trust rubrics. While our empirical production trials executed at baseline strictness $\zeta = 0$ ($\gamma = 1.00$) to evaluate unattenuated raw model behavior, deploying non-linear damping in live organizational environments can lead human operators to perceive score compression at lower tiers as excessively punitive without peer normalization. In the empirical paired trials across both human–AI evaluation cases (the Remote Work policy case and the Strategic Foresight / Sitra case), normalized matrix scores ranged from $0.0\%$ to $61.9\%$ with stable inter-run consistency (MAD $3.05–3.99$ points). To remain interpretable across diverse user populations, raw BARS scores require supplementary cohort percentile calibration that contextualizes diagnostic results against normalized institutional baselines.
4. **The Enthymeme Boundary and the Semantic Entailment Gap:** Natural discourse is inherently elliptical and enthymematic, frequently omitting unstated common-sense warrants. Quorum's deterministic guarantees are strictly confined to physical citation provenance ($\lambda \in \{0, 1\}$), as universal semantic entailment is bounded by the semantic entailment gap (see Section 2.1). Residual semantic validity is bounded stochastically by role-asymmetric Popperian falsification ($\beta_{\text{sem}}$) and isolated through discrete ATMS reachability pruning.
5. **Vulnerability to the "Illusion of Control" via Prompt Sanitization:** As demonstrated across both empirical audits (the Remote Work policy trial and the Strategic Foresight / Sitra trial), human users may operate under the cognitive assumption that formulating concise, jargon-free prompts guarantees analytically rigorous output. However, this clean surface form (specifically zero mechanical phrase load) can mask unreflective routine delegation wherein the AI's first associative draft is accepted without counterfactual testing, boundary specification, or trade-off evaluation. While Quorum's Human Agency & Collaboration Matrix ($\mathcal{M}_{\text{HACM}}$) and Agency-to-Outcome Divergence ($\Delta_{\text{agency-outcome}}$) explicitly diagnose this form-to-content disparity, automated diagnostic evaluation cannot substitute for the operator's active willingness to engage in critical cognitive steering.
6. **Episodic Identifier Aliasing, Attention Economics, and Fail-Fast State Hydration:** While Section 2.1 formalizes the bijective mapping $\mu: \mathcal{I}_{\text{UUID}} \longleftrightarrow \mathcal{V}_{\text{alias}}$, maintaining distributed referential integrity requires strict lifecycle isolation. In Quorum, alias mappings are strictly scoped per execution instance to prevent cross-tenant state pollution. When execution is distributed across asynchronous worker nodes, the mapping state is serialized into an immutable manifest transported within execution metadata. The worker reconstitutes the bijection and executes strict fail-fast validation: any hallucinated alias matching an active prefix that does not exist in the manifest immediately halts execution with an unrecoverable validation error, preventing corrupted foreign keys from entering persistent graph state.
7. **Design-Time Rubric Compilation Overhead (Cold-Start Engineering Cost):** Unlike zero-shot LLM-as-a-Judge paradigms that evaluate arbitrary tasks via ad-hoc natural language instructions, Quorum's epistemic guarantees require pre-compiled, version-controlled BARS matrices ($N = 110$ criteria in our benchmark) with explicit positive capability anchors ($\pi_i = +1$) and contrastive anti-pattern distractors ($\pi_i = -1$). While this design-time human curation is mathematically necessary to bound the semantic entailment gap (Section 2.1) and maintain longitudinal psychometric invariance (Section 5.4.4), it introduces an upfront domain-engineering cost when onboarding novel specialized verticals. Quorum mitigates this cold-start overhead by separating domain-agnostic process and structural matrices ($\mathcal{M}_{\text{HACM}}, \mathcal{M}_{\text{Toulmin}}, \mathcal{M}_{\text{Causal}}, \mathcal{M}_{\text{Bloom}}$)—which transfer invariant epistemological standards across workflows with zero modification—from the task-specific substance matrix ($\mathcal{M}_{\text{Domain}}$). Domain architects instantiate new audit workflows by authoring only the localized domain module (typically requiring 2–4 hours of expert specification rather than weeks of model fine-tuning), after which automated schema verification suites ensure physical anchorability.

### 10.1. Summary of Architectural Trade-Offs and System Mitigations

To provide a consolidated reference for system architects and regulatory auditors, Table 8 synthesizes the fundamental engineering trade-offs inherent in Quorum's neurosymbolic architecture, mapping each mechanism to its design trade-off, empirical boundary observed in trials, and system mitigation:

| Architectural Mechanism | Inherent Trade-Off / Constraint | Empirical Bound in Trials | System Mitigation & Roadmap |
| :--- | :--- | :--- | :--- |
| **1. Macro-Topological Guttman Filter & Micro-Graph Variance ($\mathcal{G}_1 \not\simeq \mathcal{G}_2$)** | Stochastic proposition mining yields non-isomorphic micro-topologies ($\mathcal{G}_1 \not\simeq \mathcal{G}_2$) and run-specific root causes ($RC_1 \neq RC_2$). | Verbatim quote Jaccard overlap $25.3\%–31.9\%$; claim text overlap $2.5\%–7.2\%$. | Macro-topological Guttman low-pass filter achieves $100\%$ reproducibility ($\kappa = 1.00$ on $\mathcal{M}_{\text{Causal}}$); roadmap formalizes graph-edit distance (GED) bounds and graph kernels. |
| **2. Five-Gate Lexical Firewall & Recall Trade-Off ($\lambda_i \in \{0,1\}$)** | Verbatim normalized substring matching penalizes inflected, formatted, or diffuse multi-sentence evidence (*Retrieval Gaps*). | $27.59\%$ benchmark recall gap; $\text{FNR}_{\text{pop}} = 28.61\%$ ($\widehat{\text{FOR}} = 13.33\%$: $3.33\%$ inflectional $\text{FOR}_{\text{rejection}}$, $10.00\%$ diffuse $\text{FOR}_{\text{omission}}$); accounts for $85.7\%$ of stochastic inter-run variance. | Neyman–Pearson prioritization locks $\text{Specificity}_{\text{lex}} = 1.000$ ($\alpha \to 0$, $0\%$ fabrication leakage); Gate 5 Snowball stemming and LCS coverage ($\ge 70\%$) at $\zeta_{\text{lex}} < 100$ recovers $87.5\%$ ($7/8$) of inflectional gaps, while multi-turn iterative re-prompting (within the $1,000$-char Gate 2 ceiling) recovers diffuse multi-sentence sensor omissions. |
| **3. Heterogeneous Ensembling & Semantic Entailment Gap ($\bar{\rho}_{\text{intra}} \approx 1$)** | Deterministic string verification is semantically blind to implicit entailment ($\mathcal{C}_i \models \tau_i$); single-model ensembling shares systematic epistemic priors ($\bar{\rho}_{\text{intra}} \approx 1$). | Residual Type II semantic misattribution $\hat{\beta}_{\text{sem}} = 2.50\%$ ($95\%$ Wilson CI $[0.44\%, 12.88\%]$); score inflation $< 2.1\%$. | Gate 4 reasoning trace triangulation asserts syntactic anchor existence; roadmap routes live Bo3 waves across heterogeneous model families (Gemini, Claude, GPT-4o) to suppress inter-model correlation ($\bar{\rho}_{\text{inter}} \ll 1$). |
| **4. Sliding-Window Proposition Linker ($\Phi_{\text{link}}$) & Horizon Bounds ($\Delta_{\max} \le 20$)** | Localized sliding window truncates long-range deductive dependencies across distant chapters ($\Delta_{\max} \le M_{\text{win}} = 20$ atoms). | Inflates unanchored degree-zero root axioms ($\text{OutDegree}=0$), contributing to $r_{\text{iso}}^{\text{deliv}} \in [27.59\%, 50.00\%]$. | Avoids $\mathcal{O}(N^2)$ context bloat; calibrated scoping tolerance ($r^{\max}_{L3} = 0.30$) and planned persistent Global Context Anchor header for root axioms ($\text{InDegree}=0$) enable chapter-spanning causal leaps. |
| **5. Deliverable Subgraph Induction ($\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$) & Enthymematic Cascades** | Topological metric blindness to non-deductive conversational dialogue and unstated common-sense warrants (enthymemes). | Unpartitioned dialogue turns inflate isolated concept counts (67 vs. 8 in Sitra); single root premise failure cascades up to $9.52\%$ of claims under strict conjunction. | Deliverable Subgraph Induction ($\mathcal{G}[\mathcal{V}_{\text{deliverable}}]$) purges 59 conversational dialogue nodes; exogenous boundary axioms and corroborative warrant redundancy (`DISJUNCTIVE_OR`) reduce cascade propagation by $62.5\%$. |
| **6. BARS Scoring Rigidity, Cumulative Malus Ceiling, and Modular Onboarding** | Strict BARS zero-trust thresholds and cumulative Popperian malus risk perceived scoring rigidity or excessive punitive cliff-edges; domain onboarding requires custom rubric curation. | Normalized scores span $0.0\%–61.9\%$ (MAD $3.05–3.99$); full-rubric cold-start engineering overhead across novel specialized verticals. | Modular $\mathcal{M}_{\text{Domain}}$ decomposition limits onboarding to 2–4 hours (preserving 4 invariant matrices); fatal baseline failures are governed via `EnrichedDagExecutor` Kahn wave short-circuiting (clamping dependent $L_2 \dots L_5$ criteria to `BLOCKED` / `N_A` to bound $\rho$), whereas non-fatal anti-pattern deductions ($\pi_i = -1$) are capped at $P_{\max} = 0.40$ ($\Pi_{\text{penalty}} \ge 0.60$) with cohort percentile calibration to preserve Lipschitz stability. |

**Table 8:** Comprehensive architectural trade-off and mitigation matrix across Quorum's core neurosymbolic mechanisms, mapping identified failure modes to mathematical mitigations and verified empirical results.

---

## 11. Conclusions

The Quorum architecture establishes an epistemically anchored neurosymbolic foundation for transforming stochastic large language models into verifiable, reproducible expert systems. By replacing unconstrained autoregressive generation with:

* Kahn wave-based DAG scheduling (Architectural Principle 1),
* Decoupled epistemic error suppression separating physical citation provenance from semantic entailment (Architectural Property 1),
* Monotonic, Lipschitz-stable BARS power-curve scoring (Mathematical Property 1), and
* Discrete structural argument surgery and ATMS-based fault isolation (Architectural Property 2),

the framework eliminates hallucination cascades and enforces structural accountability. Across two paired empirical production audits ($N = 220$ proposition atom frames) and a 5-configuration component ablation benchmark, Quorum demonstrates that:

1. **Evidentiary Anchoring & Replication Reliability (RQ1):** Multi-gate physical lexical verification combined with parallel Best-of-3 ensembling elevates evaluative test–retest reproducibility from $\kappa = 0.2146$ (unconstrained prompt-based LLM judge) to $\kappa = 0.9453$ in the benchmark harness ($\bar{\kappa} = 0.9348$, $P_o = 96.82\%$ in physical production trials), while completely eliminating unanchored chimera quotations from $20.7\%$ to $0.0\%$ under our offline benchmark stress test with 19.7% candidate attack pressure ($\text{Specificity}_{\text{lex}} = 1.000$, $\alpha \to 0$). Blinded human expert calibration bounds the empirical False Omission Rate to $\widehat{\text{FOR}} = 13.33\%$, isolating $3.33\%$ inflectional firewall rejections (recoverable via Gate 5 stemming at $\zeta < 100$) from $10.00\%$ diffuse multi-sentence context omissions (mitigated via multi-turn iterative re-prompting).
2. **Decomposition & Attention Integrity (RQ2):** Propositional epistemic atomization (Linked Atom Graph 6-tuple) and single-token attention aliasing eradicate the $8.6\%$ criterion omission rate characteristic of monolithic step-level evaluation, guaranteeing complete evaluative coverage.
3. **Structural Causality & Human Agency Discrimination (RQ3):** The 0-token Cumulative Guttman Invariant on mined argument graphs and the Human Agency & Collaboration Matrix ($\mathcal{M}_{\text{HACM}}$) successfully penetrate surface fluency to diagnose passive automation complacency and distinguish genuine causal reasoning from rhetorical correlation.
4. **Two-Tier Fault Governance & Lipschitz Stability:** Decoupling fatal baseline failures (governed via Kahn wave precondition short-circuiting clamping ungrounded downstream criteria to `BLOCKED` / `N_A`) from non-fatal cognitive anti-patterns (bounded multiplicatively by the $40\%$ penalty ceiling $P_{\max} = 0.40$, $\Pi_{\text{penalty}} \ge 0.60$) preserves Lipschitz score stability while preventing capability score accumulation on compromised foundations.

These findings provide an auditable, verifiable methodology for enterprise, clinical, and strategic artificial intelligence where deterministic accountability and regulatory compliance (specifically EU AI Act Articles 12–15) are paramount.

---

## Data and Software Availability

The Quorum reference implementation, ablation evaluation harnesses, test datasets, and audit reproduction scripts are maintained in the open-source repository at `https://github.com/launis/quorum`. The repository includes the autonomous causal discovery engine, pure stateless causal cohesion evaluator, and complete configuration seeds evaluated in this study.

---

### Selected References

1. **Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001).** *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy of Educational Objectives*. Longman.
2. **Artstein, R., & Poesio, M. (2008).** Inter-coder agreement for computational linguistics. *Computational Linguistics*, 34(4), 555–596.
3. **Asai, A. et al. (2024).** Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. *International Conference on Learning Representations (ICLR 2024)*.
4. **Besta, M. et al. (2024).** Graph of Thoughts: Solving Elaborate Problems with Large Language Models. *AAAI Conference on Artificial Intelligence (AAAI 2024)*.
5. **Bloom, B. S. (Ed.). (1956).** *Taxonomy of Educational Objectives: The Classification of Educational Goals. Handbook I: Cognitive Domain*. David McKay Co.
6. **Buçinca, Z., Malaya, M. B., & Gajos, K. Z. (2021).** To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making. *Proceedings of the ACM on Human-Computer Interaction*, 5(CSCW1), Article 188, 1–21.
7. **Carlsson, G. (2009).** Topology and data. *Bulletin of the American Mathematical Society*, 46(2), 255–308.
8. **Church, A., & Rosser, J. B. (1936).** Some properties of conversion. *Transactions of the American Mathematical Society*, 39(3), 472–482.
9. **Cohen, J. (1960).** A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46.
10. **de Kleer, J. (1986).** An assumption-based TMS. *Artificial Intelligence*, 28(2), 127–162.
11. **Doyle, J. (1979).** A truth maintenance system. *Artificial Intelligence*, 12(3), 231–272.
12. **Dung, P. M. (1995).** On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357.
13. **Dziri, N. et al. (2023).** Faith and fate: Limits of transformers on compositionality. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.
14. **Edelsbrunner, H., & Harer, J. (2010).** *Computational Topology: An Introduction*. American Mathematical Society.
15. **Fleiss, J. L. (1971).** Measuring nominal scale agreement among many raters. *Psychological Bulletin*, 76(5), 378–382.
16. **Gao, L. et al. (2023).** RARR: Researching and Revising What Language Models Say, Using Language Models. *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL 2023)*, 16477–16508.
17. **Google DeepMind. (2026).** *Gemini 3.8 Flash Model Card*. https://deepmind.google/models/model-cards/gemini-3-8-flash/
18. **Grice, H. P. (1975).** Logic and conversation. In P. Cole & J. L. Morgan (Eds.), *Syntax and Semantics, Vol. 3: Speech Acts* (pp. 41–58). Academic Press.
19. **Guttman, L. (1944).** A basis for scaling qualitative data. *American Sociological Review*, 9(2), 139–150.
20. **Huang, J. et al. (2024).** Large Language Models Cannot Self-Correct Reasoning Yet. *International Conference on Learning Representations (ICLR 2024)*.
21. **Johnson, D. B. (1975).** Finding all the elementary circuits of a directed graph. *SIAM Journal on Computing*, 4(1), 77–84.
22. **Kahn, A. B. (1962).** Topological sorting of large networks. *Communications of the ACM*, 5(11), 558–562.
23. **Kahn, G. (1974).** The semantics of a simple language for parallel programming. *Information Processing 74: Proceedings of IFIP Congress 74*, 471–475.
24. **Kahneman, D. (2011).** *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
25. **Khattab, O. et al. (2024).** DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines. *International Conference on Learning Representations (ICLR 2024)*.
26. **Landis, J. R., & Koch, G. G. (1977).** The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174.
27. **Lewis, P. et al. (2020).** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems (NeurIPS 2020)*.
28. **Liu, Y. et al. (2023).** G-Eval: NLG evaluation using GPT-4 with better human alignment. *Empirical Methods in Natural Language Processing (EMNLP 2023)*.
29. **Min, S. et al. (2023).** FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. *Empirical Methods in Natural Language Processing (EMNLP 2023)*.
30. **Nie, Y. et al. (2020).** Adversarial NLI: A New Benchmark for Natural Language Understanding. *Association for Computational Linguistics (ACL 2020)*.
31. **Parasuraman, R., Sheridan, T. B., & Wickens, C. D. (2000).** A model for types and levels of human interaction with automation. *IEEE Transactions on Systems, Man, and Cybernetics - Part A: Systems and Humans*, 30(3), 286–297.
32. **Pearl, J. (1995).** Causal diagrams for empirical research. *Biometrika*, 82(4), 669–688.
33. **Pearl, J. (2009).** *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
34. **Pearl, J., & Mackenzie, D. (2018).** *The Book of Why: The New Science of Cause and Effect*. Basic Books.
35. **Popper, K. (1959).** *The Logic of Scientific Discovery*. Hutchinson & Co.
36. **Rice, H. G. (1953).** Classes of recursively enumerable sets and their decision problems. *Transactions of the American Mathematical Society*, 74(2), 358–366.
37. **Ross, S., & Bagnell, J. A. (2010).** Efficient reductions for imitation learning. *International Conference on Artificial Intelligence and Statistics (AISTATS 2010)*, 661–668.
38. **Sheridan, T. B., & Verplank, W. L. (1978).** *Human and Computer Control of Undersea Teleoperators*. MIT Man-Machine Systems Laboratory.
39. **Shinn, N. et al. (2023).** Reflexion: Language Agents with Verbal Reinforcement Learning. *NeurIPS 2023*.
40. **Smith, P. C., & Kendall, L. M. (1963).** Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. *Journal of Applied Psychology*, 47(2), 149–155.
41. **Tarjan, R. (1972).** Depth-first search and linear graph algorithms. *SIAM Journal on Computing*, 1(2), 146–160.
42. **Thorne, J. et al. (2018).** FEVER: a large-scale dataset for Fact Extraction and VERification. *North American Chapter of the Association for Computational Linguistics (NAACL 2018)*.
43. **Toulmin, S. E. (1958).** *The Uses of Argument*. Cambridge University Press.
44. **Turing, A. M. (1936).** On computable numbers, with an application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society*, s2-42(1), 230–265.
45. **Wang, X. et al. (2023).** Self-Consistency Improves Chain of Thought Reasoning in Language Models. *International Conference on Learning Representations (ICLR 2023)*.
46. **Wei, J. et al. (2022).** Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *NeurIPS 2022*.
47. **Yao, S. et al. (2023a).** ReAct: Synergizing Reasoning and Acting in Language Models. *International Conference on Learning Representations (ICLR 2023)*.
48. **Yao, S. et al. (2023b).** Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.
49. **Zečević, M., Willig, M., Dhami, D. S., & Kersting, K. (2023).** Causal Parrots: Large Language Models May Talk Causality But Are Not Causal. *Transactions on Machine Learning Research (TMLR)*, August 2023.
50. **Zheng, L. et al. (2023).** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*.

---

## Appendix A: Statistical Methodology & Schema Accounting

### A.1. Two-Stage Hierarchical Cluster Bootstrap and Finite-Sample Bounds

In high-stakes natural language evaluation, proposition atoms evaluated within the same workflow step or document section are not identically and independently distributed (i.i.d.): they share common prompt contexts, common foundation model key-value attention caches, and common latent document representations. In standard biostatistical and psychometric literature, naive application of Cohen's asymptotic variance formula:
$$\text{Var}_{\text{nominal}}(\hat{\kappa}) = \frac{P_o(1 - P_o)}{N (1 - P_e)^2}$$
underestimates the true standard error when positive intra-cluster correlation exists ($\rho_{\text{ICC}} > 0$), inducing pseudoreplication bias and artificially narrow confidence intervals.

To account for batch-level clustering across our empirical evaluations without imposing parametric distribution assumptions, Quorum implements a **Hierarchical Two-Stage Non-Parametric Cluster Bootstrap**:

1. **Stage 1 (Meso-Level Cluster Resampling):** Let $\mathcal{K} = \{C_1, C_2, \dots, C_K\}$ denote the set of $K = 10$ distinct matrix step execution clusters across trials ($K = 5$ clusters per trial: $\mathcal{M}_{\text{Toulmin}}, \mathcal{M}_{\text{Causal}}, \mathcal{M}_{\text{Transp}}, \mathcal{M}_{\text{HACM}}, \mathcal{M}_{\text{Bloom}}$). In each bootstrap iteration $b \in \{1, \dots, B\}$ ($B = 2,000$ to $10,000$), we draw $K$ step clusters with replacement:
   $$\mathcal{K}^{(b)} = \{C_{k_1}, C_{k_2}, \dots, C_{k_K}\}, \quad k_j \sim \text{Uniform}(\{1, \dots, K\})$$
2. **Stage 2 (Within-Cluster Atom Resampling):** For each selected cluster $C \in \mathcal{K}^{(b)}$ containing $N_C$ proposition criteria, we resample $N_C$ atom evaluation frames with replacement:
   $$\mathcal{A}_C^{(b)} = \{a_{i_1}, \dots, a_{i_{N_C}}\}, \quad i_j \sim \text{Uniform}(\{1, \dots, N_C\})$$
3. **Empirical Percentile Confidence Intervals:** For each resampled replicate dataset $\mathcal{D}^{(b)} = \bigcup_{C \in \mathcal{K}^{(b)}} \mathcal{A}_C^{(b)}$, we recompute the evaluation concordance $\kappa^{(b)}$. Across $B$ bootstrap realizations, the 95% confidence interval is extracted non-parametrically using empirical percentiles:
   $$\text{CI}_{95\%} = \left[ \hat{\kappa}_{0.025}^*, \; \hat{\kappa}_{0.975}^* \right]$$
   Empirical percentile intervals preserve the natural parameter boundaries $[-1.0, 1.0]$ and naturally accommodate distribution skewness near the upper boundary ($\kappa \to 1.0$), avoiding standard normal approximation clipping artifacts.
4. **Conservative Truncation Floor:** Standard single-stage cluster resampling artificially contracts confidence intervals when error rates are stratified uniformly across clusters ($\rho_{\text{ICC}} \le 0$), as between-cluster variance vanishes while within-cluster binomial sampling variance is omitted. By combining Stage 1 and Stage 2 resampling with the conservative truncation floor:
   $$\text{SE}_{\text{conservative}} = \max\left(\text{SE}_{\text{nominal}}, \; \text{SE}_{\text{cluster}}\right)$$
   Quorum restores finite-sample binomial degrees of freedom, yielding Kish Design Effect standard error inflations of $\text{Deff}^{1/2} \in [1.10\times, 1.37\times]$ across all configurations while proving that lower bounds remain strictly within the *Almost Perfect Agreement* tier ($> 0.81$).
5. **Discrete Granularity and Finite-Cluster Ceiling Effect ($K = 5$ per Trial):** When evaluating trial-specific bootstrap confidence intervals on a per-pair basis, each trial comprises $K = 5$ matrix step clusters ($N = 110$ criteria per trial; $K = 10$ across both pooled trials). In Trial Pair B (Table 3), 3 of the 5 matrices ($\mathcal{M}_{\text{Toulmin}}$, $\mathcal{M}_{\text{Causal}}$, and $\mathcal{M}_{\text{Transp}}$) exhibited zero disagreements across runs ($P_o = 100\%$). Consequently, in a non-parametric bootstrap over $K = 5$ clusters, the probability that all 5 resampled clusters in Stage 1 are drawn exclusively from these 3 perfect-agreement matrices is at least:
   $$P(\text{All 5 drawn clusters have 0 disagreements}) = \left(\frac{3}{5}\right)^5 = 0.07776 \approx 7.8\%$$
   Additionally, even in Stage 1 draws that include one of the 2 matrices containing disagreements (totaling only 2 discordant atoms across the entire trial), Stage 2 within-cluster atom resampling with replacement has a non-negligible probability of missing the discordant atoms entirely. In all such resampled realizations ($> 7.8\%$ of total bootstrap iterations), the resampled dataset contains zero disagreements ($P_o^{(b)} = 1.0$, $P_e^{(b)} < 1.0$), yielding exact concordance $\kappa^{(b)} = 1.0000$. Because this point-mass probability at $1.0000$ exceeds the upper tail alpha cutoff ($7.8\% > 2.5\%$), the non-parametric 97.5th empirical percentile is discretely clipped at the mathematical ceiling $\hat{\kappa}_{0.975}^* = 1.0000$ (yielding $[0.8946, 1.0000]$ for Pair B, and analogously $[0.8212, 1.0000]$ for Pair A where 5 disagreements are concentrated across 2 matrices). Crucially, cross-checking Table 3 reveals that Pair A also possesses 3 zero-disagreement clusters ($\mathcal{M}_{\text{Toulmin}}$, $\mathcal{M}_{\text{Causal}}$, and $\mathcal{M}_{\text{HACM}}$), meaning that out of the $K = 10$ pooled clusters across both trials ($N = 220$ criteria), exactly 6 clusters exhibit zero disagreements ($K_0 = 6$). Consequently, the Stage 1 probability of drawing 10 zero-disagreement clusters contracts to:
   $$P(\text{All 10 drawn clusters have 0 disagreements}) = \left(\frac{6}{10}\right)^{10} = 0.6^{10} \approx 0.006047 \; (0.605\%)$$
   In Stage 2 within-cluster resampling, when one of the 4 remaining clusters with disagreements is drawn (Pair A $\mathcal{M}_{\text{Transp}}$ [$N_C = 25, d_C = 3$ disagreements], Pair A $\mathcal{M}_{\text{Bloom}}$ [$N_C = 30, d_C = 2$], Pair B $\mathcal{M}_{\text{HACM}}$ [$N_C = 25, d_C = 1$], and Pair B $\mathcal{M}_{\text{Bloom}}$ [$N_C = 30, d_C = 1$]), the exact finite-sample probability of resampling $N_k$ atoms with zero disagreements is $(1 - d_k/N_k)^{N_k}$: specifically $(22/25)^{25} = 0.88^{25} = 0.04091 \approx 4.09\%$ for Pair A $\mathcal{M}_{\text{Transp}}$, $(28/30)^{30} \approx 12.63\%$ for Pair A $\mathcal{M}_{\text{Bloom}}$, $(24/25)^{25} = 0.96^{25} \approx 36.04\%$ for Pair B $\mathcal{M}_{\text{HACM}}$, and $(29/30)^{30} \approx 36.17\%$ for Pair B $\mathcal{M}_{\text{Bloom}}$ (contrasting with the asymptotic Poisson limit $(1 - 1/N_C)^{N_C} \to 1/e \approx 36.79\%$). Because Stage 1 draws $K = 10$ cluster slots independently with replacement and Stage 2 resamples $N_k$ atoms independently with replacement within each drawn cluster, the exact probability that a single resampled cluster slot yields zero disagreements is the uniform expectation across all $K = 10$ clusters:
   $$p_{\text{slot}}(0) = \frac{1}{K} \sum_{k=1}^{K} \left(1 - \frac{d_k}{N_k}\right)^{N_k} = \frac{6(1) + 0.88^{25} + (28/30)^{30} + 0.96^{25} + (29/30)^{30}}{10} = \frac{6.88927}{10} = 0.688927$$
   Consequently, across $K = 10$ independent cluster slot draws in a bootstrap replicate $\mathcal{D}^{(b)}$, the exact closed-form multinomial-binomial convolution probability of observing zero total disagreements is:
   $$P\left(\text{Zero disagreements in } \mathcal{D}^{(b)}\right) = \left[p_{\text{slot}}(0)\right]^{10} = (0.688927)^{10} \approx 0.02387 \;\; (2.39\%)$$
   Crucially, $2.39\%$ remains strictly below the two-sided $\alpha/2 = 2.50\%$ upper-tail percentile cutoff, which eliminates the discrete boundary ceiling truncation at $1.0000$ and yields a smooth, interior upper percentile bound of $\hat{\kappa}_{0.975}^* = 0.9868$ ($[0.8784, 0.9868]$), while mathematically demonstrating why this upper bound sits very close to $1.0000$.

### A.2. Evidentiary Citation Accounting & Empirical $2 \times 2$ Contingency Tables (59 Physical Citations across 4 Runs)

Across Trial Pairs A and B, a total of **59 verified physical citations** were extracted across the four production runs, partitioned into **54 positive capability citations** ($\pi_i = +1, \lambda_i = 1, \tau_{\text{val}, i} = 1$) and **5 anti-pattern violation citations** ($\pi_i = -1, \lambda_i = 1, \tau_{\text{val}, i} = 1$). This citation census is fully distinct from the overall production pass rate of 57.7% (127 / 220 passed criteria across baseline Runs A1 and B1).$^\dagger$

Specifically, the design-time benchmark schema specifies exactly $N = 110$ criteria per trial, partitioned into:
1. **57 positive capability atoms** ($\pi_i = +1$, requiring physical citations and semantic validation):
   - $\mathcal{M}_{\text{Toulmin}}$: 8 positive criteria
   - $\mathcal{M}_{\text{Transp}}$: 16 positive criteria
   - $\mathcal{M}_{\text{HACM}}$: 15 positive criteria
   - $\mathcal{M}_{\text{Bloom}}$: 18 positive criteria
2. **48 negative anti-pattern atoms** ($\pi_i = -1$, passing with zero citations under clean performance):
   - $\mathcal{M}_{\text{Toulmin}}$: 17 anti-pattern criteria
   - $\mathcal{M}_{\text{Transp}}$: 9 anti-pattern criteria
   - $\mathcal{M}_{\text{HACM}}$: 10 anti-pattern criteria
   - $\mathcal{M}_{\text{Bloom}}$: 12 anti-pattern criteria
3. **5 topological causal cohesion tiers** ($\mathcal{M}_{\text{Causal}}$, evaluated in 0 tokens from graph invariants without text citations)

Totaling $57 + 48 + 5 = 110$ criteria per trial, and $114 + 96 + 10 = 220$ across both paired trials.

#### 1. Evidentiary Citation Breakdown Across All Four Runs
Across all four production runs (A1, A2, B1, B2), the 59 verified physical citations break down as follows:
* **Positive Capability Citations ($\pi_i = +1, \lambda_i = 1, \tau_{\text{val}, i} = 1$):**
  - Run A1: 18 verified citations
  - Run A2: 16 verified citations (drop of 2 relative to A1)
  - Run B1: 11 verified citations
  - Run B2: 9 verified citations (drop of 2 relative to B1)
  *Subtotal: 54 capability citations across 35 unique text spans (100% satisfying Tier 1 exact normalized substring containment, $\text{find} \neq -1$).*
* **Anti-Pattern Violation Citations ($\pi_i = -1, \lambda_i = 1, \tau_{\text{val}, i} = 1$):**
  - Run A1: 2 verified violations ($48 - 2 = 46$ clean passes)
  - Run A2: 3 verified violations ($48 - 3 = 45$ clean passes; increase of 1 violation relative to A1)
  - Run B1: 0 verified violations ($48 - 0 = 48$ clean passes)
  - Run B2: 0 verified violations ($48 - 0 = 48$ clean passes)
  *Subtotal: 5 anti-pattern violation citations.*
* **Total Physical Citations Extracted:** Run A1: 20 ($18 + 2$), Run A2: 19 ($16 + 3$), Run B1: 11 ($11 + 0$), Run B2: 9 ($9 + 0$). Grand total: $20 + 19 + 11 + 9 = 59$ physical citations.

| Category | Run A1 | Run A2 | Run B1 | Run B2 | Total Citations |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Positive Capability Citations ($\pi_i = +1, \lambda_i=1, \tau_{\text{val}, i}=1$)** | 18 | 16 | 11 | 9 | **54** |
| **Anti-Pattern Violation Citations ($\pi_i = -1, \lambda_i=1, \tau_{\text{val}, i}=1$)** | 2 | 3 | 0 | 0 | **5** |
| **Total Physical Citations Extracted** | **20** | **19** | **11** | **9** | **59** |
| Clean Anti-Pattern Passes ($\pi_i = -1, \lambda_i=0 \lor \tau_{\text{val}, i}=0$) | 46 | 45 | 48 | 48 | — |
| Macro-Topological Guttman Tiers ($\mathcal{M}_{\text{Causal}}$, 0 tokens) | 2 | 2 | 2 | 2 | — |
| **Total Passed Criteria ($\omega(a_i) = \text{PASSED}$)** | **66** | **63** | **61** | **59** | — |

#### 2. Reconciliation of Net Pass Counts and Marginal Decision Bias
In baseline physical production execution (Runs A1 + B1), the 127 passed atoms decompose into:
- **29 positive atoms with verified citations** ($18 \text{ in A1} + 11 \text{ in B1}$),
- **94 clean anti-patterns with zero citations** ($46 \text{ in A1} + 48 \text{ in B1}$), and
- **4 topological causal cohesion tiers** ($2 \text{ in A1} + 2 \text{ in B1}$).

In Pair A (Remote Work Policy Case), total criteria passing in Run A1 was $18 + 46 + 2 = 66$ ($60.00\%$), while in Run A2 total passing criteria was $16 + 45 + 2 = 63$ ($57.27\%$). The net drop of 3 passes ($66 - 63 = 3$) corresponds exactly to the reported marginal decision bias $d_{\text{bias}} = -3 / 110 = -0.0273$ (Table 2), decomposing into a drop of 2 positive capability citations ($18 \to 16$) and a drop of 1 clean anti-pattern pass ($46 \to 45$, due to 1 additional detected anti-pattern violation in Run A2).

In Pair B (Strategic Foresight / Sitra Case), total criteria passing in Run B1 was $11 + 48 + 2 = 61$ ($55.45\%$), while in Run B2 total passing criteria was $9 + 48 + 2 = 59$ ($53.64\%$). The net drop of 2 passes ($61 - 59 = 2$) corresponds exactly to $d_{\text{bias}} = -2 / 110 = -0.0182$ (Table 2), where anti-pattern performance was perfectly invariant ($48 \to 48$, 0 violations in both runs) and the drop arose solely from positive capability extraction variance ($11 \to 9$).

#### 3. Empirical $2 \times 2$ Contingency Matrices
Given observed agreements, marginal biases, and disagreement counts ($b + c = 5$ in Pair A; $b + c = 2$ in Pair B), the $2 \times 2$ contingency tables are uniquely and algebraically determined:

**Trial Pair A: Remote Work Policy Case ($N = 110, P_o = 95.45\%, P_e = 51.45\%, \kappa = 0.9064$)**

| Evaluator State | Run A2: PASSED ($\omega = \text{PASS}$) | Run A2: FAILED ($\omega = \text{FAIL}$) | Row Marginal (Run A1) |
| :--- | :---: | :---: | :---: |
| **Run A1: PASSED** | $a = 62$ | $b = 4$ | $a + b = 66$ ($60.00\%$) |
| **Run A1: FAILED** | $c = 1$ | $d = 43$ | $c + d = 44$ ($40.00\%$) |
| **Column Marginal (Run A2)** | $a + c = 63$ ($57.27\%$) | $b + d = 47$ ($42.73\%$) | $N = 110$ |

*Verification:* $P_o = (62 + 43)/110 = 105/110 = 95.4545\%$; $P_e = (66/110)(63/110) + (44/110)(47/110) = 0.343636 + 0.170909 = 0.514545$; $\kappa = (0.954545 - 0.514545)/(1 - 0.514545) = 0.9064$. The 5 disagreements decompose into $b = 4$ (A1 PASS, A2 FAIL: 3 capability retrieval gaps + 1 anti-pattern citation detected in A2) and $c = 1$ (A1 FAIL, A2 PASS: 1 reasoning gap where both runs had $\lambda_i = 1$, but $\tau_{\text{val}, i}^{(A1)} = 0 \neq \tau_{\text{val}, i}^{(A2)} = 1$).

**Trial Pair B: Strategic Foresight / Sitra Case ($N = 110, P_o = 98.18\%, P_e = 50.40\%, \kappa = 0.9633$)**

| Evaluator State | Run B2: PASSED ($\omega = \text{PASS}$) | Run B2: FAILED ($\omega = \text{FAIL}$) | Row Marginal (Run B1) |
| :--- | :---: | :---: | :---: |
| **Run B1: PASSED** | $a = 59$ | $b = 2$ | $a + b = 61$ ($55.45\%$) |
| **Run B1: FAILED** | $c = 0$ | $d = 49$ | $c + d = 49$ ($44.55\%$) |
| **Column Marginal (Run B2)** | $a + c = 59$ ($53.64\%$) | $b + d = 51$ ($46.36\%$) | $N = 110$ |

*Verification:* $P_o = (59 + 49)/110 = 108/110 = 98.1818\%$; $P_e = (61/110)(59/110) + (49/110)(51/110) = 0.297438 + 0.206530 = 0.503968$; $\kappa = (0.981818 - 0.503968)/(1 - 0.503968) = 0.9633$. The 2 disagreements decompose into $b = 2$ (B1 PASS, B2 FAIL: 2 capability retrieval gaps) and $c = 0$.

#### 4. Polarity-Stratified Reliability on Positive Capability Criteria ($N_{\text{pos}} = 57$)
To verify that Quorum's high test–retest stability ($\bar{\kappa} = 0.9348$) is not an artifact of unviolated negative anti-pattern criteria ($N_{\text{anti}} = 48$, which pass by default under clean authorial performance), we isolate the $N_{\text{pos}} = 57$ positive capability criteria requiring physical citation grounding ($\lambda_i = 1$) and semantic entailment ($\tau_{\text{val}, i} = 1$). In Pair A ($N_{\text{pos}} = 57$), 4 disagreements occurred (3 retrieval gaps + 1 reasoning gap), yielding $a = 15, b = 3, c = 1, d = 38$, $P_o = 53 / 57 = 92.98\%$, $P_e = 0.5808$, and $\kappa_{\text{pos}}^{(A)} = 0.8326$. In Pair B ($N_{\text{pos}} = 57$), 2 retrieval gap disagreements occurred, yielding $a = 9, b = 2, c = 0, d = 46$, $P_o = 55 / 57 = 96.49\%$, $P_e = 0.7101$, and $\kappa_{\text{pos}}^{(B)} = 0.8790$. Across both trials, polarity-stratified reproducibility on positive citation criteria alone achieves pooled $\bar{\kappa}_{\text{pos}} = 0.8558$ ($\kappa_{\text{pos}}^{(A)} = 0.8326, \kappa_{\text{pos}}^{(B)} = 0.8790 > 0.81$), demonstrating that Quorum preserves *Almost Perfect Agreement* even when evaluated exclusively on positive citation criteria.

$^\dagger$*Footnote on Exploratory Baseline `exe_04a0`:* An early developmental pilot run (`exe_04a0`) recorded 128 / 220 passed atoms (58.2%) due to 1 additional positive capability citation extracted in Run B1 (30 vs. 29 positive atoms). All primary benchmark statistics, contingency matrices, and Cohen's kappa values throughout this paper are locked strictly to the 57.7% (127 / 220) production baseline.

### A.3. Ontological Reconciliation: Tripartite Production Schema vs. Homogeneous Benchmark Harness

Across the manuscript, the identical $N = 220$ criteria frames are evaluated under two computationally distinct protocols:

1. **The Physical Production Pipeline (Tables 2–6):**
   Executes on the heterogeneous tripartite ontology ($\mathcal{U}_{\text{total}} = \mathcal{U}_{\text{pos}} \cup \mathcal{U}_{\text{anti}} \cup \mathcal{U}_{\text{topo}}$, $|\mathcal{U}_{\text{total}}| = 114 + 96 + 10 = 220$). Across baseline Runs A1 and B1, the platform recorded 127 passes ($57.73\% \approx 57.7\%$), comprising 29 positive capability demonstrations with verified citations, 94 clean negative anti-patterns requiring zero citations, and 4 macro-topological Guttman tiers.
2. **The Offline Component Ablation Harness (Table 7):**
   Standardizes all 220 frames into a homogeneous diagnostic testbed where every positive assertion is required to extract a citation, and where 29 candidate chimera citations ($19.7\%$ candidate attack pressure)—empirically harvested from unconstrained frontier LLM extraction passes ($21$ synthetic hallucinations and $8$ paraphrased retrieval gaps)—are compiled into the proposition pool to measure the lexical firewall's physical specificity ($\text{Specificity}_{\text{lex}} = 1.000$) deterministically without recurring multi-thousand-dollar API costs. After firewall interception of the 29 unanchored citations and accounting for 2 aleatoric decoding jitter cases ($118 - 2 = 116$), exactly $116 / 220 = 52.73\% \approx 52.7\%$ pass.

The 11-atom difference ($127 - 116 = 11$) is thus an artifact of ontological normalization—specifically the presence of 94 clean anti-pattern passes in production that require no citations—rather than an algorithmic regression, model grading drift, or strictness divergence. Crucially, test–retest reliability remains invariant across both regimes ($P_o = 96.82\%, \bar{\kappa} = 0.9348$ in physical trials; $P_o = 97.27\%, \kappa = 0.9453$ in the benchmark harness), proving that Quorum's Almost Perfect Agreement ($\kappa > 0.90$) is an invariant property of the neurosymbolic architecture.