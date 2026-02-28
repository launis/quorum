//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'dart:async';

// ignore: unused_import
import 'dart:convert';
import 'package:backend_api/src/deserialize.dart';
import 'package:dio/dio.dart';

import 'package:backend_api/src/model/audit_event.dart';
import 'package:backend_api/src/model/http_validation_error.dart';

class AuditApi {
  final Dio _dio;

  const AuditApi(this._dio);

  /// Get Audit Logs
  /// Retrieve audit logs.  Role Rules: - ROOT: Can see logs for ANY organization or system-wide (if org_id is None). - ADMIN: Can ONLY see logs for THEIR OWN organization. - MEMBER: Cannot see audit logs (403).
  ///
  /// Parameters:
  /// * [organizationId] - Filter by Organization ID
  /// * [actorId] - Filter by Actor UID
  /// * [action] - Filter by Action type
  /// * [limit]
  /// * [authorization]
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [List<AuditEvent>] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<List<AuditEvent>>> getAuditLogsAuditLogsGet({
    String? organizationId,
    String? actorId,
    String? action,
    int? limit = 100,
    String? authorization,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/audit/logs';
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{r'authorization': authorization, ...?headers},
      extra: <String, dynamic>{'secure': <Map<String, String>>[], ...?extra},
      validateStatus: validateStatus,
    );

    final _queryParameters = <String, dynamic>{
      r'organization_id': organizationId,
      r'actor_id': actorId,
      r'action': action,
      if (limit != null) r'limit': limit,
    };

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      queryParameters: _queryParameters,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    List<AuditEvent>? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<List<AuditEvent>, AuditEvent>(
              rawData,
              'List<AuditEvent>',
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

    return Response<List<AuditEvent>>(
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
