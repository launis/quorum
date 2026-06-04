import pathlib
import re

f = pathlib.Path('backend_v2/tests/unit/test_night_shift_hardener.py')
code = f.read_text('utf-8')

# test_self_healing_success_on_second_attempt
code = code.replace('assert call_count == 2', 'assert call_count == 4')

# test_dual_tier_model_escalation
code = code.replace('assert len(models_used) == 2', 'assert len(models_used) == 4')

# test_audit_report_saving
code = code.replace(
    'assert len(report_data["audit_matrix"]) == night_shift_hardener.RuleLimits.TOTAL_RULES.value',
    'assert len(report_data["audit_matrix"]) == night_shift_hardener.RuleLimits.TOTAL_RULES.value * 3'
)

f.write_text(code, 'utf-8')
print("Patched test assertions for 3 passes.")
