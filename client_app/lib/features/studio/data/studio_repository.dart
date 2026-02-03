import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/error/problem_detail.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_repository.g.dart';

@riverpod
StudioRepository studioRepository(Ref ref) {
  return StudioRepository(ref.watch(apiClientProvider), ref.watch(loggerServiceProvider));
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

  Future<List<StudioComponentDef>> getComponents({String? type}) async {
    _logger.info('REPO', 'Fetching components: type=$type');
    try {
      final Map<String, dynamic> queryParams = {};
      if (type != null) {
        queryParams['type'] = type;
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

        // Local Filter: Backend ignores query params currently
        if (type != null && item['type'] != type) {
          // Log skipped items only if debugging deep issues
          // _logger.debug('REPO', 'Skipping item type mismatch: ${item['type']}');
          continue;
        }

        // Sanitize Data
        final data = Map<String, dynamic>.from(item);

        // 1. Polyfill Name
        if (data['name'] == null) {
          data['name'] = data['id'] ?? 'Unnamed';
        }

        // 2. Ensure Content is Map
        if (data['content'] is! Map) {
          data['content'] = {'_value': data['content']};
        }

        try {
          parsed.add(StudioComponentDef.fromJson(data));
        } catch (e) {
          _logger.error('REPO', 'Error parsing component ${data['id']}: $e', e as Exception);
          // Skip invalid items to prevent total failure
          print('Skipping invalid component ${data['id']}: $e');
        }
      }
      _logger.info('REPO', 'Parsed components count: ${parsed.length}');
      return parsed;
    } catch (e) {
      _logger.error('REPO', 'getComponents failed: $e', e as Exception);
      throw AppError.network(e is Exception ? e : Exception(e.toString()));
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
      final result = list
          .map((e) => OntologyDimension.fromJson(e as Map<String, dynamic>))
          .toList();
      print('DEBUG: fetchOntology success. Items: ${result.length}');
      return result;
    } catch (e) {
      print('DEBUG: fetchOntology FAILED: $e');
      throw AppError.network(e);
    }
  }

  Future<void> saveDimension(OntologyDimension dim) async {
    try {
      await _api.post('/v1/config/ontology/dimensions', data: dim.toJson());
    } catch (e) {
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

  Future<MatrixDef> fetchMatrix(String id) async {
    try {
      // First get the component wrapper
      final response = await _api.get('/v1/config/components/$id');
      final compData = response.data as Map<String, dynamic>;

      // Extract inner content and merge with top-level metadata if needed
      // MatrixDef expects {id, name, description, scale, criteria...}
      // content has {scale, criteria...}
      // wrapper has {id, name, description...}

      final content = compData['content'] as Map<String, dynamic>;

      return MatrixDef(
        id: compData['id'] as String,
        name: compData['name'] as String,
        description: (compData['description'] as String?) ?? '',
        scale: Map<String, int>.from((content['scale'] as Map?) ?? {'min': 1, 'max': 5}),
        roleDescription: content['role_description'] as String?,
        criteria:
            (content['criteria'] as List? ?? [])
                .map((e) => MatrixCriterion.fromJson(e as Map<String, dynamic>))
                .toList(),
      );
    } catch (e) {
      throw AppError.network(e);
    }
  }

  Future<void> saveMatrix(MatrixDef matrix) async {
    try {
      // Wrap it back into component structure
      final contentMap = <String, dynamic>{
        'scale': matrix.scale,
        'role_description': matrix.roleDescription,
        'criteria': matrix.criteria.map((e) => e.toJson()).toList(),
      };

      final component = StudioComponentDef(
        id: matrix.id,
        name: matrix.name,
        type: 'evaluation_matrix',
        description: matrix.description,
        content: contentMap,
      );
      await saveComponent(component);
    } catch (e) {
      throw AppError.server(e.toString());
    }
  }

  Future<void> saveComponent(StudioComponentDef component) async {
    try {
      if (component.id.isEmpty || component.id.startsWith('new_')) {
        await _api.post('/v1/config/components', data: component.toJson());
      } else {
        await _api.put(
          '/v1/config/components/${component.id}',
          data: component.toJson(),
        );
      }
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to save component: ${e.toString()}');
    }
  }
}
