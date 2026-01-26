import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'schema_repository.g.dart';

@riverpod
SchemaRepository schemaRepository(Ref ref) {
  return SchemaRepository(ref.watch(apiClientProvider));
}

class SchemaRepository {
  final Dio _api;

  SchemaRepository(this._api);

  /// Fetches the JSON Schema for a specific component type.
  ///
  /// Endpoint: GET /api/v1/studio/schema/{componentType}
  Future<JsonSchema> fetchSchema(String componentType) async {
    final response = await _api.get('/builder/schema/$componentType');

    // Dio returns dynamic, response.data should be Map<String, dynamic>
    final data = response.data as Map<String, dynamic>;

    return JsonSchema.fromJson(data);
  }
}
