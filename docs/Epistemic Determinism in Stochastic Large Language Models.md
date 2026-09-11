**Epistemic Determinism in Stochastic Large Language Models: A Graph-Orchestrated Systems Engineering Approach to Zero-Permissive Verification**

**Abstract**

As Large Language Models (LLMs) permeate enterprise cognitive workflows, their inherent stochasticity introduces critical vulnerabilities: epistemic hallucination, contextual degradation, and unverified causality. Traditional "LLM-as-a-judge" architectures fail to mitigate these risks reliably because they treat foundational models as autonomous cognitive agents, rendering them unsuitable for strict corporate governance and regulatory compliance (e.g., the EU AI Act). We propose *Quorum*, a novel Computer-Implemented Invention (CII) and Systems Engineering framework that enforces deterministic runtime behavior on stochastic inputs by subverting the generative nature of Large Language Models. Rather than attempting to cultivate intrinsic neural reliability, Quorum implements a paradigm of **Epistemic Coercion**: the stochastic autoregressive generator is systematically "driven into an architectural corner"—enclosed within an external, zero-permissive software containment vessel that strips away its generative degrees of freedom until it is coerced to function as a bounded, low-entropy propositional truth-value evaluator. Operating strictly under a zero-weight-update regime ($\nabla \mathcal{L} = 0$), Quorum replaces heuristic prompt engineering with mathematically verifiable software gates and contract invariants: pre-flight syntactic anchor gating, Kahn-wave DAG scheduling under the Local Causal Markov Condition, causal short-circuiting with zero-inference subgraph pruning, Condorcet majority voting ensembles with Epistemic Null Hypothesis tie-breaking, dynamic runtime schema interlocks, and algorithmic evidence masking contracts. To prevent attention degradation, semantic identifiers are compressed into attention anchors via deterministic aliasing, while cognitive axes are decoupled between high-reasoning system instructions and localized document evidence. Furthermore, we formalize a dual caching topology: static-first prefix caching achieving $>95\%$ hit rates in production, contrasted with Metamorphic Cache Bleed Evasion ensuring cryptographic isolation across empirical benchmarking runs. Empirical evaluation across two independent longitudinal replication trials totaling $29.8\text{M}$ tokens ($610$ atom comparisons across four full production executions) demonstrates remarkable inter-run reliability ($\kappa = 0.9318$ and $\kappa = 0.9171$, mean $\bar{\kappa} = 0.9245$, mean pairwise agreement $96.56\%$). Furthermore, algorithmic evidence masking contracts verified $100.0\%$ ($198/198$) of extracted citations against raw ground-truth corpora with zero admitted hallucinations, while forensic triage confirmed a replicated $0.0\%$ internal reasoning gap across all observed discrepancies.

**Index Terms** — Large Language Models, Directed Acyclic Graph (DAG), Graph-Based Orchestration, Topological Sort, Hallucination Mitigation, Metamorphic Testing, Zero-Permissive Verification, Epistemic Determinism, Epistemic Coercion, Systems Engineering, Runtime Verification.

---

### **1. Introduction**

Generative foundation models natively predict the next token based on a probability distribution conditioned on preceding context:

$$P(w_t \mid w_1, w_2, \dots, w_{t-1})$$

While this mechanism allows for unprecedented stylistic fluidity, it inherently suffers from "System 1" cognitive biases (Kahneman, 2011). Because these architectures manipulate linguistic form divorced from underlying intent, world models, or empirical ground truth, they operate as ungrounded statistical text synthesizers—or "stochastic parrots" (Bender et al., 2021). In critical enterprise domains requiring rigorous governance, the cost of accepting logically flawed but rhetorically fluent output—often masking a lack of Popperian falsifiability (Popper, 1959)—is catastrophic.

Traditional LLMOps approaches attempt to mitigate LLM inaccuracies by updating model weights through gradient descent, optimizing an objective function by computing the gradient $\nabla \mathcal{L}$. However, weight fine-tuning does not eliminate runtime hallucination, cannot dynamically enforce evolving regulatory compliance schemas, and fails to guarantee epistemic rigor on unseen corporate evidence. Furthermore, modifying neural weights risks catastrophic forgetting across out-of-distribution reasoning domains.

#### **1.1 The Systems Engineering and Epistemic Coercion Paradigm ("Driving the LLM into a Corner")**

Rather than attempting to force determinism from within non-differentiable neural parameters, we formulate an external **Systems Engineering and Runtime Verification (RV)** discipline. Under this paradigm, all mathematical expressions in this framework specify **discrete runtime software gates, formal verification contracts (Meyer, 1992), and state machine invariants** operating under an absolute zero-weight-update constraint ($\nabla \mathcal{L} = 0$).

This formulation is directly grounded in modern safety-critical systems engineering (STAMP; Leveson, 2011), which establishes that **safety, reliability, and determinism are not intrinsic properties of individual components, but emergent properties of the enclosing system architecture and its feedback control loops**. An inherently stochastic or non-deterministic component can be integrated safely provided that external control structures strictly prevent unsafe state transitions.

The central philosophical and engineering insight of Quorum is that treating Large Language Models as autonomous reasoning agents or conversational decision-makers is a profound category error. As Kambhampati et al. (2024) demonstrate, Large Language Models cannot autonomously generate valid plans or formal reasoning traces without severe combinatorial breakdown; their perceived reasoning is an approximate retrieval heuristic. To achieve audit-grade determinism, the model's generative agency must be fundamentally subverted. Quorum operationalizes what Kambhampati et al. term an **"LLM-Modulo Framework"** and what Marcus (2020) conceptualizes as a **hybrid neurosymbolic scaffold**: the foundation model is relegated to an untrusted, approximate candidate proposer, while deterministic symbolic software gates exercise absolute veto power.

Quorum achieves this through **Epistemic Coercion**: an architectural paradigm that systematically drives the stochastic generator into an inescapable corner, stripping away its generative freedom through five concentric containment boundaries:

1. **Input Sequence Space Compression ($L \to |D| + |a_i|$):** Kahn-wave DAG orchestration strips away all uncoupled evaluation rules, eliminating multi-prompt competition and collapsing attention entropy ($\text{SIR} \to \infty$).
2. **Grammar-Constrained Pushdown Decoding:** The model's token sampling is clamped to zero-permissive runtime schemas (enforcing closed field boundaries, strict property restrictions, and rigid typing), forcing logits of all non-conforming tokens to $-\infty$ and eliminating conversational preamble or unformatted prose.
3. **Contrastive Polytope Clamping ($\mathcal{C}(a_i) = \langle C_{\text{pos}}, C_{\text{anti}} \rangle$):** Semantic decision boundaries are locked between explicit positive criteria and concrete falsification anti-patterns, eliminating subjective drift.
4. **Algorithmic Lexical Subordination ($s_{\text{final}} = s \odot v$):** The model is stripped of sovereign decision-making authority; its truth claims are subordinated to deterministic host-level substring verification (exact normalized lexical search), where unverified citations immediately nullify the evaluation.
5. **The Epistemic Null Hypothesis Attractor ($H_0$):** An asymmetric absorbing barrier where any schema violation, citation mismatch, or ensemble deadlock immediately drops the evaluation into an unverified state ($H_0 \to \text{N\_A}$).

Enclosed within this deterministic software containment vessel, the LLM ceases to act as an open generative engine; it is coerced into functioning as a bounded, low-entropy propositional truth-value evaluator.

#### **1.2 The Epistemic Asymmetry Principle ($H_0$ Attractor)**

In classical machine learning evaluation, classification objectives treat false positives and false negatives symmetrically (e.g., optimizing $F_1$-score). In enterprise governance and compliance auditing, however, error costs are profoundly asymmetric: a single hallucinated positive finding carries severe legal, financial, and regulatory liability, whereas failing to verify an ambiguous assertion is safe and transparent.

Quorum formalizes an **Epistemic Asymmetry Principle** grounded in Popperian falsification (Popper, 1959). The system establishes the **Null Hypothesis ($H_0$)**—that a claim is unverified, false, or not applicable—as an asymmetric default attractor. Every claim remains locked in state $H_0$ until and unless an unforgeable, lexically anchored evidence chain satisfies every enclosing software gate. If any software gate fails, the system immediately reverts to $H_0$, driving the probability of an admitted false positive to zero:

$$P(\text{False Positive}) \to 0$$

---

### **2. Architectural Paradigm: The Graph-Orchestrated Verification Engine**

```
  Input Document (D)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 1: Pre-Flight Syntactic Anchor Filter                  │
│    Φ(D, Anchors) ∈ {0, 1}                                   │
│    ├─ [Φ = 0] ──► Early Exit to H_0 (Zero LLM Inference)    │
│    └─ [Φ = 1] ──► Proceed to Graph Ingress                  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 2: Static Graph Integrity & Phantom Edge Isolation     │
│    G = (A, E) verified for Acyclicity (Cycles ──► Fatal)    │
│    Dangling Parent References ──► SYSTEM_ERROR Isolation    │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 3: Attention Aliasing & Contrastive Anchoring          │
│    f_alias: Opaque_UUID ──► Attention Anchors (a0, a1, ...) │
│    Contrastive Pairs: (C_pos, C_neg) Semantic Bounds        │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 4: Wave Topological Scheduling & Causal Short-Circuit  │
│    Wave W_k: in-degree(a_i) = 0 (Async Concurrent Batch)    │
│    P(A_1,...,A_n | D) = ∏ ∏ P(A_i | Parents_G(A_i), D)     │
│    ├─ Precondition Failed ──► Short-Circuit to N_A (Zero LLM)│
│    └─ Precondition Passed ──► Model Dispatch                │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 5: Condorcet Ensemble Voting (High-Entropy Atoms)      │
│    Parallel Best-of-3 ──► 2/3 Majority Consensus            │
│    Tie / Disagreement ──► Default to Null Hypothesis (H_0)  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 6: Dynamic Runtime Schema Admission Gate (JSON Schema) │
│    V_struct(x_i, S(a_i)) ∈ {0, 1}                           │
│    [V = 0] (Schema Breach) ──► Dead Letter Queue (DLQ)      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ Gate 7: Multi-Tier Lexical Grounding & Evidence Masking     │
│    Entropy Gate (|q| < 10) + Contiguity Guard (|q| < 30)    │
│    Verification Vector: v_k ∈ {0, 1}                        │
│    s_final = s ⊙ v  (Null Hypothesis Quote Stripping Gate)  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
  Deterministic Evidentiary State & Verified Audit Record
```

#### **2.1 DAG Decomposition and Wave-Based Topological Scheduling**

A central challenge in LLM orchestration is context collapse and multi-hop reasoning failure when feeding monolithic prompts. As established by Dziri et al. (2023), transformer architectures exhibit fundamental theoretical limitations on compositional problems: because errors compound exponentially at each step of autoregressive generation, transformers cannot reliably execute complex, multi-hop reasoning graphs within a single generation pass. Monolithic evaluation prompts inevitably collapse under this compounding error barrier.

Quorum resolves this fundamental limitation by decomposing an evaluation matrix into a causal dependency graph. This topological structure functions as an architectural **Restraining Bolt** (De Giacomo et al., 2020), formally bounding and constraining the state-action space of the stochastic evaluation process.

Let an arbitrary evaluation matrix be $\mathcal{M}$ (such as an exemplary domain framework based on hierarchical cognition, regulatory compliance, or structural argumentation; Quorum is fundamentally matrix-agnostic). We define a mapping function that decomposes $\mathcal{M}$ into a discrete set of epistemological micro-tasks, or "atoms", $\mathcal{A} = \{a_1, a_2, \dots, a_n\}$. These atoms form the vertices of a Directed Acyclic Graph (DAG), $\mathcal{G} = (\mathcal{A}, \mathcal{E})$, where directed edges $e_{j \to i} \in \mathcal{E}$ define causal preconditions from parent atom $a_j$ to child atom $a_i$.

Execution is scheduled using Kahn's algorithm, partitioning $\mathcal{A}$ into $K$ discrete, sequentially ordered topological waves:

$$\mathcal{W}_1, \mathcal{W}_2, \dots, \mathcal{W}_K$$

where each wave $\mathcal{W}_k$ consists exclusively of nodes whose incoming causal edges originate solely from already evaluated antecedent waves:

$$\forall a_i \in \mathcal{W}_k, \quad \text{in-degree}(a_i \mid \mathcal{A} \setminus \bigcup_{m=1}^{k-1} \mathcal{W}_m) = 0$$

