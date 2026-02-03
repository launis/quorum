import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/step_config.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'steps_controller.g.dart';

@riverpod
class StepsController extends _$StepsController {
  @override
  FutureOr<List<StepConfig>> build() async {
    return _fetchSteps();
  }

  Future<List<StepConfig>> _fetchSteps() async {
    final repo = ref.read(studioRepositoryProvider);
    return repo.fetchSteps();
  }

  Future<void> create(StepConfig step) async {
    final repo = ref.read(studioRepositoryProvider);
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await repo.saveStep(step);
      return _fetchSteps();
    });
  }

  Future<void> updateStep(StepConfig step) async {
    // Optimistic Update can be tricky with full list reload,
    // but for safety we reload.
    // For true optimistic UI, we would update the list locally first.
    final repo = ref.read(studioRepositoryProvider);
    
    // Optimistic Local Update
    final currentList = state.value ?? [];
    final updatedList = currentList.map((s) => s.id == step.id ? step : s).toList();
    state = AsyncValue.data(updatedList);

    // Actual Save
    try {
      await repo.saveStep(step);
      // Re-fetch to ensure consistency (optional if we trust backend return)
      // state = await AsyncValue.guard(() => _fetchSteps()); 
    } catch (e, st) {
       // Revert on error
       state = AsyncValue.error(e, st);
       // Re-fetch to allow retry or show actual state
       ref.invalidateSelf();
    }
  }

  Future<void> delete(String id) async {
    final repo = ref.read(studioRepositoryProvider);
    
    // Optimistic Local Delete
    final currentList = state.value ?? [];
    final updatedList = currentList.where((s) => s.id != id).toList();
    state = AsyncValue.data(updatedList);

    try {
      await repo.deleteStep(id);
    } catch (e, st) {
       state = AsyncValue.error(e, st);
       ref.invalidateSelf();
    }
  }
}
