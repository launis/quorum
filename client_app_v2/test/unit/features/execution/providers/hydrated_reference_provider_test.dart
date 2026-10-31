import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';
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
  group('hydratedReferenceProvider Unit & ISTQB Boundary Tests', () {
    final validExecId = generateOpaqueUuid7('exe');
    final otherExecId = generateOpaqueUuid7('exe');
    final validWorkflowId = generateOpaqueUuid7('wf');
    final validProfileId = generateOpaqueUuid7('op');
    final validTdaId = generateOpaqueUuid7('tda');
    final unmappedTdaId = generateOpaqueUuid7('tda');

    test(
      'Positive 1: resolves HydratedAtomDTO in O(1) time and updates reactively when ReportDataDto changes',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        const initialAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.extractedValueCard,
          resolvedClaim: 'Initial verified strategic claim',
          sourceQuotes: <String>['Direct quote A'],
        );

        final initialReport = ReportDataDto(
          executionId: validExecId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          hydratedReferences: <String, HydratedAtomDTO>{
            validTdaId: initialAtom,
          },
        );

        container
            .read(reportDataV2Provider(validExecId).notifier)
            .setReportData(initialReport);

        final resolved = container.read(
          hydratedReferenceProvider(validExecId, validTdaId),
        );
        expect(resolved, isNotNull);
        expect(
          resolved?.sduiComponent,
          equals(SDUIComponentType.extractedValueCard),
        );
        expect(
          resolved?.resolvedClaim,
          equals('Initial verified strategic claim'),
        );
        expect(resolved?.sourceQuotes, equals(<String>['Direct quote A']));

        const updatedAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.booleanCard,
          resolvedClaim: 'Updated claim synthesis',
        );
        final updatedReport = initialReport.copyWith(
          hydratedReferences: <String, HydratedAtomDTO>{
            validTdaId: updatedAtom,
          },
        );

        container
            .read(reportDataV2Provider(validExecId).notifier)
            .setReportData(updatedReport);

        final updatedResolved = container.read(
          hydratedReferenceProvider(validExecId, validTdaId),
        );
        expect(
          updatedResolved?.sduiComponent,
          equals(SDUIComponentType.booleanCard),
        );
        expect(
          updatedResolved?.resolvedClaim,
          equals('Updated claim synthesis'),
        );
      },
    );

    test(
      'Positive 2 (Boundary - Unmapped Key): returns null when tdaId is absent in initialized ReportDataDto',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        final report = ReportDataDto(
          executionId: validExecId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          hydratedReferences: const <String, HydratedAtomDTO>{},
        );

        container
            .read(reportDataV2Provider(validExecId).notifier)
            .setReportData(report);

        final result = container.read(
          hydratedReferenceProvider(validExecId, unmappedTdaId),
        );
        expect(result, isNull);
      },
    );

    test(
      'Negative 1 (Fail-Fast Uninitialized State): throws AppException.validation when ReportDataDto is null for executionId',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        // Populate a different executionId to verify strict tenant/execution scope isolation
        container
            .read(reportDataV2Provider(otherExecId).notifier)
            .setReportData(
              ReportDataDto(
                executionId: otherExecId,
                workflowId: validWorkflowId,
                profileId: validProfileId,
              ),
            );

        expect(
          () => container.read(
            hydratedReferenceProvider(validExecId, validTdaId),
          ),
          _throwsAppValidationException(
            'Fail-Fast: ReportDataDto is not initialized for execution $validExecId',
          ),
        );
      },
    );

    test(
      'Negative 2 (ISTQB BVA - Empty/Whitespace Identifiers): throws AppException.validation when executionId or tdaId is empty or whitespace',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        expect(
          () => container.read(hydratedReferenceProvider('', validTdaId)),
          _throwsAppValidationException(
            'Fail-Fast: executionId and tdaId must not be empty.',
          ),
        );

        expect(
          () => container.read(hydratedReferenceProvider('   ', validTdaId)),
          _throwsAppValidationException(
            'Fail-Fast: executionId and tdaId must not be empty.',
          ),
        );

        expect(
          () => container.read(hydratedReferenceProvider(validExecId, '')),
          _throwsAppValidationException(
            'Fail-Fast: executionId and tdaId must not be empty.',
          ),
        );

        expect(
          () => container.read(hydratedReferenceProvider(validExecId, '  \t ')),
          _throwsAppValidationException(
            'Fail-Fast: executionId and tdaId must not be empty.',
          ),
        );
      },
    );
  });
}
