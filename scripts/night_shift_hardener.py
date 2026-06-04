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
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Load environment variables from the project's .env file (for GCP service-account authentication)
load_dotenv()


# --- CONFIGURATION ---
BACKEND_DIR = Path("backend_v2")
STATE_FILE = Path("tmp/night_shift_state.json")
SYSTEM_PROMPT_FILE = Path("scripts/hardening.xml")


def _count_rules(xml_path: Path) -> int:
    import re

    if xml_path.exists():
        content = xml_path.read_text(encoding="utf-8")
        # Lasketaan <rule num="X"> elementtien määrä
        return len(re.findall(r"<rule\s+num=", content))
    return 73


class RuleLimits(IntEnum):
    """Define architectural hardening rules limits.

    Use TOTAL_RULES as the single source of truth for the validation matrix count.
    """

    TOTAL_RULES = _count_rules(SYSTEM_PROMPT_FILE)


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
HEALING_MODEL = "gemini/gemini-3.1-pro-preview"

# Concurrency and FinOps Rate Limit controls
CONCURRENCY_LIMIT = 2
COOLDOWN_SECONDS = 15.0
MAX_RETRIES = 5

IGNORED_DIRS = {
    "__pycache__",
    "venv",
    ".venv",
    "alembic",
    "versions",
    "tests",
    "prompt_compiler.py",
    "prompt_compiler_adapter.py",
    "dag_executor.py",
    "context_builder.py",
    "context_router.py",
    "llm_task_executor.py",
}

# Varmista että tmp-kansio on olemassa lokia varten
Path("tmp").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("tmp/night_shift.log", encoding="utf-8"), logging.StreamHandler()],
)
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


async def run_async_cmd(*args: str) -> tuple[str, str]:
    """Suorita komentorivikomento asynkronisesti blokkaamatta event looppia."""
    import asyncio
    import subprocess

    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout_bytes, stderr_bytes = await process.communicate()
    stdout_str = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
    stderr_str = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=process.returncode or 1, cmd=args, output=stdout_str, stderr=stderr_str
        )

    return stdout_str, stderr_str


import ast


def analyze_file_context(code: str) -> set[str]:
    """Analyze file context deterministically using AST (Phase 2).

    Instead of regex heuristics, this uses the Python AST compiler to check
    exact imports and module dependencies to return semantic triggers.

    Args:
        code: The raw Python source code string.

    Returns:
        A set of trigger strings (e.g., 'pydantic', 'database', 'arq', 'state').
    """
    triggers: set[str] = set()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        logger.warning("⚠️ AST Parsing failed for file context analysis (SyntaxError). Returning empty triggers.")
        return triggers

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.lower()
                if "pydantic" in name:
                    triggers.add("pydantic")
                if "sqlalchemy" in name or "database" in name or "db" in name:
                    triggers.add("database")
                if "arq" in name:
                    triggers.add("arq")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.lower()
                if "pydantic" in name:
                    triggers.add("pydantic")
                if "sqlalchemy" in name or "database" in name or "db" in name:
                    triggers.add("database")
                if "arq" in name:
                    triggers.add("arq")
                if "models" in name or "state" in name:
                    triggers.add("state")
                    triggers.add("flow")

    # Fallback heuristic for state management classes not explicitly imported
    if "HookState" in code or "HookResult" in code or "StepOutputDTO" in code:
        triggers.add("state")
        triggers.add("flow")

    return triggers


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
    pass_id: str | None = Field(None, description="Missä vaiheessa tämä tarkistus suoritettiin (1, 2, 3...)")


class HardeningResponse(BaseModel):
    """Pydantic model representing the output of the headless Python file hardening.

    Attributes:
        audit_matrix: List of architectural rule violations that were found and fixed.
        is_rewritten: True jos koodia jouduttiin muuttamaan, False jos se oli jo täydellinen.
        hardened_code: The completely rewritten, Phase 9 compliant Python file content.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    audit_matrix: list[AuditItem] = Field(
        ...,
        description="List of architectural rule violations that were found and fixed.",
    )
    is_rewritten: bool = Field(
        ...,
        description="True jos koodia jouduttiin muuttamaan, False jos se oli jo täydellinen.",
    )
    hardened_code: str = Field(
        ...,
        description="Täydellinen, korjattu Python-koodi. Jos ei muutoksia, alkuperäinen koodi.",
    )


class HealingResponse(BaseModel):
    """A lightweight Pydantic model for self-healing loops to save token bandwidth."""

    model_config = ConfigDict(strict=True, extra="forbid")

    hardened_code: str = Field(
        ...,
        description="The fixed Python code that resolves the MyPy/Ruff compilation errors.",
    )


class JudgeResponse(BaseModel):
    """Pydantic model representing the Adversarial Judge's verdict on the LLM's modifications.

    Field ordering is deliberate: chain_of_thought MUST come first to force
    the LLM to reason through the diff systematically before committing to
    a binary is_approved verdict (Chain-of-Thought before Decision pattern).
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    chain_of_thought: str = Field(
        ...,
        description=(
            "Analysoi askel askeleelta jokainen diffin muutos. "
            "Päätä kutakin muutosta varten: onko kyseessä 1) kosmeettinen/tyylimuutos "
            "(sallittu ilman mainintaa matriisissa) vai 2) looginen/algoritminen muutos "
            "(VAATII vastaavan maininnan matriisissa). Listaa löydöksesi."
        ),
    )
    is_approved: bool = Field(..., description="True jos kaikki loogiset muutokset diffissä on perusteltu matriisissa.")
    rejection_reason: str = Field(..., description="Jos hylättiin, miksi? Mikä muutos diffissä ei täsmää matriisiin?")


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
            raise
    return {}


