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

  /// Retrieves a specific prompt block by id.
  Future<Map<String, dynamic>> getPromptBlock(String id) async {
    final response = await _dio.get('studio/prompt-blocks/$id');
    return response.data as Map<String, dynamic>;
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

  /// Dry-runs a prompt block or matrix rendering with mock variables.
  Future<Map<String, dynamic>> simulatePromptBlock(
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.post(
      'studio/prompt-blocks/simulate',
      data: data,
    );
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a prompt block.
  Future<void> deletePromptBlock(String id) async {
    await _dio.delete('studio/prompt-blocks/$id');
  }

  /// Deep clones a prompt block securely via SSOT Service Layer.
  Future<Map<String, dynamic>> clonePromptBlock(String id) async {
    final response = await _dio.post('studio/prompt-blocks/$id/clone');
    return response.data as Map<String, dynamic>;
  }

  // --- Workflows (DAG definitions) ---

  /// Retrieves all workflow definitions.
  Future<List<Map<String, dynamic>>> getWorkflows() async {
    final response = await _dio.get('studio/workflows');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Retrieves a specific workflow definition by id.
  Future<Map<String, dynamic>> getWorkflow(String id) async {
    final response = await _dio.get('studio/workflows/$id');
    return response.data as Map<String, dynamic>;
  }

  /// Appends or updates a workflow definition.
  Future<Map<String, dynamic>> saveWorkflow(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/workflows/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Validates a workflow definition using the Pre-Flight Simulator API.
  Future<Map<String, dynamic>> simulateWorkflow(
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.post('studio/workflows/simulate', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a workflow definition.
  Future<void> deleteWorkflow(String id) async {
    await _dio.delete('studio/workflows/$id');
  }

  /// Deep clones a workflow definition securely via SSOT Service Layer.
  Future<Map<String, dynamic>> cloneWorkflow(String id) async {
    final response = await _dio.post('studio/workflows/$id/clone');
    return response.data as Map<String, dynamic>;
  }

  // --- Steps ---

  /// Retrieves all steps.
  Future<List<Map<String, dynamic>>> getSteps() async {
    final response = await _dio.get('studio/steps');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Appends or updates a step.
  Future<Map<String, dynamic>> saveStep(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/steps/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a step.
  Future<void> deleteStep(String id) async {
    await _dio.delete('studio/steps/$id');
  }

  /// Validates a step definition using the Pre-Flight Simulator API.
  Future<Map<String, dynamic>> simulateStep(Map<String, dynamic> data) async {
    final response = await _dio.post('studio/steps/simulate', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deep clones a step securely.
  Future<Map<String, dynamic>> cloneStep(String id) async {
    final response = await _dio.post('studio/steps/$id/clone');
    return response.data as Map<String, dynamic>;
  }
  // --- Model Registry ---

  /// Retrieves available models.
  Future<List<String>> getAvailableModels() async {
    final response = await _dio.get('studio/model-registry/available-models');
    return List<String>.from(response.data as List);
  }

  /// Retrieves all system configs (Model Registries).
  Future<List<Map<String, dynamic>>> getSystemConfigs() async {
    final response = await _dio.get('studio/model-registry/');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Retrieves a system config by ID.
  Future<Map<String, dynamic>> getSystemConfig(String id) async {
    final response = await _dio.get('studio/model-registry/$id');
    return response.data as Map<String, dynamic>;
  }

  /// Updates a system config.
  Future<Map<String, dynamic>> saveSystemConfig(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/model-registry/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes a system config.
  Future<void> deleteSystemConfig(String id) async {
    await _dio.delete('studio/model-registry/$id');
  }

  /// Deep clones a system config.
  Future<Map<String, dynamic>> cloneSystemConfig(String id) async {
    final response = await _dio.post('studio/model-registry/$id/clone');
    return response.data as Map<String, dynamic>;
  }

  // --- MCP Gateways ---

  /// Retrieves all MCP Gateways.
  Future<List<Map<String, dynamic>>> getMcpGateways() async {
    final response = await _dio.get('studio/mcp-gateways/');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Retrieves a specific MCP Gateway by ID.
  Future<Map<String, dynamic>> getMcpGateway(String id) async {
    final response = await _dio.get('studio/mcp-gateways/$id');
    return response.data as Map<String, dynamic>;
  }

  /// Appends or updates an MCP Gateway.
  Future<Map<String, dynamic>> saveMcpGateway(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('studio/mcp-gateways/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes an MCP Gateway.
  Future<void> deleteMcpGateway(String id) async {
    await _dio.delete('studio/mcp-gateways/$id');
  }

  /// Deep clones an MCP Gateway.
  Future<Map<String, dynamic>> cloneMcpGateway(String id) async {
    final response = await _dio.post('studio/mcp-gateways/$id/clone');
    return response.data as Map<String, dynamic>;
  }

  // --- Output Profiles ---

  /// Retrieves all output profiles.
  Future<List<Map<String, dynamic>>> getOutputProfiles() async {
    final response = await _dio.get('output-profiles/');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  /// Appends or updates an output profile.
  Future<Map<String, dynamic>> saveOutputProfile(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('output-profiles/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Deletes an output profile.
  Future<void> deleteOutputProfile(String id) async {
    await _dio.delete('output-profiles/$id');
  }

  /// Deep clones an output profile.
  Future<Map<String, dynamic>> cloneOutputProfile(String id) async {
    final response = await _dio.post('output-profiles/$id/clone');
    return response.data as Map<String, dynamic>;
  }
}
