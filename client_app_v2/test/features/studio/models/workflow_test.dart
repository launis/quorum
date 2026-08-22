import 'dart:isolate';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/features/studio/models/workflow.dart';

void main() {
  // Phase 1, Step 4: Renamed from 'Epic 11 Phase B: NodeStrategy Strict Parsing'
  group('NodeStrategy Strict Parsing', () {
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

  // Phase 1, Step 4: Governance field deserialization tests
  group('StepRule Governance Fields', () {
    test('test_step_rule_deserializes_is_synthesis_source_default_true', () {
      final json = {
        'id': 'sr_1234567890abcdef',
        'task_blueprint': 'sp_1234567890abcdef',
      };

      final stepRule = StepRule.fromJson(json);
      expect(stepRule.isSynthesisSource, isTrue);
    });

    test('test_step_rule_deserializes_is_synthesis_source_explicit_false', () {
      final json = {
        'id': 'sr_1234567890abcdef',
        'task_blueprint': 'sp_1234567890abcdef',
        'is_synthesis_source': false,
      };

      final stepRule = StepRule.fromJson(json);
      expect(stepRule.isSynthesisSource, isFalse);
    });

    test('test_step_rule_rejects_is_synthesis_source_wrong_type', () {
      final json = {
        'id': 'sr_1234567890abcdef',
        'task_blueprint': 'sp_1234567890abcdef',
        'is_synthesis_source': 'not_a_bool',
      };

      expect(
        () => StepRule.fromJson(json),
        throwsA(isA<CheckedFromJsonException>()),
      );
    });
  });

  group('NodeStrategy Governance Fields', () {
    test(
      'test_node_strategy_llm_deserializes_is_system_core_default_false',
      () {
        final json = {
          'id': 'st_1234567890abcdef',
          'slug': 'test',
          'name': {'default_locale': 'en'},
          'type': 'llm',
          'model_strategy': 'fast',
        };

        final parsed = NodeStrategy.fromJson(json);
        expect(parsed, isA<NodeStrategyLlm>());

        switch (parsed) {
          case NodeStrategyLlm l:
            expect(l.isSystemCore, isFalse);
          case NodeStrategyLogic _:
            fail('Should be LLM');
        }
      },
    );

    test(
      'test_node_strategy_llm_deserializes_is_system_core_explicit_true',
      () {
        final json = {
          'id': 'st_1234567890abcdef',
          'slug': 'test',
          'name': {'default_locale': 'en'},
          'type': 'llm',
          'model_strategy': 'fast',
          'is_system_core': true,
        };

        final parsed = NodeStrategy.fromJson(json);
        expect(parsed, isA<NodeStrategyLlm>());

        switch (parsed) {
          case NodeStrategyLlm l:
            expect(l.isSystemCore, isTrue);
          case NodeStrategyLogic _:
            fail('Should be LLM');
        }
      },
    );

    test(
      'test_node_strategy_logic_deserializes_is_system_core_explicit_true',
      () {
        final json = {
          'id': 'st_1234567890abcdef',
          'slug': 'test',
          'name': {'default_locale': 'en'},
          'type': 'logic',
          'hook': 'my_hook',
          'is_system_core': true,
        };

        final parsed = NodeStrategy.fromJson(json);
        expect(parsed, isA<NodeStrategyLogic>());

        switch (parsed) {
          case NodeStrategyLlm _:
            fail('Should be Logic');
          case NodeStrategyLogic l:
            expect(l.isSystemCore, isTrue);
        }
      },
    );

    test(
      'test_node_strategy_rejects_unknown_extra_key_with_is_system_core',
      () {
        final json = {
          'id': 'st_1234567890abcdef',
          'slug': 'test',
          'name': {'default_locale': 'en'},
          'type': 'llm',
          'model_strategy': 'fast',
          'is_system_core': false,
          'unknown_forbidden_key': 'should_crash',
        };

        expect(
          () => NodeStrategy.fromJson(json),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
