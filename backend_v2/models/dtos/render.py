"""Execution render result DTO.

SSOT for rendered execution outputs across multi-channel presentation formats.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.execution import JobAcceptedDTO
from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO
from backend_v2.models.dtos.report_data import ReportDataDTO

__all__ = ["RenderExecutionResultDTO"]


class RenderExecutionResultDTO(V2CoreBase):
    """Encapsulates rendered execution artifacts and HTTP transmission metadata.

    Attributes:
        content: Formatted content artifact (binary payload, text, or typed DTO).
        media_type: MIME media type for HTTP Content-Type headers.
        filename: Suggested filename for Content-Disposition header.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    content: Annotated[
        bytes | str | FlatExecutionRecordDTO | ReportDataDTO | JobAcceptedDTO,
        Field(description="Rendered execution artifact payload"),
    ]
    media_type: Annotated[str, Field(description="MIME media type string")]
    filename: Annotated[str | None, Field(default=None, description="Suggested attachment filename")] = None
