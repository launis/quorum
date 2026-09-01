import 'dart:isolate';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/features/studio/models/workflow.dart';

void main() {
  // Phase 1, Step 4: Renamed from 'Epic 11 Phase B: NodeStrategy Strict Parsing'
  group('NodeStrategy Strict Parsing', () {
    test(
      'Successfully parses valid expectedInputs via Isolate',
      () async {
        final payload = {
          'id': 'st_a1b2c3d4e5f60000',
          'slug': 'test_slug',
          'name': {
            'translations': {'en': 'Test'},
          },
          'type': 'llm',
          'model_strategy': 'fast',
          'expected_inputs': ['doc_id', 'prompt_text'],
        };

        final NodeStrategy parsed = await Isolate.run(() {
          return NodeStrategy.fromJson(payload);
        });

        expect(parsed, isA<NodeStrategyLlm>());

        // Dart 3 'switch' pattern matching to unpack sealed class securely
        switch (parsed) {
          case NodeStrategyLlm l:
            expect(l.expectedInputs, equals(['doc_id', 'prompt_text']));
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
          'name': {
            'translations': {'en': 'Test'},
          },
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
      'Logic nodes parse successfully without requiring expectedInputs',
      () async {
        final payload = {
          'id': 'st_a1b2c3d4e5f60002',
          'slug': 'logic_slug',
          'name': {
            'translations': {'en': 'Test'},
          },
          'type': 'logic',
          'hook': 'my_logic_hook',
          // Omitting expectedInputs entirely to test correct @Default injection
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
        }
      },
    );

    test(
      'ExpectedInput successfully parses scan_for_performative_patterns from backend payload',
      () {
        final payload = {
          'input_key': 'test_key',
          'label': {'translations': <String, String>{}},
          'required': false,
          'description': {'translations': <String, String>{}},
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
          'name': {
            'translations': {'en': 'Test'},
          },
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
          'name': {
            'translations': {'en': 'Test'},
          },
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
          'name': {
            'translations': {'en': 'Test'},
          },
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
          'name': {
            'translations': {'en': 'Test'},
          },
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

  group('Workflow Schema Parity & Purged Fields Verification', () {
    test(
      'Workflow.toJson() must not contain purged legacy field ui_schema',
      () {
        const workflow = Workflow(
          id: 'wf_0123456789abcdef',
          slug: 'test_wf',
          name: I18nText(translations: {'en': 'Test Workflow'}),
          description: I18nText(translations: {'en': 'Test Description'}),
        );

        final json = workflow.toJson();
        expect(
          json.containsKey('ui_schema'),
          isFalse,
          reason:
              'ui_schema was purged in Epic 150 and causes 422 extra_forbidden on backend PUT',
        );
      },
    );

    test(
      'NodeStrategy.toJson() must not contain purged legacy field output_schema',
      () {
        const node = NodeStrategy.llm(
          id: 'st_0123456789abcdef',
          slug: 'test_step',
          name: I18nText(translations: {'en': 'Test Step'}),
          modelStrategy: 'fast',
        );

        final json = node.toJson();
        expect(
          json.containsKey('output_schema'),
          isFalse,
          reason:
              'output_schema was purged in Epic 150 and causes 422 extra_forbidden on backend PUT',
        );
      },
    );
  });
}

