# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 182
- Total mismatching atoms: 19
- Variance percentage: 10.4 %
- PASSED -> FAILED (Run 1 -> Run 2): 8
- FAILED -> PASSED (Run 1 -> Run 2): 11
- Other state changes: 0

## Atom: tda_d46093a71bbbcd79
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from 'ai:' output blocks. STEP 1 (Syntactic Anchor): Find affirmative acceptance phrases by the user (e.g., 'looks good', 'thanks', 'perfect'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user accepts an AI output without requesting a single structural or logical change. NEGATIVE CONDITION (RETURN NULL IF MET): the user requests a modification. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate if the response was actually 'good'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_247927c98b0c46f8
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_0871942d6add46f1
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find contrast markers ('however, data shows that', 'despite X, metric Y'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a specific counter-argument is addressed using empirical counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): it's dismissed rhetorically. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rhetorical dismissals without data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_8f668ea29869ba8b
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_6be555cac0b9115b
**Rule:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_5cff62a0ae1e41d3
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find weak associative language ('relates to', 'is associated with', 'impacts'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it connects Data to a Claim without defining the exact causal mechanism. NEGATIVE CONDITION (RETURN NULL IF MET): it uses precise causal mechanism ('which directly causes'). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Precise causal mechanisms. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_47219840710895f0
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit reasoning markers by the user (e.g., 'I am challenging this because', 'the reason this is wrong is'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly documents the 'why' behind their challenge to the AI. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unreasoned rejections ('this is bad'). TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_4956abf072945f43
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Syntactic Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context. NEGATIVE CONDITION (RETURN NULL IF MET): the alternative is dismissed without evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_d335b4457e3e4ac7
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find thought-terminating clichés ('it is simply a matter of', 'there is no alternative', 'period'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: complexity or opposing views are dismissed without data. NEGATIVE CONDITION (RETURN NULL IF MET): data is provided. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Data-driven rebuttals. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_92af590371ba4f3d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'thoughtfulness'. STEP 1 (Syntactic Anchor): Find dialectical markers (e.g., 'While X is true, Y proves', 'Reconciling these', 'Toisaalta'). STEP 2: EXTRACTION CONDITION: the text explicitly introduces two opposing variables and generates a third, novel conclusion (synthesis) rather than just picking one. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_c45a513f2e724e06
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_d0b6789c895808eb
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find binary reduction words (e.g., 'either', 'or', 'simply boils down to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a complex phenomenon is reduced to a strict binary choice without acknowledging nuance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept binary choices in literal boolean logic or code. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_04a1f24c02e6dba2
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Locate a section dedicated to methodology or limitations. STEP 2: Find at least three distinct listed data gaps or foundational assumptions. Document them step-by-step. EXTRACTION CONDITION: 3 or more exist. NEGATIVE CONDITION (RETURN NULL IF MET): less than 3. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_05dfe1f129dc4488
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields or instructions. STEP 1 (Syntactic Anchor): Find dogmatic absolute markers ('is the best', 'must be done', 'is the only way'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. EXTRACTION CONDITION: no empirical data or external reference exists in the same paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): data exists. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate if the data is 'good', only its physical presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_7cdd3652e248e6a9
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find tension markers between metrics and goals (e.g., 'this metric is flawed because', 'we need to ensure this actually works'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly questions the reliability of a proxy metric in relation to the ultimate qualitative goal. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept simple metric tracking. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

## Atom: tda_653b3f5497b9147e
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find explicit external anchoring for uncertainty (e.g., 'due to X, as noted by [Source]'). STEP 2: Map the cognitive friction. EXTRACTION CONDITION: an external citation is used specifically to justify why a variable remains unknown. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_3d3f1162d2ff1558
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a limitation acknowledgment (e.g., 'a limitation is'). STEP 2: Scan the next two sentences. EXTRACTION CONDITION: a dismissive marker (e.g., 'however', 'regardless') immediately rationalizes away the limitation without citing new data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_c74c4367acc028cf
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly adopts the AI's proposed framework without adding their own constraints. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user modifies the AI's framework. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> 

**Run 2 [false]**
> 

---

## Atom: tda_e6a0c9d3eb6c443f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find dialectical reasoning markers ('One might argue that X, but testing showed Y because'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the author explicitly attempts to falsify their own Claim with a test/data before accepting it. NEGATIVE CONDITION (RETURN NULL IF MET): it is just a pros/cons list. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Simple pros/cons lists. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> 

**Run 2 [true]**
> 

---

