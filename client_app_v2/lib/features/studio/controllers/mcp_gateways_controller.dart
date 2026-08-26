import 'package:client_app/core/utils/safe_isolate.dart';
import 'dart:async';
import 'dart:convert';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'mcp_gateways_controller.g.dart';

// --- Controllers ---

/// Controller managing the MCP Gateways strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
@riverpod
class McpGatewaysController extends _$McpGatewaysController {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    // SWR Strategy for List Views
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchGateways();
  }

  Future<List<Map<String, dynamic>>> _fetchGateways() async {
    final client = ref.read(studioClientProvider);
    return client.getMcpGateways();
  }

  /// Refreshes the MCP Gateways list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newGateways = await _fetchGateways();
      state = AsyncValue.data(newGateways);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Refresh failed', e, st);
      state = AsyncValue.error(e, st);
    }
  }

  /// Saves an MCP Gateway config utilizing Optimistic Updates.
  Future<Map<String, dynamic>> saveGateway(
    String id,
    Map<String, dynamic> payload,
  ) async {
    final previousState = state;
    Map<String, dynamic> returnData = {...payload, 'id': id};

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<Map<String, dynamic>>.from(state.value!);
      final index = currentList.indexWhere((m) => m['id'] == id);

      final updatedGateway = {...payload, 'id': id};
      if (index >= 0) {
        currentList[index] = updatedGateway;
      } else {
        currentList.add(updatedGateway);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedGateway = await client.saveMcpGateway(id, payload);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        final index = currentList.indexWhere((m) => m['id'] == id);
        if (index >= 0) {
          currentList[index] = verifiedGateway;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedGateway;
      }
      return returnData;
    } catch (e, st) {
      // 4. Rollback on Failure
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes an MCP Gateway. Throwing AppException on orphan rejection
  Future<void> deleteGateway(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteMcpGateway(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.removeWhere((m) => m['id'] == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones an MCP Gateway utilizing Optimistic UI.
  Future<Map<String, dynamic>> cloneGateway(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final clonedGateway = await client.cloneMcpGateway(id);

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.add(clonedGateway);
        state = AsyncValue.data(currentList);
      }
      return clonedGateway;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft MCP Gateway via the SSoT backend.
  Future<Map<String, dynamic>> createMcpGatewayDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final draftGateway = await client.createMcpGatewayDraft();

      if (state.hasValue && state.value != null) {
        final currentList = List<Map<String, dynamic>>.from(state.value!);
        currentList.insert(0, draftGateway);
        state = AsyncValue.data(currentList);
      }
      return draftGateway;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) throw e.error!;
      throw AppException.unknown(e);
    }
  }
}

/// Fetches a single MCP Gateway natively by ID
@riverpod
Future<Map<String, dynamic>> mcpGatewayById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return client.getMcpGateway(id);
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class McpGatewayForm extends _$McpGatewayForm {
  @override
  FutureOr<Map<String, dynamic>> build(String gatewayId) async {
    // 1. Fetch raw data
    final rawData = await ref.watch(mcpGatewayByIdProvider(gatewayId).future);

    // 2. ISOLATE MANDATE: Deep Copy / Parse in Isolate protecting Main Thread
    final str = jsonEncode(rawData);
    return safeIsolateRun(() => jsonDecode(str) as Map<String, dynamic>);
  }

  /// Synchronous local state mutations for the form
  void addTool() {
    final payload = state.value;
    if (payload == null) return;

    final tools = List<Map<String, dynamic>>.from(payload['tools'] ?? []);
    tools.add({
      'tool_id': 'new_tool',
      'name': {
        'translations': {'en': 'New Tool', 'fi': 'Uusi työkalu'},
      },
      'description': '',
      'input_schema': <String, dynamic>{},
    });

    payload['tools'] = tools;
    state = AsyncData(Map<String, dynamic>.from(payload)); // Force rebuild
  }

  void removeTool(int index) {
    final payload = state.value;
    if (payload == null) return;

    final tools = List<Map<String, dynamic>>.from(payload['tools'] ?? []);
    if (index >= 0 && index < tools.length) {
      tools.removeAt(index);
      payload['tools'] = tools;
      state = AsyncData(Map<String, dynamic>.from(payload));
    }
  }

  void forceRebuild() {
    final payload = state.value;
    if (payload != null) {
      state = AsyncData(Map<String, dynamic>.from(payload));
    }
  }

  Future<void> submit(Map<String, dynamic> updatedData) async {
    state = const AsyncLoading(); // Side effect isolation

    state = await AsyncValue.guard(() async {
      final idToSave = updatedData['id'] ?? gatewayId;
      await ref
          .read(mcpGatewaysControllerProvider.notifier)
          .saveGateway(idToSave, updatedData);
      return updatedData; // Optimistic form state return
    });
  }
}