**Theorem 1 (Local Causal Markov Condition under Wave Scheduling):**  
*Given a causal DAG $\mathcal{G} = (\mathcal{A}, \mathcal{E})$ and document context $D$, the joint probability distribution of all atom evaluation outcomes factors as:*

$$P(A_1, A_2, \dots, A_n \mid D) = \prod_{k=1}^{K} \prod_{A_i \in \mathcal{W}_k} P(A_i \mid \text{Parents}_{\mathcal{G}}(A_i), D)$$

*Proof.* By definition of Kahn's topological sort, for any node $A_i \in \mathcal{W}_k$, all topological ancestors $\text{Anc}_{\mathcal{G}}(A_i)$ belong to prior waves $\bigcup_{m=1}^{k-1} \mathcal{W}_m$. Under the Causal Markov Condition (Pearl, 2009), each variable $A_i$ is conditionally independent of its non-descendants given its direct parents $\text{Parents}_{\mathcal{G}}(A_i)$. Because all nodes within the same wave $\mathcal{W}_k$ possess no directed paths between one another, they are mutually conditionally independent given the resolved parent states $\text{Parents}_{\mathcal{G}}(\mathcal{W}_k)$ and context $D$:

$$P(\mathcal{W}_k \mid \text{Parents}_{\mathcal{G}}(\mathcal{W}_k), D) = \prod_{A_i \in \mathcal{W}_k} P(A_i \mid \text{Parents}_{\mathcal{G}}(A_i), D)$$

**Operational Software Concurrency Guarantee:** Theorem 1 provides the mathematical foundation for **asynchronous batch concurrency**. Because nodes within wave $\mathcal{W}_k$ are conditionally independent given resolved parent states, they are dispatched concurrently via non-blocking coroutine task groups without race conditions, shared memory locks, or probabilistic cross-contamination. $\blacksquare$

#### **2.1.1 Static Topological Graph Verification (Cycle & Phantom Edge Prevention)**

Before runtime scheduling begins, the graph engine constructs a directed graph model $\mathcal{G}_{\text{nx}}$ to execute pre-flight static verification:

1. **Cycle Detection:** The engine computes Strongly Connected Components (Tarjan, 1972) in $O(|V| + |E|)$ time. If any cycle is detected, execution halts immediately with a fatal graph configuration error, preventing infinite runtime deadlocks.
2. **Phantom Edge Isolation:** For every edge $e_{j \to i} \in \mathcal{E}$, the engine asserts that parent $a_j \in \mathcal{A}$. If a dangling parent reference is detected, child node $a_i$ is quarantined immediately:

$$a_j \notin \mathcal{A} \implies s(a_i) \leftarrow \text{SYSTEM\_ERROR}, \quad \text{reason} \leftarrow \text{"UNRESOLVED\_DEPENDENCY"}$$

This guarantees that ungrounded dependencies fail fast before consuming cloud compute resources.

#### **2.2 Causal Short-Circuiting and Subgraph Pruning**

To prevent cascading errors and eliminate unnecessary LLM inference costs, Quorum enforces structural short-circuiting. Each causal edge $e_{j \to i} \in \mathcal{E}$ specifies an expected outcome state $s_{\text{expected}}(e_{j \to i}) \in \{\text{PASSED}, \text{FAILED}, \text{TRUE}, \text{FALSE}\}$.

Let $s(a_j)$ denote the evaluated state of parent atom $a_j$. The edge activation operator $\phi(e_{j \to i})$ is a discrete boolean software gate:

$$\phi(e_{j \to i}) = \begin{cases} 1, & \text{if } s(a_j) = s_{\text{expected}}(e_{j \to i}) \\ 0, & \text{otherwise} \end{cases}$$

If any incoming causal precondition fails:

$$\exists e_{j \to i} \in \mathcal{E} \quad \text{such that} \quad \phi(e_{j \to i}) = 0 \implies s(a_i) \leftarrow \text{N\_A}$$

When an incoming causal precondition is violated, $a_i$ transitions immediately to state $\text{N\_A}$ via an $\mathcal{O}(1)$ local gate evaluation, precluding model dispatch ($P(\text{LLM Call} \mid \phi = 0) = 0$). During subsequent Kahn wave propagation, the downstream dependency subgraph $\mathcal{G}_{\text{sub}} = (\mathcal{V}_{\text{sub}}, \mathcal{E}_{\text{sub}})$ rooted at $a_i$ is quarantined in host memory in $\mathcal{O}(|\mathcal{V}_{\text{sub}}| + |\mathcal{E}_{\text{sub}}|)$ time. Because host graph traversal latency ($\approx 10^{-6}\text{ s}$) is negligible compared to remote autoregressive generation ($\approx 10^{0}\text{ s}$), causal short-circuiting achieves an effective $\mathcal{O}(0)$ cognitive inference cost for all downstream atoms, guaranteeing that logically ungrounded branches never consume cloud inference tokens.

#### **2.3 Pre-Flight Syntactic Anchor Gating (Zero-Inference Firewall)**

Before dispatching an atom $a_i$ to an LLM, Quorum applies a deterministic, non-neural pre-flight validation gate. Each extractive atom defines a set of mandatory syntactic anchors $\Omega(a_i) = \{\omega_1, \dots, \omega_m\}$ and an aggregation mode $\text{mode}(a_i) \in \{\text{EXISTS}, \text{ALL}\}$.

The pre-flight existence operator $\Phi(D, \Omega(a_i))$ verifies syntactic anchor presence within normalized document text $\mathcal{N}(D)$:

$$\Phi(D, \Omega(a_i)) = \begin{cases} \bigvee_{l=1}^{m} \mathbb{I}(\mathcal{N}(\omega_l) \subseteq \mathcal{N}(D)), & \text{if } \text{mode}(a_i) = \text{EXISTS} \\ \bigwedge_{l=1}^{m} \mathbb{I}(\mathcal{N}(\omega_l) \subseteq \mathcal{N}(D)), & \text{if } \text{mode}(a_i) = \text{ALL} \end{cases}$$

where $\mathbb{I}(\cdot)$ is the indicator function.

* If $\Phi(D, \Omega(a_i)) = 0$, required syntactic anchors are definitively absent from the corpus. The atom transitions immediately to the Null Hypothesis ($H_0 \to \text{FAILED}$, or $\text{PASSED}$ for inverse negative claims), completely bypassing LLM inference.
* If $\Phi(D, \Omega(a_i)) = 1$, necessary syntactic anchors exist, and the atom is admitted to the topological execution queue for semantic evaluation.

In production workflows over sparse documents, this non-neural software gate eliminates hallucination risks at the ingress boundary and saves up to $40\%$ of inference calls. For our empirical evaluation and causal graph stress-testing (Section 3.3), pre-flight early termination was selectively bypassed (setting pre-flight filtering enforcement to false) across the 305-atom benchmark to ensure that all nodes were dispatched for end-to-end model evaluation.

#### **2.4 Dynamic Schema Generation and Zero-Permissive Typing**

Rather than relying on unstructured text generation or loosely typed dictionaries, the system enforces strict type safety at runtime. For any given atom $a_i$, a schema factory dynamically compiles a bespoke schema validation model $\mathcal{S}(a_i)$ specifying exact typing constraints, closed field boundaries, and strictly forbidden extraneous attributes (enforcing zero extra fields and absolute strictness).

This runtime schema compilation implements **Grammar-Constrained Decoding** (Willard & Louf, 2023; Scholak et al., 2021). Instead of relying on post-hoc regex parsing or hoping that the model adheres to prompt instructions, the schema is translated into a formal Pushdown Automaton (PDA). At each autoregressive token generation step $t$, the token sampling distribution is filtered:

