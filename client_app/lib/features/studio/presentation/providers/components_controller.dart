import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'components_controller.g.dart';

@riverpod
class ComponentsController extends _$ComponentsController {
  @override
  FutureOr<List<StudioComponentDef>> build() async {
    // The strict SSOT API now guarantees /components only returns text/rule configurations
    return ref.watch(studioRepositoryProvider).getComponents();
  }

  Future<void> create(StudioComponentDef component) async {
    final previousState = state;
    // 1. Optimistic Update
    state = AsyncData([...(state.value ?? []), component]);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).createComponent(component);
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e) {
      // 4. Rollback
      state = previousState;
      rethrow;
    }
  }

  Future<void> updateComponent(StudioComponentDef component) async {
    final previousState = state;
    // 1. Optimistic Update
    final oldList = state.value ?? [];
    final newList =
        oldList.map((c) => c.id == component.id ? component : c).toList();
    state = AsyncData(newList);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).updateComponent(component);
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e) {
      // 4. Rollback
      state = previousState;
      rethrow;
    }
  }

  Future<void> delete(String id) async {
    final previousState = state;
    // 1. Optimistic Update
    state = AsyncData((state.value ?? []).where((c) => c.id != id).toList());

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).deleteComponent(id);
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e) {
      // 4. Rollback
      state = previousState;
      rethrow;
    }
  }
}
