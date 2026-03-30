// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prompt_block.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_TheoryGrounding _$TheoryGroundingFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_TheoryGrounding',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['source_url', 'citation_reference'],
        );
        final val = _TheoryGrounding(
          sourceUrl: $checkedConvert('source_url', (v) => v as String),
          citationReference: $checkedConvert(
            'citation_reference',
            (v) => v as String,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'sourceUrl': 'source_url',
        'citationReference': 'citation_reference',
      },
    );

Map<String, dynamic> _$TheoryGroundingToJson(_TheoryGrounding instance) =>
    <String, dynamic>{
      'source_url': instance.sourceUrl,
      'citation_reference': instance.citationReference,
    };

_MatrixClaim _$MatrixClaimFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_MatrixClaim', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['label', 'ai_description']);
      final val = _MatrixClaim(
        label: $checkedConvert(
          'label',
          (v) => I18nText.fromJson(v as Map<String, dynamic>),
        ),
        aiDescription: $checkedConvert('ai_description', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'aiDescription': 'ai_description'});

Map<String, dynamic> _$MatrixClaimToJson(_MatrixClaim instance) =>
    <String, dynamic>{
      'label': instance.label.toJson(),
      'ai_description': instance.aiDescription,
    };

_MatrixRow _$MatrixRowFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_MatrixRow', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['label', 'ai_description']);
      final val = _MatrixRow(
        label: $checkedConvert(
          'label',
          (v) => I18nText.fromJson(v as Map<String, dynamic>),
        ),
        aiDescription: $checkedConvert('ai_description', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'aiDescription': 'ai_description'});

Map<String, dynamic> _$MatrixRowToJson(_MatrixRow instance) =>
    <String, dynamic>{
      'label': instance.label.toJson(),
      'ai_description': instance.aiDescription,
    };

_MatrixScale _$MatrixScaleFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_MatrixScale', json, ($checkedConvert) {
      $checkKeys(
        json,
        allowedKeys: const ['score', 'name', 'ai_label', 'claims'],
      );
      final val = _MatrixScale(
        score: $checkedConvert('score', (v) => (v as num).toInt()),
        name: $checkedConvert(
          'name',
          (v) =>
              v == null ? null : I18nText.fromJson(v as Map<String, dynamic>),
        ),
        aiLabel: $checkedConvert('ai_label', (v) => v as String),
        claims: $checkedConvert(
          'claims',
          (v) => (v as List<dynamic>)
              .map((e) => MatrixClaim.fromJson(e as Map<String, dynamic>))
              .toList(),
        ),
      );
      return val;
    }, fieldKeyMap: const {'aiLabel': 'ai_label'});

Map<String, dynamic> _$MatrixScaleToJson(_MatrixScale instance) =>
    <String, dynamic>{
      'score': instance.score,
      'name': instance.name?.toJson(),
      'ai_label': instance.aiLabel,
      'claims': instance.claims.map((e) => e.toJson()).toList(),
    };

_PromptBlock _$PromptBlockFromJson(Map<String, dynamic> json) => $checkedCreate(
  '_PromptBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'slug',
        'label',
        'description',
        'ai_description',
        'category_id',
        'is_evaluative',
        'type',
        'allow_decimals',
        'output_extensions',
        'theory_grounding',
        'scale_min',
        'scale_max',
        'scales',
        'rows',
        'columns',
      ],
    );
    final val = _PromptBlock(
      id: $checkedConvert(
        'id',
        (v) => const StrictOpaqueIdConverter().fromJson(v as String),
      ),
      slug: $checkedConvert('slug', (v) => v as String),
      label: $checkedConvert(
        'label',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      description: $checkedConvert(
        'description',
        (v) => I18nText.fromJson(v as Map<String, dynamic>),
      ),
      aiDescription: $checkedConvert('ai_description', (v) => v as String?),
      categoryId: $checkedConvert(
        'category_id',
        (v) => v as String? ?? 'system',
      ),
      isEvaluative: $checkedConvert('is_evaluative', (v) => v as bool? ?? true),
      type: $checkedConvert(
        'type',
        (v) =>
            $enumDecodeNullable(_$BlockDataTypeEnumMap, v) ??
            BlockDataType.stringType,
      ),
      allowDecimals: $checkedConvert(
        'allow_decimals',
        (v) => v as bool? ?? false,
      ),
      outputExtensions: $checkedConvert(
        'output_extensions',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      theoryGrounding: $checkedConvert(
        'theory_grounding',
        (v) => v == null
            ? null
            : TheoryGrounding.fromJson(v as Map<String, dynamic>),
      ),
      scaleMin: $checkedConvert('scale_min', (v) => (v as num?)?.toInt()),
      scaleMax: $checkedConvert('scale_max', (v) => (v as num?)?.toInt()),
      scales: $checkedConvert(
        'scales',
        (v) => (v as List<dynamic>?)
            ?.map((e) => MatrixScale.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      rows: $checkedConvert(
        'rows',
        (v) => (v as List<dynamic>?)
            ?.map((e) => MatrixRow.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      columns: $checkedConvert(
        'columns',
        (v) => (v as List<dynamic>?)
            ?.map((e) => I18nText.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'aiDescription': 'ai_description',
    'categoryId': 'category_id',
    'isEvaluative': 'is_evaluative',
    'allowDecimals': 'allow_decimals',
    'outputExtensions': 'output_extensions',
    'theoryGrounding': 'theory_grounding',
    'scaleMin': 'scale_min',
    'scaleMax': 'scale_max',
  },
);

Map<String, dynamic> _$PromptBlockToJson(_PromptBlock instance) =>
    <String, dynamic>{
      'id': const StrictOpaqueIdConverter().toJson(instance.id),
      'slug': instance.slug,
      'label': instance.label.toJson(),
      'description': instance.description.toJson(),
      'ai_description': instance.aiDescription,
      'category_id': instance.categoryId,
      'is_evaluative': instance.isEvaluative,
      'type': _$BlockDataTypeEnumMap[instance.type]!,
      'allow_decimals': instance.allowDecimals,
      'output_extensions': instance.outputExtensions,
      'theory_grounding': instance.theoryGrounding?.toJson(),
      'scale_min': instance.scaleMin,
      'scale_max': instance.scaleMax,
      'scales': instance.scales?.map((e) => e.toJson()).toList(),
      'rows': instance.rows?.map((e) => e.toJson()).toList(),
      'columns': instance.columns?.map((e) => e.toJson()).toList(),
    };

const _$BlockDataTypeEnumMap = {
  BlockDataType.floatType: 'float',
  BlockDataType.intType: 'int',
  BlockDataType.stringType: 'string',
  BlockDataType.instruction: 'instruction',
  BlockDataType.panel: 'panel',
  BlockDataType.compliance: 'compliance',
  BlockDataType.question: 'question',
  BlockDataType.criteria: 'criteria',
};
