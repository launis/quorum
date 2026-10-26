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

  /// Saves an MCP Gateway configuration utilizing optimistic updates with rollback on failure.
  Future<McpGateway> saveGateway(String id, McpGateway payload) async {
    final previousState = state;
    final returnData = payload.copyWith(id: id);

    if (state case AsyncData(:final value)) {
      final currentList = List<McpGateway>.from(value);
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
      final verifiedGateway = await client.saveMcpGateway(id, returnData);

      if (state case AsyncData(:final value)) {
        final currentList = List<McpGateway>.from(value);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedGateway;
          state = AsyncValue.data(currentList);
        }
      }
      // Invalidate single-gateway provider to prevent stale detail view cache after save
      ref.invalidate(mcpGatewayByIdProvider(id));
      return verifiedGateway;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes an MCP Gateway and propagates AppException on active reference conflicts.
  Future<void> deleteGateway(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteMcpGateway(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<McpGateway>.from(value)
          ..removeWhere((m) => m.id == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones an MCP Gateway and appends the backend-minted copy to state.
  Future<McpGateway> cloneGateway(String id) async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final clonedGateway = await client.cloneMcpGateway(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<McpGateway>.from(value)..add(clonedGateway);
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
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft MCP Gateway via the backend SSOT service.
  Future<McpGateway> createMcpGatewayDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final draftGateway = await client.createMcpGatewayDraft();

      if (state case AsyncData(:final value)) {
        final currentList = List<McpGateway>.from(value)
          ..insert(0, draftGateway);
        state = AsyncValue.data(currentList);
      }
      return draftGateway;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      if (e is AppException) {
        rethrow;
      }
      throw AppException.unknown(e);
    }
  }

  /// Connects to the external MCP server to discover tools and synchronize schemas.
  Future<McpGateway> discoverTools(String id) async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final discoveredGateway = await client.discoverMcpGatewayTools(id);

      if (state case AsyncData(:final value)) {
        final currentList = List<McpGateway>.from(value);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = discoveredGateway;
        } else {
          currentList.add(discoveredGateway);
        }
        state = AsyncValue.data(currentList);
      }
      ref.invalidate(mcpGatewayByIdProvider(id));
      return discoveredGateway;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('McpGatewaysController', 'Discover tools failed', e, st);
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

/// Fetches a single MCP Gateway natively by ID.
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

  /// Appends a default tool entry to the local form state.
  void addTool() {
    if (state case AsyncValue(value: final payload?)) {
      final tools = List<AllowedMcpTool>.from(payload.tools)
        ..add(
          const AllowedMcpTool(
            toolId: 'new_tool',
            name: I18nText(translations: {'en': 'New Tool'}),
            description: '',
            inputSchema: McpToolInputSchemaDto(),
          ),
        );

      state = AsyncData(payload.copyWith(tools: tools));
    }
  }

  void removeTool(int index) {
    if (state case AsyncValue(value: final payload?)) {
      final tools = List<AllowedMcpTool>.from(payload.tools);
      if (index >= 0 && index < tools.length) {
        tools.removeAt(index);
        state = AsyncData(payload.copyWith(tools: tools));
      }
    }
  }

  void forceRebuild(McpGateway gateway) {
    state = AsyncData(gateway);
  }

  Future<void> submit(McpGateway updatedData) async {
    // Seed AsyncData before AsyncLoading so Riverpod retains unsaved edits if save fails
    state = AsyncData(updatedData);
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final idToSave = updatedData.id.isNotEmpty ? updatedData.id : gatewayId;
      if (idToSave.isEmpty) {
        throw AppException.validation('Gateway ID is required.');
      }
      final saved = await ref
          .read(mcpGatewaysControllerProvider.notifier)
          .saveGateway(idToSave, updatedData);
      return saved;
    });
    if (state case AsyncValue(error: final Object error)) {
      throw error;
    }
  }

  /// Saves current connection parameters and triggers live MCP tool discovery.
  Future<void> discoverTools([McpGateway? updatedData]) async {
    final currentPayload = switch (updatedData) {
      final McpGateway data => data,
      null => switch (state) {
        AsyncValue(value: final payload?) => payload,
        _ => null,
      },
    };
    if (currentPayload == null) {
      throw AppException.validation(
        'Cannot discover tools on uninitialized gateway.',
      );
    }

    // Seed AsyncData before AsyncLoading so Riverpod retains unsaved edits if discovery fails
    state = AsyncData(currentPayload);
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final idToDiscover = currentPayload.id.isNotEmpty
          ? currentPayload.id
          : gatewayId;
      if (idToDiscover.isEmpty) {
        throw AppException.validation('Gateway ID is required.');
      }
      final controller = ref.read(mcpGatewaysControllerProvider.notifier);
      await controller.saveGateway(idToDiscover, currentPayload);
      final discovered = await controller.discoverTools(idToDiscover);
      return discovered;
    });
    if (state case AsyncValue(error: final Object error)) {
      throw error;
    }
  }
}
