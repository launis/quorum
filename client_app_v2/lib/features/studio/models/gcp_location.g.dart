// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'gcp_location.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GcpLocation _$GcpLocationFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_GcpLocation', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'label', 'description']);
      final val = _GcpLocation(
        id: $checkedConvert('id', (v) => v as String),
        label: $checkedConvert('label', (v) => v as String),
        description: $checkedConvert('description', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$GcpLocationToJson(_GcpLocation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'description': instance.description,
    };
