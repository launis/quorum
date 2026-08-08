import re

with open("backend_v2/services/blueprint.py", encoding="utf-8") as f:
    content = f.read()

# Replace the methods
content = re.sub(
    r'    @staticmethod\n    def _clean_hallucinated_numbers\(text: str\) -> str:.*?(?=    def _apply_pii_masking)',
    '',
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'    def _parse_matrix_trace_results\(.*?(?=    def _hydrate_global_score_block)',
    '',
    content,
    flags=re.DOTALL
)

# Replace the call site
call_site_old = """        (
            evaluative_matrices,
            informational_matrices,
            all_parsed_matrices,
            step_scorecard_atoms,
        ) = self._parse_matrix_trace_results(
            results=results,
            locale=locale,
            blocks_by_id=blocks_by_id,
            workflow_steps=workflow_steps_map,
            profile=profile,
            row_explanations_cache=row_explanations_cache,
            workflow_ext_values=workflow_ext_values,
            row_curated_quotes_cache=row_curated_quotes_cache,
            has_synthesis_cache=bool(profile_cache),
            rejected_evq_ids=rejected_evq_ids,
            mcp_audit_map=mcp_audit_map,
            source_identity_manifest=None,
            execution=execution,
        )"""

call_site_new = """        (
            evaluative_matrices,
            informational_matrices,
            all_parsed_matrices,
            step_scorecard_atoms,
        ) = MatrixDomainParser.parse_matrices(
            results=results,
            locale=locale,
            blocks_by_id=blocks_by_id,
            workflow_steps=workflow_steps_map,
            profile=profile,
            row_explanations_cache=row_explanations_cache,
            workflow_ext_values=workflow_ext_values,
            row_curated_quotes_cache=row_curated_quotes_cache,
            has_synthesis_cache=bool(profile_cache),
            rejected_evq_ids=rejected_evq_ids,
            mcp_audit_map=mcp_audit_map,
            source_identity_manifest=None,
            execution=execution,
        )"""

content = content.replace(call_site_old, call_site_new)

# Add import
import_statement = "from backend_v2.services.matrix_domain_parser import MatrixDomainParser"
content = content.replace(
    "from backend_v2.settings import get_settings",
    "from backend_v2.settings import get_settings\n" + import_statement
)

with open("backend_v2/services/blueprint.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Refactored blueprint.py")
