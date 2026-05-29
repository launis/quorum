"""Night Shift Hardener module for Cognitive Quorum V2 Python Backend files.

This script runs during off-peak hours (night shift) to scan the entire
backend directory, identify Python files requiring architectural hardening,
interact with LLM models using LiteLLM structured outputs to automatically refactor
each file according to Quorum 2026 Enterprise Standards (Strict Nirvana),
and write the verified results back to the filesystem.
"""

import asyncio
import ctypes
import json
import logging
import os
import subprocess
import sys
from enum import IntEnum
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Load environment variables from the project's .env file (for GCP service-account authentication)
load_dotenv()


class RuleLimits(IntEnum):
    """Define architectural hardening rules limits.

    Use TOTAL_RULES as the single source of truth for the validation matrix count.
    """

    TOTAL_RULES = 56


# --- CONFIGURATION ---
BACKEND_DIR = Path("backend_v2")
STATE_FILE = Path("tmp/night_shift_state.json")
SYSTEM_PROMPT_FILE = Path("scripts/hardening.xml")

# Location/Region management for Vertex AI:
# We default to "global" (flagship global endpoint with highest quotas, lowest latency,
# and guaranteed support for Gemini 3.5/Pro/Flash models via the new GenAI SDK), but allow override.
VERTEX_LOCATION = os.getenv("HARDENING_VERTEX_LOCATION", "global")
os.environ["VERTEX_LOCATION"] = VERTEX_LOCATION
os.environ["VERTEXAI_LOCATION"] = VERTEX_LOCATION

# The LLM models supported by Cognitive Quorum V2 (Kehityskohde 5: Dual-Tier)
# Optimized as a hybrid flagship stack: Primary sweep with Gemini 3.5 Flash,
# escalating to the validated stable Gemini 2.5 Pro for complex self-healing loops.
PRIMARY_MODEL = "vertex_ai/gemini-3.5-flash"
HEALING_MODEL = "vertex_ai/gemini-2.5-pro"

# Concurrency and FinOps Rate Limit controls
CONCURRENCY_LIMIT = 2
COOLDOWN_SECONDS = 15.0
MAX_RETRIES = 3

IGNORED_DIRS = {"__pycache__", "venv", ".venv", "alembic", "versions", "tests"}

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("NightShift")

# --- WINDOWS KEEP-AWAKE (C-level API) ---
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


def prevent_sleep() -> None:
    """Prevent the Windows system from entering sleep mode during execution.

    Uses Windows kernel32 ThreadExecutionState C-API to lock the sleep mode,
    ensuring continuous execution of overnight hardening runs on NT platforms.

    Raises:
        OSError: If kernel32 system call fails on Windows platforms.
    """
    if os.name == "nt":
        try:
            logger.info("🛡️ Windowsin lepotila estetty skriptin ajon ajaksi.")
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        except Exception as e:
            logger.error(f"⚠️ Lepotilan estäminen epäonnistui: {e}", exc_info=True)
            raise OSError("Windows kernel32 call failed to prevent sleep.") from e


def allow_sleep() -> None:
    """Allow the Windows system to enter sleep mode again.

    Releases the thread execution state lock previously set by prevent_sleep
    on NT platforms, allowing the system to resume normal sleep behaviors.

    Raises:
        OSError: If kernel32 system call fails on Windows platforms.
    """
    if os.name == "nt":
        try:
            logger.info("💤 Windowsin lepotilalukko vapautettu. Kone saa nukahtaa.")
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        except Exception as e:
            logger.error(f"⚠️ Lepotilan vapauttaminen epäonnistui: {e}", exc_info=True)
            raise OSError("Windows kernel32 call failed to allow sleep.") from e


class AuditItem(BaseModel):
    """Pydantic model representing a single rule check from the audit matrix."""

    model_config = ConfigDict(strict=True, extra="forbid")

    rule_id: int = Field(
        ...,
        ge=1,
        le=RuleLimits.TOTAL_RULES.value,
        description=f"Säännön numero (1-{RuleLimits.TOTAL_RULES.value})",
    )
    rule_name: str = Field(..., description="Tarkistettavan säännön kuvaus")
    status: Literal["Pass", "Fail", "Not_Applicable"]
    finding: str = Field(..., description="Konkreettinen löydös koodista tai perustelu")


