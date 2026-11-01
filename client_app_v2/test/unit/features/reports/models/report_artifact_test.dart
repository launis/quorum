import 'dart:convert';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/reports/models/report_artifact.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ReportArtifact & Sub-DTOs Unit & ISTQB Boundary Tests', () {
    final validReportId = generateOpaqueUuid7('rep');
    final validExecutionId = generateOpaqueUuid7('exe');
    final validWorkflowId = generateOpaqueUuid7('wf');
    final validProfileId = generateOpaqueUuid7('op');
    final validRegistryId = generateOpaqueUuid7('reg');

    test(
      'Positive 1: ReportStoragePaths and ReportMetadata deserialize full and minimal payloads and roundtrip cleanly',
      () {
        final pathsJson = <String, Object?>{
          'pdf_path': '/files/reports/rep_01.pdf',
          'sdui_json_path': '/files/reports/rep_01.json',
          'excel_path': '/files/reports/rep_01.xlsx',
          'csv_path': '/files/reports/rep_01.csv',
        };
        final paths = ReportStoragePaths.fromJson(pathsJson);
        expect(paths.pdfPath, equals('/files/reports/rep_01.pdf'));
        expect(paths.sduiJsonPath, equals('/files/reports/rep_01.json'));
        expect(paths.excelPath, equals('/files/reports/rep_01.xlsx'));
        expect(paths.csvPath, equals('/files/reports/rep_01.csv'));
        expect(paths.toJson(), equals(pathsJson));

        final emptyPaths = ReportStoragePaths.fromJson(<String, Object?>{});
        expect(emptyPaths.pdfPath, isNull);
        expect(emptyPaths.sduiJsonPath, isNull);

        final metaJson = <String, Object?>{
          'cost_usd': 0.0345,
          'duration_ms': 4200,
          'tokens_used': 3100,
          'llm_model': 'gemini-2.5-pro',
          'provider': 'vertex_ai',
          'cognitive_tier': 'deep',
          'model_registry_id': validRegistryId,
          'thinking_tokens': 512,
        };
        final meta = ReportMetadata.fromJson(metaJson);
        expect(meta.costUsd, equals(0.0345));
        expect(meta.durationMs, equals(4200));
        expect(meta.tokensUsed, equals(3100));
        expect(meta.llmModel, equals('gemini-2.5-pro'));
        expect(meta.provider, equals('vertex_ai'));
        expect(meta.cognitiveTier, equals(CognitiveTier.deep));
        expect(meta.modelRegistryId, equals(validRegistryId));
        expect(meta.thinkingTokens, equals(512));
        expect(meta.toJson(), equals(metaJson));
      },
    );

    test(
      'Positive 2: ReportRowItem deserializes valid 32-hex IDs, applies is_inverse_evidence default, and roundtrips cleanly',
      () {
        final rowJson = <String, Object?>{
          'execution_id': validExecutionId,
          'report_id': validReportId,
          'metric_key': 'blk_0195f3a0000070008000000000000099',
          'metric_label': 'Strategic Alignment',
          'score': 4.5,
          'max_scale': 5.0,
          'weight': 1.25,
          'reasoning': 'Clear executive alignment demonstrated.',
          'quote': 'We prioritized core architectural goals.',
          'is_inverse_evidence': true,
        };

        final item = ReportRowItem.fromJson(rowJson);
        expect(item.executionId, equals(validExecutionId));
        expect(item.reportId, equals(validReportId));
        expect(item.metricLabel, equals('Strategic Alignment'));
        expect(item.score, equals(4.5));
        expect(item.maxScale, equals(5.0));
        expect(item.weight, equals(1.25));
        expect(
          item.reasoning,
          equals('Clear executive alignment demonstrated.'),
        );
        expect(item.quote, equals('We prioritized core architectural goals.'));
        expect(item.isInverseEvidence, isTrue);
        expect(item.toJson(), equals(rowJson));

        final minimalRowJson = <String, Object?>{
          'execution_id': validExecutionId,
          'report_id': validReportId,
          'metric_key': 'm_key',
          'metric_label': 'Label',
          'score': 3.0,
          'max_scale': 5.0,
          'weight': 1.0,
        };
        final minimalItem = ReportRowItem.fromJson(minimalRowJson);
        expect(minimalItem.isInverseEvidence, isFalse);
        expect(minimalItem.reasoning, isNull);
        expect(minimalItem.quote, isNull);
      },
    );

    test(
      'Positive 3: ReportArtifact, ReportArtifactSummary, and CreateReportRequest deserialize and roundtrip cleanly',
      () {
        final createdAtIso = '2026-10-31T21:00:00.000Z';
        final updatedAtIso = '2026-10-31T21:05:00.000Z';

        final artifactJson = <String, Object?>{
          'id': validReportId,
          'execution_id': validExecutionId,
          'workflow_id': validWorkflowId,
          'profile_id': validProfileId,
          'locale': 'fi',
          'title': 'Johtoryhmän Yhteenveto',
          'status': 'ready',
          'storage_paths': <String, Object?>{
            'pdf_path': '/files/rep.pdf',
            'sdui_json_path': null,
            'excel_path': null,
            'csv_path': null,
          },
          'metadata': <String, Object?>{
            'cost_usd': 0.05,
            'duration_ms': 1500,
            'tokens_used': 1200,
            'llm_model': null,
            'provider': null,
            'cognitive_tier': 'balanced',
            'model_registry_id': null,
            'thinking_tokens': null,
          },
          'custom_preface_md': '# Esipuhe',
          'error_message': null,
          'created_at': createdAtIso,
          'updated_at': updatedAtIso,
        };

        final artifact = ReportArtifact.fromJson(artifactJson);
        expect(artifact.id, equals(validReportId));
        expect(artifact.executionId, equals(validExecutionId));
        expect(artifact.workflowId, equals(validWorkflowId));
        expect(artifact.profileId, equals(validProfileId));
        expect(artifact.locale, equals('fi'));
        expect(artifact.title, equals('Johtoryhmän Yhteenveto'));
        expect(artifact.status, equals(ReportStatus.ready));
        expect(artifact.storagePaths.pdfPath, equals('/files/rep.pdf'));
        expect(artifact.metadata.cognitiveTier, equals(CognitiveTier.balanced));
        expect(artifact.customPrefaceMd, equals('# Esipuhe'));
        expect(artifact.createdAt, equals(DateTime.parse(createdAtIso)));
        expect(artifact.updatedAt, equals(DateTime.parse(updatedAtIso)));

        final roundtrippedArtifact = ReportArtifact.fromJson(
          jsonDecode(jsonEncode(artifact.toJson())) as Map<String, Object?>,
        );
        expect(roundtrippedArtifact.id, equals(validReportId));
        expect(roundtrippedArtifact.status, equals(ReportStatus.ready));

        final summaryJson = <String, Object?>{
          'id': validReportId,
          'execution_id': validExecutionId,
          'profile_id': validProfileId,
          'locale': 'en',
          'title': 'Executive Report',
          'status': 'generating',
          'created_at': createdAtIso,
          'updated_at': updatedAtIso,
        };
        final summary = ReportArtifactSummary.fromJson(summaryJson);
        expect(summary.id, equals(validReportId));
        expect(summary.status, equals(ReportStatus.generating));
        expect(summary.toJson(), equals(summaryJson));

        final requestJson = <String, Object?>{
          'profile_id': validProfileId,
          'locale': 'en',
          'force_resynthesis': true,
          'custom_preface_md': 'Custom note',
          'model_registry_id': validRegistryId,
        };
        final request = CreateReportRequest.fromJson(requestJson);
        expect(request.profileId, equals(validProfileId));
        expect(request.locale, equals('en'));
        expect(request.forceResynthesis, isTrue);
        expect(request.customPrefaceMd, equals('Custom note'));
        expect(request.modelRegistryId, equals(validRegistryId));
        expect(request.toJson(), equals(requestJson));

        final defaultRequest = CreateReportRequest.fromJson(<String, Object?>{
          'profile_id': validProfileId,
        });
        expect(defaultRequest.locale, equals('fi'));
        expect(defaultRequest.forceResynthesis, isFalse);
      },
    );

    test(
      'Negative 1: rejects unrecognized keys across all 6 models under strict disallowUnrecognizedKeys configuration',
      () {
        expect(
          () => ReportStoragePaths.fromJson(<String, Object?>{
            'pdf_path': '/a.pdf',
            'unknown_key': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => ReportMetadata.fromJson(<String, Object?>{
            'cost_usd': 0.01,
            'unknown_key': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => ReportRowItem.fromJson(<String, Object?>{
            'execution_id': validExecutionId,
            'report_id': validReportId,
            'metric_key': 'k',
            'metric_label': 'l',
            'score': 1.0,
            'max_scale': 5.0,
            'weight': 1.0,
            'unknown_key': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => ReportArtifact.fromJson(<String, Object?>{
            'id': validReportId,
            'execution_id': validExecutionId,
            'workflow_id': validWorkflowId,
            'profile_id': validProfileId,
            'locale': 'fi',
            'title': 'T',
            'status': 'ready',
            'created_at': '2026-10-31T21:00:00.000Z',
            'updated_at': '2026-10-31T21:00:00.000Z',
            'unknown_key': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => ReportArtifactSummary.fromJson(<String, Object?>{
            'id': validReportId,
            'execution_id': validExecutionId,
            'profile_id': validProfileId,
            'locale': 'fi',
            'title': 'T',
            'status': 'ready',
            'created_at': '2026-10-31T21:00:00.000Z',
            'updated_at': '2026-10-31T21:00:00.000Z',
            'unknown_key': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => CreateReportRequest.fromJson(<String, Object?>{
            'profile_id': validProfileId,
            'unknown_key': 'forbidden',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative 2 (ISTQB BVA): StrictOpaqueIdConverter rejects empty, legacy 16-hex, 31-hex (min-1), and 33-hex (max+1) IDs and invalid enum values',
      () {
        const boundaryInvalidIds = <String>[
          '',
          'rep_0195f3a000007000', // legacy 16-hex
          'rep_0195f3a000007000800000000000000', // 31-hex (min-1)
          'rep_0195f3a00000700080000000000000012', // 33-hex (max+1)
          'r_0195f3a0000070008000000000000001', // 1-char prefix (min-1)
          'report_0195f3a0000070008000000000000001', // 6-char prefix (max+1)
        ];

        for (final invalidId in boundaryInvalidIds) {
          expect(
            () => ReportArtifact.fromJson(<String, Object?>{
              'id': invalidId,
              'execution_id': validExecutionId,
              'workflow_id': validWorkflowId,
              'profile_id': validProfileId,
              'locale': 'fi',
              'title': 'T',
              'status': 'ready',
              'created_at': '2026-10-31T21:00:00.000Z',
              'updated_at': '2026-10-31T21:00:00.000Z',
            }),
            throwsA(
              isA<CheckedFromJsonException>().having(
                (e) => e.innerError,
                'innerError',
                isA<AppException>(),
              ),
            ),
          );

          expect(
            () => CreateReportRequest.fromJson(<String, Object?>{
              'profile_id': invalidId,
            }),
            throwsA(
              isA<CheckedFromJsonException>().having(
                (e) => e.innerError,
                'innerError',
                isA<AppException>(),
              ),
            ),
          );
        }

        // Invalid enum value for ReportStatus
        expect(
          () => ReportArtifactSummary.fromJson(<String, Object?>{
            'id': validReportId,
            'execution_id': validExecutionId,
            'profile_id': validProfileId,
            'locale': 'fi',
            'title': 'T',
            'status': 'invalid_status_enum',
            'created_at': '2026-10-31T21:00:00.000Z',
            'updated_at': '2026-10-31T21:00:00.000Z',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
