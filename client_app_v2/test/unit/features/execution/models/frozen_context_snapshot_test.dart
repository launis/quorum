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
            'entries': <String, Object?>{'th_1': 'Theory content block'},
          },
          'generated_schemas': <String, Object?>{
            'stp_1': <String, Object?>{'type': 'object'},
          },
          'ui_hints_snapshot': <String, Object?>{
            'score': <String, Object?>{'widget': 'badge'},
          },
          'mcp_tool_audit': <Map<String, Object?>>[
            <String, Object?>{
              'tool_name': 'search_docs',
              'duration_ms': 120,
              'status': 'success',
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
        expect(snapshot.injectedTheory, contains('entries'));
        expect(snapshot.generatedSchemas, contains('stp_1'));
        expect(snapshot.uiHintsSnapshot, contains('score'));
        expect(snapshot.mcpToolAudit, hasLength(1));
        expect(snapshot.mcpToolAudit.first['tool_name'], equals('search_docs'));

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
        expect(roundtripped.mcpToolAudit.first['duration_ms'], equals(120));
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
        expect(emptySnapshot.injectedTheory, isEmpty);
        expect(emptySnapshot.generatedSchemas, isEmpty);
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
