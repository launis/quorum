//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'dart:async';

// ignore: unused_import
import 'dart:convert';
import 'package:backend_api/src/deserialize.dart';
import 'package:dio/dio.dart';

import 'package:backend_api/src/model/agent_definition.dart';
import 'package:backend_api/src/model/agent_run_response.dart';
import 'package:backend_api/src/model/body_run_agent_agents_agent_name_run_post.dart';
import 'package:backend_api/src/model/http_validation_error.dart';

class AgentsApi {
  final Dio _dio;

  const AgentsApi(this._dio);

  /// List All Agents
  /// List all available agents with their metadata, models, and schemas.  Dynamically resolves model strategy based on the selected workflow configuration.  Args:     workflow_id (Optional[str]): Context for model resolution.     registry (RegistryDep): Injected registry service.  Returns:     List[AgentDefinition]: A list of agent definition objects.
  ///
  /// Parameters:
  /// * [workflowId] - Optional Workflow ID to resolve model strategies contextually.
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [List<AgentDefinition>] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<List<AgentDefinition>>> listAgentsAgentsGet({
    String? workflowId,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/agents/';
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      validateStatus: validateStatus,
    );

    final _queryParameters = <String, dynamic>{r'workflow_id': workflowId};

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      queryParameters: _queryParameters,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    List<AgentDefinition>? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<List<AgentDefinition>, AgentDefinition>(
              rawData,
              'List<AgentDefinition>',
              growable: true,
            );
    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _response.requestOptions,
        response: _response,
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    return Response<List<AgentDefinition>>(
      data: _responseData,
      headers: _response.headers,
      isRedirect: _response.isRedirect,
      requestOptions: _response.requestOptions,
      redirects: _response.redirects,
      statusCode: _response.statusCode,
      statusMessage: _response.statusMessage,
      extra: _response.extra,
    );
  }

  /// Run Specific Agent
  /// Executes a specific agent in isolation with provided inputs.  Args:     agent_name (str): The class name of the agent to run.     inputs (Dict[str, Any]): Input data for the agent&#39;s context.     system_instruction (Optional[str]): optional prompt override.     model (Optional[str]): optional model override (strategy key or model name).     repo (RepositoryDep): Database repository.     registry (RegistryDep): Registry dependency for strategy resolution.  Returns:     AgentRunResponse: A DTO containing the execution result.  Raises:     ResourceNotFoundError: If the agent class cannot be loaded.     AppException: If execution fails (400 for validation, 500 for runtime).
  ///
  /// Parameters:
  /// * [agentName]
  /// * [bodyRunAgentAgentsAgentNameRunPost]
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [AgentRunResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<AgentRunResponse>> runAgentAgentsAgentNameRunPost({
    required String agentName,
    required BodyRunAgentAgentsAgentNameRunPost
    bodyRunAgentAgentsAgentNameRunPost,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/agents/{agent_name}/run'.replaceAll(
      '{'
      r'agent_name'
      '}',
      agentName.toString(),
    );
    final _options = Options(
      method: r'POST',
      headers: <String, dynamic>{...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      contentType: 'application/json',
      validateStatus: validateStatus,
    );

    dynamic _bodyData;

    try {
      _bodyData = jsonEncode(bodyRunAgentAgentsAgentNameRunPost);
    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _options.compose(_dio.options, _path),
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    final _response = await _dio.request<Object>(
      _path,
      data: _bodyData,
      options: _options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    AgentRunResponse? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<AgentRunResponse, AgentRunResponse>(
              rawData,
              'AgentRunResponse',
              growable: true,
            );
    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _response.requestOptions,
        response: _response,
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    return Response<AgentRunResponse>(
      data: _responseData,
      headers: _response.headers,
      isRedirect: _response.isRedirect,
      requestOptions: _response.requestOptions,
      redirects: _response.redirects,
      statusCode: _response.statusCode,
      statusMessage: _response.statusMessage,
      extra: _response.extra,
    );
  }
}
