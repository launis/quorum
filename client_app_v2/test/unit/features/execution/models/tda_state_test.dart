import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

void main() {
  group('TDAState JSON Parsing & Union Serialization', () {
    test(
      'Positive: deserializes and roundtrips Pending, Evaluated, and Dlq variants cleanly',
      () {
        final pendingJson = <String, dynamic>{'runtimeType': 'pending'};
        final pending = TDAState.fromJson(pendingJson);
        expect(pending, isA<Pending>());
        expect(pending.toJson(), equals(pendingJson));

        final evaluatedJson = <String, dynamic>{
          'runtimeType': 'evaluated',
          'passed': true,
          'display_quote': 'Verbatim anchor text',
          'raw_anchor': 'anchor_01',
        };
        final evaluated = TDAState.fromJson(evaluatedJson);
        switch (evaluated) {
          case Evaluated(:final passed, :final displayQuote, :final rawAnchor):
            expect(passed, isTrue);
            expect(displayQuote, equals('Verbatim anchor text'));
            expect(rawAnchor, equals('anchor_01'));
          case Pending() || Dlq():
            fail('Expected Evaluated variant');
        }
        expect(evaluated.toJson(), equals(evaluatedJson));

        final dlqJson = <String, dynamic>{
          'runtimeType': 'dlq',
          'user_reason': 'Source document truncated',
          'backend_trace': 'TimeoutError at stage 2',
        };
        final dlq = TDAState.fromJson(dlqJson);
        switch (dlq) {
          case Dlq(:final userReason, :final backendTrace):
            expect(userReason, equals('Source document truncated'));
            expect(backendTrace, equals('TimeoutError at stage 2'));
          case Pending() || Evaluated():
            fail('Expected Dlq variant');
        }
        expect(dlq.toJson(), equals(dlqJson));
      },
    );

    test(
      'Negative 1: throws CheckedFromJsonException on unrecognized key (Fail-Fast)',
      () {
        final jsonWithUnknownKey = <String, dynamic>{
          'runtimeType': 'evaluated',
          'passed': true,
          'display_quote': 'Yes',
          'raw_anchor': '123',
          'hallucinated_key': 'this should crash',
        };

        expect(
          () => TDAState.fromJson(jsonWithUnknownKey),
          throwsA(isA<CheckedFromJsonException>()),
          reason:
              'TDAState should disallow unrecognized keys to enforce silent_json_fallbacks rule',
        );
      },
    );

    test(
      'Negative 2: throws CheckedFromJsonException on invalid runtimeType discriminator or missing required fields',
      () {
        final invalidDiscriminatorJson = <String, dynamic>{
          'runtimeType': 'unknown_variant',
        };
        expect(
          () => TDAState.fromJson(invalidDiscriminatorJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final missingRequiredFieldsJson = <String, dynamic>{
          'runtimeType': 'evaluated',
          'passed': true,
        };
        expect(
          () => TDAState.fromJson(missingRequiredFieldsJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final invalidFieldTypeJson = <String, dynamic>{
          'runtimeType': 'dlq',
          'user_reason': 12345,
          'backend_trace': 'trace',
        };
        expect(
          () => TDAState.fromJson(invalidFieldTypeJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
