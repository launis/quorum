import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';

// --- Providers ---

/// Manages the state of the Studio MCP Gateways.
final mcpGatewaysControllerProvider =
    AsyncNotifierProvider<McpGatewaysController, List<Map<String, dynamic>>>(
      McpGatewaysController.new,
    );

/// Fetches a single MCP Gateway natively by ID
final mcpGatewayByIdProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>, String>((ref, id) async {
      final client = ref.watch(studioClientProvider);
      return client.getMcpGateway(id);
    });

// --- Controllers ---

/// Controller managing the MCP Gateways strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
class McpGatewaysController extends AsyncNotifier<List<Map<String, dynamic>>> {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    // SWR Strategy for List Views
    ref.cacheFor(const Duration(minutes: 3));
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
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
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
    } catch (e) {
      // 4. Rollback on Failure
      state = previousState;
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to save MCP Gateway: $e');
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
    } catch (e) {
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw Exception('Failed to delete MCP Gateway: $e');
    }
  }
}
