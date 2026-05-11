import os

file_path = "backend_v2/hooks/scoring.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update atom_mapping
old_mapping = "atom_mapping[aid] = (pb_id, s_val, tda.ai_rule_description)"
new_mapping = "atom_mapping[aid] = (pb_id, s_val, tda.ai_rule_description, getattr(tda, \"aggregation_mode\", \"EXISTS\"))"
if new_mapping not in code:
    code = code.replace(old_mapping, new_mapping)

# 2. Add MatrixReducer import
if "from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer" not in code:
    code = code.replace("from backend_v2.models.v2_core import PromptBlock", "from backend_v2.models.v2_core import PromptBlock, TDAAssertion\nfrom backend_v2.services.orchestrator.matrix_reducer import MatrixReducer")

# 3. Rewrite evaluation loop
old_eval_loop = """        # 2. Iterate evaluations
        for ev in evaluations:
            try:
                ev_dto = AtomEvaluationItemDTO.model_validate(ev)
            except ValidationError as e:
                msg = f"Strict Fail-Fast Enforced: Invalid evaluation item format: {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            atom_id = ev_dto.atom_id
            boolean_val = ev_dto.step_5_boolean
            reasoning = ev_dto.step_4_reasoning

            if not atom_id:
                continue

            mapping = atom_mapping.get(atom_id)
            if not mapping:
                continue

            pb_id, s_val, text = mapping

            if pb_id not in block_scale_stats:
                block_scale_stats[pb_id] = {}
                missing_atoms_by_block[pb_id] = []
                evaluated_atoms_by_block[pb_id] = {}

            # Save the raw output per atom
            # We will use "DLQ" string to represent DLQ state, otherwise bool
            if getattr(ev_dto, "dlq_status", False):
                evaluated_atoms_by_block[pb_id][atom_id] = "DLQ"
            else:
                evaluated_atoms_by_block[pb_id][atom_id] = boolean_val

            if s_val not in block_scale_stats[pb_id]:
                block_scale_stats[pb_id][s_val] = {"hits": 0, "total": 0, "dlqs": 0}

            block_scale_stats[pb_id][s_val]["total"] += 1
            if getattr(ev_dto, "dlq_status", False):
                block_scale_stats[pb_id][s_val]["dlqs"] += 1
                missing_atoms_by_block[pb_id].append(f"- {text} (DLQ - Unscorable)")
            elif boolean_val:
                block_scale_stats[pb_id][s_val]["hits"] += 1
            else:
                if reasoning:
                    missing_atoms_by_block[pb_id].append(f"- {text} (Reasoning: {reasoning})")
                else:
                    missing_atoms_by_block[pb_id].append(f"- {text}")"""

new_eval_loop = """        # 2. Iterate evaluations with MatrixReducer for Three-State Logic
        from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer
        from backend_v2.models.v2_core import TDAAssertion
        
        # Accumulate states per atom_id across all chunks
        raw_states_by_atom: dict[str, list[str]] = {}
        reasoning_by_atom: dict[str, list[str]] = {}
        
        for ev in evaluations:
            try:
                ev_dto = AtomEvaluationItemDTO.model_validate(ev)
            except ValidationError as e:
                msg = f"Strict Fail-Fast Enforced: Invalid evaluation item format: {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            atom_id = ev_dto.atom_id
            boolean_val = ev_dto.step_5_boolean
            reasoning = ev_dto.step_4_reasoning
            dlq = getattr(ev_dto, "dlq_status", False)
            
            if not atom_id:
                continue
                
            if atom_id not in raw_states_by_atom:
                raw_states_by_atom[atom_id] = []
                reasoning_by_atom[atom_id] = []
                
            if dlq:
                raw_states_by_atom[atom_id].append("DLQ")
            elif boolean_val:
                raw_states_by_atom[atom_id].append("PASSED")
            else:
                raw_states_by_atom[atom_id].append("FAILED")
                
            if reasoning:
                reasoning_by_atom[atom_id].append(reasoning)

        # Reduce states and apply to math logic
        for atom_id, states in raw_states_by_atom.items():
            mapping = atom_mapping.get(atom_id)
            if not mapping:
                continue

            pb_id, s_val, text, agg_mode = mapping

            if pb_id not in block_scale_stats:
                block_scale_stats[pb_id] = {}
                missing_atoms_by_block[pb_id] = []
                evaluated_atoms_by_block[pb_id] = {}
                
            if s_val not in block_scale_stats[pb_id]:
                block_scale_stats[pb_id][s_val] = {"hits": 0, "total": 0, "dlqs": 0}

            # Create dummy TDAAssertion to use the MatrixReducer
            # We bypass full validation since we only need aggregation_mode
            dummy_tda = TDAAssertion.model_construct(
                tda_id=atom_id, 
                ai_rule_description=text, 
                inverse_evidence=False, 
                aggregation_mode=agg_mode
            )
            
            final_state = MatrixReducer.reduce(dummy_tda, states)
            reasoning_str = " | ".join(reasoning_by_atom[atom_id])

            if final_state == "DLQ":
                evaluated_atoms_by_block[pb_id][atom_id] = "DLQ"
                block_scale_stats[pb_id][s_val]["total"] += 1
                block_scale_stats[pb_id][s_val]["dlqs"] += 1
                missing_atoms_by_block[pb_id].append(f"- {text} (DLQ - Unscorable)")
            elif final_state == "PASSED":
                evaluated_atoms_by_block[pb_id][atom_id] = True
                block_scale_stats[pb_id][s_val]["total"] += 1
                block_scale_stats[pb_id][s_val]["hits"] += 1
            else:
                evaluated_atoms_by_block[pb_id][atom_id] = False
                block_scale_stats[pb_id][s_val]["total"] += 1
                if reasoning_str:
                    missing_atoms_by_block[pb_id].append(f"- {text} (Reasoning: {reasoning_str})")
                else:
                    missing_atoms_by_block[pb_id].append(f"- {text}")"""

if "raw_states_by_atom" not in code:
    code = code.replace(old_eval_loop, new_eval_loop)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated scoring.py with MatrixReducer")
