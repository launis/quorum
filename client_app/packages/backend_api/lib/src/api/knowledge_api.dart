//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'dart:async';

// ignore: unused_import
import 'dart:convert';
import 'package:backend_api/src/deserialize.dart';
import 'package:dio/dio.dart';

import 'package:backend_api/src/model/http_validation_error.dart';
import 'package:backend_api/src/model/knowledge_ingest_response.dart';
import 'package:backend_api/src/model/knowledge_job_status_response.dart';
import 'package:backend_api/src/model/knowledge_reset_response.dart';
import 'package:backend_api/src/model/knowledge_status_response.dart';

class KnowledgeApi {
  final Dio _dio;

  const KnowledgeApi(this._dio);

  /// Get Ingestion Status
  /// Polls the status of an ingestion job.  Args:     job_id (str): The unique identifier of the ingestion job.  Returns:     KnowledgeJobStatusResponse: The current state of the job (status, progress, stage, result, error).  Raises:     AppException: If the job_id is not found (404 JOB_NOT_FOUND).
  ///
  /// Parameters:
  /// * [jobId]
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [KnowledgeJobStatusResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<KnowledgeJobStatusResponse>>
  getIngestionStatusV1ConfigKnowledgeIngestJobIdGet({
    required String jobId,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/v1/config/knowledge/ingest/{job_id}'.replaceAll(
      '{'
      r'job_id'
      '}',
      jobId.toString(),
    );
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      validateStatus: validateStatus,
    );

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    KnowledgeJobStatusResponse? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<KnowledgeJobStatusResponse, KnowledgeJobStatusResponse>(
              rawData,
              'KnowledgeJobStatusResponse',
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

    return Response<KnowledgeJobStatusResponse>(
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

  /// Get Knowledge Status
  /// Checks the status of the Knowledge Base.  Returns:     KnowledgeStatusResponse: Contains a boolean indicating if documents exist,                              and counts of documents and precedents.
  ///
  /// Parameters:
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [KnowledgeStatusResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<KnowledgeStatusResponse>>
  getKnowledgeStatusV1ConfigKnowledgeStatusGet({
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/v1/config/knowledge/status';
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      validateStatus: validateStatus,
    );

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    KnowledgeStatusResponse? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<KnowledgeStatusResponse, KnowledgeStatusResponse>(
              rawData,
              'KnowledgeStatusResponse',
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

    return Response<KnowledgeStatusResponse>(
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

  /// Ingest Knowledge Base
  /// Starts an asynchronous knowledge base ingestion job.  This endpoint accepts a file upload (DOCX or MD), initiates an asynchronous processing task, and returns a job ID for polling status.  Args:     background_tasks (BackgroundTasks): FastAPI background task manager.     file (UploadFile): The file to ingest (docx, md).     service (KnowledgeBaseServiceDep): The knowledge base service dependency.     language (str): Language code of the document (e.g. &#39;en&#39;, &#39;fi&#39;, &#39;auto&#39;).                   Defaults to \&quot;auto\&quot;.  Returns:     KnowledgeIngestResponse: A generic response containing the &#39;job_id&#39;.
  ///
  /// Parameters:
  /// * [file]
  /// * [language]
  /// * [modelStrategy]
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [KnowledgeIngestResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<KnowledgeIngestResponse>>
  ingestKnowledgeBaseV1ConfigKnowledgeIngestPost({
    required MultipartFile file,
    String? language = 'auto',
    String? modelStrategy,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/v1/config/knowledge/ingest';
    final _options = Options(
      method: r'POST',
      headers: <String, dynamic>{...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      contentType: 'multipart/form-data',
      validateStatus: validateStatus,
    );

    final _queryParameters = <String, dynamic>{
      if (language != null) r'language': language,
      r'model_strategy': modelStrategy,
    };

    dynamic _bodyData;

    try {} catch (error, stackTrace) {
      throw DioException(
        requestOptions: _options.compose(
          _dio.options,
          _path,
          queryParameters: _queryParameters,
        ),
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    final _response = await _dio.request<Object>(
      _path,
      data: _bodyData,
      options: _options,
      queryParameters: _queryParameters,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    KnowledgeIngestResponse? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<KnowledgeIngestResponse, KnowledgeIngestResponse>(
              rawData,
              'KnowledgeIngestResponse',
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

    return Response<KnowledgeIngestResponse>(
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

  /// Reset Knowledge Base
  /// Resets the Knowledge Base by deleting all items.  Args:     service (KnowledgeBaseServiceDep): The knowledge base service dependency.  Returns:     KnowledgeResetResponse: Success message.
  ///
  /// Parameters:
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [KnowledgeResetResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<KnowledgeResetResponse>>
  resetKnowledgeBaseV1ConfigKnowledgeResetDelete({
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/v1/config/knowledge/reset';
    final _options = Options(
      method: r'DELETE',
      headers: <String, dynamic>{...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      validateStatus: validateStatus,
    );

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    KnowledgeResetResponse? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<KnowledgeResetResponse, KnowledgeResetResponse>(
              rawData,
              'KnowledgeResetResponse',
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

    return Response<KnowledgeResetResponse>(
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