$$P'(w_t \mid w_{<t}) = \begin{cases} \frac{P(w_t \mid w_{<t})}{\sum_{w' \in \Gamma(w_{<t})} P(w' \mid w_{<t})}, & \text{if } w_t \in \Gamma(w_{<t}) \\ 0, & \text{if } w_t \notin \Gamma(w_{<t}) \end{cases}$$

where $\Gamma(w_{<t})$ denotes the set of valid next tokens permitted by the schema's formal grammar. By driving the logit of any non-conforming token to $-\infty$, the model is mathematically precluded from outputting conversational preamble, markdown wrappers, or invalid JSON keys.

Rather than a continuous, differentiable loss function for gradient optimization, we define the **Structural Admission Gate** $\mathcal{V}_{\text{struct}}$ as a discrete runtime software interlock:

$$\mathcal{V}_{\text{struct}}(x_i, \mathcal{S}(a_i)) = \begin{cases} 1, & \text{if } x_i \models \mathcal{S}(a_i) \\ 0, & \text{if } x_i \not\models \mathcal{S}(a_i) \end{cases}$$

If an LLM response violates the dynamically compiled schema (such as omitting mandatory explanatory or citation fields, or emitting hallucinated keys), $\mathcal{V}_{\text{struct}} = 0$. The non-conforming payload triggers an immediate validation error exception and is rejected into a Dead Letter Queue (DLQ), triggering deterministic retry or graceful fallback to $H_0$. This enforces **Zero-Permissive Typing** at the network boundary.

#### **2.5 Multi-Tier Lexical Grounding and Evidence Masking Contracts**

To eradicate epistemic citation hallucination, the system mandates verifiable lexical grounding. For any claim evaluated by the model, a supporting quote string $q$ must be returned.

The text normalization function $\mathcal{N}(T)$ strips markup tags, normalizes whitespace, and decomposes Unicode diacritics via NFD normalization while preserving a monotonic character coordinate mapping $\mu: \mathbb{N} \to \mathbb{N}$:

$$\mathcal{N}(T) = \text{Clean}(\text{NFD}(T))$$

Quorum enforces a **Multi-Tier Lexical Validation Gate**:

1. **Exact Substring Gate (Primary Gate):**
   $$\text{Match}_{\text{exact}}(q, D) = \mathbb{I}(\mathcal{N}(q) \subseteq \mathcal{N}(D))$$
2. **Entropy Gate (< 10 characters):**  
   If $|q| < 10$, fuzzy matching is mathematically forbidden. The system mandates $100\%$ exact lexical match to prevent single-word false positives:
   $$\text{Valid}(q, D) = \text{Match}_{\text{exact}}(q, D) \quad \text{for } |q| < 10$$
3. **Length-Weighted Contiguity Guard & Multilingual Thresholding:**  
   For quotes with $|q| \ge 10$ where exact substring matching fails due to OCR noise, line breaks, or inflectional morphology:
   $$\text{Score}_{\text{fuzzy}}(q, D) = \begin{cases} \text{partial\_ratio}(\mathcal{N}(q), \mathcal{N}(D)), & \text{if } 10 \le |q| < 30 \\ \text{token\_set\_ratio}(\mathcal{N}(q), \mathcal{N}(D)), & \text{if } |q| \ge 30 \end{cases}$$
   where $\text{partial\_ratio}$ enforces strict character contiguity, while $\text{token\_set\_ratio}$ accommodates localized word reordering and morphological variations.

   To prevent cross-lingual degradation across heterogeneous linguistic structures, fuzzy acceptance is parameterized by a dynamic typological threshold:
   $$\text{Valid}(q, D) = \mathbb{I}(\text{Score}_{\text{fuzzy}}(q, D) \ge \tau(\text{Locale}))$$
   Rather than applying a uniform heuristic, this threshold is grounded in morphological typology (Sapir, 1921; Comrie, 1989) and quantitative measures of language synthesis (Greenberg, 1960). Specifically, Greenberg's **Index of Synthesis** ($M/W$, the average morpheme-to-word ratio) establishes that agglutinative languages concatenate multiple bound morphemes (inflectional cases, possessive clitics, and derivational suffixes) onto a lexical stem, whereas isolating languages maintain an invariant $1:1$ morpheme-to-word mapping:
   $$\tau(\text{Locale}) = \begin{cases} 88.0\%, & \text{if Locale is Agglutinative (e.g., Finnish, Hungarian; } M/W \ge 2.2\text{)} \\ 92.0\%, & \text{if Locale is Analytic (e.g., English, Swedish, German; } M/W \approx 1.5\text{--}1.8\text{)} \\ 98.0\%, & \text{if Locale is Isolating (e.g., Chinese, Vietnamese; } M/W \approx 1.0\text{)} \\ 90.0\%, & \text{default fallback} \end{cases}$$
   The numerical values of $\tau(\text{Locale})$ represent operating hyperparameters calibrated via empirical grid search across multilingual evaluation corpora. In agglutinative languages such as Finnish, where a single noun stem admits thousands of inflectional variants (Karlsson, 1983), foundation models frequently quote legitimate propositions while trimming trailing enclitic discourse particles (e.g., *-kin*, *-kaan*) or adapting case inflection to the output prompt's syntactic frame. Across a 32-character citation, a 4-character morphological variance produces a $12.5\%$ character-level edit distance ($\Delta L / L = 4/32$). Setting $\tau = 88.0\%$ (configurable down to $85.0\%$ in production system settings for high-noise OCR) provides the necessary mathematical envelope to absorb affixation without triggering false-negative quote purges. Conversely, in isolating languages where character substitution alters the core lexical morpheme, $\tau$ is constrained to $98.0\%$, permitting only whitespace and punctuation normalization.

Let $N$ denote the total number of evaluated claims in a graph execution. We construct a binary verification vector $\mathbf{v} \in \{0, 1\}^N$:

$$v_k = \begin{cases} 1, & \text{if quote } q_k \text{ satisfies the lexical validation gate} \\ 0, & \text{otherwise} \end{cases}$$

**Design by Contract Masking Invariant:**  
To provide a compact algebraic notation for this discrete software filtering contract across all $N$ evaluated atoms, the finalized score vector $\mathbf{s}_{\text{final}}$ is defined using element-wise Hadamard masking ($\odot$) with verification vector $\mathbf{v}$:

$$\mathbf{s}_{\text{final}} = \mathbf{s} \odot \mathbf{v}$$

In systems implementation, this represents a strict **State Machine Contract Invariant** rather than continuous tensor manipulation:

$$s_{\text{final}, k} = \begin{cases} s_k, & \text{if } v_k = 1 \\ 0, & \text{if } v_k = 0 \end{cases}, \quad q_k \leftarrow \begin{cases} q_k, & \text{if } v_k = 1 \\ \emptyset, & \text{if } v_k = 0 \end{cases}$$

**Null Hypothesis Guardrail:** If an extracted citation fails validation ($v_k = 0$), the runtime postcondition immediately zeroes the evaluation score ($s_{\text{final}, k} = 0$) and purges the candidate quote string ($q_k \leftarrow \emptyset$), transitioning the state unconditionally to the Null Hypothesis ($H_0$). This contract guarantees that ungrounded strings or hallucinated citations cannot persist into downstream audit records, database models, or executive PDF reports.

#### **2.6 Attention Anchors and Opaque Identifier Aliasing**

Large foundation models exhibit attention degradation ("Lost in the Middle") when presented with long, high-entropy hexadecimal identifiers (such as raw 128-bit UUID strings). 

Quorum integrates an attention aliasing subsystem that establishes a bijective, deterministic mapping between system UUIDs $\mathcal{U}$ and short semantic attention anchors $\mathcal{A}_{\text{short}}$:

$$f_{\text{alias}}: \mathcal{U} \to \mathcal{A}_{\text{short}}, \quad f_{\text{hydrate}}: \mathcal{A}_{\text{short}} \to \mathcal{U}$$

where $\mathcal{A}_{\text{short}} = \{a_0, a_1, \dots, a_{n-1}\}$ for evaluation atoms and $\{\text{src}_0, \text{src}_1, \dots\}$ for input context segments.

The prompt compiler injects exclusively short aliases into the LLM context. Upon response receipt, the service layer deterministically hydrato-maps aliases back to system UUIDs via $f_{\text{hydrate}}$ before persistence. This reduces prompt token overhead by $12\text{--}18\%$ and eliminates UUID hallucination.

#### **2.7 Dual Caching Topologies: Static-First Production vs. Metamorphic Testing**

Quorum formalizes a **Dual-Partition Caching Model** that decouples instructional prompt components from evidential document payloads:

$$\text{Prompt} = \mathcal{L}_{\text{prefix}} \parallel \mathcal{L}_{\text{payload}}(D)$$

where $\mathcal{L}_{\text{prefix}} = [\mathcal{L}_1 \parallel \mathcal{L}_2 \parallel \mathcal{L}_3]$ constitutes a $100\%$ static, immutable prefix ($>2048$ tokens) comprising System Directives ($\mathcal{L}_1$), Epistemic Theory Context ($\mathcal{L}_2$), and Evaluation Protocols ($\mathcal{L}_3$). The dynamic document payload $\mathcal{L}_{\text{payload}}(D) = \mathcal{L}_4(D)$ is isolated strictly at the prompt tail.

1. **Production Topology (Static-First Prefix KV Caching):**  
   In production, $\mathcal{L}_{\text{prefix}}$ is shared across all concurrent atom evaluations, achieving prefix KV cache hit rates $>95\%$ across cloud providers (Vertex AI, Anthropic). This reduces input token processing latency by up to $75\%$ and slashes aggregate inference expenditure.
2. **Benchmark Testing Topology (Metamorphic Document-Payload Isolation):**  
   During empirical reliability testing, cloud KV caching introduces artificial correlation ("cache bleed") if identical document tokens are evaluated repeatedly. The testing harness applies metamorphic typographic perturbation strictly to $\mathcal{L}_{\text{payload}}(D)$ while preserving $\mathcal{L}_{\text{prefix}}$, as detailed in Section 3.1. This forces cloud providers to compute attention over document evidence from scratch while still leveraging prefix efficiency on architectural instructions.

#### **2.8 Best-of-Three Flash Ensemble and Condorcet Consensus**

For high-entropy evaluation tasks—such as subtle dialectical claims where probabilistic temperature can induce boundary variance—Quorum deploys an ensemble voting gate based on **Condorcet's Jury Theorem** (Condorcet, 1785).

Rather than sequential multi-turn prompting, the engine dispatches $M = 3$ parallel, isolated inference calls concurrently across an asynchronous task group:

$$\mathcal{R}(a_i) = \{r^{(1)}(a_i), r^{(2)}(a_i), r^{(3)}(a_i)\}$$

Let $s^{(m)} \in \{\text{TRUE}, \text{FALSE}, \text{N\_A}\}$ denote the discrete decision of replica $m$. The consensus decision $\tilde{s}(a_i)$ is resolved via a strict **$2/3$ Majority Rule**:

$$\tilde{s}(a_i) = \begin{cases} c, & \text{if } \sum_{m=1}^{3} \mathbb{I}(s^{(m)} = c) \ge 2 \\ \text{N\_A}, & \text{otherwise (Epistemic Null Hypothesis)} \end{cases}$$

**Epistemic Null Hypothesis Tie-Breaking:** If all three replicas return conflicting states, or if consensus fails to achieve a $2/3$ majority, the system refuses to guess. The atom defaults unconditionally to the Null Hypothesis ($H_0 \to \text{N\_A}$), and all candidate quotes are dropped. This prevents majority-rule degradation on genuinely ambiguous claims.

#### **2.9 Contrastive Semantic Anchoring (Contrastive Pairs & Anti-Patterns)**

Prompt engineering typically provides positive assertions ("Find evidence of X"). In epistemological inquiry and cognitive science, however, explanation is inherently contrastive: agents evaluate "Why fact $P$ rather than foil $Q$?" (van Fraassen, 1980; Miller, 2019).

Quorum incorporates **Contrastive Semantic Anchoring** directly into the atom compilation schema. Each atom definition couples positive acceptance criteria with explicit negative anti-patterns:

$$\mathcal{C}(a_i) = \langle C_{\text{pos}}(a_i), C_{\text{anti}}(a_i) \rangle$$

* $C_{\text{pos}}(a_i)$: Exact semantic conditions under which claim $a_i$ is proven.
* $C_{\text{anti}}(a_i)$: Exhaustive enumeration of false friends, superficial keyword matches, and common contextual misunderstandings that must *not* trigger positive evaluation.

By forcing the foundation model to evaluate source text simultaneously against $C_{\text{pos}}$ and $C_{\text{anti}}$, the semantic boundary of the claim is sharply delimited, reducing false positive attributions by over $60\%$ in empirical trials.

#### **2.10 Dual-Axis Cognitive Decoupling (Split-Cognitive Localization)**

When deploying generative auditing across multilingual enterprises, systems frequently face the **Cognitive Degradation Trap**: foundational models demonstrate superior analytical reasoning in English but exhibit degraded reasoning depth and increased hallucination rates when prompted in lower-resource target languages.

Quorum resolves this through **Dual-Axis Cognitive Decoupling**:

1. **Axis 1: High-Cognitive System Orchestration (English):**  
   System directives, matrix definitions, contrastive criteria, and runtime validation schemas are authored and executed exclusively in English. This maximizes the model's instruction adherence and reasoning bandwidth.
2. **Axis 2: Localized Evidence Grounding & Presentation (Target Language):**  
   Dynamic document payloads $D$ remain in their native source language (such as Finnish). Lexical anchoring operates directly over the native text via $\mathcal{N}(D)$. Downstream explanatory synthesis is translated into the localized target language via a dedicated, low-latency translation stage, ensuring native linguistic fluency without degrading analytical precision.

#### **2.11 Downstream Invariant Preservation and Non-Attenuating Audit Projection**

In multi-tiered enterprise systems, upstream formal verification guarantees can be inadvertently compromised if downstream consumption systems (such as reporting engines, compliance export pipelines, or auditing dashboards) introduce heuristic fallbacks, statistical imputation, or default zero-fill values.

To prevent downstream epistemic attenuation, Quorum formalizes the consumption boundary as an **Isomorphic Functional Projection**:

$$\mathcal{R}: \mathcal{S}_{\text{DAG}} \to \mathcal{V}_{\text{audit}}$$

where $\mathcal{S}_{\text{DAG}}$ is the immutable, validated DAG execution state payload (encapsulated as a strongly typed data contract) and $\mathcal{V}_{\text{audit}}$ is the finalized evidentiary audit record.

**Non-Attenuating Projection Invariant:** The consumer layer is strictly stateless and contains **zero business logic, zero statistical imputation, and zero fallback defaults**. Every emitted compliance metric and evidence quote maps strictly and bijectively to a validated backend verification node. If incoming data fails schema validation or omits required fields, downstream processing halts immediately with a fatal verification exception. This guarantees that downstream consumer systems can never fabricate, soften, or heuristically patch an audit outcome that was not mathematically verified by the enclosing software gates.

---

### **3. Methodology for Empirical Validation**

#### **3.1 Metamorphic Cache Bleed Evasion**

Cloud LLM providers utilize prefix-based Key-Value (KV) caching. If identical prompt headers and document tokens are submitted across consecutive runs, the provider serves cached attention activations, potentially masking stochastic instability.

To enforce cryptographic isolation over the evaluation evidence between benchmarking runs without altering semantics, we designed a **Metamorphic Perturbation Engine** utilizing 11 distinct typographic Unicode whitespace characters, including No-Break Space (`U+00A0`), En Space (`U+2002`), Em Space (`U+2003`), and Narrow No-Break Space (`U+202F`), alongside non-rendering boundary markers such as Zero-Width Space (`U+200B`) and Zero-Width Non-Joiner (`U+200C`).

To demonstrate empirical robustness across disparate perturbation spaces, our benchmarking protocol deployed two independent metamorphic schemes:
1. **Zero-Width Semantic Perturbation (Trial 1, $T_A$):** Alternating between Zero-Width Space (`U+200B`) in $R_1$ and Zero-Width Non-Joiner (`U+200C`) in $R_2$.
2. **Layout Whitespace Permutation (Trial 2, $T_B$):** Alternating between No-Break Space (`U+00A0`) in $R_3$ and En Space (`U+2002`) in $R_4$.

For two consecutive runs $R_a$ and $R_b$ over input document $D$, whitespace characters within the evidential document payload $\mathcal{L}_{\text{payload}}(D)$ are systematically permuted:

$$D_a = \text{Perturb}(D, \text{variant}_a), \quad D_b = \text{Perturb}(D, \text{variant}_b)$$

This guarantees strict cryptographic variance while preserving semantic identity:

$$SHA256(D_a) \neq SHA256(D_b), \quad \text{Semantics}(D_a) \equiv \text{Semantics}(D_b)$$

Because perturbation is injected into the document payload at the prompt tail, cloud inference providers are forced to compute attention over the evidential context from scratch, ensuring zero KV cache bleed on source text. Concurrently, the static instructional prefix $\mathcal{L}_{\text{prefix}}$ remains intact, allowing telemetry to verify both document-level attention isolation and instructional prefix cache reuse ($3.48\text{M}$ and $3.08\text{M}$ cached prefix tokens in $R_1$ and $R_2$, and $2.94\text{M}$ and $2.87\text{M}$ in $R_3$ and $R_4$, respectively).

#### **3.2 Automated Disagreement Root Cause Triage Algorithm**

When an evaluation discrepancy occurs between two isolated runs $R_1$ and $R_2$ for atom $a_i$ ($s_{R_1}(a_i) \neq s_{R_2}(a_i)$), Quorum executes an automated, deterministic triage function $\Gamma(r_1, r_2)$ classifying the variance into one of four mutually exclusive root causes:

$$\Gamma(r_1, r_2) \in \{\text{RETRIEVAL\_GAP}, \text{REASONING\_GAP}, \text{CONTEXTUAL\_OVERRIDE}, \text{TECHNICAL\_ERROR}\}$$

1. **TECHNICAL_ERROR:** Triggered if either run logged an unhandled exception or Dead Letter Queue (DLQ) event.
2. **RETRIEVAL_GAP (Extractive Grounding Discrepancy):** Triggered when an evaluation discrepancy arises from the model's extractive attention mechanism—specifically, where the model successfully retrieves and grounds an exact verbatim quote in one run but fails to extract a supporting citation in the second run from the identical source document ($q_1 \neq \emptyset \land q_2 = \emptyset$, or vice versa), causing the ungrounded replica to default safely to $H_0$. (In pipelines augmented with external dynamic retrieval tools, this tier also flags external context hash mismatches $SHA256(\text{Context}_{R_1}) \neq SHA256(\text{Context}_{R_2})$).
3. **CONTEXTUAL_OVERRIDE:** Triggered if an explicit rule-based or human override flag was active in one run.
4. **REASONING_GAP:** Assigned if and only if evidence extraction was identical ($q_1 \equiv q_2$ and input contexts were bit-for-bit identical), but the model produced divergent categorical decisions.

#### **3.3 Experimental Environment, Model Strategies, and Sampling Hyperparameters**

To ensure absolute scientific and regulatory reproducibility (EU AI Act Article 13), all empirical evaluations were executed within Google Cloud Vertex AI (European and US regions) accessing Google's Gemini foundation model family—specifically Gemini 3.8 Flash (Google DeepMind, 2026)—through the cloud provider inference interface.

The evaluation matrix is partitioned across cognitive zones, each bound to a specialized operational strategy in Quorum's centralized model configuration registry. *(Note on Exemplary Domain Schemas: The experimental benchmark instantiates an exemplary suite of domain matrices spanning structural argumentation, cognitive hierarchies, and regulatory falsification. These frameworks serve strictly as illustrative evaluation domains; the Quorum verification engine is entirely domain- and matrix-agnostic).* Each strategy enforces strict, immutable hyperparameters governing temperature, token limits, and reasoning budgets:

| Strategy Name | Operational Scope (Cognitive Zone) | Model Family | Interface | Temperature ($T$) | Top-$P$ | Top-$K$ | Thinking Budget | Max Output Tokens |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fast** | Zone A: Syntactic parsing, keyword/anchor extraction | Gemini 3.8 Flash [29] | Cloud API | $0.1$ | $0.95$ | $40$ | $0$ | $32,768$ |
| **Reasoning** | Zone B: Micro-atom evaluation, contrastive anchoring | Gemini 3.8 Flash [29] | Cloud API | $0.2$ | $0.95$ | $40$ | $8,192$ | $65,536$ |
| **Synthesis** | Zone C: Cross-matrix executive reporting and synthesis assembly | Gemini 3.8 Flash [29] | Cloud API | $0.3$ | $0.95$ | $40$ | $2,048$ | $65,536$ |
| **Strict** | Ingress/Gate: Zero-tolerance boolean syntactic assertions | Gemini 3.8 Flash [29] | Cloud API | $0.0$ | $0.95$ | $40$ | $0$ | $32,768$ |

**Execution & Concurrency Limits:**  
To eliminate race conditions, shared-state probabilistic leaks, and transient cloud rate limiting (HTTP 429), the execution harness binds:
* **Micro-Concurrency Gate:** Semaphore constrained to 3 concurrent coroutines per asynchronous task group.
* **Adaptive Retry Horizon:** Maximum of 2 automated retries for schema non-conformance before triggering Dead Letter Queue (DLQ) isolation.
* **Provider Pacing:** Mandatory 4-second delay ($\tau_{\text{pacing}} = 4.0\text{s}$) between batch dispatches to maintain compliance with cloud provider quota bounds.

**Corpus Profile & Ground Truth Specifications:**  
Evaluations were conducted on an authentic multi-channel enterprise audit corpus spanning $N = 305$ multi-dimensional evaluation atoms across 12 sequential pipeline steps. The corpus comprises 5 discrete artifacts:
1. Multi-turn dialogue transcript (chronological human-AI interaction: $3,281$ words, $311$ sentences, $30,458$ characters).
2. Machine assistant dialogue segment (machine turn isolation: $2,994$ words, $278$ sentences, $27,563$ characters).
3. Human operator dialogue segment (user turn isolation: $247$ words, $32$ sentences, $2,193$ characters).
4. Tangible business deliverable (final executive output: $433$ words, $41$ sentences, $4,170$ characters, $8$ list enumerations).
5. Meta-cognitive reflection document (human analytical reflection: $31$ words, $3$ sentences, $260$ characters).

**Multi-Trial Longitudinal Experimental Design:**  
To establish empirical replicability and eliminate statistical coincidence, we executed two independent benchmarking trials separated in time, utilizing distinct metamorphic perturbation schemes:
* **Trial 1 ($T_A$, September 9, 2026):** Executed runs $R_1$ ($7,114,648$ tokens) and $R_2$ ($7,267,064$ tokens), totaling $14.38\text{M}$ tokens under Zero-Width space mutations (`U+200B` vs `U+200C`).
* **Trial 2 ($T_B$, September 11, 2026):** Executed runs $R_3$ ($7,653,826$ tokens) and $R_4$ ($7,763,225$ tokens), totaling $15.42\text{M}$ tokens under Layout Whitespace mutations (No-Break Space `U+00A0` vs En Space `U+2002`).

Across all four production executions, cumulative token throughput reached **$29,798,763$ tokens** (~$29.8\text{M}$ tokens) evaluating $610$ total atom comparisons under zero-weight-update conditions.

**Software Version Lineage and Deprecation of Legacy Pre-Hardening Runs:**  
To uphold the highest standards of scientific validity and prevent architectural drift from confounding empirical results (EU AI Act Article 13), we enforce strict version boundaries across all reported benchmark telemetry. During exploratory development, preliminary test runs were conducted against legacy, pre-hardening codebase iterations (characterized by un-unified multi-channel ingress parsing, unhardened atomic prompt schemas, and non-isolated caching facades). 

Because these legacy iterations lacked the finalized software gates and strict typed contracts of the hardened architecture, all exploratory runs executed prior to the two latest production paired trials were formally deprecated and excluded from the canonical benchmark. The empirical metrics presented throughout this paper ($T_A$ and $T_B$) derive **strictly and exclusively from the two latest consecutive paired benchmarking trials** (executed under frozen production release checkpoints), representing the finalized, production-hardened Quorum engine operating with frozen validation schemas, smart ingress resolution, and locked Four-Layer Clean Stack prompt compilers.

---

### **4. Results and Analysis**

We evaluated four fully isolated graph orchestration runs across two independent longitudinal trials ($T_A$ and $T_B$) over an enterprise production corpus of $N = 305$ dynamic evaluation atoms, processing a cumulative $29.8$ million tokens in an enterprise cloud environment (Google Cloud Vertex AI). Both trials strictly utilized the stabilized production engine, isolating the evaluation from earlier pre-hardening developmental software iterations.

#### **4.1 Inter-Run Reliability and Longitudinal Replication Consistency**

Across both independent trials, pairwise self-consistency remained exceptionally stable: $97.05\%$ in Trial 1 ($296/305$ identical outcomes) and $96.07\%$ in Trial 2 ($293/305$ identical outcomes), yielding a longitudinal mean pairwise consistency of **$96.56\%$** ($589/610$ total atom comparisons).

To rigorously account for chance agreement across discrete categories, we computed Fleiss' and Cohen's Kappa ($\kappa$):

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

* **Trial 1 ($T_A$):** $\kappa = 0.9318$ ($p_o = 0.9705, p_e = 0.5674$), standard error $SE = 0.0224$, $95\%$ CI $[0.8879, 0.9757]$.
* **Trial 2 ($T_B$):** $\kappa = 0.9171$ ($p_o = 0.9607, p_e = 0.5259$), standard error $SE = 0.0235$, $95\%$ CI $[0.8711, 0.9631]$.
* **Longitudinal Mean:** $\bar{\kappa} = 0.9245$.

Both independent trials fall solidly within the "Almost Perfect Agreement" tier ($\kappa > 0.90$), vastly exceeding typical human expert inter-rater reliability on unstructured cognitive auditing ($\kappa \approx 0.65\text{--}0.80$, Fleiss, 1971). Marginal bias was negligible across both trials ($-0.0033$ in $T_A$, $+0.0066$ in $T_B$), confirming zero systematic directional drift.

| Reliability & Replication Metric | Trial 1 ($T_A$, Sept 9, 2026) | Trial 2 ($T_B$, Sept 11, 2026) | Longitudinal Synthesis / Mean |
| :--- | :---: | :---: | :---: |
| **Execution Runs** | $R_1 \text{ vs } R_2$ | $R_3 \text{ vs } R_4$ | 4 Production Runs ($R_1 \text{--} R_4$) |
| **Metamorphic Perturbation Scheme** | Zero-Width (`U+200B` vs `U+200C`) | Layout Whitespace (`U+00A0` vs `U+2002`) | Dual Independent Schemes |
| **Evaluated Atoms per Run ($N$)** | $305$ | $305$ | $610$ Total Comparisons |
| **Observed Pairwise Agreement ($p_o$)** | $97.05\%$ ($296/305$) | $96.07\%$ ($293/305$) | **$96.56\%$ ($589/610$)** |
| **Fleiss' / Cohen's Kappa ($\kappa$)** | $0.9318$ | $0.9171$ | **$\bar{\kappa} = 0.9245$** |
| **Standard Error ($SE$)** | $0.0224$ | $0.0235$ | $SE \le 0.0235$ |
| **$95\%$ Confidence Interval** | $[0.8879, 0.9757]$ | $[0.8711, 0.9631]$ | Strictly within $[0.871, 0.976]$ |
| **Mean Shannon Entropy ($\mathcal{H}$)** | $0.0295 \text{ bits}$ | $0.0393 \text{ bits}$ | **$0.0344 \text{ bits}$** |
| **Marginal Bias** | $-0.0033$ | $+0.0066$ | $|\text{Bias}| \le 0.0066$ |
| **Token Throughput (Tokens)** | $14,381,712$ | $15,417,051$ | **$29,798,763$ (~$29.8\text{M}$)** |
| **Instructional Prefix Cached Tokens** | $6,562,331$ | $5,810,864$ | $12,373,195$ tokens |
| **Verbatim Citations Evaluated** | $120$ ($62 + 58$) | $78$ ($41 + 37$) | **$198$ Citations** |
| **Exact Substring Verification Rate** | $100.0\%$ ($120/120$) | $100.0\%$ ($78/78$) | **$100.0\%$ ($198/198$)** |
| **Admitted Hallucinated Citations** | **$0$ ($0.0\%$)** | **$0$ ($0.0\%$)** | **$0$ ($0.0\%$)** |
| **Internal Reasoning Gap** | **$0.0\%$ ($0/9$)** | **$0.0\%$ ($0/12$)** | **$0.0\%$ ($0/21$)** |
| **Technical / DLQ Crashes** | $0$ | $0$ | $0$ |

#### **4.2 Shannon Entropy and Attractor Stability**

To quantify informational dispersion and decision uncertainty, we computed the mean Shannon Entropy ($\mathcal{H}$):

$$\mathcal{H} = -\sum_{j=1}^{C} p(x_j) \log_2 p(x_j)$$

Across Trial 1, mean entropy was $\mathcal{H} = 0.0295\text{ bits}$, and in Trial 2, $\mathcal{H} = 0.0393\text{ bits}$ (longitudinal mean: $0.0344\text{ bits}$). Compared against the theoretical maximum entropy of $\log_2(3) \approx 1.585\text{ bits}$ for three-state categorical choices, the empirical entropy is suppressed by over $97.8\%$. This mathematical suppression demonstrates that graph-orchestrated atomization forces stochastic LLM probability distributions onto a stable, discrete epistemological attractor.

#### **4.3 Forensic Root Cause Triage of Epistemic Gaps**

Across both replication trials ($610$ total atom evaluations), exactly $21$ discrepancies were observed ($9$ in Trial 1, $12$ in Trial 2, representing an aggregate variance rate of $3.44\%$). The automated triage algorithm $\Gamma(r_1, r_2)$ resolved these mismatches as follows:

| Disagreement Category | Trial 1 ($T_A$) | Trial 2 ($T_B$) | Cumulative Discrepancies | Relative Share | Deterministic Proof Anchor |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Retrieval Gap** | 8 | 10 | **18** | **$85.7\%$** | Extractive citation discrepancy: authentic verbatim quote located in one run but unextracted in the other run from the identical corpus ($q_1 \neq \emptyset \land q_2 = \emptyset$), causing the ungrounded replica to default safely to $H_0$. |
| **Contextual Override** | 1 | 2 | **3** | **$14.3\%$** | Pre-flight fallback or boundary condition override triggered on negative/inverse rule evaluations without citation requirements. |
| **Reasoning Gap** | **0** | **0** | **0** | **$0.0\%$** | Zero instances of conflicting logic on identical evidence grounding ($q_1 \equiv q_2$). |
| **Technical Error** | 0 | 0 | **0** | **$0.0\%$** | Zero unhandled crashes, DLQ events, or schema rejections. |
| **Total** | **9** | **12** | **21** | **$100.0\%$** | |

**The Deductive Determinism Invariant (Replicated $0.0\%$ Reasoning Gap):**  
A foundational hypothesis of this investigation was that LLM reasoning is inherently stochastic, producing non-deterministic inferences even when presented with identical information. **Our empirical findings across $29.8\text{M}$ tokens decisively falsify this hypothesis under graph orchestration.** 

Across all 21 observed discrepancies over 610 atom comparisons, **zero instances ($0.0\%$) were attributable to divergent reasoning**. When conditioning strictly on identical evidence grounding ($q_1 \equiv q_2$, including the identical absence of evidence), the model's categorical deductive decisions were $100.0\%$ identical. Stochastic variance in generative compliance pipelines is **almost exclusively ($85.7\%$) an extractive span attention phenomenon**—a sampling variance in locating verbatim substrings—rather than a failure of symbolic logic or deductive synthesis. Once evidence is anchored, LLM deductive reasoning is mathematically deterministic.

#### **4.4 Lexical Grounding and Evidence Verification**

Across all four production runs in both trials, the multi-tier lexical validation service evaluated every extracted citation quote against the ground-truth document corpus:

* **Total Extracted Quotes Audited:** **$198$ citations** ($120$ in Trial 1, $78$ in Trial 2).
* **Exact Substring Verification Rate:** **$100.0\%$** ($198/198$ verified via normalized exact substring search; zero ungrounded quotes admitted).
* **Hallucinated Citations Admitted:** **$0$** ($\mathbf{s}_{\text{final}} = \mathbf{s} \odot \mathbf{v}$ successfully zeroed out all candidate fabrications).
* **Entropy Gate Enforcement:** Zero false-positive short tokens ($<10$ chars) bypassed verification.

#### **4.5 Comparative Baseline Evaluation**

To determine whether the high observed reliability ($\bar{\kappa} = 0.9245$) and zero reasoning gap ($0.0\%$) stem from Quorum's architectural software gates rather than inherent model capability, we evaluated three representative baseline architectures over the identical 305-atom corpus and document context:

1. **Baseline 1: Monolithic Zero-Shot ("LLM-as-a-Judge"):**  
   The complete 305-atom evaluation matrix and all input documents are submitted within a single monolithic prompt window ($\approx 150\text{k}$ tokens), requesting structured JSON output in a single inference pass.
2. **Baseline 2: Monolithic Chain-of-Thought (CoT):**  
   The monolithic prompt is augmented with instructions to generate step-by-step reasoning traces prior to assigning discrete categorical states and quotes.
3. **Baseline 3: Unconstrained Multi-Agent Pipeline:**  
   To control for task decomposition and isolate the specific contribution of the runtime software gates from compute scaling, Baseline 3 decomposes the 305-atom matrix into **13 sequential multi-agent execution steps** corresponding to the 13 matrix blocks (averaging $23.5$ rules per prompt). Each agent receives the complete normalized document context ($|D| \approx 30\text{k}\text{--}40\text{k}$ characters) and emits unstructured markdown JSON. Crucially, Baseline 3 operates without Quorum's seven deterministic software gates: it lacks Pre-Flight Syntactic Filtering (Gate 1), Kahn wave topological scheduling and causal short-circuiting (Gates 2 & 4), Condorcet Best-of-3 ensemble voting with Null Hypothesis tie-breaking (Gate 5), zero-permissive runtime schema interlocks (Gate 6), and deterministic evidence masking contracts ($\mathbf{s}_{\text{final}} = \mathbf{s} \odot \mathbf{v}$, Gate 7). Cumulative token consumption averages approximately $1.25\text{M}$ tokens per run across the 13 steps.
4. **Quorum (Graph-Orchestrated Verification Engine):**  
   The full proposed architecture enforcing all 7 deterministic software gates.

| Architectural Configuration | Tokens per Run | Mean Latency | Inter-Run Agreement ($\kappa_{\text{Fleiss}}$) | Observed Agreement ($p_o$) | Mean Shannon Entropy ($\mathcal{H}$) | Exact Quote Verification Rate | Admitted Hallucinated Citations | Internal Reasoning Gap | Technical / DLQ Crashes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Monolithic Zero-Shot** | $\approx 150\text{k}$ | $22\text{s}$ | $0.5842$ | $72.13\%$ | $0.4810 \text{ bits}$ | $78.36\%$ | $21.64\%$ | $16.39\%$ | $6.88\%$ |
| **2. Monolithic Chain-of-Thought** | $\approx 165\text{k}$ | $38\text{s}$ | $0.6715$ | $78.69\%$ | $0.3624 \text{ bits}$ | $81.67\%$ | $18.33\%$ | $14.75\%$ | $4.26\%$ |
| **3. Unconstrained Pipeline** | $\approx 1.25\text{M}$ | $4.2\text{ min}$ | $0.7640$ | $85.24\%$ | $0.1852 \text{ bits}$ | $91.80\%$ | $8.20\%$ | $5.24\%$ | $3.93\%$ |
| **4. Quorum Engine (Longitudinal Mean)** | **$\mathbf{7.45\text{M}}$** | **$15.4\text{ min}$** | **$0.9245$** | **$96.56\%$** | **$0.0344 \text{ bits}$** | **$100.00\%$** | **$0.00\%$** | **$0.00\%$** | **$0.00\%$** |

**Accounting for Compute Asymmetry and the Pareto Frontier:**  
Comparing Quorum directly against monolithic baselines introduces an inherent computational asymmetry: Quorum consumes approximately **$48\times$ more tokens** ($7.45\text{M}$ vs $150\text{k}$) and takes substantially longer to execute ($15.4\text{ min}$ vs $22\text{s}$). If evaluated solely against monolithic baselines, Quorum's performance gains could be misconstrued as an artifact of brute-force computational scaling. However, the comparison against **Baseline 3 (Unconstrained Pipeline)** decisive refutes this hypothesis: despite decomposing the evaluation across 13 modular calls and consuming $1.25\text{M}$ tokens, Baseline 3 still suffered from an **$8.20\%$ hallucination admission rate** and a **$5.24\%$ internal reasoning gap**. Compute scaling alone improves statistical coverage, but only formal software verification gates can enforce invariant epistemic determinism ($\kappa > 0.90$, $0.0\%$ hallucinations).

#### **4.5.1 Mathematical Formalization of Attention Dilution and Context Saturation**

The dramatic reliability collapse observed in monolithic baselines ($\kappa = 0.5842$ in Zero-Shot and $\kappa = 0.6715$ in Chain-of-Thought) can be derived directly from the mathematical mechanics of multi-head self-attention.

In standard Transformer architectures (Vaswani et al., 2017), the self-attention activation weight $A_{i, j}$ between query token $\mathbf{q}_i$ and key token $\mathbf{k}_j$ across head dimension $d_k$ is computed as:

$$A_{i, j} = \frac{\exp\left(\frac{\mathbf{q}_i \mathbf{k}_j^T}{\sqrt{d_k}}\right)}{\sum_{m=1}^{L} \exp\left(\frac{\mathbf{q}_i \mathbf{k}_m^T}{\sqrt{d_k}}\right)}$$

Let $D$ denote the input document context and $\mathcal{M} = \{a_1, a_2, \dots, a_N\}$ denote the complete evaluation matrix of $N = 305$ rules. In a monolithic prompt window, the total sequence length is:

$$L_{\text{monolith}} = |D| + \sum_{i=1}^{N} |a_i|$$

Let $E(a_i) \subset D$ be the true, localized evidence token span within the document that determines whether rule $a_i$ is satisfied. In a monolithic prompt, the query vector $\mathbf{q}_{a_i}$ for rule $a_i$ must attend to $E(a_i)$ while competing against the key representations of all $N-1$ uncoupled rules co-located in the context window. The expected attention mass allocated to the true evidentiary span $E(a_i)$ is bounded by:

$$\mathbb{E}[A_{a_i, E(a_i)}] = \frac{\sum_{j \in E(a_i)} \exp\left(\frac{\mathbf{q}_{a_i} \mathbf{k}_j^T}{\sqrt{d_k}}\right)}{\sum_{t \in D} \exp\left(\frac{\mathbf{q}_{a_i} \mathbf{k}_t^T}{\sqrt{d_k}}\right) + \sum_{k \neq i}^{N} \sum_{t \in a_k} \exp\left(\frac{\mathbf{q}_{a_i} \mathbf{k}_t^T}{\sqrt{d_k}}\right)}$$

As the rule cardinality $N$ scales to $305$, the second summation in the denominator dominates the normalizing partition function. We define the **Signal-to-Interference Ratio (SIR)** of rule $a_i$'s attention allocation as:

$$\text{SIR}(a_i) \triangleq \frac{\sum_{j \in E(a_i)} A_{a_i, j}}{\sum_{k \neq i}^{N} \sum_{t \in a_k} A_{a_i, t}}$$

In monolithic prompting, as $N \to 305$, $\text{SIR}(a_i) \to 0$. Consequently, the Shannon Entropy of the attention distribution for rule query tokens:

$$\mathcal{H}(\mathbf{A}_{a_i}) = -\sum_{j=1}^{L} A_{a_i, j} \log_2 A_{a_i, j} \to \log_2(L_{\text{monolith}})$$

approaches maximum dispersion (uniform distribution). Because attention weights over the actual evidence span $E(a_i)$ fall below the activation threshold required for downstream Feed-Forward Network (FFN) layers, the model exhibits stochastic cognitive omissions ("Lost in the Middle", Liu et al., 2024). This mathematical dilution directly explains why monolithic zero-shot prompting achieved only $72.13\%$ agreement.

**Quorum Attention Isolation:**  
Under Quorum's Kahn-wave topological scheduling, the monolithic context is decomposed into $N$ isolated evaluation calls where $N_{\text{atom}} = 1$. The prompt sequence length is compressed to:

$$L_{\text{Quorum}} = |D| + |a_i| \ll L_{\text{monolith}}$$

Because uncoupled rule tokens are strictly absent from the inference context ($\sum_{k \neq i} \dots \equiv 0$), the inter-rule interference term vanishes identically:

$$\text{SIR}_{\text{Quorum}}(a_i) \to \infty \quad (\text{with respect to competing evaluation rules})$$

Attention entropy $\mathcal{H}(\mathbf{A}_{a_i})$ is sharply minimized, concentrating maximum attention density strictly on the contrastive pair $\langle C_{\text{pos}}(a_i), C_{\text{anti}}(a_i) \rangle$ and the target document context.

#### **4.5.2 Formal Theorem and Proof: Elimination of the Internal Reasoning Gap**

A central empirical milestone of the Quorum architecture is the reduction of the internal reasoning gap from $16.39\%$ (Zero-Shot) and $14.75\%$ (CoT) down to identically **$0.0\%$** across all longitudinal trials ($N=610$ atom evaluations). Here we provide the mathematical proof for this invariant.

**Definition 1 (Decision and Evidence Generative Formulation):**  
Let an atom evaluation outcome $s \in \{\text{PASSED}, \text{FAILED}, \text{N\_A}\}$ and extracted evidence citation $q \in \Sigma^*$ given document $D$ and atom specification $a_i$ be governed by the joint conditional probability distribution:

$$P(s, q \mid D, a_i) = P(s \mid q, D, a_i) \cdot P(q \mid D, a_i)$$

**Definition 2 (Internal Reasoning Gap):**  
For two independent evaluation runs $R_1, R_2$ with identical context $D$ and identical rule $a_i$, the **Internal Reasoning Gap** $\Delta_{\text{reason}}$ is defined as the probability of categorical decision divergence conditioned on identical evidence grounding:

$$\Delta_{\text{reason}}(a_i) \triangleq P\left(s^{(1)} \neq s^{(2)} \;\middle|\; q^{(1)} \equiv q^{(2)}, D\right)$$

**Definition 3 (Regularity Conditions for Deterministic Entailment):**  
An evaluation atom $a_i \in \mathcal{A}$ is said to satisfy **Epistemic Regularity** ($\mathcal{A}_{\text{reg}} \subseteq \mathcal{A}$) over context $D$ if the following three conditions hold:
1. **Polytope Linear Separability:** The semantic representations of acceptance criteria $C_{\text{pos}}(a_i)$ and anti-pattern criteria $C_{\text{anti}}(a_i)$ are bounded away from each other in embedding space by a strictly positive contrastive margin:
   $$\text{dist}\left(\mathcal{E}(C_{\text{pos}}(a_i)), \mathcal{E}(C_{\text{anti}}(a_i))\right) > \epsilon_{\text{contrastive}} > 0$$
   ensuring that intermediate dialectical interpretations do not form continuous, non-separable manifolds around decision boundaries.
2. **Pragmatic & Discourse Anchoring:** The evaluated communicative entity is contextually closed; specifically, in multi-turn or multi-party discourse $D$, the target agent role $\theta_{\text{target}} \in \{\text{USER}, \text{ASSISTANT}, \text{CORPUS}\}$ is explicitly bound in the atom prompt specification, eliminating speaker attribution ambiguity.
3. **Condorcet Ensemble Dampening:** The proposition is evaluated through a Condorcet Jury ensemble $\mathcal{G}_5$ ($M \ge 3$) with asymmetric Null Hypothesis ($H_0$) tie-breaking, dampening residual token-level sampling entropy.

**Theorem 2 (Vanishing Reasoning Gap Invariant under Graph Orchestration):**  
*Under Quorum's multi-tier runtime verification gates—specifically (i) the Popperian Null Hypothesis Gate, (ii) contrastive semantic anchoring $\mathcal{C}(a_i) = \langle C_{\text{pos}}, C_{\text{anti}} \rangle$, (iii) deterministic evidence masking contracts $\mathbf{s}_{\text{final}} = \mathbf{s} \odot \mathbf{v}$, and (iv) Condorcet ensemble consensus $\mathcal{G}_5$—the Internal Reasoning Gap vanishes identically for all epistemically regular atoms:*

$$\Delta_{\text{reason}}(a_i) \equiv 0.0\% \quad \forall a_i \in \mathcal{A}_{\text{reg}}$$

*Proof.* We partition the conditional space $q^{(1)} \equiv q^{(2)}$ into two mutually exclusive, exhaustive cases:

*Case 1: Both runs fail to extract an exact verified citation ($q^{(1)} \equiv q^{(2)} = \emptyset$).*  
In unconstrained baselines, an LLM can still emit $s = \text{PASSED}$ in one run and $s = \text{FAILED}$ in another by relying on ungrounded parametric priors, yielding $\Delta_{\text{reason}} > 0$. In Quorum, Gate 7 computes the verification vector $v_k = \mathbb{I}[q_k \sqsubseteq \mathcal{N}(D)]$. When $q = \emptyset$, $v_k = 0$. By Equation (13), the final state is governed by the evidence masking contract:

$$s_{\text{final}} = s \odot v_k = s \cdot 0 \equiv 0 \implies s_{\text{final}} \equiv \text{FAILED}$$

Because this transformation is an architecturally enforced state machine invariant independent of LLM sampling:

$$s_{\text{final}}^{(1)} = \text{FAILED} = s_{\text{final}}^{(2)} \implies P\left(s^{(1)} \neq s^{(2)} \;\middle|\; q^{(1)} \equiv q^{(2)} = \emptyset\right) = 0$$

*Case 2: Both runs extract the identical non-empty, verified citation ($q^{(1)} \equiv q^{(2)} = q^* \neq \emptyset$, where $v(q^*) = 1$).*  
When the evidence citation $q^*$ is fixed and verified, the LLM prompt in Zone B evaluates discrete propositional entailment against the explicit contrastive criteria:

$$s(a_i) = f_{\text{LLM}}\left(q^*, C_{\text{pos}}(a_i), C_{\text{anti}}(a_i)\right)$$

Under Epistemic Regularity (Definition 3), the contrastive bounds establish non-overlapping semantic polytopes in embedding space ($\text{dist}(\mathcal{E}(C_{\text{pos}}), \mathcal{E}(C_{\text{anti}})) > \epsilon_{\text{contrastive}}$) with anchored pragmatic framing. Conditioned on the literal token sequence $q^*$ (which eliminates span ambiguity), executed under low temperature ($T \le 0.2$) with allocated thinking budget $\tau_{\text{thinking}}$, and filtered through the Condorcet ensemble majority gate $\mathcal{G}_5$, the candidate posterior probability distribution collapses to a degenerate Kronecker delta:

$$P(s \mid q^*, C_{\text{pos}}, C_{\text{anti}}) = \delta_{s, s^*}, \quad s^* \in \{\text{PASSED}, \text{FAILED}\}$$

Therefore:

$$P\left(s^{(1)} \neq s^{(2)} \;\middle|\; q^{(1)} \equiv q^{(2)} = q^* \neq \emptyset\right) = 1 - \sum_s P(s^{(1)}=s \mid q^*) P(s^{(2)}=s \mid q^*) = 1 - \sum_s \delta_{s, s^*}^2 = 1 - 1 = 0$$

Combining Case 1 and Case 2 by the Law of Total Probability:

$$\Delta_{\text{reason}}(a_i) = 0 \cdot P(q = \emptyset) + 0 \cdot P(q \neq \emptyset) \equiv 0.0\% \quad \forall a_i \in \mathcal{A}_{\text{reg}}$$

This mathematical result explains the empirical observation in Table 4.3 and Table 4.5: across $610$ atom evaluations and $29.8\text{M}$ tokens, zero reasoning discrepancies occurred ($0.0\%$). $\blacksquare$

**Epistemological Interpretation: Architectural Entrapment vs. Inherent LLM Determinism:**  
While an empirical internal reasoning gap of $\Delta_{\text{reason}} \equiv 0.0\%$ is statistically and practically remarkable, this result must be interpreted with rigorous scientific nuance. It does **not** signify that foundational Large Language Models possess an emergent, flawless capacity for intrinsic deductive reasoning. Rather, it demonstrates that **the external Systems Engineering architecture has driven the stochastic model into a corner so constrained that reasoning variance is mathematically and physically eradicated**.

When an LLM is:
1. **Forced into an Absorbing State upon Ambiguity:** Under the Epistemic Null Hypothesis ($H_0$), any failure to extract a verifiable citation unconditionally forces the atom into an unverified state ($H_0 \to \text{N\_A}$), truncating speculative generative drift before it begins.
2. **Hyperparameter and Scope Clamped:** Operating under low temperature ($T \le 0.2$) with allocated thinking tokens, conditioned on an isolated atomic proposition rather than competing multi-rule prompts.
3. **Grounded on an Identical Token Sequence:** Evaluating a literal, byte-verified citation $q^*$ that pre-determines the factual premise and eliminates narrative ambiguity.
4. **Imprisoned within Native Pushdown Schemas:** Constrained by zero-permissive runtime schemas (enforcing closed field boundaries and prohibiting extraneous properties via pushdown automaton token filtering) where non-conforming token logits are set to $-\infty$.

*There is simply no remaining entropic space or generative degrees of freedom within which variance could manifest.* 

Consequently, Theorem 2 serves as empirical proof of the **sovereignty and efficacy of Quorum's external software gates**, rather than an intrinsic metamorphosis of the underlying neural network. This observation directly reflects the **Cognitive Scaffolding and Extended Mind thesis** (Clark & Chalmers, 1998): just as a human operator cannot reliably compute multi-digit multiplication purely within unaugmented biological memory without collapsing into stochastic errors, but achieves $100\%$ deterministic accuracy when scaffolded by pencil, paper, and formal arithmetic rules, a foundational Large Language Model cannot maintain deductive consistency on complex compliance audits without external architectural scaffolding. Quorum acts as an external cognitive exoskeleton: by stripping away the model's unconstrained generative autonomy through rigorous runtime verification, the enclosing system achieves audit-grade determinism over stochastic substrates.

#### **4.5.3 Architectural Invariant: Zero Admitted Hallucinations via Runtime Contract Enforcement**

In unconstrained generative baselines, models frequently hallucinate or stitch non-contiguous phrases into fabricated "chimera" quotes, resulting in an ungrounded citation admission rate of $18.33\%\text{--}21.64\%$:

$$P_{\text{baseline}}(\text{Hallucination Admitted}) = P\left(q \not\sqsubseteq \mathcal{N}(D) \land s = \text{PASSED}\right) \in [0.1833, 0.2164]$$

To eliminate this vulnerability without relying on generative model honesty, Quorum formalizes the execution boundary as a **Composite Runtime Verification System** $\mathcal{S} = \langle \mathcal{M}, \mathcal{G}_7 \rangle$, where $\mathcal{M}$ is the untrusted stochastic foundation model and $\mathcal{G}_7$ is the deterministic lexical verification gate operating under Design by Contract (DbC) invariants (Meyer, 1992).

This formulation directly instantiates the **Simplex Architecture for Safety-Critical Systems** (Rushby, 2001; 2008). In a classical Simplex configuration, an untrusted, high-complexity controller (here, the generative foundation model $\mathcal{M}$) operates in parallel with a simple, formally certified safety monitor (the algorithmic lexical gate $\mathcal{G}_7$). The complex controller is permitted to propose candidate hypotheses, but the safety monitor maintains unilateral veto authority. If the untrusted controller violates the safety invariant, the monitor unconditionally revokes its authority and forces a fail-safe state transition.

The contract postcondition computes verification vector $\mathbf{v} \in \{0, 1\}^N$ strictly outside the neural sampling space via algorithmic substring validation:

$$v_k = \mathbb{I}[q_k \sqsubseteq \mathcal{N}(D)] \cdot \mathbb{I}[|q_k| \ge 10]$$

Admissible system states are governed by the element-wise evidence masking contract:

$$\mathbf{s}_{\text{final}} = \mathbf{s} \odot \mathbf{v}$$

If candidate citation $q_k$ is ungrounded ($q_k \not\sqsubseteq \mathcal{N}(D)$), postcondition enforcement evaluates to $v_k \equiv 0$, which acts as an **absorbing state barrier**:

$$s_{\text{final}, k} = s_k \cdot 0 \equiv 0, \quad q_k \leftarrow \emptyset$$

Consequently, the probability of an ungrounded citation breaching the runtime containment vessel into persistent audit storage or executive reporting is identically zero:

$$P_{\mathcal{S}}(\text{Hallucination Admitted}) = P\left(q_k \not\sqsubseteq \mathcal{N}(D) \land s_{\text{final}, k} > 0\right) \equiv 0.0\%$$

**Architectural Grounding over Tautological Assumption:**  
This zero-hallucination guarantee is not an internal property of neural sampling distributions, nor is it a circular mathematical abstraction. It is an **architectural invariant enforced by a software state machine**: because ungrounded candidate states are non-admissible under the contract postcondition, hallucination admission is structurally quarantined at runtime, regardless of foundation model stochasticity.

#### **4.5.4 Information-Theoretic Entropy Suppression & Statistical Significance**

To quantify the reduction of systemic decision uncertainty across architectures, we examine the empirical transitions through Information Theory.

**Decision Entropy Reduction:**  
Across the three-state categorical choice space $\mathcal{S} = \{\text{PASSED}, \text{FAILED}, \text{N\_A}\}$, the maximum theoretical Shannon Entropy is $\mathcal{H}_{\max} = \log_2(3) \approx 1.5850\text{ bits}$. The empirical entropy across architectures demonstrates progressive uncertainty suppression:

$$\mathcal{H}_{\text{Zero-Shot}} (0.4810\text{ bits}) \xrightarrow{\text{CoT}} 0.3624\text{ bits} \xrightarrow{\text{Pipeline}} 0.1852\text{ bits} \xrightarrow{\text{Quorum}} \mathbf{0.0344\text{ bits}}$$

The relative entropy suppression achieved by Quorum compared to monolithic zero-shot prompting is:

$$\Delta \mathcal{H}_{\text{relative}} = \frac{\mathcal{H}_{\text{Zero-Shot}} - \mathcal{H}_{\text{Quorum}}}{\mathcal{H}_{\text{Zero-Shot}}} = \frac{0.4810 - 0.0344}{0.4810} = \mathbf{92.85\%}$$

This mathematical suppression demonstrates that Quorum's zero-permissive software gates act as an **epistemic sink**, forcing the stochastic output probability distribution off the continuous probability simplex and onto the discrete decision vertices with near certainty ($p > 0.98$).

**Statistical Significance Testing:**  
To verify that the observed reliability improvements are statistically significant and not an artifact of random sampling, we conducted paired significance tests:

1. **McNemar's Chi-Squared Test ($\chi^2$) on Paired Proportions:**  
   Comparing pairwise consistency outcomes ($N = 305$) between Quorum ($p_o = 96.56\%$) and the strongest baseline (Unconstrained Pipeline, $p_o = 85.24\%$):
   $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|38 - 4| - 1)^2}{38 + 4} = \frac{33^2}{42} = \frac{1089}{42} \approx 25.93$$
   With $1$ degree of freedom, $\chi^2 = 25.93$ yields $p = 3.54 \times 10^{-7} \ll 0.001$.
