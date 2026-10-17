# Epistemic Determinism and the Architecture of Causal-Topological Orchestrated Inference in Stochastic Large Language Models: Theoretical Framework, Mathematical Model, and Empirical Validation

**Quorum Research Collective**

*arXiv preprint: cs.AI / cs.CL / cs.DS*

---

### Abstract

Autoregressive Large Language Models (LLMs) operate as stochastic token probability generators whose unconstrained inference paths are fundamentally susceptible to hallucinations, semantic drift, error compounding, and epistemic instability. This paper presents the **Quorum** architecture: a formal neurosymbolic computational framework that transforms unconstrained stochastic generative processes into a deterministically supervised, epistemically anchored state machine. The theoretical foundation comprises:

> 1. Propositional epistemic atomization via the five-tuple Linked Atom Graph (LAG),
> 2. Wave-based topological execution over a Cognitive Directed Acyclic Graph (Cognitive DAG),
> 3. Topological Directed Atom (TDA) poset wave scheduling governed by an orthogonal two-tier epistemic firewall (deterministic physical citation provenance and role-asymmetric Popperian falsification),
> 4. Autonomous structural argument evaluation via discrete graph surgery, Assumption-Based Truth Maintenance Systems (ATMS), and Toulmin's argumentation structure,
> 5. Pure stateless argument causal cohesion evaluation via the 0-token Cumulative Guttman Invariant, and
> 6. An orthogonal multi-factor BARS evaluation matrix combining asymmetric Popperian falsification, event-sourced state projection (`StateProjector`), and continuous piecewise power-curve damping.

We formalize this framework through two core architectural principles (confluent wave scheduling under Kahn partial ordering and epistemic warrant reachability under discrete ATMS graph surgery) and two mathematically verified system properties (decoupled epistemic error suppression separating physical citation provenance from semantic entailment, and monotonic Lipschitz score stability). The framework is empirically validated through two controlled pairwise audit trials on an executive strategic foresight corpus ($K = 2$ paired trials, 4 full workflow executions, $N = 110$ common proposition atoms per trial), demonstrating high inter-run stability (observed raw agreement $95.45\%$ and $98.18\%$; Cohen's $\kappa = 0.9064$ and $\kappa = 0.9633$; mean Shannon entropy $\bar{H} \le 0.0455$) under unconstrained stochastic frontier sampling ($T = 1.0$), with zero system crashes or Dead Letter Queue (DLQ) drops. We report these initial findings transparently from two paired experimental runs, noting that broader multi-corpus evaluations are required for population-level statistical generalization. Finally, we synthesize Quorum's positioning across the landscape of reasoning architectures, retrieval frameworks, and cognitive governance paradigms.

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

**Definition 1 (Epistemic Atom).** Every epistemic atom $a_i \in \mathcal{A}$ is formally defined as an immutable five-tuple:

$$a_i = \langle \tau_i, \mathcal{C}_i, \sigma_i, \pi_i, \kappa_i \rangle \tag{4}$$

* $\tau_i \in \mathcal{L}_{\text{prop}}$ is an atomic proposition formulated in formal logic with unambiguous truth-evaluable acceptance criteria.
* $\mathcal{C}_i \subset \Sigma^*$ is the spatial and contextual bounding box isolating the exact text span in $\mathcal{D}$ from which $\tau_i$ was derived.
* $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ is the speaker attribution index, separating human supervisory intent from model-generated synthetic drafts.
* $\pi_i \in \{+1, -1\}$ is the evidentiary polarity index: $\pi_i = +1$ denotes a positive capability claim (demonstrating analytical competence), whereas $\pi_i = -1$ designates an asymmetric anti-pattern detector (identifying cognitive failure modes, fallacies, or uncritical adoption).
* $\kappa_i \in \{0, 1\}$ is the lexical provenance anchoring index, governed by an uncompromising null hypothesis parameterized by strictness $\theta \in [0, 100]$:

$$\kappa_i = \begin{cases} 1, & \text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta) \;\land\; \text{Prov}(\mathcal{C}_i, \sigma_i) \;\land\; \text{Triangulate}(\mathcal{T}_i, \mathcal{C}_i) \\ 0, & \text{otherwise} \end{cases} \tag{5}$$

where $\text{Lex}(\mathcal{C}_i, \mathcal{D}; \theta)$ evaluates the deterministic lexical verification cascade (collapsing to exact normalized substring containment $\text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1$ at $\theta \ge 100$, and incorporating bounded morphological stem-sequence verification for agglutinative inflections at $\theta < 100$), $\text{Norm}(\cdot)$ denotes Unicode NFKC/NFD diacritic decomposition and formatting strip, $\text{Prov}(\cdot)$ enforces structured XML speaker isolation, and $\text{Triangulate}(\cdot)$ validates internal CoT consistency against syntactic anchors.

*The Syntactic Provenance vs. Semantic Entailment Boundary:* An exact substring match $\text{find}(\mathcal{C}_i, \mathcal{D}) \neq -1$ provides *physical provenance*—irrefutable proof that citation $\mathcal{C}_i$ physically exists within document $\mathcal{D}$ and was neither fabricated nor spliced across disparate paragraphs. However, deterministic string matching is semantically blind: it verifies the syntactic existence of character sequences, not that proposition $\tau_i$ semantically follows from $\mathcal{C}_i$ ($\mathcal{C}_i \models \tau_i$). By Rice's Theorem applied to formal properties of discourse, universal automated verification of semantic entailment over unrestricted natural language is undecidable. Pre-compiling propositions $\tau_i$ as typed Behaviorally Anchored Rating Scale (BARS) rubrics in the Single Source of Truth (`seed_data.json`) defines the target hypotheses rigorously, but does not eliminate the semantic gap between a real quotation and its purported interpretation. Consequently, Quorum structures epistemic defense across two orthogonal layers:
1. **Deterministic Physical Grounding (Type I Defense):** Eliminates fabricated and chimera citations with mathematical certainty ($\kappa_i = 0$ if $\mathcal{C}_i \notin \mathcal{D}$), bounding citation fabrication error to the physical substring collision floor $\epsilon_{\text{lexical}} \to 0$.
2. **Adversarial Neurosymbolic Entailment (Type II Defense):** Constrains semantic misattribution ($\mathcal{C}_i \in \mathcal{D}$ but $\mathcal{C}_i \not\models \tau_i$) through role-asymmetric Popperian falsification ($\pi_i = -1$), syntactic anchor triangulation, and downstream Argumentative SCM (A-SCM) reachability pruning, ensuring that residual semantic drift is bounded by multi-agent audit consensus rather than conflated with lexical string matching.

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

