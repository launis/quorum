import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'tenant_secret_dto.freezed.dart';
part 'tenant_secret_dto.g.dart';

/// Represents a tenant or customer organization.
@Freezed(equal: false)
abstract class Organization with _$Organization {
  const Organization._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory Organization({
    @StrictOpaqueIdConverter() required String id,
    String? slug,
    required String name,
    @JsonKey(name: 'created_at') DateTime? createdAt,
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    @Default('standard') String tier,
    @JsonKey(name: 'contact_email') String? contactEmail,
    @JsonKey(name: 'billing_id') String? billingId,
    @JsonKey(name: 'subscription_status')
    @Default(SubscriptionStatus.active)
    SubscriptionStatus subscriptionStatus,
    @JsonKey(name: 'quota_limit') @Default(0.0) double quotaLimit,
    @JsonKey(name: 'tpm_limit') @Default(100000) int tpmLimit,
    @JsonKey(name: 'rpm_limit') @Default(60) int rpmLimit,
    @JsonKey(name: 'allowed_email_domains')
    @Default([])
    List<String> allowedEmailDomains,
  }) = _Organization;

  factory Organization.fromJson(Map<String, dynamic> json) =>
      _$OrganizationFromJson(json);
}

/// Payload for updating an existing organization.
@Freezed(equal: false)
abstract class OrganizationUpdateDto with _$OrganizationUpdateDto {
  const OrganizationUpdateDto._();

  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    includeIfNull: false,
  )
  const factory OrganizationUpdateDto({
    String? name,
    String? tier,
    @JsonKey(name: 'is_active') bool? isActive,
    @JsonKey(name: 'contact_email') String? contactEmail,
    @JsonKey(name: 'billing_id') String? billingId,
    @JsonKey(name: 'subscription_status')
    SubscriptionStatus? subscriptionStatus,
    @JsonKey(name: 'quota_limit') double? quotaLimit,
    @JsonKey(name: 'tpm_limit') int? tpmLimit,
    @JsonKey(name: 'rpm_limit') int? rpmLimit,
    @JsonKey(name: 'allowed_email_domains') List<String>? allowedEmailDomains,
  }) = _OrganizationUpdateDto;

  factory OrganizationUpdateDto.fromJson(Map<String, dynamic> json) =>
      _$OrganizationUpdateDtoFromJson(json);
}

/// Payload response for deleting an organization or tenant secret.
@Freezed(equal: false)
abstract class OrganizationDeleteResponse with _$OrganizationDeleteResponse {
  const OrganizationDeleteResponse._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory OrganizationDeleteResponse({
    required String status,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'deleted_id')
    required String deletedId,
  }) = _OrganizationDeleteResponse;

  factory OrganizationDeleteResponse.fromJson(Map<String, dynamic> json) =>
      _$OrganizationDeleteResponseFromJson(json);
}

/// Payload response for deleting (GDPR soft-deleting) a user account.
@Freezed(equal: false)
abstract class UserDeleteResponse with _$UserDeleteResponse {
  const UserDeleteResponse._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory UserDeleteResponse({
    required String status,
    @StrictOpaqueIdConverter() required String id,
  }) = _UserDeleteResponse;

  factory UserDeleteResponse.fromJson(Map<String, dynamic> json) =>
      _$UserDeleteResponseFromJson(json);
}

/// Payload for inviting a user to an organization.
@Freezed(equal: false)
abstract class InvitationCreateDto with _$InvitationCreateDto {
  const InvitationCreateDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory InvitationCreateDto({
    required String email,
    @Default(UserRole.member) UserRole role,
    @JsonKey(name: 'expires_in_hours') @Default(168) int expiresInHours,
  }) = _InvitationCreateDto;

  factory InvitationCreateDto.fromJson(Map<String, dynamic> json) =>
      _$InvitationCreateDtoFromJson(json);
}

