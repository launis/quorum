import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/error/problem_detail.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:client_app/features/studio/domain/models/step_config.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_repository.g.dart';

@riverpod
StudioRepository studioRepository(Ref ref) {
  return StudioRepository(
    ref.watch(apiClientProvider),
    ref.watch(loggerServiceProvider),
  );
}

class StudioRepository {
  final Dio _api;
  final LoggerService _logger;

  StudioRepository(this._api, this._logger);

  Future<List<WorkflowDef>> getWorkflows() async {
    try {
      final response = await _api.get('/builder/workflows');
      return (response.data as List)
          .map((e) {
            try {
              return WorkflowDef.fromJson(e as Map<String, dynamic>);
            } catch (error) {
              // ignore: avoid_print
              print("Error parsing workflow: $error. Data: $e");
              return null;
            }
          })
          .whereType<WorkflowDef>()
          .toList();
    } catch (e) {
      if (e is AppError) rethrow; // Already parsed by ErrorInterceptor
      throw AppError.server('Failed to fetch workflows: $e');
    }
  }

  Future<WorkflowDef> getWorkflow(String id) async {
    try {
      final response = await _api.get('/builder/workflows/$id');
      return WorkflowDef.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch workflow $id: $e');
    }
  }

  Future<void> saveWorkflow(WorkflowDef workflow) async {
    try {
      if (workflow.id.isEmpty || workflow.id.startsWith('new_')) {
        await _api.post('/builder/workflows', data: workflow.toJson());
      } else {
        await _api.put(
          '/builder/workflows/${workflow.id}',
          data: workflow.toJson(),
        );
      }
    } catch (e) {
      if (e is AppError) rethrow;
      if (e is DioException) {
        try {
          if (e.response?.data != null) {
            final problem = ProblemDetail.fromJson(e.response!.data);
            throw AppError.fromProblemDetail(problem);
          }
        } catch (_) {
          // Fallback if parsing fails
        }
      }
      throw AppError.server('Failed to save workflow: $e');
    }
  }

  Future<void> deleteWorkflow(String id) async {
    try {
      await _api.delete('/builder/workflows/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete workflow $id: $e');
    }
  }

  Future<void> copyWorkflow(String originalId, String newName) async {
    try {
      await _api.post(
        '/builder/workflows/$originalId/copy',
        data: {'new_name': newName},
      );
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to copy workflow: $e');
    }
  }

  Future<List<StudioComponentDef>> getAvailableComponents() async {
    return getComponents();
  }

  Future<List<StudioComponentDef>> getComponents({
    String? type,
    List<String>? excludeTypes,
  }) async {
    _logger.info(
      'REPO',
      'Fetching raw text components: type=$type, excludeTypes=$excludeTypes',
    );
    try {
      final Map<String, dynamic> queryParams = {};
      if (type != null) {
        queryParams['type'] = type;
      }
      if (excludeTypes != null && excludeTypes.isNotEmpty) {
        queryParams['exclude_type'] = excludeTypes;
      }

      final response = await _api.get(
        '/v1/config/components',
        queryParameters: queryParams,
      );

      final rawList = response.data as List;
      _logger.info('REPO', 'Raw components fetched: ${rawList.length}');

      final parsed = <StudioComponentDef>[];

      for (var item in rawList) {
        if (item is! Map<String, dynamic>) {
          _logger.warning('REPO', 'Skipping non-map item');
          continue;
        }

        // Sanitize Data
        final data = Map<String, dynamic>.from(item);

        // 1. Polyfill Name (REMOVED - Backend ensures name or schema validation catches it)

        try {
          parsed.add(StudioComponentDef.fromJson(data));
        } catch (e) {
          _logger.error(
            'REPO',
            'Error parsing component ${data["id"]}: $e. RAW: $data',
            e as Exception,
          );
          // Skip invalid items to prevent total failure
          print('Skipping invalid component ${data["id"]}: $e. RAW: $data');
        }
      }
      _logger.info('REPO', 'Parsed text components count: ${parsed.length}');
      return parsed;
    } catch (e) {
      final exception = e is Exception ? e : Exception(e.toString());
      _logger.error('REPO', 'getComponents failed: $e', exception);
      throw AppError.network(exception);
    }
  }

  // --- Matrices API ---

  Future<List<MatrixDef>> getMatrices() async {
    try {
      final response = await _api.get('/v1/config/matrices');
      return (response.data as List).map((e) {
        final json = Map<String, dynamic>.from(e as Map);
        // Flatten backend DTO "content" to root for MatrixDef
        final content = json['content'] as Map<String, dynamic>? ?? {};
        final flattened = {
          ...json,
          'scale': content['scale'] ?? {'min': 1, 'max': 5},
          'criteria': content['criteria'] ?? [],
          if (content.containsKey('role_description'))
            'role_description': content['role_description'],
        };
        return MatrixDef.fromJson(flattened);
      }).toList();
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch matrices: $e');
    }
  }

  Future<MatrixDef> fetchMatrix(String id) async {
    try {
      final response = await _api.get('/v1/config/matrices/$id');
      final json = response.data as Map<String, dynamic>;
      final content = json['content'] as Map<String, dynamic>? ?? {};
      final flattened = {
        ...json,
        'scale': content['scale'] ?? {'min': 1, 'max': 5},
        'criteria': content['criteria'] ?? [],
        if (content.containsKey('role_description'))
          'role_description': content['role_description'],
      };
      return MatrixDef.fromJson(flattened);
    } catch (e) {
      throw AppError.network(e);
    }
  }

