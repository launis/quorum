import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/network/api_client.dart';

/// Studio API Client Provider
final studioClientProvider = Provider<StudioClient>((ref) {
  return StudioClient(ref.watch(apiClientProvider));
});

/// Client for interacting with the V2 Studio API (Admin/Config features).
///
/// Strictly adheres to V2 De-Generator policy. All data in and out
/// are pure `Map<String, dynamic>` representations.
class StudioClient {
  final Dio _dio;

  StudioClient(this._dio);

  // --- Matrices (Criteria & Scoring) ---

  /// Retrieves all evaluation prompt blocks.
  Future<List<Map<String, dynamic>>> getPromptBlocks() async {
    final response = await _dio.get('studio/prompt-blocks');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Appends or updates a prompt block.
  /// In V2, blocks are append-only. This typically returns a new version ID.
  Future<Map<String, dynamic>> savePromptBlock(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/prompt-blocks/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a prompt block.
  Future<void> deletePromptBlock(String id) async {
    await _dio.delete('studio/prompt-blocks/$id');
  }

  // --- Workflows (DAG definitions) ---

  /// Retrieves all workflow definitions.
  Future<List<Map<String, dynamic>>> getWorkflows() async {
    final response = await _dio.get('studio/workflows');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Appends or updates a workflow definition.
  Future<Map<String, dynamic>> saveWorkflow(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/workflows/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a workflow definition.
  Future<void> deleteWorkflow(String id) async {
    await _dio.delete('studio/workflows/$id');
  }

  // --- Task Blueprints (Independent steps) ---

  /// Retrieves all task blueprints.
  Future<List<Map<String, dynamic>>> getTaskBlueprints() async {
    final response = await _dio.get('studio/task-blueprints');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Appends or updates a task blueprint.
  Future<Map<String, dynamic>> saveTaskBlueprint(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/task-blueprints/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a task blueprint.
  Future<void> deleteTaskBlueprint(String id) async {
    await _dio.delete('studio/task-blueprints/$id');
  }

  // --- System Configs (e.g., model_registry) ---

  /// Retrieves a system config by ID.
  Future<Map<String, dynamic>> getSystemConfig(String id) async {
    final response = await _dio.get('studio/system-configs/$id');
    return response.data as Map<String, dynamic>;
  }

  /// Updates a system config.
  Future<Map<String, dynamic>> saveSystemConfig(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/system-configs/$id', data: data);
    return response.data as Map<String, dynamic>;
  }
}
