// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_exception.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_AppException _$AppExceptionFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_AppException', json, ($checkedConvert) {
      $checkKeys(
        json,
        allowedKeys: const [
          'type',
          'title',
          'status',
          'detail',
          'instance',
          'request_id',
          'extensions',
        ],
      );
      final val = _AppException(
        type: $checkedConvert('type', (v) => v as String? ?? 'about:blank'),
        title: $checkedConvert('title', (v) => v as String? ?? 'Error'),
        status: $checkedConvert('status', (v) => (v as num?)?.toInt() ?? 500),
        detail: $checkedConvert(
          'detail',
          (v) => v as String? ?? 'Unknown error',
        ),
        instance: $checkedConvert('instance', (v) => v as String?),
        requestId: $checkedConvert('request_id', (v) => v as String?),
        extensions: $checkedConvert(
          'extensions',
          (v) => v as Map<String, dynamic>? ?? const <String, dynamic>{},
        ),
      );
      return val;
    }, fieldKeyMap: const {'requestId': 'request_id'});

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
