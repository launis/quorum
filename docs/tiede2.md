# Epistemic Determinism and the Architecture of Causal-Topological Orchestrated Inference in Stochastic Large Language Models: Theoretical Framework, System Architecture, and Empirical Validation



**Quorum Research Collective**

*Preprint — Artificial Intelligence (cs.AI), Computation and Language (cs.CL), Data Structures and Algorithms (cs.DS)*

---

## Abstract

Autoregressive Large Language Models (LLMs) operate as stochastic token probability generators whose unconstrained inference trajectories are inherently vulnerable to hallucination, semantic drift, superlinear error compounding, and epistemic instability. This manuscript presents the **Quorum** architecture: a formal neurosymbolic computational framework and full-stack software platform that transforms unconstrained stochastic generation into a deterministically supervised, epistemically anchored state machine. The theoretical foundation encompasses five core mechanisms: (1) propositional epistemic atomization via an immutable five-tuple Linked Atom Graph (LAG); (2) confluent wave-based execution over a Cognitive Directed Acyclic Graph (Cognitive DAG); (3) Topological Directed Atom (TDA) partial-order scheduling governed by an uncompromising lexical null hypothesis and a five-gate deterministic verification cascade; (4) structural argument evaluation via discrete graph surgery, Assumption-Based Truth Maintenance Systems (ATMS), and Argumentative Structural Causal Models (A-SCM); and (5) a two-factor orthogonal Behaviorally Anchored Rating Scale (BARS) evaluation matrix combining asymmetric Popperian falsification with continuous piecewise power-curve damping. We formalize two foundational architectural principles—confluent wave scheduling under Kahn partial ordering and discrete ATMS warrant reachability—alongside two mathematically verified system properties establishing deterministic lexical error suppression and monotonic Lipschitz score stability. We detail the multi-tier system implementation spanning asynchronous Python orchestration, multi-provider LLM adapters, Server-Driven UI (SDUI) state projection, and cross-platform reactive rendering under European Union Artificial Intelligence Act (EU AI Act) auditability invariants. Empirical validation via an executive strategic foresight audit (Sitra Megatrend dataset, $N = 255$ extracted causal propositions) demonstrates that Quorum reliably penalizes passive conversational delegation (Human Agency score: **11.7%**, Causal Architecture score: **7.2%**) and isolates pseudo-competence despite polished linguistic presentation (mechanical jargon load of $0.00 / 2.0$ versus cognitive authenticity of $1.47 / 3.0$, yielding a Form-to-Content Disparity Ratio of $1.53$).

---

## 1. Introduction and Problem Formulation

An autoregressive language model is formally parameterized as a conditional probability distribution over a discrete token vocabulary $\mathcal{V}$:

$$P(Y \mid X; \theta) = \prod_{t=1}^{T} P(y_t \mid y_{<t}, X; \theta), \quad y_t \in \mathcal{V} \tag{1}$$

where $X = (x_1, \dots, x_N)$ denotes an input prompt sequence and $\theta \in \mathbb{R}^D$ represents static neural network parameters. Although contemporary frontier models generate syntactically fluent discourse, their epistemic reliability in high-stakes analytical workflows is fundamentally constrained by three structural failure modes:

1. **Aleatoric Uncertainty and Calibration Divergence:** The conditional distribution $P(Y \mid X; \theta)$ models statistical token co-occurrence frequencies across pretraining corpora rather than objective truth values ($\mathcal{T} \neq \mathcal{P}$). Consequently, autoregressive sampling routinely yields statistically plausible assertions that lack empirical or textual grounding.


2. **Conflation of Association with Causation:** Self-attention mechanisms capture symmetric statistical associations $P(A \mid B)$ but cannot structurally distinguish a directed causal mechanism ($B \to A$) from common-cause confounding ($C \to A \land C \to B$) or reverse causation ($A \to B$).


3. **Superlinear Error Cascade:** In unconstrained multi-step generation, minor semantic drift at decoding step $t$ conditions the probability distribution at step $t+1$, causing estimation errors to compound exponentially across extended reasoning trajectories:



$$\mathbb{E}\left[\|\hat{y}_{t+k} - y^*_{t+k}\|\right] \sim \mathcal{O}\left(e^{\lambda k}\right), \quad \lambda > 0 \tag{2}$$

To eliminate these vulnerabilities, the Quorum architecture strips the generative model of autonomous state transition authority. Within Quorum, the LLM is restricted to functioning as a stateless, syntactically constrained propositional sensor, while all control flow, state transitions, topological dependency resolution, and evidentiary scoring are governed by an external, mathematically verified neurosymbolic runtime.

---

## 2. Epistemic Atomization and Topological Wave Scheduling

### 2.1. The Atomization Morphism and Linked Atom Graph (LAG)

Let an unstructured natural language document or multi-turn discourse history over alphabet $\Sigma$ be denoted as $\mathcal{D} \in \Sigma^*$. We define the epistemic atomization morphism $\alpha: \Sigma^* \to \mathcal{A}$, which decomposes raw discourse into a finite set of minimal, mutually independent propositional assertions:

$$\mathcal{A} = \{ a_1, a_2, \dots, a_n \} \tag{3}$$

**Definition 1 (Epistemic Atom).** Each epistemic atom $a_i \in \mathcal{A}$ is structured as an immutable five-tuple:

$$a_i = \langle \tau_i, \mathcal{C}_i, \sigma_i, \pi_i, \kappa_i \rangle \tag{4}$$

where the constituent elements satisfy the following formal invariants:

* $\tau_i \in \mathcal{L}_{\text{prop}}$ is an atomic proposition expressed in formal logic with unambiguous, truth-evaluable acceptance criteria.


* $\mathcal{C}_i \subset \Sigma^*$ is the spatial and contextual bounding box isolating the exact verbatim character span in $\mathcal{D}$ from which $\tau_i$ is derived.


* $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ is the speaker attribution index, partitioning human supervisory steering from synthetic model outputs.


* $\pi_i \in \{+1, -1\}$ is the evidentiary polarity index, where $\pi_i = +1$ designates a constructive capability assertion and $\pi_i = -1$ designates an asymmetric Popperian anti-pattern detector targeting cognitive fallacies, uncritical delegation, or structural omissions.


* $\kappa_i \in \{0, 1\}$ is the deterministic lexical provenance anchoring index governed by a strict null hypothesis parameterized by evaluation strictness $\theta \in [0, 100]$:



$$\kappa_i = \begin{cases} 1, & \text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta) \;\land\; \text{Prov}(\mathcal{C}_i, \sigma_i) \;\land\; \text{Triangulate}(\mathcal{T}_i, \mathcal{C}_i) \\ 0, & \text{otherwise} \end{cases} \tag{5}$$

In Equation (5), $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta)$ evaluates a deterministic lexical verification cascade over Unicode NFKC/NFD normalized strings $\text{Norm}(\cdot)$, collapsing to exact substring containment $\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1$ at $\theta \ge 100$ and incorporating bounded morphological stem-sequence verification for agglutinative inflections at $\theta < 100$. The predicate $\text{Prov}(\mathcal{C}_i, \sigma_i)$ enforces XML-fenced speaker capsule isolation, and $\text{Triangulate}(\mathcal{T}_i, \mathcal{C}_i)$ verifies internal reasoning trace consistency against physical syntactic anchors.

