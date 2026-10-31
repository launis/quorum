import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations_en.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  final l10n = AppLocalizationsEn();

  group('AppExceptionX.toLocalizedHint', () {
    test(
      'maps direct top-level error codes (NETWORK_FATAL, UNAUTHORIZED, CANCELLED, TIMEOUT)',
      () {
        expect(AppException.network().toLocalizedHint(l10n), l10n.errorNetwork);
        expect(
          const AppException(
            extensions: {'error_code': 'UNAUTHORIZED'},
          ).toLocalizedHint(l10n),
          l10n.errorUnauthorized,
        );
        expect(
          const AppException(
            status: 401,
            extensions: {'error_code': 'OTHER'},
          ).toLocalizedHint(l10n),
          l10n.errorUnauthorized,
        );
        expect(AppException.cancelled().toLocalizedHint(l10n), l10n.cancel);
        expect(
          AppException.timeout('Custom timeout detail').toLocalizedHint(l10n),
          'Custom timeout detail',
        );
      },
    );

    test('maps VALIDATION_FAILED with ambiguous_match and custom detail', () {
      const withCustomDetailAndMatch = AppException(
        status: 400,
        detail: 'Ambiguous file match',
        extensions: {
          'error_code': 'VALIDATION_FAILED',
          'ambiguous_match': {'filename': 'report.pdf'},
        },
      );
      expect(
        withCustomDetailAndMatch.toLocalizedHint(l10n),
        '${l10n.errValidationFailed}\n\nAmbiguous file match',
      );

      const withDefaultDetailAndMatch = AppException(
        status: 400,
        detail: 'Unknown error',
        extensions: {
          'error_code': 'VALIDATION_FAILED',
          'ambiguous_match': {'filename': 'report.pdf'},
        },
      );
      expect(
        withDefaultDetailAndMatch.toLocalizedHint(l10n),
        '${l10n.errValidationFailed}\n\n${l10n.actionHintCheckInput} (report.pdf)',
      );

      final withCustomDetail = AppException.validation('Field x is invalid');
      expect(
        withCustomDetail.toLocalizedHint(l10n),
        '${l10n.errValidationFailed}\n\n${l10n.actionHintCheckInput}\n\nField x is invalid',
      );

      const withDefaultDetail = AppException(
        status: 400,
        detail: 'Unknown error',
        extensions: {'error_code': 'VALIDATION_FAILED'},
      );
      expect(
        withDefaultDetail.toLocalizedHint(l10n),
        '${l10n.errValidationFailed}\n\n${l10n.actionHintCheckInput}',
      );
    });

    test('maps structured backend error codes across all domain categories', () {
      final cases = <String, String>{
        'INTERNAL_SERVER_ERROR':
            '${l10n.errorServer}\n\n${l10n.actionHintTryAgainLater}',
        'SSE_CONNECTION_ABORTED': l10n.errorSseConnectionAborted,
        'WORKFLOW_NOT_FOUND': l10n.errorNotFound,
        'WORKFLOW_EXECUTION_FAILED': l10n.errorServer,
        'MISSING_WORKFLOW_ID': l10n.fieldRequired,
        'WORKFLOW_CLONE_FAILED': l10n.workflowCloneErrorMissingDep,
        'AUTH_TOKEN_EXPIRED': l10n.errorUnauthorized,
        'PERMISSION_DENIED': l10n.errorUnauthorized,
        'AUTHENTICATION_FAILED':
            '${l10n.errAuthenticationFailed}\n\n${l10n.actionHintLoginAgain}',
        'INVALID_JSON_PAYLOAD': l10n.errorValidation,
        'UNSUPPORTED_CONTENT_TYPE': l10n.errorValidation,
        'KNOWLEDGE_INGESTION_FAILED': l10n.errorKnowledgeIngestionFailed,
        'KNOWLEDGE_RESET_FAILED': l10n.errorKnowledgeResetFailed,
        'KNOWLEDGE_RETRIEVAL_FAILED': l10n.errorKnowledgeRetrievalFailed,
        'KNOWLEDGE_NOT_INGESTED':
            '${l10n.errKnowledgeNotIngested}\n\n${l10n.actionHintRunIngestion}',
        'RESOURCE_IN_USE': l10n.errorResourceInUse,
        'SERVICE_UNAVAILABLE':
            '${l10n.errServiceUnavailable}\n\n${l10n.actionHintTryAgainLater}',
        'AGENT_EXECUTION_CRITICAL':
            '${l10n.errAgentExecutionCritical}\n\n${l10n.actionHintContactSupport}',
        'TOOL_EXECUTION_FAILED':
            '${l10n.toolExecutionFailed}\n\n${l10n.actionHintToolFailed}',
        'URL_INVALID': '${l10n.errorValidation}\n\n${l10n.actionHintCheckUrl}',
        'FETCH_FAILED':
            '${l10n.errorNetwork}\n\n${l10n.actionHintCheckConnection}',
        'DATA_CORRUPTION':
            '${l10n.errDataCorruptionDesc}\n\n${l10n.actionHintRunAgain}',
      };

      for (final entry in cases.entries) {
        final exc = AppException(
          status: 400,
          extensions: {'error_code': entry.key},
        );
        expect(
          exc.toLocalizedHint(l10n),
          entry.value,
          reason: 'Failed mapping for error_code=${entry.key}',
        );
      }
    });

    test(
      'negative & boundary: falls back to HTTP status codes (404, 499, 500, 503) when error_code is unrecognized',
      () {
        const notFoundExc = AppException(
          status: 404,
          extensions: {'error_code': 'UNRECOGNIZED_404'},
        );
        expect(
          notFoundExc.toLocalizedHint(l10n),
          '${l10n.errorNotFound}\n\n${l10n.actionHintContactSupport}',
        );

        const status499Exc = AppException(
          status: 499,
          extensions: {'error_code': 'UNRECOGNIZED_499'},
        );
        expect(status499Exc.toLocalizedHint(l10n), l10n.errorUnknown);

        const status500Exc = AppException(
          status: 500,
          extensions: {'error_code': 'UNRECOGNIZED_500'},
        );
        expect(status500Exc.toLocalizedHint(l10n), l10n.errorServer);

        const status503Exc = AppException(
          status: 503,
          extensions: {'error_code': 'UNRECOGNIZED_503'},
        );
        expect(status503Exc.toLocalizedHint(l10n), l10n.errorServer);

        const emptyTimeout = AppException(
          status: 408,
          detail: '',
          extensions: {'error_code': 'TIMEOUT'},
        );
        expect(emptyTimeout.toLocalizedHint(l10n), l10n.errorUnknown);
      },
    );
  });

  group('AppExceptionX.extractLocalizedHint', () {
    test(
      'extracts hint from direct AppException, CheckedFromJsonException, and DioException',
      () {
        final appExc = AppException.network();
        expect(
          AppExceptionX.extractLocalizedHint(appExc, l10n),
          l10n.errorNetwork,
        );

        Object? checkedWithAppExc;
        try {
          $checkedNew<String>(
            'Dto',
            const <String, Object?>{},
            () => throw AppException.unauthorized(),
          );
        } on CheckedFromJsonException catch (e) {
          checkedWithAppExc = e;
        }
        expect(
          AppExceptionX.extractLocalizedHint(checkedWithAppExc, l10n),
          l10n.errorUnauthorized,
        );

        final checkedGeneric = CheckedFromJsonException(
          const <String, Object?>{},
          'field',
          'Dto',
          'invalid',
        );
        expect(
          AppExceptionX.extractLocalizedHint(checkedGeneric, l10n),
          '${l10n.errValidationFailed}\n\n${l10n.actionHintCheckInput}',
        );

        final reqOpts = RequestOptions(path: '/api/v2/test');
        final dioWrappingAppExc = DioException(
          requestOptions: reqOpts,
          error: AppException.cancelled(),
        );
        expect(
          AppExceptionX.extractLocalizedHint(dioWrappingAppExc, l10n),
          l10n.cancel,
        );
      },
    );

    test(
      'negative & boundary: handles null, unknown objects, and all unwrapped DioExceptionTypes',
      () {
        expect(
          AppExceptionX.extractLocalizedHint(null, l10n),
          l10n.errorUnknown,
        );
        expect(
          AppExceptionX.extractLocalizedHint(StateError('unexpected'), l10n),
          l10n.errorUnknown,
        );

        final reqOpts = RequestOptions(path: '/api/v2/test');
        for (final netType in [
          DioExceptionType.connectionTimeout,
          DioExceptionType.receiveTimeout,
          DioExceptionType.sendTimeout,
          DioExceptionType.connectionError,
          DioExceptionType.transformTimeout,
          DioExceptionType.badCertificate,
        ]) {
          expect(
            AppExceptionX.extractLocalizedHint(
              DioException(requestOptions: reqOpts, type: netType),
              l10n,
            ),
            l10n.errorNetwork,
          );
        }

        expect(
          AppExceptionX.extractLocalizedHint(
            DioException(
              requestOptions: reqOpts,
              type: DioExceptionType.cancel,
            ),
            l10n,
          ),
          l10n.cancel,
        );
        expect(
          AppExceptionX.extractLocalizedHint(
            DioException(
              requestOptions: reqOpts,
              type: DioExceptionType.badResponse,
            ),
            l10n,
          ),
          l10n.errorServer,
        );
        expect(
          AppExceptionX.extractLocalizedHint(
            DioException(
              requestOptions: reqOpts,
              type: DioExceptionType.unknown,
            ),
            l10n,
          ),
          l10n.errorUnknown,
        );
      },
    );
  });
}
