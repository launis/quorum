import 'dart:convert';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ReportDataDto Unit & ISTQB Boundary Tests', () {
    final validExecutionId = generateOpaqueUuid7('exe');
    final validWorkflowId = generateOpaqueUuid7('wf');
    final validProfileId = generateOpaqueUuid7('op');
    final validTdaId = generateOpaqueUuid7('tda');

    test(
      'Positive 1: deserializes full valid JSON payload, applies defaults on minimal payload, and roundtrips cleanly',
      () {
        final fullJson = <String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'scoring_strategy': 'WATERFALL',
          'user_name': 'Executive Coach',
          'scoring_engine_name': 'Quorum V2 Engine',
          'strictness_level': 85,
          'local_time_str': '2026-10-31 23:00',
          'custom_preface_md': '# Executive Summary',
          'profile_id': validProfileId,
          'profile_name': <String, Object?>{
            'translations': <String, Object?>{
              'en': 'Standard Profile',
              'fi': 'Oletusprofiili',
            },
          },
          'profile_description': <String, Object?>{
            'translations': <String, Object?>{
              'en': 'Profile description',
              'fi': 'Profiilin kuvaus',
            },
          },
          'available_profiles': <String, Object?>{
            validProfileId: <String, Object?>{
              'translations': <String, Object?>{
                'en': 'Standard Profile',
                'fi': 'Oletusprofiili',
              },
            },
          },
          'global_score': 88.5,
          'has_warning': true,
          'global_metrics': <String, Object?>{
            'total_atoms': 12,
            'evaluated': 10,
            'short_circuited_na': 2,
            'duration_ms': 450,
          },
          'inner_sdui_blocks': <Object?>[
            <String, Object?>{
              'block_type': 'paragraph',
              'text': 'Analytical synthesis paragraph.',
            },
          ],
          'results': <Object?>[
            <String, Object?>{'tda_id': validTdaId, 'status': 'PASSED'},
          ],
          'hydrated_references': <String, Object?>{
            validTdaId: <String, Object?>{
              'sdui_component': 'extracted_value_card',
              'resolved_claim': 'Verified strategic claim',
            },
          },
          'visible_metadata': <String>['user_name', 'global_score'],
          'created_at': '2026-10-31T21:00:00Z',
          'org_name': 'Quorum Org',
          'cost_estimate': 0.042,
          'total_tokens': 1500,
          'prompt_tokens': 1000,
          'completion_tokens': 300,
          'reasoning_tokens': 200,
          'mcp_tool_audit': <Object?>[
            <String, Object?>{
              'tool_id': 'search_docs',
              'step_name': 'Fact Verification',
              'query': 'annual report metrics',
            },
          ],
          'short_circuited_by_claims': <String>['Prerequisite claim A'],
          'falsified_warrant_claims': <String>['Falsified claim B'],
        };

        final dto = ReportDataDto.fromJson(fullJson);
        expect(dto.executionId, equals(validExecutionId));
        expect(dto.workflowId, equals(validWorkflowId));
        expect(dto.profileId, equals(validProfileId));
        expect(dto.scoringStrategy, equals('WATERFALL'));
        expect(dto.strictnessLevel, equals(85));
        expect(dto.globalScore, equals(88.5));
        expect(dto.hasWarning, isTrue);
        expect(dto.globalMetrics?.totalAtoms, equals(12));
        expect(dto.innerSduiBlocks.length, equals(1));
        expect(dto.results.single.tdaId, equals(validTdaId));
        expect(dto.results.single.status, equals(ExecutionStatus.passed));
        expect(
          dto.hydratedReferences[validTdaId]?.sduiComponent,
          equals(SDUIComponentType.extractedValueCard),
        );
        expect(dto.mcpToolAudit.single.toolId, equals('search_docs'));
        expect(
          dto.shortCircuitedByClaims,
          equals(<String>['Prerequisite claim A']),
        );
        expect(
          dto.falsifiedWarrantClaims,
          equals(<String>['Falsified claim B']),
        );

        final roundtripped = ReportDataDto.fromJson(
          jsonDecode(jsonEncode(dto.toJson())) as Map<String, Object?>,
        );
        expect(roundtripped.executionId, equals(validExecutionId));
        expect(roundtripped.workflowId, equals(validWorkflowId));
        expect(roundtripped.profileId, equals(validProfileId));
        expect(roundtripped.globalScore, equals(88.5));

        final minimalJson = <String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
        };
        final minimalDto = ReportDataDto.fromJson(minimalJson);
        expect(minimalDto.hasWarning, isFalse);
        expect(minimalDto.availableProfiles, isEmpty);
        expect(minimalDto.innerSduiBlocks, isEmpty);
        expect(minimalDto.results, isEmpty);
        expect(minimalDto.hydratedReferences, isEmpty);
        expect(minimalDto.visibleMetadata, isEmpty);
        expect(minimalDto.mcpToolAudit, isEmpty);
        expect(minimalDto.shortCircuitedByClaims, isEmpty);
        expect(minimalDto.falsifiedWarrantClaims, isEmpty);
      },
    );

    test(
      'Positive 2: parseInBackground decodes JSON string in background isolate cleanly',
      () async {
        final rawJson = jsonEncode(<String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
          'global_score': 92.0,
        });

        final dto = await ReportDataDto.parseInBackground(rawJson);
        expect(dto.executionId, equals(validExecutionId));
        expect(dto.workflowId, equals(validWorkflowId));
        expect(dto.profileId, equals(validProfileId));
        expect(dto.globalScore, equals(92.0));
      },
    );

    test(
      'Negative 1: rejects unrecognized keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
          'unrecognized_field': 'forbidden',
        };

        expect(
          () => ReportDataDto.fromJson(payloadWithExtraKey),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2 (BVA): throws CheckedFromJsonException when required keys are missing or field types are invalid',
      () {
        // Missing required execution_id
        expect(
          () => ReportDataDto.fromJson(<String, Object?>{
            'workflow_id': validWorkflowId,
            'profile_id': validProfileId,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Missing required workflow_id
        expect(
          () => ReportDataDto.fromJson(<String, Object?>{
            'execution_id': validExecutionId,
            'profile_id': validProfileId,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Missing required profile_id
        expect(
          () => ReportDataDto.fromJson(<String, Object?>{
            'execution_id': validExecutionId,
            'workflow_id': validWorkflowId,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        // Invalid type for strictness_level (String instead of int) and global_score (String instead of double)
        expect(
          () => ReportDataDto.fromJson(<String, Object?>{
            'execution_id': validExecutionId,
            'workflow_id': validWorkflowId,
            'profile_id': validProfileId,
            'strictness_level': 'invalid_int',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 3: parseInBackground throws AppException when JSON root is not an object map',
      () async {
        await expectLater(
          ReportDataDto.parseInBackground('["not", "a", "map"]'),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );
  });
}
