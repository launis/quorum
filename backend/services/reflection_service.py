from datetime import datetime, timezone

from backend.models.dtos.reflection import GuidedReflectionDTO


class ReflectionService:
    """Service for handling Guided Reflection data and combining it into structured Markdown documents."""

    @staticmethod
    def generate_markdown_document(data: GuidedReflectionDTO) -> str:
        """Generates a structured Markdown document from Guided Reflection DTO.
        Ensures strict XML tagging for agent context downstream.

        Args:
            data: The validated GuidedReflectionDTO payload.

        Returns:
            A formatted Markdown string containing the reflection answers wrapped in XML tags.
        """
        # Always use UTC isoformat for strict temporal context (Part 2.2 Date Handling Temporal Standard)
        timestamp = datetime.now(timezone.utc).isoformat()

        def _format_answer(answer: str | None) -> str:
            if not answer or not answer.strip():
                return "*Ei vastausta*"
            return answer.strip()

        q1 = _format_answer(data.q1_goal)
        q2 = _format_answer(data.q2_falsification)
        q3 = _format_answer(data.q3_synthesis)
        q4 = _format_answer(data.q4_argumentation)

        # Build markdown with XML tags to preserve semantic structure for Kognitiivinen Kvoorum
        content = f"""# Reflektiodokumentti
**Päivämäärä:** {timestamp}
**Syötetapa:** Ohjattu käyttöliittymälomake

## 1. Tavoite ja strateginen suunnittelu
<agency>
{q1}
</agency>

## 2. Tekoälyn ohjaus ja kriittinen iterointi
<falsification>
{q2}
</falsification>

## 3. Oma panos ja luovuus
<synthesis>
{q3}
</synthesis>

## 4. Laadunvarmistus ja metakognitio
<argumentation>
{q4}
</argumentation>"""

        return content.strip()
