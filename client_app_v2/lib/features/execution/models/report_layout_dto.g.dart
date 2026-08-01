// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'report_layout_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ReportLayoutDto _$ReportLayoutDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_ReportLayoutDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'preset_view',
        'title',
        'description',
        'axes',
        'target_blocks',
        'text_delivery_mode',
        'is_synthesis_enabled',
        'synthesis',
        'synthesis_blocks',
        'matrix_visible_columns',
        'matrix_column_labels',
        'extension_labels',
      ],
    );
    final val = _ReportLayoutDto(
      presetView: $checkedConvert(
        'preset_view',
        (v) =>
            $enumDecodeNullable(
              _$PresetViewEnumMap,
              v,
              unknownValue: PresetView.defaultView,
            ) ??
            PresetView.defaultView,
      ),
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
      targetBlocks: $checkedConvert(
        'target_blocks',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      textDeliveryMode: $checkedConvert(
        'text_delivery_mode',
        (v) =>
            $enumDecodeNullable(
              _$TextDeliveryModeEnumMap,
              v,
              unknownValue: TextDeliveryMode.full,
            ) ??
            TextDeliveryMode.full,
      ),
      isSynthesisEnabled: $checkedConvert(
        'is_synthesis_enabled',
        (v) => v as bool? ?? true,
      ),
      synthesis: $checkedConvert(
        'synthesis',
        (v) => v == null
            ? null
            : SynthesisConfigDto.fromJson(v as Map<String, dynamic>),
      ),
      synthesisBlocks: $checkedConvert(
        'synthesis_blocks',
        (v) => (v as List<dynamic>?)
            ?.map((e) => SduiBlockDTO.fromJson(e as Map<String, dynamic>))
            .toList(),
      ),
      matrixVisibleColumns: $checkedConvert(
        'matrix_visible_columns',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
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
              (k, e) =>
                  MapEntry(k, I18nText.fromJson(e as Map<String, dynamic>)),
            ) ??
            const {},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'presetView': 'preset_view',
    'targetBlocks': 'target_blocks',
    'textDeliveryMode': 'text_delivery_mode',
    'isSynthesisEnabled': 'is_synthesis_enabled',
    'synthesisBlocks': 'synthesis_blocks',
    'matrixVisibleColumns': 'matrix_visible_columns',
    'matrixColumnLabels': 'matrix_column_labels',
    'extensionLabels': 'extension_labels',
  },
);

Map<String, dynamic> _$ReportLayoutDtoToJson(
  _ReportLayoutDto instance,
) => <String, dynamic>{
  'preset_view': _$PresetViewEnumMap[instance.presetView]!,
  'title': instance.title?.toJson(),
  'description': instance.description?.toJson(),
  'axes': instance.axes.map((e) => e.toJson()).toList(),
  'target_blocks': instance.targetBlocks,
  'text_delivery_mode': _$TextDeliveryModeEnumMap[instance.textDeliveryMode]!,
  'is_synthesis_enabled': instance.isSynthesisEnabled,
  'synthesis': instance.synthesis?.toJson(),
  'synthesis_blocks': instance.synthesisBlocks?.map((e) => e.toJson()).toList(),
  'matrix_visible_columns': instance.matrixVisibleColumns,
  'matrix_column_labels': instance.matrixColumnLabels.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
  'extension_labels': instance.extensionLabels.map(
    (k, e) => MapEntry(k, e.toJson()),
  ),
};

const _$PresetViewEnumMap = {
  PresetView.metrics1d: '1d_metrics',
  PresetView.compare2d: '2d_compare',
  PresetView.matrix3d: '3d_matrix',
  PresetView.textOnly: 'text_only',
  PresetView.defaultView: 'default',
  PresetView.matrixSummary: 'matrix_summary',
};

const _$TextDeliveryModeEnumMap = {
  TextDeliveryMode.full: 'full',
  TextDeliveryMode.titlesOnly: 'titles_only',
  TextDeliveryMode.none: 'none',
};
