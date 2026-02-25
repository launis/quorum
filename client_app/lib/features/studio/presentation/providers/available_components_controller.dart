import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'available_components_controller.g.dart';

/// **Available Components Controller**
///
/// Manages the list of available text components (Prompts) using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).
@riverpod
class AvailableComponentsController extends _$AvailableComponentsController {
  @override
  FutureOr<List<StudioComponentDef>> build() async {
    return ref.watch(studioRepositoryProvider).getComponents();
  }

  /// **Create Component**
  Future<void> createComponent(StudioComponentDef component) async {
    final previousState = state;

    final currentList = state.value ?? [];
    state = AsyncData([...currentList, component]);

    try {
      await ref.read(studioRepositoryProvider).createComponent(component);
      ref.invalidateSelf();
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }

  /// **Delete Component**
  Future<void> deleteComponent(String id) async {
    final previousState = state;

    final currentList = state.value ?? [];
    state = AsyncData(currentList.where((c) => c.id != id).toList());

    try {
      await ref.read(studioRepositoryProvider).deleteComponent(id);
      ref.invalidateSelf();
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }
}
