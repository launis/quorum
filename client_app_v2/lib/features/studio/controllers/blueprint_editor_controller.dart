import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:client_app/features/studio/models/blueprint_config.dart';

part 'blueprint_editor_controller.g.dart';

/// Manages [BlueprintConfig] state for the Studio Blueprint Editor,
/// enforcing strict schema binding with backend Pydantic V2 models.
@riverpod
class BlueprintEditorController extends _$BlueprintEditorController {
  @override
  BlueprintConfig build() {
    ref.cacheFor(AppDurations.cacheTimeout);
    return const BlueprintConfig(presetView: PresetView.metrics1d);
  }

  /// Hydrates [BlueprintConfig] from [initialOutputMapping] or resets to default when empty.
  void initialize(Map<String, Object?>? initialOutputMapping) {
    if (initialOutputMapping != null && initialOutputMapping.isNotEmpty) {
      try {
        state = BlueprintConfig.fromJson(Map.from(initialOutputMapping));
      } catch (e, st) {
        ref
            .read(loggerServiceProvider)
            .error(
              'BlueprintEditorController',
              'BLUEPRINT_INIT_FAILED: Failed to parse initial blueprint configuration.',
              e,
              st,
            );
        rethrow;
      }
    } else {
      state = const BlueprintConfig(presetView: PresetView.metrics1d);
    }
  }

  /// Updates the active [PresetView] on the current [BlueprintConfig].
  void setPresetView(PresetView presetView) {
    state = state.copyWith(presetView: presetView);
  }
}
