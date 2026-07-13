import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/atom_result_dto.dart';
import 'report_data_v2_provider.dart';

part 'atom_result_provider.g.dart';

/// Returns `ReportDataDto.results`.
/// The frontend MUST NOT perform topological sorting. Trust the backend list sequence.
@riverpod
List<AtomResultDTO> atomResults(Ref ref, String executionId) {
  final reportData = ref.watch(reportDataV2Provider(executionId));

  if (reportData == null) {
    return const [];
  }

  return reportData.results;
}
