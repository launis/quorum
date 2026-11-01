import 'package:client_app/core/error/app_exception.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('AppException RFC 7807 Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: deserializes full RFC 7807 Problem Details JSON and roundtrips via toJson',
      () {
        final rawJson = <String, Object?>{
          'type': 'https://api.quorum.fi/errors/execution-not-found',
          'title': 'Execution Not Found',
          'status': 404,
          'detail': 'Execution exe_0195f3a0000070008000000000000001 not found.',
          'instance':
              '/api/v2/execution/executions/exe_0195f3a0000070008000000000000001',
          'request_id': 'req_0195f3a0000070008000000000000099',
          'extensions': <String, Object?>{
            'error_code': 'EXECUTION_NOT_FOUND',
            'resource_type': 'Execution',
          },
        };

        final exception = AppException.fromJson(rawJson);

        expect(
          exception.type,
          equals('https://api.quorum.fi/errors/execution-not-found'),
        );
        expect(exception.title, equals('Execution Not Found'));
        expect(exception.status, equals(404));
        expect(
          exception.detail,
          equals('Execution exe_0195f3a0000070008000000000000001 not found.'),
        );
        expect(
          exception.instance,
          equals(
            '/api/v2/execution/executions/exe_0195f3a0000070008000000000000001',
          ),
        );
        expect(
          exception.requestId,
          equals('req_0195f3a0000070008000000000000099'),
        );
        expect(exception.errorCode, equals('EXECUTION_NOT_FOUND'));

        final serialized = exception.toJson();
        expect(serialized['request_id'], equals(exception.requestId));
        expect(serialized['status'], equals(404));
        expect(serialized['extensions'], equals(rawJson['extensions']));
      },
    );

    test(
      'Positive 2: domain factory constructors populate canonical RFC 7807 status codes and error codes',
      () {
        final netDefault = AppException.network();
        expect(netDefault.status, equals(0));
        expect(netDefault.errorCode, equals('NETWORK_FATAL'));
        expect(netDefault.detail, equals('Network connection failed.'));

        final netCustom = AppException.network('Socket closed');
        expect(netCustom.detail, equals('Socket closed'));

        final unknownDefault = AppException.unknown();
        expect(unknownDefault.status, equals(500));
        expect(unknownDefault.errorCode, equals('UNKNOWN_ERROR'));
        expect(unknownDefault.detail, equals('An unknown error occurred.'));

        final serverErr = AppException.server(
          'Upstream gateway error',
          statusCode: 503,
        );
        expect(serverErr.status, equals(503));
        expect(serverErr.errorCode, equals('SERVER_ERROR'));

        final unauthorizedErr = AppException.unauthorized();
        expect(unauthorizedErr.status, equals(401));
        expect(unauthorizedErr.errorCode, equals('AUTHENTICATION_FAILED'));

        final notFoundErr = AppException.notFound('Workflow missing');
        expect(notFoundErr.status, equals(404));
        expect(notFoundErr.errorCode, equals('RESOURCE_NOT_FOUND'));

        final cancelledErr = AppException.cancelled();
        expect(cancelledErr.status, equals(499));
        expect(cancelledErr.errorCode, equals('CANCELLED'));

        final timeoutDefault = AppException.timeout();
        expect(timeoutDefault.status, equals(408));
        expect(timeoutDefault.errorCode, equals('TIMEOUT'));
        expect(timeoutDefault.detail, equals('The request timed out.'));

        final timeoutCustom = AppException.timeout('Read timed out after 30s');
        expect(timeoutCustom.detail, equals('Read timed out after 30s'));

        final validationErr = AppException.validation('Invalid field value');
        expect(validationErr.status, equals(400));
        expect(validationErr.errorCode, equals('VALIDATION_FAILED'));
      },
    );

    test(
      'Negative 1: disallowUnrecognizedKeys rejects unknown top-level JSON fields and invalid field types with CheckedFromJsonException',
      () {
        final unrecognizedKeyJson = <String, Object?>{
          'type': 'https://api.quorum.fi/errors/validation-failed',
          'title': 'Validation Error',
          'status': 400,
          'detail': 'Invalid input',
          'unexpected_shadow_field': 'forbidden',
        };

        expect(
          () => AppException.fromJson(unrecognizedKeyJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidStatusTypeJson = <String, Object?>{
          'type': 'https://api.quorum.fi/errors/server-error',
          'status': '500_as_string',
        };

        expect(
          () => AppException.fromJson(invalidStatusTypeJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2 (ISTQB Boundary Value Analysis): errorCode derives uppercase slug when extensions lack valid error_code or falls back to UNKNOWN_ERROR on blank/empty URIs',
      () {
        // Slug extraction when extensions is empty
        const slugDerived = AppException(
          type: 'https://api.quorum.fi/errors/workflow-compilation-error',
        );
        expect(slugDerived.errorCode, equals('WORKFLOW_COMPILATION_ERROR'));

        // Null or whitespace error_code in extensions falls back to URI slug
        const nullExtCode = AppException(
          type: 'https://api.quorum.fi/errors/token-limit-exceeded',
          extensions: <String, Object?>{'error_code': null},
        );
        expect(nullExtCode.errorCode, equals('TOKEN_LIMIT_EXCEEDED'));

        const blankExtCode = AppException(
          type: 'https://api.quorum.fi/errors/rate-limit-exceeded',
          extensions: <String, Object?>{'error_code': '   '},
        );
        expect(blankExtCode.errorCode, equals('RATE_LIMIT_EXCEEDED'));

        // Default 'about:blank' and trailing-slash empty slug boundaries -> UNKNOWN_ERROR
        const defaultBlank = AppException();
        expect(defaultBlank.errorCode, equals('UNKNOWN_ERROR'));

        const emptyType = AppException(type: '');
        expect(emptyType.errorCode, equals('UNKNOWN_ERROR'));

        const trailingSlashType = AppException(
          type: 'https://api.quorum.fi/errors/',
        );
        expect(trailingSlashType.errorCode, equals('UNKNOWN_ERROR'));
      },
    );
  });
}
