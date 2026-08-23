import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';

void main() {
  group('MatrixClaim and TDAAssertion Unit & ISTQB Negative Partition Tests', () {
    test(
      'Positive: TDAAssertion.create generates 32 hex char ID matching regex',
      () {
        final tda = TDAAssertion.create(
          conceptDescription:
              'This is a valid concept description with >= 10 chars',
          inverseEvidence: false,
          aggregationMode: AggregationMode.exists,
        );

        final regex = RegExp(r'^tda_[a-f0-9]{32}$');
        expect(
          regex.hasMatch(tda.tdaId),
          isTrue,
          reason: 'tdaId must match ^tda_[a-f0-9]{32}\$, got ${tda.tdaId}',
        );
        expect(
          tda.conceptDescription,
          'This is a valid concept description with >= 10 chars',
        );
        expect(tda.inverseEvidence, isFalse);
        expect(tda.aggregationMode, AggregationMode.exists);
        expect(tda.evaluationTrack, EvaluationTrack.cognitiveJudgement);
        expect(tda.boundingBoxScope, 'paragraph');
      },
    );

    test(
      'Positive: MatrixClaim deserializes from JSON without ai_description',
      () {
        final json = {
          'label': {
            'default_locale': 'en',
            'translations': {
              'en': 'Strong performance across leadership criteria',
            },
          },
          'tda_assertions': [
            {
              'tda_id': 'tda_12345678901234567890123456789012',
              'concept_description':
                  'Executive presence exhibited during board sessions',
              'inverse_evidence': false,
              'aggregation_mode': 'EXISTS',
              'evaluation_track': 'COGNITIVE_JUDGEMENT',
              'bounding_box_scope': 'paragraph',
            },
          ],
        };

        final claim = MatrixClaim.fromJson(json);
        expect(claim.label.defaultLocale, 'en');
        expect(
          claim.label.translations['en'],
          'Strong performance across leadership criteria',
        );
        expect(claim.tdaAssertions.length, 1);
        expect(
          claim.tdaAssertions.first.tdaId,
          'tda_12345678901234567890123456789012',
        );
        expect(
          claim.tdaAssertions.first.conceptDescription,
          'Executive presence exhibited during board sessions',
        );
      },
    );

    test('Positive: SystemUiConstraints.tdaConceptMinLength equals 10', () {
      expect(SystemUiConstraints.tdaConceptMinLength.value, 10);
    });

    test(
      'Negative Partition 1: MatrixClaim.fromJson with legacy ai_description throws CheckedFromJsonException',
      () {
        final legacyJson = {
          'label': {
            'default_locale': 'en',
            'translations': {'en': 'Legacy Claim'},
          },
          'ai_description':
              'LEGACY RULE: Must fail fail-fast parser immediately',
          'tda_assertions': [],
        };

        expect(
          () => MatrixClaim.fromJson(legacyJson),
          throwsA(isA<CheckedFromJsonException>()),
          reason:
              'disallowUnrecognizedKeys must reject legacy ai_description field',
        );
      },
    );

    test(
      'Negative Partition 2: Boundary Value Analysis on concept length validator (9 vs 10 characters)',
      () {
        String? validateConcept(String? val) {
          if (val == null ||
              val.trim().length <
                  SystemUiConstraints.tdaConceptMinLength.value) {
            return 'Concept description must be at least ${SystemUiConstraints.tdaConceptMinLength.value} characters long.';
          }
          return null;
        }

        // Boundary: 9 characters (min - 1) -> Must FAIL
        final nineChars = '123456789';
        expect(nineChars.length, 9);
        expect(
          validateConcept(nineChars),
          'Concept description must be at least 10 characters long.',
        );

        // Boundary: 9 characters with whitespace trimming -> Must FAIL
        final whitespaceNine = '   123456789   ';
        expect(
          validateConcept(whitespaceNine),
          'Concept description must be at least 10 characters long.',
        );

        // Boundary: null or empty -> Must FAIL
        expect(validateConcept(null), isNotNull);
        expect(validateConcept(''), isNotNull);

        // Boundary: 10 characters (min) -> Must PASS
        final tenChars = '1234567890';
        expect(tenChars.length, 10);
        expect(validateConcept(tenChars), isNull);

        // Boundary: 11 characters (min + 1) -> Must PASS
        final elevenChars = '12345678901';
        expect(elevenChars.length, 11);
        expect(validateConcept(elevenChars), isNull);
      },
    );

    test(
      'Negative Partition 3: TDAAssertion.fromJson with missing required fields throws CheckedFromJsonException',
      () {
        // Missing required inverse_evidence and aggregation_mode
        final invalidTdaJson = {
          'tda_id': 'tda_12345678901234567890123456789012',
          'concept_description': 'Valid concept description string',
        };

        expect(
          () => TDAAssertion.fromJson(invalidTdaJson),
          throwsA(isA<CheckedFromJsonException>()),
          reason:
              'Missing non-null required fields in TDAAssertion must trigger CheckedFromJsonException',
        );
      },
    );
  });
}
