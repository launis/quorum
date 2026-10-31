import 'dart:convert';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('safeIsolateRun Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: executes heavy JSON decoding and transformation in isolate and resolves typed payload',
      () async {
        const rawPayload = '{"count": 3, "items": ["alpha", "beta", "gamma"]}';

        final decoded = await safeIsolateRun<Map<String, Object?>>(() {
          final parsed = jsonDecode(rawPayload) as Map<String, Object?>;
          return parsed;
        });

        expect(decoded['count'], equals(3));
        expect(decoded['items'], equals(<String>['alpha', 'beta', 'gamma']));
      },
    );

    test(
      'Positive 2: resolves boundary scalar values, empty collections, and nullable return types accurately',
      () async {
        final zeroResult = await safeIsolateRun<int>(() => 0);
        expect(zeroResult, equals(0));

        final negativeBoundary = await safeIsolateRun<int>(() => -1);
        expect(negativeBoundary, equals(-1));

        final maxInt64Boundary = await safeIsolateRun<int>(
          () => 9223372036854775807,
        );
        expect(maxInt64Boundary, equals(9223372036854775807));

        final emptyList = await safeIsolateRun<List<String>>(() => <String>[]);
        expect(emptyList, isEmpty);

        final nullResult = await safeIsolateRun<String?>(() => null);
        expect(nullResult, isNull);
      },
    );

    test(
      'Negative 1: propagates FormatException and AppException thrown inside computation without swallowing errors',
      () async {
        await expectLater(
          () => safeIsolateRun<Map<String, Object?>>(
            () => jsonDecode('{malformed_json') as Map<String, Object?>,
          ),
          throwsA(isA<FormatException>()),
        );

        await expectLater(
          () => safeIsolateRun<String>(
            () => throw AppException.validation(
              'Fail-Fast: Invalid isolate input payload.',
            ),
          ),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );

    test(
      'Negative 2 (ISTQB Boundary Value Analysis): propagates RangeError on out-of-bounds index access (min - 1 and max + 1)',
      () async {
        const items = <int>[10, 20, 30];

        // Boundary min - 1 (index -1)
        await expectLater(
          () => safeIsolateRun<int>(() => items[-1]),
          throwsA(isA<RangeError>()),
        );

        // Boundary max + 1 (index == length)
        await expectLater(
          () => safeIsolateRun<int>(() => items[items.length]),
          throwsA(isA<RangeError>()),
        );
      },
    );
  });
}