/// API response DTO representing an organization invitation without exposing token_hash.
@Freezed(equal: false)
abstract class InvitationResponseDto with _$InvitationResponseDto {
  const InvitationResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory InvitationResponseDto({
    @StrictOpaqueIdConverter() required String id,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'organization_id')
    required String organizationId,
    required String email,
    required UserRole role,
    required InvitationStatus status,
    @JsonKey(name: 'email_delivery_status')
    @Default(EmailDeliveryStatus.pending)
    EmailDeliveryStatus emailDeliveryStatus,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'invited_by')
    required String invitedBy,
    @JsonKey(name: 'expires_at') required DateTime expiresAt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _InvitationResponseDto;

  factory InvitationResponseDto.fromJson(Map<String, dynamic> json) =>
      _$InvitationResponseDtoFromJson(json);
}

/// Payload for bulk-creating organization invitations (1 to 500 recipients).
@Freezed(equal: false)
abstract class InvitationBatchCreateDto with _$InvitationBatchCreateDto {
  const InvitationBatchCreateDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory InvitationBatchCreateDto({
    required List<InvitationCreateDto> recipients,
  }) = _InvitationBatchCreateDto;

  factory InvitationBatchCreateDto.fromJson(Map<String, dynamic> json) =>
      _$InvitationBatchCreateDtoFromJson(json);
}

/// Response payload for bulk-created organization invitations.
@Freezed(equal: false)
abstract class InvitationBatchResponseDto with _$InvitationBatchResponseDto {
  const InvitationBatchResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory InvitationBatchResponseDto({
    @JsonKey(name: 'created_count') required int createdCount,
    required List<InvitationResponseDto> invitations,
  }) = _InvitationBatchResponseDto;

  factory InvitationBatchResponseDto.fromJson(Map<String, dynamic> json) =>
      _$InvitationBatchResponseDtoFromJson(json);
}

/// Ingress payload for provisioning or rotating a tenant-scoped BYOK secret.
@Freezed(equal: false)
abstract class TenantSecretCreateDto with _$TenantSecretCreateDto {
  const TenantSecretCreateDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory TenantSecretCreateDto({
    required SecretScope scope,
    @JsonKey(name: 'target_identifier') required String targetIdentifier,
    @JsonKey(name: 'plaintext_secret') required String plaintextSecret,
    // Phase 3, Step 3: Add required storageMode with zero default value (REQ-012)
    @JsonKey(name: 'storage_mode') required SecretStorageMode storageMode,
  }) = _TenantSecretCreateDto;

  factory TenantSecretCreateDto.fromJson(Map<String, dynamic> json) =>
      _$TenantSecretCreateDtoFromJson(json);
}

/// Zero-leakage API response DTO for tenant secret metadata.
@Freezed(equal: false)
abstract class TenantSecretResponseDto with _$TenantSecretResponseDto {
  const TenantSecretResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory TenantSecretResponseDto({
    @StrictOpaqueIdConverter() required String id,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'organization_id')
    required String organizationId,
    required SecretScope scope,
    @JsonKey(name: 'target_identifier') required String targetIdentifier,
    @JsonKey(name: 'storage_mode') required SecretStorageMode storageMode,
    @Default(true) bool configured,
    @JsonKey(name: 'masked_hint') required String maskedHint,
    @JsonKey(name: 'kek_version') required String kekVersion,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
  }) = _TenantSecretResponseDto;

  factory TenantSecretResponseDto.fromJson(Map<String, dynamic> json) =>
      _$TenantSecretResponseDtoFromJson(json);
}

/// Payload for creating a single-use workflow execution assignment.
@Freezed(equal: false)
abstract class ExecutionAssignmentCreateDto
    with _$ExecutionAssignmentCreateDto {
  const ExecutionAssignmentCreateDto._();

  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    includeIfNull: false,
  )
  const factory ExecutionAssignmentCreateDto({
    @JsonKey(name: 'assigned_email') required String assignedEmail,
    @JsonKey(name: 'invited_role')
    @Default(UserRole.member)
    UserRole invitedRole,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'workflow_id')
    required String workflowId,
    @JsonKey(name: 'output_profile_id') String? outputProfileId,
    @JsonKey(name: 'target_locale') @Default('fi') String targetLocale,
    @JsonKey(name: 'locked_inputs') required WorkflowInputs lockedInputs,
    @JsonKey(name: 'assignee_input_keys')
    @Default([])
    List<String> assigneeInputKeys,
    @JsonKey(name: 'result_visibility')
    @Default(AssignmentResultVisibility.confirmationOnly)
    AssignmentResultVisibility resultVisibility,
    @JsonKey(name: 'hard_deadline_at') required DateTime hardDeadlineAt,
    @JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds,
  }) = _ExecutionAssignmentCreateDto;

  factory ExecutionAssignmentCreateDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionAssignmentCreateDtoFromJson(json);
}

