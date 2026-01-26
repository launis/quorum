import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_controller.g.dart';

@riverpod
class StudioController extends _$StudioController {
  @override
  FutureOr<WorkflowDef?> build() {
    return null; // Initially no workflow loaded
  }

  /// **Load Workflow**
  /// Fetches workflow data and hydrates state.
  Future<void> loadWorkflow(String id) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return ref.read(studioRepositoryProvider).getWorkflow(id);
    });
  }

  /// **Update Step Configuration**
  /// Optimistically updates a specific step's config in the local state.
  Future<void> updateStep(String stepId, Map<String, dynamic> newConfig) async {
    final current = state.value;
    if (current == null) return;

    final originalSteps = current.steps;

    // 1. Optimistic Update locally
    final updatedSteps = current.steps.map((step) {
      if (step.id == stepId) {
        return step.copyWith(config: newConfig);
      }
      return step;
    }).toList();

    state = AsyncValue.data(current.copyWith(steps: updatedSteps));

    // 2. Persist to Backend (Debouncing could be added here if high frequency)
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(state.value!);
    } catch (e, st) {
      // 3. Rollback on failure
      state = AsyncValue.data(current.copyWith(steps: originalSteps));
      // Optionally set error state or show toast via side-effect provider
      state = AsyncValue.error(e, st);
    }
  }

  /// **Reorder Steps**
  /// Updates the list sequence immediately and persists.
  Future<void> reorderSteps(int oldIndex, int newIndex) async {
    final current = state.value;
    if (current == null) return;

    if (oldIndex < newIndex) {
      newIndex -= 1;
    }

    final originalSteps = current.steps;
    final items = List<WorkflowStepDef>.from(current.steps);
    final item = items.removeAt(oldIndex);
    items.insert(newIndex, item);

    // 1. Optimistic Update
    final updatedWorkflow = current.copyWith(steps: items);
    state = AsyncValue.data(updatedWorkflow);

    // 2. Persist
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWorkflow);
    } catch (e, st) {
      // 3. Rollback
      state = AsyncValue.data(current.copyWith(steps: originalSteps));
      state = AsyncValue.error(e, st);
    }
  }

  /// **Add Step**
  /// Adds a new step to the workflow.
  Future<void> addStep(WorkflowStepDef step) async {
    final current = state.value;
    if (current == null) return;

    final newSteps = [...current.steps, step];
    final updatedWorkflow = current.copyWith(steps: newSteps);

    state = AsyncValue.data(updatedWorkflow);

    // Persist immediately for generic "add" action
    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(updatedWorkflow);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// **Update Workflow Metadata**
  /// Updates top-level fields (Name, Description, etc.)
  Future<void> updateMetadata({String? name, String? description}) async {
    final current = state.value;
    if (current == null) return;

    final updated = current.copyWith(
      name: name ?? current.name,
      description: description ?? current.description,
    );

    state = AsyncValue.data(updated);
    // Usually metadata update logic includes saving, but can be explicit save too.
    // For consistency with other methods, let's auto-save (or leave for explicit save button).
    // The prompt says "updateState", doesn't explicitly force save here,
    // but consistent UX usually autosaves in Studio.
  }

  /// **Save Workflow**
  /// Persists the current state to the backend explicitly (e.g. Save Button).
  Future<void> save() async {
    final current = state.value;
    if (current == null) return;

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref.read(studioRepositoryProvider).saveWorkflow(current);
      return current;
    });
  }

  /// **Validation**
  bool get isValid {
    final current = state.value;
    if (current == null) return false;
    if (current.name.trim().isEmpty) return false;
    return true;
  }
}
