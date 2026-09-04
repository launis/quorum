# Matrix Theory Explanations Compendium

Architectural reference documenting theoretical grounding, steering controls, and context target input justifications for all Quorum evaluation matrices.

---

## Canonical Matrix & Context Target Overview

Every evaluation matrix is anchored in a rigorous academic theory and bound to a specific cognitive evidence target (`product_text`, `chat_log`, or `all`), strictly enforced via its permanent Opaque Stripe ID (`blk_...`).

| Opaque Stripe ID | Matrix Name | Academic Grounding | Target Input | Override Allowed | Primary Evaluative Focus |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `blk_440a5fef9331451b` | **Toulmin Argumentation Model** | Toulmin (1958) | `product_text` | **Yes** | Evidentiary backing, warrants, and rebuttals in final claims |
| `blk_f921c7c0989b47e8` | **Bloom's Taxonomy** | Bloom (1956) | `product_text` | **Yes** | Cognitive depth, critical synthesis, and conceptual creation |
| `blk_c5804a9143c34cb1` | **Causal Inference Audit** | Pearl (2009) | `product_text` | No | Robustness of causal claims (Association vs. Intervention) |
| `blk_53f32679aa514fcb` | **Performativity & Goodhart's Law** | Goodhart (1975) | `chat_log` | **Yes** | Active steering, prompt discipline, and resistance to AI sycophancy |
| `blk_ff72c2d79edb4ebf` | **Supreme Adjudicator** | Deming (1986) | `chat_log` | No | Human executive command, accountability, and process ownership |
| `blk_109dab5b6b3f403a` | **Kahneman's Dual Process Theory** | Kahneman (2011) | `all` | **Yes** | Balance of System 1 heuristic speed vs. System 2 deliberation |
| `blk_b476f89fb732448c` | **Falsification Audit** | Popper (1963) | `all` | No | Active attempts to refute hypotheses and expose flaws |
| `blk_fb15f8dcf23f4865` | **Archival Compliance Audit** | ARMA (2014) | `all` | No | Information fidelity, source citation, and fact preservation |
| `blk_80732a33fe1947ee` | **Responsibility (Taskguard)** | OWASP (2023) | `all` | No | Mandate boundaries, ethical adherence, and safety limits |
| `blk_c3bc5f3eb8e74110` | **Causal & Abductive Integrity** | Pearl & Mackenzie (2018) | `all` | No | Anti-rationalization audit; exposes post-hoc justification |
| `blk_f6e286f050c94d60` | **Explainability & Transparency** | Lipton (2018) | `all` | No | Third-party followability and clear chain of reasoning |
| `blk_22e3598e06414409` | **Epistemic Humility** | Tetlock (2005) | `all` | No | Open acknowledgment of data boundaries and uncertainties |
| `blk_6b8c766185294f7e` | **XAI Synthesis Reporter** | Lundberg & Lee (2017) | `all` | No | Global internal consistency across multi-specialist evaluations |

---

## Detailed Matrix Profiles & Input Justifications

### Toulmin Argumentation Model
- **Opaque Stripe ID:** `blk_440a5fef9331451b`
- **Evaluation Target:** `product_text` (Deliverable Only)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `True`

The Toulmin Argumentation Model evaluation matrix is mathematically grounded in Toulmin, S. E. (1958). *The Uses of Argument*. Cambridge University Press. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=True`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `product_text`:** Toulmin evaluates the structural validity of claims, warrants, backings, and rebuttals. In decision-making and business workflows, external stakeholders and executives read and act exclusively upon the final deliverable. The deliverable must stand on its own evidentiary merits regardless of earlier drafting stages.
- **Why other inputs would corrupt assessment:** Evaluating conversational chat logs would severely penalize creative brainstorming. Dialogue naturally involves exploratory inquiries, informal conjecture, and unbacked trial ideas. Penalizing incomplete logic in chat would punish users for uninhibited collaborative brainstorming with the AI.

---

### Bloom's Taxonomy
- **Opaque Stripe ID:** `blk_f921c7c0989b47e8`
- **Evaluation Target:** `product_text` (Deliverable Only)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `True`

The Bloom's Taxonomy evaluation matrix is mathematically grounded in Bloom, B. S. (Ed.). (1956). *Taxonomy of Educational Objectives: The Classification of Educational Goals. Handbook I: Cognitive Domain*. David McKay Company. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=True`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `product_text`:** Bloom evaluates the level of cognitive processing materialized in the final work: distinguishing low-level recall and summarization from high-level critical evaluation, synthesis, and novel framework creation. This cognitive value is crystallized in the deliverable.
- **Why other inputs would corrupt assessment:** Operators routinely use chat for administrative, low-order tasks (e.g., "reformat this list", "check spelling", "summarize section B"). Mixing chat into the Bloom evaluation would artificially depress the score of a high-level strategic report simply because routine mechanical prompts were utilized during production.

