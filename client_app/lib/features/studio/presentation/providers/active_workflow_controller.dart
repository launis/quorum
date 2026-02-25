import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'active_workflow_controller.g.dart';

@riverpod
class ActiveWorkflowController extends _$ActiveWorkflowController {
  @override
  FutureOr<WorkflowDef?> build() async {
    return null; // Start empty, loaded via loadWorkflow
  }

  Future<void> loadWorkflow(String id) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      return ref.read(studioRepositoryProvider).getWorkflow(id);
    });
  }

  Future<void> updateStep(String stepId, Map<String, dynamic> newConfig) async {
    final current = state.value;
    if (current == null) return;

    final originalSteps = current.steps;
    final updatedSteps = current.steps.map((step) {
      if (step.id == stepId) return step.copyWith(config: newConfig);
      return step;
    }).toList();

    final updatedWf = current.copyWith(steps: updatedSteps);
    state = AsyncData(updatedWf);

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e) {
      state = AsyncData(current.copyWith(steps: originalSteps));
      rethrow;
    }
  }

  Future<void> reorderSteps(int oldIndex, int newIndex) async {
    final current = state.value;
    if (current == null) return;

    if (oldIndex < newIndex) newIndex -= 1;

    final originalSteps = current.steps;
    final items = List<WorkflowStepDef>.from(current.steps);
    final item = items.removeAt(oldIndex);
    items.insert(newIndex, item);

    final updatedWf = current.copyWith(steps: items);
    state = AsyncData(updatedWf);

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e) {
      state = AsyncData(current.copyWith(steps: originalSteps));
      rethrow;
    }
  }

  Future<void> addStep(WorkflowStepDef step) async {
    final current = state.value;
    if (current == null) return;

    final newSteps = [...current.steps, step];
    final updatedWf = current.copyWith(steps: newSteps);

    final previousState = state;
    state = AsyncData(updatedWf);

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e, st) {
      state = previousState;
      rethrow;
    }
  }

  Future<void> updateMetadata({String? name, String? description}) async {
    final current = state.value;
    if (current == null) return;

    final updatedWf = current.copyWith(
      name: name ?? current.name ?? 'Copy',
      description: description ?? current.description,
    );

    final previousState = state;
    state = AsyncData(updatedWf);

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }

  Future<void> save() async {
    final current = state.value;
    if (current == null) return;

    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(studioRepositoryProvider).saveWorkflow(current);
      return current;
    });
  }
}
