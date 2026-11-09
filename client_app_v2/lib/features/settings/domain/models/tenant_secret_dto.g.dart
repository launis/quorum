// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tenant_secret_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_Organization _$OrganizationFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_Organization',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'name',
        'created_at',
        'is_active',
        'tier',
        'contact_email',
        'billing_id',
        'subscription_status',
        'quota_limit',
        'tpm_limit',
        'rpm_limit',
        'allowed_email_domains',
      ],
    );
    final val = _Organization(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String?),
      name: $checkedConvert('name', (v) => v as String),
      createdAt: $checkedConvert(
        'created_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      isActive: $checkedConvert('is_active', (v) => v as bool? ?? true),
      tier: $checkedConvert('tier', (v) => v as String? ?? 'standard'),
      contactEmail: $checkedConvert('contact_email', (v) => v as String?),
      billingId: $checkedConvert('billing_id', (v) => v as String?),
      subscriptionStatus: $checkedConvert(
        'subscription_status',
        (v) =>
            $enumDecodeNullable(_$SubscriptionStatusEnumMap, v) ??
            SubscriptionStatus.active,
      ),
      quotaLimit: $checkedConvert(
        'quota_limit',
        (v) => (v as num?)?.toDouble() ?? 0.0,
      ),
      tpmLimit: $checkedConvert(
        'tpm_limit',
        (v) => (v as num?)?.toInt() ?? 100000,
      ),
      rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num?)?.toInt() ?? 60),
      allowedEmailDomains: $checkedConvert(
        'allowed_email_domains',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'createdAt': 'created_at',
    'isActive': 'is_active',
    'contactEmail': 'contact_email',
    'billingId': 'billing_id',
    'subscriptionStatus': 'subscription_status',
    'quotaLimit': 'quota_limit',
    'tpmLimit': 'tpm_limit',
    'rpmLimit': 'rpm_limit',
    'allowedEmailDomains': 'allowed_email_domains',
  },
);

Map<String, dynamic> _$OrganizationToJson(_Organization instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'name': instance.name,
      'created_at': instance.createdAt?.toIso8601String(),
      'is_active': instance.isActive,
      'tier': instance.tier,
      'contact_email': instance.contactEmail,
      'billing_id': instance.billingId,
      'subscription_status':
          _$SubscriptionStatusEnumMap[instance.subscriptionStatus]!,
      'quota_limit': instance.quotaLimit,
      'tpm_limit': instance.tpmLimit,
      'rpm_limit': instance.rpmLimit,
      'allowed_email_domains': instance.allowedEmailDomains,
    };

const _$SubscriptionStatusEnumMap = {
  SubscriptionStatus.active: 'active',
  SubscriptionStatus.trial: 'trial',
  SubscriptionStatus.pastDue: 'past_due',
  SubscriptionStatus.canceled: 'canceled',
};

_OrganizationUpdateDto _$OrganizationUpdateDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_OrganizationUpdateDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'name',
        'tier',
        'is_active',
        'contact_email',
        'billing_id',
        'subscription_status',
        'quota_limit',
        'tpm_limit',
        'rpm_limit',
        'allowed_email_domains',
      ],
    );
    final val = _OrganizationUpdateDto(
      name: $checkedConvert('name', (v) => v as String?),
      tier: $checkedConvert('tier', (v) => v as String?),
      isActive: $checkedConvert('is_active', (v) => v as bool?),
      contactEmail: $checkedConvert('contact_email', (v) => v as String?),
      billingId: $checkedConvert('billing_id', (v) => v as String?),
      subscriptionStatus: $checkedConvert(
        'subscription_status',
        (v) => $enumDecodeNullable(_$SubscriptionStatusEnumMap, v),
      ),
      quotaLimit: $checkedConvert(
        'quota_limit',
        (v) => (v as num?)?.toDouble(),
      ),
      tpmLimit: $checkedConvert('tpm_limit', (v) => (v as num?)?.toInt()),
      rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num?)?.toInt()),
      allowedEmailDomains: $checkedConvert(
        'allowed_email_domains',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'isActive': 'is_active',
    'contactEmail': 'contact_email',
    'billingId': 'billing_id',
    'subscriptionStatus': 'subscription_status',
    'quotaLimit': 'quota_limit',
    'tpmLimit': 'tpm_limit',
    'rpmLimit': 'rpm_limit',
    'allowedEmailDomains': 'allowed_email_domains',
  },
);

