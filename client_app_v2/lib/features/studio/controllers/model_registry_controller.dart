import 'dart:async';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:client_app/features/studio/models/gcp_location.dart';
import 'package:client_app/features/studio/models/llm_platform.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'model_registry_controller.g.dart';

// --- Controllers ---

/// Controller managing the Model Registry strictly using immutable [ModelConfig] models.
/// Implements optimistic UI updates with automatic state rollback on failure.
@riverpod
class ModelRegistryController extends _$ModelRegistryController {
  @override
  FutureOr<List<ModelConfig>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchConfigs();
  }

  Future<List<ModelConfig>> _fetchConfigs() async {
    final client = ref.read(studioClientProvider);
    return await client.getSystemConfigs();
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

  /// Saves a model registry configuration utilizing optimistic updates with rollback on failure.
  Future<ModelConfig> saveConfig(String id, ModelConfig payload) async {
    final previousState = state;
    final returnData = payload.copyWith(id: id);

    if (state case AsyncData(:final value)) {
      final currentList = List<ModelConfig>.from(value);
      final index = currentList.indexWhere((m) => m.id == id);

      if (index >= 0) {
        currentList[index] = returnData;
      } else {
        currentList.add(returnData);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      final client = ref.read(studioClientProvider);
      final verifiedConfig = await client.saveSystemConfig(id, returnData);

      if (state case AsyncData(:final value)) {
        final currentList = List<ModelConfig>.from(value);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedConfig;
          state = AsyncValue.data(currentList);
        }
      }
      ref.invalidate(modelRegistryByIdProvider(id));
      return verifiedConfig;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes a model registry configuration and propagates [AppException] on active reference conflicts.
  Future<void> deleteConfig(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteSystemConfig(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<ModelConfig>.from(value)
          ..removeWhere((m) => m.id == id);
        state = AsyncValue.data(currentList);
      }
      ref.invalidate(modelRegistryByIdProvider(id));
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones a system config and appends the backend-minted copy to state.
  Future<ModelConfig> cloneConfig(String id) async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final clonedConfig = await client.cloneSystemConfig(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<ModelConfig>.from(value)..add(clonedConfig);
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
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft System Config via the SSOT backend.
  Future<ModelConfig> createSystemConfigDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final draftConfig = await client.createSystemConfigDraft();

      if (state case AsyncData(:final value)) {
        final currentList = List<ModelConfig>.from(value)
          ..insert(0, draftConfig);
        state = AsyncValue.data(currentList);
      }
      return draftConfig;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('ModelRegistryController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }
}

/// Fetches a single System Config natively by ID.
@riverpod
Future<ModelConfig> modelRegistryById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return await client.getSystemConfig(id);
}

/// Fetches the list of available models from the backend filtered by platform and location.
@riverpod
Future<List<String>> availableModels(
  Ref ref, {
  String? platform,
  String? location,
}) async {
  ref.cacheFor(AppDurations.cacheTimeout);
  final client = ref.watch(studioClientProvider);
  return client.getAvailableModels(platform: platform, location: location);
}

/// Fetches supported GCP Vertex AI locations.
@riverpod
Future<List<GcpLocation>> supportedLocations(Ref ref) async {
  ref.cacheFor(AppDurations.cacheTimeout);
  final client = ref.watch(studioClientProvider);
  return client.getSupportedLocations();
}

/// Fetches supported LLM platforms.
@riverpod
Future<List<LlmPlatform>> supportedPlatforms(Ref ref) async {
  final client = ref.watch(studioClientProvider);
  return await client.getSupportedPlatforms();
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class ModelRegistryForm extends _$ModelRegistryForm {
  @override
  FutureOr<ModelConfig> build(String configId) async {
    final config = await ref.watch(modelRegistryByIdProvider(configId).future);
    return config.copyWith();
  }

  /// Updates the form state on synchronous edits.
  void forceRebuild(ModelConfig updatedConfig) {
    state = AsyncData(updatedConfig);
  }

  Future<void> submit(ModelConfig updatedData) async {
    // Seed AsyncData before AsyncLoading so Riverpod retains unsaved edits if save fails
    state = AsyncData(updatedData);
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final idToSave = updatedData.id.isNotEmpty ? updatedData.id : configId;
      if (idToSave.isEmpty || idToSave == 'new') {
        throw AppException.validation('System Config ID is required');
      }

      final saved = await ref
          .read(modelRegistryControllerProvider.notifier)
          .saveConfig(idToSave, updatedData);
      return saved;
    });
    if (state case AsyncValue(error: final Object error)) {
      throw error;
    }
  }
}
