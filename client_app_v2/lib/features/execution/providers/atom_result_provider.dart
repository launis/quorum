import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/error/app_exception.dart';
import '../models/atom_result_dto.dart';
import 'report_data_v2_provider.dart';

part 'atom_result_provider.g.dart';

/// Returns `ReportDataDto.results`.
/// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.
@riverpod
List<AtomResultDTO> atomResults(Ref ref, String executionId) {
  final reportData = ref.watch(reportDataV2Provider(executionId));

  if (reportData == null) {
    throw AppException.validation(
      'Fail-Fast: ReportDataDto is not initialized for execution $executionId',
    );
  }

  return []; // TODO(Phase C4): Migrate to unified pipeline
}