Map<String, dynamic> _$OrganizationUpdateDtoToJson(
  _OrganizationUpdateDto instance,
) => <String, dynamic>{
  'name': ?instance.name,
  'tier': ?instance.tier,
  'is_active': ?instance.isActive,
  'contact_email': ?instance.contactEmail,
  'billing_id': ?instance.billingId,
  'subscription_status':
      ?_$SubscriptionStatusEnumMap[instance.subscriptionStatus],
  'quota_limit': ?instance.quotaLimit,
  'tpm_limit': ?instance.tpmLimit,
  'rpm_limit': ?instance.rpmLimit,
  'allowed_email_domains': ?instance.allowedEmailDomains,
};

_OrganizationDeleteResponse _$OrganizationDeleteResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_OrganizationDeleteResponse', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['status', 'deleted_id']);
  final val = _OrganizationDeleteResponse(
    status: $checkedConvert('status', (v) => v as String),
    deletedId: $checkedConvert(
      'deleted_id',
      (v) => const StrictOpaqueIdConverter().fromJson(v as String),
    ),
  );
  return val;
}, fieldKeyMap: const {'deletedId': 'deleted_id'});

Map<String, dynamic> _$OrganizationDeleteResponseToJson(
  _OrganizationDeleteResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'deleted_id': const StrictOpaqueIdConverter().toJson(instance.deletedId),
};

_UserDeleteResponse _$UserDeleteResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_UserDeleteResponse', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['status', 'id']);
      final val = _UserDeleteResponse(
        status: $checkedConvert('status', (v) => v as String),
        id: $checkedConvert(
          'id',
          (v) => const StrictOpaqueIdConverter().fromJson(v as String),
        ),
      );
      return val;
    });

Map<String, dynamic> _$UserDeleteResponseToJson(_UserDeleteResponse instance) =>
    <String, dynamic>{
      'status': instance.status,
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
    };

_InvitationCreateDto _$InvitationCreateDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_InvitationCreateDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['email', 'role', 'expires_in_hours'],
        );
        final val = _InvitationCreateDto(
          email: $checkedConvert('email', (v) => v as String),
          role: $checkedConvert(
            'role',
            (v) => $enumDecodeNullable(_$UserRoleEnumMap, v) ?? UserRole.member,
          ),
          expiresInHours: $checkedConvert(
            'expires_in_hours',
            (v) => (v as num?)?.toInt() ?? 168,
          ),
        );
        return val;
      },
      fieldKeyMap: const {'expiresInHours': 'expires_in_hours'},
    );

Map<String, dynamic> _$InvitationCreateDtoToJson(
  _InvitationCreateDto instance,
) => <String, dynamic>{
  'email': instance.email,
  'role': instance.role.toJson(),
  'expires_in_hours': instance.expiresInHours,
};

const _$UserRoleEnumMap = {
  UserRole.root: 'ROOT',
  UserRole.admin: 'ADMIN',
  UserRole.manager: 'MANAGER',
  UserRole.member: 'MEMBER',
  UserRole.viewer: 'VIEWER',
  UserRole.unknown: 'UNKNOWN',
};

