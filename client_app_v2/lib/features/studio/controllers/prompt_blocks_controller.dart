import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'prompt_blocks_controller.g.dart';

// --- Providers ---

/// Fetches a single Prompt Block natively by ID
@riverpod
Future<Map<String, dynamic>> promptBlockById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return client.getPromptBlock(id);
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class PromptBlockForm extends _$PromptBlockForm {
  @override
  FutureOr<Map<String, dynamic>> build(String configId) async {
    if (configId == 'new') {
      return Isolate.run(() => {
        'id': '',
        'slug': '',
        'category_id': 'system', // Default fallback category
        'label': {
          'default_locale': 'en',
          'translations': <String, dynamic>{'en': 'New Prompt Block', 'fi': 'Uusi Promptilohko'},
        },
        'description': {
          'default_locale': 'en',
          'translations': <String, dynamic>{'en': '', 'fi': ''},
        },
        'system_instructions': '',
        'json_schema': null,
      });
    }

    final rawData = await ref.watch(promptBlockByIdProvider(configId).future);
    final str = jsonEncode(rawData);
    var copy = await Isolate.run(() => jsonDecode(str) as Map<String, dynamic>);
    
    // "The English-Only Mandate": Ensure new blocks have required 'en' structure
    if (!copy.containsKey('label')) {
      copy['label'] = {
        'default_locale': 'en',
        'translations': <String, dynamic>{'en': ''},
      };
    }
    if (!copy.containsKey('description')) {
      copy['description'] = {
        'default_locale': 'en',
        'translations': <String, dynamic>{'en': ''},
      };
    }
    
    return copy;
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
      if (idToSave.isEmpty || idToSave == 'new') throw Exception("Block ID is required");

      await ref.read(promptBlocksControllerProvider.notifier).savePromptBlock(idToSave, updatedData);
      return updatedData;
    });
  }
}

// --- Controllers ---

/// Controller managing the Prompt Blocks strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class PromptBlocksController extends _$PromptBlocksController {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
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
        currentList.insert(0, clonedBlock);
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