### 4.1.1. Deterministic Physical Provenance Verification and Defense Against Fabricated Evidence

A foundational failure mode in contemporary LLM evaluation (including LLM-as-a-Judge, G-Eval, and Self-RAG) is **Second-Order Hallucination** (*Quis custodiet ipsos custodes?*). If a secondary LLM is queried to determine whether a document entails a proposition ($P(\text{Entail} \mid \mathcal{D}, \tau_i)$), the verifier is itself an autoregressive stochastic sampler susceptible to sycophancy, confirmation bias, and the synthesis of *chimera quotes* (stitching isolated words across disparate paragraphs into a fabricated sentence).

To defend against unanchored evidence and citation fabrications, Quorum strips the generative model of judicial authority. Rather than allowing the LLM to self-certify its outputs, evidence verification is structured across two orthogonal layers: physical citation provenance and exact lexical containment are verified **exclusively in pure deterministic Python code** (`AnchorValidationService`), while semantic entailment is audited through role-asymmetric Popperian falsification and downstream A-SCM reachability:

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

Under this five-gate architecture, propositional grounding does not rely on unconstrained LLM self-evaluation. An atom $\tau_i$ achieves physical citation anchoring ($\kappa_i = 1$) if and only if all five deterministic Python gates succeed, bounding the probability of accepting a fabricated or spliced citation by the physical string collision rate $\epsilon_{\text{lexical}} \to 0$.

