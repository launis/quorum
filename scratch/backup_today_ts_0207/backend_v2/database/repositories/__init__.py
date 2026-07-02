"""Granular repository implementations based on ISP."""

from .audit import AuditRepositoryImpl
from .base import AppendOnlyRepositoryBase, BaseRepository
from .component import ComponentRepositoryImpl
from .execution import ExecutionRepositoryImpl
from .identity import IdentityRepositoryImpl
from .knowledge import KnowledgeRepositoryImpl
from .system import SystemRepositoryImpl
from .workflow import WorkflowRepositoryImpl

__all__ = [
    "BaseRepository",
    "AppendOnlyRepositoryBase",
    "AuditRepositoryImpl",
    "ComponentRepositoryImpl",
    "ExecutionRepositoryImpl",
    "IdentityRepositoryImpl",
    "KnowledgeRepositoryImpl",
    "SystemRepositoryImpl",
    "WorkflowRepositoryImpl",
]
