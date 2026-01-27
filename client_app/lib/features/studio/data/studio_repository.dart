import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/error/problem_detail.dart';
import 'package:client_app/features/studio/domain/models/workflow_def.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'studio_repository.g.dart';

@riverpod
StudioRepository studioRepository(Ref ref) {
  return StudioRepository(ref.watch(apiClientProvider));
}

class StudioRepository {
  final Dio _api;

  StudioRepository(this._api);

  Future<List<WorkflowDef>> getWorkflows() async {
    try {
      final response = await _api.get('/builder/workflows');
      return (response.data as List).map((e) {
        try {
          return WorkflowDef.fromJson(e as Map<String, dynamic>);
        } catch (error) {
          // ignore: avoid_print
          print("Error parsing workflow: $error. Data: $e");
          return null;
        }
      }).whereType<WorkflowDef>().toList();
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
         await _api.put('/builder/workflows/${workflow.id}', data: workflow.toJson());
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
      await _api.post('/builder/workflows/$originalId/copy', data: {'new_name': newName});
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to copy workflow: $e');
    }
  }

  Future<List<ComponentDef>> getAvailableComponents() async {
    try {
      final response = await _api.get('/v1/config/registry_items');
      return (response.data as List)
          .map((e) => ComponentDef.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch components: $e');
    }
  }
}
