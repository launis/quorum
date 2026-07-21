import inspect

from backend_v2.database import interfaces


def test_interfaces_are_protocols() -> None:
    """Verify that all repository interfaces are properly defined as Protocols."""
    protocol_classes = [
        interfaces.IExecutionRepository,
        interfaces.IWorkflowRepository,
        interfaces.IIdentityRepository,
        interfaces.IComponentRepository,
        interfaces.IKnowledgeRepository,
        interfaces.ISystemRepository,
        interfaces.IAuditRepository,
    ]

    for protocol_class in protocol_classes:
        assert inspect.isclass(protocol_class)
        assert (
            hasattr(protocol_class, "__parameters__")
            or getattr(protocol_class, "_is_protocol", False)
            or type(protocol_class).__name__ in ("_ProtocolMeta", "ProtocolMeta")
        )


def test_interfaces_can_be_imported() -> None:
    """Verify that the module loads without circular dependencies."""
    assert interfaces is not None
