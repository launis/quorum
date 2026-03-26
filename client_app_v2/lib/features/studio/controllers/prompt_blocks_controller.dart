import 'dart:async';
import 'dart:isolate';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';

// --- Providers ---

/// Manages the state of the Studio Prompt Blocks.
final promptBlocksControllerProvider =
    AsyncNotifierProvider<PromptBlocksController, List<Map<String, dynamic>>>(
      PromptBlocksController.new,
    );

/// Fetches a single Prompt Block natively by ID
final promptBlockByIdProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>, String>((ref, id) async {
      final client = ref.watch(studioClientProvider);
      return client.getPromptBlock(id);
    });

// --- Controllers ---

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class PromptBlocksController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    // SWR Strategy for List Views
    ref.cacheFor(const Duration(minutes: 3));
    return _fetchPromptBlocks();
  }

  Future<List<Map<String, dynamic>>> _fetchPromptBlocks() async {
    final client = ref.read(studioClientProvider);
    final rawData = await client.getPromptBlocks();
    // Using Isolate.run per 2026 Mandate to prevent Main Thread Jank on 120Hz displays
    return await Isolate.run(() => List<Map<String, dynamic>>.from(rawData));
  }

  /// Refreshes the Prompt Blocks list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newBlocks = await _fetchPromptBlocks();
      state = AsyncValue.data(newBlocks);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Saves a Prompt Block config utilizing Optimistic Updates.
  Future<Map<String, dynamic>> savePromptBlock(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;
    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedBlock = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedBlock;
      } else {
        currentList.add(updatedBlock);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedBlock = await client.savePromptBlock(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedBlock;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedBlock;
      }
      return returnData;
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to save Prompt Block: $e');
    }
  }

  /// Clones a Prompt Block, using Optimistic UI appending.
  Future<Map<String, dynamic>> clonePromptBlock(String id) async {
    final previousState = state;

    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final clonedBlock = await client.clonePromptBlock(id);

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.add(clonedBlock);
        state = AsyncValue.data(currentList);
      }
      return clonedBlock;
    } catch (e) {
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to clone Prompt Block: $e');
    }
  }

  /// Deletes a Prompt Block. Throwing AppException on orphan rejection
  Future<void> deletePromptBlock(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deletePromptBlock(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((m) => m['id'] == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to delete Prompt Block: $e');
    }
  }

  /// Simulates rendering of a Prompt Block or Matrix with mock data.
  Future<Map<String, dynamic>> simulatePromptBlock(
    Map<String, dynamic> payload,
  ) async {
    try {
      final client = ref.read(studioClientProvider);
      return await client.simulatePromptBlock(payload);
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to simulate Prompt Block: $e');
    }
  }
}