state_lock = asyncio.Lock()
fs_validation_lock = asyncio.Lock()


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
    if len(lines) <= 200:
        return error_msg
    # Gemini 2.5 Pro context is massive, keep up to 200 lines to ensure all MyPy errors are seen
    first_part = lines[:100]
    last_part = lines[-100:]
    return "\n".join(first_part) + "\n\n... [TRUNCATED FOR BREVITY] ...\n\n" + "\n".join(last_part)


import xml.etree.ElementTree as ET


def filter_rules_by_pass(xml_content: str, pass_id: str, triggers: set[str]) -> str:
    """Suodattaa hardening.xml:n kategoriat annetun Pass-vaiheen ja AST-triggerien mukaan.

    Args:
        xml_content: Koko hardening.xml sisältö.
        pass_id: Käynnissä olevan vaiheen ID (esim. '1', '2', '3').
        triggers: AST-analysaattorin löytämät trigger-sanat (esim. 'pydantic', 'database').

    Returns:
        Suodatettu XML-merkkijono, jossa on vain sallitut säännöt.
    """
    try:
        root = ET.fromstring(xml_content)
        mandates = root.find("architectural_mandates")
        if mandates is not None:
            categories_to_remove = []
            for category in mandates.findall("category"):
                cat_pass = category.get("pass")
                cat_trigger = category.get("trigger")

                # Rule is kept if it is GLOBAL or matches current pass
                is_valid_pass = cat_pass == "GLOBAL" or cat_pass == pass_id

                # If pass matches, check if trigger matches
                is_valid_trigger = False
                if cat_trigger == "always" or not cat_trigger:
                    is_valid_trigger = True
                else:
                    required_triggers = cat_trigger.split("|")
                    if any(t in triggers for t in required_triggers):
                        is_valid_trigger = True

                if not (is_valid_pass and is_valid_trigger):
                    categories_to_remove.append(category)

            for cat in categories_to_remove:
                mandates.remove(cat)

        return ET.tostring(root, encoding="unicode", method="xml")
    except Exception as e:
        logger.error(f"⚠️ XML Parsing failed: {e}. Falling back to full prompt.")
        return xml_content


import ast


