// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_data_v2_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReportDataDto _$ReportDataDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportDataDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'execution_id',
        'workflow_id',
        'scoring_strategy',
        'user_name',
        'scoring_engine_name',
        'strictness_level',
        'local_time_str',
        'custom_preface_md',
        'profile_id',
        'profile_name',
        'available_profiles',
        'global_score',
        'has_warning',
        'global_metrics',
        'global_synthesis',
        'results',
        'hydrated_references',
        'evaluative_matrices',
        'informational_matrices',
        'content_blocks',
        'visible_metadata',
        'layouts',
        'matrix_visible_columns',
        'created_at',
        'org_name',
        'cost_estimate',
        'total_tokens',
        'prompt_tokens',
        'completion_tokens',
        'reasoning_tokens',
        'mcp_tool_audit',
        'grouped_extensions',
        'penalties_applied',
      ],
    );
    final val = _ReportDataDto(
      executionId: $checkedConvert('execution_id', (v) => v as String),
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
      scoringStrategy: $checkedConvert('scoring_strategy', (v) => v as String?),
      userName: $checkedConvert('user_name', (v) => v as String?),
      scoringEngineName: $checkedConvert(
        'scoring_engine_name',
        (v) => v as String?,
      ),
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt(),
      ),
      localTimeStr: $checkedConvert('local_time_str', (v) => v as String?),
      customPrefaceMd: $checkedConvert(
        'custom_preface_md',
        (v) => v as String?,
      ),
      profileId: $checkedConvert('profile_id', (v) => v as String),
      profileName: $checkedConvert(
        'profile_name',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      availableProfiles: $checkedConvert(
        'available_profiles',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
      globalScore: $checkedConvert(
        'global_score',
        (v) => (v as num?)?.toDouble(),
      ),
      hasWarning: $checkedConvert('has_warning', (v) => v as bool? ?? false),
      globalMetrics: $checkedConvert(
        'global_metrics',
        (v) => v == null
            ? null
            : ExecutionMetricsDTO.fromJson(v as Map<String, dynamic>),
      ),
      globalSynthesis: $checkedConvert(
        'global_synthesis',
        (v) => v == null
            ? null
            : GlobalSynthesisDTO.fromJson(v as Map<String, dynamic>),
      ),
      results: $checkedConvert(
        'results',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => AtomResultDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      hydratedReferences: $checkedConvert(
        'hydrated_references',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(
                k,
                HydratedAtomDTO.fromJson(e as Map<String, dynamic>),
              ),
            ) ??
            const {},
      ),
      evaluativeMatrices: $checkedConvert(
        'evaluative_matrices',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) => MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
            )
            .toList(),
      ),
      informationalMatrices: $checkedConvert(
        'informational_matrices',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) => MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
            )
            .toList(),
      ),
      contentBlocks: $checkedConvert(
        'content_blocks',
        (v) => (v as List<dynamic>?)
            ?.map((e) => e as Map<String, dynamic>)
            .toList(),
      ),
      visibleMetadata: $checkedConvert(
        'visible_metadata',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      layouts: $checkedConvert(
        'layouts',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => ReportLayoutDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      matrixVisibleColumns: $checkedConvert(
        'matrix_visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      orgName: $checkedConvert('org_name', (v) => v as String?),
      costEstimate: $checkedConvert(
        'cost_estimate',
        (v) => (v as num?)?.toDouble(),
      ),
      totalTokens: $checkedConvert('total_tokens', (v) => (v as num?)?.toInt()),
      promptTokens: $checkedConvert(
        'prompt_tokens',
        (v) => (v as num?)?.toInt(),
      ),
      completionTokens: $checkedConvert(
        'completion_tokens',
        (v) => (v as num?)?.toInt(),
      ),
      reasoningTokens: $checkedConvert(
        'reasoning_tokens',
        (v) => (v as num?)?.toInt(),
      ),
      mcpToolAudit: $checkedConvert(
        'mcp_tool_audit',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => McpAuditTraceDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      groupedExtensions: $checkedConvert(
        'grouped_extensions',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as List<dynamic>),
        ),
      ),
      penaltiesApplied: $checkedConvert(
        'penalties_applied',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'executionId': 'execution_id',
    'workflowId': 'workflow_id',
    'scoringStrategy': 'scoring_strategy',
    'userName': 'user_name',
    'scoringEngineName': 'scoring_engine_name',
    'strictnessLevel': 'strictness_level',
    'localTimeStr': 'local_time_str',
    'customPrefaceMd': 'custom_preface_md',
    'profileId': 'profile_id',
    'profileName': 'profile_name',
    'availableProfiles': 'available_profiles',
    'globalScore': 'global_score',
    'hasWarning': 'has_warning',
    'globalMetrics': 'global_metrics',
    'globalSynthesis': 'global_synthesis',
    'hydratedReferences': 'hydrated_references',
    'evaluativeMatrices': 'evaluative_matrices',
    'informationalMatrices': 'informational_matrices',
    'contentBlocks': 'content_blocks',
    'visibleMetadata': 'visible_metadata',
    'matrixVisibleColumns': 'matrix_visible_columns',
    'createdAt': 'created_at',
    'orgName': 'org_name',
    'costEstimate': 'cost_estimate',
    'totalTokens': 'total_tokens',
    'promptTokens': 'prompt_tokens',
    'completionTokens': 'completion_tokens',
    'reasoningTokens': 'reasoning_tokens',
    'mcpToolAudit': 'mcp_tool_audit',
    'groupedExtensions': 'grouped_extensions',
    'penaltiesApplied': 'penalties_applied',
  },
);

Map<String, dynamic> _$ReportDataDtoToJson(_ReportDataDto instance) =>
    <String, dynamic>{
      'execution_id': instance.executionId,
      'workflow_id': instance.workflowId,
      'scoring_strategy': instance.scoringStrategy,
      'user_name': instance.userName,
      'scoring_engine_name': instance.scoringEngineName,
      'strictness_level': instance.strictnessLevel,
      'local_time_str': instance.localTimeStr,
      'custom_preface_md': instance.customPrefaceMd,
      'profile_id': instance.profileId,
      'profile_name': instance.profileName?.toJson(),
      'available_profiles': instance.availableProfiles.map(
        (k, e) => MapEntry(k, e.toJson()),
      ),
      'global_score': instance.globalScore,
      'has_warning': instance.hasWarning,
      'global_metrics': instance.globalMetrics?.toJson(),
      'global_synthesis': instance.globalSynthesis?.toJson(),
      'results': instance.results.map((e) => e.toJson()).toList(),
      'hydrated_references': instance.hydratedReferences.map(
        (k, e) => MapEntry(k, e.toJson()),
      ),
      'evaluative_matrices': instance.evaluativeMatrices
          ?.map((e) => e.toJson())
          .toList(),
      'informational_matrices': instance.informationalMatrices
          ?.map((e) => e.toJson())
          .toList(),
      'content_blocks': instance.contentBlocks,
      'visible_metadata': instance.visibleMetadata,
      'layouts': instance.layouts.map((e) => e.toJson()).toList(),
      'matrix_visible_columns': instance.matrixVisibleColumns,
      'created_at': instance.createdAt,
      'org_name': instance.orgName,
      'cost_estimate': instance.costEstimate,
      'total_tokens': instance.totalTokens,
      'prompt_tokens': instance.promptTokens,
      'completion_tokens': instance.completionTokens,
      'reasoning_tokens': instance.reasoningTokens,
      'mcp_tool_audit': instance.mcpToolAudit.map((e) => e.toJson()).toList(),
      'grouped_extensions': instance.groupedExtensions,
      'penalties_applied': instance.penaltiesApplied,
    };