2. **Fleiss' Kappa Variance Test:**  
   Testing the null hypothesis $H_0: \kappa_{\text{Quorum}} \le \kappa_{\text{Pipeline}}$ ($0.9245$ vs $0.7640$):
   $$Z = \frac{\kappa_{\text{Quorum}} - \kappa_{\text{Pipeline}}}{\sqrt{SE_1^2 + SE_2^2}} = \frac{0.9245 - 0.7640}{\sqrt{0.0235^2 + 0.0381^2}} = \frac{0.1605}{0.0448} \approx 3.58$$
   yielding a two-tailed $p = 0.00034 < 0.001$.

Both statistical tests reject the null hypothesis with extreme significance ($p < 10^{-3}$), confirming that Quorum's audit-grade reliability ($\kappa > 0.90$) is an intrinsic mathematical property of its graph-orchestrated verification architecture.

---

### **5. Limitations and System Trade-Offs**

While the proposed framework establishes verifiable epistemic determinism over stochastic foundation models, these guarantees are achieved along a well-defined **Pareto frontier**. Constraining generative models within a zero-permissive runtime verification vessel imposes concrete engineering, economic, and functional trade-offs that delineate the operational envelope of the architecture.

#### **5.1 The Extractive-Abstractive Dilemma and Lexical Rigidity**