**The Syntactic Provenance vs. Semantic Entailment Boundary.** Exact substring containment proves *physical provenance*—confirming that citation $\mathcal{C}_i$ exists verbatim in $\mathcal{D}$ and was not fabricated or spliced across disparate paragraphs—but string matching alone cannot decide universal semantic entailment ($\mathcal{C}_i \models \tau_i$), which is undecidable over arbitrary unconstrained text by Rice's Theorem. Quorum resolves this boundary without relapsing into second-order LLM stochasticity by ensuring that propositions $\tau_i$ are **never freely invented by the generative model at runtime**. Instead, target propositions $\tau_i$ are pre-compiled, versioned evaluation criteria defined within Single Source of Truth (SSOT) Behaviorally Anchored Rating Scale (BARS) rubrics. The stochastic model is restricted to locating the verbatim textual span $\mathcal{C}_i$ that satisfies the pre-defined rubric invariant $\tau_i$, guarded by contrastive pair boundaries and deterministic Python verification gates. If physical containment or provenance fails, $\kappa_i = 0$ and the atom fails closed unconditionally.

**Symbolic Interface Grounding and Subword Entropy Suppression.** In persistent storage, epistemic atoms $a_i \in \mathcal{A}$ are indexed via high-entropy 128-bit universally unique identifiers ($\mathcal{I}_{\text{UUID}}$, UUIDv4 hexadecimal strings). Exposing raw multi-token UUID strings to an autoregressive prompt context causes severe Byte-Pair Encoding (BPE) fragmentation (5–10 subword tokens per identifier), inducing attention dispersion, positional decay across long contexts, and character transposition hallucinations during decoding. To insulate the generative sensor from database storage identifiers, the neurosymbolic boundary executes an ephemeral bijective alias morphism prior to prompt construction:

$$\mu: \mathcal{I}_{\text{UUID}} \longleftrightarrow \mathcal{V}_{\text{alias}}, \quad \mathcal{V}_{\text{alias}} = \{a_0, a_1, \dots, a_{n-1}\}$$

This bijection compresses each propositional identifier into a single-token Attention Anchor ($a_k$) while constraining output decoding logits to the closed categorical support $\mathcal{V}_{\text{alias}}$ via dynamically compiled schema literals. Upon response receipt, the runtime executes deterministic $\mathcal{O}(1)$ inverse hydration $\mu^{-1}(a_k)$, immediately halting execution with a fail-fast validation error if an unmapped alias is encountered.

**Linked Atom Graph Topology.** Extracted atoms are assembled into a directed, attributed multi-graph $\mathcal{G}_{\text{LAG}} = (\mathcal{A}, \mathcal{E}_{\text{dep}}, \mathcal{E}_{\text{temp}}, \mathcal{E}_{\text{causal}})$, encoding logical dependency, temporal sequence, and inferred causal transmission. To prevent misclassifying foundational premises as unsubstantiated claims, root nodes ($\text{InDegree}(a_i) = 0$) are partitioned into two mutually exclusive epistemic classes:

1. **Exogenous Boundary Axioms ($\mathcal{A}_{\text{axiom}}$):** Primitive operational constraints or baseline institutional premises ($U_i$) that establish document scope and require no internal textual ancestors.


2. **Unjustified Orphan Claims ($\mathcal{A}_{\text{orphan}}$):** Inferential conclusions asserted without supporting empirical grounds, mediating warrants, or upstream causal links.



---

### 2.2. Cognitive Directed Acyclic Graph (Cognitive DAG) and Wave Execution

Macro-level cognitive operations—including ingress sanitization, two-pass atomic decomposition, structural argument mining, orthogonal matrix evaluation, Popperian falsification, and executive synthesis—are orchestrated across an immutable, acyclic computational network:

$$\mathcal{G}_{\text{DAG}} = (\mathcal{V}_{\text{cog}}, \mathcal{E}_{\text{dep}}) \tag{6}$$

where $\mathcal{V}_{\text{cog}}$ denotes strictly typed computational operators and $\mathcal{E}_{\text{dep}}$ defines explicit state and data dependencies. Because $\mathcal{G}_{\text{DAG}}$ is strictly acyclic, Kahn’s topological sorting algorithm partitions $\mathcal{V}_{\text{cog}}$ into discrete, sequentially ordered parallel execution waves $W_0, W_1, \dots, W_{K-1}$:

$$W_0 = \{ v \in \mathcal{V}_{\text{cog}} \mid \text{InDegree}(v) = 0 \} \tag{7}$$

$$W_{k+1} = \left\{ v \in \mathcal{V}_{\text{cog}} \setminus \bigcup_{j=0}^k W_j \;\middle|\; \text{Parents}(v) \subseteq \bigcup_{j=0}^k W_j \right\} \tag{8}$$

Within each topological wave $W_k$, constituent operators execute concurrently as isolated asynchronous coroutines. Each operator $v \in W_k$ computes a pure deterministic transformation over immutable Data Transfer Objects (DTOs):

$$\Phi_v: \prod_{u \in \text{Parents}(v)} \mathcal{O}_u \times \mathcal{S}_{\text{global}} \to \mathcal{O}_v \tag{9}$$

**Architectural Principle 1 (Confluent Neurosymbolic Wave Scheduling).** Let $\mathcal{G}_{\text{DAG}} = (\mathcal{V}_{\text{cog}}, \mathcal{E}_{\text{dep}})$ be a finite directed acyclic graph partitioned into $K$ disjoint topological waves $W_0, \dots, W_{K-1}$ under Kahn’s partial ordering. Let each operator $\Phi_v$ be a referentially transparent compute function operating exclusively over frozen, immutable DTOs with zero shared mutable state. By the Church–Rosser confluence theorem and the determinism invariants of Kahn Process Networks, any arbitrary asynchronous coroutine completion order or scheduling permutation $\pi \in \text{Perm}(W_k)$ within wave $W_k$ converges to the identical wave output state $\mathcal{O}_{W_k}$, guaranteeing that the global pipeline terminates at a unique, deterministic fixed-point state $\mathcal{S}^ = (\Phi_{W_{K-1}} \circ \dots \circ \Phi_{W_0})(\mathcal{S}_0)$.*

---

### 2.3. Topological Directed Atom (TDA) Poset Scheduling and Five-Gate Verification

Within the Quorum architecture, the acronym **TDA** designates **Topological Directed Atoms** rather than *Topological Data Analysis* (which studies persistent homology and Betti numbers over point clouds). Here, *topological* refers strictly to order-theoretic scheduling via Kahn’s algorithm on finite directed acyclic graphs, inducing an Alexandroff topology and a specialization poset over $\mathcal{G}_{\text{LAG}}$. Circular reasoning chains ($a_1 \implies a_2 \implies \dots \implies a_1$) violate epistemic partial-order invariants and are isolated prior to wave evaluation using Tarjan’s strongly connected components algorithm and Johnson’s elementary cycle enumeration. Nodes participating in directed cycles are immediately quarantined (`CYCLIC_DEPENDENCY_DETECTED`), and downstream nodes left unresolved after topological wave exhaustion are deterministically clamped to `BLOCKED`.

#### 2.3.1. Eradication of Second-Order Hallucination via the Five-Gate Protocol

A pervasive vulnerability in contemporary LLM evaluation paradigms (such as LLM-as-a-Judge, G-Eval, and Self-RAG) is **Second-Order Hallucination**: when a secondary LLM is prompted to judge whether document $\mathcal{D}$ entails proposition $\tau_i$, the evaluator remains an autoregressive sampler susceptible to sycophancy, confirmation bias, and the fabrication of *chimera quotes* stitched from non-contiguous paragraphs. Quorum eliminates second-order hallucination by executing propositional grounding exclusively through a five-gate deterministic verification cascade in pure Python:

1. **Gate 1 — Physical Substring Invariant with Bidirectional Index Mapping:** The source document $\mathcal{D}$ is stripped of formatting artifacts and normalized via Unicode NFKC and NFD diacritic decomposition while maintaining an exact bidirectional character index map $\mathcal{M}_{\text{idx}}: \mathbb{N} \to \mathbb{N}$. Candidate citations $\mathcal{C}_i$ must satisfy $\mathcal{O}(N)$ normalized containment $\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1$, after which the exact verbatim span is sliced directly from the original immutable text.


