import 'dart:convert';

import 'package:client_app/features/execution/models/distilled_evaluation.dart';
import 'package:client_app/features/execution/models/execution_create_request_dto.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/execution_summary_snapshot.dart';
import 'package:client_app/features/execution/models/frozen_context_snapshot.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionRecord & Group 2 Execution DTO Unit & ISTQB Boundary Tests', () {
    // test_execution_record_and_report_dto_deserialize_typed_models
    test(
      'test_execution_record_and_report_dto_deserialize_typed_models (Positive 1)',
      () async {
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
            'dynamic_inputs': <String, Object?>{
              'deliverable': 'Test text',
              'pdf_doc': <String, Object?>{
                'filename': 'report.pdf',
                'content_base64': 'YWJj',
              },
              'survey': <String, Object?>{'q1': 'Yes'},
            },
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
            'global_context_vars': <String, Object?>{
              'language': 'fi',
              'target_locale': 'fi',
              'organization_id': 'org_1',
              'passivity_detected': false,
            },
          },
          'error': null,
          'is_resumable': false,
          'frozen_context': <String, Object?>{
            'workflow_id': wfId,
            'compiled_prompts': <String, String>{'step_1': 'System prompt'},
            'injected_theory': <String, Object?>{
              'theories': <String, String>{'step_1': 'CDM Framework'},
            },
            'generated_schemas': <String, Object?>{
              'schemas': <String, Object?>{
                'step_1': <String, Object?>{
                  'type': 'object',
                  'title': 'Step1Schema',
                },
              },
            },
            'ui_hints_snapshot': <String, Object?>{
              'strictness': <String, Object?>{
                'field_id': 'strictness',
                'component_type': 'slider',
                'validation_rules': <String, Object?>{
                  'min': 0.0,
                  'max': 100.0,
                  'required': true,
                },
              },
            },
            'mcp_tool_audit': <Map<String, Object?>>[
              <String, Object?>{
                'tool_id': 'web_search',
                'gateway_id': 'sys_0195f3a0000070008000000000000001',
                'step_name': stepId,
                'query': 'Test query',
                'response_summary': 'Found 1 result.',
                'source_urls': <String>['https://example.com'],
                'duration_ms': 120,
                'timestamp': '2026-10-31T20:00:00Z',
              },
            ],
          },
          'frozen_context_storage_path': 'traces/frozen.json',
          'context_variables': <String, Object?>{
            'report_context': 'Summary context',
            'variables': <String, String>{'score': '4.5'},
          },
          'context_variables_storage_path': 'traces/vars.json',
          'execution_trace': <Map<String, Object?>>[
            <String, Object?>{
              'step_name': stepId,
              'event_type': 'STATE_UPDATE',
              'content': <String, Object?>{'status': 'RUNNING'},
            },
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
            profileId: <String, Object?>{
              'variance_explanation': 'Consistent across runs.',
              'cited_sources': <String>['src_1'],
            },
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
        expect(record.rawInputs, isA<WorkflowInputs>());
        expect(
          record.rawInputs?.dynamicInputs['deliverable']?.textValue,
          equals('Test text'),
        );
        expect(
          record.rawInputs?.dynamicInputs['pdf_doc']?.fileValue?.filename,
          equals('report.pdf'),
        );
        expect(
          record.rawInputs?.dynamicInputs['survey']?.questionnaireValue?['q1'],
          equals('Yes'),
        );
        expect(record.executionSummary, isA<ExecutionSummarySnapshot>());
        expect(record.metadata, isA<ExecutionMetadata>());
        expect(
          record.metadata?.globalContextVars?.organizationId,
          equals('org_1'),
        );
        expect(record.frozenContext, isA<FrozenContextSnapshot>());
        expect(
          record.frozenContext?.injectedTheory.theories['step_1'],
          equals('CDM Framework'),
        );
        expect(
          record.frozenContext?.generatedSchemas.schemas['step_1']?.title,
          equals('Step1Schema'),
        );
        expect(
          record
              .frozenContext
              ?.uiHintsSnapshot['strictness']
              ?.validationRules
              ?.max,
          equals(100.0),
        );
        expect(record.frozenContext?.mcpToolAudit, hasLength(1));
        expect(
          record.contextVariables?.reportContext,
          equals('Summary context'),
        );
        expect(record.contextVariables?.variables['score'], equals('4.5'));
        expect(record.executionTrace?.first.eventType, equals('STATE_UPDATE'));
        expect(
          record.profileSyntheses?[profileId]?.varianceExplanation,
          equals('Consistent across runs.'),
        );

        // Verify DistilledEvaluation and ExecutionCreateRequestDto typed models
        final distilled = DistilledEvaluation.fromJson(<String, Object?>{
          'atom_id': 'a0',
          'exact_quotes': <String>['Quote 1'],
          'status': 'PASSED',
          'extensions': <String, Object?>{
            'confidence': 0.95,
            'tags': <String>['verified'],
          },
        });
        expect(distilled.extensions?['confidence']?.numberValue, equals(0.95));
        expect(
          distilled.extensions?['tags']?.stringListValue,
          equals(<String>['verified']),
        );

        final createReq = ExecutionCreateRequestDto(
          workflowId: wfId,
          rawInputs: record.rawInputs!,
          targetLocale: 'fi',
        );
        expect(
          ExecutionCreateRequestDto.fromJson(
            jsonDecode(jsonEncode(createReq.toJson())) as Map<String, Object?>,
          ).workflowId,
          equals(wfId),
        );

        // Verify ReportDataDto parseInBackground deserializes typed models
        final reportJson = jsonEncode(<String, Object?>{
          'execution_id': execId,
          'workflow_id': wfId,
          'profile_id': profileId,
          'global_score': 88.5,
        });
        final reportDto = await ReportDataDto.parseInBackground(reportJson);
        expect(reportDto.executionId, equals(execId));
        expect(reportDto.workflowId, equals(wfId));
        expect(reportDto.globalScore, equals(88.5));

        final serialized =
            jsonDecode(jsonEncode(record.toJson())) as Map<String, Object?>;
        final roundtripped = ExecutionRecord.fromJson(serialized);
        expect(roundtripped.id, equals(execId));
        expect(roundtripped.workflowId, equals(wfId));
        expect(roundtripped.status, equals('PASSED'));
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
        expect(record.steps, isEmpty);
        expect(record.rawInputs, isNull);
        expect(record.metadata, isNull);
        expect(record.executionSummary, isNull);
      },
    );

    // test_freezed_models_reject_unrecognized_json_keys
    test('test_freezed_models_reject_unrecognized_json_keys (Negative 1)', () {
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

      expect(
        () => FrozenContextSnapshot.fromJson(<String, Object?>{
          'workflow_id': wfId,
          'unrecognized_snapshot_key': 'forbidden',
        }),
        throwsA(
          anyOf(
            isA<UnrecognizedKeysException>(),
            isA<CheckedFromJsonException>(),
          ),
        ),
      );
    });

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

    test(
      'Positive 3 (Backend Wire Parity): deserializes ExecutionRecord with backend TraceEvent, RenderedSynthesisCache, GlobalContextVarsDTO, and ContextVariablesDTO wire payloads',
      () {
        final execId = generateOpaqueUuid7('exe');
        final wfId = generateOpaqueUuid7('wf');
        final profileId = generateOpaqueUuid7('op');
        final stepId = generateOpaqueUuid7('stp');
        final blockId = generateOpaqueUuid7('blk');
        final eventId = generateOpaqueUuid7('evt');

        final backendWirePayload = <String, Object?>{
          'id': execId,
          'workflow_id': wfId,
          'target_locale': 'fi',
          'status': 'completed',
          'workflow_version': 1,
          'state_version': 4,
          'active_profile_id': profileId,
          'output_profile_id': profileId,
          'metadata': <String, Object?>{
            'matrix_sampling_strategy': 0,
            'workflow_version': 1,
            'global_context_vars': <String, Object?>{
              'language': 'fi',
              'target_locale': 'fi',
              'organization_id': 'org_0195f3a0000070008000000000000001',
              'initiator_id': 'usr_0195f3a0000070008000000000000001',
              'shuffled_atoms': <Map<String, Object?>>[
                <String, Object?>{
                  'id': 'sr_0195f3a0000070008000000000000001',
                  'category': 'Discovery',
                  'label': <String, Object?>{
                    'translations': <String, String>{'fi': 'Kysymykset'},
                  },
                },
              ],
              'hydration_results': <String, Object?>{
                blockId: <Map<String, Object?>>[
                  <String, Object?>{
                    'id': 'sr_0195f3a0000070008000000000000001',
                    'score': 4,
                  },
                ],
              },
              'step_linguistics': <String, Object?>{
                'entries': <String, Object?>{
                  'deliverable': <String, Object?>{'passive_ratio': 0.12},
                },
              },
              'profiler_metrics': <String, Object?>{
                'metrics': <String, Object?>{'word_count': 420},
              },
              'distillation': <String, Object?>{
                'matrices': <String, Object?>{},
              },
              'scoring': <String, Object?>{
                'global_score': 82.5,
                'penalties_applied': <Map<String, Object?>>[],
              },
              'interaction_analysis': <String, Object?>{
                'total_turns': 12,
                'speaker_turn_counts': <String, int>{'Coach': 6, 'Client': 6},
              },
              'bibliography': <String, Object?>{
                'entries': <Map<String, Object?>>[],
                'citation_map': <String, String>{'doc0': 'Transcript.pdf'},
              },
              'integrity_verified_output': <String, Object?>{
                'verified_quotes': 5,
                'rejected_quotes': 0,
              },
              'step_metadata': <String, Object?>{
                stepId: <String, Object?>{'attempt': 1},
              },
              'step_coach': <String, Object?>{
                'summary': 'Strong coaching presence.',
                'highlights': <String>['Active listening'],
              },
            },
          },
          'context_variables': <String, Object?>{
            'global_atom_blackboard': <String, Object?>{
              'entries': <String, Object?>{},
            },
            'matrix_reducer_output': <String, Object?>{
              'matrices': <String, Object?>{},
            },
            'report_context': <String, Object?>{
              'summary': 'Structured report context',
            },
            'evaluated_matrices': <String, Object?>{
              blockId: <String, Object?>{'average_score': 82.5},
            },
            'variables': <String, Object?>{
              'deliverable': 'Raw text',
              'pdf_doc': <String, Object?>{
                'filename': 'doc.pdf',
                'content_base64': 'YWJj',
              },
            },
          },
          'execution_trace': <Map<String, Object?>>[
            <String, Object?>{
              'event_id': eventId,
              'v': 1,
              'timestamp': '2026-10-31T20:00:00Z',
              'step_name': stepId,
              'event_type': 'STATE_UPDATE',
              'content': <String, Object?>{'score': 82.5},
              'reasoning': 'Evaluated atom criteria.',
              'metadata': <String, Object?>{
                'model': 'gemini-2.5-flash',
                'duration_ms': 450,
              },
              'mcp_audit_traces': <Map<String, Object?>>[],
            },
          ],
          'profile_syntheses': <String, Object?>{
            profileId: <String, Object?>{
              'section_syntheses': <String, String>{
                blockId: 'Executive synthesis paragraph.',
              },
              'row_explanations': <String, String>{
                'sr_0195f3a0000070008000000000000001': 'Row rationale.',
              },
              'row_curated_quotes': <String, List<String>>{
                'sr_0195f3a0000070008000000000000001': <String>['Exact quote.'],
              },
              'variance_explanation': 'Low variance across ensemble runs.',
              'authenticity_explanation': 'Organic dialogue flow.',
              'cited_sources': <String>['Transcript.pdf'],
              'xai_highlights': <Map<String, Object?>>[],
              'user_role': 'Executive Coach',
              'user_role_justification': 'Led reflective questioning.',
              'extension_metrics': <String, Object?>{
                'sr_0195f3a0000070008000000000000001': <String, Object?>{
                  'confidence': 0.92,
                },
              },
              'data_starvation': false,
              'created_at': '2026-10-31T20:01:00Z',
            },
          },
        };

        final record = ExecutionRecord.fromJson(backendWirePayload);
        expect(record.id, equals(execId));
        expect(record.status, equals('COMPLETED'));
        expect(record.executionTrace, hasLength(1));
        expect(record.executionTrace!.first.stepName, equals(stepId));
        expect(record.executionTrace!.first.eventType, equals('STATE_UPDATE'));
        expect(
          record.profileSyntheses?[profileId]?.varianceExplanation,
          equals('Low variance across ensemble runs.'),
        );
        expect(
          record.profileSyntheses?[profileId]?.userRole,
          equals('Executive Coach'),
        );
      },
    );
  });
}
