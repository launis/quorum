import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/studio/domain/models/workflow_summary.dart';
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

  Future<List<WorkflowSummary>> fetchWorkflows() async {
    final response = await _api.get('/builder/workflows');
    final List<dynamic> list = response.data as List<dynamic>;
    
    return list.map((e) {
      final map = Map<String, dynamic>.from(e as Map<String, dynamic>);
      if (map['updated_at'] != null) {
        map['updatedAt'] = map['updated_at'];
      } else if (map['created_at'] != null) {
        map['updatedAt'] = map['created_at'];
      }
      return WorkflowSummary.fromJson(map);
    }).toList();
  }

  /// Updates an existing workflow configuration.
  /// Endpoint: PUT /builder/workflows/{id}
  Future<void> updateWorkflow(String id, Map<String, dynamic> data) async {
    await _api.put(
      '/builder/workflows/$id',
      data: data,
    );
  }
  /// Fetches a single workflow by ID.
  /// Endpoint: GET /builder/workflows/{id}
  Future<Map<String, dynamic>> fetchWorkflow(String id) async {
    final response = await _api.get('/builder/workflows/$id');
    return response.data as Map<String, dynamic>;
  }
}
