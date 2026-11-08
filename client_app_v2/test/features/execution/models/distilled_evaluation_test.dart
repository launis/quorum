import 'dart:convert';

import 'package:client_app/features/execution/models/distilled_evaluation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('DistilledEvaluation & DistilledExtensionValue JSON Parsing', () {
    test(
      'MUST fail to parse if exact_quotes is missing (strict fallback ban)',
      () {
        final json = <String, Object?>{
          'atom_id': 'blk_123',
          // 'exact_quotes' is explicitly missing
          'semantic_reasoning': 'Because reasons',
        };

        expect(
          () => DistilledEvaluation.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'MUST fail to parse when unrecognized keys are present (disallowUnrecognizedKeys: true)',
      () {
        final json = <String, Object?>{
          'atom_id': 'blk_123',
          'exact_quotes': <String>['Quote 1'],
          'unexpected_legacy_field': 'forbidden',
        };

        expect(
          () => DistilledEvaluation.fromJson(json),
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
      'MUST fail to parse when exact_quotes or topological_out_degree violates type boundary',
      () {
        expect(
          () => DistilledEvaluation.fromJson(<String, Object?>{
            'atom_id': 'blk_123',
            'exact_quotes': 42,
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        expect(
          () => DistilledEvaluation.fromJson(<String, Object?>{
            'atom_id': 'blk_123',
            'exact_quotes': <String>['Quote 1'],
            'topological_out_degree': 'not_an_int',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );
      },
    );

    test(
      'MUST fail to parse when extension value is an unsupported nested map or non-string list item',
      () {
        expect(
          () => DistilledEvaluation.fromJson(<String, Object?>{
            'atom_id': 'blk_123',
            'exact_quotes': <String>['Quote 1'],
            'extensions': <String, Object?>{
              'nested_object': <String, Object?>{'invalid': true},
            },
          }),
          throwsA(
            anyOf(isA<CheckedFromJsonException>(), isA<FormatException>()),
          ),
        );

        expect(
          () => DistilledEvaluation.fromJson(<String, Object?>{
            'atom_id': 'blk_123',
            'exact_quotes': <String>['Quote 1'],
            'extensions': <String, Object?>{
              'bad_list': <Object?>['valid', 123],
            },
          }),
          throwsA(
            anyOf(isA<CheckedFromJsonException>(), isA<FormatException>()),
          ),
        );
      },
    );

    test(
      'MUST successfully parse and roundtrip full payload including extensions and topological lineage fields',
      () {
        final json = <String, Object?>{
          'atom_id': 'blk_123',
          'exact_quotes': <String>['Quote 1'],
          'semantic_reasoning': 'Because reasons',
          'status': 'PASSED',
          'extensions': <String, Object?>{
            'label': 'High confidence',
            'score': 0.95,
            'verified': true,
            'tags': <String>['anchor', 'grounded'],
          },
          'depends_on_tda_ids': <String>['tda_1'],
          'short_circuit_reason_tda_ids': <String>['tda_0'],
          'is_inverse_evidence': true,
          'topological_out_degree': 3,
        };

        final eval = DistilledEvaluation.fromJson(json);
        expect(eval.atomId, equals('blk_123'));
        expect(eval.exactQuotes, equals(<String>['Quote 1']));
        expect(eval.semanticReasoning, equals('Because reasons'));
        expect(eval.status, equals('PASSED'));
        expect(eval.extensions?['label']?.rawValue, equals('High confidence'));
        expect(eval.extensions?['score']?.rawValue, equals(0.95));
        expect(eval.extensions?['verified']?.rawValue, isTrue);
        expect(
          eval.extensions?['tags']?.rawValue,
          equals(<String>['anchor', 'grounded']),
        );
        expect(eval.dependsOnTdaIds, equals(<String>['tda_1']));
        expect(eval.shortCircuitReasonTdaIds, equals(<String>['tda_0']));
        expect(eval.isInverseEvidence, isTrue);
        expect(eval.topologicalOutDegree, equals(3));

        final roundtripped = DistilledEvaluation.fromJson(
          jsonDecode(jsonEncode(eval.toJson())) as Map<String, Object?>,
        );
        expect(roundtripped.atomId, equals('blk_123'));
        expect(roundtripped.topologicalOutDegree, equals(3));
        expect(
          roundtripped.extensions?['tags']?.stringListValue,
          equals(<String>['anchor', 'grounded']),
        );
      },
    );

    test('MUST support O(1) list equality via @Freezed(equal: false)', () {
      final eval1 = DistilledEvaluation(atomId: 'blk_123', exactQuotes: ['A']);
      final eval2 = DistilledEvaluation(atomId: 'blk_123', exactQuotes: ['A']);
      const ext1 = DistilledExtensionValue(stringListValue: <String>['A']);
      const ext2 = DistilledExtensionValue(stringListValue: <String>['A']);

      // If equal: false is set, non-const instances are compared by identity, not deep list equality.
      expect(eval1 == eval2, isFalse);
      expect(
        DistilledExtensionValue(stringListValue: <String>['A']) ==
            DistilledExtensionValue(stringListValue: <String>['A']),
        isFalse,
      );
      expect(identical(ext1, ext2), isTrue);
    });
  });
}
