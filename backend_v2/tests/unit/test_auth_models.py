"""Unit tests for authentication, identity, invitation, task assignment, and secret models in backend_v2.models.auth."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.models.auth import (
    ExecutionAssignmentBatchCreateDTO,
    ExecutionAssignmentRecipientDTO,
    Invitation,
    InvitationBatchCreateDTO,
    InvitationCreateDTO,
    Organization,
    SubscriptionStatus,
    TenantSecretDTO,
    TokenExchangeRequestDTO,
    User,
    UserAdminView,
    UserRole,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    SecretScope,
    SecretStorageMode,
    SystemLocale,
)

VALID_ORG_ID = "org_0195f3a0000070008000000000000001"
VALID_USER_ID = "usr_0195f3a0000070008000000000000002"
VALID_WF_ID = "wf_0195f3a0000070008000000000000003"


def test_organization_fail_fast_on_corrupt_datetime() -> None:
    """Verify Organization rejects malformed ISO datetime strings."""
    with pytest.raises(ValidationError) as exc_info:
        Organization.model_validate(
            {
                "id": VALID_ORG_ID,
                "name": "Test",
                "is_active": True,
                "tier": "enterprise",
                "subscription_status": SubscriptionStatus.ACTIVE,
                "quota_limit": 10.0,
                "tpm_limit": 1000,
                "rpm_limit": 1,
                "created_at": "invalid_date_string",
            }
        )
    assert "invalid_date_string" in str(exc_info.value)


def test_organization_fail_fast_on_corrupt_subscription() -> None:
    """Verify Organization rejects invalid subscription status values."""
    with pytest.raises(ValidationError) as exc_info:
        Organization.model_validate(
            {
                "id": VALID_ORG_ID,
                "name": "Test",
                "is_active": True,
                "tier": "enterprise",
                "subscription_status": "LIFETIME_HACKER",
                "quota_limit": 10.0,
                "tpm_limit": 1000,
                "rpm_limit": 1,
            }
        )
    assert "LIFETIME_HACKER" in str(exc_info.value)


def test_organization_default_id_and_empty_name_validation() -> None:
    """Verify Organization generates an Opaque Stripe ID by default and rejects empty names."""
    org = Organization.model_validate(
        {
            "name": "Acme Corp",
            "is_active": True,
            "tier": "enterprise",
            "subscription_status": SubscriptionStatus.ACTIVE,
            "quota_limit": 0.0,
            "tpm_limit": 1000,
            "rpm_limit": 1,
            "created_at": "2026-01-01T00:00:00Z",
        }
    )
    assert org.id.startswith("org_")
    assert len(org.id) == 36

    with pytest.raises(ValidationError):
        Organization(
            id=VALID_ORG_ID,
            name="   ",
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=1000,
            rpm_limit=1,
            allowed_email_domains=[],
        )


def test_user_fail_fast_on_corrupt_datetime() -> None:
    """Verify User rejects malformed ISO datetime strings."""
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(
            {
                "id": VALID_USER_ID,
                "email": "a@b.com",
                "role": UserRole.MEMBER,
                "is_active": True,
                "language": SystemLocale.EN,
                "theme_mode": "system",
                "created_at": "30.02.2025",
            }
        )
    assert "30.02.2025" in str(exc_info.value)


def test_user_fail_fast_on_corrupt_role() -> None:
    """Verify User rejects unrecognized role enum values."""
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(
            {
                "id": VALID_USER_ID,
                "email": "a@b.com",
                "role": "SUPER_ADMIN_GOD",
                "is_active": True,
                "language": SystemLocale.EN,
                "theme_mode": "system",
                "created_at": "2026-01-01T00:00:00Z",
            }
        )
    assert "SUPER_ADMIN_GOD" in str(exc_info.value)


def test_user_default_id_and_validate_non_empty() -> None:
    """Verify User generates a default Opaque Stripe ID and enforces non-empty ID validation."""
    user = User.model_validate(
        {
            "email": "valid@example.com",
            "role": UserRole.MEMBER,
            "is_active": True,
            "language": SystemLocale.EN,
            "theme_mode": "system",
            "created_at": "2026-01-01T00:00:00Z",
        }
    )
    assert user.id.startswith("usr_")
    assert len(user.id) == 36

    with pytest.raises(ValueError, match="Field cannot be empty or whitespace only"):
        User.validate_non_empty("   ")


def test_user_admin_view_inherits_all_user_fields() -> None:
    """Verify UserAdminView is a strict superset of User including firebase_uid and deleted_at."""
    user_fields = set(User.model_fields.keys())
    admin_view_fields = set(UserAdminView.model_fields.keys())
    assert user_fields.issubset(admin_view_fields)
    assert {"firebase_uid", "deleted_at", "last_login_at", "execution_count"}.issubset(admin_view_fields)

    admin_view = UserAdminView.model_validate(
        {
            "id": VALID_USER_ID,
            "email": "admin@quorum.ai",
            "role": UserRole.ADMIN,
            "organization_id": VALID_ORG_ID,
            "is_active": True,
            "language": SystemLocale.EN,
            "theme_mode": "system",
            "created_at": "2026-01-01T00:00:00Z",
            "firebase_uid": "fb_uid_admin_01",
            "deleted_at": "2026-11-02T12:00:00Z",
            "last_login_at": "2026-11-02T11:00:00Z",
            "execution_count": 7,
        }
    )
    assert admin_view.firebase_uid == "fb_uid_admin_01"
    assert isinstance(admin_view.deleted_at, datetime)
    assert isinstance(admin_view.last_login_at, datetime)
    assert admin_view.execution_count == 7

    # Also verify direct typed datetime pass-through on last_login_at
    ts = datetime(2026, 11, 2, 11, 0, tzinfo=UTC)
    admin_view_typed = UserAdminView(
        id=VALID_USER_ID,
        email="admin@quorum.ai",
        role=UserRole.ADMIN,
        organization_id=VALID_ORG_ID,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=ts,
        last_login_at=ts,
        execution_count=3,
    )
    assert admin_view_typed.last_login_at == ts

    # Negative 1: Reject unrecognized extra fields under extra="forbid"
    with pytest.raises(ValidationError):
        UserAdminView.model_validate(
            {
                "id": VALID_USER_ID,
                "email": "admin@quorum.ai",
                "role": UserRole.ADMIN,
                "is_active": True,
                "language": SystemLocale.EN,
                "theme_mode": "system",
                "created_at": "2026-01-01T00:00:00Z",
                "rogue_field": "forbidden",
            }
        )

    # Negative 2: Reject malformed ISO 8601 string in last_login_at
    with pytest.raises(ValidationError):
        UserAdminView.model_validate(
            {
                "id": VALID_USER_ID,
                "email": "admin@quorum.ai",
                "role": UserRole.ADMIN,
                "is_active": True,
                "language": SystemLocale.EN,
                "theme_mode": "system",
                "created_at": "2026-01-01T00:00:00Z",
                "last_login_at": "not-a-valid-timestamp",
            }
        )


def test_token_exchange_request_dto_mutual_exclusivity_positive() -> None:
    """Positive contract: TokenExchangeRequestDTO validates with exactly one of firebase_token or target_user_id."""
    req_fb = TokenExchangeRequestDTO(
        firebase_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",
        target_user_id=None,
    )
    assert req_fb.firebase_token == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"
    assert req_fb.target_user_id is None

    req_cli = TokenExchangeRequestDTO(
        firebase_token=None,
        target_user_id=VALID_USER_ID,
    )
    assert req_cli.target_user_id == VALID_USER_ID
    assert req_cli.firebase_token is None


def test_token_exchange_request_dto_both_fields_supplied_negative() -> None:
    """Negative contract: TokenExchangeRequestDTO raises ValidationError when both fields are supplied."""
    with pytest.raises(ValidationError, match="Exactly one of 'firebase_token' or 'target_user_id'"):
        TokenExchangeRequestDTO(
            firebase_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",
            target_user_id=VALID_USER_ID,
        )


def test_token_exchange_request_dto_neither_field_supplied_negative() -> None:
    """Negative contract: TokenExchangeRequestDTO raises ValidationError when neither field is supplied."""
    with pytest.raises(ValidationError, match="Exactly one of 'firebase_token' or 'target_user_id'"):
        TokenExchangeRequestDTO(
            firebase_token=None,
            target_user_id=None,
        )


def test_invitation_and_assignment_batch_bounds_boundary() -> None:
    """Boundary contract: InvitationBatchCreateDTO and ExecutionAssignmentBatchCreateDTO enforce [1, 500] recipients."""
    single_inv = InvitationCreateDTO(email="user1@example.com", role=UserRole.MEMBER)
    batch_1 = InvitationBatchCreateDTO(recipients=[single_inv])
    assert len(batch_1.recipients) == 1

    batch_500 = InvitationBatchCreateDTO(
        recipients=[InvitationCreateDTO(email=f"u{i}@example.com", role=UserRole.MEMBER) for i in range(500)]
    )
    assert len(batch_500.recipients) == 500

    with pytest.raises(ValidationError):
        InvitationBatchCreateDTO(recipients=[])

    with pytest.raises(ValidationError):
        InvitationBatchCreateDTO(
            recipients=[InvitationCreateDTO(email=f"u{i}@example.com", role=UserRole.MEMBER) for i in range(501)]
        )

    deadline = datetime(2027, 1, 1, tzinfo=UTC)
    rec_1 = ExecutionAssignmentRecipientDTO(email="candidate1@example.com")
    assign_batch_1 = ExecutionAssignmentBatchCreateDTO(
        recipients=[rec_1],
        workflow_id=VALID_WF_ID,
        locked_inputs=WorkflowInputs(),
        assignee_input_keys=[],
        result_visibility=AssignmentResultVisibility.CONFIRMATION_ONLY,
        hard_deadline_at=deadline,
    )
    assert len(assign_batch_1.recipients) == 1

    assign_batch_500 = ExecutionAssignmentBatchCreateDTO(
        recipients=[ExecutionAssignmentRecipientDTO(email=f"c{i}@example.com") for i in range(500)],
        workflow_id=VALID_WF_ID,
        locked_inputs=WorkflowInputs(),
        assignee_input_keys=[],
        result_visibility=AssignmentResultVisibility.FULL_REPORT_ACCESS,
        hard_deadline_at=deadline,
    )
    assert len(assign_batch_500.recipients) == 500

    with pytest.raises(ValidationError):
        ExecutionAssignmentBatchCreateDTO(
            recipients=[],
            workflow_id=VALID_WF_ID,
            locked_inputs=WorkflowInputs(),
            assignee_input_keys=[],
            hard_deadline_at=deadline,
        )

    with pytest.raises(ValidationError):
        ExecutionAssignmentBatchCreateDTO(
            recipients=[ExecutionAssignmentRecipientDTO(email=f"c{i}@example.com") for i in range(501)],
            workflow_id=VALID_WF_ID,
            locked_inputs=WorkflowInputs(),
            assignee_input_keys=[],
            hard_deadline_at=deadline,
        )


def test_invitation_and_tenant_secret_datetime_parsing() -> None:
    """Verify Invitation and TenantSecretDTO parse ISO 8601 strings and pass through datetime objects."""
    ts = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
    inv_from_str = Invitation.model_validate(
        {
            "organization_id": VALID_ORG_ID,
            "email": "invitee@example.com",
            "token_hash": "a" * 64,
            "invited_by": VALID_USER_ID,
            "expires_at": "2026-12-01T00:00:00Z",
            "created_at": "2026-11-01T00:00:00Z",
        }
    )
    assert inv_from_str.id.startswith("inv_")
    assert inv_from_str.expires_at == datetime(2026, 12, 1, 0, 0, tzinfo=UTC)

    inv_from_dt = Invitation(
        organization_id=VALID_ORG_ID,
        email="invitee@example.com",
        token_hash="b" * 64,
        invited_by=VALID_USER_ID,
        expires_at=ts,
        created_at=ts,
    )
    assert inv_from_dt.expires_at == ts

    with pytest.raises(ValidationError):
        Invitation.model_validate(
            {
                "organization_id": VALID_ORG_ID,
                "email": "invitee@example.com",
                "token_hash": "a" * 64,
                "invited_by": VALID_USER_ID,
                "expires_at": "malformed-iso-date",
            }
        )

    sec_from_str = TenantSecretDTO.model_validate(
        {
            "organization_id": VALID_ORG_ID,
            "scope": SecretScope.LLM_PROVIDER,
            "target_identifier": "gemini",
            "storage_mode": SecretStorageMode.ENVELOPE_KMS,
            "kek_version": "kek-v1",
            "masked_hint": "...1234",
            "updated_by": VALID_USER_ID,
            "updated_at": "2026-11-06T12:00:00Z",
        }
    )
    assert sec_from_str.id.startswith("sec_")
    assert sec_from_str.updated_at == ts

    sec_from_dt = TenantSecretDTO(
        organization_id=VALID_ORG_ID,
        scope=SecretScope.LLM_PROVIDER,
        target_identifier="gemini",
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
        kek_version="kek-v1",
        masked_hint="...1234",
        updated_by=VALID_USER_ID,
        updated_at=ts,
    )
    assert sec_from_dt.updated_at == ts

    with pytest.raises(ValidationError):
        TenantSecretDTO.model_validate(
            {
                "organization_id": VALID_ORG_ID,
                "scope": SecretScope.LLM_PROVIDER,
                "target_identifier": "gemini",
                "storage_mode": SecretStorageMode.ENVELOPE_KMS,
                "kek_version": "kek-v1",
                "masked_hint": "...1234",
                "updated_by": VALID_USER_ID,
                "updated_at": "invalid-timestamp",
            }
        )