_InvitationResponseDto _$InvitationResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_InvitationResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'organization_id',
        'email',
        'role',
        'status',
        'email_delivery_status',
        'invited_by',
        'expires_at',
        'created_at',
      ],
    );
    final val = _InvitationResponseDto(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      organizationId: $checkedConvert(
        'organization_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      email: $checkedConvert('email', (v) => v as String),
      role: $checkedConvert('role', (v) => $enumDecode(_$UserRoleEnumMap, v)),
      status: $checkedConvert(
        'status',
        (v) => $enumDecode(_$InvitationStatusEnumMap, v),
      ),
      emailDeliveryStatus: $checkedConvert(
        'email_delivery_status',
        (v) =>
            $enumDecodeNullable(_$EmailDeliveryStatusEnumMap, v) ??
            EmailDeliveryStatus.pending,
      ),
      invitedBy: $checkedConvert(
        'invited_by',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      expiresAt: $checkedConvert(
        'expires_at',
        (v) => DateTime.parse(v as String),
      ),
      createdAt: $checkedConvert(
        'created_at',
        (v) => DateTime.parse(v as String),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'emailDeliveryStatus': 'email_delivery_status',
    'invitedBy': 'invited_by',
    'expiresAt': 'expires_at',
    'createdAt': 'created_at',
  },
);

Map<String, dynamic> _$InvitationResponseDtoToJson(
  _InvitationResponseDto instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'organization_id': const StrictOpaqueIdConverter().toJson(
    instance.organizationId,
  ),
  'email': instance.email,
  'role': instance.role.toJson(),
  'status': _$InvitationStatusEnumMap[instance.status]!,
  'email_delivery_status':
      _$EmailDeliveryStatusEnumMap[instance.emailDeliveryStatus]!,
  'invited_by': const StrictOpaqueIdConverter().toJson(instance.invitedBy),
  'expires_at': instance.expiresAt.toIso8601String(),
  'created_at': instance.createdAt.toIso8601String(),
};

const _$InvitationStatusEnumMap = {
  InvitationStatus.pending: 'pending',
  InvitationStatus.accepted: 'accepted',
  InvitationStatus.expired: 'expired',
  InvitationStatus.revoked: 'revoked',
};

const _$EmailDeliveryStatusEnumMap = {
  EmailDeliveryStatus.pending: 'pending',
  EmailDeliveryStatus.sent: 'sent',
  EmailDeliveryStatus.failed: 'failed',
};

_InvitationBatchCreateDto _$InvitationBatchCreateDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_InvitationBatchCreateDto', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['recipients']);
  final val = _InvitationBatchCreateDto(
    recipients: $checkedConvert(
      'recipients',
      (v) => (v as List<dynamic>)
          .map((e) => InvitationCreateDto.fromJson(e as Map<String, dynamic>))
          .toList(),
    ),
  );
  return val;
});

Map<String, dynamic> _$InvitationBatchCreateDtoToJson(
  _InvitationBatchCreateDto instance,
) => <String, dynamic>{
  'recipients': instance.recipients.map((e) => e.toJson()).toList(),
};

_InvitationBatchResponseDto _$InvitationBatchResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_InvitationBatchResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['created_count', 'invitations']);
    final val = _InvitationBatchResponseDto(
      createdCount: $checkedConvert('created_count', (v) => (v as num).toInt()),
      invitations: $checkedConvert(
        'invitations',
        (v) => (v as List<dynamic>)
            .map(
              (e) => InvitationResponseDto.fromJson(e as Map<String, dynamic>),
            )
            .toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'createdCount': 'created_count'},
);

Map<String, dynamic> _$InvitationBatchResponseDtoToJson(
  _InvitationBatchResponseDto instance,
) => <String, dynamic>{
  'created_count': instance.createdCount,
  'invitations': instance.invitations.map((e) => e.toJson()).toList(),
};

_TenantSecretCreateDto _$TenantSecretCreateDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_TenantSecretCreateDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'scope',
        'target_identifier',
        'plaintext_secret',
        'storage_mode',
      ],
    );
    final val = _TenantSecretCreateDto(
      scope: $checkedConvert(
        'scope',
        (v) => $enumDecode(_$SecretScopeEnumMap, v),
      ),
      targetIdentifier: $checkedConvert(
        'target_identifier',
        (v) => v as String,
      ),
      plaintextSecret: $checkedConvert('plaintext_secret', (v) => v as String),
      storageMode: $checkedConvert(
        'storage_mode',
        (v) => $enumDecode(_$SecretStorageModeEnumMap, v),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'targetIdentifier': 'target_identifier',
    'plaintextSecret': 'plaintext_secret',
    'storageMode': 'storage_mode',
  },
);

Map<String, dynamic> _$TenantSecretCreateDtoToJson(
  _TenantSecretCreateDto instance,
) => <String, dynamic>{
  'scope': _$SecretScopeEnumMap[instance.scope]!,
  'target_identifier': instance.targetIdentifier,
  'plaintext_secret': instance.plaintextSecret,
  'storage_mode': _$SecretStorageModeEnumMap[instance.storageMode]!,
};

