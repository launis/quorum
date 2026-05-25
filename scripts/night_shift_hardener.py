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
import sys
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

# --- CONFIGURATION ---
BACKEND_DIR = Path("backend_v2")
STATE_FILE = Path("tmp/night_shift_state.json")
SYSTEM_PROMPT_FILE = Path("scripts/hardening.xml")

# The LLM model supported by Cognitive Quorum V2
MODEL_NAME = "gemini/gemini-2.5-pro"

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


class HardeningResult(BaseModel):
    """Pydantic model representing the output of the headless Python file hardening.

    Attributes:
        new_content: The completely rewritten, Phase 9 compliant Python file content.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    new_content: str = Field(
        ...,
        description="The completely rewritten, Phase 9 compliant Python file content. Do not wrap in markdown ticks."
    )


def load_state() -> dict[str, str]:
    """Load the current hardening state from the local state JSON file.

    Returns:
        A dictionary mapping absolute file paths to their hardening statuses.

    Raises:
        json.JSONDecodeError: If the state file is corrupt and cannot be parsed.
    """
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    return {str(k): str(v) for k, v in loaded.items()}
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ Tilahistorian luku epäonnistui (korruptoitunut JSON): {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"⚠️ Tilahistorian luku epäonnistui odottamattomaan virheeseen: {e}", exc_info=True)
    return {}


def save_state(state: dict[str, str]) -> None:
    """Save the current hardening state dictionary to the state JSON file.

    Args:
        state: A dictionary mapping absolute file paths to their status keys.

    Raises:
        OSError: If writing to the file system fails.
    """
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logger.error(f"⚠️ Tilahistorian tallennus epäonnistui: {e}", exc_info=True)
        raise OSError(f"Failed to write hardening state to {STATE_FILE}") from e


async def process_file_with_retry(
    system_prompt: str,
    target_file: Path,
    semaphore: asyncio.Semaphore,
    state: dict[str, str]
) -> bool:
    """Refactor a single target file using LiteLLM structured outputs with retries.

    Reads the target file, compiles a user prompt, manages API semaphore concurrency
    limits, executes the asynchronous structured LLM completion request with lazy-loaded
    LiteLLM libraries, validates the schema structure, sanitizes the response, writes
    the result back to disk, and updates the shared execution state.

    Args:
        system_prompt: The detailed system directives from the hardening XML.
        target_file: Path object pointing to the file to be hardened.
        semaphore: The concurrency controller limiting simultaneous active API calls.
        state: The global state dictionary recording finished/failed file paths.

    Returns:
        True if the file was successfully hardened and written, False otherwise.

    Raises:
        asyncio.CancelledError: If the task execution is cancelled.
    """
    async with semaphore:
        try:
            file_content = target_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"❌ Tiedoston lukuvirhe {target_file.name}: {e}", exc_info=True)
            state[target_file.as_posix()] = "FAILED"
            save_state(state)
            return False

        user_prompt = (
            f"TARGET FILE: {target_file.as_posix()}\n\n"
            "<critical_headless_mandate>\n"
            "Toimit Headless CI/CD -silmukassa. ÄLÄ odota ihmisen PROCEED tai FIX komentoja.\n"
            "Suorita Phase 2 (Audit Matrix) ja Step 3 (Fix) sisäisessä päättelyssäsi. "
            "Palauta tulos AINOASTAAN pyydetyssä JSON-formaatissa (new_content).\n"
            "</critical_headless_mandate>\n\n"
            f"```python\n{file_content}\n```"
        )

        # Rule 41: Deferred AI Initialization - Lazy load heavy ML/LLM library
        import litellm
        from litellm import acompletion

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"⏳ Auditoitavana [{attempt}/{MAX_RETRIES}]: {target_file.name}")

                # Execute asynchronous LLM call with structured output coercion
                response = await acompletion(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0,
                    response_format=HardeningResult,
                )

                raw_json = response.choices[0].message.content
                result_dto = HardeningResult.model_validate_json(raw_json)
                new_code = result_dto.new_content

                # Sanitization: Strip unexpected markdown codeblock wraps if present
                if new_code.startswith("```python"):
                    new_code = new_code.split("\n", 1)[1]
                if new_code.endswith("```"):
                    new_code = new_code.rsplit("\n", 1)[0]

                target_file.write_text(new_code, encoding="utf-8")
                logger.info(f"✅ Korjattu ja tallennettu: {target_file.name}")

                state[target_file.as_posix()] = "DONE"
                save_state(state)

                await asyncio.sleep(COOLDOWN_SECONDS)
                return True

            except Exception as e:
                logger.warning(f"⚠️ Virhe tiedostossa {target_file.name} (Yritys {attempt}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(30 * attempt)
                else:
                    logger.error(f"❌ FATAL: Tiedostoa {target_file.name} ei saatu korjattua. Virhe: {e}", exc_info=True)
                    state[target_file.as_posix()] = "FAILED"
                    save_state(state)
                    return False
        return False


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

        pending_files = []
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
        tasks = [process_file_with_retry(system_prompt, f, semaphore, state) for f in pending_files]

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