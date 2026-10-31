import 'dart:convert';

import 'package:client_app/features/execution/models/execution_summary_snapshot.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionSummarySnapshot Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: ExecutionSummarySnapshot deserializes full payload and roundtrips cleanly',
      () {
        final rawPayload = <String, Object?>{
          'strictness_level': 85,
          'is_ensemble_run': true,
          'is_degraded': true,
          'system_concurrency_snapshot': <String, int>{
            'max_concurrent_llm_calls': 4,
            'active_workers': 2,
          },
        };

        final snapshot = ExecutionSummarySnapshot.fromJson(rawPayload);

        expect(snapshot.strictnessLevel, equals(85));
        expect(snapshot.isEnsembleRun, isTrue);
        expect(snapshot.isDegraded, isTrue);
        expect(
          snapshot.systemConcurrencySnapshot,
          equals(<String, int>{
            'max_concurrent_llm_calls': 4,
            'active_workers': 2,
          }),
        );

        final roundtrippedMap =
            jsonDecode(jsonEncode(snapshot.toJson())) as Map<String, Object?>;
        final roundtripped = ExecutionSummarySnapshot.fromJson(roundtrippedMap);

        expect(roundtripped.strictnessLevel, equals(85));
        expect(roundtripped.isEnsembleRun, isTrue);
        expect(roundtripped.isDegraded, isTrue);
        expect(
          roundtripped.systemConcurrencySnapshot['max_concurrent_llm_calls'],
          equals(4),
        );
        expect(
          roundtripped.systemConcurrencySnapshot['active_workers'],
          equals(2),
        );
      },
    );

    test(
      'Positive 2 (Boundary & Defaults): applies deterministic defaults on empty payload and accepts boundary 0 strictnessLevel',
      () {
        final defaultSnapshot = ExecutionSummarySnapshot.fromJson(
          <String, Object?>{},
        );

        expect(defaultSnapshot.strictnessLevel, equals(100));
        expect(defaultSnapshot.isEnsembleRun, isFalse);
        expect(defaultSnapshot.isDegraded, isFalse);
        expect(defaultSnapshot.systemConcurrencySnapshot, isEmpty);

        final zeroBoundarySnapshot = ExecutionSummarySnapshot.fromJson(
          <String, Object?>{'strictness_level': 0},
        );
        expect(zeroBoundarySnapshot.strictnessLevel, equals(0));
      },
    );

    test(
      'Negative 1: rejects unrecognized JSON keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'strictness_level': 100,
          'is_ensemble_run': false,
          'unrecognized_legacy_field': 'forbidden',
        };

        expect(
          () => ExecutionSummarySnapshot.fromJson(payloadWithExtraKey),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'Negative 2 (ISTQB Type & Boundary Violations): rejects invalid types for strictnessLevel, flags, and concurrency map',
      () {
        // String instead of int for strictness_level
        expect(
          () => ExecutionSummarySnapshot.fromJson(<String, Object?>{
            'strictness_level': 'high',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // int instead of bool for is_ensemble_run
        expect(
          () => ExecutionSummarySnapshot.fromJson(<String, Object?>{
            'is_ensemble_run': 1,
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // Non-int values inside system_concurrency_snapshot map
        expect(
          () => ExecutionSummarySnapshot.fromJson(<String, Object?>{
            'system_concurrency_snapshot': <String, Object?>{
              'max_concurrent_llm_calls': 'four',
            },
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );
      },
    );
  });
}
