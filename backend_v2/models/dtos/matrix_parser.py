"""Matrix parser result and scorecard atom collection DTOs.

Defines immutable Pydantic V2 schemas for matrix parser results
and scorecard atom collections, eliminating anonymous tuples and nested dicts.
"""

from __future__ import annotations

from collections.abc import Iterator, ValuesView
from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO

__all__ = [
    "MatrixAtomHydrationResultDTO",
    "MatrixContextTargetResultDTO",
    "MatrixScaleProjectionDTO",
    "ParsedMatricesResultDTO",
    "ScorecardAtomCollectionDTO",
]


class ScorecardAtomCollectionDTO(V2CoreBase):
    """Immutable collection of scorecard atoms for an execution step.

    Attributes:
        atoms: Mapping of atom ID to ScorecardAtomDTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    atoms: Annotated[
        dict[str, ScorecardAtomDTO], Field(default_factory=dict, description="Mapping of atom ID to ScorecardAtomDTO")
    ]

    def __getitem__(self, atom_id: str) -> ScorecardAtomDTO:
        """Retrieve scorecard atom by atom ID.

        Args:
            atom_id: Atom identifier string.

        Returns:
            Matched ScorecardAtomDTO.
        """
        return self.atoms[atom_id]

    def __contains__(self, atom_id: str) -> bool:
        """Check if atom ID is defined.

        Args:
            atom_id: Atom identifier string.

        Returns:
            True if atom is defined, False otherwise.
        """
        return atom_id in self.atoms

    def __len__(self) -> int:
        """Return number of atoms in collection."""
        return len(self.atoms)

    def keys(self) -> Iterator[str]:
        """Iterate over atom IDs."""
        return iter(self.atoms.keys())

    def values(self) -> ValuesView[ScorecardAtomDTO]:
        """Return collection of ScorecardAtomDTO items."""
        return self.atoms.values()

    def items(self) -> Iterator[tuple[str, ScorecardAtomDTO]]:
        """Iterate over (atom_id, ScorecardAtomDTO) pairs."""
        return iter(self.atoms.items())


class ParsedMatricesResultDTO(V2CoreBase):
    """Immutable result payload of MatrixDomainParser.parse_matrices.

    Attributes:
        evaluative_matrices: Ordered list of evaluative matrix scorecard rows.
        informational_matrices: Ordered list of informational matrix scorecard rows.
        all_parsed_matrices: Mapping of composite key (step_id_block_id) to row DTO.
        step_scorecard_atoms: Mapping of step_id to ScorecardAtomCollectionDTO.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    evaluative_matrices: Annotated[
        list[MatrixScorecardRowDTO], Field(description="Ordered list of evaluative matrix scorecard rows")
    ]
    informational_matrices: Annotated[
        list[MatrixScorecardRowDTO], Field(description="Ordered list of informational matrix scorecard rows")
    ]
    all_parsed_matrices: Annotated[
        dict[str, MatrixScorecardRowDTO], Field(description="Mapping of composite key to scorecard row DTO")
    ]
    step_scorecard_atoms: Annotated[
        dict[str, ScorecardAtomCollectionDTO], Field(description="Mapping of step_id to scorecard atom collections")
    ]


# Phase 1, Step 1: Define immutable stage DTOs for MatrixDomainParser decomposition
class MatrixScaleProjectionDTO(V2CoreBase):
    """Immutable stage DTO encapsulating scale boundaries and display score projections.

    Attributes:
        true_atoms: Count of passed TDA atoms.
        total_atoms: Count of non-N_A TDA atoms.
        raw_score: Computed or payload raw score.
        norm_score: Computed or payload normalized score.
        math_min: Minimum mathematical scale boundary from PromptBlock.
        math_max: Maximum mathematical scale boundary from PromptBlock.
        display_scale_min: Resolved UI display scale minimum.
        display_scale_max: Resolved UI display scale maximum.
        score_float: Projected UI display score.
        score_display_label: Formatted UI score label string.
        ui_plot_ratio: Normalized 0.0 to 1.0 plot ratio.
        level_names: Mapping of scale level key to localized scale label.
        ui_boundary_labels: Mapping of 0.0 and 1.0 plot boundaries to localized scale labels.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    true_atoms: Annotated[int | None, Field(default=None, description="Count of passed TDA atoms")] = None
    total_atoms: Annotated[int | None, Field(default=None, description="Count of non-N_A TDA atoms")] = None
    raw_score: Annotated[float | None, Field(default=None, description="Computed or payload raw score")] = None
    norm_score: Annotated[float | None, Field(default=None, description="Computed or payload normalized score")] = None
    math_min: Annotated[float, Field(description="Minimum mathematical scale boundary from PromptBlock")]
    math_max: Annotated[float, Field(description="Maximum mathematical scale boundary from PromptBlock")]
    display_scale_min: Annotated[float, Field(description="Resolved UI display scale minimum")]
    display_scale_max: Annotated[float, Field(description="Resolved UI display scale maximum")]
    score_float: Annotated[float | None, Field(default=None, description="Projected UI display score")] = None
    score_display_label: Annotated[str, Field(description="Formatted UI score label string")]
    ui_plot_ratio: Annotated[float | None, Field(default=None, description="Normalized 0.0 to 1.0 plot ratio")] = None
    level_names: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Mapping of scale level key to localized scale label"),
    ]
    ui_boundary_labels: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Mapping of 0.0 and 1.0 plot boundaries to localized scale labels"),
    ]


class MatrixAtomHydrationResultDTO(V2CoreBase):
    """Immutable stage DTO encapsulating hydrated scorecard atoms and clustered row sources.

    Attributes:
        evaluated_atoms: Ordered list of hydrated ScorecardAtomDTO items for the row.
        clustered_row_sources: Clustered MCP audit trace sources for the row.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    evaluated_atoms: Annotated[
        list[ScorecardAtomDTO],
        Field(default_factory=list, description="Ordered list of hydrated ScorecardAtomDTO items for the row"),
    ]
    clustered_row_sources: Annotated[
        list[MCPAuditTrace],
        Field(default_factory=list, description="Clustered MCP audit trace sources for the row"),
    ]


class MatrixContextTargetResultDTO(V2CoreBase):
    """Immutable stage DTO encapsulating resolved deterministic context target and label.

    Attributes:
        context_target: Resolved deterministic input target key.
        context_target_label: Resolved localized label for the context target.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    context_target: Annotated[
        str | None, Field(default=None, description="Resolved deterministic input target key")
    ] = None
    context_target_label: Annotated[
        I18nText | None, Field(default=None, description="Resolved localized label for the context target")
    ] = None
