// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

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
}
