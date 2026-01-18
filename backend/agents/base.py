"""Base Agent implementation."""

from __future__ import annotations

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel, ValidationError

from backend.core.component import BaseComponent

# 3. Local Imports
from backend.exceptions import AgentExecutionError

# Use string forward reference to avoid circular import if needed, or if Provider is defined there.
# But LLMFactory is imported.
from backend.llm.provider import LLMFactory, LLMProvider
from backend.models.state import WorkflowState

# 4. Logger
logger = logging.getLogger(__name__)


class BaseAgent(BaseComponent[WorkflowState]):
    """Abstract base class for all Cognitive Quorum agents.

    Handles LLM interaction via the Provider Pattern and manages WorkflowState.
    """

    state_field: str | None = None

    # --- CONTRACTS (Data Flow Validation) ---
    # List of keys (in state or inputs) that this agent REQUIRES to run.
    REQUIRES_KEYS: list[str] = []

    # List of keys (in state) that this agent PRODUCES upon success.
    PRODUCES_KEYS: list[str] = []

    # Optional Pydantic Models for Schema Validation
    INPUT_SCHEMA: type[BaseModel] | None = None
    OUTPUT_SCHEMA: type[BaseModel] | None = None

    def __init__(self, model: str | None = None, provider: str | None = None):
        """Initializes the agent with an optional specific model strategy.

        Args:
            model (Optional[str]): The model identifier (e.g. 'gemini-1.5-pro').
            provider (Optional[str]): The provider (e.g. 'google').

        """
        self.model = model
        self.provider_type = provider or "vertex_ai"
        self.llm_provider: LLMProvider | None = None

        # ZERO-FALLBACK: Agents initialized via Factory might have model=None.
        # We allow this, but execution will fail if model is not set via set_model().

        if model:
            self.llm_provider = LLMFactory.create_provider(self.provider_type, model)
        else:
            self.llm_provider = None

    def set_model(
        self,
        model_name: str,
        provider: str | None = None,
        usage_service: Any = None,
        organization_id: str | None = None,
    ):
        """Dynamically updates the agent's model preference and ensures LLMProvider is ready.

        Args:
            model_name (str): The new model name.
            provider (Optional[str]): The provider type.
            usage_service (Any): UsageService instance for tracking.
            organization_id (Optional[str]): Contextual Org ID.
        """
        self.model = model_name
        if provider:
            self.provider_type = provider

        current_provider_type = self.provider_type or "vertex_ai"

        # Logic: If provider exists and matches usage, AND organization matches, keep it.
        # But organization_id changes per execution, so we almost always need to update/recreate if context changes.
        # Or we rely on the fact that we overwrite it.
        # Ideally, we should check if current provider has same org_id.

        # Simpler approach: Always recreate if dependencies provided, to ensure context is fresh.
        # Optimizing creation is secondary to correctness.
        self._create_provider(current_provider_type, model_name, usage_service, organization_id)

    def _create_provider(
        self,
        provider_type: str,
        model_name: str,
        usage_service: Any = None,
        organization_id: str | None = None,
    ):
        """Helper to instantiate and assign the LLM provider.

        Args:
            provider_type (str): Provider key (e.g. 'google', 'openai').
            model_name (str): The specific model ID.
            usage_service (Any): usage service.
            organization_id (str): org id.
        """
        try:
            self.llm_provider = LLMFactory.create_provider(
                provider_type=provider_type,
                model_name=model_name,
                usage_service=usage_service,
                organization_id=organization_id,
            )
            logger.debug(
                f"[BaseAgent] Provider initialized with {model_name} (Type: {provider_type}, Org: {organization_id})"
            )
        except Exception as e:
            logger.error(f"[BaseAgent] Failed to create provider in set_model: {e}")

    def _apply_python_authority(self, data: Any) -> None:
        """Injects system-authoritative data (Time, Identity, Checksums) into the response.

        Overrides any LLM-hallucinated values for these fields.
        Handles both raw dicts and Pydantic models.
        """
        from datetime import datetime, timezone
        import hashlib
        import json

        # 1. TIME & IDENTITY AUTHORITY
        utc_now = datetime.now(timezone.utc).isoformat()
        agent_name = self.__class__.__name__
        env_context = "Internal"
        
        # --- CASE A: Pydantic Model ---
        if isinstance(data, BaseModel):
            if hasattr(data, "metadata") and data.metadata:
                data.metadata.luontiaika = utc_now
                data.metadata.agentti = agent_name
                if not data.metadata.suoritus_ymparisto:
                    data.metadata.suoritus_ymparisto = env_context
                # Ensure fields exist
                if not getattr(data.metadata, "vaihe", None):
                    data.metadata.vaihe = 1
                if not getattr(data.metadata, "versio", None):
                    data.metadata.versio = "2.0"
                
                # Checksum for Model
                try:
                    # Dump to dict, exclude checksum, hash
                    as_dict = data.model_dump()
                    if "semanttinen_tarkistussumma" in as_dict:
                        del as_dict["semanttinen_tarkistussumma"]
                    # Hash
                    dump = json.dumps(as_dict, sort_keys=True, default=str)
                    checksum = hashlib.sha256(dump.encode("utf-8")).hexdigest()
                    
                    if hasattr(data, "semanttinen_tarkistussumma"):
                        data.semanttinen_tarkistussumma = checksum
                        logger.debug(f"[{self.__class__.__name__}] Calc Checksum (Model): {checksum[:8]}...")
                        logger.debug(f"[{self.__class__.__name__}] Calc Checksum (Model): {checksum[:8]}...")
                except Exception as e:
                    # STRICT MODE: Data integrity is critical.
                    error_msg = f"[{self.__class__.__name__}] Critical: Failed to calculate authoritative checksum (Model). Data integrity compromised."
                    logger.critical(f"{error_msg} Error: {e}")
                    raise ValueError(error_msg) from e

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
                logger.debug(f"[{self.__class__.__name__}] Calc Checksum (Dict): {checksum[:8]}...")
            except Exception as e:
                # STRICT MODE: Data integrity is critical.
                error_msg = f"[{self.__class__.__name__}] Critical: Failed to calculate authoritative checksum. Data integrity compromised."
                logger.critical(f"{error_msg} Error: {e}")
                raise ValueError(error_msg) from e

    async def _update_state(
        self, state: WorkflowState, response_data: Any, output_key: str | None = None, **kwargs
    ) -> WorkflowState:
        """Updates the WorkflowState with the LLM response.

        Generic implementation: Uses self.state_field and self.get_response_schema().

        Args:
            state (WorkflowState): Current state.
            response_data (Any): Raw data dictionary from LLM.
            output_key (Optional[str]): Override for self.state_field.
            **kwargs: Additional parameters.

        Returns:
            WorkflowState: The updated state object.

        Raises:
            Exception: If schema validation fails.

        """
        target_field = output_key or self.state_field
        SchemaClass = self.get_response_schema()

        if target_field and SchemaClass:
            try:
                # Validate and create Pydantic model
                # Ensure response_data is a dict (JSON has been parsed)
                if not isinstance(response_data, dict):
                    # Strict Mode: This assumes provider returns parsed JSON if schema is present.
                    # If prompt-based, it returns dict.
                    pass

                # FORCE SYSTEM AUTHORITY (Metadata & Checksums)
                if response_data:
                    self._apply_python_authority(response_data)

                # STRICT MODERNIZATION: Only accept pre-hydrated Pydantic objects
                if isinstance(response_data, SchemaClass):
                    validated_data = response_data
                else:
                    # STRICT MODE VIOLATION: We no longer accept raw dicts here.
                    # LLMProvider MUST handle hydration.
                    error_msg = f"Strict Mode Violation: Expected {SchemaClass.__name__}, got {type(response_data).__name__}. Check LLMProvider hydration."
                    logger.error(f"[{self.__class__.__name__}] {error_msg}")
                    raise AgentExecutionError(detail="AGENT_STRICT_MODE_VIOLATION", original_error=TypeError(error_msg))

                # Check if state has this field
                if hasattr(state, target_field):
                    logger.debug(f"_update_state [id={id(state)}] Setting {target_field}")
                    setattr(state, target_field, validated_data)
                    logger.info(f"[{self.__class__.__name__}] Updated state.{target_field}")
                else:
                    logger.warning(
                        f"[{self.__class__.__name__}] State model missing field '{target_field}'. "
                        "Assigning to aux_data."
                    )
                    state.aux_data[target_field] = validated_data.model_dump()

                return state
            except Exception as e:
                error_code = "STATE_UPDATE_FAILED"
                logger.error(f"{error_code}: Generic state update failed - {e}", exc_info=True)
                raise AgentExecutionError(detail=error_code, original_error=e) from e

        raise NotImplementedError(f"[{self.__class__.__name__}] must define 'state_field' or override '_update_state'.")

    async def execute(
        self,
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:  # type: ignore[override]
        """Standard execution entry point.

        Takes the entire WorkflowState, processes it, and returns the updated state.

        Args:
            state (WorkflowState, optional): The current workflow context.
            system_instruction (Optional[str]): Prompt override.
            **kwargs: Additional parameters for LLM (e.g. max_tokens, temperature, output_key).

        Returns:
            WorkflowState: Updated state after execution.

        Raises:
            Exception: If execution fails.

        """
        if state is None:
            raise ValueError(f"[{self.__class__.__name__}] Execution requires a valid WorkflowState.")

        logger.info(f"[{self.__class__.__name__}] Starting execution...")
        try:
            # 1. Use Generic User Prompt (The System Instruction carries the context)
            user_prompt = "Proceed with your task according to the system instructions."

            # 2. Get System Instruction
            if not system_instruction:
                system_instruction = "You are a helpful AI assistant."

            # 3. Determine Output Schema (Subclasses must define this!)
            response_schema = self.get_response_schema()

            # 3.5 Lifecycle Hook: Prepare Context
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: prepare_context")
            additional_context = await self.prepare_context(state, **kwargs)
            if additional_context:
                system_instruction = (system_instruction or "") + "\n\n" + additional_context
                logger.debug(f"[{self.__class__.__name__}] Appended dynamic context.")

            # 3.5.5 Schema Injection (Modern Polish)
            # If the prompt explicitly asks for {{SCHEMA_EXAMPLE}}, we provide it textually
            # to reinforce the API-level constraint.
            if system_instruction and "{{SCHEMA_EXAMPLE}}" in system_instruction:
                if response_schema:
                    import json
                    try:
                        # Pydantic v2: model_json_schema()
                        schema_dict = response_schema.model_json_schema()
                        schema_text = json.dumps(schema_dict, indent=2, ensure_ascii=False)
                        system_instruction = system_instruction.replace("{{SCHEMA_EXAMPLE}}", schema_text)
                        logger.info(f"[{self.__class__.__name__}] Injected JSON Schema into {{SCHEMA_EXAMPLE}} placeholder.")
                    except Exception as e:
                         logger.warning(f"[{self.__class__.__name__}] Failed to inject schema example: {e}")
                else:
                    logger.warning(f"[{self.__class__.__name__}] Prompt has {{SCHEMA_EXAMPLE}} but no response_schema defined.")


            # 3.6 Context Continuity Check (Transient Reasoning Trace)
            if state.last_reasoning_trace:
                logger.info(f"[{self.__class__.__name__}] Chain of Thought: Injecting previous reasoning trace.")
                kwargs["pass_reasoning_token"] = state.last_reasoning_trace
            else:
                logger.debug(f"[{self.__class__.__name__}] No previous reasoning trace available.")

            # --- LOGGING EXECUTION CONFIG ---
            conf_model = self.model
            conf_temp = kwargs.get("temperature", "Default")
            conf_tokens = kwargs.get("max_tokens", "Default")

            logger.info(f"[{self.__class__.__name__}] >>> EXECUTION START <<<")
            logger.info(f"[{self.__class__.__name__}] MODEL: {conf_model} | TEMP: {conf_temp} | TOKENS: {conf_tokens}")
            # --------------------------------

            if not self.llm_provider:
                error_msg = (
                    f"[{self.__class__.__name__}] LLM Provider not configured. Call set_model() before execute()."
                )
                logger.error(error_msg)
                raise AgentExecutionError(detail="AGENT_NOT_CONFIGURED", original_error=ValueError(error_msg))

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
                    import json

                    try:
                        response_data = json.loads(response_obj.content)
                    except json.JSONDecodeError as e:
                        # STRICT MODE: If json keys are malformed after provider, we fail.
                        error_code = "AGENT_RESPONSE_MALFORMED"
                        logger.error(f"{error_code}: Failed to parse JSON content from provider - {e}", exc_info=True)
                        raise AgentExecutionError(detail=error_code, original_error=e) from e
                    except Exception as e:
                        # General fallback for other errors during parsing
                        error_code = "AGENT_RESPONSE_PARSING_FAILED"
                        logger.error(f"{error_code}: Unexpected error during JSON parsing - {e}", exc_info=True)
                        raise AgentExecutionError(detail=error_code, original_error=e) from e
            else:
                response_data = response_obj.content

            # Store reasoning_token if captured (Hot Potato Update)
            reasoning_source = None
            if response_obj.reasoning_token:
                logger.info(
                    f"[{self.__class__.__name__}] Reasoning Token captured (Size: {len(response_obj.reasoning_token)})"
                )
                state.last_reasoning_trace = response_obj.reasoning_token
                reasoning_source = response_obj.reasoning_token
            # Fallback: Check if structured output contains the trace (Common in Gemini/OpenAI Pydantic mode)
            elif isinstance(response_data, dict) and response_data.get("reasoning_trace"):
                logger.info(f"[{self.__class__.__name__}] Reasoning extracted from Structured Output JSON.")
                state.last_reasoning_trace = response_data["reasoning_trace"]
                reasoning_source = response_data["reasoning_trace"]

            if reasoning_source:
                # Also store in historical context for debugging
                target_key = kwargs.get("output_key") or self.state_field or self.__class__.__name__
                state.reasoning_context[target_key] = {
                    "token": reasoning_source,
                    "model": self.model or "unknown",
                    "provider": self.provider_type or "google",
                }

            # 4.5 Capture Usage/Cost
            logger.info(f"BaseAgent processing usage. Response token_usage: {response_obj.token_usage}")
            if response_obj.token_usage:
                # PRIORITIZE usage_key for unique tracking (e.g. step_id), fallback to output_key/class
                step_key = (
                    kwargs.get("usage_key") or kwargs.get("output_key") or self.state_field or self.__class__.__name__
                )
                costs = response_obj.token_usage  # Should be dict from LiteLLMProvider
                logger.info(f"Processing costs for {step_key}: {costs}")
                state.usage[step_key] = {
                    "completion_tokens": costs.get("completion_tokens", 0),
                    "prompt_tokens": costs.get("prompt_tokens", 0),
                    "total_cost": costs.get("total_cost", 0.0),
                    "model": self.model or "unknown",
                }
                logger.info(f"[{self.__class__.__name__}] Usage tracked: {costs.get('total_cost', 0.0)} USD")
            else:
                logger.info("No token_usage found in response.")

            # 5. Update State
            output_key = kwargs.get("output_key")
            # Remove output_key from kwargs to avoid "multiple values" error when passing both explicit arg and **kwargs
            update_kwargs = {k: v for k, v in kwargs.items() if k != "output_key"}
            updated_state = await self._update_state(state, response_data, output_key=output_key, **update_kwargs)

            # 6. Lifecycle Hook: Post Process
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: post_process")
            updated_state = self.post_process(updated_state)

            logger.info(f"[{self.__class__.__name__}] Execution completed.")
            return updated_state

        except ValidationError as e:
            # ECHO PROTOCOL: Log First, Then Raise
            error_code = "AGENT_SCHEMA_VALIDATION_FAILED"
            logger.error(f"{error_code}: Output validation failed - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e

        except Exception as e:
            # ECHO PROTOCOL: Safety Net
            # Use standard error code for Frontend, specific details for Backend logs
            error_code = "AGENT_EXECUTION_CRITICAL"
            logger.error(f"{error_code}: Unexpected failure in {self.__class__.__name__} - {e}", exc_info=True)
            raise AgentExecutionError(
                detail=error_code,
                original_error=e,
                agent_name=self.__class__.__name__
            ) from e

    async def prepare_context(self, state: WorkflowState, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Override to inject dynamic context.

        Args:
            state (WorkflowState): Current state.
            **kwargs: execution arguments.

        Returns:
            Optional[str]: Text to append to system instruction.

        """
        return None

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """Lifecycle Hook: Post-Execution.

        Override to refine state or perform calculations.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Processed state.

        """
        return state

    def construct_user_prompt(self, state: WorkflowState) -> str:
        """Deprecated: User prompts are now generic.

        Args:
            state (WorkflowState): Context.

        Returns:
            str: Prompt text.

        """
        return "Proceed with your task."

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model that this agent expects as output.

        Returns:
            Optional[Type[BaseModel]]: The Pydantic output schema class.

        """
        return None

    def get_system_instruction(self) -> str:
        """Retrieves the default system instruction.

        Returns:
            str: Default instruction text.

        """
        return "You are a helpful AI assistant."

    def get_user_prompt_template(self) -> str:
        """Returns a string representation of the user prompt template for UI preview.

        Returns:
            str: Template preview.

        """
        return "Proceed with your task according to the system instructions."
