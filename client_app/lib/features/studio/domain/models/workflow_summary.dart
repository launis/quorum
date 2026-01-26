import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_summary.freezed.dart';
part 'workflow_summary.g.dart';

// ignore_for_file: invalid_annotation_target
// Force Rebuild

@freezed
abstract class WorkflowSummary with _$WorkflowSummary {
  const factory WorkflowSummary({
    required String id,
    required String name,
    String? description,
    required DateTime updatedAt,
  }) = _WorkflowSummary;

  factory WorkflowSummary.fromJson(Map<String, dynamic> json) => 
      _$WorkflowSummaryFromJson(json);
}