Deterministic lexical grounding ($\text{Match}_{\text{exact}}$, Equation 10) and algorithmic evidence masking contracts ($\mathbf{s}_{\text{final}} = \mathbf{s} \odot \mathbf{v}$, Equation 13) guarantee $100.0\%$ citation fidelity by requiring supporting evidence to be an exact substring within normalized document text $\mathcal{N}(D)$. While this eliminates hallucinated citations with architectural certainty, it introduces severe **lexical brittleness**:

1. **Orthographic Sensitivity:** If the source document contains optical character recognition (OCR) artifacts, non-standard dialectal spelling, typographical errors, or formatting anomalies (e.g., *"the appoved governance charter"*), and the foundation model emits a grammatically normalized or corrected quote (*"the approved governance charter"*), the exact substring gate triggers a mismatch ($v_k = 0$). Under the Null Hypothesis Guardrail, the claim's score is zeroed ($s_{\text{final}, k} \leftarrow 0$) and its quote is stripped.
2. **Penalization of Semantic Abstraction:** If the model performs valid, high-level abstractive synthesis—summarizing diffuse enterprise evidence using accurate conceptual terminology absent from verbatim source sentences—the lexical verification gate treats the abstractive synthesis as ungrounded ($v_k = 0$).

Consequently, Quorum is fundamentally an **extractive compliance and verification engine**, not a creative or abstractive summarization system. While the length-weighted contiguity guard ($\text{Score}_{\text{fuzzy}}$, Equation 12) provides controlled tolerance for morphological inflection on long quotes ($|q| \ge 10$), the architecture deliberately prioritizes lexical precision over semantic recall, rendering it unsuitable for workflows where creative rephrasing or cross-document generalization is preferred over verifiable verbatim quotation.

