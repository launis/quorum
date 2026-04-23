// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_data_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReportAxisDTO _$ReportAxisDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportAxisDTO',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'name',
        'description',
        'score',
        'justification',
        'cited_source_id',
        'cited_text_quote',
        'cited_web_citation',
        'coaching',
        'confidence',
        'falsification',
        'missing_context',
        'risk_flag',
        'remediation_steps',
        'emotional_sentiment',
        'theory_link',
        'scale_min',
        'scale_max',
        'scale_labels',
        'ui_plot_ratio',
        'ui_boundary_labels',
      ],
    );
    final val = _ReportAxisDTO(
      name: $checkedConvert('name', (v) => v as String),
      description: $checkedConvert('description', (v) => v as String?),
      score: $checkedConvert('score', (v) => (v as num?)?.toDouble()),
      justification: $checkedConvert('justification', (v) => v as String?),
      citedSourceId: $checkedConvert('cited_source_id', (v) => v as String?),
      citedTextQuote: $checkedConvert('cited_text_quote', (v) => v as String?),
      citedWebCitation: $checkedConvert(
        'cited_web_citation',
        (v) => v as String?,
      ),
      coaching: $checkedConvert('coaching', (v) => v as String?),
      confidence: $checkedConvert('confidence', (v) => (v as num?)?.toDouble()),
      falsification: $checkedConvert('falsification', (v) => v as String?),
      missingContext: $checkedConvert('missing_context', (v) => v as String?),
      riskFlag: $checkedConvert('risk_flag', (v) => v as bool?),
      remediationSteps: $checkedConvert(
        'remediation_steps',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      emotionalSentiment: $checkedConvert(
        'emotional_sentiment',
        (v) => v as String?,
      ),
      theoryLink: $checkedConvert('theory_link', (v) => v as String?),
      scaleMin: $checkedConvert(
        'scale_min',
        (v) => (v as num?)?.toDouble() ?? 0.0,
      ),
      scaleMax: $checkedConvert(
        'scale_max',
        (v) => (v as num?)?.toDouble() ?? 6.0,
      ),
      scaleLabels: $checkedConvert(
        'scale_labels',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ) ??
            const {},
      ),
      uiPlotRatio: $checkedConvert(
        'ui_plot_ratio',
        (v) => (v as num?)?.toDouble(),
      ),
      uiBoundaryLabels: $checkedConvert(
        'ui_boundary_labels',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ) ??
            const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'citedSourceId': 'cited_source_id',
    'citedTextQuote': 'cited_text_quote',
    'citedWebCitation': 'cited_web_citation',
    'missingContext': 'missing_context',
    'riskFlag': 'risk_flag',
    'remediationSteps': 'remediation_steps',
    'emotionalSentiment': 'emotional_sentiment',
    'theoryLink': 'theory_link',
    'scaleMin': 'scale_min',
    'scaleMax': 'scale_max',
    'scaleLabels': 'scale_labels',
    'uiPlotRatio': 'ui_plot_ratio',
    'uiBoundaryLabels': 'ui_boundary_labels',
  },
);

Map<String, dynamic> _$ReportAxisDTOToJson(_ReportAxisDTO instance) =>
    <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'score': instance.score,
      'justification': instance.justification,
      'cited_source_id': instance.citedSourceId,
      'cited_text_quote': instance.citedTextQuote,
      'cited_web_citation': instance.citedWebCitation,
      'coaching': instance.coaching,
      'confidence': instance.confidence,
      'falsification': instance.falsification,
      'missing_context': instance.missingContext,
      'risk_flag': instance.riskFlag,
      'remediation_steps': instance.remediationSteps,
      'emotional_sentiment': instance.emotionalSentiment,
      'theory_link': instance.theoryLink,
      'scale_min': instance.scaleMin,
      'scale_max': instance.scaleMax,
      'scale_labels': instance.scaleLabels,
      'ui_plot_ratio': instance.uiPlotRatio,
      'ui_boundary_labels': instance.uiBoundaryLabels,
    };

_ReportLayoutDTO _$ReportLayoutDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
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
            'text_delivery_mode',
            'synthesis',
            'synthesis_md',
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
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          description: $checkedConvert(
            'description',
            (v) =>
                v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
          ),
          axes: $checkedConvert(
            'axes',
            (v) =>
                (v as List<dynamic>?)
                    ?.map(
                      (e) => ReportAxisDTO.fromJson(e as Map<String, dynamic>),
                    )
                    .toList() ??
                const [],
          ),
          textDeliveryMode: $checkedConvert(
            'text_delivery_mode',
            (v) => v as String,
          ),
          synthesis: $checkedConvert(
            'synthesis',
            (v) => v as Map<String, dynamic>?,
          ),
          synthesisMd: $checkedConvert('synthesis_md', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'presetView': 'preset_view',
        'matrixType': 'matrix_type',
        'textDeliveryMode': 'text_delivery_mode',
        'synthesisMd': 'synthesis_md',
      },
    );

Map<String, dynamic> _$ReportLayoutDTOToJson(_ReportLayoutDTO instance) =>
    <String, dynamic>{
      'preset_view': _$PresetViewEnumMap[instance.presetView]!,
      'matrix_type': instance.matrixType,
      'title': instance.title?.toJson(),
      'description': instance.description?.toJson(),
      'axes': instance.axes.map((e) => e.toJson()).toList(),
      'text_delivery_mode': instance.textDeliveryMode,
      'synthesis': instance.synthesis,
      'synthesis_md': instance.synthesisMd,
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
        'org_name',
        'cost_estimate',
        'total_tokens',
        'prompt_tokens',
        'completion_tokens',
        'reasoning_tokens',
        'mcp_tool_audit',
        'has_warning',
        'synthesized_markdown',
        'visible_metadata',
        'grouped_extensions',
        'penalties_applied',
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
                  (e) => MCPToolAuditDTO.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
      hasWarning: $checkedConvert('has_warning', (v) => v as bool? ?? false),
      synthesizedMarkdown: $checkedConvert(
        'synthesized_markdown',
        (v) => v as String?,
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
    'orgName': 'org_name',
    'costEstimate': 'cost_estimate',
    'totalTokens': 'total_tokens',
    'promptTokens': 'prompt_tokens',
    'completionTokens': 'completion_tokens',
    'reasoningTokens': 'reasoning_tokens',
    'mcpToolAudit': 'mcp_tool_audit',
    'hasWarning': 'has_warning',
    'synthesizedMarkdown': 'synthesized_markdown',
    'visibleMetadata': 'visible_metadata',
    'groupedExtensions': 'grouped_extensions',
    'penaltiesApplied': 'penalties_applied',
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
      'org_name': instance.orgName,
      'cost_estimate': instance.costEstimate,
      'total_tokens': instance.totalTokens,
      'prompt_tokens': instance.promptTokens,
      'completion_tokens': instance.completionTokens,
      'reasoning_tokens': instance.reasoningTokens,
      'mcp_tool_audit': instance.mcpToolAudit.map((e) => e.toJson()).toList(),
      'has_warning': instance.hasWarning,
      'synthesized_markdown': instance.synthesizedMarkdown,
      'visible_metadata': instance.visibleMetadata,
      'grouped_extensions': instance.groupedExtensions,
      'penalties_applied': instance.penaltiesApplied,
    };
