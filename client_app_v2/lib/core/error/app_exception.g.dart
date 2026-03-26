// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_exception.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AppException _$AppExceptionFromJson(Map<String, dynamic> json) =>
    _AppException(
      type: json['type'] as String? ?? 'about:blank',
      title: json['title'] as String? ?? 'Error',
      status: (json['status'] as num?)?.toInt() ?? 500,
      detail: json['detail'] as String? ?? 'Unknown error',
      instance: json['instance'] as String?,
      requestId: json['request_id'] as String?,
      extensions:
          json['extensions'] as Map<String, dynamic>? ??
          const <String, dynamic>{},
    );

Map<String, dynamic> _$AppExceptionToJson(_AppException instance) =>
    <String, dynamic>{
      'type': instance.type,
      'title': instance.title,
      'status': instance.status,
      'detail': instance.detail,
      'instance': instance.instance,
      'request_id': instance.requestId,
      'extensions': instance.extensions,
    };