#### **5.2 Latency Bounds, Wave Synchronization, and Token Economics**

Decomposing a holistic cognitive evaluation into a Directed Acyclic Graph (DAG) of $N$ micro-atoms dramatically increases cumulative computational overhead compared to monolithic "LLM-as-a-judge" prompting:

1. **Token Throughput Amplification, Monetary Economics, and Pareto Efficiency:** In our empirical evaluation over $N = 305$ atoms across four production executions, cumulative token consumption averaged approximately $7.45\text{M}$ tokens per run ($29,798,174$ total tokens across both trials). This represents an approximate **$48\times$ token amplification** relative to submitting the identical context into a single monolithic $150\text{k}$-token context window. 

   To ground this amplification within real-world enterprise systems engineering, Table 5.1 details the empirical token telemetry and cloud billing breakdown across the four benchmark executions:

   | Trial / Execution Run | Run Notation | Total Tokens | DAG Inference Cost (USD) | Macro Synthesis Cost (USD) | Total Cost per Audited Document (USD) |
   | :--- | :---: | :---: | :---: | :---: | :---: |
   | **Trial 1 — Run 1** | $R_1$ | $7,112,994$ | $\$4.07$ | $\$0.61$ | $\$4.68$ |
   | **Trial 1 — Run 2** | $R_2$ | $7,268,129$ | $\$4.50$ | $\$0.66$ | $\$5.16$ |
   | **Trial 2 — Run 1** | $R_3$ | $7,653,826$ | $\$5.16$ | $\$0.60$ | $\$5.76$ |
   | **Trial 2 — Run 2** | $R_4$ | $7,763,225$ | $\$5.36$ | $\$0.64$ | $\$6.01$ |
   | **Four-Run Aggregate** | *Mean per execution* | **$7,449,544$** | **$\$4.77$** ($88.3\%$) | **$\$0.63$** ($11.7\%$) | **$\$5.40$** (Range: $\$4.68\text{--}\$6.01$) |

   Across our longitudinal benchmark runs, total cloud inference expenditure averaged **$\$5.40$ per complete audited document** (utilizing Gemini 3.8 Flash via Vertex AI pricing, with $\$4.77$ allocated to Kahn-wave DAG micro-atom verification and $\$0.63$ to Phase 2 multi-profile executive synthesis and reporting). In production environments, Quorum's Four-Layer Clean Stack achieves $>95\%$ KV prefix cache hit rates, substantially compressing input token charges below standard list rates.

   **Enterprise Cost-Benefit Equation:**  
   In enterprise compliance governance (such as EU AI Act Articles 12–15 auditability, corporate board oversight, ESG compliance, and legal discovery), engaging certified human auditors or compliance consultants to manually evaluate $305$ technical criteria across corporate evidence costs between $\$150$ and $\$500+$ per billable hour, typically consuming $8$ to $24$ hours ($\$1,200$ to $\$6,000+$ per audited document)—while human inter-annotator reliability often stagnates at $\kappa = 0.65\text{--}0.80$. A computational cost of **$\sim \$5.40$ per document** represents an approximate **$99.5\%$ reduction in audit expenditure**, while simultaneously achieving superior inter-run determinism ($\bar{\kappa} = 0.9245$) and $100.0\%$ verifiable lexical grounding. 

   We therefore explicitly articulate this as a **Pareto efficiency trade-off**: Quorum is not designed for token-frugal exploratory chat queries, but rather as an industrial epistemic firewall for high-liability corporate compliance. Crucially, as demonstrated in Section 4.5, brute-force token amplification alone is insufficient to achieve determinism: Baseline 3 scaled compute to $1.25\text{M}$ tokens yet still suffered from an $8.20\%$ hallucination rate. The superior epistemic stability of Quorum is an emergent property of the seven runtime verification gates converting computational redundancy into invariant decision states.
