// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'blueprint_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_BlueprintConfig _$BlueprintConfigFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_BlueprintConfig', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['preset_view']);
      final val = _BlueprintConfig(
        presetView: $checkedConvert(
          'preset_view',
          (v) =>
              $enumDecodeNullable(_$PresetViewEnumMap, v) ??
              PresetView.metrics1d,
        ),
      );
      return val;
    }, fieldKeyMap: const {'presetView': 'preset_view'});

Map<String, dynamic> _$BlueprintConfigToJson(_BlueprintConfig instance) =>
    <String, dynamic>{'preset_view': _$PresetViewEnumMap[instance.presetView]!};

const _$PresetViewEnumMap = {
  PresetView.metrics1d: '1d_metrics',
  PresetView.compare2d: '2d_compare',
  PresetView.matrix3d: '3d_matrix',
  PresetView.textOnly: 'text_only',
  PresetView.defaultView: 'default',
  PresetView.matrixSummary: 'matrix_summary',
};
