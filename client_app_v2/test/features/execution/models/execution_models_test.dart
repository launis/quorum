import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_inputs.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionMetadata Freezed Parity', () {
    test('instantiates from valid json with configuration fields', () {
      final json = {
        'matrix_sampling_strategy': 15,
        'workflow_version': 2,
        'global_context_vars': {'lang': 'fi'},
      };

      final meta = ExecutionMetadata.fromJson(json);
      expect(meta.matrixSamplingStrategy, 15);
      expect(meta.workflowVersion, 2);
      expect(meta.globalContextVars, {'lang': 'fi'});
    });

    test('defaults are populated when optional fields are omitted', () {
      final json = <String, dynamic>{};
      final meta = ExecutionMetadata.fromJson(json);
      expect(meta.matrixSamplingStrategy, isNull);
      expect(meta.workflowVersion, 1);
      expect(meta.globalContextVars, isNull);
    });
  });

  group('ExecutionInputs Freezed Parity', () {
    test('instantiates from valid json', () {
      final json = {
        'raw_inputs': {'input_1': 'Hello'},
        'dynamic_inputs': {'param_1': 42},
        'user_role': 'auditor',
        'target_locale': 'en',
      };

      final inputs = ExecutionInputs.fromJson(json);
      expect(inputs.rawInputs, {'input_1': 'Hello'});
      expect(inputs.dynamicInputs, {'param_1': 42});
      expect(inputs.userRole, 'auditor');
      expect(inputs.targetLocale, 'en');
    });

    test('defaults are empty maps when omitted', () {
      final inputs = ExecutionInputs.fromJson({});
      expect(inputs.rawInputs, isEmpty);
      expect(inputs.dynamicInputs, isEmpty);
      expect(inputs.userRole, isNull);
      expect(inputs.targetLocale, isNull);
    });
  });

  group('ExecutionCreateRequestDto Freezed Parity & Fail-Fast', () {
    test('instantiates from valid json with required fields', () {
      final json = {
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
        'raw_inputs': {
          'dynamic_inputs': {'doc': 'test'},
        },
        'profile_id': 'pro_1234567890abcdef',
        'matrix_sampling_strategy': 15,
      };

      final dto = ExecutionCreateRequestDto.fromJson(json);
      expect(dto.workflowId, 'wor_1234567890abcdef');
      expect(dto.targetLocale, 'fi');
      expect(dto.rawInputs, {
        'dynamic_inputs': {'doc': 'test'},
      });
      expect(dto.profileId, 'pro_1234567890abcdef');
      expect(dto.matrixSamplingStrategy, 15);
    });

    test('populates default empty map for raw_inputs when omitted', () {
      final json = {
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'en',
      };

      final dto = ExecutionCreateRequestDto.fromJson(json);
      expect(dto.workflowId, 'wor_1234567890abcdef');
      expect(dto.targetLocale, 'en');
      expect(dto.rawInputs, isEmpty);
      expect(dto.profileId, isNull);
    });

    test('test_flutter_execution_create_request_unexpected_key_throws', () {
      final json = {
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
        'unknown_field_123': 'invalid',
      };

      expect(
        () => ExecutionCreateRequestDto.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('ExecutionRecord Freezed Parity & Fail-Fast', () {
    test(
      'instantiates from valid json with required target_locale and metadata',
      () {
        final json = {
          'id': 'exe_1234567890abcdef',
          'workflow_id': 'wor_1234567890abcdef',
          'target_locale': 'fi',
          'status': 'PENDING',
          'strictness_level': 80,
          'metadata': {'workflow_version': 1},
        };

        final record = ExecutionRecord.fromJson(json);
        expect(record.id, 'exe_1234567890abcdef');
        expect(record.workflowId, 'wor_1234567890abcdef');
        expect(record.targetLocale, 'fi');
        expect(record.status, 'PENDING');
        expect(record.strictnessLevel, 80);
        expect(record.metadata?.workflowVersion, 1);
      },
    );

    test('test_flutter_execution_record_full_schema_deserialization', () {
      final json = {
        'id': 'exe_1234567890abcdef',
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
        'status': 'PASSED',
        'active_profile_id': 'pro_1234567890abcdef',
        'output_profile_id': 'pro_1234567890abcdef',
        'raw_inputs': {
          'dynamic_inputs': {'doc': 'test'},
        },
        'trace_version': '2.0',
        'strictness_level': 90,
        'duration_ms': 4500,
        'cost_estimate': 0.045,
        'prompt_tokens': 500,
        'completion_tokens': 100,
        'cached_tokens': 200,
        'reasoning_tokens': 50,
        'dag_cost_usd': 0.12,
        'cumulative_synthesis_tokens': 1200,
        'cumulative_synthesis_cost': 0.012,
        'models_used': ['gemini-1.5-pro'],
        'metadata': {'workflow_version': 1},
        'error': null,
        'is_resumable': true,
        'frozen_context': <String, dynamic>{'input': 'content'},
        'frozen_context_storage_path': 'gs://bucket/context.json',
        'context_variables': <String, dynamic>{'var1': 'val1'},
        'context_variables_storage_path': 'gs://bucket/vars.json',
        'execution_trace_storage_path': 'gs://bucket/trace.json',
        'pdf_report_path': '/reports/rep_1.pdf',
        'source_identity_manifest': <String, String>{'src_0': 'Doc A'},
        'steps': <Map<String, dynamic>>[],
        'step_states': <String, dynamic>{},
        'profile_syntheses': <String, dynamic>{},
        'results': <String, dynamic>{},
        'progress': 100,
        'status_message': 'Completed',
        'created_at': '2026-08-30T12:00:00Z',
        'updated_at': '2026-08-30T12:05:00Z',
        'completed_at': '2026-08-30T12:05:00Z',
        'created_by': 'usr_1',
        'organization_id': 'org_1',
      };

      final record = ExecutionRecord.fromJson(json);
      expect(record.id, 'exe_1234567890abcdef');
      expect(record.workflowId, 'wor_1234567890abcdef');
      expect(record.activeProfileId, 'pro_1234567890abcdef');
      expect(record.durationMs, 4500);
      expect(record.promptTokens, 500);
      expect(record.completionTokens, 100);
      expect(record.cachedTokens, 200);
      expect(record.reasoningTokens, 50);
      expect(record.dagCostUsd, 0.12);
      expect(record.cumulativeSynthesisTokens, 1200);
      expect(record.cumulativeSynthesisCost, 0.012);
      expect(record.modelsUsed, ['gemini-1.5-pro']);
      expect(record.organizationId, 'org_1');
      expect(record.createdBy, 'usr_1');
      expect(record.completedAt, '2026-08-30T12:05:00Z');
      expect(record.isResumable, true);
    });

    test('test_flutter_execution_record_deserializes_with_execution_trace', () {
      final json = {
        'id': 'exe_1234567890abcdef',
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
        'status': 'PASSED',
        'execution_trace': <Map<String, dynamic>>[
          {
            'event_type': 'tombstone',
            'step_id': 'stp_1',
            'status': 'PASSED',
            'timestamp': '2026-08-30T12:00:00Z',
          },
        ],
        'metadata': {'workflow_version': 1},
      };

      final record = ExecutionRecord.fromJson(json);
      expect(record.id, 'exe_1234567890abcdef');
    });

    test('throws when mandatory target_locale is missing', () {
      final json = {
        'id': 'exe_1234567890abcdef',
        'workflow_id': 'wor_1234567890abcdef',
        'status': 'PENDING',
      };

      expect(
        () => ExecutionRecord.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('test_flutter_execution_record_unexpected_key_throws', () {
      final json = {
        'id': 'exe_1234567890abcdef',
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
        'status': 'PENDING',
        'unknown_legacy_field': 'invalid_data',
      };

      expect(
        () => ExecutionRecord.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });
}