  Future<void> saveMatrix(MatrixDef matrix) async {
    try {
      final rawJson = matrix.toJson();

      // Un-flatten: move MatrixDef specific fields back to 'content' for backend Strict DTO
      final content = {
        'scale': rawJson['scale'],
        'criteria': rawJson['criteria'],
        if (rawJson.containsKey('role_description'))
          'role_description': rawJson['role_description'],
      };

      final payload = {
        'id': rawJson['id'],
        'name': rawJson['name'],
        'description': rawJson['description'],
        'type': 'evaluation_matrix',
        'content': content,
      };

      if (matrix.id.isEmpty || matrix.id.startsWith('new_')) {
        await _api.post('/v1/config/matrices', data: payload);
      } else {
        await _api.put('/v1/config/matrices/${matrix.id}', data: payload);
      }
    } catch (e) {
      throw AppError.server(e.toString());
    }
  }

  Future<void> deleteMatrix(String id) async {
    try {
      await _api.delete('/v1/config/matrices/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete matrix $id: $e');
    }
  }

  // --- Agents API ---

  Future<List<StudioComponentDef>> getAgents() async {
    try {
      final response = await _api.get('/v1/config/agents');
      return (response.data as List)
          .map((e) => StudioComponentDef.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch agents: $e');
    }
  }

  Future<void> saveAgent(StudioComponentDef agent) async {
    try {
      if (agent.id.isEmpty || agent.id.startsWith('new_')) {
        await _api.post('/v1/config/agents', data: agent.toJson());
      } else {
        await _api.put('/v1/config/agents/${agent.id}', data: agent.toJson());
      }
    } catch (e) {
      throw AppError.server(e.toString());
    }
  }

  Future<void> deleteAgent(String id) async {
    try {
      await _api.delete('/v1/config/agents/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete agent $id: $e');
    }
  }

  // --- Outputs API ---

  Future<List<StudioComponentDef>> getOutputConfigs() async {
    try {
      final response = await _api.get('/v1/config/outputs');
      return (response.data as List)
          .map((e) => StudioComponentDef.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch output configs: $e');
    }
  }

  Future<void> saveOutputConfig(StudioComponentDef config) async {
    try {
      if (config.id.isEmpty || config.id.startsWith('new_')) {
        await _api.post('/v1/config/outputs', data: config.toJson());
      } else {
        await _api.put(
          '/v1/config/outputs/${config.id}',
          data: config.toJson(),
        );
      }
    } catch (e) {
      throw AppError.server(e.toString());
    }
  }

  Future<void> deleteOutputConfig(String id) async {
    try {
      await _api.delete('/v1/config/outputs/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete output config $id: $e');
    }
  }

  /// **Fetch Ontology (Type-Safe)**
  Future<List<OntologyDimension>> fetchOntology() async {
    try {
      final response = await _api.get('/v1/config/ontology/dimensions');
      print('DEBUG: fetchOntology response data: ${response.data}');
      final list = response.data as List;
      // Handle both list of strings (legacy) and list of objects
      if (list.isNotEmpty && list.first is String) {
        print('Warning: Ontology endpoint returned IDs only.');
        return [];
      }
      final result =
          list
              .map((e) => OntologyDimension.fromJson(e as Map<String, dynamic>))
              .toList();
      print('DEBUG: fetchOntology success. Items: ${result.length}');
      return result;
    } catch (e) {
      print('DEBUG: fetchOntology FAILED: $e');
      throw AppError.network(e);
    }
  }

  Future<void> saveDimension(
    OntologyDimension dim, {
    bool isUpdate = false,
  }) async {
    try {
      if (isUpdate) {
        await _api.put(
          '/v1/config/ontology/dimensions/${dim.id}',
          data: dim.toJson(),
        );
      } else {
        await _api.post('/v1/config/ontology/dimensions', data: dim.toJson());
      }
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server(e.toString());
    }
  }

  Future<void> deleteDimension(String id) async {
    try {
      await _api.delete('/v1/config/ontology/dimensions/$id');
    } catch (e) {
      throw AppError.server(e.toString());
    }
  }

  Future<void> createComponent(StudioComponentDef component) async {
    try {
      await _api.post('/v1/config/components', data: component.toJson());
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to create component: ${e.toString()}');
    }
  }

  Future<void> updateComponent(StudioComponentDef component) async {
    try {
      await _api.put(
        '/v1/config/components/${component.id}',
        data: component.toJson(),
      );
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to update component: ${e.toString()}');
    }
  }

  Future<void> saveComponent(StudioComponentDef component) async {
    if (component.id.isEmpty || component.id.startsWith('new_')) {
      await createComponent(component);
    } else {
      await updateComponent(component);
    }
  }

  Future<void> deleteComponent(String id) async {
    try {
      await _api.delete('/v1/config/components/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete component $id: $e');
    }
  }

  // --- Steps Management ---

  Future<List<StepConfig>> fetchSteps() async {
    try {
      final response = await _api.get('/v1/config/steps');
      return (response.data as List)
          .map((e) => StepConfig.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch steps: $e');
    }
  }

  Future<void> saveStep(StepConfig step) async {
    try {
      if (step.id.isEmpty || step.id.startsWith('step_new')) {
        await _api.post('/v1/config/steps', data: step.toJson());
      } else {
        await _api.put('/v1/config/steps/${step.id}', data: step.toJson());
      }
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to save step: $e');
    }
  }

  Future<void> deleteStep(String id) async {
    try {
      await _api.delete('/v1/config/steps/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete step $id: $e');
    }
  }
}
