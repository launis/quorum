import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'output_profile_controller.g.dart';

// --- Controllers ---

/// Controller managing Studio Output Profiles strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class OutputProfilesController extends _$OutputProfilesController {
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

  /// Clones an Output Profile utilizing Optimistic UI.
  Future<Map<String, dynamic>> cloneProfile(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final clonedProfile = await client.cloneOutputProfile(id);

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.insert(0, clonedProfile); // prepend for visibility
        state = AsyncValue.data(currentList);
      }
      return clonedProfile;
    } catch (e) {
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to clone output profile: $e');
    }
  }
}

/// Fetches a single Output Profile natively by ID
@riverpod
Future<Map<String, dynamic>> outputProfileById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return client.getOutputProfile(id);
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class OutputProfileForm extends _$OutputProfileForm {
  @override
  FutureOr<Map<String, dynamic>> build(String configId) async {
    if (configId == 'new') {
      return Isolate.run(() => {
        'id': '',
        'name': {'fi': 'Uusi profiili', 'en': 'New Profile'},
        'layouts': <dynamic>[],
        'workflow_id': '',
      });
    }

    final rawData = await ref.watch(outputProfileByIdProvider(configId).future);
    final str = jsonEncode(rawData);
    return Isolate.run(() => jsonDecode(str) as Map<String, dynamic>);
  }

  void forceRebuild() {
    final payload = state.value;
    if (payload != null) {
      state = AsyncData(Map<String, dynamic>.from(payload));
    }
  }

  Future<void> submit(Map<String, dynamic> updatedData) async {
    state = const AsyncLoading();
    
    state = await AsyncValue.guard(() async {
      final idToSave = updatedData['id'] as String? ?? configId;
      if (idToSave.isEmpty || idToSave == 'new') throw Exception("Profile ID is required");

      await ref.read(outputProfilesControllerProvider.notifier).saveProfile(idToSave, updatedData);
      return updatedData;
    });
  }
}