const _$SecretScopeEnumMap = {
  SecretScope.llmProvider: 'llm_provider',
  SecretScope.mcpGateway: 'mcp_gateway',
  SecretScope.telemetry: 'telemetry',
};

const _$SecretStorageModeEnumMap = {
  SecretStorageMode.cloudSecretManager: 'cloud_secret_manager',
  SecretStorageMode.envelopeKms: 'envelope_kms',
};

_TenantSecretResponseDto _$TenantSecretResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_TenantSecretResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'organization_id',
        'scope',
        'target_identifier',
        'storage_mode',
        'configured',
        'masked_hint',
        'kek_version',
        'updated_at',
      ],
    );
    final val = _TenantSecretResponseDto(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      organizationId: $checkedConvert(
        'organization_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      scope: $checkedConvert(
        'scope',
        (v) => $enumDecode(_$SecretScopeEnumMap, v),
      ),
      targetIdentifier: $checkedConvert(
        'target_identifier',
        (v) => v as String,
      ),
      storageMode: $checkedConvert(
        'storage_mode',
        (v) => $enumDecode(_$SecretStorageModeEnumMap, v),
      ),
      configured: $checkedConvert('configured', (v) => v as bool? ?? true),
      maskedHint: $checkedConvert('masked_hint', (v) => v as String),
      kekVersion: $checkedConvert('kek_version', (v) => v as String),
      updatedAt: $checkedConvert(
        'updated_at',
        (v) => DateTime.parse(v as String),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'targetIdentifier': 'target_identifier',
    'storageMode': 'storage_mode',
    'maskedHint': 'masked_hint',
    'kekVersion': 'kek_version',
    'updatedAt': 'updated_at',
  },
);

Map<String, dynamic> _$TenantSecretResponseDtoToJson(
  _TenantSecretResponseDto instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'organization_id': const StrictOpaqueIdConverter().toJson(
    instance.organizationId,
  ),
  'scope': _$SecretScopeEnumMap[instance.scope]!,
  'target_identifier': instance.targetIdentifier,
  'storage_mode': _$SecretStorageModeEnumMap[instance.storageMode]!,
  'configured': instance.configured,
  'masked_hint': instance.maskedHint,
  'kek_version': instance.kekVersion,
  'updated_at': instance.updatedAt.toIso8601String(),
};

