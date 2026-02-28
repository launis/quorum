import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'workflows_controller.g.dart';

@riverpod
class WorkflowsController extends _$WorkflowsController {
  @override
  FutureOr<List<WorkflowDef>> build() async {
    return ref.watch(studioRepositoryProvider).getWorkflows();
  }

  Future<void> createWorkflow(WorkflowDef workflow) async {
    final previousState = state;
    final currentList = state.value ?? [];

    // Optimistic Update
    state = AsyncData([...currentList, workflow]);

    try {
      await ref.read(studioRepositoryProvider).saveWorkflow(workflow);
      ref.invalidateSelf();
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }

  Future<void> deleteWorkflow(String id) async {
    final previousState = state;
    final currentList = state.value ?? [];

    state = AsyncData(currentList.where((w) => w.id != id).toList());

    try {
      await ref.read(studioRepositoryProvider).deleteWorkflow(id);
      ref.invalidateSelf();
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }

  Future<void> copyWorkflow(String originalId, String newName) async {
    // Rely on loader for copying, as inserting a fake item is complex
    try {
      await ref
          .read(studioRepositoryProvider)
          .copyWorkflow(originalId, newName);
      ref.invalidateSelf();
    } catch (e) {
      rethrow;
    }
  }
}
