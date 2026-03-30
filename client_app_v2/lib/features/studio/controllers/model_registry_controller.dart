import 'dart:async';
import 'dart:isolate';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'model_registry_controller.g.dart';

// --- Controllers ---

/// Controller managing the Model Registry strictly using strict representations.
/// Implements Optimistic UI principles where possible.
@riverpod
class ModelRegistryController extends _$ModelRegistryController {
  @override
  FutureOr<List<ModelConfig>> build() async {
    // SWR Strategy for List Views
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchConfigs();
  }

  Future<List<ModelConfig>> _fetchConfigs() async {
    final client = ref.read(studioClientProvider);
    final rawList = await client.getSystemConfigs();
    return Isolate.run(
      () => rawList
          .where((map) => map['type'] == 'model_registry')
          .map((e) => ModelConfig.fromJson(e))
          .toList(),
    );
  }

  /// Refreshes the model registry list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newConfigs = await _fetchConfigs();
      state = AsyncValue.data(newConfigs);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Refresh failed', e, st);
      state = AsyncValue.error(e, st);
    }
  }

  /// Saves a model registry config utilizing Optimistic Updates.
  Future<ModelConfig> saveConfig(String id, ModelConfig payload) async {
    final previousState = state;
    ModelConfig returnData =
        payload; // Assuming payload already has ID initialized or preserved

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<ModelConfig>.from(state.value!);
      final index = currentList.indexWhere((m) => m.id == id);

      if (index >= 0) {
        currentList[index] = payload;
      } else {
        currentList.add(payload);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.saveSystemConfig(id, payload.toJson());
      final verifiedConfig = await Isolate.run(
        () => ModelConfig.fromJson(rawResponse),
      );

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<ModelConfig>.from(state.value!);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedConfig;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedConfig;
      }
      return returnData;
    } catch (e, st) {
      // 4. Rollback on Failure
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes a model registry config. Throwing AppException on orphan rejection
  Future<void> deleteConfig(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteSystemConfig(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<ModelConfig>.from(state.value!);
        currentList.removeWhere((m) => m.id == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones a system config utilizing Optimistic UI.
  Future<ModelConfig> cloneConfig(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final rawConfig = await client.cloneSystemConfig(id);
      final clonedConfig = await Isolate.run(
        () => ModelConfig.fromJson(rawConfig),
      );

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<ModelConfig>.from(state.value!);
        currentList.add(clonedConfig);
        state = AsyncValue.data(currentList);
      }
      return clonedConfig;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }
}

/// Fetches a single System Config natively by ID
@riverpod
Future<ModelConfig> modelRegistryById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  final rawData = await client.getSystemConfig(id);
  return Isolate.run(() => ModelConfig.fromJson(rawData));
}

/// Fetches the list of available models from the backend.
@riverpod
Future<List<String>> availableModels(Ref ref) async {
  final client = ref.watch(studioClientProvider);
  return client.getAvailableModels();
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class ModelRegistryForm extends _$ModelRegistryForm {
  @override
  FutureOr<ModelConfig> build(String configId) async {
    if (configId == 'new') {
      return const ModelConfig(
        id: 'syscfg_new',
        slug: 'syscfg_new',
        type: 'model_registry',
        models: {},
      );
    }

    // 1. Fetch data strictly
    return ref.watch(modelRegistryByIdProvider(configId).future);
  }

  /// Used by the form to trigger a rebuild on synchronous edits if required.
  void forceRebuild(ModelConfig updatedConfig) {
    state = AsyncData(updatedConfig);
  }

  Future<void> submit(ModelConfig updatedData) async {
    state = const AsyncLoading(); // Side effect isolation

    state = await AsyncValue.guard(() async {
      final idToSave = configId == 'new'
          ? (updatedData.id.isNotEmpty ? updatedData.id : 'syscfg_new')
          : configId;

      // Ensure the payload has the correct ID
      final payloadToSave = updatedData.copyWith(id: idToSave);

      await ref
          .read(modelRegistryControllerProvider.notifier)
          .saveConfig(idToSave, payloadToSave);
      return payloadToSave; // Optimistic form state return
    });
  }
}
