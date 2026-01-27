import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_controller.freezed.dart';
part 'studio_controller.g.dart';

@freezed
abstract class StudioState with _$StudioState {
  const factory StudioState({
    @Default(AsyncValue.data(<WorkflowDef>[])) AsyncValue<List<WorkflowDef>> workflows,
    @Default(AsyncValue.data(null)) AsyncValue<WorkflowDef?> activeWorkflow,
    @Default(AsyncValue.data(<ComponentDef>[])) AsyncValue<List<ComponentDef>> components,
  }) = _StudioState;
}

@Riverpod(keepAlive: true)
class StudioController extends _$StudioController {
  @override
  StudioState build() {
    return const StudioState();
  }

  Future<void> loadWorkflows() async {
    state = state.copyWith(workflows: const AsyncValue.loading());
    state = state.copyWith(
      workflows: await AsyncValue.guard(() async {
        return ref.read(studioRepositoryProvider).getWorkflows();
      }),
    );
  }

  /// **Load Components List**
  Future<void> loadComponents() async {
    state = state.copyWith(components: const AsyncValue.loading());
    state = state.copyWith(
      components: await AsyncValue.guard(() async {
        return ref.read(studioRepositoryProvider).getAvailableComponents();
      }),
    );
  }

  /// **Load Active Workflow**
  Future<void> loadWorkflow(String id) async {
    state = state.copyWith(activeWorkflow: const AsyncValue.loading());
    state = state.copyWith(
      activeWorkflow: await AsyncValue.guard(() async {
        return ref.read(studioRepositoryProvider).getWorkflow(id);
      }),
    );
  }

  /// **Update Step Configuration (Active Workflow)**
  Future<void> updateStep(String stepId, Map<String, dynamic> newConfig) async {
    final current = state.activeWorkflow.value;
    if (current == null) return;

    final originalSteps = current.steps;

    // 1. Optimistic Update locally
    final updatedSteps = current.steps.map((step) {
      if (step.id == stepId) {
        return step.copyWith(config: newConfig);
      }
      return step;
    }).toList();

    final updatedWf = current.copyWith(steps: updatedSteps);
    state = state.copyWith(activeWorkflow: AsyncValue.data(updatedWf));

    // 2. Persist
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e) {
      // 3. Rollback
      state = state.copyWith(
        activeWorkflow: AsyncValue.data(current.copyWith(steps: originalSteps)),
      );
      // We could set activeWorkflow to error, but usually toast is better for partial failure
      // Setting state.activeWorkflow to error might blocking the UI.
      // Ideally we use a side-effect channel. For now, we revert.
    }
  }

  /// **Reorder Steps (Active Workflow)**
  Future<void> reorderSteps(int oldIndex, int newIndex) async {
    final current = state.activeWorkflow.value;
    if (current == null) return;

    if (oldIndex < newIndex) {
      newIndex -= 1;
    }

    final originalSteps = current.steps;
    final items = List<WorkflowStepDef>.from(current.steps);
    final item = items.removeAt(oldIndex);
    items.insert(newIndex, item);

    final updatedWf = current.copyWith(steps: items);
    state = state.copyWith(activeWorkflow: AsyncValue.data(updatedWf));

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e) {
      state = state.copyWith(
        activeWorkflow: AsyncValue.data(current.copyWith(steps: originalSteps)),
      );
    }
  }

  /// **Add Step (Active Workflow)**
  Future<void> addStep(WorkflowStepDef step) async {
    final current = state.activeWorkflow.value;
    if (current == null) return;

    final newSteps = [...current.steps, step];
    final updatedWf = current.copyWith(steps: newSteps);

    state = state.copyWith(activeWorkflow: AsyncValue.data(updatedWf));

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e, st) {
      state = state.copyWith(activeWorkflow: AsyncValue.error(e, st));
    }

  }

  /// **Update Metadata (Active Workflow)**
  Future<void> updateMetadata({String? name, String? description}) async {
    final current = state.activeWorkflow.value;
    if (current == null) return;

    final updatedWf = current.copyWith(
      name: name ?? current.name,
      description: description ?? current.description,
    );

    state = state.copyWith(activeWorkflow: AsyncValue.data(updatedWf));
    // Auto-save logic
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWf);
    } catch (e) {
      // Revert in UI if critical, or just let error bubble?
    }
  }

  /// **Save Active Workflow (Explicit)**
  Future<void> save() async {
    final current = state.activeWorkflow.value;
    if (current == null) return;

    state = state.copyWith(activeWorkflow: const AsyncValue.loading());
    state = state.copyWith(
      activeWorkflow: await AsyncValue.guard(() async {
        await ref.read(studioRepositoryProvider).saveWorkflow(current);
        return current;
      }),
    );
  }

  /// **Create Workflow**
  Future<void> createWorkflow(WorkflowDef workflow) async {
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(workflow);
      await loadWorkflows();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> deleteWorkflow(String id) async {
    try {
      await ref.read(studioRepositoryProvider).deleteWorkflow(id);
      // Refresh list
      await loadWorkflows();
    } catch (e) {
      rethrow;
    }
  }

  /// **Copy Workflow**
  /// Optimistically adds a "Copying..." placeholder or just relies on fast server response.
  /// Given requirement: "temporary copying state".
  Future<void> copyWorkflow(String originalId, String newName) async {
    // 1. Optimistic Update (Optional: Add a fake item with loading status if UI supports it)
    // For now, we rely on the loader overlay usually handled by the UI listening to this future.
    // However, we can set the whole list to loading or keep it as data.
    
    try {
      await ref.read(studioRepositoryProvider).copyWorkflow(originalId, newName);
      // 2. Success - Refresh List
      await loadWorkflows(); 
    } catch (e) {
      // 3. Failure
      // No strict rollback needed since we didn't inject a fake item yet.
      // If we had injected a fake item, we would filter it out here.
      // Rethrowing allows UI to show Snackbar.
      rethrow;
    }
  }
}

