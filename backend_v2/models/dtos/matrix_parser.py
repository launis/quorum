"""Matrix parser result and scorecard atom collection DTOs.

Defines immutable Pydantic V2 schemas for matrix parser results
and scorecard atom collections, eliminating anonymous tuples and nested dicts.
"""

from __future__ import annotations

from collections.abc import Iterator, ValuesView
from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO

__all__ = [
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
    ] = Field(default_factory=dict)

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
