import 'package:client_app/app_config.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  tearDown(() {
    dotenv.clean();
  });

  group('AppConfig Hardening Tests', () {
    test(
      'Positive 1: apiBaseUrl resolves normalized URL from Env.apiUrl and strips trailing slashes',
      () {
        dotenv.loadFromString(
          envString: 'API_URL=https://api.cognitivequorum.com///\n',
        );

        expect(AppConfig.apiBaseUrl, equals('https://api.cognitivequorum.com'));
      },
    );

    test(
      'Positive 2: validateApiBaseUrl accepts valid http and https URIs with subpaths',
      () {
        expect(
          AppConfig.validateApiBaseUrl(
            'https://staging.cognitivequorum.com/v2/',
          ),
          equals('https://staging.cognitivequorum.com/v2'),
        );
        expect(
          AppConfig.validateApiBaseUrl('http://internal.cognitivequorum.local'),
          equals('http://internal.cognitivequorum.local'),
        );
      },
    );

    test(
      'Negative/Boundary 1: apiBaseUrl throws AppException (VALIDATION_FAILED) when dotenv is not initialized',
      () {
        dotenv.clean();

        expect(
          () => AppConfig.apiBaseUrl,
          throwsA(
            isA<AppException>()
                .having((e) => e.errorCode, 'errorCode', 'VALIDATION_FAILED')
                .having((e) => e.detail, 'detail', contains('not initialized')),
          ),
        );
      },
    );

    test(
      'Negative/Boundary 2: apiBaseUrl throws AppException (VALIDATION_FAILED) when API_URL is missing or whitespace',
      () {
        dotenv.loadFromString(envString: 'ENVIRONMENT=development\n');

        expect(
          () => AppConfig.apiBaseUrl,
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              'VALIDATION_FAILED',
            ),
          ),
        );

        dotenv.loadFromString(envString: 'API_URL=   \n');

        expect(
          () => AppConfig.apiBaseUrl,
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              'VALIDATION_FAILED',
            ),
          ),
        );
      },
    );

    test(
      'Negative/Boundary 3: validateApiBaseUrl throws AppException (VALIDATION_FAILED) on invalid scheme, missing scheme, or empty host',
      () {
        for (final invalidInput in const [
          'ftp://files.cognitivequorum.com',
          'api.cognitivequorum.com',
          'https://',
          '///',
        ]) {
          expect(
            () => AppConfig.validateApiBaseUrl(invalidInput),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                'VALIDATION_FAILED',
              ),
            ),
          );
        }
      },
    );
  });
}
