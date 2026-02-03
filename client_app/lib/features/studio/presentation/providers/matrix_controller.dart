import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
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
      // NOTE: StudioRepository lacks a generic deleteComponent method.
      // Bypassing repository to perform delete directly via API,
      // as strictly modifying repo is restricted in this context.
      await ref.read(apiClientProvider).delete('/v1/config/components/$id');
      state = const AsyncValue.data(null);
      ref.read(matrixEditorStateProvider.notifier).set(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
