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
          (v) => v as String? ?? '1d_metrics',
        ),
      );
      return val;
    }, fieldKeyMap: const {'presetView': 'preset_view'});

Map<String, dynamic> _$BlueprintConfigToJson(_BlueprintConfig instance) =>
    <String, dynamic>{'preset_view': instance.presetView};