---

### Kahneman's Dual Process Theory
- **Opaque Stripe ID:** `blk_109dab5b6b3f403a`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 3 | **Contextual Override Permitted:** `True`

The Kahneman's Dual Process Theory evaluation matrix is mathematically grounded in Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 3, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=True`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Kahneman's dual-process model diagnoses cognitive operational mode: fast, intuitive heuristics (System 1: confirmation bias, anchoring, availability bias) versus deliberate, critical scrutiny (System 2). Profiling cognitive habits requires trajectory-wide visibility: Did an initial prompt exhibit intuitive bias? Did subsequent analytical work correct it in the deliverable? Does the operator demonstrate meta-cognitive awareness of their cognitive tendencies in the reflection?
- **Why a single input is insufficient:** A polished deliverable alone cannot reveal whether a sound conclusion was achieved through methodical scrutiny or serendipitous guessing. Chat logs alone cannot prove whether intuitive heuristics were subsequently refined. Comparing all three reveals the authentic cognitive profile.

---

### Performativity & Goodhart's Law
- **Opaque Stripe ID:** `blk_53f32679aa514fcb`
- **Evaluation Target:** `chat_log` (Process Dialogue Only)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `True`

The Performativity & Goodhart's Law evaluation matrix is mathematically grounded in Goodhart, C. A. E. (1975). *Problems of Monetary Management: The U.K. Experience*. Papers in Political Economy. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=True`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `chat_log`:** Goodhart evaluates human-AI interaction dynamics: whether the operator acted as an active, critical driver or a passive passenger, and whether the operator coerced the AI into sycophantic agreement rather than seeking objective truth. This behavioral pattern exists exclusively in prompt phrasing (`user:` messages).
- **Why other inputs would corrupt assessment:** The final deliverable completely obscures how it was created. A flawless deliverable can be produced by a user who passively accepted a single AI response without oversight. Evaluating prompt leadership from deliverable text is an epistemological impossibility.

---

### Archival Compliance Audit
- **Opaque Stripe ID:** `blk_fb15f8dcf23f4865`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Archival Compliance Audit evaluation matrix is mathematically grounded in ARMA International. (2014). *Generally Accepted Recordkeeping Principles*. ARMA International. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Archival compliance measures information preservation and source fidelity across workflow stages: Did verified facts and empirical citations established in research survive intact into the deliverable without distortion, dilution, or hallucinated mutations?
- **Why a single input is insufficient:** Informational degradation ("the telephone game") is intrinsically a relational measurement between source data, dialogue iterations, and final output. Detecting factual mutation mathematically requires cross-referencing input streams against the deliverable.

---

### Causal Inference & Abductive Reasoning Audit
- **Opaque Stripe ID:** `blk_c5804a9143c34cb1`
- **Evaluation Target:** `product_text` (Deliverable Only)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Causal Inference & Abductive Reasoning Audit evaluation matrix is mathematically grounded in Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `product_text`:** Evaluates structural causal assertions against Pearl's ladder: distinguishing mere statistical association from actual intervention and counterfactual impact. Executive resource allocation and strategic commitments depend directly upon the explicit causal models stated in the final deliverable.
- **Why other inputs would corrupt assessment:** During brainstorming, operators often pose speculative causal questions ("Could market trend X be causing customer behavior Y?"). Exploratory questions in dialogue must not penalize the evaluation if unverified causal leaps were pruned before final publication.

---

### Falsification Audit
- **Opaque Stripe ID:** `blk_b476f89fb732448c`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 4 | **Contextual Override Permitted:** `False`

The Falsification Audit evaluation matrix is mathematically grounded in Popper, K. (1963). *Conjectures and Refutations: The Growth of Scientific Knowledge*. Routledge. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 4, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Popperian falsification measures active vulnerability testing: seeking evidence to refute one's own assumptions rather than hunting for confirming evidence. Genuine falsification is a trajectory: counterarguments raised in chat are addressed in the deliverable, and residual vulnerabilities are acknowledged in the reflection.
- **Why a single input is insufficient:** A deliverable can easily feature an artificial "limitations" section that is merely rhetorical window-dressing. Only by cross-examining dialogue challenges and reflective honesty can the engine determine whether hypotheses were genuinely stress-tested.

