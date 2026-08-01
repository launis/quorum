import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ReportDataDto JSON Parsing', () {
    test('parses correctly with valid backend JSON', () {
      final json = {
        'execution_id': 'exec_123',
        'workflow_id': 'wf_abc',
        'profile_id': 'prof_123',
        'global_metrics': {
          'total_atoms': 10,
          'evaluated': 8,
          'short_circuited_na': 2,
          'duration_ms': 1500,
        },
        'inner_sdui_blocks': [
          {'block_type': 'markdown', 'text': 'Report Markdown'},
        ],

        'results': [
          {
            'tda_id': 'node_1',
            'status': 'PASSED',
            'extracted_data': {'value': 42.0, 'unit': 'kg'},
            'source_quote': 'It is 42 kg',
            'contextual_override': false,
            'evaluation_reasoning': 'Matches exactly',
            'depends_on_tda_ids': [],
            'short_circuit_reason_tda_ids': [],
          },
        ],
        'hydrated_references': {
          'node_1': {
            'sdui_component': 'extracted_value_card',
            'resolved_claim': 'The weight',
            'source_quote': 'It is 42 kg',
          },
        },
      };

      final dto = ReportDataDto.fromJson(json);

      expect(dto.executionId, 'exec_123');
      expect(dto.workflowId, 'wf_abc');
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
      'strips unrecognized SDUI keys from RenderedReportResponse payload',
      () {
        final Map<String, dynamic> json = {
          'execution_id': 'exec_123',
          'workflow_id': 'wf_abc',
          'profile_id': 'prof_123',
          'global_metrics': <String, dynamic>{
            'total_atoms': 10,
            'evaluated': 8,
            'short_circuited_na': 2,
            'duration_ms': 1500,
          },
          'inner_sdui_blocks': [
            {'block_type': 'markdown', 'text': 'Unrecognized test markdown'},
          ],
          'results': <dynamic>[],
          'hydrated_references': <String, dynamic>{},
          'scoring_strategy': 'WATERFALL', // SDUI Extra Key
          'user_name': 'tester', // SDUI Extra Key
          'unrecognized_rogue_key': 'should_be_stripped',
        };

        // Should throw due to strict parsing
        expect(
          () => ReportDataDto.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'throws CheckedFromJsonException if legacy layouts key is present',
      () {
        final Map<String, dynamic> json = {
          'execution_id': 'exec_123',
          'workflow_id': 'wf_abc',
          'inner_sdui_blocks': [],
          'results': [],
          'hydrated_references': {},
          'layouts': [
            // Legacy key
            {'preset_view': '1d_metrics', 'axes': []},
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
        final jsonString = '''
      {
        "execution_id": "exec_isolate",
        "workflow_id": "wf_isolate",
        "profile_id": "prof_123",
        "global_metrics": {
          "total_atoms": 5,
          "evaluated": 5,
          "short_circuited_na": 0,
          "duration_ms": 100
        },
        "inner_sdui_blocks": [
          {
            "block_type": "markdown",
            "text": "Parse background test markdown"
          }
        ],
        "results": [],
        "hydrated_references": {}
      }
      ''';

        final dto = await ReportDataDto.parseInBackground(jsonString);

        expect(dto.executionId, 'exec_isolate');
        expect(dto.workflowId, 'wf_isolate');
        expect(dto.globalMetrics?.totalAtoms, 5);
      },
    );
  });
}
