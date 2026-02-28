// ignore_for_file: invalid_annotation_target, override_on_non_overriding_member, unnecessary_import, non_abstract_class_inherits_abstract_member
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/error/app_error.dart';
import '../../data/model_registry_repository.dart';
import '../../domain/models/model_registry.dart';
import 'model_registry_providers.dart';

part 'model_registry_controller.freezed.dart';
part 'model_registry_controller.g.dart';

@freezed
abstract class ModelRegistryState with _$ModelRegistryState {
  const factory ModelRegistryState({
    @Default([]) List<LLMProviderConfig> providers,
    @Default({}) Map<String, List<String>> availableOptions,
    String? selectedProviderId,
    @Default(AsyncValue.data(null)) AsyncValue<AdHocTestResult?> testResult,
    @Default(false) bool isSaving,
  }) = _ModelRegistryState;
}

@riverpod
class ModelRegistryController extends _$ModelRegistryController {
  @override
  Future<ModelRegistryState> build() async {
    final repository = ref.watch(modelRegistryRepositoryProvider);

    // Parallel Fetch (Fail Fast)
    final result = await Future.wait([
      repository.getProviders(),
      repository.getModelOptions(),
    ]);

    final providersResult =
        result[0] as Either<AppError, List<LLMProviderConfig>>;
    final optionsResult =
        result[1] as Either<AppError, Map<String, List<String>>>;

    // We throw first error encountered to set state to AsyncError
    final providers = providersResult.getRight().getOrElse(
      () => throw providersResult.getLeft().toNullable()!,
    );
    final options = optionsResult.getRight().getOrElse(
      () => throw optionsResult.getLeft().toNullable()!,
    );

    return ModelRegistryState(providers: providers, availableOptions: options);
  }

  void selectProvider(String? id) {
    final currentState = state.value;
    if (currentState == null) return;

    state = AsyncData(
      currentState.copyWith(
        selectedProviderId: id,
        testResult: const AsyncValue.data(null),
      ),
    );
  }

  /// **Save Config**
  /// Uses Optimistic Update + Invalidate pattern.
  Future<void> saveConfig(String id, LLMProviderConfig config) async {
    final previousState = state.value;
    if (previousState == null) return;

    // 1. Optimistic Update
    final currentList = previousState.providers;
    final index = currentList.indexWhere((p) => p.id == id);

    List<LLMProviderConfig> newList;
    if (index >= 0) {
      newList = List.of(currentList)..[index] = config;
    } else {
      newList = [...currentList, config];
    }

    state = AsyncData(
      previousState.copyWith(providers: newList, isSaving: true),
    );

    try {
      // 2. API Call
      await ref
          .read(modelRegistryRepositoryProvider)
          .updateProvider(id, config);

      // 3. Silent Sync
      ref.invalidateSelf();
    } catch (e, st) {
      // 4. Rollback
      state = AsyncData(previousState);
      state = AsyncError(e, st);
      // We might want to rethrow to show error toast
      rethrow;
    }
  }

  Future<void> deleteConfig(String id) async {
    final previousState = state.value;
    if (previousState == null) return;

    // 1. Optimistic Update (Remove from list)
    final currentList = previousState.providers;
    final newList = currentList.where((p) => p.id != id).toList();

    state = AsyncData(
      previousState.copyWith(
        providers: newList,
        selectedProviderId:
            previousState.selectedProviderId == id
                ? null
                : previousState.selectedProviderId,
        isSaving: true,
      ),
    );

    // 2. API Call
    final result = await ref
        .read(modelRegistryRepositoryProvider)
        .deleteProvider(id);

    result.fold(
      (l) {
        // 3. Rollback
        state = AsyncData(previousState);
        // set error while keeping data
        state = AsyncError<ModelRegistryState>(
          l,
          StackTrace.current,
        ).copyWithPrevious(AsyncData(previousState));
      },
      (r) {
        // 4. Silent Sync
        ref.invalidateSelf();
      },
    );
  }

  Future<void> runTest(AdHocTestRequest request) async {
    final currentState = state.value;
    if (currentState == null) return;

    // Local Loading State for Test Result
    state = AsyncData(
      currentState.copyWith(testResult: const AsyncValue.loading()),
    );

    final result = await ref
        .read(modelRegistryRepositoryProvider)
        .runAdHocTest(request);

    result.fold(
      (l) {
        state = AsyncData(
          currentState.copyWith(
            testResult: AsyncValue.error(l, StackTrace.current),
          ),
        );
      },
      (r) {
        state = AsyncData(
          currentState.copyWith(testResult: AsyncValue.data(r)),
        );
      },
    );
  }
}
