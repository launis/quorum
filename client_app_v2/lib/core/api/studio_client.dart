import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:client_app/features/studio/models/gcp_location.dart';
import 'package:client_app/features/studio/models/llm_platform.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/prompt_block_simulation.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/workflow_simulation.dart';

part 'studio_client.g.dart';

/// Studio API Client Provider
@Riverpod(keepAlive: true)
StudioClient studioClient(Ref ref) {
  return StudioClient(ref.watch(apiClientProvider));
}

/// Client for interacting with the V2 Studio API (Admin/Config features).
class StudioClient {
  final Dio _dio;

  StudioClient(this._dio);

  // --- Matrices (Criteria & Scoring) ---

  /// Retrieves all evaluation prompt blocks.
  Future<List<PromptBlock>> getPromptBlocks() async {
    final response = await _dio.get('studio/prompt-blocks');
    final rawList = response.data as List;
    return rawList
        .map((item) => PromptBlock.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves a specific prompt block by id.
  Future<PromptBlock> getPromptBlock(String id) async {
    final response = await _dio.get('studio/prompt-blocks/$id');
    return PromptBlock.fromJson(response.data as Map<String, dynamic>);
  }

  /// Appends or updates a prompt block.
  /// In V2, blocks are append-only. This typically returns a new version ID.
  Future<PromptBlock> savePromptBlock(String id, PromptBlock data) async {
    final response = await _dio.put(
      'studio/prompt-blocks/$id',
      data: data.toJson(),
    );
    return PromptBlock.fromJson(response.data as Map<String, dynamic>);
  }

  /// Dry-runs a prompt block or matrix rendering with mock variables.
  Future<PromptBlockSimulationResponse> simulatePromptBlock(
    PromptBlockSimulationRequest request,
  ) async {
    if (request.block.id.isEmpty) {
      throw AppException.validation('PromptBlock ID is required');
    }
    final response = await _dio.post(
      'studio/prompt-blocks/simulate',
      data: request.toJson(),
    );
    return PromptBlockSimulationResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  /// Deletes a prompt block.
  Future<void> deletePromptBlock(String id) async {
    await _dio.delete('studio/prompt-blocks/$id');
  }

  /// Deep clones a prompt block securely via SSOT Service Layer.
  Future<PromptBlock> clonePromptBlock(String id) async {
    final response = await _dio.post('studio/prompt-blocks/$id/clone');
    return PromptBlock.fromJson(response.data as Map<String, dynamic>);
  }

  /// Creates a draft prompt block securely via SSOT Service Layer.
  Future<PromptBlock> createPromptBlockDraft() async {
    final response = await _dio.post('studio/prompt-blocks/');
    return PromptBlock.fromJson(response.data as Map<String, dynamic>);
  }

  // --- Workflows (DAG definitions) ---

  /// Retrieves all workflow definitions.
  Future<List<Workflow>> getWorkflows() async {
    final response = await _dio.get('studio/workflows');
    final rawList = response.data as List;
    return rawList
        .map((item) => Workflow.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves a specific workflow definition by id.
  Future<Workflow> getWorkflow(String id) async {
    final response = await _dio.get('studio/workflows/$id');
    return Workflow.fromJson(response.data as Map<String, dynamic>);
  }

  /// Appends or updates a workflow definition.
  Future<Workflow> saveWorkflow(String id, Workflow data) async {
    final payload = data.toJson();
    payload.remove('output_profiles');
    final response = await _dio.put('studio/workflows/$id', data: payload);
    return Workflow.fromJson(response.data as Map<String, dynamic>);
  }

  /// Validates a workflow definition using the Pre-Flight Simulator API.
  Future<WorkflowSimulationResponse> simulateWorkflow(Workflow data) async {
    final response = await _dio.post(
      'studio/workflows/simulate',
      data: data.toJson(),
    );
    return WorkflowSimulationResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  /// Deletes a workflow definition.
  Future<void> deleteWorkflow(String id) async {
    await _dio.delete('studio/workflows/$id');
  }

  /// Deep clones a workflow definition securely via SSOT Service Layer.
  Future<Workflow> cloneWorkflow(String id) async {
    final response = await _dio.post('studio/workflows/$id/clone');
    return Workflow.fromJson(response.data as Map<String, dynamic>);
  }

  /// Creates a draft workflow definition securely via SSOT Service Layer.
  Future<Workflow> createWorkflowDraft() async {
    final response = await _dio.post('studio/workflows/');
    return Workflow.fromJson(response.data as Map<String, dynamic>);
  }

  /// Retrieves available block-level extensions for a workflow.
  Future<List<String>> getWorkflowAvailableExtensions(String id) async {
    final response = await _dio.get(
      'studio/workflows/$id/available-extensions',
    );
    final data = response.data as Map<String, dynamic>;
    final rawList = data['available_extensions'] as List;
    return rawList.map((e) => e.toString()).toList(growable: false);
  }

  // --- Steps ---

  /// Retrieves all steps.
  Future<List<NodeStrategy>> getSteps() async {
    final response = await _dio.get('studio/steps');
    final rawList = response.data as List;
    return rawList
        .map((item) => NodeStrategy.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves a specific step by id.
  Future<NodeStrategy> getStep(String id) async {
    final response = await _dio.get('studio/steps/$id');
    return NodeStrategy.fromJson(response.data as Map<String, dynamic>);
  }

  /// Appends or updates a step.
  Future<NodeStrategy> saveStep(String id, NodeStrategy data) async {
    final response = await _dio.put('studio/steps/$id', data: data.toJson());
    return NodeStrategy.fromJson(response.data as Map<String, dynamic>);
  }

  /// Deletes a step.
  Future<void> deleteStep(String id) async {
    await _dio.delete('studio/steps/$id');
  }

  /// Validates a step definition using the Pre-Flight Simulator API.
  Future<StepSimulationResponse> simulateStep(
    StepSimulationRequest request,
  ) async {
    final response = await _dio.post(
      'studio/steps/simulate',
      data: request.toJson(),
    );
    return StepSimulationResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  /// Deep clones a step securely.
  Future<NodeStrategy> cloneStep(String id) async {
    final response = await _dio.post('studio/steps/$id/clone');
    return NodeStrategy.fromJson(response.data as Map<String, dynamic>);
  }

  /// Creates a draft step securely via SSOT Service Layer.
  Future<NodeStrategy> createStepDraft() async {
    final response = await _dio.post('studio/steps/');
    return NodeStrategy.fromJson(response.data as Map<String, dynamic>);
  }

  // --- Model Registry ---

  /// Retrieves available models filtered by platform and location.
  Future<List<String>> getAvailableModels({
    String? platform,
    String? location,
  }) async {
    final queryParameters = <String, dynamic>{};
    if (platform != null) {
      queryParameters['platform'] = platform;
    }
    if (location != null) {
      queryParameters['location'] = location;
    }

    final response = await _dio.get(
      'studio/model-registry/available-models',
      queryParameters: queryParameters.isNotEmpty ? queryParameters : null,
    );
    return List<String>.from(response.data as List);
  }

  /// Retrieves all supported GCP Vertex AI locations.
  Future<List<GcpLocation>> getSupportedLocations() async {
    final response = await _dio.get('studio/model-registry/locations');
    final rawList = response.data as List;
    return safeIsolateRun(() {
      return rawList
          .map((item) => GcpLocation.fromJson(item as Map<String, dynamic>))
          .toList(growable: false);
    });
  }

  /// Retrieves all supported LLM platforms.
  Future<List<LlmPlatform>> getSupportedPlatforms() async {
    final response = await _dio.get('studio/model-registry/platforms');
    final rawList = response.data as List;
    return rawList
        .map((item) => LlmPlatform.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves all system configs (Model Registries).
  Future<List<ModelConfig>> getSystemConfigs() async {
    final response = await _dio.get('studio/model-registry/');
    final rawList = response.data as List;
    return rawList
        .map((item) => ModelConfig.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves a system config by ID.
  Future<ModelConfig> getSystemConfig(String id) async {
    final response = await _dio.get('studio/model-registry/$id');
    return ModelConfig.fromJson(response.data as Map<String, dynamic>);
  }

  /// Updates a system config.
  Future<ModelConfig> saveSystemConfig(String id, ModelConfig data) async {
    final response = await _dio.put(
      'studio/model-registry/$id',
      data: data.toJson(),
    );
    return ModelConfig.fromJson(response.data as Map<String, dynamic>);
  }

  /// Deletes a system config.
  Future<void> deleteSystemConfig(String id) async {
    await _dio.delete('studio/model-registry/$id');
  }

  /// Deep clones a system config.
  Future<ModelConfig> cloneSystemConfig(String id) async {
    final response = await _dio.post('studio/model-registry/$id/clone');
    return ModelConfig.fromJson(response.data as Map<String, dynamic>);
  }

  /// Creates a draft system config securely via SSOT Service Layer.
  Future<ModelConfig> createSystemConfigDraft() async {
    final response = await _dio.post('studio/model-registry/');
    return ModelConfig.fromJson(response.data as Map<String, dynamic>);
  }

  // --- MCP Gateways ---

  /// Retrieves all MCP Gateways.
  Future<List<McpGateway>> getMcpGateways() async {
    final response = await _dio.get('studio/mcp-gateways/');
    final rawList = response.data as List;
    return rawList
        .map((item) => McpGateway.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves a specific MCP Gateway by ID.
  Future<McpGateway> getMcpGateway(String id) async {
    final response = await _dio.get('studio/mcp-gateways/$id');
    return McpGateway.fromJson(response.data as Map<String, dynamic>);
  }

  /// Appends or updates an MCP Gateway.
  Future<McpGateway> saveMcpGateway(String id, McpGateway data) async {
    final response = await _dio.put(
      'studio/mcp-gateways/$id',
      data: data.toJson(),
    );
    return McpGateway.fromJson(response.data as Map<String, dynamic>);
  }

  /// Deletes an MCP Gateway.
  Future<void> deleteMcpGateway(String id) async {
    await _dio.delete('studio/mcp-gateways/$id');
  }

  /// Deep clones an MCP Gateway.
  Future<McpGateway> cloneMcpGateway(String id) async {
    final response = await _dio.post('studio/mcp-gateways/$id/clone');
    return McpGateway.fromJson(response.data as Map<String, dynamic>);
  }

  /// Creates a draft MCP Gateway securely via SSOT Service Layer.
  Future<McpGateway> createMcpGatewayDraft() async {
    final response = await _dio.post('studio/mcp-gateways/');
    return McpGateway.fromJson(response.data as Map<String, dynamic>);
  }

  // --- Output Profiles ---

  /// Retrieves all output profiles.
  Future<List<OutputProfile>> getOutputProfiles() async {
    final response = await _dio.get('output-profiles/');
    final rawList = response.data as List;
    return rawList
        .map((item) => OutputProfile.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  /// Retrieves a specific output profile by ID.
  Future<OutputProfile> getOutputProfile(String id) async {
    final response = await _dio.get('output-profiles/$id');
    return OutputProfile.fromJson(response.data as Map<String, dynamic>);
  }

  /// Appends or updates an output profile.
  Future<OutputProfile> saveOutputProfile(String id, OutputProfile data) async {
    final response = await _dio.put('output-profiles/$id', data: data.toJson());
    return OutputProfile.fromJson(response.data as Map<String, dynamic>);
  }

  /// Deletes an output profile.
  Future<void> deleteOutputProfile(String id) async {
    await _dio.delete('output-profiles/$id');
  }

  /// Deep clones an output profile.
  Future<OutputProfile> cloneOutputProfile(String id) async {
    final response = await _dio.post('output-profiles/$id/clone');
    return OutputProfile.fromJson(response.data as Map<String, dynamic>);
  }

  /// Creates a draft output profile securely via SSOT Service Layer.
  Future<OutputProfile> createOutputProfileDraft() async {
    final response = await _dio.post('output-profiles/');
    return OutputProfile.fromJson(response.data as Map<String, dynamic>);
  }
}
