# Epistemic Determinism and the Architecture of Causal-Topological Orchestrated Inference in Stochastic Large Language Models: Theoretical Framework, Mathematical Model, and Empirical Validation

**Quorum Research Collective**

*arXiv preprint: cs.AI / cs.CL / cs.DS*

---

### Abstract

Autoregressive Large Language Models (LLMs) operate as stochastic token probability generators whose unconstrained inference paths are fundamentally susceptible to hallucinations, semantic drift, error compounding, and epistemic instability. This paper presents the **Quorum** architecture: a formal neurosymbolic computational framework that transforms unconstrained stochastic generative processes into a deterministically supervised, epistemically anchored state machine. The theoretical foundation comprises:

> 1. Propositional epistemic atomization via the five-tuple Linked Atom Graph (LAG),
> 2. Wave-based topological execution over a Cognitive Directed Acyclic Graph (Cognitive DAG),
> 3. Topological Directed Atom (TDA) poset wave scheduling governed by an absolute lexical null hypothesis,
> 4. Autonomous structural argument evaluation via discrete graph surgery, Assumption-Based Truth Maintenance Systems (ATMS), and Toulmin's argumentation structure, and
> 5. An orthogonal two-factor BARS evaluation matrix combining asymmetric Popperian falsification with continuous piecewise power-curve damping.
> 
> 

We formalize this framework through two core architectural principles (confluent wave scheduling under Kahn partial ordering and epistemic warrant reachability under discrete ATMS graph surgery) and two mathematically verified system properties (deterministic lexical error suppression and monotonic Lipschitz score stability). The framework is empirically validated through a strategic foresight case study (Sitra Megatrend Audit, $N = 255$ causal atoms), demonstrating how the system penalizes passive conversational delegation (HACM: $11.7\%$, Causal Score: $7.2\%$) and detects pseudo-competence despite clean linguistic presentation (jargon load $0.00 / 2.0$ vs. cognitive depth $1.47 / 3.0$). Finally, we synthesize Quorum's positioning across the landscape of reasoning architectures, retrieval frameworks, and cognitive governance paradigms.

---

## 1. Introduction and Problem Formulation

An autoregressive language model is formally defined as a conditional probability distribution over a discrete vocabulary $\mathcal{V}$:

$$P(Y \mid X; \theta) = \prod_{t=1}^{T} P(y_t \mid y_{<t}, X; \theta), \quad y_t \in \mathcal{V} \tag{1}$$

where $X = (x_1, \dots, x_N)$ is an input prompt sequence and $\theta \in \mathbb{R}^D$ represents the static model weights. Although modern frontier models produce syntactically fluent discourse, their epistemic utility in high-stakes reasoning is bounded by three structural failures:

> 1. **Aleatoric Uncertainty and Calibration Divergence:** The distribution $P(Y \mid X; \theta)$ models statistical token co-occurrence frequencies across training corpora rather than objective truth values ($\mathcal{T} \neq \mathcal{P}$). The model generates statistically plausible assertions that lack empirical backing.
> 2. **Conflation of Association with Causation:** Autoregressive attention captures symmetric correlation $P(A \mid B)$ but cannot distinguish a genuine causal mechanism $B \to A$ from confounding background factors ($C \to A \land C \to B$) or reverse causation ($A \to B$).
> 3. **Superlinear Error Cascade:** In unconstrained multi-step inference, a minute semantic drift at step $t$ conditions the distribution at step $t+1$, causing errors to compound exponentially across generative trajectories:
> 
> 
> $$\mathbb{E}\left[\|\hat{y}_{t+k} - y^*_{t+k}\|\right] \sim \mathcal{O}\left(e^{\lambda k}\right), \quad \lambda > 0 \tag{2}$$
> 
> 

The Quorum architecture addresses these vulnerabilities by stripping the LLM of autonomous state transitions. The generative model is restricted to a stateless, constrained propositional sensor, while the control logic, state progression, and evidentiary evaluation are enforced by an external, mathematically validated neurosymbolic engine.

---

## 2. Epistemic Atomization and the Linked Atom Graph (LAG)

### 2.1. Atomization Morphism

Let an unstructured natural language input or discourse history be denoted as $\mathcal{D} \in \Sigma^*$. We define the atomization morphism $\alpha: \Sigma^* \to \mathcal{A}$ that maps the raw discourse into a finite set of minimal, mutually independent propositional assertions:

$$\mathcal{A} = \{ a_1, a_2, \dots, a_n \} \tag{3}$$

Every epistemic atom $a_i \in \mathcal{A}$ is formally defined as an immutable five-tuple:

$$a_i = \langle \tau_i, \mathcal{C}_i, \sigma_i, \pi_i, \kappa_i \rangle \tag{4}$$

* $\tau_i \in \mathcal{L}_{\text{prop}}$ is an atomic proposition formulated in formal logic with unambiguous truth-evaluable acceptance criteria.
* $\mathcal{C}_i \subset \Sigma^*$ is the spatial and contextual bounding box isolating the exact text span in $\mathcal{D}$ from which $\tau_i$ was derived.
* $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ is the speaker attribution index, separating human supervisory intent from model-generated synthetic drafts.
* $\pi_i \in \{+1, -1\}$ is the evidentiary polarity index: $\pi_i = +1$ denotes a positive capability claim (demonstrating analytical competence), whereas $\pi_i = -1$ designates an asymmetric anti-pattern detector (identifying cognitive failure modes, fallacies, or uncritical adoption).
* $\kappa_i \in \{0, 1\}$ is the lexical provenance anchoring index, governed by an uncompromising null hypothesis parameterized by strictness $\theta \in [0, 100]$:

$$\kappa_i = \begin{cases} 1, & \text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta) \;\land\; \text{Prov}(\mathcal{C}_i, \sigma_i) \;\land\; \text{Triangulate}(\mathcal{T}_i, \mathcal{C}_i) \\ 0, & \text{otherwise} \end{cases} \tag{5}$$

where $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta)$ evaluates the deterministic lexical verification cascade (collapsing to exact normalized substring containment $\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1$ at $\theta \ge 100$, and incorporating bounded morphological stem-sequence verification for agglutinative inflections at $\theta < 100$), $\text{Norm}(\cdot)$ denotes Unicode NFKC/NFD diacritic decomposition and formatting strip, $\text{Prov}(\cdot)$ enforces structured XML speaker isolation, and $\text{Triangulate}(\cdot)$ validates internal CoT consistency against syntactic anchors.

*The Syntactic Provenance vs. Semantic Entailment Boundary:* An exact substring match $\text{find}(\mathcal{C}_i, \mathcal{D}) \neq -1$ provides *physical provenance*—irrefutable proof that citation $\mathcal{C}_i$ was not fabricated or spliced across disparate paragraphs. However, deterministic string matching is semantically blind: it proves the physical existence of characters, not that proposition $\tau_i$ logically follows from $\mathcal{C}_i$. In Quorum, this semantic gap is bridged without falling into second-order LLM stochasticity because **propositions $\tau_i$ are NOT freely invented by the model**. Instead, propositions are **pre-compiled, strictly typed evaluation criteria** defined in Single Source of Truth (SSOT) Behaviorally Anchored Rating Scale (BARS) rubrics (`seed_data.json`). The generative model is constrained to identifying the exact verbatim clause $\mathcal{C}_i$ satisfying the pre-defined target invariant $\tau_i$, backed by reasoning trace syntactic anchor triangulation and asymmetric Popperian falsification ($\pi_i = -1$). If physical containment or provenance fails in deterministic Python code, $\kappa_i = 0$ and the proposition fails closed unconditionally.

*Symbolic Interface Grounding and Subword Entropy Suppression:* In physical persistence, propositions $a_i \in \mathcal{A}$ are addressed via high-entropy 128-bit identifiers ($\mathcal{I}_{\text{UUID}}$, specifically UUIDv4 hexadecimal strings). Directly exposing multi-token hexadecimal strings to autoregressive prompt contexts induces subword tokenization fragmentation (5–10 Byte-Pair Encoding subwords per identifier), triggering attention diffusion, positional degradation over extended contexts, and character transposition hallucinations during decoding. To isolate the generative sensor from persistent storage mechanics, the neurosymbolic boundary executes an ephemeral bijective alias morphism:

$$\mu: \mathcal{I}_{\text{UUID}} \longleftrightarrow \mathcal{V}_{\text{alias}}, \quad \mathcal{V}_{\text{alias}} = \{a_0, a_1, \dots, a_{n-1}\}$$

This morphism compresses each propositional target into an atomic single-token Attention Anchor ($a_k$). Concurrently, the generation grammar enforces constrained decoding via dynamic Pydantic `Literal` type definitions, bounding output logits to the closed categorical support $\mathcal{V}_{\text{alias}}$. Upon receipt, the runtime executes deterministic $\mathcal{O}(1)$ reverse hydration $\mu^{-1}(a_k)$ in pure Python (`AliasEngine`), raising a fail-fast validation exception (`AppException(422)`) if an unmapped alias prefix is hallucinated. This preserves single-token attention fidelity while guaranteeing mathematical referential integrity across the proposition graph.

### 2.2. Linked Atom Graph Structure and Root Node Typology

The extracted atoms are structured into a directed, attributed multi-graph $\mathcal{G}_{\text{LAG}} = (\mathcal{A}, \mathcal{E}_{\text{dep}}, \mathcal{E}_{\text{temp}}, \mathcal{E}_{\text{causal}})$, where edge sets define logical dependency, temporal order, and inferred causal transmission.

To avoid misclassifying legitimate foundational axioms, $\mathcal{G}_{\text{LAG}}$ partitions root nodes ($\text{InDegree}(a_i) = 0$) into two distinct epistemic classes:

