import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/error/app_exception.dart';
import '../models/report_data_v2_dto.dart';

part 'report_data_v2_provider.g.dart';

/// Fetches and holds the raw [ReportDataDto] payload for a given execution.
/// Follows tenant_data_isolation: the state is scoped by executionId.
@riverpod
class ReportDataV2 extends _$ReportDataV2 {
  @override
  ReportDataDto? build(String executionId) {
    // Enforce Fail-Fast execution scope validation on provider initialization.
    if (executionId.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: executionId must not be empty.',
      );
    }
    return null;
  }

  void setReportData(ReportDataDto data) {
    // Enforce strict execution-scoped tenant isolation before mutating state.
    if (data.executionId.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: ReportDataDto.executionId must not be empty.',
      );
    }
    if (data.executionId != executionId) {
      throw AppException.validation(
        'Fail-Fast: ReportDataDto.executionId (${data.executionId}) does not match provider scope ($executionId).',
      );
    }
    state = data;
  }
}
