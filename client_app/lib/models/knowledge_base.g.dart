// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'knowledge_base.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_IngestionStatus _$IngestionStatusFromJson(Map<String, dynamic> json) =>
    _IngestionStatus(
      jobId: json['job_id'] as String,
      status: json['status'] as String,
      progress: (json['progress'] as num).toInt(),
      stage: json['stage'] as String,
      result:
          json['result'] == null
              ? null
              : IngestionSummary.fromJson(
                json['result'] as Map<String, dynamic>,
              ),
      error: json['error'] as String?,
    );

Map<String, dynamic> _$IngestionStatusToJson(_IngestionStatus instance) =>
    <String, dynamic>{
      'job_id': instance.jobId,
      'status': instance.status,
      'progress': instance.progress,
      'stage': instance.stage,
      'result': instance.result,
      'error': instance.error,
    };

_IngestionSummary _$IngestionSummaryFromJson(Map<String, dynamic> json) =>
    _IngestionSummary(
      conceptsCount: (json['concepts_count'] as num?)?.toInt() ?? 0,
      referencesCount: (json['references_count'] as num?)?.toInt() ?? 0,
      claimsCount: (json['claims_count'] as num?)?.toInt() ?? 0,
      fileSize: (json['file_size'] as num?)?.toInt() ?? 0,
      filename: json['filename'] as String,
    );

Map<String, dynamic> _$IngestionSummaryToJson(_IngestionSummary instance) =>
    <String, dynamic>{
      'concepts_count': instance.conceptsCount,
      'references_count': instance.referencesCount,
      'claims_count': instance.claimsCount,
      'file_size': instance.fileSize,
      'filename': instance.filename,
    };

_KnowledgeModelStrategy _$KnowledgeModelStrategyFromJson(
  Map<String, dynamic> json,
) => _KnowledgeModelStrategy(
  id: json['id'] as String,
  modelName: json['model_name'] as String,
  provider: json['provider'] as String?,
);

Map<String, dynamic> _$KnowledgeModelStrategyToJson(
  _KnowledgeModelStrategy instance,
) => <String, dynamic>{
  'id': instance.id,
  'model_name': instance.modelName,
  'provider': instance.provider,
};
