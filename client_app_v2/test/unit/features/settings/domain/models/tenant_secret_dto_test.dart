import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  const validOrgId = 'org_01960000000070008000000000000001';
  const validUserId = 'usr_01960000000070008000000000000002';
  const validInvId = 'inv_01960000000070008000000000000003';
  const validSecId = 'sec_01960000000070008000000000000004';
  const validWfId = 'wf_01960000000070008000000000000005';
  const validTskId = 'tsk_01960000000070008000000000000006';
  const validBatchId = 'tsk_01960000000070008000000000000007';

  group('tenant_secret_dto Domain Models Hardening Tests', () {
    test(
      'Positive: serializes and deserializes Organization, Invitation, TenantSecret, and ExecutionAssignment DTOs with 1:1 snake_case parity',
      () {
        final org = Organization.fromJson({
          'id': validOrgId,
          'slug': 'quorum-ent',
          'name': 'Quorum Enterprise',
          'created_at': '2026-11-01T10:00:00.000Z',
          'is_active': true,
          'tier': 'enterprise',
          'contact_email': 'ops@quorum.ai',
          'billing_id': 'cus_123',
          'subscription_status': 'active',
          'quota_limit': 1500.5,
          'tpm_limit': 250000,
          'rpm_limit': 120,
          'allowed_email_domains': ['quorum.ai'],
        });
        expect(org.id, equals(validOrgId));
        expect(org.subscriptionStatus, equals(SubscriptionStatus.active));
        expect(org.allowedEmailDomains, equals(['quorum.ai']));
        expect(Organization.fromJson(org.toJson()).id, equals(validOrgId));

        const updateDto = OrganizationUpdateDto(
          name: 'Updated Name',
          subscriptionStatus: SubscriptionStatus.trial,
        );
        final updateJson = updateDto.toJson();
        expect(updateJson['name'], equals('Updated Name'));
        expect(updateJson['subscription_status'], equals('trial'));
        expect(updateJson.containsKey('billing_id'), isFalse);

        final orgDelete = OrganizationDeleteResponse.fromJson({
          'status': 'deleted',
          'deleted_id': validOrgId,
        });
        expect(orgDelete.deletedId, equals(validOrgId));
        expect(orgDelete.toJson()['deleted_id'], equals(validOrgId));

        final userDelete = UserDeleteResponse.fromJson({
          'status': 'deleted',
          'id': validUserId,
        });
        expect(userDelete.id, equals(validUserId));

        final invBatchReq = InvitationBatchCreateDto.fromJson({
          'recipients': [
            {
              'email': 'alice@quorum.ai',
              'role': 'MANAGER',
              'expires_in_hours': 72,
            },
          ],
        });
        expect(invBatchReq.recipients.single.role, equals(UserRole.manager));
        expect(invBatchReq.recipients.single.expiresInHours, equals(72));

        final invBatchRes = InvitationBatchResponseDto.fromJson({
          'created_count': 1,
          'invitations': [
            {
              'id': validInvId,
              'organization_id': validOrgId,
              'email': 'alice@quorum.ai',
              'role': 'MANAGER',
              'status': 'pending',
              'email_delivery_status': 'sent',
              'invited_by': validUserId,
              'expires_at': '2026-11-10T10:00:00.000Z',
              'created_at': '2026-11-01T10:00:00.000Z',
            },
          ],
        });
        expect(invBatchRes.createdCount, equals(1));
        expect(
          invBatchRes.invitations.single.emailDeliveryStatus,
          equals(EmailDeliveryStatus.sent),
        );

        final secretCreate = TenantSecretCreateDto.fromJson({
          'scope': 'llm_provider',
          'target_identifier': 'google',
          'plaintext_secret': 'test-placeholder-value',
          'storage_mode': 'envelope_kms',
        });
        expect(secretCreate.scope, equals(SecretScope.llmProvider));
        expect(secretCreate.storageMode, equals(SecretStorageMode.envelopeKms));
        expect(secretCreate.toJson()['target_identifier'], equals('google'));
        expect(secretCreate.toJson()['storage_mode'], equals('envelope_kms'));

        final secretRes = TenantSecretResponseDto.fromJson({
          'id': validSecId,
          'organization_id': validOrgId,
          'scope': 'mcp_gateway',
          'target_identifier': 'sys_01960000000070008000000000000099',
          'storage_mode': 'envelope_kms',
          'configured': true,
          'masked_hint': '...abcd',
          'kek_version': 'v1',
          'updated_at': '2026-11-02T12:00:00.000Z',
        });
        expect(secretRes.scope, equals(SecretScope.mcpGateway));
        expect(secretRes.storageMode, equals(SecretStorageMode.envelopeKms));

        final assignmentCreate = ExecutionAssignmentCreateDto.fromJson({
          'assigned_email': 'exec@quorum.ai',
          'invited_role': 'MEMBER',
          'workflow_id': validWfId,
          'target_locale': 'fi',
          'locked_inputs': {
            'dynamic_inputs': {'brief': 'Context doc'},
          },
          'assignee_input_keys': ['candidate_notes'],
          'result_visibility': 'full_report_access',
          'hard_deadline_at': '2026-12-01T00:00:00.000Z',
          'relative_duration_seconds': 3600,
        });
        expect(
          assignmentCreate.resultVisibility,
          equals(AssignmentResultVisibility.fullReportAccess),
        );

        final batchCreate = ExecutionAssignmentBatchCreateDto.fromJson({
          'recipients': [
            {'email': 'one@quorum.ai', 'name': 'One', 'target_locale': 'en'},
          ],
          'workflow_id': validWfId,
          'locked_inputs': const <String, dynamic>{},
          'hard_deadline_at': '2026-12-01T00:00:00.000Z',
        });
        expect(batchCreate.recipients.single.name, equals('One'));

        final batchRes = ExecutionAssignmentBatchResponseDto.fromJson({
          'batch_id': validBatchId,
          'created_count': 1,
          'assignments': [
            {
              'id': validTskId,
              'batch_id': validBatchId,
              'organization_id': validOrgId,
              'assigned_email': 'one@quorum.ai',
              'invited_role': 'MEMBER',
              'workflow_id': validWfId,
              'target_locale': 'en',
              'locked_inputs': const <String, dynamic>{},
              'assignee_input_keys': ['input_a'],
              'draft_inputs': const <String, dynamic>{},
              'status': 'activated',
              'email_delivery_status': 'sent',
              'result_visibility': 'confirmation_only',
              'hard_deadline_at': '2026-12-01T00:00:00.000Z',
              'created_by': validUserId,
              'created_at': '2026-11-01T00:00:00.000Z',
            },
          ],
        });
        expect(batchRes.batchId, equals(validBatchId));
        expect(
          batchRes.assignments.single.status,
          equals(AssignmentStatus.activated),
        );

        final preview = ExecutionAssignmentPreviewDto.fromJson({
          'id': validTskId,
          'organization_id': validOrgId,
          'organization_name': 'Quorum Enterprise',
          'assigned_email_masked': 'o***@quorum.ai',
          'workflow_id': validWfId,
          'target_locale': 'fi',
          'status': 'pending',
          'hard_deadline_at': '2026-12-01T00:00:00.000Z',
        });
        expect(preview.organizationName, equals('Quorum Enterprise'));

        final onboarding = ExecutionAssignmentOnboardingRequestDto.fromJson({
          'name': 'Onboarded User',
        });
        expect(onboarding.toJson().containsKey('firebase_token'), isFalse);

        final draft = ExecutionAssignmentDraftDto.fromJson({
          'draft_inputs': {
            'dynamic_inputs': {'draft_key': 'Draft text'},
          },
        });
        expect(
          draft.draftInputs.dynamicInputs['draft_key'],
          equals('Draft text'),
        );

        final submit = ExecutionAssignmentSubmitDto.fromJson({
          'submitted_inputs': {
            'dynamic_inputs': {'final_key': 'Final text'},
          },
        });
        expect(
          submit.submittedInputs.dynamicInputs['final_key'],
          equals('Final text'),
        );
      },
    );

    test(
      'Negative/Boundary 1: rejects unrecognized JSON keys and missing required fields across DTOs (disallowUnrecognizedKeys: true)',
      () {
        expect(
          () => Organization.fromJson({
            'id': validOrgId,
            'name': 'Quorum',
            'unexpected_shadow_key': true,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => Organization.fromJson({
            'id': validOrgId,
            'name': 'Quorum',
            'subscription_status': 'ACTIVE',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => TenantSecretCreateDto.fromJson({
            'scope': 'llm_provider',
            'target_identifier': 'openai',
            'plaintext_secret': 'placeholder',
            'storage_mode': 'envelope_kms',
            'extra_field': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => TenantSecretCreateDto.fromJson({
            'scope': 'llm_provider',
            'target_identifier': 'openai',
            'plaintext_secret': 'placeholder',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        expect(
          () => ExecutionAssignmentDraftDto.fromJson({
            'draft_inputs': const <String, dynamic>{},
            'unknown_flag': 1,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Missing required fields must throw CheckedFromJsonException
        expect(
          () => InvitationResponseDto.fromJson({'id': validInvId}),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative/Boundary 2: StrictOpaqueIdConverter rejects non-32-hex / truncated IDs and @Freezed(equal: false) enforces O(1) identity equality',
      () {
        for (final invalidId in [
          '',
          'org_1234',
          'org_0196000000007000800000000000000', // 31 hex chars (min - 1)
          'org_019600000000700080000000000000012', // 33 hex chars (max + 1)
          'INVALID_PREFIX_01960000000070008000000000000001',
        ]) {
          expect(
            () =>
                Organization.fromJson({'id': invalidId, 'name': 'Invalid Org'}),
            throwsA(
              isA<CheckedFromJsonException>().having(
                (e) => e.innerError,
                'innerError',
                isA<AppException>(),
              ),
            ),
          );

          expect(
            () => Organization(id: invalidId, name: 'Invalid Org').toJson(),
            throwsA(isA<AppException>()),
          );

          expect(
            () => OrganizationDeleteResponse.fromJson({
              'status': 'deleted',
              'deleted_id': invalidId,
            }),
            throwsA(
              isA<CheckedFromJsonException>().having(
                (e) => e.innerError,
                'innerError',
                isA<AppException>(),
              ),
            ),
          );

          expect(
            () => UserDeleteResponse.fromJson({
              'status': 'deleted',
              'id': invalidId,
            }),
            throwsA(
              isA<CheckedFromJsonException>().having(
                (e) => e.innerError,
                'innerError',
                isA<AppException>(),
              ),
            ),
          );
        }

        // Verify @Freezed(equal: false) identity equality on runtime instances
        TenantSecretCreateDto buildRuntimeSecret(String target) =>
            TenantSecretCreateDto(
              scope: SecretScope.llmProvider,
              targetIdentifier: target,
              plaintextSecret: 'placeholder',
              storageMode: SecretStorageMode.envelopeKms,
            );

        final first = buildRuntimeSecret('openai');
        final second = buildRuntimeSecret('openai');
        expect(identical(first, second), isFalse);
        expect(first == second, isFalse);
        expect(first == first, isTrue);

        ExecutionAssignmentDraftDto buildRuntimeDraft(String docVal) =>
            ExecutionAssignmentDraftDto(
              draftInputs: WorkflowInputs(
                dynamicInputs: {'k': WorkflowInputValue(textValue: docVal)},
              ),
            );

        final draftA = buildRuntimeDraft('v');
        final draftB = buildRuntimeDraft('v');
        expect(draftA == draftB, isFalse);
      },
    );
  });
}