2. **Gate 2 — Entropy Gate and Contiguity Guard (Chimera Quote Defense):** Candidate spans shorter than 10 characters are prohibited from fuzzy matching and require **100%** exact substring containment. Spans between 10 and 29 characters enforce strict contiguous sequence matching, whereas spans of 30 to 1,000 characters evaluate token-set overlap. Citations exceeding 1,000 characters trigger an immediate fail-fast exception to prevent context stuffing and prompt injection.


3. **Gate 3 — Cross-Speaker Provenance Boundary Guard:** Input discourse is partitioned into XML-fenced provenance capsules separating human supervisor input (`<user_payload>`), synthetic model drafts (`<ai_draft_context>`), and task instructions (`<assignment_context>`). Formally, provenance verification requires:



$$\text{Prov}(\mathcal{C}_i, \sigma_i) = \mathbb{I}\left( \text{Lex}(\mathcal{C}_i, \mathcal{D}_{\text{speaker}}; \theta) = 1 \right)$$

Quoting an AI assistant draft to substantiate a human agency claim ($\sigma_i = \text{USER}$) triggers an immediate provenance violation, preventing cross-speaker competence contamination.
4. **Gate 4 — Reasoning Trace Triangulation:** The structured extraction schema requires an explicit reasoning trace $\mathcal{T}_i$ declaring a verbatim syntactic anchor and a binary validation decision. Deterministic triangulation rejects the atom if (i) $\mathcal{T}_i$ concludes `FAIL` while populating $\mathcal{C}_i$, (ii) the syntactic anchor is declared empty (`NONE`), or (iii) the declared anchor does not physically exist in $\mathcal{D}$.
5. **Gate 5 — Calibrated Zero-Trust Strictness Curve and Morphological Stemming Cascade:** For strictness $\theta < 100$, $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta)$ executes a four-tier fallback cascade: (i) exact NFKC/NFD substring containment; (ii) length-stratified Levenshtein similarity scaled by tier multipliers ($\times 0.80$ for $\theta < 30$, $\times 0.90$ for $\theta \in [30, 50)$, $\times 1.00$ for $\theta \in [50, 85)$, and $\times 1.02$ for $\theta \in [85, 100)$); (iii) multilingual rule-based Snowball morphological stemmed subsequence matching to accommodate highly inflected agglutinative languages such as Finnish; and (iv) contiguous longest-common-substring coverage verification. At $\theta \ge 100$ (Absolute Zero-Trust), tiers (ii)–(iv) are disabled, enforcing **100%** exact substring containment.

**Mathematical Property 1 (Deterministic Epistemic Error Suppression).** Let an ensemble of $M$ LLM evaluators exhibit pairwise error correlation $\text{Cov}(X_i, X_j) = \rho_{ij} \ge \rho_{\min} > 0$ due to shared pretraining corpora. Under symmetric majority voting, the effective sample size is bounded asymptotically by $M_{\text{eff}} = \frac{M}{1 + (M-1)\bar{\rho}} \to \frac{1}{\bar{\rho}} < \infty$ as $M \to \infty$ (Equation 19), causing consensus error to converge to $1$ whenever shared pretraining attractors induce individual error probability $p > 0.5$. Quorum breaks symmetric voting via Role-Asymmetric Popperian Falsification ($\pi_i = -1$), requiring joint survival across extraction and adversarial audit:

$$P(\text{Claim Pass}) = P(\text{Extracted}) \cdot (1 - P(\text{Falsified} \mid \text{Extracted})) \tag{20}$$

Combined with the deterministic lexical firewall $\kappa_i = \mathbb{I}(\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1) \in \{0, 1\}$ (Equation 21), a hallucinated assertion $a_{\text{halluc}}$ can be accepted by the system if and only if its fabricated citation physically collides with an existing substring in $\mathcal{D}$:

$$P(\text{System False Accept}) = P_{\text{prior}}(\text{Hallucination}) \cdot P(\text{find}(\mathcal{C}_{\text{halluc}}, \mathcal{D}) \neq -1) \le \epsilon_{\text{lexical}} \to 0 \tag{18, 22}$$

where $\epsilon_{\text{lexical}}$ is the random string collision rate over finite document length $|\mathcal{D}|$, decoupling false-acceptance suppression from inter-model correlation $\bar{\rho}$.

---

## 3. Argumentative Structural Causal Models (A-SCM) and Truth Maintenance

### 3.1. Formalization of the Discourse A-SCM and the Enthymeme Boundary

Unlike physical data-generating processes governed by observational probability distributions, natural language argumentation is pragmatic, elliptical, and enthymematic: human authors routinely omit background premises and intermediate mechanisms. Consequently, Quorum does not claim to infer physical empirical causality from text alone; rather, it formalizes an **Argumentative Structural Causal Model (A-SCM)** to audit the *internal explanatory sufficiency and structural warrant rigor* of an authored thesis.

**Definition 2 (Argumentative Structural Causal Model).** An authored discourse is modeled as a five-tuple:

$$\mathcal{M}_{\text{arg}} = \langle \mathbf{U}, \mathbf{V}, \mathbf{W}, \mathbf{F}, P(\mathbf{U}) \rangle \tag{10}$$

where $\mathbf{V} = \{V_1, \dots, V_n\}$ denotes explicit propositional claims anchored in verbatim text ($\kappa = 1$), $\mathbf{W}$ denotes explicit Toulmin warrants specifying mediating explanatory mechanisms, $\mathbf{U} = \{U_{\text{enthymeme}}, U_{\text{context}}\}$ represents unstated background assumptions and latent conversational confounders, and $\mathbf{F} = \{f_1, \dots, f_m\}$ defines structural argument dependencies over parent claims $\mathbf{PA}_i \subseteq \mathbf{V} \setminus \{V_i\}$:

$$V_i = f_i(\mathbf{PA}_i, \mathbf{W}_i, U_i) \tag{11}$$

---

### 3.2. Discrete Structural Graph Surgery and ATMS Reachability

In classical structural causal modeling, an intervention on variable $X$ replaces its structural mechanism with a constant assignment $X = x^*$, severing all incoming edges in the mutilated graph $\mathcal{G}_{\overline{X}}$. Unlike observational *do*-calculus—which identifies interventional distributions $P(Y \mid \text{do}(X))$ from joint probability distributions via backdoor adjustment summations—discrete discourse analysis contains no continuous random variables. Quorum operationalizes graph mutilation ($\mathcal{G}_{\overline{X}}$) as deterministic premise retraction within an **Assumption-Based Truth Maintenance System (ATMS)**, executed in $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ time in pure Python without secondary LLM calls, as specified in Algorithm 1.

```
Algorithm 1: Discrete Structural Argument Surgery & Truth Maintenance (ATMS)
================================================================================
Input  : Argument DAG G = (V, E, W), perturbed node X in V,
         counterfactual state x* in {FAILED, BLOCKED},
         gate semantics mode in {CONJUNCTIVE_AND, DISJUNCTIVE_OR}
Output : Perturbed state mapping S*, Reachability Cascade Reach(X), Root Causes RC
================================================================================
1: S* <- InitialStateMap(V)                          // Base status from lexical grounding Gate
2: E_cut <- E \ { (P, X) | P in Parents(X) }         // Sever incoming parent edges (G_bar_X)
3: S*[X] <- x*                                       // Clamp intervened node to counterfactual state
4: Queue Q <- [ X ]
5: Visited Vis <- { X }
6: Cascade <- []
7: while Q is not empty do
8:     curr <- Q.pop_front()
9:     for each child C in Children(curr, E_cut) do
10:        if C not in Vis then
11:            if mode == CONJUNCTIVE_AND then
12:                // Forward Kahn Wave Scheduling: Any antecedent failure blocks C
13:                survives_gate <- forall P' in Parents(C, E_cut): S*[P'] == expected_status(P', C)
14:            else
15:                // Corroborative Warrant Redundancy: Alternative valid warrant shields C
16:                survives_gate <- exists P' in Parents(C, E_cut) \ Vis
17:                                 such that S*[P'] == PASSED and kappa(W_{P'C}) == 1
18:            end if
19:            if not survives_gate then
20:                S*[C] <- BLOCKED                      // (or N_A on precondition mismatch)
21:                Vis.add(C)
22:                Cascade.append(C)
23:                Q.push_back(C)
24:            end if
25:        end if
26:    end for
27: end while
28: RC <- { v in V | S*[v] in {FAILED, BLOCKED} and BlameParents(v) == emptyset }
29: return (S*, Cascade, RC)
================================================================================

```

