import 'package:client_app/api/api_client.dart';
import 'package:client_app/core/error/app_error.dart';
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
      final response = await _api.get('/workflows');
      return (response.data as List)
          .map((e) => WorkflowDef.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      if (e is AppError) rethrow; // Already parsed by ErrorInterceptor
      throw AppError.server('Failed to fetch workflows: $e');
    }
  }

  Future<WorkflowDef> getWorkflow(String id) async {
    try {
      final response = await _api.get('/workflows/$id');
      return WorkflowDef.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to fetch workflow $id: $e');
    }
  }

  Future<void> saveWorkflow(WorkflowDef workflow) async {
    try {
      // Use standard PUT usage for saving by ID, or POST for new.
      // Assuming upsert based on existence or always PUT to /workflows/:id
      // For safety, generally POST /workflows for create, PUT /workflows/:id for update
      // Since WorkflowDef has ID, we can assume update if ID exists in backend?
      // Or simplify: POST to /workflows (upsert logic in backend not specified).
      // I will assume POST to /workflows for now as a generic save.
      // Actually standard REST: PUT /workflows/{id}
      await _api.post('/workflows', data: workflow.toJson());
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to save workflow: $e');
    }
  }

  Future<void> deleteWorkflow(String id) async {
    try {
      await _api.delete('/workflows/$id');
    } catch (e) {
      if (e is AppError) rethrow;
      throw AppError.server('Failed to delete workflow $id: $e');
    }
  }
}
