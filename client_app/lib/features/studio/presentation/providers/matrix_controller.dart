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

    final previousState = state;

    // 1. Optimistic Update (Keep UI interactive / show clean state)
    // We assume draft is correct.
    state = AsyncValue.data(currentDraft);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).saveMatrix(currentDraft);

      // 3. Silent Invalidation
      // This will trigger build() -> fetchMatrix(id) to get backend data
      ref.invalidateSelf();
    } catch (e, st) {
      // 4. Rollback / Error
      // If save fails, we might want to keep the draft state but show error.
      state = previousState;
      state = AsyncValue.error(e, st);
      // Rethrow for UI handling
      rethrow;
    }
  }

  Future<void> deleteMatrix(String id) async {
    final previousState = state;

    // 1. Optimistic Update (Clear Editor)
    state = const AsyncValue.data(null);
    ref.read(matrixEditorStateProvider.notifier).set(null);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).deleteComponent(id);

      // 3. Silent Invalidation (Verify null)
      ref.invalidateSelf();
    } catch (e, st) {
      // 4. Rollback
      // If delete failed, restore the matrix in the editor.
      if (previousState.value != null) {
        ref.read(matrixEditorStateProvider.notifier).set(previousState.value);
        state = previousState;
      }

      // Rethrow for UI
      final appError = e is AppError ? e : AppError.server(e.toString());
      state = AsyncValue.error(appError, st);
      throw appError;
    }
  }
}