Algorithm 1 governs two complementary execution regimes across the reasoning pipeline:

* **Forward Conjunctive Wave Scheduling (`CONJUNCTIVE_AND`):** During real-time DAG evaluation, every upstream parent $P' \in \text{Parents}(C)$ serves as a necessary precondition. If any antecedent fails or violates its expected status, child node $C$ deterministically short-circuits to `BLOCKED` or `N_A`, pruning dependent nodes prior to LLM invocation.


* **Backward Fault Attribution and Corroborative Simulation (`DISJUNCTIVE_OR`):** Following graph extraction, backward traversal over inbound dependencies (`in_deps`) isolates primary epistemic breakdown points (`RC`, where $\text{BlameParents}(v) = \emptyset$) from secondary cascading failures, preventing double penalization of downstream conclusions while supporting interactive counterfactual redundancy auditing.



**Architectural Property 2 (Warrant Independence and Cascade Fault Isolation).** Let an Argumentative Discourse SCM be compiled into a discrete DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{atom}}, \mathcal{E}_{\text{deps}})$ with lexically anchored claims $\mathbf{V}$ and warrants $\mathbf{W}$ ($\kappa = 1$). If structural surgery $\text{do}(X = \text{FAILED})$ on $\mathcal{G}_{\overline{X}}$ propagates failure to $Y$ ($\text{Reach}(\mathcal{G}_{\overline{X}}, X) \cap \{Y\} \neq \emptyset$) while reverse surgery leaves $X$ invariant ($X \notin \text{Reach}(\mathcal{G}_{\overline{Y}}, Y)$), topological asymmetry holds:

$$(X \perp_{\mathcal{G}_{\overline{Y}}} Y) \implies Y \notin \text{Ancestors}(X) \quad \text{and} \quad (Y \not\!\perp_{\mathcal{G}_{\overline{X}}} X) \implies X \in \text{Ancestors}(Y) \tag{23, 24}$$

If an unstated enthymeme $U_{\text{enthymeme}}$ induces a spurious rhetorical leap $X \leftarrow U_{\text{enthymeme}} \to Y$ without an explicit warrant ($\mathbf{W}_{XY} = \emptyset$), intervention $\text{do}(X = \text{FAILED})$ yields:

$$\text{BlameParents}(Y) = \{ X \} \implies \text{Status}(Y) \gets \text{BLOCKED} \tag{25}$$

Conversely, an explicit, lexically grounded warrant $\mathbf{W}_{XY}$ ($\kappa(\mathbf{W}_{XY}) = 1$) establishes a verifiable transmission mechanism $X \xrightarrow{\mathbf{W}_{XY}} Y$, shielding the inference from enthymemic collapse.

This topological audit operationalizes three hierarchical rungs of argumentative rigor:

* **Rung 1 (Associative Co-occurrence):** Unidirectional correlation or trend listing lacking explicit warrants ($\mathbf{W} = \emptyset$), incurring passive delegation penalties.


* **Rung 2 (Intervention Audit and Warrant Isolation):** Explicit articulation of operational transmission mechanisms $\mathbf{W}_{XY}$ isolating claims from background confounders $U_{XY}$.


* **Rung 3 (Counterfactual Stress-Testing):** Explicit evaluation of boundary failure thresholds, resource exhaustion limits, and negative externalities under counterfactual perturbations.



---

## 4. Psychometric Evaluation: Two-Factor Orthogonal BARS Scoring and Multi-Matrix Governance

### 4.1. Sovereign Intra-Matrix Scoring Kernel and Lipschitz Stability

Each evaluation matrix implements a Behaviorally Anchored Rating Scale (BARS) distributed across five hierarchical competence tiers $l \in \{1, \dots, 5\}$ weighted linearly by $w(l) = l$. Every evaluated atom $a_i \in \mathcal{A}$ resolves to a discrete state:

$$\omega(a_i) \in \{ \text{PASSED}, \text{FAILED}, \text{DLQ} \} \tag{12}$$

where $\text{DLQ}$ (Dead-Letter Queue) isolates unresolvable runtime exceptions. For constructive capability criteria ($\pi_i = +1$), achieved points $A$ and effective maximum points $M$ are aggregated across all five tiers:

$$A = \sum_{l=1}^5 l \cdot h_l, \quad M = \sum_{l=1}^5 l \cdot (t_l - d_l) \tag{13}$$

where $h_l$ denotes verified passes, $t_l$ denotes total tier criteria, and $d_l$ denotes $\text{DLQ}$ exceptions at tier $l$, dynamically excluding system faults from the denominator. The linear capability ratio $\rho$ is protected against division-by-zero singularities:

$$\rho = \begin{cases} \frac{A}{M}, & M > 0 \\ 0.0, & M \le 0 \end{cases} \tag{14}$$

Negative anti-pattern criteria ($\pi_i = -1$) operate as multiplicative Popperian gatekeepers. Confirmed anti-pattern violations ($\kappa_i = 1$) register fractional deductions $p_k \in (0, 1)$, yielding the composite falsification multiplier bounded by a maximum deduction ceiling $P_{\max} = 0.40$ (**40%**):

$$\Pi_{\text{penalty}} = \begin{cases} \max\left( 1 - P_{\max}, \; \prod_{k=1}^K (1 - p_k) \right), & K > 0 \\ 1.0, & K = 0 \end{cases} \tag{15}$$

To prevent score inflation from clustering at trivial lower tiers ($l \in \{1, 2\}$), the user-configured strictness parameter $\theta \in [0, 100]$ maps to a continuous piecewise linear damping exponent $\gamma(\theta) \in [1.00, 2.20]$:

$$\gamma(\theta) = \begin{cases} 1.00, & \theta \le 0 \\ 1.00 + \left(\frac{\theta}{50}\right) \cdot 0.25, & 0 < \theta \le 50 \\ 1.25 + \left(\frac{\theta - 50}{35}\right) \cdot 0.45, & 50 < \theta \le 85 \\ 1.70 + \left(\frac{\theta - 85}{15}\right) \cdot 0.50, & 85 < \theta \le 100 \\ 2.20, & \theta > 100 \end{cases} \tag{16}$$

The sovereign intra-matrix score across matrix bounds $[S_{\min}, S_{\max}]$ is then computed as:

$$\text{Score}(\rho) = \begin{cases} S_{\min} + \left( \rho^{\gamma(\theta)} \cdot \Pi_{\text{penalty}} \right) \cdot (S_{\max} - S_{\min}), & M > 0 \\ S_{\min}, & M \le 0 \end{cases} \tag{17}$$

**Mathematical Property 2 (Score Monotonicity and Lipschitz Stability).** For any calibrated strictness exponent $\gamma(\theta) \ge 1.0$ and falsification multiplier $\Pi_{\text{penalty}} \in [0.60, 1.0]$, Equation (17) is continuously differentiable on $[0, 1]$ and satisfies two analytical stability invariants:

