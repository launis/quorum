"""Template Processor for secure LLM prompt generation.

Replaces native f-strings to prevent XML prompt injection by
using CDATA encapsulation and Breakout Shielding.
"""

from typing import Any


class TemplateProcessor:
    """Core text template processor for LLM prompts.

    Implements CDATA encapsulation to strictly isolate user inputs
    from the structural XML tags of the prompt.
    """

    @staticmethod
    def _apply_breakout_shield(text: str) -> str:
        """Neutralize CDATA breakout attempts.

        Replaces ']]>' with a safe equivalent that maintains the literal
        representation without closing the XML CDATA block.
        """
        return str(text).replace("]]>", "]]]]><![CDATA[>")

    @staticmethod
    def _encapsulate_cdata(text: str) -> str:
        """Wrap text in CDATA safely.

        Args:
            text: Raw input string to be encapsulated.

        Returns:
            The input safely enclosed in a CDATA block.
        """
        shielded = TemplateProcessor._apply_breakout_shield(text)
        return f"<![CDATA[{shielded}]]>"

    @classmethod
    def safe_interpolate(cls, template_str: str, **kwargs: Any) -> str:
        """Interpolate variables into the template string with CDATA wrapping.

        Args:
            template_str: The format string containing named placeholders.
            **kwargs: The variables to be safely injected.

        Returns:
            The fully interpolated and secured string.
        """
        safe_kwargs: dict[str, str] = {}
        for key, value in kwargs.items():
            if value is None:
                safe_kwargs[key] = ""
            elif isinstance(value, str):
                safe_kwargs[key] = cls._encapsulate_cdata(value)
            else:
                safe_kwargs[key] = cls._encapsulate_cdata(str(value))

        return template_str.format(**safe_kwargs)

    @classmethod
    def encapsulate_payload(cls, payload: Any) -> str:
        """Directly encapsulate a single payload string without interpolation.

        Args:
            payload: The raw text or object to encapsulate.

        Returns:
            The shielded CDATA block.
        """
        if payload is None:
            return ""
        return cls._encapsulate_cdata(str(payload))