1. **Exogenous Boundary Axioms ($\mathcal{A}_{\text{axiom}}$):** Primitive operational constraints or historical baseline premises ($U_i$) that require no internal textual ancestors (specifically establishing the scope of an external institutional report).
2. **Unjustified Orphan Claims ($\mathcal{A}_{\text{orphan}}$):** Dependent inferential conclusions asserted without supporting evidence, warrants, or mediating causal links.

---

## 3. Cognitive Directed Acyclic Graph (Cognitive DAG) Architecture

High-level cognitive transformations—ingress filtering, atomic decomposition, causal graph mining, matrix evaluation, falsification, and executive synthesis—are executed across an immutable, acyclic orchestration network:

$$\mathcal{G}_{\text{DAG}} = (\mathcal{V}_{\text{cog}}, \mathcal{E}_{\text{dep}}) \tag{6}$$

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
     | (Warrant Audit) |     | (Anchor κ ∈ {0,1}|
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

Because $\mathcal{G}_{\text{DAG}}$ is acyclic, Kahn’s topological sort partitions $\mathcal{V}_{\text{cog}}$ into discrete, parallel computational waves $W_0, W_1, \dots, W_{K-1}$:

$$W_0 = \{ v \in \mathcal{V}_{\text{cog}} \mid \text{InDegree}(v) = 0 \} \tag{7}$$

$$W_{k+1} = \left\{ v \in \mathcal{V}_{\text{cog}} \setminus \bigcup_{j=0}^k W_j \;\middle|\; \text{Parents}(v) \subseteq \bigcup_{j=0}^k W_j \right\} \tag{8}$$

Operators within wave $W_k$ are executed concurrently as isolated asynchronous coroutines. Each operator $v \in W_k$ evaluates an invariant deterministic function over immutable Data Transfer Objects (DTOs):

$$\Phi_v: \prod_{u \in \text{Parents}(v)} \mathcal{O}_u \times \mathcal{S}_{\text{global}} \to \mathcal{O}_v \tag{9}$$

---

## 4. Topological Directed Atom (TDA) Scheduling and Structural Argument Truth Maintenance

### 4.1. Topological Directed Atom (TDA) Poset Scheduling and Verification

*Nomenclature Demarcation and Scope Calibration:* To prevent terminological confusion with *Topological Data Analysis* (TDA in applied mathematics and machine learning, which studies persistent homology, simplicial complexes, and Betti numbers $\beta_k$ over metric point clouds; Carlsson, 2009; Edelsbrunner & Harer, 2010), we explicitly clarify that in Quorum, the acronym **TDA** designates **Topological Directed Atoms** (and their associated dependency argumentation). The term *topological* is employed strictly in its foundational computer science and order-theoretic sense: Kahn's topological sorting (Kahn, 1962) on finite directed acyclic graphs inducing an Alexandroff topology and a specialization poset ($\mathcal{G}_{\text{LAG}}$). Quorum asserts no claims of computing algebraic homology groups or metric simplicial filtrations. Rather, TDA in Quorum denotes the **order-theoretic scheduling, exact lexical provenance, and cycle-free verification** of propositional claims:

1. **Strict Lexical Grounding:** Proposition truth values are grounded directly in verbatim source evidence. Unanchored assertions fail closed ($\kappa_i = 0$).
2. **Cycle Elimination and Poset Acyclicity:** Circular reasoning chains ($a_1 \implies a_2 \implies \dots \implies a_1$) violate epistemic partial order invariants. Rather than invoking homological machinery, circularities and phantom edges (`UNRESOLVED_DEPENDENCY`) are detected prior to wave evaluation via Tarjan's strongly connected components and Johnson's elementary cycle enumeration algorithm (`nx.simple_cycles`; Tarjan, 1972; Johnson, 1975). Nodes participating in directed cycles are immediately quarantined (`CYCLIC_DEPENDENCY_DETECTED`), and any downstream nodes left unresolved after Kahn wave exhaustion are deterministically clamped to `BLOCKED`, enforcing strict directed acyclicity across the proposition graph.

### 4.1.1. Deterministic NLI/Entailment and Eradication of Second-Order Hallucination

A foundational failure mode in contemporary LLM evaluation (including LLM-as-a-Judge, G-Eval, and Self-RAG) is **Second-Order Hallucination** (*Quis custodiet ipsos custodes?*). If a secondary LLM is queried to determine whether a document entails a proposition ($P(\text{Entail} \mid \mathcal{D}, \tau_i)$), the verifier is itself an autoregressive stochastic sampler susceptible to sycophancy, confirmation bias, and the synthesis of *chimera quotes* (stitching isolated words across disparate paragraphs into a fabricated sentence).

To eliminate second-order hallucination, Quorum strips the LLM of judicial authority. Natural Language Inference (NLI) is decomposed into a **Tripartite Neurosymbolic Protocol**: the LLM operates strictly as a constrained syntactic sensor extracting proposition tuples, while propositional grounding and entailment are executed **exclusively in pure deterministic Python code** (`AnchorValidationService`):

1. **Gate 1: Physical Substring Invariant with Bidirectional Index Mapping:**
   The source text is stripped of HTML/formatting artifacts and normalized via Unicode NFKC and NFD diacritic decomposition. An invariant bidirectional index map $\mathcal{M}_{\text{idx}}: \mathbb{N} \to \mathbb{N}$ maps normalized character indices back to original byte positions. The candidate quote $\mathcal{C}_i$ is validated via exact $O(N)$ containment:
   
   $$\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1$$
   
   If matched, the exact verbatim string is sliced from the original immutable text, preventing case-folding or formatting drifts from fabricating false evidence.

2. **Gate 2: Entropy Gate & Contiguity Guard (Chimera Quote Defense):**
   * *Entropy Gate (< 10 chars):* Short quotes under 10 characters (specifically isolated buzzwords) are strictly forbidden from fuzzy matching. 100% exact substring containment is required.
   * *Contiguity Guard (< 30 chars):* Short phrases enforce strict contiguous sequence matching (`fuzz.partial_ratio`), whereas longer spans ($\ge 30$ chars) evaluate token-set overlap (`fuzz.token_set_ratio`). This prevents the model from picking disparate words from different pages and presenting them as a continuous quote.
   * *Safety Ceiling (> 1000 chars):* Quotes exceeding 1000 characters trigger an immediate `SemanticEvidenceError` fail-fast crash to prevent prompt injection and quote stuffing.

3. **Gate 3: Cross-Speaker Provenance Boundary Guard:**
   Discourse is segmented into XML-fenced provenance capsules: `<user_payload>` for human supervisor inputs, `<ai_draft_context>` for model drafts, and `<assignment_context>` for task instructions. When evaluating human capability ($\sigma_i = \text{USER}$), candidate quotes must reside strictly inside `<user_payload>`:
   
   $$\text{Prov}(\mathcal{C}_i, \sigma_i) = \mathbb{I}\left( \text{Lex}(\mathcal{C}_i, \mathcal{D}_{\text{speaker}}; \theta) = 1 \right)$$
   
   If an LLM quotes the AI assistant's draft to substantiate a human competence claim, the verifier halts with a `PROVENANCE_VIOLATION` error, mathematically preventing cross-speaker competence pollution.

4. **Gate 4: Reasoning Trace Triangulation:**
   The model's Pydantic response requires an explicit reasoning trace $\mathcal{T}_i$ specifying an exact syntactic anchor (`[2. SYNTACTIC ANCHOR: "..."]`) and decision (`[5. VALIDATION DECISION: PASS/FAIL]`). Pure Python triangulation asserts three consistency invariants:
   * *Contradiction Ban:* If $\mathcal{T}_i$ concludes `FAIL`, but quote $\mathcal{C}_i$ is populated, the atom is rejected for logical contradiction.
   * *Empty Anchor Ban:* If $\mathcal{T}_i$ declares `[2. SYNTACTIC ANCHOR: NONE]`, unanchored extraction fails closed.
   * *Hallucinated Anchor Ban:* The anchor string parsed from the trace must physically exist in the source document via `strict_match`; fabricated anchors trigger immediate rejection.

5. **Gate 5: Calibrated Zero-Trust Strictness Curve and Morphological Stemming Cascade:**
   Under Quorum's continuous strictness parameter $\theta \in [0, 100]$, the lexical predicate $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta)$ executes a calibrated four-tier deterministic cascade when $\theta < 100$: (i) exact NFKC/NFD substring containment, (ii) length-stratified RapidFuzz similarity scaled by tier multipliers ($\times 0.80$ for $\theta < 30$, $\times 0.90$ for $\theta \in [30, 50)$, $\times 1.00$ for $\theta \in [50, 85)$, and $\times 1.02$ for $\theta \in [85, 100)$), (iii) multilingual rule-based Snowball morphological stemmed subsequence matching (`StemmerService.match_stemmed_subsequence`) to accommodate grammatical case inflections in highly agglutinative languages (including Finnish), and (iv) contiguous longest-common-substring coverage verification (`difflib.SequenceMatcher`). At $\theta \ge 100$ (Absolute Zero-Trust), all non-exact tiers (ii)–(iv) are completely disabled, enforcing 100% exact normalized substring containment.

Under this five-gate architecture, propositional grounding does not rely on LLM self-evaluation. An atom $\tau_i$ is accepted ($\kappa_i = 1$) if and only if all five deterministic Python gates succeed, bounding the false acceptance probability by the physical string collision rate $\epsilon_{\text{lexical}} \to 0$.

*Formal Scope and the Semantic Undecidability Bound:* We explicitly distinguish between **Physical Citation Provenance** and **Universal Semantic Entailment**. In unconstrained natural language, determining whether an arbitrary premise $\mathcal{C}$ semantically entails an arbitrary conclusion $\tau$ without human supervision is undecidable (Rice's Theorem applied to semantic properties of formal discourse). Quorum does not claim universal automated semantic proof over arbitrary text. Instead, Quorum solves the practical enterprise failure mode: it bounds hallucination risk by enforcing that propositions $\tau_i$ originate from human-curated, pre-compiled BARS rubrics, and constrains the stochastic model to locating exact physical evidence spans whose grammatical anchors pass deterministic Python verification.

### 4.2. Argumentative Structural Dependency Models (A-SCM) and Truth Maintenance

*Ontological Scope and the Enthymeme Boundary:* Unlike physical systems where variables $\mathbf{V}$ represent empirical data-generating mechanisms, natural discourse is inherently pragmatic, elliptical, and enthymematic (Toulmin, 1958; Grice, 1975). Human authors routinely omit common-sense warrants and intermediate mechanisms. Therefore, Quorum does not claim that textual analysis discovers objective physical causality. Instead, Quorum formalizes the **Argumentative Structural Causal Model (A-SCM)**, evaluating the *internal explanatory sufficiency and structural evidentiary rigor* of the authored thesis.

We formalize the discourse argument structure through the five-tuple A-SCM:

$$\mathcal{M}_{\text{arg}} = \langle \mathbf{U}, \mathbf{V}, \mathbf{W}, \mathbf{F}, P(\mathbf{U}) \rangle \tag{10}$$

where $\mathbf{V} = \{V_1, \dots, V_n\}$ represents explicit propositional claims grounded in verbatim text ($\kappa = 1$), $\mathbf{W}$ represents explicit Toulmin warrants (backing and explanatory transmission mechanisms), $\mathbf{U} = \{U_{\text{enthymeme}}, U_{\text{context}}\}$ represents unstated background assumptions and latent conversational confounders, and $\mathbf{F} = \{f_1, \dots, f_m\}$ defines structural argument dependencies:

$$V_i = f_i(\mathbf{PA}_i, \mathbf{W}_i, U_i), \quad \mathbf{PA}_i \subseteq \mathbf{V} \setminus \{ V_i \} \tag{11}$$

*Operationalization of Structural Interventions via Discrete Graph Surgery & Truth Maintenance:* In structural causal modeling (Pearl, 2009, Chapter 3.2), an intervention on variable $X$ is defined graph-theoretically by replacing its structural equation with a constant assignment $X = x^*$, which corresponds to severing all incoming parent edges in the surgery graph $\mathcal{G}_{\overline{X}}$. 

A foundational question in NLP argumentation is: *Which computational system physically evaluates the downstream consequences of this structural intervention in discourse?* If a secondary LLM is re-prompted to judge whether claim $Y$ survives without premise $X$, the pipeline relapses into second-order stochasticity and confirmation bias.

In Quorum, structural intervention is **NOT executed via LLM prompts or statistical regression**. The extracted discourse is compiled into a discrete Argument DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{atom}}, \mathcal{E}_{\text{deps}})$, and interventions are evaluated via **deterministic graph surgery and Assumption-Based Truth Maintenance Systems (ATMS)** (Doyle, 1979; de Kleer, 1986; Dung, 1995) implemented in pure Python, formalized in Algorithm 1 as the Unified Formal Specification:

```
Algorithm 1: Discrete Structural Argument Surgery & Truth Maintenance (ATMS)
================================================================================
Input  : Argument DAG G = (V, E, W), perturbed node X in V, counterfactual state x* in {FAILED, BLOCKED},
         gate semantics mode in {CONJUNCTIVE_AND, DISJUNCTIVE_OR}
Output : Perturbed state mapping S*, Reachability Cascade Reach(X), Root Causes RC
================================================================================
1: S* <- InitialStateMap(V)                          // Base status from lexical grounding Gate
2: E_cut <- E \ { (P, X) | P in Parents(X) }         // Sever incoming parent edges (Structural graph surgery)
3: S*[X] <- x*                                       // Clamp intervened node to counterfactual state
4: Queue Q <- [ X ]
5: Visited Vis <- { X }
6: Cascade <- []
7: while Q is not empty do
8:     curr <- Q.pop_front()
9:     for each child C in Children(curr, E_cut) do
10:        if C not in Vis then
11:            // Evaluate Precondition & Warrant Gate under active topology semantics:
12:            if mode == CONJUNCTIVE_AND then
13:                // Forward Kahn Wave Scheduling (TopologicalEvaluator): Any antecedent failure blocks C
14:                survives_gate <- forall P' in Parents(C, E_cut): S*[P'] == expected_status(P', C)
15:            else
16:                // Corroborative Warrant Redundancy: Alternative valid warrant shields C
17:                survives_gate <- exists P' in Parents(C, E_cut) \ Vis
18:                                 such that S*[P'] == PASSED and kappa(W_{P'C}) == 1
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
29: RC <- { v in V | S*[v] in {FAILED, BLOCKED} and BlameParents(v) == emptyset }
30: return (S*, Cascade, RC)
================================================================================
```

*Algorithmic Guarantees and Dual-Engine Physical Pipeline Mapping of Algorithm 1:*
1. **Zero Second-Order LLM Calls:** Lines 7–28 operate in linear deterministic time $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ over in-memory adjacency lists in pure Python. No stochastic LLM sampling occurs during perturbation evaluation.
2. **Deterministic Edge Severing (Structural Graph Surgery):** Line 2 executes structural graph surgery ($\mathcal{G}_{\overline{X}}$) by pruning incoming edges in the adjacency structure while holding invariant the downstream topology.
3. **Forward Kahn Wave Scheduling (`TopologicalEvaluator`):** Lines 12–14 enforce strict `CONJUNCTIVE_AND` precondition semantics during real-time forward DAG evaluation in `TopologicalEvaluator.evaluate_graph`. Every antecedent $P' \in \text{Parents}(C)$ is a necessary condition; if any parent enters `SYSTEM_ERROR`/`BLOCKED` or violates `expected_status`, child $C$ deterministically short-circuits to `BLOCKED` or `N_A` (`short_circuit_reason_tda_ids`), completely pruning child nodes from LLM batch evaluation.
4. **Backward Fault Attribution & Root Cause Isolation (`CausalDiscoveryEngine`):** Line 29 is physically executed by `CausalDiscoveryEngine.execute`, which traverses inbound dependencies (`in_deps`) across evaluated argument structures. The engine isolates true epistemic breakdown points (`root_cause_node_ids`, where upstream nodes failed without failing parents) from secondary cascading errors (`blame_parent_ids`), ensuring authors are not penalized repeatedly for downstream consequences.
5. **Corroborative Redundancy & Future Surgery Architecture:** Lines 16–18 formalize corroborative warrant redundancy (`DISJUNCTIVE_OR`), where alternative valid evidentiary warrants preserve claim truth values. In production architecture, real-time forward DAG evaluation and interactive counterfactual simulation are cleanly decoupled: `TopologicalEvaluator` maintains strict single responsibility over forward wave execution and mutation invariance, while interactive counterfactual surgery is partitioned to dedicated simulation services (specifically future StructuralSurgeryService).

*Scope Disambiguation (Discrete ATMS Surgery vs. Observational Do-Calculus):* We explicitly repudiate any rhetorical conflation between **Discrete Structural Argument Surgery** and **Observational Confounding Adjustment via Pearl's Three Rules of Do-Calculus**. The classical do-calculus (Pearl, 1995, 2009) is an axiomatic apparatus designed for non-parametric identification of interventional probability distributions $P(Y \mid do(X))$ from non-experimental observational joint distributions $P(V)$ in the presence of unobserved statistical confounders. In Quorum's discrete text analysis, there are no observational probability distributions, random variables, or backdoor adjustment summations. Rather, Quorum utilizes Pearl's graph-theoretic definition of an intervention ($\mathcal{G}_{\overline{X}}$: severing incoming dependencies) strictly as an operational counterpart to de Kleer's (1986) premise retraction in an Assumption-Based Truth Maintenance System (ATMS). Algorithm 1 deterministically audits whether an author's conclusions possess independent evidentiary warrants ($\mathbf{W}$) or experience justification collapse when antecedent premises are invalidated.

This maps structurally to the epistemic demands of the Three Rungs of Argument Rigor:
* **Rung 1 (Associative Co-occurrence & Fluff):** Unidirectional linguistic correlation lacking explicit warrants ($\mathbf{W} = \emptyset$). Listing co-occurring industry trends without causal transmission mechanisms incurs severe passive delegation penalties.
* **Rung 2 (Intervention Audit & Warrant Isolation):** Simulating structural interventions by pruning parent dependencies. The audit evaluates whether the text explicitly defines operational mechanisms $\mathbf{W}_{XY}$ isolating the claim from common-cause confounding ($U_{XY}$).
* **Rung 3 (Counterfactual Stress-Testing):** Evaluating counterfactual boundary transitions. The audit examines whether the author subjected proposed strategies to "what-if" boundary conditions, failure thresholds, negative externalities, and resource exhaustion scenarios.

---

## 5. Two-Factor Orthogonal Matrix Scoring and Asymmetric Falsification

### 5.1. BARS Criteria Weighting and Division-by-Zero Protection

Evaluation matrices implement Behaviorally Anchored Rating Scales (BARS) distributed across five hierarchical tiers $l \in \{1, \dots, 5\}$ with natural weight function $w(l) = l$. Every atom $a_i \in \mathcal{A}$ resolves to a discrete status:

