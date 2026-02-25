import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../data/model_registry_repository.dart';
import 'model_registry_providers.dart';

part 'agent_mappings_controller.g.dart';

@riverpod
class AgentMappingsController extends _$AgentMappingsController {
  @override
  Future<Map<String, ({String? strategyId, String name})>> build() async {
    final repository = ref.watch(modelRegistryRepositoryProvider);
    final result = await repository.getAgentMappings();

    return result.fold((l) => throw l, (r) => r);
  }

  /// Updates the mapping optimistically.
  Future<void> updateMapping(String agentId, String strategyId) async {
    final previousState = state;
    if (previousState is! AsyncData<Map<String, ({String? strategyId, String name})>>) return;

    final currentMap = Map<String, ({String? strategyId, String name})>.from(previousState.value);
    
    // Preserve existing name on update
    final existingName = currentMap[agentId]?.name ?? agentId;
    final newMap = Map<String, ({String? strategyId, String name})>.from(currentMap)..[agentId] = (strategyId: strategyId, name: existingName);

    // Optimistic update
    state = AsyncData(newMap);

    final repository = ref.read(modelRegistryRepositoryProvider);
    final result = await repository.updateAgentMapping(agentId, strategyId);

    result.fold(
      (l) {
        // Rollback
        state = previousState;
        state = AsyncError(l, StackTrace.current);
      },
      (r) {
        // Silent sync
        ref.invalidateSelf();
      },
    );
  }
}
