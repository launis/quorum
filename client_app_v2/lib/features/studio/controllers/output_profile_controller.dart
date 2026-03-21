import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';

// --- Providers ---

/// Manages the state of all Studio Output Profiles.
final outputProfilesControllerProvider =
    AsyncNotifierProvider<OutputProfilesController, List<Map<String, dynamic>>>(
      OutputProfilesController.new,
    );

// --- Controllers ---

/// Controller managing Studio Output Profiles strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class OutputProfilesController
    extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    ref.cacheFor(const Duration(minutes: 3));
    return _fetchProfiles();
  }

  Future<List<Map<String, dynamic>>> _fetchProfiles() async {
    final client = ref.read(studioClientProvider);
    return client.getOutputProfiles();
  }

  /// Refreshes the profiles list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newProfiles = await _fetchProfiles();
      state = AsyncValue.data(newProfiles);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Saves a profile utilizing Optimistic Updates.
  Future<Map<String, dynamic>> saveProfile(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;
    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedProfile = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedProfile;
      } else {
        currentList.add(updatedProfile);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedProfile = await client.saveOutputProfile(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedProfile;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedProfile;
      }
      return returnData;
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to save output profile: $e');
    }
  }

  /// Deletes a profile.
  Future<void> deleteProfile(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteOutputProfile(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((m) => m['id'] == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to delete output profile: $e');
    }
  }
}