$$\omega(a_i) \in \{ \text{PASSED}, \text{FAILED}, \text{DLQ} \} \tag{12}$$

where $\text{DLQ}$ (Dead-Letter Queue) denotes unresolvable processing exceptions.

For positive capability atoms ($\pi_i = +1$), achieved points $A$ and effective maximum points $M$ are computed over all tiers:

$$A = \sum_{l=1}^5 l \cdot h_l, \quad M = \sum_{l=1}^5 l \cdot (t_l - d_l) \tag{13}$$

where $h_l$ is passed hits, $t_l$ is total criteria count, and $d_l$ is DLQ exceptions at tier $l$. The weighted linear ratio $\rho$ is safeguarded against division-by-zero singularities:

$$\rho = \begin{cases} \frac{A}{M}, & M > 0 \\ 0.0, & M \le 0 \end{cases} \tag{14}$$

### 5.2. Asymmetric Popperian Falsification Multiplier

Negative anti-pattern atoms ($\pi_i = -1$) act as non-additive gatekeeping falsifiers. If an anti-pattern violation is confirmed ($\omega(a_i) = \text{FAILED}$ relative to clean performance), a penalty deduction $p_k \in (0, 1)$ is registered. The composite multiplier is formed multiplicatively:

$$\Pi_{\text{penalty}} = \begin{cases} \max\left( 1 - P_{\max}, \; \prod_{k=1}^K (1 - p_k) \right), & K > 0 \\ 1.0, & K = 0 \end{cases} \tag{15}$$

where $P_{\max} = 0.40$ is the hard-coded ceiling capping total cumulative deductions at $40\%$.

### 5.3. Continuous Piecewise Power-Curve Damping

To penalize performance clustering at trivial lower tiers ($l \in \{1, 2\}$), the system maps user strictness $\theta \in [0, 100]$ to a damping exponent $\gamma(\theta) \in [1.00, 2.20]$ via continuous piecewise linear interpolation:

$$\gamma(\theta) = \begin{cases} 1.00, & \theta \le 0 \\ 1.00 + \left(\frac{\theta}{50}\right) \cdot 0.25, & 0 < \theta \le 50 \\ 1.25 + \left(\frac{\theta - 50}{35}\right) \cdot 0.45, & 50 < \theta \le 85 \\ 1.70 + \left(\frac{\theta - 85}{15}\right) \cdot 0.50, & 85 < \theta \le 100 \\ 2.20, & \theta > 100 \end{cases} \tag{16}$$

The final mapped score across the range $[S_{\min}, S_{\max}]$ is calculated as:

$$\text{Score}(\rho) = \begin{cases} S_{\min} + \left( \rho^{\gamma(\theta)} \cdot \Pi_{\text{penalty}} \right) \cdot (S_{\max} - S_{\min}), & M > 0 \\ S_{\min}, & M \le 0 \end{cases} \tag{17}$$

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
              DAMPING: Score ∝ ρ^γ(θ)
              γ(θ) ∈ [1.00, 2.20]