_ExecutionAssignmentCreateDto _$ExecutionAssignmentCreateDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentCreateDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'assigned_email',
        'invited_role',
        'workflow_id',
        'output_profile_id',
        'target_locale',
        'locked_inputs',
        'assignee_input_keys',
        'result_visibility',
        'hard_deadline_at',
        'relative_duration_seconds',
      ],
    );
    final val = _ExecutionAssignmentCreateDto(
      assignedEmail: $checkedConvert('assigned_email', (v) => v as String),
      invitedRole: $checkedConvert(
        'invited_role',
        (v) => $enumDecodeNullable(_$UserRoleEnumMap, v) ?? UserRole.member,
      ),
      workflowId: $checkedConvert(
        'workflow_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      outputProfileId: $checkedConvert(
        'output_profile_id',
        (v) => v as String?,
      ),
      targetLocale: $checkedConvert(
        'target_locale',
        (v) => v as String? ?? 'fi',
      ),
      lockedInputs: $checkedConvert(
        'locked_inputs',
        (v) => WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
      assigneeInputKeys: $checkedConvert(
        'assignee_input_keys',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      resultVisibility: $checkedConvert(
        'result_visibility',
        (v) =>
            $enumDecodeNullable(_$AssignmentResultVisibilityEnumMap, v) ??
            AssignmentResultVisibility.confirmationOnly,
      ),
      hardDeadlineAt: $checkedConvert(
        'hard_deadline_at',
        (v) => DateTime.parse(v as String),
      ),
      relativeDurationSeconds: $checkedConvert(
        'relative_duration_seconds',
        (v) => (v as num?)?.toInt(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'assignedEmail': 'assigned_email',
    'invitedRole': 'invited_role',
    'workflowId': 'workflow_id',
    'outputProfileId': 'output_profile_id',
    'targetLocale': 'target_locale',
    'lockedInputs': 'locked_inputs',
    'assigneeInputKeys': 'assignee_input_keys',
    'resultVisibility': 'result_visibility',
    'hardDeadlineAt': 'hard_deadline_at',
    'relativeDurationSeconds': 'relative_duration_seconds',
  },
);

Map<String, dynamic> _$ExecutionAssignmentCreateDtoToJson(
  _ExecutionAssignmentCreateDto instance,
) => <String, dynamic>{
  'assigned_email': instance.assignedEmail,
  'invited_role': instance.invitedRole.toJson(),
  'workflow_id': const StrictOpaqueIdConverter().toJson(instance.workflowId),
  'output_profile_id': ?instance.outputProfileId,
  'target_locale': instance.targetLocale,
  'locked_inputs': instance.lockedInputs.toJson(),
  'assignee_input_keys': instance.assigneeInputKeys,
  'result_visibility':
      _$AssignmentResultVisibilityEnumMap[instance.resultVisibility]!,
  'hard_deadline_at': instance.hardDeadlineAt.toIso8601String(),
  'relative_duration_seconds': ?instance.relativeDurationSeconds,
};

const _$AssignmentResultVisibilityEnumMap = {
  AssignmentResultVisibility.confirmationOnly: 'confirmation_only',
  AssignmentResultVisibility.fullReportAccess: 'full_report_access',
};

_ExecutionAssignmentRecipientDto _$ExecutionAssignmentRecipientDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentRecipientDto',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['email', 'name', 'target_locale']);
    final val = _ExecutionAssignmentRecipientDto(
      email: $checkedConvert('email', (v) => v as String),
      name: $checkedConvert('name', (v) => v as String?),
      targetLocale: $checkedConvert('target_locale', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'targetLocale': 'target_locale'},
);

Map<String, dynamic> _$ExecutionAssignmentRecipientDtoToJson(
  _ExecutionAssignmentRecipientDto instance,
) => <String, dynamic>{
  'email': instance.email,
  'name': ?instance.name,
  'target_locale': ?instance.targetLocale,
};

_ExecutionAssignmentBatchCreateDto _$ExecutionAssignmentBatchCreateDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentBatchCreateDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'recipients',
        'invited_role',
        'workflow_id',
        'output_profile_id',
        'target_locale',
        'locked_inputs',
        'assignee_input_keys',
        'result_visibility',
        'hard_deadline_at',
        'relative_duration_seconds',
      ],
    );
    final val = _ExecutionAssignmentBatchCreateDto(
      recipients: $checkedConvert(
        'recipients',
        (v) => (v as List<dynamic>)
            .map(
              (e) => ExecutionAssignmentRecipientDto.fromJson(
                e as Map<String, dynamic>,
              ),
            )
            .toList(),
      ),
      invitedRole: $checkedConvert(
        'invited_role',
        (v) => $enumDecodeNullable(_$UserRoleEnumMap, v) ?? UserRole.member,
      ),
      workflowId: $checkedConvert(
        'workflow_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      outputProfileId: $checkedConvert(
        'output_profile_id',
        (v) => v as String?,
      ),
      targetLocale: $checkedConvert(
        'target_locale',
        (v) => v as String? ?? 'fi',
      ),
      lockedInputs: $checkedConvert(
        'locked_inputs',
        (v) => WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
      assigneeInputKeys: $checkedConvert(
        'assignee_input_keys',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      resultVisibility: $checkedConvert(
        'result_visibility',
        (v) =>
            $enumDecodeNullable(_$AssignmentResultVisibilityEnumMap, v) ??
            AssignmentResultVisibility.confirmationOnly,
      ),
      hardDeadlineAt: $checkedConvert(
        'hard_deadline_at',
        (v) => DateTime.parse(v as String),
      ),
      relativeDurationSeconds: $checkedConvert(
        'relative_duration_seconds',
        (v) => (v as num?)?.toInt(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'invitedRole': 'invited_role',
    'workflowId': 'workflow_id',
    'outputProfileId': 'output_profile_id',
    'targetLocale': 'target_locale',
    'lockedInputs': 'locked_inputs',
    'assigneeInputKeys': 'assignee_input_keys',
    'resultVisibility': 'result_visibility',
    'hardDeadlineAt': 'hard_deadline_at',
    'relativeDurationSeconds': 'relative_duration_seconds',
  },
);

Map<String, dynamic> _$ExecutionAssignmentBatchCreateDtoToJson(
  _ExecutionAssignmentBatchCreateDto instance,
) => <String, dynamic>{
  'recipients': instance.recipients.map((e) => e.toJson()).toList(),
  'invited_role': instance.invitedRole.toJson(),
  'workflow_id': const StrictOpaqueIdConverter().toJson(instance.workflowId),
  'output_profile_id': ?instance.outputProfileId,
  'target_locale': instance.targetLocale,
  'locked_inputs': instance.lockedInputs.toJson(),
  'assignee_input_keys': instance.assigneeInputKeys,
  'result_visibility':
      _$AssignmentResultVisibilityEnumMap[instance.resultVisibility]!,
  'hard_deadline_at': instance.hardDeadlineAt.toIso8601String(),
  'relative_duration_seconds': ?instance.relativeDurationSeconds,
};

_ExecutionAssignmentResponseDto _$ExecutionAssignmentResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'batch_id',
        'organization_id',
        'assigned_email',
        'assigned_user_id',
        'invited_role',
        'workflow_id',
        'output_profile_id',
        'target_locale',
        'locked_inputs',
        'assignee_input_keys',
        'draft_inputs',
        'status',
        'email_delivery_status',
        'result_visibility',
        'hard_deadline_at',
        'relative_duration_seconds',
        'activated_at',
        'submitted_at',
        'execution_id',
        'created_by',
        'created_at',
      ],
    );
    final val = _ExecutionAssignmentResponseDto(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      batchId: $checkedConvert('batch_id', (v) => v as String?),
      organizationId: $checkedConvert(
        'organization_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      assignedEmail: $checkedConvert('assigned_email', (v) => v as String),
      assignedUserId: $checkedConvert('assigned_user_id', (v) => v as String?),
      invitedRole: $checkedConvert(
        'invited_role',
        (v) => $enumDecode(_$UserRoleEnumMap, v),
      ),
      workflowId: $checkedConvert(
        'workflow_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      outputProfileId: $checkedConvert(
        'output_profile_id',
        (v) => v as String?,
      ),
      targetLocale: $checkedConvert('target_locale', (v) => v as String),
      lockedInputs: $checkedConvert(
        'locked_inputs',
        (v) => WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
      assigneeInputKeys: $checkedConvert(
        'assignee_input_keys',
        (v) => (v as List<dynamic>).map((e) => e as String).toList(),
      ),
      draftInputs: $checkedConvert(
        'draft_inputs',
        (v) => WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
      status: $checkedConvert(
        'status',
        (v) => $enumDecode(_$AssignmentStatusEnumMap, v),
      ),
      emailDeliveryStatus: $checkedConvert(
        'email_delivery_status',
        (v) =>
            $enumDecodeNullable(_$EmailDeliveryStatusEnumMap, v) ??
            EmailDeliveryStatus.pending,
      ),
      resultVisibility: $checkedConvert(
        'result_visibility',
        (v) => $enumDecode(_$AssignmentResultVisibilityEnumMap, v),
      ),
      hardDeadlineAt: $checkedConvert(
        'hard_deadline_at',
        (v) => DateTime.parse(v as String),
      ),
      relativeDurationSeconds: $checkedConvert(
        'relative_duration_seconds',
        (v) => (v as num?)?.toInt(),
      ),
      activatedAt: $checkedConvert(
        'activated_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      submittedAt: $checkedConvert(
        'submitted_at',
        (v) => v == null ? null : DateTime.parse(v as String),
      ),
      executionId: $checkedConvert('execution_id', (v) => v as String?),
      createdBy: $checkedConvert(
        'created_by',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      createdAt: $checkedConvert(
        'created_at',
        (v) => DateTime.parse(v as String),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'batchId': 'batch_id',
    'organizationId': 'organization_id',
    'assignedEmail': 'assigned_email',
    'assignedUserId': 'assigned_user_id',
    'invitedRole': 'invited_role',
    'workflowId': 'workflow_id',
    'outputProfileId': 'output_profile_id',
    'targetLocale': 'target_locale',
    'lockedInputs': 'locked_inputs',
    'assigneeInputKeys': 'assignee_input_keys',
    'draftInputs': 'draft_inputs',
    'emailDeliveryStatus': 'email_delivery_status',
    'resultVisibility': 'result_visibility',
    'hardDeadlineAt': 'hard_deadline_at',
    'relativeDurationSeconds': 'relative_duration_seconds',
    'activatedAt': 'activated_at',
    'submittedAt': 'submitted_at',
    'executionId': 'execution_id',
    'createdBy': 'created_by',
    'createdAt': 'created_at',
  },
);

Map<String, dynamic> _$ExecutionAssignmentResponseDtoToJson(
  _ExecutionAssignmentResponseDto instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'batch_id': instance.batchId,
  'organization_id': const StrictOpaqueIdConverter().toJson(
    instance.organizationId,
  ),
  'assigned_email': instance.assignedEmail,
  'assigned_user_id': instance.assignedUserId,
  'invited_role': instance.invitedRole.toJson(),
  'workflow_id': const StrictOpaqueIdConverter().toJson(instance.workflowId),
  'output_profile_id': instance.outputProfileId,
  'target_locale': instance.targetLocale,
  'locked_inputs': instance.lockedInputs.toJson(),
  'assignee_input_keys': instance.assigneeInputKeys,
  'draft_inputs': instance.draftInputs.toJson(),
  'status': _$AssignmentStatusEnumMap[instance.status]!,
  'email_delivery_status':
      _$EmailDeliveryStatusEnumMap[instance.emailDeliveryStatus]!,
  'result_visibility':
      _$AssignmentResultVisibilityEnumMap[instance.resultVisibility]!,
  'hard_deadline_at': instance.hardDeadlineAt.toIso8601String(),
  'relative_duration_seconds': instance.relativeDurationSeconds,
  'activated_at': instance.activatedAt?.toIso8601String(),
  'submitted_at': instance.submittedAt?.toIso8601String(),
  'execution_id': instance.executionId,
  'created_by': const StrictOpaqueIdConverter().toJson(instance.createdBy),
  'created_at': instance.createdAt.toIso8601String(),
};

const _$AssignmentStatusEnumMap = {
  AssignmentStatus.pending: 'pending',
  AssignmentStatus.activated: 'activated',
  AssignmentStatus.submitted: 'submitted',
  AssignmentStatus.completed: 'completed',
  AssignmentStatus.expired: 'expired',
  AssignmentStatus.revoked: 'revoked',
};

_ExecutionAssignmentBatchResponseDto
_$ExecutionAssignmentBatchResponseDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentBatchResponseDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['batch_id', 'created_count', 'assignments'],
    );
    final val = _ExecutionAssignmentBatchResponseDto(
      batchId: $checkedConvert(
        'batch_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      createdCount: $checkedConvert('created_count', (v) => (v as num).toInt()),
      assignments: $checkedConvert(
        'assignments',
        (v) => (v as List<dynamic>)
            .map(
              (e) => ExecutionAssignmentResponseDto.fromJson(
                e as Map<String, dynamic>,
              ),
            )
            .toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'batchId': 'batch_id', 'createdCount': 'created_count'},
);

Map<String, dynamic> _$ExecutionAssignmentBatchResponseDtoToJson(
  _ExecutionAssignmentBatchResponseDto instance,
) => <String, dynamic>{
  'batch_id': const StrictOpaqueIdConverter().toJson(instance.batchId),
  'created_count': instance.createdCount,
  'assignments': instance.assignments.map((e) => e.toJson()).toList(),
};

_ExecutionAssignmentPreviewDto _$ExecutionAssignmentPreviewDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentPreviewDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'organization_id',
        'organization_name',
        'assigned_email_masked',
        'workflow_id',
        'target_locale',
        'status',
        'hard_deadline_at',
        'relative_duration_seconds',
      ],
    );
    final val = _ExecutionAssignmentPreviewDto(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      organizationId: $checkedConvert(
        'organization_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      organizationName: $checkedConvert(
        'organization_name',
        (v) => v as String,
      ),
      assignedEmailMasked: $checkedConvert(
        'assigned_email_masked',
        (v) => v as String,
      ),
      workflowId: $checkedConvert(
        'workflow_id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      targetLocale: $checkedConvert('target_locale', (v) => v as String),
      status: $checkedConvert(
        'status',
        (v) => $enumDecode(_$AssignmentStatusEnumMap, v),
      ),
      hardDeadlineAt: $checkedConvert(
        'hard_deadline_at',
        (v) => DateTime.parse(v as String),
      ),
      relativeDurationSeconds: $checkedConvert(
        'relative_duration_seconds',
        (v) => (v as num?)?.toInt(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'organizationName': 'organization_name',
    'assignedEmailMasked': 'assigned_email_masked',
    'workflowId': 'workflow_id',
    'targetLocale': 'target_locale',
    'hardDeadlineAt': 'hard_deadline_at',
    'relativeDurationSeconds': 'relative_duration_seconds',
  },
);

Map<String, dynamic> _$ExecutionAssignmentPreviewDtoToJson(
  _ExecutionAssignmentPreviewDto instance,
) => <String, dynamic>{
  'id': const StrictOpaqueIdConverter().toJson(instance.id),
  'organization_id': const StrictOpaqueIdConverter().toJson(
    instance.organizationId,
  ),
  'organization_name': instance.organizationName,
  'assigned_email_masked': instance.assignedEmailMasked,
  'workflow_id': const StrictOpaqueIdConverter().toJson(instance.workflowId),
  'target_locale': instance.targetLocale,
  'status': _$AssignmentStatusEnumMap[instance.status]!,
  'hard_deadline_at': instance.hardDeadlineAt.toIso8601String(),
  'relative_duration_seconds': instance.relativeDurationSeconds,
};

_ExecutionAssignmentOnboardingRequestDto
_$ExecutionAssignmentOnboardingRequestDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionAssignmentOnboardingRequestDto',
      json,
      ($checkedConvert) {
        $checkKeys(json, allowedKeys: const ['firebase_token', 'name']);
        final val = _ExecutionAssignmentOnboardingRequestDto(
          firebaseToken: $checkedConvert('firebase_token', (v) => v as String?),
          name: $checkedConvert('name', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {'firebaseToken': 'firebase_token'},
    );

Map<String, dynamic> _$ExecutionAssignmentOnboardingRequestDtoToJson(
  _ExecutionAssignmentOnboardingRequestDto instance,
) => <String, dynamic>{
  'firebase_token': ?instance.firebaseToken,
  'name': ?instance.name,
};

_ExecutionAssignmentDraftDto _$ExecutionAssignmentDraftDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentDraftDto',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['draft_inputs']);
    final val = _ExecutionAssignmentDraftDto(
      draftInputs: $checkedConvert(
        'draft_inputs',
        (v) => WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'draftInputs': 'draft_inputs'},
);

Map<String, dynamic> _$ExecutionAssignmentDraftDtoToJson(
  _ExecutionAssignmentDraftDto instance,
) => <String, dynamic>{'draft_inputs': instance.draftInputs.toJson()};

_ExecutionAssignmentSubmitDto _$ExecutionAssignmentSubmitDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ExecutionAssignmentSubmitDto',
  json,
  ($checkedConvert) {
    $checkKeys(json, allowedKeys: const ['submitted_inputs']);
    final val = _ExecutionAssignmentSubmitDto(
      submittedInputs: $checkedConvert(
        'submitted_inputs',
        (v) => WorkflowInputs.fromJson(v as Map<String, dynamic>),
      ),
    );
    return val;
  },
  fieldKeyMap: const {'submittedInputs': 'submitted_inputs'},
);

Map<String, dynamic> _$ExecutionAssignmentSubmitDtoToJson(
  _ExecutionAssignmentSubmitDto instance,
) => <String, dynamic>{'submitted_inputs': instance.submittedInputs.toJson()};
