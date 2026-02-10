// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assessment_view.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AssessmentView _$AssessmentViewFromJson(Map<String, dynamic> json) =>
    _AssessmentView(
      sessionId: json['sessionId'] as String,
      statusLabel: json['statusLabel'] as String,
      uiVariant: json['uiVariant'] as String,
      statusMessage: json['statusMessage'] as String,
      showWarningBanner: json['showWarningBanner'] as bool,
      steps:
          (json['steps'] as List<dynamic>?)
              ?.map((e) => StepProgressItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      finalScore: (json['finalScore'] as num?)?.toInt(),
    );

Map<String, dynamic> _$AssessmentViewToJson(_AssessmentView instance) =>
    <String, dynamic>{
      'sessionId': instance.sessionId,
      'statusLabel': instance.statusLabel,
      'uiVariant': instance.uiVariant,
      'statusMessage': instance.statusMessage,
      'showWarningBanner': instance.showWarningBanner,
      'steps': instance.steps,
      'finalScore': instance.finalScore,
    };

_StepProgressItem _$StepProgressItemFromJson(Map<String, dynamic> json) =>
    _StepProgressItem(
      id: json['id'] as String,
      label: json['label'] as String,
      status: json['status'] as String,
    );

Map<String, dynamic> _$StepProgressItemToJson(_StepProgressItem instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'status': instance.status,
    };
