"""Template Processor for secure LLM prompt generation.

Replaces native f-strings to prevent XML prompt injection by
using CDATA encapsulation, Breakout Shielding, and PEP 750 Template strings.
"""

import logging
from string.templatelib import Template, convert
from typing import Any
from xml.sax import saxutils

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """Core text template processor for LLM prompts.

    Implements CDATA encapsulation and PEP 750 template string rendering
    to strictly isolate user inputs from the structural XML tags of the prompt.
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
    def render_prompt(cls, template: Template) -> str:
        """Render a PEP 750 Template into a secured, CDATA-encapsulated XML prompt.

        Args:
            template: The PEP 750 Template instance to render.

        Returns:
            The fully rendered prompt string with CDATA isolation.

        Raises:
            AppException: VALIDATION_FAILED if template is not a string.templatelib.Template instance.
        """
        if not isinstance(template, Template):
            msg = (
                f"TemplateProcessor.render_prompt requires a string.templatelib.Template instance, "
                f"got '{type(template).__name__}'."
            )
            logger.error("[TemplateProcessor] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        chunks: list[str] = []
        for s, interp in zip(template.strings[:-1], template.interpolations, strict=True):
            chunks.append(s)
            val = interp.value
            if val is None:
                continue
            if interp.conversion:
                val = convert(val, interp.conversion)

            if isinstance(val, Template):
                chunks.append(cls.render_prompt(val))
            elif interp.format_spec == "raw":
                chunks.append(str(val))
            elif s.rstrip().endswith(('="', "='")) or interp.format_spec == "attr":
                chunks.append(saxutils.escape(str(val), {'"': "&quot;", "'": "&apos;"}))
            else:
                chunks.append(cls._encapsulate_cdata(str(val)))

        chunks.append(template.strings[-1])
        return "".join(chunks)

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
