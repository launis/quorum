import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/models/execution_metrics_dto.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/providers/atom_result_provider.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';
import 'package:client_app/features/execution/providers/report_data_v2_provider.dart';
import 'package:client_app/utils/json_converters.dart';
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
    final execId = generateOpaqueUuid7('exe');
    final uninitExecId = generateOpaqueUuid7('exe');
    final workflowId = generateOpaqueUuid7('wf');
    final profileId = generateOpaqueUuid7('op');
    final node1Id = generateOpaqueUuid7('tda');
    final invalidNodeId = generateOpaqueUuid7('tda');

    late ReportDataDto mockReportData;

    setUp(() {
      mockReportData = ReportDataDto(
        executionId: execId,
        workflowId: workflowId,
        profileId: profileId,
        globalMetrics: const ExecutionMetricsDTO(
          totalAtoms: 10,
          evaluated: 8,
          shortCircuitedNa: 2,
          durationMs: 1500,
        ),
        results: [
          AtomResultDTO(tdaId: node1Id, status: ExecutionStatus.passed),
        ],
        hydratedReferences: {
          node1Id: const HydratedAtomDTO(
            sduiComponent: SDUIComponentType.extractedValueCard,
            resolvedClaim: 'The weight',
          ),
        },
      );

      container = ProviderContainer(
        overrides: [
          reportDataV2Provider(
            execId,
          ).overrideWith(() => MockReportDataV2Notifier(mockReportData)),
        ],
      );
    });

    tearDown(() {
      container.dispose();
    });

    test('hydratedReference lookup is O(1) and retrieves correct node', () {
      final hydrated = container.read(
        hydratedReferenceProvider(execId, node1Id),
      );
      expect(hydrated, isNotNull);
      expect(hydrated?.sduiComponent, SDUIComponentType.extractedValueCard);
      expect(hydrated?.resolvedClaim, 'The weight');
    });

    test('hydratedReference returns null for invalid node', () {
      final hydrated = container.read(
        hydratedReferenceProvider(execId, invalidNodeId),
      );
      expect(hydrated, isNull);
    });

    test(
      'hydratedReference throws ProviderException if reportData is null',
      () {
        final emptyContainer = ProviderContainer(
          overrides: [
            reportDataV2Provider(
              uninitExecId,
            ).overrideWith(() => MockReportDataV2Notifier(null)),
          ],
        );
        addTearDown(emptyContainer.dispose);
        expect(
          () => emptyContainer.read(
            hydratedReferenceProvider(uninitExecId, node1Id),
          ),
          throwsA(
            predicate((e) => e.toString().contains('Fail-Fast: ReportDataDto')),
          ),
        );
      },
    );

    test('atomResults returns list without topological sorting', () {
      final results = container.read(atomResultsProvider(execId));
      expect(results.length, 1);
      expect(results.first.tdaId, node1Id);
    });

    test('atomResults throws ProviderException if reportData is null', () {
      final emptyContainer = ProviderContainer(
        overrides: [
          reportDataV2Provider(
            uninitExecId,
          ).overrideWith(() => MockReportDataV2Notifier(null)),
        ],
      );
      addTearDown(emptyContainer.dispose);
      expect(
        () => emptyContainer.read(atomResultsProvider(uninitExecId)),
        throwsA(
          predicate((e) => e.toString().contains('Fail-Fast: ReportDataDto')),
        ),
      );
    });
  });
}
