import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('EmbeddedOutputProfile Fail-Fast Serialization', () {
    test(
      'Should parse V2 backend payload when include_diagnostic_scorecard is present',
      () {
        final jsonPayload = {
          "name": {
            "default_locale": "en",
            "translations": {"en": "Test Profile"},
          },
          "description": null,
          "visible_metadata": ["date", "organization"],
          "visible_block_extensions": [],
          "visible_workflow_extensions": [],
          "max_extension_items": 3,
          "display_scale": "original",
          "synthesis": null,
          "include_diagnostic_scorecard": true,
          "layouts": [],
        };

        // This should fail gracefully because include_diagnostic_scorecard is an
        // unrecognized key in the Freezed model, resulting in CheckedFromJsonException.
        final result = EmbeddedOutputProfile.fromJson(jsonPayload);

        expect(result.name.translations['en'], 'Test Profile');
      },
    );

    test(
      'Should successfully parse new Epic 57 visible_extensions (variance_validation, contextual_override)',
      () {
        final jsonPayload = {
          "name": {
            "default_locale": "en",
            "translations": {"en": "Test Profile"},
          },
          "description": null,
          "visible_metadata": ["date", "organization"],
          "visible_block_extensions": [
            "variance_validation",
            "contextual_override",
          ],
          "visible_workflow_extensions": [],
          "max_extension_items": 3,
          "display_scale": "original",
          "synthesis": null,
          "include_diagnostic_scorecard": true,
          "layouts": [],
        };

        final result = EmbeddedOutputProfile.fromJson(jsonPayload);

        expect(
          result.visibleBlockExtensions.contains(
            XaiExtensionType.varianceValidation,
          ),
          isTrue,
        );
        expect(
          result.visibleBlockExtensions.contains(
            XaiExtensionType.contextualOverride,
          ),
          isTrue,
        );
      },
    );

    test(
      'TDD REPRO: SynthesisConfigDTO should parse model_strategy without crashing',
      () {
        final jsonPayload = {
          "system_prompt": null,
          "length_constraint": null,
          "preamble_text": null,
          "historical_context_mode": "DISABLED",
          "enable_pii_masking": false,
          "allowed_exports": ["pdf", "raw_json"],
          "omit_empty_sections": true,
          "allowed_mcp_tools": [],
          "matrix_visible_columns": [
            "label",
            "score",
            "distribution",
            "row_explanation",
          ],
          "model_strategy": "fast",
        };

        // This will currently crash with CheckedFromJsonException
        final result = SynthesisConfigDTO.fromJson(jsonPayload);

        expect(result, isNotNull);
      },
    );
  });
}