/// Individual recipient descriptor within a bulk task assignment batch.
@Freezed(equal: false)
abstract class ExecutionAssignmentRecipientDto
    with _$ExecutionAssignmentRecipientDto {
  const ExecutionAssignmentRecipientDto._();

  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    includeIfNull: false,
  )
  const factory ExecutionAssignmentRecipientDto({
    required String email,
    String? name,
    @JsonKey(name: 'target_locale') String? targetLocale,
  }) = _ExecutionAssignmentRecipientDto;

  factory ExecutionAssignmentRecipientDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionAssignmentRecipientDtoFromJson(json);
}

/// Payload for bulk-creating 1 to 500 single-use workflow execution assignments.
@Freezed(equal: false)
abstract class ExecutionAssignmentBatchCreateDto
    with _$ExecutionAssignmentBatchCreateDto {
  const ExecutionAssignmentBatchCreateDto._();

  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    includeIfNull: false,
  )
  const factory ExecutionAssignmentBatchCreateDto({
    required List<ExecutionAssignmentRecipientDto> recipients,
    @JsonKey(name: 'invited_role')
    @Default(UserRole.member)
    UserRole invitedRole,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'workflow_id')
    required String workflowId,
    @JsonKey(name: 'output_profile_id') String? outputProfileId,
    @JsonKey(name: 'target_locale') @Default('fi') String targetLocale,
    @JsonKey(name: 'locked_inputs') required WorkflowInputs lockedInputs,
    @JsonKey(name: 'assignee_input_keys')
    @Default([])
    List<String> assigneeInputKeys,
    @JsonKey(name: 'result_visibility')
    @Default(AssignmentResultVisibility.confirmationOnly)
    AssignmentResultVisibility resultVisibility,
    @JsonKey(name: 'hard_deadline_at') required DateTime hardDeadlineAt,
    @JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds,
  }) = _ExecutionAssignmentBatchCreateDto;

  factory ExecutionAssignmentBatchCreateDto.fromJson(
    Map<String, dynamic> json,
  ) => _$ExecutionAssignmentBatchCreateDtoFromJson(json);
}

/// API response DTO representing a task assignment without exposing token_hash.
@Freezed(equal: false)
abstract class ExecutionAssignmentResponseDto
    with _$ExecutionAssignmentResponseDto {
  const ExecutionAssignmentResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionAssignmentResponseDto({
    @StrictOpaqueIdConverter() required String id,
    @JsonKey(name: 'batch_id') String? batchId,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'organization_id')
    required String organizationId,
    @JsonKey(name: 'assigned_email') required String assignedEmail,
    @JsonKey(name: 'assigned_user_id') String? assignedUserId,
    @JsonKey(name: 'invited_role') required UserRole invitedRole,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'workflow_id')
    required String workflowId,
    @JsonKey(name: 'output_profile_id') String? outputProfileId,
    @JsonKey(name: 'target_locale') required String targetLocale,
    @JsonKey(name: 'locked_inputs') required WorkflowInputs lockedInputs,
    @JsonKey(name: 'assignee_input_keys')
    required List<String> assigneeInputKeys,
    @JsonKey(name: 'draft_inputs') required WorkflowInputs draftInputs,
    required AssignmentStatus status,
    @JsonKey(name: 'email_delivery_status')
    @Default(EmailDeliveryStatus.pending)
    EmailDeliveryStatus emailDeliveryStatus,
    @JsonKey(name: 'result_visibility')
    required AssignmentResultVisibility resultVisibility,
    @JsonKey(name: 'hard_deadline_at') required DateTime hardDeadlineAt,
    @JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds,
    @JsonKey(name: 'activated_at') DateTime? activatedAt,
    @JsonKey(name: 'submitted_at') DateTime? submittedAt,
    @JsonKey(name: 'execution_id') String? executionId,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'created_by')
    required String createdBy,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _ExecutionAssignmentResponseDto;

  factory ExecutionAssignmentResponseDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionAssignmentResponseDtoFromJson(json);
}

