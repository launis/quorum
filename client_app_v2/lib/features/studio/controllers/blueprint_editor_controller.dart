import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:client_app/features/studio/models/blueprint_config.dart';

part 'blueprint_editor_controller.g.dart';

/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `BlueprintConfig` ensuring seamless binding with Pydantic V2 schemas.
@riverpod
class BlueprintEditorController extends _$BlueprintEditorController {
  @override
  BlueprintConfig build() {
    ref.cacheFor(AppDurations.cacheTimeout);
    return const BlueprintConfig(presetView: '1d_metrics');
  }

  void initialize(Map<String, dynamic>? initialOutputMapping) {
    if (initialOutputMapping != null && initialOutputMapping.isNotEmpty) {
      state = BlueprintConfig.fromJson(initialOutputMapping);
    } else {
      state = const BlueprintConfig(presetView: '1d_metrics');
    }
  }

  void setPresetView(String presetView) {
    state = state.copyWith(presetView: presetView);
  }
}