```

### 5.4. Multi-Matrix Orthogonal Scoring Space, Polarity Mechanics, and Two-Tier Governance

While Equations (12)–(17) formulate the scoring kernel for an individual Behaviorally Anchored Rating Scale (BARS) matrix, Quorum's neurosymbolic evaluation engine is not bounded by a single evaluative lens. The platform implements a **Holistic Multi-Matrix Audit**, wherein an arbitrary set of process-, structural-, and domain-specific matrices (`docs/architecture/08_matrix_explanations.md`, `seed_data.json`) are scheduled concurrently within the cognitive graph ($\mathcal{G}_{\text{DAG}}$) under Zero-Code Domain Extensibility.

#### 5.4.1. Two-Tier Scoring Hierarchy: Sovereign Kernel vs. Macro Governance

To preserve mathematical purity and prevent cross-phase architectural pollution, Quorum enforces a strict separation of concerns through a two-tier scoring hierarchy:

1. **Tier A: Sovereign Intra-Matrix Kernel (`UnifiedScoringEngine`):**
   Equation (17) represents the sovereign intra-matrix scoring kernel implemented by `UnifiedScoringEngine.calculate`. It computes a pure mathematical evaluation bounded strictly by the evaluated matrix prompt block's extrema ($[S_{\min}, S_{\max}]$ derived via `computed_min` and `computed_max`). The kernel operates exclusively on atomic criteria within that single matrix, computing weighted capability ratio $\rho$ and intra-matrix anti-pattern falsification multiplier $\Pi_{\text{penalty}}$ under continuous strictness damping $\gamma(\theta)$. The kernel returns an immutable `ScoringResultDTO` containing the normalized score, per-level breakdown, and structured XAI audit trace. The intra-matrix kernel does not access external workflow state, execute database lookups, or apply macro-level penalties.

2. **Tier B: Macro-Workflow Governance and Multi-Matrix Aggregation (`apply_scoring_logic_hook`):**
   Multi-matrix scoring consolidation and workflow-level penalty governance are decoupled into the post-execution hook pipeline (`backend_v2/hooks/scoring/`):
   * **Commensurate Normalization (`normalization_hook.py`):** Each evaluated matrix block projects its raw score into a normalized $[0.0, 100.0]$ scale via `normalize_matrix_scores_hook`:
     $$\text{Normalized\_Score}_m = \left( \frac{\text{raw\_score}_m - \text{computed\_min}_m}{\text{computed\_max}_m - \text{computed\_min}_m} \right) \times 100.0$$
   * **Macro-Workflow Penalty Governance (`falsifier_hook.py`):** The consolidated global score is calculated by `apply_scoring_logic_hook` as the unweighted arithmetic mean of normalized matrix scores, subjected to workflow-level deduction penalties:
     $$\text{average\_score} = \frac{1}{N} \sum_{m=1}^N \text{Normalized\_Score}_m$$
     $$\text{effective\_penalty} = \min(\text{total\_penalty}, P_{\max})$$
     $$\text{global\_score} = \text{round}\left( \max(0.0, \; \text{average\_score} \times (1.0 - \text{effective\_penalty})), \; 1 \right)$$
     where $P_{\max} = 0.40$ (40% maximum cumulative workflow deduction). Workflow penalties encompass three sovereign modalities configured in `Workflow`: security injection penalty (`security_penalty`), post-hoc excuse penalty (`post_hoc_penalty`), and passivity penalty (`passivity_penalty`).
   * **Observer Hook Protocol (`passivity_hook.py`):** Behavioral passivity detection is decoupled from intra-matrix scoring math. In `enforce_passivity_penalty_hook`, the hook inspects matrix outputs (`MatrixAggregationStateDTO` or `LightweightMatrixOutput`). If a matrix resolves to its mathematical floor ($S_{\min}$) with zero positive capability hits above the baseline, the hook emits a semantic delta (`PassivityDetectionResultDTO(passivity_detected=True)`). When observed, `apply_scoring_logic_hook` applies the workflow's configured `passivity_penalty` at Tier B aggregation.

#### 5.4.2. Holistic Multi-Matrix Audit in Orthogonal Vector Space ($\mathbf{\Psi}$)

Restricting AI evaluation to a single diagnostic dimension produces structural blind spots. If auditing is confined strictly to the final artifact ($\sigma_i = \text{ASSISTANT}$), fluent autoregressive prose can achieve high marks even if the human operator acted as a completely passive passenger. Conversely, analyzing only conversational interaction ($\sigma_i = \text{USER}$) risks an **Illusion of Control**, wherein concise, confident prompting yields an epistemically hollow, Rung 1 deliverable.

Quorum formalizes holistic evaluation as a $D$-dimensional orthogonal matrix vector $\mathcal{M} = (\mathcal{M}_1, \mathcal{M}_2, \dots, \mathcal{M}_D)$, where each matrix $\mathcal{M}_d$ interrogates discourse $\mathcal{D}$ from a distinct epistemic stance anchored to an XML-isolated speaker capsule ($\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$):

$$\mathbf{\Psi}(\mathcal{D}; \theta) = \begin{bmatrix} \text{Score}_{\mathcal{M}_1}\left(\rho_1, \Pi_{\text{penalty}}^{(1)}; \theta\right) \\ \text{Score}_{\mathcal{M}_2}\left(\rho_2, \Pi_{\text{penalty}}^{(2)}; \theta\right) \\ \vdots \\ \text{Score}_{\mathcal{M}_D}\left(\rho_D, \Pi_{\text{penalty}}^{(D)}; \theta\right) \end{bmatrix} \in \prod_{d=1}^D \left[ S_{\min}^{(d)}, S_{\max}^{(d)} \right] \tag{17a}$$

In a complete audit workflow (`Workflow`), execution graph $\mathcal{G}_{\text{DAG}}$ partitions evaluation across three cross-validating epistemic layers executed concurrently via asynchronous coroutines (`asyncio.TaskGroup`) within the same Kahn topological wave $W_k$:

1. **Human Agency & Collaboration Matrix ($\mathcal{M}_{\text{HACM}}, \sigma_i = \text{USER}$):** Targets the `<user_payload>` capsule, evaluating cognitive steering responsibility, boundary definition, adversarial challenging of AI drafts, and iterative refinement.
2. **Epistemic & Causal Architecture Matrix ($\mathcal{M}_{\text{Causal}}, \sigma_i = \text{ASSISTANT}$):** Targets the `<ai_draft_context>` deliverable, measuring argument coherence, explicit Toulmin warrants ($\mathbf{W}_{XY}$), orphan claim density ($\mathcal{A}_{\text{orphan}}$), and counterfactual stress testing.
3. **Domain Substance Matrix ($\mathcal{M}_{\text{Domain}}, \sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$):** Evaluates specialized task constraints—spanning legal claim management, strategic foresight, and statutory compliance—using the identical mathematical scoring kernel.

While `apply_scoring_logic_hook` computes a commensurate scalar average for high-level governance, the Server-Driven UI presentation pipeline (`SduiMapperService`) preserves vector $\mathbf{\Psi}(\mathcal{D}; \theta)$ intact, exposing the **Agency-to-Outcome Divergence**:

$$\Delta_{\text{agency-outcome}} = \left\vert{} \hat{S}(\mathcal{M}_{\text{HACM}}) - \hat{S}(\mathcal{M}_{\text{Domain/Causal}}) \right\vert{} \tag{17b}$$

where $\hat{S}(\cdot) \in [0, 1]$ represents the normalized matrix score. An elevated divergence $\Delta_{\text{agency-outcome}}$ diagnoses either uncritical automation complacency (high outcome without human agency) or ineffective steering (active dialogue failing to materialize as structural deliverable quality).

#### 5.4.3. Matrix-Specific Polarity Mechanics and Classical Theoretical Grounding

Within every matrix $\mathcal{M}_d$, positive capability assertions ($\pi_i = +1$) and negative anti-pattern falsifiers ($\pi_i = -1$) enforce a **two-sided lexical proof burden** (`ExtractiveSensorService` & `AnchorValidationService`) grounded in **contrastive pair enforcement** (`ContrastivePairDTO`: `acceptable` vs. `rejected`):

1. **Positive Capability Assertions ($\pi_i = +1$, `is_inverse=False`):**
   * *Epistemic Role:* Measures constructive cognitive and professional competence across hierarchical BARS levels $l \in \{1, \dots, 5\}$.
   * *Evidentiary Proof Burden:* The default state is unproven ($h_l = 0$). An assertion is accepted ($\omega(a_i) = \text{PASSED}$) only if the sensor extracts an exact verbatim quote $\mathcal{C}_i$ from target speaker $\sigma_i$ matching the positive anchor (`acceptable`), avoiding the negative distractor (`rejected`), and passing all five physical Python validation gates ($\kappa_i = 1$).
   * *Mathematical Impact:* Accrues additively into weighted capability ratio $\rho = A / M$ (Equations 13–14) and is softened via piecewise power-curve damping $\rho^{\gamma(\theta)}$ (Equation 16).

2. **Negative Anti-Pattern Assertions ($\pi_i = -1$, `is_inverse=True`):**
   * *Epistemic Role:* Acts as a Popperian gatekeeper, actively searching for cognitive shortcuts, argumentation fallacies, uncritical delegation, and superficial fluency.
   * *Evidentiary Proof Burden (Defense Against Hallucinated Penalties):* The default state is clean performance ($\Pi_{\text{penalty}} = 1.0$). The LLM cannot penalize by stochastic estimation: deduction $p_k \in (0, 1)$ triggers only if the sensor extracts an exact verbatim citation passing all five `AnchorValidationService` gates ($\kappa_i = 1$) proving the violation occurred. If lexical grounding fails ($\kappa_i = 0$), the penalty is dropped.
   * *Mathematical Impact:* Verified anti-patterns deduct from the matrix score multiplicatively via $\Pi_{\text{penalty}} = \max(1 - P_{\max}, \prod_{k=1}^K (1 - p_k))$ (`falsifier_hook.py`, Equation 15), capped at $P_{\max} = 0.40$.

In accordance with Quorum's architectural compendium (`docs/architecture/08_matrix_explanations.md`) and seed vault (`seed_data.json`), assertions are anchored to classical theoretical literature across two mutually exclusive rubric tracks:

| Matrix Category & Speaker ($\sigma_i$) | Rubric Track | Classical Theoretical Grounding | Positive Capability Assertions ($\pi_i = +1$, BARS Tiers $l \in \{1, \dots, 5\}$) | Negative Anti-Pattern Falsifiers ($\pi_i = -1$, Malus Multiplier $\Pi_{\text{penalty}}$) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Human Agency & Collaboration (HACM)**<br><br>$\sigma_i = \text{USER}$ | **Track A**<br>(Developmental) | **Sheridan & Verplank (1978)** (*Levels of Automation*),<br><br>**Parasuraman et al. (2000)**,<br><br>**Kahneman (2011)** (*System 1 vs. 2*),<br><br>**Buçinca et al. (2021)** (*Cognitive Forcing*) | **L1–L2:** Foundational task framing and contextual bounding.<br><br>**L3:** Explicit boundary constraints, persona assignment, and criteria setting.<br><br>**L4:** Active adversarial challenging of AI drafts and error correction.<br><br>**L5:** Metacognitive steering, hypothesis forcing, and sovereign synthesis direction. | **Automation Bias & Passive Delegation (`passivity_hook.py`):**<br><br>• Unconstrained "do this for me" task abdication.<br><br>• Blind rubber-stamping of first-draft outputs.<br><br>• Relinquishing critical verification responsibility.<br><br>• Vacuous conversational prompts lacking steering content. |
| **2. Argumentative & Causal Structure (A-SCM)**<br><br>$\sigma_i = \text{ASSISTANT}$ | **Track B**<br>(Error Radar) | **Judea Pearl (2009)** (*Causal Ladder: Rungs 1–3*),<br><br>**Stephen Toulmin (1958)** (*Claim, Grounds, Warrant, Backing, Rebuttal*) | **L1–L2 (Rung 1):** Associative identification of variables and empirical correlations.<br><br>**L3 (Toulmin Warrant):** Explicit intermediate causal mechanism ($\mathbf{W}_{XY}$) justifying *why* $X \to Y$.<br><br>**L4 (Rung 2 Intervention):** Confounder isolation ($U$) and systemic policy side-effect modeling.<br><br>**L5 (Rung 3 Counterfactual):** "What-if" boundary stress tests, limit breaking, and opportunity cost analysis. | **Pseudo-Causality & Structural Collapse:**<br><br>• Conflating correlation with causation (bare trend listing).<br><br>• Orphan claims ($\mathcal{A}_{\text{orphan}}$) lacking evidentiary grounds or warrants ($\mathbf{W} = \emptyset$).<br><br>• Circular causal loops (`CYCLIC_DEPENDENCY_DETECTED`).<br><br>• Unqualified optimism omitting boundary exceptions (*Missing Rebuttal*). |
| **3. Critical Thinking & Epistemic Rigor**<br><br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track A & B**<br>(Hybrid) | **Benjamin Bloom (1956)** (*Cognitive Taxonomy*),<br><br>**Karl Popper (1959)** (*Empirical Falsifiability*) | **L1–L2 (Remember/Understand):** Nomenclature definition and baseline summarization.<br><br>**L3 (Apply/Analyze):** Deconstructing latent assumptions and identifying structural tensions.<br><br>**L4 (Evaluate):** Source critique, evidence weighting, and defining empirical falsification conditions.<br><br>**L5 (Create):** Synthesizing novel, empirically testable explanatory frameworks. | **Epistemic Immunization & Cognitive Biases (`falsifier_hook.py`):**<br><br>• Confirmation bias (discarding disconfirming evidence).<br><br>• Unfalsifiable tautologies and evasive non-committal prose.<br><br>• Substituting substantive depth with rhetorical buzzwords (*Jargon Load*). |
| **4. Domain & Task-Specific Substance**<br><br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track B**<br>(Substantive) | **Smith & Kendall (1963)** (*BARS Anchoring*) integrated with substantive domain theory (specifically: contract law, service recovery, or strategic foresight) | **L1–L2:** Addressing baseline factual parameters of the case or scenario.<br><br>**L3:** Proportionate response formulating standard operational remedies.<br><br>**L4:** Balancing legal/financial liability against stakeholder equity; root-cause remediation.<br><br>**L5:** Proactive systemic risk containment and strategic value creation. | **Substantive Professional Errors:**<br><br>• Defensive externalization or ignoring stakeholder grievances.<br><br>• Premature unhedged admission of legal/financial liability.<br><br>• Vacuous apologies lacking concrete operational action plans.<br><br>• Naive linear trend extrapolation presented as foresight. |

#### 5.4.4. Design-Time Human Curation and Empirical Scope Boundaries

The rigorous mapping above demonstrates why Quorum matrices are compiled through **Design-Time Human Curation** rather than unconstrained runtime LLM generation:

1. **Immunity to Second-Order Hallucinations and Rice's Theorem:** As established in Sections 2.1 and 4.1.1, arbitrary semantic consequence ($\mathcal{C}_i \models \tau_i$) across unconstrained text is undecidable without stochastic evaluation. By binding every positive ($\pi_i = +1$) and negative ($\pi_i = -1$) criterion to a pre-compiled BARS rubric and strict contrastive pair (`ContrastivePairDTO`), the LLM is stripped of judicial authority and restricted to a deterministic syntactic sensor.
2. **Psychometric Invariance and Regulatory Auditability:** Because evaluation matrices exist as versioned, immutable database entities (`ConfigDict(frozen=True)`), every execution is scored against an identical Lipschitz-stable benchmark (Equation 17), guaranteeing longitudinal repeatability across evaluation cohorts.
3. **Classical Theories as Cognitive Compilers:** Domain architects need not invent evaluative dimensions ad-hoc in Quorum Studio (`bars_matrix_builder.dart`). Sheridan–Verplank, Toulmin, Pearl, Bloom, Popper, and Kahneman provide an established five-tier competence continuum ($\pi_i = +1$) and a canonical error taxonomy ($\pi_i = -1$). Domain experts map specialized terminology directly into these established structures, after which automated AST verification suites (`scripts/sanitize_seed_vault.py`, `test_matrix_anchoring_rules.py`) guarantee lexical anchorability and prevent overfitting.

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

*Empirical Scope Boundary and Prospective Cross-Domain Validation:* While the empirical case study in Chapter 8 examines a two-matrix configuration ($\mathcal{M}_{\text{HACM}}$ and $\mathcal{M}_{\text{Causal}}$) within strategic foresight, Quorum's data-driven matrix engine is architecturally domain-agnostic. In ongoing research and prospective validation campaigns, this multi-matrix space ($\mathbf{\Psi}$) is systematically applied to enterprise contract review, regulatory compliance audits, and multi-agent software engineering workflows across diverse organizational cohorts and foundation model families.

---

## 6. Architectural Principles and Verified Mathematical Properties

*Epistemic Calibration and System Scope:* To preserve strict scientific integrity and avoid theoretical inflation, we explicitly partition the formal framework into two practical categories:
1. **Architectural Principles:** Structural design invariants inherited from established computer science (Church-Rosser lambda confluence, Kahn Process Networks, and discrete topological DAG scheduling) that govern deterministic asynchronous orchestration.
2. **Mathematically Verified System Properties:** Analytical properties of our verification and scoring pipelines (lexical error suppression bounds, Lipschitz score stability, and topological reachability) that guarantee numerical and epistemic predictability.

### Architectural Principle 1: Confluent Neurosymbolic Wave Scheduling

**Architectural Principle 1 (Wave Confluence under Kahn Ordering and Pure Computations).** *Let $\mathcal{G}_{\text{DAG}} = (\mathcal{V}_{\text{cog}}, \mathcal{E}_{\text{dep}})$ be a finite directed acyclic graph partitioned into $K$ disjoint topological waves $W_0, W_1, \dots, W_{K-1}$ via Kahn's partial ordering (Kahn, 1962). Let each node operator $\Phi_v: \prod_{u \in \text{Parents}(v)} \mathcal{O}_u \times \mathcal{S}_{\text{global}} \to \mathcal{O}_v$ be a pure compute function executing over immutable, validated Data Transfer Objects (DTOs) with zero shared memory side-effects. By the Church-Rosser theorem (Church & Rosser, 1936) and the determinism invariants of Kahn Process Networks (Kahn, 1974), any arbitrary asynchronous resolution order or coroutine scheduling permutation $\pi \in \text{Perm}(W_k)$ within `asyncio.TaskGroup` converges deterministically to the identical unique wave state snapshot $\mathcal{O}_{W_k}$, and the global system pipeline terminates at an invariant fixed-point state $\mathcal{S}^* = (\Phi_{W_{K-1}} \circ \dots \circ \Phi_{W_0})(\mathcal{S}_0)$.*

*Architectural Context & Contribution:* Confluence of pure functions over immutable inputs in acyclic topologies is a well-established foundational property of theoretical computer science (Church & Rosser, 1936; Kahn, 1974). We do not claim wave confluence as a novel mathematical discovery. Rather, Quorum's real-world contribution is the **strict architectural enforcement of referential transparency within a distributed LLM runtime**:
1. Operators communicate exclusively via immutable, frozen Pydantic DTOs (`ConfigDict(frozen=True)`).
2. Cognitive engines adhere to the Pure Compute Engine Law (100% computational pipelines with zero shared locks, event listeners, or mutable globals).
3. Concurrency throttling is cleanly decoupled into dynamic HTTP semaphore pools, preventing runtime deadlocks while guaranteeing bit-level deterministic state reproduction across re-executions.

---

### Architectural Property 1: Deterministic Error Suppression via Lexical Grounding and Role Asymmetry

**Property 1 (Deterministic Epistemic Error Suppression).** *Let an ensemble of $M$ frontier LLM evaluators exhibit pairwise error correlation $\text{Cov}(X_i, X_j) = \rho_{ij} \ge \rho_{\min} > 0$ due to shared pretraining corpora (Common Crawl, Wikipedia). While democratic majority voting hits an asymptotic error floor governed by effective sample size $M_{\text{eff}} \le 1/\rho_{\min}$, Quorum's two-tier neurosymbolic firewall—combining Role-Asymmetric Popperian Falsification ($\pi = -1$) with deterministic Physical Lexical Grounding ($\kappa \in \{0, 1\}$) over pre-compiled BARS criteria—decouples epistemic error suppression from model independence, bounding system acceptance error strictly by exact lexical substring collision tolerances:*

$$P(\text{System False Accept}) \le P_{\text{prior}}(\text{Hallucination}) \cdot P(\kappa_i = 1 \mid \text{Hallucination}) \le \epsilon_{\text{lexical}} \to 0 \tag{18}$$

*Analytical Verification & Derivation:*

1. **Failure of Democratic Consensus under Correlated Priors:** Let $X_1, \dots, X_M \in \{0, 1\}$ be binary error indicators for model evaluators on a deceptive prompt. Due to overlapping pretraining distributions, the average pairwise correlation is non-zero: $\bar{\rho} \ge \rho_{\min} > 0$. The effective sample size is bounded asymptotically:

$$M_{\text{eff}} = \frac{M}{1 + (M-1)\bar{\rho}} \implies \lim_{M \to \infty} M_{\text{eff}} = \frac{1}{\bar{\rho}} < \infty \tag{19}$$

If the prompt triggers a shared pretraining attractor where individual error probability $p > 0.5$, democratic voting inverts: $P(\text{Consensus Error}) \to 1$ as $M \to \infty$. Thus, model multiplexing alone cannot guarantee epistemic reliability.

2. **Asymmetric Popperian Falsification Barrier:** Quorum breaks symmetric voting by establishing role asymmetry. An explicit adversarial falsifier is parameterized with negative polarity ($\pi_i = -1$) under the Popperian Null Hypothesis: a claim is assumed *invalid or pseudo-competent* unless surviving rigorous counter-evidence extraction. By separating the extraction agent from the falsification auditor, the joint acceptance condition requires:

$$P(\text{Claim Pass}) = P(\text{Extracted}) \cdot (1 - P(\text{Falsified} \mid \text{Extracted})) \tag{20}$$

3. **Deterministic Physical Lexical Firewall ($\kappa \in \{0, 1\}$):** Regardless of LLM consensus or correlation $\bar{\rho}$, every extracted claim must satisfy the strict lexical grounding predicate:

$$\kappa_i = \mathbb{I}\left( \text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1 \right) \in \{0, 1\} \tag{21}$$

where $\mathcal{C}_i$ is the exact textual citation and $\mathcal{D}$ is the raw immutable source document. A hallucinated assertion $a_{\text{halluc}}$ can be accepted if and only if its verbatim citation physically matches an existing text span in $\mathcal{D}$:

$$P(\text{System False Accept}) = P(\text{Hallucinated Assertion}) \cdot P(\text{find}(\mathcal{C}_{\text{halluc}}, \mathcal{D}) \neq -1) \tag{22}$$

Because the lexical matcher is an exact, non-fuzzy string boundary invariant implemented in deterministic Python code, $P(\text{find}(\mathcal{C}_{\text{halluc}}, \mathcal{D}) \neq -1) \le \epsilon_{\text{lexical}}$, where $\epsilon_{\text{lexical}}$ is the probability of random string collision across the finite source corpus length $\vert{}\mathcal{D}\vert{}$. Furthermore, because target propositions $\tau_i$ are constrained to pre-compiled BARS rubrics rather than unconstrained model generation, semantic drift is bounded by rubric specification. Even when model representations are fully correlated ($\bar{\rho} \to 1$), hallucination acceptance is suppressed deterministically to zero.

---

### Architectural Property 2: Discrete ATMS Reachability and Cascade Fault Isolation

**Property 2 (Warrant Independence and Cascade Fault Isolation).** *Let an Argumentative Discourse SCM be compiled into an explicit discrete argument DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{atom}}, \mathcal{E}_{\text{deps}})$, where explicit claims $\mathbf{V}$ and operational warrants $\mathbf{W}$ are grounded in text ($\kappa = 1$). Assume latent conversational enthymemes $U_{\text{enthymeme}}$ act as potential unstated confounders. If a discrete structural graph surgery $\text{do}(X = \text{FAILED})$ on the surgery graph $\mathcal{G}_{\overline{X}}$ alters dependent claim validity via deterministic reachability $\text{Reach}(\mathcal{G}_{\overline{X}}, X) \cap \{Y\} \neq \emptyset$, while the reverse perturbation leaves antecedent truth invariant $X \notin \text{Reach}(\mathcal{G}_{\overline{Y}}, Y)$, and the text provides an explicit physical warrant $\mathbf{W}_{XY}$, then the directed argumentative dependency $X \xrightarrow{\mathbf{W}_{XY}} Y$ is structurally sound, self-contained, and shielded from enthymemic confounding.*

*Topological Derivation & System Mechanics:*

1. **Discrete Graph Surgery via Dual-Engine Truth Maintenance:** Rather than attempting observational density estimation via statistical do-calculus, discourse graph surgery and truth maintenance are evaluated deterministically in pure Python through decoupled dual-engine mechanics:
   * **Forward Wave Scheduling and Reachability (`TopologicalEvaluator.evaluate_graph`):** Enforces Kahn topological wave execution under strict `CONJUNCTIVE_AND` precondition rules. Applying structural intervention $\text{do}(X = \text{FAILED})$ or observing an antecedent precondition mismatch severs forward validity, deterministically cascading downstream reachability $\text{Reach}(\mathcal{G}_{\overline{X}}, X)$ into `BLOCKED` or `N_A` states without LLM invocation.
   * **Backward Blame Attribution and Root Cause Isolation (`CausalDiscoveryEngine.execute`):** Operates on the mined argument graph by traversing inbound causal edges (`in_deps`) via bounded breadth-first search. When downstream failures occur, the engine isolates upstream root causes ($\text{BlameParents}(X) = \emptyset$) from secondary cascade consequences ($\text{BlameParents}(Y) = \{ X \}$), preventing double-penalization.

2. **Topological Asymmetry and Reachability:** Let $\text{Reach}(\mathcal{G}, v)$ denote the set of all nodes reachable via directed paths from $v$. The invariant $X \notin \text{Reach}(\mathcal{G}_{\overline{Y}}, Y)$ proves that premise $X$ is topologically upstream from outcome $Y$:

$$(X \perp_{\mathcal{G}_{\overline{Y}}} Y) \implies Y \notin \text{Ancestors}(X) \tag{23}$$

No backward causal flow exists in the authored discourse. Concurrently, $Y \in \text{Reach}(\mathcal{G}_{\overline{X}}, X)$ confirms that $Y$ is structurally downstream from $X$:

$$(Y \not\!\perp_{\mathcal{G}_{\overline{X}}} X) \implies X \in \text{Ancestors}(Y) \tag{24}$$

3. **Enthymemic Confounder Isolation via Grounded Warrants:** Suppose an unstated assumption $U_{\text{enthymeme}}$ creates a spurious correlation $X \leftarrow U_{\text{enthymeme}} \to Y$ (a rhetorical leap where the author omitted mediating operational steps). Under the discrete intervention $\text{do}(X = \text{FAILED})$, the path through $X$ is severed. If the author omitted explicit warrants ($\mathbf{W}_{XY} = \emptyset$), `CausalDiscoveryEngine` detects that:

$$\text{BlameParents}(Y) = \{ X \} \implies \text{Status}(Y) \gets \text{BLOCKED} \tag{25}$$

and the audit flags an ungrounded argumentative leap (Rung 1).

Conversely, if the author explicitly stated and grounded the operational warrant $\mathbf{W}_{XY}$ ($\kappa(\mathbf{W}_{XY}) = 1$), the active transmission mechanism establishes an independent verifiable edge $X \xrightarrow{\mathbf{W}_{XY}} Y$. In discrete graph surgery, the warrant $\mathbf{W}_{XY}$ provides the deterministic transmission mechanism, shielding the claim from unstated enthymemes and confirming Rung 2/3 explanatory rigor.

---

## 7. Error Propagation and Cascade Suppression Pipeline

Unlike standard unconstrained LLM pipelines where intermediate hallucinations cascade unchecked, Quorum forces state through a four-stage suppression barrier:

$$\mathcal{S}_{\text{out}} = (\Phi_{\text{synth}} \circ \Phi_{\text{score}} \circ \Phi_{\text{fals}} \circ \Phi_{\text{TDA}} \circ \Phi_{\text{ingress}})(\mathcal{S}_{\text{in}} + \xi) \tag{26}$$

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
        | - Null hypothesis (κ = 0)                     |
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
        | - Power curve damping (γ = 1.25)              |
        +-----------------------+-----------------------+
                                |
                                v
                    Deterministic Final State

```

