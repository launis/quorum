### Input Processing (`step_input_processing`)
- **Current Strategy**: `fast`
- **Description**: Parses files and raw text into standard variables.
- **Hooks**: inject_step_metadata, detect_performative_patterns, normalize_matrix_scores

### Analyst (`sp_1624bd0454c9425e`)
- **Current Strategy**: `reasoning`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: calculate_text_metrics, calculate_control_ratio, inject_step_metadata, atom_flattening_hook, verify_citation_integrity, enforce_hypothesis_linking, matrix_scoring_hook, normalize_matrix_scores

### Archivist (`sp_2a81cb9e3e4b4694`)
- **Current Strategy**: `fast`
- **Description**: Best Practices Audit
- **Hooks**: retrieve_precedent, inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Causal Analyst (`step_causal_analyst`)
- **Current Strategy**: `reasoning`
- **Description**: Impact Verification
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Coach (`sp_744ca2e40b51424b`)
- **Current Strategy**: `fast`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Performativity Detector (`step_performativity_detector`)
- **Current Strategy**: `strict`
- **Description**: Illusion of Control Audit
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Falsifier (`sp_d948cb51bed3454c`)
- **Current Strategy**: `strict`
- **Description**: Critical Loop Audit
- **Hooks**: inject_step_metadata, atom_flattening_hook, verify_citation_integrity, matrix_scoring_hook, normalize_matrix_scores

### Guard (`sp_b080d22fcc2f4ff0`)
- **Current Strategy**: `reasoning`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: sanitize_text, verify_structure, inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Judge (`sp_282a7b15f76d4c9e`)
- **Current Strategy**: `strict`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: inject_step_metadata, atom_flattening_hook, verify_citation_integrity, matrix_scoring_hook, enforce_passivity_penalty, normalize_matrix_scores

### Logician (`sp_b7aea7179c1b4193`)
- **Current Strategy**: `reasoning`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Overseer (`sp_76b0dbf44e36495e`)
- **Current Strategy**: `reasoning`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Profiler (`sp_d86aaa8a2756481b`)
- **Current Strategy**: `strict`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: calculate_text_metrics, calculate_control_ratio, inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### XAI Reporter (`step_xai_reporter`)
- **Current Strategy**: `deep`
- **Description**: Imported from sequential_audit_chain
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Faktantarkistaja (`step_fact_checker`)
- **Current Strategy**: `strict`
- **Description**: Hakee taustatietoa tieteelliseen analyysiin.
- **Hooks**: inject_step_metadata, atom_flattening_hook, matrix_scoring_hook, normalize_matrix_scores

### Scoring Engine (`sp_d245365e4a274b9e`)
- **Current Strategy**: `unknown`
- **Description**: Laskee loppupisteet
- **Hooks**: 

### Synteesin Kokoaja (`sp_synthesis_distiller`)
- **Current Strategy**: `unknown`
- **Description**: Tiivistää metadatan ja lataa historian
- **Hooks**: 

### LLM Synteesi (`sp_synthesis_llm`)
- **Current Strategy**: `synthesis`
- **Description**: Tuottaa lopullisen markdownin ja sisältölohkot
- **Hooks**: 

### Riviselitykset (`sp_row_explanations`)
- **Current Strategy**: `strict`
- **Description**: Selittää yksittäiset matriisirivit
- **Hooks**: 

### Synteesin Generointi (`synthesis_generation`)
- **Current Strategy**: `synthesis`
- **Description**: Generates GlobalSynthesisDTO headless data.
- **Hooks**: 

