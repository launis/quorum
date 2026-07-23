// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'global_synthesis_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GlobalSynthesisDto _$GlobalSynthesisDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_GlobalSynthesisDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['executive_summary', 'urgency_level'],
        );
        final val = _GlobalSynthesisDto(
          executiveSummary: $checkedConvert(
            'executive_summary',
            (v) => v as String?,
          ),
          urgencyLevel: $checkedConvert(
            'urgency_level',
            (v) => (v as num?)?.toInt(),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'executiveSummary': 'executive_summary',
        'urgencyLevel': 'urgency_level',
      },
    );

Map<String, dynamic> _$GlobalSynthesisDtoToJson(_GlobalSynthesisDto instance) =>
    <String, dynamic>{
      'executive_summary': instance.executiveSummary,
      'urgency_level': instance.urgencyLevel,
    };
