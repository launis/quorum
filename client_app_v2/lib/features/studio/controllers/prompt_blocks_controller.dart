import 'dart:async';
import 'dart:convert';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';

import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'prompt_blocks_controller.g.dart';

// --- Providers ---

/// Fetches a single Prompt Block natively by ID
@riverpod
Future<PromptBlock> promptBlockById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  final rawData = await client.getPromptBlock(id);
  final str = jsonEncode(rawData);
  return PromptBlock.parseInBackground(str);
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class PromptBlockForm extends _$PromptBlockForm {
  @override
  FutureOr<PromptBlock> build(String configId) async {
    final block = await ref.watch(promptBlockByIdProvider(configId).future);
    return block.copyWith(); // Deep copy equivalent due to Freezed immutability
  }

  void forceRebuild(PromptBlock block) {
    state = AsyncData(block);
  }

  Future<void> submit(PromptBlock block) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final idToSave = block.id.isEmpty ? configId : block.id;
      if (idToSave.isEmpty || idToSave == 'new') {
        throw AppException.validation("Block ID is required");
      }

      await ref
          .read(promptBlocksControllerProvider.notifier)
          .savePromptBlock(idToSave, block);
      return block;
    });
  }
}

// --- Controllers ---

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class PromptBlocksController extends _$PromptBlocksController {
  @override
  FutureOr<List<PromptBlock>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchPromptBlocks();
  }

  Future<List<PromptBlock>> _fetchPromptBlocks() async {
    final client = ref.read(studioClientProvider);
    final rawData = await client.getPromptBlocks();
    // Using safeIsolateRun per 2026 Mandate to prevent Main Thread Jank on 120Hz displays
    return PromptBlock.parseListInBackground(rawData);
  }

  /// Refreshes the Prompt Blocks list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newBlocks = await _fetchPromptBlocks();
      state = AsyncValue.data(newBlocks);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Refresh failed', e, st);
      state = AsyncValue.error(e, st);
    }
  }

  /// Saves a Prompt Block config utilizing Optimistic Updates.
  Future<PromptBlock> savePromptBlock(String id, PromptBlock block) async {
    final previousState = state;
    PromptBlock returnData = block.copyWith(id: id);

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<PromptBlock>.from(state.value!);
      final index = currentList.indexWhere((m) => m.id == id);

      if (index >= 0) {
        currentList[index] = returnData;
      } else {
        currentList.add(returnData);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.savePromptBlock(id, returnData.toJson());
      final verifiedBlock = await PromptBlock.parseInBackground(
        jsonEncode(rawResponse),
      );

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<PromptBlock>.from(state.value!);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedBlock;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedBlock;
      }
      return returnData;
    } catch (e, st) {
      // 4. Rollback on Failure
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones a Prompt Block, using Optimistic UI appending.
  Future<PromptBlock> clonePromptBlock(String id) async {
    final previousState = state;

    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.clonePromptBlock(id);
      final clonedBlock = await PromptBlock.parseInBackground(
        jsonEncode(rawResponse),
      );

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<PromptBlock>.from(state.value!);
        currentList.insert(0, clonedBlock);
        state = AsyncValue.data(currentList);
      }
      return clonedBlock;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft Prompt Block via the SSoT backend.
  Future<PromptBlock> createPromptBlockDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.createPromptBlockDraft();
      final draftBlock = await PromptBlock.parseInBackground(
        jsonEncode(rawResponse),
      );

      if (state.hasValue && state.value != null) {
        final currentList = List<PromptBlock>.from(state.value!);
        currentList.insert(0, draftBlock);
        state = AsyncValue.data(currentList);
      }
      return draftBlock;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) throw e.error!;
      throw AppException.unknown(e);
    }
  }

  /// Deletes a Prompt Block. Throwing AppException on orphan rejection
  Future<void> deletePromptBlock(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deletePromptBlock(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<PromptBlock>.from(state.value!);
        currentList.removeWhere((m) => m.id == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Simulates rendering of a Prompt Block or Matrix with mock data.
  Future<Map<String, dynamic>> simulatePromptBlock(
    PromptBlock block,
    Map<String, dynamic> mockInputs,
  ) async {
    try {
      final payload = {'block': block.toJson(), 'mock_inputs': mockInputs};
      final client = ref.read(studioClientProvider);
      return await client.simulatePromptBlock(payload);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Simulate failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }
}
