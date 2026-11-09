import 'package:client_app/core/environment/env.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  tearDown(() {
    dotenv.clean();
  });

  group('Env Hardening Tests (Profile A)', () {
    test(
      'Positive 1: resolves trimmed apiUrl and environment from initialized .env and provides Env instance',
      () {
        dotenv.loadFromString(
          envString: '''
API_URL=  https://api.cognitivequorum.com  
ENVIRONMENT=  development  
''',
        );

        final container = ProviderContainer();
        addTearDown(container.dispose);

        final envInstance = container.read(envProvider);
        expect(envInstance, isA<Env>());
        expect(Env.apiUrl, equals('https://api.cognitivequorum.com'));
        expect(Env.environment, equals('development'));
      },
    );

    test('Positive 2: resolves production environment and custom API URL', () {
      dotenv.loadFromString(
        envString: '''
API_URL=https://api.qrum.ai
ENVIRONMENT=production
''',
      );

      expect(Env.apiUrl, equals('https://api.qrum.ai'));
      expect(Env.environment, equals('production'));
    });

    test(
      'test_env_throws_app_exception_when_required_api_url_or_environment_missing',
      () {
        dotenv.clean();

        expect(
          () => Env.apiUrl,
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              'VALIDATION_FAILED',
            ),
          ),
        );

        dotenv.loadFromString(envString: 'ENVIRONMENT=development\n');
        expect(
          () => Env.apiUrl,
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              'VALIDATION_FAILED',
            ),
          ),
        );

        dotenv.loadFromString(envString: 'API_URL=https://api.qrum.ai\n');
        expect(
          () => Env.environment,
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
      'Negative/Boundary 2: throws AppException (VALIDATION_FAILED) when API_URL or ENVIRONMENT is empty or whitespace-only',
      () {
        dotenv.loadFromString(envString: 'API_URL=   \nENVIRONMENT=\n');

        expect(
          () => Env.apiUrl,
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              'VALIDATION_FAILED',
            ),
          ),
        );
        expect(
          () => Env.environment,
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
  });
}