1. **Strict Monotonicity:** $\frac{\partial \text{Score}}{\partial \rho} = \gamma \rho^{\gamma - 1} \Pi_{\text{penalty}} (S_{\max} - S_{\min}) \ge 0$ for all $\rho \in [0, 1]$, ensuring that satisfying an additional capability criterion never decreases the evaluation score.


2. **Bounded Lipschitz Continuity:** Because $\frac{\partial^2 \text{Score}}{\partial \rho^2} \ge 0$ on $[0, 1]$, the derivative attains its supremum at the upper boundary $\rho = 1$, yielding the exact Lipschitz constant $K_L = \gamma \Pi_{\text{penalty}} (S_{\max} - S_{\min})$. By the Mean Value Theorem, $|\text{Score}(\rho_1) - \text{Score}(\rho_2)| \le K_L |\rho_1 - \rho_2|$, guaranteeing that bounded boundary noise cannot induce discontinuous cliff-edge score collapse.



---

### 4.2. Multi-Matrix Orthogonal Vector Space ($\mathbf{\Psi}$) and Two-Tier Governance

Evaluating human-AI collaboration through a single scalar dimension creates diagnostic blind spots: auditing only the final synthetic output ($\sigma_i = \text{ASSISTANT}$) rewards fluent prose even when the human operator acted as a passive bystander, whereas auditing only conversational prompts ($\sigma_i = \text{USER}$) risks an **Illusion of Control** when concise prompting yields an epistemically hollow deliverable.

Quorum resolves this by projecting discourse $\mathcal{D}$ into a $D$-dimensional orthogonal matrix vector space $\mathcal{M} = (\mathcal{M}_1, \dots, \mathcal{M}_D)$, where each matrix interrogates an XML-isolated speaker capsule concurrently within the same topological wave:

$$\mathbf{\Psi}(\mathcal{D}; \theta) = \begin{bmatrix} \text{Score}_{\mathcal{M}_1}\left(\rho_1, \Pi_{\text{penalty}}^{(1)}; \theta\right) \\ \text{Score}_{\mathcal{M}_2}\left(\rho_2, \Pi_{\text{penalty}}^{(2)}; \theta\right) \\ \vdots \\ \text{Score}_{\mathcal{M}_D}\left(\rho_D, \Pi_{\text{penalty}}^{(D)}; \theta\right) \end{bmatrix} \in \prod_{d=1}^D \left[ S_{\min}^{(d)}, S_{\max}^{(d)} \right] \tag{17a}$$

Standard enterprise audits partition $\mathbf{\Psi}(\mathcal{D}; \theta)$ across three cross-validating dimensions: (1) the **Human Agency & Collaboration Matrix** ($\mathcal{M}_{\text{HACM}}, \sigma_i = \text{USER}$), auditing cognitive steering and adversarial verification; (2) the **Epistemic & Causal Architecture Matrix** ($\mathcal{M}_{\text{Causal}}, \sigma_i = \text{ASSISTANT}$), auditing Toulmin warrants, orphan claim density, and counterfactual testing; and (3) **Domain Substance Matrices** ($\mathcal{M}_{\text{Domain}}, \sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$), auditing specialized task constraints.

To maintain separation of concerns between intra-matrix psychometrics and workflow-level policy, scoring executes across a **Two-Tier Governance Hierarchy**:

* **Tier A — Sovereign Intra-Matrix Kernel:** Computes Equation (17) in isolation for each matrix $m$, producing an immutable result without accessing external workflow state or global database lookups.


* **Tier B — Macro-Workflow Consolidation and Observer Hooks:** A post-execution hook pipeline first projects each raw matrix score onto a commensurate $[0.0, 100.0]$ scale:



$$\text{Normalized\_Score}_m = \left( \frac{\text{raw\_score}_m - \text{computed\_min}_m}{\text{computed\_max}_m - \text{computed\_min}_m} \right) \times 100.0$$

Subsequently, an observer hook inspects whether any matrix resolved to its mathematical floor ($S_{\min}$) with zero positive capability hits, emitting a passivity flag if detected. Macro-level workflow deductions (comprising security injection, post-hoc excuse, and passivity penalties, capped at $P_{\max} = 0.40$) are then applied to the unweighted mean $\text{average\_score} = \frac{1}{N} \sum_{m=1}^N \text{Normalized\_Score}_m$:

$$\text{global\_score} = \text{round}\left( \max\left(0.0, \; \text{average\_score} \times \left(1.0 - \min(\text{total\_penalty}, P_{\max})\right)\right), \; 1 \right)$$

Concurrently, the presentation layer preserves the uncollapsed vector $\mathbf{\Psi}(\mathcal{D}; \theta)$ and exposes the **Agency-to-Outcome Divergence** across normalized matrix scores $\hat{S}(\cdot) \in [0, 1]$:

$$\Delta_{\text{agency-outcome}} = \left\vert{} \hat{S}(\mathcal{M}_{\text{HACM}}) - \hat{S}(\mathcal{M}_{\text{Domain/Causal}}) \right\vert{} \tag{17b}$$

---

### 4.3. Two-Sided Lexical Proof Burden and Classical Theoretical Grounding

Both polarity tracks enforce a strict lexical proof burden governed by contrastive pairs (`acceptable` positive anchor versus `rejected` distractor):

* **Constructive Capabilities ($\pi_i = +1$):** Default to unproven ($h_l = 0$) and transition to $\text{PASSED}$ only if an extracted citation $\mathcal{C}_i$ from speaker $\sigma_i$ matches the positive anchor, avoids the negative distractor, and passes all five physical verification gates ($\kappa_i = 1$).


* **Popperian Anti-Patterns ($\pi_i = -1$):** Default to clean performance ($\Pi_{\text{penalty}} = 1.0$) and trigger a multiplicative deduction $p_k$ only if the sensor extracts a verbatim citation passing all five verification gates ($\kappa_i = 1$) proving the violation occurred, mathematically preventing hallucinated penalties.



As synthesized in Table 1, all evaluation rubrics are compiled via **Design-Time Human Curation** anchored to classical cognitive and decision sciences, ensuring longitudinal psychometric invariance.

| Matrix Dimension & Speaker ($\sigma_i$) | Rubric Track | Classical Theoretical Grounding | Constructive Capability Tiers ($\pi_i = +1$, BARS Levels $l \in \{1, \dots, 5\}$) | Popperian Anti-Pattern Falsifiers ($\pi_i = -1$, Malus Multiplier $\Pi_{\text{penalty}}$) |
| --- | --- | --- | --- | --- |
| **1. Human Agency & Collaboration (HACM)**<br>

<br>$\sigma_i = \text{USER}$<br> | **Track A**<br>

<br>(Developmental)

 | Sheridan & Verplank (1978); Parasuraman et al. (2000); Kahneman (2011); Buçinca et al. (2021)

 | **L1–L2:** Task framing and context bounding.<br>

<br>**L3:** Explicit constraints and criteria.<br>

<br>**L4:** Adversarial challenging and error correction.<br>

<br>**L5:** Metacognitive steering and hypothesis forcing.

 | **Automation Bias & Passivity:** Unconstrained task abdication; blind rubber-stamping of first drafts; relinquishing verification; vacuous prompts.

 |
| **2. Argumentative & Causal Structure (A-SCM)**<br>

<br>$\sigma_i = \text{ASSISTANT}$<br> | **Track B**<br>

<br>(Error Radar)

 | Pearl (2009) (*Causal Ladder*); Toulmin (1958) (*Argumentation*)

 | **L1–L2 (Rung 1):** Variable and correlation identification.<br>

<br>**L3 (Warrant):** Explicit mechanism $\mathbf{W}_{XY}$.<br>

<br>**L4 (Rung 2):** Confounder isolation ($U$) and side effects.<br>

<br>**L5 (Rung 3):** Counterfactual boundary stress-testing.

 | **Structural Collapse:** Correlation-causation conflation; orphan claims ($\mathcal{A}_{\text{orphan}}, \mathbf{W} = \emptyset$); circular loops; missing rebuttals.

 |
