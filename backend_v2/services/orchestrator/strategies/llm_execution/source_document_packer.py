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
    def pack(inputs_payload: Any, expected_inputs: list[ExpectedInput] | None = None) -> str:
        """Pack input documents with inline context directives for TDA paragraph splitting.

        Args:
            inputs_payload: Raw payload containing a string or key-value dictionary of documents.
            expected_inputs: Optional workflow definitions containing input keys and ai_descriptions.

        Returns:
            Formatted document string with inline directives, or an empty string if invalid.
        """
        if not inputs_payload:
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
            if not isinstance(value, str) or not value.strip():
                continue
            clean_value = value.strip()
            directive = meta_map.get(key)
            if directive:
                sections.append(
                    f'<ai_context_directive document="{key}">{directive}</ai_context_directive>\n\n{clean_value}'
                )
            else:
                sections.append(clean_value)
        return "\n\n".join(sections)
