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

# 4. Logger
logger = logging.getLogger(__name__)


class BaseAgent(BaseComponent):
    """Abstract base class for all Cognitive Quorum agents.

    Handles LLM interaction via the Provider Pattern.
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

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:  # type: ignore[override]
        """Standard execution entry point.

        Takes input dict, processes it, and returns the result dict.

        Args:
            input_data (dict): The resolved input variables.
            execution_context (Optional[dict]): Access to repo/config.
            system_instruction (Optional[str]): Prompt override.
            **kwargs: Additional parameters for LLM.

        Returns:
            dict: The execution result (response data).

        Raises:
            Exception: If execution fails.

        """
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
            additional_context = await self.prepare_context(input_data, execution_context, **kwargs)
            if additional_context:
                system_instruction = (system_instruction or "") + "\n\n" + additional_context
                logger.debug(f"[{self.__class__.__name__}] Appended dynamic context.")

            # 3.5.5 Schema Injection (Modern Polish)
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
            # Access trace from input_data or context? 
            # Assuming input_data might contain 'last_reasoning_trace' if mapped?
            # Or execution_context? 
            # For now, if we are strictly stateless, we depend on inputs.
            # However, prompt says "Remove all imports and type hints referring to WorkflowState."
            # So we check input_data or kwargs.
            if kwargs.get("pass_reasoning_token"):
                 pass # Already in kwargs
            elif input_data.get("last_reasoning_trace"):
                logger.info(f"[{self.__class__.__name__}] Chain of Thought: Injecting previous reasoning trace.")
                kwargs["pass_reasoning_token"] = input_data["last_reasoning_trace"]

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

            # 4.5 Capture Usage/Cost (Return in metadata or separate logging?)
            # Since we return a dict, we can't update state directly.
            # Should we attach usage to the response?
            # For now, we just log it as the prompt requested "return its result".
            # If the engine handles usage, it needs parsing.
            # But the prompt said: "The agent should no longer modify state objects; it should purely return its result as a dictionary (or Pydantic model)."
            # We assume usage tracking is handled by the caller or logging for now.
            logger.info(f"BaseAgent processing usage. Response token_usage: {response_obj.token_usage}")

             # FORCE SYSTEM AUTHORITY (Metadata & Checksums)
            if response_data:
                self._apply_python_authority(response_data)
            
            # 6. Lifecycle Hook: Post Process
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: post_process")
            response_data = self.post_process(response_data)

            logger.info(f"[{self.__class__.__name__}] Execution completed.")
            
            # Return Pydantic model as dict or strict return?
            # "The agent should no longer modify state objects; it should purely return its result as a dictionary (or Pydantic model)."
            # "Update the execute method logic: ... return the validated response_data directly."
            # "signature... -> dict"
            
            if isinstance(response_data, BaseModel):
                return response_data.model_dump()
                
            return response_data

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

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Override to inject dynamic context.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
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
