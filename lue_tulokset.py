import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

# Import V2 DTOs to enforce strict validation
from backend_v2.models.v2_core import PromptBlock


class MinimalExecution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    status: str
    created_at: str | None = None
    completed_at: str | None = None


# Set up logging for error traces
logger = logging.getLogger(__name__)


def print_latest_execution_results(target_locale: str = "fi") -> None:
    db_path = Path(r"C:\src\quorum\data\db_v2.json")

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)

    executions = db.get("executions")
    if executions is None:
        raise RuntimeError("[CRITICAL FAIL FAST] 'executions' taulu puuttuu kokonaan tietokannasta.")

    # 1. Pydantic Strict Validation of PromptBlocks
    prompt_blocks = {}
    db_blocks = db.get("prompt_blocks")
    if db_blocks is None:
        raise RuntimeError("[CRITICAL FAIL FAST] 'prompt_blocks' taulu puuttuu kokonaan tietokannasta.")

    for _pb_id, pb_dict in db_blocks.items():
        # We enforce Pydantic V2 model validation at the perimeter (Fail-Fast: no except masking)
        pb_model = PromptBlock.model_validate(pb_dict)
        prompt_blocks[pb_model.id] = pb_model

    if not executions:
        print("No executions found in db_v2.json")
        return

    # V2 Arkkitehtuuri käyttää Opaque Stripe ID:tä (esim. exe_813...).
    # Lambda int(k) palauttaa aina 0 näillä avaimilla, jolloin arvotaan täysin satunnainen vanha ajo!
    # Haetaan uusin ajo aikaleiman perusteella tai jätetään luomisjärjestykseen.

    valid_executions: list[MinimalExecution] = []
    for exe in executions.values():
        try:
            exe_model = MinimalExecution.model_validate(exe)
            if exe_model.status == "completed":
                valid_executions.append(exe_model)
        except ValidationError as e:
            # Graceful Degradation is allowed ONLY with explicit typed exception logging
            logger.warning("[Fail-Fast] Ajotietueen validointi epäonnistui, ohitetaan: %s", e)

    if not valid_executions:
        raise ValueError("[FAIL-FAST] Ei löytynyt yhtään validia (completed) ajoa.")

    def get_sort_key(exe_model: MinimalExecution) -> str:
        return str(exe_model.created_at or exe_model.completed_at or "")

    latest_exe = max(valid_executions, key=get_sort_key)
    exe_id = latest_exe.id

    print("=" * 80)
    print(f" LATEST EXECUTION: {exe_id}")
    print("=" * 80)

    # V2 Arkkitehtuuri tallentaa kaiken raskaamman datan tiedostoon (Forensic Audit Trail)
    trace_path = Path(f"C:\\src\\quorum\\data\\files\\executions\\{exe_id}\\execution_trace.json")

    if not trace_path.exists():
        print(f"\n[Virhe] Ei löytynyt execution_trace.json tiedostoa: {trace_path}")
        return

    with open(trace_path, encoding="utf-8") as f:
        trace_data = json.load(f)

    print(f"\n✅ LÖYDETTY XAI LOKI! (Koko: {trace_path.stat().st_size / 1024:.1f} KB)\n")

    # Etsi kaikki blk_ alkuiset tulokset trace-blokkien sisältä
    found_any = False
    found_matrices = {}

    def extract_flat_matrices(trace: list[dict[str, Any]]) -> None:
        for event in trace:
            content = event.get("content", {})
            if not isinstance(content, dict):
                continue

            # Find all unique block IDs in this content
            block_ids = set()
            for k in content.keys():
                if k.startswith("blk_"):
                    # Extract the base block ID (e.g. blk_109dab5b6b3f403a)
                    base_id = k.split("_")[0] + "_" + k.split("_")[1]
                    block_ids.add(base_id)

            for b_id in block_ids:
                pb_model = prompt_blocks.get(b_id)
                if pb_model and getattr(pb_model, "is_evaluative", False):
                    # Check if this is a Phase 9 V2 StrictMatrixPayload dict or V1 flat keys
                    b_data = content.get(b_id)

                    if isinstance(b_data, dict):
                        b_dict: dict[str, Any] = b_data
                        norm_score = b_dict.get("normalized_score")
                        if norm_score is None:
                            continue
                        justification = b_dict.get("justification", "")
                        missing = content.get(f"{b_id}_missing_context")  # Often still at root level
                        raw_score = b_dict.get("raw_score", norm_score)
                        level_dict = b_dict.get("level_breakdown")

                        t_atoms = b_dict.get("total_atoms")
                        if t_atoms is not None:
                            extra_info = f"{b_dict.get('true_atoms')}/{t_atoms}"
                        else:
                            extra_info = ""
                    else:
                        # V1 Legacy logic
                        norm_score = content.get(f"{b_id}_normalized")
                        if norm_score is None:
                            norm_score = content.get(f"{b_id}_scaled")

                        if norm_score is None:
                            continue

                        justification = content.get(f"{b_id}_justification", "")
                        missing = content.get(f"{b_id}_missing_context")
                        raw_score = content.get(b_id, norm_score)
                        level_dict = content.get(f"{b_id}_level_breakdown")

                        if f"{b_id}_total_atoms" in content:
                            extra_info = f"{content.get(f'{b_id}_true_atoms')}/{content.get(f'{b_id}_total_atoms')}"
                        else:
                            extra_info = ""

                    just_str = str(justification)
                    if missing:
                        just_str += f"\n[Puuttuva konteksti]:\n{missing}"

                    if isinstance(level_dict, str):
                        try:
                            level_dict = json.loads(level_dict)
                        except json.JSONDecodeError:
                            pass

                    if level_dict and isinstance(level_dict, dict):
                        clean_level_dict = {}

                        def parse_float(x: str) -> float:
                            return float(x) if str(x).replace(".", "").isdigit() else 0.0

                        for lvl_key in sorted(level_dict.keys(), key=parse_float):
                            lvl_data = level_dict[lvl_key]
                            if isinstance(lvl_data, dict):
                                c_key = str(int(float(lvl_key))) if float(lvl_key).is_integer() else str(lvl_key)
                                clean_level_dict[c_key] = f"{lvl_data.get('hits', 0)}/{lvl_data.get('total', 0)}"
                        level_dict = clean_level_dict

                    found_matrices[b_id] = {
                        "score": raw_score,
                        "just": just_str,
                        "extra_info": extra_info,
                        "level_dict": level_dict,
                        "normalized_score": norm_score,
                        "pb_model": pb_model,
                    }

    extract_flat_matrices(trace_data)

    # --- PENALTY SEARCH ---
    found_penalties = {"threat_detected": False, "post_hoc_rationalization": False}

    def find_penalties(data: Any) -> None:
        if isinstance(data, dict):
            if "threat_detected" in data and str(data["threat_detected"]).lower() == "true":
                found_penalties["threat_detected"] = True
            if "post_hoc_rationalization" in data and str(data["post_hoc_rationalization"]).lower() == "true":
                found_penalties["post_hoc_rationalization"] = True

            for v in data.values():
                find_penalties(v)
        elif isinstance(data, list):
            for item in data:
                find_penalties(item)

    find_penalties(trace_data)

    eval_lines = []
    other_lines = []
    global_eval_scores = []

    for block_id, data in found_matrices.items():
        found_any = True
        score = data["score"]
        justification = data["just"]
        pb_model = data["pb_model"]

        # Etsi oikeankielinen nimi käännetystä Pydantic oliosta
        locale_name = pb_model.label.get(target_locale, block_id)
        is_evaluative = pb_model.is_evaluative

        # Hae 'computed_' arvot UI tulostetta varten (PIST.)
        calc_max = pb_model.computed_max

        norm_val = data.get("normalized_score")
        scaled_score = float(norm_val) if norm_val is not None else None

        score_str = f"{score:.1f}"
        if calc_max is not None:
            score_str = f"{score:.1f}/{float(calc_max):.1f}"

        level_dict = data.get("level_dict")
        if not isinstance(level_dict, dict):
            level_dict = {}

        l1 = level_dict.get("1", "-")
        l2 = level_dict.get("2", "-")
        l3 = level_dict.get("3", "-")
        l4 = level_dict.get("4", "-")
        l5 = level_dict.get("5", "-")
        l6 = level_dict.get("6", "-")

        if not level_dict and data.get("extra_info"):
            l1 = data.get("extra_info")

        # Tiivistetään syy ensimmäiseen virkkeeseen
        short_reason = justification.split("\n")[0].strip()
        if "." in short_reason:
            short_reason = short_reason.split(".")[0] + "."
        if len(short_reason) > 42:
            short_reason = short_reason[:39] + "..."

        scaled_str = f"{scaled_score:.1f}%" if scaled_score is not None else "-"
        lvl_str = f"{l1:<7} | {l2:<7} | {l3:<7} | {l4:<7} | {l5:<7} | {l6:<7}"
        line_str = f"{locale_name[:32]:<32} | {score_str:<10} | {lvl_str} | {short_reason:<45} | {scaled_str:<6}"

        if is_evaluative:
            eval_lines.append(line_str)
            if scaled_score is not None:
                global_eval_scores.append(scaled_score)
        else:
            other_lines.append(line_str)

    # --- TULOSTUS ---
    lvl_head = f"{'T1':<7} | {'T2':<7} | {'T3':<7} | {'T4':<7} | {'T5':<7} | {'T6':<7}"
    print(f"\n{'MATRIISI':<32} | {'PIST.':<10} | {lvl_head} | {'PERUSTELU':<45} | {'100%':<6}")
    print("=" * 165)
    for line in eval_lines:
        print(line)

    print("-" * 165)
    if global_eval_scores:
        avg = sum(global_eval_scores) / len(global_eval_scores)
        print(f"{'► KOKONAISARVOSANA (Keskiarvo)':<32} | {'':<10} | {'':<60} | {'':<45} | {avg:.1f}%")

    if other_lines:
        print("=" * 140)
        print("[ INFO-MATRIISIT (Ei vaikutusta keskiarvoon) ]")
        print("-" * 140)
        for line in other_lines:
            print(line)

    # --- PENALTY TULOSTUS ---
    print("=" * 140)
    print("[ RANGAISTUSMEKANISMIT ]")
    print("-" * 140)

    t_flag = "⚠️ AKTIVOITUNUT (Pisteitä alennettu)" if found_penalties["threat_detected"] else "✅ Puhdas"
    print(f" Guard (Turvallisuusuhka):           | {t_flag}")

    p_flag = "⚠️ AKTIVOITUNUT (Pisteitä alennettu)" if found_penalties["post_hoc_rationalization"] else "✅ Puhdas"
    print(f" Falsifier (Jälkikäteisrationalis.): | {p_flag}")
    print("=" * 140)

    if not found_any:
        print("Ei löytynyt 'blk_' arvoja trace-tiedostosta. Dumpataan juuriavaimet tracesta:")
        if isinstance(trace_data, dict):
            print(list(trace_data.keys()))


if __name__ == "__main__":
    cli_locale = sys.argv[1] if len(sys.argv) > 1 else "fi"
    print_latest_execution_results(target_locale=cli_locale)