---

## 8. Empirical Validation: The Sitra Strategic Foresight Audit

To benchmark the theoretical framework against real-world data, the Quorum engine was deployed to audit an executive foresight analysis task based on the Sitra Megatrend dataset (2017–2023). The audit evaluated both the supervisory interaction (`Chat`) and the produced strategic brief (`Lopputuote`) under strictness $\theta = 50\%$ ($\gamma = 1.25$).

### 8.1. Evaluated Score Breakdown and Reconciliation

| Parameter | HACM (Chat) | Causal (Report) |
| --- | --- | --- |
| Execution ID | exe_c0953f62f2014b40 | exe_c0953f62f2014b40 |
| Total Criteria Evaluated | 25 | 25 |
| Anti-Pattern Checks ($\pi = -1$) | 13/13 clean | 13/13 clean |
| Penalty Multiplier ($\Pi_{\text{penalty}}$) | **1.0000** | **1.0000** |
| Capability Criteria ($\pi = +1$) | 12 total | 12 total |
| Level 1 Passed (Weight x1) | 2 / 2 passed ($2.0$) | 1 / 1 passed ($1.0$) |
| Level 2 Passed (Weight x2) | 1 / 2 passed ($2.0$) | 2 / 2 passed ($4.0$) |
| Level 3 Passed (Weight x3) | 1 / 2 passed ($3.0$) | 0 / 3 passed ($0.0$) |
| Level 4 Passed (Weight x4) | 0 / 3 passed ($0.0$) | 0 / 3 passed ($0.0$) |
| Level 5 Passed (Weight x5) | 0 / 3 passed ($0.0$) | 0 / 3 passed ($0.0$) |
| Achieved Points ($A$) | **7.0 pts** | **5.0 pts** |
| Maximum Points ($M$) | **39.0 pts** | **41.0 pts** |
| Linear Ratio ($\rho = A / M$) | $17.95\%$ ($7/39$) | $12.20\%$ ($5/41$) |
| Exponent ($\gamma$ at $50\%$) | $1.2500$ | $1.2500$ |
| Curved Ratio ($\rho^{1.25}$) | $0.116827$ | $0.072066$ |
| **Final Normalized Score** | **11.68 / 100 (11.7%)** | **7.21 / 100 (7.2%)** |
| Verdict | Sparrer Profile | Associative Rung 1 |

