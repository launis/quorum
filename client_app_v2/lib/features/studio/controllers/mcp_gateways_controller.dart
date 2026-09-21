import 'dart:async';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'mcp_gateways_controller.g.dart';

// --- Controllers ---

/// Controller managing the MCP Gateways strictly using immutable Freezed models.
/// Implements Optimistic UI principles where possible.
@riverpod
class McpGatewaysController extends _$McpGatewaysController {
  @override
  FutureOr<List<McpGateway>> build() async {
    // SWR Strategy for List Views
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchGateways();
  }

  Future<List<McpGateway>> _fetchGateways() async {
    final client = ref.read(studioClientProvider);
    return await client.getMcpGateways();
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
  Future<McpGateway> saveGateway(String id, McpGateway payload) async {
    final previousState = state;
    final returnData = payload.copyWith(id: id);

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<McpGateway>.from(state.value!);
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
      final verifiedGateway = await client.saveMcpGateway(id, returnData);

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<McpGateway>.from(state.value!);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedGateway;
          state = AsyncValue.data(currentList);
        }
      }
      return verifiedGateway;
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
        final currentList = List<McpGateway>.from(state.value!);
        currentList.removeWhere((m) => m.id == id);
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
  Future<McpGateway> cloneGateway(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final clonedGateway = await client.cloneMcpGateway(id);

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<McpGateway>.from(state.value!);
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
  Future<McpGateway> createMcpGatewayDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final draftGateway = await client.createMcpGatewayDraft();

      if (state.hasValue && state.value != null) {
        final currentList = List<McpGateway>.from(state.value!);
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
Future<McpGateway> mcpGatewayById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return await client.getMcpGateway(id);
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class McpGatewayForm extends _$McpGatewayForm {
  @override
  FutureOr<McpGateway> build(String gatewayId) async {
    return ref.watch(mcpGatewayByIdProvider(gatewayId).future);
  }

  /// Synchronous local state mutations for the form
  void addTool() {
    final payload = state.value;
    if (payload == null) return;

    final tools = List<AllowedMcpTool>.from(payload.tools);
    tools.add(
      const AllowedMcpTool(
        toolId: 'new_tool',
        name: I18nText(translations: {'en': 'New Tool', 'fi': 'Uusi työkalu'}),
        description: '',
        inputSchema: <String, dynamic>{},
      ),
    );

    state = AsyncData(payload.copyWith(tools: tools));
  }

  void removeTool(int index) {
    final payload = state.value;
    if (payload == null) return;

    final tools = List<AllowedMcpTool>.from(payload.tools);
    if (index >= 0 && index < tools.length) {
      tools.removeAt(index);
      state = AsyncData(payload.copyWith(tools: tools));
    }
  }

  void forceRebuild(McpGateway gateway) {
    state = AsyncData(gateway);
  }

  Future<void> submit(McpGateway updatedData) async {
    state = const AsyncLoading(); // Side effect isolation

    state = await AsyncValue.guard(() async {
      final idToSave = updatedData.id.isNotEmpty ? updatedData.id : gatewayId;
      await ref
          .read(mcpGatewaysControllerProvider.notifier)
          .saveGateway(idToSave, updatedData);
      return updatedData; // Optimistic form state return
    });
  }
}
