// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_artifact.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReportStoragePaths _$ReportStoragePathsFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ReportStoragePaths',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'pdf_path',
            'sdui_json_path',
            'excel_path',
            'csv_path',
          ],
        );
        final val = _ReportStoragePaths(
          pdfPath: $checkedConvert('pdf_path', (v) => v as String?),
          sduiJsonPath: $checkedConvert('sdui_json_path', (v) => v as String?),
          excelPath: $checkedConvert('excel_path', (v) => v as String?),
          csvPath: $checkedConvert('csv_path', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'pdfPath': 'pdf_path',
        'sduiJsonPath': 'sdui_json_path',
        'excelPath': 'excel_path',
        'csvPath': 'csv_path',
      },
    );

Map<String, dynamic> _$ReportStoragePathsToJson(_ReportStoragePaths instance) =>
    <String, dynamic>{
      'pdf_path': instance.pdfPath,
      'sdui_json_path': instance.sduiJsonPath,
      'excel_path': instance.excelPath,
      'csv_path': instance.csvPath,
    };

_ReportMetadata _$ReportMetadataFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportMetadata',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'cost_usd',
        'duration_ms',
        'tokens_used',
        'llm_model',
        'provider',
        'cognitive_tier',
        'model_registry_id',
        'thinking_tokens',
      ],
    );
    final val = _ReportMetadata(
      costUsd: $checkedConvert('cost_usd', (v) => (v as num?)?.toDouble()),
      durationMs: $checkedConvert('duration_ms', (v) => (v as num?)?.toInt()),
      tokensUsed: $checkedConvert('tokens_used', (v) => (v as num?)?.toInt()),
      llmModel: $checkedConvert('llm_model', (v) => v as String?),
      provider: $checkedConvert('provider', (v) => v as String?),
      cognitiveTier: $checkedConvert(
        'cognitive_tier',
        (v) => $enumDecodeNullable(_$CognitiveTierEnumMap, v),
      ),
      modelRegistryId: $checkedConvert(
        'model_registry_id',
        (v) => v as String?,
      ),
      thinkingTokens: $checkedConvert(
        'thinking_tokens',
        (v) => (v as num?)?.toInt(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'costUsd': 'cost_usd',
    'durationMs': 'duration_ms',
    'tokensUsed': 'tokens_used',
    'llmModel': 'llm_model',
    'cognitiveTier': 'cognitive_tier',
    'modelRegistryId': 'model_registry_id',
    'thinkingTokens': 'thinking_tokens',
  },
);

Map<String, dynamic> _$ReportMetadataToJson(_ReportMetadata instance) =>
    <String, dynamic>{
      'cost_usd': instance.costUsd,
      'duration_ms': instance.durationMs,
      'tokens_used': instance.tokensUsed,
      'llm_model': instance.llmModel,
      'provider': instance.provider,
      'cognitive_tier': _$CognitiveTierEnumMap[instance.cognitiveTier],
      'model_registry_id': instance.modelRegistryId,
      'thinking_tokens': instance.thinkingTokens,
    };

const _$CognitiveTierEnumMap = {
  CognitiveTier.fast: 'fast',
  CognitiveTier.balanced: 'balanced',
  CognitiveTier.deep: 'deep',
  CognitiveTier.reasoning: 'reasoning',
};

_ReportRowItem _$ReportRowItemFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ReportRowItem',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'execution_id',
            'report_id',
            'metric_key',
            'metric_label',
            'score',
            'max_scale',
            'weight',
            'reasoning',
            'quote',
          ],
        );
        final val = _ReportRowItem(
          executionId: $checkedConvert('execution_id', (v) => v as String),
          reportId: $checkedConvert('report_id', (v) => v as String),
          metricKey: $checkedConvert('metric_key', (v) => v as String),
          metricLabel: $checkedConvert('metric_label', (v) => v as String),
          score: $checkedConvert('score', (v) => (v as num).toDouble()),
          maxScale: $checkedConvert('max_scale', (v) => (v as num).toDouble()),
          weight: $checkedConvert('weight', (v) => (v as num).toDouble()),
          reasoning: $checkedConvert('reasoning', (v) => v as String?),
          quote: $checkedConvert('quote', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'executionId': 'execution_id',
        'reportId': 'report_id',
        'metricKey': 'metric_key',
        'metricLabel': 'metric_label',
        'maxScale': 'max_scale',
      },
    );

