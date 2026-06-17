// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_data_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SduiParagraphBlock _$SduiParagraphBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiParagraphBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['text', 'citations', 'block_type']);
      final val = SduiParagraphBlock(
        text: $checkedConvert('text', (v) => v as String),
        citations: $checkedConvert(
          'citations',
          (v) =>
              (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
              const [],
        ),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiParagraphBlockToJson(SduiParagraphBlock instance) =>
    <String, dynamic>{
      'text': instance.text,
      'citations': instance.citations,
      'block_type': instance.$type,
    };

SduiBulletListBlock _$SduiBulletListBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiBulletListBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['items', 'block_type']);
      final val = SduiBulletListBlock(
        items: $checkedConvert(
          'items',
          (v) => (v as List<dynamic>)
              .map(
                (e) =>
                    SduiBulletListItemDTO.fromJson(e as Map<String, dynamic>),
              )
              .toList(),
        ),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiBulletListBlockToJson(
  SduiBulletListBlock instance,
) => <String, dynamic>{
  'items': instance.items.map((e) => e.toJson()).toList(),
  'block_type': instance.$type,
};

SduiAlertBoxBlock _$SduiAlertBoxBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiAlertBoxBlock', json, ($checkedConvert) {
      $checkKeys(
        json,
        allowedKeys: const ['text', 'severity', 'citations', 'block_type'],
      );
      final val = SduiAlertBoxBlock(
        text: $checkedConvert('text', (v) => v as String),
        severity: $checkedConvert('severity', (v) => v as String),
        citations: $checkedConvert(
          'citations',
          (v) =>
              (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
              const [],
        ),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiAlertBoxBlockToJson(SduiAlertBoxBlock instance) =>
    <String, dynamic>{
      'text': instance.text,
      'severity': instance.severity,
      'citations': instance.citations,
      'block_type': instance.$type,
    };

SduiHeroInsightBlock _$SduiHeroInsightBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('SduiHeroInsightBlock', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['text', 'block_type']);
  final val = SduiHeroInsightBlock(
    text: $checkedConvert('text', (v) => v as String),
    $type: $checkedConvert('block_type', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiHeroInsightBlockToJson(
  SduiHeroInsightBlock instance,
) => <String, dynamic>{'text': instance.text, 'block_type': instance.$type};

_SduiBulletListItemDTO _$SduiBulletListItemDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SduiBulletListItemDTO', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['text', 'citations']);
  final val = _SduiBulletListItemDTO(
    text: $checkedConvert('text', (v) => v as String),
    citations: $checkedConvert(
      'citations',
      (v) =>
          (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
          const [],
    ),
  );
  return val;
});

Map<String, dynamic> _$SduiBulletListItemDTOToJson(
  _SduiBulletListItemDTO instance,
) => <String, dynamic>{'text': instance.text, 'citations': instance.citations};

_ReportLayoutDTO _$ReportLayoutDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportLayoutDTO',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'preset_view',
        'matrix_type',
        'title',
        'description',
        'axes',
        'visible_columns',
        'text_delivery_mode',
        'synthesis',
        'synthesis_blocks',
      ],
    );
    final val = _ReportLayoutDTO(
      presetView: $checkedConvert(
        'preset_view',
        (v) => $enumDecode(_$PresetViewEnumMap, v),
      ),
      matrixType: $checkedConvert('matrix_type', (v) => v as String?),
      title: $checkedConvert(
        'title',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
      ),
      axes: $checkedConvert(
        'axes',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      visibleColumns: $checkedConvert(
        'visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const ['label', 'score', 'distribution', 'row_explanation'],
      ),
      textDeliveryMode: $checkedConvert(
        'text_delivery_mode',
        (v) => v as String,
      ),
      synthesis: $checkedConvert(
        'synthesis',
        (v) => v as Map<String, dynamic>?,
      ),
      synthesisBlocks: $checkedConvert(
        'synthesis_blocks',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'presetView': 'preset_view',
    'matrixType': 'matrix_type',
    'visibleColumns': 'visible_columns',
    'textDeliveryMode': 'text_delivery_mode',
    'synthesisBlocks': 'synthesis_blocks',
  },
);

Map<String, dynamic> _$ReportLayoutDTOToJson(
  _ReportLayoutDTO instance,
) => <String, dynamic>{
  'preset_view': _$PresetViewEnumMap[instance.presetView]!,
  'matrix_type': instance.matrixType,
  'title': instance.title?.toJson(),
  'description': instance.description?.toJson(),
  'axes': instance.axes.map((e) => e.toJson()).toList(),
  'visible_columns': instance.visibleColumns,
  'text_delivery_mode': instance.textDeliveryMode,
  'synthesis': instance.synthesis,
  'synthesis_blocks': instance.synthesisBlocks.map((e) => e.toJson()).toList(),
};

const _$PresetViewEnumMap = {
  PresetView.metrics1d: '1d_metrics',
  PresetView.compare2d: '2d_compare',
  PresetView.complex3d: '3d_complex',
  PresetView.matrix3d: '3d_matrix',
  PresetView.textOnly: 'text_only',
  PresetView.defaultView: 'default',
};

_MCPToolAuditDTO _$MCPToolAuditDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_MCPToolAuditDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'tool_id',
            'step_name',
            'query',
            'response_summary',
            'source_urls',
            'timestamp',
            'duration_ms',
          ],
        );
        final val = _MCPToolAuditDTO(
          id: $checkedConvert('id', (v) => v as String?),
          toolId: $checkedConvert('tool_id', (v) => v as String),
          stepName: $checkedConvert('step_name', (v) => v as String),
          query: $checkedConvert('query', (v) => v as String),
          responseSummary: $checkedConvert(
            'response_summary',
            (v) => v as String? ?? '',
          ),
          sourceUrls: $checkedConvert(
            'source_urls',
            (v) =>
                (v as List<dynamic>?)?.map((e) => e as String).toList() ??
                const [],
          ),
          timestamp: $checkedConvert('timestamp', (v) => v as String?),
          durationMs: $checkedConvert(
            'duration_ms',
            (v) => (v as num?)?.toInt() ?? 0,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'toolId': 'tool_id',
        'stepName': 'step_name',
        'responseSummary': 'response_summary',
        'sourceUrls': 'source_urls',
        'durationMs': 'duration_ms',
      },
    );

Map<String, dynamic> _$MCPToolAuditDTOToJson(_MCPToolAuditDTO instance) =>
    <String, dynamic>{
      'id': instance.id,
      'tool_id': instance.toolId,
      'step_name': instance.stepName,
      'query': instance.query,
      'response_summary': instance.responseSummary,
      'source_urls': instance.sourceUrls,
      'timestamp': instance.timestamp,
      'duration_ms': instance.durationMs,
    };

_ReportDataDTO _$ReportDataDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportDataDTO',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'workflow_id',
        'profile_id',
        'profile_name',
        'available_profiles',
        'global_score',
        'layouts',
        'created_at',
        'local_time_str',
        'org_name',
        'user_name',
        'scoring_engine_name',
        'strictness_level',
        'custom_preface_md',
        'scoring_strategy',
        'cost_estimate',
        'total_tokens',
        'prompt_tokens',
        'completion_tokens',
        'reasoning_tokens',
        'mcp_tool_audit',
        'has_warning',
        'content_blocks',
        'visible_metadata',
        'grouped_extensions',
        'penalties_applied',
        'evaluative_matrices',
        'informational_matrices',
        'matrix_visible_columns',
      ],
    );
    final val = _ReportDataDTO(
      workflowId: $checkedConvert('workflow_id', (v) => v as String),
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
      layouts: $checkedConvert(
        'layouts',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => ReportLayoutDTO.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      localTimeStr: $checkedConvert('local_time_str', (v) => v as String?),
      orgName: $checkedConvert('org_name', (v) => v as String?),
      userName: $checkedConvert('user_name', (v) => v as String?),
      scoringEngineName: $checkedConvert(
        'scoring_engine_name',
        (v) => v as String?,
      ),
      strictnessLevel: $checkedConvert(
        'strictness_level',
        (v) => (v as num?)?.toInt(),
      ),
      customPrefaceMd: $checkedConvert(
        'custom_preface_md',
        (v) => v as String?,
      ),
      scoringStrategy: $checkedConvert(
        'scoring_strategy',
        (v) => $enumDecodeNullable(_$ScoringStrategyEnumMap, v),
      ),
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
                  (e) => MCPToolAuditDTO.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      hasWarning: $checkedConvert('has_warning', (v) => v as bool? ?? false),
      contentBlocks: $checkedConvert(
        'content_blocks',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      visibleMetadata: $checkedConvert(
        'visible_metadata',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      groupedExtensions: $checkedConvert(
        'grouped_extensions',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as List<dynamic>),
            ) ??
            const {},
      ),
      penaltiesApplied: $checkedConvert(
        'penalties_applied',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      evaluativeMatrices: $checkedConvert(
        'evaluative_matrices',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      informationalMatrices: $checkedConvert(
        'informational_matrices',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) =>
                      MatrixScorecardRowDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      matrixVisibleColumns: $checkedConvert(
        'matrix_visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ??
            const ['label', 'score', 'distribution', 'row_explanation'],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'workflowId': 'workflow_id',
    'profileId': 'profile_id',
    'profileName': 'profile_name',
    'availableProfiles': 'available_profiles',
    'globalScore': 'global_score',
    'createdAt': 'created_at',
    'localTimeStr': 'local_time_str',
    'orgName': 'org_name',
    'userName': 'user_name',
    'scoringEngineName': 'scoring_engine_name',
    'strictnessLevel': 'strictness_level',
    'customPrefaceMd': 'custom_preface_md',
    'scoringStrategy': 'scoring_strategy',
    'costEstimate': 'cost_estimate',
    'totalTokens': 'total_tokens',
    'promptTokens': 'prompt_tokens',
    'completionTokens': 'completion_tokens',
    'reasoningTokens': 'reasoning_tokens',
    'mcpToolAudit': 'mcp_tool_audit',
    'hasWarning': 'has_warning',
    'contentBlocks': 'content_blocks',
    'visibleMetadata': 'visible_metadata',
    'groupedExtensions': 'grouped_extensions',
    'penaltiesApplied': 'penalties_applied',
    'evaluativeMatrices': 'evaluative_matrices',
    'informationalMatrices': 'informational_matrices',
    'matrixVisibleColumns': 'matrix_visible_columns',
  },
);

Map<String, dynamic> _$ReportDataDTOToJson(_ReportDataDTO instance) =>
    <String, dynamic>{
      'workflow_id': instance.workflowId,
      'profile_id': instance.profileId,
      'profile_name': instance.profileName?.toJson(),
      'available_profiles': instance.availableProfiles.map(
        (k, e) => MapEntry(k, e.toJson()),
      ),
      'global_score': instance.globalScore,
      'layouts': instance.layouts.map((e) => e.toJson()).toList(),
      'created_at': instance.createdAt,
      'local_time_str': instance.localTimeStr,
      'org_name': instance.orgName,
      'user_name': instance.userName,
      'scoring_engine_name': instance.scoringEngineName,
      'strictness_level': instance.strictnessLevel,
      'custom_preface_md': instance.customPrefaceMd,
      'scoring_strategy': _$ScoringStrategyEnumMap[instance.scoringStrategy],
      'cost_estimate': instance.costEstimate,
      'total_tokens': instance.totalTokens,
      'prompt_tokens': instance.promptTokens,
      'completion_tokens': instance.completionTokens,
      'reasoning_tokens': instance.reasoningTokens,
      'mcp_tool_audit': instance.mcpToolAudit.map((e) => e.toJson()).toList(),
      'has_warning': instance.hasWarning,
      'content_blocks': instance.contentBlocks.map((e) => e.toJson()).toList(),
      'visible_metadata': instance.visibleMetadata,
      'grouped_extensions': instance.groupedExtensions,
      'penalties_applied': instance.penaltiesApplied,
      'evaluative_matrices': instance.evaluativeMatrices
          .map((e) => e.toJson())
          .toList(),
      'informational_matrices': instance.informationalMatrices
          .map((e) => e.toJson())
          .toList(),
      'matrix_visible_columns': instance.matrixVisibleColumns,
    };

const _$ScoringStrategyEnumMap = {
  ScoringStrategy.waterfall: 'WATERFALL',
  ScoringStrategy.dampening: 'DAMPENING',
  ScoringStrategy.average: 'AVERAGE',
  ScoringStrategy.weightedAverage: 'WEIGHTED_AVERAGE',
  ScoringStrategy.pureMath: 'PURE_MATH',
};
