# 03 Knowledge Update Plan

Source: Epic Phase 5

## 1. Goal Description & Background
The objective of this plan is to fulfill Phase 5 of EPIC 118: Dual-Axis Documentation Update. We will create a new Knowledge Item (KI) that documents the **Context-Enriched Decompose-Verify** architectural pattern.

## 2. Proposed Changes

### Knowledge Base (KI) Update

#### [NEW] `ki_context_enriched_decompose_verify.md`
**Path:** `<appDataDir>\knowledge\context_enriched_pipeline\artifacts\ki_context_enriched_decompose_verify.md`

**Action:** 
Create a new KI that describes the dual-path (Matrix vs Regular) pipeline architecture:
1. Phase 0/1 for extracting ontology
2. Preserving original `tda_id` UUIDs
3. `EnrichedDagExecutor` evaluating against the generated `full_context`.
The KI MUST reference `provider_agnostic_caching` (cache survival) and `opaque_id_hydration` (atom aliasing).

```xml
<execution_block phase="phase_5" consumer="tier2-execute">
  <summary><![CDATA[Dual-Axis Documentation Update (EPIC 115 Compliance)]]></summary>
  <step id="phase_5.1" scope="NEW">
    <action>Create a new Knowledge Item (KI) documenting the **Context-Enriched Decompose-Verify** architectural pattern. Create `ki_context_enriched_decompose_verify.md` in the knowledge directory artifacts. Describe the pipeline: Phase 0/1 for extracting ontology → preserving original `tda_id` UUIDs → `EnrichedDagExecutor` evaluating against the generated `full_context`. Do NOT manually edit `docs/architecture/` pillars. Instruct the user to run `/tier7-describe-architecture` after KI creation to synchronize.</action>
    <target>Knowledge Item artifact directory</target>
    <invariants>
      <must>KI documents the dual-path (Matrix vs Regular) pipeline architecture</must>
      <must>KI references provider_agnostic_caching and opaque_id_hydration KIs</must>
      <forbidden>Direct edits to docs/architecture/ pillar documents</forbidden>
    </invariants>
    <tests min_negative="0"/>
  </step>
</execution_block>
```

## 3. Verification Plan
- Verify that the KI file is created in the correct artifact directory and respects the standard XML-wrapped schema (`<domain_boundary>`, `<architectural_invariants>`, etc.).
- **IMPORTANT**: Instruct the user to run `/tier7-describe-architecture` after KI creation to synchronize this structural change into the human-readable architectural narratives in `docs/architecture/`.
