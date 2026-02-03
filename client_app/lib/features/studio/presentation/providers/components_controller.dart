import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'components_controller.g.dart';

@riverpod
class ComponentsController extends _$ComponentsController {
  @override
  FutureOr<List<StudioComponentDef>> build() async {
    return ref.watch(studioRepositoryProvider).getComponents(excludeTypes: [
      'evaluation_matrix',
      'system_config',
      'agent',
      'processor',
      'output_config'
    ]);
  }

  Future<void> create(StudioComponentDef component) async {
    final previousState = state;
    // Optimistic Update: Append new component
    state = AsyncData([...(state.value ?? []), component]);
    
    try {
      await ref.read(studioRepositoryProvider).createComponent(component);
    } catch (e) {
      state = previousState; // Revert
      rethrow;
    }
  }

  Future<void> updateComponent(StudioComponentDef component) async {
     final previousState = state;
     // Optimistic Update: Replace component with matching ID
     final oldList = state.value ?? [];
     final newList = oldList.map((c) => c.id == component.id ? component : c).toList();
     state = AsyncData(newList);
     
     try {
       await ref.read(studioRepositoryProvider).updateComponent(component);
     } catch (e) {
       state = previousState; // Revert
       rethrow;
     }
  }
  
  Future<void> delete(String id) async {
      final previousState = state;
      // Optimistic Update: Remove component with matching ID
      state = AsyncData((state.value ?? []).where((c) => c.id != id).toList());
      
      try {
          await ref.read(studioRepositoryProvider).deleteComponent(id);
      } catch (e) {
          state = previousState; // Revert
          rethrow;
      }
  }
}
