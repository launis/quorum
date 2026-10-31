import 'dart:convert';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ReportDataDto JSON Parsing', () {
    final validExecutionId = generateOpaqueUuid7('exe');
    final validWorkflowId = generateOpaqueUuid7('wf');
    final validProfileId = generateOpaqueUuid7('op');

    test('parses correctly with valid backend JSON', () {
      final json = <String, Object?>{
        'execution_id': validExecutionId,
        'workflow_id': validWorkflowId,
        'profile_id': validProfileId,
        'global_metrics': <String, Object?>{
          'total_atoms': 10,
          'evaluated': 8,
          'short_circuited_na': 2,
          'duration_ms': 1500,
        },
        'inner_sdui_blocks': <Object?>[
          <String, Object?>{
            'block_type': 'markdown',
            'text': 'Report Markdown',
          },
        ],
        'results': <Object?>[
          <String, Object?>{
            'tda_id': 'node_1',
            'status': 'PASSED',
            'extracted_data': <String, Object?>{'value': 42.0, 'unit': 'kg'},
            'source_quotes': <String>['It is 42 kg'],
            'contextual_override': false,
            'evaluation_reasoning': 'Matches exactly',
            'depends_on_tda_ids': <String>[],
            'short_circuit_reason_tda_ids': <String>[],
          },
        ],
        'hydrated_references': <String, Object?>{
          'node_1': <String, Object?>{
            'sdui_component': 'extracted_value_card',
            'resolved_claim': 'The weight',
            'source_quotes': <String>['It is 42 kg'],
          },
        },
      };

      final dto = ReportDataDto.fromJson(json);

      expect(dto.executionId, validExecutionId);
      expect(dto.workflowId, validWorkflowId);
      expect(dto.globalMetrics?.totalAtoms, 10);

      expect(dto.results.length, 1);
      expect(dto.results.first.status, ExecutionStatus.passed);
      expect(dto.results.first.extractedData?.value, 42.0);
      expect(dto.hydratedReferences.length, 1);
      expect(
        dto.hydratedReferences['node_1']?.sduiComponent,
        SDUIComponentType.extractedValueCard,
      );
    });

    test(
      'rejects unrecognized SDUI keys from RenderedReportResponse payload',
      () {
        final json = <String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
          'global_metrics': <String, Object?>{
            'total_atoms': 10,
            'evaluated': 8,
            'short_circuited_na': 2,
            'duration_ms': 1500,
          },
          'inner_sdui_blocks': <Object?>[
            <String, Object?>{
              'block_type': 'markdown',
              'text': 'Unrecognized test markdown',
            },
          ],
          'results': <Object?>[],
          'hydrated_references': <String, Object?>{},
          'scoring_strategy': 'WATERFALL',
          'user_name': 'tester',
          'unrecognized_rogue_key': 'should_be_rejected',
        };

        expect(
          () => ReportDataDto.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'throws CheckedFromJsonException if legacy layouts key is present',
      () {
        final json = <String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
          'inner_sdui_blocks': <Object?>[],
          'results': <Object?>[],
          'hydrated_references': <String, Object?>{},
          'layouts': <Object?>[
            <String, Object?>{'preset_view': '1d_metrics', 'axes': <Object?>[]},
          ],
        };

        expect(
          () => ReportDataDto.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'parseInBackground correctly parses JSON in a separate isolate',
      () async {
        final jsonString = jsonEncode(<String, Object?>{
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
          'global_metrics': <String, Object?>{
            'total_atoms': 5,
            'evaluated': 5,
            'short_circuited_na': 0,
            'duration_ms': 100,
          },
          'inner_sdui_blocks': <Object?>[
            <String, Object?>{
              'block_type': 'markdown',
              'text': 'Parse background test markdown',
            },
          ],
          'results': <Object?>[],
          'hydrated_references': <String, Object?>{},
        });

        final dto = await ReportDataDto.parseInBackground(jsonString);

        expect(dto.executionId, validExecutionId);
        expect(dto.workflowId, validWorkflowId);
        expect(dto.globalMetrics?.totalAtoms, 5);
      },
    );
  });
}
