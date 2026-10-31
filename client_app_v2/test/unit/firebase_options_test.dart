import 'package:client_app/firebase_options.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  tearDown(() {
    debugDefaultTargetPlatformOverride = null;
  });

  group('DefaultFirebaseOptions Hardening Tests', () {
    test(
      'Positive 1: currentPlatform and forPlatform resolve canonical FirebaseOptions across supported native and web platforms',
      () {
        for (final entry in {
          TargetPlatform.windows: DefaultFirebaseOptions.windows,
          TargetPlatform.android: DefaultFirebaseOptions.android,
          TargetPlatform.iOS: DefaultFirebaseOptions.ios,
          TargetPlatform.macOS: DefaultFirebaseOptions.macos,
        }.entries) {
          debugDefaultTargetPlatformOverride = entry.key;
          final resolved = DefaultFirebaseOptions.currentPlatform;

          expect(resolved, same(entry.value));
          expect(resolved.projectId, equals('cognitive-quorum'));
          expect(resolved.apiKey, isNotEmpty);
          expect(resolved.appId, isNotEmpty);
          expect(resolved.messagingSenderId, equals('943560988580'));
        }

        final webResolved = DefaultFirebaseOptions.forPlatform(
          TargetPlatform.windows,
          isWeb: true,
        );
        expect(webResolved, same(DefaultFirebaseOptions.web));
        expect(
          webResolved.authDomain,
          equals('cognitive-quorum.firebaseapp.com'),
        );
      },
    );

    test(
      'Negative/Boundary 1: currentPlatform and forPlatform throw UnsupportedError on unconfigured TargetPlatform.linux',
      () {
        debugDefaultTargetPlatformOverride = TargetPlatform.linux;

        expect(
          () => DefaultFirebaseOptions.currentPlatform,
          throwsA(
            isA<UnsupportedError>().having(
              (e) => e.message,
              'message',
              contains('have not been configured for linux'),
            ),
          ),
        );

        expect(
          () => DefaultFirebaseOptions.forPlatform(
            TargetPlatform.linux,
            isWeb: false,
          ),
          throwsA(
            isA<UnsupportedError>().having(
              (e) => e.message,
              'message',
              contains('have not been configured for linux'),
            ),
          ),
        );
      },
    );

    test(
      'Negative/Boundary 2: currentPlatform throws UnsupportedError on TargetPlatform.fuchsia while isWeb=true overrides unsupported native platform',
      () {
        debugDefaultTargetPlatformOverride = TargetPlatform.fuchsia;

        expect(
          () => DefaultFirebaseOptions.currentPlatform,
          throwsA(
            isA<UnsupportedError>().having(
              (e) => e.message,
              'message',
              contains('are not supported for this platform'),
            ),
          ),
        );

        expect(
          DefaultFirebaseOptions.forPlatform(
            TargetPlatform.fuchsia,
            isWeb: true,
          ),
          same(DefaultFirebaseOptions.web),
        );
      },
    );
  });
}
