import os

# Fix llm.py
llm_path = "backend_v2/services/orchestrator/strategies/llm.py"
with open(llm_path, "r", encoding="utf-8") as f:
    llm_code = f.read()

llm_code = llm_code.replace(
    "from backend_v2.models.state import TraceEvent",
    "from backend_v2.models.state import TraceEvent, MCPAuditTrace"
)
llm_code = llm_code.replace(
    "t_trace = TraceEvent.model_validate(tr_dict)",
    "t_trace = MCPAuditTrace.model_validate(tr_dict)"
)

with open(llm_path, "w", encoding="utf-8") as f:
    f.write(llm_code)

# Fix scoring.py E501
scoring_path = "backend_v2/hooks/scoring.py"
with open(scoring_path, "r", encoding="utf-8") as f:
    scoring_code = f.read()

old_line = "atom_mapping[aid] = (pb_id, s_val, tda.ai_rule_description, getattr(tda, \"aggregation_mode\", \"EXISTS\"))"
new_line = "atom_mapping[aid] = (\n                                pb_id, s_val, tda.ai_rule_description, getattr(tda, \"aggregation_mode\", \"EXISTS\")\n                            )"

scoring_code = scoring_code.replace(old_line, new_line)

with open(scoring_path, "w", encoding="utf-8") as f:
    f.write(scoring_code)

print("Fixes applied.")
