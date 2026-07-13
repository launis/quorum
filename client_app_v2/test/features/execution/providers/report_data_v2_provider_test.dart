import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/models/execution_metrics_dto.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/providers/atom_result_provider.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';
import 'package:client_app/features/execution/providers/report_data_v2_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class MockReportDataV2Notifier extends ReportDataV2 {
  final ReportDataDto? mockData;
  MockReportDataV2Notifier(this.mockData);

  @override
  ReportDataDto? build(String executionId) {
    return mockData;
  }
}

void main() {
  group('ReportDataV2 Providers O(1) Lookups', () {
    late ProviderContainer container;

    final mockReportData = ReportDataDto(
      executionId: 'exec_123',
      workflowId: 'wf_abc',
      globalMetrics: const ExecutionMetricsDTO(
        totalAtoms: 10,
        evaluated: 8,
        shortCircuitedNa: 2,
        durationMs: 1500,
      ),
      results: [
        const AtomResultDTO(tdaId: 'node_1', status: ExecutionStatus.passed),
      ],
      hydratedReferences: {
        'node_1': const HydratedAtomDTO(
          sduiComponent: SDUIComponentType.extractedValueCard,
          resolvedClaim: 'The weight',
        ),
      },
    );

    setUp(() {
      container = ProviderContainer(
        overrides: [
          reportDataV2Provider(
            'exec_123',
          ).overrideWith(() => MockReportDataV2Notifier(mockReportData)),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    test('hydratedReference lookup is O(1) and retrieves correct node', () {
      final hydrated = container.read(
        hydratedReferenceProvider('exec_123', 'node_1'),
      );
      expect(hydrated, isNotNull);
      expect(hydrated?.sduiComponent, SDUIComponentType.extractedValueCard);
      expect(hydrated?.resolvedClaim, 'The weight');
    });

    test('hydratedReference returns null for invalid node', () {
      final hydrated = container.read(hydratedReferenceProvider('exec_123', 'invalid_node'));
      expect(hydrated, isNull);
    });

    test('hydratedReference throws ProviderException if reportData is null', () {
      final emptyContainer = ProviderContainer(
        overrides: [
          reportDataV2Provider('exec_456').overrideWith(() => MockReportDataV2Notifier(null)),
        ],
      );
      expect(
        () => emptyContainer.read(hydratedReferenceProvider('exec_456', 'node_1')),
        throwsA(predicate((e) => e.toString().contains('Fail-Fast: ReportDataDto'))),
      );
    });

    test('atomResults returns list without topological sorting', () {
      final results = container.read(atomResultsProvider('exec_123'));
      expect(results.length, 1);
      expect(results.first.tdaId, 'node_1');
    });

    test('atomResults throws ProviderException if reportData is null', () {
      final emptyContainer = ProviderContainer(
        overrides: [
          reportDataV2Provider('exec_456').overrideWith(() => MockReportDataV2Notifier(null)),
        ],
      );
      expect(
        () => emptyContainer.read(atomResultsProvider('exec_456')),
        throwsA(predicate((e) => e.toString().contains('Fail-Fast: ReportDataDto'))),
      );
    });
  });
}
