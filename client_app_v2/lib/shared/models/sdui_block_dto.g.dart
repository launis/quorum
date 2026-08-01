// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sdui_block_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SduiParagraphBlock _$SduiParagraphBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiParagraphBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'text',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiParagraphBlock(
      id: $checkedConvert('id', (v) => v as String?),
      text: $checkedConvert('text', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiParagraphBlockToJson(SduiParagraphBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'text': instance.text,
      'citations': instance.citations,
      'exact_quotes': instance.exactQuotes,
      'block_type': instance.$type,
    };

SduiBulletListBlock _$SduiBulletListBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiBulletListBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'items', 'block_type']);
      final val = SduiBulletListBlock(
        id: $checkedConvert('id', (v) => v as String?),
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
  'id': instance.id,
  'items': instance.items.map((e) => e.toJson()).toList(),
  'block_type': instance.$type,
};

SduiAccordionBlock _$SduiAccordionBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiAccordionBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'title',
        'severity',
        'icon_name',
        'children',
        'block_type',
      ],
    );
    final val = SduiAccordionBlock(
      id: $checkedConvert('id', (v) => v as String?),
      title: $checkedConvert('title', (v) => v as String),
      severity: $checkedConvert('severity', (v) => v as String? ?? 'default'),
      iconName: $checkedConvert('icon_name', (v) => v as String?),
      children: $checkedConvert(
        'children',
        (v) =>
            (v as List<dynamic>?)
                ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
                .toList() ??
            const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'iconName': 'icon_name', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiAccordionBlockToJson(SduiAccordionBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'severity': instance.severity,
      'icon_name': instance.iconName,
      'children': instance.children.map((e) => e.toJson()).toList(),
      'block_type': instance.$type,
    };

SduiAlertBoxBlock _$SduiAlertBoxBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiAlertBoxBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'text',
        'severity',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiAlertBoxBlock(
      id: $checkedConvert('id', (v) => v as String?),
      text: $checkedConvert('text', (v) => v as String),
      severity: $checkedConvert(
        'severity',
        (v) => $enumDecode(_$AlertSeverityEnumMap, v),
      ),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiAlertBoxBlockToJson(SduiAlertBoxBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'text': instance.text,
      'severity': _$AlertSeverityEnumMap[instance.severity]!,
      'citations': instance.citations,
      'exact_quotes': instance.exactQuotes,
      'block_type': instance.$type,
    };

const _$AlertSeverityEnumMap = {
  AlertSeverity.info: 'info',
  AlertSeverity.warning: 'warning',
  AlertSeverity.criticalOverride: 'critical_override',
  AlertSeverity.success: 'success',
  AlertSeverity.error: 'error',
};

SduiHeroInsightBlock _$SduiHeroInsightBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiHeroInsightBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'text',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiHeroInsightBlock(
      id: $checkedConvert('id', (v) => v as String?),
      text: $checkedConvert('text', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiHeroInsightBlockToJson(
  SduiHeroInsightBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'text': instance.text,
  'citations': instance.citations,
  'exact_quotes': instance.exactQuotes,
  'block_type': instance.$type,
};

SduiMarkdownBlock _$SduiMarkdownBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiMarkdownBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'text', 'block_type']);
      final val = SduiMarkdownBlock(
        id: $checkedConvert('id', (v) => v as String?),
        text: $checkedConvert('text', (v) => v as String),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiMarkdownBlockToJson(SduiMarkdownBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'text': instance.text,
      'block_type': instance.$type,
    };

SduiQuoteCardBlock _$SduiQuoteCardBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SduiQuoteCardBlock',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'quote',
            'source_aliases',
            'citations',
            'block_type',
          ],
        );
        final val = SduiQuoteCardBlock(
          id: $checkedConvert('id', (v) => v as String?),
          quote: $checkedConvert('quote', (v) => v as String),
          sourceAliases: $checkedConvert(
            'source_aliases',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          citations: $checkedConvert(
            'citations',
            (v) => (v as List<dynamic>).map((e) => (e as num).toInt()).toList(),
          ),
          $type: $checkedConvert('block_type', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'sourceAliases': 'source_aliases',
        r'$type': 'block_type',
      },
    );

Map<String, dynamic> _$SduiQuoteCardBlockToJson(SduiQuoteCardBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'quote': instance.quote,
      'source_aliases': instance.sourceAliases,
      'citations': instance.citations,
      'block_type': instance.$type,
    };

SduiWarningCardBlock _$SduiWarningCardBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiWarningCardBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['id', 'message', 'quote_text', 'block_type'],
    );
    final val = SduiWarningCardBlock(
      id: $checkedConvert('id', (v) => v as String?),
      message: $checkedConvert('message', (v) => v as String),
      quoteText: $checkedConvert('quote_text', (v) => v as String?),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'quoteText': 'quote_text', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiWarningCardBlockToJson(
  SduiWarningCardBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'message': instance.message,
  'quote_text': instance.quoteText,
  'block_type': instance.$type,
};

SduiNACardBlock _$SduiNACardBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SduiNACardBlock',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'short_circuit_reason_tda_ids',
            'message',
            'block_type',
          ],
        );
        final val = SduiNACardBlock(
          id: $checkedConvert('id', (v) => v as String?),
          shortCircuitReasonTdaIds: $checkedConvert(
            'short_circuit_reason_tda_ids',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          message: $checkedConvert('message', (v) => v as String),
          $type: $checkedConvert('block_type', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'shortCircuitReasonTdaIds': 'short_circuit_reason_tda_ids',
        r'$type': 'block_type',
      },
    );

Map<String, dynamic> _$SduiNACardBlockToJson(SduiNACardBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'short_circuit_reason_tda_ids': instance.shortCircuitReasonTdaIds,
      'message': instance.message,
      'block_type': instance.$type,
    };

SduiGridBlock _$SduiGridBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiGridBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'items', 'block_type']);
      final val = SduiGridBlock(
        id: $checkedConvert('id', (v) => v as String?),
        items: $checkedConvert(
          'items',
          (v) => (v as List<dynamic>)
              .map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
              .toList(),
        ),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiGridBlockToJson(SduiGridBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'items': instance.items.map((e) => e.toJson()).toList(),
      'block_type': instance.$type,
    };

SduiHeaderBlock _$SduiHeaderBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiHeaderBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'title',
        'badges',
        'metadata_lines',
        'costs',
        'tokens',
        'custom_preface_md',
        'block_type',
      ],
    );
    final val = SduiHeaderBlock(
      id: $checkedConvert('id', (v) => v as String?),
      title: $checkedConvert('title', (v) => v as String),
      badges: $checkedConvert(
        'badges',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      metadataLines: $checkedConvert(
        'metadata_lines',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      costs: $checkedConvert('costs', (v) => v as String?),
      tokens: $checkedConvert(
        'tokens',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as String),
        ),
      ),
      customPrefaceMd: $checkedConvert(
        'custom_preface_md',
        (v) => v as String?,
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'metadataLines': 'metadata_lines',
    'customPrefaceMd': 'custom_preface_md',
    r'$type': 'block_type',
  },
);