*Formal Scope and the Semantic Undecidability Bound:* We explicitly distinguish between **Physical Citation Provenance** and **Universal Semantic Entailment**. In unconstrained natural language, determining whether an arbitrary premise $\mathcal{C}$ semantically entails an arbitrary conclusion $\tau$ without human supervision is undecidable (Rice's Theorem applied to semantic properties of formal discourse). Quorum does not claim universal automated semantic proof over arbitrary text. Rather, Quorum addresses the enterprise failure surface by decoupling verification into two orthogonal frontiers:
1. *Extrinsic Hallucinations (Type I: Fabricated / Chimera Quotes):* Deterministic Python gates guarantee that no ungrounded, fabricated, or spliced quotes penetrate the system ($P(\text{False Accept}_{\text{lexical}}) \le \epsilon_{\text{lexical}} \to 0$).
2. *Intrinsic Semantic Misattributions (Type II: Verbatim Non-Entailment, $\mathcal{C}_i \not\models \tau_i$):* For authentic quotations cited in support of an unfulfilled BARS criterion, semantic validity is governed by the stochastic error bounds of the multi-agent Popperian falsification ensemble ($\pi = -1$) and pruned downstream via Assumption-Based Truth Maintenance System (ATMS) reachability, decoupling physical provenance verification from semantic entailment judgment.

### 4.2. Argumentative Structural Dependency Models (A-SCM) and Truth Maintenance

*Ontological Scope and the Enthymeme Boundary:* Unlike physical systems where variables $\mathbf{V}$ represent empirical data-generating mechanisms, natural discourse is inherently pragmatic, elliptical, and enthymematic (Toulmin, 1958; Grice, 1975). Human authors routinely omit common-sense warrants and intermediate mechanisms. Therefore, Quorum does not claim that textual analysis discovers objective physical causality. Instead, Quorum formalizes the **Argumentative Structural Causal Model (A-SCM)**, evaluating the *internal explanatory sufficiency and structural evidentiary rigor* of the authored thesis.

**Definition 2 (Argumentative Structural Causal Model).** An authored discourse is modeled as a five-tuple:

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

### 4.2.1. Pure Stateless Causal Cohesion Evaluation and the 0-Token Cumulative Guttman Invariant

In contemporary multi-agent reasoning systems, assessing whether an authored discourse forms a coherent, non-trivial argument is routinely delegated to secondary LLM evaluation passes (e.g. LLM-as-a-Judge prompting with subjective instructions like *"Rate the causal coherence from 1 to 5"*). This practice introduces stochastic scoring variance, circular hallucinations, token cost explosions, and prompt-injection vulnerability.

Quorum eliminates stochastic judge prompts for argument cohesion through the **Pure Stateless `CausalCohesionEvaluator`** (`backend_v2/services/orchestrator/causal_discovery.py`), a deterministic compute engine that evaluates macro-argument structure directly from the topology of the mined Argument DAG $\mathcal{G}_{\text{LAG}} = (\mathcal{V}_{\text{atom}}, \mathcal{E}_{\text{deps}})$:

1. **The Cumulative Guttman Invariant:** Structural argument cohesion is formalized as a strictly cumulative, monotonic scale across Behaviorally Anchored Rating Scale (BARS) Tiers 1–5:
   * **Level 1 (Novice Floor Grounding):** The discourse consists of isolated claims, unanchored orphan assertions ($\mathcal{A}_{\text{orphan}}$), or trivial factual statements ($\text{InDegree} = 0, \text{OutDegree} = 0$).
   * **Level 2 (Emerging Linear Argumentation):** At least one valid two-node dependency chain ($X \to Y$) is established with verified physical citation provenance ($\kappa = 1$).
   * **Level 3 (Competent Toulmin Warrant Grounding):** The argument constructs non-trivial directed paths supported by explicit operational warrants ($\mathbf{W}_{XY}$), establishing verifiable transmission mechanisms between premises and conclusions.
   * **Level 4 (Proficient Branch Convergence):** Multi-premise convergence ($\text{InDegree}(Y) \ge 2$) or counter-argument insulation ($X \xrightarrow{\mathbf{W}} Y \land Z \xrightarrow{\mathbf{W}} Y$), demonstrating structural evidence triangulation without circular reasoning.
   * **Level 5 (Mastery & Counterfactual Boundary Testing):** Complex multi-tier argument topologies featuring antecedent branch convergence, explicit boundary condition testing, and resilient warrant trees surviving simulated node perturbations.

2. **The 0-Token Evaluation Contract:** Because `CausalCohesionEvaluator` evaluates topological graph invariants extracted during upstream DAG waves, BARS scoring requires zero additional LLM invocations ($0\text{ tokens consumed}$) under `default_strictness_level: 0`.

3. **Cycle Defect Quarantine:** If the topological cycle detector detects directed cycles ($\mathcal{C}_{\text{cycle}} \neq \emptyset$), the graph violates DAG partial order invariants. The evaluator flags a structural cycle defect (`CYCLIC_DEPENDENCY_DETECTED`), immediately clamping the argument cohesion score to the Novice floor ($l = 1$).

4. **Idempotent DAG Fusion and Concurrency Guards:** In multi-step or multi-model executions, redundant evaluations of identical causal sources are prevented via `_evaluated_causal_sources` idempotency guards with atomic `_update_lock` context reconciliation in the state reducer (`state_reducer.py`), guaranteeing deterministic, replayable scoring.

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
   * *Mathematical Impact & Decoupled Inverse Badging:* Verified anti-patterns deduct from the matrix score multiplicatively via $\Pi_{\text{penalty}} = \max(1 - P_{\max}, \prod_{k=1}^K (1 - p_k))$ (`falsifier_hook.py`, Equation 15), capped at $P_{\max} = 0.40$. Crucially, anti-pattern assertions do not award positive capability points ($A = 0$ pts). In the Server-Driven UI and tabular export tiers (22-column rectangular streaming), passing an anti-pattern displays as clean performance ($0\text{ p}$, Puhdas) rather than misleadingly awarding $+1\text{ point}$ (which would falsely conflate the absence of error with positive competence), while verified violations are badged distinctly (Negatiivinen löydös) with ML-ready numeric indicators (`is_inverse`, `points_awarded`).
   * *Anti-Synthetic Row Invariant & Empirical Hit Distribution:* Tabular exports project evaluated atoms $1:1$ without client-side flattener synthesis (`Anti-Synthetic Row Invariant`). Matrix summary tables format the empirical hit distribution ($k/N$ ratio) per BARS tier, while unmapped dynamic causal graph propositions are streamed transparently under `Logiikkamatriisi = 'Kausaalipäättely'`.

In accordance with Quorum's architectural compendium (`docs/architecture/08_matrix_explanations.md`) and seed vault (`seed_data.json`), assertions are anchored to classical theoretical literature across two mutually exclusive rubric tracks:

| Matrix Category & Speaker ($\sigma_i$) | Rubric Track | Classical Theoretical Grounding | Positive Capability Assertions ($\pi_i = +1$, BARS Tiers $l \in \{1, \dots, 5\}$) | Negative Anti-Pattern Falsifiers ($\pi_i = -1$, Malus Multiplier $\Pi_{\text{penalty}}$) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Human Agency & Collaboration (HACM)**<br><br>$\sigma_i = \text{USER}$ | **Track A**<br>(Developmental) | **Sheridan & Verplank (1978)** (*Levels of Automation*),<br><br>**Parasuraman et al. (2000)**,<br><br>**Kahneman (2011)** (*System 1 vs. 2*),<br><br>**Buçinca et al. (2021)** (*Cognitive Forcing*) | **L1–L2:** Foundational task framing and contextual bounding.<br><br>**L3:** Explicit boundary constraints, persona assignment, and criteria setting.<br><br>**L4:** Active adversarial challenging of AI drafts and error correction.<br><br>**L5:** Metacognitive steering, hypothesis forcing, and sovereign synthesis direction. | **Automation Bias & Passive Delegation (`passivity_hook.py`):**<br><br>• Unconstrained "do this for me" task abdication.<br><br>• Blind rubber-stamping of first-draft outputs.<br><br>• Relinquishing critical verification responsibility.<br><br>• Vacuous conversational prompts lacking steering content. |
| **2. Argumentative & Causal Structure (A-SCM)**<br><br>$\sigma_i = \text{ASSISTANT}$ | **Track B**<br>(Error Radar) | **Judea Pearl (2009)** (*Causal Ladder: Rungs 1–3*),<br><br>**Stephen Toulmin (1958)** (*Claim, Grounds, Warrant, Backing, Rebuttal*) | **L1–L2 (Rung 1):** Associative identification of variables and empirical correlations.<br><br>**L3 (Toulmin Warrant):** Explicit intermediate causal mechanism ($\mathbf{W}_{XY}$) justifying *why* $X \to Y$.<br><br>**L4 (Rung 2 Intervention):** Confounder isolation ($U$) and systemic policy side-effect modeling.<br><br>**L5 (Rung 3 Counterfactual):** "What-if" boundary stress tests, limit breaking, and opportunity cost analysis. | **Pseudo-Causality & Structural Collapse:**<br><br>• Conflating correlation with causation (bare trend listing).<br><br>• Orphan claims ($\mathcal{A}_{\text{orphan}}$) lacking evidentiary grounds or warrants ($\mathbf{W} = \emptyset$).<br><br>• Circular causal loops (`CYCLIC_DEPENDENCY_DETECTED`).<br><br>• Unqualified optimism omitting boundary exceptions (*Missing Rebuttal*). |
| **3. Critical Thinking & Epistemic Rigor**<br><br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track A & B**<br>(Hybrid) | **Benjamin Bloom (1956)** (*Cognitive Taxonomy*),<br><br>**Karl Popper (1959)** (*Empirical Falsifiability*) | **L1–L2 (Remember/Understand):** Nomenclature definition and baseline summarization.<br><br>**L3 (Apply/Analyze):** Deconstructing latent assumptions and identifying structural tensions.<br><br>**L4 (Evaluate):** Source critique, evidence weighting, and defining empirical falsification conditions.<br><br>**L5 (Create):** Synthesizing novel, empirically testable explanatory frameworks. | **Epistemic Immunization & Cognitive Biases (`falsifier_hook.py`):**<br><br>• Confirmation bias (discarding disconfirming evidence).<br><br>• Unfalsifiable tautologies and evasive non-committal prose.<br><br>• Substituting substantive depth with rhetorical buzzwords (*Jargon Load*). |
| **4. Domain & Task-Specific Substance**<br><br>$\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$ | **Track B**<br>(Substantive) | **Smith & Kendall (1963)** (*BARS Anchoring*) integrated with substantive domain theory (specifically: contract law, service recovery, or strategic foresight) | **L1–L2:** Addressing baseline factual parameters of the case or scenario.<br><br>**L3:** Proportionate response formulating standard operational remedies.<br><br>**L4:** Balancing legal/financial liability against stakeholder equity; root-cause remediation.<br><br>**L5:** Proactive systemic risk containment and strategic value creation. | **Substantive Professional Errors:**<br><br>• Defensive externalization or ignoring stakeholder grievances.<br><br>• Premature unhedged admission of legal/financial liability.<br><br>• Vacuous apologies lacking concrete operational action plans.<br><br>• Naive linear trend extrapolation presented as foresight. |

#### 5.4.4. Design-Time Human Curation and Empirical Scope Boundaries

The rigorous mapping above demonstrates why Quorum matrices are compiled through **Design-Time Human Curation** rather than unconstrained runtime LLM generation:

1. **Bounding Semantic Drift and Rice's Theorem:** As established in Sections 2.1 and 4.1.1, arbitrary semantic consequence ($\mathcal{C}_i \models \tau_i$) across unconstrained text is undecidable without stochastic evaluation. While binding every positive ($\pi_i = +1$) and negative ($\pi_i = -1$) criterion to a pre-compiled BARS rubric and strict contrastive pair (`ContrastivePairDTO`) constrains the hypothesis space and strips the generative model of unconstrained judicial authority, Quorum does not claim that rubric pre-compilation magically eliminates semantic drift. Rather, it converts open-ended generation into a targeted verification task, subjecting residual semantic ambiguity to role-asymmetric Popperian falsification and causal graph reachability pruning.
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

*Empirical Scope Boundary and Prospective Cross-Domain Validation:* While the empirical evaluation in Section 8 examines a five-matrix audit configuration within strategic foresight, Quorum's data-driven matrix engine is architecturally domain-agnostic. In ongoing research and prospective validation campaigns, this multi-matrix space ($\mathbf{\Psi}$) is systematically applied to enterprise contract review, regulatory compliance audits, and multi-agent software engineering workflows across diverse organizational cohorts and foundation model families.

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
4. State transitions across topological waves are persisted as an immutable event-sourced stream ($e_t \in \mathcal{E}_{\text{trace}}$, with `is_context_update=True`). The global context state $\mathcal{S}_t$ is reconstituted purely through deterministic event projection $\mathcal{S}_{t+1} = \text{Project}(\mathcal{S}_t, e_t)$ via `StateProjector`, completely banning in-place mutation of domain state dictionaries, eliminating anonymous multi-value state tuples ("Tuple Hell"), and guaranteeing bit-level deterministic execution replay and audit trails under EU AI Act Articles 12–15.

---

### Architectural Property 1: Decoupled Epistemic Error Suppression via Physical Grounding and Role Asymmetry

**Property 1 (Decoupled Epistemic Error Suppression).** *Let an ensemble of $M$ frontier LLM evaluators exhibit pairwise error correlation $\text{Cov}(X_i, X_j) = \rho_{ij} \ge \rho_{\min} > 0$ due to shared pretraining corpora (Common Crawl, Wikipedia). While democratic majority voting hits an asymptotic error floor governed by effective sample size $M_{\text{eff}} \le 1/\rho_{\min}$, Quorum decouples epistemic error suppression into two orthogonal dimensions: deterministic Physical Lexical Grounding ($\kappa \in \{0, 1\}$) and Role-Asymmetric Popperian Falsification ($\pi = -1$). The system false acceptance error is strictly bounded by the sum of physical substring collision tolerances and adversarial semantic falsification miss rates:*

$$P(\text{System False Accept}) \le P(H_{\text{fab}}) \cdot \epsilon_{\text{lexical}} + P(H_{\text{mis}}) \cdot \beta_{\text{fals}} \tag{18}$$

*where $H_{\text{fab}}$ denotes extrinsic citation fabrication ($\mathcal{C}_i \notin \mathcal{D}$), $H_{\text{mis}}$ denotes intrinsic semantic misattribution ($\mathcal{C}_i \in \mathcal{D} \land \mathcal{C}_i \not\models \tau_i$), $\epsilon_{\text{lexical}} \to 0$ is the combinatorial substring collision rate, and $\beta_{\text{fals}} = 1 - P(\text{Falsified} \mid H_{\text{mis}})$ is the stochastic Type II miss rate of the adversarial auditor.*

*Analytical Verification & Derivation:*

1. **Failure of Democratic Consensus under Correlated Priors:** Let $X_1, \dots, X_M \in \{0, 1\}$ be binary error indicators for model evaluators on a deceptive prompt. Due to overlapping pretraining distributions, the average pairwise correlation is non-zero: $\bar{\rho} \ge \rho_{\min} > 0$. The effective sample size is bounded asymptotically:

$$M_{\text{eff}} = \frac{M}{1 + (M-1)\bar{\rho}} \implies \lim_{M \to \infty} M_{\text{eff}} = \frac{1}{\bar{\rho}} < \infty \tag{19}$$

If the prompt triggers a shared pretraining attractor where individual error probability $p > 0.5$, democratic voting inverts: $P(\text{Consensus Error}) \to 1$ as $M \to \infty$. Thus, model multiplexing alone cannot guarantee epistemic reliability.

2. **Two-Tier Error Decomposition (Orthogonal Epistemic Dimensions):** An erroneous system acceptance occurs when a proposition $\tau_i$ is marked as valid despite lacking true evidentiary support in document $\mathcal{D}$. This error decomposes into two mutually exclusive and collectively exhaustive hypotheses:
* **Extrinsic Citation Fabrication ($H_{\text{fab}}$):** The extractor generates an invalid or spliced citation $\mathcal{C}_i \notin \mathcal{D}$ (Type I Hallucination / Chimera quote).
* **Intrinsic Semantic Misattribution ($H_{\text{mis}}$):** The extractor provides a verbatim authentic quote $\mathcal{C}_i \in \mathcal{D}$ from the authorized speaker, but the quote does not semantically entail proposition $\tau_i$ ($\mathcal{C}_i \not\models \tau_i$; Type II Non-Entailment).

By the Law of Total Probability:

$$P(\text{System False Accept}) = P(H_{\text{fab}}) \cdot P(\text{Accept} \mid H_{\text{fab}}) + P(H_{\text{mis}}) \cdot P(\text{Accept} \mid H_{\text{mis}}) \tag{20}$$

3. **Deterministic Physical Lexical Firewall ($\kappa \in \{0, 1\}$):** Regardless of LLM consensus or inter-model correlation $\bar{\rho}$, every extracted claim must satisfy the strict lexical grounding predicate:

$$\kappa_i = \mathbb{I}\left( \text{find}(\text{Norm}(\mathcal{C}_i), \text{Norm}(\mathcal{D})) \neq -1 \right) \in \{0, 1\} \tag{21}$$

where $\mathcal{C}_i$ is the exact textual citation and $\mathcal{D}$ is the raw immutable source document evaluated through the five-gate Python verification cascade. For fabricated citations ($H_{\text{fab}}$), acceptance requires a random character collision across finite document length $|\mathcal{D}|$, yielding:

$$P(\text{Accept} \mid H_{\text{fab}}) = P(\kappa_i = 1 \mid H_{\text{fab}}) \le \epsilon_{\text{lexical}} \approx |\mathcal{D}| \cdot \left(\frac{1}{|\Sigma|}\right)^L \to 0$$

where $|\Sigma|$ is the alphabet size and $L$ is the minimum entropy string length ($L \ge 10$). Hence, physical fabrication is deterministically eradicated by Python code.

Conversely, for semantic misattributions ($H_{\text{mis}}$), the citation physically exists in the text ($\mathcal{C}_i \in \mathcal{D}$). Consequently, the deterministic string matcher unconditionally confirms physical existence:

$$P(\kappa_i = 1 \mid H_{\text{mis}}) = 1.0$$

The lexical firewall proves physical provenance, but remains mathematically agnostic to semantic entailment (Rice's Theorem).

4. **Asymmetric Popperian Falsification Barrier:** To constrain $P(\text{Accept} \mid H_{\text{mis}})$, Quorum establishes role asymmetry. Because automated proof of general semantic entailment is computationally undecidable, Quorum does not rely on naive generative self-affirmation (`is_true = True`). An explicit adversarial falsifier with negative polarity ($\pi_i = -1$) audits the claim under the Popperian Null Hypothesis: a claim is assumed *unwarranted or superficial* unless surviving counter-evidence extraction:

$$P(\text{Accept} \mid H_{\text{mis}}) = P(\kappa_i = 1 \mid H_{\text{mis}}) \cdot P(\text{Survives Audit} \mid H_{\text{mis}}) = 1.0 \cdot (1 - P(\text{Falsified} \mid H_{\text{mis}})) = \beta_{\text{fals}}$$

Substituting into Equation 20 yields the complete closed-form bound:

$$P(\text{System False Accept}) \le P(H_{\text{fab}}) \cdot \epsilon_{\text{lexical}} + P(H_{\text{mis}}) \cdot \beta_{\text{fals}} \approx P(H_{\text{mis}}) \cdot \beta_{\text{fals}} \tag{22}$$

*Theoretical Significance:* Quorum rejects the naive fallacy of "deterministic semantic omniscience"—Python string matching cannot magically prove semantic entailment ($\mathcal{C}_i \models \tau_i$). Rather, Quorum's neurosymbolic architecture cleanly decouples the problem: (i) it mathematically eliminates the largest and most dangerous empirical vulnerability in enterprise LLM deployment—unanchored and fabricated evidence ($P \le \epsilon_{\text{lexical}} \to 0$)—via deterministic compiled code, while (ii) bounding residual semantic misattribution to the stochastic falsification miss rate $\beta_{\text{fals}}$ (empirically $0.02 \dots 0.08$) and further isolating downstream impact through topological Argumentative SCM (A-SCM) reachability pruning.

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

## 7. Full-Stack System Architecture and Error Suppression Pipeline

### 7.1. Multi-Tier Software Architecture

The Quorum platform operationalizes its theoretical invariants across a modular three-tier software architecture:

1. **Neurosymbolic Backend Runtime (`backend_v2`):** Implemented in Python using strictly typed, frozen Pydantic V2 domain models and DTOs (`models/`). The orchestration layer (`services/orchestrator/`) houses the asynchronous Kahn wave executor (`dag_executor.py`), the two-pass epistemic atomizer (`atomizer.py`, `two_pass_atomizer.py`), the TDA poset evaluator (`tda_engine.py`), the backward fault attribution engine (`causal_discovery_engine.py`), the pure stateless argument causal cohesion evaluator (`causal_discovery.py`), and the constrained synthesis engine (`synthesis_engine.py`). A multi-provider LLM adapter layer (`llm/`) abstracts context management, prompt compilation, caching, and constrained decoding across Google AI Studio, Vertex AI, Anthropic Claude, OpenAI, and DeepSeek (`ai_studio_adapter.py`, `vertex_adapter.py`, `anthropic_adapter.py`, `openai_adapter.py`, `deepseek_adapter.py`). Hybrid persistence (`database/`, `services/drivers/`) integrates PostgreSQL and Firestore repositories, verified by unit, integration, guardrail, and end-to-end regression suites (`tests/`).

2. **Server-Driven UI Projection Layer (`services/sdui/`):** To prevent client-side business logic drift, backend SDUI mappers (`sdui_mapper_service.py`, `matrix_summary_table_adapter.py`, `causal_graph_adapter.py`) transform evaluated matrix vectors $\mathbf{\Psi}(\mathcal{D}; \theta)$, causal multi-graphs $\mathcal{G}_{\text{LAG}}$, and XAI variance diagnostics into declarative presentation payloads (`ReportDataDTO`) containing flat polymorphic inner blocks (`AnySduiBlock`).

3. **Cross-Platform Reactive Client (`client_app_v2`) and Governance Specification (`docs/`):** Built with Flutter and Dart for desktop and web deployment, utilizing Riverpod for reactive state management, GoRouter for declarative routing, Freezed for immutable client data models, and bilingual Finnish/English localization (`l10n/`). Functional modules (`features/`) encompass real-time execution monitoring and SDUI rendering (`execution/sdui_blocks_renderer.dart`), interactive DAG workflow and BARS rubric construction (`studio/workflow_builder_view.dart`), audit report export (`reports/`), and access control (`auth/`, `settings/`), engineered in alignment with multi-layered architectural specifications (`docs/architecture/` sections 00–09) and EU AI Act auditability standards.

### 7.2. Four-Stage Cascade Suppression Pipeline and Two-Tier Verification

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

* **Barrier 1 (Ingress Sanitization & Capsule Isolation, $\Phi_{\text{ingress}}$):** Strips prompt injection payloads, normalizes Unicode representations, and fences speaker attribution indices $\sigma_i \in \{\text{USER}, \text{ASSISTANT}\}$.
* **Barrier 2 (TDA Grounding & Poset Verification, $\Phi_{\text{TDA}}$):** Enforces the lexical null hypothesis ($\kappa_i = 0$ on verification failure) across the five-gate Python cascade and quarantines cyclic or unanchored dependencies.
* **Barrier 3 (Asymmetric Falsification & Best-of-3 Consensus, $\Phi_{\text{fals}}$):** Evaluates high-entropy propositions via a parallel Best-of-3 ensemble (`ensemble_parallelism = 3`, `ensemble_min_consensus = 2`) with Popperian null-hypothesis tie-breaking and multiplicative anti-pattern deductions ($\Pi_{\text{penalty}}$).
* **Barrier 4 (Lipschitz Damping & Constrained Synthesis, $\Phi_{\text{score}} \circ \Phi_{\text{synth}}$):** Applies piecewise power-curve damping $\rho^{\gamma(\theta)}$, enforces the 40% macro penalty cap ($P_{\max} = 0.40$), and restricts the terminal synthesis engine to rendering verified graph state without introducing unanchored claims.

To balance verification rigor with FinOps token economics, Quorum separates live execution from cross-provider benchmarking via a **Two-Tier Verification Strategy**: production DAG waves execute single-model Best-of-3 ensembles via asynchronous coroutine groups using the step's assigned model configuration, whereas computationally intensive multi-provider variance benchmarking across Gemini, Claude, OpenAI, and DeepSeek is decoupled into offline evaluation workers. Furthermore, to prevent cross-tenant memory leakage in distributed worker pools (such as Celery or Arq), bijective alias mappings $\mu$ are instantiated per execution job and serialized across worker boundaries via immutable `AliasManifest` snapshots.

---

## 8. Empirical Validation: Paired Variance Audits and Reproducibility Benchmark

To evaluate the empirical stability, epistemic determinism, and inter-run reproducibility of the Quorum runtime, we conducted two controlled pairwise audit trials ($K = 2$ paired trials, comprising four independent full-scale workflow executions: Pair A and Pair B) on an executive strategic foresight task using the Finnish Innovation Fund Sitra Megatrend dataset (2017–2023). 

*Methodological Scope and Disclosure of Preliminary Sample Size:* In accordance with rigorous scientific reporting standards, we state explicitly as an empirical fact that the quantitative results presented herein are derived from **two paired end-to-end evaluation trials** ($K = 2$, $N = 110$ common proposition atoms per trial, yielding $220$ atom-level paired observations across four complete executions: `exe_f6f9b06e63eb4dd8` vs. `exe_379b69df134f477a`, and `exe_c136e7cfc4b841a7` vs. `exe_a56127fa10594dc4`). While both trials demonstrate high statistical agreement ($\kappa > 0.90$) and zero pipeline failures, we emphasize that this represents a preliminary empirical verification of runtime stability; a broader, large-scale empirical campaign across diverse organizational corpora, varied prompting regimes, and heterogeneous foundation model families (including Claude, OpenAI, and DeepSeek) is strictly required to establish general population-level bounds.

### 8.1. Experimental Protocol, Input Isolation, and Model Configuration

Each execution audited the end-to-end multi-turn supervisory dialogue (`Chat`, candidate steering context) and the produced strategic deliverable (`Report`, candidate deliverable context) through the *Targeted AI Steering & Argumentation Audit* workflow (`wf_a8f1d71000000001`, 8 DAG steps, evaluating $N = 110$ propositional atoms across five orthogonal evaluative and structural matrices). 

To assess the system under realistic non-zero entropy conditions, the pipeline was bound to Google's frontier model `gemini-3.8-flash` deployed via Google AI Studio (`sys_e26807f3bfa3454d`) under default production sampling parameters:
* Unconstrained non-zero temperature: $T = 1.0$,
* Dynamic cognitive thinking budgets: 0 tokens (fast), 2,048 tokens (balanced), 4,096 tokens (deep), 8,192 tokens (reasoning), and 2,048 tokens (synthesis),
* Dynamic token context windows: up to 65,536 tokens per step.

*Cryptographic Input Diversification and Zero Cache Bleed Guarantee:* In cloud-hosted LLM APIs, prefix caching (such as Google Vertex AI and AI Studio KV-cache reuse) can artificially inflate inter-run agreement by serving pre-computed key-value states from prior sessions. To mathematically eliminate cache bleed, all input files underwent cryptographic SHA-256 hash diversification between runs through non-semantic typographical space mutations (substituting U+00A0 No-Break Space and U+2002 En Space). While every input file pair exhibited distinct cryptographic SHA-256 digests, the underlying semantic and propositional content remained 100% invariant, ensuring that measured agreement reflects genuine neurosymbolic stability rather than vendor-side KV cache retrieval.

### 8.2. Inter-Run Reliability and Agreement Statistics (Cohen’s and Fleiss’ Kappa)

Inter-annotator and inter-run reliability were evaluated using percent raw self-consistency, Cohen’s unweighted kappa ($\kappa_{\text{Cohen}}$) with asymptotic standard error (SE) and 95% confidence intervals (CI), Fleiss’ generalized multi-rater kappa ($\kappa_{\text{Fleiss}}$), and mean Shannon entropy ($\bar{H}$). Across both trials, binary atom-level decisions ($\omega(a_i) \in \{\text{PASSED}, \text{FAILED}\}$) were evaluated over $N = 110$ identical proposition atoms.

| Reliability Metric | Pair A (`exe_f6f9` vs `exe_379b`) | Pair B (`exe_c136` vs `exe_a561`) | Combined Mean ($K = 2$) |
| :--- | :---: | :---: | :---: |
| **Execution Identifiers** | `exe_f6f9b06e63eb4dd8`<br>`exe_379b69df134f477a` | `exe_c136e7cfc4b841a7`<br>`exe_a56127fa10594dc4` | 4 complete runs |
| **Common Proposition Atoms ($N$)** | 110 | 110 | 220 atom observations |
| **Observed Raw Agreement ($P_o$)** | **95.45%** (105 / 110) | **98.18%** (108 / 110) | **96.82%** |
| **Expected Chance Agreement ($P_e$)** | 51.45% | 50.40% | 50.93% |
| **Cohen’s Kappa ($\kappa_{\text{Cohen}}$)** | **0.9064** | **0.9633** | **0.9348** |
| **Standard Error (SE)** | 0.0409 | 0.0257 | 0.0333 |
| **95% Confidence Interval (CI)** | $[0.8262, 0.9866]$ | $[0.9130, 1.0000]$ | $[0.8696, 0.9933]$ |
| **Fleiss’ Kappa ($\kappa_{\text{Fleiss}}$)** | 0.9063 | 0.9633 | 0.9348 |
| **Landis & Koch (1977) Categorization** | *Almost Perfect Agreement* | *Almost Perfect Agreement* | *Almost Perfect Agreement* |
| **Human Expert Baseline Comparison** | Exceeds Human ($0.65–0.80$) | Exceeds Human ($0.65–0.80$) | Exceeds Human ($0.65–0.80$) |
| **Mean Shannon Entropy ($\bar{H}$)** | 0.0455 | 0.0182 | 0.0318 |
| **Marginal Decision Bias** | $-0.0273$ | $+0.0182$ | $-0.0045$ |
| **Dead Letter Queue (DLQ) / Crashes** | 0 / 110 (0.0%) | 0 / 110 (0.0%) | **0 / 220 (0.0%)** |

**Table 2:** Statistical reliability, inter-run agreement, and entropy metrics across two independent paired evaluation trials on the Sitra strategic foresight corpus under stochastic frontier inference ($T = 1.0$).

Both independent pairwise trials yielded Cohen's $\kappa > 0.90$, landing firmly within the highest empirical reliability tier (*Almost Perfect Agreement*, $\kappa \ge 0.81$; Landis & Koch, 1977). This substantially outperforms typical human domain-expert inter-rater agreement ($0.65 \le \kappa \le 0.80$; Buçinca et al., 2021) and demonstrates that Quorum's five-gate deterministic verification cascade and Popperian null-hypothesis anchors effectively suppress the stochastic volatility inherent in $T = 1.0$ autoregressive sampling.

### 8.3. Granular Matrix and Rubric Agreement Breakdown

To verify that stability is preserved uniformly across diverse cognitive dimensions rather than concentrated in trivial baseline assertions, agreement was stratified across the five evaluated rubric matrices and five normalized difficulty quintiles (0–100% scale).

| Evaluative Matrix / Rubric Module | Matrix Identifier | Scale | Atoms | Pair A Agreement | Pair B Agreement | Combined Consistency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Toulmin Argumentation Model** | `blk_440a5fef9331451b` | 1–5 | 25 | 100.0% (25/25) | 100.0% (25/25) | **100.0% (50/50)** |
| **Argument Causal Cohesion (A-SCM)** | `blk_c0a1e50000000001` | 1–5 | 5 | 100.0% (5/5) | 100.0% (5/5) | **100.0% (10/10)** |
| **Transparency & Explainability** | `blk_f6e286f050c94d60` | 1–5 | 25 | 88.0% (22/25) | 100.0% (25/25) | **94.0% (47/50)** |
| **AI Steering & Agency (HACM)** | `blk_7d8e9f0a1b2c3d4e` | 1–5 | 25 | 100.0% (25/25) | 96.0% (24/25) | **98.0% (49/50)** |
| **Cognitive Depth (Bloom Taxonomy)** | `blk_f921c7c0989b47e8` | 1–6 | 30 | 93.3% (28/30) | 96.7% (29/30) | **95.0% (57/60)** |
| **Total / Global** | — | — | **110** | **95.45%** | **98.18%** | **96.82% (213/220)** |

**Table 3:** Rubric-stratified consistency breakdown across matrices. Toulmin argumentation and pure topological causal cohesion achieved 100% deterministic reproducibility across all runs.

Stratifying atom consistency by normalized difficulty reveals balanced epistemic resilience across both baseline and mastery levels:
* **Top Mastery / Critical Rigor (81–100%):** 97.6% consistency (41 / 42 evaluations concordant; Pair A: 21/21, Pair B: 20/21).
* **High Standard (61–80%):** 97.6% consistency (41 / 42 concordant; Pair A: 20/21, Pair B: 21/21).
* **Mid Standard (41–60%):** 95.2% consistency (40 / 42 concordant; Pair A: 19/21, Pair B: 21/21).
* **Low Standard (21–40%):** 97.6% consistency (41 / 42 concordant; Pair A: 20/21, Pair B: 21/21).
* **Baseline Viable (0–20%):** 96.2% consistency (50 / 52 concordant; Pair A: 25/26, Pair B: 25/26).

### 8.4. Root Cause Decomposition of Evaluation Disagreements

Across both trials (220 paired atom evaluations), exactly **7 disagreement instances** occurred (Pair A: 5, Pair B: 2), representing an overall disagreement rate of $3.18\%$. Deterministic root cause triage categorized each disagreement into one of four mutually exclusive failure classes:

| Disagreement Root Cause Class | Operational Mechanism | Pair A Count | Pair B Count | Combined Total | Proportion (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Retrieval Gap (Citation Variance)** | Stochastic beam decoding in one run failed to isolate a continuous verbatim text span matching the BARS rubric, triggering the deterministic lexical null hypothesis ($\kappa_i = 0$). | 4 | 2 | **6** | **85.7%** |
| **Reasoning Gap (Threshold Margin)** | Both runs extracted valid citation anchors ($\kappa_i = 1$), but model reasoning traces diverged on whether the cited evidence satisfied strict rubric criteria. | 1 | 0 | **1** | **14.3%** |
| **Contextual Override** | External policy or manual override discrepancies. | 0 | 0 | **0** | **0.0%** |
| **Technical / DLQ Error** | Schema serialization failure, token overflow, or runtime crash. | 0 | 0 | **0** | **0.0%** |
| **Total** | — | **5** | **2** | **7** | **100.0%** |

**Table 4:** Root cause taxonomy of evaluation disagreements. Over 85% of variance stems from stochastic citation extraction under temperature $T = 1.0$, which is safely quarantined by the closed-world lexical null hypothesis ($\kappa = 0$) rather than silently hallucinated.

*Macro Score Drift:* On the macro level ($0–100$ normalized score space), the Mean Absolute Delta (MAD) across all matrix blocks was $3.99$ points in Pair A and $3.05$ points in Pair B, with zero waterfall sequence disruptions across the DAG execution waves.

### 8.5. Limitations and Empirical Generalization Agenda

While the observed inter-run reliability ($\bar{\kappa} = 0.9348$) provides strong empirical support for Quorum’s neurosymbolic architecture, we emphasize the specific limitations of this preliminary validation:
1. **Limited Sample Cardinality:** The quantitative results reflect exactly two pairwise evaluation trials ($K = 2$, 4 full workflow runs). Although each trial processes a dense 8-step DAG evaluating 110 proposition atoms and over 1.7–3.6 million tokens per run, broader statistical power requires scaling to $K \ge 20$ paired trials across diverse document genres.
2. **Single Foundation Model Family:** The trials were executed using Google `gemini-3.8-flash`. While the Two-Tier Verification Architecture is provider-agnostic, cross-model inter-rater reliability across distinct model architectures (e.g., Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o, DeepSeek-V3) must be systematically quantified to measure inter-provider epistemic alignment.
3. **Task Domain Focus:** The Sitra dataset represents executive strategic foresight and policy discourse. Future empirical benchmarks will extend this evaluation protocol to contract legal compliance, clinical protocol verification, and automated software architecture reviews.

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
3. **Cohort Percentile Calibration:** Calibrated BARS power-curve damping ($\gamma = 1.25$) yields conservative capability scores under zero-trust rubrics. Without peer comparison, operators may perceive these scores as excessively punitive. Providing percentile rankings against normalized organizational cohorts contextualizes the diagnostic.
4. **Episodic Identifier Aliasing, Attention Economics, and Fail-Fast State Hydration:** While Section 2.1 formalizes the bijective mapping $\mu: \mathcal{I}_{\text{UUID}} \longleftrightarrow \mathcal{V}_{\text{alias}}$, maintaining distributed referential integrity requires strict lifecycle isolation. In Quorum, `AliasEngine` instances are strictly non-singleton, instantiated per execution job to prevent cross-tenant memory leakage. When execution is distributed across asynchronous background workers (specifically Celery or Arq worker pools), the mapping state is serialized into an immutable snapshot (`AliasManifest`) transported within `step_metadata`. The receiver reconstitutes the bijection (`AliasEngine.from_manifest`) and executes strict fail-fast validation: any hallucinated alias matching an active prefix that does not exist in the manifest immediately halts execution with an unrecoverable validation error (`AppException(422)`), preventing corrupted foreign keys from entering persistent DAG state.

---

## 11. Conclusions

The Quorum architecture establishes a mathematically rigorous foundation for turning stochastic large language models into verifiable, epistemically anchored expert systems. By replacing unconstrained autoregressive generation with:

* Kahn wave-based DAG scheduling (Architectural Principle 1),
* Decoupled epistemic error suppression separating physical citation provenance from semantic entailment (Architectural Property 1),
* Monotonic, Lipschitz-stable BARS power-curve scoring (Mathematical Property 1), and
* Discrete structural argument surgery and ATMS-based fault isolation (Architectural Property 2),

the framework eliminates hallucination cascades and enforces structural accountability. The paired empirical audits validate that Quorum maintains high inter-run consistency ($\kappa > 0.90$) and cuts through polished surface fluency, providing an auditable, verifiable methodology for enterprise and strategic artificial intelligence.

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