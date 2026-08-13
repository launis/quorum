import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/distilled_evaluation.dart';

void main() {
  group('DistilledEvaluation JSON Parsing', () {
    test(
      'MUST fail to parse if exact_quotes is missing (strict fallback ban)',
      () {
        final Map<String, dynamic> json = {
          'atom_id': 'blk_123',
          // 'exact_quotes' is explicitly missing
          'semantic_reasoning': 'Because reasons',
        };

        expect(
          () => DistilledEvaluation.fromJson(json),
          throwsA(anything),
        );
      },
    );

    test('MUST successfully parse when exact_quotes is provided', () {
      final Map<String, dynamic> json = {
        'atom_id': 'blk_123',
        'exact_quotes': ['Quote 1'],
        'semantic_reasoning': 'Because reasons',
        'extensions': null,
      };

      final eval = DistilledEvaluation.fromJson(json);
      expect(eval.exactQuotes, ['Quote 1']);
    });

    test('MUST support O(1) list equality via @Freezed(equal: false)', () {
      final eval1 = DistilledEvaluation(atomId: 'blk_123', exactQuotes: ['A']);
      final eval2 = DistilledEvaluation(atomId: 'blk_123', exactQuotes: ['A']);

      // If equal: false is set, the instances are not equal by value, they are equal by reference.
      expect(eval1 == eval2, false);
    });
  });
}
