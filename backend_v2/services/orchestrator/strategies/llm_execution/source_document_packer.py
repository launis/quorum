"""Source document packer for TDA and LLM evaluation strategies."""

from typing import Any

from pydantic import TypeAdapter, ValidationError

from backend_v2.models.v2_core import ExpectedInput


class SourceDocumentPacker:
    """Utility for packing heterogeneous input documents with in-context metadata directives.

    Emits inline `<ai_context_directive>` paragraph headers preceding document content.
    These headers survive TDAEngine paragraph splitting by remaining self-contained within
    their own paragraph blocks rather than enclosing child paragraphs in multiline XML wrappers.
    Distinct from `<ai_context_mandate>`, which is reserved for prompt compiler system prompts.
    """

    @staticmethod
    def resolve_allowed_keys(input_mappings: dict[str, str] | None) -> set[str]:
        """Resolve explicitly mapped input keys from step input mappings.

        Parses canonical '$inputs.<key>' values to identify input documents
        targeted for ingestion by the step. Non-input mappings and other
        variable references are ignored.

        Args:
            input_mappings: Mapping dictionary from step definition, e.g. {'doc': '$inputs.product_text'}.

        Returns:
            Set of resolved input document keys. Returns an empty set if input_mappings is None or empty.
        """
        if not input_mappings:
            return set()

        allowed: set[str] = set()
        for value in input_mappings.values():
            if isinstance(value, str) and value.startswith("$inputs."):
                key = value[len("$inputs.") :].strip()
                if key:
                    allowed.add(key)
        return allowed

    @staticmethod
    def pack(
        inputs_payload: Any,
        expected_inputs: list[ExpectedInput] | None = None,
        allowed_keys: set[str] | None = None,
    ) -> str:
        """Pack input documents with inline context directives for TDA paragraph splitting.

        Args:
            inputs_payload: Raw payload containing a string or key-value dictionary of documents.
            expected_inputs: Optional workflow definitions containing input keys and ai_descriptions.
            allowed_keys: Optional set of allowed input keys. If provided and empty, returns empty string.
                When populated, filters dictionary payload to include only matching keys.

        Returns:
            Formatted document string with inline directives, or an empty string if invalid.
        """
        if not inputs_payload:
            return ""

        if allowed_keys is not None and len(allowed_keys) == 0:
            return ""

        meta_map: dict[str, str] = {}
        if expected_inputs:
            for ei in expected_inputs:
                if ei.ai_description and ei.ai_description.strip():
                    meta_map[ei.input_key] = ei.ai_description.strip()

        if isinstance(inputs_payload, str):
            return inputs_payload.strip()

        try:
            dict_payload = TypeAdapter(dict[str, Any]).validate_python(inputs_payload)
        except ValidationError:
            return ""

        sections: list[str] = []
        for key, value in dict_payload.items():
            if allowed_keys is not None and key not in allowed_keys:
                continue
            if not isinstance(value, str) or not value.strip():
                continue
            clean_value = value.strip()
            if key in meta_map:
                directive = meta_map[key]
                sections.append(
                    f'<ai_context_directive document="{key}">{directive}</ai_context_directive>\n\n{clean_value}'
                )
            else:
                sections.append(clean_value)
        return "\n\n".join(sections)
