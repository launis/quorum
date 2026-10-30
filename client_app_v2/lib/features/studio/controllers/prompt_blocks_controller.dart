import 'dart:async';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';

import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'prompt_blocks_controller.g.dart';

// --- Providers ---

/// Fetches a single Prompt Block natively by ID.
@riverpod
Future<PromptBlock> promptBlockById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return await client.getPromptBlock(id);
}

// --- Form State (Flat MVC) ---

@riverpod
class PromptBlockForm extends _$PromptBlockForm {
  @override
  FutureOr<PromptBlock> build(String configId) async {
    final block = await ref.watch(promptBlockByIdProvider(configId).future);
    return block.copyWith();
  }

  void forceRebuild(PromptBlock block) {
    state = AsyncData(block);
  }

  Future<void> submit(PromptBlock block) async {
    // Seed AsyncData before AsyncLoading so Riverpod retains unsaved edits if save fails
    state = AsyncData(block);
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final idToSave = block.id.isEmpty ? configId : block.id;
      if (idToSave.isEmpty || idToSave == 'new') {
        throw AppException.validation('Block ID is required');
      }

      final saved = await ref
          .read(promptBlocksControllerProvider.notifier)
          .savePromptBlock(idToSave, block);
      return saved;
    });
    if (state case AsyncValue(error: final Object error)) {
      throw error;
    }
  }
}

// --- Controllers ---

/// Controller managing Prompt Blocks strictly using strongly typed [PromptBlock] models.
/// Implements optimistic UI updates with automatic state rollback on failure.
@riverpod
class PromptBlocksController extends _$PromptBlocksController {
  @override
  FutureOr<List<PromptBlock>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchPromptBlocks();
  }

  Future<List<PromptBlock>> _fetchPromptBlocks() async {
    final client = ref.read(studioClientProvider);
    return await client.getPromptBlocks();
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

  /// Saves a Prompt Block configuration utilizing optimistic updates with rollback on failure.
  Future<PromptBlock> savePromptBlock(String id, PromptBlock block) async {
    final previousState = state;
    final returnData = block.copyWith(id: id);

    if (state case AsyncData(:final value)) {
      final currentList = List<PromptBlock>.from(value);
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
      final verifiedBlock = await client.savePromptBlock(id, returnData);

      if (state case AsyncData(:final value)) {
        final currentList = List<PromptBlock>.from(value);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedBlock;
          state = AsyncValue.data(currentList);
        }
      }
      ref.invalidate(promptBlockByIdProvider(id));
      return verifiedBlock;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones a Prompt Block and prepends the backend-minted copy to state.
  Future<PromptBlock> clonePromptBlock(String id) async {
    final previousState = state;

    try {
      final client = ref.read(studioClientProvider);
      final clonedBlock = await client.clonePromptBlock(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<PromptBlock>.from(value)
          ..insert(0, clonedBlock);
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
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft Prompt Block via the SSOT backend.
  Future<PromptBlock> createPromptBlockDraft({String? categoryId}) async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final draftBlock = await client.createPromptBlockDraft(
        categoryId: categoryId,
      );

      if (state case AsyncData(:final value)) {
        final currentList = List<PromptBlock>.from(value)
          ..insert(0, draftBlock);
        state = AsyncValue.data(currentList);
      }
      return draftBlock;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes a Prompt Block and propagates AppException on active reference conflicts.
  Future<void> deletePromptBlock(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deletePromptBlock(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<PromptBlock>.from(value)
          ..removeWhere((m) => m.id == id);
        state = AsyncValue.data(currentList);
      }
      ref.invalidate(promptBlockByIdProvider(id));
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Simulates rendering of a Prompt Block or Matrix with mock data.
  Future<PromptBlockSimulationResponse> simulatePromptBlock(
    PromptBlock block,
    Map<String, Object?> mockInputs, {
    int? targetScaleScore,
    String? targetLocale,
    String? contextText,
  }) async {
    try {
      final resolvedLocale =
          (targetLocale == null || targetLocale.trim().isEmpty)
          ? 'en'
          : targetLocale.trim();
      final resolvedContext =
          (contextText == null || contextText.trim().isEmpty)
          ? '[SIMULATED CONTEXT DOCUMENT]'
          : contextText.trim();
      final request = PromptBlockSimulationRequest(
        block: block,
        mockInputs: mockInputs,
        targetScaleScore: targetScaleScore,
        targetLocale: resolvedLocale,
        contextText: resolvedContext,
      );
      final client = ref.read(studioClientProvider);
      return await client.simulatePromptBlock(request);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('PromptBlocksController', 'Simulate failed', e, st);
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