/// Response payload for bulk-created workflow execution assignments.
@Freezed(equal: false)
abstract class ExecutionAssignmentBatchResponseDto
    with _$ExecutionAssignmentBatchResponseDto {
  const ExecutionAssignmentBatchResponseDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionAssignmentBatchResponseDto({
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'batch_id')
    required String batchId,
    @JsonKey(name: 'created_count') required int createdCount,
    required List<ExecutionAssignmentResponseDto> assignments,
  }) = _ExecutionAssignmentBatchResponseDto;

  factory ExecutionAssignmentBatchResponseDto.fromJson(
    Map<String, dynamic> json,
  ) => _$ExecutionAssignmentBatchResponseDtoFromJson(json);
}

/// Public pre-activation preview of a single-use workflow execution assignment.
@Freezed(equal: false)
abstract class ExecutionAssignmentPreviewDto
    with _$ExecutionAssignmentPreviewDto {
  const ExecutionAssignmentPreviewDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionAssignmentPreviewDto({
    @StrictOpaqueIdConverter() required String id,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'organization_id')
    required String organizationId,
    @JsonKey(name: 'organization_name') required String organizationName,
    @JsonKey(name: 'assigned_email_masked') required String assignedEmailMasked,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'workflow_id')
    required String workflowId,
    @JsonKey(name: 'target_locale') required String targetLocale,
    required AssignmentStatus status,
    @JsonKey(name: 'hard_deadline_at') required DateTime hardDeadlineAt,
    @JsonKey(name: 'relative_duration_seconds') int? relativeDurationSeconds,
  }) = _ExecutionAssignmentPreviewDto;

  factory ExecutionAssignmentPreviewDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionAssignmentPreviewDtoFromJson(json);
}

/// Payload for activating a single-use task assignment and auto-onboarding the assignee.
@Freezed(equal: false)
abstract class ExecutionAssignmentOnboardingRequestDto
    with _$ExecutionAssignmentOnboardingRequestDto {
  const ExecutionAssignmentOnboardingRequestDto._();

  @JsonSerializable(
    explicitToJson: true,
    disallowUnrecognizedKeys: true,
    includeIfNull: false,
  )
  const factory ExecutionAssignmentOnboardingRequestDto({
    @JsonKey(name: 'firebase_token') String? firebaseToken,
    String? name,
  }) = _ExecutionAssignmentOnboardingRequestDto;

  factory ExecutionAssignmentOnboardingRequestDto.fromJson(
    Map<String, dynamic> json,
  ) => _$ExecutionAssignmentOnboardingRequestDtoFromJson(json);
}

/// Payload for auto-saving assignee draft inputs prior to final submission.
@Freezed(equal: false)
abstract class ExecutionAssignmentDraftDto with _$ExecutionAssignmentDraftDto {
  const ExecutionAssignmentDraftDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionAssignmentDraftDto({
    @JsonKey(name: 'draft_inputs') required WorkflowInputs draftInputs,
  }) = _ExecutionAssignmentDraftDto;

  factory ExecutionAssignmentDraftDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionAssignmentDraftDtoFromJson(json);
}

/// Payload for submitting a single-use workflow execution assignment.
@Freezed(equal: false)
abstract class ExecutionAssignmentSubmitDto
    with _$ExecutionAssignmentSubmitDto {
  const ExecutionAssignmentSubmitDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory ExecutionAssignmentSubmitDto({
    @JsonKey(name: 'submitted_inputs') required WorkflowInputs submittedInputs,
  }) = _ExecutionAssignmentSubmitDto;

  factory ExecutionAssignmentSubmitDto.fromJson(Map<String, dynamic> json) =>
      _$ExecutionAssignmentSubmitDtoFromJson(json);
}
