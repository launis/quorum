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
    @Default(AsyncValue.loading())
    AsyncValue<List<LLMProviderConfig>> providers,
    @Default(AsyncValue.loading())
    AsyncValue<Map<String, List<String>>> availableOptions,
    String? selectedProviderId,
    @Default(AsyncValue.data(null)) AsyncValue<AdHocTestResult?> testResult,
    @Default(false) bool isSaving,
  }) = _ModelRegistryState;
}

@riverpod
class ModelRegistryController extends _$ModelRegistryController {
  late final ModelRegistryRepository _repository;

  @override
  ModelRegistryState build() {
    _repository = ref.watch(modelRegistryRepositoryProvider);
    // Move side-effect to next microtask to ensure state is initialized
    Future.microtask(() => _loadData());
    return const ModelRegistryState();
  }

  Future<void> _loadData() async {
    state = state.copyWith(
      providers: const AsyncValue.loading(),
      availableOptions: const AsyncValue.loading(),
    );

    final result = await Future.wait([
      _repository.getProviders(),
      _repository.getModelOptions(),
    ]);
    
    // Process Providers
    final providersResult = result[0] as Either<AppError, List<LLMProviderConfig>>;
    providersResult.fold(
      (l) => state = state.copyWith(providers: AsyncValue.error(l, StackTrace.current)),
      (r) => state = state.copyWith(providers: AsyncValue.data(r)),
    );

    // Process Options
    final optionsResult = result[1] as Either<AppError, Map<String, List<String>>>;
    optionsResult.fold(
      (l) => state = state.copyWith(availableOptions: AsyncValue.error(l, StackTrace.current)),
      (r) => state = state.copyWith(availableOptions: AsyncValue.data(r)),
    );
  }

  void selectProvider(String? id) {
    state = state.copyWith(
      selectedProviderId: id,
      testResult: const AsyncValue.data(null),
    );
  }

  Future<void> saveConfig(String id, LLMProviderConfig config) async {
    state = state.copyWith(isSaving: true);

    final result = await _repository.updateProvider(id, config);

    state = state.copyWith(isSaving: false);

    result.fold((l) {}, (r) {
      state.providers.whenData((list) {
        final index = list.indexWhere((p) => p.id == id);

        List<LLMProviderConfig> newList;
        if (index >= 0) {
          newList = List.of(list)..[index] = r;
        } else {
          newList = List.of(list)..add(r);
        }
        state = state.copyWith(providers: AsyncValue.data(newList));
      });
    });
  }

  Future<void> runTest(AdHocTestRequest request) async {
    state = state.copyWith(testResult: const AsyncValue.loading());

    final result = await _repository.runAdHocTest(request);

    result.fold(
      (l) =>
          state = state.copyWith(
            testResult: AsyncValue.error(l, StackTrace.current),
          ),
      (r) =>
          state = state.copyWith(
            testResult: AsyncValue.data(r),
          ),
    );
  }
}