def ast_parity_check(original_code: str, new_code: str) -> None:
    """Verify that no public classes, functions, or imports have been removed.

    Uses set-based symbol identity verification instead of naive numerical
    counting. This prevents the scenario where the LLM deletes a critical
    function (e.g., process_payment) but generates a hallucinated helper
    (e.g., _format_date), keeping the count equal while silently corrupting
    the public API surface.

    Allowed changes:
        - Adding new functions, classes, or imports.
        - Removing or renaming private symbols (prefixed with underscore).

    Rejected changes:
        - Removing any public function or class (not prefixed with underscore).
        - Reducing the total number of import statements (Rule 76).

    Args:
        original_code: The original Python source code before hardening.
        new_code: The hardened Python source code produced by the LLM.

    Raises:
        ValueError: If any public symbol was removed or imports were lost.
    """
    def _extract_symbols(code: str) -> tuple[set[str], set[str], int]:
        """Extract named symbols and import count from source code.

        Args:
            code: Raw Python source code string.

        Returns:
            Tuple of (class_names, function_names, import_count).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return set(), set(), 0

        classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        funcs = {
            n.name for n in ast.walk(tree)
            if isinstance(n, ast.AsyncFunctionDef | ast.FunctionDef)
        }
        imports = len([n for n in ast.walk(tree) if isinstance(n, ast.Import | ast.ImportFrom)])
        return classes, funcs, imports

    try:
        orig_classes, orig_funcs, orig_imports = _extract_symbols(original_code)
        new_classes, new_funcs, new_imports = _extract_symbols(new_code)

        # Set-based identity check: find public symbols that were removed
        missing_public_classes = {
            sym for sym in (orig_classes - new_classes) if not sym.startswith("_")
        }
        missing_public_funcs = {
            sym for sym in (orig_funcs - new_funcs) if not sym.startswith("_")
        }

        if missing_public_classes:
            raise ValueError(
                f"AST Parity Error: Julkisia luokkia poistettiin luvatta: {missing_public_classes}"
            )
        if missing_public_funcs:
            raise ValueError(
                f"AST Parity Error: Julkisia funktioita poistettiin luvatta: {missing_public_funcs}"
            )

        # Import count guard (Rule 76: never remove imports used by Protocol types)
        if new_imports < orig_imports:
            raise ValueError(f"AST Parity Error: Importteja katosi ({orig_imports} -> {new_imports})")

        # Audit log for transparency: report removed private symbols (allowed but notable)
        removed_private_classes = {sym for sym in (orig_classes - new_classes) if sym.startswith("_")}
        removed_private_funcs = {sym for sym in (orig_funcs - new_funcs) if sym.startswith("_")}
        if removed_private_classes or removed_private_funcs:
            logger.info(
                f"ℹ️ AST Parity: Privaatteja symboleita refaktoroitu (sallittu): "
                f"luokat={removed_private_classes or '∅'}, funktiot={removed_private_funcs or '∅'}"
            )

    except SyntaxError as e:
        raise ValueError(f"Syntax Error AST-pariteetin tarkistuksessa: {e}")


def pydantic_field_signature_guard(original_code: str, new_code: str) -> None:
    """Verify that existing Pydantic model field signatures have not been mutated.

    This is the mechanical enforcement of Rule 85 (Pydantic Schema Freeze Mandate).
    It prevents the hardener LLM from autonomously tightening or altering field types
    on existing models, which would break downstream SSOT database validation.

    Allowed changes:
        - Adding entirely NEW classes (e.g., converting raw dicts to Pydantic models).
        - Adding new fields to existing classes.
        - Modifying docstrings, methods, and non-field code within classes.

    Rejected changes:
        - Changing the type annotation of an existing field.
        - Removing an existing field from a class.
        - Adding or changing ``model_config`` assignments.

    Args:
        original_code: The original Python source code before hardening.
        new_code: The hardened Python source code produced by the LLM.

    Raises:
        ValueError: If any existing field signature was mutated or removed.
    """
    def _normalize_type(t_str: str) -> str:
        """Canonicalize a type annotation string for semantic comparison using AST.

        Resolves syntactic equivalences that Rule 24 (modern syntax) introduces
        so that the Schema Freeze Guard (Rule 85) does not reject legitimate
        modernizations like Optional[X] -> X | None, even in nested structures.
        """
        import ast

        class TypeNormalizer(ast.NodeTransformer):
            def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
                # Convert typing.Optional/Union -> Optional/Union
                if isinstance(node.value, ast.Name) and node.value.id == "typing":
                    return ast.Name(id=node.attr, ctx=ast.Load())
                return self.generic_visit(node)

            def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
                import typing
                visited_node = typing.cast(ast.Subscript, self.generic_visit(node))
                # Check for Optional[X] -> X | None
                is_optional = False
                if isinstance(getattr(visited_node, "value", None), ast.Name) and getattr(visited_node, "value").id == "Optional":
                    is_optional = True
                
                if is_optional:
                    return ast.BinOp(
                        left=typing.cast(ast.expr, getattr(visited_node, "slice", None)),
                        op=ast.BitOr(),
                        right=ast.Constant(value=None)
                    )
                
                # Check for Union[X, Y] -> X | Y
                is_union = False
                if isinstance(getattr(visited_node, "value", None), ast.Name) and getattr(visited_node, "value").id == "Union":
                    is_union = True
                    
                if is_union:
                    if isinstance(getattr(visited_node, "slice", None), ast.Tuple) and len(getattr(visited_node, "slice").elts) >= 2:
                        elements = getattr(visited_node, "slice").elts
                        res = elements[0]
                        for el in elements[1:]:
                            res = ast.BinOp(left=res, op=ast.BitOr(), right=el)
                        return typing.cast(ast.AST, res)
                return visited_node

        try:
            tree = ast.parse(t_str, mode='eval')
            normalized_tree = TypeNormalizer().visit(tree)
            
            unparsed = ast.unparse(normalized_tree).replace(" ", "")
            if "|" in unparsed:
                parts = unparsed.split("|")
                unparsed = "|".join(sorted(parts))
            return unparsed
        except SyntaxError:
            return t_str.replace(" ", "").replace("typing.", "")

    def _extract_class_signatures(code: str) -> dict[str, dict[str, str]]:
        """Extract {class_name: {field_name: type_annotation_str}} from AST.

        Parses annotated assignments (Pydantic fields) and model_config
        assignments from all class definitions in the given source code.

        Args:
            code: Raw Python source code string.

        Returns:
            Nested dict mapping class names to their field signatures.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {}

        result: dict[str, dict[str, str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                fields: dict[str, str] = {}
                for item in node.body:
                    # Capture annotated fields: `name: Type = Field(...)`
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_name = item.target.id
                        type_str = ast.unparse(item.annotation) if item.annotation else "Any"
                        fields[field_name] = type_str
                    # Capture model_config assignments: `model_config = ConfigDict(...)`
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "model_config":
                                fields["model_config"] = ast.unparse(item.value)
                result[node.name] = fields
        return result

    orig_signatures = _extract_class_signatures(original_code)
    new_signatures = _extract_class_signatures(new_code)

    violations: list[str] = []

    for class_name, orig_fields in orig_signatures.items():
        if class_name not in new_signatures:
            # Class deletion is already caught by ast_parity_check
            continue

        new_fields = new_signatures[class_name]

        # Check for removed fields
        for field_name in orig_fields:
            if field_name not in new_fields:
                violations.append(
                    f"Field '{field_name}' was REMOVED from class '{class_name}'"
                )

        # Check for changed type annotations (using semantic normalization)
        for field_name, orig_type in orig_fields.items():
            if field_name in new_fields:
                new_type = new_fields[field_name]
                if _normalize_type(orig_type) != _normalize_type(new_type):
                    violations.append(
                        f"Field '{class_name}.{field_name}' type changed: "
                        f"'{orig_type}' -> '{new_type}'"
                    )

        # Check for model_config being ADDED where none existed
        if "model_config" not in orig_fields and "model_config" in new_fields:
            violations.append(
                f"model_config was ADDED to class '{class_name}' "
                f"(value: {new_fields['model_config']}). Rule 84 violation."
            )

    if violations:
        detail = "\n".join(f"  - {v}" for v in violations)
        raise ValueError(
            f"Pydantic Schema Freeze Guard (Rule 85) REJECTED the change:\n{detail}"
        )

def pydantic_decorator_stacking_guard(code: str) -> None:
    """Verify that Pydantic V2 computed fields have decorators in the correct order.

    The @computed_field decorator must strictly be placed ABOVE the @property decorator.
    In Python AST, decorator_list is ordered from top (outermost) to bottom (innermost).
    Thus, the index of computed_field must be less than the index of property.

    Args:
        code: Raw Python source code string.

    Raises:
        ValueError: If property is stacked above computed_field.
    """
    import ast

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax Error in stacking guard: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef):
            dec_names = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    dec_names.append(dec.id)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                    dec_names.append(dec.func.id)
                elif isinstance(dec, ast.Attribute) and isinstance(dec.value, ast.Name):
                    dec_names.append(dec.attr)

            if "computed_field" in dec_names and "property" in dec_names:
                cf_idx = dec_names.index("computed_field")
                p_idx = dec_names.index("property")
                if p_idx < cf_idx:
                    raise ValueError(
                        f"Pydantic Decorator Stacking Error (Rule 86): "
                        f"Metodissa '{node.name}' on '@property' asetettu '@computed_field':n yläpuolelle! "
                        f"Käännä järjestys siten, että '@computed_field' on ylimpänä."
                    )


async def pre_linting(file_path: Path) -> None:
    """Ajaa ruff format ja ruff check --fix ennen LLM-kutsua."""
    try:
        proc = await asyncio.create_subprocess_shell(
            f"uv run ruff format {file_path}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        proc2 = await asyncio.create_subprocess_shell(
            f"uv run ruff check --fix {file_path}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc2.communicate()
    except Exception as e:
        logger.warning(f"Pre-linting epäonnistui: {e}")


async def tdd_guard(file_path: Path) -> None:
    """Etsii ja ajaa tiedostoon liittyvän yksikkötestin tests/-kansiosta."""
    parts = list(file_path.parts)
    if "backend_v2" in parts:
        b_idx = parts.index("backend_v2")
        test_parts = parts[: b_idx + 1] + ["tests", "unit"] + parts[b_idx + 1 : -1]
        test_name = f"test_{file_path.name}"
        test_parts.append(test_name)
        test_path = Path(*test_parts)

        if not test_path.exists():
            raise ValueError("SKIPPED_NO_TESTS: Strict TDD Guard: Tiedostolla ei ole yksikkötestiä. Estetään karkaisu.")

        logger.info(f"🛡️ TDD Guard: Ajetaan testi {test_path}...")
        proc = await asyncio.create_subprocess_shell(
            f"uv run pytest {test_path} -q", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ValueError(f"TDD Guard Error: Yksikkötesti kaatui!\n{stdout.decode()}")


async def process_file_with_retry(
    system_prompt: str,
    target_file: Path,
    semaphore: asyncio.Semaphore,
    state_file_path: Path,
    resume_mode: bool = False,
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
        resume_mode: Boolean indicating if this is a specialized run for _needs_review files.

    Returns:
        True if the file was successfully hardened and passed verification, False otherwise.

    Raises:
        asyncio.CancelledError: If the task execution is cancelled.
    """
    async with semaphore:
        # Pre-Linting (Säästä tekoälyn aivoja)
        # Suoritetaan automaattinen kosmeettinen siivous ennen LLM-kutsua, jotta
        # tekoäly ei tuhlaa "huomiotaan" vääriin sisennyksiin tai turhiin importteihin.
        await pre_linting(target_file)

        try:
            # Keep a backup of the original content in memory to allow atomic rollback if checks fail
            original_code = target_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"❌ Tiedoston lukuvirhe {target_file.name}: {e}", exc_info=True)
            await safe_update_state(target_file.as_posix(), "FAILED_TO_READ", state_file_path)
            return False

        # Phase 3: Multi-Pass Execution Pipeline
        passes = ["1", "2", "3"] if not resume_mode else ["3"]
        current_code_to_fix = original_code
        aggregated_audit_matrix: list[AuditItem] = []

        for current_pass in passes:
            logger.info(f"🚀 Aloitetaan Pass {current_pass} tiedostolle {target_file.name}")

            # Analyze AST context from current code state
            triggers = analyze_file_context(current_code_to_fix)

            # Filter the system prompt specifically for this pass
            pass_system_prompt = filter_rules_by_pass(system_prompt, current_pass, triggers)

            error_feedback = ""
            pass_success = False

            if resume_mode:
                # We already have a mostly correct file. Let's just generate a validation failure locally.
                real_file = target_file.with_name(target_file.name.replace("_needs_review", ""))
                
                # Rule 60 concurrency protection: Secure global filesystem before writing unverified code
                await fs_validation_lock.acquire()
                _resume_fs_lock_acquired = True
                try:
                    real_file.write_text(current_code_to_fix, encoding="utf-8")
                    await run_async_cmd(
                        "uv",
                        "run",
                        "mypy",
                        real_file.as_posix(),
                        "--strict",
                        "--cache-dir",
                        f"tmp/mypy_cache_{real_file.stem}",
                    )
                    await run_async_cmd("uv", "run", "ruff", "check", real_file.as_posix())
                    # If it magically passes:
                    logger.info(f"✅ Resume Mode: Tiedosto {real_file.name} läpäisi Gaten suoraan!")
                    if target_file.exists():
                        target_file.unlink()
                    await safe_update_state(real_file.as_posix(), "DONE", state_file_path)
                    return True
                except subprocess.CalledProcessError as audit_err:
                    error_feedback = audit_err.stderr or audit_err.stdout or "Validation failed."
                    logger.info(
                        f"Resume Mode: Löydetty {len(error_feedback.splitlines())} riviä virheitä. Aloitetaan mikrokorjaus."
                    )
                finally:
                    if real_file.exists():
                        real_file.unlink()
                    if _resume_fs_lock_acquired:
                        fs_validation_lock.release()
                        _resume_fs_lock_acquired = False

            # Rule 41: Deferred AI Initialization - Lazy load heavy ML/LLM library
            from litellm import acompletion

            rejected_code = ''
            seen_code_hashes: set[str] = set()  # Track all LLM outputs to detect A-B-A yo-yo loops

            # Rule 4: Context Injection to prevent hallucinations
            # Hoisted outside retry loop: these files don't change during the run.
            # Placed in sys_prompt (not user_prompt) so the entire system message forms
            # a stable prefix for Vertex AI Ephemeral Prompt Caching (Rule 53 / FinOps).
            global_context = ""
            try:
                exceptions_code = Path("backend_v2/exceptions.py").read_text(encoding="utf-8")
                global_context += f"\n<file path='backend_v2/exceptions.py'>\n{exceptions_code}\n</file>"
            except OSError:
                pass

            try:
                enums_code = Path("backend_v2/models/enums.py").read_text(encoding="utf-8")
                global_context += f"\n<file path='backend_v2/models/enums.py'>\n{enums_code}\n</file>"
            except OSError:
                pass

            global_context_block = (
                f"\n<global_reference_context>\nThe following files are provided purely for global context (so you know which Enums and ErrorCodes exist). DO NOT modify these files. DO NOT hallucinate enums, use only what is available here or map as TODO.\n{global_context}\n</global_reference_context>\n"
                if global_context
                else ""
            )

            for attempt in range(1, MAX_RETRIES + 1):
                _fs_lock_acquired = False
                try:
                    # Kehityskohde 5: Kaksivaiheinen mallihierarkia (Flash ➡️ Pro)
                    current_model = PRIMARY_MODEL if attempt == 1 else HEALING_MODEL
                    # Gemini 3.5 Flash struggles with valid syntax for large files
                    if current_model == PRIMARY_MODEL and target_file.stat().st_size > 25000:
                        logger.info(f"⏭️ File size ({target_file.stat().st_size} bytes) exceeds Flash capability. Upgrading to PRO.")
                        current_model = HEALING_MODEL
                    logger.info(
                        f"⏳ Auditoitavana [{attempt}/{MAX_RETRIES}] mallilla {current_model}: {target_file.name}"
                    )

                    # Determine file context to help LLM apply rules more accurately
                    file_context = "unknown module type"
                    if "api" in target_file.parts and "routers" in target_file.parts:
                        file_context = "FastAPI router endpoint module (No business logic allowed)"
                    elif "services" in target_file.parts:
                        file_context = "Service logic module (Must use validated Pydantic properties)"
                    elif "models" in target_file.parts:
                        file_context = "Pydantic data models / DTO module"
                    elif "database" in target_file.parts:
                        file_context = "Database repository module (Pure Pydantic projections)"
                    elif "hooks" in target_file.parts:
                        file_context = "Workflow hook module (State is frozen, append-only)"

                    is_healing = bool(error_feedback)

                    # Compile prompt based on whether we have previous error feedback to allow self-healing
                    if is_healing:
                        logger.warning(f"🔄 Attempting self-healing for {target_file.name} due to prior failures...")
                        user_prompt = (
                            f"TARGET FILE: {target_file.as_posix()}\n\n"
                            "<critical_headless_mandate>\n"
                            "Your previous attempt failed the quality gate checks. Read the error trace below, "
                            "fix the issue (syntax, type mismatch or lint), and return the complete corrected code.\n\n"
                            f"ERROR RECEIVED:\n{slim_error_feedback(error_feedback)}\n"
                            "</critical_headless_mandate>\n\n"
                            f"<execution_parameters>\nModule Type: {file_context}\n</execution_parameters>\n\n"
                            f"PREVIOUS ATTEMPT:\n```python\n{rejected_code or current_code_to_fix}\n```"
                        )
                    else:
                        user_prompt = (
                            f"TARGET FILE: {target_file.as_posix()}\n\n"
                            "<critical_headless_mandate>\n"
                            "Toimit Headless CI/CD -silmukassa. ÄLÄ odota ihmisen PROCEED tai FIX komentoja.\n"
                            "Suorita Phase 2 (Audit Matrix) ja Step 3 (Fix) sisäisessä päättelyssäsi. "
                            "Palauta tulos AINOASTAAN pyydetyssä JSON-formaatissa (hardened_code).\n"
                            "</critical_headless_mandate>\n\n"
                            f"<execution_parameters>\nModule Type: {file_context}\n</execution_parameters>\n\n"
                            f"```python\n{current_code_to_fix}\n```"
                        )

                    # Select response format: save tokens by omitting 59-rule audit matrix during self-healing
                    target_format = HealingResponse if is_healing else HardeningResponse
                    sys_prompt = (
                        pass_system_prompt
                        + "\n\nCRITICAL MANDATE: DO NOT hallucinate imports or invent Pydantic models. NEVER delete existing classes or enums assuming they are unused. `dict[str, Any]` is explicitly ALLOWED at the Database boundary."
                        if not is_healing
                        else "Olet kokenut Python-arkkitehti. Korjaa antamastani koodista vain annetut MyPy/Ruff-virheet rikkomatta muuta logiikkaa. CRITICAL MANDATE: DO NOT hallucinate imports or invent Pydantic models. NEVER delete existing classes or enums."
                    ) + global_context_block  # Appended to sys_prompt for Vertex AI prefix caching (Rule 53)

                    # Execute asynchronous LLM call to get structured refactoring suggestions
                    response = await acompletion(
                        model=current_model,
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                        temperature=1.0,  # SSOT: Maximum deterministic surgical precision for both normal and healing modes
                        response_format=target_format,
                        vertex_location=VERTEX_LOCATION,
                    )

                    raw_json = response.choices[0].message.content.strip()
                    if raw_json.startswith("```json"):
                        raw_json = raw_json.removeprefix("```json").removesuffix("```").strip()
                    elif raw_json.startswith("```"):
                        raw_json = raw_json.removeprefix("```").removesuffix("```").strip()

                    result_dto = target_format.model_validate_json(raw_json)
                    new_code = result_dto.hardened_code

                    if not is_healing and isinstance(result_dto, HardeningResponse):
                        for item in getattr(result_dto, "audit_matrix", []):
                            item.pass_id = current_pass
                        aggregated_audit_matrix.extend(getattr(result_dto, "audit_matrix", []))

                    # Strip unexpected markdown wraps to retrieve pure compilable python code
                    new_code = new_code.strip()
                    if new_code.startswith("```python"):
                        new_code = new_code.split("\n", 1)[1]
                    if new_code.endswith("```"):
                        new_code = new_code.rsplit("\n", 1)[0]
                    new_code = new_code.strip()

                    # Phase 2.5: AST Parity Check
                    try:
                        ast_parity_check(current_code_to_fix, new_code)
                    except ValueError as ast_err:
                        logger.warning(f"⚠️ AST Parity Guard failed for {target_file.name}: {ast_err}")
                        rejected_code = new_code
                        raise ast_err

                    # Phase 2.6: Pydantic Schema Freeze Guard (Rule 85)
                    try:
                        pydantic_field_signature_guard(current_code_to_fix, new_code)
                    except ValueError as schema_err:
                        logger.warning(f"🛡️ Schema Freeze Guard REJECTED {target_file.name}: {schema_err}")
                        rejected_code = new_code
                        raise schema_err
                    # Phase 2.7: Pydantic Decorator Stacking Guard (Rule 86)
                    try:
                        pydantic_decorator_stacking_guard(new_code)
                    except ValueError as stacking_err:
                        logger.warning(f"🛡️ Decorator Stacking Guard REJECTED {target_file.name}: {stacking_err}")
                        rejected_code = new_code
                        raise stacking_err

                    # --- ADVERSARIAL JUDGE PASS ---
                    if not is_healing and new_code != current_code_to_fix:
                        import difflib
                        import tempfile

                        # Normalize new_code with ruff format before diffing to eliminate
                        # whitespace noise (blank lines, trailing spaces, import ordering)
                        # that would confuse the Judge into false rejections.
                        normalized_new_code = new_code
                        try:
                            with tempfile.NamedTemporaryFile(
                                mode="w", suffix=".py", delete=False, encoding="utf-8"
                            ) as tmp:
                                tmp.write(new_code)
                                tmp_path = Path(tmp.name)
                            await run_async_cmd("uv", "run", "ruff", "format", tmp_path.as_posix())
                            normalized_new_code = tmp_path.read_text(encoding="utf-8")
                            tmp_path.unlink(missing_ok=True)
                        except Exception:
                            # If normalization fails, fall back to raw diff
                            if tmp_path.exists():
                                tmp_path.unlink(missing_ok=True)

                        diff_lines = list(
                            difflib.unified_diff(
                                current_code_to_fix.splitlines(),
                                normalized_new_code.splitlines(),
                                fromfile="original.py",
                                tofile="hardened.py",
                                lineterm="",
                            )
                        )
                        if diff_lines:
                            diff_str = "\n".join(diff_lines)
                            audit_matrix_json = json.dumps(
                                [a.model_dump() for a in getattr(result_dto, "audit_matrix", [])] if isinstance(result_dto, HardeningResponse) else [], ensure_ascii=False
                            )
                            judge_sys_prompt = (
                                "Olet Quorum Arkkitehtuurituomari. Varmista, ettei Koodari tehnyt luvattomia loogisia muutoksia, "
                                "joita ei ole selkeästi mainittu Audit-matriisissa.\n\n"
                                "SALLITUT muutokset (ei tarvitse matriisimerkintää):\n"
                                "- Tyypitysten tarkentaminen (esim. dict -> dict[str, Any], Optional[X] -> X | None)\n"
                                "- Docstringien lisäys tai päivitys PEP 257 -muotoon\n"
                                "- Importtien järjestely, lisäys tai poisto\n"
                                "- Kosmeettiset whitespace-muutokset\n\n"
                                "KIELLETYT muutokset (VAATIVAT matriisimerkinnän):\n"
                                "- Algoritmin tai funktion alkuperäisen toimintalogiikan muutos\n"
                                "- Ehtolauseiden (if/else) lisäys, poisto tai muutos\n"
                                "- Virheenkäsittelyn (try/except) lisäys, poisto tai muutos\n\n"
                                "Jos löydät luvattoman loogisen muutoksen, aseta is_approved=False ja kerro tarkka syy."
                            )
                            judge_user_prompt = f"Audit-matriisi:\n{audit_matrix_json}\n\nGit Diff:\n{diff_str}"

                            logger.info(f"⚖️ Tuomari tutkii {target_file.name} diffiä...")
                            judge_resp = await acompletion(
                                model=HEALING_MODEL,
                                messages=[
                                    {"role": "system", "content": judge_sys_prompt},
                                    {"role": "user", "content": judge_user_prompt},
                                ],
                                temperature=0.0,  # Deterministic: Judge must not hallucinate violations
                                response_format=JudgeResponse,
                                vertex_location=VERTEX_LOCATION,
                            )

                            raw_judge_json = judge_resp.choices[0].message.content.strip()
                            if raw_judge_json.startswith("```json"):
                                raw_judge_json = raw_judge_json.removeprefix("```json").removesuffix("```").strip()
                            elif raw_judge_json.startswith("```"):
                                raw_judge_json = raw_judge_json.removeprefix("```").removesuffix("```").strip()

                            judge_result = JudgeResponse.model_validate_json(raw_judge_json)
                            if not judge_result.is_approved:
                                logger.warning(f"❌ Tuomari hylkäsi muutoksen: {judge_result.rejection_reason}")
                                rejected_code = new_code
                                raise ValueError(f"Strict Judge Rejection: {judge_result.rejection_reason}")
                            else:
                                logger.info("✅ Tuomari hyväksyi diffin!")

                    # Jojo-silmukan esto (Yo-Yo effect) - hash-pohjainen tilahistoria
                    import hashlib

                    code_hash = hashlib.sha256(new_code.encode("utf-8")).hexdigest()
                    if code_hash in seen_code_hashes and is_healing:
                        logger.warning(
                            f"⚠️ LLM jumiutui Jojo-silmukkaan (A-B-A oskillaatio havaittu yrityksellä {attempt}). "
                            f"Keskeytetään!"
                        )
                        raise ValueError("LLM stuck in a repetitive A-B-A self-healing loop.")
                    seen_code_hashes.add(code_hash)

                    # Update current code iteration for potential next self-healing loop
                    current_code_to_fix = new_code

                    # Validate compilation of generated code first to catch syntax and indentation errors early
                    try:
                        compile(new_code, target_file.name, "exec")
                    except (SyntaxError, IndentationError) as syntax_err:
                        logger.warning(f"⚠️ LLM generated invalid syntax for {target_file.name}: {syntax_err}")
                        raise ValueError(f"Syntax compile validation failed: {syntax_err}") from syntax_err

                    # Write hardened code to the REAL file to maintain proper module context for relative imports
                    real_file = (
                        target_file.with_name(target_file.name.replace("_needs_review", ""))
                        if resume_mode
                        else target_file
                    )

                    # Acquire exclusive filesystem validation lock to prevent race conditions.
                    # LLM calls remain concurrent (Semaphore), but disk writes + linting/testing
                    # are serialized to guarantee that pytest --collect-only and tdd_guard
                    # never see another task's partially-written or broken file on disk.
                    _fs_lock_acquired = False
                    await fs_validation_lock.acquire()
                    _fs_lock_acquired = True
                    real_file.write_text(new_code, encoding="utf-8")

                    # Run ruff check, ruff format and strict mypy verification on the modified real file
                    try:
                        logger.info(f"🔍 Running Ruff check on {real_file.name}")
                        # MUST run format before check so whitespace errors (W293) are auto-fixed before the check gate
                        await run_async_cmd("uv", "run", "ruff", "format", real_file.as_posix())
                        await run_async_cmd("uv", "run", "ruff", "check", real_file.as_posix(), "--fix")

                        # Update current_code_to_fix with formatted code so the self-healing loop doesn't send stale code
                        current_code_to_fix = real_file.read_text(encoding="utf-8")

                        logger.info(f"🔍 Running MyPy strict type-checking on {real_file.name}")
                        await run_async_cmd(
                            "uv",
                            "run",
                            "mypy",
                            real_file.as_posix(),
                            "--strict",
                            "--cache-dir",
                            f"tmp/mypy_cache_{real_file.stem}",
                        )

                        # Execute Bandit SAST security scan
                        logger.info(f"🛡️ Running Bandit SAST security scan on {real_file.name}")
                        await run_async_cmd(
                            "uv", "run", "--with", "bandit", "bandit", "-r", real_file.as_posix(), "-lll"
                        )

                        # Varmistus: Ajetaan arkkitehtuurin eheystarkistus (Pydantic & Imports)
                        logger.info(
                            f"🔬 Running Architectural Integrity Check (pytest collect-only) on {real_file.name}"
                        )
                        try:
                            await run_async_cmd("uv", "run", "pytest", "backend_v2", "--collect-only")
                        except subprocess.CalledProcessError as pytest_err:
                            # Jos pytest collect kaatuu, syynä on 99% varmuudella tämän tiedoston hallusinaatio
                            raise subprocess.CalledProcessError(
                                pytest_err.returncode,
                                pytest_err.cmd,
                                output=pytest_err.stdout,
                                stderr=f"Arkkitehtuurivirhe (Import/Pydantic kaatui muokkauksen jälkeen):\n{pytest_err.stderr or pytest_err.stdout}",
                            )

                        # Phase 2.5: TDD Guard (Aja yksikkötesti jos sellainen on)
                        await tdd_guard(real_file)
                    except subprocess.CalledProcessError as audit_err:
                        raw_details = audit_err.stderr or audit_err.stdout or ""
                        # Filter output so the LLM doesn't get confused by errors in other files
                        real_posix = real_file.as_posix()
                        real_win = real_posix.replace("/", "\\")

                        is_architecture_error = "Arkkitehtuurivirhe" in raw_details or "pytest" in str(audit_err.cmd)

                        filtered_lines = [
                            line
                            for line in raw_details.splitlines()
                            if real_posix in line
                            or real_win in line
                            or ("error:" in line and "backend_v2" not in line)
                            or is_architecture_error
                        ]

                        if not filtered_lines and not is_architecture_error:
                            logger.info(
                                f"✅ MyPy ei löytänyt suoria virheitä tiedostosta {target_file.name}. (Riippuvuuksissa on virheitä, mutta tämä tiedosto on puhdas). Hyväksytään!"
                            )
                            # Emme nosta poikkeusta, eli koodi saa jatkaa tallennukseen!
                        else:
                            error_details = "\n".join(filtered_lines)
                            logger.warning(f"⚠️ Quality Gate failed for {real_file.name}:\n{error_details}")
                            if real_file.exists():
                                current_code_to_fix = real_file.read_text(encoding="utf-8")
                                # Rollback välittömästi, jotta levyllä oleva koodikanta ei jää rikki!
                                if resume_mode:
                                    real_file.unlink()
                                else:
                                    real_file.write_text(original_code, encoding="utf-8")
                            raise ValueError(f"Quality Gate audit failed:\n{error_details.strip()}") from audit_err
                    except Exception as ex:
                        # Rollback välittömästi, jotta levyllä oleva koodikanta ei jää rikki!
                        if real_file.exists():
                            if resume_mode:
                                real_file.unlink()
                            else:
                                real_file.write_text(original_code, encoding="utf-8")
                        raise ex

                    # Everything passed successfully!
                    pass_success = True
                    break  # Break out of retry loop for this pass

                except Exception as e:
                    error_feedback = str(e)
                    if "SKIPPED_NO_TESTS" in error_feedback:
                        logger.warning(f"⏭️ Ohitetaan tiedosto {target_file.name} - Puuttuva yksikkötesti.")
                        if not resume_mode:
                            target_file.write_text(original_code, encoding="utf-8")
                        elif real_file.exists():
                            real_file.unlink()
                        return False

                    logger.warning(
                        f"⚠️ Virhe tiedostossa {target_file.name} (Pass {current_pass} Yritys {attempt}/{MAX_RETRIES}): {e}"
                    )

                    # Varmistetaan, että In-Place rollback on varmasti tehty (jos poikkeus heitettiin jossain muualla)
                    if not resume_mode:
                        target_file.write_text(original_code, encoding="utf-8")
                    else:
                        real_file = target_file.with_name(target_file.name.replace("_needs_review", ""))
                        if real_file.exists():
                            real_file.unlink()

                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(15 * attempt)
                    else:
                        logger.error(
                            f"❌ FATAL: Tiedostoa {target_file.name} ei saatu korjattua turvallisesti (Pass {current_pass}). Virhe: {e}",
                            exc_info=True,
                        )
                        # Soft Fail: Tallenna needs_review -tiedosto
                        clean_stem = target_file.stem.replace("_needs_review", "")
                        review_file = target_file.with_name(f"{clean_stem}_needs_review.py")
                        try:
                            review_file.write_text(current_code_to_fix, encoding="utf-8")
                            logger.warning(f"💾 Tallennettu osittain korjattu versio: {review_file.name}")
                        except OSError as write_err:
                            logger.error(f"Failed to save review file: {write_err}")

                        original_posix = target_file.as_posix().replace("_needs_review", "")
                        await safe_update_state(original_posix, "FAILED_VERIFICATION", state_file_path)
                        return False
                finally:
                    # Guarantee the filesystem validation lock is always released,
                    # regardless of how the try block exits (break, raise, return).
                    # This prevents deadlocks when a task crashes between acquire and release.
                    if _fs_lock_acquired:
                        fs_validation_lock.release()
                        _fs_lock_acquired = False

            if not pass_success:
                return False

        # Kaikki passit suoritettu onnistuneesti!

        # Raportoinnin ja Tilan (State) integrointi: Tallenna kooste kaikista passeista
        report_dir = Path("tmp/audit_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"{target_file.stem}_FINAL_{timestamp}_audit_report.json"

        final_dto = HardeningResponse(
            audit_matrix=aggregated_audit_matrix,
            is_rewritten=(original_code != current_code_to_fix),
            hardened_code=current_code_to_fix,
        )

        try:
            with open(report_file, "w", encoding="utf-8") as rf:
                json.dump(final_dto.model_dump(), rf, indent=4, ensure_ascii=False)
            logger.info(f"📊 Lopullinen yhdistetty Audit-matriisin raportti tallennettu: {report_file.as_posix()}")
        except Exception as report_err:
            logger.error(
                f"⚠️ Lopullisen raportin tallennus epäonnistui kohteelle {target_file.name}: {report_err}",
                exc_info=True,
            )

        if resume_mode:
            if target_file.exists():
                target_file.unlink()
            logger.info(f"✅ Resume Mode: Korjattu onnistuneesti ja palautettu: {real_file.name}")
            await safe_update_state(real_file.as_posix(), "DONE", state_file_path)
        else:
            logger.info(f"✅ Kovetettu, validoitu ja formatoitu onnistuneesti: {real_file.name}")
            await safe_update_state(real_file.as_posix(), "DONE", state_file_path)

        await asyncio.sleep(COOLDOWN_SECONDS)
        return True


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
            # SSOT: Korvataan XML-tiedostossa oleva sääntöjen maksimimäärä dynaamisesti
            raw_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
            system_prompt = raw_prompt.replace("{TOTAL_RULES}", str(RuleLimits.TOTAL_RULES.value))
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
        force_mode = "--force" in sys.argv
        git_mode = "--git" in sys.argv
        resume_mode = "--resume-failed" in sys.argv

        # Get target_arg if provided and not a flag
        target_arg = next((arg for arg in sys.argv[1:] if not arg.startswith("--")), None)

        pending_files = []
        if resume_mode:
            logger.info(
                "🛠️ Resume Mode: Etsitään osittain korjatut *_needs_review.py -tiedostot mikrokorjausta varten..."
            )
            for p in BACKEND_DIR.rglob("*_needs_review.py"):
                pending_files.append(p)
            logger.info(f"Resume Mode löysi {len(pending_files)} puolikuntoista tiedostoa.")
        elif git_mode:
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
                        if p.name.endswith("_needs_review.py"):
                            continue
                        # Varmistetaan, että emme prosessoi valmiita tiedostoja uudelleen
                        if state.get(p.as_posix()) != "DONE":
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
                if p.name.endswith("_needs_review.py"):
                    continue
                if state.get(p.as_posix()) != "DONE":
                    pending_files.append(p)

        if not pending_files:
            logger.info("🎉 Koodikanta on jo täysin puunattu! Mene nukkumaan.")
            return

        logger.info(f"Käsittelemättömiä tiedostoja: {len(pending_files)}")

        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        # Pass the immutable state file path directly to avoid sharing mutable dictionary references
        results = []
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(process_file_with_retry(system_prompt, f, semaphore, STATE_FILE, resume_mode))
                for f in pending_files
            ]

        results = [t.result() for t in tasks]

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
