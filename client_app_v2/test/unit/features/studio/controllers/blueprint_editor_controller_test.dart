import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/blueprint_editor_controller.dart';
import 'package:client_app/features/studio/models/blueprint_config.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:mocktail/mocktail.dart';

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockLoggerService mockLogger;
  late ProviderContainer container;

  setUp(() {
    mockLogger = MockLoggerService();
    container = ProviderContainer(
      retry: (retryCount, error) => null,
      overrides: [loggerServiceProvider.overrideWithValue(mockLogger)],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('BlueprintEditorController Unit Tests', () {
    test(
      'Positive: initializes with default PresetView.metrics1d, hydrates valid BlueprintConfig instances, and mutates presetView across all PresetView variants',
      () {
        final BlueprintConfig initialConfig = container.read(
          blueprintEditorControllerProvider,
        );
        expect(initialConfig.presetView, equals(PresetView.metrics1d));
        expect(
          initialConfig.toJson(),
          equals(<String, Object?>{'preset_view': '1d_metrics'}),
        );

        final notifier = container.read(
          blueprintEditorControllerProvider.notifier,
        );

        notifier.initialize(
          const BlueprintConfig(presetView: PresetView.compare2d),
        );
        expect(
          container.read(blueprintEditorControllerProvider).presetView,
          equals(PresetView.compare2d),
        );

        notifier.setPresetView(PresetView.matrix3d);
        final updatedConfig = container.read(blueprintEditorControllerProvider);
        expect(updatedConfig.presetView, equals(PresetView.matrix3d));
        expect(
          updatedConfig.toJson(),
          equals(<String, Object?>{'preset_view': '3d_matrix'}),
        );

        notifier.setPresetView(PresetView.textOnly);
        expect(
          container.read(blueprintEditorControllerProvider).presetView,
          equals(PresetView.textOnly),
        );

        notifier.initialize(null);
        expect(
          container.read(blueprintEditorControllerProvider).presetView,
          equals(PresetView.metrics1d),
        );
      },
    );

    test(
      'Negative 1 (ISTQB BVA / Strict Schema): BlueprintConfig.fromJson fails fast with CheckedFromJsonException on unrecognized JSON keys and preserves prior controller state',
      () {
        final notifier = container.read(
          blueprintEditorControllerProvider.notifier,
        );
        notifier.setPresetView(PresetView.compare2d);

        expect(
          () => BlueprintConfig.fromJson(<String, Object?>{
            'preset_view': '3d_matrix',
            'unrecognized_extra_key': 'forbidden',
          }),
          throwsA(
            isA<CheckedFromJsonException>().having(
              (e) => e.toString(),
              'toString()',
              contains('unrecognized_extra_key'),
            ),
          ),
        );

        expect(
          container.read(blueprintEditorControllerProvider).presetView,
          equals(PresetView.compare2d),
        );
      },
    );

    test(
      'Negative 2 (ISTQB BVA / Type & Enum Boundaries): BlueprintConfig.fromJson fails fast on invalid preset_view enum values or wrong value types',
      () {
        final notifier = container.read(
          blueprintEditorControllerProvider.notifier,
        );
        notifier.setPresetView(PresetView.matrixSummary);

        final invalidPayloads = <Map<String, Object?>>[
          <String, Object?>{'preset_view': ''},
          <String, Object?>{'preset_view': '4d_invalid_preset'},
          <String, Object?>{'preset_view': 42},
        ];

        for (final payload in invalidPayloads) {
          expect(
            () => BlueprintConfig.fromJson(payload),
            throwsA(
              anyOf(
                isA<CheckedFromJsonException>(),
                isA<ArgumentError>(),
                isA<TypeError>(),
              ),
            ),
          );

          expect(
            container.read(blueprintEditorControllerProvider).presetView,
            equals(PresetView.matrixSummary),
          );
        }
      },
    );
  });
}