| **3. Critical Thinking & Epistemic Rigor**<br>

<br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$<br> | **Track A & B**<br>

<br>(Hybrid)

 | Bloom (1956) (*Cognitive Taxonomy*); Popper (1959) (*Falsifiability*)

 | **L1–L2:** Nomenclature and baseline recall.<br>

<br>**L3:** Deconstructing latent assumptions.<br>

<br>**L4:** Evidence weighting and falsification criteria.<br>

<br>**L5:** Testable explanatory synthesis.

 | **Epistemic Immunization:** Confirmation bias; unfalsifiable tautologies; evasive prose; rhetorical buzzword substitution (*Jargon Load*).

 |
| **4. Domain & Task-Specific Substance**<br>

<br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$<br> | **Track B**<br>

<br>(Substantive)

 | Smith & Kendall (1963) (*BARS Anchoring*) & Domain Law/Strategy

 | **L1–L2:** Baseline case parameters.<br>

<br>**L3:** Standard operational remedies.<br>

<br>**L4:** Liability vs. stakeholder equity; root causes.<br>

<br>**L5:** Systemic risk containment and strategic value.

 | **Substantive Professional Errors:** Defensive externalization; premature liability admission; vacuous apologies; naive linear trend extrapolation.

 |

**Table 1:** Orthogonal multi-matrix rubric architecture mapping classical cognitive, causal, and psychometric theories to constructive capability tiers and Popperian falsifiers.

---

## 5. Full-Stack System Architecture and Error Suppression Pipeline

### 5.1. Multi-Tier Software Architecture

The Quorum platform operationalizes its theoretical invariants across a modular three-tier software architecture:

1. **Neurosymbolic Backend Runtime (`backend_v2`):** Implemented in Python using strictly typed, frozen Pydantic V2 domain models and DTOs (`models/`). The orchestration layer (`services/orchestrator/`) houses the asynchronous Kahn wave executor (`dag_executor.py`), the two-pass epistemic atomizer (`atomizer.py`, `two_pass_atomizer.py`), the TDA poset evaluator (`tda_engine.py`), the backward fault attribution engine (`causal_discovery_engine.py`), and the constrained synthesis engine (`synthesis_engine.py`). A multi-provider LLM adapter layer (`llm/`) abstracts context management, prompt compilation, caching, and constrained decoding across Google AI Studio, Vertex AI, Anthropic Claude, OpenAI, and DeepSeek (`ai_studio_adapter.py`, `vertex_adapter.py`, `anthropic_adapter.py`, `openai_adapter.py`, `deepseek_adapter.py`). Hybrid persistence (`database/`, `services/drivers/`) integrates PostgreSQL and Firestore repositories, verified by unit, integration, guardrail, and end-to-end regression suites (`tests/`).


2. **Server-Driven UI Projection Layer (`services/sdui/`):** To prevent client-side business logic drift, backend SDUI mappers transform evaluated matrix vectors $\mathbf{\Psi}(\mathcal{D}; \theta)$, causal multi-graphs $\mathcal{G}_{\text{LAG}}$, and XAI variance diagnostics into declarative presentation payloads.


3. **Cross-Platform Reactive Client (`client_app_v2`) and Governance Specification (`docs/`):** Built with Flutter and Dart for desktop and web deployment, utilizing Riverpod for reactive state management, GoRouter for declarative routing, Freezed for immutable client data models, and bilingual Finnish/English localization (`l10n/`). Functional modules (`features/`) encompass real-time execution monitoring and SDUI rendering (`execution/sdui_blocks_renderer.dart`), interactive DAG workflow and BARS rubric construction (`studio/workflow_builder_view.dart`), audit report export (`reports/`), and access control (`auth/`, `settings/`), engineered in alignment with multi-layered architectural specifications (`docs/architecture/` sections 00–09) and EU AI Act auditability standards.



---

### 5.2. Four-Stage Cascade Suppression Pipeline and Two-Tier Verification

Across the end-to-end execution lifecycle, input state $\mathcal{S}_{\text{in}}$ corrupted by stochastic semantic noise $\xi$ is filtered through four sequential deterministic barriers:

$$\mathcal{S}_{\text{out}} = (\Phi_{\text{synth}} \circ \Phi_{\text{score}} \circ \Phi_{\text{fals}} \circ \Phi_{\text{TDA}} \circ \Phi_{\text{ingress}})(\mathcal{S}_{\text{in}} + \xi) \tag{26}$$

* **Barrier 1 (Ingress Sanitization & Capsule Isolation, $\Phi_{\text{ingress}}$):** Strips prompt injection payloads, normalizes Unicode representations, and fences speaker attribution indices $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$.


* **Barrier 2 (TDA Grounding & Poset Verification, $\Phi_{\text{TDA}}$):** Enforces the lexical null hypothesis ($\kappa_i = 0$ on verification failure) across the five-gate Python cascade and quarantines cyclic or unanchored dependencies.


* **Barrier 3 (Asymmetric Falsification & Best-of-3 Consensus, $\Phi_{\text{fals}}$):** Evaluates high-entropy propositions via a parallel Best-of-3 ensemble (`ensemble_parallelism = 3`, `ensemble_min_consensus = 2`) with Popperian null-hypothesis tie-breaking and multiplicative anti-pattern deductions ($\Pi_{\text{penalty}}$).


* **Barrier 4 (Lipschitz Damping & Constrained Synthesis, $\Phi_{\text{score}} \circ \Phi_{\text{synth}}$):** Applies piecewise power-curve damping $\rho^{\gamma(\theta)}$, enforces the **40%** macro penalty cap ($P_{\max} = 0.40$), and restricts the terminal synthesis engine to rendering verified graph state without introducing unanchored claims.



To balance verification rigor with FinOps token economics, Quorum separates live execution from cross-provider benchmarking via a **Two-Tier Verification Strategy**: production DAG waves execute single-model Best-of-3 ensembles via asynchronous coroutine groups using the step's assigned model configuration, whereas computationally intensive multi-provider variance benchmarking across Gemini, Claude, OpenAI, and DeepSeek is decoupled into offline evaluation workers. Furthermore, to prevent cross-tenant memory leakage in distributed worker pools (such as Celery or Arq), bijective alias mappings $\mu$ are instantiated per execution job and serialized across worker boundaries via immutable `AliasManifest` snapshots.

---

## 6. Empirical Validation: The Sitra Strategic Foresight Audit

### 6.1. Experimental Setup and Quantitative Matrix Reconciliation

To empirically validate the framework, Quorum audited an executive strategic foresight task based on the Finnish Innovation Fund Sitra Megatrend dataset (2017–2023). The evaluation concurrently audited the human supervisor's conversational steering (`Chat`, $\mathcal{M}_{\text{HACM}}, \sigma_i = \text{USER}$) and the resulting strategic report (`Lopputuote`, $\mathcal{M}_{\text{Causal}}, \sigma_i = \text{ASSISTANT}$) at calibrated strictness $\theta = 50\%$ ($\gamma(50) = 1.25$). Table 2 presents the complete psychometric reconciliation for Execution ID `exe_c0953f62f2014b40`.

| Evaluation Parameter | HACM Matrix ($\mathcal{M}_{\text{HACM}}$, Chat) | Causal Matrix ($\mathcal{M}_{\text{Causal}}$, Report) |
| --- | --- | --- |
| **Execution Identifier** | `exe_c0953f62f2014b40`<br> | `exe_c0953f62f2014b40`<br> |
| **Total Rubric Criteria Evaluated** | 25

 | 25

 |
| **Popperian Anti-Pattern Checks ($\pi_i = -1$)** | 13 / 13 clean

 | 13 / 13 clean

 |
