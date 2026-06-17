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
          "content_blocks": [
            {"block_type": "paragraph", "text": "Great job"},
          ],
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
                "block_id": "test_block",
                "label_i18n": {
                  "default_locale": "fi",
                  "translations": {"fi": "Loogisuus", "en": "Logicality"},
                },
                "name": "Loogisuus",
                "score": 88.0,
                "row_explanation": "Analyysi perustelu...",
              },
            ],
          },
        ],
        "content_blocks": [
          {"block_type": "paragraph", "text": "Kokonaisarvio..."},
        ],
      };

      final dto = ReportDataDTO.fromJson(json);
      expect(dto.workflowId, 'wf_123');
      expect(dto.layouts.length, 1);
      expect(dto.layouts.first.presetView, PresetView.metrics1d);
      expect(dto.layouts.first.axes.length, 1);
      expect(dto.layouts.first.axes.first.score, 88.0);
    });

    test('Parses SduiBulletListBlock Maps successfully (Tier 4 Repro)', () {
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
        "layouts": [],
        "content_blocks": [
          {
            "block_type": "bullet_list",
            "items": [
              {"text": "Sääntelypaine: CSRD", "citations": []},
              {
                "text": "Item 2",
                "citations": [1],
              },
            ],
          },
        ],
      };

      final dto = ReportDataDTO.fromJson(json);
      expect(dto.contentBlocks.length, 1);
      // Notice: Once the schema is fixed, this test will pass.
      // Right now it will FAIL (Red) because SduiBlockDTO still expects List<String>.
    });
    test('Parses SduiAlertBoxBlock Maps successfully (Tier 4 Repro)', () {
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
        "layouts": [],
        "content_blocks": [
          {
            "block_type": "alert_box",
            "text": "Tämä on backendin generoima teksti",
            "severity": "warning",
            "citations": [],
          },
        ],
      };

      final dto = ReportDataDTO.fromJson(json);
      expect(dto.contentBlocks.length, 1);
    });
  });
}
