import 'dart:io';

import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../api/api_client.dart';
import '../models/knowledge_base.dart';

part 'knowledge_repository.g.dart';

@Riverpod(keepAlive: true)
class KnowledgeRepository extends _$KnowledgeRepository {
  late final Dio _dio;

  @override
  void build() {
    _dio = ref.watch(apiClientProvider);
  }

  /// Uploads a knowledge base file and starts the ingestion process.
  ///
  /// This method performs a `multipart/form-data` upload to the backend.
  /// It takes a [File] object as input, which should be a valid DOCX or MD file.
  /// [modelStrategy] can be provided to select a specific LLM analysis level.
  ///
  /// Returns the [String] Job ID uniquely identifying the ingestion background task.
  /// Throws [DioException] if the upload fails.
  Future<String> uploadKnowledgeBase(File file, {String? modelStrategy}) async {
    final fileName = file.path.split(Platform.pathSeparator).last;

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(file.path, filename: fileName),
    });

    final queryParams = <String, dynamic>{};
    if (modelStrategy != null) {
      queryParams['model_strategy'] = modelStrategy;
    }

    final response = await _dio.post(
      '/v1/config/knowledge/ingest',
      data: formData,
      queryParameters: queryParams,
    );

    // API returns {"job_id": "..."}
    return response.data['job_id'] as String;
  }

  /// Polls the status of an active ingestion job.
  ///
  /// Takes the [jobId] returned by [uploadKnowledgeBase].
  /// Returns an [IngestionStatus] object containing the current progress, stage, and result.
  ///
  /// Throws [DioException] if the network request fails.
  Future<IngestionStatus> getIngestionStatus(String jobId) async {
    final response = await _dio.get('/v1/config/knowledge/ingest/$jobId');
    return IngestionStatus.fromJson(response.data);
  }

  /// Resets the knowledge base by clearing all items.
  Future<void> resetKnowledgeBase() async {
    await _dio.delete('/v1/config/knowledge/reset');
  }

  /// Fetches available model strategies from the backend.
  Future<List<KnowledgeModelStrategy>> getModels() async {
    // We reuse the generic /ids endpoint or /models if available.
    // The backend `list_models` returns List<LLMProviderConfig>.
    // We map that to KnowledgeModelStrategy.
    final response = await _dio.get('/v1/config/models');
    final List<dynamic> data = response.data;

    return data
        .map((e) => KnowledgeModelStrategy.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