---

### Supreme Adjudicator
- **Opaque Stripe ID:** `blk_ff72c2d79edb4ebf`
- **Evaluation Target:** `chat_log` (Process Dialogue Only)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Supreme Adjudicator evaluation matrix is mathematically grounded in Deming, W. E. (1986). *Out of the Crisis*. MIT Center for Advanced Engineering Study. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `chat_log`:** Measures process ownership and executive command: Did the human operator retain sovereign command of the analytical process, enforcing standards and correcting errors, or did they abdicate intellectual control to the AI?
- **Why other inputs would corrupt assessment:** Evaluating the deliverable measures the AI's generation quality, not the human's governance. Executive ownership is demonstrated exclusively in how the human directs, critiques, and steers the system during interaction.

---

### Responsibility (Taskguard)
- **Opaque Stripe ID:** `blk_80732a33fe1947ee`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Responsibility evaluation matrix is mathematically grounded in OWASP Foundation. (2023). *OWASP Top 10 for Large Language Model Applications*. OWASP. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Taskguard enforces mandate boundaries, safety limits, and ethical compliance. It verifies that the analysis remained focused on its authorized mandate without straying into unverified, hazardous, or policy-violating domains.
- **Why a single input is insufficient:** Violations can occur at any stage: prompt injections in dialogue, unauthorized assertions in deliverables, or rationalized boundary violations in reflection. Total lifecycle monitoring prevents security and mandate leakage.

---

### XAI Synthesis Reporter
- **Opaque Stripe ID:** `blk_6b8c766185294f7e`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 3 | **Contextual Override Permitted:** `False`

The XAI Synthesis Reporter evaluation matrix is mathematically grounded in Lundberg, S. M., & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. *Advances in Neural Information Processing Systems, 30*. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 3, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Evaluates the internal harmony and structural coherence across the entire analytical pipeline. It detects contradictions between raw inputs, multi-specialist evaluations, and final recommendations.
- **Why a single input is insufficient:** Synthesis coherence cannot be measured on an isolated text slice. It is inherently a global property evaluating the mathematical and semantic alignment across all pipeline elements.

---

### Explainability & Transparency
- **Opaque Stripe ID:** `blk_f6e286f050c94d60`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Explainability & Transparency evaluation matrix is mathematically grounded in Lipton, Z. C. (2018). The Mythos of Model Interpretability. *Communications of the ACM*, 61(10), 36-43. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Evaluates whether conclusions are auditable and reconstructible by an independent auditor: Can a third party trace the logical journey from original mandate through intermediate debate to final recommendations?
- **Why a single input is insufficient:** A clear deliverable whose research trail, data sources, and conversational iterations are hidden remains an opaque black box. True transparency requires an unbroken, auditable chain of reasoning.

---

### Causal & Abductive Integrity
- **Opaque Stripe ID:** `blk_c3bc5f3eb8e74110`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Causal & Abductive Integrity evaluation matrix is mathematically grounded in Pearl, J., & Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*. Basic Books. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Exposes post-hoc rationalizations where conclusions were predetermined prior to inquiry and supporting arguments were retrospectively fabricated to justify preconceived convictions.
- **Why a single input is insufficient:** Post-hoc rationalization is an asymmetrical temporal defect. It can only be detected by comparing the chronology of chat dialogue against the deliverable: if the conclusion was locked early in chat before supporting data was examined, retrospective rationalization is conclusively proven.

---

### Epistemic Humility
- **Opaque Stripe ID:** `blk_22e3598e06414409`
- **Evaluation Target:** `all` (Holistic Multi-Input Trajectory)
- **BARS Levels:** 1 to 5 | **Contextual Override Permitted:** `False`

The Epistemic Humility evaluation matrix is mathematically grounded in Tetlock, P. E. (2005). *Expert Political Judgment: How Good Is It? How Can We Know?* Princeton University Press. It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards across analytical tasks.

Operationally, the matrix controls evaluation precision through targeted parameters including contextual override permissions (`allow_contextual_override=False`) and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict distinction between universal structural invariants requiring chunk compliance and specialized existential error radars.

**Context Target & Epistemic Justification:**
- **Why `all`:** Measures the open acknowledgment of contextual boundaries, missing data, and intrinsic uncertainties. Rewards prudent hedging and penalizes ungrounded epistemic certainty.
- **Why a single input is insufficient:** Authors frequently insert polite hedges into deliverables while displaying aggressive dogmatism in conversational prompts or uncritical hubris in reflection. Authentic epistemic humility requires consistent intellectual modesty across all three touchpoints.
