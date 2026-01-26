import 'package:client_app/features/studio/data/schema_repository.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
// Force Rebuild

part 'studio_workflow_controller.freezed.dart';
part 'studio_workflow_controller.g.dart';

@freezed
abstract class WorkflowEditorState with _$WorkflowEditorState {
  const factory WorkflowEditorState({
    JsonSchema? schema,
    Map<String, dynamic>? data,
    @Default(false) bool isSaving,
    String? lastError,
  }) = _WorkflowEditorState;
}

@riverpod
class StudioWorkflowController extends _$StudioWorkflowController {
  @override
  FutureOr<WorkflowEditorState> build(String workflowId) async {
    // Parallel Fetch
    // 1. Schema for "workflow"
    // 2. Data for this specific workflow
    final results = await Future.wait([
      ref.read(schemaRepositoryProvider).fetchSchema('workflow'),
      ref.read(studioRepositoryProvider).fetchWorkflow(workflowId),
    ]);

    return WorkflowEditorState(
      schema: results[0] as JsonSchema,
      data: results[1] as Map<String, dynamic>,
    );
  }

  /// Updates the workflow data.
  /// Uses optimistic updates to reflect changes immediately in UI.
  Future<void> save(Map<String, dynamic> newData) async {
    final previousState = state.value;
    if (previousState == null) return;

    // 1. Optimistic Update
    state = AsyncData(previousState.copyWith(
      data: newData,
      isSaving: true,
      lastError: null,
    ));

    try {
      // 2. Async Persist
      await ref.read(studioRepositoryProvider).updateWorkflow(workflowId, newData);
      
      // 3. Success (Stop loading)
      // Note: We don't fetch again unless granular response needed.
      state = AsyncData(previousState.copyWith(
        data: newData, // Confirm new data
        isSaving: false,
      ));
    } catch (e, st) {
      // 4. Failure: Revert and show error
      state = AsyncData(previousState.copyWith(
        // Revert data to purely previous state? 
        // Or keep user edits but show error? 
        // "Revert" is safer for data integrity, "Keep" is better for UX (don't lose typing).
        // Strategy: Keep "dirty" data in UI but flag error so they can retry.
        // Actually, for "Optimistic", if it failed, the backend doesn't have it.
        // If we revert, we lose what they typed. 
        // Let's Keep the data but mark error.
        data: newData, 
        isSaving: false,
        lastError: 'Failed to save: $e',
      ));
      
      // Log for debugging
      print('Save failed: $e\n$st');
    }
  }
}
