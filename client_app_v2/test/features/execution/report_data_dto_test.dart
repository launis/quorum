import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';

void main() {
  group('ReportDataDTO Parsing (Fail-Fast Verification)', () {
    test(
      'Throws ArgumentError when layouts is omitted entirely or invalid',
      () {
        final json = {"workflow_id": "wf_123", "synthesis": "Great job"};

        expect(
          () => ReportDataDTO.fromJson(json),
          throwsA(isA<ArgumentError>()),
        );
      },
    );

    test('Parses successfully with valid data', () {
      final json = {
        "workflow_id": "wf_123",
        "profile_id": "prof_1",
        "profile_name": {"fi": "Profiili"},
        "available_profiles": {"prof_1": "Profiilit"},
        "layouts": [
          {
            "preset_view": "1d_metrics",
            "show_text": true,
            "axes": [
              {
                "name": "Loogisuus",
                "score": 88.0,
                "justification": "Analyysi perustelu...",
              },
            ],
          },
        ],
        "synthesis": "Kokonaisarvio...",
      };

      final dto = ReportDataDTO.fromJson(json);
      expect(dto.workflowId, 'wf_123');
      expect(dto.layouts.length, 1);
      expect(dto.layouts.first.presetView, '1d_metrics');
      expect(dto.layouts.first.axes.length, 1);
      expect(dto.layouts.first.axes.first.score, 88.0);
    });
  });
}