class HardeningResponse(BaseModel):
    """Pydantic model representing the output of the headless Python file hardening.

    Attributes:
        audit_matrix: Exactly total rules audit items, one for each rule in the matrix.
        is_rewritten: Boolean indicating whether changes were made.
        hardened_code: The completely rewritten, Phase 9 compliant Python file content.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    audit_matrix: list[AuditItem] = Field(
        ...,
        description=f"Tasan {RuleLimits.TOTAL_RULES.value}-rivinen laatuporttimatriisi",
    )
    is_rewritten: bool = Field(..., description="Tehtiinkö tiedostoon muutoksia?")
    hardened_code: str = Field(
        ...,
        description="Täydellinen, korjattu Python-koodi. Jos ei muutoksia, alkuperäinen koodi.",
    )

    @field_validator("audit_matrix")
    @classmethod
    def validate_exactly_total_checks(cls, v: list[AuditItem]) -> list[AuditItem]:
        """Validate that the LLM returned exactly the configured number of checklist items to prevent laziness."""
        if len(v) != RuleLimits.TOTAL_RULES.value:
            raise ValueError(
                f"The audit checklist must contain exactly {RuleLimits.TOTAL_RULES.value} items, but got {len(v)}."
            )
        return v


def load_state() -> dict[str, str]:
    """Load the current hardening state from the local state JSON file.

    Returns:
        A dictionary mapping absolute file paths to their hardening statuses.

    Raises:
        json.JSONDecodeError: If the state file is corrupt and cannot be parsed.
    """
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    return {str(k): str(v) for k, v in loaded.items()}
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ Tilahistorian luku epäonnistui (korruptoitunut JSON): {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"⚠️ Tilahistorian luku epäonnistui odottamattomaan virheeseen: {e}", exc_info=True)
    return {}


state_lock = asyncio.Lock()


async def safe_update_state(file_path: str, status: str, state_file_path: Path) -> None:
    """Update and save the execution state atomically using an async lock.

    Args:
        file_path: The absolute/relative string path of the processed file.
        status: The execution status ("DONE", "FAILED", etc.).
        state_file_path: Path object pointing to the state JSON file.

    Raises:
        OSError: If writing to the state file fails.
    """
    async with state_lock:
        state_data = {}
        if state_file_path.exists():
            try:
                # Read the current state under the safety lock to prevent dirty reads
                with open(state_file_path, encoding="utf-8") as f:
                    state_data = json.load(f)
            except json.JSONDecodeError:
                logger.warning("⚠️ State JSON file is corrupt, re-initializing.")

        state_data[file_path] = status

        # Ensure the state directory exists and write atomically to prevent serialization loss
        state_file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(state_file_path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to write atomic state update: {e}", exc_info=True)
            raise OSError(f"Failed to write state update to {state_file_path}") from e


def slim_error_feedback(error_msg: str) -> str:
    """Slim down long error messages to preserve LLM token context while retaining actionable details.

    Args:
        error_msg: The raw error message string from subprocess or compiler.

    Returns:
        A slimmed-down, truncated version of the error message.
    """
    # Kehityskohde 3: Itseparantavan silmukan virhepalautteen optimointi
    if not error_msg:
        return "No error feedback details provided."
    lines = error_msg.splitlines()
    if len(lines) <= 40:
        return error_msg
    # Keep first 20 lines and last 20 lines
    first_part = lines[:20]
    last_part = lines[-20:]
    return "\n".join(first_part) + "\n\n... [TRUNCATED FOR BREVITY] ...\n\n" + "\n".join(last_part)


async def process_file_with_retry(
    system_prompt: str, target_file: Path, semaphore: asyncio.Semaphore, state_file_path: Path
) -> bool:
    """Refactor a single file, runs self-healing loops on linter/compiler errors, and rolls back on exhaustion.

    Reads the target file, compiles a user prompt, manages API semaphore concurrency
    limits, executes the asynchronous structured LLM completion request with lazy-loaded
    LiteLLM libraries, validates compilation, runs sub-process linter, formatter and type checks,
    and rolls back to original code on any validation failure.

    Args:
        system_prompt: The detailed system directives from the hardening XML.
        target_file: Path object pointing to the file to be hardened.
        semaphore: The concurrency controller limiting simultaneous active API calls.
        state_file_path: Path object pointing to the state JSON file.

    Returns:
        True if the file was successfully hardened and passed verification, False otherwise.

    Raises:
        asyncio.CancelledError: If the task execution is cancelled.
    """
    async with semaphore:
        try:
            # Keep a backup of the original content in memory to allow atomic rollback if checks fail
            original_code = target_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"❌ Tiedoston lukuvirhe {target_file.name}: {e}", exc_info=True)
            await safe_update_state(target_file.as_posix(), "FAILED_TO_READ", state_file_path)
            return False

        # State variables for the self-healing loop
        current_code_to_fix = original_code
        error_feedback = ""

        # Rule 41: Deferred AI Initialization - Lazy load heavy ML/LLM library
        from litellm import acompletion

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Kehityskohde 5: Kaksivaiheinen mallihierarkia (Flash ➡️ Pro)
                current_model = PRIMARY_MODEL if attempt == 1 else HEALING_MODEL
                logger.info(f"⏳ Auditoitavana [{attempt}/{MAX_RETRIES}] mallilla {current_model}: {target_file.name}")

                # Compile prompt based on whether we have previous error feedback to allow self-healing
                if error_feedback:
                    logger.warning(f"🔄 Attempting self-healing for {target_file.name} due to prior failures...")
                    user_prompt = (
                        f"TARGET FILE: {target_file.as_posix()}\n\n"
                        "<critical_headless_mandate>\n"
                        "Your previous attempt failed the quality gate checks. Read the error trace below, "
                        "fix the issue (syntax, type mismatch or lint), and return the complete corrected code.\n\n"
                        f"ERROR RECEIVED:\n{slim_error_feedback(error_feedback)}\n"
                        "</critical_headless_mandate>\n\n"
                        f"PREVIOUS ATTEMPT:\n```python\n{current_code_to_fix}\n```"
                    )
                else:
                    user_prompt = (
                        f"TARGET FILE: {target_file.as_posix()}\n\n"
                        "<critical_headless_mandate>\n"
                        "Toimit Headless CI/CD -silmukassa. ÄLÄ odota ihmisen PROCEED tai FIX komentoja.\n"
                        "Suorita Phase 2 (Audit Matrix) ja Step 3 (Fix) sisäisessä päättelyssäsi. "
                        "Palauta tulos AINOASTAAN pyydetyssä JSON-formaatissa (hardened_code).\n"
                        "</critical_headless_mandate>\n\n"
                        f"```python\n{original_code}\n```"
                    )

                # Execute asynchronous LLM call to get structured refactoring suggestions
                response = await acompletion(
                    model=current_model,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    temperature=0.0,
                    response_format=HardeningResponse,
                    vertex_location=VERTEX_LOCATION,
                )

                raw_json = response.choices[0].message.content
                result_dto = HardeningResponse.model_validate_json(raw_json)
                new_code = result_dto.hardened_code

                # Kehityskohde 1: Audit-matriisin raportointi (Audit Report Cards)
                # Create output folder safely and write the JSON-serialized audit matrix result
                report_dir = Path("tmp/audit_reports")
                report_dir.mkdir(parents=True, exist_ok=True)
                report_file = report_dir / f"{target_file.stem}_audit_report.json"
                try:
                    with open(report_file, "w", encoding="utf-8") as rf:
                        json.dump(result_dto.model_dump(), rf, indent=4, ensure_ascii=False)
                    logger.info(f"📊 Audit-matriisin raportti tallennettu: {report_file.as_posix()}")
                except Exception as report_err:
                    logger.error(
                        f"⚠️ Raportin tallennus epäonnistui kohteelle {target_file.name}: {report_err}",
                        exc_info=True,
                    )

                # Strip unexpected markdown wraps to retrieve pure compilable python code
                new_code = new_code.strip()
                if new_code.startswith("```python"):
                    new_code = new_code.split("\n", 1)[1]
                if new_code.endswith("```"):
                    new_code = new_code.rsplit("\n", 1)[0]
                new_code = new_code.strip()

                # Update current code iteration for potential next self-healing loop
                current_code_to_fix = new_code

                # Validate compilation of generated code first to catch syntax and indentation errors early
                try:
                    compile(new_code, target_file.name, "exec")
                except (SyntaxError, IndentationError) as syntax_err:
                    logger.warning(f"⚠️ LLM generated invalid syntax for {target_file.name}: {syntax_err}")
                    raise ValueError(f"Syntax compile validation failed: {syntax_err}") from syntax_err

                # Write hardened code to target file temporarily to run quality gate sub-processes
                target_file.write_text(new_code, encoding="utf-8")

                # Run ruff check, ruff format and strict mypy verification on the modified target file
                try:
                    logger.info(f"🔍 Running Ruff check on {target_file.name}")
                    subprocess.run(
                        ["uv", "run", "ruff", "check", target_file.as_posix(), "--fix"],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30.0,
                    )

                    logger.info(f"🔍 Running Ruff format on {target_file.name}")
                    subprocess.run(
                        ["uv", "run", "ruff", "format", target_file.as_posix()],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30.0,
                    )

                    logger.info(f"🔍 Running MyPy strict type-checking on {target_file.name}")
                    subprocess.run(
                        ["uv", "run", "mypy", target_file.as_posix(), "--strict"],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=60.0,
                    )

                    # Execute Bandit SAST security scan to prevent LLM outputs from
                    # introducing security vulnerabilities or hardcoded secrets.
                    logger.info(f"🛡️ Running Bandit SAST security scan on {target_file.name}")
                    subprocess.run(
                        ["uv", "run", "--with", "bandit", "bandit", "-r", target_file.as_posix(), "-lll"],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30.0,
                    )
                except subprocess.CalledProcessError as audit_err:
                    error_details = audit_err.stderr or audit_err.stdout or ""
                    logger.warning(f"⚠️ Quality Gate failed for {target_file.name}:\n{error_details}")
                    raise ValueError(f"Quality Gate audit failed:\n{error_details.strip()}") from audit_err

                # Everything passed successfully!
                logger.info(f"✅ Kovetettu, validoitu ja formatoitu onnistuneesti: {target_file.name}")
                await safe_update_state(target_file.as_posix(), "DONE", state_file_path)
                await asyncio.sleep(COOLDOWN_SECONDS)
                return True

            except Exception as e:
                logger.warning(f"⚠️ Virhe tiedostossa {target_file.name} (Yritys {attempt}/{MAX_RETRIES}): {e}")

                # Save the failure details as feedback for the next self-healing loop iteration
                error_feedback = str(e)

                # Restore original working code immediately to preserve codebase stability on validation failure
                try:
                    target_file.write_text(original_code, encoding="utf-8")
                    logger.info(f"🔄 Restored original content for {target_file.name} due to verification failure.")
                except Exception as rollback_err:
                    logger.critical(
                        f"🚨 CRITICAL: Rollback failed for {target_file.name}: {rollback_err}", exc_info=True
                    )

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(15 * attempt)
                else:
                    logger.error(
                        f"❌ FATAL: Tiedostoa {target_file.name} ei saatu korjattua turvallisesti. Virhe: {e}",
                        exc_info=True,
                    )
                    await safe_update_state(target_file.as_posix(), "FAILED_VERIFICATION", state_file_path)
                    return False
        return False


def get_git_modified_files() -> list[Path]:
    """Get the list of modified, staged, and untracked Python files in backend_v2 using git.

    Runs git command-line client via subprocess securely.

    Returns:
        A sorted list of unique Path objects representing modified/new files.
    """
    # Kehityskohde 2: Muuttuneiden tiedostojen kohdistaminen
    files: set[Path] = set()

    # 1. Get staged and unstaged modified files from git diff
    try:
        res_diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in res_diff.stdout.splitlines():
            line = line.strip()
            if line.endswith(".py") and line.startswith("backend_v2/"):
                files.add(Path(line))
    except Exception as e:
        logger.warning(f"⚠️ Git diff --name-only epäonnistui: {e}")

    # 2. Get untracked files from git status
    try:
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in res_status.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # Porcelain format: STATUS PATH or STATUS "PATH"
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                status, path = parts
                path = path.strip('"')
                if "->" in path:  # Käsitellään uudelleennimetyt tiedostot (Renamed)
                    path = path.split("->")[1].strip()
                if path.endswith(".py") and path.startswith("backend_v2/"):
                    files.add(Path(path))
    except Exception as e:
        logger.warning(f"⚠️ Git status --porcelain epäonnistui: {e}")

    return sorted(list(files))


async def main() -> None:
    """Orchestrate the entire Night Shift hardening pipeline across the backend.

    Loads the XML system prompt, walks the backend directory structure, ignores
    non-Python, cache, and test folders, resolves the pending files that are not yet
    successfully completed, runs the async processor with strict concurrency controls,
    and handles sleep lock prevention cleanup in all execution outcomes.

    Raises:
        SystemExit: If the system prompt file cannot be resolved.
    """
    logger.info("🌙 Yövuoro (Night Shift Hardener) käynnistyy...")
    prevent_sleep()

    try:
        if not SYSTEM_PROMPT_FILE.exists():
            logger.error(f"❌ XML System Prompt puuttuu: {SYSTEM_PROMPT_FILE}")
            sys.exit(1)

        try:
            system_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"❌ XML System Promptin luku epäonnistui: {e}", exc_info=True)
            sys.exit(1)

        try:
            state = load_state()
        except Exception:
            # Re-initialize state if it was corrupt
            state = {}

        # Support target override via command-line argument for focused testing
        # Kehityskohde 2: Muuttuneiden tiedostojen kohdistaminen ja suoritusmoodit
        target_arg = sys.argv[1] if len(sys.argv) > 1 else None
        force_mode = target_arg == "--force"
        git_mode = target_arg == "--git"

        pending_files = []
        if git_mode:
            logger.info("🎯 Etsitään muuttuneet tiedostot Git-tilasta...")
            git_files = get_git_modified_files()
            for p in git_files:
                if any(ignored in p.parts for ignored in IGNORED_DIRS):
                    continue
                if p.name == "__init__.py" and p.stat().st_size == 0:
                    continue
                pending_files.append(p)
            logger.info(f"Git-tila löysi {len(pending_files)} muuttunutta/uutta tiedostoa.")
        elif force_mode:
            logger.info("⚠️ Force-tila aktivoitu: käydään läpi kaikki tiedostot tilasta huolimatta!")
            for p in BACKEND_DIR.rglob("*.py"):
                if any(ignored in p.parts for ignored in IGNORED_DIRS):
                    continue
                if p.name == "__init__.py" and p.stat().st_size == 0:
                    continue
                pending_files.append(p)
        elif target_arg:
            target_path = Path(target_arg)
            if target_path.exists():
                if target_path.is_file():
                    pending_files.append(target_path)
                elif target_path.is_dir():
                    logger.info(f"📁 Kohdistetaan rekursiivinen ajo hakemistoon: {target_arg}")
                    for p in target_path.rglob("*.py"):
                        if any(ignored in p.parts for ignored in IGNORED_DIRS):
                            continue
                        if p.name == "__init__.py" and p.stat().st_size == 0:
                            continue
                        pending_files.append(p)
                else:
                    logger.error(f"❌ Target override exists but is neither file nor directory: {target_arg}")
                    sys.exit(1)
            else:
                logger.error(f"❌ Target override path does not exist: {target_arg}")
                sys.exit(1)
        else:
            # Default incremental mode
            for p in BACKEND_DIR.rglob("*.py"):
                if any(ignored in p.parts for ignored in IGNORED_DIRS):
                    continue
                if p.name == "__init__.py" and p.stat().st_size == 0:
                    continue
                if state.get(p.as_posix()) != "DONE":
                    pending_files.append(p)

        if not pending_files:
            logger.info("🎉 Koodikanta on jo täysin puunattu! Mene nukkumaan.")
            return

        logger.info(f"Käsittelemättömiä tiedostoja: {len(pending_files)}")

        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        # Pass the immutable state file path directly to avoid sharing mutable dictionary references
        tasks = [process_file_with_retry(system_prompt, f, semaphore, STATE_FILE) for f in pending_files]

        results = await asyncio.gather(*tasks)

        failures = results.count(False)
        if failures > 0:
            logger.warning(f"⚠️ Yövuoro ohi. {failures} tiedostoa epäonnistui. Tarkista {STATE_FILE.name}")
        else:
            logger.info("✅ Yövuoro ohi. Koko koodikanta päivitetty onnistuneesti!")

    finally:
        allow_sleep()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Ajo keskeytetty manuaalisesti. Tila on tallennettu. Voit jatkaa myöhemmin.")
        try:
            allow_sleep()
        except Exception:
            pass
