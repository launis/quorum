import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'model_registry_controller.g.dart';

// --- Controllers ---

/// Controller managing the Model Registry strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class ModelRegistryController extends _$ModelRegistryController {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    // SWR Strategy for List Views
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchConfigs();
  }

  Future<List<Map<String, dynamic>>> _fetchConfigs() async {
    final client = ref.read(studioClientProvider);
    return client.getSystemConfigs();
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
  Future<Map<String, dynamic>> saveConfig(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;
    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedConfig = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedConfig;
      } else {
        currentList.add(updatedConfig);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedConfig = await client.saveSystemConfig(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
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
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((m) => m['id'] == id);
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
  Future<Map<String, dynamic>> cloneConfig(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final clonedConfig = await client.cloneSystemConfig(id);

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
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
Future<Map<String, dynamic>> modelRegistryById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return client.getSystemConfig(id);
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
  FutureOr<Map<String, dynamic>> build(String configId) async {
    if (configId == 'new') {
      return Isolate.run(
        () => {
          'id': 'syscfg_new',
          'type': 'model_registry',
          'models': <String, dynamic>{}, // Map<String, Map<String, dynamic>>
        },
      );
    }

    // 1. Fetch raw data
    final rawData = await ref.watch(modelRegistryByIdProvider(configId).future);

    // 2. ISOLATE MANDATE: Deep Copy / Parse in Isolate protecting Main Thread
    final str = jsonEncode(rawData);
    return Isolate.run(() => jsonDecode(str) as Map<String, dynamic>);
  }

  /// Used by the form to trigger a rebuild on synchronous memory edits if required.
  void forceRebuild() {
    final payload = state.value;
    if (payload != null) {
      state = AsyncData(Map<String, dynamic>.from(payload));
    }
  }

  Future<void> submit(Map<String, dynamic> updatedData) async {
    state = const AsyncLoading(); // Side effect isolation

    state = await AsyncValue.guard(() async {
      final idToSave =
          configId == 'new' ? (updatedData['id'] ?? 'syscfg_new') : configId;
      await ref
          .read(modelRegistryControllerProvider.notifier)
          .saveConfig(idToSave, updatedData);
      return updatedData; // Optimistic form state return
    });
  }
}
