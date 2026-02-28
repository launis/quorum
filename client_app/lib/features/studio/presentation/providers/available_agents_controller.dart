import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'available_agents_controller.g.dart';

@riverpod
class AvailableAgentsController extends _$AvailableAgentsController {
  @override
  FutureOr<List<StudioComponentDef>> build() async {
    return ref.watch(studioRepositoryProvider).getAgents();
  }

  Future<void> saveAgent(StudioComponentDef agent) async {
    final previousState = state;
    final currentList = state.value ?? [];

    // Naively replace or append based on ID, simple optimistic approach
    final isNew = !currentList.any((a) => a.id == agent.id);
    final newList =
        isNew
            ? [...currentList, agent]
            : currentList.map((a) => a.id == agent.id ? agent : a).toList();

    state = AsyncData(newList);

    try {
      await ref.read(studioRepositoryProvider).saveAgent(agent);
      ref.invalidateSelf();
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }
}
