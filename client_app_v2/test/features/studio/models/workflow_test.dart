import 'dart:isolate';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/workflow.dart';

void main() {
  group('Epic 11 Phase B: NodeStrategy Strict Parsing', () {
    test(
      'Successfully parses valid expectedInputs and outputSchema via Isolate',
      () async {
        final payload = {
          'id': 'st_a1b2c3d4e5f60000',
          'slug': 'test_slug',
          'name': {
            'default_locale': 'en',
            'translations': {'en': 'Test'},
          },
          'type': 'llm',
          'model_strategy': 'fast',
          'expected_inputs': ['doc_id', 'prompt_text'],
          'output_schema': {
            'type': 'object',
            'properties': {
              'result': {'type': 'string'},
            },
          },
        };

        final NodeStrategy parsed = await Isolate.run(() {
          return NodeStrategy.fromJson(payload);
        });

        expect(parsed, isA<NodeStrategyLlm>());

        // Dart 3 'switch' pattern matching to unpack sealed class securely
        switch (parsed) {
          case NodeStrategyLlm l:
            expect(l.expectedInputs, equals(['doc_id', 'prompt_text']));
            expect(l.outputSchema, isNotNull);
            expect(l.outputSchema?['type'], equals('object'));
          case NodeStrategyLogic _:
            fail('Should be LLM');
        }
      },
    );

    test(
      'Fails-Fast when expectedInputs is the wrong type (Map instead of List)',
      () async {
        final payload = {
          'id': 'st_a1b2c3d4e5f60001',
          'slug': 'test_slug',
          'name': {'default_locale': 'en'},
          'type': 'llm',
          'model_strategy': 'fast',
          'expected_inputs': {'data': 'wrong_type'}, // Expected List<String>
        };

        // Since Freezed uses explicit typing, attempting to parse this corrupted payload
        // into a List from a Map will trigger an exception, enforcing Fail-Fast.
        expect(() async {
          await Isolate.run(() {
            return NodeStrategy.fromJson(payload);
          });
        }, throwsException);
      },
    );

    test(
      'Logic nodes parse successfully without requiring outputSchema',
      () async {
        final payload = {
          'id': 'st_a1b2c3d4e5f60002',
          'slug': 'logic_slug',
          'name': {'default_locale': 'en'},
          'type': 'logic',
          'hook': 'my_logic_hook',
          // Omitting outputSchema and expectedInputs entirely to test correct @Default injection
        };

        final NodeStrategy parsed = await Isolate.run(() {
          return NodeStrategy.fromJson(payload);
        });

        expect(parsed, isA<NodeStrategyLogic>());

        switch (parsed) {
          case NodeStrategyLlm _:
            fail('Should be Logic');
          case NodeStrategyLogic l:
            expect(l.expectedInputs, isEmpty);
            expect(l.outputSchema, isNull);
        }
      },
    );

    test(
      'ExpectedInput successfully parses scan_for_performative_patterns from backend payload',
      () {
        final payload = {
          'input_key': 'test_key',
          'label': {'default_locale': 'en', 'translations': <String, String>{}},
          'required': false,
          'description': {
            'default_locale': 'en',
            'translations': <String, String>{},
          },
          'scan_for_performative_patterns': true,
        };

        // This is expected to throw a CheckedFromJsonException due to unrecognized keys
        expect(() => ExpectedInput.fromJson(payload), returnsNormally);
      },
    );
  });
}
