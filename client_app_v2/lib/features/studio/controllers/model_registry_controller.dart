import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';

// --- Providers ---

/// Manages the state of the Studio Model Registry Config.
final modelRegistryControllerProvider =
    AsyncNotifierProvider<ModelRegistryController, Map<String, dynamic>>(
      ModelRegistryController.new,
    );

// --- Controllers ---

/// Controller managing the Model Registry strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class ModelRegistryController extends AsyncNotifier<Map<String, dynamic>> {
  static const String _configId = 'model_registry';

  @override
  FutureOr<Map<String, dynamic>> build() async {
    return _fetchConfig();
  }

  Future<Map<String, dynamic>> _fetchConfig() async {
    final client = ref.read(studioClientProvider);
    return client.getSystemConfig(_configId);
  }

  /// Refreshes the model registry config from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newConfig = await _fetchConfig();
      state = AsyncValue.data(newConfig);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Saves the model registry config utilizing Optimistic Updates.
  Future<void> saveConfig(Map<String, dynamic> payload) async {
    final previousState = state;

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final updatedConfig = {...state.value!, ...payload, 'id': _configId};
      state = AsyncValue.data(updatedConfig);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedConfig = await client.saveSystemConfig(_configId, payload);

      // 3. Confirm with Actual Data
      state = AsyncValue.data(verifiedConfig);
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      // Re-throw to allow view layer to show snackbar
      throw Exception('Failed to save model registry config: $e');
    }
  }
}