Map<String, dynamic> _$SduiHeaderBlockToJson(SduiHeaderBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'badges': instance.badges,
      'metadata_lines': instance.metadataLines,
      'costs': instance.costs,
      'tokens': instance.tokens,
      'custom_preface_md': instance.customPrefaceMd,
      'block_type': instance.$type,
    };

SduiRadarChartBlock _$SduiRadarChartBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('SduiRadarChartBlock', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['id', 'title', 'axes', 'block_type']);
  final val = SduiRadarChartBlock(
    id: $checkedConvert('id', (v) => v as String?),
    title: $checkedConvert(
      'title',
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
    $type: $checkedConvert('block_type', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiRadarChartBlockToJson(
  SduiRadarChartBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'title': instance.title?.toJson(),
  'axes': instance.axes.map((e) => e.toJson()).toList(),
  'block_type': instance.$type,
};

SduiScatterPlotBlock _$SduiScatterPlotBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('SduiScatterPlotBlock', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['id', 'title', 'axes', 'block_type']);
  final val = SduiScatterPlotBlock(
    id: $checkedConvert('id', (v) => v as String?),
    title: $checkedConvert(
      'title',
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
    $type: $checkedConvert('block_type', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiScatterPlotBlockToJson(
  SduiScatterPlotBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'title': instance.title?.toJson(),
  'axes': instance.axes.map((e) => e.toJson()).toList(),
  'block_type': instance.$type,
};

SduiMetrics1DBlock _$SduiMetrics1DBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('SduiMetrics1DBlock', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['id', 'title', 'axes', 'block_type']);
  final val = SduiMetrics1DBlock(
    id: $checkedConvert('id', (v) => v as String?),
    title: $checkedConvert(
      'title',
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
    $type: $checkedConvert('block_type', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiMetrics1DBlockToJson(SduiMetrics1DBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title?.toJson(),
      'axes': instance.axes.map((e) => e.toJson()).toList(),
      'block_type': instance.$type,
    };

SduiMatrixTableBlock _$SduiMatrixTableBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiMatrixTableBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'title',
        'axes',
        'matrix_column_labels',
        'extension_labels',
        'matrix_visible_columns',
        'block_type',
      ],
    );
    final val = SduiMatrixTableBlock(
      id: $checkedConvert('id', (v) => v as String?),
      title: $checkedConvert(
        'title',
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
      matrixColumnLabels: $checkedConvert(
        'matrix_column_labels',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
      extensionLabels: $checkedConvert(
        'extension_labels',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(
                $enumDecode(_$XaiExtensionTypeEnumMap, k),
                I18nText.fromJson(e as Map<String, dynamic>),
              ),
            ) ??
            const {},
      ),
      matrixVisibleColumns: $checkedConvert(
        'matrix_visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'matrixColumnLabels': 'matrix_column_labels',
    'extensionLabels': 'extension_labels',
    'matrixVisibleColumns': 'matrix_visible_columns',
    r'$type': 'block_type',
  },
);

Map<String, dynamic> _$SduiMatrixTableBlockToJson(
  SduiMatrixTableBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'title': instance.title?.toJson(),
  'axes': instance.axes.map((e) => e.toJson()).toList(),
  'matrix_column_labels': instance.matrixColumnLabels.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'extension_labels': instance.extensionLabels.map(
    (k, e) => MapEntry(_$XaiExtensionTypeEnumMap[k]!, e.toJson()),
  ),
  'matrix_visible_columns': instance.matrixVisibleColumns,
  'block_type': instance.$type,
};

const _$XaiExtensionTypeEnumMap = {
  XaiExtensionType.citation: 'citation',
  XaiExtensionType.justification: 'justification',
  XaiExtensionType.falsification: 'falsification',
  XaiExtensionType.theoryLink: 'theory_link',
  XaiExtensionType.riskFlag: 'risk_flag',
  XaiExtensionType.coaching: 'coaching',
  XaiExtensionType.missingContext: 'missing_context',
  XaiExtensionType.remediationSteps: 'remediation_steps',
  XaiExtensionType.emotionalSentiment: 'emotional_sentiment',
  XaiExtensionType.confidence: 'confidence',
  XaiExtensionType.sourceId: 'source_id',
  XaiExtensionType.contextualOverride: 'contextual_override',
  XaiExtensionType.varianceValidation: 'variance_validation',
  XaiExtensionType.authenticityEvaluation: 'authenticity_evaluation',
};

_SduiBulletListItemDTO _$SduiBulletListItemDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SduiBulletListItemDTO', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['text', 'citations', 'exact_quotes']);
  final val = _SduiBulletListItemDTO(
    text: $checkedConvert('text', (v) => v as String),
    citations: $checkedConvert(
      'citations',
      (v) =>
          (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
          const [],
    ),
    exactQuotes: $checkedConvert(
      'exact_quotes',
      (v) =>
          (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
    ),
  );
  return val;
}, fieldKeyMap: const {'exactQuotes': 'exact_quotes'});

Map<String, dynamic> _$SduiBulletListItemDTOToJson(
  _SduiBulletListItemDTO instance,
) => <String, dynamic>{
  'text': instance.text,
  'citations': instance.citations,
  'exact_quotes': instance.exactQuotes,
};
