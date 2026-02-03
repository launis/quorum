import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'matrix_controller.g.dart';

/// Holds the scratchpad/unsaved changes of the currently active matrix.
@riverpod
class MatrixEditorState extends _$MatrixEditorState {
  @override
  MatrixDef? build() {
    return null;
  }

  void set(MatrixDef? matrix) {
    state = matrix;
  }

  void update(MatrixDef Function(MatrixDef) updater) {
    if (state != null) {
      state = updater(state!);
    }
  }
}

/// Manages the lifecycle and persistence of the current matrix.
@riverpod
class MatrixController extends _$MatrixController {
  @override
  FutureOr<MatrixDef?> build() {
    return null;
  }

  Future<void> selectMatrix(String id) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final matrix = await ref.read(studioRepositoryProvider).fetchMatrix(id);
      // Seed the editor state
      ref.read(matrixEditorStateProvider.notifier).set(matrix);
      return matrix;
    });
  }

  Future<void> createNewMatrix() async {
    // Optional helper to start fresh
    final newMatrix = MatrixDef(
      id: 'new_${DateTime.now().millisecondsSinceEpoch}',
      name: 'New Matrix',
      description: '',
      scale: {'min': 1, 'max': 5},
      criteria: [],
    );
    state = AsyncValue.data(newMatrix);
    ref.read(matrixEditorStateProvider.notifier).set(newMatrix);
  }

  Future<void> saveCurrentMatrix() async {
    final currentDraft = ref.read(matrixEditorStateProvider);
    if (currentDraft == null) return;

    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref.read(studioRepositoryProvider).saveMatrix(currentDraft);
      // After save, we might want to reload to get finalized ID or confirmed state
      // But typically we just update our canonical state to match the draft
      return currentDraft;
    });
  }

  Future<void> deleteMatrix(String id) async {
    state = const AsyncValue.loading();
    try {
      await ref.read(studioRepositoryProvider).deleteComponent(id);
      state = const AsyncValue.data(null);
      ref.read(matrixEditorStateProvider.notifier).set(null);
    } catch (e, st) {
      if (e is AppError) {
        // AppError should be caught by UI, but we must set state to error/null/previous?
        // Actually, if we set state to error, UI shows error widget.
        // We want to KEEP the current state visible and show SnackBar.
        // So we set state back to data (maybe null if we want to close editor, but we failed).
        // Best approach: Rethrow for UI to catch, set state to data(current) to stop spinner.
        
        final currentDraft = ref.read(matrixEditorStateProvider);
        state = AsyncValue.data(currentDraft); // Stop loading, restore view
        rethrow; // UI catches this to show SnackBar
      }
      state = AsyncValue.error(e, st);
    }
  }
}
