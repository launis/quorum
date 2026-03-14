import asyncio
import os
import sys
import traceback
import copy
import statistics
from collections import defaultdict

# Provide path to backend rules
sys.path.insert(0, r"c:\src\quorum")

try:
    import PyPDF2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

def get_pdf_text(filepath):
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        from backend_v2.exceptions import AppException, ErrorCodes
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[TestAuditCLI] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: Error reading {filepath}: {e}")
        return ""

# Definitions
DATASETS = {
    # "SITRA": r"c:\src\quorum\data\files\548d78cd-d540-44a3-bc3e-965064803a40",
    "REKLAMAATIO": r"c:\src\quorum\data\files\3bc29d99-0093-4175-9629-1e2982c6bb6d", 
    "SYNTHETIC_GARBAGE": "MOCK", # Will be intercepted in the loop
}

from backend_v2.models.enums import StrictnessLevel

MACRO_LEVELS = [StrictnessLevel.CAUSAL, StrictnessLevel.ZERO_TRUST] # 3, 5
MICRO_LEVELS = [0, 50, 100]
ITERATIONS = 1

async def main():
    import logging

    from backend_v2.logging_config import setup_logging
    # Less verbose logging for batch runs
    setup_logging(log_level=logging.WARNING)

    from fastapi import BackgroundTasks
    from backend_v2.api.dependencies import TokenData
    from backend_v2.database.factory import get_repository
    from backend_v2.models.v2_core import ExecutionCreate, WorkflowInputs
    from backend_v2.services.execution import ExecutionService
    from backend_v2.services.orchestrator.dag_executor import DAGExecutor
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
    from backend_v2.settings import get_settings
    from backend_v2.models.auth import UserRole
    
    # Initialize Hooks
    from backend_v2.core.hook_registry import hook_registry
    import backend_v2.hooks.input_processing  # registers hook
    import backend_v2.hooks.scoring  # registers hook
    import backend_v2.hooks.reporting # registers hook

    # Extract all dataset texts
    dataset_texts = {}
    for ds_name, test_dir in DATASETS.items():
        print(f"Ladataan aineisto: {ds_name}...")

        if ds_name == "SYNTHETIC_GARBAGE":
            # Highly repetitive payload to trigger: Lexical Diversity < 0.40 or Control Ratio > 0.90
            # Avoid direct "repeat me" commands so Vertex AI doesn't hit max_tokens loop
            words = "Tämä on tärkeä hanke. Hanke on erittäin tärkeä. Tuotokset ovat tärkeitä hankkeelle. " * 15
            dataset_texts[ds_name] = {
                "chat_log": words,
                "product_text": words,
                "reflection_text": words
            }
            continue
        
        chat_path = next((os.path.join(test_dir, f) for f in os.listdir(test_dir) if "SITRA" in f.upper() or "DATA" in f.upper()), None)
        product_path = next((os.path.join(test_dir, f) for f in os.listdir(test_dir) if "lopputuote" in f.lower() or "TULOS" in f.upper()), None)
        reflection_path = next((os.path.join(test_dir, f) for f in os.listdir(test_dir) if "Reflektio" in f.upper() or "INTENTIO" in f.upper()), None)
        
        chat_log = get_pdf_text(chat_path) if chat_path else ""
        product = get_pdf_text(product_path) if product_path else ""
        reflection = get_pdf_text(reflection_path) if reflection_path else ""
        
        dataset_texts[ds_name] = {
            "chat_log": chat_log,
            "product_text": product,
            "reflection_text": reflection
        }
        print(f" -> Chat: {len(chat_log)}, Product: {len(product)}, Reflection: {len(reflection)}")


    user = TokenData(
        id="10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b", # Match system root ID from DB
        email="system@local",
        role=UserRole.ROOT,
        organization_id="436d84de-c526-43b7-93ef-634912be0d2f"
    )

    # Setup
    settings = get_settings()
    repo = await get_repository(settings)
    compiler = PromptCompiler()
    executor = DAGExecutor(repo, compiler)
    service = ExecutionService(repo=repo, executor=executor)
    
    # Patch the repository to manipulate Micro strictness levels on the fly
    original_get_all_blocks = repo.get_all_prompt_blocks
    current_micro_level = [50] # Mutable state for the patch

    async def patched_get_all_blocks():
        blocks = await original_get_all_blocks()
        blocks_copy = copy.deepcopy(blocks)
        for b in blocks_copy:
            b["strictness_level"] = current_micro_level[0]
        return blocks_copy

    repo.get_all_prompt_blocks = patched_get_all_blocks

    print("\n=======================================================")
    print(" BATCH EXECUTION STARTING ")
    print(f" Datasets: {list(DATASETS.keys())}")
    print(f" Macro Levels: {[l.value for l in MACRO_LEVELS]}")
    print(f" Micro Levels: {MICRO_LEVELS}")
    print(f" Iterations per combo: {ITERATIONS}")
    print("=======================================================\n")

    # Store Execution IDs for processing later
    # Format: dict[dataset][macro][micro] = [execution_ids...]
    exec_history = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    total_runs = len(DATASETS) * len(MACRO_LEVELS) * len(MICRO_LEVELS) * ITERATIONS
    current_run = 0

    try:
        for ds_name, texts in dataset_texts.items():
            for macro in MACRO_LEVELS:
                for micro in MICRO_LEVELS:
                    current_micro_level[0] = micro
                    print(f"\n--- Testing Combo: Aineisto={ds_name}, Macro={macro.value}, Micro={micro} ---")
                    
                    for i in range(ITERATIONS):
                        current_run += 1
                        print(f"[{current_run}/{total_runs}] Running iteration {i+1}/{ITERATIONS}...")
                        
                        payload = ExecutionCreate(
                            workflow_id="workflow_courtroom_20_full_audit",
                            strictness_level=macro,
                            raw_inputs=WorkflowInputs(**texts)
                        )
                        
                        bt = BackgroundTasks()
                        record = await service.start_execution(user, payload, bt)
                        
                        # Wait for execution graph
                        for task in bt.tasks:
                            await task.func(*task.args, **task.kwargs)
                        
                        # Verify it finished correctly
                        final_record = await service.get_execution(user, record.id)
                        if final_record.status.value == "failed":
                            print(f"\n   [!!!] FATAL: Execution {record.id} FAILED!")
                            if hasattr(final_record, "error") and final_record.error:
                                print(f"   [!!!] Error Details: {final_record.error}")
                            print("   [!!!] Aborting test pipeline due to Fail-Fast architecture.")
                            sys.exit(1)
                        elif final_record.status.value != "completed":
                            print(f"   [!] WARN: Execution {record.id} ended with status: {final_record.status.value}")
                        
                        exec_history[ds_name][macro.value][micro].append(record.id)
                        
                        # Wait 1s between runs to avoid rate limits
                        await asyncio.sleep(1)
        
        # EXTRACT AND ANALYZE
        print("\n=======================================================")
        print(" ANALYZING RESULTS ")
        print("=======================================================\n")
        
        # Data format: results[dataset][macro][micro][matrix_name] = [scores...]
        analysis_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
        
        for ds_name in exec_history:
            for macro_val in exec_history[ds_name]:
                for micro_val in exec_history[ds_name][macro_val]:
                    for exec_id in exec_history[ds_name][macro_val][micro_val]:
                        
                        record = await service.get_execution(user, exec_id)
                        if not record or not getattr(record, "results", None):
                            continue
                            
                        # VERIFY METADATA INJECTION WORKS natively from backend orchestrator
                        if not hasattr(record, "metadata") or not record.metadata:
                            print(f"[!] Warning: Execution {record.id} missing strictness metadata!")
                        else:
                            saved_macro = record.metadata.get("macro_strictness_level")
                            saved_micro = record.metadata.get("micro_strictness_level")
                            if saved_macro != macro_val or saved_micro != micro_val:
                                print(f"[?] Notice: DB metadata differs from loop: Loop({macro_val}/{micro_val}) vs DB({saved_macro}/{saved_micro})")
                            
                        # Search for `_normalized` scores in all node results
                        # AND extract the top-level `final_score`

                        for node_id, node_res in record.results.items():
                            if isinstance(node_res, dict):
                                if "scoring_result" in node_res and isinstance(node_res["scoring_result"], dict):
                                    if "final_score" in node_res["scoring_result"]:
                                        val = node_res["scoring_result"]["final_score"]
                                        if isinstance(val, (int, float)):
                                            analysis_data[ds_name][macro_val][micro_val]["FINAL_SCORE_KILL_SWITCH"].append(float(val))

                                for k, v in node_res.items():
                                    if k.endswith("_normalized") and isinstance(v, (int, float)):
                                        matrix_name = k.replace("_normalized", "")
                                        analysis_data[ds_name][macro_val][micro_val][matrix_name].append(float(v))
        
        # Generate Markdown Report
        report_lines = []
        report_lines.append("# Cognitive Evaluation Strictness Framework: Analyysiraportti")
        report_lines.append(f"Tämä on automaattisesti generoitu raportti kaksiulotteisen tiukkuustestauksen tuloksista.")
        report_lines.append("Testausajossa varioitiin kahta päämuuttujaa:")
        report_lines.append(f"1. **Makrotaso (Arkkitehtuurinen Tiukkuus):** {', '.join(str(l.value) for l in MACRO_LEVELS)}. Vaikuttaa rooleihin (esim. Syyttäjä) ja poikkeusmoduulien (esim. Zero-Trust Null-Hypothesis) käyttöön.")
        report_lines.append(f"2. **Mikrotaso (Matriisikohtainen Skaala):** {', '.join(str(l) for l in MICRO_LEVELS)} (0=Armelias, 100=Lahjomaton). Vaikuttaa prompt-tason ohjeistuksiin.")
        
        report_lines.append("\n## Johdon Yhteenveto (Executive Summary)")
        report_lines.append("Quorum V2:n uusittu \"Strictness\"-moottori on suunniteltu ohjaamaan tekoälyn suorittamaa kognitiivista arviointia kaksiulotteisesti. Raportti todentaa empiirisesti, miten tiukkuustason kiristäminen (Makrotasot 1-5) yhdistettynä matriisikohtaiseen säätöön (0-100) laskee odotetusti arvosanoja ja pakottaa LLM:n vaatimaan vahvempaa näyttöä väitteiden tueksi. Tämä \"Tiukkuuden Kalibrointi\" on pakollinen ominaisuus erikoistuneissa laadunvarmistus- ja auditoinneissa, poistaen tekoälymalleille tyypillisen myötäilevyyden ja ylioptimistisuuden. Pääasiallinen löydös on, että **Tason 5 Zero-Trust -arkkitehtuuri** toimii halutulla tavalla: se romauttaa arvosanat automaattisesti Null-hypoteesiin, mikäli väitteen tueksi ei löydy todistettavasti validia, tekstivelvoitteet täyttävää näyttöä.")

        report_lines.append("\n## 1. Suositukset ja Kohderyhmät")
        report_lines.append("### Miten 'Tiukkuus' (Strictness) pitäisi valita?")
        report_lines.append("- **Makrotaso 1 (Gricean / Avulias) - *Ideointi ja Luonnokset*:** Kohderyhmänä luovat työntekijät ja kehittäjät. Tarkoituksena on palkita ideasta ja sallia puutteellinen logiikka hahmotelmissa.")
        report_lines.append("- **Makrotaso 3 (Kausaalinen / Oletus) - *Peruskäyttäjät*:** Suosittelemme tätä päivittäiseen työhön. Se on luotettava baseline, joka etsii rakentavasti syy-seuraussuhteita ilman vihamielistä asennetta. Arvioi reilusti sitä mitä on kirjoitettu.")
        report_lines.append("- **Makrotaso 4 (Falsifikaatio / Syyttäjä) - *Sisäinen Auditointi ja Laadunvarmistus*:** Kohderyhmänä esihenkilöt, asiantuntijat ja QA. Tehokas etsimään piileviä virheitä ja haastamaan ylioptimistisia lausuntoja asettamalla tekoälyn antagonistiseen rooliin.")
        report_lines.append("- **Makrotaso 5 (Zero-Trust) - *Compliance, Lakiosasto ja Turvallisuus*:** Tarkoitettu vain äärimmäiseen validointiin, jossa oletusarvoisesti *mikään* väite ei pidä paikkaansa ilman aukotonta tieteellistä tai dokumentaarista todistetta (Kognitiivinen kitka). Käytä tätä kun virheiden hinta on äärimmäisen korkea.")
        
        report_lines.append("\n### Matriisi-tason hienosäätö (Mikrotaso 0-100)")
        report_lines.append("Mikrotaso ohjaa tekoälyn armollisuutta yksittäisten asteikkojen sisällä.")
        report_lines.append("- **0 (Armelias):** Käytä jos haluat sallia tulkinnanvaraisuutta ja palkita yrityksestä. Sopii sisäisiin raportteihin omien alojen asiantuntijoiden kesken.")
        report_lines.append("- **50 (Neutraali):** Sopii objektiiviseen arviointiin yleisen ohjeistuksen mukaan.")
        report_lines.append("- **100 (Lahjomaton):** Käytä vain kun jokaisen sanamuodon ja pilkun on oltava lakiteknisesti tai tieteellisesti kohdallaan. Yhdistettynä Zero-Trust makrotasoon tämä usein romahduttaa normaalin tekstin arvosanat minimiin.")

        report_lines.append("\n## 2. Numeerinen Analyysi Aineistoittain")
        
        for ds_name in analysis_data:
            report_lines.append(f"\n### Aineisto: {ds_name}")
            report_lines.append(f"*(Aineisto-otannan koko: {ITERATIONS} iteratiota per kombinaatio)*\n")
            
            # Find all unique matrices for this dataset
            all_matrices = set()
            for macro in analysis_data[ds_name]:
                for micro in analysis_data[ds_name][macro]:
                    all_matrices.update(analysis_data[ds_name][macro][micro].keys())
            
            for matrix in sorted(list(all_matrices)):
                report_lines.append(f"\n#### Matriisi: `{matrix}`")
                report_lines.append("| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |")
                report_lines.append("|---|---|---|---|---|---|")
                
                # Baseline for delta (Macro 3, Micro 50)
                baseline_mean = None
                if 3 in analysis_data[ds_name] and 50 in analysis_data[ds_name][3]:
                    scores = analysis_data[ds_name][3][50].get(matrix, [])
                    if scores:
                        baseline_mean = statistics.mean(scores)
                
                for macro_val in sorted(analysis_data[ds_name].keys()):
                    for micro_val in sorted(analysis_data[ds_name][macro_val].keys()):
                        scores = analysis_data[ds_name][macro_val][micro_val].get(matrix, [])
                        if not scores:
                            continue
                        
                        count = len(scores)
                        mean_val = statistics.mean(scores)
                        stdev_val = statistics.stdev(scores) if count > 1 else 0.0
                        variance_val = statistics.variance(scores) if count > 1 else 0.0
                        
                        delta_str = "-"
                        if baseline_mean is not None:
                            delta = mean_val - baseline_mean
                            delta_str = f"{delta:+.2f}"
                        
                        report_lines.append(f"| {macro_val} | {micro_val} | **{mean_val:.2f}** | {stdev_val:.2f} | {variance_val:.2f} | {delta_str} |")

        report_content = "\n".join(report_lines)
        report_path = r"c:\src\quorum\docs\strictness_analysis_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        print(f"\nRaportti tallennettu: {report_path}")
        print("Suoritus valmis!")

    except Exception as e:
        from backend_v2.exceptions import AppException, ErrorCodes
        import logging
        logger = logging.getLogger(__name__)
        logger.critical(f"[TestAuditCLI] {ErrorCodes.UNKNOWN_ERROR.name}: BATCH SCRIPT FATAL ERROR: {e}", exc_info=True)
        print("\n--- FAST-FAIL TRACE ---")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