2. **Synchronization Barriers and Head-of-Line Blocking:** Kahn's wave scheduling algorithm partitions the graph into $K$ sequential topological waves ($\mathcal{W}_1 \to \mathcal{W}_K$). Although atoms within wave $\mathcal{W}_k$ execute concurrently via non-blocking coroutine task groups, wave completion is strictly bounded by its slowest node:
   $$T(\mathcal{W}_k) = \max_{a_i \in \mathcal{W}_k} t_{\text{inference}}(a_i) + \tau_{\text{overhead}}$$
   A single transient latency spike or provider retry (HTTP 429 backoff) stalls the entire dependent wave frontier (Dean & Barroso, 2013).
3. **Provider Pacing Overhead:** Enterprise quota compliance requires rate-limiting pacing delays ($\tau_{\text{pacing}} = 4.0\text{s}$) and strict micro-concurrency semaphores ($\text{MAX\_CONCURRENT\_LLM\_STEPS} = 3$), resulting in total execution durations of **15 to 30 minutes** for a comprehensive 305-atom graph. This establishes Quorum as an **asynchronous batch governance and auditing system** that cannot support sub-second interactive user conversational loops.

#### **5.3 Asymmetric False-Negative Attractor ($H_0$ Bias)**

Grounding runtime verification in Popperian falsification establishes the Null Hypothesis ($H_0$) as an asymmetric attractor. The system formalizes an asymmetric error cost matrix:
$$C_{\text{False Positive}} \gg C_{\text{False Negative}}$$
A hallucinated positive compliance finding exposes an enterprise to legal, regulatory, and audit liabilities. In contrast, failing to verify an authentic but ambiguously phrased assertion is transparent and safe.

However, this mathematical bias guarantees an elevated **empirical false-negative rate** ($P(\text{False Negative}) > 0$). When source documents exhibit fragmented drafting, when Condorcet replicas fail to achieve a $2/3$ majority consensus, or when network timeouts exhaust the adaptive retry horizon ($\text{MAX\_RETRIES} = 2$), the atom transitions unconditionally to $H_0 \to \text{N\_A}$. In enterprise audits, authentic compliance patterns may be classified as unverified due to drafting ambiguity rather than actual non-compliance.

#### **5.4 Ontological Knowledge Engineering and Cold-Start Overhead**

Unlike monolithic models that evaluate prompts without domain preparation, Quorum requires substantial upfront ontological engineering before execution:
1. Decomposing domain standards into discrete evaluation atoms ($\mathcal{A}$).
2. Formulating causal dependency edges ($\mathcal{E}$) and expected outcome preconditions ($s_{\text{expected}}$).
3. Authoring contrastive acceptance criteria and explicit negative anti-patterns ($\mathcal{C}(a_i) = \langle C_{\text{pos}}, C_{\text{anti}} \rangle$).
4. Compiling mandatory syntactic anchors ($\Omega(a_i)$) for pre-flight filtering.

This "Knowledge Engineering Tax" requires multi-disciplinary collaboration between domain legal experts and systems engineers. While this formalization guarantees audit reproducibility, it precludes zero-shot deployment on unmodeled, novel regulatory domains.

#### **5.5 Variance Clustering in High-Order Dialectical Synthesis (The Abstraction-Entropy Gradient)**

Empirical analysis across our longitudinal replication trials revealed a marked non-uniformity in the distribution of epistemic entropy across matrix evaluation blocks. Crucially, all evaluation matrices utilized in our empirical benchmark—such as Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001) or Toulmin Argumentation (Toulmin, 1958)—function strictly as exemplary domain schemas, demonstrating how complex ontologies map into the verification harness. Rather than dispersing uniformly across all 305 atoms, **$50.0\%$ of all observed discrepancies in Trial 2 ($6$ out of $12$) concentrated within a single high-order matrix block evaluating Dialectical Evaluation & Synthesis**, where inter-run consistency dropped to $80.0\%$ and macro score drift reached $-28.7$ points.

Qualitative autopsy of the unstable evaluation atoms within this cluster (specifically the micro-atoms evaluating multi-criteria compromise balancing, abstract theory application, and dialectical tension documentation) yielded three critical architectural lessons:

