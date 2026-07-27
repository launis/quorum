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
          allowedKeys: const [
            'executive_summary',
            'urgency_level',
            'user_role',
            'user_role_justification',
          ],
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
          userRole: $checkedConvert('user_role', (v) => v as String?),
          userRoleJustification: $checkedConvert(
            'user_role_justification',
            (v) => v as String?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'executiveSummary': 'executive_summary',
        'urgencyLevel': 'urgency_level',
        'userRole': 'user_role',
        'userRoleJustification': 'user_role_justification',
      },
    );

Map<String, dynamic> _$GlobalSynthesisDtoToJson(_GlobalSynthesisDto instance) =>
    <String, dynamic>{
      'executive_summary': instance.executiveSummary,
      'urgency_level': instance.urgencyLevel,
      'user_role': instance.userRole,
      'user_role_justification': instance.userRoleJustification,
    };
