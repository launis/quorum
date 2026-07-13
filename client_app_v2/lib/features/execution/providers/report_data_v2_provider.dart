import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/report_data_v2_dto.dart';

part 'report_data_v2_provider.g.dart';

/// Fetches and holds the raw [ReportDataDto] payload for a given execution.
/// Follows tenant_data_isolation: the state is scoped by executionId.
@riverpod
class ReportDataV2 extends _$ReportDataV2 {
  @override
  ReportDataDto? build(String executionId) {
    // Placeholder for Phase 2 implementation.
    // In actual implementation, this could fetch from a local repository
    // or from the backend.
    return null;
  }

  void setReportData(ReportDataDto data) {
    state = data;
  }
}
