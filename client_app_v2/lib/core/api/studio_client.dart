import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
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
import 'package:client_app/features/studio/models/task_brief.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/workflow_simulation.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_client.g.dart';

/// Studio API Client Provider
@Riverpod(keepAlive: true)
StudioClient studioClient(Ref ref) {
  return StudioClient(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

/// Client for interacting with the V2 Studio API (Admin/Config features).
class StudioClient {
  final Dio _dio;
  final LoggerService? _logger;
  static const StrictOpaqueIdConverter _idValidator = StrictOpaqueIdConverter();

  StudioClient(this._dio, [this._logger]);

  void _validateOpaqueId(String id, String fieldName, String methodName) {
    try {
      _idValidator.fromJson(id);
    } on AppException catch (e, st) {
      _logger?.error(
        'StudioClient',
        'Invalid $fieldName format "$id" for $methodName',
        e,
        st,
      );
      rethrow;
    }
  }

  T _parseResponse<T>(
    Response<Map<String, Object?>> response,
    T Function(Map<String, Object?>) parser,
    String methodName,
  ) {
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null response payload received in StudioClient.$methodName',
      );
      _logger?.error(
        'StudioClient',
        'Null response data for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return parser(data);
  }

  List<T> _parseListResponse<T>(
    Response<List<Object?>> response,
    T Function(Map<String, Object?>) itemParser,
    String methodName,
  ) {
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null list response payload received in StudioClient.$methodName',
      );
      _logger?.error(
        'StudioClient',
        'Null list response data for $methodName',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return data
        .map((item) {
          if (item is! Map<String, Object?>) {
            final error = AppException.validation(
              'Malformed list element in StudioClient.$methodName: expected Map<String, Object?>.',
            );
            _logger?.error(
              'StudioClient',
              'Malformed list item for $methodName',
              error,
              StackTrace.current,
            );
            throw error;
          }
          return itemParser(item);
        })
        .toList(growable: false);
  }

  // --- Matrices (Criteria & Scoring) ---

  /// Retrieves all evaluation prompt blocks.
  Future<List<PromptBlock>> getPromptBlocks() async {
    final response = await _dio.get<List<Object?>>('studio/prompt-blocks');
    return _parseListResponse(
      response,
      PromptBlock.fromJson,
      'getPromptBlocks',
    );
  }

  /// Retrieves a specific prompt block by id.
  Future<PromptBlock> getPromptBlock(String id) async {
    _validateOpaqueId(id, 'id', 'getPromptBlock');
    final response = await _dio.get<Map<String, Object?>>(
      'studio/prompt-blocks/$id',
    );
    return _parseResponse(response, PromptBlock.fromJson, 'getPromptBlock');
  }

  /// Appends or updates a prompt block.
  /// In V2, blocks are append-only. This typically returns a new version ID.
  Future<PromptBlock> savePromptBlock(String id, PromptBlock data) async {
    _validateOpaqueId(id, 'id', 'savePromptBlock');
    final response = await _dio.put<Map<String, Object?>>(
      'studio/prompt-blocks/$id',
      data: data.toJson(),
    );
    return _parseResponse(response, PromptBlock.fromJson, 'savePromptBlock');
  }

  /// Dry-runs a prompt block or matrix rendering with mock variables.
  Future<PromptBlockSimulationResponse> simulatePromptBlock(
    PromptBlockSimulationRequest request,
  ) async {
    _validateOpaqueId(request.block.id, 'block.id', 'simulatePromptBlock');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/prompt-blocks/simulate',
      data: request.toJson(),
    );
    return _parseResponse(
      response,
      PromptBlockSimulationResponse.fromJson,
      'simulatePromptBlock',
    );
  }

  /// Deletes a prompt block.
  Future<void> deletePromptBlock(String id) async {
    _validateOpaqueId(id, 'id', 'deletePromptBlock');
    await _dio.delete<void>('studio/prompt-blocks/$id');
  }

  /// Deep clones a prompt block securely via SSOT Service Layer.
  Future<PromptBlock> clonePromptBlock(String id) async {
    _validateOpaqueId(id, 'id', 'clonePromptBlock');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/prompt-blocks/$id/clone',
    );
    return _parseResponse(response, PromptBlock.fromJson, 'clonePromptBlock');
  }

  /// Creates a draft prompt block securely via SSOT Service Layer.
  Future<PromptBlock> createPromptBlockDraft({String? categoryId}) async {
    final queryParameters = <String, Object?>{};
    if (categoryId != null) {
      queryParameters['category_id'] = categoryId;
    }
    final response = await _dio.post<Map<String, Object?>>(
      'studio/prompt-blocks/',
      queryParameters: queryParameters.isNotEmpty ? queryParameters : null,
    );
    return _parseResponse(
      response,
      PromptBlock.fromJson,
      'createPromptBlockDraft',
    );
  }

  // --- Workflows (DAG definitions) ---

  /// Retrieves all workflow definitions.
  Future<List<Workflow>> getWorkflows() async {
    final response = await _dio.get<List<Object?>>('studio/workflows');
    return _parseListResponse(response, Workflow.fromJson, 'getWorkflows');
  }

  /// Retrieves a specific workflow definition by id.
  Future<Workflow> getWorkflow(String id) async {
    _validateOpaqueId(id, 'id', 'getWorkflow');
    final response = await _dio.get<Map<String, Object?>>(
      'studio/workflows/$id',
    );
    return _parseResponse(response, Workflow.fromJson, 'getWorkflow');
  }

  /// Appends or updates a workflow definition.
  Future<Workflow> saveWorkflow(String id, Workflow data) async {
    _validateOpaqueId(id, 'id', 'saveWorkflow');
    final payload = Map<String, Object?>.from(data.toJson())
      ..remove('output_profiles');
    final response = await _dio.put<Map<String, Object?>>(
      'studio/workflows/$id',
      data: payload,
    );
    return _parseResponse(response, Workflow.fromJson, 'saveWorkflow');
  }

  /// Validates a workflow definition using the Pre-Flight Simulator API.
  Future<WorkflowSimulationResponse> simulateWorkflow(Workflow data) async {
    _validateOpaqueId(data.id, 'data.id', 'simulateWorkflow');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/workflows/simulate',
      data: data.toJson(),
    );
    return _parseResponse(
      response,
      WorkflowSimulationResponse.fromJson,
      'simulateWorkflow',
    );
  }

  /// Deletes a workflow definition.
  Future<void> deleteWorkflow(String id) async {
    _validateOpaqueId(id, 'id', 'deleteWorkflow');
    await _dio.delete<void>('studio/workflows/$id');
  }

  /// Deep clones a workflow definition securely via SSOT Service Layer.
  Future<Workflow> cloneWorkflow(String id) async {
    _validateOpaqueId(id, 'id', 'cloneWorkflow');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/workflows/$id/clone',
    );
    return _parseResponse(response, Workflow.fromJson, 'cloneWorkflow');
  }

  /// Creates a draft workflow definition securely via SSOT Service Layer.
  Future<Workflow> createWorkflowDraft() async {
    final response = await _dio.post<Map<String, Object?>>('studio/workflows/');
    return _parseResponse(response, Workflow.fromJson, 'createWorkflowDraft');
  }

  /// Retrieves available block-level extensions for a workflow.
  Future<List<String>> getWorkflowAvailableExtensions(String id) async {
    _validateOpaqueId(id, 'id', 'getWorkflowAvailableExtensions');
    final response = await _dio.get<Map<String, Object?>>(
      'studio/workflows/$id/available-extensions',
    );
    final data = response.data;
    if (data == null || data['available_extensions'] is! List<Object?>) {
      final error = AppException.validation(
        'Malformed available_extensions payload in StudioClient.getWorkflowAvailableExtensions',
      );
      _logger?.error(
        'StudioClient',
        'Malformed available_extensions payload for getWorkflowAvailableExtensions',
        error,
        StackTrace.current,
      );
      throw error;
    }
    final rawList = data['available_extensions'] as List<Object?>;
    return rawList.map((e) => e.toString()).toList(growable: false);
  }

  // --- Steps ---

  /// Retrieves all steps.
  Future<List<NodeStrategy>> getSteps({
    StepFilterScope scope = StepFilterScope.specialists,
  }) async {
    final queryParameters = <String, Object?>{'scope': scope.backendValue};
    final response = await _dio.get<List<Object?>>(
      'studio/steps',
      queryParameters: queryParameters,
    );
    return _parseListResponse(response, NodeStrategy.fromJson, 'getSteps');
  }

  /// Retrieves a specific step by id.
  Future<NodeStrategy> getStep(String id) async {
    _validateOpaqueId(id, 'id', 'getStep');
    final response = await _dio.get<Map<String, Object?>>('studio/steps/$id');
    return _parseResponse(response, NodeStrategy.fromJson, 'getStep');
  }

  /// Appends or updates a step.
  Future<NodeStrategy> saveStep(String id, NodeStrategy data) async {
    _validateOpaqueId(id, 'id', 'saveStep');
    final response = await _dio.put<Map<String, Object?>>(
      'studio/steps/$id',
      data: data.toJson(),
    );
    return _parseResponse(response, NodeStrategy.fromJson, 'saveStep');
  }

  /// Deletes a step.
  Future<void> deleteStep(String id) async {
    _validateOpaqueId(id, 'id', 'deleteStep');
    await _dio.delete<void>('studio/steps/$id');
  }

  /// Validates a step definition using the Pre-Flight Simulator API.
  Future<StepSimulationResponse> simulateStep(
    StepSimulationRequest request,
  ) async {
    _validateOpaqueId(request.step.id, 'step.id', 'simulateStep');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/steps/simulate',
      data: request.toJson(),
    );
    return _parseResponse(
      response,
      StepSimulationResponse.fromJson,
      'simulateStep',
    );
  }

  /// Deep clones a step securely.
  Future<NodeStrategy> cloneStep(String id) async {
    _validateOpaqueId(id, 'id', 'cloneStep');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/steps/$id/clone',
    );
    return _parseResponse(response, NodeStrategy.fromJson, 'cloneStep');
  }

  /// Creates a draft step securely via SSOT Service Layer.
  Future<NodeStrategy> createStepDraft() async {
    final response = await _dio.post<Map<String, Object?>>('studio/steps/');
    return _parseResponse(response, NodeStrategy.fromJson, 'createStepDraft');
  }

  // --- Model Registry ---

  /// Retrieves available models filtered by platform and location.
  Future<List<String>> getAvailableModels({
    String? platform,
    String? location,
  }) async {
    final queryParameters = <String, Object?>{};
    if (platform != null) {
      queryParameters['platform'] = platform;
    }
    if (location != null) {
      queryParameters['location'] = location;
    }

    final response = await _dio.get<List<Object?>>(
      'studio/model-registry/available-models',
      queryParameters: queryParameters.isNotEmpty ? queryParameters : null,
    );
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null list response payload received in StudioClient.getAvailableModels',
      );
      _logger?.error(
        'StudioClient',
        'Null list response data for getAvailableModels',
        error,
        StackTrace.current,
      );
      throw error;
    }
    return data.map((e) => e.toString()).toList(growable: false);
  }

  /// Retrieves all supported GCP Vertex AI locations.
  Future<List<GcpLocation>> getSupportedLocations() async {
    final response = await _dio.get<List<Object?>>(
      'studio/model-registry/locations',
    );
    final data = response.data;
    if (data == null) {
      final error = AppException.validation(
        'Null list response payload received in StudioClient.getSupportedLocations',
      );
      _logger?.error(
        'StudioClient',
        'Null list response data for getSupportedLocations',
        error,
        StackTrace.current,
      );
      throw error;
    }
    for (final item in data) {
      if (item is! Map<String, Object?>) {
        final error = AppException.validation(
          'Malformed list element in StudioClient.getSupportedLocations: expected Map<String, Object?>.',
        );
        _logger?.error(
          'StudioClient',
          'Malformed list item for getSupportedLocations',
          error,
          StackTrace.current,
        );
        throw error;
      }
    }
    return safeIsolateRun(() {
      return data
          .cast<Map<String, Object?>>()
          .map(GcpLocation.fromJson)
          .toList(growable: false);
    });
  }

  /// Retrieves all supported LLM platforms.
  Future<List<LlmPlatform>> getSupportedPlatforms() async {
    final response = await _dio.get<List<Object?>>(
      'studio/model-registry/platforms',
    );
    return _parseListResponse(
      response,
      LlmPlatform.fromJson,
      'getSupportedPlatforms',
    );
  }

  /// Retrieves all system configs (Model Registries).
  Future<List<ModelConfig>> getSystemConfigs() async {
    final response = await _dio.get<List<Object?>>('studio/model-registry/');
    return _parseListResponse(
      response,
      ModelConfig.fromJson,
      'getSystemConfigs',
    );
  }

  /// Retrieves a system config by ID.
  Future<ModelConfig> getSystemConfig(String id) async {
    _validateOpaqueId(id, 'id', 'getSystemConfig');
    final response = await _dio.get<Map<String, Object?>>(
      'studio/model-registry/$id',
    );
    return _parseResponse(response, ModelConfig.fromJson, 'getSystemConfig');
  }

  /// Updates a system config.
  Future<ModelConfig> saveSystemConfig(String id, ModelConfig data) async {
    _validateOpaqueId(id, 'id', 'saveSystemConfig');
    final response = await _dio.put<Map<String, Object?>>(
      'studio/model-registry/$id',
      data: data.toJson(),
    );
    return _parseResponse(response, ModelConfig.fromJson, 'saveSystemConfig');
  }

  /// Deletes a system config.
  Future<void> deleteSystemConfig(String id) async {
    _validateOpaqueId(id, 'id', 'deleteSystemConfig');
    await _dio.delete<void>('studio/model-registry/$id');
  }

  /// Deep clones a system config.
  Future<ModelConfig> cloneSystemConfig(String id) async {
    _validateOpaqueId(id, 'id', 'cloneSystemConfig');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/model-registry/$id/clone',
    );
    return _parseResponse(response, ModelConfig.fromJson, 'cloneSystemConfig');
  }

  /// Creates a draft system config securely via SSOT Service Layer.
  Future<ModelConfig> createSystemConfigDraft() async {
    final response = await _dio.post<Map<String, Object?>>(
      'studio/model-registry/',
    );
    return _parseResponse(
      response,
      ModelConfig.fromJson,
      'createSystemConfigDraft',
    );
  }

  // --- MCP Gateways ---

  /// Retrieves all MCP Gateways.
  Future<List<McpGateway>> getMcpGateways() async {
    final response = await _dio.get<List<Object?>>('studio/mcp-gateways/');
    return _parseListResponse(response, McpGateway.fromJson, 'getMcpGateways');
  }

  /// Retrieves a specific MCP Gateway by ID.
  Future<McpGateway> getMcpGateway(String id) async {
    _validateOpaqueId(id, 'id', 'getMcpGateway');
    final response = await _dio.get<Map<String, Object?>>(
      'studio/mcp-gateways/$id',
    );
    return _parseResponse(response, McpGateway.fromJson, 'getMcpGateway');
  }

  /// Appends or updates an MCP Gateway.
  Future<McpGateway> saveMcpGateway(String id, McpGateway data) async {
    _validateOpaqueId(id, 'id', 'saveMcpGateway');
    final response = await _dio.put<Map<String, Object?>>(
      'studio/mcp-gateways/$id',
      data: data.toJson(),
    );
    return _parseResponse(response, McpGateway.fromJson, 'saveMcpGateway');
  }

  /// Deletes an MCP Gateway.
  Future<void> deleteMcpGateway(String id) async {
    _validateOpaqueId(id, 'id', 'deleteMcpGateway');
    await _dio.delete<void>('studio/mcp-gateways/$id');
  }

  /// Deep clones an MCP Gateway.
  Future<McpGateway> cloneMcpGateway(String id) async {
    _validateOpaqueId(id, 'id', 'cloneMcpGateway');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/mcp-gateways/$id/clone',
    );
    return _parseResponse(response, McpGateway.fromJson, 'cloneMcpGateway');
  }

  /// Creates a draft MCP Gateway securely via SSOT Service Layer.
  Future<McpGateway> createMcpGatewayDraft() async {
    final response = await _dio.post<Map<String, Object?>>(
      'studio/mcp-gateways/',
    );
    return _parseResponse(
      response,
      McpGateway.fromJson,
      'createMcpGatewayDraft',
    );
  }

  /// Introspects an external MCP server and discovers available tools.
  Future<McpGateway> discoverMcpGatewayTools(String id) async {
    _validateOpaqueId(id, 'id', 'discoverMcpGatewayTools');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/mcp-gateways/$id/discover',
    );
    return _parseResponse(
      response,
      McpGateway.fromJson,
      'discoverMcpGatewayTools',
    );
  }

  // --- Output Profiles ---

  /// Retrieves all output profiles.
  Future<List<OutputProfile>> getOutputProfiles() async {
    final response = await _dio.get<List<Object?>>('output-profiles/');
    return _parseListResponse(
      response,
      OutputProfile.fromJson,
      'getOutputProfiles',
    );
  }

  /// Retrieves a specific output profile by ID.
  Future<OutputProfile> getOutputProfile(String id) async {
    _validateOpaqueId(id, 'id', 'getOutputProfile');
    final response = await _dio.get<Map<String, Object?>>(
      'output-profiles/$id',
    );
    return _parseResponse(response, OutputProfile.fromJson, 'getOutputProfile');
  }

  /// Appends or updates an output profile.
  Future<OutputProfile> saveOutputProfile(String id, OutputProfile data) async {
    _validateOpaqueId(id, 'id', 'saveOutputProfile');
    final response = await _dio.put<Map<String, Object?>>(
      'output-profiles/$id',
      data: data.toJson(),
    );
    return _parseResponse(
      response,
      OutputProfile.fromJson,
      'saveOutputProfile',
    );
  }

  /// Deletes an output profile.
  Future<void> deleteOutputProfile(String id) async {
    _validateOpaqueId(id, 'id', 'deleteOutputProfile');
    await _dio.delete<void>('output-profiles/$id');
  }

  /// Deep clones an output profile.
  Future<OutputProfile> cloneOutputProfile(String id) async {
    _validateOpaqueId(id, 'id', 'cloneOutputProfile');
    final response = await _dio.post<Map<String, Object?>>(
      'output-profiles/$id/clone',
    );
    return _parseResponse(
      response,
      OutputProfile.fromJson,
      'cloneOutputProfile',
    );
  }

  /// Creates a draft output profile securely via SSOT Service Layer.
  Future<OutputProfile> createOutputProfileDraft() async {
    final response = await _dio.post<Map<String, Object?>>('output-profiles/');
    return _parseResponse(
      response,
      OutputProfile.fromJson,
      'createOutputProfileDraft',
    );
  }

  // --- Task Briefs ---

  /// Retrieves all task briefs accessible to the current tenant.
  Future<List<TaskBrief>> getTaskBriefs() async {
    final response = await _dio.get<List<Object?>>('studio/task-briefs/');
    return _parseListResponse(response, TaskBrief.fromJson, 'getTaskBriefs');
  }

  /// Retrieves a specific task brief by ID.
  Future<TaskBrief> getTaskBrief(String id) async {
    _validateOpaqueId(id, 'id', 'getTaskBrief');
    final response = await _dio.get<Map<String, Object?>>(
      'studio/task-briefs/$id',
    );
    return _parseResponse(response, TaskBrief.fromJson, 'getTaskBrief');
  }

  /// Appends or updates a task brief.
  Future<TaskBrief> saveTaskBrief(String id, TaskBrief data) async {
    _validateOpaqueId(id, 'id', 'saveTaskBrief');
    final response = await _dio.put<Map<String, Object?>>(
      'studio/task-briefs/$id',
      data: data.toJson(),
    );
    return _parseResponse(response, TaskBrief.fromJson, 'saveTaskBrief');
  }

  /// Deletes a task brief.
  Future<void> deleteTaskBrief(String id) async {
    _validateOpaqueId(id, 'id', 'deleteTaskBrief');
    await _dio.delete<void>('studio/task-briefs/$id');
  }

  /// Deep clones a task brief securely.
  Future<TaskBrief> cloneTaskBrief(String id) async {
    _validateOpaqueId(id, 'id', 'cloneTaskBrief');
    final response = await _dio.post<Map<String, Object?>>(
      'studio/task-briefs/$id/clone',
    );
    return _parseResponse(response, TaskBrief.fromJson, 'cloneTaskBrief');
  }

  /// Creates a draft task brief securely via SSOT Service Layer.
  Future<TaskBrief> createTaskBriefDraft() async {
    final response = await _dio.post<Map<String, Object?>>(
      'studio/task-briefs/',
    );
    return _parseResponse(response, TaskBrief.fromJson, 'createTaskBriefDraft');
  }
}
