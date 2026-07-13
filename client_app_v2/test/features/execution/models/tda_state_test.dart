import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/tda_state.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

void main() {
  group('TDAState JSON Parsing', () {
    test('Throws CheckedFromJsonException on unrecognized key (Fail-Fast)', () {
      final jsonWithUnknownKey = {
        'runtimeType': 'evaluated',
        'passed': true,
        'displayQuote': 'Yes',
        'rawAnchor': '123',
        'hallucinated_key': 'this should crash',
      };

      expect(
        () => TDAState.fromJson(jsonWithUnknownKey),
        throwsA(isA<CheckedFromJsonException>()),
        reason: 'TDAState should disallow unrecognized keys to enforce silent_json_fallbacks rule',
      );
    });
  });
}
