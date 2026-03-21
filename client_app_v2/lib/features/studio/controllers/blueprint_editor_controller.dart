import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/utils/riverpod_extensions.dart';

part 'blueprint_editor_controller.g.dart';

/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `output_mapping` dictionary ensuring seamless binding with Pydantic V2 schemas.
@riverpod
class BlueprintEditorController extends _$BlueprintEditorController {
  @override
  Map<String, dynamic> build() {
    ref.cacheFor(const Duration(minutes: 3));
    return {'preset_view': '1d_metrics'};
  }

  void initialize(Map<String, dynamic>? initialOutputMapping) {
    if (initialOutputMapping != null && initialOutputMapping.isNotEmpty) {
      state = Map<String, dynamic>.from(initialOutputMapping);
    } else {
      state = {'preset_view': '1d_metrics'};
    }
  }

  void setPresetView(String presetView) {
    state = {...state, 'preset_view': presetView};
  }
}