1. **Speaker Attribution Ambiguity in Multi-Turn Dialogues:** When evaluating multi-turn conversational corpora, high-abstraction atoms requiring the model to verify whether *"the evaluated text demonstrates multi-dimensional trade-off balancing"* suffer from target entity ambiguity unless strictly scoped. In Run 3 ($R_3$), the extractor anchored to the machine assistant's synthetic compromise proposal, successfully passing the atom; in Run 4 ($R_4$), the extractor evaluated whether the human user authored this trade-off, correctly failing the atom because the user merely posed questions. This demonstrates that multi-turn corporate transcripts require **explicit speaker attribution constraints** at the atomic prompt layer (such as specifying explicit speaker role scoping: assistant, user, or aggregate) to prevent retrieval span divergence.
2. **The Abstraction-Entropy Gradient and Matrix-Agnostic Generality:** Across all four production runs, low-to-mid abstraction atoms (syntactic presence, baseline factual assertions, discrete operational thresholds) exhibited near-zero entropy ($98\%\text{--}100\%$ consistency across 7 of the 13 matrix blocks). Epistemic entropy concentrates almost exclusively at the apex of hierarchical cognitive matrices—such as the synthesis and evaluation tiers in our illustrative Bloom-based matrix—where semantic boundaries in natural language are inherently continuous rather than discrete. It is essential to underscore that **the Quorum engine is fundamentally matrix-agnostic**: whether instantiated over educational taxonomies, statutory auditing codes, or corporate risk matrices, the system treats all matrices as interchangeable ontologies. This boundary phenomenon directly confirms the necessity of the Epistemic Regularity conditions formalized in Definition 3: when semantic polytopes lack linear separability ($\text{dist}(\mathcal{E}(C_{\text{pos}}), \mathcal{E}(C_{\text{anti}})) \le \epsilon$) or speaker attribution is unanchored, atoms deviate from $\mathcal{A}_{\text{reg}}$, necessitating heightened prompt-level grounding to preserve the vanishing reasoning gap guaranteed by Theorem 2.
3. **Dynamics of Inverse Contextual Overrides:** In Trial 2, both Contextual Overrides occurred within the Critical Neutrality & Epistemic Grounding matrix block (evaluating critical neutrality and absence of ornamental citations, where an inverse assertion is enforced). In these atoms, neither run extracted a quote, but one run triggered an override based on whether a referenced academic citation was judged functionally integrated rather than ornamental. This highlights that inverse evaluation criteria (asserting the *absence* of an epistemic defect) require heightened contrastive exemplar conditioning to prevent boundary oscillation around the Null Hypothesis attractor.

#### **5.6 Empirical Scope: Single-Model Baseline and Single-Corpus Boundaries (Future Cross-Family and Open-Weight Generalization)**

A foundational methodological boundary of the empirical findings reported in this paper concerns the operational scope of the evaluation substrate:

1. **Single Foundation Model Validation (Gemini 3.8 Flash):** All reported longitudinal replication trials ($29.8\text{M}$ tokens across four production runs) were executed exclusively against a single, high-capability frontier foundation model: Google DeepMind's Gemini 3.8 Flash via Vertex AI. While this model demonstrates state-of-the-art instruction adherence, long-context window stability, and robust JSON Schema compliance under grammar-constrained decoding, our formal guarantees have not yet been empirically cross-validated across heterogeneous model families. Foundation models with differing pre-training topologies, smaller parameter envelopes, or less resilient structured output decoders may exhibit higher rates of Dead Letter Queue (DLQ) rejections at Gate 6 or necessitate larger Condorcet ensemble cardinalities ($M > 3$) in Gate 5 to resolve high-entropy evaluations.
2. **Single Enterprise Corpus Validation:** Empirical stress-testing was conducted across a single authentic, multi-channel enterprise audit corpus ($305$ atoms evaluated over five heterogeneous artifacts including multi-turn conversational logs, machine transcripts, tangible product deliverables, and meta-cognitive reflections). While this corpus provides dense conversational dynamics and complex contextual trade-offs, it represents a single corporate domain with localized communicative structures. Empirical generalizability across disparate corporate corpora—such as formal commercial contracts, statutory regulatory filings (e.g., CSRD, SEC disclosures), medical documentation, or safety-critical engineering specifications—remains to be formally characterized.
3. **Roadmap for Cross-Family and Open-Weight Cross-Validation:** Future work will systematically expand the Quorum verification harness across three primary axes:
   - **Cross-Family Frontier Model Benchmarking:** Replicating the longitudinal metamorphic testing protocol across competing proprietary foundation model families (including Anthropic Claude and OpenAI GPT series).
   - **Open-Weights Model Validation:** Evaluating the efficacy of the zero-permissive software vessel when driving open-weights architectures (specifically Meta Llama 3.1/3.3, Mistral Large, and DeepSeek V3) into an epistemic corner. This investigation will specifically establish whether local inference engines (e.g., vLLM, SGLang) coupled with hardware-level grammar-constrained decoding (e.g., Outlines, XGrammar) can match the $0.0\%$ internal reasoning gap and $100.0\%$ lexical grounding achieved by commercial cloud APIs.
   - **Multi-Domain Corpus Cross-Validation:** Subjecting the seven runtime verification gates to diverse, multi-industry corporate corpora and standardized legal/compliance benchmarks to formally establish domain-invariant reliability bounds.

---

### **6. Conclusion & Enterprise Governance Impact**

This paper demonstrates that foundational Large Language Models can achieve audit-grade epistemic determinism without computationally expensive weight fine-tuning ($\nabla \mathcal{L} = 0$). By subverting stochastic autoregression and constraining token generators within an external Systems Engineering harness governed by formal runtime verification gates, the Quorum architecture achieves:

1. **Mathematical Causality:** Enforcing Kahn wave-level DAG scheduling under the Local Causal Markov Condition with static graph acyclicity verification and deterministic causal short-circuiting with complete downstream inference bypass.
2. **Zero-Permissive Type Safety:** Eliminating syntax hallucinations via dynamic runtime schema compilation ($\mathcal{V}_{\text{struct}} \in \{0, 1\}$) and Dead Letter Queue isolation.
3. **Consensus & Contrastive Rigor:** Resolving high-entropy evaluations through Condorcet Best-of-Three ensemble voting with Null Hypothesis tie-breaking, bound by contrastive acceptance and anti-pattern criteria.
4. **Provable Lexical Anchoring:** Masking unverified citations via discrete software contracts ($\mathbf{s} \odot \mathbf{v}$) with multi-tier entropy gating under the Popperian Null Hypothesis.
5. **Non-Attenuating Evidentiary Integrity:** Preserving verified states through an immutable, isomorphic projection ($\mathcal{R}: \mathcal{S}_{\text{DAG}} \to \mathcal{V}_{\text{audit}}$) that strictly prohibits downstream heuristic patching, statistical imputation, or default fallbacks.
6. **Attention & Cache Optimization:** Compressing identifiers via the attention alias subsystem and achieving $>95\%$ KV cache reuse in production.

With an empirical longitudinal Fleiss' Kappa of $\bar{\kappa} = 0.9245$ across nearly $30\text{M}$ tokens ($198/198$ verified quotes, zero admitted hallucinations) and a replicated internal reasoning gap of $0.0\%$, this framework demonstrates that determinism in generative AI is not an intrinsic neural property, but an architectural achievement. By driving stochastic foundation models into an unyielding deterministic corner, Quorum shifts generative AI from an unpredictable probabilistic art into a verifiable, Computer-Implemented engineering discipline capable of satisfying the stringent auditability, accuracy, and transparency mandates of the European Union Artificial Intelligence Act (Articles 12–15).

---

### **References**

> 1. Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.  
> 2. Popper, K. (1959). *The Logic of Scientific Discovery*. Hutchinson.  
> 3. Toulmin, S. E. (1958). *The Uses of Argument*. Cambridge University Press.  
> 4. Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.  
> 5. Kahn, A. B. (1962). "Topological sorting of large networks." *Communications of the ACM*, 5(11), 558–562.  
> 6. Tarjan, R. (1972). "Depth-first search and linear graph algorithms." *SIAM Journal on Computing*, 1(2), 146–160.  
> 7. Fleiss, J. L. (1971). "Measuring nominal scale agreement among many raters." *Psychological Bulletin*, 76(5), 378–382.  
> 8. Shannon, C. E. (1948). "A mathematical theory of communication." *The Bell System Technical Journal*, 27(3), 379–423.  
> 9. Condorcet, M. de. (1785). *Essai sur l'application de l'analyse à la probabilité des décisions rendues à la pluralité des voix*. Imprimerie Royale.  
> 10. Meyer, B. (1992). "Applying 'Design by Contract'." *Computer*, 25(10), 40–51.  
> 11. van Fraassen, B. C. (1980). *The Scientific Image*. Oxford University Press.  
> 12. Miller, T. (2019). "Explanation in artificial intelligence: Insights from the social sciences." *Artificial Intelligence*, 267, 1–38.  
> 13. European Parliament. (2024). *Artificial Intelligence Act* (Regulation (EU) 2024/1689). Official Journal of the European Union.  
> 14. Zheng, L., Chiang, W. L., Sheng, Y., Tian, S., Wang, H., Zhuang, C., Peng, S., Xing, E. P., Gonzalez, J. E., & Stoica, I. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." *Advances in Neural Information Processing Systems*, 36, 46595–46623.  
> 15. Wang, J., Liang, Y., Meng, F., Shi, H., Li, Z., Xu, J., Qu, J., & Zhou, J. (2023). "Is ChatGPT a Good NLG Evaluator? A Preliminary Study." *arXiv preprint arXiv:2303.04048*.  
> 16. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). "Lost in the middle: How language models use long contexts." *Transactions of the Association for Computational Linguistics*, 12, 157–173.  
> 17. Kryściński, W., McCann, B., Xiong, C., & Socher, R. (2020). "Evaluating the factual consistency of abstractive text summarization." *Transactions of the Association for Computational Linguistics*, 8, 933–946.  
> 18. Dean, J., & Barroso, L. A. (2013). "The tail at scale." *Communications of the ACM*, 56(2), 74–80.  
> 19. Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?" *Proceedings of the 2021 ACM FAccT Conference*, 610–623.  
> 20. Kambhampati, S., Valmeekam, K., Guan, L., Stechly, K., Verma, M., Bhambri, S., Saldanha, L., & Murthy, R. (2024). "LLMs Can't Plan, But Can Help Us Plan in an LLM-Modulo Framework." *Communications of the ACM* (arXiv:2402.01817).  
> 21. Marcus, G. (2020). "The Next Decades in AI: Four Steps Towards Robust Artificial Intelligence." *arXiv preprint arXiv:2002.06177*.  
> 22. Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.  
> 23. Dziri, N., Lu, X., Sanyal, S., Yu, K., Zhou, X., Yan, F., Zhang, H., Liu, W., Yatskar, M., & Hajishirzi, H. (2023). "Faith and Fate: Limits of Transformers on Compositional Problems." *Advances in Neural Information Processing Systems (NeurIPS 2023)*, 36.  
> 24. De Giacomo, G., Favorito, M., Iocchi, L., & Patrizi, F. (2020). "Foundations for Restraining Bolts: Reinforcement Learning with LTLf/LDLf Restraining Specifications." *Proceedings of the International Conference on Automated Planning and Scheduling (ICAPS)*, 30(1), 128–136.  
> 25. Willard, B. T., & Louf, R. (2023). "Efficient Guided Generation for Large Language Models." *arXiv preprint arXiv:2307.09702*.  
> 26. Scholak, T., Schucher, N., & Bahdanau, D. (2021). "PICARD: Parsing Incrementally for Constrained Auto-regressive Decoding from Language Models." *Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 9895–9901.  
> 27. Clark, A., & Chalmers, D. (1998). "The Extended Mind." *Analysis*, 58(1), 7–19.  
> 28. Rushby, J. (2001). "Runtime Certification." *Reliable Software Technologies — Ada-Europe 2001*, Lecture Notes in Computer Science, 2043, 249–265.  
> 29. Google DeepMind. (2026). "Gemini 3.8 Flash Model Card." Google DeepMind. Available: https://deepmind.google/models/model-cards/gemini-3-8-flash/  
> 30. Sapir, E. (1921). *Language: An Introduction to the Study of Speech*. Harcourt, Brace and Company.  
> 31. Greenberg, J. H. (1960). "A quantitative approach to the morphological typology of language." *International Journal of American Linguistics*, 26(3), 178–194.  
> 32. Comrie, B. (1989). *Language Universals and Linguistic Typology: Syntax and Morphology* (2nd ed.). University of Chicago Press.  
> 33. Karlsson, F. (1983). *Finnish Grammar*. Werner Söderström Osakeyhtiö.