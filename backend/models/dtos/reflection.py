from pydantic import BaseModel, ConfigDict, Field


class GuidedReflectionDTO(BaseModel):
    """Data Transfer Object for Guided Reflection form inputs."""

    q1_goal: str | None = Field(
        default=None,
        description=(
            "Goal and strategic planning: What was your original goal, "
            "and how did you break down the broad problem into smaller parts "
            "before giving the first prompt to the AI?"
        ),
    )
    q2_falsification: str | None = Field(
        default=None,
        description=(
            "Directing the AI and critical iteration: What flaws, errors, or "
            "hallucinations did you notice in the AI's responses during the process, "
            "and how did you direct the AI to correct them?"
        ),
    )
    q3_synthesis: str | None = Field(
        default=None,
        description=(
            "Personal contribution and creativity: What in the final work is purely your own, "
            "human added value?"
        ),
    )
    q4_argumentation: str | None = Field(
        default=None,
        description=(
            "Quality assurance and metacognition: On what grounds do you judge "
            "the final result to be high quality and reliable? If you were to do "
            "the task again, what would you do differently?"
        ),
    )

    model_config = ConfigDict(strict=True)
