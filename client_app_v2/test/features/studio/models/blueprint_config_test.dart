import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/features/studio/models/blueprint_config.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('BlueprintConfig JSON Parsing', () {
    // Contract: test_blueprint_config_valid_preset_view
    test('test_blueprint_config_valid_preset_view', () {
      final jsonPayload = {'preset_view': '1d_metrics'};

      final config = BlueprintConfig.fromJson(jsonPayload);
      expect(config, isNotNull);
      expect(config.presetView, PresetView.metrics1d);
    });

    test('Should parse default preset_view when empty JSON provided', () {
      final jsonPayload = <String, dynamic>{};

      final config = BlueprintConfig.fromJson(jsonPayload);
      expect(config, isNotNull);
      expect(config.presetView, PresetView.metrics1d);
    });

    // Contract: test_blueprint_config_unknown_preset_view_throws
    test('test_blueprint_config_unknown_preset_view_throws', () {
      final jsonPayload = {'preset_view': 'invalid_preset'};

      expect(
        () => BlueprintConfig.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });

    // Contract: test_blueprint_config_extra_key_throws
    test('test_blueprint_config_extra_key_throws', () {
      final jsonPayload = {'preset_view': '1d_metrics', 'extra_field': true};

      expect(
        () => BlueprintConfig.fromJson(jsonPayload),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });
}
