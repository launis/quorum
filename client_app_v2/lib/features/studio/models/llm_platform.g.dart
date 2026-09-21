// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'llm_platform.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LlmPlatform _$LlmPlatformFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_LlmPlatform', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'label', 'has_regions']);
      final val = _LlmPlatform(
        id: $checkedConvert('id', (v) => v as String),
        label: $checkedConvert('label', (v) => v as String),
        hasRegions: $checkedConvert('has_regions', (v) => v as bool),
      );
      return val;
    }, fieldKeyMap: const {'hasRegions': 'has_regions'});

Map<String, dynamic> _$LlmPlatformToJson(_LlmPlatform instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'has_regions': instance.hasRegions,
    };
