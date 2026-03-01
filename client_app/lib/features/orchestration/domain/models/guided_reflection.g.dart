// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'guided_reflection.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_GuidedReflectionDTO _$GuidedReflectionDTOFromJson(Map<String, dynamic> json) =>
    _GuidedReflectionDTO(
      q1Goal: json['q1_goal'] as String?,
      q2Falsification: json['q2_falsification'] as String?,
      q3Synthesis: json['q3_synthesis'] as String?,
      q4Argumentation: json['q4_argumentation'] as String?,
    );

Map<String, dynamic> _$GuidedReflectionDTOToJson(
  _GuidedReflectionDTO instance,
) => <String, dynamic>{
  'q1_goal': instance.q1Goal,
  'q2_falsification': instance.q2Falsification,
  'q3_synthesis': instance.q3Synthesis,
  'q4_argumentation': instance.q4Argumentation,
};
