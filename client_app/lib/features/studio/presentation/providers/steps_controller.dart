import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/step_config.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'steps_controller.g.dart';

@riverpod
class StepsController extends _$StepsController {
  @override
  FutureOr<List<StepConfig>> build() async {
    // Wait for auth to be ready (Critical for Mock Mode)
    await ref.watch(authControllerProvider.future);
    return _fetchSteps();
  }

  Future<List<StepConfig>> _fetchSteps() async {
    final repo = ref.read(studioRepositoryProvider);
    return repo.fetchSteps();
  }

  Future<void> create(StepConfig step) async {
    final previousState = state;
    // 1. Optimistic Update (Append)
    // Note: ID might be temporary, but invalidation resolves it.
    if (state.value != null) {
      state = AsyncData([...state.value!, step]);
    }
    
    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).saveStep(step);
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e, st) {
      // 4. Rollback
      state = previousState;
      state = AsyncValue.error(e, st);
      // We rethrow to let UI handle toasts if needed
      if (e is AppError) rethrow; // Or generic
    }
  }

  Future<void> updateStep(StepConfig step) async {
    final previousState = state;
    if (previousState.value == null) return;

    // 1. Optimistic Update
    final updatedList =
        previousState.value!.map((s) => s.id == step.id ? step : s).toList();
    state = AsyncValue.data(updatedList);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).saveStep(step);
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e, st) {
       // 4. Rollback
       state = previousState;
       state = AsyncValue.error(e, st);
    }
  }

  Future<void> delete(String id) async {
    final previousState = state;
    if (previousState.value == null) return;
    
    // 1. Optimistic Update
    final updatedList = previousState.value!.where((s) => s.id != id).toList();
    state = AsyncValue.data(updatedList);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).deleteStep(id);
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e, st) {
       // 4. Rollback
       state = previousState;
       state = AsyncValue.error(e, st);
    }
  }
}
