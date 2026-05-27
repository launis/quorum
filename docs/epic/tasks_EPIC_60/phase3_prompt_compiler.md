# Phase 3: Prompt Compiler and Executor (Kääntäjämoottori ja Executor)

This sub-plan addresses **Phase 3: Kääntäjämoottorin ja Executorin Päivitys (Prompt Compiler Evolution)** from Epic 60. It updates the LLM Strategy Executor and Prompt Construction engine to parse the decoupled blocks, enforce XML boundaries, and maximize prompt caching efficiency via strict parameter isolation.

## System Invariants & Rules
* **Rule 1: Role Segregation & Fencing (05_llm_architecture.md)**: All user-supplied inputs must be strictly enclosed within `<user_payload>...</user_payload>` tags as a firewall against prompt injection.
* **Rule 2: High-Fidelity Prompting & Caching (05_llm_architecture.md)**: All dynamic parameters and execution-time variables must be strictly isolated into an `<execution_parameters>` XML tag at the very beginning of the user payload. Direct system prompts must remain 100% static to leverage LLM Context Caching.
* **Rule 3: LLM Structured Execution Mandate (05_llm_architecture.md)**: Constrained decoding via `executor.execute_structured_task()` or `executor.execute_chat_task()` is mandatory. Manual parsing of JSON using regex or self-healing loops is banned.
* **Rule 4: Prompt Compiler Immutability (01-python-backend.md)**: Do NOT modify `prompt_compiler.py` itself. Build compilation logic inside the Strategy and PromptFactory wrappers unless explicit permission is granted.

---

## Proposed Changes

### [Component: Orchestrator Service]
We will update `llm.py` and `prompt_factory.py` to compile prompts using role blocks and global protocol guidelines decoupled from domain criteria.

#### [MODIFY] [prompt_factory.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py)
* **Step 1 (Source: Epic Phase 2, Toimenpide 2)**: Update the signature of `PromptFactory.build` and prompt assembly logic to isolate instructions and support role and protocol blocks.
  ```python
  # Targets c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\prompt_factory.py
  @classmethod
  def build(
      cls,
      compiler: Any,
      role_block: PromptBlock | None,
      protocol_block: PromptBlock | None,
      criteria_blocks: list[PromptBlock],
      target_locale: str,
      effective_mcp_tools: list[str] | None,
      input_mappings: dict[str, Any],
      llm_context_data: dict[str, Any],
      expected_inputs: list[Any] | None,
      has_shuffled_atoms: bool = False,
      execution_id: str | None = None,
  ) -> PromptPayload:
      # Isolate dynamic parameters in <execution_parameters> to optimize prefix caching
      execution_time = cls._resolve_execution_time(llm_context_data, execution_id)
      
      # 1. Base System Prompt construction
      base_system_prompt = "You are a highly accurate, structured evaluation assistant."
      if role_block and role_block.ai_description:
          base_system_prompt += f"\n\n<ROLE_DIRECTIVE>\n{role_block.ai_description}\n</ROLE_DIRECTIVE>"
      
      if protocol_block and protocol_block.ai_description:
          base_system_prompt += f"\n\n<EXTRACTION_PROTOCOL>\n{protocol_block.ai_description}\n</EXTRACTION_PROTOCOL>"

      # Compile other static matrix instructions
      static_instructions = compiler.compile_static_instructions(criteria_blocks, target_locale)
      if static_instructions:
          base_system_prompt += f"\n\n<CRITERIA_GUIDELINES>\n{static_instructions}\n</CRITERIA_GUIDELINES>"

      mcp_instruction = compiler.generate_mcp_instruction(effective_mcp_tools)
      if mcp_instruction:
          base_system_prompt += f"\n\n{mcp_instruction}"

      # 2. User Payload construction with strict fencing
      exec_params = f"<execution_parameters>\n<target_locale>{target_locale}</target_locale>\n"
      if execution_time:
          exec_params += f"<document_date>{execution_time}</document_date>\n"
      exec_params += "</execution_parameters>\n"

      xml_ctx = compiler.build_xml_context(
          input_mappings=input_mappings,
          state_data=llm_context_data,
          target_locale=target_locale,
          expected_inputs=expected_inputs,
      )

      # Fence raw user payloads securely
      user_payload = f"{exec_params}\n<source_data>\n{xml_ctx}\n</source_data>"

      dynamic_instructions = compiler.compile_dynamic_instructions(
          criteria_blocks, target_locale, execution_time=execution_time
      )
      if dynamic_instructions:
          user_payload += f"\n\n<RUNTIME_AWARENESS>\n{dynamic_instructions}\n</RUNTIME_AWARENESS>"

      # Generate atom maps for matrix alignment
      atom_to_block_ids = cls._generate_atom_map(criteria_blocks)

      return PromptPayload(
          base_system_prompt=base_system_prompt,
          user_payload=user_payload,
          atom_to_block_ids=atom_to_block_ids,
      )
  ```

#### [MODIFY] [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py)
* **Step 2 (Source: Epic Phase 2, Toimenpide 1)**: Update `LLMNodeStrategy.execute` to retrieve `role_block_id` and `extraction_protocol_block_id` from the database.
  ```python
  # Targets c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py
  # Old:
  # criteria_blocks_models = []
  # for m_id in step_obj.prompt_blocks:
  #     ...
  
  # New:
  role_block = None
  if step_obj.role_block_id:
      role_block = block_map.get(step_obj.role_block_id)
      if not role_block:
          raise ConfigurationError(
              f"Role Block '{step_obj.role_block_id}' not found.",
              details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
          )

  protocol_block = None
  if step_obj.extraction_protocol_block_id:
      protocol_block = block_map.get(step_obj.extraction_protocol_block_id)
      if not protocol_block:
          raise ConfigurationError(
              f"Extraction Protocol Block '{step_obj.extraction_protocol_block_id}' not found.",
              details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
          )

  criteria_blocks_models = []
  for m_id in step_obj.criteria_block_ids:
      b = block_map.get(m_id)
      if b:
          criteria_blocks_models.append(b)
      else:
          raise ConfigurationError(
              f"Criteria PromptBlock '{m_id}' not found.",
              details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
          )

  criteria_blocks = sorted(criteria_blocks_models, key=lambda x: str(x.id or ""))
  ```
* **Step 3 (Source: Epic Phase 2, Toimenpide 1)**: Pass the newly loaded decoupled prompt blocks into `PromptFactory.build`.
  ```python
  # Targets c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py
  prompt_payload = PromptFactory.build(
      compiler=self.compiler,
      role_block=role_block,
      protocol_block=protocol_block,
      criteria_blocks=criteria_blocks,
      target_locale=target_locale,
      effective_mcp_tools=effective_mcp_tools,
      input_mappings=input_mappings,
      llm_context_data=llm_context_data,
      expected_inputs=context.expected_inputs,
      has_shuffled_atoms=has_shuffled_atoms,
      execution_id=context.execution_id,
  )
  ```

---

## Testing & Quality Gate Plan

### Automated Verification
1. **Prompt Compilation Unit Tests**:
   Create mock matrices and assert that the generated system prompt and user payload structure are composed of XML-fenced boundaries and contain both the protocol block instructions and criteria rules correctly.
   ```powershell
   uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_prompt_factory.py -v
   ```
2. **Strategy Loop verification**:
   Audit logic execution thread:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test
   ```

---

## Session Handover
To proceed, start a new chat session and run the following command to load the tracking context:
```powershell
/tier5-resume --target="docs/epic/EPIC_60_tracker.md"
```
