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
      'Positive 1: resolves apiUrl, environment, allowMockTokens, and 32-hex UUIDv7 mock user IDs from initialized .env',
      () {
        dotenv.loadFromString(
          envString: '''
API_URL=https://api.cognitivequorum.com
ENVIRONMENT=development
MOCK_ADMIN_USER_ID=usr_0195f3a00000700188a0d5f6151349a5
MOCK_ROOT_USER_ID=usr_0195f3a00000700a83fd6b3d77c748f4
MOCK_ANALYST_USER_ID=usr_0195f3a000007009836983a7a6c643ab
MOCK_MEMBER_USER_ID=usr_0195f3a0000070018c1cf9c5178846bb
MOCK_VIEWER_USER_ID=usr_0195f3a00000700b82d6e4487afc4e69
''',
        );

        final container = ProviderContainer();
        addTearDown(container.dispose);

        final envInstance = container.read(envProvider);
        expect(envInstance, isA<Env>());
        expect(Env.apiUrl, equals('https://api.cognitivequorum.com'));
        expect(Env.environment, equals('development'));
        expect(Env.allowMockTokens, isTrue);
        expect(
          Env.mockAdminUserId,
          equals('usr_0195f3a00000700188a0d5f6151349a5'),
        );
        expect(
          Env.mockRootUserId,
          equals('usr_0195f3a00000700a83fd6b3d77c748f4'),
        );
        expect(
          Env.mockAnalystUserId,
          equals('usr_0195f3a000007009836983a7a6c643ab'),
        );
        expect(
          Env.mockMemberUserId,
          equals('usr_0195f3a0000070018c1cf9c5178846bb'),
        );
        expect(
          Env.mockViewerUserId,
          equals('usr_0195f3a00000700b82d6e4487afc4e69'),
        );
      },
    );

    test(
      'Positive 2: allowMockTokens returns false when ENVIRONMENT is production',
      () {
        dotenv.loadFromString(
          envString: '''
API_URL=https://api.cognitivequorum.com
ENVIRONMENT=production
''',
        );

        expect(Env.environment, equals('production'));
        expect(Env.allowMockTokens, isFalse);
      },
    );

    test(
      'Negative/Boundary 1: throws AppException (VALIDATION_FAILED) when dotenv is not initialized or required variables are missing/blank',
      () {
        dotenv.clean();
        expect(Env.allowMockTokens, isFalse);

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
        expect(
          () => Env.mockAdminUserId,
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
      'Negative/Boundary 2: throws AppException (VALIDATION_FAILED) when mock user IDs violate 32-hex UUIDv7 format or usr_ prefix',
      () {
        dotenv.loadFromString(
          envString: '''
MOCK_ADMIN_USER_ID=usr_short16hex000000
MOCK_ROOT_USER_ID=wf_0195f3a00000700a83fd6b3d77c748f4
MOCK_ANALYST_USER_ID=invalid_id
MOCK_MEMBER_USER_ID=usr_0195f3a0000070018c1cf9c5178846bz
MOCK_VIEWER_USER_ID=usr_0195f3a00000700b82d6e4487afc4e690
''',
        );

        for (final getter in <String Function()>[
          () => Env.mockAdminUserId,
          () => Env.mockRootUserId,
          () => Env.mockAnalystUserId,
          () => Env.mockMemberUserId,
          () => Env.mockViewerUserId,
        ]) {
          expect(
            getter,
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
