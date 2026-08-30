import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/execution/models/execution_inputs.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_record.dart';

void main() {
  group('ExecutionMetadata Freezed Parity', () {
    test('instantiates from valid json with mandatory target_locale', () {
      final json = {
        'target_locale': 'fi',
        'matrix_sampling_strategy': 15,
        'workflow_version': 2,
        'user_id': 'usr_1',
        'organization_id': 'org_1',
        'global_context_vars': {'lang': 'fi'},
        'execution_summary': {'score': 90},
        'step_metrics': {'s1': 0.05},
        'dag_cost_usd': 0.12,
        'prompt_tokens': 500,
        'completion_tokens': 100,
        'cached_tokens': 200,
        'reasoning_tokens': 50,
      };

      final meta = ExecutionMetadata.fromJson(json);
      expect(meta.targetLocale, 'fi');
      expect(meta.matrixSamplingStrategy, 15);
      expect(meta.workflowVersion, 2);
      expect(meta.userId, 'usr_1');
      expect(meta.organizationId, 'org_1');
      expect(meta.dagCostUsd, 0.12);
      expect(meta.promptTokens, 500);
      expect(meta.completionTokens, 100);
      expect(meta.cachedTokens, 200);
      expect(meta.reasoningTokens, 50);
    });

    test('defaults are populated when optional fields are omitted', () {
      final json = {'target_locale': 'en'};
      final meta = ExecutionMetadata.fromJson(json);
      expect(meta.targetLocale, 'en');
      expect(meta.matrixSamplingStrategy, 10);
      expect(meta.workflowVersion, 1);
      expect(meta.profileId, isNull);
      expect(meta.userId, isNull);
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

  group('ExecutionRecord Freezed Parity & Fail-Fast', () {
    test('instantiates from valid json with required target_locale and metadata', () {
      final json = {
        'id': 'exe_1234567890abcdef',
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
        'status': 'PENDING',
        'strictness_level': 80,
        'metadata': {
          'target_locale': 'fi',
          'workflow_version': 1,
        },
      };

      final record = ExecutionRecord.fromJson(json);
      expect(record.id, 'exe_1234567890abcdef');
      expect(record.workflowId, 'wor_1234567890abcdef');
      expect(record.targetLocale, 'fi');
      expect(record.status, 'PENDING');
      expect(record.strictnessLevel, 80);
      expect(record.metadata?.targetLocale, 'fi');
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
  });
}
