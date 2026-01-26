// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_summary.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_WorkflowSummary _$WorkflowSummaryFromJson(Map<String, dynamic> json) =>
    _WorkflowSummary(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$WorkflowSummaryToJson(_WorkflowSummary instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'updatedAt': instance.updatedAt.toIso8601String(),
    };
