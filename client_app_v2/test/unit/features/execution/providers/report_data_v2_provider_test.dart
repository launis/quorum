import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/models/execution_metrics_dto.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/providers/report_data_v2_provider.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

Matcher _throwsAppValidationException(String expectedMessageSubstring) {
  return throwsA(
    predicate<Object>(
      (error) {
        if (error is AppException) {
          return error.errorCode == 'VALIDATION_FAILED' &&
              error.detail.contains(expectedMessageSubstring);
        }
        final errStr = error.toString();
        return errStr.contains('VALIDATION_FAILED') ||
            errStr.contains(expectedMessageSubstring);
      },
      'AppException(VALIDATION_FAILED) containing "$expectedMessageSubstring"',
    ),
  );
}

void main() {
  group('ReportDataV2 Provider Unit & ISTQB Boundary Tests', () {
    final validExecId = generateOpaqueUuid7('exe');
    final otherExecId = generateOpaqueUuid7('exe');
    final validWorkflowId = generateOpaqueUuid7('wf');
    final validProfileId = generateOpaqueUuid7('op');
    final validTdaId = generateOpaqueUuid7('tda');

    test(
      'Positive 1: build initializes state to null and setReportData updates scoped state',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        expect(container.read(reportDataV2Provider(validExecId)), isNull);

        final reportData = ReportDataDto(
          executionId: validExecId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          globalMetrics: const ExecutionMetricsDTO(
            totalAtoms: 4,
            evaluated: 4,
            shortCircuitedNa: 0,
            durationMs: 420,
          ),
          results: <AtomResultDTO>[
            AtomResultDTO(tdaId: validTdaId, status: ExecutionStatus.passed),
          ],
          hydratedReferences: <String, HydratedAtomDTO>{
            validTdaId: const HydratedAtomDTO(
              sduiComponent: SDUIComponentType.extractedValueCard,
              resolvedClaim: 'Verified metric claim',
            ),
          },
        );

        container
            .read(reportDataV2Provider(validExecId).notifier)
            .setReportData(reportData);

        final current = container.read(reportDataV2Provider(validExecId));
        expect(current, isNotNull);
        expect(current?.executionId, equals(validExecId));
        expect(current?.workflowId, equals(validWorkflowId));
        expect(current?.profileId, equals(validProfileId));
        expect(current?.results, hasLength(1));
        expect(current?.results.first.tdaId, equals(validTdaId));
      },
    );

    test(
      'Positive 2 (Boundary - Execution Scope Isolation & State Replacement): mutating one executionId does not leak state to another executionId',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        final firstReport = ReportDataDto(
          executionId: validExecId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          globalScore: 3.5,
        );
        final replacementReport = firstReport.copyWith(
          globalScore: 4.8,
          hasWarning: true,
        );

        final notifier = container.read(
          reportDataV2Provider(validExecId).notifier,
        );
        notifier.setReportData(firstReport);
        expect(
          container.read(reportDataV2Provider(validExecId))?.globalScore,
          equals(3.5),
        );
        expect(container.read(reportDataV2Provider(otherExecId)), isNull);

        notifier.setReportData(replacementReport);
        final updated = container.read(reportDataV2Provider(validExecId));
        expect(updated?.globalScore, equals(4.8));
        expect(updated?.hasWarning, isTrue);
        expect(container.read(reportDataV2Provider(otherExecId)), isNull);
      },
    );

    test(
      'Negative 1 (ISTQB BVA - Empty/Whitespace executionId on build): throws AppException.validation when executionId is empty or whitespace',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        expect(
          () => container.read(reportDataV2Provider('')),
          _throwsAppValidationException(
            'Fail-Fast: executionId must not be empty.',
          ),
        );

        expect(
          () => container.read(reportDataV2Provider('   \t\n ')),
          _throwsAppValidationException(
            'Fail-Fast: executionId must not be empty.',
          ),
        );
      },
    );

    test(
      'Negative 2 (Fail-Fast Scope Mismatch & Empty DTO ID on setReportData): throws AppException.validation when ReportDataDto.executionId mismatches provider scope or is empty',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        final notifier = container.read(
          reportDataV2Provider(validExecId).notifier,
        );

        final mismatchedReport = ReportDataDto(
          executionId: otherExecId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
        );

        expect(
          () => notifier.setReportData(mismatchedReport),
          _throwsAppValidationException(
            'Fail-Fast: ReportDataDto.executionId ($otherExecId) does not match provider scope ($validExecId).',
          ),
        );
        expect(container.read(reportDataV2Provider(validExecId)), isNull);

        final emptyIdReport = ReportDataDto(
          executionId: '   ',
          workflowId: validWorkflowId,
          profileId: validProfileId,
        );

        expect(
          () => notifier.setReportData(emptyIdReport),
          _throwsAppValidationException(
            'Fail-Fast: ReportDataDto.executionId must not be empty.',
          ),
        );
        expect(container.read(reportDataV2Provider(validExecId)), isNull);
      },
    );
  });
}
