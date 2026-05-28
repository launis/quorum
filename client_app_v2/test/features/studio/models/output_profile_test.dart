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
          "visible_extensions": [],
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
          "visible_extensions": ["variance_validation", "contextual_override"],
          "max_extension_items": 3,
          "display_scale": "original",
          "synthesis": null,
          "include_diagnostic_scorecard": true,
          "layouts": [],
        };

        final result = EmbeddedOutputProfile.fromJson(jsonPayload);

        expect(result.visibleExtensions.contains(XaiExtensionType.varianceValidation), isTrue);
        expect(result.visibleExtensions.contains(XaiExtensionType.contextualOverride), isTrue);
      },
    );
  });
}
