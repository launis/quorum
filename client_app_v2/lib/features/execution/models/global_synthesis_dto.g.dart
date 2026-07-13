// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'global_synthesis_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GlobalSynthesisDTO _$GlobalSynthesisDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_GlobalSynthesisDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const ['executive_summary', 'urgency_level'],
        );
        final val = _GlobalSynthesisDTO(
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

Map<String, dynamic> _$GlobalSynthesisDTOToJson(_GlobalSynthesisDTO instance) =>
    <String, dynamic>{
      'executive_summary': instance.executiveSummary,
      'urgency_level': instance.urgencyLevel,
    };