| **Falsification Multiplier ($\Pi_{\text{penalty}}$)** | $1.0000$<br> | $1.0000$<br> |
| **Constructive Capability Criteria ($\pi_i = +1$)** | 12 total

 | 12 total

 |
| **Tier 1 Passed ($w = 1$)** | 2 / 2 ($2.0\text{ pts}$)

 | 1 / 1 ($1.0\text{ pt}$)

 |
| **Tier 2 Passed ($w = 2$)** | 1 / 2 ($2.0\text{ pts}$)

 | 2 / 2 ($4.0\text{ pts}$)

 |
| **Tier 3 Passed ($w = 3$)** | 1 / 2 ($3.0\text{ pts}$)

 | 0 / 3 ($0.0\text{ pts}$)

 |
| **Tier 4 Passed ($w = 4$)** | 0 / 3 ($0.0\text{ pts}$)

 | 0 / 3 ($0.0\text{ pts}$)

 |
| **Tier 5 Passed ($w = 5$)** | 0 / 3 ($0.0\text{ pts}$)

 | 0 / 3 ($0.0\text{ pts}$)

 |
| **Achieved Weighted Points ($A$)** | $7.0\text{ pts}$<br> | $5.0\text{ pts}$<br> |
| **Effective Maximum Points ($M$)** | $39.0\text{ pts}$<br> | $41.0\text{ pts}$<br> |
| **Linear Capability Ratio ($\rho = A / M$)** | **17.95%** ($7 / 39$)

 | **12.20%** ($5 / 41$)

 |
| **Strictness Damping Exponent ($\gamma$ at $\theta = 50\%$)** | $1.2500$<br> | $1.2500$<br> |
| **Damped Capability Ratio ($\rho^{1.25}$)** | $0.116827$<br> | $0.072066$<br> |
| **Final Normalized Score** | **11.68 / 100 (11.7%)**<br> | **7.21 / 100 (7.2%)**<br> |
| **Diagnostic Classification** | Sparrer Profile

 | Associative Rung 1

 |

**Table 2:** Empirical reconciliation of BARS capability tiers, Popperian falsifiers, and power-curve damping on the Sitra Megatrend foresight audit.

---

### 6.2. Structural Graph Topology and XAI Disparity Diagnostics

The two-pass atomization pipeline decomposed the evaluated corpus into a Linked Atom Graph $\mathcal{G}_{\text{LAG}}$ comprising $N = 255$ causal propositions, whose topological properties are summarized in Table 3.

| Graph Topological Metric | Empirical Value | Epistemic and Architectural Significance |
| --- | --- | --- |
| **Total Extracted Propositions ($\vert\mathcal{A}\vert$)** | $255$<br> | Complete atomic proposition pool extracted from discourse.

 |
| **Validated Connected Nodes** | $161$ (**63.1%**)

 | Claims anchored within verified dependency chains.

 |
| **Orphan Claims ($\text{InDegree} = 0$)** | $94$ (**36.9%**)

 | Unsubstantiated inferential leaps or exogenous baseline premises.

 |
| **Maximum In-Degree Connectivity (Hub)** | $5.0$<br> | Primary terminal strategic recommendation node.

 |
| **Mean In-Degree Connectivity** | $0.41$<br> | Sparse, predominantly linear Rung 1 argumentative topology.

 |

**Table 3:** Structural topology metrics of the extracted Linked Atom Graph ($\mathcal{G}_{\text{LAG}}$) for the Sitra strategic foresight case study.

In parallel with BARS capability scoring, the orthogonal Explainable AI (XAI) variance engine evaluated surface linguistic presentation against substantive cognitive depth:

* **Mechanical Phrase Load ($\text{Load}_{\text{mech}}$):** $0.00 / 2.0$, indicating complete absence of rhetorical clichés or corporate buzzwords.


* **Cognitive Authenticity ($\text{Score}_{\text{cog}}$):** $1.47 / 3.0$, reflecting unreflective, routine task delegation.


* **Form-to-Content Disparity Ratio:** Computed orthogonally without mutating Equation (17) as $\Delta = \vert{}\text{Score}_{\text{cog}} - (3.0 - \text{Load}_{\text{mech}})\vert{} = \vert{}1.47 - (3.0 - 0.00)\vert{} = 1.53$ (Diagnostic Verdict: **IN CONFLICT**).



Qualitative inspection of the `<user_payload>` capsule confirms the mechanism behind this divergence: the operator issued brief, jargon-free steering prompts (e.g., *"mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila"*), which induced an **Illusion of Control**. Because the prompt was direct and the resulting AI draft avoided superficial buzzwords ($\text{Load}_{\text{mech}} = 0.00$), the human supervisor accepted the initial associative output without demanding explicit Toulmin warrants ($\mathbf{W}_{XY}$), confounder isolation, or Rung 3 counterfactual stress-testing—causing both matrices to fail all Tier 4 and Tier 5 criteria.

---

## 7. Related Work, Limitations, and Architectural Synthesis

### 7.1. Comparative Positioning Across Reasoning and Verification Paradigms

Quorum bridges a foundational divide between heuristic prompt-driven orchestration and formal neurosymbolic verification:

* **Autoregressive Reasoning Chains and Search Graphs:** Chain-of-Thought (CoT; Wei et al., 2022) relies on unconstrained autoregressive continuation, remaining vulnerable to exponential error compounding (Equation 2). Tree of Thoughts (ToT; Yao et al., 2023) and Graph of Thoughts (GoT; Besta et al., 2024) introduce heuristic graph search over natural language strings, but rely on stochastic LLM self-evaluation for state pruning. Similarly, ReAct (Yao et al., 2022) and Reflexion (Shinn et al., 2023) employ iterative self-correction loops, which struggle to reliably self-correct without external ground truth (Huang et al., 2023). Quorum replaces unstructured string states and self-reflection with Kahn-sorted waves of pure operators over frozen DTOs and external Popperian falsification.


* **Retrieval-Augmented Generation and Atomic Factuality:** Standard RAG (Lewis et al., 2020) and Self-RAG (Asai et al., 2023) retrieve coarse passage chunks via dense vector similarity ($k$-NN), often introducing distracting context and failing on fine-grained multi-step entailment. While FActScore (Min et al., 2023) and RARR (Gao et al., 2023) decompose text into atomic facts, they evaluate claims symmetrically as binary counters without modeling speaker agency ($\sigma_i$), asymmetric falsification polarity ($\pi_i$), or structural ATMS graph surgery. Table 4 summarizes these architectural distinctions.



| Architectural Dimension | Standard RAG / CoT | ReAct / Reflexion / ToT | Quorum Neurosymbolic Engine |
| --- | --- | --- | --- |
| **Execution Topology** | Linear autoregressive sequence

 | Heuristic cyclic search / trial loop

 | **Kahn Wave-Sorted Acyclic Graph ($\mathcal{G}_{\text{DAG}}$)**<br> |
| **State Representation** | Unstructured token strings

 | Natural language scratchpads

 | **Frozen Typed DTOs & 5-Tuple Atoms ($a_i$)**<br> |
| **Evidentiary Grounding** | $k$-NN dense vector similarity

 | External tool output strings

 | **5-Gate Deterministic Lexical Null Hypothesis ($\kappa_i$)**<br> |
| **Causal & Warrant Audit** | None (associative co-occurrence)

 | Prompted heuristic reflection

 | **A-SCM & Discrete ATMS Graph Surgery (Alg. 1)**<br> |
| **Psychometric Scoring** | Stochastic LLM-as-a-Judge

 | Heuristic reward scalar

 | **Lipschitz-Stable Power-Curve BARS (Eq. 17)**<br> |
| **Error Falsification** | None

 | Symmetric candidate reranking

 | **Role-Asymmetric Popperian Malus ($\pi_i = -1$)**<br> |
