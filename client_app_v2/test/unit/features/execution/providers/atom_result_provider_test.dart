import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/providers/atom_result_provider.dart';
import 'package:client_app/features/execution/providers/report_data_v2_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _StubReportDataV2 extends ReportDataV2 {
  final ReportDataDto? stubData;

  _StubReportDataV2(this.stubData);

  @override
  ReportDataDto? build(String executionId) => stubData;
}

void main() {
  group('atomResultsProvider', () {
    test(
      'returns exact backend sequence of AtomResultDTO without re-sorting (Positive)',
      () {
        const firstAtom = AtomResultDTO(
          tdaId: 'tda_01960000000070008000000000000002',
          status: ExecutionStatus.passed,
        );
        const secondAtom = AtomResultDTO(
          tdaId: 'tda_01960000000070008000000000000001',
          status: ExecutionStatus.failed,
        );
        final reportData = ReportDataDto(
          executionId: 'exe_01960000000070008000000000000001',
          workflowId: 'wfl_01960000000070008000000000000001',
          profileId: 'prf_01960000000070008000000000000001',
          results: const [firstAtom, secondAtom],
        );

        final container = ProviderContainer(
          overrides: [
            reportDataV2Provider(
              'exe_01960000000070008000000000000001',
            ).overrideWith(() => _StubReportDataV2(reportData)),
          ],
        );
        addTearDown(container.dispose);

        final results = container.read(
          atomResultsProvider('exe_01960000000070008000000000000001'),
        );

        expect(results, hasLength(2));
        expect(results[0].tdaId, 'tda_01960000000070008000000000000002');
        expect(results[0].status, ExecutionStatus.passed);
        expect(results[1].tdaId, 'tda_01960000000070008000000000000001');
        expect(results[1].status, ExecutionStatus.failed);
      },
    );

    test(
      'throws AppException when ReportDataDto is null / uninitialized (Negative)',
      () {
        final container = ProviderContainer(
          overrides: [
            reportDataV2Provider(
              'exe_01960000000070008000000000000099',
            ).overrideWith(() => _StubReportDataV2(null)),
          ],
        );
        addTearDown(container.dispose);

        expect(
          () => container.read(
            atomResultsProvider('exe_01960000000070008000000000000099'),
          ),
          throwsA(
            predicate(
              (Object? error) =>
                  error.toString().contains(
                    'Fail-Fast: ReportDataDto is not initialized for execution exe_01960000000070008000000000000099',
                  ) ||
                  (error is AppException &&
                      error.detail.contains('Fail-Fast: ReportDataDto')),
            ),
          ),
        );
      },
    );

    test(
      'returns empty list when ReportDataDto has zero atom results (Boundary: 0 items)',
      () {
        final emptyReportData = ReportDataDto(
          executionId: 'exe_01960000000070008000000000000000',
          workflowId: 'wfl_01960000000070008000000000000001',
          profileId: 'prf_01960000000070008000000000000001',
          results: const [],
        );

        final container = ProviderContainer(
          overrides: [
            reportDataV2Provider(
              'exe_01960000000070008000000000000000',
            ).overrideWith(() => _StubReportDataV2(emptyReportData)),
          ],
        );
        addTearDown(container.dispose);

        final results = container.read(
          atomResultsProvider('exe_01960000000070008000000000000000'),
        );

        expect(results, isEmpty);
      },
    );
  });
}
