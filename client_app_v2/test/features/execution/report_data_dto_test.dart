import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('ReportDataDTO Parsing (Fail-Fast Verification)', () {
    test(
      'Throws ArgumentError when layouts is omitted entirely or invalid',
      () {
        final json = {
          "workflow_id": "wf_123",
          "synthesized_markdown": "Great job",
        };

        expect(() => ReportDataDTO.fromJson(json), throwsException);
      },
    );

    test('Parses successfully with valid data', () {
      final json = {
        "workflow_id": "wf_123",
        "profile_id": "prof_1",
        "profile_name": {
          "default_locale": "fi",
          "translations": {"fi": "Profiili"},
        },
        "available_profiles": {
          "prof_1": {
            "default_locale": "fi",
            "translations": {"fi": "Profiilit"},
          },
        },
        "layouts": [
          {
            "preset_view": "1d_metrics",
            "text_delivery_mode": "full",
            "axes": [
              {
                "name": "Loogisuus",
                "score": 88.0,
                "justification": "Analyysi perustelu...",
              },
            ],
          },
        ],
        "synthesized_markdown": "Kokonaisarvio...",
      };

      final dto = ReportDataDTO.fromJson(json);
      expect(dto.workflowId, 'wf_123');
      expect(dto.layouts.length, 1);
      expect(dto.layouts.first.presetView, PresetView.metrics1d);
      expect(dto.layouts.first.axes.length, 1);
      expect(dto.layouts.first.axes.first.score, 88.0);
    });
  });
}