| **Termination Guarantee** | Maximum token length cutoff

 | Maximum iteration count

 | **Mathematically Proved Poset Acyclicity**<br> |
| **Human Agency Audit** | None

 | None

 | **XML-Isolated Multi-Matrix Vector ($\mathbf{\Psi}, \mathcal{M}_{\text{HACM}}$)**<br> |

**Table 4:** Cross-paradigm comparison between unconstrained prompting, heuristic agent loops, and the Quorum neurosymbolic architecture.

---

### 7.2. Methodological Limitations and Operational Scope

Four operational boundaries govern the deployment of the Quorum architecture:

1. **Inference Token Overhead vs. Diagnostic Precision:** Executing Best-of-3 consensus ensembles alongside multi-matrix extraction increases token consumption compared to single-pass generation, motivating the Two-Tier FinOps partitioning between single-model production waves and offline multi-provider variance suites.


2. **Exogenous Axiom Disambiguation:** In highly condensed executive texts where authors omit explicit citations for foundational domain priors ($U_i$), strict lexical provenance ($\kappa_i = 0$) classifies unanchored root nodes as orphan claims ($\mathcal{A}_{\text{orphan}}$), requiring domain-specific axiomatic whitelisting during rubric design.


3. **Psychometric Cohort Calibration:** Because power-curve damping ($\gamma \in [1.00, 2.20]$) strictly penalizes performance restricted to lower BARS tiers (yielding scores such as **11.7%** and **7.2%** in the Sitra audit), raw scores should be accompanied by organizational cohort percentiles to prevent operator misinterpretation.


4. **Distributed Bijective State Hydration:** Maintaining single-token alias integrity ($\mu: \mathcal{I}_{\text{UUID}} \leftrightarrow \mathcal{V}_{\text{alias}}$) across stateless asynchronous workers requires strict per-job `AliasManifest` serialization; any unmapped alias prefix intentionally triggers an immediate fail-fast halt (`422`) rather than permitting silent data corruption.



By unifying Kahn wave-scheduled DAG orchestration, deterministic five-gate lexical provenance, discrete ATMS argument surgery, and Lipschitz-stable orthogonal BARS psychometrics within a production-grade full-stack platform, the Quorum framework demonstrates that stochastic language models can be effectively governed as verifiable, epistemically accountable reasoning engines.

---

## References

1. **Asai, A. et al. (2023).** Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. *arXiv preprint*.


2. **Besta, M. et al. (2024).** Graph of Thoughts: Solving Elaborate Problems with Large Language Models. *Proceedings of the AAAI Conference on Artificial Intelligence (AAAI 2024)*.


3. **Bloom, B. S. (1956).** *Taxonomy of Educational Objectives, Handbook I: The Cognitive Domain*. David McKay Co..


4. **Buçinca, Z. et al. (2021).** To Trust or to Think: Cognitive Forcing Functions to Address Overreliance on AI. *Proceedings of the ACM on Human-Computer Interaction (CHI 2021)*.


5. **Carlsson, G. (2009).** Topology and data. *Bulletin of the American Mathematical Society*, 46(2), 255–308.


6. **Chernoff, H. (1952).** A measure of asymptotic efficiency for tests of a hypothesis based on the sum of observations. *The Annals of Mathematical Statistics*, 23(4), 493–507.


7. **Church, A., & Rosser, J. B. (1936).** Some properties of conversion. *Transactions of the American Mathematical Society*, 39(3), 472–482.


8. **de Kleer, J. (1986).** An assumption-based TMS. *Artificial Intelligence*, 28(2), 127–162.


9. **Doyle, J. (1979).** A truth maintenance system. *Artificial Intelligence*, 12(3), 231–272.


10. **Dung, P. M. (1995).** On the acceptability of arguments and its fundamental properties: A formal framework for computational argumentation. *Artificial Intelligence*, 77(2), 321–357.


11. **Edelsbrunner, H., & Harer, J. (2010).** *Computational Topology: An Introduction*. American Mathematical Society.


12. **Gao, L. et al. (2023).** RARR: Researching and Refining What Language Models Say with Retrieval. *Proceedings of the Association for Computational Linguistics (ACL 2023)*.


13. **Grice, H. P. (1975).** Logic and conversation. In *Syntax and Semantics, Vol. 3: Speech Acts*, 41–58.


14. **Huang, J. et al. (2023).** Large Language Models Cannot Self-Correct Reasoning Yet. *arXiv preprint arXiv:2310.01798*.


15. **Johnson, D. B. (1975).** Finding all the elementary circuits of a directed graph. *SIAM Journal on Computing*, 4(1), 77–84.


16. **Kahn, A. B. (1962).** Topological sorting of large networks. *Communications of the ACM*, 5(11), 558–562.


17. **Kahn, G. (1974).** The semantics of a simple language for parallel programming. *Information Processing 74: Proceedings of IFIP Congress 74*, 471–475.


18. **Kahneman, D. (2011).** *Thinking, Fast and Slow*. Farrar, Straus and Giroux.


19. **Khattab, O. et al. (2023).** DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines. *arXiv preprint arXiv:2310.03714*.


20. **Kıcıman, E. et al. (2023).** Causal Reasoning and Large Language Models: Opening a New Frontier for Causality. *Microsoft Research Technical Report*.


21. **Lewis, P. et al. (2020).** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems (NeurIPS 2020)*.


22. **Min, S. et al. (2023).** FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. *Proceedings of Empirical Methods in Natural Language Processing (EMNLP 2023)*.


23. **Pan, L. et al. (2023).** Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Reasoning. *Findings of EMNLP 2023*.


24. **Parasuraman, R., Sheridan, T. B., & Wickens, C. D. (2000).** A model for types and levels of human interaction with automation. *IEEE Transactions on Systems, Man, and Cybernetics - Part A: Systems and Humans*, 30(3), 286–297.


25. **Pearl, J. (1995).** Causal diagrams for empirical research. *Biometrika*, 82(4), 669–688.


26. **Pearl, J. (2009).** *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.


27. **Popper, K. (1959).** *The Logic of Scientific Discovery*. Hutchinson & Co..


28. **Sheridan, T. B., & Verplank, W. L. (1978).** *Human and Computer Control of Undersea Teleoperators*. MIT Man-Machine Systems Laboratory.


29. **Shinn, N. et al. (2023).** Reflexion: Language Agents with Verbal Reinforcement Learning. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.


30. **Smith, P. C., & Kendall, L. M. (1963).** Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. *Journal of Applied Psychology*, 47(2), 149–155.


31. **Spirtes, P., Glymour, C. N., & Scheines, R. (2000).** *Causation, Prediction, and Search*. MIT Press.


32. **Tarjan, R. (1972).** Depth-first search and linear graph algorithms. *SIAM Journal on Computing*, 1(2), 146–160.


33. **Toulmin, S. E. (1958).** *The Uses of Argument*. Cambridge University Press.


34. **Vaswani, A. et al. (2017).** Attention Is All You Need. *Advances in Neural Information Processing Systems (NeurIPS 2017)*.


35. **Wang, X. et al. (2022).** Self-Consistency Improves Chain of Thought Reasoning in Language Models. *International Conference on Learning Representations (ICLR 2023)*.


36. **Wei, J. et al. (2022).** Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *Advances in Neural Information Processing Systems (NeurIPS 2022)*.


37. **Yang, K. et al. (2023).** LeanDojo: Theorem Proving with Retrieval-Augmented Language Models. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.


38. **Yao, S. et al. (2022).** ReAct: Synergizing Reasoning and Acting in Language Models. *International Conference on Learning Representations (ICLR 2023)*.


39. **Yao, S. et al. (2023).** Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.


40. **Zečević, M. et al. (2023).** Causal Parrots: Large Language Models May Talk Versus Reason on Causality. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.


41. **Zheng, L. et al. (2023).** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems (NeurIPS 2023)*.