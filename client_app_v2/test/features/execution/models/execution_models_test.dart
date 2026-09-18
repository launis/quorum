import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/features/execution/models/execution_summary_snapshot.dart';
import 'package:client_app/features/execution/models/frozen_context_snapshot.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
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
      expect(meta.providerOverride, isNull);
      expect(meta.modelRegistryId, isNull);
    });

    test(
      'instantiates from backend execution metadata containing provider_override and model_registry_id',
      () {
        final json = {
          'matrix_sampling_strategy': 1,
          'workflow_version': 1,
          'provider_override': 'vertex_ai',
          'model_registry_id': 'sys_b1c2d3e4f5a60718',
        };
        final meta = ExecutionMetadata.fromJson(json);
        expect(meta, isNotNull);
        expect(meta.providerOverride, LLMProvider.vertexAi);
        expect(meta.modelRegistryId, 'sys_b1c2d3e4f5a60718');
      },
    );

    test('supports ai_studio provider_override and null fields', () {
      final json = {
        'matrix_sampling_strategy': 1,
        'workflow_version': 1,
        'provider_override': 'ai_studio',
        'model_registry_id': 'sys_b1c2d3e4f5a60719',
      };
      final meta = ExecutionMetadata.fromJson(json);
      expect(meta.providerOverride, LLMProvider.aiStudio);
      expect(meta.modelRegistryId, 'sys_b1c2d3e4f5a60719');

      final nullJson = {
        'matrix_sampling_strategy': 1,
        'workflow_version': 1,
        'provider_override': null,
        'model_registry_id': null,
      };
      final nullMeta = ExecutionMetadata.fromJson(nullJson);
      expect(nullMeta.providerOverride, isNull);
      expect(nullMeta.modelRegistryId, isNull);
    });
  });

  group('ExecutionStep Freezed Parity', () {
    test('instantiates from valid json with model_strategy', () {
      final json = {
        'id': 'stp_1234567890abcdef',
        'label': 'Analysis Step',
        'status': 'passed',
        'model_strategy': 'fast',
        'physical_model': 'vertex_ai/gemini-2.5-flash',
        'progress': 75,
        'has_warning': false,
      };

      final step = ExecutionStep.fromJson(json);
      expect(step.id, 'stp_1234567890abcdef');
      expect(step.label, 'Analysis Step');
      expect(step.status, 'passed');
      expect(step.modelStrategy, 'fast');
      expect(step.physicalModel, 'vertex_ai/gemini-2.5-flash');
      expect(step.progress, 75);
      expect(step.hasWarning, isFalse);
    });

    test('instantiates with strongly typed scorecardAtoms', () {
      final json = {
        'id': 'stp_1',
        'label': 'Step 1',
        'status': 'passed',
        'scorecard_atoms': {
          'atom_1': {
            'atom_id': 'atm_1',
            'level': 5,
            'level_name': 'Level 5',
            'claim_label': 'Claim',
            'extracted_facts': <String, String?>{},
            'exact_quotes': <Map<String, dynamic>>[],
            'internal_logic_en': {
              'step_1_identify_premise': 'p',
              'step_2_scan_source': 's',
              'step_3_evaluate_anti_patterns': 'e',
              'step_4_final_conclusion': 'c',
            },
            'status': 'PASSED',
            'semantic_reasoning': 'Valid reason',
            'contextual_override': false,
            'chart_display_label': 'Label',
            'visual_intent': 'NEUTRAL',
          },
        },
      };

      final step = ExecutionStep.fromJson(json);
      expect(step.scorecardAtoms, isNotEmpty);
      expect(step.scorecardAtoms['atom_1']?.atomId, 'atm_1');
      expect(step.scorecardAtoms['atom_1']?.level, 5);
      expect(step.scorecardAtoms['atom_1']?.semanticReasoning, 'Valid reason');
    });

    test(
      'unrecognized key in scorecardAtoms throws CheckedFromJsonException',
      () {
        final json = {
          'id': 'stp_1',
          'label': 'Step 1',
          'status': 'passed',
          'scorecard_atoms': {
            'atom_1': {
              'atom_id': 'atm_1',
              'level': 5,
              'level_name': 'Level 5',
              'claim_label': 'Claim',
              'extracted_facts': <String, String?>{},
              'exact_quotes': <Map<String, dynamic>>[],
              'internal_logic_en': {
                'step_1_identify_premise': 'p',
                'step_2_scan_source': 's',
                'step_3_evaluate_anti_patterns': 'e',
                'step_4_final_conclusion': 'c',
              },
              'status': 'PASSED',
              'semantic_reasoning': 'Valid reason',
              'contextual_override': false,
              'chart_display_label': 'Label',
              'visual_intent': 'NEUTRAL',
              'unrecognized_rogue_key': 'invalid',
            },
          },
        };

        expect(
          () => ExecutionStep.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });

  group('WorkflowInputs Freezed Parity', () {
    test('instantiates from valid json with dynamic inputs', () {
      final json = {
        'organization_id': 'org_123',
        'user_id': 'usr_456',
        'simulation_mode': true,
        'language': 'fi',
        'dynamic_inputs': {'param_1': 42, 'text': 'Hello'},
      };

      final inputs = WorkflowInputs.fromJson(json);
      expect(inputs.organizationId, 'org_123');
      expect(inputs.userId, 'usr_456');
      expect(inputs.simulationMode, isTrue);
      expect(inputs.language, 'fi');
      expect(inputs.dynamicInputs, {'param_1': 42, 'text': 'Hello'});
    });

    test('defaults are populated when optional fields omitted', () {
      final inputs = WorkflowInputs.fromJson({});
      expect(inputs.organizationId, isNull);
      expect(inputs.userId, isNull);
      expect(inputs.simulationMode, isFalse);
      expect(inputs.language, 'en');
      expect(inputs.dynamicInputs, isEmpty);
    });

    test('unrecognized key throws CheckedFromJsonException', () {
      final json = {'unknown_field': 'invalid'};
      expect(
        () => WorkflowInputs.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('ExecutionSummarySnapshot Freezed Parity', () {
    test('instantiates from valid json and populates typed fields', () {
      final json = {
        'strictness_level': 70,
        'is_ensemble_run': true,
        'is_degraded': false,
        'system_concurrency_snapshot': {'LLM_MAX_CHUNK_SIZE': 5000},
      };

      final summary = ExecutionSummarySnapshot.fromJson(json);
      expect(summary.strictnessLevel, 70);
      expect(summary.isEnsembleRun, isTrue);
      expect(summary.isDegraded, isFalse);
      expect(summary.systemConcurrencySnapshot, {'LLM_MAX_CHUNK_SIZE': 5000});
    });

    test('defaults are populated when empty json provided', () {
      final summary = ExecutionSummarySnapshot.fromJson({});
      expect(summary.strictnessLevel, 100);
      expect(summary.isEnsembleRun, isFalse);
      expect(summary.isDegraded, isFalse);
      expect(summary.systemConcurrencySnapshot, isEmpty);
    });

    test('unrecognized key throws CheckedFromJsonException', () {
      final json = {'total_steps': 5};
      expect(
        () => ExecutionSummarySnapshot.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('FrozenContextSnapshot Freezed Parity', () {
    test('instantiates with version_id and backend snapshot fields', () {
      final json = {
        'version_id': 'v2.0.0',
        'workflow_id': 'wor_123',
        'compiled_prompts': {'p1': 'Prompt text'},
      };

      final snapshot = FrozenContextSnapshot.fromJson(json);
      expect(snapshot.versionId, 'v2.0.0');
      expect(snapshot.workflowId, 'wor_123');
      expect(snapshot.compiledPrompts, {'p1': 'Prompt text'});
    });

    test('defaults are populated when empty json provided', () {
      final snapshot = FrozenContextSnapshot.fromJson({});
      expect(snapshot.versionId, isNull);
      expect(snapshot.compiledPrompts, isEmpty);
      expect(snapshot.mcpToolAudit, isEmpty);
    });

    test('unrecognized key throws CheckedFromJsonException', () {
      final json = {'invalid_key': 'boom'};
      expect(
        () => FrozenContextSnapshot.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
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
      };

      final dto = ExecutionCreateRequestDto.fromJson(json);
      expect(dto.workflowId, 'wor_1234567890abcdef');
      expect(dto.targetLocale, 'fi');
      expect(dto.rawInputs['dynamic_inputs'], {'doc': 'test'});
      expect(dto.profileId, 'pro_1234567890abcdef');
    });

    test('throws when mandatory target_locale is missing', () {
      final json = {
        'workflow_id': 'wor_1234567890abcdef',
        'raw_inputs': {'input_1': 'val'},
      };

      expect(
        () => ExecutionCreateRequestDto.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    test('defaults raw_inputs when omitted from create request', () {
      final json = {
        'workflow_id': 'wor_1234567890abcdef',
        'target_locale': 'fi',
      };

      final dto = ExecutionCreateRequestDto.fromJson(json);
      expect(dto.rawInputs, isEmpty);
    });

    test(
      'unrecognized key in create request throws CheckedFromJsonException',
      () {
        final json = {
          'workflow_id': 'wor_1234567890abcdef',
          'target_locale': 'fi',
          'raw_inputs': {'input_1': 'val'},
          'unsupported_field': 'malicious_injection',
        };

        expect(
          () => ExecutionCreateRequestDto.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });

  group('ExecutionRecord Freezed Parity', () {
    test('instantiates from valid backend execution record json', () {
      final json = {
        'id': 'exe_1234567890abcdef',
        'workflow_id': 'wor_1234567890abcdef',
        'workflow_version': 2,
        'target_locale': 'fi',
        'active_profile_id': 'pro_1234567890abcdef',
        'output_profile_id': 'pro_1234567890abcdef',
        'status': 'passed',
        'raw_inputs': {
          'dynamic_inputs': {'input_1': 'Hello'},
        },
        'duration_ms': 4500,
        'cost_estimate': 0.12,
        'prompt_tokens': 500,
        'completion_tokens': 100,
        'cached_tokens': 200,
        'reasoning_tokens': 50,
        'dag_cost_usd': 0.12,
        'cumulative_synthesis_tokens': 1200,
        'cumulative_synthesis_cost': 0.012,
        'models_used': {'gemini-1.5-pro': 100},
        'metadata': {'workflow_version': 1},
        'error': null,
        'is_resumable': true,
        'frozen_context': {'version_id': 'v2.0.0'},
        'frozen_context_storage_path': 'gs://bucket/context.json',
        'context_variables': <String, dynamic>{'var1': 'val1'},
        'context_variables_storage_path': 'gs://bucket/vars.json',
        'execution_trace_storage_path': 'gs://bucket/trace.json',
        'pdf_report_path': '/reports/rep_1.pdf',
        'source_identity_manifest': <String, String>{'src_0': 'Doc A'},
        'steps': <Map<String, dynamic>>[],
        'step_states': <String, dynamic>{
          'stp_1': {'id': 'stp_1', 'label': 'Step 1', 'status': 'passed'},
        },
        'profile_syntheses': <String, dynamic>{},
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
      expect(record.modelsUsed, {'gemini-1.5-pro': 100});
      expect(record.progress, 100);
      expect(record.statusMessage, 'Completed');
      expect(record.organizationId, 'org_1');
      expect(record.createdBy, 'usr_1');
      expect(record.completedAt, '2026-08-30T12:05:00Z');
      expect(record.isResumable, true);
      expect(record.frozenContext?.versionId, 'v2.0.0');
      expect(record.stepStates?['stp_1']?.id, 'stp_1');
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

    test(
      'test_flutter_execution_record_deserializes_sse_payload_with_workflow_version_and_execution_summary',
      () {
        final json = <String, dynamic>{
          'id': 'exe_7fa9ecf00b604f1e840b0bd6a21ab6f9',
          'workflow_id': 'wor_1234567890abcdef',
          'workflow_version': 1,
          'target_locale': 'fi',
          'status': 'RUNNING',
          'output_profile_id': 'prof_default',
          'models_used': {'gemini-3.7-flash': 10711},
          'execution_summary': {
            'strictness_level': 70,
            'is_ensemble_run': true,
            'is_degraded': false,
            'system_concurrency_snapshot': {'LLM_MAX_CHUNK_SIZE': 5000},
          },
          'metadata': {'matrix_sampling_strategy': 2, 'workflow_version': 1},
        };

        expect(() => ExecutionRecord.fromJson(json), returnsNormally);
      },
    );
  });
}
