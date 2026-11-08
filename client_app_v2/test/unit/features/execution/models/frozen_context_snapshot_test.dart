import 'dart:convert';

import 'package:client_app/features/execution/models/frozen_context_snapshot.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('FrozenContextSnapshot Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: FrozenContextSnapshot deserializes full payload and roundtrips cleanly',
      () {
        final versionId = generateOpaqueUuid7('ver');
        final workflowId = generateOpaqueUuid7('wf');
        final organizationId = generateOpaqueUuid7('org');
        final userId = generateOpaqueUuid7('usr');
        final stepId = generateOpaqueUuid7('stp');

        final rawPayload = <String, Object?>{
          'version_id': versionId,
          'workflow_id': workflowId,
          'workflow_name': 'Executive Leadership Audit',
          'organization_id': organizationId,
          'user_id': userId,
          'created_at': '2026-10-31T22:00:00Z',
          'compiled_prompts': <String, String>{
            'stp_1': 'Evaluate strategic alignment across dimensions.',
          },
          'injected_theory': <String, Object?>{
            'theories': <String, String>{'th_1': 'Theory content block'},
          },
          'generated_schemas': <String, Object?>{
            'schemas': <String, Object?>{
              'stp_1': <String, Object?>{
                'type': 'object',
                'title': 'StepOutputSchema',
                'description': 'Schema for step 1 output',
                'required': <String>['score'],
                'additionalProperties': false,
                'properties': <String, Object?>{
                  'score': <String, Object?>{
                    'type': 'number',
                    'format': 'double',
                  },
                },
              },
            },
          },
          'ui_hints_snapshot': <String, Object?>{
            'score': <String, Object?>{
              'field_id': 'score',
              'component_type': 'badge',
              'options': <Map<String, Object?>>[
                <String, Object?>{'value': 'high', 'label': 'High'},
              ],
              'validation_rules': <String, Object?>{
                'min': 0.0,
                'max': 5.0,
                'required': true,
                'pattern': r'^[0-5]$',
              },
            },
          },
          'mcp_tool_audit': <Map<String, Object?>>[
            <String, Object?>{
              'tool_id': 'search_docs',
              'gateway_id': 'sys_0195f3a0000070008000000000000001',
              'step_name': stepId,
              'query': 'Test query',
              'source_urls': <String>['https://example.com'],
              'duration_ms': 120,
              'timestamp': '2026-10-31T22:00:00Z',
            },
          ],
        };

        final snapshot = FrozenContextSnapshot.fromJson(rawPayload);

        expect(snapshot.versionId, equals(versionId));
        expect(snapshot.workflowId, equals(workflowId));
        expect(snapshot.workflowName, equals('Executive Leadership Audit'));
        expect(snapshot.organizationId, equals(organizationId));
        expect(snapshot.userId, equals(userId));
        expect(snapshot.createdAt, equals('2026-10-31T22:00:00Z'));
        expect(
          snapshot.compiledPrompts,
          equals(<String, String>{
            'stp_1': 'Evaluate strategic alignment across dimensions.',
          }),
        );
        expect(
          snapshot.injectedTheory.theories['th_1'],
          equals('Theory content block'),
        );
        expect(
          snapshot.generatedSchemas.schemas['stp_1']?.type,
          equals('object'),
        );
        expect(
          snapshot.generatedSchemas.schemas['stp_1']?.title,
          equals('StepOutputSchema'),
        );
        expect(
          snapshot.generatedSchemas.schemas['stp_1']?.additionalProperties,
          isFalse,
        );
        expect(
          snapshot
              .generatedSchemas
              .schemas['stp_1']
              ?.properties['score']
              ?.format,
          equals('double'),
        );
        expect(
          snapshot.uiHintsSnapshot['score']?.componentType,
          equals('badge'),
        );
        expect(
          snapshot.uiHintsSnapshot['score']?.options?.first.value,
          equals('high'),
        );
        expect(
          snapshot.uiHintsSnapshot['score']?.validationRules?.max,
          equals(5.0),
        );
        expect(snapshot.mcpToolAudit, hasLength(1));
        expect(snapshot.mcpToolAudit.first.toolId, equals('search_docs'));

        final roundtrippedMap =
            jsonDecode(jsonEncode(snapshot.toJson())) as Map<String, Object?>;
        final roundtripped = FrozenContextSnapshot.fromJson(roundtrippedMap);

        expect(roundtripped.versionId, equals(versionId));
        expect(roundtripped.workflowId, equals(workflowId));
        expect(roundtripped.workflowName, equals('Executive Leadership Audit'));
        expect(roundtripped.organizationId, equals(organizationId));
        expect(roundtripped.userId, equals(userId));
        expect(
          roundtripped.compiledPrompts['stp_1'],
          equals('Evaluate strategic alignment across dimensions.'),
        );
        expect(roundtripped.mcpToolAudit, hasLength(1));
        expect(roundtripped.mcpToolAudit.first.durationMs, equals(120));
      },
    );

    test(
      'Positive 2 (Boundary & Defaults): applies deterministic empty collection defaults on minimal payload',
      () {
        final emptySnapshot = FrozenContextSnapshot.fromJson(
          <String, Object?>{},
        );

        expect(emptySnapshot.versionId, isNull);
        expect(emptySnapshot.workflowId, isNull);
        expect(emptySnapshot.workflowName, isNull);
        expect(emptySnapshot.organizationId, isNull);
        expect(emptySnapshot.userId, isNull);
        expect(emptySnapshot.createdAt, isNull);
        expect(emptySnapshot.compiledPrompts, isEmpty);
        expect(emptySnapshot.injectedTheory.theories, isEmpty);
        expect(emptySnapshot.generatedSchemas.schemas, isEmpty);
        expect(emptySnapshot.uiHintsSnapshot, isEmpty);
        expect(emptySnapshot.mcpToolAudit, isEmpty);
      },
    );

    test(
      'Negative 1: rejects unrecognized JSON keys under strict disallowUnrecognizedKeys configuration',
      () {
        final payloadWithExtraKey = <String, Object?>{
          'workflow_id': generateOpaqueUuid7('wf'),
          'unrecognized_legacy_field': 'forbidden',
        };

        expect(
          () => FrozenContextSnapshot.fromJson(payloadWithExtraKey),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => InjectedTheoryManifestDto.fromJson(<String, Object?>{
            'extra': 'bad',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => SchemaManifestNodeDto.fromJson(<String, Object?>{
            'extra': 'bad',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => GeneratedSchemaManifestDto.fromJson(<String, Object?>{
            'extra': 'bad',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => SystemConfigOptionDto.fromJson(<String, Object?>{
            'value': 'ok',
            'extra': 'bad',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => SystemValidationRulesDto.fromJson(<String, Object?>{
            'extra': 'bad',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => DataDictionaryField.fromJson(<String, Object?>{
            'field_id': 'f1',
            'component_type': 'text_input',
            'extra': 'bad',
          }),
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
      'Negative 2 (ISTQB Type & Boundary Violations): rejects invalid types for scalar, map, and audit list fields',
      () {
        // Non-String value for workflow_id
        expect(
          () => FrozenContextSnapshot.fromJson(<String, Object?>{
            'workflow_id': 12345,
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // Non-String values inside compiled_prompts map
        expect(
          () => FrozenContextSnapshot.fromJson(<String, Object?>{
            'compiled_prompts': <String, Object?>{'stp_1': 999},
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // List instead of Map for injected_theory
        expect(
          () => FrozenContextSnapshot.fromJson(<String, Object?>{
            'injected_theory': <String>['invalid_list'],
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );

        // Map instead of List for mcp_tool_audit
        expect(
          () => FrozenContextSnapshot.fromJson(<String, Object?>{
            'mcp_tool_audit': <String, Object?>{'invalid': true},
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );
      },
    );
  });
}
