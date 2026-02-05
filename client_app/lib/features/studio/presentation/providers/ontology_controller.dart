import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'ontology_controller.g.dart';

@riverpod
class OntologyController extends _$OntologyController {
  @override
  FutureOr<List<OntologyDimension>> build() async {
    return ref.watch(studioRepositoryProvider).fetchOntology();
  }

  Future<void> addDimension(OntologyDimension dimension) async {
    final previousState = state;
    if (previousState.value == null) return;

    // 1. Optimistic Update
    state = AsyncValue.data([...previousState.value!, dimension]);

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).saveDimension(dimension);
      
      // 3. Silent Invalidation
      // Always invalidate to ensure backend-generated IDs or sanitization is reflected.
      ref.invalidateSelf();
    } catch (e, st) {
      // 4. Rollback
      state = previousState; // Revert
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> updateDimension(OntologyDimension dimension) async {
    final previousState = state;
    if (previousState.value == null) return;

    // 1. Optimistic Update
    final updatedList =
        previousState.value!.map((e) {
          return e.id == dimension.id ? dimension : e;
        }).toList();
    state = AsyncValue.data(updatedList);

    try {
      // 2. API Call
      await ref
          .read(studioRepositoryProvider)
          .saveDimension(dimension, isUpdate: true);
      
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e, st) {
      // 4. Rollback
      state = previousState; // Revert
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> removeDimension(String id) async {
    final previousState = state;
    if (previousState.value == null) return;

    // 1. Optimistic Update
    state = AsyncValue.data(
      previousState.value!.where((e) => e.id != id).toList(),
    );

    try {
      // 2. API Call
      await ref.read(studioRepositoryProvider).deleteDimension(id);
      
      // 3. Silent Invalidation
      ref.invalidateSelf();
    } catch (e) {
      // 4. Rollback
      state = previousState;
      // Rethrow so UI can show SnackBar
      throw e is AppError ? e : AppError.server(e.toString());
    }
  }
}
