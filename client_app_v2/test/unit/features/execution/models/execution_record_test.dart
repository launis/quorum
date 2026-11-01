import 'dart:convert';

import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/execution_step.dart';
import 'package:client_app/features/execution/models/execution_summary_snapshot.dart';
import 'package:client_app/features/execution/models/frozen_context_snapshot.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionRecord Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: ExecutionRecord roundtrips full JSON payload and normalizes status to uppercase',
      () {
        final execId = generateOpaqueUuid7('exe');
        final wfId = generateOpaqueUuid7('wf');
        final profileId = generateOpaqueUuid7('op');
        final stepId = generateOpaqueUuid7('stp');

        final rawPayload = <String, Object?>{
          'id': execId,
          'workflow_id': wfId,
          'target_locale': 'fi',
          'status': 'passed',
          'workflow_version': 2,
          'state_version': 3,
          'active_profile_id': profileId,
          'output_profile_id': profileId,
          'raw_inputs': <String, Object?>{
            'organization_id': 'org_1',
            'user_id': 'usr_1',
            'simulation_mode': true,
            'language': 'fi',
            'dynamic_inputs': <String, Object?>{'deliverable': 'Test text'},
          },
          'duration_ms': 1540,
          'cost_estimate': 0.045,
          'prompt_tokens': 1200,
          'completion_tokens': 350,
          'cached_tokens': 400,
          'reasoning_tokens': 150,
          'dag_cost_usd': 0.032,
          'cumulative_synthesis_tokens': 500,
          'cumulative_synthesis_cost': 0.013,
          'models_used': <String, int>{'gemini-2.5-flash': 2},
          'execution_summary': <String, Object?>{
            'strictness_level': 80,
            'is_ensemble_run': true,
            'is_degraded': false,
            'system_concurrency_snapshot': <String, int>{'max_llm': 2},
          },
          'metadata': <String, Object?>{
            'matrix_sampling_strategy': 0,
            'workflow_version': 2,
            'provider_override': 'vertex_ai',
          },
          'error': null,
          'is_resumable': false,
          'frozen_context': <String, Object?>{
            'workflow_id': wfId,
            'compiled_prompts': <String, String>{'step_1': 'System prompt'},
          },
          'frozen_context_storage_path': 'traces/frozen.json',
          'context_variables': <String, Object?>{'score': 4.5},
          'context_variables_storage_path': 'traces/vars.json',
          'execution_trace': <Map<String, Object?>>[
            <String, Object?>{'event': 'STEP_START'},
          ],
          'execution_trace_storage_path': 'traces/trace.json',
          'pdf_report_path': 'reports/out.pdf',
          'source_identity_manifest': <String, String>{'src_1': 'Report.pdf'},
          'steps': <Map<String, Object?>>[
            <String, Object?>{
              'id': stepId,
              'label': 'Analysis Step',
              'status': 'PASSED',
              'prompt_tokens': 600,
            },
          ],
          'step_states': <String, Object?>{
            stepId: <String, Object?>{
              'id': stepId,
              'label': 'Analysis Step',
              'status': 'PASSED',
              'prompt_tokens': 600,
            },
          },
          'profile_syntheses': <String, Object?>{
            profileId: <String, Object?>{'cached': true},
          },
          'progress': 100,
          'status_message': 'Completed',
          'created_at': '2026-10-31T20:00:00Z',
          'updated_at': '2026-10-31T20:01:00Z',
          'completed_at': '2026-10-31T20:01:00Z',
          'created_by': 'usr_1',
          'organization_id': 'org_1',
        };

        final record = ExecutionRecord.fromJson(rawPayload);

        expect(record.id, equals(execId));
        expect(record.workflowId, equals(wfId));
        expect(record.targetLocale, equals('fi'));
        expect(record.status, equals('PASSED'));
        expect(record.workflowVersion, equals(2));
        expect(record.stateVersion, equals(3));
        expect(record.activeProfileId, equals(profileId));
        expect(record.outputProfileId, equals(profileId));
        expect(record.rawInputs, isA<WorkflowInputs>());
        expect(record.rawInputs?.simulationMode, isTrue);
        expect(record.durationMs, equals(1540));
        expect(record.costEstimate, equals(0.045));
        expect(record.promptTokens, equals(1200));
        expect(record.completionTokens, equals(350));
        expect(record.cachedTokens, equals(400));
        expect(record.reasoningTokens, equals(150));
        expect(record.dagCostUsd, equals(0.032));
        expect(record.cumulativeSynthesisTokens, equals(500));
        expect(record.cumulativeSynthesisCost, equals(0.013));
        expect(record.modelsUsed?['gemini-2.5-flash'], equals(2));
        expect(record.executionSummary, isA<ExecutionSummarySnapshot>());
        expect(record.executionSummary?.strictnessLevel, equals(80));
        expect(record.metadata, isA<ExecutionMetadata>());
        expect(record.metadata?.providerOverride, equals(LLMProvider.vertexAi));
        expect(record.frozenContext, isA<FrozenContextSnapshot>());
        expect(record.steps, hasLength(1));
        expect(record.steps.first, isA<ExecutionStep>());
        expect(record.stepStates?[stepId]?.label, equals('Analysis Step'));
        expect(record.progress, equals(100));

        final serialized =
            jsonDecode(jsonEncode(record.toJson())) as Map<String, Object?>;
        final roundtripped = ExecutionRecord.fromJson(serialized);
        expect(roundtripped.id, equals(execId));
        expect(roundtripped.workflowId, equals(wfId));
        expect(roundtripped.status, equals('PASSED'));
        expect(roundtripped.stateVersion, equals(3));
        expect(roundtripped.promptTokens, equals(1200));
        expect(roundtripped.steps.first.id, equals(stepId));
      },
    );

    test(
      'Positive 2 (Boundary & Isolate): applies default values on minimal payload and parses in background isolate',
      () async {
        final execId = generateOpaqueUuid7('exe');
        final wfId = generateOpaqueUuid7('wf');
        final minimalJsonMap = <String, Object?>{
          'id': execId,
          'workflow_id': wfId,
          'target_locale': 'en',
          'status': 'running',
        };

        final record = await ExecutionRecord.parseInBackground(
          jsonEncode(minimalJsonMap),
        );

        expect(record.id, equals(execId));
        expect(record.workflowId, equals(wfId));
        expect(record.targetLocale, equals('en'));
        expect(record.status, equals('RUNNING'));
        expect(record.workflowVersion, equals(1));
        expect(record.promptTokens, equals(0));
        expect(record.completionTokens, equals(0));
        expect(record.cachedTokens, equals(0));
        expect(record.reasoningTokens, equals(0));
        expect(record.dagCostUsd, equals(0.0));
        expect(record.steps, isEmpty);
        expect(record.rawInputs, isNull);
        expect(record.metadata, isNull);
        expect(record.executionSummary, isNull);
      },
    );

    test(
      'Negative 1: rejects unrecognized JSON keys via disallowUnrecognizedKeys',
      () {
        final execId = generateOpaqueUuid7('exe');
        final wfId = generateOpaqueUuid7('wf');

        expect(
          () => ExecutionRecord.fromJson(<String, Object?>{
            'id': execId,
            'workflow_id': wfId,
            'target_locale': 'fi',
            'status': 'PENDING',
            'unknown_legacy_field': 'forbidden',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'Negative 2 (BVA & Type Safety): rejects missing required fields, wrong field types, and non-object isolate JSON',
      () async {
        final execId = generateOpaqueUuid7('exe');
        final wfId = generateOpaqueUuid7('wf');

        // Missing required 'status'
        expect(
          () => ExecutionRecord.fromJson(<String, Object?>{
            'id': execId,
            'workflow_id': wfId,
            'target_locale': 'fi',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Wrong type for 'prompt_tokens' (String instead of num)
        expect(
          () => ExecutionRecord.fromJson(<String, Object?>{
            'id': execId,
            'workflow_id': wfId,
            'target_locale': 'fi',
            'status': 'PENDING',
            'prompt_tokens': 'invalid_int',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // Malformed JSON array instead of object in parseInBackground
        await expectLater(
          ExecutionRecord.parseInBackground('["not", "a", "map"]'),
          throwsA(isA<TypeError>()),
        );
      },
    );
  });
}
