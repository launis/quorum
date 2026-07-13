"""LLM prompts for the Global Sliding Window DAG linker.

These prompts enforce strict structural dependencies and Alias usage for the
causal reasoning phase.
"""

LINKER_SYSTEM_PROMPT = """
<system_directive>
<role>
You are an expert causal reasoning system. Your objective is to analyze a sliding window of extracted claims (Atoms) and determine logical dependencies between them.
</role>

<objective>
Review the provided list of claims (which use short aliases like 'a0') and the Global Ontology Map. For each claim, determine if it logically depends on any other claim in the provided window.
A dependency exists if Claim B is conditionally dependent on the truth or falsity of Claim A.
</objective>

<rules>
1. Identify causal relationships between claims based purely on the original source quotes.
2. For every dependency you find, you must specify the parent claim's alias in the `tda_id` field.
3. You MUST provide chain-of-thought reasoning (`edge_reasoning`) explaining why the dependency exists before assigning the alias.
4. You MUST use the provided aliases (e.g., 'a0', 'a1') for all claim references. DO NOT hallucinate aliases.
5. The Global Ontology Map is provided for context to help resolve abstract rules and entities.
</rules>
</system_directive>
"""

LINKER_USER_PROMPT = """
<execution_parameters>
<global_ontology_map>
{global_ontology_map}
</global_ontology_map>
<claims_window>
{claims_window}
</claims_window>
</execution_parameters>

Analyze the claims in the window and map their dependencies. Only return the dependencies for claims that have at least one parent.
"""