### 8.2. Granular Causal Graph Extraction Metrics

The automated pipeline parsed the corpus into a Linked Atom Graph containing **255 extracted causal propositions**:

| Metric Parameter | Value | Architectural Significance |
| --- | --- | --- |
| Total Causal Propositions | 255 | Raw Cognitive Proposition Pool |
| Validated Connected Nodes | 161 (63.1%) | Context-Anchored Evidence Chains |
| Orphan Claims ($\text{InDeg} = 0$) | 94 (36.9%) | Unanchored Leaps or Exogenous Axioms |
| Maximum In-Degree (Hub) | 5.0 | Central Terminal Recommendation |
| Mean In-Degree Connectivity | 0.41 | Sparse Linear Argumentative Topology |

### 8.3. Cognitive Depth and the "Illusion of Control"

Linguistic analysis revealed a severe disparity between form and substance:

* **Mechanical Phrase Load:** $0.00 / 2.0$ (Zero clichés or empty buzzwords detected).
* **Cognitive Authenticity:** $1.47 / 3.0$ (Low, unreflective routine delegation).
* **Form-to-Content Disparity Ratio:** $1.53$ (Verdict: **IN CONFLICT**).

*Orthogonal XAI Diagnostic Classification:* The Form-to-Content Disparity Ratio is computed strictly as an orthogonal Explainable AI (XAI) diagnostic metric by `variance_engine.py`. Parameterized by the absolute difference between cognitive authenticity and the inverse mechanical phrase load ($\Delta = |\text{Score}_{\text{cog}} - (3.0 - \text{Load}_{\text{mech}})| = |1.47 - (3.0 - 0.00)| = 1.53$), this metric quantifies operator misalignment and detects superficial compliance without altering the evaluative capability scoring. It does NOT deduct points from the BARS normalized score ($11.7\%$ / $7.2\%$) or mutate Equation (17). Evaluative capability scoring (BARS) and orthogonal cognitive diagnostic classification remain strictly decoupled.

The user formulated concise, jargon-free prompts (*"mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila"*), which created an **Illusion of Control**. The operator assumed the concise prompt guaranteed an analytically rigorous output. In reality, the AI's first associative draft was accepted without counterfactual testing, sensitivity analysis, or trade-off evaluation.

---

## 9. Synthesis: Quorum’s Positioning in the Research Landscape

