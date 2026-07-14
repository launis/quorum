// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';
import 'dart:convert';
import 'package:client_app/core/utils/safe_isolate.dart';

import 'atom_result_dto.dart';
import 'execution_metrics_dto.dart';
import 'global_synthesis_dto.dart';
import 'hydrated_atom_dto.dart';

part 'report_data_v2_dto.freezed.dart';
part 'report_data_v2_dto.g.dart';

@Freezed(equal: false)
abstract class ReportDataDto with _$ReportDataDto {
  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory ReportDataDto({
    @JsonKey(name: 'execution_id') required String executionId,
    @JsonKey(name: 'workflow_id') required String workflowId,
    @JsonKey(name: 'global_metrics') required ExecutionMetricsDTO globalMetrics,
    @JsonKey(name: 'global_synthesis') GlobalSynthesisDTO? globalSynthesis,
    required List<AtomResultDTO> results,
    @JsonKey(name: 'hydrated_references')
    required Map<String, HydratedAtomDTO> hydratedReferences,
  }) = _ReportDataDto;

  factory ReportDataDto.fromJson(Map<String, dynamic> json) =>
      _$ReportDataDtoFromJson(json);

  factory ReportDataDto.fromBackendResponse(Map<String, dynamic> json) {
    // Tier 4 Bugfix: Strip RenderedReportResponse SDUI keys from the payload
    // to comply with ReportDataDto's disallowUnrecognizedKeys strictness.
    const allowedKeys = {
      'execution_id',
      'workflow_id',
      'global_metrics',
      'global_synthesis',
      'results',
      'hydrated_references',
    };
    final filtered = Map<String, dynamic>.from(json)
      ..removeWhere((key, value) => !allowedKeys.contains(key));
    return _$ReportDataDtoFromJson(filtered);
  }

  /// Parses a heavy raw JSON string into a ReportDataDto entirely off the Main Thread.
  /// This prevents Main Thread Jank when handling large payloads.
  static Future<ReportDataDto> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ReportDataDto.fromBackendResponse(decoded);
    });
  }
}
