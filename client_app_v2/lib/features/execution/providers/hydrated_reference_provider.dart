import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/error/app_exception.dart';
import '../models/hydrated_atom_dto.dart';
import 'report_data_v2_provider.dart';

part 'hydrated_reference_provider.g.dart';

/// Extracts the static reference from `ReportDataDto.hydratedReferences[tdaId]`
/// in O(1) time without nested loops, enforcing the Topo-Graph rules.
@riverpod
HydratedAtomDTO? hydratedReference(Ref ref, String executionId, String tdaId) {
  final reportData = ref.watch(reportDataV2Provider(executionId));

  if (reportData == null) {
    throw AppException.validation(
      'Fail-Fast: ReportDataDto is not initialized for execution $executionId',
    );
  }

  return reportData.hydratedReferences?[tdaId];
}
