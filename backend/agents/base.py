"""Base Agent implementation."""

from __future__ import annotations

import hashlib
import json
import logging
import socket
from datetime import datetime, timezone
from typing import Any

import litellm
import requests
import urllib3

# 2. Third Party
from pydantic import BaseModel, ValidationError
from typing import Generic, TypeVar

from backend.core.component import BaseComponent
from backend.models.domain.base import ReasoningTrace

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes

# Use string forward reference to avoid circular import if needed, or if Provider is defined there.
# But LLMFactory is imported.
from backend.llm.provider import LLMFactory, LLMProvider
from backend.models.domain.base import AuditLogEntry, Metadata
from backend.services.localization import LocalizationService

# 4. Logger
logger = logging.getLogger(__name__)

InputT = TypeVar("InputT")
# Output must implicitly support ReasoningTrace behavior (metadata, checksums)
OutputT = TypeVar("OutputT", bound=ReasoningTrace)

class BaseAgent(BaseComponent, Generic[InputT, OutputT]):
    """Abstract base class for all Cognitive Quorum agents.

    Handles LLM interaction via the Provider Pattern.
    Enforces Strict Type Safety via Generics [InputT, OutputT].
    """

    state_field: str | None = None

    # --- CONTRACTS (Data Flow Validation) ---
    # List of keys (in state or inputs) that this agent REQUIRES to run.
    REQUIRES_KEYS: list[str] = []

    # List of keys (in state) that this agent PRODUCES upon success.
    PRODUCES_KEYS: list[str] = []

    # Optional Pydantic Models for Schema Validation
    INPUT_SCHEMA: type[InputT] | None = None
    OUTPUT_SCHEMA: type[OutputT] | None = None # Domain Model (With Metadata)
    DTO_SCHEMA: type[BaseModel] | None = None    # LLM Interface (Content Only)

    def __init__(self, model: str | None = None, provider: str | None = None):

        """Initializes the agent with an optional specific model strategy.

        Args:
            model (Optional[str]): The model identifier (e.g. 'gemini-1.5-pro').
            provider (Optional[str]): The provider (e.g. 'google').

        """
        self.model = model
        self.provider_type = provider # Strict: No default "vertex_ai"
        self.llm_provider: LLMProvider | None = None

        # ZERO-FALLBACK: Agents initialized via Factory might have model=None.
        # We allow this, but execution will fail if model is not set via set_model().

        if model:
            if not self.provider_type:
                 raise ValueError("Provider type required if model is set.")
            self.llm_provider = LLMFactory.create_provider(self.provider_type, model)
        else:
            self.llm_provider = None

    def set_model(
        self,
        model_name: str,
        provider: str | None = None,
        usage_service: Any = None,
        organization_id: str | None = None,
        config: Any | None = None,
    ):
        """Dynamically updates the agent's model preference and ensures LLMProvider is ready.

        Args:
            model_name (str): The new model name.
            provider (Optional[str]): The provider type.
            usage_service (Any): UsageService instance for tracking.
            organization_id (Optional[str]): Contextual Org ID.
            config (Optional[Any]): Full LLMProviderConfig object.
        """
        self.model = model_name
        if provider:
            self.provider_type = provider

        current_provider_type = self.provider_type
        if not current_provider_type:
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_NOT_CONFIGURED,
                 original_error=ValueError("Provider type not set and no default allowed."),
                 agent_name=self.__class__.__name__
             )

        self._create_provider(current_provider_type, model_name, usage_service, organization_id, config)

    def _create_provider(
        self,
        provider_type: str,
        model_name: str,
        usage_service: Any = None,
        organization_id: str | None = None,
        config: Any | None = None,
    ):
        """Helper to instantiate and assign the LLM provider.

        Args:
            provider_type (str): Provider key (e.g. 'google', 'openai').
            model_name (str): The specific model ID.
            usage_service (Any): usage service.
            organization_id (str): org id.
            config (Any): strict config object.
        """
        try:
            self.llm_provider = LLMFactory.create_provider(
                provider_type=provider_type,
                model_name=model_name,
                usage_service=usage_service,
                organization_id=organization_id,
                config=config,
            )
            logger.debug(
                f"[BaseAgent] Provider initialized with {model_name} (Type: {provider_type}, Org: {organization_id})"
            )
        except Exception as e:
            error_code = ErrorCodes.AGENT_NOT_CONFIGURED
            logger.error(f"[BaseAgent] Failed to create provider in set_model: {e}", exc_info=True)
            raise AgentExecutionError(
                detail=error_code,
                original_error=e,
                agent_name=self.__class__.__name__
            ) from e

    def _apply_python_authority(self, data: Any, token_usage: dict[str, int] | None = None) -> OutputT:
        """Injects system-authoritative data (Time, Identity, Checksums).

        Promotes DTOs to Domain Models if DTO_SCHEMA is defined.
        Overrides any LLM-hallucinated values for metadata fields.
        Handles both raw dicts and immutable Pydantic models.
        Returns the modified (or new) object.
        """
        # 1. TIME & IDENTITY AUTHORITY
        utc_now = datetime.now(timezone.utc)
        agent_name = self.__class__.__name__
        env_context = "Internal"

        # --- CASE A: Pydantic Model (DTO or Domain) ---
        if isinstance(data, BaseModel):
            # 1. Construct Updated Metadata (Immutable)
            # Use getattr to support DTOs that lack 'metadata' field (e.g. PanelOutputDTO)
            current_meta = getattr(data, "metadata", None)

            # Prepare metadata fields
            meta_updates = {
                "luontiaika": utc_now,
                "agentti": agent_name,
                "suoritus_ymparisto": env_context,
            }
            
            if token_usage:
                meta_updates["token_usage"] = token_usage

            # Default optional fields if missing
            # We check if they exist in current_meta (if it's a model)
            if current_meta:
                 if not current_meta.vaihe:
                     meta_updates["vaihe"] = 1
                 if not current_meta.versio:
                     meta_updates["versio"] = "2.0"
            else:
                 meta_updates["vaihe"] = 1
                 meta_updates["versio"] = "2.0"

            if current_meta:
                # Use model_copy(update=...) to create new Metadata instance
                new_metadata = current_meta.model_copy(update=meta_updates)
            else:
                # Create fresh Metadata
                new_metadata = Metadata(
                    luontiaika=utc_now,
                    agentti=agent_name,
                    suoritus_ymparisto=env_context,
                    vaihe=int(meta_updates["vaihe"]),
                    versio=str(meta_updates["versio"])
                )

            # 2. Calculate Checksum (using new metadata)
            try:
                content_dict = data.model_dump()
                # Inject metadata into dict for hashing (ensure reproducibility)
                content_dict["metadata"] = new_metadata.model_dump(mode='json')

                if "semanttinen_tarkistussumma" in content_dict:
                    del content_dict["semanttinen_tarkistussumma"]

                dump = json.dumps(content_dict, sort_keys=True, default=str)
                checksum = hashlib.sha256(dump.encode("utf-8")).hexdigest()

                logger.debug(f"[{self.__class__.__name__}] Calc Checksum (Model): {checksum[:8]}...")

                # 3. Promotion or Update
                # CHECK FOR PROMOTION: If data is DTO and we have an OUTPUT_SCHEMA
                if (
                    self.DTO_SCHEMA 
                    and isinstance(data, self.DTO_SCHEMA) 
                    and self.OUTPUT_SCHEMA 
                    and not isinstance(data, self.OUTPUT_SCHEMA)
                ):
                    # Promote DTO -> Domain
                    promoted_data = self.OUTPUT_SCHEMA(
                        **data.model_dump(),
                        metadata=new_metadata,
                        semanttinen_tarkistussumma=checksum
                    )
                    # strict: cast
                    from typing import cast
                    return cast(OutputT, promoted_data)
                
                else:
                    # Regular Update (Domain -> Domain)
                    updates = {
                        "metadata": new_metadata,
                        "semanttinen_tarkistussumma": checksum
                    }
                    from typing import cast
                    return cast(OutputT, data.model_copy(update=updates))

            except Exception as e:
                error_msg = (
                    f"[{self.__class__.__name__}] Critical: Failed to calculate authoritative checksum/promote model. "
                    "Data integrity compromised."
                )
                logger.critical(f"{error_msg} Error: {e}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name=self.__class__.__name__
                ) from e

        # --- CASE B: Dictionary ---
        elif isinstance(data, dict):
            # 1. METADATA AUTHORITY
            if "metadata" not in data or not isinstance(data["metadata"], dict):
                data["metadata"] = {}

            meta = data["metadata"]
            meta["luontiaika"] = utc_now
            meta["agentti"] = agent_name

            # Environment default
            if "suoritus_ymparisto" not in meta:
                meta["suoritus_ymparisto"] = env_context

            # Schema defaults
            if "vaihe" not in meta:
                meta["vaihe"] = 1
            if "versio" not in meta:
                meta["versio"] = "2.0"
                
            if token_usage:
                meta["token_usage"] = token_usage

            # 2. CHECKSUM AUTHORITY
            try:
                # Create a copy to calculate hash without the hash field itself
                content_to_hash = data.copy()
                if "semanttinen_tarkistussumma" in content_to_hash:
                    del content_to_hash["semanttinen_tarkistussumma"]
                # Exclude unstable fields? Validation result is content, so keep it.

                # Sort keys for deterministic hashing
                dump = json.dumps(content_to_hash, sort_keys=True, default=str)
                checksum = hashlib.sha256(dump.encode("utf-8")).hexdigest()

                data["semanttinen_tarkistussumma"] = checksum
                logger.debug(f"[{self.__class__.__name__}] Calc Checksum (Dict): {checksum[:8]}...")
                # 3. Promotion (Dict -> Domain)
                if self.DTO_SCHEMA and self.OUTPUT_SCHEMA:
                    try:
                        promoted_data = self.OUTPUT_SCHEMA(**data)
                        logger.debug(f"[{self.__class__.__name__}] Promoted Dict -> {self.OUTPUT_SCHEMA.__name__}")
                        return promoted_data
                    except Exception as e:
                        logger.warning(f"[{self.__class__.__name__}] Failed to promote dict to Domain Model: {e}")
                        from typing import cast
                        return cast(OutputT, data)

                return data

            except Exception as e:
                # STRICT MODE: Data integrity is critical.
                error_msg = (
                    f"[{self.__class__.__name__}] Critical: Failed to calculate authoritative checksum. "
                    "Data integrity compromised."
                )
                logger.critical(f"{error_msg} Error: {e}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=ValueError(error_msg),
                    agent_name=self.__class__.__name__
                ) from e

        return data

    async def execute(
        self,
        input_data: InputT,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> OutputT:
        """Standard execution entry point.

        Takes typed input model, processes it via the LLM Provider, and returns the typed result.
        Enforces RFC 7807 Error Handling and Pydantic Schema Validation.

        Args:
            input_data (InputT): The resolved input model (or dict) from the Workflow Engine.
            execution_context (dict[str, Any] | None): Access to repository, config, or global state.
            system_instruction (str | None): Optional prompt override (rarely used).
            **kwargs: Additional parameters for LLM (temperature, max_tokens, etc).

        Returns:
            OutputT: The execution result (response domain model).

        Raises:
            AgentExecutionError: If execution fails (wraps all internal exceptions).
        """
        logger.info(f"[{self.__class__.__name__}] Starting execution...")
        
        # --- INPUT DIAGNOSTICS (Context Bloat Investigation) ---
        try:
            # Create a safe copy for inspection
            debug_inputs = input_data
            if isinstance(debug_inputs, BaseModel):
                debug_inputs = debug_inputs.model_dump()
            
            if isinstance(debug_inputs, dict):
                log_msg = []
                for k, v in debug_inputs.items():
                    if isinstance(v, str):
                        # Log length and preview start/end to catch duplication
                        preview = v[:50].replace("\n", "\\n")
                        log_msg.append(f"{k}: {len(v)} chars ('{preview}...')")
                    elif isinstance(v, (list, dict, tuple)):
                        log_msg.append(f"{k}: {len(v)} items")
                    else:
                        log_msg.append(f"{k}: {type(v).__name__}")
                logger.info(f"[{self.__class__.__name__}] INPUT DIAGNOSTICS: " + " | ".join(log_msg))
            else:
                 logger.info(f"[{self.__class__.__name__}] INPUT DIAGNOSTICS: Non-dict input: {type(debug_inputs)}")
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Failed to log input sizes: {e}")
        # -------------------------------------------------------

        try:
            # 0. STRICT INPUT VALIDATION (Phase 8: Type Safety)
            # The Engine is responsible for inflating dict -> Model.
            # Here we enforce that we actually received a Model.
            if self.INPUT_SCHEMA:
                if not isinstance(input_data, self.INPUT_SCHEMA):
                     # FAIL FAST: This is a system integrity failure.
                     # The Engine should have converted it.
                     msg = f"Agent '{self.__class__.__name__}' expected model '{self.INPUT_SCHEMA.__name__}' but received '{type(input_data)}'."
                     error_code = ErrorCodes.AGENT_INVALID_INPUT
                     logger.critical(f"{error_code}: {msg}")
                     raise AgentExecutionError(
                         detail=error_code,
                         original_error=TypeError(msg),
                         agent_name=self.__class__.__name__
                     )

                try:
                    # Double-check validation (redundant if strict, but safe)
                    # strict: cast to type[BaseModel]
                    from typing import cast
                    if issubclass(self.INPUT_SCHEMA, BaseModel):
                         cast(type[BaseModel], self.INPUT_SCHEMA).model_validate(input_data)
                    logger.debug(f"[{self.__class__.__name__}] Input Validation Successful: {self.INPUT_SCHEMA.__name__}")
                except ValidationError as e:
                     error_code = ErrorCodes.AGENT_INVALID_INPUT
                     logger.error(f"{error_code}: Input validation failed for {self.__class__.__name__} - {e}", exc_info=True)
                     raise AgentExecutionError(
                         detail=error_code,
                         original_error=e,
                         agent_name=self.__class__.__name__
                     ) from e
            elif isinstance(input_data, dict):
                 # Legacy Fallback? NO. Zero-Compromise means we MUST have a schema eventually.
                 # But for incremental migration, we allow dict if INPUT_SCHEMA is None.
                 pass
            # 1. Use Generic User Prompt (The System Instruction carries the context)
            user_prompt = "Proceed with your task according to the system instructions."

            # 3. Determine Output Schema (Subclasses must define this!)
            response_schema = self.get_response_schema()

            # 3.5 Lifecycle Hook: Prepare Context
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: prepare_context")
            additional_context = await self.prepare_context(input_data, execution_context, **kwargs)
            if additional_context:
                system_instruction = (system_instruction or "") + "\n\n" + additional_context
                logger.debug(f"[{self.__class__.__name__}] Appended dynamic context.")

            # 2. Get System Instruction (Check AFTER dynamic context injection)
            if not system_instruction:
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_MISSING_INSTRUCTION,
                    original_error=ValueError(
                        f"Agent {self.__class__.__name__} executed without system_instruction. "
                        "Strict mode requires DB-sourced prompts."
                    ),
                )

            # 3.5.5 Schema Injection (Modern Polish)
            if system_instruction and "{{SCHEMA_EXAMPLE}}" in system_instruction:
                if response_schema:
                    try:
                        # Pydantic v2: model_json_schema()
                        schema_dict = response_schema.model_json_schema()
                        schema_text = json.dumps(schema_dict, indent=2, ensure_ascii=False)
                        system_instruction = system_instruction.replace("{{SCHEMA_EXAMPLE}}", schema_text)
                        logger.info(
                            f"[{self.__class__.__name__}] Injected JSON Schema into {{SCHEMA_EXAMPLE}} placeholder."
                        )
                    except Exception as e:
                         logger.warning(f"[{self.__class__.__name__}] Failed to inject schema example: {e}")
                else:
                    logger.warning(
                        f"[{self.__class__.__name__}] Prompt has {{SCHEMA_EXAMPLE}} but no response_schema defined."
                    )


            # 3.6 Context Continuity Check (Transient Reasoning Trace)
            # Access trace from input_data or context?
            # Assuming input_data might contain 'last_reasoning_trace' if mapped?
            # Or execution_context?
            # For now, if we are strictly stateless, we depend on inputs.
            # However, prompt says "Remove all imports and type hints referring to WorkflowState."
            # So we check input_data or kwargs.
            if kwargs.get("pass_reasoning_token"):
                 pass # Already in kwargs
            else:
                 # Safe Access for InputT (Dict or Model)
                 trace = None
                 if isinstance(input_data, dict):
                     trace = input_data.get("last_reasoning_trace")
                 else:
                     trace = input_data.last_reasoning_trace
                 
                 if trace:
                    logger.info(f"[{self.__class__.__name__}] Chain of Thought: Injecting previous reasoning trace.")
                    kwargs["pass_reasoning_token"] = trace

            # --- LOGGING EXECUTION CONFIG ---
            conf_model = self.model
            conf_temp = kwargs.get("temperature", "Default")
            conf_tokens = kwargs.get("max_tokens", "Default")

            logger.info(f"[{self.__class__.__name__}] >>> EXECUTION START <<<")

            # Identify extras
            # Identify extras
            std_keys = {
                "temperature",
                "max_tokens",
                "pass_reasoning_token",
                "mock_identity",
                "system_instruction",
                "repository",
                "output_key",
                "usage_key",
                "execution_config",
                "step_id",
            }
            extras = {k: v for k, v in kwargs.items() if k not in std_keys}

            logger.info(
                f"[{self.__class__.__name__}] MODEL: {conf_model} | TEMP: {conf_temp} | "
                f"TOKENS: {conf_tokens} | EXTRAS: {extras}"
            )
            # --------------------------------

            if not self.llm_provider:
                error_msg = (
                    f"[{self.__class__.__name__}] LLM Provider not configured. Call set_model() before execute()."
                )
                logger.error(error_msg)
                raise AgentExecutionError(detail=ErrorCodes.AGENT_NOT_CONFIGURED, original_error=ValueError(error_msg))

            # 4. Call LLM (The "Mask" handles the details) — ASYNC WAIT
            kwargs["mock_identity"] = self.__class__.__name__

            response_obj = await self.llm_provider.generate(
                prompt=user_prompt,
                system_instruction=system_instruction,
                response_schema=response_schema,
                **kwargs,
            )

            # Handle Response Content
            if response_schema:
                # OPTIMIZATION: Use pre-parsed content if available (Instructor Pattern)
                if response_obj.parsed_content is not None:
                    logger.debug(f"[{self.__class__.__name__}] Structured Output used directly (No re-parsing).")
                    response_data = response_obj.parsed_content
                else:
                    # Provider ensures content is valid JSON string if schema was used

                    try:
                        response_data = json.loads(response_obj.content)
                    except json.JSONDecodeError as e:
                        # STRICT MODE: If json keys are malformed after provider, we fail.
                        error_code = ErrorCodes.AGENT_RESPONSE_MALFORMED
                        logger.error(f"{error_code}: Failed to parse JSON content from provider - {e}", exc_info=True)
                        raise AgentExecutionError(detail=error_code, original_error=e) from e
                    except Exception as e:
                        # General fallback for other errors during parsing
                        error_code = ErrorCodes.AGENT_RESPONSE_PARSING_FAILED
                        logger.error(f"{error_code}: Unexpected error during JSON parsing - {e}", exc_info=True)
                        raise AgentExecutionError(detail=error_code, original_error=e) from e
            else:
                response_data = response_obj.content

            # 4.5 Capture Usage/Cost (Return in metadata or separate logging?)
            # Since we return a dict, we can't update state directly.
            # Should we attach usage to the response?
            # For now, we just log it as the prompt requested "return its result".
            # If the engine handles usage, it needs parsing.
            # But the prompt said: "The agent should no longer modify state objects; it should purely return its result as a dictionary (or Pydantic model)."
            # We assume usage tracking is handled by the caller or logging for now.
            logger.info(f"BaseAgent processing usage. Response token_usage: {response_obj.token_usage}")

            # 4.6 Capture Audit Logs (Prompts)
            if hasattr(response_obj, "messages") and response_obj.messages:
                 # DE-DUPLICATION LOGIC (Jan 2026):
                 # Replace massive input strings (like full history_text) with references <<REFERENCE: key>>
                 # to keep the audit log readable. The full content exists in execution['inputs'].
                 sanitized_messages = []
                 try:
                     import copy
                     sanitized_messages: list[dict[str, Any]] = copy.deepcopy(response_obj.messages)

                     for msg in sanitized_messages:
                         if "content" in msg and isinstance(msg["content"], str):
                             content_str = msg["content"]

                             # Handle Pydantic Models or Dicts
                             start_inputs: Any = input_data
                             if isinstance(start_inputs, BaseModel):
                                 start_inputs = start_inputs.model_dump()

                             if isinstance(start_inputs, dict):
                                 for key, value in start_inputs.items():
                                     # Only replace if value is a long string (avoid replacing 'id' or '1')
                                     if isinstance(value, str) and len(value) > 100:
                                         if value in content_str:
                                             # Replace with reference
                                             content_str = content_str.replace(value, f"<<REFERENCE: {key}>>")
                             msg["content"] = content_str
                 except Exception as e:
                     logger.warning(f"Audit log sanitization failed: {e}. Saving raw logs.")
                     sanitized_messages = response_obj.messages

                     # Convert to AuditLogEntry (Strict Schema)
                     audit_entries = []
                     timestamp_now = datetime.now(timezone.utc)

                     for msg in sanitized_messages:
                         try:
                             role = msg.get("role", "unknown")
                             content = msg.get("content", "")
                             if not isinstance(content, str):
                                 content = str(content)

                             entry = AuditLogEntry(
                                 timestamp=timestamp_now,
                                 level="INFO", # Default for chat logs
                                 message=content[:5000], # Truncate massive logs
                                 context={"original_role": role}
                             )
                             audit_entries.append(entry)
                         except Exception as e:
                             logger.warning(f"Failed to convert message to AuditLogEntry: {e}")

                     if isinstance(response_data, dict):
                         if "metadata" not in response_data:
                             response_data["metadata"] = {}
                         if isinstance(response_data["metadata"], dict):
                             response_data["metadata"]["audit_logs"] = audit_entries
                     elif isinstance(response_data, BaseModel):
                         if hasattr(response_data, "metadata"):
                             if isinstance(response_data.metadata, dict):
                                 response_data.metadata["audit_logs"] = audit_entries
                             elif hasattr(response_data.metadata, "audit_logs"): # Check field existence first
                                 # We enabled extra="allow" in Metadata but strict validation means type must match
                                 try:
                                    # If metadata is a model (Metadata), set the field
                                    if hasattr(response_data.metadata, "model_dump"):
                                         # Pydantic model
                                         # We can't set directly if it's frozen, but BaseAgent constructs it?
                                         # Metadata is frozen=False.
                                         response_data.metadata.audit_logs = audit_entries
                                    else:
                                         # Unknown type
                                         pass
                                 except Exception as e:
                                    logger.warning(f"Could not attach audit logs to metadata model: {e}")

             # FORCE SYSTEM AUTHORITY (Metadata & Checksums)
            if response_data is not None:
                response_data = self._apply_python_authority(response_data, token_usage=getattr(response_obj, "token_usage", None))



            # 6. Lifecycle Hook: Post Process (HEALING PATTERN)
            # STRATEGY: "Late Validation"
            # We intentionally keep response_data as a Dict (if possible) during this phase.
            # This allows the 'post_process' hook to "heal" structural errors (like missing IDs or 
            # malformed keys) that would otherwise cause Pydantic validation to crash immediately.
            # The Agent is responsible for ensuring the data is valid BEFORE the strict check below.
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: post_process")

            # SCRUBBER (Jan 2026): Remove 'instructor' library prompt leakage
            if response_data is not None:
                response_data = self._scrub_prompt_leakage(response_data)

            # HEALING STEP: Fix structure before validation
            response_data = self.post_process(response_data)

            # 7. LATE VALIDATION (Schema Enforcement)
            # Since Provider no longer enforces schema (to allow healing), we must do it here.
            # This is the "Fail Fast" gate: If data is still invalid after healing, we crash.
            # FIX (Jan 2026): Use explicit None check to catch empty dicts {} which are Falsy.
            if response_schema and response_data is not None:
                try:
                    # If it's already a model, we are good (provider might have done it distinctively)
                    if isinstance(response_data, BaseModel):
                        pass
                    else:
                        # Convert dict to Model (Validation happens here)
                        response_data = response_schema.model_validate(response_data)
                        logger.info(f"[{self.__class__.__name__}] Late Validation Successful: {response_schema.__name__}")
                except ValidationError as e:
                    # If healing failed to fix it, we crash now.
                    error_code = ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED
                    logger.error(f"{error_code}: Post-Healing Validation Failed - {e}", exc_info=True)
                    raise AgentExecutionError(detail=error_code, original_error=e) from e

            # 8. STRICT TYPE SAFEGUARD (Zero-Compromise)
            # Child agents rely on us to return the correct Pydantic Model.
            # If we somehow reached here with a dict when a schema is required, we must crash.
            if response_schema and not isinstance(response_data, BaseModel):
                 # This theoretically shouldn't happen due to Late Validation above, 
                 # but this protects against logic regressions or loose typing.
                 error_msg = f"CRITICAL: {self.__class__.__name__} violated strict return contract. Expected {response_schema.__name__}, got {type(response_data)}."
                 logger.critical(error_msg)
                 raise AgentExecutionError(
                     detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                     original_error=TypeError(error_msg),
                     agent_name=self.__class__.__name__
                 )

            return response_data


        except AgentExecutionError:
            # Pass through already wrapped errors
            raise

        except (
            socket.gaierror,
            urllib3.exceptions.NameResolutionError,
            requests.exceptions.ConnectionError,
            litellm.APIConnectionError,
        ) as e:
            # Network / Offline Handling
            error_code = ErrorCodes.NETWORK_UNAVAILABLE

            # Use LocalizationService to build bilingual error
            msg_fi = LocalizationService.get("network_error_msg", "fi")
            msg_en = LocalizationService.get("network_error_msg", "en")
            friendly_msg = f"{msg_en} / {msg_fi}"

            # Log full stack trace for debugging
            logger.error(f"{error_code}: {friendly_msg} - Cause: {e}", exc_info=True)

            # Raise with clean message for UI but original error preserved
            raise AgentExecutionError(
                detail=error_code,
                original_error=e,
                agent_name=self.__class__.__name__
            ) from e

        except ValidationError as e:
            # ECHO PROTOCOL: Log First, Then Raise
            error_code = ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED
            logger.error(f"{error_code}: Output validation failed - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e

        except Exception as e:
            # ECHO PROTOCOL: Safety Net
            # Use standard error code for Frontend, specific details for Backend logs
            error_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
            logger.error(f"{error_code}: Unexpected failure in {self.__class__.__name__} - {e}", exc_info=True)
            raise AgentExecutionError(
                detail=error_code,
                original_error=e,
                agent_name=self.__class__.__name__
            ) from e

    async def prepare_context(self, input_data: InputT, execution_context: dict[str, Any] | None, **kwargs: Any) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Override to inject dynamic context.

        Args:
            input_data (InputT): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            Optional[str]: Text to append to system instruction.

        """
        return None

    def post_process(self, response_data: Any) -> Any:
        """Lifecycle Hook: Post-Execution.

        Override to refine response.

        Args:
            response_data (Any): The result.

        Returns:
            Any: Processed result.

        """
        return response_data

    def construct_user_prompt(self, input_data: Any) -> str:
        """Deprecated: User prompts are now generic.

        Args:
            input_data: Context.

        Returns:
            str: Prompt text.

        """
        # Strict Mode: No implicit prompts.
        return ""

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model that this agent expects as output from LLM.
        
        If DTO_SCHEMA is defined, returns that (Content Only).
        Otherwise falls back to OUTPUT_SCHEMA (Legacy).
        """
        return self.DTO_SCHEMA or self.OUTPUT_SCHEMA

    def get_system_instruction(self) -> str:
        """Retrieves the default system instruction.

        Returns:
            str: Default instruction text.

        """
        # Strict Mode: No hardcoded defaults.
        return ""

    def get_user_prompt_template(self) -> str:
        """Returns a string representation of the user prompt template for UI preview.

        Returns:
            str: Template preview.

        """
        return ""

    def _scrub_prompt_leakage(self, data: Any) -> Any:
        """Recursively removes 'instructor' library prompt leakage from strings."""
        leak_phrases = [
            "Return the correct JSON response.",
            "Return the correct JSON",
            "Example JSON:",
            "Here is the correct JSON response:",
        ]

        if isinstance(data, str):
            for phrase in leak_phrases:
                if phrase in data:
                    data = data.replace(phrase, "").strip()
            return data

        if isinstance(data, dict):
            return {k: self._scrub_prompt_leakage(v) for k, v in data.items()}

        if isinstance(data, list):
            return [self._scrub_prompt_leakage(item) for item in data]

        if isinstance(data, BaseModel):
            try:
                updates = {}
                has_changes = False

                # Iterate over fields to check for changes
                for name, field_info in data.model_fields.items():
                    # Strict: Accessing fields by name for recursive scrubbing
                    val = getattr(data, name)
                    # Recursively scrub
                    new_val = self._scrub_prompt_leakage(val)

                    # Check for change (simple equality check might be expensive deeply, but necessary)
                    # We can rely on reference or value equality
                    if new_val != val:
                        updates[name] = new_val
                        has_changes = True

                if has_changes:
                     # Check if frozen
                     if data.model_config.get("frozen"):
                         return data.model_copy(update=updates)
                     else:
                         for k, v in updates.items():
                             setattr(data, k, v)
                         return data

                return data
            except Exception as e:
                logger.warning(f"[{self.__class__.__name__}] Scrubbing failed on model: {e}")
                return data

        return data