Map<String, dynamic> _$ReportRowItemToJson(_ReportRowItem instance) =>
    <String, dynamic>{
      'execution_id': instance.executionId,
      'report_id': instance.reportId,
      'metric_key': instance.metricKey,
      'metric_label': instance.metricLabel,
      'score': instance.score,
      'max_scale': instance.maxScale,
      'weight': instance.weight,
      'reasoning': instance.reasoning,
      'quote': instance.quote,
    };

_ReportArtifact _$ReportArtifactFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ReportArtifact',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'execution_id',
            'workflow_id',
            'profile_id',
            'locale',
            'title',
            'status',
            'storage_paths',
            'metadata',
            'custom_preface_md',
            'error_message',
            'created_at',
            'updated_at',
          ],
        );
        final val = _ReportArtifact(
          id: $checkedConvert('id', (v) => v as String),
          executionId: $checkedConvert('execution_id', (v) => v as String),
          workflowId: $checkedConvert('workflow_id', (v) => v as String),
          profileId: $checkedConvert('profile_id', (v) => v as String),
          locale: $checkedConvert('locale', (v) => v as String),
          title: $checkedConvert('title', (v) => v as String),
          status: $checkedConvert(
            'status',
            (v) => $enumDecode(_$ReportStatusEnumMap, v),
          ),
          storagePaths: $checkedConvert(
            'storage_paths',
            (v) => v == null
                ? const ReportStoragePaths()
                : ReportStoragePaths.fromJson(v as Map<String, dynamic>),
          ),
          metadata: $checkedConvert(
            'metadata',
            (v) => v == null
                ? const ReportMetadata()
                : ReportMetadata.fromJson(v as Map<String, dynamic>),
          ),
          customPrefaceMd: $checkedConvert(
            'custom_preface_md',
            (v) => v as String?,
          ),
          errorMessage: $checkedConvert('error_message', (v) => v as String?),
          createdAt: $checkedConvert(
            'created_at',
            (v) => DateTime.parse(v as String),
          ),
          updatedAt: $checkedConvert(
            'updated_at',
            (v) => DateTime.parse(v as String),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'executionId': 'execution_id',
        'workflowId': 'workflow_id',
        'profileId': 'profile_id',
        'storagePaths': 'storage_paths',
        'customPrefaceMd': 'custom_preface_md',
        'errorMessage': 'error_message',
        'createdAt': 'created_at',
        'updatedAt': 'updated_at',
      },
    );

Map<String, dynamic> _$ReportArtifactToJson(_ReportArtifact instance) =>
    <String, dynamic>{
      'id': instance.id,
      'execution_id': instance.executionId,
      'workflow_id': instance.workflowId,
      'profile_id': instance.profileId,
      'locale': instance.locale,
      'title': instance.title,
      'status': _$ReportStatusEnumMap[instance.status]!,
      'storage_paths': instance.storagePaths.toJson(),
      'metadata': instance.metadata.toJson(),
      'custom_preface_md': instance.customPrefaceMd,
      'error_message': instance.errorMessage,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

const _$ReportStatusEnumMap = {
  ReportStatus.pending: 'pending',
  ReportStatus.generating: 'generating',
  ReportStatus.ready: 'ready',
  ReportStatus.failed: 'failed',
};

_ReportArtifactSummary _$ReportArtifactSummaryFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportArtifactSummary',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'execution_id',
        'profile_id',
        'locale',
        'title',
        'status',
        'created_at',
        'updated_at',
      ],
    );
    final val = _ReportArtifactSummary(
      id: $checkedConvert('id', (v) => v as String),
      executionId: $checkedConvert('execution_id', (v) => v as String),
      profileId: $checkedConvert('profile_id', (v) => v as String),
      locale: $checkedConvert('locale', (v) => v as String),
      title: $checkedConvert('title', (v) => v as String),
      status: $checkedConvert(
        'status',
        (v) => $enumDecode(_$ReportStatusEnumMap, v),
      ),
      createdAt: $checkedConvert(
        'created_at',
        (v) => DateTime.parse(v as String),
      ),
      updatedAt: $checkedConvert(
        'updated_at',
        (v) => DateTime.parse(v as String),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'executionId': 'execution_id',
    'profileId': 'profile_id',
    'createdAt': 'created_at',
    'updatedAt': 'updated_at',
  },
);

Map<String, dynamic> _$ReportArtifactSummaryToJson(
  _ReportArtifactSummary instance,
) => <String, dynamic>{
  'id': instance.id,
  'execution_id': instance.executionId,
  'profile_id': instance.profileId,
  'locale': instance.locale,
  'title': instance.title,
  'status': _$ReportStatusEnumMap[instance.status]!,
  'created_at': instance.createdAt.toIso8601String(),
  'updated_at': instance.updatedAt.toIso8601String(),
};