```
           NEUROSYMBOLIC & FORMAL
                     ^
                     |   * QUORUM ARCHITECTURE
                     |     - Kahn Wave DAG
                     |     - LAG 5-tuple
                     |     - SCM do-surgery
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

* **Chain-of-Thought (CoT) (Wei et al., 2022):** CoT relies entirely on the autoregressive distribution to maintain reasoning consistency. As demonstrated in Equation (2), early errors cascade exponentially. Quorum eliminates autoregressive reasoning chains, substituting them with Kahn-sorted wave execution (Architectural Principle 1) over an explicit acyclic network.
* **Tree of Thoughts (ToT) (Yao et al., 2023) and Graph of Thoughts (GoT) (Besta et al., 2024):** ToT and GoT structure thoughts into search graphs (BFS/DFS). However, their nodes remain unstructured natural language strings, and state pruning relies on LLM self-evaluation. Quorum’s nodes are strictly typed computational operators producing validated DTOs, and state termination is mathematically guaranteed.
* **ReAct (Yao et al., 2022) and Reflexion (Shinn et al., 2023):** Reflexion implements heuristic self-correction loops. However, recent empirical work (Huang et al., 2023) proves that LLMs cannot reliably self-correct without external deterministic ground truth. Quorum replaces circular self-reflection with external, asymmetric Popperian falsification.

### 9.2. Comparison with Retrieval and Factuality Verification

* **Standard RAG (Lewis et al., 2020) and Self-RAG (Asai et al., 2023):** Standard RAG retrieves passage chunks via embedding similarity ($k$-NN), which introduces irrelevant context and fails on fine-grained logic. Quorum rejects chunk-level vector retrieval, deploying the epistemic atomization morphism $\alpha(\mathcal{D}) \to \mathcal{A}$ to evaluate discrete propositions against an absolute lexical null hypothesis.
* **FActScore (Min et al., 2023) and RARR (Gao et al., 2023):** FActScore decomposes text into atomic facts, but evaluates them symmetrically as binary factual counters. Quorum structures atoms into the five-tuple $a_i = \langle \tau_i, \mathcal{C}_i, \sigma_i, \pi_i, \kappa_i \rangle$, tracking speaker attribution, evidentiary polarity, and directional causality within a coherent multigraph.

### 9.3. Cross-Paradigm Architectural Comparison

| Dimension | Standard RAG / CoT | ReAct / Reflexion | Quorum Engine |
| --- | --- | --- | --- |
| **Orchestration** | Linear Sequence | Heuristic Loop | **Kahn Wave DAG** |
| **State Verify** | None (Generative) | Self-Reflection | **DTO Invariants** |
| **Grounding** | k-NN Dense Vector | Tool Output | **Lexical Null $H_0$** |
| **Causal Logic** | None (Spurious) | Trial-and-Error | **A-SCM & Truth Maint.** |
| **Scoring** | LLM-as-a-Judge | Heuristic | **Lipschitz BARS** |
| **Falsification** | None | Reranking | **Asymmetric Malus** |
| **Termination** | Max Length | Max Iterations | **Proved Acyclic** |
| **Agency Audit** | None | None | **HACM Tracking** |

---

## 10. Limitations and Practical Considerations

1. **Computational Overhead and FinOps Allocation (Two-Tier Verification Strategy):** Parallel ensemble verification and deterministic lexical verification (Architectural Property 1) increase inference token consumption relative to unverified single-pass sampling. In Quorum, FinOps resource allocation and verification rigor are strictly partitioned into a Two-Tier Verification Architecture:
   * **Production DAG Execution:** DAG nodes evaluate high-entropy proposition atoms using a single-pass Best-of-3 ensemble executed strictly with the single model configuration assigned to the step via Model Garden (`LLMClient.from_strategy`), dispatching parallel calls via `asyncio.TaskGroup` (`settings.ensemble_parallelism = 3`, `settings.ensemble_min_consensus = 2`) with Popperian Null Hypothesis tie-breaking. Acknowledge that while future architectural evolutions may evaluate heterogeneous multi-provider runtime dispatch, production currently enforces standard single-model execution with zero backend code changes.
   * **Offline Cross-Model Variance Testing:** Comprehensive multi-provider benchmarking across diverse foundation model families (including Gemini, Claude, OpenAI, and DeepSeek) is decoupled into dedicated offline variance testing suites (`scripts/run_e2e_variance_test.py` and `backend_v2/workers/variance_synthesis.py`). This assesses cross-model parameter stability and alignment variance without introducing live production latency penalties or heterogeneous API key dependencies into real-time DAG scheduling.
2. **Exogenous Axiom Misattribution:** In sparse strategic corpora, separating genuine exogenous axioms ($U_i$) from unanchored orphan claims relies on accurate bounding box parsing. If an author introduces implicit domain premises without citations, TDA provenance verification flags them as orphans ($\kappa_i = 0$). Domain-specific white-listing of axiomatic priors resolves this friction.
3. **Cohort Percentile Calibration:** The scores reported ($11.7\%$ and $7.2\%$) reflect strict BARS damping ($\gamma = 1.25$). Without peer comparison, operators may perceive these scores as excessively punitive. Providing percentile rankings against normalized organizational cohorts contextualizes the diagnostic.
4. **Episodic Identifier Aliasing, Attention Economics, and Fail-Fast State Hydration:** While Section 2.1 formalizes the bijective mapping $\mu: \mathcal{I}_{\text{UUID}} \longleftrightarrow \mathcal{V}_{\text{alias}}$, maintaining distributed referential integrity requires strict lifecycle isolation. In Quorum, `AliasEngine` instances are strictly non-singleton, instantiated per execution job to prevent cross-tenant memory leakage. When execution is distributed across asynchronous background workers (specifically Celery or Arq worker pools), the mapping state is serialized into an immutable snapshot (`AliasManifest`) transported within `step_metadata`. The receiver reconstitutes the bijection (`AliasEngine.from_manifest`) and executes strict fail-fast validation: any hallucinated alias matching an active prefix that does not exist in the manifest immediately halts execution with an unrecoverable validation error (`AppException(422)`), preventing corrupted foreign keys from entering persistent DAG state.

---

## 11. Conclusions

The Quorum architecture establishes a mathematically rigorous foundation for turning stochastic large language models into verifiable, epistemically anchored expert systems. By replacing unconstrained autoregressive generation with:

* Kahn wave-based DAG scheduling (Architectural Principle 1),
* Deterministic physical lexical grounding and role-asymmetric Popperian falsification (Architectural Property 1),
* Monotonic, Lipschitz-stable BARS power-curve scoring (Mathematical Property 1), and
* Discrete structural argument surgery and ATMS-based fault isolation (Architectural Property 2),

the framework eliminates hallucination cascades and enforces structural accountability. The Sitra empirical audit validates that Quorum cuts through polished surface fluency to diagnose cognitive delegation traps, providing an auditable, verifiable methodology for enterprise and strategic artificial intelligence.

---

### Selected References

1. **Besta, M. et al. (2024).** Graph of Thoughts: Solving Elaborate Problems with Large Language Models. *AAAI Conference on Artificial Intelligence (AAAI 2024)*.
2. **Buçinca, Z. et al. (2021).** To Trust or to Think: Cognitive Forcing Functions to Address Overreliance on AI. *ACM Human Factors in Computing Systems (CHI 2021)*.
3. **Carlsson, G. (2009).** Topology and data. *Bulletin of the American Mathematical Society*, 46(2), 255–308.
4. **Chernoff, H. (1952).** A measure of asymptotic efficiency for tests of a hypothesis based on the sum of observations. *The Annals of Mathematical Statistics*, 23(4), 493–507.
5. **Church, A., & Rosser, J. B. (1936).** Some properties of conversion. *Transactions of the American Mathematical Society*, 39(3), 472–482.
6. **de Kleer, J. (1986).** An assumption-based TMS. *Artificial Intelligence*, 28(2), 127–162.
7. **Doyle, J. (1979).** A truth maintenance system. *Artificial Intelligence*, 12(3), 231–272.
8. **Dung, P. M. (1995).** On the acceptability of arguments and its fundamental properties: A formal framework for computational argumentation. *Artificial Intelligence*, 77(2), 321–357.
9. **Edelsbrunner, H., & Harer, J. (2010).** *Computational Topology: An Introduction*. American Mathematical Society.
10. **Gao, L. et al. (2023).** RARR: Researching and Refining What Language Models Say with Retrieval. *Association for Computational Linguistics (ACL 2023)*.
11. **Huang, J. et al. (2023).** Large Language Models Cannot Self-Correct Reasoning Yet. *arXiv preprint arXiv:2310.01798*.
12. **Kahn, A. B. (1962).** Topological sorting of large networks. *Communications of the ACM*, 5(11), 558–562.
13. **Kahn, G. (1974).** The semantics of a simple language for parallel programming. *Information Processing 74: Proceedings of IFIP Congress 74*, 471–475.
14. **Khattab, O. et al. (2023).** DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines. *arXiv preprint arXiv:2310.03714*.
15. **Kıcıman, E. et al. (2023).** Causal Reasoning and Large Language Models: Opening a New Frontier for Causality. *Microsoft Research Technical Report*.
16. **Lewis, P. et al. (2020).** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems (NeurIPS 2020)*.
17. **Min, S. et al. (2023).** FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. *Empirical Methods in Natural Language Processing (EMNLP 2023)*.
18. **Pan, L. et al. (2023).** Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Reasoning. *Findings of EMNLP 2023*.
19. **Parasuraman, R., Sheridan, T. B., & Wickens, C. D. (2000).** A model for types and levels of human interaction with automation. *IEEE Transactions on Systems, Man, and Cybernetics - Part A: Systems and Humans*, 30(3), 286–297.
20. **Pearl, J. (2009).** *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
21. **Popper, K. (1959).** *The Logic of Scientific Discovery*. Hutchinson & Co.
22. **Sheridan, T. B., & Verplank, W. L. (1978).** *Human and Computer Control of Undersea Teleoperators*. MIT Man-Machine Systems Laboratory.
23. **Shinn, N. et al. (2023).** Reflexion: Language Agents with Verbal Reinforcement Learning. *NeurIPS 2023*.
24. **Smith, P. C., & Kendall, L. M. (1963).** Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. *Journal of Applied Psychology*, 47(2), 149–155.
25. **Spirtes, P., Glymour, C. N., & Scheines, R. (2000).** *Causation, Prediction, and Search*. MIT Press.
26. **Tarjan, R. (1972).** Depth-first search and linear graph algorithms. *SIAM Journal on Computing*, 1(2), 146–160.
27. **Toulmin, S. E. (1958).** *The Uses of Argument*. Cambridge University Press.
28. **Vaswani, A. et al. (2017).** Attention Is All You Need. *Advances in Neural Information Processing Systems (NeurIPS 2017)*.
29. **Wang, X. et al. (2022).** Self-Consistency Improves Chain of Thought Reasoning in Language Models. *ICLR 2023*.
30. **Wei, J. et al. (2022).** Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. *NeurIPS 2022*.
31. **Yang, K. et al. (2023).** LeanDojo: Theorem Proving with Retrieval-Augmented Language Models. *NeurIPS 2023*.
32. **Yao, S. et al. (2022).** ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR 2023*.
33. **Yao, S. et al. (2023).** Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *NeurIPS 2023*.
34. **Zečević, M. et al. (2023).** Causal Parrots: Large Language Models May Talk Versus Reason on Causality. *NeurIPS 2023*.
35. **Zheng, L. et al. (2023).** Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *NeurIPS 2023*.